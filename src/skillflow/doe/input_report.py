"""Shared English summary for all-input edits, including nonsensitive data."""
from html import escape
import json


def render_input_edits(assessments):
    rows = []
    for assessment in assessments:
        location = assessment.get("location", {})
        for decision in assessment.get("ranges", []):
            if decision["status"] != "deletable":
                continue
            modification = decision.get("modification")
            kind = modification["kind"] if modification else "edit not established"
            selector = {k: decision[k] for k in ("property", "path", "excluded_paths")}
            source = "; ".join(span["file"] + ":" + str(span["start_line"]) + "–" + str(span["end_line"])
                + " (" + span["evidence_origin"] + ")" for span in location.get("source_spans", [])) or "No source span supplied"
            coordinates = ["CFG: " + location.get("cfg_pointer", "not supplied")]
            coordinates.extend("raw: " + site["pointer"] for site in location.get("raw_annotation_sites", []))
            coordinates.extend("wire: " + site["pointer"] for site in location.get("wire_annotation_sites", []))
            coordinates.extend("metadata binding: " + site["pointer"] for site in location.get("metadata_binding_sites", []))
            reason = modification["reason"] if modification else decision.get("modification_limit") or decision["reason"]
            projection = assessment.get("retrieval_projection")
            if projection is not None:
                reason += " Retrieval projection: " + projection["status"] + ". " + projection["reason"]
            cells = [assessment["id"], kind, json.dumps(selector, ensure_ascii=False), source,
                     "\n".join(coordinates), reason]
            rows.append("<tr>" + "".join("<td>" + escape(cell) + "</td>" for cell in cells) + "</tr>")
    if not rows:
        return "<p>No completed input deletion is established.</p>"
    return ("<table><thead><tr><th>Input use</th><th>Modification type</th><th>Information range</th>"
            "<th>Source evidence</th><th>Actual locations</th><th>Scope and limits</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")
