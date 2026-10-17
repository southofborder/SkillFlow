"""Offline propagation over explicitly authored, evidence-checked specifications.

No Skill, tool, remote model or embedded function is executed. The handwritten
annotation is an engineering example, not a model-quality measurement.
"""
from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path

from skillflow.propagation.data import DataRegistry
from skillflow.propagation.data import LiteralContent
from skillflow.common.inputs.snapshot import _describe
from skillflow.propagation import FlowLocation
from skillflow.propagation import FlowState
from skillflow.propagation import propagate
from skillflow.propagation.contracts.boundaries import derive_sink_boundaries
from skillflow.propagation.material import prepare_material
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.annotation.services import validate_compiled_response
from skillflow.propagation.contracts.task import task_reference
from examples.propagation.authored_task import authored_baseline, unseeded_realizations


NOTICE = "这是人工编写并核验证据的传播规格示例，不是模型实测；未调用 LLM，未执行 Skill 或工具。"


def demo_source():
    text = "# 离线传播示例\n\n所有动作与传播说明均由示例作者提供。此文不是模型实测。\n"
    identity = {"original_path": "authored:propagation-demo", "storage": "authored",
                "root_name": "propagation-demo", "archive_sha256": None}
    _, source, metadata = _describe(identity, [("SKILL.md", text.encode("utf-8"))])
    return source, metadata


def demo_task(source):
    return authored_baseline(source, purpose="演示作者显式声明的传播关系。", requirements=["保持作者声明的教学传播关系；本示例不建立真实任务必要性结论。"])


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


def fixture_annotation(cfg, plans, location_shapes=None, partial_irs=(), *, return_response=False):
    """Attach authentic CFG quotes to authored cases; never infer open opcodes.

    plans maps IR ID to (effect labels, operations per event, output aliases).
    The author shorthand uses an optional label-list position; the emitted contract has only event-local effects.
    """
    source, _ = demo_source()
    task = demo_task(source)
    material = prepare_material(source, cfg, task_baseline=task)
    specs = {}
    evidence_by_ir = {}
    from skillflow.propagation.contracts.references import cfg_instructions
    for ir_id, ir in cfg_instructions(material["cfg"]).items():
        effects, operations, aliases = plans.get(ir_id, plans.get(ir_id.removeprefix("ir_"), ([], [], [])))
        basis = {"target": {"instruction_id": ir_id, "path": []},
                 "reason": "离线示例显式指定此关系；真实定位校验不等于语义正确性证明。"}
        evidence_by_ir[ir_id] = basis
        specs[ir_id] = {
            "operator": ["agent_runtime"],
            "operator_evidences": [{**deepcopy(basis), "value": "agent_runtime"}],
            **({} if effects else {"empty_effect_evidences": [deepcopy(basis)]}),
            "sensitivity": [],
            "order": "partial" if ir_id in partial_irs else "fixed", "precedence": [],
            "events": [{"effect": effects[index_] if index_ is not None else None,
                        "evidences": [deepcopy(basis)] if index_ is not None else [], "atomic_ops": [
                {**deepcopy(op), "evidences": [deepcopy(basis)]} for op in ops
            ]} for index_, ops in operations],
            "output_bindings": [{"output_index": index_, "value": deepcopy(ref),
                                 "evidences": [deepcopy(basis)]} for index_, ref in enumerate(aliases)],
        }
    first = next(iter(evidence_by_ir.values()))
    # These are explicit authored fixture assumptions, not a production
    # migration of old responses. Additional attrs can be supplied in shapes.
    locations = {location_id: {"kind": shape[0], "name": shape[1], "operand_refs": [],
                    "access_scope": shape[2] if len(shape) > 2 else (
                        "task" if shape[0] in {"storage", "runtime_context"} else "recipient"),
                    "retention": shape[3] if len(shape) > 3 else (
                        "persistent" if shape[0] == "storage" else "task" if shape[0] == "runtime_context" else None)}
                 for location_id, shape in (location_shapes or {}).items()}
    response = {"outcome": "completed", "ir_semantics": specs, "locations": locations,
                "location_evidences": {location_id: [deepcopy(first)] for location_id in locations}}
    task_evidence = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                     "reason": "This is an explicitly authored engineering example, not a semantic assessment."}
    response["task_ref"] = task_reference(task)
    response["realizations"] = unseeded_realizations(task)
    response["demands"], response["expressions"] = [], []
    response["sink_boundaries"] = [row.model_dump(mode="json") for row in
        derive_sink_boundaries(locations, specs)]
    checked = validate_compiled_response(response, material)
    return material["cfg"], checked if return_response else to_payload(checked)


