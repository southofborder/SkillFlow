"""Chinese review: conversion evidence is separate from model semantic judgments."""
from collections import Counter

LABELS = {"represented": "保留（模型判定）", "omitted": "遗漏", "mistranslated": "错转",
          "unsupported_addition": "无依据新增", "internal_conflict": "内部冲突"}


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _details(finding):
    refs = [f"{r['file']}:{r['start_line']}-{r['end_line']}" for r in finding["source_refs"]]
    units = [r["unit_id"] for r in finding["controlled_refs"]]
    lines = [f"### {finding['id']} · {LABELS[finding['status']]}", "",
            "原文要求：" + finding["source_requirement"], "",
            "实际表示：" + finding["actual_representation"], "",
            "理由：" + finding["reason"], "",
            "源文位置：" + "; ".join(refs), "",
            "受控证据编号：" + ", ".join(units), "",
            "程序映射的图位置：" + "; ".join(finding["graph_refs"]), ""]
    if finding.get("conservative"):
        item = finding["conservative"]
        lines.extend(["保守保留说明：模型明确采用以下依赖解释。", "",
                      "保守规则：" + item["rule_id"], "",
                      "候选事实：" + ", ".join(item["candidate_fact_ids"]), "",
                      "精度损失：" + "; ".join(item["lost_distinctions"]), "",
                      "保守表示依据：" + item["reason"], "",
                      "候选图位置：" + "; ".join(item["graph_refs"]), ""])
    return lines


def _failure_details(stage):
    failure = stage.get("failure")
    if not failure:
        return []
    lines = ["必要判断失败的依据（不作为正常发现，不触发语义修复）：", ""]
    for reference in failure.get("source_refs", []):
        lines.extend([f"源文：`{reference['file']}:{reference['start_line']}-{reference['end_line']}`（`{reference['unit_id']}`）。", "",
                      *["> " + line for line in reference["quote"].splitlines()], ""])
    for reference in failure.get("controlled_refs", []):
        lines.extend(["受控事实：`" + reference["unit_id"] + "`。", ""])
    lines.extend(["程序映射的图位置：" + "; ".join(failure.get("graph_refs", [])), ""])
    return lines


def render_suggestions(identifier, stage):
    lines = [f"# {identifier} 逐项核对与修改建议", "",
             "以下是模型核对及程序定位的结果，尚未经用户确认；不会自动修改原图。", ""]
    if stage["status"] != "complete":
        return "\n".join(lines + ["核对未完成：" + stage.get("error", stage.get("reason", stage["status"])), ""] + _failure_details(stage))
    findings = [f for f in stage["result"]["findings"] if f.get("kind", "semantic") == "semantic"
                and (f["status"] != "represented" or f.get("conservative"))]
    if not findings:
        lines.extend(["模型没有报告业务差异或保守依赖；这不等于已证明语义正确。", ""])
    for finding in findings:
        lines.extend(_details(finding))
        for suggestion in finding["suggestions"]:
            lines.extend(["建议：" + suggestion["change"], "",
                          "建议依据：" + suggestion["reason"], "",
                          "修改目标：" + ", ".join(suggestion["target_ids"]), "",
                          "目标图位置：" + "; ".join(suggestion["graph_refs"]), ""])
    return "\n".join(lines)


