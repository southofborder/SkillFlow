"""Only exact preparation prefixes may resume; accepted calls are never rebuilt."""
from copy import deepcopy

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.task import runner
from tests.task.test_protocol import source, candidate, Client, inventory


def test_exact_partial_task_inputs_resume_without_overwriting_saved_bytes(tmp_path, monkeypatch):
    directory = tmp_path / "task"
    original = runner._write_exact_text
    def stop_after_prompt(path, text, writer):
        original(path, text, writer)
        raise KeyboardInterrupt("after Task prompt")
    with monkeypatch.context() as scoped:
        scoped.setattr(runner, "_write_exact_text", stop_after_prompt)
        with pytest.raises(KeyboardInterrupt):
            runner.prepare_task_run(directory, source())
    before = inventory(directory)
    assert not (directory / "manifest.json").exists()
    runner.prepare_task_run(directory, source(), resume_preparation=True)
    assert all((directory / name).read_bytes() == value for name, value in before.items())
    assert runner.run_task(directory, client=Client(candidate()))["status"] == "complete"
    accepted = inventory(directory)
    runner.prepare_task_run(directory, source(), resume_preparation=True)
    assert inventory(directory) == accepted


@pytest.mark.parametrize("unexpected", ["calls/task/a001/call.json", "result.json", "task.json", "unknown.txt"])
def test_missing_manifest_with_model_or_unknown_artifacts_is_not_reconstructed(tmp_path, unexpected):
    directory = tmp_path / "task"
    path = directory / unexpected
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(runner.TaskRunIdentityError, match="Unknown"):
        runner.prepare_task_run(directory, source(), resume_preparation=True)
    assert path.read_text(encoding="utf-8") == "{}"
    assert not (directory / "manifest.json").exists()
    assert not (directory / "inputs").exists()


def test_different_partial_prompt_is_rejected_before_any_input_is_rewritten(tmp_path, monkeypatch):
    directory = tmp_path / "task"
    original = runner._write_exact_text
    def stop(path, value, writer):
        original(path, value, writer)
        raise KeyboardInterrupt("after prompt")
    with monkeypatch.context() as scoped:
        scoped.setattr(runner, "_write_exact_text", stop)
        with pytest.raises(KeyboardInterrupt):
            runner.prepare_task_run(directory, source())
    (directory / "inputs/prompt.txt").write_bytes(b"different prompt")
    before = inventory(directory)
    with pytest.raises(runner.TaskRunIdentityError, match="input differs"):
        runner.prepare_task_run(directory, source(), resume_preparation=True)
    assert inventory(directory) == before


def test_completed_task_preparation_cannot_accept_a_different_request(tmp_path):
    directory = tmp_path / "task"
    runner.prepare_task_run(directory, source())
    before = inventory(directory)
    with pytest.raises(runner.TaskRunIdentityError, match="different request"):
        runner.prepare_task_run(directory, source(), user_request="A new user task.", resume_preparation=True)
    assert inventory(directory) == before
