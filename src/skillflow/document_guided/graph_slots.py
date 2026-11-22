"""Plan and apply bounded graph fact updates without regenerating accepted material."""

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import replace
import re
from typing import Any

from pydantic import ValidationError

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import Digest, StrictRecord, Text, validate_source_ref
from skillflow.common.validation import structural_error
from .graph_facts import assemble_graph_facts, field_slot, instruction_ref, source_digest


IDENTITY = "skillflow-graph-slot-plan-v1"


class Update(StrictRecord):
    slot_id: Text
    value: Any


class Updates(StrictRecord):
    plan_sha256: Digest
    updates: list[Update]


GRAPH_UPDATES_SCHEMA = Updates.model_json_schema()


def _edges(block):
    exit = block["exit"]
    kind = exit["kind"]
    if kind == "jump":
        return [(block["ref"], exit["target"], None)]
    if kind == "branch":
        return [(block["ref"], arm["target"], arm["condition"]) for arm in exit["arms"]]
    return []


def _uses(block):
    exit = block["exit"]
    values = [value for op in block["operations"] for value in op["inputs"]]
    values.extend(exit.get("values", exit.get("conditions", [])))
    return {value["result"] for value in values if "result" in value}


def _definitions(block):
    return {ref for op in block["operations"] for ref in op["outputs"]}


def _returns(blocks):
    return Counter(canonical_sha256(block["exit"]["values"]) for block in blocks
                   if block["exit"]["kind"] == "return")


def _region_slot(facts, bi):
    old = facts["blocks"][bi]
    ref = old["ref"]
    peers = [block for index, block in enumerate(facts["blocks"]) if index != bi]
    peer_edges = [edge for block in peers for edge in _edges(block)]
    outside_uses = set().union(*(_uses(block) for block in peers))
    boundary = {
        "inbound_control": [list(edge) for edge in peer_edges if edge[1] == ref],
        "outbound_control": [[target, guard] for _, target, guard in _edges(old) if target != ref],
        "inbound_results": sorted(_uses(old) - _definitions(old)),
        "outbound_results": sorted(_definitions(old) & outside_uses),
        "return_values": dict(_returns([old])),
    }
    return {"slot_id": "cfg_region_" + canonical_sha256(ref)[:24], "kind": "region",
            "path": ["blocks", bi], "target": ref, "old_value": deepcopy(old), "boundary": boundary,
            "new_block_prefix": ref + "."}


def _simple_slots(facts, bi, oi, suffix):
    path = ("blocks", bi)
    block = facts["blocks"][bi]
    if oi is None:
        if suffix == ("constraints",):
            return [field_slot(facts, (*path, "constraints"))]
        return [_region_slot(facts, bi)] if not suffix else []
    ops = block["operations"]
    if oi < len(ops):
        path = (*path, "operations", oi)
        if suffix:
            allowed = {"opcode", "inputs", "outputs", "source", "constraints", "metadata"}
            if suffix[0] not in allowed:
                return []
            valid_index = (len(suffix) == 2 and suffix[0] in {"inputs", "outputs"} and suffix[1].isdecimal()
                           and int(suffix[1]) < len(ops[oi].get(suffix[0], [])))
            if len(suffix) == 1 or valid_index:
                return [field_slot(facts, (*path, suffix[0], *((int(suffix[1]),) if valid_index else ())))]
            return []
        # An uncategorized source-review finding cannot prove which field must change.
        # The patch may elect one of these existing semantic faces or one bounded region.
        return [field_slot(facts, (*path, key)) for key in ("opcode", "inputs", "outputs", "constraints", "source")
                ] + [_region_slot(facts, bi)]
    if oi != len(ops):
        return []
    exit_kind = block["exit"]["kind"]
    known_fields = {"jump": ("target",), "branch": ("conditions", "arms"), "return": ("values",)}
    path = (*path, "exit")
    if suffix and suffix[0] == "inputs":
        field = {"branch": "conditions", "return": "values"}.get(exit_kind)
        if field is None:
            return []
        valid_index = len(suffix) == 2 and suffix[1].isdecimal() and int(suffix[1]) < len(block["exit"][field])
        if len(suffix) == 1 or valid_index:
            return [field_slot(facts, (*path, field, *((int(suffix[1]),) if valid_index else ())))]
        return []
    return [_region_slot(facts, bi)] + [field_slot(facts, (*path, key))
        for key in (*known_fields[exit_kind], "source", "constraints")] if not suffix else []