def render_report(result):
    lines = ["# 受控语义回述与完整源文核对", "", f"运行：`{result['run_id']}`；模式：`{result['mode']}`。", "",
             f"解释契约：`{result['contract_version']}`，SHA-256 `{result['contract_sha256']}`。", "",
             "唯一模型任务是比较完整原文与受控文本。转换检查、模型判断与外置评测分别报告。", "",
             "## 差异与执行状态", "",
             "以下保留模型原始有效判定；context 项仅记录非业务上下文，不计为业务语义保留。", ""]
    for identifier, stage in result["stages"].items():
        selection = result["case_selections"][identifier]
        label = (f"暂停批次 {selection['sample_index']} 第 {selection['revision']} 轮"
                 if "sample_index" in selection else f"F01 第 {selection['repetition']} 轮及其固定变体")
        lines.extend([f"### {identifier} · {label}", ""])
        if stage["status"] != "complete":
            lines.extend(["执行状态：" + stage["status"], "", stage.get("error", stage.get("reason", "")), ""])
            lines.extend(_failure_details(stage))
            continue
        semantic = [f for f in stage["result"]["findings"] if f.get("kind", "semantic") == "semantic"]
        counts = Counter(f["status"] for f in semantic)
        lines.extend(["；".join(f"{LABELS[k]} {v}" for k,v in counts.items()), "",
                      f"保留项 {len(stage['result']['representation_summary']['represented_ids'])} 项，"
                      f"其中明确填写保守说明 {len(stage['result']['representation_summary']['conservative_ids'])} 项。"
                      "未填写保守说明不代表精确表示。", "",
                      f"逐项修改建议：[suggestions/{identifier}.md](suggestions/{identifier}.md)。", "",
                      "| 核对项 | 原文要求 / 实际表示 | 理由 | 受控证据 |", "|---|---|---|---|"])
        for finding in semantic:
            if finding["status"] == "represented" and not finding.get("conservative"):
                continue
            label = "保留（含保守说明）" if finding.get("conservative") else LABELS[finding["status"]]
            lines.append(f"| {finding['id']} / {label} | {_cell(finding['source_requirement'])}<br>{_cell(finding['actual_representation'])} | {_cell(finding['reason'])} | {_cell(', '.join(r['unit_id'] for r in finding['controlled_refs']))} |")
        lines.append("")
    lines.extend(["## 转换与执行记录", "",
                  f"计划 {result['planned_logical_calls']} 次逻辑调用，已记录 {result['recorded_logical_calls']} 次；状态 `{result['execution_status']}`。", "",
                  f"记录执行 {result['recorded_execution_calls']} 次，额外执行重试 {result['audit_execution_retries']} 次，HTTP 尝试 {result['http_attempts']} 次。", "",
                  f"请求配置：`{result['config']['model']}` / `{result['config']['reasoning_effort']}`。独立上下文，无自动修复或择优。", "",
                  "| 输入 | 受控转换检查 | 模型执行 |", "|---|---|---|"])
    for identifier, stage in result["stages"].items():
        lines.append(f"| {identifier} | {result['conversion'][identifier]} | {stage['status']} |")
    review = result["review30"]
    lines.extend(["", f"固定30图离线验收：启用={review['enabled']}；通过 {sum(r['status']=='passed' for r in review['samples'])}/{len(review['samples'])}。", "",
                  "转换通过仅说明当前受控文本保留规范化图的明确记录；证明边界和逐输入证书另见 inputs 与 verification。", "",
                  "## 外置预期的复核候选", "",
                  "以下仅匹配判定类别与证据区域，不能自动认定语义命中、漏报或误报。", "",
                  "| 输入 | 外置预期 | 匹配状态 | 候选核对项 |", "|---|---|---|---|"])
    for identifier, case in result["evaluation"]["cases"].items():
        if case.get("evaluation_status") == "assistant_review_required":
            lines.append(f"| {identifier} | 无本实验人工标准答案 | 待助手逐项复核 | — |")
        for row in case["expectations"]:
            lines.append(f"| {identifier} | {row['oracle_finding_id']} | {row['status']} | {', '.join(row['candidate_finding_ids'])} |")
    lines.extend(["", "## 可复核材料与限制", "",
                  "- inputs：完整源文、原始案例图、实际受控文本、证据索引和转换检查记录；原始图不进入模型提示词。",
                  "- calls：原始提示词、响应、摘要、实际模型名和 SSE；parsed：严格核验后的结果。",
                  "- suggestions：逐案例修改建议；replay：新版离线重放结果。",
                  "- 约束仅为声明；条件文字未求值；开放操作、源码及运行成功未经证明。",
                  "- 保守依赖列出候选与精度损失，不代表候选同时发生，也不证明后续传播结论。",
                  "- 保留项是模型判定；未填写保守说明不自动意味着精确表示。",
                  "- 固定案例为开发诊断，不能支持泛化正确性或统计显著性结论。", ""])
    return "\n".join(lines)
