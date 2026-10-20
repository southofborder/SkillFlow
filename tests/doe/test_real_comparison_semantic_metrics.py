"""Synthetic engineering fixtures only; no target calls or human approvals."""
from copy import deepcopy

import pytest

from tools.doe.real_comparison.assessment import validate_grade
from tools.doe.real_comparison.semantic_metrics import (
    GRADING_SCHEMA_VERSION, aggregate_semantic_metrics, grading_template,
    reconcile_semantic_grades, validate_grade_evidence, validate_semantic_grade,
)


def evidence():
    # Genuine multilingual quotations must remain unchanged in new English records.
    return {"reason": "The exact source and candidate distinguish this exposure.",
            "source_evidence": [{"path": "SKILL.md", "start_line": 1, "end_line": 1,
                                 "quote": "Preserve summary. 原文引用"}],
            "candidate_evidence": [{"start_line": 1, "end_line": 1,
                                    "quote": "Keep the summary. 原文引用"}]}


def unit(identifier="X1", recipient="service"):
    return {"id": identifier, "source": "records.json:1", "sensitive_scope": "credential",
            "version": "original", "condition": "retry", "recipient": recipient,
            "boundary_event": "delivery"}


def reference(*, positives=True):
    return {"grading_schema_version": GRADING_SCHEMA_VERSION,
            "supported_excesses": [unit()] if positives else [],
            "receiving_points": [{"id": "B1"}], "mandatory_checks": [{"id": "M1"}]}


def claim(*, identifier="C1", status="supported", ref="X1", recipient="service"):
    return {**{k: v for k, v in unit(recipient=recipient).items() if k != "id"},
            "claim_id": identifier, "assessment": status,
            "matched_reference_ids": [ref] if ref else [], **evidence()}


def grade(ref=None, *, method="audit", supported=True):
    ref = ref or reference()
    result = {"human_verified": True, "reviewer_id": "fictional-verifier",
              "judgment": "satisfies_reference" if supported else "substantive_error",
              "check_results": [{"check_id": "M1", "status": "pass" if supported else "fail",
                                 "reason": "Synthetic source comparison."}],
              "matched_exposure_ids": [u["id"] for u in ref["supported_excesses"]] if supported else [],
              "findings": [], **grading_template(ref, method)}
    result["claim_units"] = [claim(ref=u["id"], identifier="C" + str(i), recipient=u["recipient"])
                             for i, u in enumerate(ref["supported_excesses"])] if supported else []
    for item in result["receiving_point_coverage"]:
        item.update(status="covered" if supported else "missed", **evidence())
    for item in result["reduction_assessments"]:
        item.update(status="adequate" if supported else "missing", **evidence())
    if result["chain_assessment"]:
        for records in result["chain_assessment"].values():
            for item in records:
                item.update(status="pass", **evidence())
    return result


def row(case="A", *, repeat=1, assessment=None, method="audit", judgment=None):
    return {"case_id": case, "source_cluster": "source-" + case, "method": method,
            "kind": "main", "repeat": repeat, "adjudicated_grade": assessment,
            "judgment": judgment or (assessment["judgment"] if assessment else "workflow_failure")}


def test_source_strata_keep_necessary_use_and_true_uncertainty_separate():
    from tools.doe.real_comparison.semantic_metrics import stratified_check_metrics
    ref = reference()
    ref["mandatory_checks"] = [{"id": "M1", "stratum": "necessary_sensitive_use"},
                               {"id": "M2", "stratum": "source_uncertainty"}]
    checked = {"check_results": [{"check_id": "M1", "status": "pass"}, {"check_id": "M2", "status": "fail"}]}
    rows = [row(repeat=i, assessment={**checked, "judgment": "substantive_error"}) for i in (1, 2, 3)]
    result = stratified_check_metrics(rows, {"A": ref})
    necessary = next(g for g in result["groups"] if g["stratum"] == "necessary_sensitive_use")
    uncertainty = next(g for g in result["groups"] if g["stratum"] == "source_uncertainty")
    absent = next(g for g in result["groups"] if g["stratum"] == "unnecessary_action_exposure")
    assert necessary["case_averaged_check_pass_fraction"] == 1
    assert uncertainty["case_averaged_check_pass_fraction"] == 0
    assert absent["case_averaged_check_pass_fraction"] is None and absent["source_eligible_cases"] == 0
    rows[0]["adjudicated_grade"] = None
    assert next(g for g in stratified_check_metrics(rows, {"A": ref})["groups"]
                if g["stratum"] == "necessary_sensitive_use")["case_averaged_check_pass_fraction"] is None


def test_v2_requires_grader_fields_while_unversioned_legacy_fixture_remains_compatible():
    current = grade()
    validate_grade(current, reference(), method="audit")
    legacy = {k: current[k] for k in ("human_verified", "reviewer_id", "judgment", "check_results", "matched_exposure_ids", "findings")}
    with pytest.raises(ValueError, match="schema v2"):
        validate_grade(legacy, reference(), method="audit")
    old_ref = {k: v for k, v in reference().items() if k != "grading_schema_version"}
    validate_grade(legacy, old_ref)


