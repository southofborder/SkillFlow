"""Prove direct positional transfers into a represented Python function body."""
import ast
import re

from .source_calls import _resolved_lexically, _signatures, source_call, source_span


def _plain_function(text, call, span):
    names = [sig for sig in _signatures(span["file"], text) if sig.name == call.callee]
    if len(names) != 1 or names[0].variadic:
        return None
    sig = names[0]
    # Only ordinary module-level functions whose positional parameters are
    # all supplied at this physical call. Decorators and generators can change
    # whether invoking the value enters this body at all.
    tree = ast.parse(text)
    calls = [node for node in ast.walk(tree) if isinstance(node, (ast.Assign, ast.Return))
             and node.lineno == span["start_line"] and node.end_lineno == span["end_line"]
             and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
             and node.value.func.id == call.callee]
    if len(calls) != 1:
        return None
    if any((isinstance(node, ast.alias) and node.name == "*")
           or (isinstance(node, ast.ClassDef) and node.name == call.callee)
           or (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Del) and node.id == call.callee)
           or (isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name == call.callee)
           or (isinstance(node, ast.MatchMapping) and node.rest == call.callee)
           for node in ast.walk(tree)):
        return None
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == call.callee and node.lineno == sig.first]
    if len(functions) != 1:
        return None
    node = functions[0]
    if (node.decorator_list or node.args.kwonlyargs or len(node.args.posonlyargs + node.args.args) != len(call.args)
            or any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node))):
        return None
    return sig, node


def local_call_inputs(cfg, instruction, action, files):
    """Return the ordered actual input indexes only for a proved CFG handoff."""
    meta = instruction.get("metadata", {})
    rows = meta.get("ordered_argument_bindings")
    span = source_span(instruction)
    if (instruction["opcode"] != "call" or not isinstance(rows, list) or not rows
            or not isinstance(span, dict) or action.get("source") != span
            or not isinstance(span.get("file"), str) or not span["file"].endswith(".py")):
        return None
    call = source_call(span, files)
    if (not call or call.receiver or call.path or call.callee != meta.get("callee")
            or not all(name.isidentifier() for name in call.args)):
        return None
    target = _plain_function(files[span["file"]], call, span)
    if target is None or not _resolved_lexically(span, target[0], files):
        return None
    sig, definition = target
    blocks = cfg["blocks"]
    caller = next((b for b in blocks.values() if len(b["instructions"]) >= 2
                   and b["instructions"][-2]["id"] == instruction["id"]), None)
    if caller is None or caller.get("data_source_kind") or caller["instructions"][-1]["opcode"] != "dispatch":
        return None
    exit_op = caller["instructions"][-1]
    edges = [e for e in cfg["edges"] if e["source_block_id"] == caller["block_id"]]
    if len(edges) != 1 or edges[0].get("condition_text") or exit_op["inputs"] or exit_op.get("metadata", {}).get("outcome_dispatch"):
        return None
    entry_id = edges[0]["target_block_id"]
    entry = blocks[entry_id]
    if entry_id == caller["block_id"] or sum(e["target_block_id"] == entry_id for e in cfg["edges"]) != 1:
        return None
    if entry.get("data_source_kind") == "context" or not entry["instructions"]:
        return None
    first = entry["instructions"][0]
    body = source_span(first)
    if (not isinstance(body, dict) or body.get("file") != sig.file
            or body.get("start_line") != definition.body[0].lineno
            or not isinstance(body.get("end_line"), int)
            or not body["start_line"] <= body["end_line"] <= sig.body_end):
        return None
    ins, outs = instruction["inputs"], instruction["outputs"]
    if (len(ins) != len(rows) + 1 or len(outs) != len(rows) or len(call.args) != len(rows)
            or any(port["type"] != "result" for port in [*ins, *outs])):
        return None
    # The leading port must carry this unique function's physical declaration.
    decl = [op for b in blocks.values() for op in b["instructions"]
            if any(port.get("identifier") == ins[0]["identifier"] for port in op["outputs"])]
    if (len(decl) != 1 or decl[0]["opcode"] != "value" or len(decl[0]["outputs"]) != 1
            or source_span(decl[0]) != {"file": sig.file, "start_line": sig.first, "end_line": sig.body_end}):
        return None
    for i, (row, actual, formal) in enumerate(zip(rows, call.args, sig.parameters, strict=True)):
        a, f = ins[i+1].get("semantic_name"), outs[i].get("semantic_name")
        if (not a or not f or row != {"actual": a, "formal": f}
                or re.split(r"[.:/]", a)[-1] != actual or re.split(r"[.:/]", f)[-1] != formal[0]):
            return None
    if not _confined_uses(cfg, entry_id, outs, sig, definition):
        return None
    return tuple(range(1, len(ins)))


def _confined_uses(cfg, entry_id, outs, sig, definition):
    """Follow the represented body; each observed formal use must belong to that activation."""
    def inside(op):
        span = source_span(op) or {}
        return (span.get("file") == sig.file and isinstance(span.get("start_line"), int)
                and isinstance(span.get("end_line"), int)
                and sig.first < span["start_line"] <= span["end_line"] <= sig.body_end)

    successors = {}
    for edge in cfg["edges"]:
        successors.setdefault(edge["source_block_id"], []).append(edge["target_block_id"])
    reachable, pending = set(), [entry_id]
    while pending:
        block = pending.pop()
        if block not in reachable and any(inside(op) for op in cfg["blocks"][block]["instructions"]):
            reachable.add(block)
            pending.extend(successors.get(block, ()))
    formals = {out["identifier"]: name for out, (name, _) in zip(outs, sig.parameters, strict=True)}
    reads = [(node.id, node.lineno) for node in ast.walk(definition)
             if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)]
    witnessed = set()
    for block, row in cfg["blocks"].items():
        for op in row["instructions"]:
            used = {p["identifier"] for p in op["inputs"] if p["type"] == "result"} & formals.keys()
            if not used:
                continue
            if block not in reachable or not inside(op):
                return False
            span = source_span(op)
            local_names = {name for name, line in reads if span["start_line"] <= line <= span["end_line"]}
            if any(formals[version] not in local_names for version in used):
                return False
            witnessed.update(formals[version] for version in used)
    # Unused physical parameters still receive the caller's actual value.
    return (set(formals.values()) & {name for name, _ in reads}) <= witnessed


def binding_errors(record, indexes):
    """The callable is resolved locally; the only effects here are value transfers."""
    refs = {row["output_index"]: row["value"] for row in record.get("output_bindings", [])}
    if (record.get("segments") or record.get("order", "fixed") != "fixed"
            or len(record.get("output_bindings", [])) != len(indexes)
            or refs != {i: {"kind": "input", "index": j} for i, j in enumerate(indexes)}):
        return ["This source call enters its represented function body. Bind each positional actual "
                "directly to the corresponding formal output. The body owns its effects and result."]
    return []
