"""Read-only normalization and exact evidence locations for a validated CFG.

This module interprets no opcode, condition, constraint, or embedded payload.
Result definitions are associated with uses by identifier, never by wording.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

from skill_ir.ir.cfg import ControlFlowGraph


def json_pointer(*parts: str | int) -> str:
    """Encode locations with RFC 6901 escaping, including unusual block keys."""
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def _require_json(value: Any, path: str, active: set[int] | None = None) -> None:
    """Reject non-JSON Any payloads before Pydantic can serialize them away."""
    active = set() if active is None else active
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"Non-JSON value at {path}: non-finite float")
        return
    if type(value) not in (dict, list):
        raise ValueError(f"Non-JSON value at {path}: {type(value).__name__}")
    if id(value) in active:
        raise ValueError(f"Non-JSON value at {path}: cyclic container")
    active.add(id(value))
    try:
        items = value.items() if type(value) is dict else enumerate(value)
        for key, item in items:
            if type(value) is dict and type(key) is not str:
                raise ValueError(f"Non-JSON object key at {path}: {type(key).__name__}")
            child = path + json_pointer(key)
            _require_json(item, child, active)
    finally:
        active.remove(id(value))


def canonical_graph_sha256(graph: dict[str, Any]) -> str:
    """Sort object keys, retain every list occurrence and its recorded order."""
    _require_json(graph, "")
    try:
        encoded = json.dumps(
            graph, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (ValueError, TypeError, UnicodeError) as error:
        raise ValueError(f"CFG cannot be represented as canonical UTF-8 JSON: {error}") from error
    return hashlib.sha256(encoded).hexdigest()


def definition_refs(graph: dict[str, Any]) -> dict[str, list[str]]:
    definitions: dict[str, list[str]] = {}
    for key, block in graph["blocks"].items():
        for position, instruction in enumerate(block["instructions"]):
            for index, operand in enumerate(instruction["outputs"]):
                if operand["type"] == "result":
                    definitions.setdefault(operand["identifier"], []).append(
                        json_pointer("blocks", key, "instructions", position, "outputs", index)
                    )
    return definitions


def normalize_cfg(cfg: ControlFlowGraph) -> dict[str, Any]:
    """Validate actual fields and return the complete public JSON graph.

    Embedded content remains inert data, including strings that resemble code
    or instructions. A metadata hash never replaces that content in the view.
    """
    if not isinstance(cfg, ControlFlowGraph):
        raise TypeError("normalize_cfg requires a ControlFlowGraph")
    cfg.validate_integrity()
    # These Any fields otherwise allow datetime/set/tuple/custom values that a
    # JSON-mode model export might coerce or reject after losing their identity.
    for key, block in cfg.blocks.items():
        for position, instruction in enumerate(block.instructions):
            base = ("blocks", key, "instructions", position)
            _require_json(instruction.metadata, json_pointer(*base, "metadata"))
            for direction in ("inputs", "outputs"):
                for index, operand in enumerate(getattr(instruction, direction)):
                    if operand.type.value == "literal":
                        _require_json(operand.literal_value, json_pointer(*base, direction, index, "literal_value"))
    try:
        graph = json.loads(cfg.to_json())
    except (ValueError, TypeError, UnicodeError) as error:
        raise ValueError(f"CFG JSON serialization failed: {error}") from error
    canonical_graph_sha256(graph)
    return graph


def resolve_pointer(document: Any, pointer: str) -> Any:
    """Strict RFC 6901 lookup for program-generated evidence positions."""
    if pointer == "":
        return document
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("Invalid JSON pointer")
    current = document
    for encoded in pointer[1:].split("/"):
        index = 0
        while index < len(encoded):
            if encoded[index] == "~":
                if index + 1 >= len(encoded) or encoded[index + 1] not in "01":
                    raise ValueError("Invalid JSON pointer escape")
                index += 2
            else:
                index += 1
        part = encoded.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(current, list):
                if not part.isascii() or not part.isdigit() or (len(part) > 1 and part[0] == "0"):
                    raise ValueError("Invalid JSON pointer array index")
                current = current[int(part)]
            elif isinstance(current, dict):
                current = current[part]
            else:
                raise ValueError("JSON pointer traverses a scalar")
        except (IndexError, KeyError) as error:
            raise ValueError("JSON pointer does not exist") from error
    return current
