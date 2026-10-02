"""Acquisition, scope and visibility remain separate, without opcode heuristics."""
import pytest

from skill_ir.data import OpaqueContent
from skill_ir.propagation import FlowLocation, propagate
from skill_ir.propagation.handoff import build_doe_input, validate_doe_input
from skill_ir.propagation.specs import validate_specs
from skill_ir.security_profile.evidence import prepare_material
from .test_solver import (
    DEMO, annotation_for, at, input_ref, instruction, linear, literal, local,
    location, operand,
)


@pytest.mark.parametrize("boundary,effect", [("tool", None), ("remote", "net_receive")])
def test_returned_content_is_an_acquired_source_with_request_dependencies(boundary, effect):
    cfg, annotation = linear([
        instruction("query", outputs=["reply"]),
        instruction("inspect", [operand("reply")]),
    ], {
        "query": ([] if effect is None else [effect], [(None if effect is None else 0, [{
            "op": "receive", "location": "catalog", "inputs": [literal("needle"), literal("needle")],
            "output": "reply",
        }])], [local("reply")]),
        "inspect": (["model_observe"], [(0, [{"op": "deliver", "inputs": [input_ref()], "target": "model"}])], []),
    }, {"catalog": (boundary, "catalog.lookup"), "model": ("model_context", "assistant")})
    solved = propagate(cfg, annotation)
    assert solved.status == "complete"
    response = solved.registry.get(at(solved, "ir_query", "reply"))
    assert isinstance(response.content, OpaqueContent)
    assert response.origin.acquired_from == f"{boundary}:catalog.lookup"
    assert len(response.origin.inputs) == 2  # preserve parameter positions
    assert [dependency.relation for dependency in response.origin.dependencies] == ["possible", "possible"]
    assert not solved.initial_data["records"]  # no preallocated tool/remote response
    assert solved.records.get("ir_inspect").events[0].atomic_ops[0].inputs == [frozenset([response.id])]
    source, metadata = DEMO["demo_source"]()
    business = build_doe_input(source, cfg, annotation, solved, source_metadata=metadata,
                               execution_model=prepare_material(source, cfg)["execution_model"])
    assert validate_doe_input(business) == business
    assert business["records"]["ir_query"]["events"][0]["effect"] == effect


def test_tool_compute_is_not_automatically_reclassified_as_acquisition():
    cfg, annotation = linear([instruction("calculate", outputs=["reply"])], {
        "calculate": (["transform"], [(0, [{"op": "compute", "inputs": [literal(17)],
            "dependencies": ["derived"], "output": "reply"}])], [local("reply")]),
    }, {"unused_tool": ("tool", "calculator")})
    solved = propagate(cfg, annotation)
    result = solved.registry.get(at(solved, "ir_calculate", "reply"))
    assert result.origin.acquired_from is None
    assert result.origin.dependencies[0].relation == "derived"
    assert not solved.initial_data["records"]


@pytest.mark.parametrize("wrong_effect,boundary", [
    (None, "remote"), (None, "storage"), ("net_receive", "tool"),
    ("transform", "tool"), ("model_observe", "tool"),
])
def test_specs_and_standalone_facts_reject_incompatible_tool_receipts(wrong_effect, boundary):
    cfg, annotation = linear([instruction("query", outputs=["reply"])], {
        "query": ([], [(None, [{"op": "receive", "location": "catalog", "inputs": [], "output": "reply"}])], [local("reply")]),
    }, {"catalog": ("tool", "catalog.lookup")})
    source, metadata = DEMO["demo_source"]()
    solved = propagate(cfg, annotation)
    business = build_doe_input(source, cfg, annotation, solved, source_metadata=metadata,
                               execution_model=prepare_material(source, cfg)["execution_model"])
    annotation["locations"]["catalog"]["kind"] = boundary
    annotation["profiles"]["ir_query"]["effects"] = [] if wrong_effect is None else [wrong_effect]
    annotation["transfer_specs"]["ir_query"]["events"][0]["effect_index"] = None if wrong_effect is None else 0
    with pytest.raises(ValueError):
        validate_specs(cfg, annotation)
    business["locations"]["catalog"]["kind"] = boundary
    event = business["records"]["ir_query"]["events"][0]
    event["effect"] = wrong_effect
    event["atomic_ops"][0]["endpoints"][0]["kind"] = boundary
    with pytest.raises(ValueError):
        validate_doe_input(business)


