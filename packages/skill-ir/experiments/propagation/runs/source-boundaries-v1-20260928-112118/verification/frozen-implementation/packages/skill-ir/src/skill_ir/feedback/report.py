"""Chinese review artifacts; checker decisions are never semantic proofs."""

from __future__ import annotations

from collections import Counter
import json


STATUS_LABELS = {
    "audit_passed": "核对器通过",
    "unresolved": "仅剩未决，停止",
    "revision_limit": "语义修复次数耗尽",
    "extraction_error": "提取执行错误",
    "fidelity_error": "受控文本保真检查错误",
    "audit_error": "核对执行错误",
    "interrupted": "已中断",
    "running": "运行中",
    "not_run": "未执行",
    "revise": "发现明确语义差异，继续完整重新提取",
}
FINDING_LABELS = {
    "represented": "保留（模型判定）",
    "omitted": "遗漏",
    "mistranslated": "错转",
    "unsupported_addition": "无依据新增",
    "internal_conflict": "内部冲突",
    "unknown": "未决",
}


def _cell(value):
    return str(value).replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def audit_findings(round_result):
    """Accept the runner's stage wrapper, without inferring absent findings."""
    audit = round_result.get("audit") or {}
    return audit.get("result", audit).get("findings", [])


def finding_summary(round_result):
    counts = Counter(
        finding["status"] for finding in audit_findings(round_result)
        if finding.get("kind") == "semantic"
    )
    return "；".join(f"{FINDING_LABELS.get(key, key)} {value}" for key, value in counts.items()) or "无有效业务核对项"


def _finding_lines(finding):
    lines = [f"### {finding['id']} · {FINDING_LABELS.get(finding['status'], finding['status'])}", ""]
    if finding.get("conservative"):
        detail = finding["conservative"]
        lines.extend([f"保守规则：`{detail['rule_id']}`；候选事实：" + ", ".join(detail["candidate_fact_ids"]), "",
                      "保留理由：" + detail["reason"], "", "损失的区分：" + "；".join(detail["lost_distinctions"]), ""])
    for label, key in (("原文要求", "source_requirement"), ("当前回述", "actual_representation"), ("差异理由", "reason")):
        lines.extend([f"{label}：{finding.get(key, '')}", ""])
    for reference in finding.get("source_refs", []):
        lines.extend([
            f"源文：`{reference['file']}:{reference['start_line']}-{reference['end_line']}`（`{reference['unit_id']}`）。", "",
            *["> " + line for line in reference.get("quote", "").splitlines()], "",
        ])
    lines.extend(["受控事实：" + ", ".join(f"`{ref['unit_id']}`" for ref in finding.get("controlled_refs", [])), "",
                  "程序映射的当前图位置：" + ", ".join(f"`{ref}`" for ref in finding.get("graph_refs", [])), ""])
    if finding.get("unknown_reason"):
        lines.extend(["未决原因：" + finding["unknown_reason"], ""])
    for suggestion in finding.get("suggestions", []):
        lines.extend([
            "修改建议：" + suggestion["change"], "",
            "依据：" + suggestion["reason"], "",
            "当前目标事实：" + ", ".join(f"`{ref}`" for ref in suggestion["target_ids"]), "",
            "当前目标图位置：" + ", ".join(f"`{ref}`" for ref in suggestion.get("graph_refs", [])), "",
        ])
    return lines


