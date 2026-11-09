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
            operations = [{"op": "call", "location": "api", "inputs": [{"kind": "input", "index": 0}], "output": "reply"}]
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
        assert result.coverage["ir_fetch"] == "not_reached"
    # Serialization plus the ordinary material loader must understand the new
    # records; solver completion alone is not enough for a useful downstream run.
    facts = materials_from_result(result, material=material, raw_annotation=raw,
        compiled_annotation=json.loads(json.dumps(compiled)), mapping=mapping, wire_annotation=saved)
    facts.record_store.validate(require_complete=True)
    review = prepare_joint_sensitivity_review(facts, facts.annotation)
    assert review.to_dict()["status"] in {"complete", "incomplete"}
    assert review.demand_dict()["goals"]
    assert not any(d.get("code") == "missing_collection_record" for d in review.demand_dict()["diagnostics"])
