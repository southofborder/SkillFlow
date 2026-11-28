from copy import deepcopy

from skillflow.document_guided.fragments import assemble_outcome_dispatches
from skillflow.document_guided.graph_facts import assemble_graph_facts
from tests.document_guided.test_outcome_dispatch_graph import FILES, example, span


def material():
    cfg = assemble_graph_facts(example(ports=True), files=FILES).cfg
    return {"cfg": cfg, "source": {"files": [
        {"path": k.removeprefix("skill/"), "content": v} for k, v in FILES.items()]}}


def test_program_supplies_only_missing_control_row_and_preserves_producer_gap():
    value = {"ir_semantics": {}, "processing_gaps": [
        {"instruction_id": ir, "unmodeled": True, "control": True, "evidences": [span(1)],
         "reason": "No submitted processing summary."} for ir in ("ir_001", "ir_002")]}
    assemble_outcome_dispatches(value, material())
    assert list(value["ir_semantics"]) == ["ir_002"]
    assert list(value["ir_semantics"]["ir_002"]) == ["evidences"]
    assert [r["instruction_id"] for r in value["processing_gaps"]] == ["ir_001"]
    before = deepcopy(value)
    assemble_outcome_dispatches(value, material())
    assert value == before


def test_preserves_fixed_or_contested_rows_for_validation():
    existing = {"evidences": [span(1)], "segments": []}
    gap = {"instruction_id": "ir_002", "unmodeled": True, "control": True,
           "reason": "Conflict in this submission.", "evidences": [span(1)]}
    for records, gaps, fixed in (({}, [gap], {"ir_002"}), ({"ir_002": existing}, [gap], set())):
        value = {"ir_semantics": records, "processing_gaps": gaps}
        before = deepcopy(value)
        assemble_outcome_dispatches(value, material(), fixed=fixed)
        assert value == before
