"""Typed loop guards and persisted reachability; no source-language evaluator."""
from __future__ import annotations


def _empty_collection_base(data, identity, seen=frozenset()):
    """A filter or member-preserving map of an empty base remains empty.

    Follow only finite content alternatives, without evaluating predicates or
    rebuilding the registry. A recursive or otherwise unknown base proves
    nothing about cardinality.
    """
    if identity in seen:
        return False
    from skillflow.propagation.data.summary import content_options
    values = content_options(data, identity, seen)
    return bool(values) and all(
        (value["form"] == "literal" and value["value"] == [])
        or (value["form"] in {"subset_view", "mapped_collection"}
            and _empty_collection_base(data, value["base"], seen | {identity}))
        for value in values)


def guard_values(data, identities, predicate, *, traversal_exit=True):
    """Finite may-truths. A typed traversal can exhaust its collection."""
    def content(identity):
        value = data.get(identity)
        value = value.model_dump(mode="json") if hasattr(value, "model_dump") else value
        return value["content"]
    truths = set()
    for identity in identities:
        from skillflow.propagation.data.summary import content_options
        values = content_options(data, identity)
        for value in values:
            if predicate == "truthy":
                if value["form"] == "literal":
                    if type(value["value"]) is not bool:
                        raise ValueError("typed Boolean branch requires a Boolean, never source-language truthiness")
                    truths.add(value["value"])
                else:
                    truths.update((False, True))
            elif value["form"] == "literal":
                if type(value["value"]) is not list:
                    raise ValueError("typed collection branch requires a list")
                nonempty = bool(value["value"])
                truths.add(not nonempty if predicate == "empty" else nonempty)
                if nonempty and predicate == "has_member" and traversal_exit:
                    truths.add(False)
            elif value["form"] == "known_parts" and value.get("parts_complete"):
                if any(type(part["path"][0]) is str for part in value["parts"]):
                    raise ValueError("typed collection branch cannot traverse object fields")
                nonempty = bool(value["parts"])
                truths.add(not nonempty if predicate == "empty" else nonempty)
                if nonempty and predicate == "has_member" and traversal_exit:
                    truths.add(False)
            elif value["form"] in {"subset_view", "mapped_collection"} and _empty_collection_base(data, value["base"]):
                truths.add(predicate == "empty")
            else:
                truths.update((False, True))
    return truths or {False, True}


def admitted_instructions(cfg, annotation, records, data):
    """Recompute pruning from compiled guards and recorded actual operands.

    Missing records provide no proof of pruning. Reported target lists alone
    are insufficient to hide an unprocessed branch.
    """
    blocks = cfg["blocks"]
    incoming = {name: set() for name in blocks}
    outgoing = {name: set() for name in blocks}
    for edge in cfg["edges"]:
        source, target = edge["source_block_id"], edge["target_block_id"]
        incoming[target].add(source)
        outgoing[source].add(target)
    for block, body in blocks.items():
        for instruction in body["instructions"]:
            identity = instruction["id"]
            record = records.get(identity)
            if record is None:
                continue
            record = record.model_dump(mode="json") if hasattr(record, "model_dump") else record
            spec = annotation["ir_semantics"].get(identity)
            if spec is None:
                continue
            for event_index, event in enumerate(spec["events"]):
                if event.get("kind") == "for_each":
                    continue
                for op_index, op in enumerate(event["atomic_ops"]):
                    if op["op"] != "branch":
                        continue
                    actual = record["events"][event_index]["atomic_ops"][op_index]
                    if len(actual["inputs"]) != 1:
                        raise ValueError("branch record requires its actual condition operand")
                    truths = guard_values(data, actual["inputs"][0], op["predicate"])
                    expected = {op["true_target"] if truth else op["false_target"] for truth in truths}
                    if not set(actual.get("branch_targets", [])) <= expected:
                        raise ValueError("branch record admits a target ruled out by its typed guard")
                    for candidate in actual.get("alternatives", []):
                        values = guard_values(data, candidate["inputs"][0], op["predicate"])
                        permitted = {op["true_target"] if value else op["false_target"] for value in values}
                        if not set(candidate.get("branch_targets", [])) <= permitted:
                            raise ValueError("branch candidate route contradicts its typed operand")
                    outgoing[block] &= expected
    roots = {cfg["entry_block_id"], *(block for block in blocks if not incoming[block])}
    reached, pending = set(), list(roots)
    while pending:
        block = pending.pop()
        if block not in reached:
            reached.add(block)
            pending.extend(outgoing[block] - reached)
    return {ir["id"] for block in reached for ir in blocks[block]["instructions"]}
