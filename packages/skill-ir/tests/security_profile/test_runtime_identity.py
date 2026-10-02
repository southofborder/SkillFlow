"""Frozen runtime assumptions stay identifiable through acceptance and replay."""
import json

import pytest

from skill_ir.runtime_contract import execution_model, execution_model_binding
from skill_ir.security_profile import runner
from security_profile.helpers import FakeClient
from security_profile.test_security_runner import setup_run, forbidden


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def test_runtime_binding_roundtrip_without_additional_call(tmp_path, monkeypatch):
    directory, _, _ = setup_run(tmp_path)
    expected = execution_model_binding(execution_model())
    manifest = runner.read_json(directory / "manifest.json")
    assert manifest["execution_model"] == expected
    client = FakeClient()
    result = runner.run_annotation(directory, client=client)
    assert result["execution_model"] == expected
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    assert runner.replay_run(directory) == result
    assert len(client.prompts) == 1


@pytest.mark.parametrize("change", ["missing", "old", "digest", "rules"])
def test_runtime_identity_refused_before_source_mismatch_or_network(tmp_path, monkeypatch, change):
    directory, _, _ = setup_run(tmp_path)
    manifest = runner._unseal(runner.read_json(directory / "manifest.json"))
    if change == "missing":
        manifest.pop("execution_model")
    elif change == "old":
        manifest["execution_model"]["version"] = "wide-read-agent-v6"
    elif change == "digest":
        manifest["execution_model"]["sha256"] = "0" * 64
    else:
        material = runner.read_json(directory / "inputs/material.json")
        material["execution_model"]["rules"][0]["text"] = "changed assumption"
        write(directory / "inputs/material.json", material)
    manifest["implementation"] = {"old": "implementation"}
    write(directory / "manifest.json", runner._seal(manifest))
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    with pytest.raises(runner.RunIdentityError, match="runtime contract identity"):
        runner.run_annotation(directory, client_factory=forbidden)
    with pytest.raises(runner.RunIdentityError, match="runtime contract identity"):
        runner.replay_run(directory)
    assert not (directory / runner.CALL_PATH / "call.json").exists()


def test_accepted_result_contract_tampering_is_not_silently_repaired(tmp_path, monkeypatch):
    directory, _, _ = setup_run(tmp_path)
    client = FakeClient()
    result = runner.run_annotation(directory, client=client)
    result["execution_model"]["sha256"] = "0" * 64
    write(directory / "result.json", result)
    before = (directory / "result.json").read_bytes()
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    with pytest.raises(runner.RunIdentityError, match="runtime contract identity"):
        runner.run_annotation(directory, client_factory=forbidden)
    with pytest.raises(runner.RunIdentityError, match="runtime contract identity"):
        runner.replay_run(directory)
    assert (directory / "result.json").read_bytes() == before
    assert len(client.prompts) == 1
