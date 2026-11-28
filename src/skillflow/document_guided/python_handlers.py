"""Explicit Python handler admission for source-located exceptional continuations."""
import ast
from collections import defaultdict
from functools import lru_cache
import textwrap

from skillflow.propagation.python_exceptions import builtin_exception
from .entry_occurrences import _body_owner
from .source_calls import _edges, source_span


MATCH = "matches Python handler"
BYPASS = "does not match Python handler"


@lru_cache(maxsize=64)
def _parsed(text):
    try:
        tree = ast.parse(text)
    except (ValueError, SyntaxError):
        return None, set()
    # Only resolve an unshadowed name to a Python built-in. Unresolved classes
    # and exception groups need separate source semantics.
    bound = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            bound.add(n.id)
        elif isinstance(n, ast.arg):
            bound.add(n.arg)
        elif isinstance(n, ast.alias):
            bound.add(n.asname or n.name.split(".")[0])
        elif isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            bound.add(n.name)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            bound.add(n.name)
        elif isinstance(n, ast.Name) and n.id in {"exec", "globals", "locals", "__builtins__"}:
            bound.add("*")
    return tree, bound


@lru_cache(maxsize=64)
def _handlers(text):
    tree, bound = _parsed(text)
    if tree is None:
        return {}
    result = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Try, getattr(ast, "TryStar", ast.Try))):
            continue
        for handler in node.handlers:
            if handler.type is None:
                continue
            types = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
            exact = (type(node) is ast.Try and len(node.handlers) == 1 and not node.finalbody and types
                     and "*" not in bound and all(isinstance(t, ast.Name) and t.id not in bound
                                                  and builtin_exception(t.id) for t in types))
            names = list(dict.fromkeys(t.id for t in types)) if exact else []
            result[handler.lineno] = (names, handler, node.body)
    return result


# These built-ins construct their own exact type with zero or literal positional
# arguments. In particular OSError can construct a different concrete subclass
# and specialized constructors can raise TypeError before the raise executes.
_SIMPLE_RAISES = frozenset({"Exception", "BaseException", "ValueError", "TypeError", "RuntimeError",
                            "KeyboardInterrupt", "SystemExit", "GeneratorExit", "IndexError", "KeyError",
                            "LookupError", "ZeroDivisionError", "ArithmeticError", "AssertionError"})


def qualify_raised_classes(candidate, files, inherited):
    for block in candidate["blocks"]:
        for ir in block["instructions"][:-1]:
            if ir["instruction_ref"] in inherited:
                continue
            meta = ir["metadata"]
            span = meta.get("source_span")
            if not span or not span["file"].endswith(".py") or len(meta.get("source_actions", [])) != 1:
                continue
            raw = meta["script_content"]
            if not raw.lstrip().startswith("raise"):
                continue
            try:
                statements = ast.parse(textwrap.dedent(raw)).body
            except SyntaxError:
                continue
            if len(statements) != 1 or not isinstance(statements[0], ast.Raise) or statements[0].cause:
                continue
            exc = statements[0].exc
            if isinstance(exc, ast.Call) and not exc.keywords and all(isinstance(a, ast.Constant) for a in exc.args):
                exc = exc.func
            tree, bound = _parsed(files[span["file"]])
            if (tree is not None and isinstance(exc, ast.Name) and exc.id in _SIMPLE_RAISES
                    and exc.id not in bound and "*" not in bound
                    and any(isinstance(n, ast.Raise) and n.lineno == span["start_line"]
                            and n.end_lineno == span["end_line"] for n in ast.walk(tree))):
                meta["python_raised_class"] = exc.id


def _handler(span, files):
    if not span or not span["file"].endswith(".py") or span["start_line"] != span["end_line"]:
        return None
    return _handlers(files.get(span["file"], "")).get(span["start_line"])


def _incoming(blocks, target):
    return [b for b in blocks.values() if target in _edges(b)]


def _throw_inputs(rows, target, inputs):
    """Require a unique result of the typed failing producer for each predecessor."""
    values = []
    for block in rows:
        end = block["exit"]
        if end["kind"] != "outcome_dispatch" or end["on_throw"] != target:
            return None
        producer = next((op for op in block["operations"] if op["ref"] == end["producer"]), None)
        matches = [v for v in inputs if producer and v.get("result") in producer["outputs"]]
        if len(matches) != 1:
            return None
        values.extend(matches)
    return values if values and len(values) == len(inputs) and len({v["result"] for v in values}) == len(values) else None


