"""Saved demand contracts reject contradictory or unauditable records."""
from copy import deepcopy

import pytest

from skillflow.doe.demand_results import validate_result_shape


def test_information_bound_preserves_named_conservative_scope_without_changing_legacy_default():
    from skillflow.doe.demand_results import Derivation
    from skillflow.doe.sensitivity_results import SharedDerivations
    original = result()["derivations"]["d1"]
    assert "information_bound" not in Derivation.model_validate(original).model_dump(mode="json")
    bounded = {**original, "conservative": True, "information_bound": True}
    assert Derivation.model_validate(bounded).model_dump(mode="json") == bounded
    shared = {"sensitivity": {}, "demand": {"d1": bounded}}
    assert SharedDerivations.model_validate(shared).model_dump(mode="json") == shared
    with pytest.raises(ValueError, match="remain conservative"):
        Derivation.model_validate({**bounded, "conservative": False})


def test_bounded_information_requires_scoped_review_origin_and_exact_ancestry():
    from skillflow.doe.demand_results import _validate_information_bounds
    origin = {**result()["derivations"]["d1"], "conservative": True, "information_bound": True,
              "rules": ["input_contract_gap:gap"], "parents": []}
    child = {**deepcopy(origin), "rules": ["actual_operand"], "parents": ["origin"]}
    records = {"origin": origin, "child": child}
    diagnostics = {"gap": {"code": "input_contract_semantic_gap", "operation_id": "op_send", "instruction_id": "send",
                           "requirement_id": "R1", "affected_instruction_ids": ["send"]}}
    _validate_information_bounds(records, diagnostics, "bound-receipt")
    merged = {**deepcopy(records), "deterministic": result()["derivations"]["d1"]}
    merged["child"]["parents"].append("deterministic")
    _validate_information_bounds(merged, diagnostics, "bound-receipt")
    with pytest.raises(ValueError, match="review receipt"):
        _validate_information_bounds(records, diagnostics, None)
    for code in ("input_contract_unavailable", "input_contract_review_gap", "unmodeled_processing"):
        with pytest.raises(ValueError, match="generic or unmodeled"):
            _validate_information_bounds(records, {"gap": {**diagnostics["gap"], "code": code}}, "bound-receipt")
    changed = deepcopy(records); changed["child"]["rules"] = ["conservative_processing"]
    with pytest.raises(ValueError, match="generic or unmodeled"):
        _validate_information_bounds(changed, diagnostics, "bound-receipt")
    changed = {"a": {**child, "parents": ["b"]}, "b": {**child, "parents": ["a"]}}
    with pytest.raises(ValueError, match="lacks ancestry"):
        _validate_information_bounds(changed, {}, "bound-receipt")


def result():
    return {
        "schema_version": "skillflow-demand-v13", "status": "complete",
        "input_assessments": [], "input_findings": [],
        "input_contract_review_sha256": None,
        "goals": [{"id": "G1", "requirement_id": "R1", "target": {"instruction_id": "send", "side": "input", "index": 0},
                   "preserve": "value", "path": [], "expected": None, "expected_path": [],
                   "reason": "Preserve the specified original payload."}],
        "traceability": {"task_ref": {
            "schema_version": "skillflow-task-reference-v3", "task_schema_version": "skillflow-task-v5",
            "task_sha256": "1" * 64, "source_sha256": "2" * 64},
            "requirements": [{"requirement_id": "R1",
                "seeds": [{"goal_id": "G1", "raw_pointer": "/demands/0", "derivation_ids": ["d1"]}]}]},
        "derivations": {"d1": {
            "node": {"kind": "op_input", "instruction_id": "send", "operation_id": "op_send",
                     "slot": 0, "data_ids": ["D_body"]},
            "property": "value", "path": [], "each": False, "excluded_paths": [],
            "requirement_id": "R1", "seed_goal_id": "G1", "conservative": False, "rules": ["task_value"], "parents": []}},
        "sinks": [{"id": "sink_1", "boundary": {
            "instruction_id": "send", "event_index": 0, "op_index": 0,
            "body_event_index": None, "scope": None, "target": "receiver",
            "sink_type": "external_tool", "exposure_level": 2},
            "actual_payload": [{"operation_id": "op_send", "position": {
                "instruction_id": "send", "event_index": 0, "op_index": 0,
                "body_event_index": None, "instance_index": None}, "inputs": [["D_body"], ["D_body"]]}],
            "related_requirements": ["R1"], "demanded_information": ["d1"],
            "conservative_retention": [], "unestablished_ranges": [], "limitations": []}],
        "diagnostics": [],
        "coverage": {"requirements": {"R1": {
            "requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": [],
            "goal_ids": ["G1"], "constraint_ids": [], "has_applicable_goal": True}}, "sinks": 1, "expected_sinks": 1,
                     "upstream": {"send": "processed"}},
    }


def test_strict_saved_result_preserves_repeated_parameter_positions_and_isolates():
    raw = result()
    checked = validate_result_shape(raw)
    assert checked == raw
    assert checked["sinks"][0]["actual_payload"][0]["inputs"] == [["D_body"], ["D_body"]]
    checked["derivations"]["d1"]["path"].append("changed")
    assert raw["derivations"]["d1"]["path"] == []


def test_archived_demand_v12_is_read_only_and_never_accepts_selector_proof_fields():
    archived = {**result(), "schema_version": "skillflow-demand-v12"}
    assert validate_result_shape(archived, archived_v12=True) == archived
    with pytest.raises(ValueError, match="v13"):
        validate_result_shape(archived)
    with pytest.raises(ValueError, match="v12"):
        validate_result_shape(result(), archived_v12=True)
    archived["derivations"]["d1"]["selector_ref"] = None
    with pytest.raises(ValueError, match="selector_ref"):
        validate_result_shape(archived, archived_v12=True)


@pytest.mark.parametrize("mutation", [
    lambda x: x.update(necessary=True),
    lambda x: x.update(schema_version="skillflow-demand-v2"),
    lambda x: x["derivations"]["d1"].update(seed_goal_id="missing"),
    lambda x: x["traceability"]["requirements"][0]["seeds"][0].update(derivation_ids=[]),
    lambda x: x["coverage"]["requirements"]["R1"].update(goal_ids=[]),
    lambda x: x["derivations"]["d1"]["node"].update(slot=True),
    lambda x: x["derivations"]["d1"].update(parents=["absent"]),
    lambda x: x["derivations"]["d1"].update(requirement_id="missing"),
    lambda x: x["derivations"]["d1"].update(conservative=True),
    lambda x: x["derivations"]["d1"]["node"].update(operation_id="other_use"),
    lambda x: x["sinks"][0]["boundary"].update(event_index=1),
    lambda x: x["sinks"][0]["actual_payload"][0]["inputs"].append(["D_body", "D_body"]),
    lambda x: x["sinks"][0].update(related_requirements=[]),
    lambda x: x["sinks"][0].update(limitations=["missing"]),
    lambda x: x["coverage"].update(expected_sinks=2),
    lambda x: x.update(status="partial"),
    lambda x: x["goals"].append(deepcopy(x["goals"][0])),
])
def test_invalid_saved_result_is_not_an_ordinary_complete_analysis(mutation):
    raw = result()
    mutation(raw)
    with pytest.raises(ValueError):
        validate_result_shape(raw)