def _targets(assembly, finding, files):
    if finding.get("domain") != "cfg":
        return []
    refs = finding.get("source_refs", [])
    if not refs:
        return []
    try:
        for ref in refs:
            validate_source_ref(ref, files)
    except (ValueError, TypeError):
        return []
    index = {assembly.id_map["blocks"][block["ref"]]: bi
             for bi, block in enumerate(assembly.facts["blocks"])}
    selected = []
    for target in finding.get("target_ids", []):
        if not isinstance(target, str):
            continue
        edge_target = re.fullmatch(r"cfg:/edges/(0|[1-9][0-9]*)", target)
        if edge_target is not None:
            ordinal = int(edge_target[1])
            edges = assembly.cfg["edges"]
            if ordinal >= len(edges):
                continue
            edge = edges[ordinal]
            source = index.get(edge["source_block_id"])
            if source is None:
                continue
            exit = assembly.facts["blocks"][source]["exit"]
            path = ("blocks", source, "exit")
            ids = assembly.id_map["blocks"]
            if exit["kind"] == "jump" and edge["condition_text"] is None and ids[exit["target"]] == edge["target_block_id"]:
                selected.append(field_slot(assembly.facts, (*path, "target")))
            if exit["kind"] == "branch":
                matches = [ai for ai, arm in enumerate(exit["arms"])
                           if ids[arm["target"]] == edge["target_block_id"]
                           and (arm["condition"] or "").strip() == (edge["condition_text"] or "")]
                if len(matches) == 1:
                    selected.append(field_slot(assembly.facts, (*path, "arms", matches[0])))
            continue
        match = re.fullmatch(r"cfg:/blocks/([^/]+)(?:/instructions/(0|[1-9][0-9]*))?(/.*)?", target)
        if match is None:
            continue
        ref = match[1].replace("~1", "/").replace("~0", "~")
        if ref not in index:
            continue
        suffix = tuple(match[3][1:].split("/")) if match[3] else ()
        selected.extend(_simple_slots(assembly.facts, index[ref],
                                      int(match[2]) if match[2] is not None else None, suffix))
    return [slot for slot in selected if slot is not None]


def _context(assembly, slots):
    """Display known producer identities even when the only base is an incomplete draft."""
    rows = assembly.facts.get("blocks")
    if not slots or not isinstance(rows, list):
        return []
    affected = {slot["path"][1] for slot in slots.values() if slot["path"][0] == "blocks"}
    known = {bi: block for bi, block in enumerate(rows) if isinstance(block, dict)
             and isinstance(block.get("ref"), str) and block["ref"]}
    roots = {block["ref"] for bi, block in known.items() if bi in affected}
    predecessors = defaultdict(set)
    block_edges = {}
    for block in known.values():
        ref, exit = block["ref"], block.get("exit")
        if not isinstance(exit, dict):
            continue
        if exit.get("kind") == "jump":
            raw = [(ref, exit.get("target"), None)]
        elif exit.get("kind") == "branch" and isinstance(exit.get("arms"), list):
            raw = [(ref, arm.get("target"), arm.get("condition")) for arm in exit["arms"] if isinstance(arm, dict)]
        else:
            raw = []
        block_edges[ref] = [edge for edge in raw if isinstance(edge[1], str)]
        for source, target, _ in block_edges[ref]:
            predecessors[target].add(source)
    upstream, pending = set(), list(roots)
    while pending:
        ref = pending.pop()
        if ref not in upstream:
            upstream.add(ref)
            pending.extend(predecessors[ref] - upstream)
    connected = {target for ref in roots for _, target, _ in block_edges.get(ref, [])}
    result = []
    for block in known.values():
        ref = block["ref"]
        if roots and ref not in upstream | connected:
            continue
        operations = block.get("operations")
        compact = []
        for row in operations if isinstance(operations, list) else []:
            if not isinstance(row, dict) or not isinstance(row.get("ref"), str):
                continue
            names = assembly.id_map.get("instructions", {})
            compact.append({key: row[key] for key in ("ref", "opcode", "outputs", "source")
                            if key in row and row[key] is not None})
            compiled = names.get(instruction_ref(ref, row["ref"]))
            if compiled is not None:
                compact[-1]["canonical_instruction"] = compiled
        result.append({"block_ref": ref, "operations": compact,
            "control_edges": [list(edge) for edge in block_edges.get(ref, [])
                              if edge[0] in roots or edge[1] in roots]})
    return result


