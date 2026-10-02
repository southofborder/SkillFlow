"""Attach assistant review to the frozen v3 experiment, without changing results."""
from pathlib import Path
import hashlib
import json
from collections import Counter

from skill_ir.llm.config import load_environment
from skill_ir.backtrace.runner import verify_run
from skill_ir.feedback.policy import decide

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v3-seven-20260918"
report = json.loads((RUN / "report.json").read_text(encoding="utf-8"))
replayed = json.loads((RUN / "replay/report.json").read_text(encoding="utf-8"))
manifest = verify_run(RUN, live=True)
comparisons = {key: report[key] == replayed[key] for key in (
    "stages", "conversion", "evaluation", "calls", "execution_status",
    "recorded_logical_calls", "recorded_execution_calls", "audit_execution_retries",
    "http_attempts", "case_selections",
)}
assert all(comparisons.values())

names = {
    "c01": "F01 原图（013，第1轮）",
    "c02": "F01 反例：archive 多传密钥",
    "c03": "F01 反例：失败出口缺少状态追加",
    "c04": "F01 反例：重试成功返回首次结果",
    "c05": "F01 反例：新增两秒等待",
    "c06": "001 原图（暂停批次第0轮）",
    "c07": "010 原图（暂停批次第0轮）",
}
judgments = {
    "c01": "执行错误：完整响应末尾多出孤立 Markdown 围栏，未删改后接受；不能判定原图通过。",
    "c02": "有效命中：明确多传 FAST_KEY，并指出调用与禁传声明冲突。",
    "c03": "执行错误：9 个核对项缺少必填 unknown_cause。原始回答提到缺追加，但不能计为有效命中。",
    "c04": "有效命中：实际返回首次 body，未被重试成功标题与约束掩盖。",
    "c05": "有效命中：明确两秒等待无原文依据，并定位等待在分支前。",
    "c06": "18 项业务要求被判为精确保留，助手未确认明确假通过；精确声明不等于运行保证。",
    "c07": "35 项精确保留、1 项保守保留。四个响应来源按 DEP-MERGE 保留，没有将候选当成同时传递。",
}
notes = [
    {"case": "c02", "finding_ids": ["f_data_archive_only_source", "f_grounding_archive_conflict"],
     "kind": "confirmed_target", "note": "SKILL.md:12、15 要求仅传 source_id 并禁传 FAST_KEY；/blocks/block_011/instructions/0/inputs/2 实际引用环境密钥 result_002。资源定位符与业务参数区分正确。"},
    {"case": "c02", "finding_ids": ["f_order_append_before_return"], "kind": "explanation_identifier_error",
     "note": "自由说明文字列出 block_012，而正确的成功返回块为 block_013；结构化 graph_refs 与实际图正确。说明文本的编号错误未被引文校验发现，不改变该项总体结论。"},
    {"case": "c04", "finding_ids": ["f_data_return_retry_body", "f_ground_internal_conflict_retry_body"],
     "kind": "confirmed_target", "note": "/blocks/block_010/instructions/1/inputs/0 返回首次 result_004；重试 body 实际为 block_008 定义的 result_008。错转与内部冲突成立。"},
    {"case": "c04", "finding_ids": ["f_guard_retry_outcome"], "kind": "overly_broad_obligation",
     "note": "source_requirement 同时写入成功返回 body 与失败回退，整体判 represented，但本项证据仅支持分支去向；返回身份已在另一项判错。应将此项表述限定为分支去向。当前未造成整例假通过，但说明逐项拆分仍依赖模型。"},
    {"case": "c05", "finding_ids": ["finding_10"], "kind": "confirmed_target",
     "note": "/blocks/block_007/instructions/1 存在 wait_for_seconds，输入2且约束有秒单位；等待位于 dispatch 前，两个后继均受影响。不是依据不透明名称猜测。"},
    {"case": "c05", "finding_ids": ["finding_20", "finding_22"], "kind": "execution_boundary",
     "note": "“满足”“有对应实现”只应理解为图中记录了对应操作与次序，不证明文件追加成功或工具内部行为正确。"},
    {"case": "c06", "finding_ids": ["finding_1", "finding_2", "finding_4", "finding_9", "finding_10", "finding_12"],
     "kind": "declaration_boundary", "note": "precise 针对声明、范围或绑定要求的准确记录，不证明载荷不存在夹带、不证明运行时逐条恰好发送一次；后续传播仍需分析。"},
    {"case": "c06", "finding_ids": ["finding_13", "finding_18"], "kind": "source_interpretation_boundary",
     "note": "从选中集合计数可以成立，但“处理条数”不能直接等同成功发送条数；原文要求写入在处理完成后，未独立要求计数必须晚于发送。现图次序可接受，不能把额外次序提升成通用义务。"},
    {"case": "c07", "finding_ids": ["b6_extract_candidate_inputs"], "kind": "confirmed_conservative",
     "note": "四个实际响应结果均被引用，按路径选值未细化的损失被保留。下游 b5、b7、b8 的精确输出绑定不消除该来源精度损失。"},
    {"case": "c07", "finding_ids": ["c1_search_exactly_once", "c2_write_return_singular_terminal", "gc2_branch_calls_supported"],
     "kind": "execution_boundary", "note": "四个静态调用点对应互斥条件分支，不是一次运行调用四次；这些是记录的控制关系，不证明条件求值、可执行性或写入成功。"},
    {"case": "c07", "finding_ids": ["gc3_resource_targets"], "kind": "source_wording_boundary",
     "note": "正确区分 external_resource 与远端；把用户提供的 request.json 称为本地文件比原文略强，是说明措辞问题，不是当前图的明确缺陷。"},
    {"case": "c03", "finding_ids": ["f_action_append_failure_missing", "f_order_append_before_return_failure", "f_ground_internal_conflict_append_failure"],
     "kind": "invalid_response_diagnostic_only", "note": "未通过协议校验的原始响应包含失败出口只有 return、残留标题和约束不能补回 append 的诊断。不得据此将执行错误改为有效命中。"},
]

