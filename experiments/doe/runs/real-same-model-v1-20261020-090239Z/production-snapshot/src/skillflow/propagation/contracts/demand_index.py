"""Deterministic targets for offline demands and raw symbolic operations.

The index describes existing positions; it never fabricates a public return
output or a compiled observation coordinate. Input uses retain their positions,
including repeated arguments and conditional construction controls.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import TypeAdapter

from skillflow.common.source_evidence import json_pointer, resolve_pointer
from skillflow.propagation.contracts.paths import semantics_pointer
from skillflow.graph.validation import checked_cfg
from skillflow.propagation.contracts.specs import RawAtomicOp, RawIRSemantics
from skillflow.propagation.contracts.task import build_task_target_index
from skillflow.propagation.contracts.references import target_key
from skillflow.propagation.contracts.uses import value_uses


def operation_target(instruction_id, raw_path):
    path = list(raw_path)
    slot = {"kind": "self"}
    if len(path) >= 2 and path[-2] == "uses":
        slot = {"kind": "input", "index": path[-1]}
        path = path[:-2]
    elif path and path[-1] == "output":
        slot = {"kind": "output"}
        path = path[:-1]
    return {"instruction_id": instruction_id, "operation_path": path, "slot": slot}


def target_id_for(instruction_id, raw_path):
    return target_key(operation_target(instruction_id, raw_path))


def resolve_demand_target(target, targets):
    key = target_key(target)
    if key not in targets:
        raise ValueError("demand target does not exist: " + key)
    return targets[key]


def _pointer_parts(pointer: str, root: Any) -> list[str | int]:
    """Decode a known pointer with container types, retaining numeric object keys."""
    if not pointer:
        return []
    result = []
    current = root
    for token in pointer.lstrip("/").split("/"):
        name = token.replace("~1", "/").replace("~0", "~")
        part = int(name) if isinstance(current, list) else name
        result.append(part)
        current = current[part]
    return result


def build_demand_target_index(cfg: dict[str, Any], raw_annotation: Any) -> dict[str, dict[str, Any]]:
    """Index validated graph/raw positions without mutating either material.

    Source evidence and annotation compilation identities are checked by the
    caller. This function additionally checks each raw transfer schema and its
    exact IR coverage, so compiled input cannot masquerade as a raw specification.
    """
    graph = checked_cfg(cfg)
    if hasattr(raw_annotation, "model_dump"):
        raw_annotation = raw_annotation.model_dump(mode="json")
    if not isinstance(raw_annotation, dict) or not isinstance(raw_annotation.get("ir_semantics"), dict):
        raise ValueError("demand targets require a raw annotation with ir_semantics")
    instructions = {ir["id"]: ir for block in graph["blocks"].values() for ir in block["instructions"]}
    if set(raw_annotation["ir_semantics"]) != set(instructions):
        raise ValueError("demand target specs must cover exactly the actual CFG instructions")
    raw_specs = {ir_id: RawIRSemantics.model_validate(spec).model_dump(mode="json")
                 for ir_id, spec in raw_annotation["ir_semantics"].items()}
    targets = build_task_target_index(graph)

    def input_metadata(ir_id):
        ir = instructions.get(ir_id, {})
        return {"input_count": len(ir.get("inputs", [])),
                "input_literals": {str(i): deepcopy(value.get("literal_value"))
                                   for i, value in enumerate(ir.get("inputs", [])) if value["type"] == "literal"},
                "resource_inputs": [i for i, value in enumerate(ir.get("inputs", []))
                                    if value["type"] == "external_resource"]}

    for entry in targets.values():
        path = _pointer_parts(entry["pointer"], graph)
        entry.update(domain="cfg", raw_path=path, value=deepcopy(resolve_pointer(graph, entry["pointer"])),
                     available_locals=[], supports_expression=False)
        ir_id = entry.get("instruction_id")
        entry.update(input_metadata(ir_id))
        # Conditions belong to the dispatch at the source block. No references
        # are inferred from free-form condition text or arbitrary metadata names.
        if len(path) >= 2 and path[0] == "edges":
            edge = graph["edges"][path[1]]
            source = graph["blocks"][edge["source_block_id"]]
            control = source["instructions"][-1] if source["instructions"] else None
            if control and control["opcode"] == "dispatch":
                entry["instruction_id"] = control["id"]
                entry.update(input_metadata(control["id"]))
                entry["supports_expression"] = len(path) == 2 or path[2:] == ["condition_text"]
        elif ir_id and instructions[ir_id]["opcode"] == "dispatch":
            entry["supports_expression"] = entry["kind"] in {"instruction", "input", "constraint"}

    adapter = TypeAdapter(RawAtomicOp)
    for ir_id in sorted(raw_specs):
        spec = raw_specs[ir_id]
        meta = input_metadata(ir_id)

        def add(path, kind, value, available, **extra):
            identity = target_id_for(ir_id, path)
            if identity in targets:
                raise ValueError("demand target identity collision")
            targets[identity] = {
                "domain": "transfer", "target": operation_target(ir_id, path), "kind": kind, "instruction_id": ir_id,
                "raw_path": list(path), "pointer": semantics_pointer(ir_id, *path),
                "value": deepcopy(value), "available_locals": sorted(available),
                "supports_expression": False, **meta, **deepcopy(extra),
            }
            return targets[identity]

        def segment(value, path, available, scope_path):
            add(path, "processing", value, available, segment_path=path, scope_path=scope_path)
            for event_index, event in enumerate(value["events"]):
                event_path = [*path, "events", event_index]
                add(event_path, "effect", event, available, segment_path=path, scope_path=scope_path)
                for op_index, operation in enumerate(event["atomic_ops"]):
                    op_path = [*event_path, "atomic_ops", op_index]
                    shared = {"operation_raw_path": op_path, "segment_path": path, "scope_path": scope_path}
                    typed = adapter.validate_python(operation)
                    def leaves(ref):
                        value = ref.model_dump(mode="json")
                        if value["kind"] == "alternatives":
                            return [item for child in ref.items for item in leaves(child)]
                        return [value]
                    add(op_path, "operation", operation, available,
                        supports_expression=operation["op"] in {"compute", "filter_items"},
                        declared_refs=[ref for use in value_uses(typed) for ref in leaves(use.value)], **shared)
                    for slot, use in enumerate(value_uses(typed)):
                        reference = use.value.model_dump(mode="json")
                        add([*op_path, "uses", slot], "input_use", reference, available,
                            slot=slot, ref=reference, role=use.role,
                            when=None if use.when is None else use.when.model_dump(mode="json"),
                            member_index=use.member_index, **shared)
                    if "output" in operation:
                        # Its own output may be used by an output target, but
                        # not to define an expression replacing this operation.
                        available.add(operation["output"])
                        add([*op_path, "output"], "local_output", operation["output"], available,
                            ref={"kind": "local", "name": operation["output"]}, **shared)
            for i, ref in enumerate(value["returns"]):
                add([*path, "returns", i], "segment_return", ref, available,
                    ref=ref, slot=i, segment_path=path, scope_path=scope_path)

        available: set[str] = set()
        for event_index, event in enumerate(spec["events"]):
            path = ["events", event_index]
            if event["kind"] == "processing":
                segment(event, path, available, None)
            else:
                add(path, "for_each", event, available, scope_path=path)
                add([*path, "collection"], "collection", event["collection"], available,
                    ref=event["collection"], scope_path=path)
                inner = {*available, event["item"]}
                add([*path, "item"], "element", event["item"], inner,
                    ref={"kind": "local", "name": event["item"]}, scope_path=path)
                for body_index, child in enumerate(event["body"]):
                    segment(child, [*path, "body", body_index], inner, path)
        for binding_index, binding in enumerate(spec["output_bindings"]):
            add(["output_bindings", binding_index], "output_binding", binding["value"], available,
                output_index=binding["output_index"], ref=binding["value"], scope_path=None)
    return targets
