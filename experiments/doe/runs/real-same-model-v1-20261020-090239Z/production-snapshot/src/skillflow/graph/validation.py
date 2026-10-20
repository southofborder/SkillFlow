"""Exact JSON boundary for the existing CFG structure validator.

Supplied fields remain unchanged; model defaults are accepted only when absent.
This validates representation identity, not business semantics or reachability.
"""
from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from skillflow.common.source_evidence import _require_json, json_pointer
from skillflow.graph.ir.cfg import ControlFlowGraph


def _preserved_fields(raw: Any, normalized: Any, pointer: str = "") -> None:
    """Allow model defaults only when absent; never normalize a supplied field."""
    if isinstance(raw, dict):
        if not isinstance(normalized, dict):
            raise ValueError(f"CFG field changed during validation: {pointer}")
        for key, value in raw.items():
            if key not in normalized:
                raise ValueError(f"CFG field lost during validation: {pointer}/{key}")
            _preserved_fields(value, normalized[key], pointer + json_pointer(key))
    elif isinstance(raw, list):
        if not isinstance(normalized, list) or len(raw) != len(normalized):
            raise ValueError(f"CFG list changed during validation: {pointer}")
        for index, value in enumerate(raw):
            _preserved_fields(value, normalized[index], pointer + json_pointer(index))
    elif type(raw) is not type(normalized) or raw != normalized:
        raise ValueError(f"CFG field would be normalized: {pointer}")


def checked_cfg(cfg: dict[str, Any]) -> dict[str, Any]:
    if type(cfg) is not dict:
        raise ValueError("cfg must be the actual CFG JSON object")
    _require_json(cfg, "")
    # Use JSON validation so the existing enum contracts remain unchanged.
    model = ControlFlowGraph.model_validate_json(json.dumps(cfg, ensure_ascii=False, allow_nan=False))
    model.validate_integrity()
    _preserved_fields(cfg, model.model_dump(mode="json"))
    return deepcopy(cfg)


