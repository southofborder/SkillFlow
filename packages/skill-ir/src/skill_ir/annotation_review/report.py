"""Human review of issues first; evidence and raw locations stay expandable."""
from __future__ import annotations

from html import escape
import json
import re
from pathlib import Path

from skill_ir.experiments.report import ArtifactWriter

SUMMARY_LABELS = {"issues_found": "有明确问题", 
                  "no_material_issue": "未发现实质问题"}
NOTICE = "这是旁置模型审查；不修改原标注或传播结果。编号覆盖仅表示声明检查过，未发现实质问题不等于已证明语义正确。"


def display_model(result, material):
    review = result.get("review") or {}
    return {"status": result["status"], "summary": SUMMARY_LABELS.get(result.get("summary"), "审查未完成"),
            "failure": result.get("failure"), "reason": result["reason"], "reviewed_ir_ids": review.get("reviewed_ir_ids", []),
            "findings": review.get("findings", []), "resolved": result.get("resolved_findings", []),
            "targets": material.get("target_index", {}), "observations": material.get("observations", []),
            "counts": result.get("counts", {}), "notice": NOTICE}


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def _md(value):
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", escape(str(value), quote=False))


def render_markdown(model):
    lines = ["# 联合标注聚焦审查", "", f"**{model['summary']}** · 执行状态：`{model['status']}`", "",
             _md(model["reason"]), "", NOTICE, ""]
    for finding in model["findings"]:
        lines += [f"## {_md(finding['id'])} · 问题", "",
                  _md(finding["explanation"]), "", "定位：" + "、".join(map(_md, finding["target_ids"])), ""]
        if finding.get("suggestion"):
            lines += ["修改建议：" + _md(finding["suggestion"]), ""]
        for evidence in finding["evidences"]:
            lines += [f"- {_md(evidence['basis'])} / {_md(evidence['ref_id'])}：{_md(evidence['quote'])}"]
        lines.append("")
    if not model["findings"]:
        lines += ["没有问题条目。" if model["status"] == "complete" else "本次未形成有效问题清单；不能作为未发现问题。", ""]
    if model.get("failure"):
        lines += ["## 无法完成语义任务", "", _md(model["failure"]["reason"]), "",
                  "定位：" + "、".join(map(_md, model["failure"]["target_ids"])), ""]
    resolved = _json(model["resolved"])
    fence = "`" * max(3, max((len(m.group()) + 1 for m in re.finditer(r"`+", resolved)), default=3))
    lines += ["## 审计材料", "", "声明检查的 IR：" + "、".join(map(_md, model["reviewed_ir_ids"])), "",
              "原始调用：[call.json](calls/review/a001/call.json)；定位与材料：[material.json](inputs/material.json)。",
              "", "### 程序解析定位", "", fence + "json", resolved, fence, ""]
    return "\n".join(lines)


def render_html(model):
    e = escape
    cards = []
    for f in model["findings"]:
        evidence = "".join(f"<li><code>{e(v['basis'])} / {e(v['ref_id'])}</code><blockquote>{e(v['quote'])}</blockquote></li>"
                           for v in f["evidences"])
        cards.append(f"<article id='{e(f['id'], quote=True)}'><h2>{e(f['id'])} · 问题</h2>"
                     f"<p>{e(f['explanation'])}</p><p><b>建议：</b>{e(f.get('suggestion') or '未提出猜测性修改。')}</p>"
                     f"<details><summary>查看定位与证据：{e('、'.join(f['target_ids']))}</summary><ul>{evidence}</ul></details></article>")
    if model.get("failure"):
        cards.append(f"<details><summary>无法完成任务的定位与依据</summary><pre>{e(_json(model['failure']))}</pre></details>")
    if not cards:
        cards.append("<p>本次未列出实质问题；这不是语义正确性证明。</p>" if model["status"] == "complete"
                     else "<p>审查未成功，未形成有效问题清单。</p>")
    return ("<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>联合标注聚焦审查</title>"
            "<style>body{max-width:1080px;margin:36px auto;padding:0 24px;font:16px/1.75 system-ui;background:#f7f9fc;color:#1b293a}"
            "article{background:white;border:1px solid #cfd9e5;padding:20px;margin:18px 0;border-radius:10px}"
            "pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}p,blockquote{white-space:pre-wrap;overflow-wrap:anywhere}"
            "details{margin:18px 0}summary{cursor:pointer}code{color:#254e87}a{color:#155d9c}</style><body>"
            f"<h1>联合标注聚焦审查</h1><p><b>{e(model['summary'])}</b> · {e(model['status'])}</p>"
            f"<p>{e(model['reason'])}</p><p>{e(NOTICE)}</p>" + "".join(cards)
            + f"<details><summary>声明覆盖与调用统计</summary><pre>{e(_json({'reviewed_ir_ids': model['reviewed_ir_ids'], 'counts': model['counts']}))}</pre></details>"
            + f"<details><summary>程序解析的原标注位置与值</summary><pre>{e(_json(model['resolved']))}</pre></details>"
            + f"<details><summary>程序编译的观察清单</summary><pre>{e(_json(model['observations']))}</pre></details>"
            + "<p><a href='result.json'>原始审查结果</a> · <a href='inputs/material.json'>冻结审查材料</a> · "
            "<a href='calls/review/a001/call.json'>真实调用</a></p></body></html>")


def write_reports(directory, result, material, *, writer=None):
    writer = writer or ArtifactWriter(())
    directory = Path(directory)
    model = display_model(result, material)
    markdown, html = render_markdown(model), render_html(model)
    if directory.name == "replay":
        for folder in ("inputs/", "calls/"):
            markdown = markdown.replace("](" + folder, "](../" + folder)
            html = html.replace("href='" + folder, "href='../" + folder)
    writer.text(directory / "report.md", markdown)
    writer.text(directory / "report.html", html)
