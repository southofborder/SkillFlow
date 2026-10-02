"""Shared recording preserves accepted responses, isolation and no-resend rules."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from skill_ir import recording
from skill_ir.backtrace import runner
from skill_ir.experiments.report import ArtifactWriter


class Factory:
    def __init__(self, directory, *, interrupt=False, incomplete=False, secret=""):
        self.directory = directory
        self.interrupt, self.incomplete, self.secret = interrupt, incomplete, secret
        self.prompts = []

    def __call__(self, writer, checkpoint):
        factory = self

        class Client:
            def complete(self, prompt):
                assert recording.read_json(factory.directory / "call.json")["status"] == "running"
                factory.prompts.append(prompt)
                response = {"content": "response", "model": "fake"}
                checkpoint([{
                    "status": "error" if factory.incomplete else "complete",
                    "prompt": prompt, "response": None if factory.incomplete else response,
                    "error": factory.secret,
                    "returned_model": "fake", "usage": {"total_tokens": 7},
                    "http_attempts": [{"http_status": 503}, {"http_status": 200}],
                }])
                if factory.interrupt:
                    raise KeyboardInterrupt("after transport checkpoint " + factory.secret)
                if factory.incomplete:
                    raise RuntimeError("incomplete accepted response " + factory.secret)
                return response
        return Client()


def forbidden(*args):
    pytest.fail("This path must never create or call an online client")


def recorded_http(tmp_path, monkeypatch, *, failure=False):
    import io
    import urllib.error
    from skill_ir.llm import LlmClient, LlmConfig, LlmClientError

    class Response:
        status = 200
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"choices":[{"finish_reason":"stop","message":{"content":"{}"}}]}'

    def request(req, timeout):
        if failure:
            raise urllib.error.HTTPError(req.full_url, 400, "unsupported", {}, io.BytesIO(b"response_format unsupported"))
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", request)
    config = {"model": "offline", "reasoning_effort": "high", "response_format": "json_object"}
    writer = ArtifactWriter(())
    factory = lambda writer, checkpoint: LlmClient(LlmConfig(api_key="test-secret", **config), record_calls=True, on_record=checkpoint)
    client = recording.RecordingClient(tmp_path, factory, writer)
    if failure:
        with pytest.raises(LlmClientError):
            client.complete("checked JSON 中文")
    else:
        assert client.complete("checked JSON 中文") == "{}"
    return config


@pytest.mark.parametrize("failure", [False, True])
def test_http_request_identity_checks_public_parameters_on_success_and_failure(tmp_path, monkeypatch, failure):
    config = recorded_http(tmp_path, monkeypatch, failure=failure)
    summary = recording.verify_request_identity(tmp_path, config, prompt="checked JSON 中文")
    assert summary["observed"] is True and summary["transport"] == "http"
    assert summary["requests"][0]["request_parameters"]["response_format"] == {"type": "json_object"}
    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    assert summary == recording.verify_request_identity(tmp_path, config, prompt="checked JSON 中文")


@pytest.mark.parametrize("mutation", ["parameters", "body", "missing", "config", "prompt", "old"])
def test_request_identity_rejects_rehashed_tampering_or_old_records(tmp_path, monkeypatch, mutation):
    config = recorded_http(tmp_path, monkeypatch)
    trace = recording.read_json(tmp_path / "transport.json")
    attempt = trace[0]["http_attempts"][0]
    prompt = "checked JSON 中文"
    if mutation == "parameters":
        attempt["request_parameters"]["response_format"] = {"type": "text"}
    elif mutation == "body":
        attempt["request_body_sha256"] = "0" * 64
    elif mutation == "missing":
        attempt.pop("request_parameters")
    elif mutation == "config":
        config["response_format"] = None
    elif mutation == "prompt":
        prompt += "changed"
    else:
        trace[0].pop("request_parameters_observed")
    trace[0].pop("record_sha256")
    trace[0]["record_sha256"] = recording.canonical_sha256(trace[0])
    ArtifactWriter(()).json(tmp_path / "transport.json", trace)
    with pytest.raises(recording.ResponseIntegrityError, match="Request identity"):
        recording.verify_request_identity(tmp_path, config, prompt=prompt)


def test_injected_request_identity_is_explicitly_unobserved(tmp_path):
    class Plain:
        def complete(self, prompt):
            return "{}"

    recording.RecordingClient(tmp_path, recording.injected_factory(Plain()), ArtifactWriter(())).complete("JSON")
    summary = recording.verify_request_identity(tmp_path, {"response_format": "json_object"}, prompt="JSON")
    assert summary["observed"] is False and summary["transport"] == "injected" and summary["requests"] == []
    trace = recording.read_json(tmp_path / "transport.json")
    trace[0].pop("request_parameters_observed")
    trace[0].pop("record_sha256")
    trace[0]["record_sha256"] = recording.canonical_sha256(trace[0])
    ArtifactWriter(()).json(tmp_path / "transport.json", trace)
    with pytest.raises(recording.ResponseIntegrityError, match="Injected"):
        recording.verify_request_identity(tmp_path, {}, prompt="JSON")


def test_pre_request_failure_does_not_claim_observed_http_parameters(tmp_path):
    writer = ArtifactWriter(())

    def factory(writer, checkpoint):
        class Client:
            def complete(self, prompt):
                checkpoint([{"status": "error", "prompt": prompt, "response": None,
                             "http_attempts_observed": True, "request_parameters_observed": True,
                             "http_attempts": []}])
                raise RuntimeError("before request")
        return Client()

    with pytest.raises(RuntimeError):
        recording.RecordingClient(tmp_path, factory, writer).complete("JSON")
    summary = recording.verify_request_identity(tmp_path, {}, prompt="JSON")
    assert summary["observed"] is False and summary["transport"] == "not_started"


def test_existing_runner_imports_the_single_shared_implementation():
    for name in ("RecordingClient", "SavedResponseClient", "SavedCallFailure", "validated_trace",
                 "implementation_provenance"):
        assert getattr(runner, name) is getattr(recording, name)
    # Online factory selection was moved to the CLI; the offline runner does
    # not keep an unused public import merely to satisfy the historical test.
    from skill_ir.backtrace import __main__ as cli
    assert cli.streaming_factory is recording.streaming_factory


def test_complete_call_durable_trace_and_exact_offline_response(tmp_path):
    writer = ArtifactWriter(())
    factory = Factory(tmp_path)
    client = recording.RecordingClient(tmp_path, factory, writer)
    response = client.complete("checked prompt")
    record = recording.read_json(tmp_path / "call.json")
    assert record["status"] == "complete"
    assert record["response_sha256"] == recording.canonical_sha256(response)
    trace = recording.validated_trace(tmp_path / "transport.json")
    assert len(trace) == 1 and len(trace[0]["http_attempts"]) == 2
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    saved = recording.SavedResponseClient(tmp_path, writer)
    assert saved.complete("checked prompt") == response
    assert len(factory.prompts) == 1
    assert before == {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    with pytest.raises(ValueError, match="one logical model call"):
        saved.complete("checked prompt")
    with pytest.raises(ValueError, match="one logical model call"):
        client.complete("checked prompt")


def test_completed_transport_survives_interruption_without_resending(tmp_path):
    writer = ArtifactWriter(())
    factory = Factory(tmp_path, interrupt=True)
    with pytest.raises(KeyboardInterrupt):
        recording.RecordingClient(tmp_path, factory, writer).complete("checked")
    assert recording.read_json(tmp_path / "call.json")["status"] == "interrupted"
    saved = recording.SavedResponseClient(tmp_path, writer)
    assert saved.complete("checked") == {"content": "response", "model": "fake"}
    with pytest.raises(ValueError, match="already exists"):
        recording.RecordingClient(tmp_path, forbidden, writer).complete("checked")
    assert factory.prompts == ["checked"]


def test_incomplete_accepted_response_remains_error_and_secrets_are_redacted(tmp_path):
    secret = "synthetic-private-credential"
    writer = ArtifactWriter((secret,))
    factory = Factory(tmp_path, incomplete=True, secret=secret)
    with pytest.raises(RuntimeError):
        recording.RecordingClient(tmp_path, factory, writer).complete("checked")
    with pytest.raises(recording.SavedCallFailure) as error:
        recording.SavedResponseClient(tmp_path, writer).complete("checked")
    assert error.value.error_type == "RuntimeError"
    assert secret not in str(error.value)
    for path in tmp_path.iterdir():
        assert secret.encode() not in path.read_bytes()
    with pytest.raises(ValueError, match="already exists"):
        recording.RecordingClient(tmp_path, forbidden, writer).complete("checked")
    assert factory.prompts == ["checked"]


def test_credential_overlap_in_prompt_is_rejected_before_recording_or_transmission(tmp_path):
    writer = ArtifactWriter(("synthetic-private-credential",))
    with pytest.raises(ValueError, match="credential overlaps"):
        recording.RecordingClient(tmp_path, forbidden, writer).complete(
            "source contains synthetic-private-credential"
        )
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("interrupt", [False, True])
def test_plain_client_adapter_records_unknown_http_counts_and_replays(tmp_path, interrupt):
    class PlainClient:
        calls = 0

        def complete(self, prompt):
            self.calls += 1
            assert recording.validated_trace(tmp_path / "transport.json")[0]["status"] == "running"
            if interrupt:
                raise KeyboardInterrupt("injected interruption")
            return {"answer": "recorded"}

    plain = PlainClient()
    writer = ArtifactWriter(())
    client = recording.RecordingClient(tmp_path, recording.injected_factory(plain), writer)
    if interrupt:
        with pytest.raises(KeyboardInterrupt):
            client.complete("checked")
        with pytest.raises(recording.SavedCallFailure) as failure:
            recording.SavedResponseClient(tmp_path, writer).complete("checked")
        assert failure.value.error_type == "KeyboardInterrupt"
    else:
        assert client.complete("checked") == {"answer": "recorded"}
        assert recording.SavedResponseClient(tmp_path, writer).complete("checked") == {"answer": "recorded"}
    trace = recording.validated_trace(tmp_path / "transport.json")
    assert trace[0]["transport"] == "injected"
    assert trace[0]["http_attempts"] == []
    assert trace[0]["http_attempts_observed"] is False
    assert trace[0]["returned_model"] is None and trace[0]["usage"] is None
    assert plain.calls == 1


@pytest.mark.parametrize("corrupt", ["prompt", "response", "trace", "trace_response"])
def test_replay_refuses_tampering_even_for_accepted_response(tmp_path, corrupt):
    writer = ArtifactWriter(())
    recording.RecordingClient(tmp_path, Factory(tmp_path), writer).complete("checked")
    call_path, trace_path = tmp_path / "call.json", tmp_path / "transport.json"
    call = recording.read_json(call_path)
    trace = recording.read_json(trace_path)
    if corrupt == "prompt":
        call["prompt_sha256"] = "invalid"
    elif corrupt == "response":
        call["response"]["content"] = "changed"
    elif corrupt == "trace":
        trace[0]["returned_model"] = "changed"
    else:
        trace[0]["response"]["content"] = "changed"
        unsigned = deepcopy(trace[0]); unsigned.pop("record_sha256")
        trace[0]["record_sha256"] = recording.canonical_sha256(unsigned)
    writer.json(call_path, call)
    writer.json(trace_path, trace)
    with pytest.raises(ValueError, match="mismatch|disagree"):
        recording.SavedResponseClient(tmp_path, writer).complete("checked")


@pytest.mark.parametrize("mismatch", ["response", "json_type", "prompt", "incomplete", "absent", "multiple"])
def test_returned_response_requires_one_exact_complete_transport_and_cannot_recover(tmp_path, mismatch):
    def factory(writer, checkpoint):
        class Client:
            def complete(self, prompt):
                response = {"value": 1}
                trace = [{"status": "complete", "prompt": prompt, "response": deepcopy(response),
                          "http_attempts": []}]
                if mismatch == "response":
                    trace[0]["response"] = {"value": "different"}
                elif mismatch == "json_type":
                    trace[0]["response"] = {"value": True}
                elif mismatch == "prompt":
                    trace[0]["prompt"] = "different"
                elif mismatch == "incomplete":
                    trace[0]["status"] = "running"
                elif mismatch == "absent":
                    trace = []
                else:
                    trace.append(deepcopy(trace[0]))
                checkpoint(trace)
                return response
        return Client()

    writer = ArtifactWriter(())
    with pytest.raises(recording.ResponseIntegrityError):
        recording.RecordingClient(tmp_path, factory, writer).complete("checked")
    record = recording.read_json(tmp_path / "call.json")
    assert record["status"] == "invalid_record" and record["response_rejected"] is True
    with pytest.raises(recording.SavedCallFailure) as error:
        recording.SavedResponseClient(tmp_path, writer).complete("checked")
    assert error.value.error_type == "ResponseIntegrityError"


@pytest.mark.parametrize("checkpoint_first", [False, True])
def test_redacted_response_is_durably_rejected_not_replayed_as_a_substitute(tmp_path, checkpoint_first):
    secret = "synthetic-private-credential"
    writer = ArtifactWriter((secret,))

    def factory(writer, checkpoint):
        class Client:
            def complete(self, prompt):
                response = {"content": secret}
                if checkpoint_first:
                    checkpoint([{"status": "complete", "prompt": prompt, "response": response,
                                 "http_attempts": []}])
                    pytest.fail("A credential-bearing complete checkpoint must stop before another event")
                return response
        return Client()

    with pytest.raises(recording.ResponseIntegrityError, match="credential overlaps"):
        recording.RecordingClient(tmp_path, factory, writer).complete("checked")
    record = recording.read_json(tmp_path / "call.json")
    assert record["status"] == "invalid_record" and record["response_rejected"] is True
    # Offline replay intentionally does not load the original credentials.
    with pytest.raises(recording.SavedCallFailure) as error:
        recording.SavedResponseClient(tmp_path, ArtifactWriter(())).complete("checked")
    assert error.value.error_type == "ResponseIntegrityError"
    for path in tmp_path.iterdir():
        assert secret.encode() not in path.read_bytes()


def _deny_json_writes(monkeypatch, writer, predicate, message="synthetic local disk failure"):
    """Exercise the real atomic writer's error boundary, not a network stub."""
    from skill_ir import artifact_io

    original_json = writer.json
    denied = []

    def json_write(path, value):
        path = Path(path)
        if not predicate(path, value):
            return original_json(path, value)
        denied.append(path)

        def deny_replace(source, target):
            raise PermissionError(13, message, str(target))

        with monkeypatch.context() as local:
            local.setattr(artifact_io.os, "replace", deny_replace)
            return original_json(path, value)

    monkeypatch.setattr(writer, "json", json_write)
    return denied


