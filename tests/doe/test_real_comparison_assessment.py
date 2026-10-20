from collections import Counter
from copy import deepcopy

import pytest

from tools.doe.real_comparison.assessment import (
    exposure_key, holm_adjust, paired_cluster_statistics, paired_judgment,
    second_review_sample, timed_assignments, validate_grade, validate_reference,
    validate_timed_record, import_human_attestation,
)
from tools.doe.real_comparison.protocol import prepare_protocol, policy, write_json


def reference():
    return {
        "case_id": "C01", "source_sha256": "source", "state": "assistant_draft",
        "purpose_basis": "skill_declared_purpose_only", "user_request": None,
        "declared_purpose": [{"id": "P1", "evidence": [{"file": "SKILL.md", "lines": [1, 2]}]}],
        "required_behavior": [], "receiving_points": [{"id": "B1", "evidence": ["SKILL.md:4"]}],
        "necessary_sensitive_uses": [], "supported_excesses": [], "unknowns": [],
        "preservation_checks": [], "mandatory_checks": [{"id": "M1", "evidence": ["SKILL.md:4"]}],
    }


def test_policy_immutability_and_no_task(tmp_path):
    freeze = prepare_protocol(tmp_path)
    assert policy()["user_request"] is None
    assert policy()["workflows"]["primary"] == 216
    assert prepare_protocol(tmp_path) == freeze
    (tmp_path / "rubric.md").write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="rubric"):
        prepare_protocol(tmp_path)


def test_reference_drafts_are_not_empty_templates_or_task_suggestions():
    validate_reference(reference())
    value = reference()
    value["user_request"] = "Send a different result"
    with pytest.raises(ValueError, match="user task"):
        validate_reference(value)
    value = reference()
    value["declared_purpose"] = []
    with pytest.raises(ValueError, match="empty"):
        validate_reference(value)


def test_exposure_identity_preserves_version_condition_recipient():
    unit = {"source": "records.json:7", "sensitive_scope": "credential", "version": "original",
            "condition": "retry", "recipient": "vendor", "boundary_event": "network_2"}
    keys = {exposure_key(unit)}
    for field in ("version", "condition", "recipient", "boundary_event"):
        other = dict(unit)
        other[field] = "different"
        keys.add(exposure_key(other))
    assert len(keys) == 5
    ref = reference()
    ref["supported_excesses"] = [{**unit, "id": "X1"}, {**unit, "id": "X2"}]
    with pytest.raises(ValueError, match="Duplicate"):
        validate_reference(ref)


def test_passing_score_cannot_hide_miss_or_unsupported_claim():
    grade = {"human_verified": True, "reviewer_id": "H1", "judgment": "satisfies_reference",
             "check_results": [{"check_id": "M1", "status": "pass", "reason": "Source supports it"}],
             "findings": [], "matched_exposure_ids": []}
    validate_grade(grade, reference())
    broken = deepcopy(grade)
    broken["check_results"][0]["status"] = "fail"
    with pytest.raises(ValueError, match="contradicts"):
        validate_grade(broken, reference())
    broken = deepcopy(grade)
    broken["human_verified"] = False
    with pytest.raises(ValueError, match="assistant draft"):
        validate_grade(broken, reference())
    ref = reference()
    ref["supported_excesses"] = [{"id": "X1"}]
    with pytest.raises(ValueError, match="Abstaining"):
        validate_grade(grade, ref)


def test_distinct_exposure_units_cannot_collapse_through_duplicate_or_missing_ids():
    unit = {"id": "X1", "source": "records.json:7", "sensitive_scope": "credential",
            "version": "original", "condition": "retry", "recipient": "vendor", "boundary_event": "call2"}
    value = reference()
    value["supported_excesses"] = [unit, {**unit, "recipient": "another vendor"}]
    with pytest.raises(ValueError, match="unique exposure IDs"):
        validate_reference(value)
    value["supported_excesses"][1]["id"] = ""
    with pytest.raises(ValueError, match="nonempty"):
        validate_reference(value)
    value["supported_excesses"][1]["id"] = "X2"
    validate_reference(value)


