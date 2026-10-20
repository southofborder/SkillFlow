"""English joint semantic annotation records; no final DOE judgment."""
from __future__ import annotations

import json

from skillflow.propagation.material import evidence_reference
from skillflow.propagation.contracts.runtime_contract import runtime_contract_binding
from skillflow.propagation.contracts.runtime_contract import validate_runtime_contract_binding

STATUS_LABELS = {"complete": "Annotation record complete", "semantic_failure": "Semantic annotation could not be completed",
                 "input_error": "Input error", "invalid_response": "Invalid response",
                 "execution_error": "Call execution error", "interrupted": "Interrupted"}


def _cell(value):
    return str(value).replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def _effect_steps(profile, partial=False):
    steps = "<br>".join(
        f"{index + 1}. {effect}" + (" (context write)" if effect == "context_write" else "")
        for index, effect in enumerate([event["effect"] for outer in profile["events"]
            for event in (outer["body"] if outer.get("kind") == "for_each" else [outer]) if event["effect"] is not None])
    ) or "[] (no recorded effects; not a no-op; inspect the action and bindings)"
    return ("Partial order; retain possible arrangements under causal constraints.<br>" if partial else "") + steps


def render_report(result, material=None, *, call_root=""):
    binding = result.get("runtime_contract")
    if binding is not None:
        binding = validate_runtime_contract_binding(binding)
    if material is not None and "runtime_contract" in material:
        material_binding = runtime_contract_binding(material["runtime_contract"])
        if binding is not None and binding != material_binding:
            raise ValueError("report abstract runtime contract binding differs from material")
        binding = material_binding
    contract_line = (
        f"Abstract runtime contract: `{binding['version']}`; digest: `{binding['sha256']}`."
        if binding is not None else "No contract identity was supplied; the execution assumptions cannot be verified from this report."
    )
    lines = [f"# Joint semantic annotation: {result['run_id']}", "",
             f"Status: **{STATUS_LABELS.get(result['status'], result['status'])}** (`{result['status']}`)", "",
             "These are static possibilities under the contract, not an execution trace. Defaults do not establish actual reads or observations; explicit local acquisition, return or isolation mechanisms constrain their scope.", "",
             contract_line, "",
             result["reason"], "", result["notice"], "",
             "Calls, JSON normalizations and model corrections are counted separately:", "",
             "```json", json.dumps(result.get("counts", {}), ensure_ascii=False, indent=2), "```", "",
             f"Graph digest: `{result['graph_sha256']}`", "",
             "[Compiled semantics, locations and sinks](audit/compiled-response.json) · [Location evidence](audit/location-evidences.json) · [Validation record](validation.json) · [Run result](result.json)", "",
             "## Execution issues and capability boundaries", ""]
    if result.get("error_kind"):
        lines.append(f"Error category: `{result['error_kind']}`.")
    request = result.get("request_validation")
    if result.get("response_chain"):
        lines += ["", "[Recorded response chain](" + call_root + "calls/annotation/chain.json). "
                  "Raw responses are retained unchanged. A normalized request has a "
                  "normalization.json receipt beside its validation.json; validation binds both "
                  "the raw response and the candidate. Parsed specifications are not raw model text.", ""]
        for attempt in result["response_chain"]["attempts"]:
            if attempt["validation_sha256"] is not None:
                path = call_root + attempt["call"]
                lines += [f"- `{attempt['call']}`: [raw response]({path}/response.json) · "
                          f"[candidate validation]({path}/validation.json)"]
    if request is not None:
        lines.extend(["", "Request identity validation (not a semantic correctness proof):", "",
                      "```json", json.dumps(request, ensure_ascii=False, indent=2), "```", ""])
    for error in result.get("validation", {}).get("errors", []):
        lines.append("- " + error)
    if not result.get("validation", {}).get("errors"):
        lines.append("No execution issue was recorded; this is not human confirmation of the annotation."
                     if result["status"] == "complete" else result["reason"])
    lines.extend(["", "## Sink boundaries and fixed levels", "",
                  "The program derives types and levels from location properties and delivery/write operations. Levels describe access and retention, not sensitivity, danger, task necessity or DOE conclusions. Symbolic operations will bind actual data versions during propagation.", "",
                  "| IR / event / operation | Boundary | Type | Level | Access / retention | Scope |",
                  "|---|---|---|---|---|"])
    for sink in result.get("sink_boundaries", []):
        location = result.get("locations", {}).get(sink["target"], {})
        event = str(sink["event_index"])
        if sink.get("body_event_index") is not None:
            event += "." + str(sink["body_event_index"])
        values = [f"{sink['instruction_id']} / {event} / {sink['op_index']}",
                  f"{sink['target']} · {location.get('kind', '')} / {location.get('name', '')}",
                  sink["sink_type"], str(sink["exposure_level"]),
                  f"{location.get('access_scope', '')} / {location.get('retention')}", sink.get("scope") or "—"]
        lines.append("| " + " | ".join(_cell(x) for x in values) + " |")
    if not result.get("sink_boundaries"):
        lines.append("| — | No compiler-collected sink boundary | — | — | — | — |")
    lines.extend(["", "Task-internal temporary flow remains represented; level 0 is excluded from the sink list. Deleting a binding does not deliver its old contents. Exclusion from this list is not a data-safety guarantee.", "",
                  "## IR semantics by block", ""])
    if material is not None:
        for block_id, block in material["cfg"]["blocks"].items():
            lines.extend([f"### {block_id} · {_cell(block['block_name'])}", "",
                          "| IR | Action | Executing subjects (operator) | effects |",
                          "|---|---|---|---|"])
            for instruction in block["instructions"]:
                profile = result["ir_semantics"].get(instruction["id"])
                partial = result.get("ir_semantics", {}).get(instruction["id"], {}).get("order") == "partial"
                values = ([", ".join(profile["operator"]) or "[]"]
                          + [_effect_steps(profile, partial)]) if profile else ["Not accepted"] * 2
                lines.append("| " + " | ".join(_cell(x) for x in [instruction["id"], instruction["opcode"], *values]) + " |")
            lines.append("")
    task = material.get("task") if material is not None else None
    if task is not None:
        lines.extend(["## Independent Task basis and demand realization", "",
                      f"Purpose basis: `{task['basis']}`; Task revision: `{task['task_sha256']}`.", "", _cell(task["purpose"]["text"]), "",
                      f"Task requirements: {len(task['requirements'])}; Positive preservation goals: {len(result.get('demands', []))}; Expressions: {len(result.get('expressions', []))}.", "",
                      "Task comes from the independent source stage; annotation references that revision only. Expression states below do not prove requirements are satisfied, demands are minimal or semantics are complete.", ""])
        lines.extend(["| Requirement | Expression status | Remaining limitations |", "| --- | --- | --- |"])
        for row in result.get("realizations", []):
            lines.append("| " + " | ".join(_cell(value) for value in (row["requirement_id"], row["status"],
                "; ".join(gap["reason"] for gap in row["gaps"]))) + " |")
        lines.append("")
    lines.extend(["## Symbolic transfer specifications", "",
                  "These are compiler-generated symbolic operations. The model declares processing segments; the compiler derives model_observe from their modes and the runtime contract. Compilation does not prove that these semantic claims are correct. Data propagation has not run here; symbolic references are not Data IDs.", "",
                  "[Validated raw specification (parsed candidate)](audit/raw-annotation.json) · [Compiled response](audit/compiled-response.json) · [Compilation mapping](audit/compilation-map.json)", ""])
    for location_id, location in result.get("locations", {}).items():
        lines.append(f"- Location `{location_id}`: `{location['kind']}` / `{location['name']}`; access `{location['access_scope']}`, retention `{location['retention']}`. Evidence remains in its audit table; default properties are not measured execution facts.")
    for ir_id, spec in result.get("ir_semantics", {}).items():
        lines.extend(["", f"### {ir_id} · Events and public results", "", f"Order: `{spec['order']}`; compiled causal constraints: {len(spec['precedence'])}.", ""])
        def describe_event(event, position):
            label = event["effect"] or "Data relationship without a security label"
            lines.append(f"- Event {position}: {label}.")
            for op_index, operation in enumerate(event["atomic_ops"]):
                body = {key: value for key, value in operation.items() if key != "evidences"}
                lines.append(f"  - Operation {op_index}: `{_cell(json.dumps(body, ensure_ascii=False))}`")
        for event_index, event in enumerate(spec["events"]):
            if event.get("kind") == "for_each":
                lines.append(f"- Element scope {event_index}: collection `{_cell(json.dumps(event['collection'], ensure_ascii=False))}`, item binding `{_cell(event['item'])}`. Fields retain same-element pairing; this is not a concrete collection length or call count.")
                for body_index, child in enumerate(event["body"]):
                    describe_event(child, f"{event_index}.{body_index}")
            else:
                describe_event(event, event_index)
        if not spec["events"]:
            lines.append("- No events; the following result bindings still apply.")
        for binding in spec["output_bindings"]:
            lines.append(f"- output[{binding['output_index']}] ← `{_cell(json.dumps(binding['value'], ensure_ascii=False))}`")
    lines.extend(["", "## Evidence by claim", ""])
    def show_evidence(item, target):
        if material is None:
            reference = item.get("rule_id") or (json.dumps(item["target"], ensure_ascii=False) if "target" in item else f"{item['file']}:{item['start_line']}-{item['end_line']}")
            excerpt = "Source material is required to extract the exact evidence."
        else:
            resolved = evidence_reference(item, material)
            reference = item.get("rule_id") or (json.dumps(item["target"], ensure_ascii=False) if "target" in item else f"{item['file']}:{item['start_line']}-{item['end_line']}")
            excerpt = resolved["text"]
        lines.extend([f"- {_cell(target)} · `{_cell(reference)}`: {_cell(item['reason'])}", ""])
        lines.extend("> " + line for line in excerpt.splitlines())
        lines.append("")
    for ir_id, spec in result.get("ir_semantics", {}).items():
        lines.extend([f"### {ir_id}", ""])
        for item in spec["operator_evidences"]:
            show_evidence(item, "operator=" + str(item["value"]))
        for item in spec.get("empty_effect_evidences", []):
            show_evidence(item, "No applicable effect")
        for i, outer in enumerate(spec["events"]):
            for j, event in enumerate(outer["body"] if outer.get("kind") == "for_each" else [outer]):
                position = f"{i}.{j}" if outer.get("kind") == "for_each" else str(i)
                for item in event.get("evidences", []):
                    show_evidence(item, f"Event {position}: {event['effect']}")
    lines.extend(["## Analysis boundaries", "",
                  "This stage declares Task requirements, supported demand semantics, sensitivity, action properties and symbolic operations. It does not execute the Skill or compute final sensitive exposure, risk or indispensability.",
                  "Broad reads and model returns are conservative contract defaults. Tool-internal reads, tool returns and model inputs are distinct boundaries. Evidence matching validates references, not semantic support.",
                  "Effects preserve occurrence positions. With order=partial, constraints determine possible arrangements; the array is not the unique execution order. Model inference is not proven correct.",
                  "context_write changes runtime content or bindings readable by later actions. It is not automatically transform, fs_write or model_observe; ordinary IR output binding does not imply a context write.",
                  "Empty effects are not a no-op and cannot establish equal entry and exit states. Failure to represent required relationships is recorded explicitly.",
                  "Uninterpreted binary and code boundaries remain in result.json. Assistant review is separate and does not imply user confirmation.", ""])
    return "\n".join(lines)
