import pytest

from tools.doe.real_comparison.efficiency import efficiency_decision, efficiency_comparisons


def pairs():
    return [{"case_id": str(i), "source_cluster": str(i % 8), "adjudicated": True,
             "claimant_quality": .7 + (i % 8) * .03, "comparator_quality": .4,
             "claimant_cost": 50, "comparator_cost": 100} for i in range(24)]


def test_efficiency_needs_both_quality_and_resource_bounds():
    result = efficiency_decision(pairs(), bootstrap_samples=500)
    assert result["quality_noninferiority_supported"] and result["efficiency_supported"]
    assert result["resource_ratio_upper_bound"] == .5
    costly = [{**p, "claimant_cost": 90} for p in pairs()]
    assert not efficiency_decision(costly, bootstrap_samples=500)["efficiency_supported"]
    inferior = [{**p, "claimant_quality": .05 + (i % 8) * .01} for i, p in enumerate(pairs())]
    assert not efficiency_decision(inferior, bootstrap_samples=500)["quality_noninferiority_supported"]


@pytest.mark.parametrize("change, status", [
    ({"claimant_cost": None}, "unknown_cost_or_censored_review"),
    ({"censored": True}, "unknown_cost_or_censored_review"),
    ({"adjudicated": False}, "incomplete_or_unresolved_quality")])
def test_missing_cost_censoring_and_pending_humans_prevent_claim(change, status):
    observed = pairs()
    observed[0].update(change)
    result = efficiency_decision(observed, bootstrap_samples=50)
    assert result["status"] == status and not result["efficiency_supported"]


def test_equal_observed_quality_is_not_evidence_of_noninferiority():
    observed = [{**p, "claimant_quality": 1, "comparator_quality": 1} for p in pairs()]
    result = efficiency_decision(observed, bootstrap_samples=50)
    assert result["status"] == "degenerate_quality_interval_noninferiority_unestablished"
    assert not result["quality_noninferiority_supported"]
    assert not result["efficiency_supported"]


def test_all_planned_cases_and_clusters_required():
    assert not efficiency_decision(pairs()[:-1])["efficiency_supported"]
    observed = [{**p, "source_cluster": "one"} for p in pairs()]
    assert efficiency_decision(observed)["status"] == "insufficient_source_clusters"
    assert len(efficiency_comparisons({"rows": []}, {})["comparisons"]) == 20


def test_review_resource_includes_original_and_no_completed_subset():
    rows, work, enhanced = [], [], []
    for i in range(24):
        for method in ("skillflow", "audit", "chain"):
            for repeat in (1, 2, 3):
                key = f"{i}-{method}-{repeat}"
                rows.append({"workflow_id": key, "case_id": str(i), "method": method, "kind": "main", "repeat": repeat,
                             "source_cluster": str(i % 8), "human_verification_complete": True, "judgment": "satisfies_reference"})
                work.append({"workflow_id": key, "usage": {"totals": {"total_tokens": 100}}, "workflow_elapsed_seconds": 20})
            if method != "skillflow":
                key = f"{i}-{method}-review"
                rows.append({"workflow_id": key, "case_id": str(i), "method": method, "kind": "review", "repeat": 1,
                             "source_cluster": str(i % 8), "human_verification_complete": True, "judgment": "satisfies_reference"})
                enhanced.append({"workflow_id": key, "usage_original_plus_review": {"totals": {"total_tokens": 150}}, "additive_workflow_seconds": 30})
    result = efficiency_comparisons({"rows": rows}, {"workflows": work, "enhanced_original_plus_review_cost": enhanced})
    comparison = next(c for c in result["comparisons"] if c["methods"] == ["skillflow_r1", "audit+fixed_review"] and c["resource"] == "reported_total_tokens")
    assert comparison["resource_ratio"] == pytest.approx(2 / 3)
    assert not comparison["efficiency_supported"]  # equal quality still cannot establish NI
    assert all(not c["efficiency_supported"] for c in result["comparisons"] if c["resource"] == "all_planned_timed_review_active_seconds")
