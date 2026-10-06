"""Offline transport framing, accounting, isolation, and pipeline integration."""

from skillflow.common.paths import project_root, resolve_material_path

from copy import deepcopy
import hashlib
import importlib
import io
import json
from pathlib import Path
import threading
import urllib.error

import pytest

from skillflow.common.artifact_io import ArtifactWriteError
from skillflow.graph.experiments import resumable
from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.llm.config import LlmClientError
from skillflow.common.llm.config import LlmConfig
from skillflow.common.llm.config import OutputTruncatedError
from skillflow.common import recording


BASE = project_root() / "experiments/graph/baseline"
CANDIDATE = {
    "entry_block_ref": "finish", "constraints": ["保留原文约束"],
    "blocks": [{"block_ref": "finish", "block_name": "完成", "instructions": [{
        "instruction_ref": "finish", "opcode": "return",
        "inputs": [{"type": "literal", "literal_value": "完成"}],
    }]}], "edges": [],
}


def event(content=None, *, finish=None, usage=None, choice=True):
    return {
        "id": "chat-test", "model": "gpt-5.6-sol", "object": "chat.completion.chunk",
        "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": finish}] if choice else [],
        "usage": usage,
    }


def wire(*events, done=True, newline="\n"):
    value = "".join("data: " + json.dumps(item, ensure_ascii=False) + newline * 2 for item in events)
    if done:
        value += "data: [DONE]" + newline * 2
    return value.encode("utf-8")