@pytest.mark.parametrize("field", ["source", "sensitive_scope", "version", "condition", "recipient", "boundary_event"])
def test_claim_units_keep_each_material_dimension(field):
    current = grade()
    current["claim_units"][0][field] = ""
    with pytest.raises(ValueError, match="six material"):
        validate_semantic_grade(current, reference(), method="audit")


def test_broad_or_duplicate_claims_cannot_inflate_unit_credit():
    ref = reference()
    ref["supported_excesses"].append(unit("X2", "other-service"))
    current = grade(ref)
    current["claim_units"] = [claim()]
    current["claim_units"][0]["matched_reference_ids"] = ["X1", "X2"]
    with pytest.raises(ValueError, match="broad claims"):
        validate_semantic_grade(current, ref)
    current = grade()
    current["claim_units"].append({**deepcopy(current["claim_units"][0]), "claim_id": "C2"})
    with pytest.raises(ValueError, match="Duplicate normalized"):
        validate_semantic_grade(current, reference())


def test_duplicate_reference_receiver_ids_cannot_shrink_coverage_denominator():
    ref = reference()
    ref["receiving_points"].append({"id": "B1"})
    with pytest.raises(ValueError, match="unique identities"):
        grading_template(ref, "audit")


def test_every_receiver_and_reduction_requires_an_explicit_human_assessment():
    for field in ("receiving_point_coverage", "reduction_assessments"):
        current = grade()
        current[field] = []
        with pytest.raises(ValueError, match="every"):
            validate_semantic_grade(current, reference())


def test_unsupported_and_functionality_breaking_claims_cannot_receive_primary_pass():
    current = grade()
    current["claim_units"].append(claim(identifier="false", status="unsupported", ref=None, recipient="invented-service"))
    with pytest.raises(ValueError, match="passing primary"):
        validate_semantic_grade(current, reference())
    current = grade()
    current["error_records"] = [{"error_id": "E1", "category": "harmful_reduction", "severity": "minor",
                                 "functionality_impact": "breaks_required_behavior", **evidence()}]
    with pytest.raises(ValueError, match="passing primary"):
        validate_semantic_grade(current, reference())


def test_chain_secondary_failure_does_not_change_common_primary_judgment():
    current = grade(method="chain")
    current["chain_assessment"]["completeness"][0]["status"] = "fail"
    validate_grade(current, reference(), method="chain")
    with pytest.raises(ValueError, match="does not have a chain"):
        validate_semantic_grade(current, reference(), method="audit")
    current["chain_assessment"] = None
    with pytest.raises(ValueError, match="require separate chain"):
        validate_semantic_grade(current, reference(), method="skillflow")


def test_exact_multilingual_evidence_is_preserved_and_checked_against_frozen_bytes(tmp_path):
    (tmp_path / "SKILL.md").write_text("Preserve summary. 原文引用\n", encoding="utf-8")
    current = grade()
    validate_grade_evidence(current, source_root=tmp_path, candidate_text="Keep the summary. 原文引用\n")
    assert current["claim_units"][0]["source_evidence"][0]["quote"] == "Preserve summary. 原文引用"
    bad = deepcopy(current)
    bad["claim_units"][0]["candidate_evidence"][0]["end_line"] = 50
    with pytest.raises(ValueError, match="candidate quotation"):
        validate_grade_evidence(bad, source_root=tmp_path, candidate_text="Keep the summary. 原文引用\n")
    with pytest.raises(ValueError, match="candidate quotation"):
        validate_grade_evidence(current, source_root=tmp_path, candidate_text="Different candidate")


def test_source_evidence_cannot_escape_frozen_source():
    current = grade()
    current["claim_units"][0]["source_evidence"][0]["path"] = "../other.md"
    with pytest.raises(ValueError, match="relative frozen-source"):
        validate_semantic_grade(current, reference())


def test_case_means_precede_method_means_and_empty_claim_precision_is_undefined():
    hit, miss = grade(), grade(supported=False)
    rows = [row("A", repeat=i, assessment=hit if i == 1 else miss) for i in (1, 2, 3)]
    rows += [row("B", repeat=i, assessment=hit) for i in (1, 2, 3)]
    output = aggregate_semantic_metrics(rows, {"A": reference(), "B": reference()})
    summary = output["groups"]["audit/main"]
    assert summary["planned_workflows"] == 6 and summary["source_positive_units"] == 2
    assert summary["source_positive_cases"] == 2 and summary["source_clusters"] == 2
    assert summary["case_averaged"]["recall"] == pytest.approx(2 / 3)
    assert summary["case_averaged"]["precision"] is None
    assert output["rows"][1]["precision"] is None and output["rows"][1]["fn"] == 1


def test_nonpositive_case_and_empty_output_do_not_receive_perfect_precision():
    ref = reference(positives=False)
    current = grade(ref)
    output = aggregate_semantic_metrics([row(assessment=current)], {"A": ref})
    result = output["groups"]["audit/main"]
    assert result["source_positive_cases"] == 0 and result["source_positive_units"] == 0
    assert result["case_averaged"]["precision"] is None and result["case_averaged"]["recall"] is None


