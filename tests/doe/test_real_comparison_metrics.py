"""Human-cost arithmetic on fictional imports; zero model or real human work.

Full cohort closure/reference gates have independent integration coverage. These
unit fixtures mock only those outer prerequisites, preserving all local hashes,
roles, assignments, personal attestations and physical-source checks.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from tools.doe.real_comparison.metrics import human_cost_summary, cost_ledger
from tools.doe.real_comparison.protocol import sha256, write_json


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def imported(run, relative, manifest, record, **identity):
    path = run / relative
    write_json(path, record)
    entry = {"path": relative, "sha256": sha256(path), "reviewer_id": record["reviewer_id"],
             "import_source": "human_user_submission", **identity}
    current = read(run / manifest) if (run / manifest).exists() else {"records": []}
    current["records"].append(entry)
    write_json(run / manifest, current)
    return entry


@pytest.fixture
def humans(tmp_path, monkeypatch):
    run = tmp_path / "fictional-cost-records"
    write_json(run / "human-roster.json", {"reviewers": [
        {"reviewer_id": p, "human": True, "role": "reference_verifier"} for p in ("H1", "H2")]
        + [{"reviewer_id": p, "human": True, "role": "timed_reviewer"} for p in ("R1", "R2", "R3")]})
    source = run / "cases/case-01/source/SKILL.md"
    source.parent.mkdir(parents=True)
    source.write_text("Return the approved summary.\nThe caller is unspecified.\n", encoding="utf-8")
    evidence = [{"path": "SKILL.md", "start_line": 1, "end_line": 1, "quote": "Return the approved summary."}]
    reference = {"case_id": "case-01", "source_sha256": "fictional-source", "state": "approved",
                 "coverage_state": "complete_for_human_verification", "purpose_basis": "skill_declared_purpose_only", "user_request": None,
                 "declared_purpose": [{"id": "P1", "evidence": evidence}], "required_behavior": [],
                 "receiving_points": [{"id": "B1", "evidence": evidence}], "necessary_sensitive_uses": [],
                 "supported_excesses": [], "unknowns": [], "preservation_checks": [],
                 "mandatory_checks": [{"id": "M1", "evidence": evidence}]}
    write_json(run / "references/case-01.json", reference)
    # The local cost checks below remain real. Only complete-study prerequisites
    # are mocked to avoid fabricating a full human-scored 264-result experiment.
    monkeypatch.setattr("tools.doe.real_comparison.results.verify_output_freeze", lambda *_: {})
    monkeypatch.setattr("tools.doe.real_comparison.assessment.verify_human_reference_freeze", lambda *_: {})
    return run


def confirm(run, person, seconds=None):
    record = {"reviewer_id": person, "case_id": "case-01", "human": True, "approved": True,
              "role": "reference_verifier", "source_sha256": "fictional-source", "reference_sha256": sha256(run / "references/case-01.json"),
              "attestation_id": "fictional-" + person, "attested_at": "2026-10-20T00:00:00+00:00",
              "confirmation": "I personally verified this source reference."}
    if seconds is not None:
        record["active_seconds"] = seconds
    return imported(run, f"approvals/submissions/{person}.json", "approvals/import-manifest.json", record, case_id="case-01")


def score(run, *, person="H1", role="primary", seconds=None, judgment="substantive_error"):
    identifier = "case-01_audit_r1"
    write_json(run / "review/private-scoring-map.json", {"assignments": [{"candidate_id": "anonymous", "case_id": "case-01",
               "workflow_id": identifier, "primary_reviewer_id": "H1"}]})
    write_json(run / "workflows" / identifier / "result.json", {"status": "failed", "answer_sha256": None})
    record = {"candidate_id": "anonymous", "workflow_id": identifier, "reviewer_id": person, "scoring_role": role,
              "human_verified": True, "submission_id": "fictional-" + role, "attested_at": "2026-10-20T00:00:00+00:00",
              "confirmation": "I personally checked this candidate against the source reference.", "reference_sha256": sha256(run / "references/case-01.json"),
              "candidate_sha256": None, "judgment": judgment, "check_results": [{"check_id": "M1", "status": "fail" if judgment == "substantive_error" else "pass", "reason": "Fictional source-based judgment."}],
              "matched_exposure_ids": [], "findings": []}
    if seconds is not None:
        record["active_seconds"] = seconds
    return imported(run, f"grades/{role}.json", "grades/import-manifest.json", record, workflow_id=identifier, scoring_role=role)


def timed(run, identifier, person, method, status, seconds):
    manifest = run / "review/private-assignment-map.json"
    assignments = read(manifest)["assignments"] if manifest.exists() else []
    assignments.append({"assignment_id": identifier, "case_id": "case-01", "reviewer_id": person, "method": method, "repeat": 1, "seconds_cap": 1800})
    write_json(manifest, {"assignments": assignments})
    record = {"assignment_id": identifier, "case_id": "case-01", "reviewer_id": person, "human": True,
              "status": status, "started_at": "2026-10-20T00:00:00+00:00", "finished_at": "2026-10-20T00:30:00+00:00",
              "final_quality": "pending_independent_adjudication", "corrected_conclusion": "Fictional conclusion.",
              "attestation": "I personally performed this timed review without consulting this case reference or another method answer."}
    if seconds is not None:
        record["active_seconds"] = seconds
    return imported(run, f"review/submissions/{identifier}.json", "review/import-manifest.json", record, assignment_id=identifier)


def adjudicate(run, identifier, quality, *, seconds=None):
    original = next(r for r in read(run / "review/import-manifest.json")["records"] if r["assignment_id"] == identifier)
    record = {"assignment_id": identifier, "reviewer_id": "H1", "submission_sha256": original["sha256"], "quality": quality,
              "human_verified": True, "attested_at": "2026-10-20T01:00:00+00:00", "evidence": ["SKILL.md:1"], "reason": "Fictional independent source judgment."}
    if seconds is not None:
        record["active_seconds"] = seconds
    return imported(run, f"review/adjudications/{identifier}.json", "review/adjudications/import-manifest.json", record, assignment_id=identifier)


def test_no_human_records_means_unknown_time_not_zero(tmp_path):
    result = human_cost_summary(tmp_path)
    assert result["status"] == "awaiting_actual_human_records"
    assert result["source_reference_work"]["planned_records"] == 60
    assert result["scoring_primary"]["planned_records"] == 264
    assert result["scoring_secondary"]["planned_records"] is None
    assert result["practical_timed_review"]["planned_records"] == 72
    assert result["observed_active_seconds_subtotal"] is None
    assert result["planned_record_time_seconds"] is None and result["currency"] is None


def test_reference_and_score_work_separate_known_subtotals_from_unknown_totals(humans):
    confirm(humans, "H1", 120)
    confirm(humans, "H2")
    score(humans, seconds=30)
    score(humans, person="H2", role="secondary")
    result = human_cost_summary(humans)
    refs = result["source_reference_work"]
    assert refs["observed_records"] == 2 and refs["covered_planned_units"] == 2
    assert refs["unknown_duration_records"] == 1 and refs["observed_active_seconds_subtotal"] == 120
    assert refs["reported_record_time_seconds"] is None and refs["planned_record_time_seconds"] is None
    assert result["scoring_primary"]["observed_active_seconds_subtotal"] == 30
    assert result["scoring_secondary"]["observed_records"] == 1
    assert result["scoring_secondary"]["required_so_far"] == 1 and result["scoring_secondary"]["subset_finalized"] is False
    assert result["observed_active_seconds_subtotal"] == 150
    assert result["planned_record_time_seconds"] is None and result["complete_study_human_time_seconds"] is None


def test_censored_and_quick_wrong_timed_work_never_becomes_successful_efficiency(humans):
    timed(humans, "quick", "R1", "audit", "finished", 5)
    timed(humans, "timeout", "R2", "chain", "timeout", 1800)
    timed(humans, "abandoned", "R3", "skillflow", "abandoned", 90)
    adjudicate(humans, "quick", "incorrect", seconds=20)
    adjudicate(humans, "timeout", "unresolved")
    adjudicate(humans, "abandoned", "correct")
    result = human_cost_summary(humans)
    practical = result["practical_timed_review"]
    rows = {r["assignment_id"]: r for r in practical["rows"]}
    assert rows["quick"]["correct_within_cap"] is False
    assert rows["timeout"]["right_censored"] is True and rows["timeout"]["active_seconds"] == 1800
    assert rows["abandoned"]["right_censored"] is True and rows["abandoned"]["active_seconds"] == 90
    assert rows["abandoned"]["completion_time_lower_bound_seconds"] == 90
    assert rows["abandoned"]["correct_within_cap"] is False
    assert practical["by_method"]["audit"]["correct_finished_active_seconds_median"] is None
    assert practical["by_method"]["chain"]["qualities"] == {"unresolved": 1}
    assert result["independent_timed_quality_adjudication"]["observed_records"] == 3
    assert result["independent_timed_quality_adjudication"]["unknown_duration_records"] == 2


def test_finished_correct_requires_manifested_independent_quality_and_known_time(humans):
    timed(humans, "known", "R1", "audit", "finished", 50)
    timed(humans, "unknown", "R2", "chain", "finished", None)
    adjudicate(humans, "known", "correct")
    adjudicate(humans, "unknown", "correct")
    write_json(humans / "review/adjudications/loose.json", {"quality": "correct"})
    result = human_cost_summary(humans)
    rows = {r["assignment_id"]: r for r in result["practical_timed_review"]["rows"]}
    assert rows["known"]["correct_within_cap"] is True
    assert rows["unknown"]["active_seconds"] is None and rows["unknown"]["correct_within_cap"] is None
    assert result["practical_timed_review"]["by_method"]["audit"]["correct_finished_active_seconds_median"] == 50
    assert result["unmanifested_adjudication_files"] == 1
    assert result["practical_timed_review"]["reported_record_time_seconds"] is None


def test_hash_and_actual_role_changes_fail_closed(humans):
    entry = confirm(humans, "H1", 20)
    path = humans / entry["path"]
    value = read(path)
    write_json(path, {**value, "active_seconds": 1})
    with pytest.raises(ValueError, match="changed"):
        human_cost_summary(humans)
    write_json(path, value)
    roster = read(humans / "human-roster.json")
    roster["reviewers"][0]["human"] = False
    write_json(humans / "human-roster.json", roster)
    with pytest.raises(ValueError, match="registered human role"):
        human_cost_summary(humans)


@pytest.mark.parametrize("value", [False, -1, float("nan"), float("inf"), "12"])
def test_invalid_optional_active_seconds_is_not_coerced_to_valid_work(humans, value):
    record = {"reviewer_id": "H1", "active_seconds": value}
    imported(humans, "approvals/submissions/invalid.json", "approvals/import-manifest.json", record, case_id="case-01")
    with pytest.raises(ValueError, match="finite nonnegative"):
        human_cost_summary(humans)


def test_cost_ledger_uses_human_records_without_estimated_rates_or_new_model_calls(humans):
    confirm(humans, "H1", 0)
    result = cost_ledger(humans)
    assert result["human_cost"]["source_reference_work"]["observed_active_seconds_subtotal"] == 0
    assert result["human_cost"]["status"] == "partial_human_records"
    assert result["model_calls"] == 0 and result["human_cost"]["model_calls"] == 0
    assert result["billing_amount"] is None and result["human_cost"]["currency"] is None
    assert result["target_usage"]["totals"]["total_tokens"] is None


def test_secondary_plan_finalizes_only_after_all264_primary_scores_and_retains_failures(humans):
    assignments, manifest = [], []
    for i in range(264):
        identifier = f"fictional_workflow_{i:03d}"
        candidate_id = f"anonymous_{i:03d}"
        assignments.append({"candidate_id": candidate_id, "case_id": "case-01", "workflow_id": identifier,
                            "primary_reviewer_id": "H1"})
        # These deliberately failed fixture workflows remain failures even if a
        # hypothetical primary human marks its limited content acceptable.
        write_json(humans / "workflows" / identifier / "result.json", {"status": "failed", "answer_sha256": None})
        record = {"candidate_id": candidate_id, "workflow_id": identifier, "reviewer_id": "H1", "scoring_role": "primary",
                  "human_verified": True, "submission_id": "fixture-" + identifier, "attested_at": "2026-10-20T00:00:00+00:00",
                  "confirmation": "I personally checked this candidate against the source reference.",
                  "reference_sha256": sha256(humans / "references/case-01.json"), "candidate_sha256": None,
                  "judgment": "satisfies_reference", "check_results": [{"check_id": "M1", "status": "pass", "reason": "Fictional limited-content judgment."}],
                  "matched_exposure_ids": [], "findings": []}
        path = humans / "grades" / (identifier + ".json")
        write_json(path, record)
        manifest.append({"path": path.relative_to(humans).as_posix(), "sha256": sha256(path), "reviewer_id": "H1",
                         "import_source": "human_user_submission", "workflow_id": identifier, "scoring_role": "primary"})
    write_json(humans / "review/private-scoring-map.json", {"assignments": assignments})
    write_json(humans / "grades/import-manifest.json", {"records": manifest})
    summary = human_cost_summary(humans)
    assert summary["scoring_primary"]["observed_records"] == 264
    assert summary["scoring_primary"]["unknown_duration_records"] == 264
    assert summary["scoring_secondary"]["subset_finalized"] is True
    assert summary["scoring_secondary"]["planned_records"] == 264
    assert summary["scoring_secondary"]["uncollected_planned_units"] == 264
    assert summary["observed_active_seconds_subtotal"] is None