def _protected(pred, blocks, span, body, files):
    """Check this activation enters through the protected suite or a local call in it."""
    caller = _body_owner(span, files)
    callee = _body_owner(source_span(pred["exit"]), files)
    todo, seen = [pred], set()
    reached = False
    while todo:
        block = todo.pop()
        if block["ref"] in seen:
            continue
        seen.add(block["ref"])
        site = source_span(block["exit"])
        if not site or site["file"] != span["file"]:
            return False
        owner = _body_owner(site, files)
        if owner == caller:
            suites = [s for s in body if s.lineno <= site["start_line"] <= site["end_line"] <= s.end_lineno]
            if not suites:
                return False
            if callee != caller and not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == callee.name and site["start_line"] <= n.lineno <= n.end_lineno <= site["end_line"]
                    for suite in suites for n in ast.walk(suite)):
                return False
            reached = True
        else:
            parents = _incoming(blocks, block["ref"])
            if callee is None or owner != callee or not parents:
                return False
            todo.extend(parents)
    return reached


def _direct_escape(block, value, span, files):
    end = block["exit"]
    site = source_span(end)
    return (not block["operations"] and end["kind"] == "return" and end["values"] == [{"result": value}]
            and site and site["file"] == span["file"] and _body_owner(site, files) == _body_owner(span, files)
            and end.get("metadata", {}).get("disposition") in {"raise", "throw", "propagate"})


def _handler_body(block, value, span, handler, files):
    """A concrete entry in this handler may bind e together with formatting/delivery, or only perform effects."""
    rows = [*block["operations"], block["exit"]]
    places = [source_span(row) for row in rows]
    if not all(p and p["file"] == span["file"] and handler.lineno <= p["start_line"] <= p["end_line"] <= handler.end_lineno
               and _body_owner(p, files) == _body_owner(span, files) for p in places):
        return False
    if not any(p["end_line"] >= handler.body[0].lineno for p in places):
        return False
    uses_name = handler.name and any(isinstance(n, ast.Name) and n.id == handler.name and isinstance(n.ctx, ast.Load)
                                    for stmt in handler.body for n in ast.walk(stmt))
    return (not uses_name or any({"result": value} in row.get("inputs", row.get("values", [])) for row in rows))


def _explicit_admission(block, blocks, incoming, values, span, classes, handler, files):
    bind, end = block["operations"][0], block["exit"]
    if len(block["operations"]) != 1 or source_span(end) != span:
        return ("exit",), "The handler match must follow just its exception merge at the cited except clause."
    value, = bind["outputs"]
    bindings = bind.get("metadata", {}).get("predecessor_bindings")
    if bindings is not None:
        expected = {b["ref"]: v["result"] for b, v in zip(incoming, values)}
        if bindings != expected and bindings != {pred: {value: v} for pred, v in expected.items()}:
            return ("operations", 0, "metadata"), "Each predecessor must bind this merge to its own thrown output."
    if (bind.get("role", bind["opcode"]) != "value" or bind.get("source_actions")
            and any(a.get("role", a["kind"]) != "value" for a in bind["source_actions"])):
        return ("operations", 0), "Handler admission cannot move other actions into the incoming exception merge."
    conditions = end["conditions"]
    kind = end.get("metadata", {}).get("predicate")
    types = [{"external_resource": "builtins." + name} for name in classes]
    if (kind not in (None, "exception_type_matches") or conditions[:1] != [{"result": value}]
            or conditions[1:] != types and not (kind == "exception_type_matches" and len(conditions) == 1)):
        return ("exit",), "Use the merged thrown object and its source-resolved Python handler type in the exception match."
    arms = end["arms"]
    if (len(arms) != 2 or any(a["target"] not in blocks for a in arms) or arms[0]["target"] == arms[1]["target"]
            or not _handler_body(blocks[arms[0]["target"]], value, span, handler, files)):
        return ("exit",), "The matching successor must enter this source handler and the other successor must propagate."
    outer = blocks[arms[1]["target"]]
    if not _direct_escape(outer, value, span, files):
        return ("exit",), "The nonmatching successor must propagate this same exception to the caller."
    # Class identity is a control specification from the physical clause, not
    # another Data input. Canonicalize the actual predicate and keep both targets.
    bind.update(opcode="python_handler_merge", role="value")
    end["conditions"] = [{"result": value}]
    end.setdefault("metadata", {})["predicate"] = "exception_type_matches"
    arms[0]["condition"], arms[1]["condition"] = MATCH, BYPASS
    return None


