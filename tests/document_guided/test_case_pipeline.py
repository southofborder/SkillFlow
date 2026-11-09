"""Offline case propagation survives JSON loading and final DOE presentation."""
import json

import pytest

from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.binding_examples import evidence
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.records import PropagationRecords
from skillflow.propagation.report import render_html as propagation_html, render_markdown as propagation_markdown
from skillflow.propagation.solver import propagate
from skillflow.doe.material import prepare_doe_material
from skillflow.doe.report import render_html, render_markdown
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.doe.sensitivity_report import render_html as sensitivity_html, render_markdown as sensitivity_markdown
from tests.document_guided.test_case_summaries import case_fixture, local


def roundtrip(value):
    return json.loads(json.dumps(value))


@pytest.mark.parametrize("catch", [True, False])
def test_case_collection_roundtrip_demand_sensitivity_and_reports(catch):
    material, wire = case_fixture(catch=catch)
    wire["ir_semantics"]["ir_call"]["segments"][0]["sensitivity"] = [{
        "value": local("reply"), "label": "Private response", "evidences": [evidence()],
        "case_path": ["segments", 0, "body", 0, "cases", 0]}]
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete"

    restored = PropagationRecords.from_records(roundtrip(solved.records.records_dict()), cfg=material["cfg"],
        annotation=roundtrip(to_payload(compiled)), data_registry=DataRegistry.from_dict(roundtrip(solved.registry.to_dict())),
        initial_data=roundtrip(solved.initial_data), initial_state=roundtrip(solved.initial_state))
    restored.validate(require_complete=True)
    assert restored.records_dict() == solved.records.records_dict()
    facts = materials_from_result(solved, material=material, raw_annotation=roundtrip(raw),
        compiled_annotation=roundtrip(compiled), mapping=roundtrip(mapping), wire_annotation=roundtrip(saved))
    assert facts.record_store.records_dict() == restored.records_dict()
    assert propagation_html(facts) and propagation_markdown(facts)

    doe = prepare_doe_material(facts)
    markdown, html = render_markdown(doe), render_html(doe)
    assert "mapped" in markdown.lower() and "mapped" in html.lower()
    assert "alternative" in markdown.lower() and "alternative" in html.lower()
    review = prepare_joint_sensitivity_review(facts, facts.annotation)
    result = review.to_dict()
    assert result["status"] == "complete"
    assert result["coverage"]["declarations"] > 0
    assert review.demand_dict()["status"] == "complete"
    assert sensitivity_markdown(review) and sensitivity_html(review)


@pytest.mark.parametrize("mode", ["default", "model"])
def test_case_observations_retain_candidate_and_member_scope(mode):
    material, wire = case_fixture(state=False)
    normal = wire["ir_semantics"]["ir_call"]["segments"][0]["body"][0]["cases"][0]["segments"][0]
    normal["mode"] = mode
    normal.pop("returns")
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete"
    loop = solved.records.get("ir_call").events[0]
    assert {instance.selector for instance in loop.instances} == {0, 1}
    for instance in loop.instances:
        observations = [event for event in instance.body if event.effect == "model_observe"]
        assert observations
        assert all(event.case is not None and event.case.phase == "normal" for event in observations)
        actual_case = next(event.case for event in instance.body if event.effect == "net_send")
        assert all(event.case == actual_case for event in observations)
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)
    facts.record_store.validate(require_complete=True)
