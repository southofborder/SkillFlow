"""One direct CFG address space replaces target tables and evidence aliases."""
from copy import deepcopy
import json

import pytest
from pydantic import TypeAdapter

from skillflow.propagation.contracts.references import (
    CFGTarget, cfg_target_index, resolve_cfg_target, target_key,
)
from skillflow.propagation.contracts.demand import RawDemandSupplement, goal_target_capability
from tests.propagation.annotation.helpers import prepare_material
from skillflow.propagation.material import model_material, evidence_reference
from tests.propagation.annotation.helpers import graph, source_bundle, valid_raw_response
from skillflow.propagation.annotation.services import compile_response


def direct_graph():
    cfg = graph()
    cfg["blocks"]["entry"]["instructions"][0]["metadata"] = {"0": {"a/b~c": ["payload"]}}
    return cfg


@pytest.mark.parametrize("target,kind", [
    ({"path": []}, "graph"),
    ({"path": ["constraints", 0]}, "constraint"),
    ({"block_id": "entry", "path": []}, "block"),
    ({"instruction_id": "ir_read", "path": []}, "instruction"),
    ({"instruction_id": "ir_read", "side": "output", "index": 0}, "output"),
    ({"instruction_id": "ir_return", "side": "input", "index": 0}, "input"),
    ({"instruction_id": "ir_read", "path": ["outputs", 0, "identifier"]}, "operand_field"),
    ({"instruction_id": "ir_read", "path": ["metadata", "0", "a/b~c", 0]}, "metadata_value"),
])
def test_direct_reference_resolves_same_object_for_task_demand_and_evidence(target, kind):
    cfg = direct_graph()
    resolved = resolve_cfg_target(target, cfg)
    assert resolved["kind"] == kind
    assert cfg_target_index(cfg)[target_key(target)] == resolved
    material = prepare_material(source_bundle(), cfg)
    evidence = evidence_reference({"target": target, "reason": "The CFG carries this exact object."}, material)
    assert evidence["value"] == resolved["value"]
    assert evidence["target"] == target
    if kind in {"input", "output"}:
        assert goal_target_capability(resolved, "value")
    elif kind in {"graph", "block", "operand_field", "metadata_value", "constraint"}:
        assert goal_target_capability(resolved, "value") is None


@pytest.mark.parametrize("target", [
    {"path": ["blocks", "entry"]},
    {"path": ["blocks", "entry", "instructions", 0]},
    {"block_id": "entry", "path": ["instructions", 0]},
    {"instruction_id": "ir_read", "path": ["outputs", 0]},
    {"instruction_id": "ir_read", "side": "output", "index": True},
    {"instruction_id": "ir_read", "side": "output", "index": 99},
    {"instruction_id": "ir_read", "path": ["metadata", 0]},
    {"instruction_id": "ir_read", "path": ["outputs", "0"]},
    {"instruction_id": "missing", "path": []},
    {"block_id": "missing", "path": []},
    {"target_id": "g_0001"},
])
def test_noncanonical_invalid_and_legacy_addresses_are_not_aliases(target):
    with pytest.raises(ValueError):
        resolve_cfg_target(target, direct_graph())


def test_target_has_no_stale_instruction_position_after_reordering():
    cfg = direct_graph()
    target = {"instruction_id": "ir_read", "path": ["metadata", "0", "a/b~c", 0]}
    original = resolve_cfg_target(target, cfg)
    cfg["blocks"]["entry"]["instructions"].reverse()
    after = resolve_cfg_target(target, cfg)
    assert original["value"] == after["value"] == "payload"
    assert original["pointer"] != after["pointer"]
    assert after["target"] == target


def test_top_level_model_expression_cannot_predict_raw_operation_coordinate():
    with pytest.raises(ValueError):
        RawDemandSupplement.model_validate({
            "target": {"instruction_id": "ir_read", "operation_path": ["events", 0], "slot": {"kind": "self"}},
            "expression": {"op": "literal", "value": True},
            "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "reason": "A real line."}],
        })


def test_joint_material_has_one_request_and_no_registry_or_representation_material():
    request = "Preserve the original selection.\r\nDo not add recipients."
    material = prepare_material(source_bundle(), graph(), user_request=request)
    sent = model_material(material)
    assert set(material) == {"version", "source", "cfg", "runtime_contract", "user_request", "task"}
    assert sent["user_request"] == request
    assert all(item["file"].startswith("skill/") for item in sent["source"]["files"])
    evidence = evidence_reference({"file": "task/user-request.txt", "start_line": 1, "end_line": 1, "reason": "User purpose."}, material)
    assert evidence["text"] == "Preserve the original selection.\r\n"
    raw, compiled, _ = compile_response(valid_raw_response(material), material)
    assert set(compiled) >= {"task_ref", "realizations", "demands", "expressions"}
    assert set(compiled).isdisjoint({"demand", "task_targets", "semantic_context"})
    assert compiled["task_ref"]["basis"] == "user_request"
    for old in ("task_goals", "task_expressions", "policies", "semantic_context"):
        invalid = deepcopy(raw)
        invalid[old] = []
        with pytest.raises(ValueError):
            compile_response(invalid, material)
