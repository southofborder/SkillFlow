"""Source-backed call arguments, returned values and local response projections."""

from copy import deepcopy
from dataclasses import dataclass
import ast
import re

from .entry_occurrences import _body_owner, _EXTENSIONS, _JS_NONCODE, _masked_js, _signatures, _source_span

CALL_RULES = (
    "For one physical call bind its actual receiver, ordered arguments and paired response. "
    "Reading a member of that response (including array destructuring) is a local value projection. "
    "If a wrapper enters the callee body, bind its arguments at the call site and use the body return "
    "at the actual consumer. A local call summary instead owns its response. Do not execute both "
    "representations on the same path. Distinct physical calls, branches and iterations keep their identities."
)
PROJECTION = "call_result_projection"
ARGUMENTS = "inlined_call_arguments"
_ID = r"[A-Za-z_$][\w$]*"
_JS_ASSIGN = re.compile(
    rf"(?:const|let|var)\s+(?P<pattern>\[[\s\w$,]*\]|\{{\s*{_ID}(?:\s*:\s*{_ID})?\s*\}})"
    rf"\s*=\s*(?:await\s+)?(?:(?P<receiver>{_ID})\s*\.\s*)?(?P<callee>{_ID})\s*\((?P<args>[^()]*)\)\s*;?"
)
_JS_INVOKE = re.compile(
    rf"(?:(?:return\s+)|(?:(?:const|let|var)\s+(?P<variable>{_ID})\s*=\s*))"
    rf"(?:await\s+)?(?P<callee>{_ID})\s*\((?P<args>[^()]*)\)\s*;?"
)
_JS_RESULT = re.compile(rf"return\s+(?P<variable>{_ID})(?:\s+as\s+{_ID})?\s*;?")


@dataclass(frozen=True)
class Call:
    callee: str
    receiver: str | None
    args: tuple[str, ...]
    path: tuple = ()
    assigned: str | None = None
    tail: bool = False


def source_span(row):
    return row.get("source") or row.get("metadata", {}).get("source_span")


def _text(span, files):
    if not _source_span(span, files):
        return ""
    return "\n".join(files[span["file"]].splitlines()[span["start_line"] - 1 : span["end_line"]]).strip()


def _arguments(raw):
    level, begin, args = [], 0, []
    for i, c in enumerate(raw):
        if c in "[{":
            level.append("]" if c == "[" else "}")
        elif c in "]}":
            if not level or level.pop() != c:
                return None
        elif c == "," and not level:
            args.append(raw[begin:i].strip())
            begin = i + 1
    if level:
        return None
    return tuple(args + ([raw[begin:].strip()] if raw[begin:].strip() else []))


def source_call(span, files):
    """Recognize one complete statement; additional calls and computed callees need source review."""
    raw = _text(span, files)
    if not raw:
        return None
    if span["file"].endswith(_EXTENSIONS):
        text = _JS_NONCODE.sub(_masked_js, raw).strip()
        m = _JS_ASSIGN.fullmatch(text)
        if m:
            target = m["pattern"]
            if target.startswith("["):
                names = [(i, val.strip()) for i, val in enumerate(target[1:-1].split(",")) if val.strip()]
                if len(names) != 1 or not re.fullmatch(_ID, names[0][1]):
                    return None
                member, name = names[0]
            else:
                parts = target[1:-1].split(":")
                member, name = parts[0].strip(), parts[-1].strip()
            args = _arguments(m["args"])
            return None if args is None else Call(m["callee"], m["receiver"], args, (member,), name)
        m = _JS_INVOKE.fullmatch(text)
        if m:
            args = _arguments(m["args"])
            if args is not None:
                return Call(m["callee"], None, args, assigned=m["variable"], tail=text.startswith("return"))
    elif span["file"].endswith(".py"):
        import textwrap

        try:
            tree = ast.parse(textwrap.dedent(raw))
        except SyntaxError:
            return None
        if len(tree.body) != 1:
            return None
        statement = tree.body[0]
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            target = statement.targets[0]
        elif isinstance(statement, ast.Return):
            target = None
        else:
            return None
        call = statement.value
        if isinstance(call, ast.Await):
            call = call.value
        if (
            not isinstance(call, ast.Call)
            or call.keywords
            or any(isinstance(a, (ast.Call, ast.Starred)) for arg in call.args for a in ast.walk(arg))
        ):
            return None
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
            receiver, name = call.func.value.id, call.func.attr
        elif isinstance(call.func, ast.Name):
            receiver, name = None, call.func.id
        else:
            return None
        args = tuple(ast.unparse(a) for a in call.args)
        if (
            isinstance(target, (ast.Tuple, ast.List))
            and len(target.elts) == 1
            and isinstance(target.elts[0], ast.Name)
        ):
            return Call(name, receiver, args, (0,), target.elts[0].id)
        if target is None or isinstance(target, ast.Name):
            return Call(name, receiver, args, assigned=target.id if target else None, tail=target is None)
    return None


