import json
from pathlib import Path

import pytest

from tools.doe import document_guided_transport as transport


def test_prospective_prepare_preserves_full_input_and_max(tmp_path, monkeypatch):
    exe = tmp_path / "codex.exe"
    exe.write_bytes(b"offline executable fixture")
    monkeypatch.setattr(transport, "EXECUTABLE", str(exe))
    monkeypatch.setattr(transport, "EXECUTABLE_SHA256", transport.sha256(exe))
    target = tmp_path / "request"
    prepared = transport.prepare(target, "Full source\n原文\r\n")
    assert 'model_reasoning_effort="max"' in prepared["command"]
    assert "--ignore-user-config" in prepared["command"]
    assert not (target / "started.json").exists()
    assert (target / "core.txt").read_bytes() == "Full source\n原文\r\n".encode()
    assert transport.sha256(target / "prompt.txt") == prepared["stdin_sha256"]
    with pytest.raises(ValueError, match="new directory"):
        transport.prepare(target, "different")


def test_started_transport_does_not_resend(tmp_path, monkeypatch):
    exe = tmp_path / "codex.exe"
    exe.write_bytes(b"fixture")
    monkeypatch.setattr(transport, "EXECUTABLE", str(exe))
    monkeypatch.setattr(transport, "EXECUTABLE_SHA256", transport.sha256(exe))
    target = tmp_path / "request"
    transport.prepare(target, "test")
    (target / "started.json").write_text("{}")
    monkeypatch.setattr(transport.subprocess, "Popen", lambda *a, **k: pytest.fail("unexpected dispatch"))
    with pytest.raises(ValueError, match="never resent"):
        transport.execute(target)


def test_accepted_response_reused_and_tamper_rejected(tmp_path, monkeypatch):
    exe = tmp_path / "codex.exe"
    exe.write_bytes(b"fixture")
    monkeypatch.setattr(transport, "EXECUTABLE", str(exe))
    monkeypatch.setattr(transport, "EXECUTABLE_SHA256", transport.sha256(exe))
    target = tmp_path / "request"
    transport.prepare(target, "test")
    (target / "answer.txt").write_bytes(b"accepted")
    (target / "receipt.json").write_bytes(b"{}")
    (target / "accepted.json").write_text(json.dumps({
        "answer_sha256": transport.sha256(target / "answer.txt"),
        "receipt_sha256": transport.sha256(target / "receipt.json"),
        "prepared_sha256": transport.sha256(target / "prepared.json"),
    }))
    monkeypatch.setattr(transport.subprocess, "Popen", lambda *a, **k: pytest.fail("unexpected dispatch"))
    assert transport.execute(target) == "accepted"
    (target / "answer.txt").write_text("changed")
    with pytest.raises(ValueError, match="changed"):
        transport.execute(target)


def test_actual_envelope_limit_stops_before_any_directory_or_process(tmp_path, monkeypatch):
    monkeypatch.setattr(transport.subprocess, "Popen", lambda *a, **k: pytest.fail("unexpected dispatch"))
    target = tmp_path / "oversize"
    with pytest.raises(ValueError, match="no request was started"):
        transport.prepare(target, "x" * 1_048_576)
    assert not target.exists()


def test_native_costs_keep_missing_usage_and_do_not_add_reasoning_twice(tmp_path):
    from tools.doe.document_guided_pilot import transport_metrics
    from tests.document_guided.test_metrics import attempt, final
    # The current passive observer uses public completion events linked to the
    # saved final answer. A legacy receipt-shaped JSON file alone is insufficient.
    attempt(tmp_path, [{"type": "turn.started"}, final("answer"),
        {"type": "turn.completed", "response_id": "r1", "usage": {
            "input_tokens": 10, "output_tokens": 5, "total_tokens": 15,
            "reasoning_output_tokens": 3, "cached_input_tokens": 6}}], stage="first")
    attempt(tmp_path, [], stage="failed", accepted=False)
    result = transport_metrics(tmp_path)
    assert result["cli_dispatches"] == 2
    assert result["unknown_usage_requests"] == 1
    assert result["known_token_usage"]["total_tokens"] == 15
    assert result["known_request_seconds"] == 5
    assert result["http_attempts"] is None


def confirmed_profile(directory):
    directory.mkdir()
    base, developer, catalog = "a" * 64, [["b" * 64]], ["c" * 64]
    (directory / "prepared.json").write_text('{}')
    (directory / "process.json").write_text('{"returncode":0}')
    (directory / "receipt.json").write_text(json.dumps({
        "protocol_status": "conformant", "violations": [],
        "configuration_verified": True, "provider_verified": True,
        "usage_verified": True, "completed": True,
        "base_instructions_sha256": base, "runtime_developer_segment_sha256": developer,
        "confirmed_additional_tools_sha256": catalog,
    }))
    return {"schema_version": transport.PROFILE_VERSION,
            "executable_sha256": transport.EXECUTABLE_SHA256, "cli_version": transport.CLI_VERSION,
            "runtime": transport.EXPECTED, "engineering_checks_passed": True,
            "base_instructions_sha256": base, "developer_segment_sha256": developer,
            "additional_tools_sha256": catalog,
            "confirmation": {"directory": str(directory), "files": {
                name: transport.sha256(directory / name)
                for name in ("prepared.json", "receipt.json", "process.json")}}}


def test_new_analysis_rejects_bare_old_profile_and_changed_confirmation(tmp_path):
    profile = confirmed_profile(tmp_path / "confirmation")
    assert transport.validate_profile(profile) == profile
    with pytest.raises(ValueError, match="Confirm the current"):
        transport.validate_profile({**profile, "schema_version": transport.VERSION})
    with pytest.raises(ValueError, match="does not match"):
        transport.validate_profile({**profile, "additional_tools_sha256": ["d" * 64]})
    (tmp_path / "confirmation/receipt.json").write_text('{}')
    with pytest.raises(ValueError, match="missing or changed"):
        transport.validate_profile(profile)


def test_confirmation_is_explicit_and_reopening_does_not_resend(tmp_path, monkeypatch):
    directory = tmp_path / "confirmation"
    profile = confirmed_profile(directory)
    (directory / "profile.json").write_text(json.dumps(profile))
    prepared = {"core_sha256": transport.receipts.digest(
        'Environment confirmation only. Return exactly {"status":"ready"}.')}
    (directory / "prepared.json").write_text(json.dumps(prepared))
    profile["confirmation"]["files"]["prepared.json"] = transport.sha256(directory / "prepared.json")
    (directory / "profile.json").write_text(json.dumps(profile))
    monkeypatch.setattr(transport, "execute", lambda p: '{"status":"ready"}')
    monkeypatch.setattr(transport, "prepare", lambda *a, **k: pytest.fail("unexpected new request"))
    assert transport.confirm_profile(directory) == profile
