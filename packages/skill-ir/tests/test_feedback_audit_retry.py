"""Communication retries are bounded, durable, and outside semantic decisions."""
from copy import deepcopy
from http.client import IncompleteRead, RemoteDisconnected
import json
from threading import Event

import pytest

from skill_ir.feedback import runner
from skill_ir.feedback.models import FeedbackLimits
from skill_ir.llm.client import LlmClientError
from skill_ir.recording import canonical_sha256, read_json
from test_feedback_runner import Client, answer, candidate, material


@pytest.fixture(autouse=True)
def no_test_backoff(monkeypatch):
    monkeypatch.setattr(runner, "retry_delay_ms", lambda _: 0)


def run(material, client, **kwargs):
    source, seed, directory = material
    return runner.refine_skill(source, run_dir=directory, initial_analysis=seed,
                               audit_client=client, **kwargs)


def test_timeout_then_success_same_prompt_one_logical_audit(material):
    client = Client([TimeoutError("timed out"), answer])
    result = run(material, client)
    assert result["status"] == "audit_passed", result["reason"]
    assert len(client.prompts) == 2 and client.prompts[0] == client.prompts[1]
    assert result["counts"]["audit_logical_calls"] == 1
    assert result["counts"]["audit_execution_calls"] == 2
    assert result["counts"]["audit_execution_retries"] == 1
    assert result["counts"]["semantic_revisions"] == 0
    assert result["counts"]["total_execution_calls"] == 2
    assert result["rounds"][0]["audit_execution"][0]["retry"] is True
    assert read_json(material[2]/"calls/r000/audit/a001/call.json")["status"] == "error"
    assert read_json(material[2]/"calls/r000/audit/a002/call.json")["status"] == "complete"
    assert run(material, client) == result  # no fresh request on resume
    assert len(client.prompts) == 2
    assert runner.replay_run(material[2]) == result


def test_exhausted_failures_keep_three_attempts_not_semantic_revisions(material):
    client = Client([TimeoutError("timed out")] * 4)
    result = run(material, client)
    assert result["status"] == "audit_error"
    assert len(client.prompts) == 3
    assert result["counts"]["audit_logical_calls"] == 1
    assert result["counts"]["audit_execution_calls"] == 3
    assert result["counts"]["semantic_revisions"] == 0
    assert [r["retry"] for r in result["rounds"][0]["audit_execution"]] == [True, True, False]
    assert run(material, client) == result and len(client.prompts) == 3
    assert runner.replay_run(material[2]) == result


@pytest.mark.parametrize("response,status", [("bad json", "audit_error"),
                                            (lambda p: answer(p, "cannot_assess"), "semantic_failure"),
                                            (lambda p: answer(p, "omitted"), "revision_limit")])
def test_complete_response_never_retried_for_its_quality(material, response, status):
    client = Client([response, answer])
    result = run(material, client, max_semantic_revisions=0)
    assert result["status"] == status and len(client.prompts) == 1
    assert result["counts"]["audit_execution_calls"] == result["counts"]["audit_logical_calls"] == 1


@pytest.mark.parametrize("error", [PermissionError("Access is denied: transport.json"),
                                  LlmClientError("LLM SSE network failure: [WinError 5] Access is denied: transport.json"),
                                  RuntimeError("accepted but incomplete"),
                                  KeyboardInterrupt("user pause")])
def test_local_unknown_and_user_interrupt_never_retry(material, error):
    client = Client([error, answer])
    result = run(material, client)
    assert result["status"] in {"audit_error", "interrupted"}
    assert len(client.prompts) == 1
    assert result["counts"]["audit_execution_retries"] == 0
    assert runner.replay_run(material[2]) == result


def transport_factory(outcomes, *, stop=None):
    outcomes, prompts = iter(outcomes), []
    def factory(writer, checkpoint):
        class Transport:
            def complete(self, prompt):
                prompts.append(prompt)
                value = next(outcomes)
                if isinstance(value, tuple):
                    error, status = value
                    record = {"status": "error", "prompt": prompt, "response": None,
                              "error": str(error), "error_type": type(error).__name__,
                              "http_attempts": [{"status": "error", "http_status": status,
                                                 "stream": {"done_received": False, "finish_reason": None,
                                                            "outcome": "remote_outcome_unknown" if status == 200 else "network_error"}}]}
                    checkpoint([record])
                    if stop is not None:
                        stop.set()
                    raise error
                response = value(prompt)
                checkpoint([{"status": "complete", "prompt": prompt, "response": response,
                             "http_attempts": [{"status": "complete", "http_status": 200}]}])
                return response
        return Transport()
    return factory, prompts


@pytest.mark.parametrize("error,status", [
    (IncompleteRead(b""), 200),
    (LlmClientError("Incomplete SSE response: both [DONE] and choice finish_reason are required"), 200),
    (LlmClientError("LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed>"), None),
    (LlmClientError("LLM HTTP 429: rate limited"), 429),
    (LlmClientError("LLM HTTP 503: unavailable"), 503),
    (RemoteDisconnected("Remote end closed connection without response"), None),
])
def test_real_transport_shapes_retry_in_separate_records(material, error, status):
    source, seed, directory = material
    factory, prompts = transport_factory([(error, status), answer])
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_factory=factory)
    assert result["status"] == "audit_passed", result["reason"]
    assert len(prompts) == 2 and prompts[0] == prompts[1]
    assert result["counts"]["http_attempts"] == 2
    assert result["counts"]["http_retries"] == 0
    assert result["counts"]["audit_execution_retries"] == 1
    assert runner.replay_run(directory) == result


