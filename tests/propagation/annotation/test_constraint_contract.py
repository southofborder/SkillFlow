"""Constraint references are executable correspondence, never positive seeds."""
from copy import deepcopy

import pytest
from pydantic import TypeAdapter

from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.contracts.constraints import TaskConstraint, validate_constraints
from skillflow.propagation.contracts.demand_index import build_demand_target_index
from skillflow.propagation.contracts.realizations import TaskRealization
from tests.propagation.annotation.helpers import material, valid_raw_response


def event(ir="ir_return"):
    return {"instruction_id": ir, "path": []}


def operation(ir="ir_filter", slot=None):
    return {"instruction_id": ir,
            "operation_path": ["events", 0, "events", 0, "atomic_ops", 0],
            "slot": slot or {"kind": "self"}}


def prohibition():
    return {"kind": "forbid_information", "scope": {"kind": "task"},
            "source": {"instruction_id": "ir_read", "scope_path": [],
                       "value": {"kind": "local", "name": "stage_0"}},
            "path": ["internal_token"], "receivers": {"kind": "all"}}


def constrained(constraint=None):
    prepared = material()
    raw = valid_raw_response(prepared)
    raw["realizations"][0].update(status="expressed", gaps=[], constraints=[constraint or prohibition()])
    return prepared, raw


def boolean_expression(raw, expression=None):
    op = raw["ir_semantics"]["ir_filter"]["events"][0]["events"][0]["atomic_ops"][0]
    op["expression"] = {
        "expression": expression or {"op": "ref", "value": {"kind": "input", "index": 0}},
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                       "reason": "The fixture declares this Boolean condition."}],
    }


def test_pure_prohibition_compiles_without_positive_seed_and_roundtrips():
    prepared, raw = constrained()
    original = deepcopy(raw)
    checked, compiled, mapping = compile_response(raw, prepared)
    assert raw == original
    assert compiled["demands"] == [] and mapping["goals"] == []
    assert len(mapping["constraints"]) == 1
    identity = mapping["constraints"][0]
    assert set(identity) == {"constraint_id", "requirement_id", "raw_pointer"}
    assert identity["constraint_id"].startswith("constraint_")
    assert identity["raw_pointer"] == "/realizations/0/constraints/0"
    assert identity["requirement_id"] == "R001"
    assert checked["realizations"] == compiled["realizations"]
    assert compile_response(checked, prepared) == (checked, compiled, mapping)


def test_empty_constraint_list_is_omitted_without_rewriting_historical_shape():
    prepared = material()
    raw = valid_raw_response(prepared)
    before = deepcopy(raw)
    checked, _, mapping = compile_response(raw, prepared)
    assert checked == before and mapping["constraints"] == []
    raw["realizations"][0]["constraints"] = []
    assert compile_response(raw, prepared)[0] == before


def test_receiver_kind_selects_generated_observations_without_predicting_a_location_id():
    prepared, raw = constrained()
    raw["realizations"][0]["constraints"][0]["receivers"] = {"kind": "kind", "value": "model_context"}
    raw["ir_semantics"]["ir_read"]["events"][0]["mode"] = "default"
    _, compiled, _ = compile_response(raw, prepared)
    assert any(row["sink_type"] == "model_observe" for row in compiled["sink_boundaries"])
    raw["realizations"][0]["constraints"][0]["receivers"] = {
        "kind": "locations", "ids": ["__compiled_model_context__"]}
    with pytest.raises(ValueError, match="absent declared location"):
        compile_response(raw, prepared)


@pytest.mark.parametrize("receivers", [
    {"kind": "kind", "value": "network"}, {"kind": "locations", "ids": []},
    {"kind": "locations", "ids": ["same", "same"]}, {"kind": "all", "ids": ["extra"]},
])
def test_receiver_selector_has_only_the_existing_boundary_kinds(receivers):
    with pytest.raises(ValueError):
        TypeAdapter(TaskConstraint).validate_python({**prohibition(), "receivers": receivers})


@pytest.mark.parametrize("constraint", [
    {"kind": "only_if", "scope": {"kind": "task"}, "events": [event()], "condition": operation()},
    {"kind": "at_most", "scope": {"kind": "task"}, "events": [event("ir_read")], "limit": 2, "unit": "attempt"},
    {"kind": "at_most", "scope": {"kind": "task"}, "events": [event("ir_read")], "limit": 0, "unit": "success", "success": operation()},
    {"kind": "requires_prior", "scope": {"kind": "task"}, "before": [event("ir_read")], "after": [event()], "matching": "scope"},
    {"kind": "forbid_after", "scope": {"kind": "task"}, "triggers": [event("ir_read")], "events": [event()]},
])
def test_each_supported_variant_reuses_existing_raw_references(constraint):
    prepared, raw = constrained(constraint)
    boolean_expression(raw)
    raw["ir_semantics"]["ir_filter"]["events"][0]["mode"] = "default"
    checked, compiled, _ = compile_response(raw, prepared)
    # Compilation inserts an observation before compute; references stay raw.
    assert compiled["ir_semantics"]["ir_filter"]["events"][0]["effect"] == "model_observe"
    assert checked["realizations"] == compiled["realizations"]
    assert compiled["demands"] == []