def container_selection(*, field_only=False):
    # The original context operand describes the requested target. The explicit
    # transfer locates the related container without claiming value equivalence.
    cfg = {"entry_block_id": "source", "declared_context_keys": ["member"], "blocks": {
        "source": {"block_id": "source", "block_name": "acquire", "data_source_kind": "context", "instructions": [
            instruction("obtain", [operand("member", "context_key")], ["chosen"]),
            instruction("dispatch", opcode="dispatch")]},
        "main": {"block_id": "main", "block_name": "use chosen value", "instructions": [
            instruction("send", [operand("chosen")]), instruction("return", opcode="return")]}},
        "edges": [{"source_block_id": "source", "target_block_id": "main"}]}
    effects = ["context_read", "model_observe"] if field_only else ["context_read", "model_observe", "transform"]
    ops = [
        (0, [{"op": "read", "location": "entry", "output": "read_value"}]),
        (1, [{"op": "deliver", "inputs": [local("read_value")], "target": "model"}]),
    ]
    if not field_only:
        ops.append((2, [{"op": "select_part", "input": local("read_value"), "path": ["member"], "output": "chosen"}]))
    return annotation_for(cfg, {
        "obtain": (effects, ops, [local("read_value" if field_only else "chosen")]),
        "send": (["net_send"], [(0, [{"op": "deliver", "inputs": [input_ref()], "target": "remote"}])], []),
    }, {"entry": ("runtime_context", "isolated-member" if field_only else "request-document"),
        "model": ("model_context", "assistant"), "remote": ("remote", "service")})


def test_related_container_observation_does_not_widen_sent_argument_or_seed_a_second_leaf():
    cfg, annotation = container_selection()
    solved = propagate(cfg, annotation)
    assert solved.status == "complete"
    assert len(solved.initial_data["records"]) == 1
    source = solved.initial_data["records"][0]["data"]
    assert source["origin"]["acquired_from"] == "runtime_context:request-document"
    assert all(binding["location"]["name"] != "member" for binding in solved.initial_state["bindings"])
    chosen = solved.registry.get(at(solved, "ir_obtain", "chosen"))
    assert chosen.origin.part_of == source["id"] and chosen.origin.path == ["member"]
    assert solved.registry.get(source["id"]).content.parts_complete is False
    assert solved.records.get("ir_obtain").events[1].atomic_ops[0].inputs == [frozenset([source["id"]])]
    assert solved.records.get("ir_send").events[0].atomic_ops[0].inputs == [frozenset([chosen.id])]
    assert len(solved.registry) == 2


@pytest.mark.parametrize("observe_whole", [False, True])
def test_local_scan_and_model_processing_keep_different_observation_versions(observe_whole):
    read = {"op": "read", "location": "document", "output": "whole"}
    select = {"op": "select_part", "input": local("whole"), "path": ["account"], "output": "selected"}
    observe = {"op": "deliver", "inputs": [local("whole" if observe_whole else "selected")], "target": "model"}
    effects = ["context_read", "model_observe", "transform"] if observe_whole else ["context_read", "transform", "model_observe"]
    operations = [read, observe, select] if observe_whole else [read, select, observe]
    cfg, annotation = linear([
        instruction("acquire", outputs=["account"]), instruction("send", [operand("account")]),
    ], {
        "acquire": (effects, [(index, [operation]) for index, operation in enumerate(operations)], [local("selected")]),
        "send": (["net_send"], [(0, [{"op": "deliver", "inputs": [input_ref()], "target": "remote"}])], []),
    }, {"document": ("runtime_context", "customer-document"),
        "model": ("model_context", "assistant"), "remote": ("remote", "account-service")})
    solved = propagate(cfg, annotation)
    assert solved.status == "complete" and len(solved.registry) == 2
    whole = solved.initial_data["records"][0]["data"]["id"]
    selected = at(solved, "ir_acquire", "account")
    assert selected != whole
    assert solved.registry.get(selected).origin.part_of == whole
    assert solved.registry.get(whole).content.parts_complete is False
    observed = [operation.inputs for event in solved.records.get("ir_acquire").events
                if event.effect == "model_observe" for operation in event.atomic_ops]
    assert observed == [[frozenset([whole if observe_whole else selected])]]
    assert solved.records.get("ir_send").events[0].atomic_ops[0].inputs == [frozenset([selected])]
    # A source whole can remain registered and in state without automatic observation.
    assert whole in solved.records.get("ir_acquire").exit_state.get(FlowLocation(kind="runtime_context", name="customer-document"))
    assert [event.effect for event in solved.records.get("ir_acquire").events] == effects


def test_explicit_isolated_value_read_does_not_invent_a_parent_container():
    cfg, annotation = container_selection(field_only=True)
    solved = propagate(cfg, annotation)
    chosen = solved.registry.get(at(solved, "ir_obtain", "chosen"))
    assert chosen.origin.acquired_from == "runtime_context:isolated-member"
    assert chosen.origin.part_of is None
    assert len(solved.registry) == 1
    assert solved.records.get("ir_obtain").events[1].atomic_ops[0].inputs == [frozenset([chosen.id])]


