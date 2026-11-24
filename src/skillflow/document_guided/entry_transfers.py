"""Source-backed context acquisition checks shared by processing and its repairs."""
from copy import deepcopy

from skillflow.common.source_evidence import json_pointer, validate_source_ref
from skillflow.common.validation import structural_error
from skillflow.propagation.contracts.task import task_source_files


def acquisition_ports(material):
    """Return only independently established input/output correspondences."""
    from .entry_occurrences import callable_signature_ports

    files = None
    result = {}
    for block in material["cfg"]["blocks"].values():
        if block.get("data_source_kind") != "context" or not block.get("instructions"):
            continue
        ir = block["instructions"][0]
        if not ir.get("inputs") or any(v["type"] != "context_key" for v in ir["inputs"]):
            continue
        if files is None:
            files = task_source_files(material["source"])
        ports = callable_signature_ports(ir, files)
        if ports:
            result[ir["id"]] = (ir, ports)
    return result


def _input(index):
    return {"kind": "input", "index": index}


def location_errors(entries, locations):
    """An operand anchor denotes its value, not a container holding several callers' values."""
    from collections import defaultdict

    by_operand = defaultdict(list)
    for name, loc in locations.items():
        for ref in loc.get("operand_refs", []):
            if ref["side"] == "input":
                by_operand[ref["instruction_id"], ref["index"]].append(name)
    addresses = defaultdict(list)
    for ir_id, (ir, ports) in entries.items():
        for port in ports:
            index = port["input_index"]
            names = by_operand.get((ir_id, index))
            if names:
                for name in names:
                    loc = locations[name]
                    addresses[loc["kind"], loc["name"]].append((name, port))
            else:
                addresses["runtime_context", ir["inputs"][index]["identifier"]].append((None, port))
    errors = []
    for refs in addresses.values():
        owners = sorted({(port["owner"], port["parameter"]) for _, port in refs})
        if len(owners) > 1:
            for name in sorted({name for name, _ in refs if name is not None}):
                errors.extend(structural_error("entry_location_alias", json_pointer("locations", name, "operand_refs"),
                    f"This address identifies distinct caller arguments {owners}. Anchor each argument to "
                    "its own occurrence; use a separate read and field projections for a real shared container.").diagnostics)
    return errors


def _read_index(op, ir, locations):
    """An explicit read must address the actual operand of this occurrence."""
    loc = locations.get(op.get("location"), {})
    if (op.get("op") != "read" or loc.get("kind") != "runtime_context"
            or loc.get("address_kind", "identified") != "identified"):
        return None
    matches = [i for i, operand in enumerate(ir["inputs"])
               if operand.get("identifier") == loc.get("name")]
    refs = loc.get("operand_refs", [])
    if refs:
        matches = [ref["index"] for ref in refs
                   if ref["instruction_id"] == ir["id"] and ref["side"] == "input"]
    return matches[0] if len(matches) == 1 else None


def entry_binding_errors(ir, ports, spec, locations):
    """An unrelated read, selected sibling or newly acquired response cannot bind a caller argument."""
    from .action_bindings import action_coordinates, _at

    ir_id = ir["id"]
    coordinates = list(action_coordinates(spec))
    bindings = {b["output_index"]: (i, b["value"]) for i, b in enumerate(spec.get("output_bindings", []))}
    reads = {}
    errors = []
    for path, choices in coordinates:
        if len(path) < 2 or path[-2] != "ops":
            continue
        op = _at(spec, path)
        if op["op"] not in {"read", "receive", "call"}:
            continue
        index = _read_index(op, ir, locations)
        if index is None:
            errors.extend(structural_error("entry_acquisition", json_pointer("ir_semantics", ir_id, *path),
                "This source occurrence receives the indicated caller arguments. Its acquisition cannot read "
                "another address or issue a fresh user/tool request. Use its actual entry operands.").diagnostics)
        elif not choices and "body" not in path:
            reads[op["output"]] = index
    for port in ports:
        index, out = port["input_index"], port["output_index"]
        if out not in bindings:
            errors.extend(structural_error("entry_output_binding", json_pointer("ir_semantics", ir_id, "output_bindings"),
                f"Bind output {out} to input {index} of {port['owner']} ({port['parameter']}).").diagnostics)
            continue
        bi, ref = bindings[out]
        if ref == _input(index):
            continue
        if ref.get("kind") == "local" and reads.get(ref["name"]) == index and not port["optional"]:
            continue
        errors.extend(structural_error("entry_output_binding", json_pointer("ir_semantics", ir_id, "output_bindings", bi, "value"),
            f"Output {out} receives input {index} of {port['owner']} ({port['parameter']}). Preserve this "
            "occurrence's entry snapshot, including omission of an optional argument.").diagnostics)
    return errors


