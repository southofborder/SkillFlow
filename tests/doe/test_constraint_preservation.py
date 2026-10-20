"""Boundary-local change, request effects and independent forward restrictions."""
from copy import deepcopy
import pytest

from skillflow.doe.constraint_preservation import ForwardInfluence
from tests.doe.test_demand_engine import fixture, solve, inp, local, literal


def with_constraints(values, constraints):
    """Author a new checked fixture; never reinterpret an accepted response."""
    from skillflow.propagation.annotation.compiler import compile_response
    from skillflow.propagation.annotation.services import to_payload
    from skillflow.propagation.loading import materials_from_result
    from skillflow.propagation.solver import propagate
    material, raw, previous = values
    raw = deepcopy(raw)
    raw["realizations"][0].update(status="expressed", gaps=[], constraints=constraints)
    checked, compiled, mapping = compile_response(raw, material)
    from skillflow.propagation.data import DataRegistry
    solved = propagate(material["cfg"], to_payload(compiled),
                       initial_registry=DataRegistry(previous.registry.namespace))
    assert solved.status == "complete"
    facts = materials_from_result(solved, material=material, raw_annotation=checked,
        compiled_annotation=compiled, mapping=mapping)
    return material, checked, facts


def raw_operation(index):
    return {"instruction_id": "ir_format", "operation_path":
            ["events", index, "events", 0, "atomic_ops", 0], "slot": {"kind": "self"}}


def observation(engine):
    return next(key for key, info in engine.ops.items()
                if info["generated"] and info["position"]["instruction_id"] == "ir_filter")


def test_model_observation_change_reaches_processing_but_disjoint_selection_stops_it():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "selected"}], mode="model")
    engine, demand = solve(values)
    before = deepcopy((values[0], demand, engine.derivations))
    graph = ForwardInfluence(engine)
    changed = graph.run(observation(engine), 0, ["token"])
    assert changed["complete"]
    selected = next(key for key, info in engine.ops.items() if info["spec"]["op"] == "select_part")
    assert selected in changed["affected"]
    assert not any(engine.nodes[row["node"]]["kind"] == "op_output" for row in changed["steps"].values())
    assert (values[0], demand, engine.derivations) == before


def test_required_value_change_follows_public_result_and_return_without_events():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "selected"}], mode="model")
    engine, _ = solve(values)
    changed = ForwardInfluence(engine).run(observation(engine), 0, ["body"])
    assert "ir_return" in changed["instructions"]
    assert any(engine.nodes[row["node"]]["kind"] == "ir_output" for row in changed["steps"].values())


@pytest.mark.parametrize("field,reaches", [("body", True), ("token", False)])
def test_member_range_change_reaches_matching_fixed_index_only(field, reaches):
    values = fixture([{"op": "select_part", "input": inp(), "path": [0, "body"], "output": "selected"}], mode="model")
    engine, _ = solve(values)
    changed = ForwardInfluence(engine).run(observation(engine), 0, [{"kind": "each"}, field])
    assert any(engine.nodes[row["node"]]["kind"] == "op_output" for row in changed["steps"].values()) is reaches


@pytest.mark.parametrize("operation", [
    {"op": "exclude_parts", "input": inp(), "paths": [[0, "token"]], "output": "clean"},
    {"op": "update_fields", "input": inp(), "updates": [{"path": [0, "token"], "value": literal("public")}], "output": "clean"},
])
def test_one_member_cut_cannot_erase_change_to_all_members(operation):
    values = fixture([operation], mode="model")
    engine, _ = solve(values)
    changed = ForwardInfluence(engine).run(observation(engine), 0, [{"kind": "each"}, "token"])
    assert any(engine.nodes[row["node"]]["kind"] == "op_output" for row in changed["steps"].values())


@pytest.mark.parametrize("operation", [
    {"op": "exclude_parts", "input": inp(), "paths": [["token"]], "output": "clean"},
    {"op": "update_fields", "input": inp(), "updates": [{"path": ["token"], "value": literal("public")}], "output": "clean"},
])
def test_independent_exclusion_or_overwrite_stops_old_field_change(operation):
    values = fixture([operation], mode="model")
    engine, _ = solve(values)
    changed = ForwardInfluence(engine).run(observation(engine), 0, ["token"])
    assert not any(engine.nodes[row["node"]]["kind"] == "op_output" for row in changed["steps"].values())


def test_influence_queue_order_and_same_receiver_scope_are_deterministic():
    values = fixture([
        {"op": "select_part", "input": inp(), "path": ["body"], "output": "selected"},
        {"op": "build", "container": "object", "parts": [
            {"path": ["left"], "value": local("selected")},
            {"path": ["right"], "value": local("selected")}], "output": "pair"},
    ], mode="model")
    engine, _ = solve(values)
    graph = ForwardInfluence(engine)
    assert graph.run(observation(engine), 0, ["body"]) == graph.run(observation(engine), 0, ["body"], queue_order="lifo")


