"""Offline optional request construction; no model, tool, or Skill execution."""
from __future__ import annotations

import json

from skillflow.common.inputs.snapshot import _describe
from skillflow.propagation import propagate
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.annotation.services import to_payload
from examples.propagation.authored_task import authored_baseline, unseeded_realizations


def example():
    text = ("# 人工可选参数示例\n将 query 原值与存在时的 cutoff 原值构成请求，"
            "交给部署未说明的工具，并取得该请求的返回。存在旗标不是请求参数。\n")
    _, source, metadata = _describe({"original_path": "authored:optional-request-demo",
        "storage": "authored", "root_name": "optional-request-demo", "archive_sha256": None},
        [("SKILL.md", text.encode())])
    inputs = [{"type": "literal", "literal_value": value} for value in ("weather", "2026-01-01", False)]
    call = {"id": "ir_request", "opcode": "construct optional request and acquire tool response",
            "inputs": inputs, "outputs": [{"type": "result", "identifier": "response"}]}
    cfg = {"entry_block_id": "entry", "blocks": {"entry": {
        "block_id": "entry", "block_name": "构造与获取", "instructions": [call,
            {"id": "ir_return", "opcode": "return", "inputs": [{"type": "result", "identifier": "response"}]}]}},
        "edges": []}
    task = authored_baseline(source, purpose="构造可选参数请求并取得对应工具返回。",
        requirements=["query 与存在时的 cutoff 保持原值，cutoff 缺失时省略，存在旗标不成为请求参数。", "获取同一请求的工具返回。"])
    material = prepare_material(source, cfg, task_baseline=task)

    def evidence(ir_id):
        return {"target": {"instruction_id": ir_id, "path": []},
                "reason": "人工离线关系示例；可选字段保持原值，控制不成为载荷，未断言网络。"}

    def semantics(ir_id, has_effect):
        return {"operator": ["agent_runtime"],
                "operator_evidences": [{**evidence(ir_id), "value": "agent_runtime"}],
                **({} if has_effect else {"empty_effect_evidences": [evidence(ir_id)]}), "sensitivity": []}

    ref = lambda index: {"kind": "input", "index": index}
    request = {"kind": "local", "name": "request"}
    ops = [
        {"op": "build", "container": "object", "parts": [
            {"path": ["query"], "value": ref(0)},
            {"path": ["cutoff"], "value": ref(1), "when": ref(2)},
        ], "output": "request", "evidences": [evidence("ir_request")]},
        {"op": "deliver", "inputs": [request], "target": "search", "evidences": [evidence("ir_request")]},
        {"op": "receive", "location": "search", "inputs": [request], "output": "response",
         "evidences": [evidence("ir_request")]},
    ]
    raw = {"outcome": "completed", "locations": {"search": {"kind": "tool", "name": "search", "operand_refs": [],
                                    "access_scope": "recipient", "retention": None}},
        "location_evidences": {"search": [evidence("ir_request")]},
        "ir_semantics": {"ir_request": {**semantics("ir_request", True), "order": "fixed", "events": [{"kind": "processing",
            "mode": "default", "returns": [], "evidences": [evidence("ir_request")], "events": [
                {"effect": "transform", "evidences": [evidence("ir_request")], "atomic_ops": [ops[0]]},
                {"effect": None, "evidences": [], "atomic_ops": ops[1:]},
            ]}], "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "response"},
                                        "evidences": [evidence("ir_request")]}]},
            "ir_return": {**semantics("ir_return", False), "order": "fixed", "events": [], "output_bindings": []}}}
    span = {"file": "skill/SKILL.md", "start_line": 2, "end_line": 2,
            "reason": "The example describes optional fields and tool acquisition."}
    raw.update(task_revision_id=task.task_sha256, realizations=unseeded_realizations(task), demands=[], expressions=[])
    raw, compiled, mapping = compile_response(raw, material)
    annotation = to_payload(compiled)
    solved = propagate(material["cfg"], annotation)
    if solved.status != "complete":
        raise ValueError(solved.diagnostics)
    return materials_from_result(solved, material=material, source_metadata=metadata,
                                 raw_annotation=raw, compiled_annotation=compiled, mapping=mapping)


if __name__ == "__main__":
    print(json.dumps(example().records, ensure_ascii=False, indent=2, allow_nan=False))
