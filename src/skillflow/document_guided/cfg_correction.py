"""Select existing CFG correction records from bound, actual dependencies.

This module does not repair or validate a graph. A selected scope is an editing
permission, never an acceptance decision: the caller retains the entire source
and candidate as read-only context and validates the entire merged replacement.
"""
from __future__ import annotations

from copy import deepcopy
import re

from skillflow.common.recording import canonical_sha256


IDENTITY = "skillflow-cfg-correction-scope-v2"
CASCADE_IDENTITY = "skillflow-cfg-rejected-block-cascade-v1"
MIXED_CASCADE_IDENTITY = "skillflow-cfg-rejected-block-cascade-v2"
_AMBIGUOUS = {"DUPLICATE_BLOCK_REF", "DUPLICATE_INSTRUCTION_REF",
              "DUPLICATE_RESULT_IDENTIFIER", "DUPLICATE_EDGE"}


class _InsufficientScope(ValueError):
    pass


def _pointer(path):
    if not isinstance(path, str):
        raise _InsufficientScope("A diagnostic location is malformed.")
    if path.startswith("/") or not path:
        return path
    if path in {"cfg", "candidate"}:
        return ""
    return "/" + "/".join(part.replace("~", "~0").replace("/", "~1")
        for part in re.findall(r"[^.\[\]]+", path))


def _record(path, candidate):
    if path == "/entry_block_ref" and "entry_block_ref" in candidate:
        return path
    match = re.match(r"^/(blocks|edges)/(0|[1-9][0-9]*)(?:/|$)", path)
    if match and int(match[2]) < len(candidate.get(match[1], [])):
        return f"/{match[1]}/{match[2]}"
    return None


def _text(value):
    return isinstance(value, str) and bool(value) and value == value.strip()


def _index(candidate):
    """Index authored identities; never infer references from names or prose."""
    blocks, edges = candidate.get("blocks"), candidate.get("edges")
    if not isinstance(blocks, list) or not blocks or not isinstance(edges, list):
        raise _InsufficientScope("Missing or malformed block/edge record arrays.")
    refs, outputs, instruction_refs = {}, {}, set()
    inputs, instructions = {}, {}
    for bi, block in enumerate(blocks):
        if not isinstance(block, dict) or not _text(block.get("block_ref")):
            raise _InsufficientScope("A block has a missing or malformed identity.")
        ref = block["block_ref"]
        if ref in refs:
            raise _InsufficientScope("Block identities are ambiguous.")
        refs[ref] = bi
        rows = block.get("instructions", [])
        if not isinstance(rows, list):
            raise _InsufficientScope("Instruction records cannot be indexed.")
        instructions[bi], inputs[bi] = rows, []
        for ii, instruction in enumerate(rows):
            if not isinstance(instruction, dict):
                raise _InsufficientScope("An instruction record is malformed.")
            if "instruction_ref" in instruction:
                ref = instruction["instruction_ref"]
                if not _text(ref) or ref in instruction_refs:
                    raise _InsufficientScope("Instruction identities are malformed or ambiguous.")
                instruction_refs.add(ref)
            for side in ("inputs", "outputs"):
                operands = instruction.get(side, [])
                if not isinstance(operands, list):
                    raise _InsufficientScope("Operand records cannot be indexed.")
                for oi, operand in enumerate(operands):
                    if not isinstance(operand, dict):
                        raise _InsufficientScope("An operand record is malformed.")
                    if operand.get("type") != "result":
                        continue
                    name = operand.get("identifier")
                    if not _text(name):
                        raise _InsufficientScope("A result identity is missing or malformed.")
                    item = {"block_index": bi, "instruction_index": ii,
                            "operand_index": oi, "identifier": name,
                            "path": f"/blocks/{bi}/instructions/{ii}/{side}/{oi}"}
                    if side == "outputs":
                        if name in outputs:
                            raise _InsufficientScope("Result producer identities are ambiguous.")
                        outputs[name] = item
                    else:
                        inputs[bi].append(item)
    predecessors, successors, seen_edges, missing_edges = {}, {}, set(), []
    for bi in range(len(blocks)):
        predecessors[bi], successors[bi] = set(), set()
    for ei, edge in enumerate(edges):
        if not isinstance(edge, dict) or any(not _text(edge.get(key))
                for key in ("source_block_ref", "target_block_ref")):
            raise _InsufficientScope("An edge has a malformed identity.")
        source, target = edge["source_block_ref"], edge["target_block_ref"]
        condition = edge.get("condition_text")
        if condition is not None and not isinstance(condition, str):
            raise _InsufficientScope("An edge condition is malformed.")
        key = source, target, condition
        if key in seen_edges:
            raise _InsufficientScope("Edge identities are ambiguous.")
        seen_edges.add(key)
        if source not in refs or target not in refs:
            missing_edges.append(ei)
            continue
        predecessors[refs[target]].add(refs[source])
        successors[refs[source]].add(refs[target])
    return {"refs": refs, "outputs": outputs, "inputs": inputs,
            "instructions": instructions, "predecessors": predecessors,
            "successors": successors, "missing_edges": missing_edges}


