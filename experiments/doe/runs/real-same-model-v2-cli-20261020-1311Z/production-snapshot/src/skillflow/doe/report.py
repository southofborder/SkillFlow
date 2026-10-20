"""A shared, read-only view for DOE material audit reports.

The report explains static relationships.  It deliberately has no sensitivity,
necessity or DOE verdict, and never reconstructs missing Data identities.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from html import escape
import json

from skillflow.propagation.conditions import payload_input_indices, payload_inputs


NOTICE = (
    "These are static review materials under the shared runtime contract, not execution logs. "
    "Candidate sets do not imply simultaneous presence; possible dependencies do not imply complete inclusion of input plaintext in the result. "
    "This stage makes no sensitivity, necessity or DOE judgment; downstream use does not prove that information is necessary."
)
SINK_NAMES = {
    "network_send": "Network send", "storage_write": "Persistent storage write",
    "context_save": "Context save", "model_observe": "Model observation",
    "external_tool": "External tool delivery", "user_output": "User output",
}
OP_NAMES = {
    "read": "Read", "receive": "Receive returned content", "deliver": "Deliver / observe",
    "write": "Write / unbind", "select_part": "Select original field",
    "exclude_parts": "Exclude fields", "update_fields": "Update fields",
    "build": "Build", "compute": "Compute", "filter_items": "Filter members",
}
LINK_NAMES = {
    "result_use": "CFG result use", "request_response": "Request and response",
    "produces_consumes": "Production and consumption", "saved_read": "Save and read",
    "observed_use": "Processing associated with observed content", "result_binding": "Public result binding",
}


def _plain(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return deepcopy(value)


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)


def _anchor(kind, identity):
    # Arbitrary identifiers are never interpolated into attributes or URL paths.
    return kind + "-" + sha256(str(identity).encode("utf-8")).hexdigest()[:20]


def _path(path):
    """Keep fields, array indexes and symbolic elements visibly distinct."""
    if not path:
        return "Whole value"
    pieces = []
    for step in path:
        if type(step) is str:
            pieces.append("Field " + json.dumps(step, ensure_ascii=False))
        elif type(step) is int:
            pieces.append("Index " + str(step))
        else:
            pieces.append("Symbolic element (scope " + str(step["scope"]) + ")")
    return " / ".join(pieces)


def _location(value):
    return value["kind"] + " / " + value["name"]


def _operand(value):
    if value["type"] == "literal":
        return "Literal " + json.dumps(value.get("literal_value"), ensure_ascii=False)
    return value["type"] + " / " + value["identifier"]


def _content_lines(value, labels):
    content = value["content"]
    label = lambda data_id: labels[data_id]
    form = content["form"]
    if form == "opaque":
        return ["Content is unexpanded; this does not imply empty data or absence of sensitive information."]
    if form == "literal":
        return ["Explicit JSON literal: " + json.dumps(content["value"], ensure_ascii=False)]
    if form == "known_parts":
        lines = ["Complete composition is declared." if content["parts_complete"] else "Only known possible components are recorded; an unknown remainder is retained."]
        return lines + [_path(part["path"]) + " → " + label(part["data"]) for part in content["parts"]]
    if form == "whole_except":
        return ["Based on " + label(content["base"]) + ", Excluded " + "; ".join(_path(path) for path in content["excluded_parts"]),
                "Unlisted content remains; origin links cannot restore excluded fields."]
    if form == "field_updates":
        return ["Based on " + label(content["base"]) + "; remaining content is retained."] + [
            _path(part["path"]) + " updated to " + label(part["data"]) for part in content["updates"]]
    if form == "subset_view":
        return ["Filtered from " + label(content["base"]) + "; member content identity is retained, without asserting that all members are actually selected.",
                "Symbolic condition (not evaluated): " + content["predicate"]]
    raise ValueError("unsupported Data content form: " + str(form))


def _data_view(value, labels):
    origin = value["origin"]
    lines = _content_lines(value, labels)
    if origin.get("acquired_from") is not None:
        lines.append("Acquisition boundary: " + origin["acquired_from"])
    if origin.get("part_of") is not None:
        lines.append("Part of " + labels[origin["part_of"]] + " / " + _path(origin["path"]))
    if origin.get("inputs"):
        lines.append("Ordered actual inputs at creation: " + " → ".join(labels[item] for item in origin["inputs"]))
    for dependency in origin.get("dependencies", []):
        relation = "Explicit derivation" if dependency["relation"] == "derived" else "Possible influence (not plaintext inclusion)"
        lines.append(relation + ": " + labels[dependency["data"]])
    if value["annotations"].get("description"):
        lines.append("Existing description: " + value["annotations"]["description"])
    return {"id": value["id"], "label": labels[value["id"]], "anchor": _anchor("data", value["id"]),
            "lines": lines, "raw": value}


def _position(position):
    parts = [position["instruction_id"], "Event " + str(position["event_index"]),
             "Operation " + str(position["op_index"])]
    if position.get("instance_index") is not None:
        parts.append("Candidate instance " + str(position["instance_index"]))
    if position.get("body_event_index") is not None:
        parts.append("Body event " + str(position["body_event_index"]))
    return " / ".join(parts)


def _operation_view(identity, value):
    record = value["record"]
    payload_indices = payload_input_indices(record)
    controls = sorted(set(range(len(record["inputs"]))) - set(payload_indices))
    return {"id": identity, "anchor": _anchor("operation", identity), "position": _position(value["position"]),
            "effect": value["effect"], "op": record["op"], "label": OP_NAMES[record["op"]],
            "inputs": record["inputs"], "payload": payload_inputs(record), "payload_indices": payload_indices,
            "control_indices": controls, "outputs": record["outputs"], "endpoints": record["endpoints"],
            "changes": record["changes"], "members": record.get("members", []), "raw": value}


def _source_view(source):
    return [{"path": file["path"], "content": file["content"]}
            for file in source["files"]]


def build_view(material, *, metrics=None):
    """Prepare one isolated presentation model for both report renderers."""
    wire = _plain(material)
    info = wire["shared_info"]
    labels = {identity: f"D{index:03}" for index, identity in enumerate(sorted(info["data"]), 1)}
    data = {identity: _data_view(value, labels) for identity, value in info["data"].items()}
    operations = {identity: _operation_view(identity, value) for identity, value in info["operations"].items()}
    instructions = {}
    for identity, ir in info["instructions"].items():
        action = info["actions"][identity]
        instructions[identity] = {"id": identity, "anchor": _anchor("ir", identity), "opcode": ir["opcode"],
            "inputs": [_operand(value) for value in ir.get("inputs", [])],
            "outputs": [_operand(value) for value in ir.get("outputs", [])],
            "constraints": ir.get("constraints", []), "operator": action["operator"], "raw": ir}
    sinks = []
    for index, item in enumerate(wire["sinks"], 1):
        sink = item["sink"]
        boundary = sink["boundary"]
        context = item["context"]
        sinks.append({"id": sink["id"], "label": f"S{index:03}", "anchor": _anchor("sink", sink["id"]),
            "type": boundary["sink_type"], "type_label": SINK_NAMES[boundary["sink_type"]],
            "level": boundary["exposure_level"], "boundary": boundary,
            "target": boundary["target"], "location": info["locations"][boundary["target"]],
            "operations": [operations[identity] for identity in sink["operations"]],
            "backward_data": [data[identity] for identity in item["backward_slice"]["data"]],
            "backward_operations": [operations[identity] for identity in item["backward_slice"]["operations"]],
            "usage_instructions": [instructions[identity] for identity in item["usage_context"]["instructions"]],
            "usage_operations": [operations[identity] for identity in item["usage_context"]["operations"]],
            "links": [{"id": identity, **info["links"][identity]} for identity in item["usage_context"]["links"]],
            "blocks": [info["blocks"][identity] for identity in context["blocks"]],
            "edges": [info["edges"][index] for index in context["edge_indices"]],
            "scopes": [{"id": identity, **info["scopes"][identity]} for identity in context["scope_ids"]],
            "orders": {identity: info.get("orders", {})[identity] for identity in item["usage_context"]["instructions"]
                       if identity in info.get("orders", {})},
            "diagnostics": context["diagnostics"], "partial_ir_ids": context["partial_ir_ids"], "raw": item})
    return {"schema_version": wire["schema_version"], "task": wire["task"],
            "runtime_contract": wire["runtime_contract"], "notice": NOTICE,
            "source": _source_view(wire["source"]), "source_metadata": {
                key: value for key, value in wire["source"].items() if key != "files"},
            "labels": labels, "data": data, "operations": operations, "instructions": instructions,
            "sinks": sinks, "metrics": deepcopy(metrics or {}),
            "constraints": info.get("constraints", []), "declared_context_keys": info.get("declared_context_keys", []),
            "shared_info": info}


def _metric_rows(metrics):
    names = {"input_chars": "Full-fact characters", "input_characters": "Full-fact characters", "input_bytes": "Full-fact UTF-8 bytes",
             "material_chars": "Review-material characters", "material_characters": "Review-material characters", "material_bytes": "Review-material UTF-8 bytes",
             "material_status": "Material coverage status", "input_status": "Upstream propagation status", "coverage": "IR record coverage",
             "missing_ir_ids": "IR without records", "input_compact_characters": "Full-fact canonical compact JSON characters",
             "material_compact_characters": "Review-material canonical compact JSON characters", "input_compact_chars": "Full-fact canonical compact JSON characters",
             "material_compact_chars": "Review-material canonical compact JSON characters", "runtime_contract_characters": "Runtime-contract text characters for this case",
             "rule_text_characters": "Runtime-contract text characters for this case"}
    return [(names.get(key, key), value) for key, value in metrics.items()]


def _coverage_notice(view):
    metrics = view["metrics"]
    status, missing = metrics.get("material_status", metrics.get("input_status")), metrics.get("missing_ir_ids", [])
    if missing or status is not None and status != "complete":
        return "These review materials are partial; IR without records: " + (", ".join(missing) or "See preparation manifest") + ". Missing slices do not establish absence of exposure."
    return None


def _md(value):
    # HTML entities keep pipes, backticks, brackets and raw tags inert even when
    # Markdown is embedded in an HTML-capable review panel.
    text = escape(str(value), quote=True)
    for char in "|`[]*_":
        text = text.replace(char, f"&#{ord(char)};")
    return text.replace("\r", "").replace("\n", "<br>")


def _md_detail(title, value):
    return ["<details><summary>" + escape(title) + "</summary>", "", "<pre>" + escape(_json(value)) + "</pre>", "", "</details>", ""]


def _md_ids(view, ids):
    return ", ".join("[" + view["labels"][identity] + "](#" + _anchor("data", identity) + ")" for identity in sorted(ids)) or "No candidates"


def _md_entity(view, identity):
    if identity in view["operations"]:
        operation = view["operations"][identity]
        return "[" + _md(operation["position"]) + "](#" + operation["anchor"] + ")"
    if identity in view["instructions"]:
        ir = view["instructions"][identity]
        return "[" + _md(identity + " / " + ir["opcode"]) + "](#" + ir["anchor"] + ")"
    return _md(identity)


def _md_slots(view, slots, indices=None):
    indexes = range(len(slots)) if indices is None else indices
    return "; ".join(str(index) + ": {" + _md_ids(view, ids) + "}" for index, ids in zip(indexes, slots)) or "No modeled arguments"


def _md_ops(view, operations):
    rows = ["| Operation position (zero-based) | Effect / operation | Actual payload inputs | Control slots | Outputs / state changes |", "|---|---|---|---|---|"]
    for operation in operations:
        out = _md_slots(view, operation["outputs"]) if operation["outputs"] else "No public local result"
        changes = [f'{_md(_location(change["location"]))}: {_md_ids(view, change["before"])} → {_md_ids(view, change["after"])} ({change["update"]})'
                   for change in operation["changes"]]
        controls = "; ".join(str(index) + ": {" + _md_ids(view, operation["inputs"][index]) + "}" for index in operation["control_indices"]) or "None"
        rows.append("| " + " | ".join(["[" + _md(operation["position"]) + "](#" + operation["anchor"] + ")", _md((operation["effect"] or "Unlabeled relationship") + " / " + operation["label"]),
                    _md_slots(view, operation["payload"], operation["payload_indices"]), controls, out + ("<br>" + "<br>".join(changes) if changes else "")]) + " |")
    return rows + [""]


def render_markdown(material, *, metrics=None):
    view = build_view(material, metrics=metrics)
    lines = ["# DOE offline sink review materials", "", view["notice"], "", "[Visual review](report.html)", "",
             "Task basis: " + ("Independent user request" if view["task"]["basis"] == "user_request" else "Declared Skill purpose (not actual user authorization)") + ".", "",
             "Runtime contract: " + _md(view["runtime_contract"]["version"]) + "; SHA-256: " + _md(view["runtime_contract"]["sha256"]) + ".", "",
             f'Actual sinks: {len(view["sinks"])}; Shared Data: {len(view["data"])}; Shared operations: {len(view["operations"])}.', "",
             "D short names are for readability; data cards retain complete Data IDs. Operation coordinates are zero-based. Parent wholes in origin tracing are not actual payload; control slots govern inclusion or observation and are not delivered plaintext.", ""]
    if _coverage_notice(view):
        lines += ["**" + _md(_coverage_notice(view)) + "**", ""]
    if view["task"].get("text") is not None:
        lines += ["Independent request text: ", "", "<pre>" + escape(view["task"]["text"]) + "</pre>", ""]
    if view["metrics"]:
        lines += ["## Material size", "", "| Metric | Actual size |", "|---|---|"]
        lines += ["| " + _md(name) + " | " + _md(value) + " |" for name, value in _metric_rows(view["metrics"])] + ["", "These are character/byte measurements, not model-tokenizer token counts.", ""]
    for sink in view["sinks"]:
        location = sink["location"]
        lines += ['<a id="' + sink["anchor"] + '"></a>', "", "## " + sink["label"] + " · " + sink["type_label"], "",
                  "Receiving boundary: " + _md(sink["target"] + " · " + _location(location)) + "; Access: " + _md(location["access_scope"]) + "; Retention: " + _md(location["retention"] or "Retention period not modeled") + "; Boundary level: " + str(sink["level"]) + ".", "",
                  "### Actual payload", ""]
        lines += _md_ops(view, sink["operations"])
        if sink["scopes"]:
            lines += ["Per-element candidate instances (no cross-instance pairing; not actual execution counts): ", ""]
            for scope in sink["scopes"]:
                lines += [f'- {_md(scope["id"])}: Collection {_md_ids(view, [scope["collection"]])} → Element {_md_ids(view, [scope["element"]])}; Instance index {scope["instance_index"]}.']
            lines += [""]
        lines += ["### Origin and processing", "", "The following data explains origin and content relationships; parent wholes are not counted again as actual payload.", ""]
        for data in sink["backward_data"]:
            lines += ["- " + _md_ids(view, [data["id"]]) + ": " + _md("; ".join(data["lines"]))]
        lines += [""] + _md_ops(view, sink["backward_operations"])
        lines += ["### Current and downstream use facts", "", "These usage relationships are not necessity conclusions; storage without a later read is not automatically useless.", ""]
        for ir in sink["usage_instructions"]:
            lines += ["- " + _md(ir["id"] + " / " + ir["opcode"]) + "; Inputs: " + _md("; ".join(ir["inputs"]) or "None") + "; Outputs: " + _md("; ".join(ir["outputs"]) or "None")]
            lines += ["  - Constraints: " + _md(constraint) for constraint in ir["constraints"]]
        lines += [""] + _md_ops(view, sink["usage_operations"])
        for link in sink["links"]:
            lines += ["- " + _md(LINK_NAMES.get(link["kind"], link["kind"])) + ": " + _md_entity(view, link["source"]) + " → " + _md_entity(view, link["target"]) + "; Related Data: " + _md_ids(view, link["data_ids"]) + ("; CFG result: " + _md(link["result"]) if link.get("result") else "")]
        lines += ["", "### Conditions, order and limitations", ""]
        if sink["partial_ir_ids"]:
            lines += ["**Partial order: " + _md(", ".join(sink["partial_ir_ids"])) + ". Candidates are not one definite execution trace.**", ""]
        if sink["orders"]:
            lines += _md_detail("Recorded fixed/partial order and required precedence", sink["orders"])
        for block in sink["blocks"]:
            lines += ["- " + _md(block["block_id"] + " / " + block["block_name"])]
            lines += ["  - " + _md(constraint) for constraint in block["constraints"]]
        for edge in sink["edges"]:
            lines += ["- " + _md(edge["source_block_id"] + " → " + edge["target_block_id"] + ": " + (edge["condition_text"] or "No condition text recorded; unconditional truth is not inferred"))]
        lines += [""]
        if sink["diagnostics"]:
            lines += _md_detail("Related binding and capability diagnostics", sink["diagnostics"])
        lines += ['<details><summary>Complete sink ID</summary>', '', '<pre>' + escape(sink["id"]) + '</pre>', '', '</details>', '']
    lines += ["## Shared Data", "", "Each complete Data object appears only here; sensitivity judgment has not been performed.", ""]
    for data in view["data"].values():
        lines += ['<a id="' + data["anchor"] + '"></a>', "", "### " + data["label"], "", "Complete ID: " + _md(data["id"]), ""]
        lines += ["- " + _md(line) for line in data["lines"]] + [""]
        lines += _md_detail("Complete Data object", data["raw"])
    lines += ["## Shared raw operation records", "", "Complete operation records are stored once; select their coordinates in the operation table above.", ""]
    for operation in view["operations"].values():
        lines += ['<a id="' + operation["anchor"] + '"></a>', ""]
        lines += _md_detail(operation["id"] + " / " + operation["position"], operation["raw"])
    lines += ["## Shared raw IR records", "", "Complete source-graph IR fields appear once; usage sections above show only related operands and constraints.", ""]
    for ir in view["instructions"].values():
        lines += ['<a id="' + ir["anchor"] + '"></a>', ""]
        lines += _md_detail(ir["id"] + " / " + ir["opcode"], ir["raw"])
    lines += ["## Complete source and shared constraints", "", "The complete readable source appears once, including field descriptions without Data entries and global prohibitions.", ""]
    for file in view["source"]:
        lines += ['<details><summary>' + escape(file["path"]) + '</summary>', "", "<pre>" + escape(file["content"]) + "</pre>", "", "</details>", ""]
    lines += _md_detail("Source inventory and binary/uninterpreted-content boundaries", view["source_metadata"])
    lines += _md_detail("Graph-wide constraints and declared context", {"constraints": view["constraints"], "declared_context_keys": view["declared_context_keys"]})
    lines += _md_detail("Complete shared runtime contract", view["runtime_contract"])
    return "\n".join(lines)


def _h_ids(view, ids):
    return ", ".join('<a href="#' + _anchor("data", identity) + '">' + view["labels"][identity] + "</a>" for identity in sorted(ids)) or "No candidates"


def _h_entity(view, identity):
    if identity in view["operations"]:
        operation = view["operations"][identity]
        return '<a href="#' + operation["anchor"] + '">' + escape(operation["position"]) + '</a>'
    if identity in view["instructions"]:
        ir = view["instructions"][identity]
        return '<a href="#' + ir["anchor"] + '">' + escape(identity + ' / ' + ir["opcode"]) + '</a>'
    return escape(identity)


def _h_slots(view, slots, indices=None):
    indexes = range(len(slots)) if indices is None else indices
    return "<br>".join('<span class="slot">Slot ' + str(index) + ": {" + _h_ids(view, ids) + "}</span>" for index, ids in zip(indexes, slots)) or "No modeled arguments"


def _h_detail(title, value):
    return "<details><summary>" + escape(title) + "</summary><pre>" + escape(_json(value)) + "</pre></details>"


def _h_ops(view, operations):
    if not operations:
        return '<p class="muted">No additional operation record; this does not imply the action is useless.</p>'
    rows = []
    for operation in operations:
        controls = "<br>".join("Slot " + str(index) + ": {" + _h_ids(view, operation["inputs"][index]) + "}" for index in operation["control_indices"]) or "None"
        outputs = _h_slots(view, operation["outputs"]) if operation["outputs"] else "No local output"
        changes = "".join('<div class="change">' + escape(_location(change["location"])) + ": " + _h_ids(view, change["before"]) + " → " + _h_ids(view, change["after"]) + " (" + change["update"] + ")</div>" for change in operation["changes"])
        endpoints = "<br>".join(escape(_location(endpoint)) for endpoint in operation["endpoints"]) or "None"
        members = ""
        if operation["members"]:
            members = "<details><summary>Build members and condition slots</summary><ul>" + "".join("<li>" + escape(_path(member["path"])) + "; Value slot " + str(member["value_input_index"]) + "; Condition slot " + str(member["when_input_index"]) + "</li>" for member in operation["members"]) + "</ul></details>"
        cells = ['<a href="#' + operation["anchor"] + '">' + escape(operation["position"]) + '</a>', escape((operation["effect"] or "Unlabeled relationship") + " / " + operation["label"]),
                 _h_slots(view, operation["payload"], operation["payload_indices"]), controls, endpoints, outputs + changes + members]
        rows.append('<tr data-operation="' + escape(operation["id"], quote=True) + '">' + "".join("<td>" + cell + "</td>" for cell in cells) + "</tr>")
    return '<div class="table-wrap"><table><thead><tr><th>Operation coordinates (zero-based)</th><th>Effect / operation</th><th>Actual payload inputs</th><th>Control slots</th><th>Interaction locations</th><th>Outputs / state changes</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>"


def render_html(material, *, metrics=None):
    view = build_view(material, metrics=metrics)
    output = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'none\'; connect-src \'none\'"><title>DOE offline sink review materials</title>',
        '<style>body{margin:0;background:#f5f7fa;color:#172234;font:15px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1440px;margin:auto;padding:28px}h1,h2,h3{line-height:1.3}a{color:#1559b8}code,pre{font-family:ui-monospace,Consolas,monospace}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f8;border:1px solid #e1e6ef;padding:14px;border-radius:6px}article,.shared{background:white;border:1px solid #dce3ed;border-radius:10px;padding:22px;margin:22px 0}nav{display:flex;gap:10px;flex-wrap:wrap;margin:15px 0}.notice{padding:16px;background:#e9f1fb;border-left:4px solid #2369b5}.warning{padding:12px;background:#fff5da;border-left:4px solid #d19a20}.muted{color:#58697f}.tag{display:inline-block;border-radius:4px;padding:2px 7px;background:#eef2f7;margin-right:6px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #dce3ed;text-align:left;padding:10px;vertical-align:top;overflow-wrap:anywhere}th{background:#eef2f8}.table-wrap{overflow-x:auto}summary{cursor:pointer;font-weight:600}details{margin:12px 0}li{margin:5px 0}.change{border-top:1px dashed #ccd5e0;padding-top:5px;margin-top:5px}.exact-id{overflow-wrap:anywhere;font-size:12px;color:#58697f}.data-card{border-top:1px solid #dce3ed;padding:15px 0}.slot{white-space:normal}</style></head><body><main>',
        '<h1>DOE offline sink review materials</h1><p class="notice">' + escape(view["notice"]) + '</p>',
        '<p><a href="report.md">Markdown report</a></p>',
        '<p>Task basis: <strong>' + ("Independent user request" if view["task"]["basis"] == "user_request" else "Declared Skill purpose") + '</strong>. The program records the basis without preemptively interpreting purpose or necessary scope.</p>',
        '<p>Runtime contract: <code>' + escape(view["runtime_contract"]["version"]) + '</code><br>SHA-256: <span class="exact-id">' + escape(view["runtime_contract"]["sha256"]) + '</span></p>',
        '<p>Actual sinks ' + str(len(view["sinks"])) + '; Shared Data ' + str(len(view["data"])) + '; Shared operations ' + str(len(view["operations"])) + '. D short names are for readability; data cards retain complete identities. Control slots are not delivered payload, and operation coordinates are zero-based.</p>']
    if _coverage_notice(view):
        output.append('<p class="warning">' + escape(_coverage_notice(view)) + '</p>')
    if view["task"].get("text") is not None:
        output.append('<details><summary>Independent user request text</summary><pre>' + escape(view["task"]["text"]) + '</pre></details>')
    if view["metrics"]:
        output.append('<details><summary>Actual character and byte sizes (not token counts)</summary><table><tbody>' + "".join("<tr><th>" + escape(name) + "</th><td>" + escape(str(value)) + "</td></tr>" for name, value in _metric_rows(view["metrics"])) + '</tbody></table></details>')
    output.append('<nav>' + "".join('<a class="tag" href="#' + sink["anchor"] + '">' + sink["label"] + ' · ' + sink["type_label"] + '</a>' for sink in view["sinks"]) + '<a class="tag" href="#shared-data">Shared Data</a><a class="tag" href="#full-source">Complete source</a></nav>')
    if not view["sinks"]:
        output.append('<p class="warning">No actual sink slice was produced. Check the preparation manifest and upstream coverage for completeness; this does not establish absence of exposure.</p>')
    for sink in view["sinks"]:
        location = sink["location"]
        output += ['<article id="' + sink["anchor"] + '"><h2>' + sink["label"] + ' · ' + sink["type_label"] + '</h2>',
            '<p><strong>Receiving boundary: </strong>' + escape(sink["target"] + ' · ' + _location(location)) + '<br><strong>Access / retention: </strong>' + escape(location["access_scope"] + ' / ' + (location["retention"] or 'Retention period not modeled')) + '; Boundary level ' + str(sink["level"]) + ' (not sensitivity or risk).</p>',
            '<h3>1. Actual payload</h3>', _h_ops(view, sink["operations"])]
        if sink["scopes"]:
            output.append('<p class="notice">Per-element candidate instances remain separate; recipient and body cannot be combined across instances. These are not actual collection lengths or execution counts.</p><ul>' + "".join('<li>' + escape(scope["id"]) + ': Collection ' + _h_ids(view, [scope["collection"]]) + ' → Element ' + _h_ids(view, [scope["element"]]) + '; Instance index ' + str(scope["instance_index"]) + '</li>' for scope in sink["scopes"]) + '</ul>')
        output += ['<h3>2. Origin and processing</h3><p class="muted">Parent wholes explain origin without enlarging the payload. Source fields without independent Data entries remain reviewable in the complete source below.</p><ul>',
            "".join('<li>' + _h_ids(view, [data["id"]]) + ': ' + escape('; '.join(data["lines"])) + '</li>' for data in sink["backward_data"]), '</ul>', _h_ops(view, sink["backward_operations"]),
            '<h3>3. Current and downstream use facts</h3><p class="muted">Only related production, consumption and return relationships are shown, without judging necessity. Persistent storage itself may be a task outcome.</p>']
        for ir in sink["usage_instructions"]:
            output.append('<details><summary>' + escape(ir["id"] + ' / ' + ir["opcode"]) + '</summary><p>Operator: ' + escape(', '.join(ir["operator"]) or '[]') + '</p><p>Inputs: ' + escape('; '.join(ir["inputs"]) or 'None') + '<br>Outputs: ' + escape('; '.join(ir["outputs"]) or 'None') + '</p><ul>' + ''.join('<li>' + escape(constraint) + '</li>' for constraint in ir["constraints"]) + '</ul><a href="#' + ir["anchor"] + '">Complete IR fields</a></details>')
        output.append(_h_ops(view, sink["usage_operations"]))
        output.append('<ul>' + ''.join('<li>' + escape(LINK_NAMES.get(link["kind"], link["kind"])) + ': ' + _h_entity(view, link["source"]) + ' → ' + _h_entity(view, link["target"]) + '; Data ' + _h_ids(view, link["data_ids"]) + ('; Result ' + escape(link["result"]) if link.get("result") else '') + '</li>' for link in sink["links"]) + '</ul>')
        output.append('<h3>4. Conditions, versions and ordering boundaries</h3>')
        if sink["partial_ir_ids"]:
            output.append('<p class="warning">Partial order: ' + escape(', '.join(sink["partial_ir_ids"])) + '. Operation table positions do not imply one definite execution trace; candidate conditions need not hold simultaneously.</p>')
        if sink["orders"]:
            output.append(_h_detail('Recorded fixed/partial order and required precedence', sink["orders"]))
        output.append('<ul>' + ''.join('<li>' + escape(block["block_id"] + ' / ' + block["block_name"]) + '<ul>' + ''.join('<li>' + escape(constraint) + '</li>' for constraint in block["constraints"]) + '</ul></li>' for block in sink["blocks"]) + ''.join('<li>' + escape(edge["source_block_id"] + ' → ' + edge["target_block_id"] + ': ' + (edge["condition_text"] or 'No condition text recorded; unconditional truth is not inferred')) + '</li>' for edge in sink["edges"]) + '</ul>')
        if sink["diagnostics"]:
            output.append(_h_detail('Related binding and capability diagnostics', sink["diagnostics"]))
        output.append('<details><summary>Complete sink ID</summary><code class="exact-id">' + escape(sink["id"]) + '</code></details></article>')
    output.append('<section class="shared" id="shared-data"><h2>Shared Data</h2><p>Each complete object appears only here. Sensitivity and necessity have not been judged.</p>')
    for data in view["data"].values():
        output.append('<div class="data-card" id="' + data["anchor"] + '"><h3>' + data["label"] + '</h3><div class="exact-id">' + escape(data["id"]) + '</div><ul>' + ''.join('<li>' + escape(line) + '</li>' for line in data["lines"]) + '</ul>' + _h_detail('Complete Data object', data["raw"]) + '</div>')
    output.append('</section><section class="shared"><h2>Shared raw operation records</h2><p>Complete operation records are stored once; select their coordinates in the table above.</p>')
    for operation in view["operations"].values():
        output.append('<div id="' + operation["anchor"] + '">' + _h_detail(operation["id"] + ' / ' + operation["position"], operation["raw"]) + '</div>')
    output.append('</section><section class="shared"><h2>Shared raw IR records</h2><p>Complete IR fields appear once here; use sections above retain related operands and constraints.</p>')
    for ir in view["instructions"].values():
        output.append('<div id="' + ir["anchor"] + '">' + _h_detail(ir["id"] + ' / ' + ir["opcode"], ir["raw"]) + '</div>')
    output.append('</section><section class="shared" id="full-source"><h2>Complete source and shared constraints</h2><p>The complete readable source appears once, including field descriptions without independent Data IDs and global prohibitions.</p>')
    for file in view["source"]:
        output.append('<details><summary>' + escape(file["path"]) + '</summary><pre>' + escape(file["content"]) + '</pre></details>')
    output += [_h_detail('Source inventory and binary/uninterpreted-content boundaries', view["source_metadata"]),
               _h_detail('Graph-wide constraints and declared context', {"constraints": view["constraints"], "declared_context_keys": view["declared_context_keys"]}),
               _h_detail('Complete shared runtime contract', view["runtime_contract"]), '</section></main></body></html>']
    return '\n'.join(output)
