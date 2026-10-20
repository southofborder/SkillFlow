"""Small Boolean interpretation over existing references, without program execution."""
from __future__ import annotations

from dataclasses import dataclass

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.contracts.references import target_key
from .sensitivity_engine import range_presence


UNKNOWN = object()
MISSING = object()
INVALID = object()


@dataclass(frozen=True)
class _TypedUnknown:
    kind: type


def _unknown(value):
    return value is UNKNOWN or isinstance(value, _TypedUnknown)


def _kind(value):
    return value.kind if isinstance(value, _TypedUnknown) else None if value is UNKNOWN else type(value)


class ConstraintCapability(Exception):
    """An explicit semantic or resource boundary of this bounded checker."""


class ConstraintLimit(ConstraintCapability):
    """A diagnosed bounded-analysis limit, distinct from implementation faults."""


class ConstraintUnsupported(ConstraintCapability):
    """Well-formed inputs whose evaluated types lack supported semantics."""


def _path_value(value, path):
    for step in path:
        if value is UNKNOWN or value is MISSING or value is INVALID:
            return value
        if not (type(step) is str and _kind(value) is dict or type(step) is int and _kind(value) is list):
            return INVALID
        if isinstance(value, _TypedUnknown):
            return UNKNOWN
        try:
            value = value[step]
        except (KeyError, IndexError):
            return MISSING
    return value


