"""Review: conversion evidence is separate from model semantic judgments."""
from collections import Counter

from skillflow.common.source_evidence import extract_source_lines

LABELS = {"represented": "Represented (model judgment)", "omitted": "Omission", "mistranslated": "Mistranslation",
          "unsupported_addition": "Unsupported addition", "internal_conflict": "Internal conflict"}


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def source_evidence_lines(references, source=None):
    """Render current frozen spans without persisting another quotation copy."""
    files = {item["path"]: item["content"] for item in source["files"]} if source else {}
    lines = []
    for ref in references:
        lines.extend([f"Source: `{ref['file']}:{ref['start_line']}-{ref['end_line']}`.", ""])
        if source is not None:
            excerpt = extract_source_lines(files[ref["file"]], ref["start_line"], ref["end_line"])
            lines.extend([*["> " + line for line in excerpt.splitlines()], ""])
    return lines


def _details(finding, source=None):
    refs = [f"{r['file']}:{r['start_line']}-{r['end_line']}" for r in finding["source_refs"]]
    units = [r["unit_id"] for r in finding["controlled_refs"]]
    lines = [f"### {finding['id']} · {LABELS[finding['status']]}", "",
            "Source requirement: " + finding["source_requirement"], "",
            "Actual representation: " + finding["actual_representation"], "",
            "Reason: " + finding["reason"], "",
            "Source spans: " + "; ".join(refs), "",
            "Controlled evidence IDs: " + ", ".join(units), "",
            "Program-mapped graph positions: " + "; ".join(finding["graph_refs"]), ""]
    if finding.get("conservative"):
        item = finding["conservative"]
        lines.extend(["Conservative retention: the model explicitly applies the dependency interpretation below.", "",
                      "Conservative rule: " + item["rule_id"], "",
                      "Candidate facts: " + ", ".join(item["candidate_fact_ids"]), "",
                      "Precision loss: " + "; ".join(item["lost_distinctions"]), "",
                      "Conservative representation rationale: " + item["reason"], "",
                      "Candidate graph positions: " + "; ".join(item["graph_refs"]), ""])
    lines.extend(source_evidence_lines(finding["source_refs"], source))
    return lines


def _failure_details(stage, source=None):
    failure = stage.get("failure")
    if not failure:
        return []
    lines = ["Evidence for failure to complete a necessary judgment (not a normal finding; does not trigger semantic repair): ", ""]
    lines.extend(source_evidence_lines(failure.get("source_refs", []), source))
    for reference in failure.get("controlled_refs", []):
        lines.extend(["Controlled facts: `" + reference["unit_id"] + "`.", ""])
    lines.extend(["Program-mapped graph positions: " + "; ".join(failure.get("graph_refs", [])), ""])
    return lines


def render_suggestions(identifier, stage, *, source=None):
    lines = [f"# {identifier} Itemized review and suggested changes", "",
             "These are model review and program-resolved locations, not user-confirmed conclusions; they do not automatically modify the original graph.", ""]
    if stage["status"] != "complete":
        return "\n".join(lines + ["Review incomplete: " + stage.get("error", stage.get("reason", stage["status"])), ""] + _failure_details(stage, source))
    findings = [f for f in stage["result"]["findings"] if f.get("kind", "semantic") == "semantic"
                and (f["status"] != "represented" or f.get("conservative"))]
    if not findings:
        lines.extend(["The model reported no business differences or conservative dependencies; this does not prove semantic correctness.", ""])
    for finding in findings:
        lines.extend(_details(finding, source))
        for suggestion in finding["suggestions"]:
            lines.extend(["Suggestion: " + suggestion["change"], "",
                          "Suggestion rationale: " + suggestion["reason"], "",
                          "Change targets: " + ", ".join(suggestion["target_ids"]), "",
                          "Target graph positions: " + "; ".join(suggestion["graph_refs"]), ""])
    return "\n".join(lines)


