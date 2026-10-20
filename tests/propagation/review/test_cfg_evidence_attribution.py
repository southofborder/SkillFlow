"""Reference legality and semantic attribution remain separate obligations.

These offline fixtures do not supply answers to production prompts or establish
model accuracy. Source supports field claims; graph references support exactly
their recorded graph objects.
"""
from copy import deepcopy
import json
import re

import pytest

from skillflow.propagation.annotation.binding_examples import example_material
from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
from skillflow.propagation.annotation.requests import build_repair_context
from skillflow.propagation.material import evidence_reference
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.models import task_objections
from skillflow.propagation.review.services import validate_response
from tests.propagation.review.test_endpoint_review_example import rendered_lesson
from tests.propagation.review.test_specific_demands_and_prohibitions import (
    _blank_review, _restriction_fixture, _task_omission_review,
)


def _field_review(material, prepared, evidence):
    response = _blank_review(prepared)
    target = next(row for row in prepared["target_index"]
                  if row["kind"] == "annotation"
                  and row["pointer"] == "/ir_semantics/ir_stencil_display/sensitivity")
    response["findings"] = [{
        "domain": "annotation", "target_ids": [target["id"]],
        "explanation": "This injected claim checks evidence attribution, not semantic correctness.",
        "evidences": [evidence],
        "suggestion": "Use the original source for the field claim and retain any independently useful graph identity reference.",
    }]
    return response


def test_sent_complete_lesson_separates_source_field_claims_from_bare_operand_identity():
    prompt, shown, material, prepared = rendered_lesson()
    checked = validate_response(shown["response"], prepared)
    assert len(checked.findings) == 2
    graph_reasons = []
    for finding in shown["response"]["findings"]:
        sources = [item for item in finding["evidences"] if "file" in item]
        assert sources
        for evidence in sources:
            source = evidence_reference(evidence, material)
            assert source["kind"] == "source" and "badge" in source["text"]
        for evidence in finding["evidences"]:
            if "target" not in evidence:
                continue
            graph = evidence_reference(evidence, material)
            assert set(graph["value"]) == {"type", "identifier"}
            assert graph["value"]["type"] == "result"
            graph_reasons.append(evidence["reason"])
    assert graph_reasons == [
        "This CFG output operand defines the result symbol for the read instruction.",
        "This CFG input operand references the earlier result symbol used by this instruction.",
    ]
    assert re.findall(r"<!-- SKILLFLOW_PROMPT:([A-Z_]+):BEGIN -->", prompt) == [
        "AUTHORITY", "INPUT", "FORMAT", "WORKFLOW", "RULES", "EXAMPLES", "SELF_CHECK"]
    assert prompt.count("\nREVIEW_EXAMPLES\n") == 1
    assert "A result identifier names a value, not its members." in prompt
    assert "including in sensitivity findings" in prompt
    assert "not unconditional runtime presence" in prompt


def test_source_only_field_evidence_accepts_complete_review_without_fabricated_cfg_reference():
    _, shown, material, prepared = rendered_lesson()
    raw = deepcopy(shown["response"])
    for finding in raw["findings"]:
        finding["evidences"] = [e for e in finding["evidences"] if "file" in e]
    before = deepcopy((material, prepared, raw))
    checked = validate_response(raw, prepared)
    assert len(checked.findings) == 2
    assert all(all(hasattr(e, "file") for e in finding.evidences) for finding in checked.findings)
    assert (material, prepared, raw) == before


def test_source_range_establishes_field_context_while_result_operand_only_records_symbol():
    _, material, raw = _restriction_fixture()
    prepared = prepare_review_material(material, raw)
    source_evidence = {"file": "skill/SKILL.md", "start_line": 2, "end_line": 2,
                       "reason": "The original source identifies archive_pin as a private credential."}
    response = validate_response(_field_review(material, prepared, source_evidence), prepared)
    assert response.findings[0].evidences[0].reason == source_evidence["reason"]
    assert "archive_pin" in evidence_reference(source_evidence, material)["text"]
    graph = evidence_reference({"target": {"instruction_id": "ir_stencil_display",
                                          "side": "output", "index": 0},
                                "reason": "The CFG defines this result identity."}, material)
    assert graph["value"] == {"type": "result", "identifier": "caption"}
    assert "archive_pin" not in graph["text"]


