"""Lossless input preparation and evidence locations for action annotations.

The original graph is transmitted once. Its index contains locations, never a
parallel paraphrase or a second serialization of operation contents.
"""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from skill_ir.backtrace.evidence import _require_json, json_pointer, resolve_pointer
from skill_ir.ir.cfg import ControlFlowGraph
from skill_ir.runtime_contract import execution_model, validate_execution_model
from skill_ir.representation_contract import representation_contract, validate as validate_representation
from skill_ir.source_evidence import _checked_source, _digest, source_units

from .models import SCHEMA_VERSION



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


def prepare_material(source: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    source = _checked_source(deepcopy(source))
    cfg = checked_cfg(cfg)
    graph_index: list[dict[str, Any]] = []
    instruction_index: dict[str, dict[str, Any]] = {}

    def add(pointer: str, **context: Any) -> str:
        location = f"g_{len(graph_index) + 1:04d}"
        graph_index.append({"id": location, "pointer": pointer, **context})
        return location

    # Scope/constraint locations support evidence without presenting container
    # labels as operational semantics. Instruction subtrees preserve metadata.
    for key in cfg:
        if key != "blocks":
            add(json_pointer(key))
    for block_key, block in cfg["blocks"].items():
        for key in block:
            if key != "instructions":
                add(json_pointer("blocks", block_key, key), block_id=block_key)
        for position, instruction in enumerate(block.get("instructions", [])):
            instruction_id = instruction["id"]
            if instruction_id in instruction_index:
                raise ValueError(f"duplicate instruction id: {instruction_id}")
            pointer = json_pointer("blocks", block_key, "instructions", position)
            location = add(pointer, block_id=block_key, instruction_id=instruction_id)
            instruction_index[instruction_id] = {
                "block_id": block_key, "position": position, "ref_id": location,
            }
    if not instruction_index:
        raise ValueError("security annotation requires at least one actual instruction")
    return {
        "version": SCHEMA_VERSION,
        "source": source,
        "cfg": cfg,
        "source_index": [
            {key: unit[key] for key in ("id", "file", "start_line", "end_line")}
            for unit in source_units(source)
        ],
        "graph_index": graph_index,
        "instruction_index": instruction_index,
        "execution_model": execution_model(),
        "representation_contract": representation_contract(),
    }


def checked_material(material: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(material, dict):
        raise ValueError("material must be a prepared input object")
    validate_execution_model(material.get("execution_model"))
    validate_representation(material.get("representation_contract"))
    prepared = prepare_material(material["source"], material["cfg"])
    if _digest(prepared) != _digest(material):
        raise ValueError("prepared material indexes, schema, or execution rules differ")
    return prepared


def _scalar_quotes(value: Any):
    if isinstance(value, dict):
        for item in value.values():
            yield from _scalar_quotes(item)
    elif isinstance(value, list):
        for item in value:
            yield from _scalar_quotes(item)
    elif isinstance(value, str):
        yield value
    else:
        yield json.dumps(value, ensure_ascii=False, allow_nan=False)


def check_evidence(evidence: dict[str, Any], material: dict[str, Any]) -> None:
    basis, location, quote = evidence["basis"], evidence["ref_id"], evidence["quote"]
    if basis == "source":
        units = {unit["id"]: unit for unit in source_units(material["source"])}
        unit = units.get(location)
        if unit is None:
            raise ValueError(f"source evidence location does not exist: {location}")
        # Use the indexed original lines, retaining their exact line endings;
        # a normalized index must not silently normalize model quotations.
        original = next(item["content"] for item in material["source"]["files"] if item["path"] == unit["file"])
        lines = original.splitlines(keepends=True)
        matches = quote in "".join(lines[unit["start_line"] - 1:unit["end_line"]])
    elif basis == "cfg":
        indexes = {item["id"]: item for item in material["graph_index"]}
        item = indexes.get(location)
        if item is None:
            raise ValueError(f"CFG evidence location does not exist: {location}")
        value = resolve_pointer(material["cfg"], item["pointer"])
        # Short literal snippets come from scalar VALUES inside this indexed
        # subtree, not JSON keys, fabricated summaries, or another instruction.
        matches = any(quote in text for text in _scalar_quotes(value))
    else:
        rules = {rule["id"]: rule["text"] for rule in material["execution_model"]["rules"]}
        if location not in rules:
            raise ValueError(f"execution model evidence rule does not exist: {location}")
        matches = quote in rules[location]
    if not matches:
        raise ValueError(f"evidence quote does not match {basis} location {location}")