def plan_graph_repair(assembly, *, findings=(), files):
    """Bind every writable slot, diagnostic and review finding to its exact base."""
    if assembly.source_sha256 != source_digest(files):
        raise ValueError("Graph repair source differs from the assembled facts")
    if not isinstance(findings, (list, tuple)) or any(not isinstance(row, dict) for row in findings):
        raise ValueError("Graph repair findings must be source-review records")
    if assembly.cfg is not None and assembly.gaps:
        raise ValueError("An accepted graph cannot carry assembly failures")
    slots = deepcopy(assembly.slots)
    unsupported = []
    for finding in findings:
        local = _targets(assembly, finding, files) if assembly.cfg is not None else []
        if not local:
            unsupported.append(finding.get("id") or canonical_sha256(finding)[:24])
        for slot in local:
            saved = slots.setdefault(slot["slot_id"], slot)
            if finding.get("id") is not None:
                finding_ids = saved.setdefault("finding_ids", [])
                if finding["id"] not in finding_ids:
                    finding_ids.append(finding["id"])
    body = {"identity": IDENTITY, "base": {key: value for key, value in assembly.to_receipt().items()
            if key not in {"facts", "slots", "gaps", "id_map"}},
        "mode": "slots" if slots else "unaddressable" if assembly.gaps or findings else "no_patch",
        "slots": slots, "gaps": deepcopy(assembly.gaps), "context": _context(assembly, slots),
        "remaining_findings": deepcopy(list(findings)), "unaddressable_findings": unsupported}
    return {**body, "plan_sha256": canonical_sha256(body)}


def _replace(facts, path, value):
    parent = facts
    for step in path[:-1]:
        parent = parent[step]
    parent[path[-1]] = deepcopy(value)


def _region_changes(facts, slot, rows, files):
    # First validate the local wire types before reading the promised boundary.
    from .graph_facts import Block

    if not isinstance(rows, list) or not rows:
        raise ValueError("A region value is a nonempty array of blocks")
    normalized = [Block.model_validate(row).model_dump(mode="json", exclude_unset=True) for row in rows]
    root = slot["target"]
    names = [block["ref"] for block in normalized]
    if names[0] != root or len(set(names)) != len(names) or any(
            not name.startswith(slot["new_block_prefix"]) for name in names[1:]):
        raise ValueError("A region must retain its entry block and use local names for new blocks")
    old_index = slot["path"][1]
    outsiders = {block["ref"] for bi, block in enumerate(facts["blocks"]) if bi != old_index}
    if outsiders.intersection(names):
        raise ValueError("A local region cannot replace an outside block")
    for block in normalized:
        for action in [*block["operations"], block["exit"]]:
            span = action.get("source")
            if span is not None:
                validate_source_ref(span, files)
    all_edges = [edge for block in normalized for edge in _edges(block)]
    old = facts["blocks"][old_index]
    # Ordinary opcodes are open strings, so the compiler cannot certify that
    # a newly inserted or moved operation is free of effects.
    if (normalized[0]["source_kind"] != old["source_kind"]
            or normalized[0]["operations"] != old["operations"]
            or any(row["source_kind"] != "normal" or row["operations"] for row in normalized[1:])):
        raise ValueError("A local topology update must preserve the existing actions and acquisition effects")
    if (normalized[0].get("constraints", []) != old.get("constraints", [])
            or normalized[0]["exit"].get("constraints", []) != old["exit"].get("constraints", [])
            or any(row.get("constraints") or row["exit"].get("constraints") for row in normalized[1:])):
        raise ValueError("A local topology update must preserve declaration scopes")
    had_self_loop = any(source == target == root for source, target, _ in _edges(old))
    if any(target == root for _, target, _ in all_edges) and (not had_self_loop or len(normalized) > 1):
        raise ValueError("A local topology update cannot add repeated visits to the original action block")
    adjacent = defaultdict(set)
    for source, target, _ in all_edges:
        if target in names:
            adjacent[source].add(target)
    pending, reachable = [root], set()
    while pending:
        current = pending.pop()
        if current not in reachable:
            reachable.add(current)
            pending.extend(adjacent[current])
    if reachable != set(names):
        raise ValueError("New region blocks must be reachable from the frozen entry")
    if len(normalized) > 1:
        indegree = dict.fromkeys(names, 0)
        for targets in adjacent.values():
            for target in targets:
                indegree[target] += 1
        ready = [name for name, degree in indegree.items() if degree == 0]
        visited = 0
        while ready:
            visited += 1
            for target in adjacent[ready.pop()]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    ready.append(target)
        if visited != len(names):
            raise ValueError("A local topology update must not introduce cycles that can suppress boundary effects")
    boundary = slot["boundary"]
    if dict(_returns(normalized)) != boundary["return_values"]:
        raise ValueError("A local topology update cannot add, remove or replace a returned value")
    outbound = Counter((target, guard) for _, target, guard in all_edges if target not in names)
    if outbound != Counter(tuple(pair) for pair in boundary["outbound_control"]):
        raise ValueError("A local region cannot change its outgoing control boundary")
    defs = set().union(*(_definitions(block) for block in normalized))
    uses = set().union(*(_uses(block) for block in normalized))
    if uses - defs != set(boundary["inbound_results"]) or not set(boundary["outbound_results"]) <= defs:
        raise ValueError("A local region must preserve its incoming and outgoing result identities")
    return normalized


