"""Assemble human review and engineering receipts for this frozen experiment."""
from collections import Counter
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/skill-ir/src"))
sys.path.insert(0, str(ROOT / "packages/skill-ir/experiments/propagation/tools"))
from skill_ir.recording import canonical_sha256, read_json, sha_file
import run_sink_pilot as pilot

RUN = ROOT / "packages/skill-ir/experiments/propagation/runs/sink-boundaries-v1-20261002-185934"
summary = pilot.summarize(RUN)
replay = read_json(RUN / "replay-verification.json")
preservation = read_json(RUN / "preservation.json")
assert replay["status"] == preservation["status"] == "matched"
assert summary["logical_calls"] == summary["http_attempts"] == 3
assert all((RUN / "cases" / c / "assistant-review.md").is_file() for c in ("001", "010", "013"))

test_tree = ET.parse(ROOT / "tmp/sink-boundaries-final-tests.xml")
suites = list(test_tree.getroot().iter("testsuite"))
test_counts = {key: sum(int(s.attrib.get(key, 0)) for s in suites)
               for key in ("tests", "failures", "errors", "skipped")}
assert test_counts == {"tests": 2426, "failures": 0, "errors": 0, "skipped": 0}
shutil.copyfile(ROOT / "tmp/sink-boundaries-final-tests.xml", RUN / "tests.junit.xml")

