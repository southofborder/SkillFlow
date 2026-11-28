"""Observe exact current deliveries without a client, runner, replay or writes to runs."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-lossless-delivery-high-20261122-211742"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PROJECT / "src"))
from skillflow.document_guided.processing_display import expand_display_material


def read(path):
    return json.loads(path.read_bytes()) if path.is_file() else {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def source_check(text, source):
    verified = []
    for name, content in source.items():
        lines = content.splitlines(keepends=True)
        block = f"\nSOURCE skill/{name}:1-{len(lines)}\n"
        block += "".join(f"{index}: {line}" for index, line in enumerate(lines, 1))
        if block in text:
            verified.append(name)
    return {"complete_files": len(verified), "expected_files": len(source),
            "all_complete": len(verified) == len(source),
            "missing": sorted(set(source) - set(verified))}


def shared_check(text):
    result = []
    for marker in ("\nFRAGMENT_INPUT_JSON\n", "\nPROCESSING_INPUT_JSON\n"):
        if marker not in text:
            continue
        start = text.index(marker) + len(marker)
        envelope, length = json.JSONDecoder().raw_decode(text[start:])
        logical = expand_display_material(envelope, identity=envelope["format"])
        expanded = compact(logical)
        encoded = text[start:start + length]
        # A controlled size comparison: change only this JSON body. Complete
        # source, instructions and all other characters remain byte-identical.
        replacement = text[:start] + expanded + text[start + length:]
        result.append({"format": envelope["format"], "owner": logical.get("owner"),
            "logical_keys": list(logical), "logical_sha256": envelope["logical_sha256"],
            "expanded_digest_matches": sha(expanded.encode()) == envelope["logical_sha256"],
            "encoded_json_characters": len(encoded), "expanded_json_characters": len(expanded),
            "encoding_characters_saved": len(expanded) - len(encoded),
            "actual_delivery_characters": len(text),
            "same_payload_expanded_reference_characters": len(replacement),
            "same_payload_expanded_reference_exceeds_limit": len(replacement) > 1048576,
            "outside_json_unchanged": replacement[:start] == text[:start]
                and replacement[start + len(expanded):] == text[start + length:],
            "contains_task": "task" in logical,
            "contains_correction": "correction" in logical,
            "contains_scope": "scope" in logical,
            "contains_repair_context": "repair_context" in logical,
            "documents": list(logical.get("documents", {})),
            "comparison_notice": "Same logical JSON only, with every other delivered character held fixed; not a historical-renderer or token/latency comparison."})
    return result


def main():
    observed = datetime.now(timezone.utc)
    protocol = read(RUN / "run-protocol.json")
    inherited = read(RUN / "accepted-upstream.json")
    source_root = RUN / "source/inputs/package"
    source = {name: (source_root / name).read_bytes().decode("utf-8-sig")
              for name in protocol["source_file_sha256"]}
    source_hashes = {name: sha((source_root / name).read_bytes()) for name in source}
    rows, notices, costs, incomplete = [], [], Counter(), []
    native_markers, native_pids = [], []
    for path in sorted((RUN / "transport").rglob("request.json")):
        request, preflight = read(path), read(path.with_name("preflight.json"))
        owner = path.parent
        stage = owner.parent.relative_to(RUN / "transport").as_posix()
        stage_root = RUN / stage if stage in {"task", "review", "revision/task", "revision/review"} else RUN / "steps" / stage
        logical_path = stage_root / request["logical_call"]
        call = read(logical_path)
        raw = path.with_name("prompt.txt").read_bytes()
        delivery = raw.decode("utf-8")
        core = call.get("prompt")
        preflight_checks = {"characters": preflight.get("characters") == len(delivery),
            "utf8_bytes": preflight.get("utf8_bytes") == len(raw),
            "sha256": preflight.get("sha256") == sha(raw) == request.get("delivery_sha256"),
            "section_character_sum": sum(r["characters"] for r in preflight.get("sections", {}).values()) == len(delivery),
            "section_byte_sum": sum(r["utf8_bytes"] for r in preflight.get("sections", {}).values()) == len(raw),
            "logical_core_digest": isinstance(core, str) and sha(core.encode()) == request.get("core_sha256"),
            "logical_core_is_delivery_suffix": isinstance(core, str) and delivery.endswith(core),
            "status_matches_limit": preflight.get("status") == ("within_limit" if len(delivery) <= preflight.get("max_characters", 0) else "input_too_large")}
        attempts = []
        for marker in sorted(owner.rglob("started.json")):
            native_markers.append(marker.relative_to(RUN).as_posix())
            attempt, started, pid = marker.parent, read(marker), read(marker.with_name("pid.json"))
            process = read(attempt / "process.json")
            native_pids.append(pid.get("pid"))
            usage_events = []
            for number, line in enumerate((attempt / "stdout.jsonl").read_bytes().splitlines(), 1):
                try:
                    event = json.loads(line)
                except (ValueError, UnicodeError):
                    continue
                if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                    usage_events.append(event["usage"])
                if event.get("type") in {"error", "turn.failed"}:
                    notices.append({"request": attempt.relative_to(RUN).as_posix(), "stream": "stdout", "line": number,
                        "message": event.get("message", event.get("error"))})
            stderr = attempt / "stderr.txt"
            for number, line in enumerate(stderr.read_text(encoding="utf-8", errors="replace").splitlines() if stderr.exists() else [], 1):
                if "responses_retry:" in line or ("responses_websocket:" in line and "failed to connect" in line) or "falling back to HTTP" in line:
                    notices.append({"request": attempt.relative_to(RUN).as_posix(), "stream": "stderr", "line": number, "message": line})
            complete = (len(usage_events) == 1 and process.get("exited") is True
                        and all(type(usage_events[0].get(k)) is int for k in ("input_tokens", "output_tokens")))
            if complete:
                costs.update({k: v for k, v in usage_events[0].items() if type(v) is int})
            else:
                incomplete.append(attempt.relative_to(RUN).as_posix())
            attempts.append({"pid": pid.get("pid"), "started_at": started.get("started_at"),
                "process_status": process.get("status"), "elapsed_seconds": process.get("elapsed_seconds"),
                "finished_at": process.get("finished_at"), "public_usage": usage_events,
                "single_complete_public_usage": complete,
                "preflight_file_present_no_later_than_start_marker": path.with_name("preflight.json").stat().st_mtime_ns <= marker.stat().st_mtime_ns})
        rows.append({"request": owner.relative_to(RUN).as_posix(), "stage": stage,
            "logical_call": request["logical_call"], "actual_characters": len(delivery),
            "max_characters": preflight.get("max_characters"), "preflight_checks": preflight_checks,
            "sections": {key: item["characters"] for key, item in preflight.get("sections", {}).items()},
            "source": source_check(delivery, source), "shared": shared_check(delivery),
            "attempts": attempts, "rejection": read(owner / "input-rejection.json"),
            "record_sha256": {"request": sha(path.read_bytes()), "preflight": sha(path.with_name("preflight.json").read_bytes()), "delivery": sha(raw)}})
    costs["total_tokens"] = costs["input_tokens"] + costs["output_tokens"]
    controller, replay = read(RUN / "controller-finished.json"), read(RUN / "replay-check.json")
    value = {"observed_at": observed.isoformat(), "run_directory": str(RUN),
        "status": "closed_observation" if controller else "provisional_running_observation",
        "implementation_sha256": protocol["implementation_sha256"],
        "source_bytes_match_protocol": source_hashes == protocol["source_file_sha256"],
        "source_files": len(source), "inherited_logical_calls_excluded": inherited.get("inherited_logical_calls"),
        "fresh_transport_deliveries": len(rows), "fresh_native_markers": len(native_markers),
        "pid_confirmed_native_starts": sum(type(pid) is int and pid > 0 for pid in native_pids),
        "known_public_usage": dict(costs), "incomplete_or_ambiguous_usage_requests": incomplete,
        "controller_finished": controller or None, "replay_check": replay or None,
        "deliveries": rows, "main_transport_notices": notices,
        "method": "Read actual delivery bytes/preflight/public counters; invoke only a pure codec decoder. No model, Skill, runner or replay. Same-payload expanded references replace only the JSON display body; historical different outputs are not a controlled size comparison. Public counters exclude inherited requests and do not establish provider internal attempts or billing."}
    target = VERIFY / ("independent-delivery-audit-" + observed.strftime("%Y%m%dT%H%M%SZ") + ".json")
    with target.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(target), "status": value["status"],
        "all_preflights_match": all(all(row["preflight_checks"].values()) for row in rows),
        "complete_source_in_every_delivery": all(row["source"]["all_complete"] for row in rows),
        "fresh_native_starts": value["pid_confirmed_native_starts"],
        "known_public_usage": value["known_public_usage"],
        "incomplete_usage_count": len(incomplete),
        "encoding_comparisons": [{"stage": row["stage"], **item} for row in rows for item in row["shared"]]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
