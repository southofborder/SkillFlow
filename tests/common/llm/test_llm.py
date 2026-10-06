import io
import json
import os
import urllib.error

import pytest

from skillflow.common.llm import LlmClient
from skillflow.common.llm import LlmClientError
from skillflow.common.llm import LlmConfig
from skillflow.common.llm import LlmConfigError
from skillflow.common.artifact_io import ArtifactWriteError
from skillflow.common.llm.config import OutputTruncatedError


class FakeResponse:
    status = 200

    def __init__(self, payload: dict) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_record_callback_failure_before_request_is_local(monkeypatch):
    def no_network(*args, **kwargs):
        pytest.fail("Failed pre-request persistence must not open a connection")

    def broken_record(calls):
        raise PermissionError("local file busy")

    monkeypatch.setattr("urllib.request.urlopen", no_network)
    client = LlmClient(LlmConfig(api_key="test"), record_calls=True, on_record=broken_record)
    with pytest.raises(ArtifactWriteError) as raised:
        client.complete("checked")
    assert raised.value.stage == "callback"
    assert isinstance(raised.value.__cause__, PermissionError)
    assert client.call_records[0]["error_type"] == "ArtifactWriteError"
    assert client.call_records[0]["recording_failed"] is True


def test_final_record_failure_preserves_http_error_and_blocks_retry(monkeypatch):
    requests, snapshots = [], []

    def fail_request(request, timeout):
        requests.append(request)
        raise urllib.error.HTTPError(request.full_url, 503, "unavailable", {}, io.BytesIO(b"busy"))

    def fail_terminal_attempt(calls):
        snapshots.append(calls[0]["status"])
        attempts = calls[0]["http_attempts"]
        if attempts and attempts[-1]["status"] == "error":
            raise PermissionError("local file busy")

    monkeypatch.setattr("urllib.request.urlopen", fail_request)
    client = LlmClient(
        LlmConfig(api_key="test", max_retries=3), record_calls=True,
        on_record=fail_terminal_attempt,
        sleep=lambda delay: pytest.fail("Must not retry HTTP after persistence failure"),
    )
    with pytest.raises(LlmClientError, match="HTTP 503") as raised:
        client.complete("checked")
    assert len(requests) == 1
    assert raised.value.transient is False
    assert raised.value.recording_failed is True
    assert all(item["error_type"] == "ArtifactWriteError" for item in raised.value.recording_errors)
    assert client.call_records[0]["error_type"] == "LlmClientError"
    assert client.call_records[0]["recording_failed"] is True


@pytest.mark.parametrize("outer_error_context", [False, True])
def test_complete_response_final_record_error_is_not_success_or_resend(monkeypatch, outer_error_context):
    requests = []

    def respond(request, timeout):
        requests.append(request)
        return FakeResponse({"model": "offline", "choices": [{"message": {"content": "answer"}}]})

    def fail_final_record(calls):
        if calls[0]["status"] == "complete":
            raise PermissionError("local file busy")

    monkeypatch.setattr("urllib.request.urlopen", respond)
    client = LlmClient(LlmConfig(api_key="test"), record_calls=True, on_record=fail_final_record)
    if outer_error_context:
        try:
            raise RuntimeError("unrelated error handled by caller")
        except RuntimeError:
            with pytest.raises(ArtifactWriteError):
                client.complete("checked")
    else:
        with pytest.raises(ArtifactWriteError):
            client.complete("checked")
    assert len(requests) == 1
    assert client.call_records[0]["response"] == "answer"
    assert client.call_records[0]["recording_failed"] is True


def test_llm_config_reads_provider_configuration() -> None:
    config = LlmConfig.from_env(
        {
            "LLM_API_KEY": "key",
            "LLM_ENDPOINT": "https://provider.example/v1/chat/completions",
            "LLM_MODEL": "gpt-5.6-sol",
            "LLM_REASONING_EFFORT": "high",
            "LLM_TIMEOUT": "1234",
        }
    )

    assert config.api_key == "key"
    assert config.endpoint == "https://provider.example/v1/chat/completions"
    assert config.model == "gpt-5.6-sol"
    assert config.reasoning_effort == "high"
    assert config.timeout_ms == 1234


def test_default_remote_timeout_is_ten_minutes_and_explicit_value_wins() -> None:
    assert LlmConfig.from_env({"LLM_API_KEY": "test-key"}).timeout_ms == 600000
    assert LlmConfig.from_env({"LLM_API_KEY": "test-key", "LLM_TIMEOUT": "900000"}).timeout_ms == 900000