class Response:
    status = 200

    def __init__(self, chunks, content_type="text/event-stream; charset=utf-8"):
        self.chunks = list(chunks)
        self.headers = {"Content-Type": content_type, "x-request-id": "stream-request"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read1(self, size):
        value = self.chunks.pop(0) if self.chunks else b""
        if isinstance(value, BaseException):
            raise value
        return value

    def read(self, size=None):
        return self.read1(size)


@pytest.fixture
def modules(monkeypatch):

    transport = importlib.import_module("skillflow.common.llm.stream_transport")
    entry = importlib.import_module("tools.graph.baseline.run_streaming_baseline")

    def forbidden(*args, **kwargs):
        pytest.fail("No real network is allowed")

    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    return transport, entry


def client(transport):
    checkpoints = []
    result = transport.StreamingReplayClient(
        LlmConfig(api_key="stream-test-secret", endpoint="https://offline.invalid/v1", retry_base_ms=1, retry_max_backoff_ms=1),
        prior_calls=[], writer=ArtifactWriter(("stream-test-secret",)),
        on_record=lambda calls: checkpoints.append(deepcopy(calls)),
    )
    return result, checkpoints


def test_streamed_chinese_usage_request_identity_and_lossless_trace(modules, monkeypatch):
    transport, _ = modules
    raw = b": heartbeat\r\n\r\n" + wire(
        event("中文"), event("回答"), event(finish="stop"),
        event(usage={"prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10}, choice=False),
        newline="\r\n",
    )
    requests = []

    def respond(request, timeout):
        requests.append((json.loads(request.data), timeout))
        return Response([raw[i:i + 7] for i in range(0, len(raw), 7)])

    monkeypatch.setattr("urllib.request.urlopen", respond)
    item, checkpoints = client(transport)
    assert item.complete("原始完整 Prompt") == "中文回答"
    assert requests == [({
        "model": "gpt-5.6-sol", "messages": [{"role": "user", "content": "原始完整 Prompt"}],
        "reasoning_effort": "max", "stream": True, "stream_options": {"include_usage": True},
    }, 600.0)]
    record = item.call_records[0]
    attempt = record["http_attempts"][0]
    state = attempt["stream"]
    assert state["raw_sse"].encode("utf-8") == raw
    assert state["wire_sha256"] == hashlib.sha256(raw).hexdigest()
    assert state["headers_received_at"] <= state["first_byte_at"] <= state["first_event_at"] <= state["first_content_at"]
    assert state["done_received"] and state["finish_reason"] == "stop"
    assert state["outcome"] == "complete" and attempt["request_id"] == "stream-request"
    assert record["usage"]["total_tokens"] == 10
    assert checkpoints[-1][0]["status"] == "complete"


def test_slow_full_snapshots_wait_five_seconds_after_write_completion(modules, monkeypatch):
    transport, _ = modules
    clock = [0.0]
    monkeypatch.setattr(transport.time, "monotonic", lambda: clock[0])
    requests, snapshots = [], []
    chunks = [wire(event("字"), done=False) for _ in range(12)]
    chunks.append(wire(event(finish="stop")))

    class TimedResponse(Response):
        def read1(self, size):
            clock[0] += 1.0
            return super().read1(size)

    def respond(*args, **kwargs):
        requests.append(1)
        return TimedResponse(chunks)

    def checkpoint(calls):
        attempts = calls[0]["http_attempts"]
        state = attempts[-1].get("stream") if attempts else None
        if state is not None:
            start = clock[0]
            clock[0] += 8.0  # Writing costs more than the checkpoint interval.
            snapshots.append({"start": start, "finished": clock[0], **deepcopy(state)})

    monkeypatch.setattr("urllib.request.urlopen", respond)
    item, _ = client(transport)
    item._on_record = checkpoint
    assert item.complete("original") == "字" * 12
    periodic = [s for s in snapshots if s["outcome"] == "pending" and s["received_bytes"]]
    assert [len(s["partial_content"]) for s in periodic] == [5, 10]
    assert periodic[1]["start"] - periodic[0]["finished"] == 5.0
    assert snapshots[-1]["outcome"] == "complete"
    assert snapshots[-1]["raw_sse"].encode("utf-8") == b"".join(chunks)
    assert snapshots[-1]["done_received"] is True
    assert len(requests) == 1


def test_json_output_sse_actual_request_identity_and_offline_check(modules, tmp_path, monkeypatch):
    transport, _ = modules
    requests = []
    config = {"model": "offline", "response_format": "json_object"}

    def respond(request, timeout):
        requests.append(request.data)
        return Response([wire(event("{}"), event(finish="stop"))])

    monkeypatch.setattr("urllib.request.urlopen", respond)
    factory = lambda writer, checkpoint: transport.StreamingReplayClient(
        LlmConfig(api_key="test-secret", **config), prior_calls=[], writer=writer, on_record=checkpoint)
    assert recording.RecordingClient(tmp_path, factory, ArtifactWriter(())).complete("原始 JSON") == "{}"
    payload = json.loads(requests[0])
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["stream"] is True
    metadata = recording.verify_request_identity(tmp_path, config, prompt="原始 JSON")
    assert metadata["requests"][0]["request_body_sha256"] == hashlib.sha256(requests[0]).hexdigest()
    expected = {key: value for key, value in payload.items() if key != "messages"}
    assert metadata["requests"][0]["request_parameters"] == expected
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("offline check"))
    assert recording.SavedResponseClient(tmp_path, ArtifactWriter(())).complete("原始 JSON") == "{}"
    assert recording.verify_request_identity(tmp_path, config, prompt="原始 JSON") == metadata
    trace = recording.read_json(tmp_path / "transport.json")
    trace[0]["http_attempts"][0]["stream"]["request_parameters"].pop("response_format")
    trace[0].pop("record_sha256")
    trace[0]["record_sha256"] = recording.canonical_sha256(trace[0])
    ArtifactWriter(()).json(tmp_path / "transport.json", trace)
    with pytest.raises(recording.ResponseIntegrityError, match="SSE request_parameters"):
        recording.verify_request_identity(tmp_path, config, prompt="原始 JSON")


def test_sse_length_finish_is_truncated_error_without_retry(modules, tmp_path, monkeypatch):
    transport, _ = modules
    raw = wire(event("{}"), event(finish="length"))
    requests = []

    def respond(request, timeout):
        requests.append(request)
        return Response([raw])

    monkeypatch.setattr("urllib.request.urlopen", respond)
    config = {"response_format": "json_object"}
    factory = lambda writer, checkpoint: transport.StreamingReplayClient(
        LlmConfig(api_key="test-secret", **config), prior_calls=[], writer=writer, on_record=checkpoint)
    with pytest.raises(OutputTruncatedError, match="finish_reason=length"):
        recording.RecordingClient(tmp_path, factory, ArtifactWriter(())).complete("JSON")
    trace = recording.validated_trace(tmp_path / "transport.json")
    assert len(requests) == 1 and trace[0]["status"] == "error"
    attempt = trace[0]["http_attempts"][0]
    assert attempt["http_status"] == 200
    assert attempt["stream"]["outcome"] == "output_truncated"
    assert attempt["stream"]["partial_content"] == "{}"
    assert attempt["stream"]["done_received"] is True
    assert recording.verify_request_identity(tmp_path, config, prompt="JSON")["observed"] is True
    with pytest.raises(recording.SavedCallFailure) as error:
        recording.SavedResponseClient(tmp_path, ArtifactWriter(())).complete("JSON")
    assert error.value.error_type == "OutputTruncatedError"


def test_midstream_local_recording_error_keeps_partial_facts_and_never_retries_http(modules, monkeypatch):
    transport, _ = modules
    clock = [0.0]
    monkeypatch.setattr(transport.time, "monotonic", lambda: clock[0])
    prefix = wire(event("已接收的内容"), done=False)
    requests, failures = [], []
    failure = ArtifactWriteError(Path("transport.json"), "replace")

    class TimedResponse(Response):
        def read1(self, size):
            clock[0] += 5.0
            return super().read1(size)

    def respond(*args, **kwargs):
        requests.append(1)
        return TimedResponse([prefix, wire(event(finish="stop"))])

    def checkpoint(calls):
        attempts = calls[0]["http_attempts"]
        state = attempts[-1].get("stream") if attempts else None
        if state and state["received_bytes"] and not failures:
            failures.append(failure)
            raise failure

    monkeypatch.setattr("urllib.request.urlopen", respond)
    item, _ = client(transport)
    item._on_record = checkpoint
    with pytest.raises(ArtifactWriteError) as caught:
        item.complete("original")
    assert caught.value is failure
    assert "network failure" not in str(caught.value)
    assert len(requests) == 1
    attempt = item.call_records[0]["http_attempts"][0]
    state = attempt["stream"]
    assert attempt["http_status"] == 200 and attempt["recording_failed"] is True
    assert state["outcome"] == "recording_error"
    assert state["raw_sse"].encode("utf-8") == prefix
    assert state["received_bytes"] == len(prefix)
    assert state["partial_content"] == "已接收的内容"
    assert state["done_received"] is False and state["finish_reason"] is None
    assert item.call_records[0]["response"] is None


@pytest.mark.parametrize("inside_caller_exception", [False, True])
def test_completed_sse_final_write_failure_preserves_completion_facts_without_resend(
    modules, monkeypatch, inside_caller_exception,
):
    transport, _ = modules
    raw = wire(event("完整响应"), event(finish="stop"))
    requests, failures = [], []
    failure = ArtifactWriteError(Path("transport.json"), "replace")

    def respond(*args, **kwargs):
        requests.append(1)
        return Response([raw])

    def checkpoint(calls):
        attempts = calls[0]["http_attempts"]
        state = attempts[-1].get("stream") if attempts else None
        if state and state["outcome"] == "complete" and not failures:
            failures.append(failure)
            raise failure

    monkeypatch.setattr("urllib.request.urlopen", respond)
    item, _ = client(transport)
    item._on_record = checkpoint

    def invoke():
        if inside_caller_exception:
            try:
                raise RuntimeError("previous caller error, unrelated to this request")
            except RuntimeError:
                return item.complete("original")
        return item.complete("original")

    with pytest.raises(ArtifactWriteError) as caught:
        invoke()
    assert caught.value is failure and caught.value.recording_failed is True
    assert len(requests) == 1
    attempt = item.call_records[0]["http_attempts"][0]
    state = attempt["stream"]
    assert attempt["http_status"] == 200 and attempt["recording_failed"] is True
    assert state["outcome"] == "complete"
    assert state["done_received"] is True and state["finish_reason"] == "stop"
    assert state["received_bytes"] == len(raw)
    assert state["raw_sse"].encode("utf-8") == raw
    assert state["partial_content"] == "完整响应"
    assert item.call_records[0]["status"] == "error"


def test_final_record_error_preserves_primary_network_error_and_blocks_its_retry(modules, monkeypatch):
    transport, _ = modules
    requests, failures = [], []

    def respond(*args, **kwargs):
        requests.append(1)
        raise urllib.error.URLError("connection reset before headers")

    def checkpoint(calls):
        attempts = calls[0]["http_attempts"]
        state = attempts[-1].get("stream") if attempts else None
        if state and state["outcome"] == "network_error" and not failures:
            failures.append(1)
            raise ArtifactWriteError(Path("transport.json"), "replace")

    monkeypatch.setattr("urllib.request.urlopen", respond)
    item, _ = client(transport)
    item._on_record = checkpoint
    with pytest.raises(LlmClientError, match="connection reset before headers") as caught:
        item.complete("original")
    assert caught.value.recording_failed is True
    assert caught.value.transient is False
    assert caught.value.recording_errors[0]["error_type"] == "ArtifactWriteError"
    assert len(requests) == 1
    attempt = item.call_records[0]["http_attempts"][0]
    assert attempt["recording_failed"] is True
    assert attempt["http_status"] is None
    assert attempt["stream"]["outcome"] == "network_error"
    assert attempt["stream"]["received_bytes"] == 0


@pytest.mark.parametrize("failure", ["missing_done", "missing_finish", "truncated", "timeout_after_partial", "timeout_before_event", "invalid_utf8", "sse_error", "wrong_type"])
def test_incomplete_or_invalid_stream_never_retried_or_accepted(modules, monkeypatch, failure):
    transport, _ = modules
    prefix = wire(event("部分中文"), done=False)
    bodies = {
        "missing_done": [prefix + wire(event(finish="stop"), done=False)],
        "missing_finish": [prefix + b"data: [DONE]\n\n"],
        "truncated": [prefix + b'data: {"choices":'],
        "timeout_after_partial": [prefix, TimeoutError("read timeout")],
        "timeout_before_event": [TimeoutError("read timeout")],
        "invalid_utf8": [prefix, b"\xff"],
        "sse_error": [prefix + b'event: error\ndata: {"error":{"message":"failed"}}\n\n'],
        "wrong_type": [b'{"choices": []}'],
    }
    requests = []

    def respond(*args, **kwargs):
        requests.append(1)
        return Response(bodies[failure], content_type="application/json" if failure == "wrong_type" else "text/event-stream")

    monkeypatch.setattr("urllib.request.urlopen", respond)
    item, _ = client(transport)
    with pytest.raises(LlmClientError):
        item.complete("original")
    assert len(requests) == 1
    assert item.call_records[0]["status"] == "error"
    state = item.call_records[0]["http_attempts"][0]["stream"]
    assert item.call_records[0]["http_attempts"][0]["http_status"] == 200
    assert state["outcome"] == "remote_outcome_unknown"
    if failure not in {"wrong_type", "timeout_before_event"}:
        assert state["partial_content"] == "部分中文"
        assert "部分中文" in state["raw_sse"]
    if failure == "timeout_before_event":
        assert state["first_byte_at"] is state["first_event_at"] is None
    assert item.call_records[0]["response"] is None


def test_524_before_headers_retries_but_unsupported_usage_does_not(modules, monkeypatch):
    transport, _ = modules
    requests = []

    def respond(request, timeout):
        requests.append(1)
        if len(requests) == 1:
            raise urllib.error.HTTPError(request.full_url, 524, "timeout", {"Retry-After": "0"}, io.BytesIO(b"origin timeout"))
        return Response([wire(event("ok"), event(finish="stop"))])

    monkeypatch.setattr("urllib.request.urlopen", respond)
    item, _ = client(transport)
    assert item.complete("original") == "ok"
    assert len(requests) == 2
    assert item.call_records[0]["http_attempts"][0]["http_status"] == 524
    assert item.call_records[0]["usage"] is None

    def unsupported(request, timeout):
        requests.append(1)
        raise urllib.error.HTTPError(request.full_url, 400, "unsupported", {}, io.BytesIO(b"stream_options.include_usage unsupported"))

    monkeypatch.setattr("urllib.request.urlopen", unsupported)
    item, _ = client(transport)
    with pytest.raises(LlmClientError, match="include_usage unsupported"):
        item.complete("original")
    assert len(requests) == 3
    assert "include_usage unsupported" in item.call_records[0]["http_attempts"][0]["raw_response"]


def test_multiline_sse_and_unknown_extensions_never_pollute_content(modules):
    transport, _ = modules
    value = event("答案")
    value["choices"][0]["delta"]["reasoning_content"] = "not candidate content"
    multiline = "".join("data: " + line + "\r" for line in json.dumps(value, ensure_ascii=False, indent=2).splitlines()) + "\r"
    parser = transport.SSECompletion()
    parser.feed(multiline.encode("utf-8") + wire(event(finish="stop")))
    assert parser.response()["choices"][0]["message"]["content"] == "答案"


@pytest.mark.parametrize("change", ["id", "model", "choice", "after_finish", "after_done", "tool"])
def test_ambiguous_stream_protocol_rejected(modules, change):
    transport, _ = modules
    first, last = event("answer"), event(finish="stop")
    if change in {"id", "model"}:
        last[change] = "changed"
    if change == "choice":
        first["choices"][0]["index"] = 1
    if change == "tool":
        first["choices"][0]["delta"]["tool_calls"] = [{"index": 0}]
    raw = wire(first, last)
    if change == "after_finish":
        raw = wire(first, last, event("more"))
    if change == "after_done":
        raw += wire(event("more"))
    with pytest.raises(LlmClientError):
        parser = transport.SSECompletion()
        parser.feed(raw)
        parser.response()


def test_factory_binding_restored_and_concurrent_embedding_rejected(modules):
    # Explicit factory injection needs no global monkeypatch and permits embedding.
    transport, _ = modules
    from skillflow.common.runs import ReplayClient
    assert transport.StreamingReplayClient.__bases__ == (ReplayClient,)
    assert not hasattr(resumable, "_ReplayClient")
    assert not hasattr(transport, "isolated_streaming_client")
    release = threading.Event()
    thread = threading.Thread(target=lambda: release.wait(5))
    thread.start()
    try:
        item, _ = client(transport)
        assert isinstance(item, ReplayClient)
        assert not hasattr(resumable, "_ReplayClient")
    finally:
        release.set()
        thread.join()


def test_real_pipeline_repair_replay_and_redaction_with_streams(modules, tmp_path, monkeypatch):
    transport, _ = modules
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("保留输入并返回结果。", encoding="utf-8")
    (tmp_path / "annotation.json").write_text('{"annotation_sentinel":"EXTERNAL_FACT"}')
    (tmp_path / "dataset.json").write_text(json.dumps({"cases": [{"id": "case", "input": "skill"}]}))
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"name": "sse-test", "dataset": "dataset.json", "repetitions": 3, "variants": [{"id": "sol-max", "max_repair_rounds": 1}]}))
    env = {"LLM_API_KEY": "stream-test-secret", "LLM_ENDPOINT": "https://offline.invalid/v1", "LLM_MODEL": "gpt-5.6-sol", "LLM_REASONING_EFFORT": "max"}
    requests = []

    def respond(request, timeout):
        payload = json.loads(request.data)
        requests.append(payload)
        assert "EXTERNAL_FACT" not in payload["messages"][0]["content"]
        content = "invalid JSON stream-test-secret" if len(requests) == 1 else json.dumps(CANDIDATE, ensure_ascii=False)
        return Response([wire(event(content), event(finish="stop"))])

    monkeypatch.setattr("urllib.request.urlopen", respond)
    arguments = dict(run_directory=tmp_path / "run", case_splits={"case": "development"}, environ=env, provenance={"transport": transport.TRANSPORT_POLICY})
    result = resumable.run_resumable_experiment(config, client_factory=transport.StreamingReplayClient, **arguments, workers=2)
    assert result.status == "complete" and len(requests) == 4
    assert result.report["summary"]["repair_attempts"] == 1
    for path in result.run_directory.rglob("*.json"):
        assert "stream-test-secret" not in path.read_text(encoding="utf-8")
    final = resumable.run_resumable_experiment(config, client_factory=transport.StreamingReplayClient, **arguments, workers=1)
    assert final.status == "complete" and len(requests) == 4
    path = result.run_directory / result.report["trials"][0]["artifacts"] / "record.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["status"] = "running"
    path.write_text(json.dumps(record), encoding="utf-8")
    replay = resumable.run_resumable_experiment(config, client_factory=transport.StreamingReplayClient, **arguments, workers=1)
    assert replay.status == "complete" and len(requests) == 4
    assert replay.report["trials"][0]["replayed_generations"] == 2