cases = {}
for key, stage in report["stages"].items():
    record = {"name": names[key], "execution_status": stage["status"], "assistant_assessment": judgments[key]}
    if stage["status"] == "complete":
        audit = stage["result"]
        record.update(semantic_status_counts=dict(Counter(f["status"] for f in audit["findings"] if f["kind"] == "semantic")),
                      precision_summary=audit["precision_summary"],
                      gate_preview=decide(audit, revision=0))
        record["gate_preview_notice"] = "仅离线计算同一反馈门槛，未进行重新提取或额外模型调用。"
    else:
        record.update(error_type=stage["error_type"], error=stage["error"])
    cases[key] = record

call_files = sorted((RUN / "calls").rglob("*"))
hashes = {p.relative_to(RUN).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in call_files if p.is_file()}
secret = load_environment(env_file=ROOT / ".env").get("LLM_API_KEY", "").encode()
assert secret, "Credential scan requires the configured secret; it is not emitted."
leaks = [p.relative_to(RUN).as_posix() for p in RUN.rglob("*") if p.is_file() and secret in p.read_bytes()]
assert not leaks, "Credential scan failed (secret not shown)"
usage = Counter()
for call in report["calls"]:
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        usage[key] += (call.get("usage") or {}).get(key, 0)

review = {"schema_version": 1, "reviewer": "assistant", "human_confirmed": False,
          "method": "Inspect original source, current CFG, controlled evidence and all five valid audit results; external oracle is post-evaluation only.",
          "cases": cases, "observations": notes,
          "effective_target_hits": ["c02", "c04", "c05"],
          "invalid_target_case": "c03", "baseline_validity_unestablished": "c01",
          "additional_substantive_false_positives_confirmed": [],
          "replay_equal": comparisons, "original_call_hashes": hashes,
          "credential_scan": "passed", "returned_models": sorted({c["returned_model"] for c in report["calls"] if c.get("returned_model")}),
          "available_complete_response_usage": dict(usage),
          "usage_boundary": "Two incomplete streams have no complete usage; this is not total billable usage.",
          "limitations": ["No automatic semantic accuracy score.", "No new semantic repair or annotation run.", "No inference that all obligations were found or model judgments were proved."]}
