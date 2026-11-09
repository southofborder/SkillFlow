"""Offline, metadata-only exploratory cost ledger; no model or semantic input.

Target aggregation requires all 264 outcomes to be sealed. Saved receipt counters
are reported observations, not invoices. Supplementary costs are always separate.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re

from .formal_cli_metrics import process_started, process_start_unknown
from .metrics import combine_usage
from .preparation_receipts import FIELDS

SCHEMA = "skillflow-exploratory-costs-v1"
SCHEDULE_FIELDS = ("workflow_id", "case_id", "method", "repeat", "kind", "original_workflow_id", "source_sha256")
WORKFLOW_TIMES = ("workflow_elapsed_seconds", "cli_wait_seconds", "local_processing_seconds", "schedule_wait_seconds")
RECEIPT_TIMES = ("started_at", "completed_at", "duration_ms", "time_to_first_token_ms")
SUPPLEMENTARY_KINDS = ("engineering_calibration", "historical_probe", "preparation_assistant", "scoring_assistant")


def _inside(root, path):
    path = Path(path).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError("Metadata path escapes its declared root")
    return path


def read_metadata(path, fields):
    """Decode only selected top-level values; skip message/native bodies opaquely.

    This bounded-memory projection never JSON-decodes an unselected payload.
    Receipt inspection/replay belongs to the generation harness, not this reader.
    """
    path = Path(path)
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as stream:
        current = stream.read(1)

        def take():
            nonlocal current
            value, current = current, stream.read(1)
            return value

        def space():
            while current and current.isspace():
                take()

        def value(keep):
            space()
            chars = []

            def consume():
                character = take()
                if keep:
                    chars.append(character)
                return character

            if not current:
                raise ValueError("Unexpected end of metadata JSON")
            first = consume()
            if first in "{[\"":
                stack = [first] if first != '"' else []
                quoted, escaped = first == '"', False
                while quoted or stack:
                    if not current:
                        raise ValueError("Unclosed metadata JSON value")
                    char = consume()
                    if quoted:
                        if escaped:
                            escaped = False
                        elif char == "\\":
                            escaped = True
                        elif char == '"':
                            quoted = False
                    elif char == '"':
                        quoted = True
                    elif char in "{[":
                        stack.append(char)
                    elif char in "}]":
                        if not stack or stack.pop() != ("{" if char == "}" else "["):
                            raise ValueError("Unbalanced metadata JSON value")
            else:
                while current and not current.isspace() and current not in ",}]":
                    consume()
            return json.loads("".join(chars)) if keep else None

        space()
        if take() != "{":
            raise ValueError("Metadata must be a JSON object")
        result, seen = {}, set()
        space()
        while current != "}":
            if current != '"':
                raise ValueError("Metadata object key must be a string")
            key = value(True)
            if key in seen:
                raise ValueError("Duplicate metadata object key")
            seen.add(key)
            space()
            if take() != ":":
                raise ValueError("Metadata object key lacks a colon")
            selected = value(key in fields)
            if key in fields:
                result[key] = selected
            space()
            if current == "}":
                break
            if take() != ",":
                raise ValueError("Metadata object lacks a comma")
            space()
        take()
        space()
        if current:
            raise ValueError("Trailing data in metadata JSON")
        return result


def _number(value):
    return value if type(value) in (int, float) and math.isfinite(value) and value >= 0 else None


def _duration(start, finish):
    try:
        a, b = [datetime.fromisoformat(v.replace("Z", "+00:00")) for v in (start, finish)]
        return _number((b - a).total_seconds()) if a.tzinfo is not None and b.tzinfo is not None else None
    except (ValueError, TypeError, AttributeError):
        return None


def _hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def _counters(raw):
    raw = raw if isinstance(raw, dict) else {}
    return {key: raw.get(key) if type(raw.get(key)) is int and raw[key] >= 0 else None for key in FIELDS}


def request_rows(run_dir):
    """Read only persisted launch/receipt metadata, including every failed request.

    Does not open prompts, answers, stdout, raw sessions or native stage files.
    The caller must ensure closure before drawing target-cohort conclusions.
    """
    run = Path(run_dir).resolve()
    rows = []
    for directory in sorted((run / "workflows").glob("*/requests/q*")):
        directory = _inside(run, directory)
        if not directory.is_dir():
            continue
        for relative in ("request.json", "dispatch.json", "receipt.json", "response.json", "failure.json", "cli/process-start.json", "cli/process-result.json"):
            _inside(run, directory / relative)
        workflow_id = directory.parent.parent.name
        request = read_metadata(directory / "request.json", ("workflow_id", "created_at"))
        if request.get("workflow_id", workflow_id) != workflow_id:
            raise ValueError("Request metadata differs from its workflow directory")
        dispatch = read_metadata(directory / "dispatch.json", ("attempted_at", "dispatched_at", "retries"))
        process = read_metadata(directory / "cli/process-result.json", (
            "status", "returncode", "finished_at", "supervisor_elapsed_seconds", "actual_cli_process_started", "retries"))
        start = read_metadata(directory / "cli/process-start.json", ("started_at", "actual_cli_process_started"))
        receipt = read_metadata(directory / "receipt.json", (
            "cli_session_id", "usage", "usage_verified", "timing", "protocol_status", "completed",
            "configuration_verified", "provider_verified", "raw_receipt_path", "raw_receipt_sha256"))
        response = read_metadata(directory / "response.json", ("accepted", "imported_at", "process_status"))
        failure = read_metadata(directory / "failure.json", ("failed_at", "automatic_retry"))
        usage = receipt.get("usage") or {}
        raw_rows = usage.get("by_response_id") or {}
        if not isinstance(raw_rows, dict):
            raw_rows = {}
        counters = {key: _counters(raw) for key, raw in raw_rows.items() if isinstance(key, str) and key}
        timing = receipt.get("timing") or {}
        started = process_started(directory)
        unknown_start = process_start_unknown(directory) or (not started and process.get("actual_cli_process_started") is True)
        observed_response = bool(counters)
        # Retain receipted work even when process-start evidence was interrupted.
        cost_expected = started or unknown_start or observed_response or process.get("actual_cli_process_started") is True
        missing = []
        if cost_expected and (receipt.get("usage_verified") is not True or not counters or len(counters) != len(raw_rows)):
            missing.append(directory.relative_to(run).as_posix())
        rows.append({
            "request_id": workflow_id + "/" + directory.name, "workflow_id": workflow_id,
            "request_directory": str(directory), "request_path": str(directory / "request.json"),
            "request_sha256": _hash(directory / "request.json") if (directory / "request.json").is_file() else None,
            "receipt_path": str(directory / "receipt.json") if (directory / "receipt.json").is_file() else None,
            "receipt_sha256": _hash(directory / "receipt.json") if (directory / "receipt.json").is_file() else None,
            "raw_receipt_path": receipt.get("raw_receipt_path"), "raw_receipt_sha256": receipt.get("raw_receipt_sha256"),
            "cli_session_id": receipt.get("cli_session_id"),
            "queued": True, "dispatch_attempted": (directory / "dispatch.json").is_file(),
            "actual_cli_process_started": started, "actual_cli_process_start_unknown": unknown_start,
            "cost_observation_expected": cost_expected, "response_imported": bool(response),
            "accepted": response.get("accepted") is True, "failure_recorded": bool(failure),
            "process_status": process.get("status"), "returncode": process.get("returncode"),
            "protocol_status": receipt.get("protocol_status", "unverified"),
            "usage_verified": receipt.get("usage_verified") is True,
            "configuration_verified": receipt.get("configuration_verified"), "provider_verified": receipt.get("provider_verified"),
            "usage_by_response_id": counters, "missing_requests": missing,
            "conflicting_response_ids": usage.get("conflicting_response_ids", []),
            "response_ids": sorted(counters),
            "created_at": request.get("created_at"), "dispatch_attempted_at": dispatch.get("attempted_at", dispatch.get("dispatched_at")),
            "process_started_at": start.get("started_at"), "process_finished_at": process.get("finished_at"),
            "response_imported_at": response.get("imported_at"), "failed_at": failure.get("failed_at"),
            "receipt_timing": {key: timing.get(key) for key in RECEIPT_TIMES},
            "queue_seconds": _duration(request.get("created_at"), dispatch.get("attempted_at", dispatch.get("dispatched_at"))),
            "process_supervision_seconds": _number(process.get("supervisor_elapsed_seconds")),
            "receipt_turn_duration_seconds": (_number(timing.get("duration_ms")) / 1000 if _number(timing.get("duration_ms")) is not None else None),
            "service_response_seconds": None,
            "service_time_status": "Provider service time is not separately reported; receipt task duration includes the CLI turn.",
            "request_elapsed_seconds": _duration(request.get("created_at"), response.get("imported_at") or failure.get("failed_at") or process.get("finished_at")),
            "transport_retries_reported": process.get("retries", dispatch.get("retries")),
            "automatic_retry": failure.get("automatic_retry"),
        })
    return rows


def summarize_requests(requests, *, missing=None):
    """Deduplicate identities and expose complete totals versus observed subtotals.

    Conflicting counters are not resolved by choosing the most recent receipt.
    Zero is reported only for an empty, closed, proven nonlaunched scope.
    """
    variants, locations, missing_requests, declared_conflicts = {}, {}, set(missing or []), set()
    for request in requests:
        missing_requests.update(request.get("missing_requests", []))
        declared_conflicts.update(request.get("conflicting_response_ids", []))
        for response_id, raw in request.get("usage_by_response_id", {}).items():
            counters = _counters(raw)
            if counters not in variants.setdefault(response_id, []):
                variants[response_id].append(counters)
            locations.setdefault(response_id, []).append({key: request.get(key) for key in (
                "request_id", "workflow_id", "receipt_path", "receipt_sha256", "raw_receipt_path", "raw_receipt_sha256")})
    conflicts = declared_conflicts | {key for key, values in variants.items() if len(values) > 1}
    safe = {key: {field: None for field in FIELDS} if key in conflicts else values[0] for key, values in variants.items()}
    combined = combine_usage([{"by_response_id": safe, "missing_requests": sorted(missing_requests),
                               "conflicting_response_ids": sorted(conflicts)}])
    if not variants and not missing_requests and not any(r.get("cost_observation_expected") for r in requests):
        combined["totals"] = {field: 0 for field in FIELDS}
    known = {field: [row[field] for row in safe.values() if row[field] is not None] for field in FIELDS}
    combined.update(
        known_subtotals={field: sum(values) if values else (0 if not variants and not missing_requests else None) for field, values in known.items()},
        known_response_counts={field: len(values) for field, values in known.items()},
        unknown_response_counts={field: len(safe) - len(values) for field, values in known.items()},
        unknown_request_count=len(missing_requests),
        response_ledger=[{"response_id": key, "counters": safe[key], "conflicting": key in conflicts,
            "reported_counter_variants": variants[key], "source_locations": locations[key]} for key in sorted(safe)],
        reused_response_ids=sorted(key for key, values in locations.items() if len({v["request_id"] for v in values}) > 1),
        complete=not missing_requests and not conflicts and all(value is not None for value in combined["totals"].values()),
        accounting="Reported input includes cached input and output includes reasoning. Detail counters are never added again; no character, cumulative-session, pricing or invoice estimate is used.")
    return combined


def _schedule(run):
    schedule = read_metadata(run / "schedule.json", ("main", "reviews"))
    main, reviews = schedule.get("main", []), schedule.get("reviews", [])
    rows = [{key: value for key, value in item.items() if key in SCHEDULE_FIELDS} for item in main + reviews]
    ids = [item.get("workflow_id") for item in rows]
    if (len(main) != 216 or len(reviews) != 48 or len(set(ids)) != 264
            or any(not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", key) for key in ids)):
        raise ValueError("Cost reporting requires the unchanged 216 + 48 distinct workflow schedule")
    cases = {item.get("case_id") for item in rows}
    expected = {(case, method, repeat) for case in cases for method in ("skillflow", "audit", "chain") for repeat in (1, 2, 3)}
    actual = {(item.get("case_id"), item.get("method"), item.get("repeat")) for item in rows[:216]}
    if len(cases) != 24 or actual != expected or any(item.get("kind") != "main" for item in rows[:216]):
        raise ValueError("All 24 cases, three methods and three main repetitions must remain present")
    by_id = {item["workflow_id"]: item for item in rows[:216]}
    seen = set()
    for item in rows[216:]:
        original = by_id.get(item.get("original_workflow_id"), {})
        pair = (item.get("case_id"), item.get("method"))
        if (item.get("kind") != "review" or item.get("repeat") != 1 or item.get("method") not in ("audit", "chain")
                or pair in seen or any(original.get(key) != item.get(key) for key in ("case_id", "method", "repeat"))):
            raise ValueError("Reviews must bind every exact direct R1 once, without replacement")
        seen.add(pair)
    return rows


def _workflow(run, item, requests, *, sealed_files=None):
    key = item["workflow_id"]
    directory = _inside(run, run / "workflows" / key)
    path = directory / "result.json"
    if sealed_files is not None:
        relative = path.relative_to(run).as_posix()
        _inside(run, path)
        if not path.is_file() or sealed_files.get(relative) != _hash(path):
            raise ValueError("A planned terminal result is missing or differs from the output seal")
        state_path = _inside(run, directory / "state.json")
        state_relative = state_path.relative_to(run).as_posix()
        if (state_path.is_file() or state_relative in sealed_files) and (not state_path.is_file() or sealed_files.get(state_relative) != _hash(state_path)):
            raise ValueError("Workflow timing metadata differs from the output seal")
    result = read_metadata(path, ("workflow_id", "status", "finished_at", "timing"))
    if result.get("workflow_id", key) != key:
        raise ValueError("Workflow result metadata differs from its schedule identity")
    state = read_metadata(directory / "state.json", ("started_at",))
    usage = summarize_requests(requests, missing=[] if result else ["missing_terminal_result:" + key])
    timing = result.get("timing") or {}
    times = {name: _number(timing.get(name)) for name in WORKFLOW_TIMES}
    if times["workflow_elapsed_seconds"] is None and "elapsed_seconds" in timing:
        times["workflow_elapsed_seconds"] = _number(timing["elapsed_seconds"])
    return {**item, "status": result.get("status", "missing_terminal_result"), "result_path": str(path),
        "started_at": state.get("started_at"), "finished_at": result.get("finished_at"),
        "workflow_wall_span_seconds": _duration(state.get("started_at"), result.get("finished_at")),
        "timing": times, **times, "usage": usage, "reported_total_tokens": usage["totals"]["total_tokens"],
        "request_ids": [row["request_id"] for row in requests],
        "counts": {name: sum(row.get(name) is True for row in requests) for name in (
            "queued", "dispatch_attempted", "actual_cli_process_started", "actual_cli_process_start_unknown", "accepted", "failure_recorded")},
        "human_review_work_seconds": None}


def _summarize_workflows(workflows):
    times = [row["workflow_elapsed_seconds"] for row in workflows]
    return {"planned_workflows": len(workflows), "statuses": dict(Counter(row["status"] for row in workflows)),
        "reported_workflow_elapsed_seconds_sum": sum(times) if all(t is not None for t in times) else None,
        "known_workflow_elapsed_seconds_subtotal": sum(t for t in times if t is not None) if any(t is not None for t in times) else None,
        "unknown_workflow_elapsed_count": sum(t is None for t in times),
        "time_basis": "Additive complete workflow durations include failed work. Concurrent workflows overlap; their sum is not study wall time. Missing durations stay unknown."}


def _attribution_guard(summary, workflow_ids, owners):
    """A shared response has one global charge but no invented per-arm split."""
    ambiguous = sorted(key for key in summary["by_response_id"] if not owners.get(key, set()).issubset(workflow_ids))
    summary["shared_out_of_scope_response_ids"] = ambiguous
    summary["cost_attribution_ambiguous"] = bool(ambiguous)
    if ambiguous:
        summary["observed_scope_totals"] = summary["totals"].copy()
        summary["totals"] = {field: None for field in FIELDS}
        summary["complete"] = False
    return summary


def supplementary_run(run_dir, kind):
    """Explicit supplementary run only; discovery never scans historical runs."""
    if kind not in SUPPLEMENTARY_KINDS:
        raise ValueError("Unknown supplementary accounting category")
    run = Path(run_dir).resolve()
    requests = request_rows(run)
    ids = sorted({row["workflow_id"] for row in requests} | {p.name for p in (run / "workflows").glob("*") if p.is_dir()})
    workflows = [_workflow(run, {"workflow_id": key}, [row for row in requests if row["workflow_id"] == key]) for key in ids]
    missing = ["missing_terminal_result:" + row["workflow_id"] for row in workflows if row["status"] == "missing_terminal_result"]
    return {"kind": kind, "run": str(run), "included_in_target_usage": False, "requests": requests,
        "workflows": workflows, "usage": summarize_requests(requests, missing=missing if workflows else ["no_registered_supplementary_workflows"]),
        "workflow_summary": _summarize_workflows(workflows), "complete_historical_cost": None}


def receipt_capture(path, kind):
    """Import an explicitly supplied metadata-only preparation capture.

    Capture windows and exact primary-thread attribution are retained. A capture
    is a subtotal, even when all counters inside that bounded window are known.
    """
    if kind not in ("preparation_assistant", "scoring_assistant"):
        raise ValueError("Receipt captures require an explicit assistant accounting category")
    path = Path(path).resolve()
    record = read_metadata(path, ("schema_version", "captured_at", "since", "observed", "response_locations", "counter_conflicts", "limitations"))
    if record.get("schema_version") != "skillflow-preparation-receipt-capture-v2":
        raise ValueError("Use the exact-attribution preparation_receipts v2 metadata capture")
    observed = record.get("observed") or {}
    rows = []
    for key, counters in observed.get("by_response_id", {}).items():
        rows.append({"request_id": str(path) + ":" + key, "workflow_id": None, "receipt_path": str(path),
            "usage_by_response_id": {key: counters}, "cost_observation_expected": True,
            "conflicting_response_ids": observed.get("conflicting_response_ids", [])})
    missing = list(observed.get("missing_requests", []))
    if not rows:
        missing.append("no_attributed_assistant_response_receipt:" + str(path))
    usage = summarize_requests(rows, missing=missing)
    # Preserve conflicts that were deliberately redacted by the capture helper.
    usage["conflicting_response_ids"] = sorted(set(usage["conflicting_response_ids"]) | set(observed.get("conflicting_response_ids", [])))
    if usage["conflicting_response_ids"]:
        usage["totals"] = {field: None for field in FIELDS}
        usage["complete"] = False
    return {"kind": kind, "capture_path": str(path), "capture_sha256": _hash(path), "included_in_target_usage": False,
        "since": record.get("since"), "captured_at": record.get("captured_at"), "usage": usage,
        "response_locations": record.get("response_locations", {}), "counter_conflicts": record.get("counter_conflicts", {}),
        "complete_historical_cost": None, "actual_human_work_seconds": None, "limitations": record.get("limitations")}


def build_cost_ledger(run_dir, *, supplementary_runs=(), receipt_captures=()):
    """Build all 264 planned rows after closure, without reading answer content.

    supplementary_runs and receipt_captures contain (category, explicit_path)
    pairs. No supplementary history is silently discovered or merged into targets.
    """
    run = Path(run_dir).resolve()
    closure = read_metadata(run / "output-freeze.json", ("planned_outputs", "closed_at", "files"))
    if closure.get("planned_outputs") != 264 or not closure.get("closed_at") or not isinstance(closure.get("files"), dict):
        raise ValueError("Wait for all 264 planned outputs and the immutable output-freeze before cost integration")
    frozen = read_metadata(run / "freeze.json", ("files",))
    if (frozen.get("files") or {}).get("schedule.json") != _hash(run / "schedule.json"):
        raise ValueError("The workflow schedule differs from the frozen input identity")
    schedule = _schedule(run)
    metadata_pattern = re.compile(r"workflows/[A-Za-z0-9_-]+/requests/q[^/]+/(?:request|dispatch|receipt|response|failure|cli/process-start|cli/process-result)\.json")
    for relative, expected_hash in closure["files"].items():
        if metadata_pattern.fullmatch(relative):
            path = _inside(run, run / relative)
            if not path.is_file() or _hash(path) != expected_hash:
                raise ValueError("Sealed request accounting metadata is missing or changed")
    calls = request_rows(run)
    scheduled = {item["workflow_id"] for item in schedule}
    extras = sorted({row["workflow_id"] for row in calls} - scheduled)
    if extras:
        raise ValueError("Unscheduled workflow request metadata must be reconciled explicitly")
    for row in calls:
        directory = Path(row["request_directory"])
        for path in [directory / "request.json", directory / "dispatch.json", directory / "receipt.json", directory / "response.json",
                     directory / "failure.json", directory / "cli/process-start.json", directory / "cli/process-result.json"]:
            if path.is_file() and closure["files"].get(path.relative_to(run).as_posix()) != _hash(path):
                raise ValueError("Request accounting metadata differs from the output seal")
    workflows = [_workflow(run, item, [row for row in calls if row["workflow_id"] == item["workflow_id"]], sealed_files=closure["files"]) for item in schedule]
    response_owners = {}
    for call in calls:
        for key in call["response_ids"]:
            response_owners.setdefault(key, set()).add(call["workflow_id"])
    for workflow in workflows:
        _attribution_guard(workflow["usage"], {workflow["workflow_id"]}, response_owners)
        workflow["reported_total_tokens"] = workflow["usage"]["totals"]["total_tokens"]
    by_id = {row["workflow_id"]: row for row in workflows}
    enhanced = []
    for item in schedule[216:]:
        pair = [by_id[key] for key in (item["original_workflow_id"], item["workflow_id"])]
        pair_ids = {w["workflow_id"] for w in pair}
        usage = _attribution_guard(summarize_requests([row for row in calls if row["workflow_id"] in pair_ids]), pair_ids, response_owners)
        times = [row["workflow_elapsed_seconds"] for row in pair]
        enhanced.append({**item, "usage_original_plus_review": usage,
            "reported_total_tokens": usage["totals"]["total_tokens"],
            "additive_workflow_seconds": sum(times) if all(t is not None for t in times) else None,
            "statuses": {row["workflow_id"]: row["status"] for row in pair}, "human_review_work_seconds": None})
    target_usage = summarize_requests(calls)
    extra_runs = [supplementary_run(path, kind) for kind, path in supplementary_runs]
    captures = [receipt_capture(path, kind) for kind, path in receipt_captures]
    for extra in extra_runs:
        if Path(extra["run"]) == run:
            raise ValueError("The target run cannot also be a supplementary cost")
    ownership = {}
    for category, source, ids in [("target", str(run), target_usage["by_response_id"]), *[
            (item["kind"], item.get("run", item.get("capture_path")), item["usage"]["by_response_id"]) for item in extra_runs + captures]]:
        for key in ids:
            ownership.setdefault(key, []).append({"category": category, "source": source})
    shared_categories = {key: owners for key, owners in ownership.items() if len(owners) > 1}
    for summary in [target_usage, *[row["usage"] for row in workflows],
                    *[row["usage_original_plus_review"] for row in enhanced], *[item["usage"] for item in extra_runs + captures]]:
        shared = sorted(set(summary["by_response_id"]) & shared_categories.keys())
        summary["shared_supplementary_response_ids"] = shared
        if shared:
            summary.setdefault("observed_scope_totals", summary["totals"].copy())
            summary["totals"] = {field: None for field in FIELDS}
            summary["cost_attribution_ambiguous"] = True
            summary["complete"] = False
    for row in workflows:
        row["reported_total_tokens"] = row["usage"]["totals"]["total_tokens"]
    for row in enhanced:
        row["reported_total_tokens"] = row["usage_original_plus_review"]["totals"]["total_tokens"]
    return {"schema_version": SCHEMA, "evidence_level": "assistant_exploratory_not_human_gold", "target_run": str(run),
        "output_closed_at": closure["closed_at"], "output_freeze_sha256": _hash(run / "output-freeze.json"),
        "input_freeze_sha256": _hash(run / "freeze.json"),
        "schedule_sha256": _hash(run / "schedule.json"), "planned_results": 264, "planned_main_results": 216,
        "planned_review_results": 48, "all_planned_in_denominator": True,
        "requests": calls, "workflows": workflows, "target_usage": target_usage,
        "request_counts": {name: sum(row.get(name) is True for row in calls) for name in (
            "queued", "dispatch_attempted", "actual_cli_process_started", "actual_cli_process_start_unknown", "accepted", "failure_recorded")},
        "shared_cross_workflow_response_ids": {key: sorted(owners) for key, owners in response_owners.items() if len(owners) > 1},
        "enhanced_original_plus_review_cost": enhanced, "workflow_summary": _summarize_workflows(workflows),
        "by_method_and_kind": {method + ":" + kind: _summarize_workflows([row for row in workflows if row["method"] == method and row["kind"] == kind])
            for method, kind in (("skillflow", "main"), ("audit", "main"), ("chain", "main"), ("audit", "review"), ("chain", "review"))},
        "supplementary_costs": extra_runs + captures,
        "cross_category_response_ids": shared_categories,
        "combined_study_cost": None, "actual_human_work_seconds": None, "human_review_work_seconds": None,
        "billing_amount": None, "model_calls": 0,
        "limitations": ["Only selected persisted metadata is decoded; target answers, source/reference contents, hidden reasoning and semantic reports are excluded.",
            "Saved receipt extraction and output closure are prerequisites; this ledger does not rerun raw-session protocol verification.",
            "Known subtotals exclude conflicting identities and cannot substitute for complete costs. Detail token counters overlap reported input/output totals.",
            "A response shared with an out-of-scope workflow has no inferred per-workflow charge allocation; its scoped cost total is unknown, while the full target total remains deduplicated.",
            "Supplementary categories are separate explicit inputs; response identities shared across categories are disclosed and no combined study total is inferred.",
            "Request sequence includes structural corrections and failed/retried requests without inferring their semantic role from prompts. Unobserved historical, assistant and human work remains unknown."]}


def write_cost_ledger(ledger, out_dir):
    """Write new JSON/CSV artifacts outside the immutable generation run."""
    out = Path(out_dir).resolve()
    run = Path(ledger["target_run"]).resolve()
    if out.is_relative_to(run) or out.exists():
        raise ValueError("Use a fresh output directory outside the generation run")
    out.mkdir(parents=True)

    def write_json(path, value):
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def write_csv(path, rows, columns):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value for key, value in row.items() if key in columns})

    write_json(out / "cost-ledger.json", ledger)
    write_json(out / "workflows.json", ledger["workflows"])
    write_json(out / "requests.json", ledger["requests"])
    write_json(out / "responses.json", ledger["target_usage"]["response_ledger"])
    write_csv(out / "workflows.csv", [{**{key: row.get(key) for key in (*SCHEDULE_FIELDS, "status", *WORKFLOW_TIMES)},
        "reported_total_tokens": row["reported_total_tokens"], "known_total_tokens_subtotal": row["usage"]["known_subtotals"]["total_tokens"],
        "response_count": row["usage"]["response_count"], "unknown_request_count": row["usage"]["unknown_request_count"],
        "unknown_total_token_responses": row["usage"]["unknown_response_counts"]["total_tokens"],
        "human_review_work_seconds": None} for row in ledger["workflows"]],
        [*SCHEDULE_FIELDS, "status", *WORKFLOW_TIMES, "reported_total_tokens", "known_total_tokens_subtotal", "response_count",
         "unknown_request_count", "unknown_total_token_responses", "human_review_work_seconds"])
    write_csv(out / "requests.csv", ledger["requests"], ["request_id", "workflow_id", "receipt_path", "receipt_sha256", "raw_receipt_path", "cli_session_id",
        "dispatch_attempted", "actual_cli_process_started", "actual_cli_process_start_unknown", "accepted", "failure_recorded", "process_status",
        "protocol_status", "usage_verified", "response_ids", "missing_requests", "queue_seconds", "process_supervision_seconds",
        "receipt_turn_duration_seconds", "service_response_seconds", "request_elapsed_seconds", "transport_retries_reported"])
    response_rows = [{"response_id": row["response_id"], **row["counters"], "conflicting": row["conflicting"], "source_locations": row["source_locations"]}
                     for row in ledger["target_usage"]["response_ledger"]]
    write_csv(out / "responses.csv", response_rows, ["response_id", *FIELDS, "conflicting", "source_locations"])
    summary = {key: value for key, value in ledger.items() if key not in ("requests", "workflows", "enhanced_original_plus_review_cost", "supplementary_costs", "target_usage")}
    summary["target_usage"] = {key: value for key, value in ledger["target_usage"].items() if key not in ("by_response_id", "response_ledger")}
    summary["supplementary_costs"] = [{key: value for key, value in item.items() if key in ("kind", "run", "capture_path", "included_in_target_usage", "complete_historical_cost")}
                                      | {"usage": {key: value for key, value in item["usage"].items() if key not in ("by_response_id", "response_ledger")}} for item in ledger["supplementary_costs"]]
    write_json(out / "summary.json", summary)
    return {"out_dir": str(out), "planned_workflows": len(ledger["workflows"]), "model_calls": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--supplementary-run", nargs=2, action="append", default=[], metavar=("CATEGORY", "PATH"))
    parser.add_argument("--receipt-capture", nargs=2, action="append", default=[], metavar=("CATEGORY", "PATH"))
    args = parser.parse_args(argv)
    ledger = build_cost_ledger(args.run_dir, supplementary_runs=args.supplementary_run, receipt_captures=args.receipt_capture)
    print(json.dumps(write_cost_ledger(ledger, args.out_dir), indent=2))


if __name__ == "__main__":
    main()
