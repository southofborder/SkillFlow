"""Task baseline origin stays distinct from an accepted processing response.

All clients here are explicit engineering fixtures; no remote model is called.
"""
from copy import deepcopy
import json

import pytest

from skillflow.common.recording import canonical_sha256, read_json
from skillflow.doe import formal_runner
from skillflow.propagation.runner import _task_provenance
from tests.doe.test_formal_runner import propagation_run, stable_test_implementation


@pytest.mark.parametrize("binding,expected", [
    ({"task_run_ref": {"path": "../task"}}, "independent_task_run"),
    ({"task_origin": "authored_fixture_reference"}, "authored_fixture"),
    ({"task_origin": "authored_fixture"}, "authored_fixture"),
    ({"task_origin": "independent_extraction"}, "unknown"),
    ({}, "unknown"),
])
def test_task_origin_is_derived_from_checked_owner_binding_not_an_origin_label(binding, expected):
    # This narrow classifier consumes the output of the full annotation loader.
    loaded = {"manifest": binding, "material": {"task": {"task_sha256": "1" * 64}}}
    assert _task_provenance(loaded) == {"kind": expected, "task_sha256": "1" * 64}


@pytest.mark.parametrize("candidate", [
    {"kind": "independent_task_run", "task_sha256": "2" * 64},
    {"kind": "model_extraction", "task_sha256": "1" * 64},
    {"kind": "independent_task_run", "task_sha256": "1" * 64, "verified": True},
])
def test_doe_rejects_mismatched_or_untyped_task_origin(candidate):
    annotation = {"task": {"task_sha256": "1" * 64}}
    with pytest.raises(ValueError, match="Task provenance"):
        formal_runner._checked_task_provenance(annotation, {"task_provenance": candidate})
    assert formal_runner._checked_task_provenance(annotation, {})["kind"] == "unknown"


def _write_manifest(directory, value):
    value = deepcopy(value)
    value["manifest_sha256"] = canonical_sha256({key: item for key, item in value.items() if key != "manifest_sha256"})
    (directory / "manifest.json").write_text(json.dumps(value), encoding="utf-8")


def test_recorded_task_origin_and_readonly_loading_of_prior_current_metadata(propagation_run, tmp_path):
    from skillflow.propagation.runner import load_propagation_materials
    facts = load_propagation_materials(propagation_run)
    expected = {"kind": "independent_task_run", "task_sha256": facts.annotation["task"]["task_sha256"]}
    assert facts.provenance["kind"] == "model_annotation"
    assert facts.provenance["task_provenance"] == expected
    directory = tmp_path / "doe-origin"
    result = formal_runner.run_doe(propagation_run, run_dir=directory)
    assert result["manifest"]["metadata"]["task_provenance"] == expected
    assert result["task_provenance"] == expected
    for name in ("report.html", "report.md"):
        report = (directory / name).read_text(encoding="utf-8")
        assert "Task provenance" in report and "independent_task_run" in report
    # Earlier v4 metadata remains frozen. Reading derives a separate checked view
    # and never fills in or rewrites missing historical fields.
    old = deepcopy(result["manifest"])
    del old["metadata"]["task_provenance"]
    _write_manifest(directory, old)
    before = (directory / "manifest.json").read_bytes()
    loaded = formal_runner.load_doe_run(directory)
    assert "task_provenance" not in loaded["manifest"]["metadata"]
    assert loaded["task_provenance"] == expected
    assert (directory / "manifest.json").read_bytes() == before


def test_authored_task_cannot_be_relabelled_as_independent_after_manifest_reseal(tmp_path):
    from skillflow.propagation.annotation import runner as annotations
    from skillflow.propagation.annotation.inputs import load_prepared_material
    from skillflow.propagation.review.refinement import prepare_refinement_run
    from skillflow.propagation.runner import run_propagation, load_propagation_materials
    from tests.propagation.annotation.test_security_runner import setup_run
    from tests.propagation.annotation.helpers import valid_raw_response, FakeClient
    initial, source, analysis = setup_run(tmp_path)
    material = load_prepared_material(initial)
    raw = valid_raw_response(material)
    owner = tmp_path / "authored-owner"
    prepare_refinement_run(source, analysis, material, raw, run_dir=owner,
        provenance={"kind": "explicit_authored_engineering_fixture"})
    accepted = tmp_path / "accepted-from-authored"
    prepared = annotations.prepare_run(None, None, run_dir=accepted, upstream_run=owner)
    assert prepared["task_origin"] == "authored_fixture_reference"
    assert annotations.run_annotation(accepted, client=FakeClient(raw))["status"] == "complete"
    propagated = tmp_path / "propagated-authored"
    run_propagation(accepted, run_dir=propagated)
    facts = load_propagation_materials(propagated)
    assert facts.provenance["kind"] == "model_annotation"
    assert facts.provenance["task_provenance"]["kind"] == "authored_fixture"
    directory = tmp_path / "doe-authored"
    result = formal_runner.run_doe(propagated, run_dir=directory)
    assert result["manifest"]["metadata"]["task_provenance"]["kind"] == "authored_fixture"
    forged = deepcopy(result["manifest"])
    forged["metadata"]["task_provenance"]["kind"] = "independent_task_run"
    _write_manifest(directory, forged)
    with pytest.raises(ValueError, match="status or metadata differs"):
        formal_runner.load_doe_run(directory)
