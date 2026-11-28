"""Conservative finite classification of recorded data, preserving absent fields."""
from __future__ import annotations

import json
from functools import lru_cache

from skillflow.common.recording import canonical_sha256

_MISSING = object()
_UNKNOWN = object()


def _select_literal(value, path):
    for step in path:
        if type(step) is str and type(value) is dict and step in value:
            value = value[step]
        elif type(step) is int and type(value) is list and 0 <= step < len(value):
            value = value[step]
        else:
            return _MISSING
    return value


def _values(data, identity, path, seen=frozenset()):
    marker = (identity, tuple(path))
    if marker in seen or any(node == identity for node, _ in seen):
        yield _UNKNOWN
        return
    item = data.get(identity)
    content = item.model_dump(mode="json")["content"] if hasattr(item, "model_dump") else item["content"]
    yield from _options(data, content, path, seen | {marker})


def _options(data, content, path, seen):
    form = content["form"]
    if form == "literal":
        yield _select_literal(content["value"], path)
    elif form == "loop_summary" and content["variants"]:
        for variant in content["variants"]:
            yield from _options(data, variant["content"], path, seen)
    elif form == "selection" and all(type(x) in (int, str) for x in content["path"]):
        yield from _values(data, content["base"], [*content["path"], *path], seen)
    elif form == "known_parts":
        if not path and content["parts"]:
            yield {} if type(content["parts"][0]["path"][0]) is str else []
            return
        for part in content["parts"]:
            prefix = part["path"]
            if path[:len(prefix)] == prefix:
                yield from _values(data, part["data"], path[len(prefix):], seen)
                return
            if prefix[:len(path)] == path:
                yield {} if type(prefix[len(path)]) is str else []
                return
        yield _MISSING if path and content.get("parts_complete") else _UNKNOWN
    else:
        yield _UNKNOWN


def _equal_scalar(value, literal):
    if type(value) in (int, float) and type(literal) in (int, float):
        return value == literal
    return type(value) is type(literal) and value == literal


def _matches(test, value):
    kind = test["kind"]
    if kind == "equals":
        return _equal_scalar(value, test["value"])
    return {"object": type(value) is dict, "array": type(value) is list,
            "string": type(value) is str, "nonempty_string": type(value) is str and bool(value),
            "null": value is None, "missing": value is _MISSING}[kind]


def selector_outcomes(data, identity, selector):
    tests = selector["tests"]
    outcomes = set()
    if tests[0]["kind"] == "python_exception":
        from skillflow.propagation.data.summary import content_options
        from skillflow.propagation.python_exceptions import exception_match
        options = content_options(data, identity)
        for content in options or [{}]:
            outcomes.update(0 if match else 1 for match in
                            exception_match(content.get("python_exception_type"), tests[0]["classes"]))
    else:
        outcomes = _json_outcomes(data, identity, selector)
    item = data.get(identity)
    content = item.model_dump(mode="json")["content"] if hasattr(item, "model_dump") else item["content"]
    saved = content.get("bindings", {})
    return {i for i in outcomes if compatible_bindings(saved, selector_binding(data, identity, selector, i))}


def _json_outcomes(data, identity, selector):
    tests = selector["tests"]
    outcomes = set()
    for value in _values(data, identity, selector["path"]):
        if value is _UNKNOWN:
            outcomes.update(range(len(tests) + 1))
        else:
            outcomes.add(next((i for i, test in enumerate(tests) if _matches(test, value)), len(tests)))
    return outcomes


def literal_choice(value, selector):
    if selector["tests"][0]["kind"] == "python_exception":
        raise ValueError("A JSON literal cannot identify a Python thrown exception")
    value = _select_literal(value, selector["path"])
    return next((i for i, test in enumerate(selector["tests"]) if _matches(test, value)), len(selector["tests"]))


def observed_children(data, identities, path):
    """Concrete child edit sites at a selected subject, preserving its containing value."""
    if not all(type(step) in (str, int) for step in path):
        return
    for identity in identities:
        for value in _values(data, identity, path):
            yield from _children(value, path)


def literal_children(value, path):
    yield from _children(_select_literal(value, path), path)


def _children(value, path):
    if isinstance(value, dict):
        yield from ([*path, key] for key in value)
    elif isinstance(value, list):
        yield from ([*path, index] for index in range(len(value)))


