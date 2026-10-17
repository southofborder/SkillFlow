"""Human review of issues first; evidence and raw locations stay expandable."""
from __future__ import annotations

from html import escape
from copy import deepcopy

from pydantic import TypeAdapter
from skillflow.propagation.review.models import Evidence
from skillflow.propagation.review.services import check_review_evidence
import json
import re
from pathlib import Path

from skillflow.common.artifacts import ArtifactWriter

SUMMARY_LABELS = {"issues_found": "Material issues found", "no_material_issue": "No material issue reported"}
NOTICE = ("This semantic review does not rewrite the sealed Task, annotation or propagation facts. Accounting coverage of source, Task, demands and IR does not prove semantic completeness; "
          "no reported issue does not prove correct interpretation, minimal demands or absence of DOE.")


def _evidence_display(evidence, material):
    typed = TypeAdapter(Evidence).validate_python(evidence)
    if "file" in evidence:
        return {"reference": f"{typed.file}:{typed.start_line}-{typed.end_line}",
                "excerpt": check_review_evidence(typed, material), "reason": typed.reason}
    return {"reference": typed.rule_id if hasattr(typed, "rule_id") else json.dumps(typed.target.model_dump(mode="json"), ensure_ascii=False),
            "excerpt": check_review_evidence(typed, material), "reason": typed.reason}


def display_model(result, material):
    review = result.get("review") or {}
    findings = deepcopy(review.get("findings", []))
    failure = deepcopy(result.get("failure"))
    for claim in [*findings, *([failure] if failure else [])]:
        claim["evidence_display"] = [_evidence_display(item, material) for item in claim["evidences"]]
    requirements = (material.get("task") or {}).get("requirements", [])
    realizations = {row["requirement_id"]: row for row in material.get("raw_annotation", {}).get("realizations", [])}
    checks = {row["requirement_id"]: row for row in review.get("requirement_checks", [])}
    crosswalk = [{"requirement_id": row["id"], "text": row["text"],
                  "source_evidence": [_evidence_display(evidence, material) for evidence in row["evidences"]],
                  "realization": deepcopy(realizations.get(row["id"])),
                  "seeds": deepcopy([seed for seed in material.get("goal_index", []) if seed["requirement_id"] == row["id"]]),
                  "review_check": deepcopy(checks.get(row["id"]))} for row in requirements]
    return {"status": result["status"], "summary": SUMMARY_LABELS.get(result.get("summary"), "Review incomplete"),
            "failure": failure, "reason": result["reason"], "reviewed_ir_ids": review.get("reviewed_ir_ids", []),
            "findings": findings, "resolved": result.get("resolved_findings", []),
            "checks": {key: deepcopy(review.get(key, [])) for key in ("source_checks", "requirement_checks", "goal_checks")},
            "goals": material.get("goal_index", []), "task": material.get("task"),
            "crosswalk": crosswalk,
            "targets": material.get("target_index", {}), "observations": material.get("observations", []),
            "response_chain": result.get("response_chain"),
            "accepted_call": result.get("accepted_call"),
            "counts": result.get("counts", {}), "notice": NOTICE}


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def _md(value):
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", escape(str(value), quote=False))


