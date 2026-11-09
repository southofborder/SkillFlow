"""Reuse verified owners while retaining semantic output and version checks."""
from copy import deepcopy

import pytest

from skillflow.doe import formal_runner, demand_material, sensitivity_material
from tests.doe.test_formal_runner import propagation_run, stable_test_implementation
from tests.doe.test_demand_engine import fixture, inp, candidate
from tests.doe.test_sensitivity_engine import declarations


def test_publication_loads_once_and_returns_the_computed_review(propagation_run, tmp_path, monkeypatch):
    original_load = formal_runner._model_bundle
    original_compute = formal_runner._compute
    loads, computed = [], []

    def load(path):
        loads.append(path)
        return original_load(path)

    def compute(*args):
        value = original_compute(*args)
        computed.append(value)
        return value

    monkeypatch.setattr(formal_runner, "_model_bundle", load)
    monkeypatch.setattr(formal_runner, "_compute", compute)
    with monkeypatch.context() as save_only:
        save_only.setattr(formal_runner, "_validate", lambda *_args:
                         pytest.fail("Publication reconstructed a review already validated by its producer"))
        saved = formal_runner.run_doe(propagation_run, run_dir=tmp_path / "doe")
    assert len(loads) == len(computed) == 1
    assert saved["review"] is computed[0][0]
    assert saved["result"] == saved["review"].to_dict()
    restored = formal_runner.load_doe_run(tmp_path / "doe")
    assert restored["result"] == saved["result"]
    assert restored["support"] == saved["support"]
    assert restored["review"].index_dict() == saved["review"].index_dict()
    assert restored["upstream_identity"] == saved["upstream_identity"]


def test_upstream_change_during_compute_rejects_commit_without_second_bundle_load(
        propagation_run, tmp_path, monkeypatch):
    original_load = formal_runner._model_bundle
    original_compute = formal_runner._compute
    loads = []

    def load(path):
        loads.append(path)
        return original_load(path)

    def compute(*args):
        result = original_compute(*args)
        path = propagation_run / "records.json"
        path.write_bytes(path.read_bytes() + b" ")
        return result

    monkeypatch.setattr(formal_runner, "_model_bundle", load)
    monkeypatch.setattr(formal_runner, "_compute", compute)
    with pytest.raises(ValueError, match="changed|digest"):
        formal_runner.run_doe(propagation_run, run_dir=tmp_path / "doe")
    assert len(loads) == 1
    assert not (tmp_path / "doe/manifest.json").exists()


def test_demand_material_reuses_verified_compilation_and_rejects_substitution(monkeypatch):
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}])
    from skillflow.propagation.annotation import services
    from skillflow.document_guided import annotation_wire
    for module, name in ((services, "compile_response"), (annotation_wire, "compile_flat_response")):
        monkeypatch.setattr(module, name, lambda *_args, **_kw:
                            pytest.fail("DOE recompiled its verified propagation candidate"))
    facts, task, annotation, _ = values
    checked = demand_material.checked_demand_material(facts, task, annotation)
    assert checked[2] == annotation
    for section in ("raw_annotation", "compiled_annotation", "mapping"):
        changed = deepcopy(annotation)
        changed[section]["unexpected"] = "different candidate"
        with pytest.raises(ValueError, match="verified propagation candidate"):
            demand_material.checked_demand_material(facts, task, changed)
    # bool/int equality must not turn a modified coordinate into the same input.
    changed = deepcopy(annotation)
    changed["compiled_annotation"]["ir_semantics"]["ir_filter"]["output_bindings"][0]["output_index"] = False
    with pytest.raises(ValueError, match="verified propagation candidate"):
        demand_material.checked_demand_material(facts, task, changed)


def test_sensitivity_validation_builds_one_target_index_and_preserves_comparisons(monkeypatch):
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    facts, task, annotation, targets = values
    requested = candidate(targets)
    sensitivity = declarations()
    prepared = sensitivity_material.prepare_sensitivity_review(
        facts, task, annotation, requested, sensitivity)
    result = prepared.to_dict()
    builds = []
    original = sensitivity_material.build_demand_target_index

    def build(*args):
        builds.append(1)
        return original(*args)

    monkeypatch.setattr(sensitivity_material, "build_demand_target_index", build)
    restored = sensitivity_material.validate_sensitivity_result(result, facts, task, annotation,
        requested, sensitivity, demand_result=prepared.demand_dict())
    assert builds == [1]
    assert restored == result
    assert result["status"] == "complete"
    assert all(row["conclusion"] == "excess_supported"
               for sink in result["sinks"] for row in sink["data_reviews"])
