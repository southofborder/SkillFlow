"""A bounded multi-block edit for acquisition, invocation selection and direct uses."""
from collections import Counter
from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import validate_source_ref


def occurrence_slots(assembly, slots, gaps, regions):
    from .graph_slots import _definitions, _edges, _returns, _uses
    groups = []
    for gap in gaps:
        if gap["code"] != "acquisition_occurrence":
            continue
        owned = set(gap["block_indices"])
        prior = [g for g in groups if owned.intersection(g[0])]
        for indices, _ in prior:
            owned.update(indices)
        rows = [row for _, group in prior for row in group] + [gap]
        groups = [g for g in groups if g not in prior] + [(owned, rows)]
    if not groups:
        return
    blocks = assembly.facts["blocks"]
    for indices, failures in groups:
        indices = sorted(indices)
        root = min(f["acquisition_block"] for f in failures)
        root_ref = blocks[root]["ref"]
        old = [blocks[i] for i in indices]
        refs = {b["ref"] for b in old}
        outside = [b for i, b in enumerate(blocks) if i not in indices]
        defs = set().union(*map(_definitions, old))
        slot_id = "cfg_occurrences_" + canonical_sha256([b["ref"] for b in old])[:24]
        slot = {"kind": "occurrence_region", "slot_id": slot_id, "target": root_ref,
                "path": ["blocks", root], "block_indices": indices, "old_value": deepcopy(old),
                "new_block_prefix": root_ref + ".",
                "acquisitions": [[blocks[f["acquisition_block"]]["ref"],
                                  blocks[f["acquisition_block"]]["operations"][f["action_index"]]["ref"]]
                                 for f in failures],
                "source_sites": [],
                "boundary": {
                    "inbound_control": [list(e) for b in outside for e in _edges(b) if e[1] in refs],
                    "outbound_control": [[t, g] for b in old for _, t, g in _edges(b) if t not in refs],
                    "inbound_results": sorted(set().union(*map(_uses, old)) - defs),
                    "outbound_results": sorted(defs & set().union(*map(_uses, outside))),
                    "return_values": dict(_returns(old))}}
        for f in failures:
            for site in f["source_sites"]:
                if site not in slot["source_sites"]:
                    slot["source_sites"].append(site)
                if "path" in f and "name" not in site:
                    reads = slot.setdefault("required_reads", [])
                    if site not in reads:
                        reads.append(site)
        covered = {k for k, item in slots.items() if item["path"][0] == "blocks" and item["path"][1] in indices}
        for error in gaps:
            if error.get("slot_id") in covered:
                error["slot_id"] = slot_id
        for key in covered:
            del slots[key]
        slots[slot_id] = slot
        regions.update((i, slot) for i in indices)


def _roles(op):
    from .entry_occurrences import _read_actions
    return {part.get("role") or part["kind"] for part in _read_actions(op)}


def _span(op):
    span = op.get("source") or op.get("metadata", {}).get("source_span")
    return span if isinstance(span, dict) and {"file", "start_line", "end_line"} <= span.keys() else None


def _inside(span, refs):
    return span and any(ref["file"] == span["file"] and ref["start_line"] <= span["start_line"]
                        and span["end_line"] <= ref["end_line"] for ref in refs)