def render_report(result: dict) -> str:
    """Render actual differences first, preserving incomplete and failed rounds."""
    status = result.get("status", "not_run")
    rounds = result.get("rounds", [])
    lines = ["# CFG 构建语义反馈闭环", "",
             f"停止状态：**{STATUS_LABELS.get(status, status)}**（`{status}`）。", "",
             "停止原因：" + str(result.get("reason", "")), "",
             f"解释契约：`{result.get('contract_version')}`；摘要：`{result.get('contract_sha256')}`。", "",
             "“核对器通过”表示当前结构、受控文本及核对响应均有效，并且存在业务项且所有业务项被模型判为保留。它不等于已证明源文与图语义等价。", "",
             "## 逐轮差异与停止决策", "",
             "每轮均核对同一份完整源文与当前受控文本；业务项与背景项分开计数。以下保留实际判断，后轮通过不会删除前轮错误。", "",
             "| 语义轮次 | 状态 | 业务核对 | 决策 |", "|---|---|---|---|"]
    for row in rounds:
        decision = row.get("decision", {})
        lines.append(f"| {row.get('revision', '?')} | {_cell(row.get('status', ''))} | {_cell(finding_summary(row))} | {_cell(_json(decision) if isinstance(decision, dict) else decision)} |")
    lines.extend(["", "## 最后一轮差异、未决和修改建议", ""])
    final_findings = audit_findings(rounds[-1]) if rounds else []
    problems = [finding for finding in final_findings if finding.get("kind") == "semantic" and finding["status"] != "represented"]
    if not problems:
        lines.extend(["最后一轮没有有效的差异或未决记录。若该轮执行失败、缺少业务项或尚未核对，不能据此认定已通过。", ""])
    for finding in problems:
        lines.extend(_finding_lines(finding))
    lines.extend(["## 最后一轮保守保留的依赖", "",
                  "符合契约的候选依赖可以通过；这里逐项保留精度损失，不将候选成员解释成必定发生的传递。未填写保守说明不代表精确保留。", ""])
    conservative = [finding for finding in final_findings if finding.get("conservative") is not None]
    for finding in conservative:
        lines.extend(_finding_lines(finding))
    if not conservative:
        lines.extend(["最后一轮无合法的保守保留项。", ""])
    lines.extend(["## 历史轮次差异", ""])
    for row in rounds[:-1]:
        lines.extend([f"### 第 {row.get('revision', '?')} 轮", ""])
        for finding in audit_findings(row):
            if finding.get("kind") == "semantic" and finding["status"] != "represented":
                lines.extend(_finding_lines(finding))
    lines.extend(["## 工程执行与证据", "",
                  "| 计数或上限 | 实际记录 |", "|---|---|"])
    for category in ("counts", "limits"):
        for key, value in result.get(category, {}).items():
            lines.append(f"| `{category}.{key}` | {_cell(_json(value))} |")
    lines.extend(["", "| 语义轮次 | 提取 / 结构 | 受控转换 | 核对执行 |", "|---|---|---|---|"])
    for row in rounds:
        extraction = row.get("extraction") or {}
        structural = row.get("structural") or {}
        fidelity = row.get("fidelity") or {}
        audit = row.get("audit") or {}
        audit_status = audit.get("status", "complete" if audit.get("findings") else "未执行")
        lines.append(f"| {row.get('revision', '?')} | {_cell(extraction.get('status', '已有图'))} / {_cell(structural.get('status', '未记录'))} | {_cell(fidelity.get('status', '未执行'))} | {_cell(audit_status)} |")
    for row in rounds:
        if row.get("error"):
            lines.extend(["", f"第 {row.get('revision', '?')} 轮执行错误：`{_json(row['error'])}`。", ""])
    lines.extend(["", "### 核对执行重试", "",
                  "一次完整核对是一个逻辑单元。仅明确的暂态通信失败可以启动独立记录的额外执行，"
                  "不增加语义修复次数；完整响应、未决、语义差异及响应格式错误均不触发通信重试。", "",
                  "| 语义轮次 | 执行尝试 | 结果 / 原因 | 继续重试 |", "|---|---|---|---|"])
    for row in rounds:
        for execution in row.get("audit_execution", []):
            lines.append(f"| {row.get('revision', '?')} | {execution['attempt']} | "
                         f"{_cell(execution.get('category', execution['status']))} | "
                         f"{'是' if execution.get('retry') else '否'} |")
    lines.extend(["", "最后有效图存在：" + ("是" if result.get("last_valid_cfg") is not None else "否") + "。", "",
                  "核对器通过图存在：" + ("是" if result.get("passed_cfg") is not None else "否") + "。", "",
                  "未通过时，最后有效图只供检查，不作为成功结果。每轮候选、CFG、结构诊断、受控文本及证书、核对响应和反馈 Prompt 与 calls 中的请求记录一同保存。", "",
                  "## 事后复核与信任边界", "",
                  "- 受控往返保持规范化 CFG 中明确记录的事实，不证明开放操作的执行行为、路径可执行性或文件写入成功。",
                  "- 核对模型每轮独立比较完整原文和当前受控文本；提取模型收到的建议是待核实依据，原文始终优先。",
                  "- 模型可能误报、漏报或在修复后假通过；本报告不会把停止状态自动转换成方法正确率。",
                  "- 重新提取会重新赋号，旧图指针不证明新图已经修好；需结合新图、新证据及完整源文复核。",
                  "- 二进制、未解释内容以及源码摘要、打印器与进程传输的工程边界见运行清单。",
                  "- 助手复核和用户人工确认是不同状态；本生成报告不冒充任何人工确认。", ""])
    if result.get("boundaries"):
        lines.extend(["本次输入的具体边界：", ""])
        lines.extend("- " + str(boundary) for boundary in result["boundaries"])
        lines.append("")
    return "\n".join(lines)
