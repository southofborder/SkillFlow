"""Authored filter/member/processing example; no model or Skill execution."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

from skillflow.common.inputs.snapshot import _describe
from skillflow.propagation import propagate
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.annotation.services import to_payload
from examples.propagation.authored_task import authored_baseline, unseeded_realizations


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
    task = authored_baseline(source, purpose="筛选记录并向远端逐元素交付。",
        requirements=["按 enabled 条件筛选且保持所选元素内容不变。", "同一请求中的 recipient 与 summary 来自同一个选中元素并保持原值。"])
    material = prepare_material(source, cfg, task_baseline=task)
    instructions = {ir["id"]: ir for block in material["cfg"]["blocks"].values() for ir in block["instructions"]}
    def evidence(ir_id):
        return {"target": {"instruction_id": ir_id, "path": []},
                "reason": "作者明确指定的离线示例；并非模型判断或真实执行。"}
    def op(ir_id, kind, **values):
        return {"op": kind, **values, "evidences": [evidence(ir_id)]}
    def segment(ir_id, events, mode="default"):
        return {"kind": "processing", "mode": mode, "events": events, "returns": [], "evidences": [evidence(ir_id)]}
    local = lambda name: {"kind": "local", "name": name}
    input0 = {"kind": "input", "index": 0}
    specs = {}
    for name in instructions:
        effects = {"ir_read": ["fs_read"], "ir_filter": ["transform"], "ir_send": ["transform", "net_send"]}.get(name, [])
        operators = ["llm"] if name == "ir_filter" else ["agent_runtime"]
        specs[name] = {"operator": operators,
                      "operator_evidences": [{**evidence(name), "value": value} for value in operators],
                      **({} if effects else {"empty_effect_evidences": [evidence(name)]}),
                      "order": "fixed", "events": [], "output_bindings": [], "sensitivity": []}
    specs["ir_read"]["events"] = [segment("ir_read", [{"effect": "fs_read", "evidences": [evidence("ir_read")],
        "atomic_ops": [op("ir_read", "read", location="records", output="all")]}])]
    specs["ir_filter"]["events"] = [segment("ir_filter", [{"effect": "transform", "evidences": [evidence("ir_filter")],
        "atomic_ops": [op("ir_filter", "filter_items", input=input0, predicate="enabled", output="selected")]}], "model")]
    for name, output in (("ir_read", "all"), ("ir_filter", "selected")):
        specs[name]["output_bindings"] = [{"output_index": 0, "value": local(output), "evidences": [evidence(name)]}]
    specs["ir_send"]["events"] = [{"kind": "for_each", "collection": input0, "item": "record",
        "evidences": [evidence("ir_send")], "sensitivity": [], "body": [segment("ir_send", [
            {"effect": "transform", "evidences": [evidence("ir_send")], "atomic_ops": [op("ir_send", "select_part", input=local("record"), path=[field], output=field)
                                               for field in ("recipient", "summary")]},
            {"effect": "net_send", "evidences": [evidence("ir_send")], "atomic_ops": [op("ir_send", "deliver", inputs=[local("recipient"), local("summary")], target="notify")]}])]}]
    raw = {"outcome": "completed", "ir_semantics": specs,
           "locations": {"records": {"kind": "storage", "name": "records", "operand_refs": [],
                                     "access_scope": "task", "retention": "persistent"},
                         "notify": {"kind": "remote", "name": "notify", "operand_refs": [],
                                    "access_scope": "recipient", "retention": None}},
           "location_evidences": {"records": [evidence("ir_read")], "notify": [evidence("ir_send")]}}
    span = {"file": "skill/SKILL.md", "start_line": 2, "end_line": 3,
            "reason": "The authored example states the filtering and paired delivery behavior."}
    raw.update(task_revision_id=task.task_sha256, realizations=unseeded_realizations(task), demands=[], expressions=[])
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
    facts = materials_from_result(solved, material=material, source_metadata=metadata,
        raw_annotation=compilation[0], compiled_annotation=compilation[1], mapping=compilation[2])
    if args.output:
        from skillflow.common.artifacts import ArtifactWriter
        from skillflow.propagation.report import write_reports
        if args.output.exists() and any(args.output.iterdir()):
            raise ValueError('Example output must be new or empty')
        writer = ArtifactWriter(())
        for name in ('data', 'records', 'sinks'):
            writer.json(args.output / (name + '.json'), getattr(facts, name))
        write_reports(args.output, facts, writer)
    print(json.dumps(facts.records, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
