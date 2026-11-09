"""A genuine deterministic failure remains identical in zero-call replay."""
import pytest

from skillflow.document_guided import runner
from skillflow.doe import formal_runner
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


def test_uncommitted_computation_failure_replays_without_publishing(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    harness = Harness(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    evaluations = []

    def failed_review(*args):
        evaluations.append("compute")
        raise ValueError("Synthetic unresolved collection relation")

    monkeypatch.setattr(formal_runner, "prepare_joint_sensitivity_review", failed_review)
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed" and result["stage"] == "doe"
    assert result["reason"] == "ValueError: Synthetic unresolved collection relation"
    assert len(harness.calls) == 7
    assert all(row["status"] != "running" for row in result["stages"].values())
    directory = harness.directory / "doe"
    before = {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    assert not (directory / "manifest.json").exists()
    assert runner.replay(harness.directory) == result
    assert evaluations == ["compute", "compute"] and len(harness.calls) == 7
    assert before == {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    assert not (directory / "doe-result.json").exists()


def test_failed_replay_cannot_turn_changed_computation_into_success(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    harness = Harness(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    original = formal_runner._compute

    def fail(*args):
        raise ValueError("Synthetic failed computation")

    monkeypatch.setattr(formal_runner, "_compute", fail)
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed"
    monkeypatch.setattr(formal_runner, "_compute", original)
    with pytest.raises(ValueError, match="Replayed guided decisions differ"):
        runner.replay(harness.directory)
    assert len(harness.calls) == 7
    assert not (harness.directory / "doe/manifest.json").exists()
