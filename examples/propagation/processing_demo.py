"""Authored filter/member/processing example; no model or Skill execution."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

from skillflow.common.inputs.snapshot import _describe
from skillflow.propagation import propagate
from skillflow.propagation.handoff import build_doe_input
from skillflow.propagation.runner import save_propagation_run
from skillflow.propagation.material import prepare_material
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.annotation.services import to_payload


def example():
    text = ("# 人工构造的离线示范\n读取 records 文件。模型按 enabled 条件筛选，成员内容不变。\n"
            "对每个选中元素，原样取 recipient 与 summary，作为同一 HTTPS 请求的两个参数发送到远端。\n")
    _, source, metadata = _describe({"original_path": "authored:processing-demo", "storage": "authored",
        "root_name": "processing-demo", "archive_sha256": None}, [("SKILL.md", text.encode())])
    def ir(name, opcode, inputs=(), outputs=()):
        return {"id": name, "opcode": opcode, "inputs": list(inputs),
                "outputs": [{"type": "result", "identifier": output} for output in outputs]}
    cfg = {"entry_block_id": "load", "blocks": {
        "load": {"block_id": "load", "block_name": "读取", "data_source_kind": "external", "instructions": [
            ir("ir_read", "read records", [{"type": "external_resource", "identifier": "records"}], ["records"]),
            ir("ir_dispatch", "dispatch")]},
        "use": {"block_id": "use", "block_name": "筛选及逐元素交付", "instructions": [
            ir("ir_filter", "filter enabled records", [{"type": "result", "identifier": "records"}], ["selected"]),
            ir("ir_send", "send recipient and summary through HTTPS for each record", [{"type": "result", "identifier": "selected"}]),
            ir("ir_return", "return")]}}, "edges": [{"source_block_id": "load", "target_block_id": "use"}]}
    material = prepare_material(source, cfg)
    instructions = {ir["id"]: ir for block in material["cfg"]["blocks"].values() for ir in block["instructions"]}
    def evidence(ir_id):
        return {"basis": "cfg", "ref_id": material["instruction_index"][ir_id]["ref_id"],
                "quote": instructions[ir_id]["opcode"], "reason": "作者明确指定的离线示例；并非模型判断或真实执行。"}
    def op(ir_id, kind, **values):
        return {"op": kind, **values, "evidences": [evidence(ir_id)]}
    def segment(ir_id, events, mode="default"):
        return {"kind": "processing", "mode": mode, "events": events, "returns": [], "evidences": [evidence(ir_id)]}
    local = lambda name: {"kind": "local", "name": name}
    input0 = {"kind": "input", "index": 0}
    profiles, specs = {}, {}
    for name in instructions:
        effects = {"ir_read": ["fs_read"], "ir_filter": ["transform"], "ir_send": ["transform", "net_send"]}.get(name, [])
        profile = {"operator": ["llm"] if name == "ir_filter" else ["agent_runtime"],
                   "roles": [], "effects": effects, "evidences": []}
        for field in ("operator", "roles", "effects"):
            for index, value in enumerate(profile[field] or [None]):
                profile["evidences"].append({**evidence(name), "field": field, "value": value,
                    "effect_index": index if field == "effects" and value is not None else None})
        profiles[name] = profile
        specs[name] = {"order": "fixed", "events": [], "output_bindings": []}
    specs["ir_read"]["events"] = [segment("ir_read", [{"effect_index": 0,
        "atomic_ops": [op("ir_read", "read", location="records", output="all")]}])]
    specs["ir_filter"]["events"] = [segment("ir_filter", [{"effect_index": 0,
        "atomic_ops": [op("ir_filter", "filter_items", input=input0, predicate="enabled", output="selected")]}], "model")]
    for name, output in (("ir_read", "all"), ("ir_filter", "selected")):
        specs[name]["output_bindings"] = [{"output_index": 0, "value": local(output), "evidences": [evidence(name)]}]
    specs["ir_send"]["events"] = [{"kind": "for_each", "collection": input0, "item": "record",
        "evidences": [evidence("ir_send")], "body": [segment("ir_send", [
            {"effect_index": 0, "atomic_ops": [op("ir_send", "select_part", input=local("record"), path=[field], output=field)
                                               for field in ("recipient", "summary")]},
            {"effect_index": 1, "atomic_ops": [op("ir_send", "deliver", inputs=[local("recipient"), local("summary")], target="notify")]}])]}]
    raw = {"outcome": "completed", "profiles": profiles, "transfer_specs": specs,
           "locations": {"records": {"kind": "storage", "name": "records", "operand_refs": [],
                                     "access_scope": "task", "retention": "persistent"},
                         "notify": {"kind": "remote", "name": "notify", "operand_refs": [],
                                    "access_scope": "recipient", "retention": None}},
           "location_evidences": {"records": [evidence("ir_read")], "notify": [evidence("ir_send")]}}
    compilation = compile_response(raw, material)
    annotation = to_payload(compilation[1])
    solved = propagate(material["cfg"], annotation)
    if solved.status != "complete":
        raise ValueError(solved.diagnostics)
    return material, metadata, compilation, annotation, solved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    material, metadata, compilation, annotation, solved = example()
    if args.output:
        result = save_propagation_run(args.output, material=material, source_metadata=metadata,
            annotation=annotation, location_evidences=compilation[1]["location_evidences"], solved=solved,
            raw_annotation=compilation[0], compilation_map=compilation[2],
            provenance={"kind": "hand_authored_specification", "notice": "人工规格示例，无模型调用。"})
    else:
        result = build_doe_input(material["source"], material["cfg"], annotation, solved,
                                 source_metadata=metadata, execution_model=material["execution_model"])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
