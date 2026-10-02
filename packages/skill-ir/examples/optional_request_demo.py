"""Offline optional request construction; no model, tool, or Skill execution."""
from __future__ import annotations

import json

from skill_ir.inputs.snapshot import _describe
from skill_ir.propagation import propagate
from skill_ir.runtime_contract import execution_model
from skill_ir.propagation.handoff import build_doe_input
from skill_ir.security_profile.evidence import prepare_material
from skill_ir.security_profile.services import compile_response, to_payload


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
    material = prepare_material(source, cfg)

    def evidence(ir_id):
        return {"basis": "cfg", "ref_id": material["instruction_index"][ir_id]["ref_id"],
                "quote": call["opcode"] if ir_id == "ir_request" else "return",
                "reason": "人工离线关系示例；可选字段保持原值，控制不成为载荷，未断言网络。"}

    def profile(ir_id, effects):
        result = {"operator": ["agent_runtime"], "roles": [], "effects": effects, "evidences": []}
        for field in ("operator", "roles", "effects"):
            for index, value in enumerate(result[field] or [None]):
                result["evidences"].append({"field": field, "value": value, **evidence(ir_id),
                    "effect_index": index if field == "effects" and value is not None else None})
        return result

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
    raw = {"outcome": "completed", "profiles": {"ir_request": profile("ir_request", ["transform"]),
        "ir_return": profile("ir_return", [])},
        "locations": {"search": {"kind": "tool", "name": "search", "operand_refs": [],
                                    "access_scope": "recipient", "retention": None}},
        "location_evidences": {"search": [evidence("ir_request")]},
        "transfer_specs": {"ir_request": {"order": "fixed", "events": [{"kind": "processing",
            "mode": "default", "returns": [], "evidences": [evidence("ir_request")], "events": [
                {"effect_index": 0, "atomic_ops": [ops[0]]},
                {"effect_index": None, "atomic_ops": ops[1:]},
            ]}], "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "response"},
                                        "evidences": [evidence("ir_request")]}]},
            "ir_return": {"order": "fixed", "events": [], "output_bindings": []}}}
    _, compiled, _ = compile_response(raw, material)
    annotation = to_payload(compiled)
    solved = propagate(material["cfg"], annotation)
    if solved.status != "complete":
        raise ValueError(solved.diagnostics)
    return build_doe_input(source, material["cfg"], annotation, solved,
                           source_metadata=metadata, execution_model=execution_model())


if __name__ == "__main__":
    print(json.dumps(example(), ensure_ascii=False, indent=2, allow_nan=False))
