"""Exercise imported outcome tuples against real closed in-memory solver facts."""

from copy import deepcopy

import pytest

from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.binding_examples import evidence, inp, instruction, literal, local, result
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.models import validate_public_outputs
from skillflow.propagation.solver import propagate
from tests.propagation.test_protected_outcomes import protected_call


def solve(material, wire):
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    instruction = next(row for row in material["cfg"]["blocks"]["sample"]["instructions"] if row["id"] == "ir_call")
    spec = compiled["ir_semantics"]["ir_call"]
    return instruction, spec, solved.records.get("ir_call"), solved.registry


def exchanged(record, first, second, field):
    rows = list(record.outcomes)
    rows[first] = rows[first].model_copy(update={field: getattr(record.outcomes[second], field)})
    rows[second] = rows[second].model_copy(update={field: getattr(record.outcomes[first], field)})
    return record.model_copy(update={"outcomes": rows})


@pytest.mark.parametrize("source", ["literal", "input", "local"])
@pytest.mark.parametrize("field", ["values", "completion"])
def test_same_disposition_outcomes_cannot_exchange_row_evidence(source, field):
    material, wire = protected_call()
    group = wire["ir_semantics"]["ir_call"]["segments"][0]
    normal = group["cases"][0]
    other = deepcopy(normal)
    other["name"] = "other_return"
    other["condition"] = "Returns the second documented value."
    group["cases"].insert(1, other)
    if source == "literal":
        other["yield"] = {"kind": "literal", "value": None}
    elif source == "input":
        instruction = material["cfg"]["blocks"]["sample"]["instructions"][0]
        instruction["inputs"] += [literal(7), literal(None)]
        normal["yield"], other["yield"] = inp(1), inp(2)
    else:
        for case, value in [(normal, 7), (other, None)]:
            case["segments"].append({"mode": "local", "returns": [], "ops": [
                {"op": "build", "container": "object", "parts": [
                    {"path": ["actual"], "value": {"kind": "literal", "value": value}}], "output": "case_value"}]})
            case["yield"] = local("case_value")
    instruction, spec, record, data = solve(material, wire)
    validate_public_outputs(instruction, spec, record, data)
    group = spec["outcome_bindings"][0]
    returning = {case["case_id"] for case in group["cases"] if case["disposition"] == "return"}
    i, j = [offset for offset, row in enumerate(record.outcomes) if row.case_id in returning]
    with pytest.raises(ValueError, match="declared protected outcome source|belongs to another protected outcome"):
        validate_public_outputs(instruction, spec, exchanged(record, i, j, field), data)


def test_guard_cannot_take_a_known_value_from_another_role():
    instruction, spec, record, data = solve(*protected_call(True))
    validate_public_outputs(instruction, spec, record, data)
    row, = record.outcomes
    forged = row.model_copy(update={"selectors": row.values})
    with pytest.raises(ValueError, match="not a feasible version"):
        validate_public_outputs(instruction, spec, record.model_copy(update={"outcomes": [forged]}), data)


def test_intrinsic_exception_keeps_the_real_scoped_version():
    instruction, spec, record, data = solve(*protected_call(False))
    validate_public_outputs(instruction, spec, record, data)
    row, = record.outcomes
    assert row.values and all(data.get(identity).content.form in {"loop_summary", "opaque"}
                              for identity in row.values)


def test_guard_rejects_infeasible_selector_even_from_the_correct_entry_operand():
    material, wire = protected_call(True)
    sequence = material["cfg"]["blocks"]["sample"]["instructions"]
    sequence[0]["inputs"] = [result("actual_choice")]
    sequence.insert(0, instruction("ir_choice", "value", [], "actual_choice"))
    wire["ir_semantics"]["ir_choice"] = {"evidences": [evidence()], "output_bindings": [
        {"output_index": 0, "value": {"kind": "alternatives", "items": [
            {"kind": "literal", "value": True}, {"kind": "literal", "value": False}]}}]}
    owner, spec, record, data = solve(material, wire)
    validate_public_outputs(owner, spec, record, data)
    assert len(record.outcomes) == 2
    assert len({identity for row in record.outcomes for identity in row.selectors}) == 2
    with pytest.raises(ValueError, match="not a feasible version"):
        validate_public_outputs(owner, spec, exchanged(record, 0, 1, "selectors"), data)


def test_import_keeps_valid_guarded_alternative_result_views():
    material, wire = protected_call(True)
    sequence = material["cfg"]["blocks"]["sample"]["instructions"]
    sequence[0]["inputs"] += [result("payload")]
    sequence.insert(0, instruction("ir_payload", "value", [], "payload"))
    wire["ir_semantics"]["ir_payload"] = {"evidences": [evidence()], "output_bindings": [
        {"output_index": 0, "value": {"kind": "literal", "value": {"detail": "a"}}}]}
    group = wire["ir_semantics"]["ir_call"]["segments"][0]
    normal = group["cases"][0]
    normal["yield"] = {"kind": "alternatives", "guard": deepcopy(normal["guard"]),
                       "items": [inp(1), {"kind": "literal", "value": None}]}
    owner, spec, record, data = solve(material, wire)
    versions = set().union(*(row.values for row in record.outcomes))
    assert len(versions) == 2
    assert all(data.get(identity).content.form in {"selection", "loop_summary"} for identity in versions)
    validate_public_outputs(owner, spec, record, data)


def test_missing_literal_projection_does_not_assert_null():
    from skillflow.propagation.data import DataRegistry, LiteralContent, Origin, SelectionContent
    from skillflow.propagation.outcome_validation import _literal_matches

    data = DataRegistry("outcome_literal")
    source = data.create_result("source", content=LiteralContent(value={}), origin=Origin(at="source"))
    missing = data.create_result("missing", content=SelectionContent(base=source.id, path=["absent"]),
        origin=Origin(at="missing", inputs=[source.id]))
    assert not _literal_matches(data, missing.id, None)
