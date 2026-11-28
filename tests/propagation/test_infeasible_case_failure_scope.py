"""Offline authored regressions; no model, network, or retained run replay."""
import pytest

from tests.propagation.test_protected_outcomes import protected_call
from skillflow.propagation.annotation.binding_examples import evidence, instruction, local, result
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.solver import propagate


def segment(ops):
    return {"mode": "local", "returns": [], "ops": ops}


def filtered(value, name):
    return {"op": "filter_items", "input": value, "predicate": "keep", "output": name}


def guarded_bad_dependency(choice, *, guard_kind="literal", dependency="outcome", selected=False):
    material, wire = protected_call(choice)
    rows = material["cfg"]["blocks"]["sample"]["instructions"]
    call = rows[0]
    cases = wire["ir_semantics"]["ir_call"]["segments"][0]["cases"]
    if guard_kind != "literal":
        rows.insert(0, instruction("ir_guard_value", "load", [], "guard_value"))
        call["inputs"][0] = result("guard_value")
        for index, case in enumerate(cases):
            case["guard"] = {"input_index": 0, "path": ["selected"],
                "tests": [{"kind": "equals", "value": True}], "outcome": index}
        ref = {"kind": "literal", "value": {"selected": choice}}
        wire["ir_semantics"]["ir_guard_value"] = {"evidences": [evidence()], "segments": [],
            "output_bindings": [{"output_index": 0, "value": ref}]}
        if guard_kind == "unknown":
            wire["ir_semantics"]["ir_guard_value"].update(segments=[segment([
                {"op": "read", "location": "cache", "output": "guard"}])],
                output_bindings=[{"output_index": 0, "value": local("guard")}])

    rows.insert(0, instruction("ir_bad", "filter", [], "bad"))
    wire["ir_semantics"]["ir_bad"] = {"evidences": [evidence()], "segments": [segment([
        filtered({"kind": "literal", "value": {"wrong": "shape"}}, "bad")])],
        "output_bindings": [{"output_index": 0, "value": local("bad")}]}
    call["inputs"].append(result("bad"))
    case_index = (0 if choice else 1) if selected else (1 if choice else 0)
    chosen = cases[case_index]
    bad_ref = {"kind": "input", "index": 1}
    if dependency == "outcome":
        chosen["yield" if case_index == 0 else "raise"] = bad_ref
    else:
        chosen["segments"].append(segment([filtered(bad_ref, "unused")]))
    return material, wire


def solve(material, wire):
    _, _, compiled, _ = compile_flat_response(wire, material)
    return propagate(material["cfg"], to_payload(compiled))


@pytest.mark.parametrize("choice", [True, False])
@pytest.mark.parametrize("guard_kind", ["literal", "result_field"])
@pytest.mark.parametrize("dependency", ["outcome", "operation"])
def test_infeasible_sibling_cannot_poison_selected_outcome(choice, guard_kind, dependency):
    solved = solve(*guarded_bad_dependency(choice, guard_kind=guard_kind, dependency=dependency))
    assert solved.coverage["ir_bad"] == "execution_error"
    assert solved.coverage["ir_call"] == solved.coverage["ir_route"] == "processed"
    selected, absent = ("normal", "raised") if choice else ("raised", "normal")
    assert solved.coverage["ir_read_" + selected] == "processed"
    assert solved.coverage["ir_end_" + selected] == "processed"
    assert solved.coverage["ir_read_" + absent] == "infeasible"
    error = next(row for row in solved.diagnostics if row["code"] == "operation_execution_error")
    assert error["affected_instruction_ids"] == ["ir_bad"]
    solved.records.validate()


@pytest.mark.parametrize("choice", [True, False])
@pytest.mark.parametrize("dependency", ["outcome", "operation"])
def test_feasible_case_dependency_is_still_blocked(choice, dependency):
    solved = solve(*guarded_bad_dependency(choice, dependency=dependency, selected=True))
    assert solved.coverage["ir_call"] == solved.coverage["ir_route"] == "blocked"


@pytest.mark.parametrize("choice", [True, False])
@pytest.mark.parametrize("dependency", ["outcome", "operation"])
def test_unknown_guard_remains_conservative(choice, dependency):
    solved = solve(*guarded_bad_dependency(choice, guard_kind="unknown", dependency=dependency))
    assert solved.coverage["ir_call"] == solved.coverage["ir_route"] == "blocked"


@pytest.mark.parametrize("choice", [True, False])
def test_unavailable_selector_is_always_a_control_dependency(choice):
    material, wire = guarded_bad_dependency(choice)
    call = next(row for row in material["cfg"]["blocks"]["sample"]["instructions"]
                if row["id"] == "ir_call")
    call["inputs"][0] = result("bad")
    solved = solve(material, wire)
    assert solved.coverage["ir_call"] == solved.coverage["ir_route"] == "blocked"


@pytest.mark.parametrize("choice", [True, False])
def test_actual_selected_case_operation_error_is_not_suppressed(choice):
    material, wire = protected_call(choice)
    cases = wire["ir_semantics"]["ir_call"]["segments"][0]["cases"]
    cases[0 if choice else 1]["segments"].append(segment([
        filtered({"kind": "literal", "value": {"wrong": "shape"}}, "bad")]))
    solved = solve(material, wire)
    assert solved.coverage["ir_call"] == "execution_error"
    assert solved.coverage["ir_route"] == "blocked"

