"""Bounded map-collect preserves occurrences and acquired versions offline."""
from copy import deepcopy

import pytest
from pydantic import ValidationError

from skillflow.propagation.contracts.boundaries import derive_sink_boundaries
from skillflow.propagation.contracts.specs import ForEachSpec, validate_specs
from skillflow.propagation.data import (
    DataRegistry, DataPart, KnownPartsContent, LiteralContent, MappedCollectionContent,
    Origin, WholeExceptContent, SubsetViewContent,
)
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.solver import propagate
from skillflow.doe.constraint_control import collection_size
from tests.propagation.test_collection_scopes import fixture, local, input_ref

EVIDENCE = {"target": {"path": []}, "reason": "Explicit offline map-collect fixture."}


def op(kind, **values):
    return {"op": kind, **values, "evidences": [deepcopy(EVIDENCE)]}


def event(effect, *operations):
    return {"effect": effect, "evidences": [deepcopy(EVIDENCE)], "atomic_ops": list(operations)}


def map_fixture(*, alternatives=False, zero_args=False):
    body = [event("net_send", op("deliver", inputs=[] if zero_args else [local("item")], target="service")),
            event("net_receive", op("receive", location="service",
                                     inputs=[] if zero_args else [local("item")], output="response")),
            event("transform", op("build", container="object", output="record", parts=[
                {"path": ["url"], "value": local("item")},
                {"path": ["response"], "value": local("response")}]))]
    if alternatives:
        body[-1]["atomic_ops"].append(op("build", container="object", output="other", parts=[
            {"path": ["url"], "value": local("item")},
            {"path": ["status"], "value": {"kind": "literal", "value": "alternate"}}]))
    cfg, annotation = fixture(body=body)
    if zero_args:
        # Known zero-argument requests use the tool boundary, not empty networking.
        for child in annotation["ir_semantics"]["ir_process"]["events"][0]["body"][:2]:
            child.pop("evidences")
            child["effect"] = None
        annotation["locations"]["service"]["kind"] = "tool"
    process = cfg["blocks"]["main"]["instructions"][0]
    process["outputs"] = [{"type": "result", "identifier": "batch_result"}]
    spec = annotation["ir_semantics"]["ir_process"]
    loop = spec["events"][0]
    loop["yield"] = ({"kind": "alternatives", "items": [local("record"), local("other")]}
                     if alternatives else local("record"))
    loop["output"] = "batch"
    annotation["locations"]["saved"] = {"kind": "storage", "name": "results.json",
        "operand_refs": [], "access_scope": "task", "retention": "persistent"}
    spec["events"].append(event("fs_write", op("write", target="saved", mode="replace", input=local("batch"))))
    spec["output_bindings"] = [{"output_index": 0, "value": local("batch"), "evidences": [EVIDENCE]}]
    annotation["sink_boundaries"] = [value.model_dump(mode="json") for value in
        derive_sink_boundaries(annotation["locations"], annotation["ir_semantics"])]
    return cfg, annotation


def solve_map(value, *, alternatives=False, zero_args=False, repeated_identity=False):
    cfg, annotation = map_fixture(alternatives=alternatives, zero_args=zero_args)
    registry = DataRegistry("map-collect-offline")
    if repeated_identity:
        same = registry.register_source("same", acquired_from="fixture", content=LiteralContent(value="same-url"))
        source = registry.register_source("urls", acquired_from="fixture", content=KnownPartsContent(
            parts=[DataPart(path=[index], data=same.id) for index in range(2)], parts_complete=True))
    else:
        source = registry.register_source("urls", acquired_from="fixture",
            **({"content": LiteralContent(value=value)} if value is not None else {}))
    initial = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset([source.id])})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=initial)
    assert result.status == "complete", result.diagnostics
    return cfg, annotation, result, source.id


