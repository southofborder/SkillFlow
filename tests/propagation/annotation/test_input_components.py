from tests.propagation.annotation.helpers import authored_prepare_run
"""Stages retain their own facts and reference the single frozen input owner."""
import json

import pytest

from skillflow.propagation.annotation import load_annotation_run, load_prepared_material
from skillflow.propagation.annotation import runner as annotation_runner
from skillflow.propagation.review import runner as review_runner
from tests.propagation.annotation.helpers import FakeClient, valid_raw_response
from tests.propagation.annotation.test_security_runner import setup_run
from tests.propagation.review.test_runner import ReviewClient


def test_annotation_source_has_one_byte_owner_and_no_aggregate_material(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    material = load_prepared_material(directory)
    assert not (directory / "inputs/material.json").exists()
    assert not (directory / "inputs/repair-context.json").exists()
    assert not (directory / "inputs/source.json").exists()
    assert (directory / "inputs/package/SKILL.md").is_file()
    assert (directory / "inputs/cfg.json").is_file()
    assert (directory / "inputs/runtime-contract.json").is_file()
    assert json.loads((directory / "inputs/user-request.json").read_text(encoding="utf-8")) is None
    result = annotation_runner.run_annotation(directory, client=FakeClient())
    assert result["status"] == "complete"
    saved = json.loads((directory / "result.json").read_text(encoding="utf-8"))
    assert not annotation_runner.BUSINESS_FIELDS.intersection(saved)
    assert all(not (directory / name).exists() for name in
               ("ir-semantics.json", "locations.json", "sink-boundaries.json"))
    assert load_annotation_run(directory)["material"] == material
    assert annotation_runner.replay_run(directory) == result


def test_accepted_review_rebuilds_source_candidate_and_compilation_from_upstream(tmp_path):
    upstream, _, _ = setup_run(tmp_path)
    assert annotation_runner.run_annotation(upstream, client=FakeClient())["status"] == "complete"
    directory = tmp_path / "review"
    review_runner.prepare_run(upstream, run_dir=directory)
    assert {path.name for path in (directory / "inputs").iterdir()} == {
        "targets.json", "observations.json", "prompt.txt"}
    prepared = review_runner.load_prepared_review_material(directory)
    assert prepared["raw_annotation"] == load_annotation_run(upstream)["raw_annotation"]
    result = review_runner.run_review(directory, client=ReviewClient())
    assert result["status"] == "complete"
    assert review_runner.replay_run(directory) == result


def test_explicit_candidate_retains_only_its_candidate_and_review_coordinates(tmp_path):
    upstream, _, _ = setup_run(tmp_path)
    assert annotation_runner.run_annotation(upstream, client=FakeClient())["status"] == "complete"
    original = load_annotation_run(upstream)
    directory = tmp_path / "candidate-review"
    review_runner.prepare_candidate_run(original["material"], original["raw_annotation"],
        run_dir=directory, provenance={"kind": "offline_authored_candidate"}, upstream_run=upstream)
    assert {path.name for path in (directory / "inputs").iterdir()} == {
        "candidate.json", "provenance.json", "targets.json", "observations.json", "prompt.txt"}
    assert review_runner.load_prepared_review_material(directory)["source"] == original["material"]["source"]
    (upstream / "inputs/user-request.json").write_text('"changed purpose"', encoding="utf-8")
    with pytest.raises(ValueError):
        review_runner.load_prepared_review_material(directory)


def test_failed_preparation_does_not_require_missing_material_parts(tmp_path):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("A small task.", encoding="utf-8")
    analysis = tmp_path / "bad.json"
    analysis.write_text("{}", encoding="utf-8")
    directory = tmp_path / "failed"
    manifest = authored_prepare_run(source, analysis, run_dir=directory)
    assert manifest["preparation_status"] == "input_error"
    result = annotation_runner.run_annotation(directory)
    assert result["status"] == "input_error"
    assert annotation_runner.replay_run(directory) == result


def test_persistent_repair_without_checked_owner_is_not_ready(tmp_path):
    from skillflow.propagation.annotation.requests import build_repair_context
    from skillflow.propagation.review.material import prepare_review_material
    from tests.propagation.review.test_runner import response_for
    original, source, analysis = setup_run(tmp_path)
    material = load_prepared_material(original)
    raw = valid_raw_response(material)
    view = prepare_review_material(material, raw)
    from skillflow.propagation.review.services import validate_response
    reviewed = validate_response(response_for(view, finding=True), view)
    context = build_repair_context(material, raw, view, reviewed)
    directory = tmp_path / "ownerless-repair"
    manifest = authored_prepare_run(source, analysis, run_dir=directory, repair_context=context)
    assert manifest["preparation_status"] == "input_error"
    assert "explicit refinement owner" in manifest["preparation_error"]
    assert not (directory / "inputs/repair-context.json").exists()
    assert annotation_runner.replay_run(directory)["status"] == "input_error"
