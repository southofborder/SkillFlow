"""Review artifacts; checker decisions are never semantic proofs."""

from __future__ import annotations

from collections import Counter
import json

from skillflow.graph.audit.report import source_evidence_lines


STATUS_LABELS = {
    "audit_passed": "Review passed",
    "semantic_failure": "Unable to complete necessary semantic judgment",
    "revision_limit": "Semantic repair budget exhausted",
    "extraction_error": "Extraction execution error",
    "fidelity_error": "Controlled-text fidelity check error",
    "audit_error": "Review execution error",
    "interrupted": "Interrupted",
    "running": "Running",
    "not_run": "Not run",
    "revise": "Explicit semantic differences found; continue with complete re-extraction",
}
FINDING_LABELS = {
    "represented": "Represented (model judgment)",
    "omitted": "Omission",
    "mistranslated": "Mistranslation",
    "unsupported_addition": "Unsupported addition",
    "internal_conflict": "Internal conflict",
}


def _cell(value):
    return str(value).replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def audit_findings(round_result):
    """Accept the runner's stage wrapper, without inferring absent findings."""
    audit = round_result.get("audit") or {}
    return audit.get("result", audit).get("findings", [])


def finding_summary(round_result):
    counts = Counter(
        finding["status"] for finding in audit_findings(round_result)
        if finding.get("kind") == "semantic"
    )
    return "; ".join(f"{FINDING_LABELS.get(key, key)} {value}" for key, value in counts.items()) or "No valid business-semantic findings"


def _finding_lines(finding, source=None):
    lines = [f"### {finding['id']} · {FINDING_LABELS.get(finding['status'], finding['status'])}", ""]
    if finding.get("conservative"):
        detail = finding["conservative"]
        lines.extend([f"Conservative rule: `{detail['rule_id']}`; Candidate facts: " + ", ".join(detail["candidate_fact_ids"]), "",
                      "Retention rationale: " + detail["reason"], "", "Lost distinctions: " + "; ".join(detail["lost_distinctions"]), ""])
    for label, key in (("Source requirement", "source_requirement"), ("Current retelling", "actual_representation"), ("Difference rationale", "reason")):
        lines.extend([f"{label}: {finding.get(key, '')}", ""])
    lines.extend(source_evidence_lines(finding.get("source_refs", []), source))
    lines.extend(["Controlled facts: " + ", ".join(f"`{ref['unit_id']}`" for ref in finding.get("controlled_refs", [])), "",
                  "Program-mapped positions in the current graph: " + ", ".join(f"`{ref}`" for ref in finding.get("graph_refs", [])), ""])
    for suggestion in finding.get("suggestions", []):
        lines.extend([
            "Suggested change: " + suggestion["change"], "",
            "Evidence: " + suggestion["reason"], "",
            "Current target facts: " + ", ".join(f"`{ref}`" for ref in suggestion["target_ids"]), "",
            "Current target graph positions: " + ", ".join(f"`{ref}`" for ref in suggestion.get("graph_refs", [])), "",
        ])
    return lines


