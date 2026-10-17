"""Exact rendered teaching candidate: optional receiver paths and expected limits."""
from copy import deepcopy
import json

import pytest

from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.doe.sensitivity_material import joint_demands
from skillflow.propagation.annotation.binding_examples import example_material
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.prompt_examples import endpoint_example
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.task import Task
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.solver import propagate


def rendered_candidate():
    prompt = build_prompt(example_material(endpoint_example()))
    decoder = json.JSONDecoder()
    context = decoder.raw_decode(prompt.split("\nFORMAT_EXAMPLE_CONTEXT\n", 1)[1])[0]
    candidate = decoder.raw_decode(prompt.split("\nFORMAT_EXAMPLE\n", 1)[1])[0]
    material = prepare_material(context["source"], context["cfg"], task_baseline=context["task"])
    return material, candidate


def solve(condition, *, add_optional_expected=False):
    material, candidate = rendered_candidate()
    shown = deepcopy(candidate)
    delivery = candidate["ir_semantics"]["ir_packet_send"]["events"][0]["events"][1]["atomic_ops"][0]
    offset = next(goal for goal in delivery["demands"] if goal.get("path") == ["offset"])
    assert "expected" not in offset and "expected_path" not in offset
    if add_optional_expected:
        # A named experimental contrast, never an internal repair of the shown positive.
        offset.update(expected={"kind": "input", "index": 0}, expected_path=["offset"])
    raw, compiled, mapping = compile_response(candidate, material)
    registry = DataRegistry("rendered-endpoint-guard-test")
    content = None if condition == "abstract" else LiteralContent(value={
        "badge": "B17", "offset": 12, "adjustment": condition, "internal_note": "synthetic test"})
    packet = registry.register_source("packet", acquired_from="runtime_context:calibration_packet", content=content)
    state = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="calibration_packet"):
                                   frozenset([packet.id])})
    propagated = propagate(material["cfg"], to_payload(compiled), initial_registry=registry, initial_state=state)
    facts = materials_from_result(propagated, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping)
    args = (facts, Task.model_validate(material["task"]), facts.annotation,
            joint_demands(facts.annotation), build_demand_target_index(facts.cfg, raw))
    engine = DemandEngine(*args)
    result = engine.solve()
    assert result == DemandEngine(*args).solve(queue_order="lifo")
    assert propagated.status == result["status"] == "complete"
    assert propagated.diagnostics == result["diagnostics"] == []
    if not add_optional_expected:
        assert candidate == shown
    goal = next(goal for goal in result["goals"] if goal["path"] == ["offset"])
    rows = [row for row in result["derivations"].values() if row["seed_goal_id"] == goal["id"]]
    return engine, facts, rows


@pytest.mark.parametrize("condition", [True, False, "abstract"])
def test_rendered_optional_receiver_field_respects_actual_build_condition(condition):
    engine, facts, rows = solve(condition)
    build = next(op for op in engine.ops.values() if op["spec"]["op"] == "build")
    delivery = next(op for op in engine.ops.values()
                    if op["spec"]["op"] == "deliver" and op["spec"]["target"] == "calibration_interface")
    data = {row["id"]: row for row in facts.data}
    shapes = {tuple(part["path"][0] for part in data[identifier]["content"]["parts"])
              for identifier in delivery["record"]["inputs"][0]}
    assert shapes == ({("badge",), ("badge", "offset")} if condition == "abstract"
                      else {("badge", "offset")} if condition else {("badge",)})
    assert build["record"]["members"][1]["value_input_index"] == (None if condition is False else 2)
    assert any(row["node"]["operation_id"] == build["key"] and row["node"]["kind"] == "op_input"
               and row["node"]["slot"] == 1 and row["property"] == "truth" for row in rows)
    # The nominal boundary path remains even when absent. It is not an assertion
    # of actual containment; the fact above controls whether the member exists.
    assert any(row["node"]["operation_id"] == delivery["key"] and row["property"] == "value"
               and row["path"] == ["offset"] for row in rows)
    for operation in ("op_ir_packet_read:e0:a0", "op_ir_packet_read:e1:a0",
                      "op_ir_packet_send:e0:a0", "op_ir_packet_send:e1:a1"):
        content_demand = any(row["node"]["operation_id"] == operation
                             and row["property"] == "value" and row["path"] == ["offset"] for row in rows)
        assert content_demand is (condition is not False)
    values_at_build = [row for row in rows if row["node"]["operation_id"] == build["key"]
                       and row["node"]["kind"] == "op_input" and row["property"] == "value"]
    assert {row["node"]["slot"] for row in values_at_build} == (set() if condition is False else {2})


def test_explicit_optional_expected_retains_existing_unconditional_source_seed_limitation():
    engine, facts, rows = solve(False, add_optional_expected=True)
    build = next(op for op in engine.ops.values() if op["spec"]["op"] == "build")
    assert build["record"]["members"][1]["value_input_index"] is None
    # This structurally legal declaration is not rejected. Current expected
    # semantics independently demand the original field, even when omitted.
    assert any(row["rules"] == ["required_original_value"] and not row["parents"]
               and row["path"] == ["offset"] for row in rows)
    assert any(row["node"]["operation_id"] == "op_ir_packet_read:e1:a0"
               and row["property"] == "value" and row["path"] == ["offset"] for row in rows)
    assert not any(row["node"]["operation_id"] == "op_ir_packet_send:e0:a0"
                   and row["property"] == "value" and row["path"] == ["offset"] for row in rows)
