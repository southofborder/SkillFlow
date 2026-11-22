"""Focused acceptance assertions over the frozen input-necessity implementation."""
from copy import deepcopy

import pytest

from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.doe.input_assessments import deletable_reduction
from skillflow.doe.sensitivity_material import (
    joint_demands, prepare_sensitivity_review, validate_sensitivity_result,
)
from skillflow.propagation.contracts.task import Task
from tests.doe.test_demand_engine import fixture, inp, literal
from tests.doe.test_input_contract_preservation import accepted_receipt, reviewed_fixture
from tests.doe.test_reviewed_input_necessity import compute, row, rule, solve
from tests.doe.test_sensitivity_engine import declarations
from tests.doe.test_sink_payload_seeds import synthetic_fixture


def test_reviewed_tool_whole_value_requirement_retains_every_present_field():
    from skillflow.propagation.annotation.binding_examples import evidence
    contract = {"inputs": [{"input_index": 0, "required": [{"property": "value", "path": []}],
        "remainder": "independent",
        "reason": "The interface transmits the complete supplied document as one necessary parameter."}],
        "reason": "The service response is the complete original document, including its service_note field.",
        "evidences": [evidence()]}
    material, raw, facts = synthetic_fixture([
        {"op": "deliver", "target": "label_receiver", "inputs": [inp()], "input_contract": contract},
        {"op": "receive", "location": "label_receiver", "inputs": [inp()], "output": "receipt",
         "input_contract": contract}], output="receipt", return_demand=True,
        source="The service requires the entire supplied document and returns it unchanged, including service_note.")
    annotation = facts.annotation
    engine = DemandEngine(facts, Task.model_validate(material["task"]), annotation, joint_demands(annotation),
        build_demand_target_index(facts.cfg, raw), input_contract_review=accepted_receipt(facts, annotation))
    original = deepcopy(facts.records)
    result = engine.solve()
    assert result["status"] == "complete"
    for key, info in engine.ops.items():
        if info["spec"]["op"] not in {"deliver", "receive"}:
            continue
        assessment = next(item for item in result["input_assessments"]
            if item["node_kind"] == "op_input" and item["operation_id"] == key and item["input_index"] == 0)
        assert any(item["status"] == "required" and item["property"] == "value"
                   and item["path"] == [] for item in assessment["ranges"])
        assert not any(item["status"] == "deletable" for item in assessment["ranges"])
        for data_id in info["record"]["inputs"][0]:
            assert deletable_reduction(result, key, 0, data_id, ["service_note"]) == (None, [])
    assert facts.records == original


def test_invalid_required_field_selector_reports_wrong_input_without_repairing_data():
    values = fixture([compute([literal(7)], [rule([], [row(0, ["needed"])])])])
    original = deepcopy((values[0].records, values[0].data))
    _, result = solve(values)
    assert result["status"] == "partial"
    diagnostic = next(item for item in result["diagnostics"] if item["code"] == "input_contract_wrong_input")
    finding = next(item for item in result["input_findings"] if item["kind"] == "wrong_input")
    assert finding["diagnostic_refs"] == [diagnostic["id"]]
    assert "needed" in finding["reason"] and "invalid" in finding["reason"]
    assert not any(item["kind"] == "missing_input" for item in result["input_findings"])
    assert (values[0].records, values[0].data) == original


@pytest.mark.parametrize("receipt_kind", ["missing", "different"])
def test_sensitivity_loader_rejects_a_demand_bound_to_another_review_receipt(receipt_kind):
    values, receipt, request, _ = reviewed_fixture([])
    facts, task, annotation, _ = values
    review = prepare_sensitivity_review(facts, task, annotation, request, declarations(),
                                       input_contract_review=receipt)
    supplied = None
    if receipt_kind == "different":
        supplied = deepcopy(receipt)
        supplied["receipt_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="Demand input-contract review identity differs"):
        validate_sensitivity_result(review.to_dict(), facts, task, annotation, request, declarations(),
            demand_result=review.demand_dict(), input_contract_review=supplied)
