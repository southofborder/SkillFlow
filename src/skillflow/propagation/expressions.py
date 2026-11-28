"""Typed compute expressions over the actual inputs of one operation candidate."""
from __future__ import annotations

from dataclasses import dataclass
from operator import ge, gt, le, lt

from pydantic import TypeAdapter

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import structural_error
from skillflow.propagation.contracts.demand import DemandExpression, _ref_leaves, expression_refs
from skillflow.propagation.contracts.paths import compiled_event_position, split_semantics_path
from skillflow.propagation.contracts.values import LiteralRef
from skillflow.propagation.data import KnownPartsContent, LiteralContent, OpaqueContent, SelectionContent


_EXPRESSION = TypeAdapter(DemandExpression)


def bind_operation_expressions(expressions, event_mapping):
    """Attach compiled coordinates to the existing raw expression targets."""
    pending = {(target["instruction_id"], tuple(target["operation_path"])): item
               for item in expressions if "operation_path" in (target := item["target"])}
    if not pending:
        return
    for row in event_mapping:
        if row["kind"] in {"retained", "slice"}:
            ir, raw = split_semantics_path(row["raw_path"])
            start, end = row["raw_atomic_range"]
            for index in range(start, end):
                item = pending.pop((ir, (*raw, "atomic_ops", index)), None)
                if item is not None:
                    event, body = compiled_event_position(row["compiled_path"])
                    item["operation_position"] = {"event_index": event, "op_index": index - start}
                    if body is not None:
                        item["operation_position"]["body_event_index"] = body
    if pending:
        raise ValueError("Operation expression has no compiled operation position")


def operation_expressions(annotation):
    """Check and index the exact compiled operations available to the interpreter."""
    found = {}
    targets = set()
    for index, item in enumerate(annotation.get("expressions", [])):
        position = item.get("operation_position")
        if position is None:
            # Legacy supplements and CFG control expressions have no compiled
            # operation position. Their existing use remains unchanged.
            continue
        path = f"/expressions/{index}"
        ir = item["target"]["instruction_id"]
        target = canonical_sha256(item["target"])
        event_index, op_index = position["event_index"], position["op_index"]
        body_index = position.get("body_event_index")
        key = ir, event_index, body_index, op_index
        try:
            event = annotation["ir_semantics"][ir]["events"][event_index]
            if body_index is not None:
                event = event["body"][body_index]
            operation = event["atomic_ops"][op_index]
        except (KeyError, IndexError) as error:
            raise structural_error("expression_position", path + "/operation_position",
                                   "Expression position does not identify a compiled atomic operation") from error
        kind = operation["op"]
        if kind not in {"compute", "filter_items"} or key in found or target in targets:
            raise structural_error("expression_position", path + "/operation_position",
                                   "Expression requires a unique compiled compute or filter operation")
        operands = operation["inputs"] if kind == "compute" else [operation["input"]]
        declared = {leaf for operand in operands for leaf in _leaves(operand)}
        expression = item["expression"]
        for reference in expression_refs(_EXPRESSION.validate_python(expression)):
            for leaf in _ref_leaves(reference):
                if not isinstance(leaf, LiteralRef) and canonical_sha256(leaf.model_dump(mode="json")) not in declared:
                    raise structural_error("expression_input", path + "/expression",
                                           "Expression references an input not consumed by the compiled operation")
        found[key] = expression
        targets.add(target)
    return found


def _leaves(reference):
    if reference["kind"] == "alternatives":
        return {leaf for item in reference["items"] for leaf in _leaves(item)}
    return {canonical_sha256(reference)}


def expression_slots(reference, operands, *, include_alternatives=False):
    """Bind a lexical reference by declared coordinates, independent of its Data IDs."""
    identity = canonical_sha256(reference)
    if not include_alternatives:
        return tuple(slot for slot, actual in operands.items() if canonical_sha256(actual) == identity)
    leaves = _leaves(reference)
    return tuple(slot for slot, actual in operands.items() if leaves & _leaves(actual))


def expression_path_steps(expression):
    """Count declared selector steps for the backward finite-path budget."""
    op = expression["op"]
    if op in {"ref", "literal"}:
        return 0
    if op in {"field", "present", "count", "not"}:
        return len(expression.get("path", [])) + expression_path_steps(expression["arg"])
    children = expression["args"] if op in {"and", "or"} else [expression["left"], expression["right"]]
    return sum(expression_path_steps(child) for child in children)


_UNKNOWN, _MISSING, _INVALID, _PRESENT = object(), object(), object(), object()
_ORDERED = {"lt": lt, "le": le, "gt": gt, "ge": ge}


@dataclass(frozen=True)
class _Projection:
    identity: str
    path: tuple = ()


@dataclass(frozen=True)
class _Shape:
    container: type
    size: int | None = None


