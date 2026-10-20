"""English views of declared sensitivity and sink-specific demand comparisons."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from html import escape
import json

from skillflow.common.source_evidence import extract_source_lines
from .sensitivity_results import resolve_data_review


NOTICE = (
    "Sensitivity coverage is limited to explicit declarations. Undeclared content is not proven non-sensitive. "
    "Comparisons apply to the recorded processing and task-demand rules, not to all possible implementations. "
    "A possible dependency is not evidence that sensitive plaintext is present."
)
CONCLUSIONS = {
    "excess_supported": "Excess supported by the current rules",
    "possible_excess": "Possible excess through an influence relationship",
    "no_excess_established": "No excess established for this declared range",
}


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)


def _anchor(kind, identity):
    return kind + "-" + sha256(str(identity).encode("utf-8")).hexdigest()[:20]


def build_view(review, *, metadata=None):
    """Share ordering, conclusions and exact evidence excerpts across renderers."""
    result, index = review.to_dict(), review.index_dict()
    metadata = deepcopy(metadata or {})
    files = metadata.get("source_files", {})
    requirements = {row["id"]: row for row in metadata.get("task", {}).get("requirements", [])}
    task = deepcopy(metadata.get("task", {}))
    task_evidences = []
    for owner, item in [("purpose", task.get("purpose", {})), *requirements.items()]:
        for evidence in item.get("evidences", []):
            quote = (extract_source_lines(files[evidence["file"]], evidence["start_line"], evidence["end_line"])
                     if evidence.get("file") in files else None)
            task_evidences.append({"owner": owner, "reference": deepcopy(evidence), "quote": quote})
    diagnostics = {row["id"]: row for row in result["diagnostics"]}
    demand_sinks = {row["id"]: row for row in metadata.get("demand", {}).get("sinks", [])}
    declarations = []
    for identity, entry in index.get("declarations", {}).items():
        declaration = entry["declaration"]
        evidences = []
        for evidence in declaration.get("evidences", []):
            quote = (extract_source_lines(files[evidence["file"]], evidence["start_line"], evidence["end_line"])
                     if evidence.get("file") in files else None)
            evidences.append({"reference": evidence, "quote": quote})
        declarations.append({"id": identity, "anchor": _anchor("declaration", identity),
            "value": entry, "evidences": evidences})
    sinks = []
    counts = {key: 0 for key in CONCLUSIONS}
    for sink in result["sinks"]:
        rows = []
        for compact_item in sink["data_reviews"]:
            item = resolve_data_review(compact_item, sink, result["derivations"]["sensitivity"])
            counts[item["conclusion"]] += 1
            rows.append({"id": item["id"], "value": item, "conclusion": CONCLUSIONS[item["conclusion"]],
                "declaration_anchor": _anchor("declaration", item["declaration_id"]),
                "derivation_anchor": _anchor("sensitivity", item["derivation_id"]),
                "demands": [{"id": identity, "anchor": _anchor("demand", identity)}
                            for identity in item["demand_refs"]],
                "constraints": [{"id": identity, "anchor": _anchor("preservation", identity)}
                                for identity in item["constraint_refs"]],
                "limitations": [diagnostics[identity] for identity in item["limitations"]]})
        sinks.append({"id": sink["id"], "anchor": _anchor("sink", sink["id"]), "value": sink,
            "rows": rows, "requirements": [requirements.get(identity, {"id": identity, "text": ""})
                                              for identity in sink["related_requirements"]],
            "demand": ({key: deepcopy(demand_sinks[sink["id"]][key]) for key in (
                "demanded_information", "conservative_retention", "unestablished_ranges", "limitations")}
                if sink["id"] in demand_sinks else None),
            "limitations": [diagnostics[identity] for identity in sink["limitations"]]})
    demand = metadata.get("demand", {})
    traceability = []
    trace_index = {r["requirement_id"]: r for r in demand.get("traceability", {}).get("requirements", [])}
    for requirement in task.get("requirements", []):
        req = requirement["id"]
        trace = deepcopy(trace_index.get(req, {"requirement_id": req, "source_accounting_indices": [], "seeds": []}))
        trace["requirement"] = deepcopy(requirement)
        trace["source_accounting"] = []
        for accounting_index in trace["source_accounting_indices"]:
            row = deepcopy(task["source_accounting"][accounting_index])
            row["quote"] = extract_source_lines(files[row["file"]], row["start_line"], row["end_line"]) if row["file"] in files else None
            trace["source_accounting"].append(row)
        trace["realization"] = deepcopy(demand.get("coverage", {}).get("requirements", {}).get(req))
        goals = {g["id"]: g for g in demand.get("goals", [])}
        for seed in trace["seeds"]:
            seed["compiled_goal"] = deepcopy(goals.get(seed["goal_id"]))
            seed["sink_ids"] = [sink["id"] for sink in demand.get("sinks", [])
                if set(seed["derivation_ids"]) & set(sink["demanded_information"] + sink["conservative_retention"])]
        traceability.append(trace)
    all_derivations = {**result["derivations"],
        "demand": metadata.get("demand", {}).get("derivations", result["derivations"]["demand"])}
    derivations = [{"kind": kind, "id": identity, "anchor": _anchor(kind, identity), "value": value}
                   for kind in ("sensitivity", "demand")
                   for identity, value in all_derivations[kind].items()]
    derivations += [{"kind": kind, "id": identity, "anchor": _anchor(kind, identity), "value": row}
                    for kind in ("preservation", "influence")
                    for identity, row in result["constraints"][kind].items()]
    return {"schema_version": result["schema_version"], "status": result["status"], "notice": NOTICE,
        "business_filename": metadata.get("business_filename", "sensitivity-review.json"),
        "task": task, "task_evidences": task_evidences, "traceability": traceability,
        "task_provenance": deepcopy(metadata.get("task_provenance", {
            "kind": "unknown", "task_sha256": task.get("task_sha256")})),
        "realization_coverage": deepcopy(demand.get("coverage", {}).get("requirements", {})),
        "candidate_origin": metadata.get("candidate_origin", "Offline candidate"),
        "declaration_source": metadata.get("declaration_source", "offline_candidate"),
        "coverage": result["coverage"], "counts": counts, "declarations": declarations,
        "constraint_checks": result["constraints"]["checks"],
        "sinks": sinks, "derivations": derivations, "diagnostics": result["diagnostics"],
        "index": index}


def _pre(value):
    return "<pre>" + escape(_json(value)) + "</pre>"


def _info(item):
    text = item["label"] + " / " + item["property"] + " / " + _json(item["path"])
    if item.get("excluded_paths"):
        text += "; excluding " + _json(item["excluded_paths"])
    return text


def render_html(review, *, metadata=None):
    view = build_view(review, metadata=metadata)
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Sensitivity and sink demand</title>'
        '<style>body{font:16px/1.55 system-ui,sans-serif;background:#f4f6fa;color:#172334;margin:0}'
        'main{max-width:1400px;margin:auto;padding:28px}.card{background:#fff;padding:20px;border:1px solid #dce3ec;'
        'border-radius:9px;margin:18px 0}.notice{background:#eaf2fb;border-left:5px solid #3778b1;padding:15px}'
        'nav{display:flex;gap:18px;flex-wrap:wrap}a{color:#145a9d}summary{cursor:pointer}pre{white-space:pre-wrap;'
        'overflow-wrap:anywhere;max-height:28rem;overflow:auto;background:#f5f7fa;padding:12px;font-size:13px}'
        'table{border-collapse:collapse;width:100%}th,td{vertical-align:top;text-align:left;border-bottom:1px solid #dce3ec;'
        'padding:9px;overflow-wrap:anywhere}.muted{color:#526475}h3,p,li{overflow-wrap:anywhere}'
        '</style></head><body><main><h1>Sensitivity and sink-demand comparisons</h1><p class="notice">'
        + escape(view["notice"]) + '</p><p>Status: <b>' + escape(view["status"]) + '</b> · '
        + escape(view["schema_version"]) + '</p><p>Candidate origin: ' + escape(view["candidate_origin"])
        + '. Source: ' + escape(view["declaration_source"])
        + '. Offline preparation; zero API calls.</p><nav><a href="#sinks">Sink comparisons</a>'
        '<a href="#declarations">Declarations and evidence</a><a href="#derivations">Shared derivations</a>'
        '<a href="#diagnostics">Diagnostics</a><a href="' + escape(view["business_filename"], quote=True)
        + '">Business JSON</a></nav>',
        '<section class="card"><h2>Coverage</h2>' + _pre(view["coverage"]) + '<h3>Range comparisons</h3>'
        + _pre(view["counts"]) + '<p>These counts concern declared ranges, not unique leaks or measured events.</p></section>',
        '<section class="card" id="constraints"><h2>Forward constraint checks</h2>'
        '<p>Constraints do not prune actual propagation or create positive demands. Baseline violations remain visible '
        'even when an independent local reduction is supported. Satisfied means only the supported static model.</p>'
        + _pre(view["constraint_checks"]) + '</section>',
        '<section class="card" id="task"><h2>Task and demand basis</h2>'
        '<p>These front-end requirements drive preservation demands. Reference checks do not prove '
        'semantic support or completeness; current payload use is not a necessity argument.</p>'
        + '<h3>Task provenance</h3>' + _pre(view["task_provenance"])
        + '<p>Annotation acceptance and Task provenance are recorded separately; an assistant-authored fixture is not evidence of independent Task extraction performance.</p>'
        + _pre(view["task"]) + '<details><summary>Task source evidence</summary>'
        + _pre(view["task_evidences"]) + '</details></section>',
        '<section class="card" id="traceability"><h2>Source → Task → demands correspondence</h2>'
        '<p>These links are generated by the program; expression, review and computation states remain separate. Accounting coverage does not prove semantic completeness. '
        'Neither model-declared whole-value goals nor rule-derived conservative whole-value demands are necessity proofs.</p>'
        + _pre(view["traceability"]) + '</section>',
        '<section id="sinks"><h2>Sink comparisons</h2>']
    for sink in view["sinks"]:
        value = sink["value"]
        out.append('<article class="card" id="' + sink["anchor"] + '"><h3>' + escape(sink["id"])
            + '</h3><details><summary>Boundary and actual payload</summary>'
            + _pre({"boundary": value["boundary"], "actual_payload": value["actual_payload"]}) + '</details>'
            '<h4>Demand-driving requirements</h4><ul>')
        out.extend('<li><b>' + escape(row["id"]) + '</b>: ' + escape(row.get("text", "")) + '</li>'
                   for row in sink["requirements"])
        out.append('</ul>')
        if sink["demand"] is not None:
            out.append('<details><summary>Full boundary-specific preservation demand</summary>'
                '<p>Unestablished demand is not a deletion certificate; all conservative retention '
                'and relevant limitations constrain a reduction.</p>' + _pre(sink["demand"]) + '</details>')
        if not sink["rows"]:
            out.append('<p class="notice">No declared sensitive range reaches this sink in the supported '
                'relationships. This is not a non-sensitive or no-DOE certificate.</p>')
        else:
            out.append('<table><thead><tr><th>Payload slot and data version</th><th>Declared information</th>'
                '<th>Relationship</th><th>Demand comparison</th><th>Support</th></tr></thead><tbody>')
            for row in sink["rows"]:
                item = row["value"]
                out.append('<tr><td>' + escape(item["operation_id"]) + ' / input ' + str(item["input_index"])
                    + '<br>' + escape(item["data_id"]) + '</td><td>' + escape(_info(item)) + '</td><td>'
                    + escape(item["relation"]) + '</td><td><b>' + escape(row["conclusion"]) + '</b><p>'
                    + escape(item["reason"]) + '</p></td><td><a href="#' + row["declaration_anchor"]
                    + '">Declaration</a> · <a href="#' + row["derivation_anchor"] + '">Sensitivity derivation</a>')
                out.extend('<br><a href="#' + demand["anchor"] + '">' + escape(demand["id"]) + '</a>'
                           for demand in row["demands"])
                out.extend('<br><a href="#' + proof["anchor"] + '">Constraint preservation</a>'
                           for proof in row["constraints"])
                if row["limitations"]:
                    out.append('<details><summary>Limits</summary>' + _pre(row["limitations"]) + '</details>')
                if item.get("reduction") is not None:
                    out.append('<details><summary>Supported field reduction</summary>' + _pre(item["reduction"]) + '</details>')
                out.append('</td></tr>')
            out.append('</tbody></table>')
        if sink["limitations"]:
            out.append('<h4>Sink limitations</h4>' + _pre(sink["limitations"]))
        out.append('<details><summary>Full comparison record</summary>' + _pre(value) + '</details></article>')
    out.append('</section><section id="declarations"><h2>Shared declarations and source evidence</h2>'
        '<p>Evidence locates the claim; a real excerpt does not prove the sensitivity interpretation.</p>')
    if not view["declarations"]:
        out.append('<p>No explicit sensitivity declarations. Unknown source remainder is retained in facts, '
                   'but is not assigned invented sensitive fields or labels.</p>')
    for declaration in view["declarations"]:
        out.append('<article class="card" id="' + declaration["anchor"] + '"><h3>'
            + escape(declaration["id"]) + '</h3>' + _pre(declaration["value"]))
        for evidence in declaration["evidences"]:
            out.append('<details><summary>Exact frozen source excerpt</summary>' + _pre(evidence) + '</details>')
        out.append('</article>')
    out.append('</section><section id="derivations"><h2>Shared derivations</h2>')
    for item in view["derivations"]:
        out.append('<details class="card" id="' + item["anchor"] + '"><summary>' + escape(item["kind"])
                   + ' · ' + escape(item["id"]) + '</summary>' + _pre(item["value"]) + '</details>')
    out.append('</section><section class="card" id="diagnostics"><h2>Diagnostics and limitations</h2>'
        + _pre(view["diagnostics"]) + '</section></main></body></html>')
    return ''.join(out)


def _md(value):
    text = escape(str(value), quote=False)
    for char in ('\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|', '>'):
        text = text.replace(char, '\\' + char)
    return text


def render_markdown(review, *, metadata=None):
    view = build_view(review, metadata=metadata)
    out = ['# Sensitivity and sink-demand comparisons', view["notice"], '**Status:** ' + _md(view["status"]),
        '**Candidate origin:** ' + _md(view["candidate_origin"]), 'Offline preparation; zero API calls.',
        '**Declaration source:** ' + _md(view["declaration_source"]),
        '## Coverage', _pre(view["coverage"]), '## Range comparisons', _pre(view["counts"]),
        'These counts concern declared ranges, not unique leaks or measured events.',
        '## Forward constraint checks',
        'Constraints do not change actual propagation or create positive demands. Baseline findings remain visible independently of any local reduction. Satisfaction is limited to the supported static model.',
        _pre(view["constraint_checks"]),
        '## Task and demand basis',
        'These front-end requirements drive preservation demands. Reference checks do not prove '
        'semantic support or completeness; current payload use is not a necessity argument.',
        '### Task provenance', _pre(view["task_provenance"]),
        'Annotation acceptance and Task provenance are recorded separately; an assistant-authored fixture is not evidence of independent Task extraction performance.',
        _pre(view["task"]), '<details><summary>Task source evidence</summary>'
        + _pre(view["task_evidences"]) + '</details>',
        '## Source → Task → demands correspondence',
        'Links are program-generated; accounting coverage and completed computation do not prove semantic completeness. Each entry retains source evidence, expression gaps, raw demand positions, compiled goals, per-seed derivations and receiving boundaries.',
        _pre(view["traceability"]), '## Sink comparisons']
    for sink in view["sinks"]:
        value = sink["value"]
        out += ['<a id="' + sink["anchor"] + '"></a>', '### ' + _md(sink["id"]),
            '<details><summary>Boundary and actual payload</summary>'
            + _pre({"boundary": value["boundary"], "actual_payload": value["actual_payload"]}) + '</details>',
            '#### Demand-driving requirements']
        out += ['- **' + _md(row["id"]) + ':** ' + _md(row.get("text", "")) for row in sink["requirements"]]
        if sink["demand"] is not None:
            out += ['<details><summary>Full boundary-specific preservation demand</summary>'
                    '<p>Unestablished demand is not a deletion certificate; all conservative retention '
                    'and relevant limitations constrain a reduction.</p>' + _pre(sink["demand"]) + '</details>']
        if not sink["rows"]:
            out.append('No declared sensitive range reaches this sink in the supported relationships. '
                       'This is not a non-sensitive or no-DOE certificate.')
        for row in sink["rows"]:
            item = row["value"]
            out += ['#### ' + _md(row["conclusion"]),
                '**Payload:** ' + _md(item["operation_id"]) + ' / input ' + str(item["input_index"])
                + ' / ' + _md(item["data_id"]), '**Information:** ' + _md(_info(item)),
                '**Relationship:** ' + _md(item["relation"]), _md(item["reason"]),
                '[Declaration](#' + row["declaration_anchor"] + ') · [Sensitivity derivation](#'
                + row["derivation_anchor"] + ')',
                '\n'.join('- [' + _md(demand["id"]) + '](#' + demand["anchor"] + ')' for demand in row["demands"])]
            out += ['\n'.join('- [Constraint preservation](#' + proof["anchor"] + ')' for proof in row["constraints"])]
            if row["limitations"]:
                out += ['**Limits:**', _pre(row["limitations"])]
            if item.get("reduction") is not None:
                out += ['**Supported field reduction:**', _pre(item["reduction"])]
        if sink["limitations"]:
            out += ['#### Sink limitations', _pre(sink["limitations"])]
    out += ['## Shared declarations and source evidence',
            'Evidence locates the claim; a real excerpt does not prove the sensitivity interpretation.']
    if not view["declarations"]:
        out.append('No explicit sensitivity declarations. Unknown source remainder is retained in facts, '
                   'but is not assigned invented sensitive fields or labels.')
    for declaration in view["declarations"]:
        out += ['<a id="' + declaration["anchor"] + '"></a>', '### ' + _md(declaration["id"]), _pre(declaration["value"])]
        out.extend('<details><summary>Exact frozen source excerpt</summary>' + _pre(evidence) + '</details>'
                   for evidence in declaration["evidences"])
    out.append('## Shared derivations')
    for item in view["derivations"]:
        out += ['<a id="' + item["anchor"] + '"></a>', '### ' + _md(item["kind"] + ' · ' + item["id"]), _pre(item["value"])]
    out += ['## Diagnostics and limitations', _pre(view["diagnostics"])]
    return '\n\n'.join(out) + '\n'
