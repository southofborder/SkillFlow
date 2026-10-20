"""Conservative secondary efficiency decisions with complete paired cohorts.

The primary accuracy/Holm family is unchanged. Twenty prespecified directional
efficiency claims use forty one-sided bounds (quality and resource per claim).
Degenerate bootstrap quality intervals cannot establish noninferiority.
"""
from collections import defaultdict
import math
import random

from .assessment import _quantile
from .protocol import SEED

CLAIMS = 20
TAIL = .05 / (2 * CLAIMS)


def _number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def efficiency_decision(pairs, *, bootstrap_samples=10000):
    """Pairs supply claimant/comparator quality (0..1) and all resource costs."""
    result = {"planned_cases": 24, "observed_cases": len(pairs),
              "quality_noninferiority_margin": .05, "required_resource_reduction": .20,
              "directional_claim_family": CLAIMS, "one_sided_tail": TAIL,
              "quality_noninferiority_supported": False, "efficiency_supported": False}
    if (len(pairs) != 24 or len({p['case_id'] for p in pairs}) != 24
            or any(not p.get("adjudicated") for p in pairs)):
        return {**result, "status": "incomplete_or_unresolved_quality"}
    if any(not all(_number(p.get(k)) for k in ("claimant_quality", "comparator_quality"))
           or p["claimant_quality"] > 1 or p["comparator_quality"] > 1 for p in pairs):
        raise ValueError("Efficiency requires bounded case-level quality proportions")
    if any(p.get("censored") or not all(_number(p.get(k)) for k in ("claimant_cost", "comparator_cost")) for p in pairs):
        return {**result, "status": "unknown_cost_or_censored_review"}
    groups = defaultdict(list)
    for pair in pairs:
        groups[pair["source_cluster"]].append(pair)
    result["source_clusters"] = len(groups)
    if len(groups) < 8:
        return {**result, "status": "insufficient_source_clusters"}
    def estimates(observed):
        quality = sum(p["claimant_quality"] - p["comparator_quality"] for p in observed) / len(observed)
        denominator = sum(p["comparator_cost"] for p in observed)
        return quality, sum(p["claimant_cost"] for p in observed) / denominator if denominator else None
    quality, ratio = estimates(pairs)
    result.update(quality_difference=quality, resource_ratio=ratio)
    if ratio is None:
        return {**result, "status": "zero_comparator_resource"}
    ordered = [groups[k] for k in sorted(groups)]
    rng = random.Random(SEED)
    quality_samples, ratios = [], []
    for _ in range(bootstrap_samples):
        observed = [p for _ in ordered for p in rng.choice(ordered)]
        q, r = estimates(observed)
        quality_samples.append(q)
        if r is None:
            return {**result, "status": "zero_bootstrap_comparator_resource"}
        ratios.append(r)
    bounds = [_quantile(quality_samples, TAIL), _quantile(quality_samples, 1 - TAIL)]
    upper = _quantile(ratios, 1 - TAIL)
    result.update(quality_bounds=bounds, resource_ratio_upper_bound=upper,
                  bootstrap_samples=bootstrap_samples)
    if bounds[1] - bounds[0] <= 1e-12:
        return {**result, "status": "degenerate_quality_interval_noninferiority_unestablished"}
    noninferior = bounds[0] > -.05
    return {**result, "status": "secondary_cluster_bootstrap_evidence",
            "quality_noninferiority_supported": noninferior,
            "efficiency_supported": noninferior and upper <= .80}