@pytest.mark.parametrize("change", [
    {"proof": "safe"}, {"id": "model_constraint"}, {"safe_to_remove": True},
    {"requirement_id": "R001"}, {"label": "secret"},
])
def test_model_cannot_supply_verdicts_ids_or_duplicate_requirement_identity(change):
    with pytest.raises(ValueError):
        TypeAdapter(TaskConstraint).validate_python({**prohibition(), **change})


@pytest.mark.parametrize("change", [
    {"limit": True}, {"limit": -1}, {"limit": 1.0}, {"unit": "count"},
    {"unit": "success"}, {"success": operation()},
    {"events": []}, {"events": [event(), event()]},
    {"events": [{"instruction_id": "ir_return", "path": ["inputs"]}]},
    {"events": [operation(slot={"kind": "input", "index": 0})]},
    {"events": [event("ir_filter"), operation()]},
])
def test_count_unit_event_and_bound_types_are_strict(change):
    candidate = {"kind": "at_most", "scope": {"kind": "task"},
                 "events": [event()], "limit": 1, "unit": "attempt", **change}
    with pytest.raises(ValueError):
        TypeAdapter(TaskConstraint).validate_python(candidate)


@pytest.mark.parametrize("mutation", ["missing_ir", "missing_local", "resource", "bad_scope", "receiver", "duplicate", "retained"])
def test_invalid_source_scope_receiver_and_status_fail_before_compilation(mutation):
    prepared, raw = constrained()
    row = raw["realizations"][0]
    value = row["constraints"][0]
    if mutation == "missing_ir":
        value["source"]["instruction_id"] = "absent"
    elif mutation == "missing_local":
        value["source"]["value"]["name"] = "undefined"
    elif mutation == "resource":
        value["source"]["value"] = {"kind": "input", "index": 0}
    elif mutation == "bad_scope":
        value["source"]["scope_path"] = ["events", 0]  # a processing segment, not for_each
    elif mutation == "receiver":
        value["receivers"] = {"kind": "locations", "ids": ["unknown"]}
    elif mutation == "duplicate":
        row["constraints"].append(deepcopy(value))
    else:
        row.update(status="retained_only", gaps=[{"reason": "A remaining unsupported requirement.",
            "evidences": prepared["task"]["requirements"][0]["evidences"]}])
    with pytest.raises(ValueError):
        compile_response(raw, prepared)


@pytest.mark.parametrize("mutation", ["missing_expression", "non_boolean", "missing_event", "processing_event"])
def test_conditions_require_real_boolean_expression_and_actual_event_target(mutation):
    constraint = {"kind": "only_if", "scope": {"kind": "task"},
                  "events": [event()], "condition": operation()}
    prepared, raw = constrained(constraint)
    if mutation != "missing_expression":
        boolean_expression(raw, {"op": "literal", "value": 3} if mutation == "non_boolean" else None)
    if mutation == "missing_event":
        constraint = raw["realizations"][0]["constraints"][0]
        constraint["events"] = [event("missing")]
    elif mutation == "processing_event":
        raw["realizations"][0]["constraints"][0]["events"] = [
            {"instruction_id": "ir_filter", "operation_path": ["events", 0], "slot": {"kind": "self"}}]
    with pytest.raises(ValueError):
        compile_response(raw, prepared)


def test_existing_element_scope_is_exact_and_its_local_cannot_escape():
    from tests.doe.test_demand_contract import inputs
    cfg, raw = inputs()
    targets = build_demand_target_index(cfg, raw)
    target = next(item for item in targets.values()
                  if item["kind"] == "operation" and item.get("scope_path") == ["events", 0]
                  and item["instruction_id"] == "ir_005")
    constraint = {"kind": "forbid_information",
        "scope": {"kind": "element", "instruction_id": "ir_005", "scope_path": ["events", 0]},
        "source": {"instruction_id": "ir_005", "scope_path": ["events", 0],
                   "value": {"kind": "local", "name": "event_record"}},
        "path": ["access_token"], "receivers": {"kind": "all"}, "events": [target["target"]]}
    row = {"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": [], "constraints": [constraint]}
    def check():
        return validate_constraints([TaskRealization.model_validate(row)], cfg=cfg, raw=raw,
            targets=targets, expressions=[], locations=raw["locations"])
    assert check() == {"R1"}
    constraint["source"]["scope_path"] = []
    with pytest.raises(ValueError, match="lexical scope"):
        check()
    constraint["source"]["scope_path"] = ["events", 0]
    constraint["events"] = [event("ir_001")]
    with pytest.raises(ValueError, match="element scope"):
        check()