def _checked_gaps(ir, value, indexes, files):
    from .annotation_wire import FlatProcessingGap
    from pydantic import ValidationError

    seen = set()
    if not isinstance(value.get("locations", {}), dict):
        return False
    for index in indexes:
        raw = value["processing_gaps"][index]
        try:
            gap = FlatProcessingGap.model_validate(raw)
            identity = gap.model_dump_json()
            if (identity in seen or any(i >= len(ir["outputs"]) for i in gap.outputs)
                    or set(gap.locations) - value.get("locations", {}).keys()
                    or len(set(gap.outputs)) != len(gap.outputs) or len(set(gap.locations)) != len(gap.locations)):
                return False
            seen.add(identity)
            for evidence in gap.evidences:
                validate_source_ref(evidence.model_dump(include={"file", "start_line", "end_line"}), files)
        except (ValueError, TypeError, ValidationError):
            return False
    return True


def _contains(span, ref):
    return (isinstance(span, dict) and span.get("file") == ref["file"]
            and span["start_line"] <= ref["start_line"] <= ref["end_line"] <= span["end_line"])


def scope_entry_gaps(value, material, *, quarantine=False):
    """Resolve state/control claims at their cited occurrence, independently of argument receipt."""
    rows = value.get("processing_gaps", [])
    if not isinstance(rows, list) or not any(isinstance(g, dict) and (g.get("locations") or g.get("control")) for g in rows):
        return []
    entries = acquisition_ports(material)
    files = task_source_files(material["source"])
    actions = {ir["id"]: ir.get("metadata", {}).get("source_actions", [])
               for block in material["cfg"]["blocks"].values() for ir in block["instructions"]}
    errors, misplaced = [], set()
    for index, gap in enumerate(rows):
        if not isinstance(gap, dict) or gap.get("instruction_id") not in entries or not (gap.get("locations") or gap.get("control")):
            continue
        source = gap["instruction_id"]
        ir, ports = entries[source]
        if not _checked_gaps(ir, value, [index], files):
            continue
        other = [ref for ref in gap["evidences"] if not _contains(ports[0]["source"], ref)]
        if not other:
            continue
        owners = [owner for owner, inventory in actions.items() if owner != source and all(any(
            isinstance(action, dict) and (action.get("role") or action.get("kind")) in {"call", "read", "write", "branch", "loop", "other"}
            and _contains(action.get("source"), ref) for action in inventory) for ref in other)]
        # Indexed outputs refer to the old operation. Only its proved input
        # bindings may be discharged when moving a state/control footprint.
        if len(owners) == 1 and set(gap.get("outputs", [])) <= {p["output_index"] for p in ports}:
            from .action_bindings import action_coordinates, _at
            owner = owners[0]
            record = value.get("ir_semantics", {}).get(owner)
            witnessed = False
            if isinstance(record, dict):
                coords = [p for p, _ in action_coordinates(record)]
                ops = [_at(record, p) for p in coords if len(p) >= 2 and p[-2] == "ops"]
                named = {op.get("target", op.get("location")) for op in ops}
                control = any(p[-1] in {"guard", "condition", "disposition"} for p in coords) or any(
                    op["op"] == "branch" for op in ops)
                witnessed = set(gap.get("locations", [])) <= named and (not gap.get("control") or control)
            gap.update(instruction_id=owner, outputs=[], unmodeled=bool(gap.get("unmodeled") and not witnessed))
            continue
        citations = ", ".join(f"{r['file']}:{r['start_line']}-{r['end_line']}" for r in other)
        errors.extend(structural_error("entry_gap_scope", json_pointer("processing_gaps", index),
            f"The declared state/control issue at {citations} has no unique action at this invocation. "
            f"Locate the separate source occurrence and its affected state or control. Original issue: {gap['reason']}",
            instruction_id=source).diagnostics)
        misplaced.add(index)
    if quarantine and misplaced:
        value["processing_gaps"] = [g for i, g in enumerate(rows) if i not in misplaced]
    return errors


