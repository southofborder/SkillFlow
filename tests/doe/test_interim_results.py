"""Synthetic dispute-gating checks; never read a research packet."""
from copy import deepcopy

from tools.doe.real_comparison.interim_results import reconcile
from tools.doe.real_comparison.semantic_metrics import GRADING_SCHEMA_VERSION


def grade():
    return {"grading_schema_version": GRADING_SCHEMA_VERSION,
            "judgment": "satisfies_reference", "reference_correction_proposals": [],
            "check_results": [{"check_id": "one", "status": "pass"}],
            "claim_units": [], "receiving_point_coverage": [],
            "reduction_assessments": [], "error_records": [], "findings": [],
            "chain_assessment": None}


def test_matching_fresh_recheck_preserves_pass():
    primary = grade()
    result = reconcile(primary, deepcopy(primary), required=True)
    assert result["judgment"] == "satisfies_reference"
    assert result["disputes"] == []


def test_missing_mandatory_recheck_remains_unknown():
    result = reconcile(grade(), required=True)
    assert result["judgment"] == "indeterminate"
    assert "mandatory_independent_recheck_missing" in result["disputes"]


def test_agreeing_coarse_failure_does_not_erase_check_dispute():
    primary = grade()
    primary["judgment"] = "substantive_error"
    secondary = deepcopy(primary)
    secondary["check_results"][0]["status"] = "fail"
    result = reconcile(primary, secondary, required=True)
    assert result["judgment"] == "indeterminate"
    assert "mandatory_check_disagreement" in result["disputes"]


def test_reference_proposal_is_not_automatically_new_gold():
    primary = grade()
    primary.update(judgment="indeterminate", reference_correction_proposals=[{"reason": "Synthetic source conflict"}])
    result = reconcile(primary, deepcopy(primary), required=True)
    assert result["adjudicated_grade"] is None
    assert "source_reference_correction_proposed" in result["disputes"]


def test_receiver_classification_disagreement_blocks_metric():
    primary = grade()
    primary["receiving_point_coverage"] = [{"receiving_point_id": "receiver", "status": "covered"}]
    secondary = deepcopy(primary)
    secondary["receiving_point_coverage"][0]["status"] = "missed"
    result = reconcile(primary, secondary, required=True)
    assert result["judgment"] == "indeterminate"
    assert "receiving_point_coverage" in result["disputes"]


def test_legacy_findings_disagreement_is_preserved():
    primary = grade()
    primary["judgment"] = "substantive_error"
    secondary = deepcopy(primary)
    secondary["findings"] = [{"category": "unsupported_excess", "severity": "substantive", "functionality_impact": "none"}]
    result = reconcile(primary, secondary, required=True)
    assert result["judgment"] == "indeterminate"
    assert "findings_classification_disagreement" in result["disputes"]
