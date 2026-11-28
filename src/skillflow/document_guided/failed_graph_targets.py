"""Source-review coordinates in a rejected GraphFacts response."""
from collections import Counter

from skillflow.common.source_evidence import _json_object, json_pointer, validate_source_ref
from .graph_facts import field_slot


def _name(row):
    ref = row.get("ref") if isinstance(row, dict) else None
    return ref if isinstance(ref, str) and ref.strip() == ref and ref else None


def _sites(facts):
    blocks = facts.get("blocks")
    if not isinstance(blocks, list):
        return
    counts = Counter(map(_name, blocks))
    for bi, block in enumerate(blocks):
        ref = _name(block)
        if not ref or counts[ref] != 1:
            continue
        prefix = "stage:graph" + json_pointer("blocks", ref)
        path = ("blocks", bi)
        yield prefix, path, None
        ops = block.get("operations")
        if isinstance(ops, list):
            names = Counter(map(_name, ops))
            for oi, op in enumerate(ops):
                name = _name(op)
                if name and names[name] == 1:
                    yield prefix + json_pointer("operations", name), (*path, "operations", oi), oi
        if isinstance(block.get("exit"), dict) and isinstance(ops, list):
            yield prefix + "/exit", (*path, "exit"), len(ops)


def failed_graph_targets(material, parent):
    """Stable names identify the authored facts, including when the response is JSON text."""
    key = "candidate" if "candidate" in material else "response"
    value = material.get(key)
    try:
        facts = _json_object(value)
    except (ValueError, TypeError):
        return []
    base = json_pointer("graph", "evidence", "material", key)
    return [{**parent, "id": name,
             "pointer": base + (json_pointer(*path) if isinstance(value, dict) else "")}
            for name, path, _ in _sites(facts)]


def failed_graph_slots(assembly, finding, files):
    """Grant edits at the reviewed draft sites. A stage-level finding has no local owner."""
    from .graph_slots import _action_slot, _region_slot
    if finding.get("domain") != "cfg" or not finding.get("source_refs"):
        return []
    refs = finding["source_refs"]
    try:
        for ref in refs:
            validate_source_ref(ref, files)
    except (ValueError, TypeError):
        return []
    wanted = set(finding.get("target_ids", []))
    capability = finding.get("required_graph_edit", "field")
    slots = []
    for name, path, oi in _sites(assembly.facts):
        if name not in wanted:
            continue
        bi = path[1]
        if capability in {"topology", "action_inventory"}:
            # A malformed neighbour can leave the result/control boundary unknown.
            # Its schema failures retain their ordinary field correction slots.
            try:
                if capability == "topology":
                    slots.append(_region_slot(assembly.facts, bi))
                else:
                    op = assembly.facts["blocks"][bi]["operations"][oi] if path[-2] == "operations" else None
                    slots.append(_action_slot(assembly.facts, bi, op["ref"] if op else None, refs))
            except (KeyError, TypeError, IndexError, AttributeError):
                continue
            continue
        if path[-1] == "exit":
            kind = assembly.facts["blocks"][bi]["exit"].get("kind")
            fields = {"jump": ("target",), "branch": ("conditions", "arms"), "return": ("values",),
                      "outcome_dispatch": ("producer", "on_return", "on_throw", "inputs")}.get(kind, ())
        else:
            fields = ("inputs", "outputs", "opcode", "constraints", "source") if oi is not None else ("constraints",)
        slots.extend(field_slot(assembly.facts, (*path, key)) for key in fields)
    return [slot for slot in slots if slot is not None]