def _declared_acquisitions(block):
    ir = block["instructions"][0]
    meta = ir.get("metadata", {})
    actions = meta.get("source_actions") or [{"kind": ir["opcode"], "source": meta.get("source_span")}]
    return [a for a in actions if isinstance(a, dict) and (a.get("role") or a.get("kind")) in {"read", "receive"} and isinstance(a.get("source"), dict)]


def _witnessed_projections(ir, spec, locations, actions):
    """Trace authored linear reads/projections. No positional mapping is inferred."""
    read = set()
    roots = []
    unknown = set()
    effects = set()
    for si, segment in enumerate(spec.get("segments", [])):
        if segment.get("kind", "processing") != "processing":
            return None
        for oi, op in enumerate(segment.get("ops", [])):
            kind, target = op["op"], op.get("output")
            path = ["segments", si, "ops", oi]
            bound = spec.get("action_bindings")
            at_receipt = any(not bound or path in bound.get(a.get("ref"), []) for a in actions)
            if kind in {"read", "receive"} and at_receipt:
                location = locations.get(op["location"], {})
                name = location.get("name")
                identified = _read_index(op, ir, locations) is not None or any(
                    v["type"] == "external_resource" and v["identifier"] == name for v in ir["inputs"])
                if (identified and kind == "read" and location.get("kind") in {"runtime_context", "storage"}
                        or kind == "receive" and location.get("kind") in {"remote", "tool", "user"}):
                    read.add(target)
                    roots.append({"kind": "local", "name": target})
            elif kind == "select_part":
                ref = op["input"]
                if (ref.get("kind") == "local" and ref["name"] in read
                        or ref.get("kind") == "input" and 0 <= ref["index"] < len(ir["inputs"])
                        and ir["inputs"][ref["index"]]["type"] == "context_key"):
                    read.add(target)
                elif ref.get("kind") == "local" and ref["name"] in unknown:
                    unknown.add(target)
            elif kind == "placeholder":
                if op["kind"] == "value":
                    unknown.add(target)
                elif op.get("location"):
                    effects.add(op["location"])
    known_outputs, unknown_outputs = set(), set()
    for binding in spec.get("output_bindings", []):
        out, ref = binding["output_index"], binding["value"]
        if (ref.get("kind") == "input" and 0 <= ref["index"] < len(ir["inputs"])
                and ir["inputs"][ref["index"]]["type"] == "context_key"
                or ref.get("kind") == "local" and ref["name"] in read):
            known_outputs.add(out)
        elif ref.get("kind") == "local" and ref["name"] in unknown:
            unknown_outputs.add(out)
    return known_outputs, unknown_outputs, effects, roots


def _localize_missing(ir, spec, gap, indexes, roots):
    """Place missing output values at an unambiguous, source-declared value action."""
    if not roots or not indexes:
        return False
    actions = ir.get("metadata", {}).get("source_actions") or spec.get("source_actions") or []
    candidates = [action for action in actions if (action.get("role") or action["kind"]) in {"value", "other"}
                  and any(ref["file"] == action["source"]["file"]
                          and action["source"]["start_line"] <= ref["start_line"] <= ref["end_line"] <= action["source"]["end_line"]
                          for ref in gap["evidences"])]
    if len(candidates) != 1:
        return False
    owner = candidates[0]["ref"]
    binding = spec.get("action_bindings", {})
    if set(binding) - {a["ref"] for a in actions} or (len(actions) > 1 and not binding):
        return False
    # Only append to the final position for the final action. Moving a value
    # across a later action could change its visible versions or frequency.
    if owner != actions[-1]["ref"]:
        return False
    occupied = {op["output"] for s in spec.get("segments", []) for op in s.get("ops", []) if "output" in op}
    segments, bindings = spec.setdefault("segments", []), spec.setdefault("output_bindings", [])
    paths = binding.setdefault(owner, []) if binding else None
    ops = []
    for out in sorted(indexes):
        name = f"unresolved_entry_output_{out}"
        while name in occupied:
            name += "_"
        occupied.add(name)
        if paths is not None:
            paths.extend([["segments", len(segments), "ops", len(ops)], ["output_bindings", len(bindings)]])
        ops.append({"op": "placeholder", "kind": "value", "inputs": deepcopy(roots), "output": name,
                    "reason": gap["reason"], "evidences": deepcopy(gap["evidences"])})
        bindings.append({"output_index": out, "value": {"kind": "local", "name": name}})
    segments.append({"mode": "local", "ops": ops, "returns": []})
    return True