def test_llm_config_loads_nearest_dotenv_without_overriding_environment(
    monkeypatch, tmp_path
) -> None:
    (tmp_path / ".env").write_text(
        "LLM_API_KEY=file-key\nLLM_REASONING_EFFORT=high\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_ENDPOINT", raising=False)
    monkeypatch.setenv("LLM_REASONING_EFFORT", "low")

    config = LlmConfig.from_env()

    assert config.api_key == "file-key"
    assert config.endpoint == "https://api.openai.com/v1/chat/completions"
    assert config.reasoning_effort == "low"
    assert "LLM_API_KEY" not in os.environ


def test_provider_credentials_and_address_are_used_together() -> None:
    config = LlmConfig.from_env(
        {
            "LLM_API_KEY": "provider-key",
            "LLM_ENDPOINT": "https://provider.example/v1/chat/completions",
            "LLM_MODEL": "gpt-5.6-sol",
            "OPENAI_API_KEY": "unrelated-official-key",
            "OPENAI_MODEL": "unrelated-model",
            "OPENAI_REASONING_EFFORT": "medium",
        }
    )
    assert config.api_key == "provider-key"
    assert config.endpoint == "https://provider.example/v1/chat/completions"
    assert config.model == "gpt-5.6-sol"
    assert config.reasoning_effort == "max"


def test_official_key_is_not_silently_sent_to_configured_provider(monkeypatch) -> None:
    def unexpected_request(*args, **kwargs):
        pytest.fail("Missing provider credentials must fail before any network call")

    monkeypatch.setattr("urllib.request.urlopen", unexpected_request)
    config = LlmConfig.from_env(
        {
            "OPENAI_API_KEY": "official-key",
            "LLM_ENDPOINT": "https://provider.example/v1/chat/completions",
        }
    )
    with pytest.raises(LlmConfigError, match="LLM_API_KEY"):
        LlmClient(config).complete("prompt")


def test_explicit_provider_endpoint_is_accepted() -> None:
    config = LlmConfig(
        api_key="key", endpoint="https://provider.example/v1/chat/completions"
    )
    assert config.endpoint == "https://provider.example/v1/chat/completions"


def test_invalid_reasoning_effort_is_rejected() -> None:
    with pytest.raises(LlmConfigError, match="LLM_REASONING_EFFORT"):
        LlmConfig.from_env({"LLM_REASONING_EFFORT": "typo"})


def test_config_representation_does_not_include_api_key() -> None:
    assert "secret-key" not in repr(LlmConfig(api_key="secret-key"))


def test_llm_client_requires_api_key() -> None:
    with pytest.raises(LlmConfigError, match="LLM_API_KEY"):
        LlmClient(LlmConfig(api_key=""))


def test_explicit_environment_file_is_overridden_by_process_variables(
    tmp_path, monkeypatch
):
    from skillflow.common.llm.config import load_environment

    path = tmp_path / "settings.env"
    path.write_text("LLM_MODEL=file-model\nLLM_API_KEY=file-key\n")
    monkeypatch.setenv("LLM_MODEL", "process-model")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    config = LlmConfig.from_env(env_file=path)
    assert config.model == "process-model"
    assert config.api_key == "file-key"
    assert "LLM_API_KEY" not in os.environ
    assert (
        load_environment(environ={"LLM_MODEL": "mapping-model"}, env_file=path)[
            "LLM_MODEL"
        ]
        == "mapping-model"
    )
    with pytest.raises(FileNotFoundError):
        LlmConfig.from_env(env_file=tmp_path / "missing.env")


def test_llm_client_posts_chat_completion(monkeypatch) -> None:
    requests = []

    def fake_urlopen(request, timeout):
        requests.append((request, timeout))
        return FakeResponse({"choices": [{"message": {"content": '{"ok": true}'}}]})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = LlmClient(
        LlmConfig(
            api_key="secret",
            endpoint="https://provider.example/v1/chat/completions",
            timeout_ms=2000,
        )
    )

    assert client.complete("prompt") == '{"ok": true}'
    request, timeout = requests[0]
    assert request.full_url == "https://provider.example/v1/chat/completions"
    assert request.get_header("Authorization") == "Bearer secret"
    assert timeout == 2
    payload = json.loads(request.data.decode("utf-8"))
    assert payload["model"] == "gpt-5.6-sol"
    assert payload["reasoning_effort"] == "max"
    assert "temperature" not in payload
    assert payload["messages"][0]["content"] == "prompt"
    assert "response_format" not in payload


