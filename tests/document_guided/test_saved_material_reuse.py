"""Ordinary material reads reuse decisions; explicit new-fixture replay validates."""
from copy import deepcopy
import pytest

from skillflow.document_guided import annotation_wire, online, runner
from skillflow.propagation import loading, runner as propagation
from tests.document_guided.test_online import Client
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


@pytest.fixture(autouse=True)
def frozen_offline_producer(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


def test_saved_corrected_step_skips_semantic_chain_and_explicit_recompute_replays(tmp_path, monkeypatch):
    stage = tmp_path / "stage"
    online.prepare_step(stage, "Return the synthetic location records.", kind="locations")
    value = {"locations": {}, "location_evidences": {}}
    client = Client({**value, "ir_semantics": {}}, value)
    assert online.run_step(stage, client=client) == value
    count = 0
    original = online._run_candidate
    def tracked(*args, **kwargs):
        nonlocal count
        count += 1
        return original(*args, **kwargs)
    monkeypatch.setattr(online, "_run_candidate", tracked)
    assert online.load_step(stage) == value
    assert count == 0
    assert online.load_step(stage, recompute=True) == value
    assert count == 1 and client.calls == 2
    response = stage / "calls/a002/response.json"
    response.write_text('{"changed": true}', encoding="utf-8")
    with pytest.raises(ValueError, match="response or prompt changed"):
        online.load_step(stage)


def test_saved_step_rejects_value_or_dependency_changes(tmp_path):
    dependency = tmp_path / "source.txt"
    dependency.write_text("Frozen source.", encoding="utf-8")
    stage = tmp_path / "stage"
    online.prepare_step(stage, "Describe the frozen source.", kind="document", dependencies=[dependency])
    online.run_step(stage, client=Client("# Flow\nKeep the original relationship."))
    value = stage / "document.md"
    original = value.read_bytes()
    value.write_bytes(original + b"changed")
    with pytest.raises(ValueError, match="differs"):
        online.load_step(stage)
    value.write_bytes(original)
    dependency.write_text("Different source.", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        online.load_step(stage)


def test_guided_saved_annotation_and_publication_reuse_validated_material(tmp_path, monkeypatch):
    harness = Harness(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    def stop_before_backend(state):
        if state["stage"] == "propagation":
            raise KeyboardInterrupt("Offline reuse fixture stops before the backend.")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=stop_before_backend)
    assert result["status"] == "interrupted" and len(harness.calls) == 7
    annotation = harness.directory / "annotation"
    expected = online.load_annotation(annotation)
    original_load = propagation.load_annotation_run
    loads = 0
    def tracked(*args, **kwargs):
        nonlocal loads
        loads += 1
        return original_load(*args, **kwargs)
    def forbidden(*args, **kwargs):
        raise AssertionError("A checked ordinary read must not reconstruct semantic material")
    with monkeypatch.context() as patch:
        patch.setattr(online, "_assembled_values", forbidden)
        patch.setattr(online, "_run_candidate", forbidden)
        patch.setattr(annotation_wire, "compile_flat_response", forbidden)
        patch.setattr(propagation, "load_annotation_run", tracked)
        loaded = online.load_annotation(annotation)
        for key in ("raw_annotation", "compiled_annotation", "mapping", "wire_annotation"):
            assert loaded[key] == expected[key]
        facts = propagation.run_propagation(annotation, run_dir=harness.directory / "propagation")
        assert loads == 1
        assert facts.records and facts.manifest
        propagation.check_propagation_unchanged(harness.directory / "propagation", facts.manifest)
        assert loads == 1
    # Explicit reconstruction is still available, with the original implementation pin.
    rebuilt = online.load_annotation(annotation, recompute=True)
    assert rebuilt["compiled_annotation"] == expected["compiled_annotation"]
    saved = annotation / "audit/compiled-response.json"
    saved.write_bytes(saved.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed"):
        propagation.check_propagation_unchanged(harness.directory / "propagation", facts.manifest)


def test_seven_call_run_and_new_fixture_zero_call_replay_preserve_material(tmp_path):
    harness = Harness(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete" and len(harness.calls) == 7
    saved = {str(p.relative_to(harness.directory)): p.read_bytes()
             for p in harness.directory.rglob("response.json")}
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 7
    assert saved == {str(p.relative_to(harness.directory)): p.read_bytes()
                     for p in harness.directory.rglob("response.json")}


def test_public_raw_material_compilation_remains_enabled(tmp_path, monkeypatch):
    from tests.document_guided.test_fragments import fixture
    material, wire, _ = fixture()
    _, raw, compiled, mapping = annotation_wire.compile_flat_response(wire, material)
    count = 0
    original = annotation_wire.compile_flat_response
    def checked(*args, **kwargs):
        nonlocal count
        count += 1
        return original(*args, **kwargs)
    monkeypatch.setattr(annotation_wire, "compile_flat_response", checked)
    compiled = deepcopy(compiled)
    compiled["outcome"] = "changed"
    with pytest.raises(ValueError, match="annotation or compilation differs"):
        loading.materials_from_result(None, material=material, raw_annotation=raw,
            compiled_annotation=compiled, mapping=mapping, wire_annotation=wire)
    assert count == 1