@pytest.mark.parametrize("location,expected", [
    ({"side": "input", "index": 0}, {"type": "literal", "literal_value": {"caption": "Ready", "archive_pin": "private"}}),
    ({"path": ["inputs", 0, "literal_value", "archive_pin"]}, "private"),
    ({"path": ["constraints", 0]}, "If archive_pin exists, never display it."),
    ({"path": ["metadata", "events", "path"]}, ["archive_pin"]),
])
def test_explicit_graph_literal_constraint_or_metadata_can_support_its_recorded_fact(location, expected):
    example, _, raw = _restriction_fixture()
    instruction = example["cfg"]["blocks"]["sample"]["instructions"][0]
    instruction["constraints"] = ["If archive_pin exists, never display it."]
    instruction["metadata"] = {"events": {"path": ["archive_pin"]}}
    material = example_material(example)
    raw["task_revision_id"] = material["task"]["task_sha256"]
    prepared = prepare_review_material(material, raw)
    evidence = {"target": {"instruction_id": "ir_stencil_display", **location},
                "reason": "This graph location records the stated literal, condition or path; it does not establish every execution's content or sensitivity."}
    before = deepcopy((material, raw))
    assert validate_response(_field_review(material, prepared, evidence), prepared).findings
    resolved = evidence_reference(evidence, material)
    assert resolved["value"] == expected
    assert json.loads(resolved["text"]) == expected
    assert (material, raw) == before


@pytest.mark.parametrize("reason", [
    "The result operand names the caption result symbol.",
    "The result operand names a value which contains archive_pin on every path and proves its sensitivity.",
])
def test_real_operand_with_semantically_overclaiming_reason_remains_mechanically_legal(reason):
    _, material, raw = _restriction_fixture()
    prepared = prepare_review_material(material, raw)
    evidence = {"target": {"instruction_id": "ir_stencil_display", "side": "output", "index": 0},
                "reason": reason}
    checked = validate_response(_field_review(material, prepared, evidence), prepared)
    assert checked.findings[0].evidences[0].reason == reason
    assert evidence_reference(evidence, material)["value"] == {"type": "result", "identifier": "caption"}
    # The second reason is deliberately wrong. A valid reference is neither
    # semantic verification nor a reason to add a keyword-based rejection.


def test_attribution_refinement_preserves_specific_migration_targets_and_task_objection_routing():
    _, shown, material, prepared = rendered_lesson()
    checked = validate_response(shown["response"], prepared)
    finding = checked.findings[1]
    named = set(re.findall(r"\bann_\d+\b", finding.suggestion))
    context = build_repair_context(material, prepared["raw_annotation"], prepared, checked)
    prompt = annotation_prompt(material, repair_context=context)
    sent = json.JSONDecoder().raw_decode(prompt.split("\nREPAIR_CONTEXT\n", 1)[1])[0]
    resolved = {row["id"]: row for group in sent["resolved_targets"] for row in group["targets"]}
    assert named <= set(finding.target_ids) and named <= set(resolved)
    assert len([target for target in named if "/demands/" in resolved[target]["pointer"]]) == 2
    assert "do not retain their upstream copies" in finding.suggestion
    _, restriction_material, raw = _restriction_fixture()
    restriction = prepare_review_material(restriction_material, raw)
    objection = validate_response(_task_omission_review(restriction), restriction)
    assert task_objections(objection) == [{"code": "missing_requirement", "source_spans": [
        {"file": "skill/SKILL.md", "start_line": 2, "end_line": 2}], "requirement_ids": []}]
