"""Stop decisions after structural, fidelity, and audit-response validation.

This policy is not a semantic checker. Its input must already have passed the
single-audit service's strict quote, evidence, and whole-unit coverage checks.
"""

from __future__ import annotations

from typing import Any

from skill_ir.semantic_contract import CONSERVATIVE_RULE_IDS, contract_binding
from .models import FeedbackLimits


ACTIONABLE_STATUSES = frozenset({
    "omitted", "mistranslated", "unsupported_addition", "internal_conflict",
})
ALL_STATUSES = ACTIONABLE_STATUSES | {"represented"}


def decide(
    audit: dict[str, Any], revision: int, max_semantic_revisions: int = 3,
) -> dict[str, Any]:
    """Keep incomplete, failed, and background-only review records from passing."""
    FeedbackLimits(max_semantic_revisions=max_semantic_revisions)
    if type(revision) is not int or not 0 <= revision <= max_semantic_revisions:
        raise ValueError("revision is outside the configured semantic budget")
    if audit.get("outcome") != "completed":
        raise ValueError("a decision requires a completed validated audit")
    findings = audit.get("findings")
    if not isinstance(findings, list) or not findings:
        raise ValueError("a decision requires a nonempty validated audit")
    if any(
        not isinstance(item, dict)
        or item.get("kind") not in {"semantic", "context"}
        or item.get("status") not in ALL_STATUSES
        or not isinstance(item.get("id"), str)
        for item in findings
    ):
        raise ValueError("invalid finding contract in decision input")
    if any(item["kind"] == "context" and item["status"] != "represented" for item in findings):
        raise ValueError("background findings cannot carry semantic judgments")
    business = [item for item in findings if item["kind"] == "semantic"]
    for item in business:
        conservative = item.get("conservative")
        if conservative is not None:
            if (item["status"] != "represented" or not isinstance(conservative, dict)
                    or conservative.get("rule_id") not in CONSERVATIVE_RULE_IDS
                    or not conservative.get("candidate_fact_ids")
                    or not conservative.get("lost_distinctions") or not conservative.get("reason")):
                raise ValueError("invalid conservative dependency finding")
    actionable = [item["id"] for item in business if item["status"] in ACTIONABLE_STATUSES]
    result = {
        "revision": revision, "max_semantic_revisions": max_semantic_revisions,
        "actionable_ids": actionable,
        "semantic_items": len(business),
        **contract_binding(),
        "representation_summary": {
            "represented_ids": [item["id"] for item in business if item["status"] == "represented"],
            "conservative_ids": [item["id"] for item in business if item.get("conservative") is not None],
        },
        "notice": "核对器通过仅表示本轮有效核对记录满足通过门槛；保守依赖保留精度损失，不表示已证明语义等价。",
    }
    if not business:
        return {**result, "status": "semantic_failure", "reason": "核对记录只有背景项，没有业务语义核对项，未完成必要业务核对。"}
    if actionable:
        if revision >= max_semantic_revisions:
            return {**result, "status": "revision_limit", "reason": "明确差异仍存在，语义修复次数已用尽。"}
        return {**result, "status": "revise", "reason": "存在明确差异；按当前图和本轮证据重新完整提取。"}
    return {**result, "status": "audit_passed", "reason": "所有业务项均为 represented，且没有明确差异；未填写保守说明不代表精确保留。"}
