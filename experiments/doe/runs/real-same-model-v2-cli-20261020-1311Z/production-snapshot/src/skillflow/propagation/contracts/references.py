"""Direct references to frozen CFG objects, without a persisted address table."""
from __future__ import annotations

from copy import deepcopy
import json
from typing import Annotated, Literal

from pydantic import Field, StrictStr, TypeAdapter
from skillflow.common.source_evidence import json_pointer
from skillflow.propagation.contracts.values import StrictSpec, Text, Index

ReferencePath = list[StrictStr | Index]


class OperandRef(StrictSpec):
    instruction_id: Text
    side: Literal["input", "output"]
    index: Index


class InstructionTarget(StrictSpec):
    instruction_id: Text
    path: ReferencePath


class BlockTarget(StrictSpec):
    block_id: Text
    path: ReferencePath


class GraphTarget(StrictSpec):
    path: ReferencePath


CFGTarget = OperandRef | InstructionTarget | BlockTarget | GraphTarget
CFG_TARGET = TypeAdapter(CFGTarget)


class SelfTarget(StrictSpec):
    kind: Literal["self"]


class InputTarget(StrictSpec):
    kind: Literal["input"]
    index: Index


class OutputTarget(StrictSpec):
    kind: Literal["output"]


OperationSlot = Annotated[SelfTarget | InputTarget | OutputTarget, Field(discriminator="kind")]


class OperationTarget(StrictSpec):
    """Program-generated raw operation coordinate, never a predicted model ID."""
    instruction_id: Text
    operation_path: ReferencePath
    slot: OperationSlot


DemandTarget = CFGTarget | OperationTarget


def cfg_instructions(cfg):
    return {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}


def target_key(target):
    if hasattr(target, "model_dump"):
        target = target.model_dump(mode="json")
    return json.dumps(target, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _kind(parts):
    if not parts:
        return "graph"
    if parts[0] == "constraints":
        return "constraints" if len(parts) == 1 else "constraint"
    if parts[0] == "edges":
        return "container" if len(parts) == 1 else "edge" if len(parts) == 2 else "field"
    if parts[0] != "blocks":
        return "field"
    if len(parts) == 1:
        return "container"
    if len(parts) == 2:
        return "block"
    if parts[2] == "constraints":
        return "constraints" if len(parts) == 3 else "constraint"
    if parts[2] != "instructions":
        return "field"
    if len(parts) == 3:
        return "container"
    if len(parts) == 4:
        return "instruction"
    if parts[4] == "metadata":
        return "metadata" if len(parts) == 5 else "metadata_value"
    if parts[4] == "constraints":
        return "constraints" if len(parts) == 5 else "constraint"
    if parts[4] in {"inputs", "outputs"}:
        if len(parts) == 5:
            return "container"
        if len(parts) == 6:
            return "input" if parts[4] == "inputs" else "output"
        return "operand_field"
    return "field"


def cfg_target_from_path(cfg, path):
    path = list(path)
    if len(path) >= 4 and path[0] == "blocks" and path[2] == "instructions":
        ir = cfg["blocks"][path[1]]["instructions"][path[3]]
        tail = path[4:]
        if len(tail) == 2 and tail[0] in {"inputs", "outputs"}:
            return {"instruction_id": ir["id"], "side": tail[0][:-1], "index": tail[1]}
        return {"instruction_id": ir["id"], "path": tail}
    if len(path) >= 2 and path[0] == "blocks":
        return {"block_id": path[1], "path": path[2:]}
    return {"path": path}


def resolve_cfg_target(target, cfg):
    """Resolve a canonical reference and classify its actual schema position."""
    if hasattr(target, "model_dump"):
        target = target.model_dump(mode="json")
    value = CFG_TARGET.validate_python(target)
    data = value.model_dump(mode="json")
    if isinstance(value, (OperandRef, InstructionTarget)):
        matches = [(bid, index) for bid, block in cfg["blocks"].items()
                   for index, ir in enumerate(block["instructions"]) if ir["id"] == value.instruction_id]
        if len(matches) != 1:
            raise ValueError("target instruction does not exist uniquely: " + value.instruction_id)
        bid, index = matches[0]
        tail = [value.side + "s", value.index] if isinstance(value, OperandRef) else value.path
        parts = ["blocks", bid, "instructions", index, *tail]
    elif isinstance(value, BlockTarget):
        parts = ["blocks", value.block_id, *value.path]
    else:
        parts = list(value.path)
    current = cfg
    for step in parts:
        if isinstance(current, dict) and type(step) is str and step in current:
            current = current[step]
        elif isinstance(current, list) and type(step) is int and 0 <= step < len(current):
            current = current[step]
        else:
            raise ValueError("CFG target path does not exist or uses the wrong key/index type")
    if cfg_target_from_path(cfg, parts) != data:
        raise ValueError("noncanonical CFG target: use an IR/block anchor or the real OperandRef")
    result = {"domain": "cfg", "target": data, "pointer": json_pointer(*parts),
              "raw_path": parts, "kind": _kind(parts), "value": deepcopy(current)}
    if len(parts) >= 2 and parts[0] == "blocks":
        result["block_id"] = parts[1]
    if len(parts) >= 4 and parts[0] == "blocks" and parts[2] == "instructions":
        result["instruction_id"] = cfg["blocks"][parts[1]]["instructions"][parts[3]]["id"]
    return result


def cfg_target_index(cfg):
    """Ephemeral lookup only; neither model material nor a saved target table."""
    result = {}
    def walk(value, path):
        target = cfg_target_from_path(cfg, path)
        result[target_key(target)] = resolve_cfg_target(target, cfg)
        if isinstance(value, dict):
            for name in sorted(value):
                walk(value[name], [*path, name])
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, [*path, index])
    walk(cfg, [])
    return result