@pytest.mark.parametrize("status", [400, 401, 403])
def test_auth_and_permanent_http_failures_stop(material, status):
    source, seed, directory = material
    factory, prompts = transport_factory([(LlmClientError(f"LLM HTTP {status}: rejected"), status), answer])
    result = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_factory=factory)
    assert result["status"] == "audit_error" and len(prompts) == 1


def test_pause_before_retry_replay_preserves_pause_then_resume_consumes_failure(material):
    source, seed, directory = material
    stop = Event()
    factory, prompts = transport_factory([(IncompleteRead(b""), 200)], stop=stop)
    paused = runner.refine_skill(source, run_dir=directory, initial_analysis=seed,
                                 audit_factory=factory, stop_event=stop)
    assert paused["status"] == "interrupted" and len(prompts) == 1
    assert paused["counts"]["audit_execution_calls"] == 1
    assert read_json(directory/"execution-boundary.json")["kind"] == "before_audit_retry"
    assert runner.replay_run(directory) == paused
    next_client = Client([answer])
    resumed = run(material, next_client)
    assert resumed["status"] == "audit_passed" and len(next_client.prompts) == 1
    assert resumed["counts"]["audit_execution_calls"] == 2
    assert runner.replay_run(directory) == resumed


def test_running_uncertain_record_never_creates_second_attempt(material):
    client = Client([RuntimeError("temporary setup")])
    run(material, client)
    directory = material[2]/"calls/r000/audit/a001"
    call = read_json(directory/"call.json")
    call.update(status="running", error="timed out", error_type="TimeoutError")
    (directory/"call.json").write_text(json.dumps(call), encoding="utf8")
    trace = [{"status": "running", "prompt": call["prompt"], "http_attempts": []}]
    trace[0]["record_sha256"] = canonical_sha256(trace[0])
    (directory/"transport.json").write_text(json.dumps(trace), encoding="utf8")
    resumed = run(material, client)
    assert resumed["status"] == "audit_error" and len(client.prompts) == 1
    assert not (directory.parent/"a002").exists()


def test_execution_bounds_and_v1_rejection(material):
    limits = FeedbackLimits()
    assert limits.logical_call_bounds(initial_graph=False) == {"extraction": 16, "audit": 4, "total": 20}
    assert limits.execution_call_bounds(initial_graph=False) == {"extraction": 16, "audit": 12, "total": 28}
    assert limits.execution_call_bounds(initial_graph=True) == {"extraction": 12, "audit": 12, "total": 24}
    with pytest.raises(ValueError):
        FeedbackLimits(max_audit_execution_retries=6)
    directory = material[2]; directory.mkdir()
    (directory/"manifest.json").write_text('{"schema_version":1,"identity":"skill-ir-semantic-feedback-v1"}')
    with pytest.raises(ValueError, match="Unsupported"):
        runner.replay_run(directory)


def test_complete_transport_then_interrupt_replays_pause_before_explicit_resume(material):
    source, seed, directory = material
    prompts = []
    def factory(writer, checkpoint):
        class Accepted:
            def complete(self, prompt):
                prompts.append(prompt)
                checkpoint([{"status": "complete", "prompt": prompt, "response": answer(prompt),
                             "http_attempts": [{"status": "complete", "http_status": 200}]}])
                raise KeyboardInterrupt("paused after accepted answer")
        return Accepted()
    paused = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_factory=factory)
    assert paused["status"] == "interrupted"
    assert runner.replay_run(directory) == paused
    resumed = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_factory=factory)
    assert resumed["status"] == "audit_passed" and len(prompts) == 1
    assert runner.replay_run(directory) == resumed


def test_uncertain_second_attempt_never_starts_third(material):
    client = Client([TimeoutError("timed out"), KeyboardInterrupt("stopped")])
    paused = run(material, client)
    assert paused["status"] == "interrupted" and len(client.prompts) == 2
    directory = material[2]/"calls/r000/audit/a002"
    call = read_json(directory/"call.json")
    call["status"] = "running"
    for key in ("error", "error_type"):
        call.pop(key, None)
    (directory/"call.json").write_text(json.dumps(call), encoding="utf8")
    trace = [{"status": "running", "prompt": call["prompt"], "response": None,
              "http_attempts": [{"status": "running", "http_status": 200}]}]
    trace[0]["record_sha256"] = canonical_sha256(trace[0])
    (directory/"transport.json").write_text(json.dumps(trace), encoding="utf8")
    resumed = run(material, client)
    assert resumed["status"] == "audit_error" and len(client.prompts) == 2
    assert not (directory.parent/"a003").exists()


def test_retries_never_consume_semantic_revision_budget(material):
    client = Client([item for _ in range(4) for item in
                     (TimeoutError("timed out"), TimeoutError("timed out"), lambda p: answer(p, "omitted"))])
    result = run(material, client, extraction_client=Client([candidate()] * 3))
    assert result["status"] == "revision_limit"
    assert result["counts"]["audit_logical_calls"] == 4
    assert result["counts"]["audit_execution_calls"] == 12
    assert result["counts"]["audit_execution_retries"] == 8
    assert result["counts"]["semantic_revisions"] == 3
    assert result["counts"]["extraction_logical_calls"] == 3
    assert result["counts"]["total_execution_calls"] == 15
