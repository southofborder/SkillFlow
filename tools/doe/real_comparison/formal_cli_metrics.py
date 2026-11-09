"""Read-only formal CLI accounting; dispatch records never prove process starts."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
from pathlib import Path

from . import cli_adapter_v3 as cli
from . import execution as native
from .metrics import combine_usage, human_cost_summary

SCHEMA = "skillflow-real-comparison-formal-cli-v1"


def read(path, default=None):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def _seconds(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() if value else None


def _duration(start, finish):
    a, b = _seconds(start), _seconds(finish)
    return max(0., b - a) if a is not None and b is not None else None


def process_started(directory):
    """Only a persisted successful Popen boundary proves an actual process."""
    return read(Path(directory) / "cli/process-start.json", {}).get("actual_cli_process_started") is True


def process_start_unknown(directory):
    directory = Path(directory)
    if process_started(directory) or not (directory / "dispatch.json").is_file():
        return False
    process = read(directory / "cli/process-result.json", {})
    return not (process.get("actual_cli_process_started") is False
                and process.get("status") in {"prelaunch_error", "launch_failed"})


def usage_summary(run_dir, workflow_id=None):
    rows, missing, conflicts, reused, owners = {}, [], set(), set(), {}
    actual, unknown_processes = 0, []
    for directory, request in native._requests(run_dir, workflow_id):
        if not process_started(directory):
            if process_start_unknown(directory):
                unknown_processes.append(request["request_id"])
                missing.append(request["request_id"])
            continue
        actual += 1
        receipt = read(directory / "receipt.json", {})
        usage = receipt.get("usage", {}).get("by_response_id", {})
        if receipt.get("usage_verified") is not True or not usage:
            missing.append(request["request_id"])
        for response_id, counters in usage.items():
            if not isinstance(response_id, str) or not response_id:
                missing.append(request["request_id"])
                continue
            if response_id in owners and owners[response_id] != request["request_id"]:
                reused.add(response_id)
            owners[response_id] = request["request_id"]
            if response_id in rows and rows[response_id] != counters:
                conflicts.add(response_id)
            rows[response_id] = counters
    summary = combine_usage([{"by_response_id": rows, "missing_requests": missing,
                              "conflicting_response_ids": sorted(conflicts)}])
    # A proven zero-process request consumes no target tokens. Queuing and
    # prelaunch failures must not manufacture an unknown actual request.
    if actual == 0 and not unknown_processes:
        summary["totals"] = {key: 0 for key in cli.TOKEN_FIELDS}
    summary.update(actual_cli_processes=actual, unknown_process_start_requests=unknown_processes,
                   reused_response_ids=sorted(reused))
    return summary


def request_rows(run_dir):
    rows = []
    for directory, request in native._requests(run_dir):
        dispatch = read(directory / "dispatch.json", {})
        process = read(directory / "cli/process-result.json", {})
        receipt, response = read(directory / "receipt.json", {}), read(directory / "response.json", {})
        timing = receipt.get("timing", {})
        assessments = [read(p) for p in sorted((directory / "protocol-assessments").glob("*.json"))]
        duration = timing.get("duration_ms")
        rows.append({"request_id": request["request_id"], "workflow_id": request["workflow_id"],
            "mode": request.get("mode"), "queued": True, "dispatch_attempted": bool(dispatch),
            "actual_cli_process_started": process_started(directory),
            "actual_cli_process_start_unknown": process_start_unknown(directory),
            "attributed_response": bool(receipt.get("usage", {}).get("by_response_id")),
            "response_imported": bool(response), "accepted": response.get("accepted") is True,
            "protocol_status": receipt.get("protocol_status", "unverified"),
            "runtime": receipt.get("observed_configuration"),
            "usage_by_response_id": receipt.get("usage", {}).get("by_response_id", {}),
            "queue_seconds": _duration(request.get("created_at"), dispatch.get("dispatched_at")),
            "process_supervision_seconds": process.get("supervisor_elapsed_seconds"),
            "response_seconds": duration / 1000 if type(duration) in {float, int} else None,
            "protocol_assessments": assessments, "stopped": read(directory / "stop.json")})
    return rows


def build_cost_ledger(run_dir):
    """Return an allowlisted zero-call ledger without writing experiment files."""
    from .corrigenda import _root, resolve_grading_run, lineage_human_cost
    run = _root(run_dir)
    grading_run = resolve_grading_run(run)
    calls, workflows = request_rows(run), []
    schedule = read(run / "schedule.json", {"main": [], "reviews": []})
    for item in schedule["main"] + schedule["reviews"]:
        key = item["workflow_id"]
        result = read(native._workflow(run, key) / "result.json", {})
        related = [c for c in calls if c["workflow_id"] == key]
        workflows.append({**item, "status": result.get("status", "not_started"),
            "usage": usage_summary(run, key), "timing": result.get("timing", {}),
            "workflow_elapsed_seconds": result.get("timing", {}).get("workflow_elapsed_seconds"),
            "deterministic_processing_seconds": result.get("timing", {}).get("local_processing_seconds"),
            "counts": {name: sum(c[name] for c in related) for name in (
                "queued", "dispatch_attempted", "actual_cli_process_started", "attributed_response", "accepted")}})
    by_id = {w["workflow_id"]: w for w in workflows}
    enhanced = []
    for item in schedule["reviews"]:
        pair = [by_id[k] for k in (item["original_workflow_id"], item["workflow_id"])]
        times = [w["timing"].get("workflow_elapsed_seconds") for w in pair]
        combined = combine_usage([w["usage"] for w in pair])
        if not any(w["usage"]["actual_cli_processes"] or w["usage"]["unknown_process_start_requests"] for w in pair):
            combined["totals"] = {key: 0 for key in cli.TOKEN_FIELDS}
        enhanced.append({"workflow_id": item["workflow_id"], "original_workflow_id": item["original_workflow_id"],
            "usage_original_plus_review": combined,
            "additive_workflow_seconds": sum(times) if all(type(t) in {int, float} for t in times) else None,
            "actual_cli_processes": sum(w["counts"]["actual_cli_process_started"] for w in pair)})
    bindings = read(run / "formal-gate.json", {}).get("bindings", {})
    cal = bindings.get("calibration_run")
    calibration_usage = usage_summary(cal) if cal else None
    return {"schema_version": SCHEMA, "requests": calls, "workflows": workflows,
        "target_run": str(run), "grading_run": str(grading_run),
        "planned_results": len(workflows), "all_planned_in_denominator": len(workflows) == 264,
        "counts": {key: sum(c[key] for c in calls) for key in (
            "queued", "dispatch_attempted", "actual_cli_process_started", "attributed_response", "accepted")},
        "execution_statuses": dict(Counter(w["status"] for w in workflows)),
        "unknown_process_start_requests": [c["request_id"] for c in calls if c["actual_cli_process_start_unknown"]],
        "formal_target_usage": usage_summary(run), "enhanced_original_plus_review_cost": enhanced,
        "calibration_cost": {"run": cal, "usage": calibration_usage, "included_in_formal_target_usage": False},
        "historical_and_probe_cost": {"complete_cost": None, "included_in_formal_target_usage": False},
        "preparation_cost": {"reported_record": read(run / "preparation-cost.json"), "complete_cost": None},
        "human_cost": human_cost_summary(grading_run) if (grading_run / "human-roster.json").is_file() else {
            "complete_study_human_time_seconds": None,
            "reason": "Source confirmations, primary/secondary scoring and timed work remain separate human records."},
        "grading_epoch_human_work_history": lineage_human_cost(run) if grading_run != run else None,
        "target_cost_identity": "Original target cohort only; copied grading-epoch receipts never create another target charge.",
        "billing_amount": None, "model_calls": 0,
        "unknowns": "Missing actual-process response usage stays null; response identities are deduplicated. Reasoning and cache counters are not added to reported totals."}
