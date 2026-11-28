"""Lower a shared inline/public callee to ordinary call-site-specific CFG blocks."""
import ast
from collections import defaultdict
from copy import deepcopy
import re

from .entry_occurrences import _body_owner
from .graph_slots import _definitions, _uses
from .source_calls import _edges, inline_calls, source_span


def _contains(span, node):
    return span and span["start_line"] <= node.lineno <= node.end_lineno <= span["end_line"]


def _caller_source(site, span, call, files):
    """Locate consumers of the assigned result and handlers enclosing this exact call."""
    if not site.file.endswith(".py") or not call.assigned:
        return None
    try:
        tree = ast.parse(files[site.file])
    except SyntaxError:
        return None
    caller = _body_owner(span, files)
    next_uses = {node.lineno for node in ast.walk(tree) if isinstance(node, ast.Name)
                 and isinstance(node.ctx, ast.Load) and node.id == call.assigned and node.lineno > span["end_line"]
                 and _body_owner({"file": site.file, "start_line": node.lineno, "end_line": node.lineno}, files) == caller}
    handlers = {handler.lineno for node in ast.walk(tree) if isinstance(node, (ast.Try, getattr(ast, "TryStar", ast.Try)))
                and any(stmt.lineno <= span["start_line"] <= span["end_line"] <= stmt.end_lineno for stmt in node.body)
                for handler in node.handlers}
    returns = [node for node in ast.walk(tree) if isinstance(node, ast.Return)
               and _body_owner({"file": site.file, "start_line": node.lineno, "end_line": node.end_lineno}, files) == site]
    return next_uses, handlers, returns


def _source_role(target, value, site, caller_source, files):
    normal, handlers, _ = caller_source
    positions = [source_span(item) for item in [*target["operations"], target["exit"]]
                 if {"result": value} in item.get("inputs", item.get("values", item.get("conditions", [])))]
    caller_lines = {line for span in positions if span and span["file"] == site.file
                    and _body_owner(span, files) != site
                    for line in range(span["start_line"], span["end_line"] + 1)}
    roles = [kind for kind, lines in (("return", normal), ("throw", handlers)) if lines & caller_lines]
    return roles[0] if len(roles) == 1 else None


def _valid_carrier(value, role, region, blocks, incoming, returns):
    producers = [(ref, op) for ref in region for op in blocks[ref]["operations"] if value in op["outputs"]]
    if len(producers) != 1:
        return False
    ref, operation = producers[0]
    if role == "return":
        # The returned expression is produced at the physical return statement.
        return any(_contains(source_span(operation), ret) for ret in returns)
    # A predecessor merge carries precisely the individual operations' raised
    # values, independently of the normal return and their completion predicates.
    rows = operation.get("metadata", {}).get("predecessor_bindings")
    if not isinstance(rows, dict) or not rows or set(rows) != incoming[ref] or not set(rows) <= region:
        return False
    inputs = {item["result"] for item in operation["inputs"] if "result" in item}
    for pred, bindings in rows.items():
        name = bindings.get(value) if isinstance(bindings, dict) else None
        if not isinstance(name, str) or name not in inputs or name not in _definitions(blocks[pred]):
            return False
        # A completion flag, or a value consumed by the sibling continuation
        # (e.g. its successful response), cannot be its exceptional payload.
        siblings = set(_edges(blocks[pred])) - {ref}
        if (any(op.get("metadata", {}).get("paired_response") == name for op in blocks[pred]["operations"])
                or {"result": name} in blocks[pred]["exit"].get("conditions", [])
                or any(other not in blocks or name in _uses(blocks[other]) for other in siblings)):
            return False
    return True


def _region(entry, marker, site, blocks, files):
    region, routes, pending = set(), [], [entry]
    while pending:
        ref = pending.pop()
        if ref in region:
            continue
        block = blocks.get(ref)
        if not block or _body_owner(source_span(block["exit"]), files) != site:
            return None
        region.add(ref)
        if block["exit"].get("conditions") == [{"result": marker}]:
            routes.append(ref)
        else:
            pending.extend(_edges(block))
    return region, routes


