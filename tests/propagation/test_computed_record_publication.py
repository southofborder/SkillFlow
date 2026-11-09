"""Trusted computation publication and strict, read-only legacy record loading."""
from copy import deepcopy

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import read_json, sha_file
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.models import FlowState, IRFlowRecord
from skillflow.propagation.records import PropagationRecords
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION as PROFILE_VERSION
from skillflow.propagation.runner import load_propagation_materials, replay_propagation, run_propagation
from tests.propagation.test_records import records_case
from tests.propagation.test_runner import annotation_run, components, reseal


def computed_store(case):
    store, registry, *_ = case
    registry.enable_computation()
    return PropagationRecords.from_computation(store.cfg, store.annotation, registry,
        profile_schema_version=PROFILE_VERSION, annotation_cfg_sha256=store._annotation_cfg_sha256,
        initial_data=store.initial_data, initial_state=FlowState.model_validate(store.initial_state))


def test_computed_constructor_put_and_reference_check_do_not_repeat_full_validation(records_case, monkeypatch):
    store, registry, *_ = records_case
    registry.enable_computation()
    inputs = (store.cfg, store.annotation, registry)
    metadata = dict(profile_schema_version=PROFILE_VERSION,
        annotation_cfg_sha256=store._annotation_cfg_sha256, initial_data=store.initial_data,
        initial_state=FlowState.model_validate(store.initial_state))
    import skillflow.propagation.records as module

    def full_validation(*args, **kwargs):
        pytest.fail("The computation path repeated whole input or record validation")

    for name in ("_graph_payload", "_annotation_payload", "validate_specs"):
        monkeypatch.setattr(module, name, full_validation)
    monkeypatch.setattr(DataRegistry, "validate", full_validation)
    monkeypatch.setattr(PropagationRecords, "_validate_record", full_validation)
    computed = PropagationRecords.from_computation(*inputs, **metadata)
    record = records_case[-1]
    computed.put_computed("ir_action", record)
    record.events.clear()
    computed.check_references()
    assert len(computed.get("ir_action").events) == 3
    assert computed.computation_owned


def test_computed_references_still_reject_missing_evidence(records_case):
    store = computed_store(records_case)
    record = records_case[-1].model_copy(deep=True)
    record.events[0].atomic_ops[0].inputs[0] = frozenset({"missing-data"})
    store.put_computed("ir_action", record)
    with pytest.raises(ValueError, match="unknown Data reference"):
        store.check_references()
    record = records_case[-1].model_copy(update={"exit_state": FlowState()})
    store.put_computed("ir_action", record)
    with pytest.raises(ValueError, match="public output binding"):
        store.check_references()


def test_external_store_cannot_accept_unchecked_computed_records(records_case):
    store = records_case[0]
    with pytest.raises(ValueError, match="internal computation owner"):
        store.put_computed("ir_action", records_case[-1])
    record = records_case[-1].model_copy(deep=True)
    record.events[0].atomic_ops.clear()
    with pytest.raises(ValueError, match="coverage"):
        store.put("ir_action", record)


def test_projected_report_omission_is_not_a_deletion():
    from skillflow.propagation.report import _changes
    record = {"entry_state": {"bindings": [{"location": {"kind": "result", "name": "old"},
                                            "data_ids": ["value"]}]},
              "exit_state": {"bindings": []}, "events": []}
    assert _changes(record) == []
    record["events"] = [{"atomic_ops": [{"changes": [{"location": {"kind": "storage", "name": "saved"},
        "before": ["value"], "after": [], "update": "delete"}]}]}]
    assert _changes(record) == [{"location": {"kind": "storage", "name": "saved"},
                                 "before": ["value"], "after": []}]


def test_current_publication_reuses_computed_materials(annotation_run, tmp_path, monkeypatch):
    import skillflow.propagation.loading as loading
    import skillflow.propagation.runner as runner
    from skillflow.propagation.annotation.loading import load_annotation_run
    from skillflow.propagation.annotation.services import to_payload
    loaded = load_annotation_run(annotation_run)
    solved = runner._calculate(loaded["material"]["cfg"], to_payload(loaded["compiled_annotation"]), None, None)

    def repeated(*args, **kwargs):
        pytest.fail("Saving computed facts repeated full validation")

    with monkeypatch.context() as save:
        save.setattr(DataRegistry, "validate", repeated)
        save.setattr(PropagationRecords, "validate", repeated)
        save.setattr(loading, "validate_propagation_facts", repeated)
        saved = runner.save_propagation_run(tmp_path / "computed", annotation_run=annotation_run,
                                            solved=solved, _loaded_annotation=loaded)
    assert saved.manifest["identity"] == "skill-ir-propagation-v21"
    assert saved.manifest["records_schema_version"] == "skillflow-propagation-record-v16"
    assert components(load_propagation_materials(tmp_path / "computed")) == components(saved)


def test_authored_v20_complete_snapshots_are_read_only(annotation_run, tmp_path):
    directory = tmp_path / "authored-legacy"
    run_propagation(annotation_run, run_dir=directory)
    records = read_json(directory / "records.json")
    # Build a fresh authored complete-state fixture. No historical run is read,
    # rewritten, migrated or replayed to produce this compatibility receipt.
    prior = {}
    for record in records.values():
        for side in ("entry_state", "exit_state"):
            for binding in record[side]["bindings"]:
                prior[(binding["location"]["kind"], binding["location"]["name"])] = deepcopy(binding)
            record[side]["bindings"] = [deepcopy(prior[key]) for key in sorted(prior)]
    writer = ArtifactWriter(())
    writer.json(directory / "records.json", records)
    manifest = read_json(directory / "manifest.json")
    manifest.update(identity="skill-ir-propagation-v20", schema_version=20,
                    records_schema_version="skillflow-propagation-record-v15")
    manifest["artifacts"]["records.json"] = sha_file(directory / "records.json")
    reseal(directory, manifest)
    before = {path.relative_to(directory): path.read_bytes() for path in directory.rglob("*") if path.is_file()}
    loaded = load_propagation_materials(directory)
    assert loaded.records == records
    assert loaded.manifest["identity"] == "skill-ir-propagation-v20"
    assert before == {path.relative_to(directory): path.read_bytes() for path in directory.rglob("*") if path.is_file()}
    with pytest.raises(ValueError, match="read-only"):
        replay_propagation(directory)
    assert not (directory / "replay").exists()


def test_mixed_record_and_run_versions_are_rejected(annotation_run, tmp_path):
    directory = tmp_path / "mixed-version"
    run_propagation(annotation_run, run_dir=directory)
    manifest = read_json(directory / "manifest.json")
    manifest["records_schema_version"] = "skillflow-propagation-record-v15"
    reseal(directory, manifest)
    with pytest.raises(ValueError, match="Unsupported propagation run version"):
        load_propagation_materials(directory)
