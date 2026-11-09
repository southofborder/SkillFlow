"""English views of task-driven demand; neither necessity nor DOE verdicts.

Both renderers consume one isolated presentation model. Array order is retained
for payload slots and scope instances; display never rewrites input identities.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from html import escape
import json


NOTICE = (
    "Backward demand describes information retained under the recorded processing "
    "relationships. It does not prove irreplaceability, global minimality, "
    "sensitivity, or absence of data over-exposure."
)


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)


def _anchor(kind, value):
    return kind + "-" + sha256(str(value).encode("utf-8")).hexdigest()[:20]


def _demand_summary(value):
    """Render properties as properties, never as a claim of minimal fields."""
    if not isinstance(value, dict):
        return {"requirement": "", "information": "Missing derivation", "position": "", "rules": ""}
    path = json.dumps(value.get("path", []), ensure_ascii=False)
    labels = {"value": "Value", "presence": "Presence", "cardinality": "Cardinality",
              "shape": "Collection structure", "truth": "Condition outcome",
              "action": "Required behavior"}
    information = labels.get(value.get("property"), str(value.get("property", "Demand")))
    information += " at " + path if value.get("path") else " (whole referenced value)"
    if value.get("each"):
        information = "Per element: " + information
    if value.get("excluded_paths"):
        information += "; excluding " + json.dumps(value["excluded_paths"], ensure_ascii=False)
    node = value.get("node", {})
    position = str(node.get("instruction_id") or "") + " / " + str(node.get("kind") or "")
    if node.get("slot") is not None:
        position += " / slot " + str(node["slot"])
    return {"requirement": value.get("requirement_id", ""), "information": information,
            "position": position, "rules": ", ".join(value.get("rules", []))}


def build_view(review, *, metadata=None):
    """Prepare the same goal, sink and derivation ordering for HTML and Markdown."""
    result, index = review.to_dict(), review.index_dict()
    metadata = deepcopy(metadata or {})
    task = metadata.get("task", {})
    requirements = {item["id"]: item for item in task.get("requirements", [])}
    derivations = result.get("derivations", {})
    diagnostics = result.get("diagnostics", [])
    diagnostics_by_id = {item.get("id", str(i)): item for i, item in enumerate(diagnostics)}
    goals = []
    for number, goal in enumerate(result.get("goals", [])):
        identity = goal.get("id", "goal-" + str(number + 1))
        requirement = requirements.get(goal.get("requirement_id"), {})
        goals.append({"id": identity, "anchor": _anchor("goal", identity),
                      "value": goal, "requirement": requirement})
    sinks = []
    for number, sink in enumerate(result.get("sinks", [])):
        identity = sink.get("id", "sink-" + str(number + 1))
        reasons = []
        for key, title in (("demanded_information", "Rule-supported demand"),
                           ("conservative_retention", "Conservative retention")):
            reasons.append({"title": title, "items": [
                {"id": ref, "anchor": _anchor("derivation", ref), "value": derivations.get(ref),
                 "summary": _demand_summary(derivations.get(ref))}
                for ref in sink.get(key, [])]})
        sinks.append({"id": identity, "anchor": _anchor("sink", identity),
            "boundary": sink.get("boundary", {}), "payload": sink.get("actual_payload", []),
            "requirements": [{"id": ref, "text": requirements.get(ref, {}).get("text", "")}
                             for ref in sink.get("related_requirements", [])],
            "reasons": reasons, "ranges": sink.get("unestablished_ranges", []),
            "limitations": [{"id": ref, "value": diagnostics_by_id.get(ref)}
                            for ref in sink.get("limitations", [])], "value": sink})
    return {"schema_version": result.get("schema_version", ""),
            "status": result.get("status", ""), "notice": NOTICE,
            "candidate_origin": metadata.get("candidate_origin", "Offline candidate"),
            "coverage": result.get("coverage", {}), "goals": goals, "sinks": sinks,
            "retained_restrictions": [{"id": req, "anchor": _anchor("requirement", req),
                "requirement": requirements.get(req, {}), "realization": value}
                for req, value in result.get("coverage", {}).get("requirements", {}).items()
                if value["status"] != "expressed" or value["gaps"]],
            "traceability": deepcopy(result.get("traceability", {})),
            "restriction_notice": "Retained review context; not executable or verified predicates. "
                "These task restrictions remain available for review across sink comparisons. "
                "Their listing does not establish a per-sink scope or that a restriction was satisfied.",
            "derivations": [{"id": identity, "anchor": _anchor("derivation", identity), "value": value}
                            for identity, value in derivations.items()],
            "diagnostics": diagnostics, "index": index,
            "assistant_review": metadata.get("assistant_review",
                "No additional semantic approval is implied by preparation or replay.")}


def _pre(value):
    return "<pre>" + escape(_json(value)) + "</pre>"


def _html_ref(item):
    return '<a href="#' + item["anchor"] + '">' + escape(str(item["id"])) + '</a>'


def _html_demands(items):
    rows = ['<table><thead><tr><th>Task</th><th>Information to preserve</th><th>Use position</th>'
            '<th>Rule and derivation</th></tr></thead><tbody>']
    for item in items:
        summary = item["summary"]
        rows.append('<tr><td>' + escape(summary["requirement"]) + '</td><td>' + escape(summary["information"])
            + '</td><td>' + escape(summary["position"]) + '</td><td>' + escape(summary["rules"])
            + '<details><summary>Derivation</summary>' + _html_ref(item) + '</details></td></tr>')
    return ''.join(rows) + '</tbody></table>'


def render_html(review, *, metadata=None):
    view = build_view(review, metadata=metadata)
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Task-driven Backward Demand</title><style>'
        'body{margin:0;background:#f4f6fa;color:#172334;font:16px/1.55 system-ui,sans-serif}'
        'main{max-width:1400px;margin:auto;padding:28px}a{color:#145a9d}a:focus{outline:3px solid #f0bb43}'
        '.card{background:white;border:1px solid #dce3ec;border-radius:10px;padding:20px;margin:18px 0}'
        '.notice{background:#eaf2fb;border-left:5px solid #3778b1;padding:14px 18px}'
        '.warning{background:#fff3d8;padding:12px}nav{display:flex;gap:18px;flex-wrap:wrap}'
        'table{width:100%;border-collapse:collapse}td,th{vertical-align:top;text-align:left;padding:9px;border-bottom:1px solid #e0e5eb}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:30rem;overflow:auto;background:#f5f7fa;padding:12px;font-size:13px}'
        'p,li,td{overflow-wrap:anywhere}summary{cursor:pointer}.columns{display:grid;grid-template-columns:1fr 1fr;gap:20px}'
        '@media(max-width:850px){.columns{grid-template-columns:1fr}main{padding:12px}}'
        '</style></head><body><main><h1>Task-driven Backward Demand</h1><p class="notice">'
        + escape(view["notice"]) + '</p><p>Status: <b>' + escape(view["status"]) + '</b> · '
        + escape(view["schema_version"]) + '</p><p>Candidate origin: ' + escape(view["candidate_origin"])
        + '. Offline preparation; no model calls.</p><nav><a href="#goals">Task goals</a>'
        '<a href="#restrictions">Retained restrictions</a>'
        '<a href="#sinks">Sink comparisons</a><a href="#derivations">Shared derivations</a>'
        '<a href="#diagnostics">Limitations</a><a href="demand-review.json">Business JSON</a></nav>',
        '<section class="card"><h2>Coverage</h2>' + _pre(view["coverage"]) + '</section>',
        '<section id="goals"><h2>Task preservation goals</h2><p>Goals are offline interpretations of existing requirements. '
        'A required action does not exempt all of its current payload.</p>']
    for goal in view["goals"]:
        out.append('<article class="card" id="' + goal["anchor"] + '"><h3>' + escape(str(goal["id"]))
            + '</h3><p>' + escape(goal["requirement"].get("text", "")) + '</p>' + _pre(goal["value"])
            + '<details><summary>Existing Task evidence and binding</summary>' + _pre(goal["requirement"])
            + '</details></article>')
    out.append('</section><section id="restrictions" class="card"><h2>Retained task restrictions</h2><p>'
        + escape(view["restriction_notice"]) + '</p>')
    if view["retained_restrictions"]:
        out.append('<ul>' + ''.join('<li>' + _html_ref(goal) + ': '
            + escape(goal["requirement"].get("text", "")) + '</li>'
            for goal in view["retained_restrictions"]) + '</ul>')
    else:
        out.append('<p>No retained-only or partially expressed task limitations.</p>')
    out.append('</section><section id="sinks"><h2>Sink comparisons</h2><p>Payload slots retain order and candidate identity. '
        'A range with no established demand is not automatically removable, especially when limitations apply.</p>')
    for sink in view["sinks"]:
        out.append('<article class="card" id="' + sink["anchor"] + '"><h3>' + escape(str(sink["id"]))
            + '</h3><p><a href="#restrictions">Shared retained task restrictions</a></p>'
            + '<div class="columns"><div><h4>Current boundary</h4>' + _pre(sink["boundary"])
            + '<h4>Actual payload</h4>' + _pre(sink["payload"]) + '</div><div><h4>Demand-driving requirements</h4><ul>')
        out.extend('<li><b>' + escape(str(item["id"])) + '</b>: ' + escape(item["text"]) + '</li>'
                   for item in sink["requirements"])
        out.append('</ul>')
        for reason in sink["reasons"]:
            out.append('<h4>' + reason["title"] + '</h4>')
            if reason["items"]:
                out.append(_html_demands(reason["items"]))
            else:
                out.append('<p>No entries in this category.</p>')
        out.append('</div></div><h4>Payload ranges without established demand</h4>' + _pre(sink["ranges"]))
        if sink["limitations"]:
            out.append('<h4>Analysis limitations</h4><div class="warning">' + _pre(sink["limitations"]) + '</div>')
        out.append('<details><summary>Full sink comparison</summary>' + _pre(sink["value"]) + '</details></article>')
    out.append('</section><section id="derivations"><h2>Shared rule derivations</h2>')
    for item in view["derivations"]:
        out.append('<details class="card" id="' + item["anchor"] + '"><summary>' + escape(str(item["id"]))
            + '</summary>' + _pre(item["value"]) + '</details>')
    out.append('</section><section class="card" id="diagnostics"><h2>Limitations and diagnostics</h2>'
        + _pre(view["diagnostics"]) + '<p>' + escape(view["assistant_review"]) + '</p></section>'
        '<details class="card"><summary>Reference index</summary>' + _pre(view["index"])
        + '</details></main></body></html>')
    return ''.join(out)


def _md(value):
    result = escape(str(value), quote=False)
    for character in ('\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|', '>'):
        result = result.replace(character, '\\' + character)
    return result


def render_markdown(review, *, metadata=None):
    view = build_view(review, metadata=metadata)
    out = ['# Task-driven Backward Demand', view["notice"], '**Status:** ' + _md(view["status"]),
        '**Candidate origin:** ' + _md(view["candidate_origin"]), 'Offline preparation; no model calls.',
        '## Coverage', _pre(view["coverage"]), '## Per-goal derivation provenance', _pre(view["traceability"]), '## Task preservation goals',
        'A required action does not exempt all of its current payload.']
    for goal in view["goals"]:
        out.extend(['<a id="' + goal["anchor"] + '"></a>', '### ' + _md(goal["id"]),
                    _md(goal["requirement"].get("text", "")), _pre(goal["value"]),
                    '<details><summary>Existing Task evidence and binding</summary>'
                    + _pre(goal["requirement"]) + '</details>'])
    out += ['<a id="restrictions"></a>', '## Retained task restrictions', view["restriction_notice"]]
    if view["retained_restrictions"]:
        out.append('\n'.join('- [' + _md(goal["id"]) + '](#' + goal["anchor"] + '): '
            + _md(goal["requirement"].get("text", "")) for goal in view["retained_restrictions"]))
    else:
        out.append('No retained-only or partially expressed task limitations.')
    out += ['## Sink comparisons', 'Payload slots retain parameter order and candidate identity. '
            'No established demand does not automatically authorize deletion.']
    for sink in view["sinks"]:
        out.extend(['<a id="' + sink["anchor"] + '"></a>', '### ' + _md(sink["id"]),
                    '[Shared retained task restrictions](#restrictions)',
                    '#### Current boundary', _pre(sink["boundary"]), '#### Actual payload', _pre(sink["payload"]),
                    '#### Demand-driving requirements'])
        out += ['- **' + _md(item["id"]) + ':** ' + _md(item["text"]) for item in sink["requirements"]]
        for reason in sink["reasons"]:
            out.append('#### ' + reason["title"])
            if reason["items"]:
                rows = ['| Task | Information to preserve | Use position | Rule and derivation |',
                        '| --- | --- | --- | --- |']
                for item in reason["items"]:
                    summary = item["summary"]
                    rows.append('| ' + ' | '.join(_md(summary[key]) for key in
                        ("requirement", "information", "position")) + ' | ' + _md(summary["rules"])
                        + ' [' + _md(item["id"]) + '](#' + item["anchor"] + ') |')
                out.append('\n'.join(rows))
            else:
                out.append('No entries in this category.')
        out += ['#### Payload ranges without established demand', _pre(sink["ranges"]),
                '#### Analysis limitations', _pre(sink["limitations"])]
    out.append('## Shared rule derivations')
    for item in view["derivations"]:
        out += ['<a id="' + item["anchor"] + '"></a>', '### ' + _md(item["id"]), _pre(item["value"])]
    out += ['## Limitations and diagnostics', _pre(view["diagnostics"]), _md(view["assistant_review"]),
            '<details><summary>Reference index</summary>' + _pre(view["index"]) + '</details>']
    return '\n\n'.join(out) + '\n'
