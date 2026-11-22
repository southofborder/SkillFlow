"""A frozen GA4 batch projection through compact compile, loop solving and DOE.

The source is hashed and read, never executed. Concrete URLs are synthetic input
fixtures. This tests the declared batch boundary, not full-Skill correctness.
"""
from copy import deepcopy
import json

import pytest

from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from tests.document_guided.test_ga4_granularity import source_material
from tests.propagation.test_explicit_loops import explicit_loop_fixture


def batch_projection(values):
    cfg, annotation = explicit_loop_fixture(values)
    material, citation = source_material(cfg, "api/indexing.ts", 89, 105)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}],
        "locations": {"api": {"kind": "remote", "name": "api", "evidences": [citation]}},
        "demands": [{"requirement_id": "R1", "target": {
            "instruction_id": "ir_return", "side": "input", "index": 0},
            "preserve": "value", "reason": "The batch returns its complete collected result on normal completion."}],
        "ir_semantics": {}}
    for identity, spec in annotation["ir_semantics"].items():
        operations = [deepcopy(op) for event in spec["events"] for op in event["atomic_ops"]]
        if identity == "ir_fetch":
            operations = [{"op": "call", "location": "api", "inputs": [{"kind": "input", "index": 0}], "output": "reply",
                "input_contract": {"inputs": [{"input_index": 0,
                    "required": [{"property": "value", "path": []}], "remainder": "independent",
                    "reason": "The projected request's actual argument is the required URL string."}],
                    "reason": "requestIndexing requires the URL argument and forwards its value in requestBody.url.",
                    "evidences": [{**citation, "start_line": 53, "end_line": 67,
                        "reason": "The URL parameter is required and passed to the remote indexing request."},
                        {**citation, "start_line": 95, "end_line": 97,
                         "reason": "Each batch occurrence supplies its URL to requestIndexing."}]}}]
        wire["ir_semantics"][identity] = {"evidences": [citation],
            "segments": [{"mode": "local", "returns": [], "ops": operations}] if operations else [],
            "output_bindings": deepcopy(spec["output_bindings"])}
    return material, wire


@pytest.mark.parametrize("values", [[], ["https://a.example", "https://b.example"],
                                   ["https://a.example", "https://a.example"]])
def test_ga4_explicit_batch_compiles_propagates_and_roundtrips_to_doe(values):
    material, wire = batch_projection(values)
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    result = propagate(material["cfg"], to_payload(compiled))
    assert result.status == "complete", result.diagnostics
    assert result.coverage["ir_return"] == "processed"
    if values:
        operation = result.records.get("ir_member").events[0].atomic_ops[0]
        assert len(operation.outputs[0]) == len(values)
        assert any(e.effect == "net_send" for e in result.records.get("ir_fetch").events)
    else:
        # This exact empty batch excludes the body through its recorded guard.
        assert result.coverage["ir_fetch"] == "infeasible"
    # Serialization plus the ordinary material loader must understand the new
    # records; solver completion alone is not enough for a useful downstream run.
    facts = materials_from_result(result, material=material, raw_annotation=raw,
        compiled_annotation=json.loads(json.dumps(compiled)), mapping=mapping, wire_annotation=saved)
    facts.record_store.validate(require_complete=True)
    review = prepare_joint_sensitivity_review(facts, facts.annotation)
    demand = review.demand_dict()
    contract_gaps = [row for row in demand["diagnostics"] if row["code"] == "input_contract_unavailable"]
    if values:
        assert review.to_dict()["status"] == "partial"
        assert contract_gaps and {row["instruction_id"] for row in contract_gaps} == {"ir_fetch"}
        assert all(row["blocking"] and row["operation_id"] for row in contract_gaps)
        # The interface is authored, but this standalone projection has no
        # source-review receipt. Its complete propagation records remain usable.
    else:
        assert review.to_dict()["status"] == "complete" and not contract_gaps
    assert demand["goals"]
    assert not any(d.get("code") == "missing_collection_record" for d in review.demand_dict()["diagnostics"])