def demo_inputs(*, with_compilation=False):
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
    authored_operators = {
        "ir_read": (["agent_runtime"],
                    "运行时从 document 上下文取得原始整体 B，承担数据引入角色。"),
        "ir_source_end": (["agent_runtime"],
                          "运行时执行控制转移；没有在此动作中引入、交付或变换数据。"),
        "ir_model_filter": (["llm"],
                            "本示范规定由模型先读取原始 B，再删除 api_key；同段产物不作为一次新的外部输入观察。"),
        "ir_local_filter": (["agent_runtime", "llm"],
                            "本示范规定运行时先在本地删除 api_key，再将清理结果交给模型；执行主体列表自身不表达时序。"),
        "ir_update": (["agent_runtime"],
                      "运行时以明确字面值覆盖 api_key 字段，其余原整体内容保留；未声明模型参与处理。"),
        "ir_build": (["agent_runtime"],
                     "运行时将 updated 和 local_clean 组成一个新对象，不引入新的外部来源。"),
        "ir_opaque": (["agent_runtime"],
                      "运行时登记未解释的结果关系；仅有可能依赖不能证明另有数据引入、边界交付或实际变换动作。"),
        "ir_copy": (["agent_runtime"],
                    "运行时登记已有值的结果别名，不生成新数据，也没有额外的引入、边界交付或变换。"),
        "ir_save": (["agent_runtime"],
                    "运行时将已有数据原样写入 cache 上下文边界，保存本身不改变内容。"),
        "ir_append": (["agent_runtime"],
                      "运行时把清理结果追加到 journal 文件边界；追加状态由传递规格记录。"),
        "ir_delete": (["agent_runtime"],
                      "运行时只删除 cache 绑定，不读取或交付原内容；不能因发生状态修改就补贴内容变换角色。"),
        "ir_network": (["agent_runtime", "tool", "llm"],
                       "运行时调用网络工具发送清理请求并取得外部响应，随后模型读取响应；该动作同时涉及交付与引入。"),
        "ir_return": (["agent_runtime"],
                      "运行时结束流程并返回已有 response；未声明直接向用户展示，不补造用户输出。"),
    }
    phase_reasons = {
        "ir_read": ["从 document 取得完整候选 B；尚未选取或删除字段。"],
        "ir_model_filter": ["模型首先观察原始 B，此时 api_key 尚未删除。",
                            "模型在观察 B 之后删除 api_key，产生不同数据版本 clean。",
                            "旧作者草图的末尾观察被新处理段语义移除：clean 是本次模型计算的中间产物。"],
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
    for ir_id, (operators, reason) in authored_operators.items():
        spec = annotation["ir_semantics"][ir_id]
        spec["operator"] = operators
        ref = spec["operator_evidences"][0]["target"]
        spec["operator_evidences"] = [{"target": ref, "value": value, "reason": reason}
                                      for value in operators]
        for index, event in enumerate(spec["events"]):
            if event["effect"] is not None:
                event["evidences"] = [{"target": ref, "reason": phase_reasons[ir_id][index]}]
    # Recheck the amended contract and authentic quotes against the unchanged
    # fixture input. This validates evidence identity, not the author's semantics.
    source, metadata = demo_source()
    annotation = validate_compiled_response(annotation, prepare_material(source, cfg, task_baseline=demo_task(source)))
    # Author the current processing protocol for this fixed example. The helper
    # above remains a compiled-spec fixture for interpreter-only regression tests.
    # This is not a migration path for model responses or saved runs.
    from skillflow.propagation.annotation.services import compile_response
    raw = deepcopy(annotation)
    raw.pop('sink_boundaries')  # Compiler-derived, never part of an authored raw response.
    raw['task_revision_id'] = raw.pop('task_ref')['task_sha256']
    raw['demands'], raw['expressions'] = [], []
    for ir_id, spec in raw['ir_semantics'].items():
        spec.pop('precedence')
        kept, returns = [], []
        basis = {key: spec['operator_evidences'][0][key] for key in ('target', 'reason')}
        for event in spec['events']:
            if event['effect'] == 'model_observe':
                if ir_id == 'ir_model_filter' and event['atomic_ops'][0]['inputs'] == [input_ref()]:
                    continue  # Implied by the explicitly model-executed segment.
                returns.extend(event['atomic_ops'][0]['inputs'])
            else:
                kept.append(event)
        if any(e['effect'] is not None for e in kept):
            spec.pop('empty_effect_evidences', None)
        else:
            spec['empty_effect_evidences'] = [deepcopy(basis)]
        spec['events'] = ([{'kind': 'processing',
            'mode': 'model' if ir_id == 'ir_model_filter' else 'local',
            'events': kept, 'returns': [] if ir_id == 'ir_model_filter' else returns,
            'evidences': [basis]}] if kept else [])
    compilation = compile_response(raw, prepare_material(source, cfg, task_baseline=demo_task(source)))
    annotation = compilation[1]
    data = DataRegistry("propagation-demo")
    document = data.register_source("initial-document", acquired_from="runtime_context:document")
    data.register_part(document.id, ["api_key"])
    data.register_part(document.id, ["owner"])
    journal = data.register_source("initial-journal", acquired_from="storage:journal", content=LiteralContent(value=[]))
    state = FlowState.from_mapping({
        FlowLocation(kind="runtime_context", name="document"): frozenset([document.id]),
        FlowLocation(kind="storage", name="journal"): frozenset([journal.id]),
    })
    values = (source, metadata, cfg, annotation, data, state)
    return (*values, compilation) if with_compilation else values


def build_demo():
    _, _, cfg, annotation, data, state = demo_inputs()
    result = propagate(cfg, to_payload(annotation), initial_registry=data, initial_state=state)
    assert result.status == "complete", result.diagnostics
    result.records.validate(require_complete=True)
    return result


def demo_materials():
    from skillflow.propagation.loading import materials_from_result
    source, metadata, cfg, response, data, state, compilation = demo_inputs(with_compilation=True)
    solved = propagate(cfg, to_payload(response), initial_registry=data, initial_state=state)
    return materials_from_result(solved, material=prepare_material(source, cfg, task_baseline=demo_task(source)), source_metadata=metadata,
        raw_annotation=compilation[0], compiled_annotation=compilation[1], mapping=compilation[2])


def save_demo(output):
    """Write an authored display example, not a model-backed propagation run."""
    from skillflow.common.artifacts import ArtifactWriter
    from skillflow.propagation.report import write_reports
    facts = demo_materials()
    directory = Path(output)
    if directory.exists() and any(directory.iterdir()):
        raise ValueError('Example output must be a new or empty directory')
    writer = ArtifactWriter(())
    for name in ('data', 'records', 'sinks'):
        writer.json(directory / (name + '.json'), getattr(facts, name))
    writer.text(directory / 'NOTICE.txt', NOTICE + '\nAuthored display files; not a committed propagation run.\n')
    write_reports(directory, facts, writer)
    return facts


def main(argv=None):
    parser = argparse.ArgumentParser(description=NOTICE)
    parser.add_argument('--output', type=Path, help='Save authored fact components and reports; no model-run manifest')
    parser.add_argument('--records-only', action='store_true', help='Print only the IR record map')
    args = parser.parse_args(argv)
    facts = save_demo(args.output) if args.output is not None else demo_materials()
    print(json.dumps(facts.records if args.records_only else {
        'status': facts.status, 'data_count': len(facts.data), 'record_count': len(facts.records),
        'sink_count': len(facts.sinks)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