def split_handler_admission(facts, files):
    """Split only a physical handler with proved exceptional predecessors and outer continuation."""
    blocks = {block["ref"]: block for block in facts["blocks"]}
    outputs = {name for b in blocks.values() for op in b["operations"] for name in op["outputs"]}
    for target, block in list(blocks.items()):
        if not block["operations"]:
            continue
        bind = block["operations"][0]
        span = source_span(bind)
        found = _handler(span, files)
        if not found or len(bind["outputs"]) != 1 or bind["opcode"] == "python_handler_merge":
            continue
        incoming = _incoming(blocks, target)
        if not any(p["exit"].get("on_throw") == target for p in incoming):
            continue
        values = _throw_inputs(incoming, target, bind["inputs"])
        if not values:
            yield target, ("operations", 0, "inputs"), "Handler entry must receive the actual thrown output from each protected predecessor."
            continue
        classes, handler, body = found
        if not classes:
            yield target, ("exit",), "Handler type resolution, ordered clauses, or cleanup requires an explicit source-backed route."
            continue
        if not all(_protected(p, blocks, span, body, files) for p in incoming):
            yield target, ("exit",), "The protected try suite cannot catch an exception from outside its activation."
            continue
        if block["exit"]["kind"] == "branch" and source_span(block["exit"]) == span:
            issue = _explicit_admission(block, blocks, incoming, values, span, classes, handler, files)
            if issue:
                yield target, *issue
            continue
        # A failure inside this handler already escapes to its enclosing continuation.
        # Follow only this actual handler body, never a same-line copy in another invocation.
        pending, seen, escapes = [target], set(), set()
        while pending:
            ref = pending.pop()
            if ref in seen or ref not in blocks:
                continue
            seen.add(ref)
            end = blocks[ref]["exit"]
            pos = source_span(end)
            if not pos or pos["file"] != span["file"] or not handler.lineno <= pos["start_line"] <= pos["end_line"] <= handler.end_lineno:
                continue
            if end["kind"] == "outcome_dispatch":
                escapes.add(end["on_throw"])
                pending.append(end["on_return"])
            elif end["kind"] == "jump":
                pending.append(end["target"])
        outer = blocks.get(next(iter(escapes))) if len(escapes) == 1 else None
        merge = outer["operations"][0] if outer and len(outer["operations"]) == 1 else None
        if (not merge or len(merge["outputs"]) != 1 or outer["exit"]["kind"] != "return"
                or outer["exit"]["values"] != [{"result": merge["outputs"][0]}]
                or not _throw_inputs(_incoming(blocks, outer["ref"]), outer["ref"], merge["inputs"])):
            yield target, ("exit",), "Add a source-backed match decision and carry its nonmatching value to the enclosing exceptional continuation."
            continue
        gate = target + ".exception_match"
        thrown = bind["outputs"][0] + ".incoming"
        if gate in blocks or thrown in outputs:
            yield target, ("operations", 0, "outputs"), "Handler admission needs distinct block and exception result references."
            continue
        if any(op.get("metadata", {}).get("predecessor_bindings") for op in (bind, merge)):
            yield target, ("operations", 0, "metadata"), "Update the explicit predecessor rows for the matched and unmatched routes."
            continue
        facts["blocks"].append({"ref": gate, "source_kind": "normal", "operations": [{
            "ref": "incoming_exception", "opcode": "python_handler_merge", "role": "value",
            "inputs": bind["inputs"], "outputs": [thrown], "source": span}],
            "exit": {"kind": "branch", "source": span, "conditions": [{"result": thrown}],
                     "arms": [{"target": target, "condition": MATCH}, {"target": outer["ref"], "condition": BYPASS}]}})
        for pred in incoming:
            pred["exit"]["on_throw"] = gate
        bind["inputs"] = [{"result": thrown}]
        merge["inputs"].append({"result": thrown})
        outputs.add(thrown)


