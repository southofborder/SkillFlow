"""External-oracle comparison after all inference; never a model input builder."""

from __future__ import annotations

import hashlib
import json

from .fixtures import PACKAGE_ROOT


def _overlap(left, right):
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def _source_overlap(left, right):
    return left["file"] == right["file"] and max(left["start_line"], right["start_line"]) <= min(left["end_line"], right["end_line"])


def compare_expectation(expected, audit):
    """Evidence/status matches are review candidates, not a semantic proof or score."""
    if audit.get("status") != "complete":
        return {"oracle_finding_id": expected["oracle_finding_id"], "status": "execution_error",
                "candidate_finding_ids": [], "note": "核对未产生有效结果，不能计为语义漏报或通过。"}
    candidates = []
    for finding in audit["result"]["findings"]:
        if finding.get("kind", "semantic") != "semantic":
            continue
        status_match = finding["status"] in expected["acceptable_statuses"]
        graph_match = any(_overlap(left, right) for left in finding["graph_refs"] for right in expected["graph_refs"])
        source_match = not expected["source_refs"] or any(
            _source_overlap(left, right) for left in finding["source_refs"] for right in expected["source_refs"])
        if status_match and graph_match and source_match:
            candidates.append(finding["id"])
    return {"oracle_finding_id": expected["oracle_finding_id"],
            "status": "candidate_match" if candidates else "no_candidate",
            "candidate_finding_ids": candidates,
            "note": "候选仅匹配类别及证据区域，理由是否识别目标缺陷仍需人工复核；无候选也不自动计为漏报。"}


def evaluate(stages, manifest, *, oracle=None):
    """Run only after model outputs, with the unchanged external F01 expectations."""
    if oracle is None:
        path = PACKAGE_ROOT / "experiments/semantic_backtrace/f01/oracle.json"
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != manifest["oracle_sha256"]:
            raise ValueError("External evaluation oracle changed after prepare")
        oracle = json.loads(raw)
    else:
        digest = None
    if oracle["source_sha256"] != manifest["source_sha256"]:
        raise ValueError("Oracle source digest mismatch")
    cases = {}
    for case in manifest["cases"]:
        key = case["case_id"]
        if case["oracle_key"] is None:
            audit = stages[key]
            cases[key] = {"expectations": [], "evaluation_status": "assistant_review_required",
                          "selection": case["selection"],
                          "unknowns": [f["id"] for f in audit.get("result", {}).get("findings", []) if f["status"] == "unknown"],
                          "allowed_unresolved": [],
                          "note": "暂停批次原图没有本实验人工标准答案；001、010的旧判断不作为新核对答案。"}
            continue
        gold = oracle["cases"][case["oracle_key"]]
        if gold["graph_sha256"] != case["input_graph_sha256"]:
            raise ValueError("Oracle current-graph digest mismatch")
        audit = stages[key]
        cases[key] = {
            "expectations": [compare_expectation(item, audit) for item in gold["expected_findings"]],
            "unknowns": [f["id"] for f in audit.get("result", {}).get("findings", []) if f["status"] == "unknown"],
            "allowed_unresolved": gold["allowed_unresolved"],
        }
    return {"oracle_sha256": digest, "cases": cases,
            "adjudication": "Evidence matches are candidates requiring review, not semantic accuracy scores.",
            "false_positives": "未匹配外置预期的问题不自动视为误报；需要逐项复核。",
            "limitations": ["未决不算通过；执行错误与语义问题分别记录。",
                            "固定开发示范和暂停批次的诊断，不支持统计显著性或泛化结论。",
                            "受控文本事实保持不证明原文转换正确、模型判定正确或运行行为安全。"]}
