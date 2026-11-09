"""Native CLI transport tests use fake processes only, with no model execution."""
import json
from pathlib import Path

import pytest

from tools.doe import document_guided_client as transport


def pending(owner, prompt, path="calls/graph/a001"):
    file = owner / path / "call.json"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps({"status": "running", "prompt": prompt}), encoding="utf-8")
    return file


def message(text, **extra):
    return {"type": "item.completed", "item": {"type": "agent_message", "text": text, **extra}}


def fake_processes(scripts, launches):
    def popen(argv, **kwargs):
        script = scripts.pop(0)
        launches.append({"argv": argv, **kwargs})
        assert not list(Path(kwargs["cwd"]).iterdir())

        class Process:
            pid = 12345 + len(launches)
            returncode = None

            def communicate(self, input=None, timeout=None):
                launches[-1]["input"] = input
                kwargs["stdout"].write("\n".join(json.dumps(row) for row in script.get("rows", [])).encode())
                kwargs["stdout"].flush()
                kwargs["stderr"].write(script.get("stderr", "").encode())
                kwargs["stderr"].flush()
                if "last" in script:
                    Path(argv[argv.index("--output-last-message") + 1]).write_bytes(script["last"].encode())
                self.returncode = script.get("returncode", 0)
                return None, None

            def poll(self):
                return self.returncode

            def kill(self):
                self.returncode = -9

        return Process()
    return popen


def client(tmp_path, scripts, *, retries=2):
    owner = tmp_path / "owner"
    prompt = "Analyze frozen source.\n原文\r\n"
    pending(owner, prompt)
    executable = tmp_path / "codex.exe"
    executable.write_bytes(b"offline fixture; never executable")
    launches = []
    return transport.Client(tmp_path / "transport", owner=owner, executable=executable,
        retries=retries, popen=fake_processes(scripts, launches)), prompt, launches


def test_complete_answer_survives_missing_usage_empty_tail_and_empty_last(tmp_path):
    answer = '{"outcome":"completed","findings":[]}'
    value, prompt, launches = client(tmp_path, [{"rows": [message(answer), message("")], "last": ""}])
    assert value.complete(prompt) == answer
    assert value.complete(prompt) == answer
    assert len(launches) == 1
    argv = launches[0]["argv"]
    assert argv[argv.index("--model") + 1] == "gpt-6.1-sol"
    for text in ('model_reasoning_effort="max"', 'model_provider="openai"', "--ignore-user-config", "--ignore-rules", "read-only"):
        assert text in argv
    assert [argv[index + 1] for index, item in enumerate(argv) if item == "--disable"] == [
        "plugins", "remote_plugin", "recommended_plugins"]
    assert launches[0]["input"].decode("utf-8") == transport.ENVELOPE + prompt
    usage = next((tmp_path / "transport").rglob("usage.json"))
    assert transport.read(usage) == {"usage": {}, "known": False}
    assert not list((tmp_path / "transport").rglob("*receipt*"))


def test_identical_prompt_in_two_structural_calls_uses_distinct_request_keys(tmp_path):
    value, prompt, launches = client(tmp_path, [{"rows": [message("first")]}, {"rows": [message("second")]}])
    assert value.complete(prompt) == "first"
    first = value.owner / "calls/graph/a001/call.json"
    first.write_text(json.dumps({"status": "complete", "prompt": prompt}), encoding="utf-8")
    pending(value.owner, prompt, "calls/graph/a002")
    assert value.complete(prompt) == "second"
    assert len(launches) == 2
    assert len(list((tmp_path / "transport").glob("*/request.json"))) == 2


@pytest.mark.parametrize("script", [
    {"rows": [message("first"), message("second")], "stderr": "HTTP 503 service unavailable"},
    {"rows": [message("first")], "last": "different last message"},
])
def test_different_completed_answers_stop_without_selecting_or_retrying(tmp_path, script):
    value, prompt, launches = client(tmp_path, [script])
    with pytest.raises(transport.AmbiguousCLIAnswer):
        value.complete(prompt)
    assert len(launches) == 1 and not list((tmp_path / "transport").rglob("accepted.json"))


