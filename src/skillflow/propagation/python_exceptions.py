"""Finite Python built-in class matching without importing the analyzed program."""
import builtins
import ast
import textwrap


def builtin_exception(name):
    value = vars(builtins).get(name)
    return value if isinstance(value, type) and issubclass(value, BaseException) else None


def exception_match(actual, classes):
    received = builtin_exception(actual)
    caught = [builtin_exception(name) for name in classes]
    if BaseException in caught:
        return {True}
    if received is None or any(cls is None for cls in caught):
        return {False, True}
    return {issubclass(received, tuple(caught))}


def validate_handler_record(cfg, block_id, ir_id, spec, specs):
    block = cfg["blocks"][block_id]
    if len(block["instructions"]) != 2:
        return "Handler admission requires a predecessor merge followed by dispatch"
    merge, end = block["instructions"]
    ops = [op for event in spec.events for op in getattr(event, "atomic_ops", [])]
    if len(ops) != 1:
        return "Handler admission requires exactly its selected merge or branch"
    op = ops[0]
    if ir_id == merge["id"]:
        preds = {e["source_block_id"] for e in cfg["edges"] if e["target_block_id"] == block_id}
        if op.op != "merge" or {p.predecessor for p in op.incoming} != preds:
            return "The exception merge must cover every protected predecessor"
        for incoming in op.incoming:
            pred = cfg["blocks"][incoming.predecessor]
            producer, dispatch = pred["instructions"][-2:]
            route = dispatch.get("metadata", {}).get("outcome_dispatch", {})
            if route.get("on_throw") != block_id or incoming.value.kind != "input" or incoming.value.index >= len(merge["inputs"]):
                return "Each exception input must come from the throwing predecessor"
            if producer["id"] not in specs:
                continue
            indexes = {group.exception_index for group in specs[producer["id"]].outcome_bindings
                       if group.exception_index is not None and group.exception_index < len(producer["outputs"])}
            if merge["inputs"][incoming.value.index].get("identifier") not in {producer["outputs"][i]["identifier"] for i in indexes}:
                return "The merged version must be the protected operation's declared exception output"
    else:
        edges = {e["condition_text"]: e["target_block_id"] for e in cfg["edges"] if e["source_block_id"] == block_id}
        try:
            clause = textwrap.dedent(end["metadata"]["script_content"]).strip()
            expr = ast.parse("try:\n    pass\n" + clause + "\n    pass").body[0].handlers[0].type
            names = list(dict.fromkeys(t.id for t in (expr.elts if isinstance(expr, ast.Tuple) else [expr])))
        except (SyntaxError, KeyError, IndexError, AttributeError):
            return "Handler selector must cite the actual Python except clause"
        if (op.op != "branch" or op.predicate != "selector" or op.input.kind != "input" or op.input.index != 0
                or op.selector.outcome != 0 or op.selector.tests[0].kind != "python_exception"
                or op.selector.tests[0].classes != names or op.true_target != edges.get("matches Python handler")
                or op.false_target != edges.get("does not match Python handler")
                or len(merge["outputs"]) != 1 or end["inputs"] != merge["outputs"]):
            return "Handler dispatch must test the merged exception against the source class and preserve its two continuations"
    return None
