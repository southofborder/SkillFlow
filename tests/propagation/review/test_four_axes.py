"""Coverage and isolation checks verify the protocol, never model detection rates."""
from copy import deepcopy
import json

import pytest

from skillflow.propagation.review.material import prepare_review_material, checked_review_material
from skillflow.propagation.review.models import task_objections
from skillflow.propagation.review.services import validate_response
from skillflow.propagation.review.prompts import build_prompt
from tests.propagation.review.test_core import fixture, empty_response
from tests.propagation.review.test_binding_coordinates import fixture as coordinate_fixture
from skillflow.propagation.annotation.binding_examples import example_material


def goal_material():
    example = coordinate_fixture(1)
    material = example_material(example)
    return prepare_review_material(material, example["annotation"])


def task_issue(prepared):
    result = empty_response(prepared)
    target = next(item for item in prepared["target_index"] if item["kind"] == "task" and item["pointer"] == "/requirements")
    span = {key: prepared["task"]["requirements"][0]["evidences"][0][key]
            for key in ("file", "start_line", "end_line")}
    result["findings"] = [{"domain": "task", "target_ids": [target["id"]],
        "explanation": "人工错误样例：原文义务遗漏，需独立重读源文核实。",
        "suggestion": "从原始材料重新提取该范围，不能以当前载荷扩大任务。",
        "evidences": [{**span, "reason": "原文义务证据，不包含实现反馈。"}],
        "task_objection": {"code": "missing_requirement", "source_spans": [span], "requirement_ids": []}}]
    return result


@pytest.mark.parametrize("axis", ["requirement_checks", "declaration_checks", "reviewed_ir_ids"])
def test_each_axis_rejects_omissions_duplicates_and_unknown_positions(axis):
    prepared = goal_material()
    for mode in ("missing", "duplicate", "unknown"):
        response = empty_response(prepared)
        if mode == "missing":
            response[axis].pop()
        elif mode == "duplicate":
            response[axis].append(deepcopy(response[axis][0]))
        elif axis == "requirement_checks":
            response[axis][0]["requirement_id"] = "missing"
        elif axis == "declaration_checks":
            response[axis][0]["raw_pointer"] = "/demands/999"
        else:
            response[axis][0] = "missing"
        with pytest.raises(ValueError):
            validate_response(response, prepared)


def test_source_omission_uses_real_evidence_without_a_per_line_table_or_fake_requirement():
    prepared = goal_material()
    response = task_issue(prepared)
    assert "source_line_universe" not in prepared
    accepted = validate_response(response, prepared)
    assert "source_checks" not in accepted.model_dump()
    assert accepted.findings[0].task_objection.requirement_ids == []
    assert all(check.status == "accepted" for check in accepted.requirement_checks)
    for field in ("source_checks", "source_line_universe"):
        mutated = deepcopy(response)
        mutated[field] = []
        with pytest.raises(ValueError):
            validate_response(mutated, prepared)
    altered = deepcopy(prepared)
    altered["source_line_universe"] = []
    with pytest.raises(ValueError):
        checked_review_material(altered)
    prompt = build_prompt(prepared)
    assert "source_checks" not in prompt and "source_accounting" not in prompt
    assert "exact source evidence and a real Task parent target" in prompt


def test_concrete_conclusions_link_findings_and_normalization_resolves_positions():
    prepared = goal_material()
    response = task_issue(prepared)
    response["requirement_checks"][0].update(status="issue", finding_indexes=[0])
    accepted = validate_response(response, prepared)
    assert accepted.requirement_checks[0].finding_ids == ["F001"]
    assert "finding_indexes" not in accepted.requirement_checks[0].model_dump()
    assert task_objections(accepted) == [response["findings"][0]["task_objection"]]
    normalized = accepted.model_dump(mode="json")
    assert validate_response(normalized, prepared, normalized=True) == accepted
    for indexes in ([], [10]):
        mutated = deepcopy(response)
        mutated["requirement_checks"][0]["finding_indexes"] = indexes
        with pytest.raises(ValueError):
            validate_response(mutated, prepared)
    normalized["requirement_checks"][0]["finding_ids"] = ["F999"]
    with pytest.raises(ValueError):
        validate_response(normalized, prepared, normalized=True)