def _assert_no_saved_secret(directory, secret):
    for path in directory.rglob("*"):
        if path.is_file():
            assert secret.encode() not in path.read_bytes(), path


def test_injected_first_error_survives_terminal_checkpoint_failure(tmp_path, monkeypatch):
    secret = "synthetic-recording-private-credential"
    writer = ArtifactWriter((secret,))
    primary = TimeoutError("business operation timed out " + secret)

    class PlainClient:
        calls = 0

        def complete(self, prompt):
            self.calls += 1
            raise primary

    plain = PlainClient()
    denied = _deny_json_writes(
        monkeypatch, writer,
        lambda path, value: path.name == "transport.json" and value[0]["status"] != "running",
        "terminal checkpoint cannot be persisted " + secret,
    )
    with pytest.raises(TimeoutError) as error:
        recording.RecordingClient(tmp_path, recording.injected_factory(plain), writer).complete("checked")
    assert error.value is primary
    assert primary.recording_failed is True
    assert primary.recording_errors[-1]["error_type"] == "ArtifactWriteError"
    record = recording.read_json(tmp_path / "call.json")
    assert record["status"] == "error" and record["error_type"] == "TimeoutError"
    assert record["recording_failed"] is True
    assert record["recording_errors"][-1]["error_type"] == "ArtifactWriteError"
    assert "business operation timed out" in record["error"]
    assert "transport.json" in record["recording_errors"][-1]["error"]
    assert plain.calls == 1 and denied
    _assert_no_saved_secret(tmp_path, secret)
    with pytest.raises(recording.SavedCallFailure) as saved:
        recording.SavedResponseClient(tmp_path, ArtifactWriter(())).complete("checked")
    assert saved.value.error_type == "TimeoutError"