def test_possible_computation_keeps_behavioral_influence_without_plaintext_claim():
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "classified"}], mode="model")
    engine, _ = solve(values)
    changed = ForwardInfluence(engine).run(observation(engine), 0, ["token"])
    assert "ir_return" in changed["instructions"]
    assert any(row["rule"] == "conservative_processing_change" for row in changed["steps"].values())
    assert all("sensitive" not in row and "seed_goal_id" not in row for row in changed["steps"].values())


def test_request_change_reaches_paired_response_and_its_processing():
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    operations = [
        {"op": "build", "container": "object", "parts": [{"path": ["packet"], "value": inp()}], "output": "formatted"},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
        {"op": "receive", "location": "label_receiver", "inputs": [local("formatted")], "output": "receipt"},
        {"op": "compute", "inputs": [local("receipt")], "dependencies": ["possible"], "output": "answer"},
    ]
    engine, _ = solve_fixture(synthetic_fixture(operations, output="answer", return_demand=True))
    delivery = next(key for key, op in engine.ops.items() if op["spec"]["op"] == "deliver")
    changed = ForwardInfluence(engine).run(delivery, 0, ["packet", "service_note"])
    assert changed["complete"]
    assert "ir_finish" in changed["instructions"]
    assert any(row["rule"] == "request_response_change" for row in changed["steps"].values())
    assert any(row["rule"] == "conservative_processing_change" for row in changed["steps"].values())


@pytest.mark.parametrize("partial,weak,reaches", [(False, False, False), (True, False, True), (False, True, True)])
def test_reaching_storage_change_respects_overwrite_weak_alias_and_partial_order(partial, weak, reaches):
    from tests.doe.test_demand_order import memory_case
    engine, _ = solve(memory_case(partial=partial, weak=weak))
    first = next(key for key, info in engine.ops.items()
                 if info["spec"]["op"] == "write" and info["spec"].get("input") == inp())
    read = next(key for key, info in engine.ops.items() if info["spec"]["op"] == "read" and info["spec"]["location"] == "cache")
    changed = ForwardInfluence(engine).run(first, 0, ["body"])
    assert (read in changed["affected"]) is reaches


def test_same_data_other_receiver_is_not_changed_and_original_violation_remains():
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture, declared_goal
    from skillflow.doe.constraint_preservation import ConstraintAnalysis
    public = {"kind": "tool", "name": "viewer", "operand_refs": [], "access_scope": "recipient", "retention": None}
    operations = [
        {"op": "build", "container": "object", "parts": [{"path": ["packet"], "value": inp()}], "output": "formatted"},
        {"op": "deliver", "target": "viewer", "inputs": [local("formatted")], "demands": [declared_goal("self", preserve="action")]},
        {"op": "receive", "location": "viewer", "inputs": [local("formatted")], "output": "receipt"},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
    ]
    case = with_constraints(synthetic_fixture(operations, extra_locations={"viewer": public}), [{
        "kind": "forbid_information", "scope": {"kind": "task"},
        "source": {"instruction_id": "ir_format", "scope_path": [], "value": inp()},
        "path": ["service_note"], "receivers": {"kind": "locations", "ids": ["label_receiver"]},
    }])
    engine, demand = solve_fixture(case)
    original = deepcopy((case[2].data, case[2].records, case[2].sinks, demand))
    deliveries = {info["spec"]["target"]: key for key, info in engine.ops.items() if info["spec"]["op"] == "deliver"}
    left, right = deliveries["viewer"], deliveries["label_receiver"]
    assert engine.ops[left]["record"]["inputs"] == engine.ops[right]["record"]["inputs"]
    changed = ForwardInfluence(engine).run(left, 0, ["packet", "service_note"])
    assert left in changed["affected"] and right not in changed["affected"]
    analysis = ConstraintAnalysis(engine)
    assert {check["status"] for check in analysis.checks.values()} == {"potential_violation"}, analysis.checks
    refs, preserved = analysis.evaluate(left, 0, engine.ops[left]["record"]["inputs"][0][0], ["packet", "service_note"])
    assert preserved and refs
    assert {check["status"] for check in analysis.checks.values()} == {"potential_violation"}
    assert (case[2].data, case[2].records, case[2].sinks, demand) == original


def test_structural_count_proof_does_not_seed_control_or_payload_demands():
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from skillflow.doe.constraint_preservation import ConstraintAnalysis
    operations = [
        {"op": "build", "container": "object", "parts": [{"path": ["packet"], "value": inp()}], "output": "formatted"},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
    ]
    case = with_constraints(synthetic_fixture(operations), [{"kind": "at_most", "scope": {"kind": "task"},
        "events": [raw_operation(1)], "limit": 1, "unit": "attempt"}])
    engine, demand = solve_fixture(case)
    assert not demand["derivations"]
    assert not any(row["code"] == "unbound_requirement" for row in demand["diagnostics"])
    analysis = ConstraintAnalysis(engine)
    assert all(row["structural"] for row in analysis.checks.values())
    delivery = next(key for key, op in engine.ops.items() if op["spec"]["op"] == "deliver")
    refs, preserved = analysis.evaluate(delivery, 0, engine.ops[delivery]["record"]["inputs"][0][0], ["packet", "service_note"])
    assert preserved and all(analysis.preservation[ref]["rule"] == "structural" for ref in refs)
    assert not demand["derivations"]


