"""Assemble post-run evidence and explicitly authored assistant review notes."""
from pathlib import Path
from collections import Counter
import hashlib
import json

from skill_ir.backtrace.runner import verify_run
from skill_ir.feedback.policy import decide
from skill_ir.llm.config import load_environment

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / "packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v4-seven-20260918"
OLD = RUN.with_name("controlled-v3-seven-20260918")
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
write = lambda p, value: p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
manifest = verify_run(RUN, live=True)
report, replayed, previous = read(RUN / "report.json"), read(RUN / "replay/report.json"), read(OLD / "report.json")
assert set(report["stages"]) == {f"c{i:02}" for i in range(1, 8)}
assert report["recorded_logical_calls"] == 7
comparisons = {key: report[key] == replayed[key] for key in (
    "stages", "conversion", "evaluation", "calls", "execution_status", "recorded_logical_calls",
    "recorded_execution_calls", "audit_execution_retries", "http_attempts", "case_selections")}
assert all(comparisons.values())
original = read(HERE / "calls-before-replay.json")
current = {p.relative_to(RUN).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in (RUN / "calls").rglob("*") if p.is_file()}
assert original == current
secret = load_environment(env_file=ROOT / ".env").get("LLM_API_KEY", "").encode()
assert secret, "Credential scan requires configured secret (never emitted)"
assert not any(secret in p.read_bytes() for p in RUN.rglob("*") if p.is_file()), "Credential scan failed; secret not shown"
names = {"c01": "F01 原图", "c02": "F01：archive 多传密钥", "c03": "F01：失败出口缺少状态追加",
         "c04": "F01：重试成功返回首次结果", "c05": "F01：新增两秒等待",
         "c06": "001：条件通知原图", "c07": "010：目录查询原图"}
notes = read(HERE / "case-reviews.json")
assert set(notes) == set(names), "Every case requires an explicit assistant assessment"
cases = {}
for case, stage in report["stages"].items():
    record = {"name": names[case], "execution_status": stage["status"],
              "previous_execution_status": previous["stages"][case]["status"], **notes[case]}
    if stage["status"] == "complete":
        record["business_status_counts"] = dict(Counter(f["status"] for f in stage["result"]["findings"] if f["kind"] == "semantic"))
        record["representation_summary"] = stage["result"]["representation_summary"]
        record["gate_preview"] = decide(stage["result"], revision=0)
        record["gate_preview_notice"] = "仅离线计算现有反馈通过门槛，本次没有重新提取。"
    else:
        record["error_type"], record["error"] = stage.get("error_type"), stage.get("error")
    cases[case] = record
usage = Counter()
for call in report["calls"]:
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = (call.get("usage") or {}).get(key)
        if type(value) is int:
            usage[key] += value
review = {"schema_version": 1, "reviewer": "assistant", "human_confirmed": False,
          "method": "Read full source, actual CFG and every valid finding; invalid responses remain execution failures. Historical results are read as frozen reports, not reinterpreted with v4.",
          "cases": cases, "replay_equal": comparisons, "original_calls_unchanged": True,
          "credential_scan": "passed", "runtime_incidents": read(HERE / "runtime-incidents.json"),
          "returned_models": sorted({c["returned_model"] for c in report["calls"] if c.get("returned_model")}),
          "available_recorded_usage": dict(usage),
          "usage_boundary": "失败或不完整响应可能没有用量；已记录用量不是完整账单统计。",
          "interpretation_boundary": "记录完整不等于语义正确；未填写保守说明不等于精确保留；七例不能支持泛化或统计显著性结论。"}
write(RUN / "assistant_review.json", review)
lines = ["# v4 七例助手复核", "", "助手事后检查，尚未经用户确认；不修改原始模型判定或失败记录。", ""]
for case, record in cases.items():
    lines.extend([f"## {case} · {record['name']}", "", record["assessment"], ""])
    for observation in record["observations"]:
        lines.extend(["- " + observation, ""])
lines.extend(["## 解释边界", "", review["interpretation_boundary"], "",
              "c01、c03 的 Windows 文件替换错误归为本地记录失败，均未重发；无法根据记录单独确定占用文件的进程。首次失败后观察器允许文件并发替换，第二次失败后停止读取全部活跃传输文件。生产源码和本轮输入未修改。", "",
              "c05 的完整响应引用了不存在的事实编号，整例仍是执行错误。原始文字识别到等待只作为诊断，不计有效命中。", "",
              "[运行记录与开销诊断](runtime_diagnostics.md)说明已确认的实现问题及尚未实施的最小修复方向。", ""])
(RUN / "assistant_review.md").write_text("\n".join(lines), encoding="utf-8")
engineering = read(RUN / "engineering.json")
engineering.update(replay_equal=comparisons, original_call_files=len(current), original_calls_unchanged=True,
                   credential_scan="passed", runtime_incidents=review["runtime_incidents"])