def efficiency_comparisons(scores, costs):
    rows = scores.get("rows", [])
    cases = sorted({r["case_id"] for r in rows})
    work = {w["workflow_id"]: w for w in costs.get("workflows", [])}
    enhancements = {e["workflow_id"]: e for e in costs.get("enhanced_original_plus_review_cost", [])}
    def method_case(case, method, enhanced=False):
        found = [r for r in rows if r["case_id"] == case and r["method"] == method
                 and r["kind"] == ("review" if enhanced else "main")]
        if enhanced or method == "skillflow_r1":
            found = [r for r in found if r["repeat"] == 1]
        quality = sum(r["judgment"] == "satisfies_reference" for r in found) / len(found) if found else None
        valid = len(found) == (1 if enhanced else 3) and all(r.get("human_verification_complete")
                   and r["judgment"] in {"satisfies_reference", "substantive_error", "workflow_failure"} for r in found)
        return found, quality, valid
    comparisons = []
    for enhanced in (False, True):
        for other in ("audit", "chain"):
            for resource in ("reported_total_tokens", "workflow_elapsed_seconds"):
                pairs = []
                for case in cases:
                    native = [r for r in rows if r["case_id"] == case and r["method"] == "skillflow" and r["kind"] == "main"
                              and (not enhanced or r["repeat"] == 1)]
                    direct, direct_q, direct_ok = method_case(case, other, enhanced)
                    native_ok = len(native) == (1 if enhanced else 3) and all(r.get("human_verification_complete")
                        and r["judgment"] in {"satisfies_reference", "substantive_error", "workflow_failure"} for r in native)
                    def cost(observed, reviewed):
                        values = []
                        for r in observed:
                            item = (enhancements if reviewed else work).get(r["workflow_id"], {})
                            usage = item.get("usage_original_plus_review" if reviewed else "usage", {})
                            value = (usage.get("totals", {}).get("total_tokens") if resource == "reported_total_tokens"
                                     else item.get("additive_workflow_seconds" if reviewed else "workflow_elapsed_seconds"))
                            values.append(value)
                        return sum(values) / len(values) if values and all(_number(v) for v in values) else None
                    pairs.append({"case_id": case, "source_cluster": (native or direct)[0]["source_cluster"],
                        "adjudicated": native_ok and direct_ok,
                        "claimant_quality": sum(r["judgment"] == "satisfies_reference" for r in native) / len(native) if native else None,
                        "comparator_quality": direct_q, "claimant_cost": cost(native, False), "comparator_cost": cost(direct, enhanced)})
                for reverse in (False, True):
                    directed = [{**p, **({"claimant_quality": p["comparator_quality"], "comparator_quality": p["claimant_quality"],
                                         "claimant_cost": p["comparator_cost"], "comparator_cost": p["claimant_cost"]} if reverse else {})} for p in pairs]
                    arms = ["skillflow" + ("_r1" if enhanced else ""), other + ("+fixed_review" if enhanced else "")]
                    comparisons.append({"methods": arms[::-1] if reverse else arms, "resource": resource,
                                        **efficiency_decision(directed)})
    timed = costs.get("human_cost", {}).get("practical_timed_review", {}).get("rows", [])
    for other in ("audit", "chain"):
        pairs = []
        for case in cases:
            selected = {m: [t for t in timed if t["case_id"] == case and t["method"] == m] for m in ("skillflow", other)}
            a, b = (selected[m][0] if len(selected[m]) == 1 else {} for m in ("skillflow", other))
            source_cluster = next(r["source_cluster"] for r in rows if r["case_id"] == case)
            pairs.append({"case_id": case, "source_cluster": source_cluster,
                "adjudicated": all(t.get("quality") in {"correct", "incorrect"} and t.get("correct_within_cap") is not None for t in (a, b)),
                "claimant_quality": int(a.get("correct_within_cap") is True), "comparator_quality": int(b.get("correct_within_cap") is True),
                "claimant_cost": a.get("active_seconds"), "comparator_cost": b.get("active_seconds"),
                "censored": a.get("right_censored", True) or b.get("right_censored", True)})
        for reverse in (False, True):
            directed = [{**p, **({"claimant_quality": p["comparator_quality"], "comparator_quality": p["claimant_quality"],
                                 "claimant_cost": p["comparator_cost"], "comparator_cost": p["claimant_cost"]} if reverse else {})} for p in pairs]
            comparisons.append({"methods": [other, "skillflow"] if reverse else ["skillflow", other],
                                "resource": "all_planned_timed_review_active_seconds", **efficiency_decision(directed)})
    return {"comparisons": comparisons, "model_calls": 0,
        "interpretation": "Secondary symmetric efficiency claims require supported 5 pp quality noninferiority and at least 20 percent resource reduction with source-cluster uncertainty. Unknown costs, censored review or degenerate quality intervals prevent claims. All planned cases, failures, retries and original-plus-review costs remain included; no successful-subset median or currency estimate is used."}
