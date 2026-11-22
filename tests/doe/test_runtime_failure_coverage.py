"""Execution gaps stay unresolved while independent comparisons remain usable."""
from copy import deepcopy

import pytest

from skillflow.doe.demand_material import prepare_demand_review
from skillflow.doe.demand_results import validate_result_references
from skillflow.doe.sensitivity_material import prepare_sensitivity_review, prepare_joint_sensitivity_review
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.demand_index import build_demand_target_index
from skillflow.propagation.interpreter import TransferInterpreter, PropagationLimitError
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate
from tests.doe.components import mutable_components
from tests.doe.test_processing_limits import authored, segment, local, CITATION, model_rows


def broken_branch():
    material, raw = authored(gap=False)
    spec = raw["ir_semantics"]["ir_unknown"]
    spec.pop("empty_effect_evidences", None)
    spec["events"] = [segment("transform", {"op":"filter_items", "input":{"kind":"literal","value":{"bad":1}},
                                            "predicate":"keep", "output":"broken"})]
    spec["output_bindings"] = [{"output_index":0,"value":local("broken"),"evidences":[CITATION]}]
    checked, compiled, mapping = compile_response(raw, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=checked,
                                  compiled_annotation=compiled, mapping=mapping)
    return facts


def demand_for(facts):
    return prepare_joint_sensitivity_review(facts, facts.annotation).demand_dict()


def test_local_execution_fault_does_not_block_independent_doe_comparison():
    facts = broken_branch()
    assert facts.coverage["ir_unknown"] == "execution_error"
    assert facts.coverage["ir_late"] == facts.coverage["ir_filter"] == "processed"
    review = prepare_sensitivity_review(facts, annotation=facts.annotation)
    assert model_rows(review) and {row["conclusion"] for row in model_rows(review)} == {"excess_supported"}
    assert review.to_dict()["status"] == "partial"
    demand = demand_for(facts)
    limitation = next(row for row in demand["diagnostics"] if row["code"] == "upstream_diagnostic"
                      and row.get("instruction_id") == "ir_unknown")
    assert limitation["affected_instruction_ids"] == ["ir_unknown"]
    broken_inputs = [row for row in demand["input_assessments"] if row["instruction_id"] == "ir_unknown"]
    assert broken_inputs and all(row["ranges"] for row in broken_inputs)
    assert all(part["status"] == "unresolved" for row in broken_inputs for part in row["ranges"])
    assert not any(row["code"] == "inactive_goal" and row["instruction_id"] == "ir_unknown"
                   for row in demand["diagnostics"])


def test_demand_cannot_change_recorded_execution_failure_scope():
    facts = broken_branch()
    demand = demand_for(facts)
    targets = build_demand_target_index(facts.cfg, facts.raw_annotation)
    changed = deepcopy(demand)
    diagnostic = next(row for row in changed["diagnostics"] if row["code"] == "upstream_diagnostic"
                      and "affected_instruction_ids" in row)
    diagnostic["affected_instruction_ids"].append("ir_filter")
    with pytest.raises(ValueError, match="Upstream diagnostic scope differs"):
        validate_result_references(changed, facts, targets)


def test_legacy_not_reached_is_not_positive_infeasibility_or_deletion_evidence():
    facts = mutable_components(broken_branch())
    facts.records = {}
    facts.sinks = []
    facts.coverage = {ir:"not_reached" for ir in facts.coverage}
    facts.status = "execution_error"
    facts.diagnostics = [{"code":"execution_error","reason":"Synthetic global stop before worklist completion."}]
    demand = demand_for(facts)
    assert demand["status"] == "partial"
    assert not any(row["code"] == "inactive_goal" for row in demand["diagnostics"])
    assert any(row["code"] == "upstream_coverage" for row in demand["diagnostics"])
    assert demand["input_assessments"]
    assert all(row["ranges"] for row in demand["input_assessments"])
    assert not any(part["status"] == "deletable" for row in demand["input_assessments"] for part in row["ranges"])


def test_real_resource_abort_never_seeds_verified_inactive_goals(monkeypatch):
    material, raw = authored(gap=False)
    checked, compiled, mapping = compile_response(raw, material)
    def exhausted(*args, **kwargs):
        raise PropagationLimitError("Synthetic bounded resource exhaustion before completing the first IR")
    monkeypatch.setattr(TransferInterpreter, "evaluate", exhausted)
    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=checked,
                                  compiled_annotation=compiled, mapping=mapping)
    assert set(facts.coverage.values()) == {"not_solved"}
    demand = demand_for(facts)
    assert demand["status"] == "partial"
    assert not any(row["code"] == "inactive_goal" for row in demand["diagnostics"])
    assert not any(part["status"] == "deletable" for row in demand["input_assessments"] for part in row["ranges"])


