"""Ordered effects keep occurrence identity in English review reports."""

from skillflow.propagation.annotation.report import render_report
from tests.propagation.annotation.helpers import material, semantics


def test_report_keeps_repeated_effect_steps_and_their_evidence():
    prepared = material()
    spec = semantics(prepared, "ir_filter", operator=["llm"],
                     effects=["model_observe", "transform", "model_observe"])
    spec["order"] = "partial"
    for index, event in enumerate(spec["events"]):
        event["evidences"][0]["reason"] = f"Occurrence evidence {index}"
    result = {"run_id": "ordered", "status": "complete", "reason": "Partial order is computable",
              "notice": "Not a proof", "graph_sha256": "graph", "ir_semantics": {"ir_filter": spec}}
    text = render_report(result, prepared)
    assert "1. model_observe<br>2. transform<br>3. model_observe" in text
    assert "Partial order; retain possible arrangements under causal constraints" in text
    assert "Event 0: model_observe" in text and "Event 2: model_observe" in text
    assert "Occurrence evidence 0" in text and "Occurrence evidence 2" in text
    assert "the array is not the unique execution order" in text


def test_report_displays_operator_context_writes_and_non_nop_empty_effects():
    prepared = material()
    specs = {
        "ir_read": semantics(prepared, "ir_read", operator=["agent_runtime"],
                             effects=["context_write", "context_write"]),
        "ir_return": semantics(prepared, "ir_return", operator=["agent_runtime"]),
    }
    result = {"run_id": "context", "status": "complete", "reason": "Offline example",
              "notice": "Not a semantic measurement", "graph_sha256": "graph", "ir_semantics": specs}
    text = render_report(result, prepared)
    assert "Executing subjects (operator)" in text
    assert "1. context_write (context write)<br>2. context_write (context write)" in text
    assert "[] (no recorded effects; not a no-op" in text
    assert "cannot establish equal entry and exit states" in text
    assert "| ir_return | return | agent_runtime | [] (no recorded effects" in text


def test_report_displays_program_boundary_location_and_scope_without_free_risk_score():
    result = {"run_id": "boundaries", "status": "complete", "reason": "记录完整",
              "notice": "非风险判断", "graph_sha256": "graph", "ir_semantics": {},
              "locations": {"endpoint": {"kind": "remote", "name": "公开发布",
                    "operand_refs": [], "access_scope": "public", "retention": None}},
              "sink_boundaries": [{"instruction_id": "send", "event_index": 2,
                    "op_index": 1, "body_event_index": 3, "scope": "row", "target": "endpoint",
                    "sink_type": "network_send", "exposure_level": 3}]}
    report = render_report(result, None)
    assert "send / 2.3 / 1" in report
    assert "network_send | 3 | public / None | row" in report
    assert "not sensitivity, danger, task necessity or DOE conclusions" in report
    assert "[Compiled semantics, locations and sinks](audit/compiled-response.json)" in report
    assert "level 0 is excluded from the sink list" in report