@pytest.mark.parametrize("outer_error_context", [False, True])
def test_complete_transport_recovers_offline_after_final_call_save_failure(tmp_path, monkeypatch, outer_error_context):
    from skill_ir.artifact_io import ArtifactWriteError

    writer = ArtifactWriter(())
    factory = Factory(tmp_path)
    denied = _deny_json_writes(
        monkeypatch, writer,
        lambda path, value: path.name == "call.json" and value["status"] != "running",
    )
    client = recording.RecordingClient(tmp_path, factory, writer)
    if outer_error_context:
        try:
            raise RuntimeError("unrelated error handled by caller")
        except RuntimeError:
            with pytest.raises(ArtifactWriteError):
                client.complete("checked")
    else:
        with pytest.raises(ArtifactWriteError):
            client.complete("checked")
    # A failed final checkpoint cannot turn the live execution into a success.
    assert recording.read_json(tmp_path / "call.json")["status"] == "running"
    assert recording.validated_trace(tmp_path / "transport.json")[0]["status"] == "complete"
    assert denied and factory.prompts == ["checked"]
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    monkeypatch.setattr(recording, "streaming_factory", forbidden)
    monkeypatch.setattr(recording, "injected_factory", forbidden)
    assert recording.SavedResponseClient(tmp_path, writer).complete("checked") == {"content": "response", "model": "fake"}
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    with pytest.raises(ValueError, match="already exists"):
        recording.RecordingClient(tmp_path, forbidden, writer).complete("checked")
    assert factory.prompts == ["checked"]


