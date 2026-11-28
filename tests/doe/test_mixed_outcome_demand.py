"""A protected result can reach a consumer as both exact and re-routed Data."""

from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.propagation.annotation.binding_examples import (
    _fixture, evidence, example_material, inp, instruction, result,
)
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate


def routed_call():
    source = ("Read a possible object and continue only for objects. The protected call returns either "
              "that object or a fixed ready result. If the returned status is ready, preserve its detail.")
    initial = [instruction("ir_source", "acquire", [], "source"),
               instruction("ir_object", "dispatch", [result("source")])]
    fixture = _fixture("routed_protected_call", source, source, initial, {})
    call = instruction("ir_call", "parse", [result("source")])
    call["outputs"] = [result("returned"), result("completed")]
    for key, instructions in [
        ("call", [call, instruction("ir_ready", "dispatch", [result("returned")])]),
        ("use", [instruction("ir_use", "return", [result("returned")])]),
        ("done", [instruction("ir_done", "return", [])]),
    ]:
        fixture["cfg"]["blocks"][key] = {"block_id": key, "block_name": key, "instructions": instructions}
    fixture["cfg"]["edges"] = [{"source_block_id": start, "target_block_id": end, "condition_text": reason}
        for start, end, reason in [("sample", "call", "source is object"), ("sample", "done", "not an object"),
            ("call", "use", "status is ready"), ("call", "done", "status is not ready")]]
    material = example_material(fixture)
    ev = [evidence()]

    def operations(ops):
        return {"evidences": ev, "segments": [{"mode": "local", "returns": [], "ops": ops}]}

    def branch(path, test, yes, no):
        return operations([{"op": "branch", "predicate": "selector", "input": inp(),
            "selector": {"path": path, "tests": [test], "outcome": 0},
            "true_target": yes, "false_target": no}])

    acquire = operations([{"op": "read", "location": "input", "output": "source"}])
    acquire["output_bindings"] = [{"output_index": 0, "value": {"kind": "local", "name": "source"}}]
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}],
            "locations": {"input": {"kind": "runtime_context", "name": "source", "evidences": ev}},
            "ir_semantics": {
                "ir_source": acquire,
                "ir_object": branch([], {"kind": "object"}, "call", "done"),
                "ir_call": {"evidences": ev, "segments": [{"kind": "cases", "outcome": {
                    "completion_index": 1, "return_index": 0}, "cases": [
                    {"name": "input", "phase": "normal", "disposition": "return", "condition": "echo branch",
                     "segments": [], "yield": inp()},
                    {"name": "fixed", "phase": "normal", "disposition": "return", "condition": "fixed branch",
                     "segments": [], "yield": {"kind": "literal", "value": {"status": "ready", "detail": "fixed"}}},
                ]}]},
                "ir_ready": branch(["status"], {"kind": "equals", "value": "ready"}, "use", "done"),
                "ir_use": {"evidences": ev}, "ir_done": {"evidences": ev},
            },
            "demands": [{"requirement_id": "R1", "target": {"instruction_id": "ir_use", "side": "input", "index": 0},
                         "preserve": "value", "path": ["detail"], "reason": source}]}
    return material, wire


def test_recorded_typed_routes_match_public_versions_through_sensitivity_entry():
    material, wire = routed_call()
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)
    result = prepare_joint_sensitivity_review(facts, facts.annotation).demand_dict()
    bound = [row for row in result["derivations"].values() if row["node"]["kind"] == "ir_output"
             and row["node"]["instruction_id"] == "ir_call" and row["path"] == ["detail"]]
    exact, = [row for row in bound if not row["conservative"]]
    assert len(exact["node"]["data_ids"]) == 2 and exact["outcome_data_ids"] == exact["node"]["data_ids"]
    consumer = result["derivations"][exact["parents"][0]]["node"]["data_ids"]
    assert len(set(consumer).intersection(exact["outcome_data_ids"])) == 1
    assert not any(row["code"] == "unavailable_outcome_dependency" for row in result["diagnostics"])


def test_protected_dispatch_demands_the_case_selector_and_no_payload_for_control():
    from tests.propagation.test_protected_outcomes import protected_call, use_outcome_dispatch
    from skillflow.propagation.material import prepare_material
    material, wire = protected_call(True)
    use_outcome_dispatch(material, wire)
    instructions = material["cfg"]["blocks"]["sample"]["instructions"]
    instructions[0]["inputs"] = [result("choice"), result("shared")]
    instructions.insert(0, instruction("ir_choice", "choose", [], "choice"))
    instructions.insert(0, instruction("ir_shared", "value", [], "shared"))
    wire["ir_semantics"]["ir_shared"] = {"evidences": [evidence()], "output_bindings": [
        {"output_index": 0, "value": {"kind": "literal", "value": False}}]}
    normal, raised = wire["ir_semantics"]["ir_call"]["segments"][0]["cases"]
    normal["yield"] = inp(1)
    raised["raise"] = inp(1)
    wire["ir_semantics"]["ir_choice"] = {"evidences": [evidence()], "output_bindings": [
        {"output_index": 0, "value": {"kind": "alternatives", "items": [
            {"kind": "literal", "value": flag} for flag in [False, True]]}}]}
    material = prepare_material(material["source"], material["cfg"], task_baseline=material["task"])
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)
    demanded = prepare_joint_sensitivity_review(facts, facts.annotation).demand_dict()
    rows = list(demanded["derivations"].values())
    routes = {row.case_id: row.target for row in solved.records.get("ir_route").outcome_routes}
    traces = {routes[row.case_id]: row for row in solved.records.get("ir_call").outcomes}
    assert traces["normal"].values == traces["raised"].values
    assert traces["normal"].selectors.isdisjoint(traces["raised"].selectors)
    controls = [row for row in rows if "outcome_dispatch_selector" in row["rules"]]
    assert controls and all(row["node"]["instruction_id"] == "ir_call" and row["node"]["slot"] == 0
                            and set(row["outcome_data_ids"]) == traces["normal"].selectors for row in controls)
    assert not any(row["node"]["instruction_id"] == "ir_route" and "control_operands_retained" in row["rules"]
                   for row in rows)
    from skillflow.doe.demand_results import validate_result_references
    from skillflow.propagation.contracts.demand_index import build_demand_target_index
    import pytest
    targets = build_demand_target_index(facts.cfg, raw)
    controls[0]["outcome_data_ids"] = sorted(traces["raised"].selectors)
    with pytest.raises(ValueError):
        validate_result_references(demanded, facts, targets)