def test_last_message_fallback_and_nonzero_exit_with_final_answer_are_reusable(tmp_path):
    value, prompt, launches = client(tmp_path, [{"rows": [{"type": "turn.failed", "error": {"message": "monitor failed"}}],
                                              "last": "complete final answer", "returncode": 1}])
    assert value.complete(prompt) == "complete final answer"
    assert value.complete(prompt) == "complete final answer"
    assert len(launches) == 1


def test_at_most_two_extra_network_attempts_after_confirmed_exit(tmp_path):
    failure = {"rows": [{"type": "turn.failed", "error": {"message": "HTTP 503 service unavailable"}}], "returncode": 1}
    success = {"rows": [message("done"), {"type": "turn.completed", "usage": {
        "input_tokens": 10, "output_tokens": 5, "cached_input_tokens": 6, "reasoning_output_tokens": 2}}]}
    value, prompt, launches = client(tmp_path, [failure, failure, success])
    assert value.complete(prompt) == "done"
    assert len(launches) == 3
    assert len({str(item["cwd"]) for item in launches}) == 3
    assert transport.read(next((tmp_path / "transport").rglob("attempt-003/usage.json")))["usage"]["output_tokens"] == 5


def test_network_retry_exhaustion_and_nonnetwork_errors_do_not_resend_on_reopen(tmp_path):
    failure = {"rows": [{"type": "error", "message": "stream disconnected: connection reset"}], "returncode": 1}
    value, prompt, launches = client(tmp_path / "network", [failure, failure, failure])
    with pytest.raises(ValueError, match="retry limit"):
        value.complete(prompt)
    with pytest.raises(ValueError, match="retry limit"):
        value.complete(prompt)
    assert len(launches) == 3
    bad, prompt2, launches2 = client(tmp_path / "auth", [{"rows": [{"type": "error", "message": "authentication denied"}], "returncode": 1}])
    with pytest.raises(ValueError, match="not an eligible"):
        bad.complete(prompt2)
    assert len(launches2) == 1


@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_complete_delivery_limit_includes_envelope_and_preserves_source(tmp_path, offset):
    value, _, launches = client(tmp_path, [{"rows": [message("complete")]}])
    # Multilingual and non-BMP text are retained, with no byte/token conversion.
    prefix = "源文🌍\r\n"
    size = transport.MAX_INPUT_CHARS - len(transport.ENVELOPE) + offset
    prompt = prefix + "x" * (size - len(prefix))
    pending(value.owner, prompt)
    if offset <= 0:
        assert value.complete(prompt) == "complete"
        assert len(launches) == 1
        assert launches[0]["input"].decode("utf-8") == transport.ENVELOPE + prompt
    else:
        for _ in range(2):
            with pytest.raises(transport.InputTooLarge, match="no CLI process started"):
                value.complete(prompt)
        assert launches == []
        rejection = next((tmp_path / "transport").rglob("input-rejection.json"))
        record = transport.read(rejection)
        assert record["actual_chars"] == transport.MAX_INPUT_CHARS + 1
        assert record["max_chars"] == transport.MAX_INPUT_CHARS
        assert record["process_started"] is False and record["usage"] is None
        assert (rejection.parent / "prompt.txt").read_bytes().decode("utf-8") == transport.ENVELOPE + prompt
        assert not list((tmp_path / "transport").rglob("started.json"))
        assert not list((tmp_path / "transport").glob("*/attempt-*"))
        from tools.doe.document_guided_metrics import transport_metrics
        metrics = transport_metrics(tmp_path)
        assert metrics["inputs_rejected_before_start"] == 1
        assert metrics["native_process_starts"] == metrics["cli_dispatches"] == 0
        assert metrics["complete_usage_requests"] == metrics["unknown_usage_requests"] == 0


def test_known_request_failure_is_typed_but_owner_failure_is_not(tmp_path):
    value, prompt, launches = client(tmp_path, [{"rows": [{"type": "error", "message": "input_too_large"}], "returncode": 1}])
    with pytest.raises(transport.ModelRequestFailure):
        value.complete(prompt)
    assert len(launches) == 1
    with pytest.raises(ValueError) as failure:
        value.complete("A prompt with no durable owner")
    assert not isinstance(failure.value, transport.ModelRequestFailure)


def test_saved_complete_answer_is_reused_before_new_length_check(tmp_path, monkeypatch):
    value, prompt, launches = client(tmp_path, [{"rows": [message("complete")]}])
    assert value.complete(prompt) == "complete"
    monkeypatch.setattr(transport, "MAX_INPUT_CHARS", 1)
    assert value.complete(prompt) == "complete"
    assert len(launches) == 1


