"""Bound call-site, formal and return edits to their physical caller/callee relationship."""

from collections import Counter, defaultdict
from copy import deepcopy
import re

from skillflow.common.recording import canonical_sha256
from .entry_occurrences import _body_owner
from .source_calls import _edges, _result, _text, _JS_RESULT, inline_calls, source_call, source_span


def _variable(span, files):
    match = _JS_RESULT.fullmatch(_text(span, files))
    return match["variable"] if match else None


def _body(blocks, entry, sig):
    pending, seen = [entry], set()
    while pending:
        ref = pending.pop()
        if ref in seen or ref not in blocks:
            continue
        block = blocks[ref]
        span = source_span(block["exit"])
        if (
            not span
            or sig.file != span["file"]
            or not sig.first <= span["start_line"] <= span["end_line"] <= sig.body_end
        ):
            continue
        seen.add(ref)
        pending.extend(_edges(block))
    return seen


def call_sites(facts, files):
    blocks = {b["ref"]: b for b in facts["blocks"]}
    predecessors = defaultdict(list)
    for block in blocks.values():
        for dest in _edges(block):
            predecessors[dest].append(block)
    for caller, invoke, call, entry, formal, site, bridges in inline_calls(facts, files):
        span = source_span(invoke)
        if not site.body_end:
            continue
        body = _body(blocks, entry["ref"], site)
        owner = _body_owner(span, files)
        edits = {
            caller["ref"]: {invoke["ref"]: "arguments", "$exit": "entry"},
            entry["ref"]: {formal["ref"]: "formal"},
        }
        diagnostics = []
        # The exact same physical call along a linear path has one execution.
        # Stop at a join, conditional, or change of caller; a shared callee body
        # reached through a separate caller is another dynamic invocation.
        earlier = [(caller, caller["operations"][:-1])]
        seen = {caller["ref"]}
        current = caller
        while owner and len(predecessors[current["ref"]]) == 1:
            parent = predecessors[current["ref"]][0]
            if (
                parent["ref"] in seen
                or parent["exit"]["kind"] != "jump"
                or _body_owner(source_span(parent["exit"]), files) != owner
            ):
                break
            earlier.append((parent, parent["operations"]))
            seen.add(parent["ref"])
            current = parent
        for block, operations in earlier:
            for operation in operations:
                if operation["opcode"] == "call" and source_span(operation) == span:
                    edits.setdefault(block["ref"], {})[operation["ref"]] = "duplicate"
                    diagnostics.append(
                        f"One physical call to {call.callee!r} already executes through "
                        f"the callee body; remove or reconnect its duplicate at {block['ref']}/{operation['ref']}."
                    )
        # One formal record may merge the same parameter from several distinct callers.
        actual_values = invoke["outputs"] or [v["result"] for v in invoke["inputs"] if "result" in v]
        formal_values = [_result(v) for v in formal["inputs"]]
        if call.args and actual_values and not set(actual_values) <= set(formal_values):
            diagnostics.append(
                "The callee's formal binding must consume this caller's actual argument versions."
            )
        elif (
            len(actual_values) == len(call.args) == len(site.parameters) == len(formal_values)
            and len(formal["outputs"]) == len(formal_values)
            and len(formal_values) > 1
            and formal_values != actual_values
        ):
            diagnostics.append(
                "The callee's ordered formal parameters must receive the actual arguments in source order."
            )
        returns, returned_versions = [], set()
        # Locate the next actual source use even when the submitted CFG has lost its return edge.
        uses = []
        if call.assigned and owner:
            for dest in blocks.values():
                for candidate in [*dest["operations"], dest["exit"]]:
                    at = source_span(candidate)
                    if (
                        at
                        and at["start_line"] > span["end_line"]
                        and _body_owner(at, files) == owner
                        and re.search(r"\b" + re.escape(call.assigned) + r"\b", _text(at, files))
                    ):
                        uses.append((at["start_line"], dest["ref"], candidate))
        first_use = min((line for line, _, _ in uses), default=None)
        for line, dest, op in uses:
            if line == first_use:
                edits.setdefault(dest, {})[op.get("ref", "$exit")] = "consumer"
        for ref in sorted(body):
            block = blocks[ref]
            name = _variable(source_span(block["exit"]), files)
            if not name:
                continue
            returns.append(ref)
            producers = []
            for b in body:
                for op in blocks[b]["operations"]:
                    producing = source_call(source_span(op), files)
                    if producing and producing.assigned == name and len(op["outputs"]) == 1:
                        producers.append(op["outputs"][0])
            if len(producers) == 1:
                returned_versions.update(producers)
            return_values = [v.get("result") for v in block["exit"].get("values", [])]
            if len(producers) == 1 and block["exit"]["kind"] == "return" and return_values != producers:
                diagnostics.append(
                    f"The body return at {ref} must forward its actual {name!r} version {producers[0]!r}."
                )
            if not call.assigned or not owner:
                continue
            continuations = _edges(block)
            if (
                uses
                and continuations
                and not any(dest in edits and dest not in body for dest in continuations)
            ):
                diagnostics.append(
                    "The callee return must reconnect to the consumer belonging to this invocation."
                )
            for dest in continuations:
                if dest in body or dest not in blocks:
                    continue
                continuation = blocks[dest]
                # A common return can have several caller-specific continuations.
                for op in [*continuation["operations"], continuation["exit"]]:
                    position = source_span(op)
                    if (
                        not position
                        or _body_owner(position, files) != owner
                        or position["start_line"] < span["end_line"]
                    ):
                        continue
                    if not re.search(r"\b" + re.escape(call.assigned) + r"\b", _text(position, files)):
                        continue
                    key = op.get("ref", "$exit")
                    edits.setdefault(dest, {})[key] = "consumer"
                    values = [_result(v) for v in op.get("inputs", op.get("values", []))]
                    if len(producers) == 1 and producers[0] not in values:
                        diagnostics.append(
                            f"The caller's consumer {dest}/{key} must use the body return version {producers[0]!r}."
                        )
            if uses and block["exit"]["kind"] == "return":
                diagnostics.append("The local call's result has no return edge to its caller's consumer.")
        for ref in returns:
            edits.setdefault(ref, {})["$exit"] = "return"
        for ref in bridges:
            edits.setdefault(ref, {})
        yield {
            "caller": caller["ref"],
            "callee": site.owner,
            "site": span,
            "formals": entry["ref"],
            "returns": returns,
            "returned_versions": sorted(returned_versions),
            "edits": edits,
            "errors": diagnostics,
        }