def test_entrypoint_identity_binds_both_new_sources_and_rejects_nonstream_run(modules, tmp_path):
    transport, entry = modules
    provenance = entry.streaming_provenance()
    assert set(provenance["transport"]["source_sha256"]) == {"stream_transport.py", "run_streaming_baseline.py"}
    assert provenance["transport"]["parameters"] == transport.STREAM_PARAMETERS
    assert "inactivity" in provenance["transport"]["timeout"]
    (tmp_path / "experiment.json").write_text('{"provenance":{"contract":"constraints-v2"}}')
    with pytest.raises(ValueError, match="new run directory"):
        entry.require_streaming_directory(tmp_path)


def test_incomplete_stream_is_durable_error_with_unknown_remote_outcome_and_no_resend(modules, tmp_path, monkeypatch):
    transport, _ = modules
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("Return input.")
    (tmp_path / "dataset.json").write_text('{"cases":[{"id":"case","input":"skill"}]}')
    config = tmp_path / "config.json"
    config.write_text('{"name":"partial-sse","dataset":"dataset.json","variants":[{"id":"sol-max"}]}')
    requests = []

    def respond(*args, **kwargs):
        requests.append(1)
        return Response([wire(event("残片"), done=False), TimeoutError("no next event")])

    monkeypatch.setattr("urllib.request.urlopen", respond)
    args = dict(run_directory=tmp_path / "run", case_splits={"case": "development"},
                environ={"LLM_API_KEY": "offline-key", "LLM_ENDPOINT": "https://offline.invalid/v1"},
                provenance={"transport": transport.TRANSPORT_POLICY}, workers=1)
    first = resumable.run_resumable_experiment(config, client_factory=transport.StreamingReplayClient, **args)
    assert first.report["trials"][0]["status"] == "error"
    assert first.report["trials"][0]["http_attempts"] == 1
    directory = first.run_directory / first.report["trials"][0]["artifacts"]
    trace = json.loads((directory / "trace.json").read_text(encoding="utf-8"))
    attempt = trace["calls"][0]["http_attempts"][0]
    assert attempt["http_status"] == 200
    assert attempt["stream"]["outcome"] == "remote_outcome_unknown"
    assert attempt["stream"]["partial_content"] == "残片"
    assert not (directory / "analysis.json").exists()
    assert not (directory / "candidate.json").exists()
    before = (directory / "trace.json").read_bytes()
    again = resumable.run_resumable_experiment(config, client_factory=transport.StreamingReplayClient, **args)
    assert again.report["trials"][0]["status"] == "error" and len(requests) == 1
    assert (directory / "trace.json").read_bytes() == before


def test_entrypoint_offline_check_requires_explicit_new_directory(modules, tmp_path, monkeypatch, capsys):
    _, entry = modules
    with pytest.raises(SystemExit):
        entry.main(["--check"])
    monkeypatch.setenv("LLM_API_KEY", "offline-check-key")
    assert entry.main(["--run-dir", str(tmp_path / "new"), "--check"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["mode"] == "offline_sse_preflight" and result["selected"] == 66
    assert not (tmp_path / "new").exists()
