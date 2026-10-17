"""Actual stage interruptions and cross-run substitutions remain auditable."""
from pathlib import Path
import json
import shutil

import pytest

from skillflow import pipeline
from skillflow.common.recording import canonical_sha256, injected_factory
from skillflow.doe import formal_runner
from skillflow.propagation import runner as propagation_runner
from skillflow.propagation.annotation import runner as annotation_runner
from tests.test_pipeline import (
    Annotation, SequenceReview, forbidden, offline_stable_implementation,
    prepared,
)


@pytest.mark.parametrize("stage,module,function", [
    ("propagation", propagation_runner, "run_propagation"),
    ("doe", formal_runner, "run_doe"),
])
def test_actual_offline_interrupt_replays_and_resumes_without_calls(tmp_path, monkeypatch, stage, module, function):
    directory = prepared(tmp_path)
    first, review = Annotation(), SequenceReview(["ok"])
    original = getattr(module, function)

    def interrupt(*_args, **kwargs):
        target = Path(kwargs["run_dir"])
        target.mkdir()
        (target / "partial.json").write_text('{"owned":"partial"}', encoding="utf8")
        raise KeyboardInterrupt(f"Interrupted inside {stage}")

    monkeypatch.setattr(module, function, interrupt)
    result = pipeline.run_analysis(directory, client_factory=injected_factory(first),
                                   review_client_factory=injected_factory(review))
    assert result["status"] == "interrupted"
    assert result["stage"] == result["interrupt_point"] == stage
    assert result["unfinished_outputs"]["stage"] == stage
    assert pipeline.replay_analysis(directory) == result
    assert (directory / stage / "partial.json").is_file()

    monkeypatch.setattr(module, function, original)
    resumed = pipeline.run_analysis(directory, client_factory=forbidden, review_client_factory=forbidden)
    assert resumed["status"] in {"complete", "diagnostic"}, resumed
    assert resumed["counts"]["logical_calls"] == 3
    assert len(first.prompts) == len(review.prompts) == 1
    assert not (directory / stage / "partial.json").exists()
    assert pipeline.replay_analysis(directory) == resumed


def test_valid_foreign_doe_is_rejected_by_selected_propagation_binding(tmp_path, monkeypatch):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    complete = prepared(a)
    result = pipeline.run_analysis(complete, client_factory=injected_factory(Annotation()),
        review_client_factory=injected_factory(SequenceReview(["ok"])))
    assert result["doe"] is not None, result
    waiting = prepared(b)
    original = formal_runner.run_doe

    def interrupt_before_save(*_args, **_kwargs):
        raise KeyboardInterrupt("Before DOE save")

    monkeypatch.setattr(formal_runner, "run_doe", interrupt_before_save)
    stopped = pipeline.run_analysis(waiting, client_factory=injected_factory(Annotation()),
        review_client_factory=injected_factory(SequenceReview(["ok"])))
    assert stopped["status"] == "interrupted" and stopped["stage"] == "doe"
    assert stopped["unfinished_outputs"] is None
    monkeypatch.setattr(formal_runner, "run_doe", original)
    shutil.copytree(complete / "doe", waiting / "doe")
    # Relative references resolve in this tree, where the pinned upstream is different.
    with pytest.raises(ValueError, match="Upstream run identity"):
        formal_runner.load_doe_run(waiting / "doe")
    with pytest.raises(ValueError, match="Upstream run identity"):
        pipeline.run_analysis(waiting, client_factory=forbidden, review_client_factory=forbidden)


def test_prepared_child_with_other_task_is_rejected(tmp_path, monkeypatch):
    from tests.propagation.annotation.test_security_runner import setup_run
    _unused, source, graph = setup_run(tmp_path)
    directory = tmp_path / "pipeline"
    pipeline.prepare_analysis_run(source, graph, run_dir=directory, user_request="The intended user task.")
    original = annotation_runner.prepare_run
    def substitute(input, analysis, **kwargs):
        kwargs["user_request"] = "A different, independently supplied user task."
        return original(input, analysis, **kwargs)
    monkeypatch.setattr(annotation_runner, "prepare_run", substitute)
    result = pipeline.run_analysis(directory, client_factory=injected_factory(Annotation()),
                                   review_client_factory=forbidden)
    assert result["status"] == "failed" and result["annotation"]["status"] == "input_error"
    assert not (directory / "annotation/calls").exists()


@pytest.mark.parametrize("claimed_status", ["complete", "diagnostic"])
def test_failed_annotation_cannot_be_resealed_as_finished_analysis(tmp_path, claimed_status):
    directory = prepared(tmp_path)
    result = pipeline.run_analysis(directory, client_factory=injected_factory(Annotation("error")),
                                   review_client_factory=forbidden)
    assert result["status"] == "failed" and result["stage"] == "annotation"
    path = directory / "result.json"
    record = json.loads(path.read_text(encoding="utf8"))
    record["status"] = claimed_status
    record["manifest_sha256"] = canonical_sha256({k: v for k, v in record.items() if k != "manifest_sha256"})
    path.write_text(json.dumps(record), encoding="utf8")
    with pytest.raises(pipeline.PipelineIdentityError):
        pipeline.load_analysis_run(directory)


def test_resealed_policy_cannot_replace_integer_limit_with_boolean(tmp_path):
    directory = prepared(tmp_path)
    path = directory / 'manifest.json'
    manifest = json.loads(path.read_text(encoding='utf8'))
    manifest['policy']['max_repairs'] = True
    manifest['manifest_sha256'] = canonical_sha256({
        key: value for key, value in manifest.items() if key != 'manifest_sha256'})
    path.write_text(json.dumps(manifest), encoding='utf8')
    with pytest.raises(pipeline.PipelineIdentityError, match='source/Task analysis protocol'):
        pipeline.load_analysis_run(directory)


def test_entire_analysis_tree_is_portable_and_uses_canonical_stage_inputs(tmp_path):
    directory = prepared(tmp_path)
    result = pipeline.run_analysis(directory, client_factory=injected_factory(Annotation()),
        review_client_factory=injected_factory(SequenceReview(['ok'])))
    assert result['doe'] is not None, result
    moved = tmp_path / 'moved-analysis'
    shutil.move(str(directory), moved)
    assert pipeline.load_analysis_run(moved)['result'] == result
    assert pipeline.replay_analysis(moved) == result
    facts = propagation_runner.load_propagation_materials(moved / 'propagation')
    assert facts.manifest['upstream']['path'] == '../annotation'
    assert formal_runner.load_doe_run(moved / 'doe')['upstream_identity'] == facts.upstream_identity
    assert not list((moved / 'propagation').rglob('doe-input.json'))
    assert not (moved / 'propagation/audit/material.json').exists()
    assert not (moved / 'doe/audit/annotation.json').exists()
