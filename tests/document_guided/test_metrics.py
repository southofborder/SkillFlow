"""Passive accounting uses public events only; fixtures never start a process."""
import hashlib
import json
from pathlib import Path

from tools.doe.document_guided_metrics import transport_metrics


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def final(text, turn=None):
    value = {"type": "item.completed", "item": {"type": "agent_message", "text": text}}
    if turn:
        value["turn_id"] = turn
    return value


def completed(usage, turn=None):
    value = {"type": "turn.completed", "usage": usage}
    if turn:
        value["turn_id"] = turn
    return value


def attempt(root, events, *, stage="graph", call=1, native=1, answer="answer", accepted=True,
            elapsed=2.5, start="2026-10-28T00:00:00+00:00", end="2026-10-28T00:00:02.500000+00:00"):
    request = root / "transport" / stage / f"request-{call}"
    directory = request / f"attempt-{native:03d}"
    write(request / "request.json", {"logical_call": f"calls/a{call:03d}/call.json"})
    write(directory / "started.json", {"started_at": start})
    write(directory / "pid.json", {"pid": 23456})
    write(directory / "process.json", {"status": "exited", "exited": True, "returncode": 0,
        "elapsed_seconds": elapsed, "finished_at": end})
    (directory / "stdout.jsonl").write_text("\n".join(json.dumps(row) for row in events), encoding="utf-8")
    if accepted:
        (request / "answer.txt").write_text(answer, encoding="utf-8")
        write(request / "accepted.json", {"answer_sha256": hashlib.sha256(answer.encode()).hexdigest(), "attempt": native})
    # This intentionally lies: final completeness must come from raw events.
    write(directory / "usage.json", {"known": True, "usage": {"total_tokens": 999999}})
    return directory


def test_public_turn_order_associates_final_and_keeps_subsets_out_of_total(tmp_path):
    attempt(tmp_path, [{"type": "turn.started"}, final("answer"), completed({
        "input_tokens": 10, "output_tokens": 5, "cached_input_tokens": 6, "reasoning_output_tokens": 2})])
    result = transport_metrics(tmp_path)
    assert result["cli_dispatches"] == result["complete_usage_requests"] == 1
    assert result["unknown_usage_requests"] == 0 and result["total_usage_known"]
    assert result["known_token_usage"] == {"input_tokens": 10, "output_tokens": 5,
        "cached_input_tokens": 6, "reasoning_output_tokens": 2, "total_tokens": 15}
    assert result["partial_token_usage"] == {}


def test_complete_answer_with_missing_usage_and_later_empty_tail_usage_stays_partial(tmp_path):
    attempt(tmp_path, [{"type": "turn.started", "turn_id": "answer-turn"}, final("answer", "answer-turn"),
        {"type": "turn.started", "turn_id": "tail-turn"}, final("", "tail-turn"),
        completed({"input_tokens": 133857, "output_tokens": 194, "cached_input_tokens": 133632}, "tail-turn")])
    result = transport_metrics(tmp_path)
    assert not result["total_usage_known"] and result["unknown_usage_requests"] == 1
    assert result["known_token_usage"] == {}
    assert result["partial_token_usage"]["output_tokens"] == 194
    assert result["requests"][0]["public_turns"][0]["usage_completeness"] == "unknown"
    assert result["requests"][0]["public_turns"][1]["usage_completeness"] == "partial"


def test_only_cached_usage_is_partial_even_with_final_and_claimed_known_flag(tmp_path):
    attempt(tmp_path, [{"type": "turn.started"}, final("answer"), completed({"cached_input_tokens": 8})])
    result = transport_metrics(tmp_path)
    assert result["known_token_usage"] == {} and result["partial_token_usage"] == {"cached_input_tokens": 8}
    assert result["partial_usage_requests"] == result["unknown_usage_requests"] == 1


def test_missing_association_or_last_message_only_does_not_invent_final_usage(tmp_path):
    attempt(tmp_path, [final("answer"), completed({"input_tokens": 10, "output_tokens": 5})], stage="unbounded")
    directory = attempt(tmp_path, [{"type": "turn.started"}, completed({"input_tokens": 20, "output_tokens": 5})], stage="fallback")
    (directory / "last-message.txt").write_text("answer", encoding="utf-8")
    result = transport_metrics(tmp_path)
    assert result["complete_usage_requests"] == 0 and result["partial_usage_requests"] == 2
    assert result["partial_token_usage"]["total_tokens"] == 40


def test_explicit_turn_identity_associates_without_a_started_notification(tmp_path):
    attempt(tmp_path, [final("answer", "t1"), completed({"input_tokens": 10, "output_tokens": 5}, "t1")])
    assert transport_metrics(tmp_path)["total_usage_known"]


