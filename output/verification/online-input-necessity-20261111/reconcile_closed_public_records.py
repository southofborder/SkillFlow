"""Independent stdlib-only recount of a closed fresh case's public records.

Reads only batch 20261111-173347. No project imports or process execution.
Creates a new verification artifact; never overwrites an existing result.
"""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("ga4", "001", "010", "013"))
    args = parser.parse_args()
    run = ROOT / f"experiments/doe/runs/document-guided-{args.case}-input-necessity-high-20261111-173347"
    started = read(run / "controller-started.json")
    finished = read(run / "controller-finished.json")
    replay = read(run / "replay-check.json")
    replay_start = read(run / "replay-started.json")
    metrics = read(run / "metrics.json")
    result = read(run / "result.json")
    sums = {key: 0 for key in ("input_tokens", "output_tokens", "cached_input_tokens",
                               "cache_write_input_tokens", "reasoning_output_tokens")}
    requests, reconnects, stderr_retries, hashes = [], [], [], {}
    for marker in sorted((run / "transport").rglob("started.json")):
        attempt = marker.parent
        process = read(attempt / "process.json")
        events = [json.loads(line) for line in (attempt / "stdout.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        completed = [event for event in events if event.get("type") == "turn.completed"]
        usages = [event["usage"] for event in completed if isinstance(event.get("usage"), dict)]
        request = attempt.relative_to(run).as_posix()
        for usage in usages:
            for key in sums:
                sums[key] += usage.get(key, 0)
        for line, event in enumerate(events, 1):
            if isinstance(event.get("message"), str) and "Reconnecting..." in event["message"]:
                reconnects.append({"request": request, "stdout_line": line, "message": event["message"]})
        for line, message in enumerate((attempt / "stderr.txt").read_text(encoding="utf-8").splitlines(), 1):
            if "responses_retry" in message:
                stderr_retries.append({"request": request, "stderr_line": line, "message": message})
        sidecar = read(attempt / "usage.json")
        requests.append({"request": request, "pid": read(attempt / "pid.json")["pid"],
            "thread_ids": [event["thread_id"] for event in events if event.get("type") == "thread.started"],
            "started_at": read(marker)["started_at"], "finished_at": process["finished_at"],
            "elapsed_seconds": process["elapsed_seconds"], "process_status": process["status"],
            "returncode": process["returncode"], "complete_public_turn_events": len(completed),
            "public_usage_events": usages, "usage_sidecar_known": sidecar["known"], "usage_sidecar": sidecar["usage"]})
        for name in ("started.json", "pid.json", "process.json", "stdout.jsonl", "stderr.txt", "usage.json"):
            path = attempt / name
            hashes[path.relative_to(run).as_posix()] = sha256(path.read_bytes()).hexdigest()
    sums["total_tokens"] = sums["input_tokens"] + sums["output_tokens"]
    known = [row for row in requests if row["public_usage_events"]]
    unknown = [row["request"] for row in requests if not row["public_usage_events"]]
    first = min(datetime.fromisoformat(row["started_at"]) for row in requests)
    last = max(datetime.fromisoformat(row["finished_at"]) for row in requests)
    duration = sum(row["elapsed_seconds"] for row in requests)
    checks = {
        "start_inventory_equals_saved_metrics": len(requests) == metrics["launch_attempts"] == metrics["native_process_starts"],
        "all_pid_confirmed": all(type(row["pid"]) is int for row in requests),
        "one_completed_public_turn_per_known_request": all(row["complete_public_turn_events"] == 1 for row in known),
        "known_usage_count_equals_metrics": len(known) == metrics["complete_usage_requests"],
        "unknown_usage_count_equals_metrics": len(unknown) == metrics["unknown_usage_requests"],
        "direct_token_sums_equal_saved_metrics": sums == metrics["known_token_usage"],
        "duration_sum_equal_saved_metrics": abs(duration - metrics["known_request_seconds"]) < 1e-6,
        "native_span_equal_saved_metrics": abs((last - first).total_seconds() - metrics["wall_clock_seconds"]) < 1e-5,
        "no_marker_at_or_after_replay": all(datetime.fromisoformat(row["started_at"]) < datetime.fromisoformat(replay_start["started_at"]) for row in requests),
        "replay_matched_with_zero_starts": replay["status"] == "matched" and replay["new_native_markers"] == 0,
        "no_outer_attempt_002": not any((run / "transport").rglob("attempt-002")) and metrics["network_retry_attempts"] == 0,
        "all_reported_sidecar_counters_match_raw_events": all(row["usage_sidecar_known"]
            and {"input_tokens", "output_tokens"} <= set(row["usage_sidecar"])
            and all(key in row["public_usage_events"][0] and value == row["public_usage_events"][0][key]
                    for key, value in row["usage_sidecar"].items()) for row in known),
        "unknown_sidecars_are_unknown": all(row["usage_sidecar"] == {} and not row["usage_sidecar_known"]
                                           for row in requests if not row["public_usage_events"]),
    }
    for name in ("metrics.json", "result.json", "controller-started.json", "controller-finished.json",
                 "replay-started.json", "replay-check.json"):
        hashes[name] = sha256((run / name).read_bytes()).hexdigest()
    stamp = datetime.now(timezone.utc)
    output = BASE / f"{args.case}-closed-cost-independent-reconciliation-{stamp.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    value = {"scope": "Independent standard-library recount of closed fresh public records; no project imports or process execution.",
        "observed_at": stamp.isoformat(), "run_directory": str(run),
        "utility_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "status": ("verified_with_usage_limitations" if unknown else "verified") if all(checks.values()) else "mismatch",
        "checks": checks, "known_public_usage": sums, "unknown_usage_requests": unknown, "requests": requests,
        "stdout_reconnect_notice_count": len(reconnects), "stdout_reconnect_notices": reconnects,
        "stderr_sampling_retry_log_line_count": len(stderr_retries), "stderr_sampling_retry_log_lines": stderr_retries,
        "notice": "Stdout and stderr internal notices overlap and must not be added. Provider HTTP attempts, unreported internal-attempt usage and billing remain unknown. Sidecars may omit optional zero counters; every reported counter is checked.",
        "native_wall_span_seconds": (last - first).total_seconds(), "summed_request_seconds": duration,
        "controller_elapsed_seconds": (datetime.fromisoformat(finished["finished_at"]) - datetime.fromisoformat(started["started_at"])).total_seconds(),
        "analysis_seconds": finished["analysis_seconds"], "replay": replay,
        "run_status": result["status"], "run_stage": result["stage"], "result_reason": result.get("reason"), "hashes": hashes}
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(output), "status": value["status"], "checks": checks,
        "known_public_usage": sums, "unknown_requests": len(unknown), "stdout_notices": len(reconnects),
        "stderr_retry_lines": len(stderr_retries), "controller_elapsed_seconds": value["controller_elapsed_seconds"]}))


if __name__ == "__main__":
    main()