def register_slots(assembly, slots, gaps, regions, findings, files):
    from .graph_slots import _targets, _edges as edges, _uses, _definitions

    if not assembly.check_calls or not (gaps or findings):
        return
    blocks = assembly.facts.get("blocks", [])
    if not isinstance(blocks, list) or not all(
        isinstance(b, dict) and isinstance(b.get("operations"), list) and isinstance(b.get("exit"), dict)
        for b in blocks
    ):
        return
    index = {b.get("ref"): i for i, b in enumerate(blocks)}
    grants = [
        slot
        for finding in findings
        if assembly.cfg and finding.get("required_graph_edit") in {"action_inventory", "topology"}
        for slot in _targets(assembly, finding, files)
    ]
    failing = {gap["call_site"] for gap in gaps if gap["code"] == "call_return_binding"}
    if not grants and not failing:
        return
    groups = {}
    for site in call_sites(assembly.facts, files):
        owner = blocks[index[site["caller"]]]
        invocation = owner["operations"][-1]["ref"]
        targeted = any(
            slot["path"][1] == index[site["caller"]]
            and (
                slot["kind"] == "region"
                or slot["kind"] == "action_region"
                and invocation in slot["editable_action_refs"]
            )
            for slot in grants
        )
        if not targeted and site["caller"] not in failing:
            continue
        groups.setdefault(site["formals"], []).append(site)
    for sites in groups.values():
        permissions = defaultdict(dict)
        for s in sites:
            for block, actions in s["edits"].items():
                permissions[block].update(actions)
        indices = sorted(index[ref] for ref in permissions)
        if any(i in regions for i in indices):
            continue
        root = indices[0]
        old = [blocks[i] for i in indices]
        outside = [b for i, b in enumerate(blocks) if i not in indices]
        defined = set().union(*map(_definitions, old))
        names = set(permissions)
        slot = {
            "kind": "call_region",
            "target": blocks[root]["ref"],
            "path": ["blocks", root],
            "block_indices": indices,
            "old_value": deepcopy(old),
            "editable_actions": dict(permissions),
            "calls": [{k: s[k] for k in ("caller", "site", "callee", "formals", "returns")} for s in sites],
            "boundary": {
                "inbound_results": sorted(set().union(*map(_uses, old)) - defined),
                "returned_versions": sorted({v for s in sites for v in s["returned_versions"]}),
                "outbound_results": sorted(defined & set().union(*map(_uses, outside))),
                "inbound_control": [list(e) for b in outside for e in edges(b) if e[1] in names],
                "outbound_control": [list(e) for b in old for e in edges(b) if e[1] not in names],
            },
        }
        slot_id = "cfg_calls_" + canonical_sha256([b["ref"] for b in old])[:24]
        slot["slot_id"] = slot_id
        for s in gaps:
            if (
                s.get("code") == "call_return_binding"
                and s.get("call_site") in {x["caller"] for x in sites}
                and s.get("slot_id")
            ):
                slots.pop(s["slot_id"], None)
                s["slot_id"] = slot_id
        slots[slot_id] = slot
        regions.update((i, slot) for i in indices)


