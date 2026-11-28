"""Read existing guided-run evidence and emit a public, read-only request audit."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RUN = ROOT / "experiments/doe/runs/document-guided-ga4-program-owned-cfg-high-20261118-153823"
sys.dont_write_bytecode = True
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256
from tools.doe.document_guided_metrics import transport_metrics


def blob(path, warnings):
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as exc:
        warnings.append(f"{path}: {type(exc).__name__}")
        return None


def obj(path, warnings):
    raw = blob(path, warnings)
    if raw is None:
        return {}
    try:
        value = json.loads(raw)
        if isinstance(value, dict):
            return value
        warnings.append(f"{path}: expected JSON object")
    except (ValueError, UnicodeError) as exc:
        warnings.append(f"{path}: {type(exc).__name__} (possibly still being written)")
    return {}


def typed(row, *keys):
    return {key: row[key] for key in keys if key in row}


def source_in_delivery(prompt, files):
    if files is None or prompt is None:
        return None
    marker = "COMPLETE_ORIGINAL_SOURCE\n\n"
    if marker in prompt:
        source = prompt.split(marker, 1)[1]
        try:
            value, _ = json.JSONDecoder().raw_decode(source)
            rows = value["source_files"]
            observed = {row["file"]: row["lines"] for row in rows}
            if len(rows) != len(observed):
                return None
        except (ValueError, TypeError, KeyError):
            return None
        verified = sorted(name for name, lines in files.items() if observed.get(name) == lines)
        mode = "task_source_json_exact_line_arrays"
    elif "\nRELATED SOURCE\n" in prompt or "\nCOMPLETE SOURCE\n" in prompt:
        # Match the complete numbered source block with original line endings.
        # A filename mention or a matching number range alone proves nothing.
        splitter = "\nRELATED SOURCE\n" if "\nRELATED SOURCE\n" in prompt else "\nCOMPLETE SOURCE\n"
        view = prompt.split(splitter, 1)[1]
        if splitter == "\nRELATED SOURCE\n":
            view = view.rsplit("\n\nOUTPUT REQUIREMENTS\n", 1)[0]
        verified = []
        for name, lines in files.items():
            if lines:
                block = f"\nSOURCE {name}:1-{len(lines)}\n"
                block += "".join(f"{index}: {line}" for index, line in enumerate(lines, 1))
                at = view.find(block)
                end = at + len(block)
                if at >= 0 and (end == len(view) or view.startswith("\n\nSOURCE ", end)):
                    verified.append(name)
        verified.sort()
        mode = "numbered_source_blocks_exact_lines"
    else:
        return None
    return {"mode": mode, "complete_file_count": len(verified), "snapshot_file_count": len(files),
            "complete_files": verified, "not_verified_complete": sorted(set(files) - set(verified)),
            "all_verified_complete": len(verified) == len(files)}


_STAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\b")
_RETRY = re.compile(r"(?:sampling request \(|Reconnecting\.\.\.\s*)(\d+)/(\d+)", re.I)
_BACKOFF = re.compile(r"sampling request \(\d+/\d+ in (\d+(?:\.\d+)?)(ms|s)\)")
_SIGNALS = {
    "tls handshake eof": "tls_handshake_eof",
    "error decoding response body": "response_body_decode_error",
    "request timed out": "request_timed_out",
    "deadline has elapsed": "deadline_elapsed",
    "network unreachable": "network_unreachable",
    "connection reset": "connection_reset",
    "(os error 10054)": "windows_peer_connection_reset",
    "connection refused": "connection_refused",
    "selected model is at capacity": "selected_model_at_capacity",
}


def _notice(line, text, category):
    stamp = _STAMP.match(text)
    retry = _RETRY.search(text)
    backoff = _BACKOFF.search(text)
    signals = [name for phrase, name in _SIGNALS.items() if phrase in text.lower()]
    return {"line": line, "timestamp": stamp[0] if stamp else None, "category": category,
            "excerpt_signals": signals, "retry_index": int(retry[1]) if retry else None,
            "retry_limit": int(retry[2]) if retry else None,
            "reported_backoff_seconds": (float(backoff[1]) / (1000 if backoff[2] == "ms" else 1)
                                         if backoff else None)}


def network_observations(attempt, warnings):
    main, auxiliary, notices = [], [], []
    raw = blob(attempt / "stderr.txt", warnings)
    for number, line in enumerate((raw or b"").decode("utf-8", errors="replace").splitlines(), 1):
        if "responses_retry:" in line:
            kind = ("sampling_retry" if "retrying sampling request" in line else
                    "connection_wait" if "waiting to retry" in line else "other_responses_retry")
            main.append(_notice(number, line, kind))
        elif "responses_websocket:" in line and "failed to connect" in line:
            main.append(_notice(number, line, "websocket_connection_failed"))
        elif "codex_core::client:" in line and "falling back to HTTP" in line:
            main.append(_notice(number, line, "responses_fallback_to_http"))
        elif "failed to refresh available models" in line:
            auxiliary.append(_notice(number, line, "model_catalog_refresh_failed"))
        elif ("codex_mcp::" in line or "codex_rmcp_client::" in line) and any(
                marker in line.lower() for marker in ("startup", "initialize", "failed", "shutdown", "reconnect")):
            auxiliary.append(_notice(number, line, "mcp_endpoint_activity"))
    stdout = blob(attempt / "stdout.jsonl", warnings)
    for number, raw_line in enumerate((stdout or b"").splitlines(), 1):
        try:
            row = json.loads(raw_line)
        except (ValueError, UnicodeError):
            continue
        if not isinstance(row, dict) or row.get("type") not in {"error", "turn.failed"}:
            continue
        message = row.get("message") or row.get("error")
        message = message.get("message") if isinstance(message, dict) else message
        if isinstance(message, str) and re.search(r"\breconnecting\b", message, re.I):
            category = ("public_connection_wait" if "waiting for network" in message.lower()
                        else "public_sampling_reconnect" if _RETRY.search(message) else "public_other_reconnect")
            notices.append(_notice(number, message, category))
    return {"responses_stderr_events": main, "auxiliary_stderr_events": auxiliary,
            "public_stdout_notices": notices, "stderr_present": raw is not None,
            "stdout_present": stdout is not None,
            "scope": "Timestamped and line-indexed diagnostic signals only. Public reconnect notices may repeat stderr; auxiliary endpoints, provider HTTP requests and native process launches are distinct."}


def _stage(owner):
    parts = owner.parts
    if len(parts) == 2 and parts[0] == "steps":
        return parts[1]
    if parts in {("review",), ("task",), ("revision", "task"), ("revision", "review")}:
        return owner.as_posix()
    return None


def _category(stage, index):
    if index is not None and index > 1:
        return "structural_correction"
    if index != 1:
        return "unclassified"
    return "semantic_repair" if stage.startswith(("revision-", "revision/")) else "normal"


def _index(logical):
    match = re.search(r"(?:^|/)a(\d+)/call\.json$", logical or "")
    return int(match[1]) if match else None


def _logical_calls(run, warnings):
    roots = [run / name for name in ("task", "review", "revision/task", "revision/review")]
    roots.extend(sorted(p for p in (run / "steps").glob("*") if p.is_dir()))
    calls = {}
    for root in roots:
        stage = _stage(root.relative_to(run))
        if stage is None:
            continue
        for path in sorted((root / "calls").rglob("call.json")):
            logical = path.relative_to(root).as_posix()
            index = _index(logical)
            if index is None:
                continue
            call = obj(path, warnings)
            request = obj(path.with_name("request.json"), warnings)
            validation = obj(path.with_name("validation.json"), warnings)
            prompt = call.get("prompt")
            core_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest() if isinstance(prompt, str) else None
            calls[(stage, logical)] = {"path": path.relative_to(run).as_posix(), "stage": stage,
                "logical_call": logical, "index": index, "category": _category(stage, index),
                "call": typed(call, "status", "started_at", "finished_at", "response_sha256"),
                "validation": typed(validation, "status", "outcome", "error_type"),
                "request": typed(request, "kind", "prompt_sha256", "response_sha256", "correction_strategy"),
                "core_sha256": core_sha256,
                "canonical_prompt_digest_matches": (canonical_sha256(prompt) == request["prompt_sha256"]
                    if core_sha256 is not None and "prompt_sha256" in request else None),
                "transport_deliveries": []}
    return calls


def audit(run):
    run = run.resolve(strict=True)
    warnings = []
    manifest = obj(run / "manifest.json", warnings)
    if not manifest.get("identity", "").startswith("skillflow-document-guided-run-"):
        raise ValueError(f"Not a document-guided run: {run}")
    try:
        _, snapshot, _ = read_snapshot(run / "source")
        files = {"skill/" + row["path"]: row["content"].splitlines(keepends=True) for row in snapshot["files"]}
    except (ValueError, OSError, KeyError) as exc:
        warnings.append(f"Cannot verify source snapshot: {type(exc).__name__}")
        files = None
    result = obj(run / "result.json", warnings)
    controller = obj(run / "controller-finished.json", warnings)
    analysis = obj(run / "analysis-finished.json", warnings)
    inherited = obj(run / "accepted-upstream.json", warnings)
    calls = _logical_calls(run, warnings)
    metrics = transport_metrics(run)
    native_by_delivery = defaultdict(list)
    for row in metrics["requests"]:
        path = run / row["request"]
        # Request paths are generated by transport_metrics from this run directory.
        row["network"] = network_observations(path, warnings)
        row.pop("thread_id", None)
        native_by_delivery[row["logical_request"] or path.parent.relative_to(run).as_posix()].append(row)
    delivered = []
    for path in sorted((run / "transport").rglob("request.json")):
        prep = obj(path, warnings)
        stage = path.parent.parent.relative_to(run / "transport").as_posix()
        key = path.parent.relative_to(run).as_posix()
        logical = prep.get("logical_call")
        file_row = calls.get((stage, logical))
        index = _index(logical)
        raw = blob(path.with_name("prompt.txt"), warnings)
        prompt = None
        delivery = None
        if raw is not None:
            digest = hashlib.sha256(raw).hexdigest()
            try:
                prompt = raw.decode("utf-8")
            except UnicodeError:
                warnings.append(f"{key}: delivery is not UTF-8")
            delivery = {"characters": len(prompt) if prompt is not None else None, "utf8_bytes": len(raw),
                        "sha256": digest, "request_digest_matches": digest == prep.get("delivery_sha256"),
                        "logical_core_digest_matches": (prep.get("core_sha256") == file_row["core_sha256"]
                            if file_row and file_row["core_sha256"] else None)}
        accepted = obj(path.with_name("accepted.json"), warnings)
        rejection = obj(path.with_name("input-rejection.json"), warnings)
        delivered.append({"path": key, "stage": stage, "logical_call": logical, "index": index,
            "category": _category(stage, index), "logical_receipt_present": file_row is not None,
            "delivery": delivery, "source": source_in_delivery(prompt, files),
            "runtime": typed(prep, "runtime", "timeout", "network_retries"),
            "accepted": typed(accepted, "attempt", "answer_sha256", "finished_at"),
            "rejection": typed(rejection, "status", "actual_chars", "max_chars", "process_started"),
            "native_attempts": native_by_delivery.pop(key, [])})
        if file_row is not None:
            file_row["transport_deliveries"].append(key)
    confirmed_categories = Counter()
    native_outer_retry_starts = 0
    responses_events, auxiliary_events, public_notices = Counter(), Counter(), Counter()
    for item in delivered:
        for row in item["native_attempts"]:
            if row["native_process_started"]:
                confirmed_categories[item["category"]] += 1
                native_outer_retry_starts += (row.get("network_attempt_index") or 0) > 1
            for counter, stream in ((responses_events, "responses_stderr_events"),
                    (auxiliary_events, "auxiliary_stderr_events"), (public_notices, "public_stdout_notices")):
                counter.update(event["category"] for event in row["network"][stream])
    if native_by_delivery:
        warnings.append("Native markers without a captured request: " + ", ".join(sorted(native_by_delivery)))
    inherited_count = inherited.get("inherited_logical_calls")
    return {"identity": "skillflow-passive-request-audit-v1", "run": str(run),
        "observed_at": datetime.now(timezone.utc).isoformat(), "guided_identity": manifest["identity"],
        "status": {"result": typed(result, "status", "stage", "repair_used"),
            "analysis_finished": typed(analysis, "status", "started_at", "finished_at", "analysis_seconds"),
            "controller_finished": typed(controller, "status", "finished_at", "analysis_seconds", "replay")},
        "counts": {"fresh_logical_call_receipts": len(calls), "inherited_logical_calls_excluded": inherited_count,
            "logical_by_category": dict(Counter(row["category"] for row in calls.values())),
            "transport_deliveries": len(delivered), "confirmed_native_by_logical_category": dict(confirmed_categories),
            "confirmed_native_outer_retry_starts": native_outer_retry_starts,
            "calls_without_transport_delivery": sum(not item["transport_deliveries"] for item in calls.values()),
            **typed(metrics, "native_process_starts", "launch_attempts", "inputs_rejected_before_start",
                    "unknown_native_process_starts", "network_retry_attempts", "complete_usage_requests",
                    "partial_usage_requests", "unknown_usage_requests", "known_request_seconds", "wall_clock_seconds"),
            "responses_stderr_events": dict(responses_events), "auxiliary_stderr_events": dict(auxiliary_events),
            "public_stdout_notices": dict(public_notices)},
        "usage": typed(metrics, "known_token_usage", "partial_token_usage", "total_usage_known", "notice"),
        "source": {"source_sha256": None if files is None else snapshot["source_sha256"],
            "snapshot_file_count": None if files is None else len(files)},
        "logical_calls": list(calls.values()), "deliveries": delivered, "unbound_native_attempts": dict(native_by_delivery),
        "warnings": warnings + metrics["monitor_warnings"],
        "scope": ("Saved public evidence only, with possible live observation races. Native request time includes local, "
            "connection and response time; pure generation and unreported provider usage are unavailable. "
            "Counts describe inspected receipts, not permissions, and exclude the inherited calls from fresh totals.")}


def compare(current, prior):
    def bucket(audit):
        grouped = defaultdict(list)
        for item in audit["deliveries"]:
            grouped[(item["stage"], item["index"])].append(item)
        return grouped
    new, old = bucket(current), bucket(prior)
    rows = []
    for stage, index in sorted(new.keys() | old.keys(), key=lambda key: (key[0], key[1] or 0)):
        left, right = old[(stage, index)], new[(stage, index)]
        def single(items):
            return items[0]["delivery"] if len(items) == 1 else None
        prev, now = single(left), single(right)
        delta = (now["characters"] - prev["characters"]
                 if prev and now and prev["characters"] is not None and now["characters"] is not None else None)
        rows.append({"stage": stage, "logical_attempt_index": index, "prior_deliveries": len(left),
                     "current_deliveries": len(right), "prior_delivery": prev, "current_delivery": now,
                     "characters_change": delta})
    return {"prior_run": prior["run"], "source_snapshot_matches": (
        current["source"]["source_sha256"] == prior["source"]["source_sha256"]
        if current["source"]["source_sha256"] and prior["source"]["source_sha256"] else None),
        "prior_counts": prior["counts"], "prior_usage": prior["usage"], "rows": rows,
        "scope": "Descriptive comparison by stage and logical attempt. Same source does not hold model answers, diagnostics or network conditions fixed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--compare", type=Path, help="Optional prior guided run for a descriptive comparison.")
    args = parser.parse_args()
    result = audit(args.run)
    if args.compare:
        result["comparison"] = compare(result, audit(args.compare))
    print(json.dumps(result, ensure_ascii=True, allow_nan=False, indent=2))


if __name__ == "__main__":
    main()
