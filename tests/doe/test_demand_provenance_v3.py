"""Seed provenance and explicit expression gaps survive deterministic solving.

These are authored engineering examples, not model semantic-effect experiments.
"""
from copy import deepcopy
import pytest

from skillflow.doe.demand_material import prepare_demand_review
from skillflow.doe.demand_results import validate_result_shape
from skillflow.doe.sensitivity_material import prepare_sensitivity_review
from tests.doe.test_demand_engine import fixture, inp, candidate, solve


def test_same_requirement_same_value_keeps_each_seed_and_queue_order():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    request = candidate(values[3])
    request["goals"].append({**deepcopy(request["goals"][0]), "id": "G2"})
    _, result = solve(values, request)
    rows = result["derivations"]
    assert {row["seed_goal_id"] for row in rows.values()} == {"G", "G2"}
    for row in rows.values():
        assert all(rows[parent]["seed_goal_id"] == row["seed_goal_id"] for parent in row["parents"])
    per_seed = {seed: [row for row in rows.values() if row["seed_goal_id"] == seed] for seed in ("G", "G2")}
    assert len(per_seed["G"]) == len(per_seed["G2"])
    assert result["coverage"]["requirements"]["R"]["goal_ids"] == ["G", "G2"]
    trace = result["traceability"]["requirements"][0]
    assert {seed["goal_id"] for seed in trace["seeds"]} == {"G", "G2"}
    assert all(seed["raw_pointer"] is None for seed in trace["seeds"])  # Explicit offline seeds have no accepted raw coordinate.
    assert validate_result_shape(result) == result


def test_saved_parent_cannot_cross_seed_after_structural_reseal():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}])
    request = candidate(values[3])
    request["goals"].append({**deepcopy(request["goals"][0]), "id": "G2"})
    _, result = solve(values, request)
    rows = result["derivations"]
    first = next(row for row in rows.values() if row["seed_goal_id"] == "G")
    other = next(key for key, row in rows.items() if row["seed_goal_id"] == "G2")
    first["parents"] = [other]
    with pytest.raises(ValueError, match="crosses seed"):
        validate_result_shape(result)


def test_realization_gap_is_global_even_with_a_model_binding():
    from skillflow.propagation.annotation.services import compile_response, to_payload
    from skillflow.propagation.loading import materials_from_result
    from skillflow.propagation.solver import propagate
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    annotation = deepcopy(values[2])
    raw = annotation["raw_annotation"]
    raw["realizations"][0].update(status="partial", bindings=[{
        "target": {"instruction_id": "ir_return", "path": []}, "reason": "模型自行声称局部绑定，不构成范围证明。"}],
        gaps=[{"reason": "次数限制尚未可执行表达。", "evidences": annotation["task"]["requirements"][0]["evidences"]}])
    checked, compiled, mapping = compile_response(raw, annotation["material"])
    facts = materials_from_result(propagate(annotation["material"]["cfg"], to_payload(compiled)),
        material=annotation["material"], raw_annotation=checked, compiled_annotation=compiled, mapping=mapping)
    from skillflow.propagation.contracts.sensitivity import extract_sensitivity_candidate
    request = candidate(values[3])
    result = prepare_demand_review(facts, annotation["task"], facts.annotation, request).to_dict()
    gap = next(row for row in result["diagnostics"] if row["code"] == "requirement_expression_gap")
    assert gap["instruction_id"] is None and gap["blocking"]
    assert all(gap["id"] in sink["limitations"] for sink in result["sinks"])
    assert result["coverage"]["requirements"]["R"]["status"] == "partial"
    assert result["coverage"]["requirements"]["R"]["has_applicable_goal"]
    assert result["status"] == "partial"
    from tests.doe.test_sensitivity_engine import declarations, rows
    sensitivity = prepare_sensitivity_review(facts, annotation["task"], facts.annotation, request, declarations()).to_dict()
    assert rows(sensitivity)
    assert all(row["conclusion"] == "no_excess_established" and row["reduction"] is None
               for row in rows(sensitivity))


def test_raw_pointer_and_task_revision_are_bound_to_frozen_facts():
    from skillflow.doe.demand_results import validate_result_references
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}])
    from skillflow.doe.sensitivity_material import joint_demands
    result = prepare_demand_review(values[0], values[1], values[2], joint_demands(values[2])).to_dict()
    seed = result["traceability"]["requirements"][0]["seeds"][0]
    assert seed["raw_pointer"] == "/demands/0"
    changed = deepcopy(result)
    changed["traceability"]["requirements"][0]["seeds"][0]["raw_pointer"] = "/demands/999"
    with pytest.raises(ValueError, match="raw declaration coordinate"):
        validate_result_references(changed, values[0], values[3])
    changed = deepcopy(result)
    changed["traceability"]["task_ref"]["task_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="Task revision"):
        validate_result_references(changed, values[0], values[3])