def _cascade_owners(candidate, diagnostics, row, digest):
    # The compiled digest is provenance for the source-normalized compiler
    # input. It is intentionally not compared to the raw wire. The adapter's
    # independently attached raw digest is the authoritative selection binding.
    context = row.get("context", {})
    cause = context.get("cfg_rejected_block_cascade")
    if (row.get("code") != "CFG_STRUCTURE_INVALID" or not isinstance(cause, dict)
            or cause.get("version") not in {CASCADE_IDENTITY, MIXED_CASCADE_IDENTITY} or cause.get("complete") is not True
            or context.get("cfg_correction_candidate_sha256") != digest
            or cause.get("root_diagnostic_sha256") != canonical_sha256({
                "code": row.get("code"), "path": _pointer(row.get("path", "")), "message": row.get("message")})
            or not re.fullmatch(r"[0-9a-f]{64}", str(cause.get("compiled_candidate_sha256", "")))):
        raise _InsufficientScope("The global diagnostic has no complete current-candidate causal ownership.")
    owners, endpoints = cause.get("rejected_blocks"), cause.get("endpoints")
    mixed = cause["version"] == MIXED_CASCADE_IDENTITY
    if (not isinstance(owners, list) or not isinstance(endpoints, list)
            or bool(owners) != bool(endpoints) or (not mixed and not owners)):
        raise _InsufficientScope("The rejected-block cascade has incomplete ownership records.")
    owned = {}
    for owner in owners:
        if not isinstance(owner, dict):
            raise _InsufficientScope("A rejected-block owner is malformed.")
        bi, di = owner.get("block_index"), owner.get("diagnostic_index")
        if (type(bi) is not int or not 0 <= bi < len(candidate["blocks"]) or bi in owned
                or type(di) is not int or not 0 <= di < len(diagnostics)):
            raise _InsufficientScope("A rejected-block owner has stale or ambiguous indices.")
        original, local = owner.get("original_diagnostic"), diagnostics[di]
        if (not isinstance(original, dict) or original.get("code") not in
                {"RESULT_READ_BEFORE_DEFINITION", "BASIC_BLOCK_INVALID"}
                or original.get("code") != local.get("code")
                or original.get("message") != local.get("message")
                or _pointer(original.get("path", "")) != f"/blocks/{bi}"
                or _pointer(local.get("path", "")) != f"/blocks/{bi}"
                or owner.get("block_ref") != candidate["blocks"][bi]["block_ref"]
                or owner.get("canonical_block_id") != f"block_{bi + 1:03d}"):
            raise _InsufficientScope("The cascade does not bind the actual rejecting diagnostic and block.")
        owned[bi] = owner
    # No missing authored endpoint is eligible, even if another endpoint has a
    # valid rejected owner. Re-derive every explained occurrence structurally.
    all_refs = {block["block_ref"] for block in candidate["blocks"]}
    expected = []
    for ei, edge in enumerate(candidate["edges"]):
        if any(edge[key] not in all_refs for key in ("source_block_ref", "target_block_ref")):
            raise _InsufficientScope("An authored edge endpoint is actually absent.")
        for role in ("source", "target"):
            for bi, owner in owned.items():
                if edge[f"{role}_block_ref"] == owner["block_ref"]:
                    expected.append({"edge_index": ei, "canonical_edge_index": ei, "role": role,
                        "block_index": bi, "block_ref": owner["block_ref"],
                        "canonical_block_id": owner["canonical_block_id"]})
    if endpoints != expected:
        raise _InsufficientScope("Cascade endpoint evidence is incomplete, reordered or stale.")
    dispatch_roots = set()
    if mixed:
        dispatches = cause.get("dispatches")
        if (not isinstance(dispatches, list) or not dispatches
                or type(cause.get("structure_issue_count")) is not int
                or cause["structure_issue_count"] != len(endpoints) + len(dispatches)):
            raise _InsufficientScope("Mixed structural ownership does not cover every issue.")
        for dispatch in dispatches:
            if not isinstance(dispatch, dict):
                raise _InsufficientScope("A dispatch owner is malformed.")
            bi = dispatch.get("block_index")
            if (type(bi) is not int or not 0 <= bi < len(candidate["blocks"])
                    or bi in owned or bi in dispatch_roots):
                raise _InsufficientScope("A dispatch owner has stale or ambiguous indices.")
            block = candidate["blocks"][bi]
            ii = len(block["instructions"]) - 1
            terminal = block["instructions"][ii] if ii >= 0 else {}
            outgoing = [ei for ei, edge in enumerate(candidate["edges"])
                        if edge["source_block_ref"] == block["block_ref"]]
            serial = sum(len(b["instructions"]) for b in candidate["blocks"][:bi]) + ii + 1
            if (dispatch.get("code") != "DISPATCH_INPUTS_MISSING"
                    or dispatch.get("block_ref") != block["block_ref"]
                    or dispatch.get("canonical_block_id") != f"block_{bi + 1:03d}"
                    or dispatch.get("canonical_instruction_id") != f"ir_{serial:03d}"
                    or dispatch.get("instruction_index") != ii or dispatch.get("edge_indices") != outgoing
                    or terminal.get("opcode") != "dispatch" or terminal.get("inputs")
                    or not (len(outgoing) > 1 or any(candidate["edges"][ei].get("condition_text") for ei in outgoing))):
                raise _InsufficientScope("The dispatch proof does not match its actual terminator and outgoing edges.")
            local = [item for item in diagnostics if item.get("code") == "dispatch_inputs"
                     and item.get("path") == f"/blocks/{bi}/instructions/{ii}/inputs"
                     and item.get("context", {}).get("cfg_correction_candidate_sha256") == digest]
            if len(local) != 1:
                raise _InsufficientScope("The mixed root has no unique current preflight dispatch diagnostic.")
            dispatch_roots.add(bi)
        expected_dispatches = []
        for bi, block in enumerate(candidate["blocks"]):
            if bi in owned or not block["instructions"]:
                continue
            terminal = block["instructions"][-1]
            outgoing = [edge for edge in candidate["edges"] if edge["source_block_ref"] == block["block_ref"]]
            if (terminal.get("opcode") == "dispatch" and not terminal.get("inputs")
                    and (len(outgoing) > 1 or any(edge.get("condition_text") for edge in outgoing))):
                expected_dispatches.append(bi)
        if [item["block_index"] for item in dispatches] != expected_dispatches:
            raise _InsufficientScope("Mixed structural ownership omitted or reordered a surviving guarded dispatch.")
    elif "dispatches" in cause or "structure_issue_count" in cause:
        raise _InsufficientScope("Legacy endpoint ownership cannot claim additional structural issues.")
    return set(owned) | dispatch_roots