def _targets(region, routes, site, blocks, incoming, caller_source, files):
    choices, carriers = {}, {}
    for ref in routes:
        arms = _edges(blocks[ref])
        if len(set(arms)) != 2 or any(dest not in blocks or dest in region for dest in arms):
            return None
        terminals = [dest for dest in arms if blocks[dest]["exit"]["kind"] == "return"
                     and not blocks[dest]["operations"] and _body_owner(source_span(blocks[dest]["exit"]), files) == site]
        if len(terminals) != 1:
            return None
        public = terminals[0]
        local = next(dest for dest in arms if dest != public)
        values = blocks[public]["exit"]["values"]
        if len(values) != 1 or "result" not in values[0] or incoming[public] != {ref}:
            return None
        value = values[0]["result"]
        role = _source_role(blocks[local], value, site, caller_source, files)
        if not role or not _valid_carrier(value, role, region, blocks, incoming, caller_source[2]):
            return None
        choices[ref] = (public, local)
        carriers[role] = carriers.get(role, set()) | {value}
    controls = {v["result"] for ref in region for v in blocks[ref]["exit"].get("conditions", []) if "result" in v}
    raised = carriers.get("throw", set())
    raised_inputs = {operand["result"] for ref in region for op in blocks[ref]["operations"]
                     if raised.intersection(op["outputs"]) for operand in op["inputs"] if "result" in operand}
    if not choices or carriers.get("return", set()) & (controls | raised | raised_inputs):
        return None
    return choices


def _rename_metadata(metadata, names):
    """Only remap identifier positions. Field names, source actions and arbitrary metadata are data."""
    for key in ("receiver", "paired_response"):
        value = metadata.get(key)
        if isinstance(value, str):
            metadata[key] = names.get(value, value)
    if isinstance(fields := metadata.get("parameter_fields"), dict):
        metadata["parameter_fields"] = {key: names.get(value, value) if isinstance(value, str) else value
                                        for key, value in fields.items()}
    if isinstance(producers := metadata.get("output_producers"), dict):
        metadata["output_producers"] = {names.get(key, key): value for key, value in producers.items()}
    if isinstance(bindings := metadata.get("predecessor_bindings"), dict):
        metadata["predecessor_bindings"] = {names.get(pred, pred): {
            names.get(k, k): names.get(v, v) if isinstance(v, str) else v for k, v in row.items()
        } if isinstance(row, dict) else row for pred, row in bindings.items()}


def _rename_block(block, names, mentions=None):
    block["ref"] = names.get(block["ref"], block["ref"])
    for row in [*block["operations"], block["exit"]]:
        for key in ("inputs", "conditions", "values"):
            for operand in row.get(key, []):
                if "result" in operand:
                    operand["result"] = names.get(operand["result"], operand["result"])
        if "outputs" in row:
            row["outputs"] = [names.get(value, value) for value in row["outputs"]]
        if "target" in row:
            row["target"] = names.get(row["target"], row["target"])
        if row.get("kind") == "outcome_dispatch":
            for key in ("on_return", "on_throw"):
                row[key] = names.get(row[key], row[key])
        for arm in row.get("arms", []):
            arm["target"] = names.get(arm["target"], arm["target"])
        if "metadata" in row:
            _rename_metadata(row["metadata"], names)
    if mentions:
        for row in [block, *block["operations"], block["exit"]]:
            if "constraints" in row:
                row["constraints"] = [mentions.sub(lambda m: names[m[0]], note) for note in row["constraints"]]


