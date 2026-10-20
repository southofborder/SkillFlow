"""Read-only normalization and exact evidence locations for a validated CFG.

This module interprets no opcode, condition, constraint, or embedded payload.
Result definitions are associated with uses by identifier, never by wording.
"""

from __future__ import annotations

import json
from typing import Any

from skillflow.common.source_evidence import (
    _require_json, canonical_graph_sha256, json_pointer, resolve_pointer,
)

from skillflow.graph.ir.cfg import ControlFlowGraph


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


