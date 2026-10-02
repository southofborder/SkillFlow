"""Combine external assistant reviews without altering model annotations."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "packages/skill-ir/experiments/security_profile/runs/security-profile-20260917"
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
cases = []
for name in ("review-001-010.json", "review-011-020.json", "review-021-030.json"):
    group = read(RUN / name)
    assert len(group) == 10
    cases.extend(group)
assert [case["case_id"] for case in cases] == [f"{i:03}" for i in range(1, 31)]
original = read(RUN / "experiment-result.json")
manifest = read(RUN / "manifest.json")
for case, provenance in zip(cases, manifest["cases"]):
    assert case["sample_id"] == provenance["sample_id"]
    assert case["status_observed"] == original["cases"][case["case_id"]]["status"]
    assert (RUN / f"cases/{case['case_id']}/assistant-review.md").is_file()
    assert case["checked_focus"]
assessable = [case["case_id"] for case in cases if case["status_observed"] in {"complete", "incomplete"}]
result = {"reviewer": "assistant", "user_confirmed": False,
          "case_records_reviewed": 30, "accepted_annotations_reviewed": assessable,
          "unaccepted_candidate_diagnostics": ["028", "029"],
          "execution_failures_without_accepted_annotations": 19,
          "no_model_outputs_modified": True, "cases": cases}
(RUN / "assistant-review.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
lines = ["# 30 例安全语义标注：助手逐例复核", "",
         "这是助手复核，未由用户确认；原始模型标注、未决和执行状态保持不变。", "",
         "30 例均已核查源文、实际 CFG 和已保存运行记录。其中只有 9 例存在经过严格校验接受的标注；",
         "028、029 仅诊断未接受的完整原始候选，另外 19 例没有可接受标注，不能评价其标注语义。", "",
         "[实施验收总报告](acceptance.md) · [机器可读复核](assistant-review.json) · [原始批次结果](experiment-result.json)", "",
         "## 主要意见", "",
         "- 执行者归属影响模型可见性，同类读取/提取操作的 runtime、tool、llm 分配存在证据不足和波动，不能用缺少观察标签证明模型不可见。",
         "- 已明确记录 model_observe 的动作仍有漏记 sink 角色的情况；复合的修改/渲染操作也有只列 LLM 而遗漏工具参与的情况。",
         "- 网络、文件和用户边界需要具体依据；工具名、delivery_path 或普通 return 本身不足以确定效果。",
         "- 030 的观察理由混淆工具默认输出路径与 --stdout 输出正文；有 model_observe 不等于已看到文件正文，更不等于已完成传播判断。",
         "- 028、029 的源文定位错误被严格拒收，分别发现 33、12 处错配；它们的其他语义观察只属于未接受候选诊断。",
         "- 7 项模型未决保留原样。隐私声明没有被自动视为保护操作，脚本支持的多效果和部分网络双向效果得到了合理标注。", "",
         "这些是方法诊断，不计算正确率，不把助手发现补写进模型 profiles 或 unresolved。", "",
         "## 逐例结论", "", "| 编号／样例 | 程序状态 | 助手结论 |", "|---|---|---|"]
for case in cases:
    conclusion = str(case["review_conclusion"]).replace("|", "\\|").replace("\n", "<br>")
    lines.append(f"| [{case['case_id']} / {case['sample_id']}](cases/{case['case_id']}/assistant-review.md) | `{case['status_observed']}` | {conclusion} |")
lines += ["", "每例报告包含已阅读范围、具体 IR、原文/图/标注证据、未决边界与后续建议。", "",
          "程序 complete 仅表示记录完整；助手复核也没有证明推断正确或运行行为。数据传播及综合安全判断仍未实施。", ""]
(RUN / "assistant-review.md").write_text("\n".join(lines), encoding="utf-8")
# This generated artifact's original review-status sentence was true when it was
# produced. Update only that run-local sentence now that external review exists.
path = RUN / "report.md"
text = path.read_text(encoding="utf-8")
text = text.replace(
    "助手复核尚待逐例完成，记录应另外保存为 assistant-review.md；本自动报告不冒充人工确认。重点检查模型观察、多主体／多角色、网络双向效果及声明与实际变换的区别。",
    "助手已完成 30 例源图与运行记录复核，其中 9 例存在可接受标注。意见单独保存于 [assistant-review.md](assistant-review.md)，实施验收见 [acceptance.md](acceptance.md)。模型输出保持原样，尚未由用户确认。")
path.write_text(text, encoding="utf-8")
print(json.dumps({"case_records_reviewed": 30, "accepted_annotations_reviewed": len(assessable),
                  "model_statuses": dict(Counter(case["status_observed"] for case in cases))}, ensure_ascii=False))
