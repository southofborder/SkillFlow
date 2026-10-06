"""Behavioral regression for finite, offline propagation and Data identities."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
from pathlib import Path
import runpy
import socket

import pytest

from skillflow.propagation.data import DataReferenceError
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.data import FieldUpdatesContent
from skillflow.propagation.data import KnownPartsContent
from skillflow.propagation.data import LiteralContent
from skillflow.propagation.data import OpaqueContent
from skillflow.propagation.data import WholeExceptContent
from skillflow.propagation import FlowLocation
from skillflow.propagation import FlowState
from skillflow.propagation import PropagationRecords
from skillflow.propagation import propagate
from skillflow.propagation.annotation.services import to_payload


DEMO = runpy.run_path(str(project_root() / "examples" / "propagation" / "propagation_demo.py"))
annotation_for = DEMO["fixture_annotation"]
instruction, operand = DEMO["instruction"], DEMO["operand"]
input_ref, local, literal = DEMO["input_ref"], DEMO["local"], DEMO["literal"]


def location(key, kind="result"):
    return FlowLocation(kind=kind, name=key)


def only(ids):
    assert len(ids) == 1
    return next(iter(ids))


def at(result, ir_id, output):
    return only(result.records.get(ir_id).exit_state.get(location(output)))


def linear(instructions, plans, locations=None, partial_irs=()):
    cfg = {"entry_block_id": "main", "blocks": {"main": {
        "block_id": "main", "block_name": "fixture", "instructions": [
            *instructions, instruction("return", opcode="return"),
        ]}}, "edges": []}
    return annotation_for(cfg, plans, locations, partial_irs)


def read_case(extra, plans, *, locations=None, partial_irs=()):
    return linear([instruction("read", outputs=["B"]), *extra], {
        "read": (["context_read"], [(0, [{"op": "read", "location": "document", "output": "b"}])], [local("b")]),
        **plans,
    }, {"document": ("runtime_context", "document"), **(locations or {})}, partial_irs)


def test_demo_observation_keeps_raw_and_clean_versions_and_network_stages():
    result = DEMO["build_demo"]()
    raw = at(result, "ir_read", "B")
    model = result.records.get("ir_model_filter").events
    clean = at(result, "ir_model_filter", "model_clean")
    assert [event.effect for event in model] == ["model_observe", "transform"]
    assert only(model[0].atomic_ops[0].inputs[0]) == raw
    assert only(model[1].atomic_ops[0].outputs[0]) == clean != raw
    local_events = result.records.get("ir_local_filter").events
    local_clean = at(result, "ir_local_filter", "local_clean")
    assert only(local_events[1].atomic_ops[0].inputs[0]) == local_clean != raw
    assert isinstance(result.registry.get(local_clean).content, WholeExceptContent)
    with pytest.raises(DataReferenceError):
        result.registry.resolve_part(local_clean, ["api_key"])
    network = result.records.get("ir_network").events
    assert only(network[0].atomic_ops[0].inputs[0]) == local_clean
    response = only(network[1].atomic_ops[0].outputs[0])
    assert only(network[2].atomic_ops[0].inputs[0]) == response
    assert result.registry.get(response).origin.acquired_from == "remote:example-service"
    assert result.registry.get(response).origin.inputs == [local_clean]


@pytest.mark.parametrize("as_model", [False, True])
def test_solver_and_records_require_explicit_business_projection(as_model):
    from skillflow.propagation.contracts.profiles import AnnotationResponse
    from skillflow.propagation.records import cfg_sha256
    _, _, cfg, response, registry, state = DEMO["demo_inputs"]()
    response = AnnotationResponse.model_validate(response) if as_model else response
    with pytest.raises(ValueError, match="location_evidences"):
        propagate(cfg, response, initial_registry=registry, initial_state=state)
    with pytest.raises(ValueError, match="location_evidences"):
        PropagationRecords(cfg, response, registry, profile_schema_version="security-profile-v10", annotation_cfg_sha256=cfg_sha256(cfg))
    payload = to_payload(response)
    assert set(payload) == {"profiles", "locations", "transfer_specs", "sink_boundaries"}
    assert propagate(cfg, payload, initial_registry=registry, initial_state=state).status == "complete"


def test_flow_location_uses_name_and_rejects_prior_key():
    with pytest.raises(ValueError):
        FlowLocation.model_validate({"kind": "storage", "key": "cache"})
    storage = FlowLocation(kind="storage", name="cache")
    context = FlowLocation(kind="runtime_context", name="cache")
    state = FlowState.from_mapping({storage: frozenset({"A"}), context: frozenset({"B"})})
    assert state.get(storage) == frozenset({"A"})
    assert state.get(context) == frozenset({"B"})
    assert FlowState.model_validate_json(state.model_dump_json()) == state


def test_one_operand_can_resolve_multiple_named_locations():
    cfg = {"entry_block_id": "main", "declared_context_keys": ["caller_value"],
           "blocks": {"main": {"block_id": "main", "block_name": "source", "data_source_kind": "context", "instructions": [
               instruction("copy", [{"type": "context_key", "identifier": "caller_value"}], ["copied"]),
               instruction("return", opcode="return")]}}, "edges": []}
    cfg, annotation = annotation_for(cfg, {
        "copy": ([], [], [input_ref()]),
    }, {"left": ("runtime_context", "left_container"), "right": ("runtime_context", "right_container")})
    for declaration in annotation["locations"].values():
        declaration["operand_refs"] = [{"instruction_id": "ir_copy", "side": "input", "index": 0}]
    registry = DataRegistry("multiple-locations")
    a = registry.register_source("left", acquired_from="left_container")
    b = registry.register_source("right", acquired_from="right_container")
    state = FlowState.from_mapping({
        location("left_container", "runtime_context"): frozenset({a.id}),
        location("right_container", "runtime_context"): frozenset({b.id}),
    })
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    assert result.status == "complete"
    assert result.records.get("ir_copy").exit_state.get(location("copied")) == frozenset({a.id, b.id})
    assert len(result.registry) == 2


def test_propagation_preserves_explicit_sensitivity_but_generates_no_evidence():
    from skillflow.propagation.data import Annotations
    _, _, cfg, response, registry, state = DEMO["demo_inputs"]()
    raw = next(iter(state.bindings[0].data_ids))
    registry.refine(raw, annotations=Annotations(sensitivity=["explicit-existing-label"], evidences=["external-doe-evidence"]))
    result = propagate(cfg, to_payload(response), initial_registry=registry, initial_state=state)
    assert result.registry.get(raw).annotations.evidences == ["external-doe-evidence"]
    for row in result.registry.to_dict()["records"]:
        data = row["data"]
        assert "evidence_refs" not in str(data)
        if data["id"] != raw:
            assert data["annotations"]["evidences"] == []
            assert data["annotations"]["sensitivity"] == []


def test_demo_field_updates_build_and_unknown_computation_do_not_claim_plaintext():
    result = DEMO["build_demo"]()
    changed = result.registry.get(at(result, "ir_update", "updated"))
    assert isinstance(changed.content, FieldUpdatesContent)
    assert result.registry.resolve_part(changed.id, ["api_key"]).content.value == "[redacted]"
    combined = result.registry.get(at(result, "ir_build", "combined"))
    assert isinstance(combined.content, KnownPartsContent) and combined.content.parts_complete
    assert result.registry.resolve_part(combined.id, ["updated"]).id == changed.id
    computed = result.registry.get(at(result, "ir_opaque", "computed"))
    assert isinstance(computed.content, OpaqueContent)
    assert computed.origin.inputs == [combined.id]
    assert [(item.data, item.relation) for item in computed.origin.dependencies] == [(combined.id, "possible")]
    event = result.records.get("ir_opaque").events[0]
    assert event.effect is None


def test_copy_without_effect_changes_result_binding_but_not_data_identity():
    result = DEMO["build_demo"]()
    record = result.records.get("ir_copy")
    assert record.events == []
    assert record.entry_state.get(location("alias")) is None
    assert at(result, "ir_copy", "alias") == at(result, "ir_opaque", "computed")


def test_write_append_and_delete_change_positions_without_revoking_old_events():
    result = DEMO["build_demo"]()
    saved = result.records.get("ir_save")
    deleted = result.records.get("ir_delete")
    cache = location("cache", "runtime_context")
    assert saved.entry_state.get(cache) is None
    assert saved.exit_state.get(cache) == deleted.entry_state.get(cache)
    assert deleted.exit_state.get(cache) is None
    delete = deleted.events[0].atomic_ops[0]
    assert delete.inputs == [] and delete.outputs == []
    assert delete.changes[0].update == "delete"
    append = result.records.get("ir_append").events[0].atomic_ops[0]
    changed = append.changes[0]
    appended = result.registry.get(only(changed.after))
    assert appended.origin.inputs == [only(changed.before), only(append.inputs[0])]
    assert appended.id not in changed.before
    raw = at(result, "ir_read", "B")
    assert only(result.records.get("ir_model_filter").events[0].atomic_ops[0].inputs[0]) == raw


def test_solver_clones_seed_registry_and_state_and_replays_without_network(monkeypatch):
    _, _, cfg, response, registry, state = DEMO["demo_inputs"]()
    annotation = to_payload(response)
    before = registry.to_dict(), state.model_dump(mode="json"), deepcopy(cfg), deepcopy(annotation)
    monkeypatch.setattr(socket.socket, "connect", lambda *args: pytest.fail("offline solver called network"))
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    assert result.status == "complete"
    assert before == (registry.to_dict(), state.model_dump(mode="json"), cfg, annotation)
    restored = PropagationRecords.from_json(result.records.to_json(), cfg=result.records.cfg,
        annotation=annotation, data_registry=result.registry, initial_data=result.initial_data,
        initial_state=result.initial_state)
    assert restored.to_dict() == result.records.to_dict()


def branch_case():
    blocks = {
        "entry": {"block_id": "entry", "block_name": "branch", "instructions": [instruction("branch", [{"type": "literal", "literal_value": "choice"}], opcode="dispatch")]},
        "left": {"block_id": "left", "block_name": "left", "instructions": [
            instruction("left", outputs=["L"]), instruction("left_end", opcode="dispatch")]},
        "right": {"block_id": "right", "block_name": "right", "instructions": [
            instruction("right", outputs=["R"]), instruction("right_end", opcode="dispatch")]},
        "join": {"block_id": "join", "block_name": "join", "instructions": [
            instruction("join", [operand("L"), operand("R")], ["choice"]),
            instruction("compute", [operand("choice")], ["result"]), instruction("return", opcode="return")]},
    }
    cfg = {"entry_block_id": "entry", "blocks": blocks, "edges": [
        {"source_block_id": a, "target_block_id": b} for a, b in
        [("entry", "left"), ("entry", "right"), ("left", "join"), ("right", "join")]
    ]}
    return annotation_for(cfg, {
        "left": ([], [], [literal("left")]), "right": ([], [], [literal("right")]),
        "join": ([], [], [{"kind": "alternatives", "items": [input_ref(), input_ref(1)]}]),
        "compute": (["transform"], [(0, [{"op": "compute", "inputs": [input_ref()],
                                            "dependencies": ["possible"], "output": "computed"}])], [local("computed")]),
    })


def test_branch_candidates_get_distinct_immutable_derived_identities():
    cfg, annotation = branch_case()
    result = propagate(cfg, annotation)
    assert result.status == "complete"
    choices = result.records.get("ir_join").exit_state.get(location("choice"))
    outputs = result.records.get("ir_compute").exit_state.get(location("result"))
    assert len(choices) == len(outputs) == 2
    assert {tuple(result.registry.get(data).origin.inputs) for data in outputs} == {(data,) for data in choices}
    assert all(isinstance(result.registry.get(data).content, OpaqueContent) for data in outputs)


def test_fifo_lifo_have_identical_canonical_data_and_records():
    cfg, annotation = branch_case()
    fifo, lifo = propagate(cfg, annotation, schedule="fifo"), propagate(cfg, annotation, schedule="lifo")
    assert fifo.status == lifo.status == "complete"
    assert fifo.registry.to_dict() == lifo.registry.to_dict()
    assert fifo.records.to_dict() == lifo.records.to_dict()
    assert fifo.coverage == lifo.coverage


def loop_case(mode):
    irs = [instruction("read", outputs=["B"])]
    plans = {"read": (["context_read"], [(0, [{"op": "read", "location": "document", "output": "b"}])], [local("b")])}
    written = "B"
    if mode == "generate":
        irs.append(instruction("compute", [operand("B")], ["next"]))
        plans["compute"] = (["transform"], [(0, [{"op": "compute", "inputs": [input_ref()],
                                                  "dependencies": ["possible"], "output": "next"}])], [local("next")])
        written = "next"
    if mode == "retry":
        irs.append(instruction("fetch", [operand("B")], ["response"]))
        plans["fetch"] = (["net_receive"], [(0, [{"op": "receive", "location": "service", "inputs": [input_ref()], "output": "response"}])], [local("response")])
    else:
        irs.append(instruction("write", [operand(written)]))
        plans["write"] = (["context_write"], [(0, [{"op": "write", "target": "document", "mode": "replace", "input": input_ref()}])], [])
    irs.append(instruction("repeat", [operand("B")], opcode="dispatch"))
    cfg = {"entry_block_id": "loop", "blocks": {
        "loop": {"block_id": "loop", "block_name": "retry", "instructions": irs},
        "end": {"block_id": "end", "block_name": "end", "instructions": [instruction("return", opcode="return")]},
    }, "edges": [{"source_block_id": "loop", "target_block_id": target} for target in ["loop", "end"]]}
    return annotation_for(cfg, plans, {"document": ("runtime_context", "document"), "service": ("remote", "service")})


@pytest.mark.parametrize("mode", ["copy", "retry"])
def test_stable_copy_and_retry_loops_terminate_without_per_iteration_id_growth(mode):
    cfg, annotation = loop_case(mode)
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    assert result.stats["block_evaluations"] < 8
    assert len(result.registry) == (2 if mode == "retry" else 1)
    assert propagate(cfg, annotation, schedule="lifo").records.to_dict() == result.records.to_dict()


def test_generation_feedback_stops_before_claiming_a_finite_solution():
    cfg, annotation = loop_case("generate")
    result = propagate(cfg, annotation)
    assert result.status == "unsupported_feedback"
    assert len(result.records) == 0
    assert any(item["code"] == "unsupported_feedback" for item in result.diagnostics)
    assert set(result.coverage.values()) == {"not_solved"}


def test_unknown_order_keeps_raw_and_clean_candidates_without_defaulting_to_protection():
    cfg, annotation = read_case([instruction("uncertain", [operand("B")], ["clean"])], {
        "uncertain": (["model_observe", "transform"], [
            (0, [{"op": "deliver", "target": "model", "inputs": [{"kind": "alternatives", "items": [input_ref(), local("clean")]}]}]),
            (1, [{"op": "exclude_parts", "input": input_ref(), "paths": [["secret"]], "output": "clean"}]),
        ], [local("clean")]),
    }, locations={"model": ("model_context", "assistant")}, partial_irs=["ir_uncertain"])
    result = propagate(cfg, annotation)
    assert result.status == "complete"
    raw, clean = at(result, "ir_read", "B"), at(result, "ir_uncertain", "clean")
    observed = result.records.get("ir_uncertain").events[0].atomic_ops[0]
    assert observed.inputs[0] == frozenset([raw, clean])
    assert result.records.effect_order_known("ir_uncertain") is False
    assert result.records.get("ir_uncertain").order == "partial"


def test_explicit_empty_seed_does_not_turn_missing_read_or_result_into_new_source():
    cfg, annotation = read_case([instruction("copy", [operand("B")], ["alias"])], {
        "copy": ([], [], [input_ref()]),
    })
    registry = DataRegistry("empty")
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=FlowState())
    assert result.status == "incomplete"
    assert len(result.registry) == 0
    assert result.coverage["ir_read"] == "unresolved_binding"
    assert result.coverage["ir_copy"] == "not_solved"


def test_selection_keeps_actual_part_identity_and_does_not_narrow_whole_reads():
    cfg, annotation = read_case([instruction("select", [operand("B")], ["owner"])], {
        "select": (["transform"], [(0, [{"op": "select_part", "input": input_ref(),
            "path": ["owner"], "output": "owner"}])], [local("owner")]),
    })
    result = propagate(cfg, annotation)
    assert result.status == "complete"
    whole, part = at(result, "ir_read", "B"), at(result, "ir_select", "owner")
    assert whole != part
    assert result.registry.get(part).origin.part_of == whole
    assert result.registry.get(whole).content.parts_complete is False
    assert only(result.records.get("ir_read").events[0].atomic_ops[0].outputs[0]) == whole
    assert result.stats["block_evaluations"] < 5


def test_literal_selection_is_deterministic_without_open_function_execution():
    cfg, annotation = linear([instruction("select", outputs=["value"])], {
        "select": (["transform"], [(0, [{"op": "select_part", "input": literal({"0": [None]}),
            "path": ["0", 0], "output": "chosen"}])], [local("chosen")]),
    })
    result = propagate(cfg, annotation)
    assert result.status == "complete"
    assert result.registry.get(at(result, "ir_select", "value")).content == LiteralContent(value=None)


@pytest.mark.parametrize("target,expected_update", [("known", "strong"), ("unknown", "weak")])
def test_symbolic_location_writes_preserve_possible_aliases(target, expected_update):
    cfg, annotation = linear([instruction("write")], {
        "write": (["context_write"], [(0, [{"op": "write", "target": target,
            "mode": "replace", "input": literal("new")}])], []),
    }, {"known": ("runtime_context", "cache"), "unknown": ("runtime_context", "symbolic:slot")})
    registry = DataRegistry("alias")
    old = registry.register_source("old", acquired_from="cache")
    cache = location("cache", "runtime_context")
    result = propagate(cfg, annotation, initial_registry=registry,
                       initial_state=FlowState.from_mapping({cache: frozenset([old.id])}))
    assert result.status == "complete"
    record = result.records.get("ir_write")
    change = next(c for c in record.events[0].atomic_ops[0].changes if c.location == cache)
    assert change.update == expected_update
    if target == "known":
        assert old.id not in record.exit_state.get(cache)
    else:
        assert old.id in record.exit_state.get(cache)


def test_append_does_not_reseed_absent_storage_after_authoritative_empty_seed():
    cfg, annotation = linear([instruction("append")], {
        "append": (["fs_write"], [(0, [{"op": "write", "target": "journal",
            "mode": "append", "input": literal("line")}])], []),
    }, {"journal": ("storage", "journal")})
    registry = DataRegistry("absent-storage")
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=FlowState())
    assert result.status == "incomplete"
    assert not any(item["identity"]["kind"] == "source" for item in result.registry.to_dict()["records"])


def test_resource_exhaustion_is_explicit_not_a_truncated_complete_result():
    cfg, annotation = branch_case()
    result = propagate(cfg, annotation, max_variants=1)
    assert result.status == "resource_limit"
    assert any(item["code"] == "resource_limit" for item in result.diagnostics)


@pytest.mark.parametrize("schedule", ["random", "", None])
def test_unknown_schedule_is_rejected(schedule):
    cfg, annotation = branch_case()
    with pytest.raises(ValueError):
        propagate(cfg, annotation, schedule=schedule)


def late_input_case(*, select_missing=False):
    """An acyclic join may be visited before the longer defining branch."""
    blocks = {
        "entry": {"block_id": "entry", "block_name": "branch", "instructions": [
            instruction("branch", [{"type": "literal", "literal_value": "choice"}], opcode="dispatch")]},
        "left": {"block_id": "left", "block_name": "left", "instructions": [instruction("left_end", opcode="dispatch")]},
        "right1": {"block_id": "right1", "block_name": "right1", "instructions": [instruction("right1_end", opcode="dispatch")]},
        "right2": {"block_id": "right2", "block_name": "right2", "instructions": [
            instruction("value", outputs=["X"]), instruction("right2_end", opcode="dispatch")]},
        "join": {"block_id": "join", "block_name": "join", "instructions": [
            instruction("write", [operand("X")]), instruction("read", outputs=["B"]),
            instruction("operation", [operand("B")], ["C"]), instruction("return", opcode="return")]},
    }
    cfg = {"entry_block_id": "entry", "blocks": blocks, "edges": [
        {"source_block_id": a, "target_block_id": b} for a, b in [
            ("entry", "left"), ("entry", "right1"), ("right1", "right2"),
            ("left", "join"), ("right2", "join"),
        ]
    ]}
    operation = ({"op": "select_part", "input": input_ref(), "path": ["secret"], "output": "c"}
                 if select_missing else {"op": "compute", "inputs": [input_ref()],
                                         "dependencies": ["possible"], "output": "c"})
    return annotation_for(cfg, {
        "value": ([], [], [literal("new")]),
        "write": (["context_write"], [(0, [{"op": "write", "target": "cache",
            "mode": "replace", "input": input_ref()}])], []),
        "read": (["context_read"], [(0, [{"op": "read", "location": "cache", "output": "b"}])], [local("b")]),
        "operation": (["transform"], [(0, [operation])], [local("c")]),
    }, {"cache": ("runtime_context", "cache")})


def test_pending_write_cannot_emit_schedule_dependent_downstream_data():
    cfg, annotation = late_input_case()
    fifo, lifo = propagate(cfg, annotation, schedule="fifo"), propagate(cfg, annotation, schedule="lifo")
    assert fifo.status == lifo.status == "complete"
    assert fifo.registry.to_dict() == lifo.registry.to_dict()
    assert fifo.records.to_dict() == lifo.records.to_dict()


def test_missing_final_binding_cannot_leave_stale_success_record():
    cfg, annotation = late_input_case(select_missing=True)
    fifo, lifo = propagate(cfg, annotation, schedule="fifo"), propagate(cfg, annotation, schedule="lifo")
    assert fifo.status == lifo.status == "incomplete"
    for result in (fifo, lifo):
        assert result.coverage["ir_operation"] == "unresolved_binding"
        with pytest.raises(KeyError):
            result.records.get("ir_operation")
    assert fifo.registry.to_dict() == lifo.registry.to_dict()


def test_missing_part_diagnostics_keep_precise_positions_outside_compact_record():
    cfg, annotation = linear([instruction("select", outputs=["owner"])], {
        "select": (["transform"], [(0, [{"op": "select_part", "input": {
            "kind": "alternatives", "items": [literal({}), literal({"owner": "present"})]},
            "path": ["owner"], "output": "owner"}])], [local("owner")]),
    })
    result = propagate(cfg, annotation)
    assert result.status == "complete"
    issues = [item for item in result.diagnostics if item["code"] == "missing_part"]
    assert len(issues) == 1
    issue = issues[0]
    assert set(issue) == {"code", "instruction_id", "event_index", "op_index", "data_id", "reason"}
    assert (issue["instruction_id"], issue["event_index"], issue["op_index"]) == ("ir_select", 0, 0)
    assert result.registry.get(issue["data_id"]).content == LiteralContent(value={})
    event = result.records.records_dict()["ir_select"]["events"][0]
    assert set(event) == {"effect", "atomic_ops"}
    assert set(event["atomic_ops"][0]) == {"op", "inputs", "outputs", "endpoints", "changes"}
    assert result.registry.get(at(result, "ir_select", "owner")).content == LiteralContent(value="present")


def test_recomputed_diagnostics_are_replaced_instead_of_added_per_iteration():
    cfg, annotation = read_case([
        instruction("select", [operand("B")], ["owner"]),
        instruction("refine", [operand("B")], ["detail"]),
    ], {
        "select": (["transform"], [(0, [{"op": "select_part", "input": {
            "kind": "alternatives", "items": [literal({}), input_ref()]},
            "path": ["owner"], "output": "owner"}])], [local("owner")]),
        "refine": (["transform"], [(0, [{"op": "select_part", "input": input_ref(),
            "path": ["later"], "output": "detail"}])], [local("detail")]),
    })
    result = propagate(cfg, annotation)
    assert result.status == "complete"
    assert result.stats["block_evaluations"] > 1
    missing = [item for item in result.diagnostics if item["code"] == "missing_part"]
    assert len(missing) == 1
    assert result.records.records_dict()["ir_select"]["events"][0]["atomic_ops"][0]["inputs"]


def test_failed_ordering_does_not_publish_diagnostics_from_discarded_path():
    # select before replace cannot complete; only the replace-before-select
    # ordering contributes records and diagnostics.
    cfg, annotation = linear([instruction("stages", outputs=["owner"])], {
        "stages": (["transform", "transform"], [
            (0, [{"op": "update_fields", "input": literal({}),
                  "updates": [{"path": ["owner"], "value": literal("present")}],
                  "output": "replaced"}]),
            (1, [{"op": "select_part", "input": local("replaced"),
                  "path": ["owner"], "output": "owner"}]),
        ], [local("owner")]),
    }, partial_irs=["ir_stages"])
    result = propagate(cfg, annotation)
    assert result.status == "complete"
    assert not any(item["code"] == "missing_part" for item in result.diagnostics)
    assert result.registry.get(at(result, "ir_stages", "owner")).content == LiteralContent(value="present")


