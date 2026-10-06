"""Ordered effects keep occurrence identity in Chinese review reports."""

from skillflow.propagation.annotation.report import render_report


def test_report_keeps_repeated_effect_steps_and_their_evidence():
    profile = {"operator": ["llm"], "roles": ["transformer"],
               "effects": ["model_observe", "transform", "model_observe"],
               "evidences": [
                   {"field": "effects", "value": value, "effect_index": index,
                    "basis": "cfg", "ref_id": "g_1", "quote": "process",
                    "reason": f"阶段依据 {index}"}
                   for index, value in enumerate(["model_observe", "transform", "model_observe"])]}
    result = {"run_id": "ordered", "status": "complete", "reason": "部分顺序可计算",
              "notice": "不是证明", "graph_sha256": "graph", "profiles": {"ir": profile},
              "transfer_specs": {"ir": {"order": "partial", "precedence": [], "events": [], "output_bindings": []}}}
    material = {"cfg": {"blocks": {"b": {"block_name": "处理", "instructions": [{"id": "ir", "opcode": "process"}]}}}}
    text = render_report(result, material)
    assert "1. model_observe<br>2. transform<br>3. model_observe" in text
    assert "部分顺序；按因果约束保留候选安排" in text
    assert "步骤 1（索引 0）" in text and "步骤 3（索引 2）" in text
    assert "数组不是唯一执行次序" in text


def test_report_displays_operator_context_writes_and_non_nop_empty_effects():
    profiles = {
        "write": {"operator": ["agent_runtime"], "roles": ["sink"],
                  "effects": ["context_write", "context_write"], "evidences": []},
        "forward": {"operator": ["agent_runtime"], "roles": [], "effects": [], "evidences": []},
    }
    result = {"run_id": "context", "status": "complete", "reason": "离线示例",
              "notice": "非模型语义实测", "graph_sha256": "graph", "profiles": profiles}
    material = {"cfg": {"blocks": {"b": {"block_name": "上下文", "instructions": [
        {"id": "write", "opcode": "store"}, {"id": "forward", "opcode": "forward"},
    ]}}}}
    text = render_report(result, material)
    assert "执行主体（operator）" in text
    assert "1. context_write（上下文写入）<br>2. context_write（上下文写入）" in text
    assert "[]（无已记录效果；不等于空操作" in text
    assert "也不能推出入口与出口状态相同" in text
    assert "| forward | forward | agent_runtime | [] | []" in text


def test_report_displays_program_boundary_location_and_scope_without_free_risk_score():
    result = {"run_id": "boundaries", "status": "complete", "reason": "记录完整",
              "notice": "非风险判断", "graph_sha256": "graph", "profiles": {},
              "locations": {"endpoint": {"kind": "remote", "name": "公开发布",
                    "operand_refs": [], "access_scope": "public", "retention": None}},
              "sink_boundaries": [{"instruction_id": "send", "event_index": 2,
                    "op_index": 1, "body_event_index": 3, "scope": "row", "target": "endpoint",
                    "sink_type": "network_send", "exposure_level": 3}]}
    report = render_report(result, None)
    assert "send / 2.3 / 1" in report
    assert "network_send | 3 | public / None | row" in report
    assert "不表示敏感度、危险程度、任务必要性或 DOE 结论" in report
    assert "[Sink 边界](sink-boundaries.json)" in report
    assert "等级 0 不进入 Sink 清单" in report