def _reachable(start, adjacency):
    pending, reached = [start], set()
    while pending:
        current = pending.pop()
        if current not in reached:
            reached.add(current)
            pending.extend(adjacency[current] - reached)
    return reached


def _dependency_scope(candidate, index, roots):
    if index["missing_edges"]:
        raise _InsufficientScope("A dependency closure cannot cross a genuinely missing endpoint.")
    if candidate.get("entry_block_ref") not in index["refs"]:
        raise _InsufficientScope("The dependency graph has no unambiguous entry.")
    affected, dependencies = set(roots), []
    for root in sorted(roots):
        component = (_reachable(root, index["successors"])
                     & _reachable(root, index["predecessors"]))
        affected.update(component)
        for bi in sorted(component - {root}):
            dependencies.append({"kind": "control_cycle", "root": f"/blocks/{root}",
                                 "record": f"/blocks/{bi}"})
    selected = set(affected)
    for bi in sorted(affected):
        for pred in sorted(index["predecessors"][bi]):
            selected.add(pred)
            dependencies.append({"kind": "immediate_predecessor", "record": f"/blocks/{pred}",
                                 "consumer": f"/blocks/{bi}"})
        for use in index["inputs"][bi]:
            producer = index["outputs"].get(use["identifier"])
            if producer is None:
                raise _InsufficientScope("An affected input has no actual producer; the closure is insufficient.")
            selected.add(producer["block_index"])
            dependencies.append({"kind": "result_producer", "identifier": use["identifier"],
                "record": f"/blocks/{producer['block_index']}", "producer": producer["path"],
                "consumer": use["path"]})
        for ii, instruction in enumerate(index["instructions"][bi]):
            metadata = instruction.get("metadata", {})
            if not isinstance(metadata, dict):
                raise _InsufficientScope("Affected instruction metadata is malformed.")
            if "predecessors" not in metadata:
                continue
            declared = metadata["predecessors"]
            if (not isinstance(declared, list) or not declared or any(not _text(ref) for ref in declared)
                    or len(set(declared)) != len(declared)
                    or any(ref not in index["refs"] for ref in declared)
                    or {index["refs"][ref] for ref in declared} != index["predecessors"][bi]
                    or len(declared) != len(instruction.get("inputs", []))):
                raise _InsufficientScope("Declared carry predecessors do not match actual incoming relationships.")
            for pi, ref in enumerate(declared):
                pred = index["refs"][ref]
                selected.add(pred)
                dependencies.append({"kind": "declared_carry_predecessor", "record": f"/blocks/{pred}",
                    "consumer": f"/blocks/{bi}/instructions/{ii}/inputs/{pi}"})
    # Preserve all cross-boundary relationships as explicit read-only context.
    boundary = []
    for bi, uses in index["inputs"].items():
        for use in uses:
            producer = index["outputs"].get(use["identifier"])
            if producer is None:
                if bi in selected:
                    raise _InsufficientScope("A selected dependency has an input with no actual producer.")
                continue
            pb = producer["block_index"]
            if (bi in selected) != (pb in selected):
                boundary.append({"kind": "result_boundary", "identifier": use["identifier"],
                                 "producer": producer["path"], "consumer": use["path"]})
    for ei, edge in enumerate(candidate["edges"]):
        source, target = (index["refs"][edge[key]] for key in ("source_block_ref", "target_block_ref"))
        if source in selected or target in selected:
            boundary.append({"kind": "unchanged_control_edge", "path": f"/edges/{ei}",
                             "source": f"/blocks/{source}", "target": f"/blocks/{target}"})
    return selected, dependencies, boundary


