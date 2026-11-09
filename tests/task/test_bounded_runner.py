"""Document-guided callers opt into a bounded Task chain without changing defaults."""
import json

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.task.runner import prepare_task_run, run_task, TaskRunIdentityError
from tests.task.test_protocol import Client, candidate, source


@pytest.fixture(autouse=True)
def stable_producer_during_concurrent_workspace_edits(monkeypatch):
    files = {"tests/task/test_bounded_runner.py": "offline-fixture"}
    monkeypatch.setattr("skillflow.task.runner.implementation_provenance",
                        lambda: {"files": files, "sha256": canonical_sha256(files)})


def test_preparation_binds_optional_limit_and_replay_keeps_terminal_failure(tmp_path):
    directory = tmp_path / "bounded"
    manifest = prepare_task_run(directory, source(), max_corrections=1)
    assert manifest["policy"]["max_corrections"] == 1
    client = Client({"bad": 1}, {"bad": 2}, candidate())
    result = run_task(directory, client=client, max_corrections=1)
    assert result["status"] == "structural_failure"
    assert result["error_kind"] == "correction_limit"
    assert len(client.prompts) == 2
    assert not (directory / "calls/task/a003").exists()
    replay = run_task(directory, replay=True)
    assert replay == result
    assert run_task(directory) == result
    with pytest.raises(TaskRunIdentityError, match="policy"):
        run_task(directory, max_corrections=2)
    with pytest.raises(TaskRunIdentityError, match="different request"):
        prepare_task_run(directory, source(), resume_preparation=True)


def test_legacy_task_preparation_keeps_unlimited_policy_and_chain_shape(tmp_path):
    manifest = prepare_task_run(tmp_path, source())
    assert "max_corrections" not in manifest["policy"]
    result = run_task(tmp_path, client=Client({"bad": 1}, {"bad": 2}, candidate()))
    assert result["status"] == "complete"
    assert result["counts"]["structural_corrections"] == 2
    assert "max_corrections" not in json.loads((tmp_path / "calls/task/chain.json").read_text())


def test_task_monitor_failure_does_not_change_acceptance_or_replay(tmp_path, monkeypatch):
    import skillflow.task.runner as module
    prepare_task_run(tmp_path, source(), max_corrections=1)
    original_counts = module.chain_counts
    monkeypatch.setattr(module, "chain_counts", lambda *a, **k: (_ for _ in ()).throw(OSError("monitor only")))
    client = Client(candidate())
    result = run_task(tmp_path, client=client)
    assert result["status"] == "complete" and result["counts"] == {"status": "unavailable"}
    monkeypatch.setattr(module, "chain_counts", original_counts)
    assert run_task(tmp_path, replay=True) == result
    assert run_task(tmp_path) == result
    assert len(client.prompts) == 1
    # Observer tolerance does not relax the accepted Task or response-chain identity.
    path = tmp_path / "task.json"
    sealed = json.loads(path.read_text(encoding="utf-8"))
    sealed["purpose"]["text"] = "Changed accepted purpose"
    path.write_text(json.dumps(sealed), encoding="utf-8")
    with pytest.raises(TaskRunIdentityError):
        run_task(tmp_path, replay=True)