def localize_packet_gaps(value, material, positions, files, *, fixed):
    """A proved original packet projection survives a co-located unknown value or effect."""
    from .fragments import ProcessingIR
    from pydantic import ValidationError

    for block in material["cfg"]["blocks"].values():
        if block.get("data_source_kind") not in {"context", "external"} or not block.get("instructions"):
            continue
        ir = block["instructions"][0]
        ir_id = ir["id"]
        indexes = positions.get(ir_id, [])
        if ir_id in fixed or not indexes or not _checked_gaps(ir, value, indexes, files):
            continue
        actions = _declared_acquisitions(block)
        spec = value["ir_semantics"].get(ir_id)
        if not actions or not isinstance(spec, dict):
            continue
        try:
            ProcessingIR.model_validate(spec)
            for action in actions:
                validate_source_ref(action["source"], files)
        except (ValueError, ValidationError):
            continue
        coverage = _witnessed_projections(ir, spec, value.get("locations", {}), actions)
        if not coverage:
            continue
        known, symbolic, effects, roots = coverage
        if not known:
            continue
        for index in indexes:
            gap = value["processing_gaps"][index]
            impacted = set(gap.get("outputs", [])) - known
            resources = set(gap.get("locations", []))
            if gap.get("control") or not resources <= effects or not (impacted or resources):
                continue
            missing = impacted - {b["output_index"] for b in spec.get("output_bindings", [])}
            if impacted - symbolic == missing and _localize_missing(ir, spec, gap, missing, roots):
                symbolic.update(missing)
            if impacted <= symbolic:
                gap.update(unmodeled=False, outputs=sorted(impacted))


def _source_record(ir, ports, gaps):
    """Generate the proved part of a single acquisition. Local unknown outputs keep their actual site."""
    covered = {port["output_index"]: port for port in ports}
    span = ports[0]["source"]
    evidence = {**span, "reason": "The callable signature and CFG operands identify this invocation's received arguments."}
    spec = {"evidences": [evidence], "output_bindings": []}
    unknown = []
    for index in range(len(ir["outputs"])):
        if index in covered:
            ref = _input(covered[index]["input_index"])
        else:
            local = "unresolved_entry_output_" + str(index)
            matching = [g for g in gaps if index in g.get("outputs", [])]
            reason = "The source locates this acquisition, but its operands do not uniquely identify the value of output " + str(index) + "."
            unknown.append({"op": "placeholder", "kind": "value", "inputs": [_input(i) for i in range(len(ir["inputs"]))],
                            "output": local, "reason": matching[0]["reason"] if matching else reason,
                            "evidences": deepcopy(matching[0]["evidences"]) if matching else [evidence]})
            ref = {"kind": "local", "name": local}
        spec["output_bindings"].append({"output_index": index, "value": ref})
    if unknown:
        spec["segments"] = [{"mode": "local", "ops": unknown, "returns": []}]
    actions = ir.get("metadata", {}).get("source_actions", [])
    if len(actions) > 1 and not unknown and all(p.get("action_ref") for p in ports):
        bindings = {}
        for port in ports:
            bindings.setdefault(port["action_ref"], []).append(["output_bindings", port["output_index"]])
        spec["action_bindings"] = bindings
    return spec