@pytest.mark.parametrize("injection", ["reason", "cfg", "goals", "sink", "annotation"])
def test_task_objection_rejects_free_text_or_downstream_context(injection):
    prepared = goal_material()
    response = task_issue(prepared)
    response["findings"][0]["task_objection"][injection] = "current payload says keep everything"
    with pytest.raises(ValueError):
        validate_response(response, prepared)


def test_task_findings_cannot_be_routed_without_source_anchor_or_with_cfg_evidence():
    prepared = goal_material()
    for mutation in ("missing_evidence", "cfg_evidence", "annotation_target", "unknown_requirement", "unknown_span"):
        response = task_issue(prepared)
        finding = response["findings"][0]
        if mutation == "missing_evidence":
            finding["evidences"] = []
        elif mutation == "cfg_evidence":
            finding["evidences"] = [{"target": {"instruction_id": "ir_coordinate", "path": []}, "reason": "不能转为Task修订依据。"}]
        elif mutation == "annotation_target":
            finding["target_ids"] = [next(row["id"] for row in prepared["target_index"] if row["kind"] == "annotation")]
        elif mutation == "unknown_requirement":
            finding["task_objection"]["requirement_ids"] = ["missing"]
        else:
            finding["task_objection"]["source_spans"][0]["end_line"] = 999
        with pytest.raises(ValueError):
            validate_response(response, prepared)


def test_task_only_target_cannot_be_laundered_into_annotation_repair_domain():
    prepared = goal_material()
    response = task_issue(prepared)
    response["findings"][0].update(domain="annotation", task_objection=None)
    with pytest.raises(ValueError, match="real annotation or observation target"):
        validate_response(response, prepared)
    # Annotation findings may also cite Task context, provided the actual
    # candidate claim to repair is identified. This checks routing, not truth.
    response["findings"][0]["target_ids"].append(next(row["id"] for row in prepared["target_index"]
        if row["kind"] == "annotation" and row["pointer"] == "/realizations"))
    assert validate_response(response, prepared).findings[0].domain == "annotation"


def test_goal_projection_preserves_operation_slots_paths_and_original_seed_identity():
    prepared = goal_material()
    assert len(prepared["declaration_index"]) == 3
    assert [row["resolved_target"]["slot"] for row in prepared["declaration_index"]] == [0, 1, 2]
    assert [row["resolved_target"]["ref"]["index"] for row in prepared["declaration_index"]] == [0, 3, 1]
    assert prepared["declaration_index"][0]["resolved_target"]["role"] == "control"
    assert all(row["raw_pointer"].endswith(f"/demands/{i}") for i, row in enumerate(prepared["declaration_index"]))
    sent = json.JSONDecoder().raw_decode(build_prompt(prepared).split("\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n")[1])[0]
    assert sent["declaration_index"] == prepared["declaration_index"]
    assert sent["task"] == prepared["task"]
    assert "task" not in sent["raw_annotation"]
    assert not {"data", "propagation", "doe", "previous_review"} & sent.keys()
    prepared["declaration_index"][0]["resolved_target"]["ref"]["index"] = 99
    with pytest.raises(ValueError):
        checked_review_material(prepared)


@pytest.mark.parametrize("normalized", [False, True])
def test_existing_task_objection_requires_matching_requirement_check(normalized):
    prepared = goal_material()
    response = task_issue(prepared)
    requirement = prepared["task"]["requirements"][0]["id"]
    response["findings"][0]["task_objection"].update(
        code="unsupported_requirement", requirement_ids=[requirement])
    with pytest.raises(ValueError, match="linked issue checks"):
        validate_response(response, prepared)
    for row in response["requirement_checks"]:
        if row["requirement_id"] == requirement:
            row.update(status="issue", finding_indexes=[0])
    accepted = validate_response(response, prepared)
    if normalized:
        response = accepted.model_dump(mode="json")
    for row in response["requirement_checks"]:
        if row["requirement_id"] == requirement:
            row.update(status="accepted")
            row["finding_ids" if normalized else "finding_indexes"] = []
    with pytest.raises(ValueError, match="linked issue checks"):
        validate_response(response, prepared, normalized=normalized)
