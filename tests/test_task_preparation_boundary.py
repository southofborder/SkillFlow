"""Recover source-only Task preparation from its frozen root, with no active rereads."""
import json

import pytest

from skillflow import pipeline
from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import injected_factory
from skillflow.task import runner as tasks
from tests.propagation.annotation.helpers import graph


def inputs(tmp_path):
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("Return the original label.\n", encoding="utf-8")
    cfg = tmp_path / "analysis.json"
    cfg.write_text(json.dumps({"cfg": graph()}), encoding="utf-8")
    return skill, cfg, tmp_path / "analysis-run"


def interrupted_preparation(tmp_path, monkeypatch, cut="before_task"):
    skill, cfg, directory = inputs(tmp_path)
    with monkeypatch.context() as scoped:
        if cut == "before_task":
            def stop(*_args, **_kwargs):
                raise KeyboardInterrupt("before Task preparation")
            scoped.setattr(tasks, "prepare_task_run", stop)
        elif cut == "after_request":
            original = ArtifactWriter.json
            def stop(writer, path, value):
                original(writer, path, value)
                if path == directory / "task/inputs/request.json":
                    raise KeyboardInterrupt("after Task request")
            scoped.setattr(ArtifactWriter, "json", stop)
        else:
            original = tasks._write_exact_text
            def stop(path, value, writer):
                original(path, value, writer)
                raise KeyboardInterrupt("after Task prompt")
            scoped.setattr(tasks, "_write_exact_text", stop)
        with pytest.raises(KeyboardInterrupt):
            pipeline.prepare_analysis_run(skill, cfg, run_dir=directory, user_request="Return label.")
    assert (directory / "manifest.json").is_file()
    assert not (directory / "task/manifest.json").exists()
    return skill, cfg, directory


@pytest.mark.parametrize("cut", ["before_task", "after_request", "after_prompt"])
def test_prepare_resumes_task_prefix_from_frozen_owner_when_original_inputs_are_gone(tmp_path, monkeypatch, cut):
    skill, cfg, directory = interrupted_preparation(tmp_path, monkeypatch, cut)
    manifest_bytes = (directory / "manifest.json").read_bytes()
    frozen = {p.name: p.read_bytes() for p in (directory / "inputs").iterdir() if p.is_file()}
    (skill / "SKILL.md").unlink()
    skill.rmdir()
    cfg.unlink()
    with pytest.raises(pipeline.PipelineIdentityError, match="Task preparation is incomplete"):
        pipeline.verify_analysis_prepared(directory)
    result = pipeline.prepare_analysis_run(skill, cfg, run_dir=directory, user_request="Return label.")
    assert result["preparation_status"] == "ready"
    assert (directory / "manifest.json").read_bytes() == manifest_bytes
    assert all((directory / "inputs" / name).read_bytes() == value for name, value in frozen.items())
    assert pipeline.verify_analysis_prepared(directory)["preparation_status"] == "ready"
    assert not (directory / "task/calls").exists()
    with pytest.raises(pipeline.PipelineIdentityError, match="new pipeline directory"):
        pipeline.prepare_analysis_run(skill, cfg, run_dir=directory, user_request="Return label.")


def test_live_run_lazily_prepares_task_but_replay_does_not_create_it(tmp_path, monkeypatch):
    skill, cfg, directory = interrupted_preparation(tmp_path, monkeypatch, "after_request")
    before = {str(p.relative_to(directory)): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    with pytest.raises(pipeline.PipelineIdentityError, match="Task preparation is incomplete"):
        pipeline.run_analysis(directory, replay=True)
    assert before == {str(p.relative_to(directory)): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    class InterruptedClient:
        prompts = []
        def complete(self, prompt):
            self.prompts.append(prompt)
            raise KeyboardInterrupt("stop after local Task preparation")
    client = InterruptedClient()
    result = pipeline.run_analysis(directory, client_factory=injected_factory(client))
    assert result["status"] == "interrupted"
    assert len(client.prompts) == 1
    assert (directory / "task/manifest.json").is_file()
    assert not (directory / "annotation").exists()


@pytest.mark.parametrize("mutation", ["user_request", "cfg_path", "config", "frozen_cfg"])
def test_resume_refuses_changed_request_or_frozen_cfg(tmp_path, monkeypatch, mutation):
    skill, cfg, directory = interrupted_preparation(tmp_path, monkeypatch)
    before_manifest = (directory / "manifest.json").read_bytes()
    kwargs = {"user_request": "Return label."}
    if mutation == "user_request":
        kwargs["user_request"] = "Return all data."
    elif mutation == "cfg_path":
        cfg = tmp_path / "different-analysis.json"
    elif mutation == "config":
        kwargs["config"] = {"model": "different-model"}
    else:
        (directory / "inputs/cfg.json").write_text("{}", encoding="utf-8")
    with pytest.raises(pipeline.PipelineIdentityError):
        pipeline.prepare_analysis_run(skill, cfg, run_dir=directory, **kwargs)
    assert (directory / "manifest.json").read_bytes() == before_manifest
    assert not (directory / "task/manifest.json").exists()


def test_task_preparation_recovery_rejects_unknown_artifacts_without_new_calls(tmp_path, monkeypatch):
    skill, cfg, directory = interrupted_preparation(tmp_path, monkeypatch)
    path = directory / "task/result.json"
    path.parent.mkdir()
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(tasks.TaskRunIdentityError, match="Unknown file"):
        pipeline.prepare_analysis_run(skill, cfg, run_dir=directory, user_request="Return label.")
    assert path.read_text(encoding="utf-8") == "{}"
    assert not (directory / "task/manifest.json").exists()