def test_collect_reaches_actual_save_and_public_result_without_observing_local_body():
    _, _, result, _ = solve_map(["url-a", "url-b"])
    record = result.records.get("ir_process")
    loop = record.events[0]
    assert len(loop.instances) == 2 and len(loop.outputs) == 1
    batch = next(iter(loop.outputs))
    assert record.events[1].atomic_ops[0].inputs == [frozenset([batch])]
    assert next(binding.data_ids for binding in record.exit_state.bindings
                if binding.location == FlowLocation(kind="result", name="batch_result")) == frozenset([batch])
    content = result.registry.get(batch).content
    assert isinstance(content, MappedCollectionContent)
    assert [member.selector for member in content.members] == [0, 1]
    assert all(len(member.values) == 1 for member in content.members)
    assert not any(child.effect == "model_observe" for instance in loop.instances for child in instance.body)
    result.records.validate(require_complete=True)
    assert DataRegistry.from_dict(result.registry.to_dict()).to_dict() == result.registry.to_dict()


@pytest.mark.parametrize("zero_args", [False, True])
def test_equal_value_occurrences_keep_distinct_acquisition_versions(zero_args):
    _, _, result, _ = solve_map(None, zero_args=zero_args, repeated_identity=True)
    loop = result.records.get("ir_process").events[0]
    assert {instance.selector for instance in loop.instances} == {0, 1}
    assert len({instance.element for instance in loop.instances}) == 1
    responses = {next(iter(instance.body[1].atomic_ops[0].outputs[0])) for instance in loop.instances}
    assert len(responses) == 2


def test_empty_map_returns_empty_collection_without_acquisition():
    _, _, result, _ = solve_map([])
    loop = result.records.get("ir_process").events[0]
    assert not loop.instances and len(loop.outputs) == 1
    batch = next(iter(loop.outputs))
    data = {entry["data"]["id"]: entry["data"] for entry in result.registry.to_dict()["records"]}
    assert collection_size(data, batch) == 0
    assert result.registry.get(batch).content.members == []


def test_unknown_member_is_not_a_one_element_count():
    _, _, result, _ = solve_map(None)
    loop = result.records.get("ir_process").events[0]
    assert len(loop.instances) == 1
    data = {entry["data"]["id"]: entry["data"] for entry in result.registry.to_dict()["records"]}
    assert collection_size(data, next(iter(loop.outputs))) is None


def test_alternative_yields_do_not_enumerate_complete_array_products():
    _, _, result, _ = solve_map(["url"] * 18, alternatives=True)
    loop = result.records.get("ir_process").events[0]
    assert len(loop.outputs) == 1 and len(loop.instances) == 18
    content = result.registry.get(next(iter(loop.outputs))).content
    assert len(content.members) == 18 and all(len(member.values) == 2 for member in content.members)
    assert len(result.registry.resolve_part_candidates(next(iter(loop.outputs)), [0])) == 2


def test_yield_output_pairing_and_shared_write_rejection():
    cfg, annotation = map_fixture()
    loop = annotation["ir_semantics"]["ir_process"]["events"][0]
    missing = {key: value for key, value in loop.items() if key != "output"}
    with pytest.raises(ValidationError, match="together"):
        ForEachSpec.model_validate(missing)
    loop["body"].append(event("fs_write", op("write", target="saved", mode="replace", input=local("item"))))
    from skillflow.propagation.contracts.profiles import AnnotationPayload
    with pytest.raises(ValueError, match="write shared state"):
        validate_specs(cfg, AnnotationPayload.model_validate(annotation))