write(RUN / "engineering.json", engineering)
valid = sum(stage["status"] == "complete" for stage in report["stages"].values())
rows = ["| 案例 | v3 历史执行 | v4 执行 | 助手复核 |", "|---|---|---|---|"]
for case, record in cases.items():
    cell = lambda text: str(text).replace("|", "\\|").replace("\n", "<br>")
    rows.append(f"| {case} · {record['name']} | {record['previous_execution_status']} | {record['execution_status']} | {cell(record['assessment'])} |")
text = f"""# 精简语义核对 v4：实施与七例复测

协议、反馈与报告精简已完成。全套回归 **{engineering['tests']['passed']} 项通过**；实际七例为 **{valid} 例合法核对记录、{7-valid} 例执行失败**。下表中的失败保留原样，不计为核对器通过或语义漏检。

## 实现变化与工程验证

- 原图 IR 无新增字段；生产提取 Prompt、结构规则和 Lean 打印器保持不变。核对发现与保守说明全部存放在图外。
- 删除强制类别、七类响应表、精度分类与未决原因枚举。七类检查点只作为阅读提示；LLM 可以组合关联要求，但局部错误不能被整体保留结论掩盖。
- 保留六类判定、真实引文、证据编号、建议目标、完整单元覆盖和保真检查。`unknown_reason` 只在未决时必填；`conservative` 只在明确采用保守依赖时填写。无保守说明不自动推断精确。
- `representation_summary` 报告全部保留业务项及其中的保守子集。反馈仍只对明确差异修复，未决及全背景项不能通过。
- 协议与运行记录为 v4，契约为 `{manifest['contract_version']}`。旧版记录明确拒绝，历史响应不补字段、不改判。
- 固定30图往返30/30、本轮七例7/7通过；Lean构建18项任务和公理审计通过，无占位证明。{engineering['protected']['preexisting_files_checked']} 个受保护既有文件摘要未改变。
- 7次计划内逻辑核对，实际 {report['recorded_logical_calls']} 次逻辑调用、{report['recorded_execution_calls']} 次执行、{report['audit_execution_retries']} 次额外执行重试、{report['http_attempts']} 次HTTP尝试。没有提取、标注或原暂停批次续跑。
- 离线重放重新解析核验，零API；结果、错误、计数及评测候选一致，{len(current)} 个原始调用文件未改变，凭据扫描通过。

## 实际方法结果与历史对照

{chr(10).join(rows)}

历史 v3 按当时协议解释。v4 的新响应才使用精简协议，未用新解析器追溯接受旧的缺字段或坏JSON响应。有效记录数量的变化不能直接解释成语义准确率提升。

c01、c03 在持续接收过程中替换本地 `transport.json` 时出现 Windows `WinError 5`。底层异常文字包含“network failure”，但具体错误和重试分类均指向本地存储；没有完整核对结果，按既定策略不自动重发。首次失败后观察器改用允许文件并发替换的共享读取，第二次失败仍发生；之后停止读取活跃传输文件。现有记录不能确认占用者，不能断言是网络、观察器或外部扫描程序造成的。

c05 已完整返回，但引用了不存在的 `fact:/blocks/5/instructions/0/outputs/0`，该状态追加操作实际没有输出。整份响应按协议拒绝，不补编号、不计有效命中。其原始文字确实指出两秒等待无源文依据，这只是无效响应的诊断信息。

工程回归与离线重放已通过，但真实运行暴露了本地记录器的稳定性问题。已记录的后续最小修复方向包括区分本地记录和网络异常、有界重试本地原子替换，以及减少累计 SSE 的同步全量检查点开销；本轮未修改记录器或重新请求失败案例。详见[运行诊断](runtime_diagnostics.md)。

请求模型为 `deepseek-v4-flash`，实际返回名按记录保存为 {', '.join(review['returned_models']) or '无完整返回名称'}，不据此推断模型别名关系。已记录用量见结构化助手复核；不完整调用没有完整用量时不按零消耗计算。

## 阅读与复现

- [自动报告](report.md)：模型判定、差异、保守说明、转换与执行记录。
- [逐例助手复核](assistant_review.md)：目标命中、误报、措辞和判断边界，尚未经用户确认。
- [工程证据](engineering.json)与[结构化复核](assistant_review.json)：测试、来源、重放与历史对照。
- [运行诊断](runtime_diagnostics.md)：本地文件失败、可确认的检查点开销机制及未确定的原因。
- `calls/` 保存实际提示词、响应及传输记录；`suggestions/` 保存逐例建议；`replay/` 保存离线派生结果。

```powershell
python -m skill_ir.backtrace replay --run-dir packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v4-seven-20260918
```

存在保留的执行失败时退出码为1，不表示需要重发请求。工程检查和 Lean 事实保持证明不证明模型核对正确；本轮不宣称源文与图已获语义等价证明，也不依据七例推断泛化表现。
"""
(RUN / "acceptance.md").write_text(text, encoding="utf-8")
print(json.dumps({"valid": valid, "failed": 7-valid, "replay_identical": True,
                  "original_calls_unchanged": True, "credential_scan": "passed"}, ensure_ascii=False))