def render_markdown(model):
    lines = ["# Source → Task → demands whole-chain review", "", f"**{model['summary']}** · Execution status: `{model['status']}`", "",
             _md(model["reason"]), "", NOTICE, ""]
    if model["crosswalk"]:
        lines += ["## Per-requirement semantic correspondence", "", "Expression status and review acceptance do not prove requirement satisfaction. Full source excerpts, remaining gaps and resolved seeds appear in the audit records below.", "",
                  "| Source span | Task requirement | Expression status | Raw demand → goal | Review record |",
                  "| --- | --- | --- | --- | --- |"]
        def cell(value):
            return _md(value).replace("\r\n", " ").replace("\n", " ")
        for row in model["crosswalk"]:
            realization, check = row["realization"] or {}, row["review_check"] or {}
            lines.append("| " + " | ".join([
                cell("; ".join(item["reference"] for item in row["source_evidence"])),
                cell(row["requirement_id"] + ": " + row["text"]), cell(realization.get("status", "Not recorded")),
                cell("; ".join(seed["raw_pointer"] + " → " + seed["goal_id"] for seed in row["seeds"]) or "No positive seed"),
                cell(check.get("status", "No valid record"))]) + " |")
        lines.append("")
    for finding in model["findings"]:
        lines += [f"## {_md(finding['id'])} · {_md(finding.get('domain', 'annotation'))}", "",
                  _md(finding["explanation"]), "", "Related targets: " + ", ".join(map(_md, finding["target_ids"])), ""]
        if finding.get("suggestion"):
            lines += ["Suggested change: " + _md(finding["suggestion"]), ""]
        for evidence in finding["evidence_display"]:
            lines += [f"- {_md(evidence['reference'])}: {_md(evidence['excerpt'])}"]
            if evidence["reason"]:
                lines += ["  Evidence rationale: " + _md(evidence["reason"])]
        lines.append("")
    if not model["findings"]:
        lines += ["This review reported no material issue." if model["status"] == "complete" else "No valid finding list was produced; this is not a no-issue result.", ""]
    if model.get("failure"):
        lines += ["## Unable to complete semantic review", "", _md(model["failure"]["reason"]), "",
                  "Related targets: " + ", ".join(map(_md, model["failure"]["target_ids"])), ""]
        for evidence in model["failure"]["evidence_display"]:
            lines += [f"- {_md(evidence['reference'])}: {_md(evidence['excerpt'])}"]
            if evidence["reason"]:
                lines += ["  Evidence rationale: " + _md(evidence["reason"])]
    resolved = _json({"Source_Task_demands_correspondence": model["crosswalk"], "Per-item review records": model["checks"], "Raw seeds and resolved positions": model["goals"],
                      "Finding targets": model["resolved"]})
    fence = "`" * max(3, max((len(m.group()) + 1 for m in re.finditer(r"`+", resolved)), default=3))
    lines += ["## Audit materials", "", "IR declared reviewed: " + ", ".join(map(_md, model["reviewed_ir_ids"])), "",
              "Request, JSON normalization and structural correction counts: " + _md(_json(model["counts"])), "",
              (("Request chain: [chain.json](calls/review/chain.json); " if model["response_chain"] else "Request chain not started; ")
               + "Targets: [targets.json](inputs/targets.json); Observations: [observations.json](inputs/observations.json)."),
              "", "### Four-axis records and program-resolved targets", "", fence + "json", resolved, fence, ""]
    if model["accepted_call"]:
        lines += [f"Accepted call: [call.json]({model['accepted_call']}/call.json) · "
                  f"[Original response]({model['accepted_call']}/response.json) · "
                  f"[Candidate validation]({model['accepted_call']}/validation.json).", ""]
    lines += ["Original responses remain unchanged. JSON normalization records bind original and candidate digests; normalization does not prove semantic correctness.", ""]
    return "\n".join(lines)