def test_duplicate_ids_within_and_across_attempts_do_not_duplicate_cost(tmp_path):
    usage = completed({"input_tokens": 10, "output_tokens": 5}, "same-turn")
    usage["response_id"] = "globally-identical-response"
    events = [{"type": "turn.started", "turn_id": "same-turn"}, final("answer", "same-turn"), usage, usage]
    attempt(tmp_path, events, stage="first")
    attempt(tmp_path, events, stage="copied")
    result = transport_metrics(tmp_path)
    assert result["cli_dispatches"] == 2
    assert result["known_token_usage"]["total_tokens"] == 15
    assert result["partial_token_usage"] == {}
    assert sum(row["duplicate_usage_events"] for row in result["requests"]) == 3


def test_equal_local_turn_ids_from_unrelated_attempts_are_not_globally_merged(tmp_path):
    events = [final("answer", "turn_0"), completed({"input_tokens": 10, "output_tokens": 5}, "turn_0")]
    attempt(tmp_path, events, stage="without-thread-first")
    attempt(tmp_path, events, stage="without-thread-second")
    attempt(tmp_path, [{"type": "thread.started", "thread_id": "thread-A"}, *events], stage="thread-first")
    attempt(tmp_path, [{"type": "thread.started", "thread_id": "thread-B"}, *events], stage="thread-second")
    result = transport_metrics(tmp_path)
    assert result["known_token_usage"]["total_tokens"] == 60
    assert result["complete_usage_requests"] == 4
    assert sum(row["duplicate_usage_events"] for row in result["requests"]) == 0


def test_same_explicit_thread_and_turn_identity_deduplicates_copied_notifications(tmp_path):
    events = [{"type": "thread.started", "thread_id": "shared-thread"}, final("answer", "turn_0"),
              completed({"input_tokens": 10, "output_tokens": 5}, "turn_0")]
    attempt(tmp_path, events, stage="first")
    attempt(tmp_path, events, stage="copy")
    result = transport_metrics(tmp_path)
    assert result["known_token_usage"]["total_tokens"] == 15
    assert sum(row["duplicate_usage_events"] for row in result["requests"]) == 1


def test_conflicting_values_for_one_id_stay_partial_and_are_not_added_twice(tmp_path):
    attempt(tmp_path, [final("answer", "same"), completed({"input_tokens": 10, "output_tokens": 5}, "same"),
        completed({"input_tokens": 11, "output_tokens": 6}, "same")])
    result = transport_metrics(tmp_path)
    assert result["known_token_usage"] == {} and not result["total_usage_known"]
    assert result["partial_token_usage"]["total_tokens"] == 15
    assert result["monitor_warnings"]


def test_network_and_structural_attempts_and_parallel_timing_are_all_preserved(tmp_path):
    attempt(tmp_path, [{"type": "turn.failed", "error": {"message": "service unavailable"}}], accepted=False)
    attempt(tmp_path, [{"type": "turn.started"}, final("answer"), completed({"input_tokens": 10, "output_tokens": 5})],
        native=2, elapsed=4, end="2026-10-28T00:00:04+00:00")
    attempt(tmp_path, [{"type": "turn.started"}, final("answer"), completed({"input_tokens": 20, "output_tokens": 5})],
        call=2, elapsed=3, end="2026-10-28T00:00:03+00:00")
    result = transport_metrics(tmp_path)
    assert result["cli_dispatches"] == 3 and result["logical_requests"] == 2
    assert result["network_retry_attempts"] == 1
    assert sum(row["structural_correction"] for row in result["requests"]) == 1
    assert result["known_request_seconds"] == 9.5 and result["wall_clock_seconds"] == 4
    assert result["complete_usage_requests"] == 2 and result["unknown_usage_requests"] == 1


def test_missing_or_malformed_optional_monitor_data_remains_unknown(tmp_path):
    directory = attempt(tmp_path, [], accepted=False)
    (directory / "process.json").write_text("broken optional monitor", encoding="utf-8")
    (directory / "stdout.jsonl").write_text("not json\n", encoding="utf-8")
    result = transport_metrics(tmp_path)
    assert result["cli_dispatches"] == 1 and result["unknown_usage_requests"] == 1
    assert result["unknown_duration_requests"] == 1 and result["monitor_warnings"]


def test_launch_attempt_count_does_not_claim_a_failed_popen_started_a_process(tmp_path):
    directory = attempt(tmp_path, [], accepted=False)
    (directory / "pid.json").unlink()
    write(directory / "process.json", {"status": "launch_error", "exited": False, "returncode": None})
    result = transport_metrics(tmp_path)
    assert result["launch_attempts"] == result["cli_dispatches"] == 1
    assert result["native_process_starts"] == 0 and result["unknown_native_process_starts"] == 0
    write(directory / "process.json", {"status": "process_error", "exited": False})
    assert transport_metrics(tmp_path)["unknown_native_process_starts"] == 1