method = {
    "schema_version": "skill-ir-sink-assistant-review-v1",
    "reviewer": "assistant", "human_confirmed": False,
    "cases": [
        {"case_id": "001", "engineering": "complete", "method": "issue_found",
         "issues": [{"id": "001-network-inference", "instruction_id": "ir_005",
            "statement": "源文没有网络部署依据，标注却选择 remote/net_send；应保留 tool 边界的契约外部接收可能性。",
            "impact": "sink 类型应为 external_tool；等级 2 与 recipient/body 配对仍合理。",
            "automatically_modified": False}]},
        {"case_id": "010", "engineering": "complete", "method": "issues_found",
         "issues": [{"id": "010-optional-identity", "instruction_id": "ir_007",
            "statement": "原值传入、缺失省略的可选字段被合成 opaque compute，sink 载荷只保留 possible 影响。",
            "impact": "不能仅靠载荷确认参数身份和按条件省略；字段值与存在性控制应区分。",
            "automatically_modified": False},
           {"id": "010-request-binding", "instruction_id": "ir_007",
            "statement": "deliver 使用 term 和 opaque 组合，receive.inputs 则列字段值及存在性旗标；实际参数与控制影响混列。",
            "impact": "不能据此认定旗标明文外发或整个 request 外发。",
            "automatically_modified": False}]},
        {"case_id": "013", "engineering": "invalid_response", "method": "not_assessed",
         "issues": [], "failure": "完整响应末尾多余一个 }，严格 JSON 解析失败；不是超时或截断。"},
    ],
}
(RUN / "assistant-review.json").write_text(json.dumps(method, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

notice = "这是统一抽象运行时契约下的静态可能行为，不是执行日志。边界暴露等级不表示数据敏感度、任务必要性或 DOE 结论。"
status_text = {"001": "标注和传播完成；有网络分类问题", "010": "标注和传播完成；有参数精度问题", "013": "完整响应格式失败；未生成 DOE"}
details = {
    "001": "读取、筛选、字段准备与计数采用 default；编译得到 4 处可能模型观察。同一元素的 recipient 与 summary 通过 select_part 保持配对，count.txt 持久写入等级 1。唯一实质问题是 notify.send 仅由调用描述被标成网络发送，没有部署依据；应为可能的外部工具交付，等级仍为 2。",
    "010": "工具请求、取得响应和响应后的模型观察分开；index.search 为 tool/recipient/null，没有凭名称增加网络效果。来源整体及响应 total/items 原字段保持。但 ir_007 将可选参数原值与存在性旗标合成 opaque 结果，deliver 与 receive 的输入表达也不一致，不能据此作精确参数级必要性判断。",
    "013": "HTTP 200、SSE 完整结束、finish_reason=stop；响应末尾多余一个 }，解析报 Extra data。实际只调用一次，未修剪文本或质量补跑。来源范围、模型观察、首次/重试/回退身份、禁传和 status.txt 边界本轮未验收。0 个已解析 sink 不表示没有 sink。",
}

md = ["# Sink 边界：工程验收与三例复核", "", notice, "",
      "本轮代码、规范与离线验收已完成；三例真实标注得到 2 份可用 DOE 文件和 1 份格式失败记录。助手意见旁置保存，没有修改模型输出，也没有启动标注修复或 CFG 重提取。", "",
      "| 样例 | 最新状态 | 已生成 sink | 审查入口 |", "| --- | --- | --- | --- |"]
html = ["<h1>Sink 边界：工程验收与三例复核</h1><p>" + escape(notice) + "</p>",
        "<p>2,426 项测试通过；真实模型调用 3 次、HTTP 尝试 3 次、传输重试 0 次。两例完成，一例完整返回后 JSON 格式失败。模型输出保持原样，以下问题未自动修复。</p>",
        "<table><thead><tr><th>样例</th><th>最新状态</th><th>已生成 sink</th><th>审查入口</th></tr></thead><tbody>"]
for row in summary["cases"]:
    c = row["case_id"]
    base = f"cases/{c}/"
    links = [(base + "assistant-review.md", "助手复核"),
             (base + "selected-analysis.json", "既有 CFG"),
             (base + "annotation/report.md", "标注状态与边界依据"),
             (base + "annotation/calls/annotation/a001/response.json", "原始模型响应")]
    if row["propagation"] == "complete":
        links = [(base + "propagation/report.html", "数据与边界审查"),
                 (base + "propagation/doe-input.json", "DOE 原始事实"),
                 (base + "annotation/sink-boundaries.json", "编译 sink 清单")] + links
        counts = "、".join(f"{k} × {v}" for k, v in row["sink_types"].items())
    else:
        counts = "未生成；不能解释为无 sink"
    assert all((RUN / p).is_file() for p, _ in links)
    md.append(f"| {c} / {row['sample_id']} | {status_text[c]} | {counts} | " + " · ".join(f"[{t}]({p})" for p, t in links) + " |")
    html.append("<tr><td>" + c + " / " + row["sample_id"] + "</td><td>" + escape(status_text[c]) + "</td><td>" + escape(counts) + "</td><td>" + " · ".join(f'<a href="{escape(p, quote=True)}">{escape(t)}</a>' for p, t in links) + "</td></tr>")
html.append("</tbody></table>")

md += ["", "## 助手复核：实际改善与保留问题", ""]
html.append("<h2>助手复核：实际改善与保留问题</h2>")
for c in ("001", "010", "013"):
    md += [f"### {c}", "", details[c], ""]
    html += ["<h3>" + c + "</h3><p>" + escape(details[c]) + "</p>"]

engineer = [
    "LocationSpec 统一保存 access_scope 与 retention；存储和上下文 retention 必填，未知接收方留存期限允许 null。Profile 保持四字段。",
    "程序从 deliver/write 及编译观察生成六类 sink，不根据 roles 筛选；等级由范围与留存决定。等级 0 和删除不进入 sink 清单，但保留传播关系。",
    "请求交付、工具返回、模型观察与本次保存载荷保持各自版本。sink 清单只引用已有坐标和目标，Data ID 从实际操作记录读取，不另存一份载荷。",
    "运行时契约 v4、表示契约 v2、联合标注 v9、标注运行 v10、编译器 v3、传播记录 v8、DOE 输入 v6、传播运行 v9；Data 仍为 v4。旧格式明确拒绝。",
    "2,426 项离线回归全部通过，覆盖固定分级、内部/持久/共享/公开边界、删除与追加、零参数工具、重复阶段、逐元素配对、清单篡改、一次修复服务及原流程回归。",
    "三例在禁止网络及在线客户端创建的进程中完成零 API 重放；001/010 的 DOE 摘要不变，013 的同一失败状态重现。重放没有再次持久保存一份最终 Data。",
    "旧加载器在升级前核验并冻结三例。11,319 个历史/交付文件及额外 36 个生产提取、IR、Data、核对和反馈源码检查均保持摘要一致。",
]
md += ["## 工程与保护验收", "", *["- " + s for s in engineer], "",
       "浏览器自动检查因本地 file:// 策略被拒绝，未执行浏览器视觉验证。已完成离线链接、UTF-8、内容与转义检查；审查 HTML 可作为人工审计入口。", "",
       "[测试记录](tests.junit.xml) · [工程验收摘要](verification.json) · [零 API 重放凭据](replay-verification.json) · [历史保护检查](preservation.json) · [调用和状态](summary.json)", ""]
html += ["<h2>工程与保护验收</h2><ul>" + "".join("<li>" + escape(s) + "</li>" for s in engineer) + "</ul>",
         "<p>浏览器自动检查因本地 file:// 策略被拒绝，未执行浏览器视觉验证。已完成离线链接、UTF-8、内容与转义检查。</p>",
         '<p><a href="tests.junit.xml">测试记录</a> · <a href="verification.json">工程验收摘要</a> · <a href="replay-verification.json">零 API 重放凭据</a> · <a href="preservation.json">历史保护检查</a> · <a href="summary.json">调用和状态</a> · <a href="report.md">中文报告</a></p>']
(RUN / "report.md").write_text("\n".join(md), encoding="utf-8")
(RUN / "index.html").write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sink 边界三例验收</title><style>body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1450px;margin:32px auto;padding:0 24px;color:#17303b}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd7df;padding:12px;vertical-align:top;overflow-wrap:anywhere}th{background:#eef5f7}a{color:#09667a}h3{margin-bottom:8px}li{margin:8px 0}</style></head><body>' + "".join(html) + '</body></html>', encoding="utf-8")

class LinkCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])

