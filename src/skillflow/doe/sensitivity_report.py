"""English views of declared sensitivity and sink-specific demand comparisons."""
from __future__ import annotations

from copy import deepcopy
from collections import Counter, defaultdict
from functools import lru_cache
from hashlib import sha256
from html import escape
import json

from skillflow.common.source_evidence import extract_source_lines
from .sensitivity_results import resolve_data_review
from .input_report import input_edit_chunks


NOTICE = (
    "Sensitivity coverage is limited to explicit declarations. Undeclared content is not proven non-sensitive. "
    "Comparisons apply to the recorded processing and task-demand rules, not to all possible implementations. "
    "Completed input assessments identify removable ranges under the reviewed input contracts. "
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


def placeholder_sites(compiled):
    """Declared symbolic relations, including sites on paths that were never reached."""
    for ir, spec in compiled["ir_semantics"].items():
        for i, event in enumerate(spec["events"]):
            children = enumerate(event["body"]) if event.get("kind") == "for_each" else [(None, event)]
            for j, child in children:
                path = ["events", i] if j is None else ["events", i, "body", j]
                for k, op in enumerate(child["atomic_ops"]):
                    if op["op"] == "placeholder":
                        yield {"instruction": ir, "operation_path": [*path, "atomic_ops", k],
                               **{key: op[key] for key in ("kind", "reason", "inputs", "output", "location",
                                                          "may_write", "evidences") if key in op}}


def build_view(review, *, metadata=None, compact=False):
    """Share ordering, conclusions and exact evidence excerpts across renderers."""
    result, index = review.to_dict(), review.index_dict()
    metadata = dict(metadata or {})
    # A prepared/loaded review owns its full demand result, including ranges
    # that carry no sensitivity label. Caller metadata cannot hide those rows.
    if hasattr(review, "demand_dict"):
        try:
            metadata["demand"] = review.demand_dict()
        except ValueError:
            # Display-only legacy fixtures have no bound demand material.
            pass
    files = metadata.get("source_files", {})
    @lru_cache(maxsize=None)
    def excerpt(file, start, end):
        return extract_source_lines(files[file], start, end) if file in files else None

    requirements = {row["id"]: row for row in metadata.get("task", {}).get("requirements", [])}
    task = deepcopy(metadata.get("task", {}))
    task_evidences = []
    for owner, item in [("purpose", task.get("purpose", {})), *requirements.items()]:
        for evidence in item.get("evidences", []):
            quote = excerpt(evidence["file"], evidence["start_line"], evidence["end_line"])
            task_evidences.append({"owner": owner, "reference": deepcopy(evidence), "quote": quote})
    diagnostics = {row["id"]: row for row in result["diagnostics"]}
    assessments = {row["id"]: row for row in metadata.get("demand", {}).get("input_assessments", [])}
    demand_sinks = {row["id"]: row for row in metadata.get("demand", {}).get("sinks", [])}
    declarations = []
    for identity, entry in index.get("declarations", {}).items():
        declaration = entry["declaration"]
        evidences = []
        for evidence in declaration.get("evidences", []):
            quote = excerpt(evidence["file"], evidence["start_line"], evidence["end_line"])
            evidences.append({"reference": evidence, "quote": quote})
        declarations.append({"id": identity, "anchor": _anchor("declaration", identity),
            "value": entry, "evidences": evidences})
    sinks = []
    counts = {key: 0 for key in CONCLUSIONS}
    for sink in result["sinks"]:
        rows = []
        for compact_item in sink["data_reviews"]:
            counts[compact_item["conclusion"]] += 1
            if compact:
                continue
            item = resolve_data_review(compact_item, sink, result["derivations"]["sensitivity"])
            label = ("Unresolved comparison because of analysis limitations" if item["limitations"]
                     else CONCLUSIONS[item["conclusion"]])
            rows.append({"id": item["id"], "value": item, "conclusion": label,
                "declaration_anchor": _anchor("declaration", item["declaration_id"]),
                "derivation_anchor": _anchor("sensitivity", item["derivation_id"]),
                "demands": [{"id": identity, "anchor": _anchor("demand", identity)}
                            for identity in item["demand_refs"]],
                "constraints": [{"id": identity, "anchor": _anchor("preservation", identity)}
                                for identity in item["constraint_refs"]],
                "input_assessments": [assessments[ref] for ref in item.get("assessment_refs", [])],
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
    goals = {g["id"]: g for g in demand.get("goals", [])}
    sink_ids = []
    by_derivation = defaultdict(set)
    for position, sink in enumerate(demand.get("sinks", [])):
        sink_ids.append(sink["id"])
        for ref in (*sink["demanded_information"], *sink["conservative_retention"]):
            by_derivation[ref].add(position)
    for requirement in task.get("requirements", []):
        req = requirement["id"]
        trace = deepcopy(trace_index.get(req, {"requirement_id": req, "seeds": []}))
        trace["requirement"] = deepcopy(requirement)
        trace["realization"] = deepcopy(demand.get("coverage", {}).get("requirements", {}).get(req))
        for seed in trace["seeds"]:
            seed["compiled_goal"] = deepcopy(goals.get(seed["goal_id"]))
            positions = {pos for ref in seed["derivation_ids"] for pos in by_derivation.get(ref, ())}
            seed["sink_ids"] = [sink_ids[pos] for pos in sorted(positions)]
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
        "instruction_coverage": dict(sorted(Counter(demand.get("coverage", {}).get("upstream", {}).values()).items())),
        "placeholder_sites": metadata.get("placeholder_sites", []),
        "input_assessments": deepcopy(demand.get("input_assessments", [])),
        "input_findings": deepcopy(demand.get("input_findings", [])),
        "constraint_checks": result["constraints"]["checks"],
        "sinks": sinks, "derivations": derivations, "diagnostics": result["diagnostics"],
        "signals": result["derivations"]["sensitivity"],
        "declaration_aliases": result.get("declaration_aliases", {}), "index": index}


def _pre(value):
    return "<pre>" + escape(_json(value)) + "</pre>"


def _info(item):
    text = item["label"] + " / " + item["property"] + " / " + _json(item["path"])
    if item.get("excluded_paths"):
        text += "; excluding " + _json(item["excluded_paths"])
    return text


def _input_title(item):
    position = "acquisition output" if item["node_kind"] == "acquisition_output" else "input"
    owner = item["operation_id"] or item["instruction_id"]
    statuses = ", ".join(sorted({row["status"] for row in item["ranges"]})) or item["coverage"]
    return f"{owner} / {position} {item['input_index']} ({item['node_kind']}) — {statuses}"


def _link(kind, identity, label=None):
    return '<a href="#' + _anchor(kind, identity) + '">' + escape(label or identity) + '</a>'


def _details(kind, identity, title, value):
    return ('<details id="' + _anchor(kind, identity) + '"><summary>'
            + escape(title) + '</summary>' + _pre(value) + '</details>')


class _ReferenceGroups:
    """Publish identical candidate reference lists once in first-use order."""

    def __init__(self):
        self.entries = {}

    def link(self, kind, references):
        if not references:
            return ""
        key = kind, tuple(references)
        number = self.entries.setdefault(key, len(self.entries) + 1)
        return _link("references", number, f"{kind} ({len(references)})")

    def sections(self):
        for (kind, references), number in self.entries.items():
            yield ('<details id="' + _anchor("references", number) + '"><summary>'
                   + escape(kind) + f' references ({len(references)})</summary>')
            for identity in references:
                yield _link(kind, identity) + " "
            yield "</details>"


def _report_body(view, groups):
    yield '<p>' + escape(view["notice"]) + '</p>'
    yield ('<p>Status: ' + escape(view["status"]) + ' · ' + escape(view["schema_version"])
           + '<br>Candidate origin: ' + escape(view["candidate_origin"]) + ' · '
           + escape(view["declaration_source"]) + '</p>')
    yield ('<nav><a href="#inputs">All input assessments</a> · <a href="#sinks">Sink comparisons</a> · '
           '<a href="#declarations">Declarations</a> · <a href="' + escape(view["business_filename"], quote=True)
           + '">Business JSON</a></nav>')
    for title, value in (("Instruction coverage", view["instruction_coverage"]),
                         ("Declared symbolic operations", view["placeholder_sites"]),
                         ("Coverage", view["coverage"]), ("Range comparisons", view["counts"]),
                         ("Forward constraint checks", view["constraint_checks"]),
                         ("Task provenance", view["task_provenance"]), ("Task and demand basis", view["task"]),
                         ("Task source evidence", view["task_evidences"])):
        yield "<h2>" + title + "</h2>" + _pre(value)
    yield "<h2>Source → Task → demands correspondence</h2>"
    for trace in view["traceability"]:
        yield _details("requirement", trace["requirement_id"], trace["requirement_id"], trace)
    yield '<h2 id="inputs">All input assessments</h2>'
    yield from input_edit_chunks(view["input_assessments"])
    for item in view["input_assessments"]:
        yield _details("input", item["id"], _input_title(item), item)
    yield "<h3>Semantic findings</h3>" + _pre(view["input_findings"])
    yield '<h2 id="sinks">Sink comparisons</h2>'
    for sink in view["sinks"]:
        yield '<h3 id="' + sink["anchor"] + '">' + escape(sink["id"]) + '</h3>'
        data = sink["value"]
        yield _pre({key: data[key] for key in ("boundary", "actual_payload", "related_requirements")})
        if sink["demand"] is not None:
            yield "<details><summary>Boundary preservation demand</summary>" + _pre(sink["demand"]) + "</details>"
        if data["limitations"]:
            yield "<p>Sink limitations " + groups.link("diagnostic", data["limitations"]) + "</p>"
        if not data["data_reviews"]:
            yield "<p>No declared sensitive range reaches this sink. This is not a non-sensitive or no-DOE certificate.</p>"
        for candidate in data["data_reviews"]:
            row = resolve_data_review(candidate, data, view["signals"])
            links = [_link("declaration", row["declaration_id"], "Declaration"),
                     _link("sensitivity", row["derivation_id"], "Sensitivity derivation")]
            for key, kind in (("demand_refs", "demand"), ("constraint_refs", "preservation"),
                              ("assessment_refs", "input"), ("limitations", "diagnostic")):
                link = groups.link(kind, row.get(key, ()))
                if link:
                    links.append(link)
            conclusion = ("Unresolved comparison because of analysis limitations" if row["limitations"]
                          else CONCLUSIONS[row["conclusion"]])
            yield ('<details id="' + _anchor("comparison", row["id"]) + '"><summary>' + escape(conclusion)
                   + " · " + escape(row["operation_id"]) + " / input " + str(row["input_index"])
                   + " · " + escape(_info(row)) + "</summary><p>" + escape(row["id"]) + " · "
                   + escape(row["data_id"]) + " · " + escape(row["relation"]) + "</p><p>"
                   + escape(row["reason"]) + "</p>" + " · ".join(links)
                   + (_pre(row["reduction"]) if row["reduction"] is not None else "") + "</details>")
    yield "<h2>Comparison references</h2>"
    yield from groups.sections()
    yield '<h2 id="declarations">Shared declarations and source evidence</h2>'
    if not view["declarations"]:
        yield ("<p>No explicit sensitivity declarations. Unknown source remainder is retained in facts, "
               "but is not assigned invented sensitive fields or labels.</p>")
    evidence_groups = {}
    for declaration in view["declarations"]:
        yield '<h3 id="' + declaration["anchor"] + '">' + escape(declaration["id"]) + '</h3>'
        yield _pre(declaration["value"])
        aliases = view["declaration_aliases"].get(declaration["id"], ())
        if aliases:
            yield "<p>Source declaration sites: " + " · ".join(_link("declaration", ref) for ref in aliases) + "</p>"
        for evidence in declaration["evidences"]:
            ref = evidence["reference"]
            key = ref["file"], ref["start_line"], ref["end_line"]
            number, _ = evidence_groups.setdefault(key, (len(evidence_groups) + 1, evidence["quote"]))
            yield _link("excerpt", number, f"{key[0]} lines {key[1]}–{key[2]}")
    for key, (number, quote) in evidence_groups.items():
        yield _details("excerpt", number, f"{key[0]} lines {key[1]}–{key[2]}", quote)
    yield "<h2>Shared derivations</h2>"
    for item in view["derivations"]:
        yield _details(item["kind"], item["id"], item["kind"] + " · " + item["id"], item["value"])
    yield "<h2>Diagnostics and limitations</h2>"
    for diagnostic in view["diagnostics"]:
        yield _details("diagnostic", diagnostic["id"], diagnostic["id"], diagnostic)


def report_chunks(view, *, markdown=False):
    """Generate HTML fragments common to both self-contained, linked documents."""
    title = "Sensitivity and sink-demand comparisons"
    if markdown:
        yield "# " + title + "\n\n"
    else:
        yield ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
               '<meta name="viewport" content="width=device-width,initial-scale=1"><title>'
               + title + '</title><style>body{max-width:1000px;margin:auto;padding:2rem;'
               'font:16px/1.5 system-ui;color:#172334}pre{white-space:pre-wrap;background:#f4f6fa;'
               'padding:1em}body,pre{overflow-wrap:anywhere}details{margin:.5rem 0}summary{cursor:pointer}'
               'a{color:#145a9d}</style></head><body><main><h1>' + title + '</h1>\n')
    for block in _report_body(view, _ReferenceGroups()):
        yield block + "\n\n"
    if not markdown:
        yield "</main></body></html>\n"


def render_html(review, *, metadata=None):
    return "".join(report_chunks(build_view(review, metadata=metadata, compact=True)))


def render_markdown(review, *, metadata=None):
    return "".join(report_chunks(build_view(review, metadata=metadata, compact=True), markdown=True))