def test_recall_denominator_is_source_positive_cases_and_unsupported_claims_still_count_on_negative_cases():
    positive, negative = reference(), reference(positives=False)
    negative_grade = grade(negative)
    negative_grade["judgment"] = "substantive_error"
    negative_grade["claim_units"] = [claim(status="unsupported", ref=None)]
    result = aggregate_semantic_metrics([row("A", assessment=grade()), row("B", assessment=negative_grade)],
                                        {"A": positive, "B": negative})["groups"]["audit/main"]
    assert result["source_positive_cases"] == 1
    assert result["case_averaged"]["recall"] == 1 and result["case_averaged"]["fp"] == .5


def test_supported_mapping_cannot_change_a_canonical_reference_dimension():
    current = grade()
    current["claim_units"][0]["condition"] = "always"
    with pytest.raises(ValueError, match="canonical reference"):
        validate_semantic_grade(current, reference())


def test_reduction_exemption_requires_explicit_reference_fact():
    ref = reference()
    current = grade(ref)
    current["reduction_assessments"][0]["status"] = "not_established_reducible"
    with pytest.raises(ValueError, match="exemption"):
        validate_semantic_grade(current, ref)
    ref["supported_excesses"][0]["reduction_required"] = False
    validate_semantic_grade(current, ref)
    result = aggregate_semantic_metrics([row(assessment=current)], {"A": ref})["groups"]["audit/main"]
    assert result["source_reducible_units"] == 0 and result["case_averaged"]["reduction_coverage"] is None


def test_unassessed_planned_failure_keeps_full_denominator_and_unknown_rates():
    output = aggregate_semantic_metrics([row(repeat=1, assessment=grade()), row(repeat=2)], {"A": reference()})
    result = output["groups"]["audit/main"]
    assert result["planned_workflows"] == 2 and result["assessed_workflows"] == 1
    assert result["case_averaged"]["tp"] is None and result["case_averaged"]["receiving_point_coverage"] is None


def test_false_claim_and_functionality_error_counts_are_separate_from_matches():
    current = grade()
    current["judgment"] = "substantive_error"
    current["claim_units"].append(claim(identifier="false", status="unsupported", ref=None, recipient="invented-service"))
    current["error_records"] = [{"error_id": "E1", "category": "harmful_reduction", "severity": "substantive",
                                 "functionality_impact": "breaks_required_behavior", **evidence()}]
    output = aggregate_semantic_metrics([row(assessment=current)], {"A": reference()})
    result = output["groups"]["audit/main"]["case_averaged"]
    assert (result["tp"], result["fn"], result["fp"], result["precision"]) == (1, 0, 1, .5)
    assert result["functionality_errors"] == 1 and result["substantive_errors"] == 1


def test_disputed_claim_mapping_is_not_forced_to_a_miss_or_false_positive():
    current = grade(supported=False)
    current["claim_units"] = [claim(status="disputed")]
    output = aggregate_semantic_metrics([row(assessment=current)], {"A": reference()})
    result = output["groups"]["audit/main"]
    assert result["unresolved_workflows"] == 1
    assert all(result["case_averaged"][field] is None for field in ("tp", "fn", "fp", "precision", "recall"))


def test_same_coarse_error_with_different_unit_mappings_remains_a_metric_dispute():
    primary, secondary = grade(supported=False), grade(supported=False)
    primary["claim_units"] = [claim(identifier="extra", status="unsupported", ref=None)]
    secondary["claim_units"] = [claim(identifier="other", status="unsupported", ref=None, recipient="another-recipient")]
    result = reconcile_semantic_grades(primary, secondary)
    assert result["adjudicated_grade"] is None and result["metric_disputes"] == ["claim_units"]
    secondary = deepcopy(primary)
    secondary["claim_units"][0]["reason"] = "Different English wording for the same normalized claim."
    assert reconcile_semantic_grades(primary, secondary)["adjudicated_grade"] is primary


def test_unsupported_claim_stability_detects_churn_that_matched_reference_sets_miss():
    rows = []
    for repeat, recipient in enumerate(("service-a", "service-a", "service-b"), 1):
        current = grade(supported=False)
        current["claim_units"] = [claim(status="unsupported", ref=None, recipient=recipient)]
        rows.append(row(repeat=repeat, assessment=current))
    result = aggregate_semantic_metrics(rows, {"A": reference()})
    assert result["unsupported_claim_stability"][0]["unsupported_claim_jaccard"] == pytest.approx(1 / 3)


def test_duplicate_repetition_is_rejected_and_source_clusters_remain_explicit():
    current = row(assessment=grade())
    with pytest.raises(ValueError, match="Duplicate planned repetitions"):
        aggregate_semantic_metrics([current, current], {"A": reference()})
    result = aggregate_semantic_metrics([current], {"A": reference()})
    assert result["case_means"][0]["source_cluster"] == "source-A"
    assert result["model_calls"] == 0 and "Descriptive secondary" in result["interpretation"]