def test_read_inside_member_uses_existing_source_version_without_shared_mutation():
    cfg, annotation = map_fixture()
    annotation["locations"]["settings"] = {"kind": "storage", "name": "settings.json",
        "operand_refs": [], "access_scope": "task", "retention": "persistent"}
    body = annotation["ir_semantics"]["ir_process"]["events"][0]["body"]
    body.insert(0, event("fs_read", op("read", location="settings", output="settings_value")))
    annotation["sink_boundaries"] = [value.model_dump(mode="json") for value in
        derive_sink_boundaries(annotation["locations"], annotation["ir_semantics"])]
    registry = DataRegistry("member-read-offline")
    urls = registry.register_source("urls", acquired_from="fixture", content=LiteralContent(value=["a", "b"]))
    settings = registry.register_source("settings", acquired_from="storage:settings.json")
    initial = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset([urls.id]),
        FlowLocation(kind="storage", name="settings.json"): frozenset([settings.id])})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=initial)
    assert result.status == "complete", result.diagnostics
    record = result.records.get("ir_process")
    before = record.entry_state.get(FlowLocation(kind="storage", name="settings.json"))
    after = record.exit_state.get(FlowLocation(kind="storage", name="settings.json"))
    assert before == frozenset([settings.id])
    assert after is None  # Dead bindings are omitted from the projected exit.
    assert not any(operation.changes for instance in record.events[0].instances
                   for event in instance.body for operation in event.atomic_ops)
    assert all(instance.body[0].atomic_ops[0].outputs == [before] for instance in record.events[0].instances)


def test_collection_output_feedback_seals_finite_equations():
    cfg, annotation = map_fixture()
    cfg["blocks"]["main"]["instructions"][-1]["opcode"] = "dispatch"
    cfg["edges"].append({"source_block_id": "main", "target_block_id": "main"})
    spec = annotation["ir_semantics"]["ir_process"]
    spec["events"].insert(0, event("context_read", op("read", location="collection", output="current")))
    spec["events"][1]["collection"] = local("current")
    spec["events"][-1] = event("context_write", op("write", target="collection", mode="replace", input=local("batch")))
    annotation["sink_boundaries"] = [value.model_dump(mode="json") for value in
        derive_sink_boundaries(annotation["locations"], annotation["ir_semantics"])]
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    assert result.stats["loop_families"] > 0
    assert 0 < result.stats["block_evaluations"] < 50
    from skillflow.propagation.facts import resolved_sink_boundaries, validate_propagation_facts
    validate_propagation_facts(cfg=cfg, annotation=annotation,
        data=[entry["data"] for entry in result.registry.to_dict()["records"]], records=result.records.records_dict(),
        sinks=resolved_sink_boundaries(annotation["locations"], result.records.records_dict()),
        status=result.status, coverage=result.coverage, diagnostics=result.diagnostics)


@pytest.mark.parametrize("filtered", [False, True])
def test_membership_changes_do_not_reuse_original_offsets_as_output_positions(filtered):
    cfg, annotation = map_fixture()
    registry = DataRegistry("map-reindexed-source")
    base = registry.register_source("urls", acquired_from="fixture", content=LiteralContent(value=["a", "b"]))
    source = registry.create_result("view", content=(SubsetViewContent(base=base.id, predicate="keep")
        if filtered else WholeExceptContent(base=base.id, excluded_parts=[[0]])), origin=Origin(at="view"))
    initial = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset([source.id])})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=initial)
    assert result.status == "complete", result.diagnostics
    loop = result.records.get("ir_process").events[0]
    batch = next(iter(loop.outputs))
    candidates = result.registry.resolve_part_candidates(batch, [0])
    assert len(candidates) == (2 if filtered else 1)
    if not filtered:
        assert loop.instances[0].selector == 1


def test_duplicate_deliveries_are_occurrences_even_without_a_collection_output():
    cfg, annotation = fixture(body=[event("net_send", op("deliver", target="service", inputs=[local("item")]))])
    registry = DataRegistry("repeated-delivery-occurrences")
    value = registry.register_source("same", acquired_from="fixture", content=LiteralContent(value="same"))
    source = registry.register_source("items", acquired_from="fixture", content=KnownPartsContent(
        parts=[DataPart(path=[index], data=value.id) for index in range(2)], parts_complete=True))
    initial = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset([source.id])})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=initial)
    assert result.status == "complete", result.diagnostics
    instances = result.records.get("ir_process").events[0].instances
    assert len(instances) == 2 and {instance.selector for instance in instances} == {0, 1}