def select_cfg_correction(candidate, diagnostics):
    """Return exact existing-record permissions or an evidenced whole fallback.

    ``records`` contains complete original values. ``evidence`` binds the
    candidate and all original diagnostics, including explanations not shown
    as primary errors. The caller must recheck these bindings before merging.
    """
    evidence = {"identity": IDENTITY, "candidate_sha256": canonical_sha256(candidate),
        "diagnostics_sha256": canonical_sha256(diagnostics), "root_records": [],
        "dependencies": [], "readonly_boundary": [], "scope_policy": "direct_records"}
    try:
        if not isinstance(candidate, dict) or not isinstance(diagnostics, list) or not diagnostics:
            raise _InsufficientScope("Correction requires an object candidate and nonempty diagnostics.")
        index = _index(candidate)
        records, roots = set(), set()
        dependency_mode = False
        barriers = set()
        for row in diagnostics:
            if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                raise _InsufficientScope("A diagnostic has no exact location.")
            context = row.get("context", {})
            if not isinstance(context, dict):
                raise _InsufficientScope("A diagnostic context is malformed.")
            barrier = context.get("cfg_validation_barrier")
            if barrier is not None:
                if not isinstance(barrier, str) or barrier not in {
                        "candidate_schema", "wire_schema", "canonical_schema", "source_copy"}:
                    raise _InsufficientScope("Unknown compiler-inspection barrier; use the full response.")
                # Diagnostic coverage and editing permission are distinct.
                # A precise malformed field may still own an existing record;
                # it cannot justify compiler-derived dependency inference.
                barriers.add(barrier)
            bound = context.get("cfg_correction_candidate_sha256")
            if bound is not None and bound != evidence["candidate_sha256"]:
                raise _InsufficientScope("Diagnostic ownership belongs to another candidate.")
            if row.get("code") == "binary_dispatch" or row.get("code") in _AMBIGUOUS:
                raise _InsufficientScope("The defect requires topology changes or has ambiguous identities.")
            path = _pointer(row["path"])
            if not path:
                roots.update(_cascade_owners(candidate, diagnostics, row, evidence["candidate_sha256"]))
                dependency_mode = True
                continue
            record = _record(path, candidate)
            if record is None:
                raise _InsufficientScope("A diagnostic does not identify an existing editable record.")
            records.add(record)
            if record.startswith("/blocks/"):
                roots.add(int(record.rsplit("/", 1)[1]))
            if row.get("code") == "RESULT_READ_BEFORE_DEFINITION":
                dependency_mode = True
        evidence["root_records"] = sorted(records | {f"/blocks/{bi}" for bi in roots})
        if dependency_mode:
            if barriers:
                raise _InsufficientScope("A compiler-inspection barrier prevents global or causal dependency ownership; use the full response.")
            if any(not record.startswith("/blocks/") for record in records):
                raise _InsufficientScope("Dependency repair also requires an entry/edge edit; use the full response.")
            selected, dependencies, boundary = _dependency_scope(candidate, index, roots)
            records.update(f"/blocks/{bi}" for bi in selected)
            evidence.update(scope_policy="affected_control_components_with_producer_and_predecessor_boundary",
                dependencies=dependencies, readonly_boundary=boundary,
                topology_policy="Existing block identities, edges and entry are immutable. New instructions and result identities inside selected blocks are allowed.")
        if not records:
            raise _InsufficientScope("No existing record can own this correction.")
        selected_records = {}
        for record in sorted(records):
            if record == "/entry_block_ref":
                selected_records[record] = deepcopy(candidate["entry_block_ref"])
            else:
                group, ordinal = record[1:].split("/")
                selected_records[record] = deepcopy(candidate[group][int(ordinal)])
        evidence["reason"] = "Every diagnostic is owned by existing records; selected dependencies and unchanged boundaries are explicit. Full post-merge validation is required."
        if barriers:
            evidence["reason"] = ("Every diagnostic identifies an existing record, but compiler inspection remains blocked by "
                + ", ".join(sorted(barriers)) + ". Only direct record edits are permitted; no dependency closure is inferred. "
                "Full post-merge validation is required.")
        return {"mode": "records", "records": selected_records, "evidence": evidence}
    except _InsufficientScope as error:
        evidence["reason"] = str(error)
        return {"mode": "whole", "records": {}, "evidence": evidence}