def test_distinct_fields_share_one_open_container_without_independent_leaf_seeds():
    cfg = {"entry_block_id": "a", "declared_context_keys": ["target-a", "target-b"], "blocks": {},
           "edges": [{"source_block_id": "a", "target_block_id": "b"}]}
    plans = {}
    for name in ("a", "b"):
        cfg["blocks"][name] = {"block_id": name, "block_name": name, "data_source_kind": "context", "instructions": [
            instruction(name, [operand("target-" + name, "context_key")], [name]),
            instruction("finish_" + name, opcode="dispatch" if name == "a" else "return")]}
        plans[name] = (["context_read", "transform"], [
            (0, [{"op": "read", "location": "payload", "output": "whole"}]),
            (1, [{"op": "select_part", "input": local("whole"), "path": [name], "output": "chosen"}]),
        ], [local("chosen")])
    cfg, annotation = annotation_for(cfg, plans, {"payload": ("runtime_context", "shared-request")})
    solved = propagate(cfg, annotation)
    assert solved.status == "complete"
    assert len(solved.initial_data["records"]) == 1 and len(solved.registry) == 3
    a, b = solved.registry.get(at(solved, "ir_a", "a")), solved.registry.get(at(solved, "ir_b", "b"))
    assert a.id != b.id and a.origin.part_of == b.origin.part_of
    whole = solved.registry.get(a.origin.part_of)
    assert whole.content.parts_complete is False
    assert {tuple(part.path) for part in whole.content.parts} == {("a",), ("b",)}


def test_context_value_used_only_by_nested_alternative_output_still_seeds_all_bound_locations():
    cfg = {"entry_block_id": "main", "declared_context_keys": ["caller_value", "unused"], "blocks": {
        "main": {"block_id": "main", "block_name": "context", "data_source_kind": "context", "instructions": [
            instruction("copy", [operand("caller_value", "context_key"), operand("unused", "context_key")], ["result"]),
            instruction("return", opcode="return")]}}, "edges": []}
    cfg, annotation = annotation_for(cfg, {
        "copy": ([], [], [{"kind": "alternatives", "items": [input_ref(), input_ref()]}]),
    }, {"first": ("runtime_context", "entry-a"), "second": ("runtime_context", "entry-b")})
    for declaration in annotation["locations"].values():
        declaration["operand_refs"] = [{"instruction_id": "ir_copy", "side": "input", "index": 0}]
    solved = propagate(cfg, annotation)
    assert solved.status == "complete"
    assert len(solved.initial_data["records"]) == len(solved.registry) == 2
    assert {binding["location"]["name"] for binding in solved.initial_state["bindings"]} == {"entry-a", "entry-b"}
    assert len(solved.records.get("ir_copy").exit_state.get(location("result"))) == 2


@pytest.mark.parametrize("feedback", [False, True])
def test_tool_receipt_stable_retry_and_context_feedback_share_value_location_resolution(feedback):
    cfg = {"entry_block_id": "loop", "declared_context_keys": ["request-value"], "blocks": {
        "loop": {"block_id": "loop", "block_name": "retry", "data_source_kind": "context", "instructions": [
            instruction("query", [operand("request-value", "context_key")], ["reply"]),
            instruction("continue", opcode="dispatch")]},
        "update": {"block_id": "update", "block_name": "after query", "instructions": [
            *([instruction("save", [operand("reply")])] if feedback else []),
            instruction("again", [{"type": "literal", "literal_value": True}], opcode="dispatch")]},
        "end": {"block_id": "end", "block_name": "end", "instructions": [instruction("return", opcode="return")]}},
        "edges": [{"source_block_id": "loop", "target_block_id": "update"},
                  *[{"source_block_id": "update", "target_block_id": target} for target in ("loop", "end")]]}
    plans = {"query": ([], [(None, [{"op": "receive", "location": "catalog", "inputs": [input_ref()], "output": "reply"}])], [local("reply")])}
    if feedback:
        plans["save"] = (["context_write"], [(0, [{"op": "write", "target": "query-slot", "mode": "replace", "input": input_ref()}])], [])
    cfg, annotation = annotation_for(cfg, plans, {"catalog": ("tool", "catalog.lookup"), "query-slot": ("runtime_context", "request-cache")})
    annotation["locations"]["query-slot"]["operand_refs"] = [{"instruction_id": "ir_query", "side": "input", "index": 0}]
    fifo, lifo = propagate(cfg, annotation), propagate(cfg, annotation, schedule="lifo")
    assert fifo.status == lifo.status == ("unsupported_feedback" if feedback else "complete")
    assert fifo.records.records_dict() == lifo.records.records_dict()
    assert fifo.registry.to_dict() == lifo.registry.to_dict()
    assert len(fifo.initial_data["records"]) == 1
    assert fifo.initial_data["records"][0]["data"]["origin"]["acquired_from"] == "runtime_context:request-cache"
    if not feedback:
        assert len(fifo.registry) == 2 and fifo.stats["block_evaluations"] < 10


def test_latest_prior_doe_version_is_explicitly_rejected():
    cfg, annotation = linear([], {})
    source, metadata = DEMO["demo_source"]()
    previous = build_doe_input(source, cfg, annotation, propagate(cfg, annotation),
        source_metadata=metadata, execution_model=prepare_material(source, cfg)["execution_model"])
    previous["schema_version"] = "skillflow-doe-input-v5"
    with pytest.raises(ValueError):
        validate_doe_input(previous)