def _equal(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is list:
        return len(left) == len(right) and all(_equal(a, b) for a, b in zip(left, right))
    if type(left) is dict:
        return left.keys() == right.keys() and all(_equal(left[key], right[key]) for key in left)
    return left == right


def literal_at(data, identity, path=(), seen=None):
    seen = set() if seen is None else set(seen)
    marker = (identity, canonical_sha256(path))
    if marker in seen or identity not in data:
        return UNKNOWN
    seen.add(marker)
    item = data[identity]
    content = item["content"]
    form = content["form"]
    if form == "literal":
        value = content["value"]
        try:
            for step in path:
                if type(step) is str and type(value) is dict or type(step) is int and type(value) is list:
                    value = value[step]
                else:
                    return UNKNOWN
            return value
        except (KeyError, IndexError):
            return UNKNOWN
    if form == "whole_except":
        if any(list(path[:len(p)]) == p for p in content["excluded_parts"]):
            return UNKNOWN
        if any(list(p[:len(path)]) == list(path) for p in content["excluded_parts"]):
            return UNKNOWN
        return literal_at(data, content["base"], path, seen)
    if form == "field_updates":
        for part in content["updates"]:
            if list(path[:len(part["path"])]) == part["path"]:
                return literal_at(data, part["data"], path[len(part["path"]):], seen)
        if any(list(part["path"][:len(path)]) == list(path) for part in content["updates"]):
            return UNKNOWN
        return literal_at(data, content["base"], path, seen)
    if form == "known_parts":
        for part in content["parts"]:
            if list(path[:len(part["path"])]) == part["path"]:
                return literal_at(data, part["data"], path[len(part["path"]):], seen)
    return UNKNOWN


class BooleanFacts:
    """Same-reference predicates share choices; different reads are not equated."""

    def __init__(self, engine, *, max_options=4096):
        self.engine, self.max_options = engine, max_options

    def location(self, target):
        entry = self.engine.targets.get(target_key(target))
        if entry is None:
            return None
        owner = entry.get("instruction_id")
        expression = self.engine.expressions.get((owner, tuple(entry["raw_path"])))
        return (expression, owner, entry) if expression is not None else None

    def ref_node(self, ref, ir, scope):
        if ref["kind"] == "input":
            return self.engine.node_at("ir_input", ir, slot=ref["index"])
        if ref["kind"] == "local":
            return (self.engine.elements.get((ir, scope, ref["name"]))
                    or self.engine.locals.get((ir, scope, ref["name"]))
                    or self.engine.locals.get((ir, None, ref["name"])))
        return None

    def available(self, expression, ir, scope, trace, seen=None):
        """Whether existing versions are available before this occurrence."""
        seen = set() if seen is None else set(seen)
        if not isinstance(expression, (dict, list)):
            return True
        if isinstance(expression, list):
            return all(self.available(child, ir, scope, trace, seen) for child in expression)
        if expression.get("op") == "literal":
            return True
        if expression.get("op") != "ref":
            return all(self.available(child, ir, scope, trace, seen) for child in expression.values())
        ref = expression["value"]
        marker = (ir, scope, canonical_sha256(ref))
        if marker in seen:
            return False
        seen.add(marker)
        if ref["kind"] == "literal":
            return True
        if ref["kind"] == "alternatives":
            return all(self.available({"op": "ref", "value": child}, ir, scope, trace, seen) for child in ref["items"])
        if ref["kind"] == "local":
            if (ir, scope, ref["name"]) in self.engine.elements:
                return scope is not None
            candidates = [key for key, info in self.engine.ops.items()
                          if info["position"]["instruction_id"] == ir
                          and info.get("scope") in (scope, None)
                          and info["spec"].get("output") == ref["name"]]
            def occurred(key):
                producer_scope = self.engine.ops[key].get("scope")
                frame = ("@scope:" + ir + ":" + repr(producer_scope) if producer_scope is not None
                         else "@instruction:" + ir)
                start = max((i for i, item in enumerate(trace) if item == frame), default=-1)
                return key in trace[start + 1:]
            return any(occurred(key) for key in candidates)
        operand = self.engine.index.instructions[ir]["inputs"][ref["index"]]
        if operand["type"] == "literal":
            return True
        definition = self.definition(ref, ir, scope)
        if definition is not None:
            return self.available(*definition, trace, seen)
        return "@instruction:" + ir in trace

    def ref_ids(self, ref, ir, scope):
        if ref["kind"] == "alternatives":
            return set().union(*(self.ref_ids(child, ir, scope) for child in ref["items"]))
        node = self.ref_node(ref, ir, scope)
        found = set(self.engine.nodes[node]["data_ids"]) if node is not None else set()
        if not found and hasattr(self.engine, "slots"):
            # Literal CFG operands intentionally have no ir_input Data node.
            # Existing consumption records retain their actual identities; do
            # not allocate a literal or conflate equal values from other sites.
            for key, info in self.engine.ops.items():
                if info["position"]["instruction_id"] != ir or info.get("scope") != scope:
                    continue
                for slot, (used, _) in self.engine.slots(key).items():
                    if used == ref:
                        found.update(info["record"]["inputs"][slot])
        return found

    def ref_values(self, ref, ir, scope, path=()):
        """Keep individually known candidate types before joining their values."""
        if ref["kind"] == "alternatives":
            return [value for child in ref["items"] for value in self.ref_values(child, ir, scope, path)]
        if ref["kind"] == "literal":
            values = [ref["value"]]
        elif ref["kind"] == "input" and self.engine.index.instructions[ir]["inputs"][ref["index"]]["type"] == "literal":
            values = [self.engine.index.instructions[ir]["inputs"][ref["index"]]["literal_value"]]
        else:
            identities = self.ref_ids(ref, ir, scope)
            result = []
            for identity in identities:
                presence = range_presence(self.engine.index.data, identity, path)
                value = (MISSING if presence in {"absent", "empty"} else INVALID if presence == "invalid"
                         else literal_at(self.engine.index.data, identity, path))
                if value is UNKNOWN:
                    kind = self.data_kind(identity, path)
                    if kind is not None:
                        value = _TypedUnknown(kind)
                result.append(value)
            return result or [UNKNOWN]
        return [_path_value(value, path) for value in values]

    def data_kind(self, identity, path=(), seen=None):
        """Type evidence from existing content/operations, without making values."""
        seen = set() if seen is None else set(seen)
        marker = (identity, tuple(path))
        if marker in seen:
            return None
        seen.add(marker)
        content = self.engine.index.data[identity]["content"]
        form = content["form"]
        if form == "literal":
            value = _path_value(content["value"], path)
            return None if value is MISSING or value is INVALID or value is UNKNOWN else type(value)
        if form in {"whole_except", "field_updates"}:
            for update in content.get("updates", []):
                if list(path[:len(update["path"])]) == update["path"]:
                    return self.data_kind(update["data"], path[len(update["path"]):], seen)
            return self.data_kind(content["base"], path, seen)
        if form == "subset_view" and not path:
            return list
        if form == "known_parts":
            kinds = set()
            for part in content["parts"]:
                if list(path[:len(part["path"])]) == part["path"]:
                    kind = self.data_kind(part["data"], path[len(part["path"]):], seen)
                    if kind is not None:
                        kinds.add(kind)
                elif part["path"][:len(path)] == list(path):
                    kinds.add(dict if type(part["path"][len(path)]) is str else list)
            if len(kinds) == 1:
                return next(iter(kinds))
        if not path:
            for info in self.engine.ops.values():
                if info["spec"]["op"] == "build" and any(identity in output for output in info["record"]["outputs"]):
                    return dict if info["spec"]["container"] == "object" else list
        return None

    def definition(self, ref, ir, scope):
        """Reuse an existing normalized producer expression, never source prose."""
        if ref["kind"] == "input":
            operand = self.engine.index.instructions[ir]["inputs"][ref["index"]]
            definition = self.engine.definitions.get(operand.get("identifier"))
            if operand["type"] == "result" and definition:
                producer, slot = definition
                binding = next((row for row in self.engine.compiled["ir_semantics"][producer]["output_bindings"]
                                if row["output_index"] == slot), None)
                if binding:
                    return {"op": "ref", "value": binding["value"]}, producer, None
        if ref["kind"] == "local":
            for info in self.engine.ops.values():
                if (info["position"]["instruction_id"] == ir and info.get("scope") == scope
                        and info["spec"].get("output") == ref["name"] and info.get("raw_op") is not None):
                    expression = self.engine.expressions.get((ir, tuple(info["raw_op"])))
                    if expression is not None:
                        return expression, ir, scope
        return None

    def identity(self, ref, ir, scope, seen=None):
        seen = set() if seen is None else set(seen)
        marker = (ir, scope, canonical_sha256(ref))
        if marker in seen:
            return [ir, list(scope) if scope else None, ref]
        seen.add(marker)
        if ref["kind"] == "literal":
            return ["literal", ref["value"]]
        if ref["kind"] == "input":
            operand = self.engine.index.instructions[ir]["inputs"][ref["index"]]
            if operand["type"] == "literal":
                return ["literal", operand["literal_value"]]
            if operand["type"] == "result":
                definition = self.engine.definitions.get(operand["identifier"])
                if definition:
                    producer, slot = definition
                    binding = next((row for row in self.engine.compiled["ir_semantics"][producer]["output_bindings"]
                                    if row["output_index"] == slot), None)
                    if binding:
                        return self.identity(binding["value"], producer, None, seen)
                return ["result", operand["identifier"]]
        return [ir, list(scope) if scope else None, ref]

    @staticmethod
    def _defined(values):
        if any(value is MISSING or value is INVALID for value in values):
            raise ConstraintUnsupported("A condition field access is definitely absent or invalid in an evaluated candidate.")

    @classmethod
    def _boolean(cls, values):
        cls._defined(values)
        if any(value is not UNKNOWN and _kind(value) is not bool for value in values):
            raise ConstraintUnsupported("A condition candidate is not Boolean; implicit truth conversion is unsupported.")

    def _bounded(self, values):
        unique = {}
        for value in values:
            key = ("unknown" if value is UNKNOWN else "missing" if value is MISSING else "invalid" if value is INVALID
                   else "type:" + value.kind.__name__ if isinstance(value, _TypedUnknown)
                   else canonical_sha256(["value", value]))
            unique.setdefault(key, value)
            if len(unique) > self.max_options:
                raise ConstraintLimit("Expression interpretation exceeded its finite resource limit.")
        return list(unique.values())

    def _pairs(self, left, right):
        if len(left) * len(right) > self.max_options:
            raise ConstraintLimit("Expression interpretation exceeded its finite resource limit.")
        return ((a, b) for a in left for b in right)

    def values(self, expr, ir, scope, seen=None):
        """Evaluate finite candidates without erasing a known undefined operand.

        Missing field is a separate value only for present(). Every other
        consumer rejects missing/invalid values; opaque unknown remains unknown.
        """
        seen = set() if seen is None else set(seen)
        op = expr["op"]
        if op == "literal":
            return [expr["value"]]
        if op == "ref":
            marker = (ir, scope, canonical_sha256(expr))
            definition = self.definition(expr["value"], ir, scope)
            if definition is not None and marker not in seen:
                return self.values(*definition, seen | {marker})
            return self._bounded(self.ref_values(expr["value"], ir, scope))
        if op == "field":
            cursor, path = expr, []
            while cursor["op"] == "field":
                path = [*cursor["path"], *path]
                cursor = cursor["arg"]
            if cursor["op"] == "ref":
                projected = self.ref_values(cursor["value"], ir, scope, path)
                if self.definition(cursor["value"], ir, scope) is not None:
                    candidates = self.values(cursor, ir, scope, seen)
                    projected += [_path_value(value, path) for value in candidates]
                return self._bounded(projected)
            return self._bounded(_path_value(value, path) for value in self.values(cursor, ir, scope, seen))
        if op == "present":
            values = self.values(expr["arg"], ir, scope, seen)
            if any(value is INVALID for value in values):
                raise ConstraintUnsupported("A presence test has an invalid field access for a known candidate type.")
            return self._bounded(False if value is MISSING else _TypedUnknown(bool) if value is UNKNOWN else True for value in values)
        if op == "count":
            values = self.values(expr["arg"], ir, scope, seen)
            self._defined(values)
            if any(value is not UNKNOWN and _kind(value) is not list for value in values):
                raise ConstraintUnsupported("A count operand is a known non-list candidate.")
            return self._bounded(_TypedUnknown(int) if _unknown(value) else len(value) for value in values)
        if op == "not":
            values = self.values(expr["arg"], ir, scope, seen)
            self._boolean(values)
            return self._bounded(_TypedUnknown(bool) if _unknown(value) else not value for value in values)
        if op in {"and", "or"}:
            current = [op == "and"]
            for child in expr["args"]:
                values = self.values(child, ir, scope, seen)
                self._boolean(values)
                result = []
                for a, b in self._pairs(current, values):
                    decisive = False if op == "and" else True
                    result.append(decisive if a is decisive or b is decisive else _TypedUnknown(bool)
                                  if _unknown(a) or _unknown(b) else not decisive)
                current = self._bounded(result)
            return current
        if op in {"eq", "ne", "lt", "le", "gt", "ge"}:
            left, right = self.values(expr["left"], ir, scope, seen), self.values(expr["right"], ir, scope, seen)
            self._defined([*left, *right])
            result = []
            for a, b in self._pairs(left, right):
                if op not in {"eq", "ne"} and (
                        a is not UNKNOWN and _kind(a) not in {int, float, str}
                        or b is not UNKNOWN and _kind(b) not in {int, float, str}
                        or a is not UNKNOWN and b is not UNKNOWN and _kind(a) is not _kind(b)):
                    raise ConstraintUnsupported("A condition comparison has incompatible known operand types.")
                if op in {"eq", "ne"} and a is not UNKNOWN and b is not UNKNOWN and _kind(a) is not _kind(b):
                    result.append(op == "ne")
                elif _unknown(a) or _unknown(b):
                    result.append(_TypedUnknown(bool))
                elif op in {"eq", "ne"}:
                    result.append(_equal(a, b) if op == "eq" else not _equal(a, b))
                else:
                    result.append({"lt": lambda: a < b, "le": lambda: a <= b,
                                   "gt": lambda: a > b, "ge": lambda: a >= b}[op]())
            return self._bounded(result)
        raise ConstraintUnsupported("The condition uses an unsupported expression operation.")

    def value(self, expr, ir, scope):
        values = self.values(expr, ir, scope)
        self._defined(values)
        return values[0] if values and all(not _unknown(value) and _equal(value, values[0]) for value in values) else UNKNOWN

    def canonical(self, expr, ir, scope):
        if isinstance(expr, list):
            return [self.canonical(value, ir, scope) for value in expr]
        if not isinstance(expr, dict):
            return expr
        if expr.get("op") == "ref":
            return {"ref": self.identity(expr["value"], ir, scope)}
        if expr.get("op") == "literal":
            return expr
        return {key: self.canonical(value, ir, scope) for key, value in expr.items()}

    def options(self, expr, ir, scope, cube, seen=None):
        seen = set() if seen is None else set(seen)
        op = expr["op"]
        if op == "ref":
            marker = (ir, scope, canonical_sha256(expr))
            definition = self.definition(expr["value"], ir, scope)
            if definition is not None and marker not in seen:
                return self.options(*definition, cube, seen | {marker})
        if op == "not":
            return [(not value, facts) for value, facts in self.options(expr["arg"], ir, scope, cube, seen)]
        if op in {"and", "or"}:
            current = [(op == "and", dict(cube))]
            for child in expr["args"]:
                following = []
                for prior, facts in current:
                    for value, updated in self.options(child, ir, scope, facts, seen):
                        following.append(((prior and value) if op == "and" else (prior or value), updated))
                        if len(following) > self.max_options:
                            raise ConstraintLimit("Boolean interpretation exceeded its finite resource limit.")
                current = following
            return current
        candidates = self.values(expr, ir, scope)
        self._boolean(candidates)
        value = candidates[0] if candidates and all(not _unknown(candidate) and _equal(candidate, candidates[0]) for candidate in candidates) else UNKNOWN
        if type(value) is bool:
            return [(value, dict(cube))]
        key = canonical_sha256(self.canonical(expr, ir, scope))
        if key in cube:
            return [(cube[key], dict(cube))]
        return [(value, {**cube, key: value}) for value in (False, True)]


def collection_size(data, identity, seen=None):
    """Only closed list structure supplies an exact occurrence multiplicity."""
    seen = set() if seen is None else set(seen)
    if identity in seen or identity not in data:
        return None
    seen.add(identity)
    content = data[identity]["content"]
    if content["form"] == "literal":
        return len(content["value"]) if type(content["value"]) is list else None
    if content["form"] == "known_parts" and content["parts_complete"]:
        indices = {row["path"][0] for row in content["parts"] if row["path"] and type(row["path"][0]) is int}
        if indices and indices == set(range(max(indices) + 1)) and all(type(row["path"][0]) is int for row in content["parts"]):
            return len(indices)
    if content["form"] in {"whole_except", "field_updates"}:
        edits = content.get("excluded_parts", [row["path"] for row in content.get("updates", [])])
        if all(len(path) > 1 for path in edits):
            return collection_size(data, content["base"], seen)
    return None