def test_started_unknown_process_never_spawns_a_replacement(tmp_path):
    value, prompt, launches = client(tmp_path, [{"rows": [message("done")]}])
    assert value.complete(prompt) == "done"
    target = next((tmp_path / "transport").glob("*/request.json")).parent
    (target / "accepted.json").unlink()
    (target / "answer.txt").unlink()
    (target / "attempt-001/process.json").unlink()
    with pytest.raises(transport.PendingCLIRequest, match="confirmed exit"):
        value.complete(prompt)
    assert len(launches) == 1


def test_monitor_write_errors_do_not_discard_a_complete_answer(tmp_path, monkeypatch):
    value, prompt, launches = client(tmp_path, [{"rows": [message("done")]}])
    write = transport._write
    def fail_monitor(path, content):
        if Path(path).name in {"usage.json", "pid.json", "accepted.json"}:
            raise OSError("Injected optional monitoring failure")
        return write(path, content)
    monkeypatch.setattr(transport, "_write", fail_monitor)
    assert value.complete(prompt) == "done"
    assert value.complete(prompt) == "done"
    assert len(launches) == 1


def test_public_output_parser_ignores_started_and_commentary_and_malformed_rows(tmp_path):
    (tmp_path / "stdout.jsonl").write_text("\n".join([
        "not json", json.dumps({"type": "item.started", "item": {"type": "agent_message", "text": "incomplete"}}),
        json.dumps(message("commentary", phase="commentary")), json.dumps(message("answer")),
        json.dumps({"type": "turn.completed", "usage": {"input_tokens": "unknown"}})]), encoding="utf-8")
    result = transport.inspect_output(tmp_path)
    assert result["answer"] == "answer" and result["usage"] == {}
    assert result["warnings"]


def test_executable_resolution_is_local_and_performs_no_process_probe(tmp_path, monkeypatch):
    executable = tmp_path / "codex.exe"
    executable.write_bytes(b"offline fixture")
    monkeypatch.setattr(transport.subprocess, "Popen", lambda *a, **k: pytest.fail("No real process allowed"))
    monkeypatch.setattr(transport.shutil, "which", lambda name: str(executable))
    monkeypatch.delenv("CODEX_EXECUTABLE", raising=False)
    assert transport.resolve_executable() == executable.resolve()
    assert transport.resolve_executable(executable) == executable.resolve()


def test_formal_cli_run_needs_no_profile_or_confirmation_and_monitoring_is_optional(tmp_path, monkeypatch, capsys):
    from tools.doe import document_guided_pilot as pilot
    stages = []
    class Local:
        def __init__(self, directory, **kwargs):
            stages.append((directory, kwargs))
    def run(directory, *, client_factory, progress):
        client_factory("graph", directory / "steps/graph")
        return {"status": "complete"}
    monkeypatch.setattr(transport, "Client", Local)
    monkeypatch.setattr(pilot, "run", run)
    monkeypatch.setattr(pilot, "transport_metrics", lambda path: (_ for _ in ()).throw(ValueError("monitor unavailable")))
    (tmp_path / "manifest.json").write_text(json.dumps({"config": {"model": "gpt-6.1-sol",
        "reasoning_effort": "max", "response_format": "json_object"}}), encoding="utf-8")
    assert pilot.main(["run", "--run-dir", str(tmp_path)]) == 0
    assert stages[0][1]["retries"] == 2 and stages[0][1]["executable"] is None
    assert "monitor unavailable" in capsys.readouterr().err
    assert not (tmp_path / "transport-profile.json").exists()


def test_formal_prepare_and_replay_never_instantiate_cli_client(tmp_path, monkeypatch):
    from tools.doe import document_guided_pilot as pilot
    monkeypatch.setattr(transport, "Client", lambda *a, **k: pytest.fail("No CLI creation allowed"))
    monkeypatch.setattr(pilot, "prepare", lambda source, run_dir, config: {"status": "prepared"})
    monkeypatch.setattr(pilot, "replay", lambda run_dir: {"status": "diagnostic_complete"})
    assert pilot.main(["prepare", "--input", "source", "--run-dir", str(tmp_path)]) == 0
    assert pilot.main(["replay", "--run-dir", str(tmp_path)]) == 0