def required_action_fixture(*, sibling, ir_target=False, blocked=False, implicit_context=False):
    """Two acquisitions, with only x on the declared required-action path."""
    from skillflow.propagation import FlowLocation, FlowState
    from skillflow.propagation.annotation.binding_examples import (
        _fixture, evidence, example_material, goal, inp, instruction, literal, local,
        result, segment, semantics,
    )
    from skillflow.propagation.data import DataRegistry, LiteralContent

    instructions, specs, locations = [], {}, {}
    for name in ("x", "y"):
        read = f"ir_{name}"
        instructions.append(instruction(read, "read", [{"type": "external_resource", "identifier": name}], name))
        specs[read] = semantics([segment([{"op": "read", "location": name, "output": name}], "fs_read")], name)
        locations[name] = {"kind": "storage", "name": name, "access_scope": "task", "retention": "persistent",
                           "operand_refs": [{"instruction_id": read, "side": "input", "index": 0}]}
    locations["api"] = {"kind": "remote", "name": "api", "operand_refs": [], "access_scope": "recipient", "retention": None}
    locations["mode"] = {"kind": "runtime_context", "name": "mode", "operand_refs": [], "access_scope": "task", "retention": "task"}
    send_input = result("checked_x" if blocked else "x")
    if implicit_context:
        send_input = {"type": "context_key", "identifier": "payload"}
        locations["payload"] = {"kind": "runtime_context", "name": "payload", "operand_refs": [],
                                "access_scope": "task", "retention": "task"}
        instructions.append(instruction("ir_save", "save", [result("x")]))
        specs["ir_save"] = semantics([segment([{"op": "write", "target": "payload", "mode": "replace",
                                                 "input": inp()}], "context_write")])
    action = instruction("ir_send", "acquire_context" if implicit_context else "publish", [send_input],
                         "published" if implicit_context else None)
    done = instruction("ir_done", "return", [])
    delivery = {"op": "deliver", "target": "api", "inputs": [inp() if blocked else local("selected")]}
    if not ir_target:
        delivery["demands"] = [goal({"kind": "self"}, "action")]
    prep = [
        *([segment([{"op": "read", "location": "mode", "output": "mode"}], "context_read")] if sibling else []),
        segment([{"op": "select_part", "input": inp(), "path": ["needed"], "output": "selected"},
                 {"op": "filter_items", "input": local("mode") if sibling else {"kind": "literal", "value": {"bad": 1}},
                  "predicate": "allow", "output": "checked"}]),
    ]
    specs["ir_send"] = semantics([*([] if blocked else prep), segment([delivery], "net_send")],
                                 "selected" if implicit_context else None)
    if blocked:
        instructions.append(instruction("ir_prepare", "required_check", [result("x")], "checked_x"))
        specs["ir_prepare"] = semantics(prep, "selected")
    specs["ir_done"] = semantics()
    for spec in specs.values():
        for event in spec["events"]:
            event["mode"] = "local"
    if sibling or implicit_context:
        instructions.append(instruction("ir_choose", "dispatch", [literal(True)]))
        specs["ir_choose"] = semantics()
    else:
        instructions.extend([action, done])
    example = _fixture("required action unavailable", "A local execution fault is not a completed side effect.",
        "Read independent inputs x and y. Publish x.needed after checking that the current mode allows publication.",
        instructions, specs)
    if implicit_context:
        graph = example["cfg"]
        graph["blocks"]["acquire"] = {"block_id": "acquire", "block_name": "acquire",
            "instructions": [action, done], "constraints": [], "data_source_kind": "context"}
        graph["declared_context_keys"] = ["payload"]
        graph["edges"] = [{"source_block_id": "sample", "target_block_id": "acquire", "condition_text": None}]
    if sibling:
        graph = example["cfg"]
        for name, value in (("bad", {"bad": 1}), ("good", ["good"])):
            write = f"ir_{name}"
            specs[write] = semantics([segment([{"op": "write", "target": "mode", "mode": "replace",
                                               "input": {"kind": "literal", "value": value}}], "context_write")])
            graph["blocks"][name] = {"block_id": name, "block_name": name,
                "instructions": [instruction(write, "write", []), instruction(f"ir_{name}_next", "dispatch", [])],
                "constraints": [], "data_source_kind": None}
            specs[f"ir_{name}_next"] = semantics()
        graph["blocks"]["join"] = {"block_id": "join", "block_name": "join", "instructions": [action, done],
                                   "constraints": [], "data_source_kind": None}
        graph["edges"] = [{"source_block_id": before, "target_block_id": after, "condition_text": None}
                          for before, after in (("sample", "bad"), ("sample", "good"), ("bad", "join"), ("good", "join"))]
    material = example_material(example)
    raw = example["annotation"]
    raw["task_revision_id"] = material["task"]["task_sha256"]
    raw["realizations"] = [{"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": []}]
    raw["locations"] = locations
    raw["location_evidences"] = {key: [evidence()] for key in locations}
    if ir_target:
        raw["demands"] = [goal({"instruction_id": "ir_send", "path": []}, "action")]
    registry = DataRegistry("declare-required-unavailable")
    initial = {}
    for name in ("x", "y"):
        item = registry.register_source(name, acquired_from=name,
                                        content=LiteralContent(value={"needed": name, "extra": "unused"}))
        initial[FlowLocation(kind="storage", name=name)] = frozenset([item.id])
    raw, compiled, mapping = compile_response(raw, material)
    solved = propagate(material["cfg"], to_payload(compiled), initial_registry=registry,
                       initial_state=FlowState.from_mapping(initial))
    return materials_from_result(solved, material=material, raw_annotation=raw, compiled_annotation=compiled, mapping=mapping)


