"""Independent review cases for real recorded SSE failure shapes; no API calls."""
from copy import deepcopy
import json

import pytest

from skill_ir.audit_execution import classify_failure
from skill_ir.recording import canonical_sha256


def persisted_failure(tmp_path, *, message="LLM SSE network failure: getaddrinfo failed",
                      error_type="LlmClientError", status=None, stream=None,
                      attempt_status="error", call_status="error"):
    prompt = "exact audit input"
    # LlmClient always puts response:null in its initially running transport
    # record. RecordingClient's wrapper has no response key until one returns.
    call = {"status": call_status, "prompt": prompt, "response": None,
            "error": message, "error_type": error_type,
            "http_attempts": [{"status": attempt_status, "http_status": status,
                               "error": message, "error_type": error_type,
                               "stream": stream or {"outcome": "network_error",
                                                      "done_received": False,
                                                      "finish_reason": None}}]}
    wrapper = {"status": call_status, "prompt": prompt,
               "prompt_sha256": canonical_sha256(prompt),
               "error": message, "error_type": error_type}
    write_records(tmp_path, wrapper, call)
    return prompt, wrapper, call


def write_records(directory, wrapper, call):
    call = deepcopy(call)
    call["record_sha256"] = canonical_sha256(call)
    (directory / "call.json").write_text(json.dumps(wrapper), encoding="utf-8")
    (directory / "transport.json").write_text(json.dumps([call]), encoding="utf-8")


def test_real_dns_failure_has_null_response_and_can_retry(tmp_path):
    prompt, _, _ = persisted_failure(tmp_path)
    assert classify_failure(tmp_path, prompt)["eligible"] is True


@pytest.mark.parametrize("error_type,message", [
    ("IncompleteRead", "IncompleteRead(0 bytes read)"),
    ("LlmClientError", "Incomplete SSE response: both [DONE] and choice finish_reason are required"),
    ("LlmClientError", "LLM SSE network failure: timed out"),
])
def test_confirmed_terminal_accepted_stream_failure_can_retry(tmp_path, error_type, message):
    prompt, _, _ = persisted_failure(
        tmp_path, error_type=error_type, message=message, status=200,
        stream={"outcome": "remote_outcome_unknown", "done_received": False,
                "finish_reason": None})
    assert classify_failure(tmp_path, prompt)["eligible"] is True


@pytest.mark.parametrize("message", [
    'SSE provider error: {"error": "timed out"}',
    'Invalid SSE JSON event: unexpected string "connection reset"',
    'Invalid UTF-8 in SSE response: network is unreachable',
    'LLM SSE network failure: [WinError 5] Access is denied: transport.json',
])
def test_protocol_provider_and_persistence_errors_cannot_retry(tmp_path, message):
    prompt, _, _ = persisted_failure(tmp_path, message=message, status=200,
                                     stream={"outcome": "remote_outcome_unknown"})
    assert classify_failure(tmp_path, prompt)["eligible"] is False


@pytest.mark.parametrize("status", ["running", "interrupted"])
def test_unknown_attempt_cannot_be_retried_even_if_outer_record_has_error(tmp_path, status):
    prompt, _, _ = persisted_failure(tmp_path, attempt_status=status)
    assert classify_failure(tmp_path, prompt)["eligible"] is False


def test_complete_wire_response_cannot_retry_after_later_failure(tmp_path):
    prompt, _, _ = persisted_failure(
        tmp_path, message="LLM SSE network failure: timed out", status=200,
        stream={"outcome": "complete", "done_received": True, "finish_reason": "stop"})
    assert classify_failure(tmp_path, prompt)["eligible"] is False


def test_complete_http_attempt_cannot_retry_after_later_failure(tmp_path):
    prompt, _, _ = persisted_failure(tmp_path, attempt_status="complete")
    assert classify_failure(tmp_path, prompt)["eligible"] is False


def test_record_tampering_is_not_hidden_by_a_retry(tmp_path):
    prompt, _, _ = persisted_failure(tmp_path)
    transport = json.loads((tmp_path / "transport.json").read_text(encoding="utf-8"))
    transport[0]["error"] = "LLM SSE network failure: timed out"
    (tmp_path / "transport.json").write_text(json.dumps(transport), encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        classify_failure(tmp_path, prompt)


@pytest.mark.parametrize("location", ["wrapper", "call", "attempt"])
def test_secondary_recording_failure_blocks_network_retry(tmp_path, location):
    prompt, wrapper, call = persisted_failure(tmp_path)
    target = {"wrapper": wrapper, "call": call, "attempt": call["http_attempts"][0]}[location]
    target["recording_failed"] = True
    target["recording_errors"] = [{"error_type": "ArtifactWriteError", "error": "local replacement failed"}]
    write_records(tmp_path, wrapper, call)
    assert classify_failure(tmp_path, prompt) == {
        "eligible": False, "category": "local_storage_integrity_or_interrupt",
    }


def test_explicit_artifact_failure_cannot_be_retried_as_http_error(tmp_path):
    prompt, _, _ = persisted_failure(
        tmp_path, message="Artifact write failed", error_type="ArtifactWriteError", status=503,
    )
    assert classify_failure(tmp_path, prompt) == {
        "eligible": False, "category": "local_storage_integrity_or_interrupt",
    }