def _discard_wrong_packet(ir, spec, locations, span):
    """Remove a rejected fictitious packet read/projection chain only if none of its values escape."""
    segments = spec.get("segments", [])
    if len(ir.get("metadata", {}).get("source_actions", [])) > 1 or any(
        s.get("kind", "processing") != "processing" for s in segments
    ):
        return
    tainted = set()
    discarded = set()
    for si, segment in enumerate(segments):
        for oi, op in enumerate(segment.get("ops", [])):
            refs = op.get("evidences") or segment.get("evidences") or spec["evidences"]
            if any("file" in ref and (ref["file"] != span["file"] or ref["start_line"] < span["start_line"]
                                      or ref["end_line"] > span["end_line"]) for ref in refs):
                continue
            if ((op["op"] == "read" and locations.get(op["location"], {}).get("kind") == "runtime_context"
                 and _read_index(op, ir, locations) is None)
                    or (op["op"] == "receive" and not op.get("request_id")
                        and locations.get(op["location"], {}).get("kind") == "user")
                    or (op["op"] == "select_part" and op["input"]["kind"] == "local"
                        and op["input"]["name"] in tainted)):
                tainted.add(op["output"])
                discarded.add((si, oi))
    if not discarded:
        return
    def needs_discarded(value):
        if isinstance(value, list):
            return any(needs_discarded(x) for x in value)
        if not isinstance(value, dict) or value.get("kind") == "literal":
            return False
        if value.get("kind") == "local" and value.get("name") in tainted:
            return True
        return any(needs_discarded(x) for k, x in value.items() if k not in {"evidences", "expression"})
    retained = [op for si, segment in enumerate(segments) for oi, op in enumerate(segment.get("ops", []))
                if (si, oi) not in discarded]
    if needs_discarded([*retained, *spec.get("output_bindings", []), *[s.get("returns", []) for s in segments]]):
        return
    for si, segment in enumerate(segments):
        segment["ops"] = [op for oi, op in enumerate(segment.get("ops", [])) if (si, oi) not in discarded]
    spec.pop("action_bindings", None)  # The sole source action owns all surviving coordinates.


def assemble_entry_transfers(value, material, *, repair=(), fixed=()):
    """Materialize a proven receive even if it was omitted or claimed wholly unavailable.

    On a conflicting authored mapping, the ordinary validator reports the bad
    coordinates first. Only a rejected pure acquisition may be reconstructed at
    bounded salvage. The original submission remains in its attempt receipt.
    """
    from .processing_correction import gap_positions

    if (not isinstance(value.get("ir_semantics"), dict) or not isinstance(value.get("processing_gaps", []), list)
            or not isinstance(value.get("locations", {}), dict)
            or not all(isinstance(loc, dict) for loc in value.get("locations", {}).values())):
        return value
    positions = gap_positions(value)
    entries = acquisition_ports(material)
    if not entries and not positions:
        return value
    files = task_source_files(material["source"])
    if positions:
        localize_packet_gaps(value, material, positions, files, fixed=fixed)
        positions = gap_positions(value)
    remove = set()
    for ir_id, (ir, ports) in entries.items():
        if ir_id in fixed:
            continue
        indexes = positions.get(ir_id, [])
        if not _checked_gaps(ir, value, indexes, files):
            continue
        spec = value["ir_semantics"].get(ir_id)
        if ir_id in value["ir_semantics"]:
            from .fragments import ProcessingIR
            from pydantic import ValidationError
            try:
                ProcessingIR.model_validate(spec)
            except ValidationError:
                continue
        gaps = [value["processing_gaps"][i] for i in indexes]
        if spec is None:
            value["ir_semantics"][ir_id] = _source_record(ir, ports, gaps)
        elif ir_id in repair:
            # Retain authored operations, declarations and source evidence.
            # Only missing or contradicted bindings to *proved* ports are
            # replaced here; unrelated defects still face full validation.
            template = _source_record(ir, ports, gaps)
            bindings = spec.get("output_bindings", [])
            if not isinstance(bindings, list) or not all(isinstance(b, dict) and type(b.get("output_index")) is int for b in bindings):
                continue
            by_index = {b["output_index"]: b for b in bindings}
            if len(by_index) != len(bindings):
                continue
            for port in ports:
                out = port["output_index"]
                if out in by_index:
                    by_index[out]["value"] = _input(port["input_index"])
                else:
                    bindings.append(template["output_bindings"][out])
            spec["output_bindings"] = bindings
            _discard_wrong_packet(ir, spec, value.get("locations", {}), ports[0]["source"])
        elif indexes and entry_binding_errors(ir, ports, spec, value.get("locations", {})):
            continue
        for i in indexes:
            gap = value["processing_gaps"][i]
            # Same-site state/control claims still need independent source review.
            # Their uncertainty cannot suppress this verified input transfer.
            remaining = [o for o in gap.get("outputs", []) if o not in {p["output_index"] for p in ports}]
            if remaining or gap.get("locations") or gap.get("control"):
                gap.update(unmodeled=False, outputs=remaining)
            else:
                remove.add(i)
    if remove:
        value["processing_gaps"] = [g for i, g in enumerate(value["processing_gaps"]) if i not in remove]
    return value