def render_report(result: dict, *, source=None) -> str:
    """Render actual differences first, preserving incomplete and failed rounds."""
    status = result.get("status", "not_run")
    rounds = result.get("rounds", [])
    lines = ["# CFG construction semantic feedback", "",
             f"Stop status: **{STATUS_LABELS.get(status, status)}** (`{status}`).", "",
             "Stop reason: " + str(result.get("reason", "")), "",
             f"Interpretation contract: `{result.get('contract_version')}`; Digest: `{result.get('contract_sha256')}`.", "",
             "Review passing means that the current structure, controlled text and review response are valid, and all present business items were judged represented by the model. It does not prove source-to-graph semantic equivalence.", "",
             "## Per-round differences and stop decisions", "",
             "Each round compares the same complete source with the current controlled text; business and context items are counted separately. Actual judgments remain below; later passing does not erase earlier errors.", "",
             "| Semantic round | Status | Business review | Decision |", "|---|---|---|---|"]
    for row in rounds:
        decision = row.get("decision", {})
        lines.append(f"| {row.get('revision', '?')} | {_cell(row.get('status', ''))} | {_cell(finding_summary(row))} | {_cell(_json(decision) if isinstance(decision, dict) else decision)} |")
    lines.extend(["", "## Final-round differences and suggested changes", ""])
    final_findings = audit_findings(rounds[-1]) if rounds else []
    problems = [finding for finding in final_findings if finding.get("kind") == "semantic" and finding["status"] != "represented"]
    if not problems:
        lines.extend(["The final round has no valid difference record. A failed, unreviewed or business-item-free round cannot be treated as passing.", ""])
    for finding in problems:
        lines.extend(_finding_lines(finding, source))
    lines.extend(["## Conservatively retained dependencies in the final round", "",
                  "Contract-supported candidate dependencies can pass. Precision loss is retained item by item; candidates are not definite transfers. Absence of a conservative explanation does not imply exact preservation.", ""])
    conservative = [finding for finding in final_findings if finding.get("conservative") is not None]
    for finding in conservative:
        lines.extend(_finding_lines(finding, source))
    if not conservative:
        lines.extend(["No valid conservative-retention item in the final round.", ""])
    lines.extend(["## Differences in earlier rounds", ""])
    for row in rounds[:-1]:
        lines.extend([f"### Round {row.get('revision', '?')} ", ""])
        for finding in audit_findings(row):
            if finding.get("kind") == "semantic" and finding["status"] != "represented":
                lines.extend(_finding_lines(finding, source))
    lines.extend(["## Execution and evidence", "",
                  "| Count or limit | Recorded value |", "|---|---|"])
    for category in ("counts", "limits"):
        for key, value in result.get(category, {}).items():
            lines.append(f"| `{category}.{key}` | {_cell(_json(value))} |")
    lines.extend(["", "| Semantic round | Extraction / structure | Controlled transformation | Review execution |", "|---|---|---|---|"])
    for row in rounds:
        extraction = row.get("extraction") or {}
        structural = row.get("structural") or {}
        fidelity = row.get("fidelity") or {}
        audit = row.get("audit") or {}
        audit_status = audit.get("status", "complete" if audit.get("findings") else "Not run")
        lines.append(f"| {row.get('revision', '?')} | {_cell(extraction.get('status', 'Existing graph'))} / {_cell(structural.get('status', 'Not recorded'))} | {_cell(fidelity.get('status', 'Not run'))} | {_cell(audit_status)} |")
    for row in rounds:
        if row.get("error"):
            lines.extend(["", f"Round {row.get('revision', '?')} execution error: `{_json(row['error'])}`.", ""])
    lines.extend(["", "### Review execution retries", "",
                  "One complete review is one logical unit. Only an explicit transient communication failure can start an independently recorded additional execution; "
                  "this does not consume semantic repairs. Complete responses, semantic failures, semantic differences and response-format errors do not trigger communication retries.", "",
                  "| Semantic round | Execution attempt | Result / reason | Retry |", "|---|---|---|---|"])
    for row in rounds:
        for execution in row.get("audit_execution", []):
            lines.append(f"| {row.get('revision', '?')} | {execution['attempt']} | "
                         f"{_cell(execution.get('category', execution['status']))} | "
                         f"{'Yes' if execution.get('retry') else 'No'} |")
    lines.extend(["", "Last valid graph available: " + ("Yes" if result.get("last_valid_cfg") is not None else "No") + ".", "",
                  "Review-passing graph available: " + ("Yes" if result.get("passed_cfg") is not None else "No") + ".", "",
                  "Without a pass, the last valid graph is diagnostic material, not a successful result. Each round retains its candidate, CFG, structural diagnostics, controlled text and certificate, review response and feedback Prompt together with request records in calls.", "",
                  "## Post-run review and trust boundaries", "",
                  "- Controlled round trips preserve facts explicitly recorded in the normalized CFG; they do not prove open-operation behavior, path feasibility or successful file writes.",
                  "- Each review independently compares the complete source and current controlled text. Suggestions given to extraction are claims to verify; the source remains authoritative.",
                  "- Normal review references cover all nonempty physical source lines and controlled-fact IDs; this is not a semantic-completeness proof. Failure responses validate only their cited positions.",
                  "- The model may produce false positives, miss issues or falsely pass after repair. This report does not convert stop states into method accuracy.",
                  "- Re-extraction assigns new IDs; old graph pointers do not prove the new graph is corrected. Review the new graph and evidence against the complete source.",
                  "- See the run manifest for binary and uninterpreted content, source digests, printer and process-transport boundaries.",
                  "- Assistant review and user confirmation are distinct; this generated report does not claim human confirmation.", ""])
    if result.get("boundaries"):
        lines.extend(["Input-specific boundaries:", ""])
        lines.extend("- " + str(boundary) for boundary in result["boundaries"])
        lines.append("")
    return "\n".join(lines)
