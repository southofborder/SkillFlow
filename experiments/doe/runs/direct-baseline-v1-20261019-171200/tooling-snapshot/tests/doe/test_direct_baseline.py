"""Offline integrity tests for the source-only current-session experiment."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from tools.doe.direct_baseline import (
    deduplicate_exposures, exposure_identity, find_receipt, import_trial,
    package_bundle, parse_receipt, prepare_trial, render_prompt,
    resolve_agent_session, sha256, summarize, verify,
)


ROOT = Path(__file__).resolve().parents[2]


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def receipt_rows(*, child="child-1", turn="turn-1", answer="Original answer.\n", tool=False, model="gpt-6.1-sol", effort="ultra", usage=True):
    rows = [
        {"type": "session_meta", "payload": {
            "id": child, "session_id": "root-1", "parent_thread_id": "root-1",
            "source": {"subagent": {"thread_spawn": {"agent_path": "/root/dispatcher/trial-1", "parent_thread_id": "root-1"}}},
            "model_provider": "openai", "creator_account_id": "ACCOUNT_CANARY",
        }},
        # A forked transcript can embed parent metadata and complete parent turns.
        {"type": "session_meta", "payload": {"id": "root-1", "model_provider": "OTHER_PROVIDER"}},
        {"type": "event_msg", "payload": {"type": "task_started", "turn_id": "root-turn", "started_at": 1}},
        {"type": "turn_context", "payload": {"turn_id": "root-turn", "model": "another-model", "effort": "low"}},
        {"type": "response_item", "payload": {"type": "message", "id": "root-answer", "role": "assistant", "phase": "final_answer", "content": [{"type": "output_text", "text": "ROOT_ANSWER_CANARY"}]}},
        {"type": "token_usage_record", "payload": {"thread_id": "root-1", "turn_id": "root-turn", "response_id": "root-response", "usage": {"input_tokens": 999999}}},
        {"type": "event_msg", "payload": {"type": "task_started", "turn_id": turn, "started_at": 100}},
        {"type": "turn_context", "payload": {"turn_id": turn, "model": model, "effort": effort}},
        {"type": "response_item", "payload": {"type": "agent_message", "author": "/root/dispatcher", "recipient": "/root/dispatcher/trial-1", "content": [{"type": "input_text", "text": "Message Type: NEW_TASK\nPayload:\n"}, {"type": "encrypted_content", "encrypted_content": "ENCRYPTED_PROMPT_CANARY"}]}},
        {"type": "response_item", "payload": {"type": "reasoning", "summary": [{"text": "HIDDEN_REASONING_CANARY"}], "encrypted_content": "HIDDEN_CIPHERTEXT_CANARY"}},
        {"type": "event_msg", "payload": {"type": "item_completed", "thread_id": child, "turn_id": turn, "item": {"type": "Reasoning", "id": "reasoning", "content": "HIDDEN_REASONING_CANARY"}}},
        {"type": "response_item", "payload": {"type": "message", "id": "answer-1", "role": "assistant", "phase": "commentary", "content": [{"type": "output_text", "text": "COMMENTARY_CANARY"}]}},
        {"type": "response_item", "payload": {"type": "message", "id": "final-1", "role": "assistant", "phase": "final_answer", "content": [{"type": "output_text", "text": answer}]}},
        {"type": "event_msg", "payload": {"type": "item_completed", "thread_id": child, "turn_id": turn, "item": {"type": "AgentMessage", "id": "final-1", "phase": "final_answer", "content": [{"type": "Text", "text": answer}]}}},
        {"type": "event_msg", "payload": {"type": "task_complete", "turn_id": turn, "started_at": 100, "completed_at": 105, "duration_ms": 5123, "time_to_first_token_ms": 150, "last_agent_message": "DUPLICATE_FINAL_CANARY"}},
        {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 999999999}, "last_token_usage": {"input_tokens": 111111}}, "rate_limits": {"credits": "ACCOUNT_BALANCE_CANARY"}}},
    ]
    if usage:
        usage_record = {"type": "token_usage_record", "payload": {
            "thread_id": child, "session_id": "root-1", "turn_id": turn, "response_id": "response-1",
            "usage": {"input_tokens": 110, "cached_input_tokens": 80, "cache_write_input_tokens": 0, "output_tokens": 25, "reasoning_output_tokens": 5, "total_tokens": 135},
            "turn_token_usage": {"input_tokens": 123456}, "thread_token_usage": {"input_tokens": 123456789},
        }}
        rows.extend([usage_record, deepcopy(usage_record)])
        rows.append({"type": "token_usage_record", "payload": {"thread_id": "other-child", "turn_id": turn, "response_id": "other-response", "usage": {"input_tokens": 1000000}}})
    if tool:
        rows.append({"type": "response_item", "payload": {"type": "custom_tool_call", "id": "tool-1", "name": "functions.exec", "input": "TOOL_ARGUMENT_CANARY"}})
        rows.append({"type": "event_msg", "payload": {"type": "item_completed", "thread_id": child, "turn_id": turn, "item": {"type": "CommandExecution", "id": "tool-1", "command": "TOOL_ARGUMENT_CANARY", "aggregated_output": "TOOL_OUTPUT_CANARY"}}})
    return rows


def write_receipt(path, rows):
    return write(path, "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n")


def prepare(tmp_path):
    source = tmp_path / "source"
    # This is genuine project source, preserved without translating its Chinese text.
    data = (ROOT / "docs/doe/SkillFlow-DOE目标与设计原则.md").read_bytes()
    write(source / "SKILL.md", data)
    write(source / "references/details.txt", b"Keep reference {original_answer} verbatim.\r\n\r\nFinal line.\r\n")
    write(source / "analysis.json", "DERIVED_ANSWER_LEAK_CANARY")
    run = tmp_path / "run"
    package_bundle(source, run, "case-1", source_files=["SKILL.md", "references/details.txt"], user_request="Retain the stated conditions.")
    template = write(tmp_path / "audit.txt", "{shared_rules}\n{source_bundle}\nUSER\n{user_request}\n")
    shared = write(tmp_path / "shared.txt", "Source only. No tools.")
    prepare_trial(run, "trial-1", "case-1", template, shared_path=shared)
    return run, source


def test_explicit_sources_exclude_answers_and_preserve_original_bytes_and_references(tmp_path):
    run, source = prepare(tmp_path)
    frozen = run / "cases/case-1"
    assert (frozen / "inputs/SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes()
    assert (frozen / "inputs/references/details.txt").read_bytes() == (source / "references/details.txt").read_bytes()
    bundle = (frozen / "source_bundle.txt").read_text(encoding="utf-8")
    assert "FILE references/details.txt\n1: Keep reference {original_answer} verbatim.\n2: \n3: Final line." in bundle
    assert "SkillFlow-DOE任务基准与用途切片.md" in bundle
    prompt = (run / "trials/trial-1/prompt.txt").read_text(encoding="utf-8")
    assert "DERIVED_ANSWER_LEAK_CANARY" not in prompt
    assert "{original_answer}" in prompt  # Source placeholders must not be interpreted.
    assert not (frozen / "inputs/analysis.json").exists()
    assert verify(run)["verified"]


def test_freezes_and_imports_never_overwrite(tmp_path):
    run, source = prepare(tmp_path)
    with pytest.raises(FileExistsError):
        package_bundle(source, run, "case-1", source_files=["SKILL.md"])
    with pytest.raises(FileExistsError):
        prepare_trial(run, "trial-1", "case-1", tmp_path / "audit.txt")
    for bad in ("../SKILL.md", "C:/file.md", "/file.md"):
        with pytest.raises(ValueError):
            package_bundle(source, run, "other", source_files=[bad])


def test_render_prompt_does_not_interpret_user_or_source_braces(tmp_path):
    template = write(tmp_path / "review.txt", "{shared_rules}\n{source_bundle}\n{user_request}\n{original_answer}\n{arm_instruction}")
    result = render_prompt(template, "source {user_request}", "user {shared_rules}", shared_rules="common", original_answer="answer {source_bundle}", arm_instruction="audit")
    assert result == "common\nsource {user_request}\nuser {shared_rules}\nanswer {source_bundle}\naudit"
    with pytest.raises(ValueError, match="original_answer"):
        render_prompt(template, "source", "user")


def test_exact_child_turn_visible_answer_usage_dedup_and_allowlist(tmp_path):
    answer = "  Exact final answer.\r\n\n"
    receipt = write_receipt(tmp_path / "rollout-child-1.jsonl", receipt_rows(answer=answer))
    actual, decision = parse_receipt(receipt, "child-1")
    assert actual == answer
    assert decision["protocol_status"] == "conformant"
    assert decision["observed_configuration"] == [{"model": "gpt-6.1-sol", "effort": "ultra", "model_provider": "openai"}]
    assert decision["usage"]["response_count"] == 1
    assert decision["usage"]["totals"]["input_tokens"] == 110
    assert decision["usage"]["totals"]["total_tokens"] == 135
    assert decision["timing"]["duration_ms"] == 5123
    assert decision["prompt_delivery_audit"]["status"] == "unavailable_encrypted"
    exported = json.dumps(decision)
    for canary in ("ROOT_ANSWER", "HIDDEN_REASONING", "HIDDEN_CIPHERTEXT", "COMMENTARY", "ACCOUNT", "DUPLICATE_FINAL", "ENCRYPTED_PROMPT"):
        assert canary not in exported
    with pytest.raises(ValueError, match="primary session"):
        parse_receipt(receipt, "root-1")
    with pytest.raises(ValueError, match="attribution"):
        parse_receipt(receipt, "child-1", "root-turn")


def test_tool_use_and_configuration_mismatch_are_protocol_violations(tmp_path):
    receipt = write_receipt(tmp_path / "receipt.jsonl", receipt_rows(tool=True, model="other", effort="high"))
    _, decision = parse_receipt(receipt, "child-1")
    assert decision["protocol_status"] == "violated"
    assert len(decision["tools"]) == 1
    assert len(decision["violations"]) == 3
    assert "TOOL_ARGUMENT_CANARY" not in json.dumps(decision)
    assert "TOOL_OUTPUT_CANARY" not in json.dumps(decision)


def test_inherited_transcript_is_a_protocol_violation_even_with_matching_configuration(tmp_path):
    rows = receipt_rows()
    rows[0]["payload"]["forked_from_id"] = "prior-context"
    receipt = write_receipt(tmp_path / "receipt.jsonl", rows)
    _, decision = parse_receipt(receipt, "child-1")
    assert decision["configuration_verified"]
    assert decision["protocol_status"] == "violated"
    assert any("prior transcript" in v for v in decision["violations"])


def test_reference_changes_after_sealing_are_detected_without_model_calls(tmp_path):
    run, _ = prepare(tmp_path)
    reference = write(run / "references/pilot-a.json", '{"author":"A","reason":"Source-grounded reference."}\n')
    seal = {"files": {"pilot-a.json": sha256(reference.read_bytes())}}
    write(run / "pilot-reference-freeze.json", json.dumps(seal))
    assert verify(run)["verified"]
    reference.write_text('{"author":"A","reason":"Changed after sealing."}\n', encoding="utf-8")
    replayed = verify(run)
    assert not replayed["verified"]
    assert replayed["model_calls"] == 0
    assert replayed["reference_count"] == 1
    assert "Reference hash mismatch: pilot-a.json" in replayed["errors"]


def test_review_must_contain_its_own_registered_first_answer(tmp_path):
    run, _ = prepare(tmp_path)
    receipt = write_receipt(tmp_path / "receipt.jsonl", receipt_rows(answer="The actual first answer.\n"))
    import_trial(run, "trial-1", agent_session_id="child-1", receipt_path=receipt)
    template = write(tmp_path / "review.txt", "{shared_rules}\n{source_bundle}\n{user_request}\n{original_answer}\n")
    wrong = write(tmp_path / "wrong-answer.txt", "An answer from a different run.\n")
    prepare_trial(run, "review-1", "case-1", template, original_answer_path=wrong,
                  metadata={"review": True, "parent_trial_id": "trial-1"})
    replayed = verify(run)
    assert not replayed["verified"]
    assert "Review original differs from its registered parent: review-1" in replayed["errors"]


def test_unknown_usage_ignores_cumulative_and_last_token_counts(tmp_path):
    receipt = write_receipt(tmp_path / "receipt.jsonl", receipt_rows(usage=False))
    _, decision = parse_receipt(receipt, "child-1")
    assert decision["usage"]["response_count"] == 0
    assert all(value is None for value in decision["usage"]["totals"].values())
    assert decision["protocol_status"] == "conformant"


def test_multiple_turns_require_selection_and_mark_freshness_violation(tmp_path):
    rows = receipt_rows()
    rows.append({"type": "token_usage_record", "payload": {"thread_id": "child-1", "turn_id": "turn-2", "response_id": "response-2", "usage": {"input_tokens": 9999}}})
    receipt = write_receipt(tmp_path / "receipt.jsonl", rows)
    with pytest.raises(ValueError, match="supply turn_id"):
        parse_receipt(receipt, "child-1")
    answer, decision = parse_receipt(receipt, "child-1", "turn-1")
    assert answer == "Original answer.\n"
    assert decision["protocol_status"] == "violated"
    assert decision["usage"]["response_count"] == 1
    assert any("additional attributed turns" in s for s in decision["violations"])


def test_conflicting_response_usage_is_not_silently_added(tmp_path):
    rows = receipt_rows()
    conflict = deepcopy(next(r for r in rows if r["type"] == "token_usage_record" and r["payload"].get("response_id") == "response-1"))
    conflict["payload"]["usage"]["input_tokens"] = 222
    rows.append(conflict)
    _, decision = parse_receipt(write_receipt(tmp_path / "receipt.jsonl", rows), "child-1")
    assert decision["protocol_status"] == "violated"
    assert decision["usage"]["totals"]["input_tokens"] == 110
    assert any("conflict" in s for s in decision["violations"])


def test_visible_delivered_prompt_is_compared_when_available(tmp_path):
    rows = receipt_rows()
    incoming = next(r for r in rows if r["type"] == "response_item" and r["payload"].get("type") == "agent_message")
    incoming["payload"]["content"] = [{"type": "input_text", "text": "Message Type: NEW_TASK\nPayload:\nThe exact prompt."}]
    path = write_receipt(tmp_path / "receipt.jsonl", rows)
    _, decision = parse_receipt(path, "child-1", expected_prompt_sha256=sha256(b"The exact prompt."))
    assert decision["prompt_delivery_audit"]["status"] == "matches"
    _, decision = parse_receipt(path, "child-1", expected_prompt_sha256=sha256(b"Other prompt."))
    assert decision["protocol_status"] == "violated"
    assert decision["prompt_delivery_audit"]["status"] == "mismatch"


def test_agent_resolution_scopes_root_and_does_not_inspect_nested_meta(tmp_path):
    sessions = tmp_path / "sessions"
    path = write_receipt(sessions / "nested/rollout-child-1.jsonl", receipt_rows())
    assert resolve_agent_session("/root/dispatcher/trial-1", sessions, root_session_id="root-1") == "child-1"
    assert find_receipt("child-1", sessions) == path
    with pytest.raises(ValueError, match="found 0"):
        resolve_agent_session("/root/dispatcher/trial-1", sessions, root_session_id="another-root")
    duplicate = receipt_rows(child="child-2")
    write_receipt(sessions / "rollout-child-2.jsonl", duplicate)
    with pytest.raises(ValueError, match="found 2"):
        resolve_agent_session("/root/dispatcher/trial-1", sessions)


def test_import_replay_without_model_calls_and_tamper_detection(tmp_path):
    run, _ = prepare(tmp_path)
    sessions = tmp_path / "sessions"
    receipt = write_receipt(sessions / "nested/rollout-child-1.jsonl", receipt_rows(answer="Answer unchanged.\r\n"))
    record = import_trial(run, "trial-1", agent_name="/root/dispatcher/trial-1", root_session_id="root-1", sessions_dir=sessions)
    assert record["agent_session_id"] == "child-1"
    assert (run / "trials/trial-1/answer.txt").read_bytes() == b"Answer unchanged.\r\n"
    with pytest.raises(FileExistsError):
        import_trial(run, "trial-1", agent_session_id="child-1", receipt_path=receipt)
    replayed = verify(run, sessions_dir=sessions)
    assert replayed["verified"]
    assert replayed["receipt_replay_count"] == 1
    assert replayed["model_calls"] == 0
    summary = summarize(run)
    assert summary["unique_response_count"] == 1
    assert summary["usage_totals"]["total_tokens"] == 135
    write(run / "trials/trial-1/answer.txt", "Modified answer.")
    assert any("Output hash mismatch" in e for e in verify(run)["errors"])


def test_source_and_prompt_tampering_fail_replay(tmp_path):
    run, _ = prepare(tmp_path)
    write(run / "cases/case-1/inputs/SKILL.md", "Changed source.")
    assert any("Source hash mismatch" in e for e in verify(run)["errors"])
    write(run / "trials/trial-1/prompt.txt", "Changed prompt.")
    assert any("Prompt replay mismatch" in e for e in verify(run)["errors"])


def test_duplicate_exposures_use_all_five_identity_axes():
    item = {"source": "records[i]", "payload_scope": ["private_note"], "version": "before_filter", "condition": {"selected": True}, "recipient": "records[i].recipient", "reason": "First description."}
    duplicate = {**deepcopy(item), "reason": "Another description of the same exposure."}
    assert exposure_identity(item) == exposure_identity(duplicate)
    for key, changed in (("source", "records[j]"), ("payload_scope", ["token"]), ("version", "after_filter"), ("condition", {"selected": False}), ("recipient", "archive")):
        assert exposure_identity(item) != exposure_identity({**item, key: changed})
    assert deduplicate_exposures([item, duplicate, {**item, "recipient": "archive"}]) == [item, {**item, "recipient": "archive"}]
    with pytest.raises(ValueError, match="missing"):
        exposure_identity({"source": "records"})