def validate_call_region(facts, slot, proposed, files):
    from .graph_facts import Block
    from .graph_slots import _edges as edges, _definitions, _uses

    if not isinstance(proposed, list) or not proposed:
        raise ValueError("Return the changed Block[] rows for the source-backed call region.")
    old = {b["ref"]: b for b in slot["old_value"]}
    updates = {}
    for row in proposed:
        Block.model_validate(row)
        ref = row["ref"]
        if ref in updates or ref not in old:
            raise ValueError("A call-region update must name an authorized existing block exactly once.")
        before = old[ref]
        roles = slot["editable_actions"][ref]
        if {k: v for k, v in row.items() if k not in {"operations", "exit"}} != {
            k: v for k, v in before.items() if k not in {"operations", "exit"}
        }:
            raise ValueError("Keep each call-region block's activation and constraints.")
        original = {op["ref"]: op for op in before["operations"]}
        refs = [op["ref"] for op in row["operations"]]
        if refs != [key for key in original if roles.get(key) != "duplicate" or key in refs]:
            raise ValueError(
                "Keep each original physical action in order. Only an identified duplicate call may be removed."
            )
        pairs = [(original[op["ref"]], op) for op in row["operations"]]
        for a, b in [*pairs, (before["exit"], row["exit"])]:
            if a == b:
                continue
            key = a.get("ref", "$exit")
            if key not in roles:
                raise ValueError("An update changed an unrelated action in the call region.")
            role = roles[key]
            allowed = (
                {"inputs"}
                if role == "consumer" and key != "$exit"
                else (
                    {"values", "conditions", "target", "arms", "kind"}
                    if key == "$exit"
                    else {
                        "inputs",
                        "outputs",
                        "ref",
                        "role",
                        "opcode",
                        "source_actions",
                        "metadata",
                        "source",
                    }
                )
            )
            if any(a.get(k) != b.get(k) for k in a.keys() | b.keys() if k not in allowed):
                raise ValueError("Only the named call, parameter or return relationship is writable.")
            if role == "consumer" and a.get("kind") != b.get("kind"):
                raise ValueError("Keep the consumer at its original operation or terminator.")
            if key != "$exit" and role != "consumer":
                if source_span(a) != source_span(b) or any(
                    source_span(act) != source_span(a) for act in b.get("source_actions", [])
                ):
                    raise ValueError(
                        "The edited binding must keep its physical invocation or parameter evidence."
                    )
                new_roles = {action.get("role") or action["kind"] for action in b.get("source_actions", [])}
                if b["opcode"] not in {"value", "call", a["opcode"]} or new_roles - {"value", "call"}:
                    raise ValueError("This grant covers only argument/return binding and invocation.")
                metadata = {
                    k: v
                    for k, v in a.get("metadata", {}).items()
                    if k not in {"source_actions", "script_content", "source_span"}
                }
                edited = {
                    k: v
                    for k, v in b.get("metadata", {}).items()
                    if k not in {"source_actions", "script_content", "source_span"}
                }
                if edited != metadata:
                    raise ValueError("Keep the call's unrelated source metadata.")
        updates[ref] = row
    after = {**old, **updates}
    boundary = slot["boundary"]
    all_edges = [e for b in after.values() for e in edges(b)]
    if Counter(e for e in all_edges if e[1] not in old) != Counter(
        tuple(e) for e in boundary["outbound_control"]
    ):
        raise ValueError("Keep external control at the original source call and consumer.")
    defined = set().union(*map(_definitions, after.values()))
    new_inputs = set().union(*map(_uses, after.values())) - defined
    allowed = set(boundary["inbound_results"]) | set(boundary["returned_versions"])
    if not new_inputs <= allowed or not set(boundary["outbound_results"]) <= defined:
        raise ValueError("Keep the externally consumed results and input ports of this call region.")
    combined = {**facts, "blocks": [after.get(b["ref"], b) for b in facts["blocks"]]}
    verified = {
        (site["caller"], site["callee"]) for site in call_sites(combined, files) if not site["errors"]
    }
    if any((call["caller"], call["callee"]) not in verified for call in slot["calls"]):
        raise ValueError("The inlined caller must enter its actual callee and reconnect the returned value.")
    return list(after.values())
