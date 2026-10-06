"""The stage-specific HTTP contract survives acceptance, failure and replay."""
from copy import deepcopy
import io
import json
import urllib.error

import pytest

from skillflow.common.llm import LlmClient
from skillflow.common.llm import LlmConfig
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import read_json
from skillflow.propagation.annotation import runner
from tests.propagation.annotation.helpers import FakeClient
from tests.propagation.annotation.test_security_runner import setup_run, forbidden


def run_http(tmp_path, monkeypatch, kind="valid"):
    config = {"model": "offline-model", "reasoning_effort": "high"}
    directory, _, _ = setup_run(tmp_path, config=config)
    sent = []
    fake = FakeClient()

    class Response:
        status = 200
        headers = {}

        def __init__(self, payload):
            self.payload = json.dumps(payload).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return self.payload

    def request(req, timeout):
        payload = json.loads(req.data)
        sent.append(payload)
        if kind == "unsupported":
            raise urllib.error.HTTPError(req.full_url, 400, "unsupported", {}, io.BytesIO(b"response_format unsupported"))
        annotation = fake.complete(payload["messages"][0]["content"])
        if kind == "quote":
            annotation["profiles"]["ir_read"]["evidences"][0]["quote"] = "NONEXISTENT_QUOTE"
        content = json.dumps(annotation)
        if kind == "extra_brace":
            content += "}"
        return Response({"model": "offline-returned", "choices": [{
            "finish_reason": "length" if kind == "truncated" else "stop",
            "message": {"content": content}}]})

    monkeypatch.setattr("urllib.request.urlopen", request)
    factory = lambda writer, checkpoint: LlmClient(
        LlmConfig(api_key="offline-secret", **runner._config(config)), record_calls=True, on_record=checkpoint)
    result = runner.run_annotation(directory, client_factory=factory, config=config)
    return directory, result, sent


@pytest.mark.parametrize("kind,status,error_kind", [
    ("valid", "complete", None),
    ("extra_brace", "invalid_response", "json_format"),
    ("quote", "invalid_response", "structure_or_evidence"),
    ("truncated", "execution_error", "output_truncated"),
    ("unsupported", "execution_error", "execution"),
])
def test_actual_json_request_and_classified_outcome_replay_without_new_http(tmp_path, monkeypatch, kind, status, error_kind):
    directory, result, sent = run_http(tmp_path, monkeypatch, kind)
    assert result["status"] == status, result["reason"]
    assert result["error_kind"] == error_kind
    assert len(sent) == 1
    assert sent[0]["response_format"] == {"type": "json_object"}
    assert result["request_validation"]["observed"] is True
    assert read_json(directory / "manifest.json")["config"]["response_format"] == "json_object"
    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    assert runner.replay_run(directory) == result
    assert len(sent) == 1


@pytest.mark.parametrize("change", ["missing_parameter", "altered_hash", "saved_validation"])
def test_accepted_request_identity_cannot_be_resealed_to_bypass_replay(tmp_path, monkeypatch, change):
    directory, result, _ = run_http(tmp_path, monkeypatch)
    trace_path = directory / runner.CALL_PATH / "transport.json"
    if change == "saved_validation":
        saved = deepcopy(result)
        saved["request_validation"]["observed"] = False
        (directory / "result.json").write_text(json.dumps(saved), encoding="utf-8")
    else:
        trace = read_json(trace_path)
        attempt = trace[0]["http_attempts"][0]
        if change == "missing_parameter":
            attempt["request_parameters"].pop("response_format")
        else:
            attempt["request_body_sha256"] = "0" * 64
        trace[0].pop("record_sha256")
        trace[0]["record_sha256"] = canonical_sha256(trace[0])
        trace_path.write_text(json.dumps(trace), encoding="utf-8")
    before = (directory / "result.json").read_bytes()
    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    with pytest.raises(runner.RunIdentityError, match="request identity"):
        runner.replay_run(directory)
    assert (directory / "result.json").read_bytes() == before


def test_old_v7_run_is_not_reinterpreted_with_current_json_contract(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    path = directory / "manifest.json"
    manifest = runner._unseal(read_json(path))
    manifest.update(schema_version=7, identity="skill-ir-security-profile-v7")
    path.write_text(json.dumps(runner._seal(manifest)), encoding="utf-8")
    with pytest.raises(runner.RunIdentityError, match="Unsupported"):
        runner.replay_run(directory)
