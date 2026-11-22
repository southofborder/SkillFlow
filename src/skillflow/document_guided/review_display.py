"""Readable, lossless source-review display with exact shared JSON values.

This changes presentation only. Source text is not an argument to this module.
Logical object key order, array occurrences, numeric types, optional fields and
literal marker-like objects survive expansion unchanged. A fixed marked
envelope has constant overhead on tiny payloads; optional tables and references
are used only when the complete candidate envelope is shorter.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
import re
from typing import Any

from skillflow.common.source_evidence import _require_json


DISPLAY_IDENTITY = "skillflow-review-display-v1"
_MARKERS = frozenset({"$ref", "$rows", "$literal_object"})
_ENVELOPE_FIELDS = frozenset({"format", "record_columns", "shared_values", "payload"})


def _json(value: Any) -> str:
    # Insertion order is significant to this presentation's lossless guarantee.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _prepared(payload: Any, *, tables: bool) -> tuple[Any, list[list[str]]]:
    columns: list[list[str]] = []
    column_indexes: dict[tuple[str, ...], int] = {}

    def records(values: list[dict[str, Any]], path: tuple[str | int, ...]) -> dict[str, Any]:
        rows = []
        for index, record in enumerate(values):
            shape = tuple(record)
            if shape not in column_indexes:
                column_indexes[shape] = len(columns)
                columns.append(list(shape))
            rows.append([column_indexes[shape], *[
                encode(item, (*path, index, key)) for key, item in record.items()]])
        return {"$rows": rows}

    def encode(value: Any, path: tuple[str | int, ...]) -> Any:
        is_obligations = path == ("input_contract_inventory", "obligations")
        is_scopes = (len(path) == 4 and path[:2] == ("input_contract_inventory", "obligations")
                     and type(path[2]) is int and path[3] == "scopes")
        if (tables and (is_obligations or is_scopes) and isinstance(value, list)
                and value and all(isinstance(item, dict) for item in value)):
            return records(value, path)
        if isinstance(value, dict):
            if _MARKERS.intersection(value):
                return {"$literal_object": [[key, encode(item, (*path, key))]
                                             for key, item in value.items()]}
            return {key: encode(item, (*path, key)) for key, item in value.items()}
        if isinstance(value, list):
            return [encode(item, (*path, index)) for index, item in enumerate(value)]
        return value

    return encode(payload, ()), columns


def _shared_values(payload: Any) -> tuple[Any, dict[str, Any]]:
    counts: Counter[str] = Counter()
    original: dict[str, Any] = {}

    def visit(value: Any) -> None:
        if isinstance(value, (dict, list, str)):
            fingerprint = _json(value)
            counts[fingerprint] += 1
            original[fingerprint] = value
        if isinstance(value, dict):
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(payload)
    minimum_reference = len(_json({"$ref": "v0"}))
    candidates = sorted((fingerprint for fingerprint, count in counts.items()
                         if count > 1 and len(fingerprint) > minimum_reference),
                        key=lambda fingerprint: (len(fingerprint), fingerprint))
    selected = set(candidates)

    def build(names: dict[str, str]) -> tuple[Any, dict[str, Any]]:
        def encode(value: Any, defining: str | None = None) -> Any:
            fingerprint = _json(value) if isinstance(value, (dict, list, str)) else None
            if fingerprint in names and fingerprint != defining:
                return {"$ref": names[fingerprint]}
            if isinstance(value, dict):
                return {key: encode(item) for key, item in value.items()}
            if isinstance(value, list):
                return [encode(item) for item in value]
            return value
        definitions = {name: encode(original[fingerprint], defining=fingerprint)
                       for fingerprint, name in names.items()}
        return encode(payload), definitions

    while selected:
        names = {fingerprint: f"v{index}" for index, fingerprint in enumerate(
            item for item in candidates if item in selected)}
        encoded, definitions = build(names)
        uses: Counter[str] = Counter()

        def references(value: Any) -> None:
            if isinstance(value, dict):
                if set(value) == {"$ref"}:
                    uses[value["$ref"]] += 1
                else:
                    for item in value.values():
                        references(item)
            elif isinstance(value, list):
                for item in value:
                    references(item)

        references(encoded)
        for definition in definitions.values():
            references(definition)
        remove = set()
        for fingerprint, name in names.items():
            occurrences = uses[name]
            size = len(_json(definitions[name]))
            reference_size = len(_json({"$ref": name}))
            # Include the definition's key, colon and comma. Reconsider after
            # removing enclosing or nested candidates because their uses change.
            saving = (occurrences - 1) * size - occurrences * reference_size - len(_json(name)) - 2
            if occurrences < 2 or saving <= 0:
                remove.add(fingerprint)
        if not remove:
            return encoded, definitions
        selected.difference_update(remove)
    return payload, {}


def pack_review_payload(payload: Any) -> dict[str, Any]:
    """Return the shortest supported marked view without changing the input.

    The choices are plain escaped values, exact value sharing, inventory column
    tables, and their combination. The fixed envelope remains on small inputs;
    optional compression cannot make that envelope larger. No size limit causes
    truncation, omission, scope merging or a semantic fallback.
    """
    _require_json(payload, "")
    candidates = []
    for tables in (False, True):
        prepared, columns = _prepared(payload, tables=tables)
        shared, definitions = _shared_values(prepared)
        for value, values in ((prepared, {}), (shared, definitions)):
            candidates.append({"format": DISPLAY_IDENTITY, "record_columns": columns,
                               "shared_values": values, "payload": value})
    return min(candidates, key=lambda value: len(_json(value)))


def expand_review_payload(display: Any) -> Any:
    """Validate and expand a display to its exact logical JSON payload.

    Missing definitions, cycles, malformed rows, duplicate object keys and
    ambiguous marker objects fail explicitly. References copy values at each
    occurrence; they do not merge operation, member or contract identities.
    """
    try:
        _require_json(display, "")
        if not isinstance(display, dict) or set(display) != _ENVELOPE_FIELDS:
            raise ValueError("Review display must contain exactly format, record_columns, shared_values and payload")
        if display["format"] != DISPLAY_IDENTITY:
            raise ValueError("Unsupported review display format")
        columns = display["record_columns"]
        if not isinstance(columns, list):
            raise ValueError("Review display record_columns must be an array")
        for shape in columns:
            if (not isinstance(shape, list) or any(type(key) is not str for key in shape)
                    or len(set(shape)) != len(shape)):
                raise ValueError("Review display columns must contain unique string field names")
        if len({tuple(shape) for shape in columns}) != len(columns):
            raise ValueError("Review display contains duplicate column sets")
        definitions = display["shared_values"]
        if (not isinstance(definitions, dict)
                or any(not re.fullmatch(r"v(?:0|[1-9][0-9]*)", key) for key in definitions)):
            raise ValueError("Review display shared_values must map vN identifiers to values")
        visiting: set[str] = set()
        expanded: dict[str, Any] = {}

        def expand(value: Any) -> Any:
            if isinstance(value, dict):
                markers = _MARKERS.intersection(value)
                if markers:
                    if len(value) != 1:
                        raise ValueError("Review display marker objects must contain exactly one marker")
                    marker = next(iter(markers))
                    body = value[marker]
                    if marker == "$ref":
                        if type(body) is not str or body not in definitions:
                            raise ValueError("Review display reference does not identify a shared value")
                        if body in visiting:
                            raise ValueError("Review display contains a cyclic shared-value reference")
                        if body not in expanded:
                            visiting.add(body)
                            expanded[body] = expand(definitions[body])
                            visiting.remove(body)
                        return deepcopy(expanded[body])
                    body = expand(body)
                    if not isinstance(body, list):
                        raise ValueError("Review display rows and literal objects require arrays")
                    if marker == "$literal_object":
                        result = {}
                        for pair in body:
                            if (not isinstance(pair, list) or len(pair) != 2 or type(pair[0]) is not str
                                    or pair[0] in result):
                                raise ValueError("Review display literal object requires distinct string-key pairs")
                            result[pair[0]] = pair[1]
                        return result
                    result = []
                    for row in body:
                        if (not isinstance(row, list) or not row or type(row[0]) is not int
                                or not 0 <= row[0] < len(columns)):
                            raise ValueError("Review display row requires a valid integer column-set index")
                        shape = columns[row[0]]
                        if len(row) != len(shape) + 1:
                            raise ValueError("Review display row width does not match its column set")
                        result.append(dict(zip(shape, row[1:])))
                    return result
                return {key: expand(item) for key, item in value.items()}
            if isinstance(value, list):
                return [expand(item) for item in value]
            return value

        # Validate even an unused definition, rather than concealing a malformed
        # table behind an otherwise valid root payload.
        for name in definitions:
            expand({"$ref": name})
        return expand(display["payload"])
    except RecursionError as error:
        raise ValueError("Review display nesting exceeds the supported JSON depth") from error


def display_instructions() -> str:
    """Explain the complete visible representation without requiring tools."""
    return (
        "LOSSLESS REVIEW DISPLAY\n"
        "INPUT_JSON has format skillflow-review-display-v1. Its payload is the logical review input, "
        "using the following visible shorthand; no source, contract, obligation or scope is omitted. "
        "An object containing only $ref names one exact JSON value in shared_values. Read that value "
        "at every occurrence; nested references use the same table. This shares text, not data identities, "
        "operations, conditions, members or review decisions. An object containing only $rows represents "
        "an ordered array of records: each row begins with a zero-based index into record_columns, "
        "then gives one value per listed field in that exact order. Different column sets preserve missing "
        "fields versus explicit null. An object containing only $literal_object represents the literal "
        "object formed by its ordered [key,value] pairs; its resulting keys are ordinary data, even when "
        "named $ref or $rows. Expand shorthand conceptually before interpreting the input. All target "
        "coordinates and JSON pointers refer to that expanded logical payload, never to shared_values, "
        "record_columns, row positions or the display envelope. Keep every listed obligation and scope ID "
        "unchanged in the response; paired request/response obligations remain separate. Return the usual "
        "response schema, not this display encoding. COMPLETE SOURCE follows separately and is unchanged."
    )