missing, checked = [], 0
for p in RUN.rglob("*.html"):
    parser = LinkCheck()
    text = p.read_text(encoding="utf-8")
    assert "�" not in text, p
    parser.feed(text)
    for href in parser.links:
        url = urlsplit(href)
        if url.scheme or not url.path:
            continue
        checked += 1
        resolved = (p.parent / unquote(url.path)).resolve()
        if not resolved.is_file() and resolved != RUN / "verification.json":
            missing.append({"file": str(p.relative_to(RUN)), "href": href})
assert not missing, missing

usage = Counter()
for row in summary["cases"]:
    usage.update(row["counts"]["known_token_usage"])
receipt = {"status": "passed", "test_counts": test_counts, "test_report_sha256": sha_file(RUN / "tests.junit.xml"),
           "logical_calls": 3, "http_attempts": 3, "http_retries": 0,
           "requested_model": "deepseek-v4-flash", "returned_models": ["deepseek-flash"],
           "known_token_usage": dict(usage), "case_statuses": summary["annotation_statuses"],
           "replay": replay, "preservation": preservation,
           "assistant_review_sha256": canonical_sha256(method),
           "artifact_checks": {"relative_html_links": checked, "missing_links": 0,
                               "utf8_replacement_characters": 0, "browser_visual_verified": False}}
(RUN / "verification.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
assert (RUN / "verification.json").is_file()
print(json.dumps({"status": receipt["status"], "test_counts": test_counts,
                  "logical_calls": 3, "relative_html_links": checked,
                  "method_statuses": {c["case_id"]: c["method"] for c in method["cases"]}}, ensure_ascii=False))