def _select_literal(value, path):
    for step in path:
        if type(value) is not (dict if type(step) is str else list):
            return _INVALID
        try:
            value = value[step]
        except (KeyError, IndexError):
            return _MISSING
    return value


def _part_shape(paths):
    heads = {path[0] for path in paths}
    if heads and all(type(item) is str for item in heads):
        return _Shape(dict)
    if heads and all(type(item) is int for item in heads):
        return _Shape(list, len(heads) if max(heads) + 1 == len(heads) else None)
    return _UNKNOWN


def _inspect(registry, identity, path, seen=frozenset()):
    # Loop equations can gain variants during convergence. Folding a partial
    # family would turn a tentative value into a permanent concrete fact.
    if identity in seen:
        return _UNKNOWN
    content = registry.get(identity).content
    seen = seen | {identity}
    if isinstance(content, LiteralContent):
        return _select_literal(content.value, path)
    if isinstance(content, SelectionContent) and all(type(step) in (str, int) for step in content.path):
        return _inspect(registry, content.base, (*content.path, *path), seen)
    if isinstance(content, KnownPartsContent) and content.parts_complete:
        if not path:
            return _part_shape([part.path for part in content.parts])
        for part in content.parts:
            prefix = tuple(part.path)
            if path[:len(prefix)] == prefix:
                suffix = path[len(prefix):]
                observed = _inspect(registry, part.data, suffix, seen)
                return _PRESENT if not suffix and observed is _UNKNOWN else observed
        descendants = [part.path[len(path):] for part in content.parts if tuple(part.path[:len(path)]) == path]
        if descendants:
            return _part_shape(descendants)
        shape = _part_shape([part.path for part in content.parts])
        if isinstance(shape, _Shape):
            if shape.container is not (dict if type(path[0]) is str else list):
                return _INVALID
            if shape.container is dict or shape.size is not None:
                return _MISSING
    return _UNKNOWN


def _typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is list:
        return len(left) == len(right) and all(_typed_equal(a, b) for a, b in zip(left, right))
    if type(left) is dict:
        return left.keys() == right.keys() and all(_typed_equal(left[key], right[key]) for key in left)
    return left == right


def _concrete(value):
    return all(value is not state for state in (_UNKNOWN, _MISSING, _INVALID, _PRESENT)) and not isinstance(value, _Shape)


def evaluate_compute(expression, registry, operands, selected):
    """Evaluate one paired input tuple, preserving symbolic exact projection."""
    operands = dict(enumerate(operands))

    def value(arg):
        result = evaluate(arg)
        return _inspect(registry, result.identity, result.path) if isinstance(result, _Projection) else result

    def evaluate(expr):
        op = expr["op"]
        if op == "literal":
            return expr["value"]
        if op == "ref":
            ref = expr["value"]
            if ref["kind"] == "literal":
                return ref["value"]
            ids = {selected[slot] for slot in expression_slots(ref, operands)}
            return _Projection(next(iter(ids))) if len(ids) == 1 else _UNKNOWN
        if op == "field":
            arg = evaluate(expr["arg"])
            path = tuple(expr["path"])
            if isinstance(arg, _Projection):
                return _Projection(arg.identity, arg.path + path)
            return _select_literal(arg, path) if _concrete(arg) else arg
        if op == "present":
            arg = value(expr["arg"])
            return False if arg is _MISSING else _UNKNOWN if arg is _UNKNOWN or arg is _INVALID else True
        if op == "count":
            arg = value(expr["arg"])
            if isinstance(arg, _Shape):
                return arg.size if arg.container is list and arg.size is not None else _UNKNOWN
            return len(arg) if type(arg) is list else _UNKNOWN
        if op == "not":
            arg = value(expr["arg"])
            return not arg if type(arg) is bool else _UNKNOWN
        if op in {"and", "or"}:
            args = [value(child) for child in expr["args"]]
            if not all(type(arg) is bool for arg in args):
                return _UNKNOWN
            return all(args) if op == "and" else any(args)
        left, right = value(expr["left"]), value(expr["right"])
        if not (_concrete(left) and _concrete(right)):
            return _UNKNOWN
        if op in {"eq", "ne"}:
            equal = _typed_equal(left, right)
            return equal if op == "eq" else not equal
        if type(left) is type(right) and type(left) in {int, float, str}:
            return _ORDERED[op](left, right)
        return _UNKNOWN

    result = evaluate(expression)
    if isinstance(result, _Projection):
        observed = _inspect(registry, result.identity, result.path)
        if observed is not _MISSING and observed is not _INVALID:
            return SelectionContent(base=result.identity, path=list(result.path))
    elif _concrete(result):
        return LiteralContent(value=result)
    return OpaqueContent()