def _role(action):
    return action.get("role") or action["kind"]


def _set_role(action, kind, role="value"):
    action.update(kind=kind, role=role)


def _actions(op):
    return op.get("source_actions") or op.get("metadata", {}).get("source_actions") or []


def _edges(block):
    exit = block["exit"]
    return [exit["target"]] if exit["kind"] == "jump" else [arm["target"] for arm in exit.get("arms", [])]


def _result(value):
    return value.get("result")


def _signature(span, files, name):
    if not _source_span(span, files):
        return None
    sites = [
        s
        for s in _signatures(span["file"], files[span["file"]])
        if s.name == name and span["start_line"] <= s.first <= span["end_line"]
    ]
    return sites[0] if len(sites) == 1 else None


def _entry(blocks, start, file, call, files):
    """Follow only unconditional bridges to a physically identified executable callee entry."""
    seen = set()
    while start in blocks and start not in seen:
        seen.add(start)
        b = blocks[start]
        if b["operations"]:
            op = b["operations"][0]
            span = source_span(op)
            if span and span["file"] == file and (site := _signature(span, files, call.callee)):
                return b, op, site, seen
            return None
        if b["exit"]["kind"] != "jump":
            return None
        start = b["exit"]["target"]


def _resolved_lexically(span, target, files):
    """A matching declaration is not the target of a shadowed or reassigned callable."""
    text = files[target.file]
    declarations = _signatures(target.file, text)
    if sum(s.name == target.name for s in declarations) != 1:
        return False
    enclosing = [s for s in declarations if s.body_end and s.first <= span["start_line"] <= s.body_end]
    if any(p == target.name for s in enclosing for p, _ in s.parameters):
        return False
    # A declaration nested in a sibling scope is not visible at this call.
    if any(
        s != target and s.body_end and s.first <= target.first <= s.body_end and s not in enclosing
        for s in declarations
    ):
        return False
    # Bindings inside unrelated functions cannot shadow this invocation.
    excluded = {
        line
        for s in declarations
        if s.body_end and s not in enclosing
        for line in range(s.first, s.body_end + 1)
    }
    if target.file.endswith(".py"):
        try:
            nodes = (n for n in ast.walk(ast.parse(text)) if getattr(n, "lineno", 0) not in excluded)
            return not any(
                (isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store) and n.id == target.name)
                or (isinstance(n, ast.alias) and (n.asname or n.name.split(".")[0]) == target.name)
                or (isinstance(n, ast.ExceptHandler) and n.name == target.name)
                for n in nodes
            )
        except SyntaxError:
            return False
    masked = _JS_NONCODE.sub(_masked_js, text)
    visible = "\n".join(line for i, line in enumerate(masked.splitlines(), 1) if i not in excluded)
    name = re.escape(target.name)
    assignment = rf"(?<![.$\w]){name}(?![\w$])\s*(?:[+*/%-]|\?\?|&&|\|\|)?=(?!=|>)"
    declarator = (
        rf"(?:\b(?:let|const|var|class)\s+(?:{name}\b|[{{\[][^;=]*\b{name}\b)|\bcatch\s*\(\s*{name}\b)"
    )
    arrow = rf"(?:\([^()]*\b{name}\b[^()]*\)|\b{name}\b)\s*=>"
    return not any(re.search(pattern, visible) for pattern in (assignment, declarator, arrow))


def inline_calls(facts, files):
    blocks = {b["ref"]: b for b in facts["blocks"]}
    for b in blocks.values():
        if b["exit"]["kind"] != "jump" or not b["operations"]:
            continue
        op = b["operations"][-1]
        span = source_span(op)
        call = source_call(span, files)
        if not call or call.path or call.receiver or not (_role_for_op(op) in {"call", "value"}):
            continue
        matched = _entry(blocks, b["exit"]["target"], span["file"], call, files)
        if matched:
            entry, formal, site, bridges = matched
            if _resolved_lexically(span, site, files):
                yield b, op, call, entry, formal, site, bridges


def _role_for_op(op):
    return op.get("role") or op["opcode"]