@pytest.mark.parametrize("sibling,ir_target,blocked", [(False, False, False), (False, True, False),
                                                       (True, False, False), (False, False, True)])
def test_required_unavailable_action_protects_x_without_blocking_unused_y(sibling, ir_target, blocked):
    facts = required_action_fixture(sibling=sibling, ir_target=ir_target, blocked=blocked)
    expected_state = "processed" if sibling else "blocked" if blocked else "execution_error"
    assert facts.coverage["ir_send"] == expected_state
    demand = demand_for(facts)
    assert demand == prepare_joint_sensitivity_review(facts, facts.annotation, queue_order="lifo").demand_dict()
    fault = next(row for row in demand["diagnostics"] if row["code"] == "unavailable_required_action")
    assert "ir_send" in fault["reason"] and "/atomic_ops/" in fault["reason"]
    assert not any(row["code"] == "unbound_requirement" for row in demand["diagnostics"])
    assert demand["coverage"]["requirements"]["R1"]["has_applicable_goal"] == sibling
    actual_actions = [row for row in demand["derivations"].values() if row["node"]["kind"] == "action"
                      and row["node"]["operation_id"]]
    assert bool(actual_actions) == sibling
    acquisition = {row["instruction_id"]: row["ranges"] for row in demand["input_assessments"]
                   if row["node_kind"] == "acquisition_output"}
    assert any(row["status"] == "unresolved" and row["path"] == ([] if ir_target else ["needed"])
               and fault["id"] in row["diagnostic_refs"] for row in acquisition["ir_x"])
    assert not any(row["status"] == "deletable" and not row["path"] and not row["excluded_paths"]
                   for row in acquisition["ir_x"])
    assert any(row["status"] == "deletable" and not row["path"] and not row["excluded_paths"]
               for row in acquisition["ir_y"])
    if not ir_target and not sibling:
        assert any(row["status"] == "deletable" and row["excluded_paths"] == [["needed"]]
                   for row in acquisition["ir_x"])


def test_persisted_action_diagnostic_must_match_the_actual_fault():
    facts = required_action_fixture(sibling=True)
    demand = demand_for(facts)
    targets = build_demand_target_index(facts.cfg, facts.raw_annotation)
    validate_result_references(demand, facts, targets)
    changed = deepcopy(demand)
    fault = next(row for row in changed["diagnostics"] if row["code"] == "unavailable_required_action")
    fault["reason"] = "The action was available at another operation."
    with pytest.raises(ValueError, match="required action's unavailable occurrence"):
        validate_result_references(changed, facts, targets)
    changed = deepcopy(demand)
    protected = next(row for assessment in changed["input_assessments"] if assessment["instruction_id"] == "ir_x"
                     for row in assessment["ranges"] if fault["id"] in row["diagnostic_refs"])
    protected["diagnostic_refs"].remove(fault["id"])
    with pytest.raises(ValueError, match="unavailable required action's dependency evidence"):
        validate_result_references(changed, facts, targets)


def test_unavailable_required_action_follows_exact_implicit_context_operand():
    facts = required_action_fixture(sibling=False, implicit_context=True)
    assert facts.coverage["ir_save"] == "processed" and facts.coverage["ir_send"] == "execution_error"
    demand = demand_for(facts)
    assert demand == prepare_joint_sensitivity_review(facts, facts.annotation, queue_order="lifo").demand_dict()
    acquisition = {row["instruction_id"]: row["ranges"] for row in demand["input_assessments"]
                   if row["node_kind"] == "acquisition_output"}
    assert any(row["status"] == "unresolved" and row["path"] == ["needed"] for row in acquisition["ir_x"])
    assert any(row["status"] == "deletable" and not row["path"] and not row["excluded_paths"] for row in acquisition["ir_y"])
