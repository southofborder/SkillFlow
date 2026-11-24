"""Self-contained exact-value shorthand for processing responses.

This is serialization only. No prior artifact, CFG, Task or semantic default is
read here. Every expanded record still passes the existing fragment validators.
"""
from __future__ import annotations

import json
import re
from typing import Any

from skillflow.common.source_evidence import _json_object, json_pointer


PROCESSING_WIRE_IDENTITY = "skillflow-processing-json-v1"
DEFINITION_NAME_PATTERN = r"v(?:0|[1-9][0-9]*)"
WIRE_ROOT_FIELDS = frozenset({"format", "shared_values", "payload"})
WIRE_MARKERS = frozenset({"$ref", "$literal_object"})
MAX_EXPANDED_CHARS = 16 * 1024 * 1024
MAX_EXPANDED_NODES = 500_000
MAX_EXPANDED_DEPTH = 128
_FIELDS = WIRE_ROOT_FIELDS
_MARKERS = WIRE_MARKERS


def valid_definition_name(name: Any) -> bool:
    """One unchanged identifier grammar for expansion, guidance and diagnostics."""
    return isinstance(name, str) and re.fullmatch(DEFINITION_NAME_PATTERN, name) is not None


class ProcessingWireError(ValueError):
    def __init__(self, path: str, message: str):
        self.path = path
        super().__init__(message)


def expand_processing_response(raw: Any) -> dict[str, Any]:
    """Parse a plain response or strictly expand its self-contained envelope.

    The expanded size, node count and depth of all definitions and the payload
    are checked before creating expanded containers. Cached measurements never
    cache mutable values; every occurrence gets its own independently copied
    object. An invalid unused definition is rejected too.
    """
    try:
        value = _json_object(raw)
    except RecursionError as error:
        raise ProcessingWireError("", "Processing JSON nesting exceeds the supported depth") from error
    if not _FIELDS.intersection(value):
        return value

    def fail(path, message):
        raise ProcessingWireError(json_pointer(*path), message)

    if set(value) != _FIELDS or value.get("format") != PROCESSING_WIRE_IDENTITY:
        fail((), "Processing wire requires exactly format=skillflow-processing-json-v1, shared_values and payload; return the complete fragment or this exact envelope")
    definitions = value["shared_values"]
    if not isinstance(definitions, dict) or any(not valid_definition_name(key) for key in definitions):
        fail(("shared_values",), "Processing shared_values must map vN identifiers to exact JSON values")
    measured, visiting = {}, set()

    def checked(chars, nodes, depth, path, references=0):
        if chars > MAX_EXPANDED_CHARS or nodes > MAX_EXPANDED_NODES or depth > MAX_EXPANDED_DEPTH:
            fail(path, f"Processing expansion exceeds its supported limits ({MAX_EXPANDED_CHARS} characters, {MAX_EXPANDED_NODES} nodes, {MAX_EXPANDED_DEPTH} levels); reduce repeated expansion or return the complete plain fragment without omitting records")
        return chars, nodes, depth, references

    def string_size(item):
        return len(json.dumps(item, ensure_ascii=False, separators=(",", ":"), allow_nan=False))

    def reference(name, path):
        if type(name) is not str or name not in definitions:
            fail(path, "Processing reference must name one declared shared_values entry")
        if name in visiting:
            fail(path, "Processing shared_values contain a cyclic reference; use finite exact JSON values")
        if name not in measured:
            if len(visiting) >= MAX_EXPANDED_DEPTH:
                fail(path, "Processing shared-value indirection exceeds the supported depth; shorten the reference chain without omitting records")
            visiting.add(name)
            measured[name] = measure(definitions[name], ("shared_values", name))
            visiting.remove(name)
        chars, nodes, depth, references = measured[name]
        if references + 1 > MAX_EXPANDED_DEPTH:
            fail(path, "Processing shared-value indirection exceeds the supported depth; shorten the reference chain without omitting records")
        return chars, nodes, depth, references + 1

    def object_items(item, path):
        if not isinstance(item, list):
            fail(path, "Processing $literal_object requires ordered [key,value] pairs")
        seen, pairs = set(), []
        for index, pair in enumerate(item):
            if not isinstance(pair, list) or len(pair) != 2 or type(pair[0]) is not str or pair[0] in seen:
                fail((*path, index), "Processing $literal_object requires distinct string keys and one value per pair")
            seen.add(pair[0])
            pairs.append((pair[0], pair[1], (*path, index, 1)))
        return pairs

    def measure(item, path):
        if len(path) > MAX_EXPANDED_DEPTH * 4:
            fail(path, "Processing encoded nesting exceeds the supported depth")
        if isinstance(item, dict):
            markers = _MARKERS.intersection(item)
            if markers:
                if len(item) != 1:
                    fail(path, "Processing marker objects must contain exactly one marker; escape literal marker keys with $literal_object")
                if "$ref" in item:
                    return reference(item["$ref"], (*path, "$ref"))
                pairs = object_items(item["$literal_object"], (*path, "$literal_object"))
            else:
                pairs = [(key, part, (*path, key)) for key, part in item.items()]
            chars, nodes, depth, references = 2, 1, 1, 0
            for index, (key, part, child_path) in enumerate(pairs):
                size, count, levels, child_references = measure(part, child_path)
                chars += (1 if index else 0) + string_size(key) + 1 + size
                nodes += count
                depth = max(depth, 1 + levels)
                references = max(references, child_references)
                checked(chars, nodes, depth, path)
            return checked(chars, nodes, depth, path, references)
        if isinstance(item, list):
            chars, nodes, depth, references = 2, 1, 1, 0
            for index, part in enumerate(item):
                size, count, levels, child_references = measure(part, (*path, index))
                chars += (1 if index else 0) + size
                nodes += count
                depth = max(depth, 1 + levels)
                references = max(references, child_references)
                checked(chars, nodes, depth, path)
            return checked(chars, nodes, depth, path, references)
        return checked(string_size(item), 1, 1, path)

    def expand(item):
        if isinstance(item, dict):
            if "$ref" in item:
                return expand(definitions[item["$ref"]])
            if "$literal_object" in item:
                return {key: expand(part) for key, part in item["$literal_object"]}
            return {key: expand(part) for key, part in item.items()}
        if isinstance(item, list):
            return [expand(part) for part in item]
        return item

    try:
        for name in definitions:
            reference(name, ("shared_values", name))
        measure(value["payload"], ("payload",))
        result = expand(value["payload"])
    except RecursionError as error:
        raise ProcessingWireError("", "Processing shared-value nesting exceeds the supported depth") from error
    if not isinstance(result, dict):
        fail(("payload",), "Expanded processing payload must be a complete JSON object")
    return result