def test_json_output_requires_explicit_config_and_ignores_global_environment():
    assert LlmConfig.from_env({"LLM_RESPONSE_FORMAT": "json_object"}).response_format is None
    assert LlmConfig(api_key="test", response_format="json_object").response_format == "json_object"
    for invalid in ("json_schema", "text", "", False, 1, {}, []):
        with pytest.raises(LlmConfigError, match="response_format"):
            LlmConfig(api_key="test", response_format=invalid)


def test_json_output_wire_parameters_and_body_hash_are_recorded(monkeypatch):
    import hashlib
    requests = []

    def respond(request, timeout):
        requests.append(request)
        return FakeResponse({"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}]})

    monkeypatch.setattr("urllib.request.urlopen", respond)
    client = LlmClient(LlmConfig(api_key="secret", response_format="json_object"), record_calls=True)
    assert client.complete("原文 JSON") == "{}"
    payload = json.loads(requests[0].data)
    attempt = client.call_records[0]["http_attempts"][0]
    assert payload["response_format"] == {"type": "json_object"}
    assert attempt["request_parameters"] == {key: value for key, value in payload.items() if key != "messages"}
    assert attempt["request_body_sha256"] == hashlib.sha256(requests[0].data).hexdigest()
    assert "secret" not in json.dumps(client.call_records)


def test_explicit_output_truncation_is_never_accepted_or_retried(monkeypatch):
    requests = []

    def respond(request, timeout):
        requests.append(request)
        # Even syntactically valid content is incomplete by provider declaration.
        return FakeResponse({"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]})

    monkeypatch.setattr("urllib.request.urlopen", respond)
    client = LlmClient(LlmConfig(api_key="test", max_retries=3), record_calls=True,
                       sleep=lambda _: pytest.fail("Truncated output must not retry"))
    with pytest.raises(OutputTruncatedError, match="finish_reason=length"):
        client.complete("JSON")
    assert len(requests) == 1
    assert client.call_records[0]["status"] == "error"
    assert client.call_records[0]["error_type"] == "OutputTruncatedError"
    assert client.call_records[0]["http_attempts"][0]["raw_response"]["choices"][0]["finish_reason"] == "length"


def test_json_output_rejection_is_not_silently_removed_or_retried(monkeypatch):
    requests = []

    def reject(request, timeout):
        requests.append(json.loads(request.data))
        raise urllib.error.HTTPError(request.full_url, 400, "unsupported", {}, io.BytesIO(b"response_format unsupported"))

    monkeypatch.setattr("urllib.request.urlopen", reject)
    with pytest.raises(LlmClientError, match="response_format unsupported"):
        LlmClient(LlmConfig(api_key="test", response_format="json_object", max_retries=3)).complete("JSON")
    assert len(requests) == 1
    assert requests[0]["response_format"] == {"type": "json_object"}


def test_llm_client_retries_transient_http_errors(monkeypatch) -> None:
    responses = [
        urllib.error.HTTPError(
            "http://localhost/test",
            500,
            "failed",
            {"Retry-After": "0"},
            io.BytesIO(b"bad"),
        ),
        FakeResponse({"choices": [{"message": {"content": "{}"}}]}),
    ]
    waits: list[float] = []

    def fake_urlopen(request, timeout):
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = LlmClient(
        LlmConfig(api_key="secret", max_retries=1, retry_base_ms=1),
        sleep=waits.append,
        random_value=lambda: 0,
    )

    assert client.complete("prompt") == "{}"
    assert waits == [0.0]


@pytest.mark.parametrize("status", [401, 403, 404])
def test_auth_or_model_access_error_does_not_retry_or_switch_provider(
    monkeypatch, status
) -> None:
    requests = []

    def fake_urlopen(request, timeout):
        requests.append(request)
        raise urllib.error.HTTPError(
            request.full_url, status, "denied", {}, io.BytesIO(b"access denied")
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(LlmClientError) as raised:
        LlmClient(LlmConfig(api_key="official-key")).complete("prompt")
    assert raised.value.status_code == status
    assert len(requests) == 1
    assert requests[0].full_url == "https://api.openai.com/v1/chat/completions"
    assert json.loads(requests[0].data)["model"] == "gpt-5.6-sol"
