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
from skill_ir.source_evidence import _checked_source, _digest, source_units

from .models import SCHEMA_VERSION


EXECUTION_MODEL = {
    "version": "wide-read-agent-v6",
    "rules": [
        {"id": "EM01", "text": "Wide-read assumption: a natural-language request for a field from a container does not establish a key-only read mechanism. Unless an explicit narrow interface, local read mechanism, or isolation boundary supports a restricted scope, preserve the related source container as the read value, then express the requested field selection separately in symbolic operations. Merely needing one field is not a scope restriction. The container may remain unexpanded; do not invent its other fields, sensitive-data sets, file paths, or a read of all runtime state. This is an analysis assumption, not an additional source-level CFG action."},
        {"id": "EM02", "text": "Tool-result return assumption: content returned by an agent tool enters the LLM context by default. Respect explicit boundaries for local-only processing, model-invisible content, handles, or isolated storage. This is an analysis assumption, not a fact about all agents."},
        {"id": "EM03", "text": "LLM scheduling does not imply content visibility: merely selecting or initiating an action is insufficient for model_observe. For content acquired for the agent's natural-language processing, assume that content enters model processing unless an explicit local-only, model-invisible, or isolation boundary says otherwise. Apply observation to the acquired version before model selection or transformation. An agent_runtime or tool executor label, or an opcode name, is not evidence of model invisibility. Clearly distinguish this default analysis assumption from observed runtime evidence."},
        {"id": "EM04", "text": "Distinguish local and model processing: local field selection, masking, encryption, and summarization have transform. A model that selects from or transforms content first observes the input version; explicitly local processing with only its result returned to the model exposes that result instead. An explicit key-only getter may acquire only its returned value, and visibility is assessed separately. A model-invisible credential proxy or handle must not be treated as secret plaintext. Do not invent repeated observation stages. transform does not guarantee removal of sensitive data."},
        {"id": "EM05", "text": "Declarations do not replace behavior: constraints such as prohibiting disclosure or using only specified fields do not automatically constitute executed filtering, masking, or isolation. Do not invent business actions absent from the graph."},
        {"id": "EM06", "text": "Do not guess boundaries: a tool name or LLM identity alone does not prove remote network communication; an ordinary return alone does not prove user-facing output. Assess model observation and network transfer separately. Record uncertainty externally as unresolved."},
        {"id": "EM07", "text": "Runtime-context writes: context_write requires evidence of creating, updating, or deleting runtime context content or bindings that later actions can read, including shared session state and environment variables. Merely producing an IR result is not a context write. File writes and model observation do not automatically imply context_write; each effect requires its own evidence. Saving unchanged content does not imply transform. Deleting a binding does not imply reading, transforming, or observing its former content. This rule explains classification; it does not establish that an otherwise unrecorded write occurred."},
        {"id": "EM08", "text": "Symbolic transfer boundary: preserve relevant input content unless an explicit selection, deletion, replacement, or isolation supports reduction. Unknown computations retain possible input dependencies, without claiming every input byte survives. A dynamic or unresolved location identity must use a symbolic: name and cannot justify a definite overwrite or deletion. Unknown content inside an identified source is not an unknown address and must not make that source alias unrelated locations. An uncertain effect order cannot justify observing only a cleaned result; retain original candidates alongside possible later results. Broad observation does not broaden actual outbound arguments: selection results and explicit prohibitions still govern delivery. This stage declares symbolic operations, not propagated Data identities or sensitive-data sets."},
        {"id": "EM09", "text": "Acquisition and computation differ: a tool or collection can return newly acquired content whose origin is not exhausted by the query inputs. Preserve its acquisition boundary alongside actual request inputs and possible dependencies. If remote communication is established, use receive at a remote location with net_receive; if tool content is acquired but networking is unknown or explicitly local, use receive at a tool location in a null-effect event. This does not invent a network label. An explicitly pure calculation remains compute; opaque computation preserves possible input dependencies without inventing an independent acquisition source. Unknown networking does not erase known tool acquisition or the tool-result observation assumption."},
    ],
}


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
        "execution_model": deepcopy(EXECUTION_MODEL),
    }


def checked_material(material: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(material, dict):
        raise ValueError("material must be a prepared input object")
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
