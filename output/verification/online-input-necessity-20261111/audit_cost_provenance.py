"""Passive public-cost and byte-provenance audit for the sole prepared batch.

Standard library only. Never imports the analysis/transport/controller, executes
a Skill, starts a process, replays analysis, or reads private session records.
Default output is stdout; --write creates a new report only beside this utility.
Live observations are always provisional. Public counters are not provider bills.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re


VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens",
          "reasoning_output_tokens", "total_tokens")
SIDECAR_FIELDS = tuple(key for key in FIELDS if key != "cache_write_input_tokens")


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def timestamp(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (AttributeError, ValueError, OverflowError):
        return None


def read(path, warnings=None):
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_bytes().decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("expected a JSON object")
        return value
    except (OSError, ValueError) as error:
        if warnings is None:
            raise
        warnings.append({"path": str(path), "reason": str(error)})
        return {}


def file_sha(path):
    return sha(path.read_bytes()) if path.is_file() else None


def bound(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Audit reference escapes its recorded owner: " + str(relative))
    return path


def add(target, values):
    for key, value in values.items():
        target[key] = target.get(key, 0) + value


def counters(usage):
    values = {key: usage[key] for key in FIELDS
              if isinstance(usage, dict) and type(usage.get(key)) is int and usage[key] >= 0}
    complete = all(key in values for key in ("input_tokens", "output_tokens"))
    if complete:
        total = values["input_tokens"] + values["output_tokens"]
        complete = (values.get("total_tokens", total) == total
                    and values.get("cached_input_tokens", 0) <= values["input_tokens"]
                    and values.get("reasoning_output_tokens", 0) <= values["output_tokens"])
        if values.get("total_tokens", total) == total:
            values["total_tokens"] = total
    return values, complete


def classify(stage, logical_call, attempt):
    logical = re.search(r"(?:^|/)a(\d+)/call\.json$", logical_call or "")
    native = re.fullmatch(r"attempt-(\d+)", attempt)
    logical_index = int(logical[1]) if logical else None
    network_index = int(native[1]) if native else None
    semantic = stage.startswith(("revision-", "revision/"))
    structural = logical_index is not None and logical_index > 1
    category = ("network_retry" if network_index and network_index > 1 else
                "structural_correction" if structural else
                "semantic_repair" if semantic else
                "normal" if logical_index == 1 else "unknown")
    return {"category": category, "semantic_repair": semantic,
            "structural_correction": structural, "logical_attempt_index": logical_index,
            "network_attempt_index": network_index}


def reconnect_notices(notices):
    """Inventory public notices without translating their wording into attempts."""
    result = []
    for notice in notices:
        message = notice.get("message")
        message = message.get("message") if isinstance(message, dict) else message
        if isinstance(message, str) and re.search(r"\breconnecting\b", message, re.IGNORECASE):
            result.append({**notice, "scope": "Internal reconnect notice within this native process",
                "underlying_http_attempts": None, "additional_unreported_usage": None})
    return result


def public_turns(raw, accepted_hash, attempt_id, warnings):
    """Associate public final messages and completions; ignore other item bodies."""
    turns, named, entries, threads, notices = [], {}, [], set(), []
    sidecar, sidecar_seen, finals = {}, set(), set()
    current = previous = None

    def new(identity=None, ordered=False):
        row = {"order": len(turns), "turn_id": identity, "ordered": ordered,
               "final_hashes": [], "entries": []}
        turns.append(row)
        if identity is not None:
            named[identity] = row
        return row

    for number, line in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            warnings.append({"attempt": attempt_id, "reason": "Malformed public JSON line", "line": number})
            continue
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        if kind == "thread.started":
            if isinstance(event.get("thread_id"), str) and event["thread_id"]:
                threads.add(event["thread_id"])
            continue
        if kind in {"error", "turn.failed"}:
            message = event.get("error", event.get("message"))
            notices.append({"line": number, "type": kind, "message": message})
            continue
        if kind not in {"turn.started", "turn.completed", "item.completed"}:
            continue
        identity = event.get("turn_id")
        identity = identity if isinstance(identity, str) and identity else None
        if kind == "turn.started":
            current = named.get(identity) if identity else None
            current = current or new(identity, True)
            current["ordered"] = True
            previous = None
            continue
        if kind == "item.completed":
            item = event.get("item")
            if (not isinstance(item, dict) or item.get("type") != "agent_message"
                    or item.get("phase") not in (None, "final", "final_answer")):
                continue
            message = item.get("text")
            if not isinstance(message, str) or not message.strip():
                continue
            message_hash = sha(message.encode("utf-8"))
            finals.add(message_hash)
            if identity is None and isinstance(item.get("turn_id"), str) and item["turn_id"]:
                identity = item["turn_id"]
            turn = named.get(identity) if identity else current
            if turn is None:
                turn = new(identity)
                current = turn
            turn["final_hashes"].append(message_hash)
            previous = None
            continue
        # The transport sidecar sums reported counters by its local turn ID.
        sidecar_id = event.get("turn_id")
        if sidecar_id is None or sidecar_id not in sidecar_seen:
            if sidecar_id is not None:
                sidecar_seen.add(sidecar_id)
            usage = event.get("usage") or {}
            if isinstance(usage, dict):
                add(sidecar, {key: usage[key] for key in SIDECAR_FIELDS
                    if type(usage.get(key)) is int and usage[key] >= 0})
        turn = named.get(identity) if identity else current
        turn = turn or new(identity)
        fingerprint = digest(event)
        identifier = next(((key, event[key]) for key in ("response_id", "turn_id", "id")
            if isinstance(event.get(key), str) and event[key]), None)
        if identifier is None and previous is not None and previous[0] == fingerprint:
            turn = previous[1]
        values, complete = counters(event.get("usage"))
        entry = {"values": values, "counter_complete": complete, "identity": identifier,
                 "fingerprint": fingerprint, "turn": turn, "duplicate": False,
                 "conflict": False, "line": number}
        turn["entries"].append(entry)
        entries.append(entry)
        current, previous = None, (fingerprint, turn)
    ambiguous = len(finals) > 1 or bool(accepted_hash and finals and accepted_hash not in finals)
    for turn in turns:
        turn["accepted_final_associated"] = bool(accepted_hash and not ambiguous
            and accepted_hash in turn["final_hashes"] and (turn["turn_id"] or turn["ordered"]))
    return {"turns": turns, "entries": entries, "thread_ids": sorted(threads),
            "ambiguous_final": ambiguous, "sidecar_expected": sidecar, "public_notices": notices}


def finalize_usage(rows):
    """Deduplicate strong response identities; keep conflicts and unattributed use partial."""
    seen, identity_rows = {}, []
    for row in rows:
        for entry in row["_public"]["entries"]:
            identity = entry["identity"]
            if identity:
                key = identity if identity[0] == "response_id" else (identity[0],
                    ("thread", row["thread_id"]) if row["thread_id"] else ("attempt", row["request"]), identity[1])
            else:
                key = ("ordered", row["request"], entry["turn"]["order"], entry["fingerprint"])
            entry["public_identity"] = key
            if key in seen:
                entry["duplicate"] = True
                if seen[key]["values"] != entry["values"]:
                    entry["conflict"] = seen[key]["conflict"] = True
            else:
                seen[key] = entry
    total, partial = {}, {}
    for row in rows:
        row.update(complete_token_usage={}, partial_token_usage={}, public_turns=[], public_usage_events=[])
        public = row.pop("_public")
        for turn in public["turns"]:
            usable = [entry for entry in turn["entries"] if entry["values"] and not entry["duplicate"]]
            complete = (turn["accepted_final_associated"] and len(usable) == 1
                        and usable[0]["counter_complete"] and not usable[0]["conflict"])
            for entry in usable:
                add(row["complete_token_usage"] if complete else row["partial_token_usage"], entry["values"])
            row["public_turns"].append({"turn_id": turn["turn_id"], "order": turn["order"],
                "accepted_final_associated": turn["accepted_final_associated"],
                "substantive_final_count": len(turn["final_hashes"]),
                "usage_completeness": "complete" if complete else "partial" if usable else "unknown"})
        for entry in public["entries"]:
            record = {key: entry[key] for key in ("public_identity", "line", "values", "counter_complete", "duplicate", "conflict")}
            row["public_usage_events"].append(record)
            if not entry["duplicate"]:
                identity_rows.append({"request": row["request"], **record})
        row["duplicate_usage_events"] = sum(entry["duplicate"] for entry in public["entries"])
        row["usage_known"] = bool(row["public_turns"] and row["exit_confirmed"] and not row["ambiguous_final"]
            and all(turn["usage_completeness"] == "complete" for turn in row["public_turns"]))
        row["usage_completeness"] = ("complete" if row["usage_known"] else "partial"
            if row["complete_token_usage"] or row["partial_token_usage"] else "unknown")
        row["unreported_counter_fields"] = sorted(set(FIELDS) - set().union(
            *(entry["values"].keys() for entry in public["entries"])))
        add(total, row["complete_token_usage"])
        add(partial, row["partial_token_usage"])
    return total, partial, identity_rows


def attempt_record(run, marker, warnings, issues, closed):
    attempt, owner = marker.parent, marker.parent.parent
    relative = attempt.relative_to(run).as_posix()
    stage = owner.parent.relative_to(run / "transport").as_posix()
    request, accepted = read(owner / "request.json", warnings), read(owner / "accepted.json", warnings)
    process, started, pid = (read(attempt / name, warnings) for name in ("process.json", "started.json", "pid.json"))
    flags = classify(stage, request.get("logical_call"), attempt.name)
    answer_path = owner / "answer.txt"
    answer = answer_path.read_bytes() if answer_path.is_file() else None
    answer_hash = sha(answer) if answer and answer.strip() else None
    accepted_here = answer_hash is not None and accepted.get("attempt") == flags["network_attempt_index"]
    if answer_hash and accepted.get("answer_sha256") != answer_hash:
        issues.append(relative + ": accepted answer digest is absent or differs")
        accepted_here = False
    raw = (attempt / "stdout.jsonl").read_bytes() if (attempt / "stdout.jsonl").is_file() else b""
    public = public_turns(raw, answer_hash if accepted_here else None, relative, warnings)
    native = (True if type(pid.get("pid")) is int and pid["pid"] > 0 else
              False if process.get("status") == "launch_error" else None)
    row = {"request": relative, "stage": stage, "logical_request": owner.relative_to(run).as_posix(),
        "logical_call": request.get("logical_call"), **flags, "pid": pid.get("pid"),
        "request_runtime": request.get("runtime"),
        "native_process_started": native, "started_at": started.get("started_at"),
        "finished_at": process.get("finished_at"), "process_status": process.get("status"),
        "returncode": process.get("returncode"), "exit_confirmed": process.get("exited") is True,
        "elapsed_seconds": process.get("elapsed_seconds"), "thread_ids": public["thread_ids"],
        "thread_id": public["thread_ids"][0] if len(public["thread_ids"]) == 1 else None,
        "accepted_answer_present": accepted_here, "ambiguous_final": public["ambiguous_final"],
        "stdout_sha256": sha(raw), "stdout_bytes": len(raw), "public_notices": public["public_notices"],
        "internal_reconnect_notices": reconnect_notices(public["public_notices"]),
        "_public": public}
    row["receipt_sha256"] = {name: file_sha(attempt / name) for name in
        ("started.json", "pid.json", "process.json", "launch.json", "usage.json", "last-message.txt")}
    row["receipt_sha256"].update({"../" + name: file_sha(owner / name)
                                 for name in ("request.json", "accepted.json", "answer.txt")})
    duration = row["elapsed_seconds"]
    if type(duration) not in (int, float) or not math.isfinite(duration) or duration < 0:
        row["elapsed_seconds"] = None
    sidecar = read(attempt / "usage.json", warnings)
    row["usage_sidecar"] = sidecar or None
    row["usage_sidecar_matches_public_counters"] = (sidecar.get("usage") == public["sidecar_expected"]
        and sidecar.get("known") is bool(public["sidecar_expected"])) if sidecar else None
    if sidecar and not row["usage_sidecar_matches_public_counters"]:
        issues.append(relative + ": public usage sidecar differs from raw events")
    delivery = owner / "prompt.txt"
    launch = read(attempt / "launch.json", warnings)
    delivery_hash = file_sha(delivery)
    row["delivery_sha256"] = delivery_hash
    if delivery_hash != request.get("delivery_sha256") or delivery_hash != launch.get("stdin_sha256"):
        issues.append(relative + ": delivered prompt binding differs")
    owner_stage = run / stage if stage in {"task", "revision/task", "review", "revision/review"} else run / "steps" / stage
    logical = request.get("logical_call")
    call_path = (owner_stage / logical).resolve() if isinstance(logical, str) else None
    if call_path is None or not call_path.is_relative_to(owner_stage.resolve()):
        issues.append(relative + ": missing or unsafe logical call reference")
    else:
        call = read(call_path, warnings)
        row["logical_call_record"] = call_path.relative_to(run).as_posix()
        prompt = call.get("prompt")
        row["logical_core_sha256"] = sha(prompt.encode("utf-8")) if isinstance(prompt, str) else None
        row["logical_canonical_prompt_sha256"] = digest(prompt) if isinstance(prompt, str) else None
        if (row["logical_core_sha256"] != request.get("core_sha256")
                or row["logical_canonical_prompt_sha256"] != call.get("prompt_sha256")):
            issues.append(relative + ": durable logical prompt identity differs")
    if flags["network_attempt_index"] is None or flags["network_attempt_index"] > request.get("network_retries", 2) + 1:
        issues.append(relative + ": network attempt index exceeds its saved budget")
    if flags["logical_attempt_index"] is None or flags["logical_attempt_index"] > 2:
        issues.append(relative + ": structural correction index is missing or exceeds the authorized budget")
    row["launch_command_sha256"] = digest(launch.get("command"))
    row["launch_command"] = launch.get("command")
    if closed and not row["exit_confirmed"]:
        warnings.append({"attempt": relative, "reason": "No confirmed process exit in closed controller receipts"})
    return row


def provenance(run, prepared, protocol, issues):
    snapshot = read(run / "implementation-snapshot/snapshot.json")
    inventory = snapshot["files"]
    frozen_changes = [name for name, expected in inventory.items()
        if file_sha(bound(run / "implementation-snapshot", name)) != expected]
    current_changes = [name for name, expected in inventory.items() if file_sha(bound(PROJECT, name)) != expected]
    current_names = set()
    for base, extension in ((PROJECT / "src/skillflow", ".py"), (PROJECT / "formal", ".lean")):
        for directory, folders, files in os.walk(base):
            folders[:] = [folder for folder in folders if folder not in {".lake", "__pycache__"}]
            current_names.update((Path(directory) / name).relative_to(PROJECT).as_posix()
                                 for name in files if name.endswith(extension))
    current_names.update(("formal/lakefile.toml", "formal/lean-toolchain"))
    current_hash = digest({name: file_sha(PROJECT / name) for name in sorted(current_names)})
    required = current_names | {"tools/doe/document_guided_client.py", "tools/doe/document_guided_metrics.py",
        "tools/doe/document_guided_pilot.py", "formal/.lake/build/bin/skill_ir_retell.exe"}
    unpinned = sorted(required - set(inventory))
    helpers = {name: file_sha(run / name) == snapshot.get(field) for name, field in
        (("controller.py", "controller_sha256"), ("local_timing.py", "local_timing_sha256"))}
    executables = {field: file_sha(Path(protocol[field])) == protocol[field + "_sha256"]
                   for field in ("cli_executable", "renderer_executable")}
    if (frozen_changes or current_changes or unpinned or not all(helpers.values()) or not all(executables.values())
            or current_hash != protocol["implementation_sha256"] or current_hash != snapshot["implementation_sha256"]):
        issues.append("Frozen/current implementation, helpers, transport or executable binding differs")
    source = read(run / "source/inputs/snapshot.json")
    package = run / "source/inputs/package"
    actual = {path.relative_to(package).as_posix(): file_sha(path) for path in package.rglob("*") if path.is_file()}
    expected = {item["path"]: item["raw_sha256"] for item in source["files"]}
    source_changes = sorted(name for name in set(actual) | set(expected) if actual.get(name) != expected.get(name))
    decoded, raw_inventory = [], []
    for item in source["files"]:
        path = bound(package, item["path"])
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if len(raw) != item["size"]:
            source_changes.append(item["path"] + ":size")
        raw_inventory.append({"path": item["path"], "size": len(raw), "raw_sha256": sha(raw)})
        if item["decoded_sha256"] is not None:
            try:
                content_hash = sha(raw.decode("utf-8-sig").encode("utf-8"))
            except UnicodeDecodeError:
                content_hash = None
            decoded.append({"path": item["path"], "sha256": content_hash})
            if content_hash != item["decoded_sha256"]:
                source_changes.append(item["path"] + ":decoded")
    source_hash = digest(decoded)
    staged = Path(prepared["source_staging"])
    staged_inventory = {path.relative_to(staged).as_posix(): file_sha(path)
                        for path in staged.rglob("*") if path.is_file()}
    staged_changes = sorted(name for name in set(actual) | set(staged_inventory)
                            if actual.get(name) != staged_inventory.get(name))
    if (source_changes or staged_changes or actual != protocol["source_file_sha256"]
            or source_hash != protocol["source_sha256"] or source_hash != prepared["source_sha256"]
            or source_hash != source["source_sha256"]
            or digest(raw_inventory) != source["package_bytes_sha256"]
            or digest({k: v for k, v in source.items() if k != "snapshot_sha256"}) != source["snapshot_sha256"]):
        issues.append("Frozen/staged source bytes, decoded identity or snapshot digest differs")
    return {"implementation_sha256": current_hash, "pinned_files_checked": len(inventory),
        "snapshot_sha256": file_sha(run / "implementation-snapshot/snapshot.json"),
        "frozen_changes": frozen_changes, "current_changes": current_changes, "unpinned_current_files": unpinned,
        "helpers_match": helpers, "executables_match": executables, "source_sha256": source_hash,
        "source_files_checked": len(actual), "source_changes": source_changes, "staged_source_changes": staged_changes,
        "historical_answers_read": False, "source_donor_content_read": False}


def audit(case, prepared):
    run = Path(prepared["run_directory"]).resolve()
    if not run.is_relative_to(PROJECT / "experiments/doe/runs"):
        raise ValueError("Prepared run is outside this workspace")
    issues, warnings = [], []
    before = read(run / "controller-finished.json", warnings)
    closed = bool(before)
    protocol = read(run / "run-protocol.json")
    manifest = read(run / "manifest.json")
    protocol_checks = {
        "case_identity": protocol.get("case_id") == case,
        "runtime": protocol.get("runtime") == {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai"},
        "seven_calls_two_workers": protocol.get("normal_semantic_requests") == 7 and protocol.get("workers") == 2,
        "existing_repair_budgets": protocol.get("semantic_repairs") == 1 and protocol.get("structural_corrections_per_stage") == 1,
        "manifest_seal": digest({k: v for k, v in manifest.items() if k != "manifest_sha256"}) == manifest.get("manifest_sha256"),
        "manifest_implementation": manifest.get("implementation", {}).get("sha256") == protocol.get("implementation_sha256"),
    }
    if not all(protocol_checks.values()):
        issues.append("Prepared protocol or manifest differs from the authorized batch")
    markers = sorted((run / "transport").rglob("started.json"))
    rows = [attempt_record(run, marker, warnings, issues, closed) for marker in markers]
    rejected_inputs = [{"request": path.parent.relative_to(run).as_posix(), **read(path, warnings)}
                       for path in sorted((run / "transport").rglob("input-rejection.json"))]
    for row in rows:
        command = row["launch_command"] or []
        configuration = [command[index + 1] for index, item in enumerate(command[:-1]) if item == "-c"]
        checks = (row["request_runtime"] == {"model": "gpt-6.1-sol", "effort": "high", "provider": "openai"}
            and command and Path(command[0]).resolve() == Path(protocol["cli_executable"]).resolve()
            and "exec" in command and "resume" not in command and "--ignore-user-config" in command
            and "--ignore-rules" in command and 'model_reasoning_effort="high"' in configuration
            and 'model_provider="openai"' in configuration)
        row["launch_runtime_matches_protocol"] = bool(checks)
        if not checks:
            issues.append(row["request"] + ": native launch/runtime differs from the saved protocol")
    complete, partial, identities = finalize_usage(rows)
    internal_reconnects = [{"request": row["request"], "pid": row["pid"], "thread_id": row["thread_id"],
                           **notice} for row in rows for notice in row["internal_reconnect_notices"]]
    metric = read(run / "metrics.json", warnings)
    count = {"launch_attempt_markers": len(rows), "native_process_starts": sum(row["native_process_started"] is True for row in rows),
        "launch_errors_without_confirmed_pid": sum(row["native_process_started"] is False for row in rows),
        "unknown_native_process_starts": sum(row["native_process_started"] is None for row in rows),
        "logical_requests": len({row["logical_request"] for row in rows}),
        "network_retry_attempts": sum((row["network_attempt_index"] or 0) > 1 for row in rows),
        "complete_usage_requests": sum(row["usage_known"] for row in rows),
        "partial_usage_requests": sum(row["usage_completeness"] == "partial" for row in rows),
        "unknown_usage_requests": sum(not row["usage_known"] for row in rows),
        "no_public_usage_requests": sum(row["usage_completeness"] == "unknown" for row in rows),
        "inputs_rejected_before_start": sum(row.get("status") == "input_too_large" and row.get("process_started") is False
                                             for row in rejected_inputs),
        "internal_reconnect_notice_events": len(internal_reconnects)}
    starts = [timestamp(row["started_at"]) for row in rows if timestamp(row["started_at"]) is not None]
    finishes = [timestamp(row["finished_at"]) for row in rows if timestamp(row["finished_at"]) is not None]
    timing = {"known_request_seconds": sum(row["elapsed_seconds"] or 0 for row in rows),
              "unknown_duration_requests": sum(row["elapsed_seconds"] is None for row in rows),
              "wall_clock_seconds": max(finishes) - min(starts) if starts and finishes else None}
    groups = defaultdict(lambda: {"launch_attempts": 0, "pid_confirmed_starts": 0, "complete_token_usage": {}, "partial_token_usage": {}})
    for row in rows:
        group = groups[row["category"]]
        group["launch_attempts"] += 1
        group["pid_confirmed_starts"] += row["native_process_started"] is True
        add(group["complete_token_usage"], row["complete_token_usage"])
        add(group["partial_token_usage"], row["partial_token_usage"])
    comparisons = []
    if metric.get("requests") is not None:
        expected_rows = {row["request"]: row for row in metric["requests"]}
        checks = {**{key: count[key] for key in ("native_process_starts", "unknown_native_process_starts", "logical_requests",
            "network_retry_attempts", "complete_usage_requests", "partial_usage_requests", "unknown_usage_requests", "inputs_rejected_before_start")},
            **timing, "launch_attempts": len(rows), "known_token_usage": complete, "partial_token_usage": partial}
        for key, observed in checks.items():
            comparisons.append({"field": key, "matches": metric.get(key) == observed,
                                "saved": metric.get(key), "observed": observed})
        comparisons.append({"field": "request_inventory", "matches": set(expected_rows) == {row["request"] for row in rows}})
        for row in rows:
            other = expected_rows.get(row["request"], {})
            for key in ("complete_token_usage", "partial_token_usage", "thread_id", "usage_completeness",
                        "duplicate_usage_events", "native_process_started", "structural_correction"):
                comparisons.append({"request": row["request"], "field": key, "matches": other.get(key) == row[key]})
        if closed and any(not row["matches"] for row in comparisons):
            issues.append("Saved metrics disagree with independently read public records")
    elif closed:
        warnings.append({"reason": "Closed controller has no usable metrics; independent counters remain available"})
    replay = read(run / "replay-check.json", warnings)
    replay_start = read(run / "replay-started.json", warnings)
    boundary = timestamp(replay_start.get("started_at"))
    after_replay = [row["request"] for row in rows if boundary is not None
        and timestamp(row["started_at"]) is not None and timestamp(row["started_at"]) >= boundary]
    unknown_start_times = [row["request"] for row in rows if timestamp(row["started_at"]) is None]
    zero_replay = bool(replay_start.get("maximum_replays") == 1 and boundary is not None and not after_replay and not unknown_start_times
                      and replay.get("new_native_markers") == 0 and replay == before.get("replay"))
    if closed and not zero_replay:
        issues.append("A recorded sole replay with zero new launch markers is not established")
    binding = provenance(run, prepared, protocol, issues)
    stable = (before == read(run / "controller-finished.json", warnings)
              and markers == sorted((run / "transport").rglob("started.json")))
    final = closed and stable
    status = ("provisional" if not final else "discrepancies_found" if issues else
              "verified_with_usage_limitations" if count["unknown_usage_requests"] else "verified")
    return {"schema_version": "skillflow-public-cost-provenance-audit-v1", "case_id": case, "run_directory": str(run),
        "audit_utility_sha256": file_sha(Path(__file__)),
        "observed_at": stamp(), "status": status, "final_observation": final, "inventory_stable_during_audit": stable,
        "controller_status": before.get("status"), "controller_finished": before or None,
        "protocol_checks": protocol_checks, "protocol_sha256": file_sha(run / "run-protocol.json"),
        "scope": "Saved public output, counters and file hashes only; no analysis, replay, subprocess, Skill or private-session access.",
        "counts": count, "known_public_usage": complete, "partial_public_usage": partial,
        "input_rejections": rejected_inputs, "timing": {**timing,
            "analysis_seconds_recorded": before.get("analysis_seconds"),
            "notice": "Request durations can overlap and are not added to controller wall time. Missing durations remain unknown."},
        "usage_notice": "Missing counters are unknown, not zero. Total is input plus output; cache/reasoning counters are subsets. Public counters do not establish provider billing or internal HTTP attempts.",
        "http_attempts": None, "provider_billing_cost": None, "categories": dict(groups), "requests": rows,
        "internal_reconnect_notices": internal_reconnects,
        "internal_reconnect_notice": "These are observed public event messages within native processes, separate from outer launch retries. Message ordinals such as 2/5 do not establish HTTP attempt counts, extra native starts, or additional token usage; unreported usage remains unknown.",
        "unique_public_usage_identities": identities, "metrics_comparisons": comparisons,
        "metrics_sha256": file_sha(run / "metrics.json"), "replay": {"receipt": replay or None,
            "recorded_maximum_replays": replay_start.get("maximum_replays"), "zero_new_launch_markers_established": zero_replay,
            "markers_at_or_after_replay": after_replay, "unknown_start_timestamps": unknown_start_times},
        "provenance": binding, "issues": issues, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", nargs="*", choices=["ga4", "001", "010", "013"])
    parser.add_argument("--write", action="store_true", help="Create uniquely named reports beside this utility; never change run files")
    args = parser.parse_args()
    queue = read(VERIFY / "prepared-runs.json")
    inventory = {row["case_id"]: row for row in queue["run_order"]}
    for case in args.cases or list(inventory):
        report = audit(case, inventory[case])
        if args.write:
            destination = VERIFY / "cost-provenance-audit"
            destination.mkdir(exist_ok=True)
            name = case + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json"
            with (destination / name).open("x", encoding="utf-8") as handle:
                json.dump(report, handle, indent=2, ensure_ascii=False, allow_nan=False)
                handle.write("\n")
            print(json.dumps({"case_id": case, "status": report["status"], "final": report["final_observation"],
                "counts": report["counts"], "issues": report["issues"], "report": str(destination / name)}))
        else:
            print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