def test_normative_ban_and_zero_bound_do_not_prune_actual_delivery_or_payload():
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from skillflow.doe.constraint_preservation import ConstraintAnalysis
    base = synthetic_fixture([
        {"op": "build", "container": "object", "parts": [{"path": ["packet"], "value": inp()}], "output": "formatted"},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
    ])
    constrained = with_constraints(base, [
        {"kind": "forbid_information", "scope": {"kind": "task"},
         "source": {"instruction_id": "ir_format", "scope_path": [], "value": inp()},
         "path": ["service_note"], "receivers": {"kind": "all"}},
        {"kind": "at_most", "scope": {"kind": "task"}, "events": [raw_operation(1)], "limit": 0, "unit": "attempt"},
    ])
    def normalized(facts):
        # New accepted specifications intentionally have new Data identities.
        # Compare the bijection induced by the same recorded input/output slots.
        names = {}
        def replace(value):
            if isinstance(value, str) and value.startswith("data_"):
                return names.setdefault(value, "data_" + str(len(names)))
            if isinstance(value, list):
                return [replace(item) for item in value]
            if isinstance(value, dict):
                return {key: replace(value[key]) for key in sorted(value)}
            return value
        records = replace(facts.records)
        data = sorted((replace(row) for row in facts.data), key=lambda row: row["id"])
        return data, records, replace(facts.sinks)
    assert normalized(base[2]) == normalized(constrained[2])
    engine, demand = solve_fixture(constrained)
    analysis = ConstraintAnalysis(engine)
    assert {row["status"] for row in analysis.checks.values()} == {"potential_violation"}
    assert not demand["goals"] and not demand["derivations"]


@pytest.mark.parametrize("tamper", ["check", "preservation", "reference", "extra_influence"])
def test_constraint_result_is_recomputed_by_the_same_validation_gate(tamper):
    from tests.doe.test_sensitivity_engine import review, validate, rows
    def attach(prepared, raw, evidence):
        raw["realizations"][0]["constraints"] = [{
            "kind": "at_most", "scope": {"kind": "task"},
            "events": [{"instruction_id": "ir_filter", "path": []}],
            "limit": 1, "unit": "attempt"}]
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "chosen"}],
                     mode="model", custom=attach)
    result = review(values)
    assert validate(result, values) == result
    assert any(row["conclusion"] == "excess_supported" for row in rows(result))
    assert result["constraints"]["preservation"]
    altered = deepcopy(result)
    if tamper == "check":
        next(iter(altered["constraints"]["checks"].values()))["status"] = "potential_violation"
    elif tamper == "preservation":
        next(iter(altered["constraints"]["preservation"].values()))["reason"] = "Invented justification."
    elif tamper == "reference":
        next(row for sink in altered["sinks"] for row in sink["data_reviews"] if row["constraint_refs"])["constraint_refs"] = []
    else:
        altered["constraints"]["influence"]["invented"] = {"node": {
            "kind": "ir_input", "instruction_id": "ir_filter", "operation_id": None,
            "slot": 0, "data_ids": []}, "path": [], "rule": "fake", "parents": []}
    with pytest.raises(ValueError, match="[Cc]onstraint"):
        validate(altered, values)


def test_constraint_report_links_checks_and_preservation_without_task_proof_claim():
    from tests.doe.test_sensitivity_engine import declarations
    from tests.doe.test_demand_engine import candidate
    from skillflow.doe.sensitivity_material import prepare_sensitivity_review
    from skillflow.doe.sensitivity_report import render_html, render_markdown
    def attach(prepared, raw, evidence):
        raw["realizations"][0]["constraints"] = [{
            "kind": "at_most", "scope": {"kind": "task"},
            "events": [{"instruction_id": "ir_filter", "path": []}], "limit": 1, "unit": "attempt"}]
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "chosen"}],
                     mode="model", custom=attach)
    reviewed = prepare_sensitivity_review(values[0], values[1], values[2], candidate(values[3]), declarations())
    html, markdown = render_html(reviewed), render_markdown(reviewed)
    assert "Forward constraint checks" in html and "Forward constraint checks" in markdown
    assert "structural" in html and "at_most" in markdown
    import re
    anchors = set(re.findall(r'id="([^"]+)"', html))
    assert set(re.findall(r'href="#([^"]+)"', html)) <= anchors