def output_wire_example() -> dict[str, Any]:
    """Valid serialization example, deliberately separate from fragment schema."""
    return {"format": PROCESSING_WIRE_IDENTITY,
            "payload": {"example_left": {"$ref": "v1"}, "example_right": {"$ref": "v1"},
                        "example_literal": {"$literal_object": [["$ref", "ordinary literal text"],
                                                               ["nested", {"$ref": "v0"}]]}},
            "shared_values": {"v1": {"nested": {"$ref": "v0"}}, "v0": ["exact", "value"]}}


def output_wire_instructions() -> str:
    return (
        "OPTIONAL LOSSLESS PROCESSING RESPONSE\n"
        "Return either the plain complete fragment or a self-contained shared envelope. "
        "The envelope has exactly three root members: format, payload and shared_values; "
        f'format is exactly "{PROCESSING_WIRE_IDENTITY}". '
        "Every JSON object member name must occur exactly once: emit only one shared_values table, "
        "with each definition name once, never a second table to append or revise definitions. "
        f"Definition names must match exactly {DEFINITION_NAME_PATTERN}: v0, v1, v2, etc.; "
        "mnemonic names, v01 and negative indexes are invalid. "
        'Only an object with exactly {"$ref":"v0"} is a reference: its string must name a declared vN entry. '
        "References substitute exact complete JSON values, not templates or partial merges. "
        "Forward references and nested references are allowed; missing references and cycles are forbidden. "
        "Every definition is checked, including unused definitions. "
        'Escape any ordinary object with literal $ref or $literal_object keys as {"$literal_object":[["key",value],...]}; '
        "each pair has exactly a distinct string key and one value, preserving order; values may contain references. "
        "A marker object has exactly one marker and no other members. Unescaped $rows is ordinary data here, "
        "not the input display's row shorthand. All JSON numbers must be finite. "
        f"Expansion is bounded before allocation to {MAX_EXPANDED_CHARS} serialized characters, "
        f"{MAX_EXPANDED_NODES} nodes and {MAX_EXPANDED_DEPTH} levels; reference indirection is bounded too. "
        "The expanded payload must be an object and must satisfy the full required fragment or correction format. "
        "For initial, full-replacement and revision responses, every current IR and all required contracts "
        "must remain explicitly present in the complete expanded fragment. For an explicitly requested local "
        'record correction, payload is the complete {"replacements":[...]} object for the allowed selected '
        "record slots actually being replaced, not a whole fragment; each replacement value is complete, "
        "unlisted records remain unchanged and final merged coverage is rechecked. "
        "Share repeated evidence, bindings and identical structures only when the complete values are identical; "
        "references do not share data identities, members, operations, semantic claims or prior-run records. "
        "There are no templates, parameters, implicit defaults, "
        "old-fragment references or omitted-record inheritance. All JSON pointers and correction record IDs "
        "address the expanded fragment, never the envelope or definition table. Plain complete JSON remains valid. "
        "Each occurrence is validated by the unchanged fragment format and application rules below. "
        "Recommended generation order: format, then the complete payload with forward references, then one final "
        "shared_values table containing every chosen definition once. Root order is not an acceptance restriction. "
        "Choose a definition's final value before emitting that one table; never append another definition table. "
        "The following valid wire illustration shows forward/nested references and a literal escape; "
        "its example_* fields are explanatory only, so replace its payload with the required complete stage response.\n"
        + json.dumps(output_wire_example(), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    )


def expand_revision_rows(rows, definitions, *, owner, field):
    """Isolate a bad definition to its actual users, enforcing the whole-payload budget."""
    def wire(items, shared):
        return expand_processing_response({"format": PROCESSING_WIRE_IDENTITY, "shared_values": shared,
            "payload": {field: list(items.values())}})[field]

    try:
        return dict(zip(rows, wire(rows, definitions), strict=True)), []
    except (ValueError, TypeError):
        pass

    def dependencies(value):
        referenced, stack = set(), [value]
        while stack:
            item = stack.pop()
            if isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, dict):
                if set(item) == {"$ref"} and isinstance(item["$ref"], str):
                    name = item["$ref"]
                    if name not in referenced:
                        referenced.add(name)
                        if name in definitions:
                            stack.append(definitions[name])
                else:
                    stack.extend(item.values())
        return {name: definitions[name] for name in referenced if name in definitions}

    # Validate even unused definitions. An invalid definition cannot enter any
    # accepted row. The final combined expansion rechecks the original size limits.
    valid, diagnostics = {}, []
    for name in definitions:
        value = {"$ref": name}
        try:
            wire({0: value}, dependencies(value))
        except (ValueError, TypeError) as error:
            diagnostics.append({"code": "revision_shared_definition", "path": json_pointer("shared_values", name),
                "message": str(error), "context": {"member": name}})
        else:
            valid[name] = definitions[name]
    retained = {}
    for index, row in rows.items():
        try:
            refs = dependencies(row)
            wire({index: row}, {n: v for n, v in refs.items() if n in valid})
        except (ValueError, TypeError) as error:
            identity = row.get(owner) if isinstance(row, dict) else None
            diagnostics.append({"code": "revision_shared_reference", "path": json_pointer(field, index),
                "message": str(error), "context": {owner: identity} if isinstance(identity, str) else {}})
        else:
            retained[index] = row
    try:
        return dict(zip(retained, wire(retained, valid), strict=True)), diagnostics
    except (TypeError, ValueError) as error:
        from skillflow.common.validation import structural_error
        raise structural_error("revision_shared_limit", "", str(error)) from error