def _compile_edits(assembly, edits, files):
    if not edits:
        return assembly
    merged, regions = deepcopy(assembly.facts), []
    for _, slot, value in edits:
        if slot["kind"] == "region":
            regions.append((slot["path"][1], value))
        else:
            _replace(merged, slot["path"], value)
    for index, rows in sorted(regions, reverse=True):
        merged["blocks"][index:index + 1] = rows
    return assemble_graph_facts(merged, files=files, canonical_ids=assembly.id_map or None,
                                legacy_cfg=assembly.legacy_cfg)


def apply_graph_updates(assembly, plan, updates, *, files):
    """Merge only the program-issued slots, then compile the complete new candidate."""
    checked = plan_graph_repair(assembly, findings=plan.get("remaining_findings", []), files=files)
    if checked != plan:
        raise ValueError("Graph repair plan differs from its bound facts, source or scope")
    if not isinstance(updates, dict) or set(updates) != {"plan_sha256", "updates"} or not isinstance(updates["updates"], list):
        raise structural_error("cfg_slot_response", "/updates", "Expected a bound array of typed slot updates.")
    if updates["plan_sha256"] != plan["plan_sha256"]:
        raise structural_error("cfg_slot_identity", "/plan_sha256", "The reply belongs to another graph repair plan.")
    modifications, diagnostics = [], []

    def reject(index, code, message, slot_id=None, causes=()):
        diagnostics.append({"code": code, "path": f"/updates/{index}", "message": message,
                            **({"slot_id": slot_id} if slot_id is not None else {}),
                            **({"causes": deepcopy(list(causes))} if causes else {})})

    for index, row in enumerate(updates["updates"]):
        try:
            entry = Update.model_validate(row)
            canonical_sha256(entry.value)
        except ValidationError:
            reject(index, "cfg_slot_record", "Expected this record to provide its slot ID and value.")
            continue
        except (ValueError, TypeError):
            reject(index, "cfg_slot_record", "The slot value must be finite JSON.")
            continue
        slot = plan["slots"].get(entry.slot_id)
        if slot is None:
            reject(index, "cfg_slot_scope", "This slot is not writable in the bound repair plan.", entry.slot_id)
            continue
        modifications.append((index, slot, entry.value))
    edits = []
    for index, slot, value in modifications:
        path = tuple(slot["path"])
        if any(path[:len(other)] == other or other[:len(path)] == path
               for other_index, other_slot, _ in modifications if other_index != index
               for other in [tuple(other_slot["path"])]):
            reject(index, "cfg_slot_conflict", "Two updates address overlapping facts.", slot["slot_id"])
            continue
        if slot["kind"] == "region":
            try:
                value = _region_changes(assembly.facts, slot, value, files)
            except (ValueError, TypeError) as error:
                reject(index, "cfg_region_boundary", str(error), slot["slot_id"])
                continue
        edits.append((index, slot, value))
    result = _compile_edits(assembly, edits, files)
    if assembly.cfg is not None and result.cfg is None:
        independent = []
        for edit in edits:
            index, slot, _ = edit
            single = _compile_edits(assembly, [edit], files)
            if single.cfg is not None:
                independent.append(edit)
            else:
                reject(index, "cfg_slot_rejected", "This change has no independently valid merge.",
                       slot["slot_id"], single.gaps)
        result = _compile_edits(assembly, independent, files)
        if result.cfg is None:
            for index, slot, _ in independent:
                reject(index, "cfg_slot_merge_conflict", "Individually valid changes conflict when combined.",
                       slot["slot_id"], result.gaps)
            result = assembly
    return replace(result, patch_diagnostics=[*assembly.patch_diagnostics, *diagnostics])
