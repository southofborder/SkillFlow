"""Measure durable pipeline calls without invoking a model or changing inputs.

Only metrics.json and metrics.md are written. Token counts come from actual
HTTP usage records, never from prompt length or a tokenizer estimate.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from skillflow.common.artifact_io import atomic_write_text
from skillflow.common.source_evidence import _json_object

STAGES = {
    "task_extraction": ("task", "task"),
    "annotation": ("annotation", "annotation"),
    "initial_review": ("refinement/initial-review", "review"),
    "task_revision": ("refinement/task-revision", "task"),
    "annotation_repair": ("refinement/repair", "annotation"),
    "final_review": ("refinement/final-review", "review"),
}


def read(path, default=None):
    return _json_object(path.read_text(encoding="utf-8")) if path.is_file() else default


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def stamp(path):
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


def delta(start, finish):
    if not start or not finish:
        return None
    return (datetime.fromisoformat(finish) - datetime.fromisoformat(start)).total_seconds()


def flatten_numbers(value, prefix=""):
    result = {}
    if isinstance(value, dict):
        for key, item in value.items():
            name = f"{prefix}.{key}" if prefix else key
            if type(item) in (int, float):
                result[name] = item
            elif isinstance(item, dict):
                result.update(flatten_numbers(item, name))
    return result


def token_value(usage, name):
    aliases = {"input_tokens": ("input_tokens", "prompt_tokens"),
               "output_tokens": ("output_tokens", "completion_tokens"),
               "total_tokens": ("total_tokens",)}
    if not isinstance(usage, dict):
        return None
    return next((usage[key] for key in aliases[name] if type(usage.get(key)) is int), None)


def sum_usage(attempts):
    result = {"http_attempts": len(attempts), "usage_records": sum(isinstance(a["usage"], dict) for a in attempts)}
    for name in ("input_tokens", "output_tokens", "total_tokens"):
        values = [token_value(a["usage"], name) for a in attempts]
        known = [v for v in values if v is not None]
        result[name] = {
            "total": sum(known) if len(known) == len(values) and values else None,
            "reported_subtotal": sum(known) if known else None,
            "attempts_with_value": len(known),
            "attempts_missing_value": len(values) - len(known),
        }
    fields = sorted({key for a in attempts for key in flatten_numbers(a["usage"])})
    result["api_reported_fields"] = {}
    for key in fields:
        values = [flatten_numbers(a["usage"]).get(key) for a in attempts]
        known = [v for v in values if v is not None]
        result["api_reported_fields"][key] = {
            "reported_subtotal": sum(known), "attempts_with_value": len(known),
            "attempts_missing_value": len(values) - len(known),
        }
    return result


def collect_call(path, root, case, stage):
    record = read(path / "call.json")
    prompt_path = path / "prompt.txt"
    prompt_bytes = prompt_path.read_bytes() if prompt_path.is_file() else None
    prompt_text = prompt_bytes.decode("utf-8") if prompt_bytes is not None else None
    request = read(path / "request.json", {})
    trace_path = path / "transport.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8")) if trace_path.is_file() else []
    if not isinstance(trace, list) or any(not isinstance(item, dict) for item in trace):
        raise ValueError("Transport record must contain a list of objects")
    validation = read(path / "validation.json", {})
    normal = read(path / "normalization.json")
    errors, attempts = [], []
    for generation, transport in enumerate(trace):
        original = dict(transport)
        expected = original.pop("record_sha256", None)
        actual = hashlib.sha256(json.dumps(original, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
        if actual != expected:
            errors.append("transport record digest mismatch")
        for index, attempt in enumerate(transport.get("http_attempts", [])):
            raw = attempt.get("raw_response")
            raw = raw if isinstance(raw, dict) else {}
            stream = attempt.get("stream") or {}
            queue_timeout = ("unable to start processing your request within the 900-second timeout limit"
                             in (attempt.get("error") or ""))
            incomplete_read = attempt.get("error_type") == "IncompleteRead"
            attempts.append({
                "generation_index": generation + 1,
                "http_attempt_index": index + 1,
                "status": attempt.get("status"),
                "http_status": attempt.get("http_status"),
                "error_type": attempt.get("error_type"),
                "elapsed_seconds": attempt.get("elapsed_seconds"),
                "returned_model": attempt.get("returned_model"),
                "finish_reasons": [c.get("finish_reason") for c in raw.get("choices", [])],
                "usage": attempt.get("usage"),
                "stream_outcome": stream.get("outcome"),
                "stream_received_bytes": stream.get("received_bytes"),
                "stream_event_count": stream.get("event_count"),
                "headers_received_at": stream.get("headers_received_at"),
                "first_byte_at": stream.get("first_byte_at"),
                "first_event_at": stream.get("first_event_at"),
                "first_content_at": stream.get("first_content_at"),
                "last_event_at": stream.get("last_event_at"),
                "partial_content_characters": len(stream.get("partial_content", "")),
                "failure_note": ("Provider explicitly reported that processing did not start within its 900-second queue limit; this is not a JSON, reference, or semantic-review rejection."
                                 if queue_timeout else "The HTTP response stream ended with IncompleteRead before a complete candidate was accepted; this is a transport/execution failure, not structural correction or semantic-review failure."
                                 if incomplete_read else None),
            })
    wall = delta(record.get("started_at"), record.get("finished_at"))
    transport_seconds = [x.get("elapsed_seconds") for x in trace]
    http_seconds = [a["elapsed_seconds"] for a in attempts]
    return {
        "case": case, "stage": stage, "call": path.relative_to(root).as_posix(),
        "request_kind": request.get("kind"), "request_index": request.get("index"),
        "structural_correction": request.get("index", 1) > 1,
        "status": record.get("status"), "validation_status": validation.get("status"),
        "prompt_size": {"characters": len(prompt_text) if prompt_text is not None else None,
                        "utf8_bytes": len(prompt_bytes) if prompt_bytes is not None else None,
                        "sha256": hashlib.sha256(prompt_bytes).hexdigest() if prompt_bytes is not None else None},
        "started_at": record.get("started_at"), "finished_at": record.get("finished_at"),
        "call_wall_seconds": wall,
        "transport_call_seconds": sum(transport_seconds) if transport_seconds and all(type(v) in (int, float) for v in transport_seconds) else None,
        "http_seconds": sum(http_seconds) if http_seconds and all(type(v) in (int, float) for v in http_seconds) else None,
        "http_attempts_observed": bool(trace) and all(t.get("http_attempts_observed") is True for t in trace),
        "http_attempts": attempts,
        "http_retries": sum(max(0, len(t.get("http_attempts", [])) - 1) for t in trace),
        "json_normalized": validation.get("normalization_sha256") is not None,
        "normalization_receipt": (path / "normalization.json").relative_to(root).as_posix() if normal is not None else None,
        "token_usage": sum_usage(attempts),
        "record_integrity_errors": errors,
        "record_sha256": {name: digest(file) for file in sorted(path.iterdir()) if file.is_file()
                          for name in (file.name,)},
    }


def aggregate(calls):
    attempts = [a for c in calls for a in c["http_attempts"]]
    result = {
        "logical_calls": len(calls),
        "stage_initial_requests": sum(not c["structural_correction"] for c in calls),
        "structural_corrections": sum(c["structural_correction"] for c in calls),
        "json_normalizations": sum(c["json_normalized"] for c in calls),
        "semantic_repair_requests": sum(c["stage"] == "annotation_repair" and not c["structural_correction"] for c in calls),
        "task_revision_requests": sum(c["stage"] == "task_revision" and not c["structural_correction"] for c in calls),
        "http_attempts": len(attempts), "http_retries": sum(c["http_retries"] for c in calls),
        "token_usage": sum_usage(attempts),
        "returned_models": sorted({a["returned_model"] for a in attempts if a["returned_model"]}),
    }
    sizes = [c["prompt_size"] for c in calls]
    distinct = {s["sha256"]: s for s in sizes if s["sha256"] is not None}
    result["prompt_input_size"] = {
        "logical_request_prompts": len(calls),
        "prompts_with_size": sum(s["characters"] is not None for s in sizes),
        "characters": sum(s["characters"] for s in sizes) if sizes and all(s["characters"] is not None for s in sizes) else None,
        "utf8_bytes": sum(s["utf8_bytes"] for s in sizes) if sizes and all(s["utf8_bytes"] is not None for s in sizes) else None,
        "distinct_prompt_contents": len(distinct),
        "distinct_content_characters": sum(s["characters"] for s in distinct.values()) if distinct else None,
        "distinct_content_utf8_bytes": sum(s["utf8_bytes"] for s in distinct.values()) if distinct else None,
        "http_retry_duplicates_counted": False,
    }
    for name in ("call_wall_seconds", "transport_call_seconds", "http_seconds"):
        values = [c[name] for c in calls]
        result[name] = {"total": sum(values) if values and all(v is not None for v in values) else None,
                        "completed_subtotal": sum(v for v in values if v is not None) if any(v is not None for v in values) else None,
                        "calls_missing_value": sum(v is None for v in values)}
    return result


def format_metric(value):
    if value is None:
        return "unknown"
    return f"{value:,.2f}" if type(value) is float else f"{value:,}" if type(value) is int else str(value)


def token_display(usage, name):
    value = usage[name]
    if value["total"] is not None:
        return format_metric(value["total"])
    return f"unknown (reported subtotal: {format_metric(value['reported_subtotal'])}; {value['attempts_missing_value']} missing)"


def _repair_route(calls):
    revised = any(call["stage"] == "task_revision" for call in calls)
    repaired = any(call["stage"] == "annotation_repair" for call in calls)
    if revised:
        return "task_revision_and_reannotation" if repaired else "task_revision_started"
    return "fixed_task_annotation_repair" if repaired else "none"


def _call_inventory(calls):
    return {f"{call['call']}/{name}": digest
            for call in calls for name, digest in call["record_sha256"].items()}


def collect(run_dir, *, final=False, online_start=None):
    root = Path(run_dir).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Pipeline directory is unavailable")
    previous = read(root / "metrics.json", {})
    final = bool(final or previous.get("final"))
    summary = read(root / "summary.json", {})
    manifest = read(root / "manifest.json", {})
    case_names = tuple(manifest.get("cases") or summary.get("cases") or
                       sorted(p.name for p in (root / "cases").iterdir() if p.is_dir()))
    if not case_names:
        raise ValueError("No pipeline cases are available")
    calls, cases = [], {}
    for case in case_names:
        case_dir = root / "cases" / case
        own, stages = [], {}
        for name, (relative, prefix) in STAGES.items():
            stage_calls = [collect_call(p.parent, root, case, name)
                           for p in sorted((case_dir / relative / "calls" / prefix).glob("a*/call.json"))]
            own.extend(stage_calls)
            stages[name] = aggregate(stage_calls)
        result_path = case_dir / "result.json"
        result = read(result_path, {})
        terminal = bool(result) and result.get("status") not in {"running", "prepared"}
        first_call = min((c["started_at"] for c in own if c["started_at"]), default=None)
        previous_case = previous.get("cases", {}).get(case, {})
        result_digest = digest(result_path) if terminal else None
        saved_timing = (previous_case.get("online_timing", {})
                        if previous_case.get("terminal_result_sha256") == result_digest else {})
        end = saved_timing.get("finished_at") or (stamp(result_path) if terminal else None)
        timing = {"started_at": first_call, "finished_at": end,
                  "elapsed_seconds": delta(first_call, end),
                  "basis": "earliest recorded call.started_at to initially observed terminal pipeline result.json mtime; excludes pre-call preparation/verification"}
        observed = aggregate(own)
        reported = result.get("counts")
        counts_match = (all(observed.get(key) == value for key, value in reported.items())
                        if isinstance(reported, dict) else None)
        route = _repair_route(own)
        for call in own:
            if call["stage"] == "annotation_repair":
                call["semantic_role"] = "new_task_reannotation" if route.startswith("task_revision") else "fixed_task_semantic_repair"
            else:
                call["semantic_role"] = call["stage"]
        cases[case] = {"pipeline_status": result.get("status", "not_finished"),
                      "task": result.get("task"), "selected_annotation": result.get("selected_annotation"),
                      "repair_route": route,
                      "review": result.get("refinement"), "propagation": result.get("propagation"), "doe": result.get("doe"),
                      "counts": observed, "stages": stages, "online_timing": timing,
                      "pipeline_reported_counts": reported,
                      "pipeline_counts_match_observed": counts_match,
                      "terminal_result_sha256": result_digest}
        calls.extend(own)
    summary_terminal = (set(summary.get("cases", {})) == set(case_names)
                        and not summary.get("not_started")
                        and all(c["terminal_result_sha256"] for c in cases.values()))
    summary_digest = digest(root / "summary.json") if summary_terminal else None
    saved_end = (previous.get("online_timing", {}).get("finished_at")
                 if previous.get("terminal_summary_sha256") == summary_digest else None)
    end = saved_end or (stamp(root / "summary.json") if summary_terminal else None)
    saved_start = previous.get("online_timing", {}).get("started_at")
    if online_start and saved_start and previous.get("online_timing", {}).get("start_basis") == "explicit" and online_start != saved_start:
        raise ValueError("Online start differs from the recorded measurement clock")
    explicit_start = online_start or (saved_start if previous.get("online_timing", {}).get("start_basis") == "explicit" else None)
    start = explicit_start or min((c["started_at"] for c in calls if c["started_at"]), default=None)
    if start:
        datetime.fromisoformat(start)
    if delta(start, end) is not None and delta(start, end) < 0:
        raise ValueError("Online timing ends before it starts")
    inventory = _call_inventory(calls)
    previous_inventory = previous.get("frozen_call_files")
    if previous.get("final") and previous_inventory is not None and previous_inventory != inventory:
        raise ValueError("Final measured call files changed; do not overwrite their original measurement")
    output = {
        "measurement_schema": "skillflow-online-metrics-v2", "run": root.name,
        "measured_at": datetime.now(timezone.utc).isoformat(), "final": final,
        "method": {
            "scope": "Only the six durable request directories of cases in this pilot: Task extraction, annotation, initial review, isolated Task revision, annotation repair/reannotation, and final review. Connectivity diagnostics are excluded.",
            "logical_calls": "One on-disk call.json per actual request. Corrections are distinct calls; accepted-response replay is not a call.",
            "tokens": "Sum HTTP attempt usage exactly once; top-level transport usage repeats the last attempt and is excluded. Missing usage is unknown, never zero.",
            "cache": "API-reported cache-hit/miss/reasoning/detail fields are breakdowns, not extra tokens; never add them to total_tokens.",
            "prompt_size": "Character and UTF-8 byte counts use each actual prompt.txt once per logical request, with a content-hash deduplication subtotal. HTTP retries do not create prompts. These are sizes, not token estimates.",
            "time": "Call wall, transport call, and HTTP elapsed are nested measures and must not be added together. Per-case clocks include local stage work. Initial terminal times are frozen before replay.",
            "overall_start": "An explicit process start can be supplied once; otherwise use the earliest recorded call. Preparation is excluded. Never infer a process clock from measurement time.",
            "not_semantics": "Usage and completion metrics do not validate sensitivity, demand, or DOE conclusions.",
        },
        "online_timing": {"started_at": start, "finished_at": end,
                          "elapsed_seconds": delta(start, end),
                          "start_basis": "explicit" if explicit_start else "earliest_recorded_call",
                          "basis": "explicit online process start or earliest recorded call to initially observed completed pilot summary.json mtime"},
        "terminal_summary_sha256": summary_digest,
        "frozen_call_files": inventory if final else None,
        "totals": aggregate(calls), "cases": cases, "calls": calls,
        "zero_api_replay": read(root / "replay-summary.json"),
    }
    if output["zero_api_replay"] is not None:
        replay = output["zero_api_replay"]
        output["zero_api_replay"] = {k: replay.get(k) for k in ("api_calls", "history_unchanged", "interrupted", "not_started")}
        output["zero_api_replay"]["case_statuses"] = {k: v.get("status") for k, v in replay.get("cases", {}).items()}
        output["zero_api_replay"]["call_files_unchanged"] = (previous_inventory == inventory if previous_inventory is not None else None)
    if final and not summary_terminal:
        raise ValueError("Final metrics require terminal results for every pilot case")
    if final and any(c["pipeline_counts_match_observed"] is False for c in cases.values()):
        raise ValueError("Observed calls differ from recorded pipeline counts")
    if final and any(c["record_integrity_errors"] for c in calls):
        raise ValueError("Transport integrity checks failed")
    return output


def render(output):
    t = output["totals"]
    lines = ["# Online execution metrics", "", f"Run: `{output['run']}`", "",
             "These measurements describe actual requests. They do not establish semantic correctness.", "",
             "| Case | Logical calls | Structural corrections | JSON normalizations | Annotation repair / reannotation | HTTP attempts / retries | Reported input | Reported output | Reported total | Online seconds |", "|---|---:|---:|---:|---:|---:|---|---|---|---:|"]
    for case, row in output["cases"].items():
        c = row["counts"]
        lines.append(f"| {case} | {c['logical_calls']} | {c['structural_corrections']} | {c['json_normalizations']} | {c['semantic_repair_requests']} | {c['http_attempts']} / {c['http_retries']} | {token_display(c['token_usage'], 'input_tokens')} | {token_display(c['token_usage'], 'output_tokens')} | {token_display(c['token_usage'], 'total_tokens')} | {format_metric(row['online_timing']['elapsed_seconds'])} |")
    lines += ["", "Normal / fixed-Task annotation repair / isolated Task revision and reannotation use 3 / 5 / 6 semantic calls. Structural corrections and HTTP retries are additional; these are not total-request limits.",
              "", "| Case | Actual repair route | Task revision requests | Semantic-stage initial requests | Counts match pipeline |", "|---|---|---:|---:|---|"]
    for case, row in output["cases"].items():
        counts = row["counts"]
        lines.append(f"| {case} | {row['repair_route']} | {counts['task_revision_requests']} | {counts['stage_initial_requests']} | {row['pipeline_counts_match_observed']} |")
    lines += ["", f"Overall online wall time: **{format_metric(output['online_timing']['elapsed_seconds'])} seconds**.",
              f"Logical requests: **{t['logical_calls']}**. HTTP attempts: **{t['http_attempts']}**. API-reported total tokens: **{token_display(t['token_usage'], 'total_tokens')}**.",
              "", "## Per-request detail", "", "| Case / stage / call | Outcome | Correction | JSON repair | HTTP attempts | Call seconds | HTTP seconds | Reported total tokens |", "|---|---|---|---|---:|---:|---:|---|"]
    for c in output["calls"]:
        label = f"{c['case']} / {c['semantic_role']} / {Path(c['call']).name}"
        lines.append(f"| [{label}]({c['call']}/call.json) | {c['status']} / {c['validation_status']} | {c['structural_correction']} | {c['json_normalized']} | {len(c['http_attempts'])} | {format_metric(c['call_wall_seconds'])} | {format_metric(c['http_seconds'])} | {token_display(c['token_usage'], 'total_tokens')} |")
    lines += ["", "## API-reported reasoning and cache breakdown", "", "These fields are parts of the reported token totals, not additional tokens. Missing fields stay unknown.", "", "| Case / stage / call | Input | Output | Reasoning within output | Cache-hit input | Cache-miss input |", "|---|---:|---:|---:|---:|---:|"]
    def detail(c, field):
        item = c["token_usage"]["api_reported_fields"].get(field)
        if item is None:
            return "unknown"
        value = format_metric(item["reported_subtotal"])
        return value if not item["attempts_missing_value"] else f"known subtotal {value} ({item['attempts_missing_value']} missing)"
    for c in output["calls"]:
        label = f"{c['case']} / {c['semantic_role']} / {Path(c['call']).name}"
        lines.append(f"| {label} | {token_display(c['token_usage'], 'input_tokens')} | {token_display(c['token_usage'], 'output_tokens')} | {detail(c, 'completion_tokens_details.reasoning_tokens')} | {detail(c, 'prompt_cache_hit_tokens')} | {detail(c, 'prompt_cache_miss_tokens')} |")
    lines += ["", "## Actual prompt input size", "",
              "These are character and UTF-8 byte counts, not token estimates. Each logical request is counted once; HTTP retries of the same request are not additional prompts.", "",
              "| Case / stage / call | Characters | UTF-8 bytes |", "|---|---:|---:|"]
    for c in output["calls"]:
        label = f"{c['case']} / {c['semantic_role']} / {Path(c['call']).name}"
        lines.append(f"| [{label}]({c['call']}/prompt.txt) | {format_metric(c['prompt_size']['characters'])} | {format_metric(c['prompt_size']['utf8_bytes'])} |")
    size = t["prompt_input_size"]
    lines += ["", f"Across {size['logical_request_prompts']} logical requests: **{format_metric(size['characters'])} characters / {format_metric(size['utf8_bytes'])} UTF-8 bytes**. Distinct prompt contents: **{size['distinct_prompt_contents']}**, totaling {format_metric(size['distinct_content_characters'])} characters / {format_metric(size['distinct_content_utf8_bytes'])} UTF-8 bytes."]
    lines += ["", "## Consumption explanation", ""]
    usage = t["token_usage"]
    reasoning = usage["api_reported_fields"].get("completion_tokens_details.reasoning_tokens", {})
    reasoning_count = reasoning.get("reported_subtotal")
    completion_count = usage["output_tokens"]["reported_subtotal"]
    total_count = usage["total_tokens"]["reported_subtotal"]
    if reasoning_count is not None and completion_count and total_count:
        scope = "complete reported usage" if not reasoning.get("attempts_missing_value") and usage["total_tokens"]["total"] is not None else "currently API-reported subtotals; pending or unreported attempts are excluded"
        lines.append(f"For {scope}, reasoning accounts for **{format_metric(reasoning_count)} tokens**, **{reasoning_count / completion_count:.2%} of completion tokens** and **{reasoning_count / total_count:.2%} of total tokens**. Reasoning is already included in completion and total tokens; adding it again would double-count consumption.")
    else:
        lines.append("No complete reasoning-token proportion is currently available from the provider records.")
    lines += ["", "A long request can spend substantial time and output-token budget in reasoning before any final JSON text appears. Stream-event counts and bytes are not token measurements. This run uses the frozen configured reasoning effort; the report records consumption without changing generation settings.", "", "Per-request call wall times measure each model operation plus its local call wrapper. Per-case wall times additionally include stage validation, compilation, propagation, and DOE work. Overall process wall time includes sequential case orchestration. These are nested clocks and are not added together.", "", "## Measurement boundaries", ""]
    lines += [f"- {value}" for value in output["method"].values()]
    lines += ["- Per-case timing starts at the first recorded call and ends at the initial terminal pipeline result write. It excludes the small validation interval before that call.",
              "- Running requests have incomplete time/usage. Failed HTTP attempts without usage prevent a claim of complete token totals; known subtotals remain available.",
              "- API usage, including cache details, is preserved per HTTP attempt in metrics.json. No tokenizer-based estimate or price assumption is substituted.", ""]
    failures = [(c, a) for c in output["calls"] for a in c["http_attempts"] if a["failure_note"]]
    if failures:
        lines += ["## Provider and transport failures", ""]
        for c, a in failures:
            lines.append(f"- {c['case']} / {c['stage']} / {Path(c['call']).name}, HTTP attempt {a['http_attempt_index']}: {a['failure_note']} No result is inferred from HTTP status {a['http_status']} alone. Recorded content characters: {a['partial_content_characters']}.")
        lines.append("")
    return "\n".join(lines)


def write_metrics(run_dir, *, final=False, online_start=None):
    """Write external measurements only; no stage result or receipt is rewritten."""
    root = Path(run_dir).expanduser().resolve()
    output = collect(root, final=final, online_start=online_start)
    atomic_write_text(root / "metrics.json", json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    atomic_write_text(root / "metrics.md", render(output))
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--online-start", help="Actual online process start in ISO 8601 with UTC offset; optional, retained on later measurements")
    args = parser.parse_args(argv)
    output = write_metrics(args.run_dir, final=args.final, online_start=args.online_start)
    print(json.dumps({"logical_calls": output["totals"]["logical_calls"],
                      "http_attempts": output["totals"]["http_attempts"], "final": output["final"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
