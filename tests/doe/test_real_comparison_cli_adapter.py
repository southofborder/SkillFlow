"""Synthetic CLI transport integrity checks; no executable or model is invoked."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from tools.doe.real_comparison import cli_adapter as adapter


SESSION = "synthetic-cli-session"
TURN = "synthetic-cli-turn"
RESPONSE = "synthetic-response-id"
FINAL = "synthetic-final-message"
ANSWER = '{"observation":"The supplied source reference is preserved."}'


def write_rows(path, rows):
    path.write_bytes(("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8"))


def row(kind, **payload):
    return {"type": kind, "payload": payload}


def message(role, text, identifier, **fields):
    return row("response_item", type="message", id=identifier, role=role,
               content=[{"type": "output_text" if role == "assistant" else "input_text", "text": text}],
               **fields)


def environment(cwd):
    return (f"<environment_context>\n  <cwd>{cwd}</cwd>\n  <shell>powershell</shell>\n"
            "  <current_date>2026-10-20</current_date>\n  <timezone>Asia/Shanghai</timezone>\n"
            f"  <filesystem><workspace_roots><root>{cwd}</root></workspace_roots>"
            '<permission_profile type="managed"><file_system type="restricted"><entry access="read">'
            "<special>:root</special></entry></file_system></permission_profile></filesystem>\n</environment_context>")


@pytest.fixture
def receipt(tmp_path, monkeypatch):
    executable = tmp_path / "synthetic-codex.exe"
    executable.write_bytes(b"A fictional executable; this file is never executed.")
    prompt = tmp_path / "prompt.txt"
    # This is genuine multilingual input coverage, including literal source references.
    prompt.write_bytes('Source quotation: "保留原文引用" from source/记录.txt.\r\nReturn an English observation.\n'.encode("utf-8"))
    cwd = tmp_path / "empty-workdir"
    cwd.mkdir()
    output = tmp_path / "process-output"
    original_sha256 = adapter.sha256
    monkeypatch.setattr(adapter, "sha256", lambda path: adapter.PINNED_EXECUTABLE_SHA256
                        if Path(path).resolve() == executable.resolve() else original_sha256(path))

    def forbid_process(*args, **kwargs):
        pytest.fail("A transport unit test attempted to start a real process")

    monkeypatch.setattr(adapter.subprocess, "Popen", forbid_process)
    prepared = adapter.prepare_launch(executable, prompt, output, cwd)
    prepared["allowed_environment_dates"] = ["2026-10-20"]
    base = "Synthetic common runtime base instructions."
    developer = "Synthetic common developer instructions."
    prepared["base_instructions_sha256"] = adapter.digest(base)
    prepared["developer_segment_sha256"] = [[adapter.digest(developer)]]
    prompt_text = prompt.read_bytes().decode("utf-8")
    usage = {"input_tokens": 13, "cached_input_tokens": 2, "cache_write_input_tokens": 0,
             "output_tokens": 7, "reasoning_output_tokens": 3, "total_tokens": 20}
    attribution = {"turn_id": TURN, "root_turn_id": TURN, "turn_trigger": "exec",
                   "parent_turn_id": None, "initiating_agent_path": None}
    rows = [
        row("session_meta", id=SESSION, session_id=SESSION, source="exec", originator="codex_exec",
            cli_version=adapter.PINNED_VERSION, model_provider="openai", cwd=str(cwd),
            base_instructions={"text": base}, history_mode="paginated", thread_source="user"),
        row("event_msg", type="task_started", turn_id=TURN, root_turn_id=TURN,
            started_at=1000, turn_attribution=attribution),
        message("developer", developer, "synthetic-runtime-message"),
        message("user", environment(cwd), "synthetic-environment-message"),
        row("turn_context", turn_id=TURN, root_turn_id=TURN, model="gpt-6.1-sol", effort="ultra",
            cwd=str(cwd), approval_policy="never", sandbox_policy={"type": "read-only"}),
        message("user", prompt_text, "synthetic-task-message"),
        row("event_msg", type="item_completed", thread_id=SESSION, turn_id=TURN,
            item={"type": "UserMessage", "id": "synthetic-task-event",
                  "content": [{"type": "text", "text": prompt_text, "text_elements": []}]}),
        row("response_item", type="reasoning", id="synthetic-reasoning-item",
            encrypted_content="SYNTHETIC_REASONING_CANARY"),
        row("event_msg", type="item_completed", thread_id=SESSION, turn_id=TURN,
            item={"type": "AgentMessage", "id": FINAL, "phase": "final_answer",
                  "content": [{"type": "Text", "text": ANSWER}]}),
        message("assistant", ANSWER, FINAL, phase="final_answer", status="completed"),
        row("token_usage_record", thread_id=SESSION, turn_id=TURN, session_id=SESSION,
            root_turn_id=TURN, response_id=RESPONSE, usage=usage),
        row("event_msg", type="task_complete", turn_id=TURN, root_turn_id=TURN,
            started_at=1000, completed_at=1001, duration_ms=1000, time_to_first_token_ms=200),
    ]
    stdout_rows = [{"type": "thread.started", "thread_id": SESSION}, {"type": "turn.started"},
                   {"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": ANSWER}},
                   {"type": "turn.completed", "usage": {key: value for key, value in usage.items()
                                                         if key != "total_tokens"}}]
    return SimpleNamespace(prepared=prepared, rows=rows, stdout_rows=stdout_rows, usage=usage,
                           path=tmp_path / "synthetic-rollout.jsonl", stdout=tmp_path / "synthetic-stdout.jsonl",
                           last=tmp_path / "synthetic-last-message.txt", prompt=prompt, cwd=cwd, output=output)


def inspect(receipt):
    write_rows(receipt.path, receipt.rows)
    write_rows(receipt.stdout, receipt.stdout_rows)
    if not receipt.last.exists():
        receipt.last.write_bytes(ANSWER.encode("utf-8"))
    return adapter.inspect_receipt(receipt.path, SESSION, receipt.prepared,
                                   stdout_path=receipt.stdout, last_message_path=receipt.last)


def payload(receipt, kind, item_type=None):
    return next(item["payload"] for item in receipt.rows if item["type"] == kind
                and (item_type is None or item["payload"].get("type") == item_type))


def assert_rejected(receipt, expected):
    _, record = inspect(receipt)
    assert record["protocol_status"] == "violated"
    assert any(expected.lower() in reason.lower() for reason in record["violations"]), record["violations"]


def test_exact_source_bytes_runtime_envelopes_and_response_usage_are_verified(receipt):
    answer, record = inspect(receipt)
    assert answer == ANSWER
    assert record["protocol_status"] == "conformant", record["violations"]
    assert record["configuration_verified"] and record["provider_verified"] and record["usage_verified"]
    assert record["prompt_delivery_audit"]["status"] == "matches"
    assert [item["is_environment_context"] for item in record["prompt_delivery_audit"]["visible_user_messages"]] == [True, False]
    assert record["usage"]["by_response_id"] == {RESPONSE: receipt.usage}
    assert record["final_item_ids"] == [FINAL]
    assert record["tools"] == []
    assert "SYNTHETIC_REASONING_CANARY" not in json.dumps(record)


@pytest.mark.parametrize("change", ["task_bytes", "extra_user", "environment_tag", "environment_root", "developer", "base"])
def test_changed_or_additional_visible_inputs_are_rejected(receipt, change):
    if change == "task_bytes":
        receipt.rows[5]["payload"]["content"][0]["text"] += "Injected follow-up."
    elif change == "extra_user":
        receipt.rows.insert(6, message("user", "An unauthorized hint.", "injected-user-message"))
    elif change == "environment_tag":
        content = receipt.rows[3]["payload"]["content"][0]
        content["text"] = content["text"].replace("</environment_context>", "<hint>Injected instruction.</hint></environment_context>")
    elif change == "environment_root":
        content = receipt.rows[3]["payload"]["content"][0]
        content["text"] = content["text"].replace(f"<root>{receipt.cwd}</root>", "<root>unapproved-root</root>")
    elif change == "developer":
        receipt.rows[2]["payload"]["content"][0]["text"] += "Injected developer instruction."
    else:
        payload(receipt, "session_meta")["base_instructions"]["text"] += "Injected runtime instruction."
    assert_rejected(receipt, "instructions" if change in {"developer", "base"} else "input")


@pytest.mark.parametrize("change,expected", [("provider", "provider"), ("effort", "effort"),
                                             ("history", "history"), ("tool", "tool"),
                                             ("unknown_usage", "usage"), ("negative_usage", "usage")])
def test_runtime_history_activity_and_unaccountable_usage_stop_acceptance(receipt, change, expected):
    if change == "provider":
        payload(receipt, "session_meta")["model_provider"] = "unapproved-provider"
    elif change == "effort":
        payload(receipt, "turn_context")["effort"] = "max"
    elif change == "history":
        payload(receipt, "session_meta")["forked_from_id"] = "synthetic-prior-session"
    elif change == "tool":
        receipt.rows.insert(7, row("response_item", type="unfamiliar_tool_call", id="synthetic-tool", name="retrieve"))
    elif change == "unknown_usage":
        payload(receipt, "token_usage_record")["usage"]["input_tokens"] = None
    else:
        payload(receipt, "token_usage_record")["usage"]["output_tokens"] = -1
    assert_rejected(receipt, expected)


def test_identical_response_usage_is_deduplicated_and_conflicts_are_rejected(receipt):
    usage_row = next(item for item in receipt.rows if item["type"] == "token_usage_record")
    receipt.rows.insert(-1, deepcopy(usage_row))
    _, record = inspect(receipt)
    assert record["protocol_status"] == "conformant"
    assert record["usage"]["response_count"] == 1
    assert record["usage"]["totals"] == receipt.usage
    receipt.rows[-2]["payload"]["usage"]["input_tokens"] += 1
    assert_rejected(receipt, "usage")


@pytest.mark.parametrize("change,expected", [
    ("environment_date", "input"), ("session", "session_id"),
    ("turn_trigger", "attribution"), ("parent", "history"),
    ("usage_session", "attribution"), ("usage_root", "attribution"),
    ("context_root", "context"), ("extra_context", "context"),
    ("final_status", "completed"), ("final_event_id", "completion"),
    ("final_event_thread", "completion"), ("final_event_text", "completion"),
    ("duplicate_final", "completion"), ("user_event_text", "user-message"),
])
def test_entire_session_and_exact_completion_attribution_are_required(receipt, change, expected):
    if change == "environment_date":
        receipt.rows[3]["payload"]["content"][0]["text"] = environment(receipt.cwd).replace("2026-10-20", "2026-10-19")
    elif change == "session":
        payload(receipt, "session_meta")["session_id"] = "different-synthetic-session"
    elif change == "turn_trigger":
        payload(receipt, "event_msg", "task_started")["turn_attribution"]["turn_trigger"] = "resume"
    elif change == "parent":
        payload(receipt, "event_msg", "task_started")["turn_attribution"]["parent_turn_id"] = "synthetic-prior-turn"
    elif change in {"usage_session", "usage_root"}:
        payload(receipt, "token_usage_record")["session_id" if change == "usage_session" else "root_turn_id"] = "different-synthetic-identity"
    elif change == "context_root":
        payload(receipt, "turn_context")["root_turn_id"] = "different-synthetic-root"
    elif change == "extra_context":
        receipt.rows.insert(5, deepcopy(receipt.rows[4]))
    elif change == "final_status":
        receipt.rows[9]["payload"]["status"] = "in_progress"
    elif change.startswith("final_event"):
        event = receipt.rows[8]["payload"]
        if change == "final_event_id":
            event["item"]["id"] = "different-synthetic-final"
        elif change == "final_event_thread":
            event["thread_id"] = "different-synthetic-thread"
        else:
            event["item"]["content"][0]["text"] += "Changed event text."
    elif change == "duplicate_final":
        receipt.rows.insert(10, deepcopy(receipt.rows[9]))
    else:
        receipt.rows[6]["payload"]["item"]["content"][0]["text"] += "Changed user event."
    assert_rejected(receipt, expected)


@pytest.mark.parametrize("change,expected", [("stdout_answer", "stdout"), ("last_message", "last-message"),
                                             ("stdout_activity", "stdout"), ("stdout_session", "session")])
def test_stdout_and_last_message_must_bind_to_the_exact_receipt(receipt, change, expected):
    if change == "stdout_answer":
        receipt.stdout_rows[2]["item"]["text"] += " Truncated or changed."
    elif change == "last_message":
        receipt.last.write_bytes((ANSWER + "\n").encode("utf-8"))
    elif change == "stdout_activity":
        receipt.stdout_rows.insert(2, {"type": "item.completed", "item": {"id": "stdout-tool", "type": "command_execution"}})
    else:
        receipt.stdout_rows[0]["thread_id"] = "another-synthetic-session"
    assert_rejected(receipt, expected)


def test_execute_launch_sends_exact_stdin_once_and_records_every_poll(receipt, monkeypatch):
    calls = []
    clock = iter([0.0, 0.0, 0.0, 30.0, 30.0, 30.0, 30.5, 30.5])
    monkeypatch.setattr(adapter.time, "perf_counter", lambda: next(clock))

    class FakeProcess:
        pid = 4242
        returncode = None

        def communicate(self, input=None, timeout=None):
            calls.append({"input": input, "timeout": timeout})
            if len(calls) == 1:
                raise subprocess.TimeoutExpired("synthetic-command", timeout)
            self.returncode = 0

    launches = []

    def fake_popen(command, **kwargs):
        launches.append((command, kwargs))
        kwargs["stdout"].write(b'{"type":"thread.started","thread_id":"synthetic-cli-session"}\n')
        return FakeProcess()

    result = adapter.execute_launch(receipt.prepared, timeout_seconds=90, popen=fake_popen)
    assert len(launches) == 1
    assert launches[0][0] == receipt.prepared["command"]
    assert launches[0][1]["cwd"] == receipt.cwd
    assert launches[0][1]["stdin"] == subprocess.PIPE
    assert calls == [{"input": receipt.prompt.read_bytes(), "timeout": 30}, {"input": None, "timeout": 30}]
    assert result["status"] == "process_exited" and result["returncode"] == 0
    assert result["actual_cli_process_started"] and result["retries"] == 0
    assert [wait["result"] for wait in result["supervisor_waits"]] == ["still_running", "process_exited"]
    assert result["supervisor_elapsed_seconds"] == 30.5
    assert json.loads((receipt.output / "process-result.json").read_text()) == result
    assert json.loads((receipt.output / "process-start.json").read_text())["pid"] == 4242
    assert (receipt.output / "stdout.jsonl").read_bytes().endswith(b"\n")
    with pytest.raises(ValueError, match="cannot be reused"):
        adapter.execute_launch(receipt.prepared, popen=fake_popen)
    assert len(launches) == 1


def test_timeout_kills_the_one_process_without_replacement_and_retains_wait_evidence(receipt, monkeypatch):
    calls, kills, launches = [], [], []
    clock = iter([0.0, 0.0, 0.0, 1.0, 1.0, 1.25])
    monkeypatch.setattr(adapter.time, "perf_counter", lambda: next(clock))

    class FakeProcess:
        pid = 4243
        returncode = None

        def communicate(self, input=None, timeout=None):
            calls.append((input, timeout))
            if not kills:
                raise subprocess.TimeoutExpired("synthetic-command", timeout)
            self.returncode = -9

        def kill(self):
            kills.append(True)

    def fake_popen(*args, **kwargs):
        launches.append(True)
        return FakeProcess()

    result = adapter.execute_launch(receipt.prepared, timeout_seconds=1, popen=fake_popen)
    assert launches == [True] and kills == [True]
    assert calls == [(receipt.prompt.read_bytes(), 1), (None, 30)]
    assert result["status"] == "timeout" and result["returncode"] == -9
    assert result["retries"] == 0
    assert result["supervisor_waits"] == [{"wait_seconds": 1.0, "result": "still_running"}]
    assert result["supervisor_elapsed_seconds"] == 1.25


@pytest.mark.parametrize("change", ["stdin", "command", "workdir"])
def test_launch_changes_are_rejected_before_starting_a_process(receipt, change):
    if change == "stdin":
        receipt.prompt.write_bytes(receipt.prompt.read_bytes() + b"Changed after registration.")
    elif change == "command":
        receipt.prepared["command"].insert(1, "resume")
    else:
        (receipt.cwd / "unexpected-instructions.txt").write_text("An injected instruction.", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        adapter.execute_launch(receipt.prepared)
    assert not receipt.output.exists()
