"""English read-only views for task requirements and their source references.

The two renderers share a presentation model. They extract source text rather
than accepting a candidate-supplied quote and make no semantic validity claim.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from html import escape
import json

from skillflow.propagation.contracts.references import target_key

from skillflow.common.source_evidence import (
    extract_source_lines,
    resolve_pointer,
    source_lines,
)


NOTICE = "Source spans and target references are validated; semantic support and completeness are not proven."


def _plain(value):
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else deepcopy(value)


def _anchor(kind, value):
    return kind + "-" + sha256(str(value).encode("utf-8")).hexdigest()[:20]


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)


def _line_anchor(path, number):
    return _anchor("source", path) + "-line-" + str(number)


def _uncited_ranges(lines, cited):
    ranges = []
    for number, line in enumerate(lines, 1):
        if number in cited or not line.strip():
            continue
        if ranges and ranges[-1][1] == number - 1:
            ranges[-1][1] = number
        else:
            ranges.append([number, number])
    return ranges


def build_view(review, *, metadata=None):
    """Build isolated source, binding and reverse-index views without mutation."""
    metadata = deepcopy(metadata or {})
    task, cfg, targets = _plain(review.task), _plain(review.cfg), _plain(review.targets)
    files = dict(review.files)
    lines = {path: source_lines(text) for path, text in files.items()}
    cited = {path: set() for path in files}
    instructions = {}
    for block_id, block in cfg["blocks"].items():
        for instruction in block["instructions"]:
            instructions[instruction["id"]] = {
                "id": instruction["id"], "block_id": block_id,
                "opcode": instruction["opcode"], "anchor": _anchor("ir", instruction["id"]),
                "bindings": [],
            }

    def evidence_view(evidence):
        path, start, end = evidence["file"], evidence["start_line"], evidence["end_line"]
        # Validated references are resolved again: reports never accept fabricated quotes.
        quote = extract_source_lines(files[path], start, end)
        cited[path].update(range(start, end + 1))
        context_start, context_end = max(1, start - 2), min(len(lines[path]), end + 2)
        return {**evidence, "quote": quote, "source_anchor": _line_anchor(path, start),
                "context_start": context_start, "context_end": context_end,
                "context": extract_source_lines(files[path], context_start, context_end)}

    purpose = {"text": task["purpose"]["text"],
               "evidences": [evidence_view(item) for item in task["purpose"]["evidences"]]}
    realizations = {row["requirement_id"]: row for row in getattr(review, "realizations", ())}
    requirements = []
    for requirement in task["requirements"]:
        entry = {"id": requirement["id"], "text": requirement["text"],
                 "anchor": _anchor("requirement", requirement["id"]),
                 "evidences": [evidence_view(item) for item in requirement["evidences"]], "bindings": []}
        entry["realization"] = deepcopy(realizations.get(requirement["id"]))
        for binding in realizations.get(requirement["id"], {}).get("bindings", []):
            target = targets[target_key(binding["target"])]
            pointer = target["pointer"]
            bound = {**binding, **target, "target_label": _json(binding["target"]), "value": deepcopy(resolve_pointer(cfg, pointer))}
            entry["bindings"].append(bound)
            if target.get("instruction_id"):
                associated = [target["instruction_id"]]
                scope = "Direct IR target"
            elif target.get("block_id"):
                associated = [key for key, item in instructions.items() if item["block_id"] == target["block_id"]]
                scope = "Block-scope binding; not an individual data-use claim"
            elif pointer == "" or pointer.startswith(("/constraints", "/metadata", "/declared_context_keys")):
                associated = list(instructions)
                scope = "Graph-scope binding; not an individual data-use claim"
            else:
                # A control-edge binding is displayed as that edge. It is not
                # silently reinterpreted as a data dependency of every IR.
                associated, scope = [], "Specific CFG target"
            bound["scope"] = scope
            for identity in associated:
                instructions[identity]["bindings"].append({"requirement": entry["id"],
                    "requirement_anchor": entry["anchor"], "target_label": _json(binding["target"]), "scope": scope})
        requirements.append(entry)
    sources = []
    for path, text in files.items():
        sources.append({"path": path, "anchor": _anchor("source", path), "content": text,
            "lines": [{"number": number, "text": line, "cited": number in cited[path],
                       "anchor": _line_anchor(path, number)} for number, line in enumerate(lines[path], 1)],
            "uncited_ranges": _uncited_ranges(lines[path], cited[path])})
    return {"schema_version": task["schema_version"], "basis": task["basis"], "notice": NOTICE,
            "purpose": purpose, "requirements": requirements,
            "source_accounting": deepcopy(task["source_accounting"]), "issues": deepcopy(task["issues"]), "instructions": list(instructions.values()),
            "sources": sources, "boundaries": _plain(review.boundaries),
            "candidate_origin": str(metadata.get("candidate_origin", "Offline supplied candidate; not a model response, gold standard, or human confirmation.")),
            "assistant_review": str(metadata.get("assistant_review", "No semantic review is recorded in this preparation. Independent assistant reviews, if supplied, are separate opinions.")),
            "unbound_ids": [item["id"] for item in requirements if not item["bindings"]]}


def _html_evidence(item):
    label = f"{item['file']}:{item['start_line']}–{item['end_line']}"
    return ('<div class="evidence"><a href="#' + item["source_anchor"] + '">' + escape(label) + '</a>'
            '<pre class="quote">' + escape(item["quote"]) + '</pre><p><b>Support rationale:</b> '
            + escape(item["reason"]) + '</p><details><summary>Surrounding source (lines '
            + str(item["context_start"]) + '–' + str(item["context_end"]) + ')</summary><pre>'
            + escape(item["context"]) + '</pre></details></div>')


def _html_binding(item):
    return ('<div class="binding"><p><b>' + escape(item["target_label"]) + '</b> · '
            + escape(item["kind"]) + '</p><p><code>' + escape(item["pointer"] or "(graph root)")
            + '</code></p><p>' + escape(item["reason"]) + '</p><p class="muted">'
            + escape(item["scope"]) + '</p><details open><summary>Actual CFG value</summary><pre>'
            + escape(_json(item["value"])) + '</pre></details></div>')


def render_html(review, *, metadata=None):
    """Render an inert, self-contained report; no remote resources or scripts."""
    view = build_view(review, metadata=metadata)
    sections = ['<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Task Evidence Review</title><style>'
        'body{margin:0;background:#f4f6fa;color:#172334;font:16px/1.55 system-ui,sans-serif}'
        'main{max-width:1440px;margin:auto;padding:28px}h1,h2,h3{line-height:1.2}'
        'a{color:#1559a6}a:focus{outline:3px solid #e2a431}p{overflow-wrap:anywhere}'
        '.card{background:white;border:1px solid #d9e0e9;border-radius:12px;padding:22px;margin:20px 0}'
        '.notice{background:#eaf1fc;border-left:5px solid #336fa5;padding:14px 18px}'
        '.warning{background:#fff5dd;padding:12px 16px;border-radius:8px}'
        '.columns{display:grid;grid-template-columns:1fr 1.35fr 1.35fr;gap:20px;align-items:start}'
        '.evidence,.binding{border-top:1px solid #dfe5ed;padding:12px 0}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;background:#f5f7fa;'
        'padding:12px;border:1px solid #e2e7ee;border-radius:6px;tab-size:4;font-size:13px;max-height:36rem;overflow:auto}'
        '.quote{border-left:3px solid #4580b5}code{font-size:13px;overflow-wrap:anywhere}.muted{color:#576777;font-size:14px}'
        'summary{cursor:pointer}li{margin:6px 0}table{border-collapse:collapse;width:100%}td,th{padding:8px;text-align:left;vertical-align:top;border-bottom:1px solid #e2e7ee}'
        '.source-line{display:grid;grid-template-columns:4em 1fr;gap:8px}.source-line:target{background:#fff0b8}'
        '.source-line code{white-space:pre-wrap;tab-size:4}.source-line a{text-align:right;color:#617286}'
        '.cited{background:#edf5fe}.file{padding:12px;border:1px solid #e2e7ee;overflow-wrap:anywhere}'
        'nav{display:flex;gap:18px;flex-wrap:wrap}@media(max-width:1000px){.columns{grid-template-columns:1fr}main{padding:14px}}'
        '</style></head><body><main><h1>Task Evidence Review</h1><p class="notice">' + NOTICE + '</p>',
        '<nav><a href="#reference-validation">Reference validation</a><a href="#requirements">Requirements</a>'
        '<a href="#reverse-index">IR reverse index</a><a href="#full-source">Full source</a>'
        '<a href="#assistant-review">Assistant semantic review</a></nav>',
        '<section id="reference-validation" class="card"><h2>Reference validation</h2><p>Basis: <b>'
        + escape(view["basis"]) + '</b> · Format: ' + escape(view["schema_version"]) + '</p><p>'
        + escape(view["candidate_origin"]) + '</p><p>Source text is extracted from the frozen files. '
        'Bindings are resolved against the actual CFG. Valid references do not establish entailment, '
        'task completeness, action necessity, or a minimal information scope.</p></section>',
        '<section class="card"><h2>Overall purpose</h2><p>' + escape(view["purpose"]["text"]) + '</p>'
        + ''.join(_html_evidence(item) for item in view["purpose"]["evidences"]) + '</section>',
        '<section id="requirements"><h2>Requirements</h2><p>Bindings express correspondence only; '
        'they are not executable demand seeds. A required action does not exempt all of its payload.</p>']
    for item in view["requirements"]:
        bindings = ''.join(_html_binding(binding) for binding in item["bindings"]) if item["bindings"] else (
            '<p class="warning">Unbound requirement: no CFG target is recorded. This requirement must not be silently omitted by later analysis.</p>')
        sections.append('<article class="card" id="' + item["anchor"] + '"><h3>' + escape(item["id"])
            + '</h3><div class="columns"><div><h4>Requirement interpretation</h4><p>' + escape(item["text"])
            + '</p></div><div><h4>Supporting source</h4>' + ''.join(_html_evidence(evidence) for evidence in item["evidences"])
            + '</div><div><h4>CFG targets and rationale</h4>' + bindings + '</div></div></article>')
    sections.append('</section><section id="reverse-index" class="card"><h2>IR reverse index</h2>'
        '<p>Scope bindings are listed as scope, not as inferred input requirements. Absence of a binding is not a uselessness verdict.</p>'
        '<table><thead><tr><th>IR / block</th><th>Related requirements</th></tr></thead><tbody>')
    for item in view["instructions"]:
        links = '<ul>' + ''.join('<li><a href="#' + binding["requirement_anchor"] + '">' + escape(binding["requirement"])
            + '</a> · ' + escape(binding["target_label"]) + '<br>' + escape(binding["scope"]) + '</li>'
            for binding in item["bindings"]) + '</ul>' if item["bindings"] else 'No recorded requirement binding.'
        sections.append('<tr id="' + item["anchor"] + '"><td><b>' + escape(item["id"]) + '</b><br>'
            + escape(item["opcode"]) + '<br>' + escape(item["block_id"]) + '</td><td>' + links + '</td></tr>')
    sections.append('</tbody></table></section><section id="full-source" class="card"><h2>Full source and uncited ranges</h2>'
        '<p>Not cited means no purpose or requirement evidence references these nonblank lines. '
        'It does not mean omitted requirements; background text need not become a task requirement.</p>')
    for source in view["sources"]:
        uncited = ', '.join('<a href="#' + _line_anchor(source["path"], start) + '">' + str(start)
            + ('–' + str(end) if end != start else '') + '</a>' for start, end in source["uncited_ranges"])
        sections.append('<h3 id="' + source["anchor"] + '">' + escape(source["path"]) + '</h3><p>Not cited: '
            + (uncited or 'No nonblank uncited lines.') + '</p><div class="file">')
        for line in source["lines"]:
            sections.append('<div class="source-line' + (' cited' if line["cited"] else '') + '" id="' + line["anchor"]
                + '"><a href="#' + line["anchor"] + '">' + str(line["number"]) + '</a><code>'
                + escape(line["text"].rstrip('\r\n')) + '</code></div>')
        sections.append('</div>')
    sections.append('<details><summary>Source interpretation boundaries</summary><pre>' + escape(_json(view["boundaries"]))
        + '</pre></details></section><section id="assistant-review" class="card"><h2>Assistant semantic review</h2><p>'
        'This is separate from reference validation and is not human confirmation.</p><pre>'
        + escape(view["assistant_review"]) + '</pre></section></main></body></html>')
    return ''.join(sections)


def _md_text(value):
    # Escape HTML plus Markdown punctuation in candidate-controlled prose.
    value = escape(str(value), quote=False)
    for character in ('\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|', '>'):
        value = value.replace(character, '\\' + character)
    return value


def _md_pre(value):
    return '<pre>' + escape(str(value)) + '</pre>'


def _md_evidence(item):
    label = f"{item['file']}:{item['start_line']}–{item['end_line']}"
    return ['[' + _md_text(label) + '](#' + item["source_anchor"] + ')', _md_pre(item["quote"]),
            '**Support rationale:** ' + _md_text(item["reason"]),
            '<details><summary>Surrounding source (lines ' + str(item["context_start"]) + '–'
            + str(item["context_end"]) + ')</summary>' + _md_pre(item["context"]) + '</details>']


def render_markdown(review, *, metadata=None):
    """Render the same evidence and target order as HTML with safe source blocks."""
    view = build_view(review, metadata=metadata)
    parts = ['# Task Evidence Review', NOTICE, '## Reference validation',
        '**Basis:** ' + _md_text(view["basis"]), '**Format:** ' + _md_text(view["schema_version"]),
        _md_text(view["candidate_origin"]),
        'References are checked against frozen source and CFG targets. Valid references do not establish semantic support, '
        'task completeness, action necessity, or minimum information scope.',
        '## Overall purpose', _md_text(view["purpose"]["text"])]
    for evidence in view["purpose"]["evidences"]:
        parts.extend(_md_evidence(evidence))
    parts += ['## Requirements', 'Bindings express correspondence only, not executable demand seeds. '
              'A required action does not exempt all of its payload.']
    for item in view["requirements"]:
        parts.extend(['<a id="' + item["anchor"] + '"></a>', '### ' + _md_text(item["id"]),
            '**Requirement interpretation:** ' + _md_text(item["text"]), '#### Supporting source'])
        for evidence in item["evidences"]:
            parts.extend(_md_evidence(evidence))
        parts.append('#### CFG targets and rationale')
        if not item["bindings"]:
            parts.append('**Unbound requirement:** no CFG target is recorded. Later analysis must not silently omit it.')
        for binding in item["bindings"]:
            parts.extend(['**' + _md_text(binding["target_label"]) + '** · ' + _md_text(binding["kind"]),
                _md_pre(binding["pointer"] or '(graph root)'), _md_text(binding["reason"]),
                _md_text(binding["scope"]), '**Actual CFG value:**', _md_pre(_json(binding["value"]))])
    parts += ['## IR reverse index', 'Scope bindings do not assert individual input requirements. '
              'No binding is not a uselessness verdict.']
    for item in view["instructions"]:
        parts.append('### ' + _md_text(item["id"]) + ' · ' + _md_text(item["opcode"]) + ' · ' + _md_text(item["block_id"]))
        if not item["bindings"]:
            parts.append('No recorded requirement binding.')
        for binding in item["bindings"]:
            parts.append('- [' + _md_text(binding["requirement"]) + '](#' + binding["requirement_anchor"] + ') · '
                + _md_text(binding["target_label"]) + ' · ' + _md_text(binding["scope"]))
    parts += ['## Full source and uncited ranges', 'Not cited means no evidence references these nonblank lines. '
              'It is not a claim of omitted requirements; background need not become a task requirement.']
    for source in view["sources"]:
        parts.append('### ' + _md_text(source["path"]))
        parts.append('**Not cited:** ' + (', '.join(str(start) + ('–' + str(end) if end != start else '')
            for start, end in source["uncited_ranges"]) or 'No nonblank uncited lines.'))
        for line in source["lines"]:
            parts.append('<a id="' + line["anchor"] + '"></a>\n**Line ' + str(line["number"]) + ':**\n'
                + _md_pre(line["text"]))
    parts += ['### Source interpretation boundaries', _md_pre(_json(view["boundaries"])),
        '## Assistant semantic review', 'Separate from reference validation; not human confirmation.',
        _md_pre(view["assistant_review"])]
    return '\n\n'.join(parts) + '\n'
