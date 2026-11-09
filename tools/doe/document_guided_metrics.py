"""Passive public-output accounting for current document-guided CLI attempts.

This module creates no client and reads no hidden session or reasoning records.
An available counter is not necessarily the cost of the accepted final answer.
Missing/ambiguous attribution stays partial or unknown and never gates analysis.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re


FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens",
          "reasoning_output_tokens", "total_tokens")


def _read(path, warnings):
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_bytes().decode("utf-8"))
        if isinstance(value, dict):
            return value
        warnings.append("Non-object monitoring record: " + str(path))
    except (OSError, ValueError) as error:
        warnings.append("Unavailable monitoring record: " + str(path) + ": " + str(error))
    return {}


def _text(path, warnings):
    try:
        return path.read_bytes().decode("utf-8") if path.is_file() else None
    except (OSError, ValueError) as error:
        warnings.append("Unavailable public output: " + str(path) + ": " + str(error))
        return None


def _add(target, values):
    for key, value in values.items():
        target[key] = target.get(key, 0) + value


def _counters(value):
    if not isinstance(value, dict):
        return {}, False
    result = {key: value[key] for key in FIELDS if type(value.get(key)) is int and value[key] >= 0}
    complete = all(key in result for key in ("input_tokens", "output_tokens"))
    if complete:
        total = result["input_tokens"] + result["output_tokens"]
        if "total_tokens" in result and result["total_tokens"] != total:
            complete = False
        else:
            result["total_tokens"] = total
        if result.get("cached_input_tokens", 0) > result["input_tokens"]:
            complete = False
        if result.get("reasoning_output_tokens", 0) > result["output_tokens"]:
            complete = False
    return result, complete


def _request_owner(attempt, root):
    for parent in (attempt, *attempt.parents):
        if (parent / "request.json").is_file():
            return parent
        if parent == root:
            break
    return None


def _accepted_answer(attempt, root, warnings):
    owner = _request_owner(attempt, root)
    if owner is None:
        return None, None, {}
    request = _read(owner / "request.json", warnings)
    accepted = _read(owner / "accepted.json", warnings)
    answer = _text(owner / "answer.txt", warnings)
    if answer is None or not answer.strip():
        return None, owner, request
    if accepted.get("answer_sha256") is not None and accepted["answer_sha256"] != hashlib.sha256(answer.encode()).hexdigest():
        warnings.append("Accepted-answer identity differs: " + str(owner))
        return None, owner, request
    if type(accepted.get("attempt")) is int and attempt.name.startswith("attempt-"):
        try:
            if int(attempt.name.removeprefix("attempt-")) != accepted["attempt"]:
                return None, owner, request
        except ValueError:
            return None, owner, request
    return answer, owner, request


def _public_turns(attempt, answer, warnings):
    """Associate public final messages and completion usage by IDs or turn order."""
    text = _text(attempt / "stdout.jsonl", warnings)
    turns, named, entries, current, previous_completion = [], {}, [], None, None
    thread_ids = set()
    substantive = set()

    def make_turn(identity=None, ordered=False):
        turn = {"index": len(turns), "id": identity, "ordered": ordered,
                "finals": [], "entries": [], "closed": False}
        turns.append(turn)
        if identity is not None:
            named[identity] = turn
        return turn

    for line_number, line in enumerate((text or "").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            warnings.append(f"Malformed public stdout line {line_number}: {attempt}")
            continue
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        if event_type == "thread.started":
            thread_id = event.get("thread_id")
            if isinstance(thread_id, str) and thread_id:
                thread_ids.add(thread_id)
            continue
        # Ignore other item bodies, including reasoning, rather than inspecting them.
        if event_type not in {"turn.started", "turn.completed", "item.completed"}:
            continue
        identity = event.get("turn_id")
        identity = identity if isinstance(identity, str) and identity else None
        if event_type == "turn.started":
            current = named.get(identity) if identity else None
            if current is None:
                current = make_turn(identity, ordered=True)
            else:
                current["ordered"] = True
            previous_completion = None
            continue
        if event_type == "item.completed":
            item = event.get("item")
            if (not isinstance(item, dict) or item.get("type") != "agent_message"
                    or item.get("phase") not in (None, "final", "final_answer")):
                continue
            final = item.get("text")
            if not isinstance(final, str) or not final.strip():
                continue
            substantive.add(final)
            item_turn = item.get("turn_id")
            if identity is None and isinstance(item_turn, str) and item_turn:
                identity = item_turn
            turn = named.get(identity) if identity else current
            if turn is None:
                turn = make_turn(identity)
                current = turn
            turn["finals"].append(final)
            previous_completion = None
            continue
        turn = named.get(identity) if identity else current
        if turn is None:
            turn = make_turn(identity)
        counters, complete = _counters(event.get("usage"))
        identifier = next(((name, event[name]) for name in ("response_id", "turn_id", "id")
                           if isinstance(event.get(name), str) and event[name]), None)
        fingerprint = json.dumps(event, sort_keys=True, ensure_ascii=False)
        if identifier is None and previous_completion is not None and fingerprint == previous_completion[0]:
            # An exact consecutive completion notification without a new turn
            # is a duplicate, not an additional inferred model invocation.
            turn = previous_completion[1]
        entry = {"values": counters, "counter_complete": complete,
                 "identity": identifier, "fingerprint": fingerprint,
                 "turn": turn, "duplicate": False, "conflict": False}
        entries.append(entry)
        turn["entries"].append(entry)
        turn["closed"] = True
        current, previous_completion = None, (fingerprint, turn)
    ambiguous_final = len(substantive) > 1 or (answer is not None and substantive and answer not in substantive)
    thread_id = next(iter(thread_ids)) if len(thread_ids) == 1 else None
    if len(thread_ids) > 1:
        warnings.append("Multiple public thread identities; usage IDs stay attempt-scoped: " + str(attempt))
    for turn in turns:
        associated = (answer is not None and not ambiguous_final and answer in turn["finals"]
                      and (turn["id"] is not None or turn["ordered"]))
        turn["accepted_final_associated"] = associated
    return turns, entries, ambiguous_final, thread_id


def _timestamp(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() if isinstance(value, str) else None
    except (ValueError, OverflowError, OSError):
        return None


def transport_metrics(run_dir):
    """Return per-attempt counters and timing; no monitoring failure rejects work."""
    root, warnings, rows, all_entries = Path(run_dir).resolve(), [], [], []
    rejections = []
    for path in sorted((root / "transport").rglob("input-rejection.json")):
        value = _read(path, warnings)
        if value.get("status") == "input_too_large" and value.get("process_started") is False:
            rejections.append({"request": path.parent.relative_to(root).as_posix(), **value})
    try:
        started_files = sorted((root / "transport").rglob("started.json"))
    except OSError as error:
        started_files = []
        warnings.append("Transport inventory unavailable: " + str(error))
    for started_path in started_files:
        attempt = started_path.parent
        local_warnings = []
        started, process = _read(started_path, local_warnings), _read(attempt / "process.json", local_warnings)
        pid = _read(attempt / "pid.json", local_warnings).get("pid")
        answer, owner, request = _accepted_answer(attempt, root, local_warnings)
        turns, entries, ambiguous, thread_id = _public_turns(attempt, answer, local_warnings)
        elapsed = process.get("elapsed_seconds")
        elapsed = elapsed if type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0 else None
        row = {"request": attempt.relative_to(root).as_posix(),
               "logical_call": request.get("logical_call"),
               "logical_request": owner.relative_to(root).as_posix() if owner is not None else None,
               "started_at": started.get("started_at"), "finished_at": process.get("finished_at"),
               "elapsed_seconds": elapsed, "process_status": process.get("status"),
               "exit_confirmed": process.get("exited") is True,
               "thread_id": thread_id,
               "native_process_started": (True if type(pid) is int and pid > 0 else
                                          False if process.get("status") == "launch_error" else None),
               "accepted_answer_present": answer is not None, "ambiguous_final": ambiguous,
               "public_turns": [], "complete_token_usage": {}, "partial_token_usage": {},
               "duplicate_usage_events": 0, "monitor_warnings": local_warnings}
        native_index = re.fullmatch(r"attempt-(\d+)", attempt.name)
        logical_index = re.search(r"(?:^|/)a(\d+)/call\.json$", request.get("logical_call") or "")
        row["network_attempt_index"] = int(native_index[1]) if native_index else None
        row["logical_attempt_index"] = int(logical_index[1]) if logical_index else None
        row["structural_correction"] = bool(logical_index and int(logical_index[1]) > 1)
        row["_turns"], row["_entries"] = turns, entries
        for entry in entries:
            entry["owner"] = row
            all_entries.append(entry)
        rows.append(row)
    seen = {}
    for entry in all_entries:
        row, identity = entry["owner"], entry["identity"]
        # Only response IDs are globally strong. Local turn/event IDs require
        # their observed thread, or stay inside this one native attempt.
        if identity is not None:
            key = identity if identity[0] == "response_id" else (
                identity[0], ("thread", row["thread_id"]) if row["thread_id"] is not None
                else ("attempt", row["request"]), identity[1])
        else:
            key = ("ordered", row["request"], entry["turn"]["index"], entry["fingerprint"])
        if key in seen:
            prior = seen[key]
            entry["duplicate"] = True
            row["duplicate_usage_events"] += 1
            if prior["values"] != entry["values"]:
                prior["conflict"] = entry["conflict"] = True
                warnings.append("Conflicting public usage values for one ID: " + repr(identity))
        else:
            seen[key] = entry
    complete_usage, partial_usage, starts, finishes = {}, {}, [], []
    for row in rows:
        turns, entries = row.pop("_turns"), row.pop("_entries")
        for turn in turns:
            usable = [entry for entry in turn["entries"] if entry["values"] and not entry["duplicate"]]
            full = (turn["accepted_final_associated"] and len(usable) == 1
                    and usable[0]["counter_complete"] and not usable[0]["conflict"])
            for entry in usable:
                _add(row["complete_token_usage"] if full else row["partial_token_usage"], entry["values"])
            row["public_turns"].append({"turn_id": turn["id"], "order": turn["index"],
                "accepted_final_associated": turn["accepted_final_associated"],
                "substantive_final_count": len(turn["finals"]),
                "usage_completeness": "complete" if full else "partial" if usable else "unknown"})
        full_attempt = (bool(row["public_turns"]) and all(
            turn["usage_completeness"] == "complete" for turn in row["public_turns"])
            and row["exit_confirmed"] and not row["ambiguous_final"])
        available = bool(row["complete_token_usage"] or row["partial_token_usage"])
        row["usage_completeness"] = "complete" if full_attempt else "partial" if available else "unknown"
        row["usage_known"] = full_attempt
        _add(complete_usage, row["complete_token_usage"])
        _add(partial_usage, row["partial_token_usage"])
        start, finish = _timestamp(row["started_at"]), _timestamp(row["finished_at"])
        if start is not None:
            starts.append(start)
        if finish is not None:
            finishes.append(finish)
        warnings.extend(row["monitor_warnings"])
    return {"cli_dispatches": len(rows), "known_token_usage": complete_usage,
            "launch_attempts": len(rows),
            "cli_dispatches_scope": "Recorded launch-attempt markers, not proof that Popen started a process",
            "native_process_starts": sum(row["native_process_started"] is True for row in rows),
            "inputs_rejected_before_start": len(rejections),
            "input_rejections": rejections,
            "unknown_native_process_starts": sum(row["native_process_started"] is None for row in rows),
            "logical_requests": len({row["logical_request"] for row in rows if row["logical_request"] is not None}),
            "network_retry_attempts": sum((row["network_attempt_index"] or 0) > 1 for row in rows),
            "partial_token_usage": partial_usage,
            "complete_usage_requests": sum(row["usage_known"] for row in rows),
            "partial_usage_requests": sum(row["usage_completeness"] == "partial" for row in rows),
            "unknown_usage_requests": sum(not row["usage_known"] for row in rows),
            "total_usage_known": all(row["usage_known"] for row in rows),
            "known_request_seconds": sum(row["elapsed_seconds"] or 0 for row in rows),
            "unknown_duration_requests": sum(row["elapsed_seconds"] is None for row in rows),
            "wall_clock_seconds": max(finishes) - min(starts) if starts and finishes else None,
            "wall_clock_scope": "Earliest public native start to latest recorded native finish, including gaps and overlap",
            "requests": rows, "http_attempts": None, "monitor_warnings": warnings,
            "notice": "Complete usage is tied to an accepted substantive final by public turn identity/order. "
                      "Other available counters stay partial. Reasoning/cache are subsets, never extra totals. "
                      "Missing usage, native HTTP counts and unclosed turns remain unknown; analysis is never gated."}