def bind_source_calls(raw, files):
    for b in raw["blocks"]:
        for op in b["operations"]:
            if not op.get("source"):
                continue  # Reconstruct an archived selected CFG byte-for-byte.
            span = op["source"]
            call = source_call(span, files)
            if not call or not call.path:
                continue
            actions = op.get("source_actions", [])
            roles = [_role(a) for a in actions]
            if not all(a["source"] == span for a in actions):
                continue
            if not actions and _role_for_op(op) in {"receive", "call"}:
                actions = [{"ref": op["ref"], "kind": "call", "source": deepcopy(span)}]
                op["source_actions"] = actions
                roles = ["call"]
            if len(actions) == 1 and roles[0] in {"call", "receive"}:
                _set_role(actions[0], "call", "call")
                actions.append(
                    {
                        "ref": actions[0]["ref"] + ".projection",
                        "kind": PROJECTION,
                        "role": "value",
                        "source": deepcopy(span),
                    }
                )
            elif roles and len(actions) == 2 and roles[0] == "call" and roles[1] in {"receive", "value"}:
                _set_role(actions[1], PROJECTION)
            else:
                continue
            if op["opcode"] == "receive" or op.get("role") == "receive":
                op.update(opcode="call", role="call")
    for _, op, _, _, _, _, _ in inline_calls(raw, files):
        if not op.get("source") or len(_actions(op)) > 1:
            continue
        actions = op.setdefault("source_actions", [])
        if not actions:
            actions.append({"ref": op["ref"], "kind": "call", "source": deepcopy(op["source"])})
        _set_role(actions[0], ARGUMENTS)
        op.update(opcode="value", role="value")


def _name_indices(ir, name):
    if not name or not re.fullmatch(_ID, name):
        return []
    return [
        i
        for i, row in enumerate(ir.get("inputs", []))
        if row.get("type") != "literal"
        and re.split(r"[.:/]", row.get("semantic_name") or row.get("identifier", ""))[-1] == name
    ]


def _same_or_outer(owner, anchor):
    return all(anchor.get(path) == choice for path, choice in owner.items())


def _check_object_arguments(ir, record, call, ops, parameters):
    """Check explicit shorthand and renamed properties against their proved caller versions."""
    if len(call.args) != 1 or not call.args[0].startswith("{") or not call.args[0].endswith("}"):
        return
    fields = _arguments(call.args[0][1:-1]) or ()
    actual = {}
    for field in fields:
        key = re.match(rf"({_ID})(?:\s*:|$)", field)
        if not key:
            actual.clear()  # A subsequent spread or computed key can replace earlier fields.
            continue
        actual.pop(key[1], None)
        part = re.fullmatch(rf"({_ID})(?:\s*:\s*({_ID}))?", field)
        if not part:
            continue
        arg = part[2] or part[1]
        indices = [
            i for i, operand in enumerate(ir["inputs"]) if parameters.get(operand.get("identifier")) == arg
        ]
        if len(indices) == 1:
            actual[part[1]] = {"kind": "input", "index": indices[0]}
    if not actual:
        return
    # A direct formal or literal cannot acquire the field of a newly
    # constructed object by being forwarded as its entire value. Recurse
    # through the local structural operations only; opaque values and shared
    # names from different cases do not establish a contradiction.
    producers = {}
    for _, op in ops:
        name = op.get("output")
        if name:
            producers[name] = None if name in producers else op

    def disproves(ref, path, index, seen):
        kind = ref["kind"]
        if kind == "literal":
            return True  # A constant has no version of the caller's variable.
        if kind == "input":
            i = ref["index"]
            if not 0 <= i < len(ir["inputs"]):
                return False
            if not path:
                operand = ir["inputs"][i]
                return (
                    operand["type"] == "literal"
                    or i != index
                    and operand.get("identifier") in parameters
                    and operand.get("identifier") != ir["inputs"][index].get("identifier")
                )
            if i == index or ir["inputs"][i]["type"] == "literal":
                return True
            # A previously constructed options object might already carry the
            # exact field from the expected parameter.
            return False
        if kind != "local" or ref["name"] in seen:
            return False
        op = producers.get(ref["name"])
        if not op:
            return False
        seen = seen | {ref["name"]}
        if op["op"] == "select_part":
            return disproves(op["input"], (*op["path"], *path), index, seen)
        if op["op"] == "exclude_parts":
            if any(tuple(k) == path[: len(k)] for k in op["paths"]):
                return True
            return disproves(op["input"], path, index, seen)
        if op["op"] not in {"build", "update_fields"}:
            return False
        if not path:
            return op["op"] == "build"  # A new container is not a forwarded formal.
        parts = op.get("parts", op.get("updates", []))
        for field in reversed(parts):
            key = tuple(field["path"])
            if key == path[: len(key)]:
                return disproves(field["value"], path[len(key) :], index, seen)
            if path == key[: len(path)]:
                return False  # Deeper overlapping edits need a finer value proof.
        return op["op"] == "build" or disproves(op["input"], path, index, seen)

    if len(ir["outputs"]) == 1:
        for row in record.get("output_bindings", []):
            for field, expected in actual.items():
                if disproves(row["value"], (field,), expected["index"], frozenset()):
                    yield f"The returned object argument's {field!r} field must use its source parameter at input[{expected['index']}]."