def render_report(result, *, sources=None):
    lines = ["# Controlled retelling and complete-source review", "", f"Run: `{result['run_id']}`; Mode: `{result['mode']}`.", "",
             f"Interpretation contract: `{result['contract_version']}`, SHA-256 `{result['contract_sha256']}`.", "",
             "The sole model task is to compare the complete source and controlled text. Transformation checks, model judgments and external evaluation are reported separately.", "",
             "Normal review checks coverage of every nonempty physical source line and controlled-fact ID through the union of references. Reference coverage does not prove semantic completeness. Failure responses validate only their cited positions.", "",
             "## Differences and execution status", "",
             "The valid model judgments are retained below; context items record non-business context only and do not count as preservation of business semantics.", ""]
    for identifier, stage in result["stages"].items():
        selection = result["case_selections"][identifier]
        label = (f"Paused batch {selection['sample_index']} Round {selection['revision']} "
                 if "sample_index" in selection else f"F01 Round {selection['repetition']} and its fixed variants")
        lines.extend([f"### {identifier} · {label}", ""])
        if stage["status"] != "complete":
            lines.extend(["Execution status: " + stage["status"], "", stage.get("error", stage.get("reason", "")), ""])
            lines.extend(_failure_details(stage, (sources or {}).get(identifier)))
            continue
        semantic = [f for f in stage["result"]["findings"] if f.get("kind", "semantic") == "semantic"]
        counts = Counter(f["status"] for f in semantic)
        lines.extend(["; ".join(f"{LABELS[k]} {v}" for k,v in counts.items()), "",
                      f"Represented items: {len(stage['result']['representation_summary']['represented_ids'])}; "
                      f"Items with explicit conservative explanations: {len(stage['result']['representation_summary']['conservative_ids'])}. "
                      "Absence of a conservative explanation does not imply exact representation.", "",
                      f"Itemized suggested changes: [suggestions/{identifier}.md](suggestions/{identifier}.md).", "",
                      "| Finding | Source requirement / representation | Reason | Controlled evidence |", "|---|---|---|---|"])
        for finding in semantic:
            if finding["status"] == "represented" and not finding.get("conservative"):
                continue
            label = "Represented (with conservative explanation)" if finding.get("conservative") else LABELS[finding["status"]]
            lines.append(f"| {finding['id']} / {label} | {_cell(finding['source_requirement'])}<br>{_cell(finding['actual_representation'])} | {_cell(finding['reason'])} | {_cell(', '.join(r['unit_id'] for r in finding['controlled_refs']))} |")
        lines.append("")
    lines.extend(["## Transformation and execution records", "",
                  f"Planned: {result['planned_logical_calls']} logical calls; recorded: {result['recorded_logical_calls']}; status `{result['execution_status']}`.", "",
                  f"Recorded executions: {result['recorded_execution_calls']}; additional execution retries: {result['audit_execution_retries']}; HTTP attempts: {result['http_attempts']}.", "",
                  f"Request configuration: `{result['config']['model']}` / `{result['config']['reasoning_effort']}`. Independent contexts; no automatic repair or best-of selection.", "",
                  "| Input | Controlled transformation checks | Model execution |", "|---|---|---|"])
    for identifier, stage in result["stages"].items():
        lines.append(f"| {identifier} | {result['conversion'][identifier]} | {stage['status']} |")
    review = result["review30"]
    lines.extend(["", f"Fixed 30-graph offline validation: enabled={review['enabled']}; passed: {sum(r['status']=='passed' for r in review['samples'])}/{len(review['samples'])}.", "",
                  "A passing transformation check means only that the controlled text preserves explicit records in the normalized graph; proof boundaries and per-input certificates are in inputs and verification.", "",
                  "## Review candidates for external expectations", "",
                  "The following matches only judgment categories and evidence regions; it does not automatically establish semantic hits, misses or false positives.", "",
                  "| Input | External expectation | Match status | Candidate findings |", "|---|---|---|---|"])
    for identifier, case in result["evaluation"]["cases"].items():
        if case.get("evaluation_status") == "assistant_review_required":
            lines.append(f"| {identifier} | No human reference answer for this experiment | Awaiting itemized assistant review | — |")
        for row in case["expectations"]:
            lines.append(f"| {identifier} | {row['oracle_finding_id']} | {row['status']} | {', '.join(row['candidate_finding_ids'])} |")
    lines.extend(["", "## Reviewable materials and limitations", "",
                  "- inputs: complete source, original case graph, actual controlled text, evidence index and transformation checks; the original graph is not sent to the model.",
                  "- calls: original prompts, responses, digests, actual model names and SSE; parsed: strictly validated results.",
                  "- suggestions: per-case change suggestions; replay: current-format offline replay results.",
                  "- Constraints are declarations only; condition text is not evaluated; open operations, source code and runtime success are not proven.",
                  "- Conservative dependencies list candidates and precision loss; they do not imply simultaneous candidates or prove later propagation conclusions.",
                  "- Represented items are model judgments; absence of a conservative explanation does not automatically imply exact representation.",
                  "- Fixed cases are development diagnostics; they do not support general correctness or statistical significance.", ""])
    return "\n".join(lines)