(RUN / "assistant_review.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lines = ["# 七例助手复核", "", "此文件是助手的事后复核，尚未经用户确认；模型原始判断、失败响应及自动报告均保持原样。", ""]
for key, record in cases.items():
    lines.extend([f"## {key} · {record['name']}", "", record["assistant_assessment"], ""])
    for note in notes:
        if note["case"] == key:
            lines.extend([f"- `{', '.join(note['finding_ids'])}`（{note['kind']}）：{note['note']}", ""])
lines.extend(["## 保留的限制", "", "三个合法反例结果均支持目标缺陷被发现；第四个反例响应无效，不能宣布四反例全部通过方法验收。原图也没有有效核对结果。", "", "七类字段和引用合法不能保证每项足够原子：c04 的局部混合要求及 c02 的自由说明编号错误均说明这一边界。保守结果不等于必定传递，声明精确不等于运行保证。", ""])
(RUN / "assistant_review.md").write_text("\n".join(lines), encoding="utf-8")

engine = json.loads((RUN / "engineering.json").read_text(encoding="utf-8"))
engine.update(replay_equal=comparisons, credential_scan="passed", original_call_file_count=len(hashes))
(RUN / "engineering.json").write_text(json.dumps(engine, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
rows = ["| 案例 | 执行结果 | 复核结论 |", "|---|---|---|"]
for key, record in cases.items():
    rows.append(f"| {key} · {record['name']} | {'合法响应' if record['execution_status']=='complete' else '执行错误'} | {record['assistant_assessment']} |")
text = f"""# 统一解释契约与逐项核对 v3：实施及七例验收

工程实现及预定七例调用已经完成。**方法结果为五例合法、两例响应无效；不宣称七例均通过核对。**暂停的30例全流程保持暂停，冻结原图及历史交付没有改写。

## 已实现内容

- IR 通用规则集中于 `skill_ir.semantic_contract`，核对与反馈共用版本和摘要。当前契约为 `{manifest['contract_version']}`。
- 七类关系分别记录，每个业务项声明类别；`represented` 区分 `precise` 和 `conservative`。保守只允许依赖精度损失，不放宽实际动作、明确实参、返回身份或禁止事项。
- 候选证据使用已有操作数与定义链接。同一结果的不同引用不能伪装多个来源，字面值、资源或上下文键不能冒充 `DEP-MERGE` 的结果输入。
- 合法保守项可以满足反馈通过门槛，不触发修图；结果、选择记录和报告保留精度摘要。真正未决、格式错误或全背景项不能通过。
- 共用重试组件负责有界暂态执行重试；并发中断、已接受但无效响应、零调用中断的重放边界均已验证。

## 工程证据

- {engine['unique_verified_tests']} 个不同测试已验证通过：最终完整运行1254通过、1条旧夹具失败；夹具改为真实分支结果后，定向重跑通过（所在文件30项也通过）。没有为夹具放宽校验器。完整记录见 [engineering.json](engineering.json)。
- 固定30图往返30/30通过，本轮7例转换7/7通过。Lean构建、公理审计通过，只依赖 `propext`、`Classical.choice`、`Quot.sound` 等既有基础公理，无占位证明。
- 保护清单3433个既有文件摘要未变化，包括生产提取与IR、冻结语料和历史产物。
- 7次逻辑核对、9次执行、9次HTTP尝试。c01/c02首轮各遇一次 `IncompleteRead`，按同一Prompt有界重试后接收完整响应。
- 离线重放零API，逐例结果、错误、评测候选、调用及计数完全一致。凭据扫描通过，原始调用文件摘要已记录。
- 请求模型为 `deepseek-v4-flash`；完整响应的实际返回名称为 `deepseek-flash`，按服务原样保存，不推断两者别名关系。

## 方法结果

{chr(10).join(rows)}

c01的响应传输完整，但JSON后多出孤立的 Markdown 围栏；c03的完整JSON中有9个核对项缺少必填 `unknown_cause`。两者是输出协议错误，不是仍在等待网络；均未删改、补字段或重新调用来获得通过。c03原始文字确实提到了缺少状态追加，只作为无效响应诊断，不能计为有效命中。

三个有效反例的目标缺陷均得到助手复核支持，未确认额外实质性误报。001、010没有再出现先前的术语或选值误解，010明确保留四个候选来源与精度损失。不过c04一个条目混写分支去向和返回身份，局部“保留”与另一项“错转”重叠；c02一处自由说明写错块编号。这些局限保留在 [逐例助手复核](assistant_review.md) 中，未修改模型结果。

## 阅读与复现

- [自动生成的完整报告](report.md)：七类记录、差异、保守表示、来源与外置匹配候选。
- [助手复核](assistant_review.md)及[结构化复核记录](assistant_review.json)：实际命中与解释边界，尚未经用户确认。
- `calls/` 保存实际Prompt、响应、实际模型名、用量及传输记录；`suggestions/` 保存程序定位的逐项建议；`replay/` 保存离线派生产物。
- 当前运行可用 `python -m skill_ir.backtrace replay --run-dir packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v3-seven-20260918` 离线复现。退出码1对应保留的两例执行错误，不表示需要重新发送请求。

后续应优先处理结构化响应遵从性和局部核对项拆分的稳定性。本轮不增加修复调用，不把有效记录覆盖或工程测试通过当作语义保真证明，也不据七例推断泛化性能。
"""
(RUN / "acceptance.md").write_text(text, encoding="utf-8")
print(json.dumps({"valid_cases":5,"invalid_cases":2,"effective_target_hits":review["effective_target_hits"],
                  "usage":dict(usage),"replay_identical":all(comparisons.values()),"credential_scan":"passed"},ensure_ascii=False))