def binding_issues(ir, record, actions, bindings, processing, files, coordinates, at, pairs, parameters):
    """Bind a projected result to the same compatible invocation, arguments and receiver."""
    for action in actions:
        kind, ref = action["kind"], action["ref"]
        if kind not in {ARGUMENTS, PROJECTION}:
            continue
        call = source_call(action["source"], files)
        if not call:
            continue
        path_map = {tuple(p): c for p, c in coordinates}
        owned = [tuple(p) for p in bindings[ref]]
        ops = [(p, at(record, p)) for p in owned if len(p) >= 2 and p[-2] == "ops"]
        if kind == ARGUMENTS:
            yield from _check_object_arguments(ir, record, call, ops, parameters)
            if not call.path and any(op["op"] in {"call", "receive", "deliver"} for _, op in ops):
                yield (
                    "A caller already entering the source-matched callee body must bind its actual "
                    "arguments here. Repeating that invocation also executes it in the shared body."
                )
            continue
        if not call.path:
            continue
        call_actions = [a for a in actions if _role(a) == "call" and a["source"] == action["source"]]
        if len(call_actions) != 1:
            continue
        anchors = {tuple(p) for p in bindings[call_actions[0]["ref"]]}
        acquisitions = []
        for pos in anchors:
            if len(pos) < 2 or pos[-2] != "ops":
                continue
            op = at(record, pos)
            if op["op"] == "call" or (op["op"] == "receive" and pairs and pairs.get(pos) in anchors):
                acquisitions.append((pos, op))
        for i, (left, _) in enumerate(acquisitions):
            for right, _ in acquisitions[i + 1 :]:
                if all(
                    k not in path_map[right] or path_map[right][k] == v for k, v in path_map[left].items()
                ):
                    yield "The same physical invocation executes twice on a compatible processing path."
                    break
        selects = [(p, op) for p, op in ops if op["op"] == "select_part"]
        if not selects or any(
            op["path"] != list(call.path)
            or not any(
                _same_or_outer(path_map[c], path_map[p])
                and c < p
                and op["input"] == {"kind": "local", "name": returned["output"]}
                for c, returned in acquisitions
            )
            for p, op in selects
        ):
            yield f"The local projection must select {list(call.path)} from the paired result of this source call."
        for pos, op in acquisitions:
            receiver = _name_indices(ir, call.receiver)
            refs = processing.get("locations", {}).get(op["location"], {}).get("operand_refs", [])
            if (
                len(receiver) == 1
                and {"instruction_id": ir["id"], "side": "input", "index": receiver[0]} not in refs
            ):
                yield f"Bind the source receiver {call.receiver!r} at input[{receiver[0]}] to the actual call location."
            if len(call.args) != len(op.get("inputs", [])):
                yield "Use the arguments supplied at the identified invocation, in source order."
            else:
                for arg, val in zip(call.args, op["inputs"]):
                    indices = _name_indices(ir, arg)
                    if len(indices) == 1 and val != {"kind": "input", "index": indices[0]}:
                        yield f"Bind argument {arg!r} to its own input[{indices[0]}]."
        if len(ir["outputs"]) == 1:
            for row in record.get("output_bindings", []):
                if row["value"] not in [{"kind": "local", "name": op["output"]} for _, op in selects]:
                    yield "Bind the destructured CFG output to this projection's selected value."


def projection_bindings(record, actions, coordinates, at):
    owners = {a["ref"]: [] for a in actions}
    invoke, select = [a["ref"] for a in actions]
    for path, _ in coordinates:
        if path[0] == "output_bindings":
            owners[select].append(list(path))
        elif len(path) >= 2 and path[-2] == "ops":
            kind = at(record, path)["op"]
            if kind in {"call", "deliver", "receive"}:
                owners[invoke].append(list(path))
            elif kind == "select_part":
                owners[select].append(list(path))
            else:
                return None
        else:
            return None
    return owners if all(owners.values()) else None