def handler_transfers(cfg, files):
    """Derive authoritative wire records from typed incoming edges and the actual except clause."""
    incoming, outgoing = defaultdict(list), defaultdict(list)
    for edge in cfg["edges"]:
        incoming[edge["target_block_id"]].append(edge["source_block_id"])
        outgoing[edge["source_block_id"]].append(edge)
    blocks = cfg["blocks"]
    transfers = {}

    def recv(ir, pred, port):
        indexes = [i for i, value in enumerate(ir["inputs"]) if value.get("identifier") == port and value["type"] == "result"]
        if len(indexes) != 1:
            raise ValueError("A handler predecessor must supply one actual exception input")
        return {"predecessor": pred, "value": {"kind": "input", "index": indexes[0]}}

    def merged(block, extra=None):
        op = block["instructions"][0]
        rows = []
        for pred in incoming[block["block_id"]]:
            if extra and pred == extra[0]:
                rows.append(recv(op, pred, extra[1]))
                continue
            producer, end = blocks[pred]["instructions"][-2:]
            route = end["metadata"].get("outcome_dispatch", {})
            if route.get("on_throw") != block["block_id"] or producer["id"] != route.get("producer"):
                raise ValueError("Exceptional entry requires its protected producer's throw edge")
            outputs = {v["identifier"] for v in producer["outputs"]}
            matched = [v["identifier"] for v in op["inputs"] if v.get("identifier") in outputs]
            if len(matched) != 1:
                raise ValueError("Exceptional entry requires an unambiguous producer result")
            rows.append(recv(op, pred, matched[0]))
        return {"op": "merge", "incoming": rows, "output": "exception"}

    def record(ir, op=None, value=None):
        evidence = [{**ir["metadata"]["source_span"], "reason": "The source clause and incoming control edge select this exception."}]
        result = {"evidences": evidence}
        if op:
            result["segments"] = [{"mode": "local", "ops": [{**op, "evidences": evidence}], "returns": []}]
        if value:
            result["output_bindings"] = [{"output_index": 0, "value": value}]
        transfers[ir["id"]] = result

    for key, block in blocks.items():
        ins = block["instructions"]
        if len(ins) != 2 or ins[0]["opcode"] != "python_handler_merge":
            continue
        merge, end = ins
        found = _handler(end.get("metadata", {}).get("source_span"), files)
        if not found or not found[0]:
            raise ValueError("Python exception admission requires a supported physical except clause")
        targets = {edge["condition_text"]: edge["target_block_id"] for edge in outgoing[key]}
        if (set(targets) != {MATCH, BYPASS} or len(end["inputs"]) != 1 or len(merge["outputs"]) != 1
                or end["inputs"][0] != merge["outputs"][0]):
            raise ValueError("Python handler must dispatch the merged thrown value to matching and bypass successors")
        typed = {"path": [], "tests": [{"kind": "python_exception", "classes": found[0]}], "outcome": 0}
        record(merge, merged(block), {"kind": "local", "name": "exception"})
        record(end, {"op": "branch", "input": {"kind": "input", "index": 0}, "predicate": "selector",
                     "selector": typed, "true_target": targets[MATCH], "false_target": targets[BYPASS]})
        bind = blocks[targets[MATCH]]["instructions"][0]
        outer = blocks[targets[BYPASS]]
        if len(outer["instructions"]) == 1:
            escape = outer["instructions"][0]
            if (escape["opcode"] != "return" or escape["inputs"] != merge["outputs"]
                    or escape["metadata"].get("disposition") not in {"raise", "throw", "propagate"}):
                raise ValueError("A direct nonmatching exit must propagate the same exception")
            record(escape)
            # A real handler body can perform arbitrary source effects, including a
            # combined caught binding and output. Its processing remains source-owned.
            continue
        if bind["inputs"] != merge["outputs"] or len(bind["outputs"]) != 1:
            raise ValueError("Python handler binding must forward the selected exception")
        record(bind, value={"kind": "input", "index": 0})
        record(outer["instructions"][0], merged(outer, (key, merge["outputs"][0]["identifier"])),
               {"kind": "local", "name": "exception"})
    return transfers


def assemble_handler_transfers(value, material, *, fixed=(), check_existing=True):
    from .python_arguments import argument_transfers
    planned = argument_transfers(material["cfg"])
    argument_ids = set(planned)
    handlers = any(b["instructions"] and b["instructions"][0]["opcode"] == "python_handler_merge"
                   for b in material["cfg"]["blocks"].values())
    if not planned and not handlers:
        return
    from skillflow.propagation.contracts.task import task_source_files
    from skillflow.common.validation import structural_error
    files = task_source_files(material["source"])
    try:
        if handlers:
            planned.update(handler_transfers(material["cfg"], files))
    except (KeyError, ValueError, IndexError) as error:
        raise structural_error("python_handler_admission", "/ir_semantics", str(error)) from error
    records = value["ir_semantics"]
    resolved = set()
    for owner, record in planned.items():
        if owner in fixed:
            continue
        if owner in records:
            if not check_existing:
                continue
            # Compare executable relations, preserving authored evidence and sensitivity.
            def executable(spec):
                sections = []
                for segment in spec.get("segments", []):
                    ops = [{k: v for k, v in op.items() if k != "evidences"} for op in segment.get("ops", [])]
                    sections.append((segment.get("kind", "processing"), segment.get("mode"), ops, segment.get("returns", [])))
                return spec.get("output_bindings", []), spec.get("order", "fixed"), sections
            if executable(records[owner]) != executable(record):
                if owner in argument_ids:
                    raise structural_error("python_argument_presence", "/ir_semantics/" + owner,
                                           "Use the actual snapshot's omission test and the supplied/default arm bindings.")
                raise structural_error("python_handler_admission", "/ir_semantics/" + owner,
                                       "Handler transfers must use the actual predecessor, exception class and matched/escape routes.")
            continue
        gaps = [g for g in value.get("processing_gaps", []) if g["instruction_id"] == owner]
        if any(g.get("locations") or g.get("origin") == "validation" for g in gaps):
            continue
        records[owner] = record
        resolved.add(owner)
    if resolved:
        value["processing_gaps"] = [g for g in value.get("processing_gaps", []) if g["instruction_id"] not in resolved]
