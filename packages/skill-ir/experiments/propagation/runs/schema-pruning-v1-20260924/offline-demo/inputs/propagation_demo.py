"""Offline propagation over explicitly authored, evidence-checked specifications.

No Skill, tool, remote model or embedded function is executed. The handwritten
annotation is an engineering example, not a model-quality measurement.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from skill_ir.data import DataRegistry, LiteralContent
from skill_ir.propagation import FlowLocation, FlowState, propagate
from skill_ir.security_profile.evidence import prepare_material
from skill_ir.security_profile.services import to_payload, validate_response
from skill_ir.source_evidence import _digest


def input_ref(index=0):
    return {"kind": "input", "index": index}


def local(name):
    return {"kind": "local", "name": name}


def literal(value):
    return {"kind": "literal", "value": value}


def instruction(ir_id, inputs=(), outputs=(), opcode=None):
    return {"id": ir_id if ir_id.startswith("ir_") else "ir_" + ir_id, "opcode": opcode or ir_id,
            "inputs": list(inputs),
            "outputs": [{"type": "result", "identifier": value} for value in outputs]}


def operand(identifier, kind="result"):
    return {"type": kind, "identifier": identifier}


def fixture_annotation(cfg, plans, location_shapes=None, unresolved=(), *, return_response=False):
    """Attach authentic CFG quotes to authored cases; never infer open opcodes.

    plans maps IR ID to (effect labels, operations per event, output aliases).
    An event's effect index may be None for a conservative computational step.
    """
    text = "# 离线传播示例\n\n所有动作与传播说明均由示例作者提供。此文不是模型实测。\n"
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    source = {"files": [{"path": "SKILL.md", "content": text, "sha256": sha}],
              "source_sha256": _digest([{"path": "SKILL.md", "sha256": sha}])}
    material = prepare_material(source, cfg)
    profiles, specs = {}, {}
    evidence_by_ir = {}
    for ir_id, index in material["instruction_index"].items():
        ir = material["cfg"]["blocks"][index["block_id"]]["instructions"][index["position"]]
        effects, operations, aliases = plans.get(ir_id, plans.get(ir_id.removeprefix("ir_"), ([], [], [])))
        basis = {"basis": "cfg", "ref_id": index["ref_id"], "quote": ir["opcode"],
                 "reason": "离线示例显式指定此关系；真实定位校验不等于语义正确性证明。"}
        evidence_by_ir[ir_id] = basis
        profile = {"operator": ["agent_runtime"], "roles": [], "effects": effects, "evidences": []}
        for field in ("operator", "roles", "effects"):
            for index_, value in enumerate(profile[field] or [None]):
                profile["evidences"].append({**basis, "field": field, "value": value,
                    "effect_index": index_ if field == "effects" and value is not None else None})
        profiles[ir_id] = profile
        specs[ir_id] = {
            "events": [{"effect_index": index_, "atomic_ops": [
                {**deepcopy(op), "evidences": [deepcopy(basis)]} for op in ops
            ]} for index_, ops in operations],
            "output_bindings": [{"output_index": index_, "value": deepcopy(ref),
                                 "evidences": [deepcopy(basis)]} for index_, ref in enumerate(aliases)],
        }
    first = next(iter(evidence_by_ir.values()))
    locations = {location_id: {"kind": kind, "name": name, "operand_refs": []}
                 for location_id, (kind, name) in (location_shapes or {}).items()}
    response = {"profiles": profiles, "transfer_specs": specs, "locations": locations,
                "unresolved": list(unresolved),
                "location_evidences": {location_id: [deepcopy(first)] for location_id in locations}}
    checked = validate_response(response, material)
    return material["cfg"], checked if return_response else to_payload(checked)


def demo_inputs():
    irs = [
        instruction("read", [operand("document", "context_key")], ["B"]),
        instruction("model_filter", [operand("B")], ["model_clean"]),
        instruction("local_filter", [operand("B")], ["local_clean"]),
        instruction("update", [operand("B")], ["updated"]),
        instruction("build", [operand("updated"), operand("local_clean")], ["combined"]),
        instruction("opaque", [operand("combined")], ["computed"]),
        instruction("copy", [operand("computed")], ["alias"]),
        instruction("save", [operand("alias")]),
        instruction("append", [operand("local_clean")]),
        instruction("delete"),
        instruction("network", [operand("local_clean")], ["response"]),
        instruction("return", [operand("response")], opcode="return"),
    ]
    cfg = {"entry_block_id": "source", "declared_context_keys": ["document"],
           "blocks": {
               "source": {"block_id": "source", "block_name": "读取来源", "data_source_kind": "context",
                          "instructions": [irs[0], instruction("source_end", opcode="dispatch")]},
               "main": {"block_id": "main", "block_name": "传播综合示例", "instructions": irs[1:]},
           }, "edges": [{"source_block_id": "source", "target_block_id": "main"}]}
    exclude = lambda name: {"op": "exclude_parts", "input": input_ref(), "paths": [["api_key"]], "output": name}
    deliver = lambda ref, target="model": {"op": "deliver", "inputs": [ref], "target": target}
    plans = {
        "read": (["context_read"], [(0, [{"op": "read", "location": "document", "output": "b"}])], [local("b")]),
        "model_filter": (["model_observe", "transform", "model_observe"], [
            (0, [deliver(input_ref())]), (1, [exclude("clean")]), (2, [deliver(local("clean"))]),
        ], [local("clean")]),
        "local_filter": (["transform", "model_observe"], [
            (0, [exclude("clean")]), (1, [deliver(local("clean"))]),
        ], [local("clean")]),
        "update": (["transform"], [(0, [{"op": "update_fields", "input": input_ref(),
            "updates": [{"path": ["api_key"], "value": literal("[redacted]")}], "output": "changed"}])], [local("changed")]),
        "build": (["transform"], [(0, [{"op": "build", "container": "object", "parts": [
            {"path": ["updated"], "value": input_ref()}, {"path": ["clean"], "value": input_ref(1)},
        ], "output": "built"}])], [local("built")]),
        "opaque": ([], [(None, [{"op": "compute", "inputs": [input_ref()],
                                  "dependencies": ["possible"], "output": "unknown"}])], [local("unknown")]),
        "copy": ([], [], [input_ref()]),
        "save": (["context_write"], [(0, [{"op": "write", "target": "cache", "mode": "replace", "input": input_ref()}])], []),
        "append": (["fs_write"], [(0, [{"op": "write", "target": "journal", "mode": "append", "input": input_ref()}])], []),
        "delete": (["context_write"], [(0, [{"op": "write", "target": "cache", "mode": "delete"}])], []),
        "network": (["net_send", "net_receive", "model_observe"], [
            (0, [deliver(input_ref(), "service")]),
            (1, [{"op": "receive", "location": "service", "inputs": [input_ref()], "output": "response"}]),
            (2, [deliver(local("response"))]),
        ], [local("response")]),
    }
    shapes = {"document": ("runtime_context", "document"), "model": ("model_context", "assistant"),
              "cache": ("runtime_context", "cache"), "journal": ("storage", "journal"),
              "service": ("remote", "example-service")}
    cfg, annotation = fixture_annotation(cfg, plans, shapes, return_response=True)
    # These labels are explicit author assumptions for this demonstration, not
    # the fixture's neutral defaults and not a model's semantic judgment.
    authored_profiles = {
        "ir_read": (["agent_runtime"], ["source"],
                    "运行时从 document 上下文取得原始整体 B，承担数据引入角色。"),
        "ir_source_end": (["agent_runtime"], [],
                          "运行时执行控制转移；没有在此动作中引入、交付或变换数据。"),
        "ir_model_filter": (["llm"], ["sink", "transformer"],
                            "本示范规定由模型先读取原始 B，再删除 api_key，并观察清理结果；模型既接收内容也参与变换。"),
        "ir_local_filter": (["agent_runtime", "llm"], ["transformer", "sink"],
                            "本示范规定运行时先在本地删除 api_key，再将清理结果交给模型；执行主体列表自身不表达时序。"),
        "ir_update": (["agent_runtime"], ["transformer"],
                      "运行时以明确字面值覆盖 api_key 字段，其余原整体内容保留；未声明模型参与处理。"),
        "ir_build": (["agent_runtime"], ["transformer"],
                     "运行时将 updated 和 local_clean 组成一个新对象，不引入新的外部来源。"),
        "ir_opaque": (["agent_runtime"], [],
                      "运行时登记未解释的结果关系；仅有可能依赖不能证明另有数据引入、边界交付或实际变换动作。"),
        "ir_copy": (["agent_runtime"], [],
                    "运行时登记已有值的结果别名，不生成新数据，也没有额外的引入、边界交付或变换。"),
        "ir_save": (["agent_runtime"], ["sink"],
                    "运行时将已有数据原样写入 cache 上下文边界，保存本身不改变内容。"),
        "ir_append": (["agent_runtime"], ["sink"],
                      "运行时把清理结果追加到 journal 文件边界；追加状态由传递规格记录。"),
        "ir_delete": (["agent_runtime"], [],
                      "运行时只删除 cache 绑定，不读取或交付原内容；不能因发生状态修改就补贴内容变换角色。"),
        "ir_network": (["agent_runtime", "tool", "llm"], ["sink", "source"],
                       "运行时调用网络工具发送清理请求并取得外部响应，随后模型读取响应；该动作同时涉及交付与引入。"),
        "ir_return": (["agent_runtime"], [],
                      "运行时结束流程并返回已有 response；未声明直接向用户展示，不补造用户输出。"),
    }
    phase_reasons = {
        "ir_read": ["从 document 取得完整候选 B；尚未选取或删除字段。"],
        "ir_model_filter": ["模型首先观察原始 B，此时 api_key 尚未删除。",
                            "模型在观察 B 之后删除 api_key，产生不同数据版本 clean。",
                            "模型随后观察 clean；这次观察不会撤销先前对 B 的观察。"],
        "ir_local_filter": ["运行时首先在本地删除 B.api_key，产生 clean。",
                            "仅将本地清理后的 clean 提供给模型，不把原始 B 作为本次观察输入。"],
        "ir_update": ["将 B.api_key 覆盖为 [redacted]，产生字段覆盖结果。"],
        "ir_build": ["以 updated 和 local_clean 为两个组成部分构造新对象。"],
        "ir_save": ["将 alias 原样写入运行时 cache，供后续状态读取。"],
        "ir_append": ["向 journal 追加 local_clean；旧文件内容和追加参数均保留派生关系。"],
        "ir_delete": ["只移除运行时 cache 绑定，不以原内容作为读取或观察输入。"],
        "ir_network": ["网络工具先把 local_clean 请求发送至 example-service。",
                       "网络工具随后取得 response；请求的可能依赖不等于响应含请求明文。",
                       "工具响应回传后进入模型上下文，模型此时观察 response。"],
    }
    for ir_id, (operators, roles, reason) in authored_profiles.items():
        profile = annotation["profiles"][ir_id]
        profile["operator"], profile["roles"] = operators, roles
        basis = {key: profile["evidences"][0][key] for key in ("basis", "ref_id", "quote")}
        profile["evidences"] = []
        for field in ("operator", "roles", "effects"):
            for index_, value in enumerate(profile[field] or [None]):
                detail = phase_reasons[ir_id][index_] if field == "effects" and value is not None else reason
                profile["evidences"].append({**basis, "field": field, "value": value,
                    "effect_index": index_ if field == "effects" and value is not None else None,
                    "reason": "人工编写的综合示例规格，并非模型标注或语义证明。" + detail})
    # Recheck the amended contract and authentic quotes against the unchanged
    # fixture input. This validates evidence identity, not the author's semantics.
    source_text = "# 离线传播示例\n\n所有动作与传播说明均由示例作者提供。此文不是模型实测。\n"
    source_sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    source = {"files": [{"path": "SKILL.md", "content": source_text, "sha256": source_sha}],
              "source_sha256": _digest([{"path": "SKILL.md", "sha256": source_sha}])}
    annotation = validate_response(annotation, prepare_material(source, cfg))
    data = DataRegistry("propagation-demo")
    document = data.register_source("initial-document", acquired_from="runtime_context:document")
    data.register_part(document.id, ["api_key"])
    data.register_part(document.id, ["owner"])
    journal = data.register_source("initial-journal", acquired_from="storage:journal", content=LiteralContent(value=[]))
    state = FlowState.from_mapping({
        FlowLocation(kind="runtime_context", name="document"): frozenset([document.id]),
        FlowLocation(kind="storage", name="journal"): frozenset([journal.id]),
    })
    return cfg, annotation, data, state


def build_demo():
    cfg, annotation, data, state = demo_inputs()
    result = propagate(cfg, to_payload(annotation), initial_registry=data, initial_state=state)
    assert result.status == "complete", result.diagnostics
    result.records.validate(require_complete=True)
    return result


if __name__ == "__main__":
    result = build_demo()
    print(json.dumps({"status": result.status, "coverage": result.coverage,
                      "diagnostics": result.diagnostics, "snapshot": result.records.to_dict()},
                     ensure_ascii=True, indent=2))