def _selector_subject(data, identity, path):
    seen = set()
    while identity not in seen:
        seen.add(identity)
        item = data.get(identity)
        content = item.model_dump(mode="json")["content"] if hasattr(item, "model_dump") else item["content"]
        if content.get("form") == "loop_summary" and content["scope"].startswith("selector-route:"):
            identity = content["scope"].removeprefix("selector-route:")
            continue
        if content["form"] != "selection" or not all(type(step) in (str, int) for step in content["path"]):
            break
        path = [*content["path"], *path]
        identity = content["base"]
    return "selector:" + canonical_sha256([identity, path]) + ":"


_TYPE_DOMAINS = {"object": {"object"}, "array": {"array"}, "string": {"empty", "text"},
                 "nonempty_string": {"text"}, "null": {"null"}, "missing": {"missing"}}
_ATOMS = set.union(*_TYPE_DOMAINS.values(), {"true", "false", "number"})


@lru_cache(maxsize=8192)
def _consistent_subject(claims):
    """Decide a conjunction for one immutable subject in the supported JSON predicate language."""
    allowed = _ATOMS.copy()
    equalities = []
    for encoded, truth in claims:
        if encoded.startswith("equals:"):
            value = json.loads(encoded[7:])
            if type(value) not in (str, int, float, bool, type(None)):
                return False
            equalities.append((value, truth))
        elif truth:
            allowed.intersection_update(_TYPE_DOMAINS[encoded])
        else:
            allowed.difference_update(_TYPE_DOMAINS[encoded])
    if not allowed:
        return False
    for value, truth in equalities:
        if truth:
            atom = _scalar_atom(value)
            return atom in allowed and all(
                _equal_scalar(value, other) == required for other, required in equalities)
        # Finite exclusions can exhaust a singleton but cannot exhaust numbers or nonempty text.
        atom = _scalar_atom(value)
        if atom in {"null", "empty", "true", "false"}:
            allowed.discard(atom)
    return bool(allowed)


def _scalar_atom(value):
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is str:
        return "text" if value else "empty"
    return "number"


def consistent_bindings(bindings):
    grouped = {}
    for key, value in bindings.items():
        if key.startswith("selector:"):
            pieces = key.split(":", 2)
            if len(pieces) != 3 or value not in {"0", "1"}:
                return False
            _, subject, predicate = pieces
            if predicate not in _TYPE_DOMAINS and not predicate.startswith("equals:"):
                return False
            grouped.setdefault(subject, []).append((predicate, value == "1"))
    return all(_consistent_subject(tuple(sorted(claims))) for claims in grouped.values())


def compatible_bindings(left, right):
    if any(key in left and left[key] != value for key, value in right.items()):
        return False
    return consistent_bindings({**left, **right})


def selector_binding(registry, identity, selector, outcome):
    # A loop family can summarize several dynamic versions. Its stable ID
    # alone cannot prove all its observations made the same choice.
    fact = getattr(registry, "facts", {}).get(identity)
    if fact and fact["scope"] in registry.scopes.values():
        return {}
    prefix = _selector_subject(registry, identity, selector["path"])
    decisions = {}
    for index, test in enumerate(selector["tests"][:outcome + 1]):
        key = test["kind"]
        if key == "python_exception":
            decisions["python-handler:" + prefix + ",".join(sorted(test["classes"]))] = "1" if index == outcome else "0"
            continue
        if key == "equals":
            key += ":" + json.dumps(test["value"], ensure_ascii=False, separators=(",", ":"))
        decisions[prefix + key] = "1" if index == outcome else "0"
    return decisions


def routed_identity(registry, identity, bindings):
    from skillflow.propagation.data import SelectionContent, Origin, Dependency
    existing = registry.bindings(identity)
    if existing == bindings:
        return identity
    fact = registry.facts.get(identity)
    base = (fact["scope"].removeprefix("selector-route:") if fact and fact["scope"].startswith("selector-route:")
            else identity)
    return registry.family("selector-route:" + base, ["selector-route", base], [base],
        SelectionContent(base=base, path=[]), Origin(at="typed branch selector", inputs=[base],
        dependencies=[Dependency(data=base, relation="derived")]), bindings={**existing, **bindings}).id