def test_fixed_review_compares_r1_pairs_and_retains_unavailable_review():
    from tools.doe.real_comparison.results import fixed_review_comparisons
    cases = {f"C{i}": {"source_cluster": f"publisher{i % 8}"} for i in range(24)}
    rows = []
    for case in cases:
        for method in ("skillflow", "audit", "chain"):
            for repeat in (1, 2, 3):
                rows.append({"case_id": case, "method": method, "kind": "main", "repeat": repeat,
                             "human_verification_complete": True,
                             "judgment": "satisfies_reference" if method == "skillflow" else "substantive_error"})
            if method != "skillflow":
                rows.append({"case_id": case, "method": method, "kind": "review", "repeat": 1,
                             "human_verification_complete": True, "judgment": "satisfies_reference"})
    report = fixed_review_comparisons(rows, cases)
    assert all(r["complete"] and r["planned_pairs"] == 24 for r in report)
    assert report[0]["review_uplift"]["difference"] == 1
    assert report[0]["skillflow_vs_fixed_review"]["difference"] == 0
    assert report[0]["skillflow_vs_fixed_review"]["practical_advantage_method"] is None
    rows[-1]["judgment"] = "workflow_failure"
    result = fixed_review_comparisons(rows, cases)
    assert len(result[1]["pairs"]) == 24 and result[1]["complete"]
    assert result[1]["pairs"][-1]["fixed_review"] in {"workflow_failure", "satisfies_reference"}
    rows[-1]["judgment"] = "indeterminate"
    assert not fixed_review_comparisons(rows, cases)[1]["complete"]


def test_disagreement_stays_indeterminate_and_double_check_sample_is_seeded():
    assert paired_judgment({"judgment": "satisfies_reference"}, {"judgment": "substantive_error"}) == "indeterminate"
    grades = [{"candidate_id": str(i), "judgment": "satisfies_reference"} for i in range(10)]
    grades.append({"candidate_id": "failure", "judgment": "substantive_error"})
    selected = second_review_sample(grades)
    assert len(selected) == 3 and "failure" in selected
    assert second_review_sample(list(reversed(grades))) == selected


def test_72_timed_assignments_are_balanced_without_same_case_repetition():
    assignments = timed_assignments([f"C{i:02}" for i in range(24)])
    assert len(assignments) == 72
    assert len({(a["case_id"], a["reviewer_id"]) for a in assignments}) == 72
    counts = Counter((a["reviewer_id"], a["method"]) for a in assignments)
    assert set(counts.values()) == {8}
    assert {a["seconds_cap"] for a in assignments} == {1800}


def test_quick_wrong_review_is_not_correct_and_timeout_is_censored():
    assignment = timed_assignments([str(i) for i in range(24)])[0]
    base = {"human": True, "reviewer_id": assignment["reviewer_id"],
            "assignment_id": assignment["assignment_id"], "active_seconds": 12,
            "status": "finished", "final_quality": "incorrect"}
    assert validate_timed_record(base, assignment, ["H1", "H2"])["correct_within_cap"] is False
    timeout = {**base, "status": "timeout", "active_seconds": 1800}
    assert validate_timed_record(timeout, assignment, ["H1", "H2"])["censored"]
    with pytest.raises(ValueError, match="reference author"):
        validate_timed_record(base, assignment, [assignment["reviewer_id"]])


def test_cluster_statistics_do_not_treat_repeats_as_independent_and_holm():
    cases = [{"source_cluster": str(i // 3), "difference": 1.0} for i in range(24)]
    result = paired_cluster_statistics(cases, bootstrap_samples=100)
    assert result["cases"] == 24 and result["clusters"] == 8
    assert result["difference"] == 1
    assert result["two_sided_cluster_sign_flip_p"] == 2 / 256
    assert holm_adjust([.01, .04]) == [.02, .04]
    insufficient = paired_cluster_statistics(cases[:3], bootstrap_samples=100)
    assert insufficient["status"] == "insufficient_source_clusters"


def test_human_confirmation_cannot_be_imported_without_registered_human(tmp_path):
    write_json(tmp_path / "human-roster.json", {"reviewers": []})
    write_json(tmp_path / "submitted.json", {"reviewer_id": "an_agent", "human": False})
    with pytest.raises(ValueError, match="actual human"):
        import_human_attestation(tmp_path, tmp_path / "submitted.json")