@pytest.mark.parametrize("failure", ["response", "final_call", "terminal_error_checkpoint"])
def test_persistence_failure_never_starts_second_audit_execution(tmp_path, monkeypatch, failure):
    from skill_ir.audit_execution import RetryingAuditClient
    from skill_ir.artifact_io import ArtifactWriteError

    secret = "synthetic-recording-private-credential"
    writer = ArtifactWriter((secret,))

    class PlainClient:
        calls = 0

        def complete(self, prompt):
            self.calls += 1
            if failure == "terminal_error_checkpoint":
                raise TimeoutError("first transport timeout " + secret)
            return {"answer": "accepted exactly once"}

    plain = PlainClient()

    def deny(path, value):
        if failure == "response":
            return path.name == "response.json"
        if failure == "final_call":
            return path.name == "call.json" and value["status"] != "running"
        return path.name == "transport.json" and value[0]["status"] != "running"

    denied = _deny_json_writes(monkeypatch, writer, deny, "persistent local write failure " + secret)
    executions, decisions = [], []

    def execute(prompt):
        directory = tmp_path / f"a{len(executions) + 1:03}"
        executions.append(directory)
        return recording.RecordingClient(directory, recording.injected_factory(plain), writer).complete(prompt)

    client = RetryingAuditClient(
        execute=execute, retries=2,
        call_path=lambda attempt: (tmp_path / f"a{attempt:03}", f"a{attempt:03}"),
        persist=lambda attempt, decision: decisions.append(deepcopy(decision)),
        wait_for_retry=lambda *args: pytest.fail("Storage failure must not cause a second model call"),
    )
    expected_error = TimeoutError if failure == "terminal_error_checkpoint" else ArtifactWriteError
    with pytest.raises(expected_error):
        client.complete("checked")
    assert len(executions) == plain.calls == 1
    assert denied and len(decisions) == 1
    assert decisions[0]["retry"] is False and decisions[0]["eligible"] is False
    assert not (tmp_path / "a002").exists()
    _assert_no_saved_secret(tmp_path, secret)
    assert secret not in json.dumps(decisions)


def test_secondary_recording_failure_blocks_retry_even_with_matching_timeout_records(tmp_path):
    """A durable timeout is still non-retryable when its recording failed too."""
    from skill_ir.audit_execution import classify_failure

    writer = ArtifactWriter(())
    prompt = "checked"
    secondary = [{"error": "local checkpoint failed", "error_type": "ArtifactWriteError"}]
    trace = {
        "status": "error", "prompt": prompt, "response": None,
        "error": "timed out", "error_type": "TimeoutError", "http_attempts": [],
        "recording_failed": True, "recording_errors": secondary,
    }
    trace["record_sha256"] = recording.canonical_sha256(trace)
    writer.json(tmp_path / "transport.json", [trace])
    writer.json(tmp_path / "call.json", {
        "status": "error", "prompt": prompt, "prompt_sha256": recording.canonical_sha256(prompt),
        "error": "timed out", "error_type": "TimeoutError",
        "recording_failed": True, "recording_errors": secondary,
    })
    assert classify_failure(tmp_path, prompt)["eligible"] is False