def _specialize(facts, blocks, entry, caller, public, choices, region, marker, table):
    # The inlined body retains its current IDs so all caller-side uses, including
    # later uses in its handler, still refer to that invocation. Only the public
    # copy and the values consumed by its own terminal blocks are renamed.
    values = set().union(*(_definitions(blocks[ref]) for ref in region))
    occupied = set(blocks) | set().union(*(_definitions(b) for b in blocks.values()))
    suffix = "." + public["ref"]
    names = {ref: ref + suffix for ref in (region | values) - {marker}}
    if occupied.intersection(names.values()):
        return False
    mentions = re.compile(r"(?<!\w)(?:" + "|".join(map(re.escape, sorted(names, key=len, reverse=True))) + r")(?!\w)")
    public_ends = {pair[0] for pair in choices.values()}
    local_continuations = set()
    pending = [pair[1] for pair in choices.values()]
    while pending:
        ref = pending.pop()
        if ref in local_continuations or ref in region or ref not in blocks:
            continue
        local_continuations.add(ref)
        pending.extend(_edges(blocks[ref]))
    if public_ends & local_continuations or any(
            values & _uses(block) for ref, block in blocks.items() if ref not in region | public_ends | local_continuations):
        return False
    copies = []
    for pred in (public["ref"], caller["ref"]):
        for block in list(facts["blocks"]):
            ref = block["ref"]
            if ref not in region:
                continue
            current = deepcopy(block) if pred == public["ref"] else block
            if ref == entry["ref"]:
                op = current["operations"][0]
                actual = {k: v for k, v in table[pred].items() if k != marker}
                from_other = {v for row in table.values() for v in row.values() if isinstance(v, str)}
                op["inputs"] = [v for v in op["inputs"] if v.get("result") not in from_other - set(actual.values())]
                op["outputs"].remove(marker)
                op["metadata"]["predecessor_bindings"] = {pred: actual}
                producers = op["metadata"].get("output_producers", {})
                if isinstance(producers, dict):
                    producers.pop(marker, None)
                if "constraints" in op:
                    op["constraints"] = [c for c in op["constraints"] if marker not in c]
            if ref in choices:
                old = current["exit"]
                current["exit"] = {"kind": "jump", "source": old["source"],
                                   "target": choices[ref][0 if pred == public["ref"] else 1]}
            if pred == public["ref"]:
                _rename_block(current, names, mentions)
                copies.append(current)
    for public_exit in public_ends:
        _rename_block(blocks[public_exit], names, mentions)
    public["exit"]["target"] = names[entry["ref"]]
    facts["blocks"].extend(copies)
    return True


def specialize_call_continuations(facts, files):
    """Discharge caller-only routing when both continuations are physically identifiable."""
    blocks = {b["ref"]: b for b in facts["blocks"]}
    incoming = defaultdict(set)
    for ref, block in blocks.items():
        for target in _edges(block):
            incoming[target].add(ref)
    unresolved = []
    for caller, invoke, call, entry, formal, site, _ in list(inline_calls(facts, files)):
        preds = incoming[entry["ref"]]
        if len(preds) != 2 or caller["ref"] not in preds or caller["exit"].get("target") != entry["ref"]:
            continue
        public = blocks[next(ref for ref in preds if ref != caller["ref"])]
        if (public["exit"].get("target") != entry["ref"] or public["source_kind"] != "context"
                or len(public["operations"]) != 1 or source_span(public["operations"][0]) != site.source):
            continue
        table = formal.get("metadata", {}).get("predecessor_bindings")
        if not isinstance(table, dict) or set(table) != preds or not all(isinstance(row, dict) for row in table.values()):
            continue
        parameters = formal["outputs"][:len(site.parameters)]
        predicates = {v["result"] for b in blocks.values() for v in b["exit"].get("conditions", []) if "result" in v}
        for marker in formal["outputs"][len(parameters):]:
            if marker not in predicates:
                continue
            found = _region(entry["ref"], marker, site, blocks, files)
            if not found or not found[1]:
                continue
            region, routes = found
            if not any(any(t in blocks and _body_owner(source_span(blocks[t]["exit"]), files) != site
                           for t in _edges(blocks[r])) for r in routes):
                continue
            caller_source = _caller_source(site, source_span(invoke), call, files)
            choices = _targets(region, routes, site, blocks, incoming, caller_source, files) if caller_source else None
            actual = invoke["outputs"] or [v.get("result") for v in invoke["inputs"]]
            public_actual = public["operations"][0]["outputs"]
            static_tag = all(marker not in row for row in table.values()) or all(
                isinstance(row.get(marker), dict) and set(row[marker]) == {"literal"} for row in table.values())
            valid_entries = (all(set(row) <= {*parameters, marker} for row in table.values())
                             and static_tag
                             and all(isinstance(v, str) and {"result": v} in formal["inputs"]
                                     for row in table.values() for k, v in row.items() if k != marker)
                             and all([table[pred].get(k) for k in parameters] == supplied for pred, supplied in
                                     ((caller["ref"], actual), (public["ref"], public_actual))))
            clean = (all(not (incoming[r] - region - (preds if r == entry["ref"] else set())) for r in region)
                     and all(marker not in _uses(b) or b["ref"] in routes and not any(
                         {"result": marker} in op["inputs"] for op in b["operations"]) for b in blocks.values()))
            if choices and valid_entries and clean and _specialize(
                    facts, blocks, entry, caller, public, choices, region, marker, table):
                break
            unresolved.append((caller["ref"], entry["ref"]))
            break
    return unresolved