def validate_region(facts, slot, rows, files):
    from .entry_occurrences import callable_signature_ports, declaration_only
    from .graph_facts import Block
    from .graph_slots import _definitions, _edges, _returns, _uses
    if not isinstance(rows, list) or not rows:
        raise ValueError("Return a nonempty Block[] for the invocation region.")
    for row in rows:
        Block.model_validate(row)
    old = {b["ref"]: b for b in slot["old_value"]}
    updates = {b["ref"]: b for b in rows}
    if len(updates) != len(rows):
        raise ValueError("Each proposed block reference must be unique.")
    proposed = {**old, **updates}
    rows = list(proposed.values())
    outside = {b["ref"] for b in facts["blocks"]} - old.keys()
    if outside.intersection(proposed) or any(not ref.startswith(slot["new_block_prefix"])
                                            for ref in proposed.keys() - old.keys()):
        raise ValueError("An invocation region must use its scoped prefix for new blocks.")
    boundary = slot["boundary"]
    fixed_entries = {e[1] for e in boundary["inbound_control"]}
    if facts["entry"] in old:
        fixed_entries.add(facts["entry"])
    if not fixed_entries <= proposed.keys():
        raise ValueError("The invocation region lost an externally selected entry.")
    if Counter((t, g) for b in rows for _, t, g in _edges(b) if t not in proposed) != Counter(
            tuple(e) for e in boundary["outbound_control"]):
        raise ValueError("The invocation region changed an outward control target or guard.")
    defs = set().union(*map(_definitions, rows))
    if (not set(boundary["outbound_results"]) <= defs or
            set().union(*map(_uses, rows)) - defs != set(boundary["inbound_results"])):
        raise ValueError("The invocation region changed an externally visible value port.")
    if dict(_returns(rows)) != boundary["return_values"]:
        raise ValueError("The invocation region changed the returned value ports.")
    ports = {(p["owner"], p["parameter"]) for b in rows if b["source_kind"] == "context"
             for op in b["operations"] for p in callable_signature_ports(op, files)}
    required = {(f'{s["file"]}:{s["start_line"]}:{s["name"]}', p) for s in slot["source_sites"]
                if "name" in s for p in s["parameters"]}
    missing = sorted(required - ports)
    if missing:
        raise ValueError("Missing sourced invocation parameter bindings: " +
                         ", ".join(f"{owner}({p})" for owner, p in missing))
    if slot.get("required_reads"):
        kept = [_span(op) for b in rows for op in b["operations"] if _roles(op) <= {"read", "receive"}]
        if any(not any(_inside(span, [prior]) for span in kept) for prior in slot["required_reads"]):
            raise ValueError("Keep each distinct original read at its sourced occurrence.")

    origins = set(map(tuple, slot["acquisitions"]))
    pooled = {v for b in old.values() for op in b["operations"] if (b["ref"], op["ref"]) in origins
              for v in op["outputs"]}
    protected = {}
    editable = {}
    anchors = list(slot["source_sites"])
    call_anchors = []
    for b in old.values():
        anchors.extend(s for op in [*b["operations"], b["exit"]] if (s := _span(op)))
        for op in b["operations"]:
            site = b["ref"], op["ref"]
            if site in origins:
                continue
            if _roles(op) <= {"value"} and any(v.get("result") in pooled for v in op["inputs"]):
                editable[site] = op
                if _span(op):
                    call_anchors.append(_span(op))
            else:
                protected[site] = op
    for b in rows:
        before = old.get(b["ref"])
        actual_protected = []
        for op in b["operations"]:
            site = b["ref"], op["ref"]
            prior = protected.get(site)
            if prior is not None:
                actual_protected.append(site)
                if op == prior:
                    continue
                if not _only_rebind(prior, op, pooled):
                    raise ValueError("Only the pooled input operands of an unrelated action may be rebound.")
                continue
            if op == editable.get(site) or before and site in origins and op in before["operations"]:
                continue
            span = _span(op)
            if not _inside(span, anchors):
                raise ValueError("A replacement action must cite a source site in its invocation region.")
            validate_source_ref(span, files)
            roles = _roles(op)
            if roles - {"read", "receive", "value"} and not (roles == {"call"} and _inside(span, call_anchors)):
                raise ValueError("New actions must acquire inputs or bind arguments of a covered invocation.")
            if "read" in roles and declaration_only(span, files):
                raise ValueError("A signature proves supplied arguments; a new independent read needs its actual read site.")
            for part in op.get("source_actions", []):
                if not _inside(part["source"], anchors):
                    raise ValueError("A replacement source action falls outside this invocation region.")
        if actual_protected != [site for site in protected if site[0] == b["ref"]]:
            raise ValueError("Keep unrelated source actions in the same block and source order.")
        if before and before.get("constraints", []) != b.get("constraints", []):
            raise ValueError("Keep restrictions on their original block.")
        if not before or before["exit"] != b["exit"]:
            if before and before["exit"].get("constraints", []) != b["exit"].get("constraints", []):
                raise ValueError("Keep restrictions on their original exit.")
            if not _inside(_span(b["exit"]), anchors):
                raise ValueError("A changed invocation exit needs source in the authorized region.")
            if before and actual_protected and not any(
                    v.get("result") in pooled for v in before["exit"].get("conditions", [])):
                # Data-operand corrections must not silently change the activation
                # condition of preexisting I/O or skip its old continuation.
                if _edges(before) != _edges(b):
                    raise ValueError("Keep the control edges following unrelated source actions.")
    if any(ref not in proposed for ref, _ in protected):
        raise ValueError("The invocation region removed a block with unrelated source actions.")
    if any(b.get("constraints") and b["ref"] not in proposed for b in old.values()):
        raise ValueError("The invocation region removed a restricted block.")
    previously_incoming = {target for old_block in facts["blocks"] for _, target, _ in _edges(old_block)}
    incoming = fixed_entries | {target for b in rows for _, target, _ in _edges(b)}
    for b in rows:
        ref = b["ref"]
        if ref in incoming or ref in old and ref not in previously_incoming:
            continue
        if b["source_kind"] not in {"context", "external"} or not b["operations"] or not _span(b["operations"][0]):
            raise ValueError("A new independent analysis root requires its own source-backed invocation or read.")
    return rows


def _only_rebind(old, new, pooled):
    if old.keys() != new.keys() or len(old["inputs"]) != len(new["inputs"]):
        return False
    if any(old[k] != new[k] for k in old if k != "inputs"):
        return False
    return all(a == b or a.get("result") in pooled and set(b) == {"result"}
               for a, b in zip(old["inputs"], new["inputs"]))
