"""Joint semantic review reuses exact spans without turning references into proof."""
from copy import deepcopy

import pytest

from skillflow.common.semantic_failure import SemanticFailure
from tests.propagation.annotation.helpers import prepare_material
from skillflow.propagation.review.material import prepare_review_material, resolve_targets
from skillflow.propagation.review.report import display_model, render_html, render_markdown
from skillflow.propagation.review.services import validate_response
from skillflow.propagation.review.prompts import INSTRUCTIONS
from tests.propagation.annotation.helpers import material, valid_raw_response
from tests.propagation.review.test_core import one_issue, cannot_assess


def joint_material():
    base = material()
    enriched = prepare_material(base["source"], base["cfg"],
        user_request="Return the selected value.\r\nDo not include credentials.\r\n")
    return prepare_review_material(enriched, valid_raw_response(enriched))


@pytest.mark.parametrize("file,first,last", [
    ("skill/SKILL.md", 3, 4), ("task/user-request.txt", 1, 2)])
def test_finding_and_failure_accept_the_same_source_spans(file, first, last):
    prepared = joint_material()
    evidence = {"file": file, "start_line": first, "end_line": last,
                "reason": "The span supports checking this claim; it does not prove the interpretation."}
    response = one_issue(prepared)
    response["findings"][0]["evidences"] = [evidence]
    checked = validate_response(response, prepared)
    assert checked.findings[0].evidences[0].model_dump() == evidence
    failure = cannot_assess(prepared)
    failure["failure"]["evidences"] = [evidence]
    with pytest.raises(SemanticFailure) as error:
        validate_response(failure, prepared)
    assert error.value.failure["evidences"] == [evidence]


@pytest.mark.parametrize("change", [
    {"file": "policy/absent.txt"}, {"start_line": True}, {"start_line": 0},
    {"start_line": 2, "end_line": 1}, {"end_line": 999}, {"quote": "forged"},
    {"basis": "source"}, {"ref_id": "src_001"}])
def test_invalid_span_or_mixed_evidence_shapes_fail_both_branches(change):
    prepared = joint_material()
    evidence = {"file": "task/user-request.txt", "start_line": 1, "end_line": 1,
                "reason": "An unverified semantic claim."} | change
    response = one_issue(prepared)
    response["findings"][0]["evidences"] = [evidence]
    failure = cannot_assess(prepared)
    failure["failure"]["evidences"] = [evidence]
    for value in (response, failure):
        with pytest.raises(ValueError) as error:
            validate_response(value, prepared)
        assert not isinstance(error.value, SemanticFailure)


def test_global_claims_and_missing_declarations_have_parent_targets_without_fake_ir():
    prepared = joint_material()
    for kind, pointer in (("task", ""), ("task", "/purpose"), ("task", "/requirements"),
                          ("annotation", "/demands"), ("annotation", "/expressions")):
        target = next(t for t in prepared["target_index"] if t["pointer"] == pointer and t["kind"] == kind)
        resolved = resolve_targets([target["id"]], prepared)[0]
        assert resolved["instruction_ids"] == []
    target = next(t for t in prepared["target_index"] if t["pointer"] == "/ir_semantics/ir_read/sensitivity")
    assert resolve_targets([target["id"]], prepared)[0]["instruction_ids"] == ["ir_read"]


def test_span_display_shares_exact_excerpt_and_does_not_upgrade_wrong_interpretation():
    prepared = joint_material()
    raw = one_issue(prepared)
    raw["findings"][0]["explanation"] = "Deliberately unsupported interpretation for reference-validation testing."
    raw["findings"][0]["evidences"] = [{"file": "task/user-request.txt", "start_line": 1, "end_line": 2,
                                       "reason": "A true span can accompany a wrong interpretation."}]
    response = validate_response(raw, prepared)
    result = {"status": "complete", "summary": "issues_found", "reason": "References validated.",
              "review": response.model_dump(mode="json")}
    before = deepcopy((result, prepared))
    model = display_model(result, prepared)
    assert model["findings"][0]["evidence_display"][0]["excerpt"] == prepared["user_request"]
    for output in (render_html(model), render_markdown(model)):
        assert "task/user-request.txt:1" in output.replace("\\", "")
        assert "Return the selected value" in output
        assert "does not prove" in output
    assert (result, prepared) == before


def test_prompt_reviews_joint_semantics_without_final_doe_or_minimality_verdict():
    for boundary in ("Source checks", "Requirement checks", "Goal checks", "IR checks",
                     "Current payload", "indispensability", "start_line", "task/", "English"):
        assert boundary in INSTRUCTIONS
    assert "Do not generate replacement annotations" in INSTRUCTIONS
    assert "not automatically task requirements" in INSTRUCTIONS
    assert "A valid range" in INSTRUCTIONS
    assert "per-IR necessity" in INSTRUCTIONS
