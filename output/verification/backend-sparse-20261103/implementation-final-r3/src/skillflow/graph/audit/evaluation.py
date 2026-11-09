"""External-oracle comparison after all inference; never a model input builder."""

from __future__ import annotations

import hashlib
import json

from skillflow.common.paths import project_root


def _overlap(left, right):
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def _source_overlap(left, right):
    return left["file"] == right["file"] and max(left["start_line"], right["start_line"]) <= min(left["end_line"], right["end_line"])


def compare_expectation(expected, audit):
    """Evidence/status matches are review candidates, not a semantic proof or score."""
    if audit.get("status") != "complete":
        return {"oracle_finding_id": expected["oracle_finding_id"], "status": audit.get("status", "execution_error"),
                "candidate_finding_ids": [], "note": "Review produced no valid result; this is neither a semantic miss nor a pass."}
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
            "note": "Candidates match only categories and evidence regions. Whether the rationale identifies the intended defect requires human review; no candidate is not automatically a miss."}


def evaluate(stages, manifest, *, oracle=None):
    """Run only after model outputs, with the unchanged external F01 expectations."""
    if oracle is None:
        path = project_root() / "experiments/graph/audit/f01/oracle.json"
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
                          "note": "The paused-batch original graphs have no human reference answer for this experiment; earlier 001 and 010 judgments are not answers for the new review."}
            continue
        gold = oracle["cases"][case["oracle_key"]]
        if gold["graph_sha256"] != case["input_graph_sha256"]:
            raise ValueError("Oracle current-graph digest mismatch")
        audit = stages[key]
        cases[key] = {
            "expectations": [compare_expectation(item, audit) for item in gold["expected_findings"]],
        }
    return {"oracle_sha256": digest, "cases": cases,
            "adjudication": "Evidence matches are candidates requiring review, not semantic accuracy scores.",
            "false_positives": "Findings outside the external expectations are not automatically false positives; review each individually.",
            "limitations": ["Inability to complete a necessary judgment is not a pass; execution errors and semantic issues are recorded separately.",
                            "Fixed development examples and paused-batch diagnostics do not support statistical-significance or generalization claims.",
                            "Fact preservation in controlled text does not prove source translation, model judgment or runtime safety."]}
