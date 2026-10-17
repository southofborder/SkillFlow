"""Frozen runtime assumptions stay identifiable through acceptance and replay."""
import json

import pytest

from skillflow.propagation.contracts.runtime_contract import runtime_contract
from skillflow.propagation.contracts.runtime_contract import runtime_contract_binding
from skillflow.propagation.annotation import runner
from tests.propagation.annotation.helpers import FakeClient
from tests.propagation.annotation.test_security_runner import setup_run, forbidden


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def test_runtime_binding_roundtrip_without_additional_call(tmp_path, monkeypatch):
    directory, _, _ = setup_run(tmp_path)
    expected = runtime_contract_binding(runtime_contract())
    manifest = runner.read_json(directory / "manifest.json")
    assert manifest["runtime_contract"] == expected
    client = FakeClient()
    result = runner.run_annotation(directory, client=client)
    assert result["runtime_contract"] == expected
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    assert runner.replay_run(directory) == result
    assert len(client.prompts) == 1


@pytest.mark.parametrize("change", ["missing", "old", "digest", "rules"])
def test_runtime_identity_refused_before_source_mismatch_or_network(tmp_path, monkeypatch, change):
    directory, _, _ = setup_run(tmp_path)
    manifest = runner._unseal(runner.read_json(directory / "manifest.json"))
    if change == "missing":
        manifest.pop("runtime_contract")
    elif change == "old":
        manifest["runtime_contract"]["version"] = "wide-read-agent-v6"
    elif change == "digest":
        manifest["runtime_contract"]["sha256"] = "0" * 64
    else:
        model = runner.read_json(directory / "inputs/runtime-contract.json")
        model["rules"][0]["text"] = "changed assumption"
        write(directory / "inputs/runtime-contract.json", model)
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
    result["runtime_contract"]["sha256"] = "0" * 64
    write(directory / "result.json", runner.result_snapshot(result))
    before = (directory / "result.json").read_bytes()
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    with pytest.raises(runner.RunIdentityError, match="runtime contract identity"):
        runner.run_annotation(directory, client_factory=forbidden)
    with pytest.raises(runner.RunIdentityError, match="runtime contract identity"):
        runner.replay_run(directory)
    assert (directory / "result.json").read_bytes() == before
    assert len(client.prompts) == 1