def render_html(model):
    e = escape
    cards = []
    correspondence = ""
    if model["crosswalk"]:
        rows = []
        for row in model["crosswalk"]:
            realization, check = row["realization"] or {}, row["review_check"] or {}
            sources = "".join("<details><summary>" + e(item["reference"]) + "</summary><blockquote>" +
                              e(item["excerpt"]) + "</blockquote></details>" for item in row["source_evidence"])
            seeds = "<br>".join(e(seed["raw_pointer"]) + " → <code>" + e(seed["goal_id"]) + "</code>" for seed in row["seeds"])
            gaps = "; ".join(gap["reason"] for gap in realization.get("gaps", []))
            rows.append("<tr><td>" + sources + "</td><td>" + e(row["requirement_id"] + ": " + row["text"]) +
                        "</td><td>" + e(realization.get("status", "Not recorded")) + ("<p>" + e(gaps) + "</p>" if gaps else "") +
                        "</td><td>" + (seeds or "No positive seed") + "</td><td>" + e(check.get("status", "No valid record")) + "</td></tr>")
        correspondence = ("<section><h2>Per-requirement semantic correspondence</h2><p>Expression status and review acceptance do not prove requirement satisfaction. Expand a source span to see the complete excerpt.</p>"
                          "<table><thead><tr><th>Source evidence</th><th>Task requirement</th><th>Expression status and remaining limitations</th>"
                          "<th>Raw demand → goal</th><th>Review record</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></section>")
    for f in model["findings"]:
        evidence = "".join(f"<li><code>{e(v['reference'])}</code><blockquote>{e(v['excerpt'])}</blockquote><p>{e(v['reason'] or '')}</p></li>"
                           for v in f["evidence_display"])
        cards.append(f"<article id='{e(f['id'], quote=True)}'><h2>{e(f['id'])} · {e(f.get('domain', 'annotation'))}</h2>"
                     f"<p>{e(f['explanation'])}</p><p><b>Suggested change: </b>{e(f.get('suggestion') or '')}</p>"
                     f"<details><summary>Related targets and evidence: {e(', '.join(f['target_ids']))}</summary><ul>{evidence}</ul></details></article>")
    if model.get("failure"):
        cards.append(f"<details><summary>Failure targets and evidence</summary><pre>{e(_json(model['failure']))}</pre></details>")
    if not cards:
        cards.append("<p>No material issue was reported; this does not prove semantic correctness.</p>" if model["status"] == "complete"
                     else "<p>Review failed; no valid finding list was produced.</p>")
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><title>Source → Task → demands whole-chain review</title>"
            "<style>body{max-width:1080px;margin:36px auto;padding:0 24px;font:16px/1.75 system-ui;background:#f7f9fc;color:#1b293a}"
            "article{background:white;border:1px solid #cfd9e5;padding:20px;margin:18px 0;border-radius:10px}"
            "pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}p,blockquote{white-space:pre-wrap;overflow-wrap:anywhere}"
            "table{width:100%;border-collapse:collapse;font-size:13px}td,th{border:1px solid #cfd9e5;padding:10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}"
            "details{margin:18px 0}summary{cursor:pointer}code{color:#254e87}a{color:#155d9c}</style><body>"
            f"<h1>Source → Task → demands whole-chain review</h1><p><b>{e(model['summary'])}</b> · {e(model['status'])}</p>"
            f"<p>{e(model['reason'])}</p><p>{e(NOTICE)}</p>" + correspondence + "".join(cards)
            + f"<details><summary>Four-axis coverage and call counts</summary><pre>{e(_json({**model['checks'], 'reviewed_ir_ids': model['reviewed_ir_ids'], 'counts': model['counts']}))}</pre></details>"
            + f"<details><summary>Program-resolved finding targets</summary><pre>{e(_json(model['resolved']))}</pre></details>"
            + f"<details><summary>Raw seeds, goals and resolved positions</summary><pre>{e(_json(model['goals']))}</pre></details>"
            + f"<details><summary>Compiler-generated observations</summary><pre>{e(_json(model['observations']))}</pre></details>"
            + f"<details><summary>Structural correction chain</summary><pre>{e(_json(model['response_chain']))}</pre></details>"
            + "<p><a href='result.json'>Review result</a> · <a href='inputs/targets.json'>Review targets</a> · <a href='inputs/observations.json'>Generated observations</a>"
            + (" · <a href='calls/review/chain.json'>Request chain</a>" if model["response_chain"] else "")
            + (f" · <a href='{e(model['accepted_call'], quote=True)}/call.json'>Accepted call</a>"
               f" · <a href='{e(model['accepted_call'], quote=True)}/response.json'>Original response</a>"
               f" · <a href='{e(model['accepted_call'], quote=True)}/validation.json'>Candidate validation</a>"
               if model["accepted_call"] else "")
            + "</p><p>Original responses remain unchanged. JSON normalization records bind original and candidate digests; normalization does not prove semantic correctness.</p></body></html>")


def write_reports(directory, result, material, *, writer=None):
    writer = writer or ArtifactWriter(())
    directory = Path(directory)
    model = display_model(result, material)
    markdown, html = render_markdown(model), render_html(model)
    if directory.name == "replay":
        for folder in ("inputs/", "calls/"):
            markdown = markdown.replace("](" + folder, "](../" + folder)
            html = html.replace("href='" + folder, "href='../" + folder)
    writer.text(directory / "report.md", markdown)
    writer.text(directory / "report.html", html)
