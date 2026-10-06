"""Build an offline, source-bound PDF from real trials and external human reviews.

No Skill script or model is executed. A full report requires all 90 trials and 30
reviews. Explicit interim reports retain that plan and only detail committed trials;
layout previews remain a separate, non-delivery mode.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import importlib.util
import hashlib
import json
from pathlib import Path
import sys

from skillflow.common.paths import project_root, resolve_material_path

BASE = project_root() / "experiments/graph/baseline"
REPO = project_root()
FROZEN = BASE / "frozen" / "corpus"

# Reuse the reviewed, glyph-checked font and wrapping primitives read-only.
from tools.corpus import build_pdfs as layout
from tools.graph.baseline import review_results, result_integrity
_SOURCE = Path(layout.__file__)
_REVIEW_SOURCE = Path(review_results.__file__)
_INTEGRITY_SOURCE = Path(result_integrity.__file__)

_PDF_IMPORT_ERROR = None
try:
    from reportlab import Version as REPORTLAB_VERSION
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Flowable, KeepTogether, PageBreak, Spacer, TableStyle
    from reportlab.platypus.tableofcontents import TableOfContents
except ModuleNotFoundError as error:
    _PDF_IMPORT_ERROR = error


def _require_pdf():
    if _PDF_IMPORT_ERROR is not None:
        raise SystemExit("PDF generation requires the optional reportlab dependency; install the PDF tool dependencies first.") from _PDF_IMPORT_ERROR
    layout.require_pdf_dependencies()


VERDICTS = {
    "preserved": "保留",
    "partial": "部分保留",
    "missing": "遗漏",
    "contradicted": "冲突",
    "unassessable": "无法判断",
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def operand_text(operand):
    kind = operand.get("type", "unknown")
    if kind == "literal":
        return "literal = " + json.dumps(operand.get("literal_value"), ensure_ascii=False)
    text = f"{kind}: {operand.get('identifier')}"
    if operand.get("semantic_name"):
        text += " | " + str(operand["semantic_name"])
    return text


def script_content_summary(script):
    """Describe the exact representation hashed by the presentation layer."""
    text = script if isinstance(script, str) else json.dumps(script, ensure_ascii=False)
    basis = "原文 UTF-8" if isinstance(script, str) else "JSON 序列化值的 UTF-8（非原始脚本字节）"
    return f"metadata.script_content：{len(text)} 字符；SHA256 {hashlib.sha256(text.encode('utf-8')).hexdigest()}；计数与摘要依据：{basis}。完整值保留在本次 analysis.json；此处保留黑盒接口及全部数据引用。"


if _PDF_IMPORT_ERROR is None and getattr(layout, "_PDF_IMPORT_ERROR", None) is None:
    class ResultsDoc(layout.ReviewDoc):
        def __init__(self, filename, interim=False):
            super().__init__(filename, "Skill-IR 语义基线 | 实际结果复核")
            self.subject = "Actual baseline outputs and independent fact review; pending joint result review"
            self.footer_text = "参考事实已共同确认 | 模型结果待共同复核"
            if interim:
                self.label = "Skill-IR 阶段性结果 | 基线未完成"
                self.title = "Skill-IR 阶段性结果复核 - 基线未完成"
                self.subject = "Interim actual results; the 90-trial baseline is incomplete"
                self.footer_text = "阶段性结果，基线未完成 | 模型结果待共同复核"

        def afterFlowable(self, item):
            super().afterFlowable(item)
            if getattr(item, "trial_key", None):
                self.page_index[item.trial_key] = self.page
                key = "trial-" + item.trial_key.replace("/", "-")
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(item.trial_title, key, 1, False)
                self.notify("TrialTOCEntry", (0, layout.markup(item.trial_title), self.page, key))

        def afterPage(self):
            c = self.canv
            c.saveState()
            c.setStrokeColor(layout.RULE)
            c.line(layout.MARGIN, layout.PAGE_H - 34, layout.PAGE_W - layout.MARGIN, layout.PAGE_H - 34)
            c.line(layout.MARGIN, 35, layout.PAGE_W - layout.MARGIN, 35)
            c.setFont("Body", 8.2)
            c.setFillColor(layout.MUTED)
            c.drawString(layout.MARGIN, layout.PAGE_H - 25, self.label)
            c.drawRightString(layout.PAGE_W - layout.MARGIN, layout.PAGE_H - 25, self.sample_id)
            c.drawString(layout.MARGIN, 22, self.footer_text)
            c.drawRightString(layout.PAGE_W - layout.MARGIN, 22, str(self.page))
            c.restoreState()


if _PDF_IMPORT_ERROR is None and getattr(layout, "_PDF_IMPORT_ERROR", None) is None:
    class GraphRow(Flowable):
        """One actual adjacency row; right boxes reference nodes by their real IDs."""
        def __init__(self, block_id, edges, entry=False, continuation=False):
            super().__init__()
            self.block_id, self.edges = block_id, edges
            self.entry, self.continuation = entry, continuation
            self.height = max(38, len(edges) * 24 + 8)
            self.spaceAfter = 7

        def wrap(self, availWidth, availHeight):
            self.width = availWidth
            return self.width, self.height

        def draw(self):
            c = self.canv
            left_width, target_x = 156, 288
            y = self.height / 2
            c.setStrokeColor(layout.TEAL if self.entry else layout.RULE)
            c.setLineWidth(1.5 if self.entry else .6)
            c.setFillColor(layout.PALE)
            c.roundRect(0, y - 15, left_width, 30, 4, fill=1, stroke=1)
            c.setFillColor(layout.BLUE)
            c.setFont("Code", 10)
            c.drawString(9, y - 3, self.block_id)
            if self.entry:
                c.setFont("Body", 8)
                c.drawRightString(left_width - 8, y - 3, "入口")
            if self.continuation:
                c.setFont("Body", 8)
                c.drawRightString(left_width - 8, y - 3, "续")
            c.setStrokeColor(layout.TEAL)
            c.setFillColor(layout.TEAL)
            c.setLineWidth(.8)
            if not self.edges:
                c.setFont("Body", 9)
                c.drawString(target_x, y - 3, "无出边")
            for index, (edge_id, target) in enumerate(self.edges):
                target_y = self.height - 16 - index * 24
                c.line(left_width, y, 208, y)
                c.line(208, y, 208, target_y)
                c.line(208, target_y, target_x - 8, target_y)
                c.line(target_x - 8, target_y, target_x - 13, target_y + 3)
                c.line(target_x - 8, target_y, target_x - 13, target_y - 3)
                c.setFont("Code", 8)
                c.drawString(216, target_y + 3, edge_id)
                c.setFillColor(colors.white)
                c.roundRect(target_x, target_y - 9, self.width - target_x, 18, 3, fill=1, stroke=1)
                c.setFillColor(layout.BLUE)
                c.setFont("Code", 9.2)
                c.drawString(target_x + 7, target_y - 3, target)


if _PDF_IMPORT_ERROR is None and getattr(layout, "_PDF_IMPORT_ERROR", None) is None:
    class TrialIndex(TableOfContents):
        def notify(self, kind, stuff):
            if kind == "TrialTOCEntry":
                super().notify("TOCEntry", stuff)


class Sources:
    def __init__(self):
        self.hashes = {}

    def load(self, path):
        path = Path(path).resolve()
        data = path.read_bytes()
        self.hashes[str(path)] = hashlib.sha256(data).hexdigest()
        return json.loads(data.decode("utf-8"))

    def add(self, path):
        path = Path(path).resolve()
        self.hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()

    def check(self):
        for path, digest in self.hashes.items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest:
                raise ValueError(f"Source changed during PDF build: {path}")


def trial_metrics(trial):
    record, analysis = trial["record"], trial["analysis"]
    cfg = (analysis or {}).get("cfg")
    blocks = list((cfg or {}).get("blocks", {}).values())
    return {
        "status": record.get("status", "not_run"),
        "blocks": len(blocks) if cfg else None,
        "edges": len(cfg.get("edges", [])) if cfg else None,
        "instructions": sum(len(b.get("instructions", [])) for b in blocks) if cfg else None,
        "constraints": (
            len(cfg.get("constraints", []))
            + sum(len(b.get("constraints", [])) for b in blocks)
            + sum(len(i.get("constraints", [])) for b in blocks for i in b.get("instructions", []))
        ) if cfg else None,
        "generation_attempts": record.get("generation_attempts"),
        "repair_attempts": record.get("repair_attempts"),
        "http_attempts": record.get("http_attempts"),
        "http_retries": record.get("http_retries"),
        "remote_unknown_http": len(result_integrity.remote_unknown_attempts(trial.get("trace"))) if trial.get("trace") is not None else None,
    }


def load_materials(args):
    sources = Sources()
    interim = getattr(args, "interim_results", False)
    freeze, identities = result_integrity.verify_result_sources(BASE, args.run_dir.resolve(), args.variant)
    for relative in freeze["files"]:
        sources.add(BASE / "frozen" / relative)
    sources.run_identity = sources.load(args.run_dir / "experiment.json")
    sources.add(args.run_dir / "dataset.json")
    samples = sources.load(FROZEN / "corpus.json")["samples"]
    run = args.run_dir.resolve()
    report = sources.load(run / "report.json")
    if report.get("mode") != "online":
        raise ValueError("Results PDF requires actual online trial artifacts")
    if interim and report.get("status") in {"running", "pending"}:
        raise ValueError("Interim results require a stopped run")
    lookup = {(x["case"], x["repetition"]): x for x in report["trials"] if x["variant"] == args.variant}
    if len(lookup) != len([x for x in report["trials"] if x["variant"] == args.variant]):
        raise ValueError("Duplicate sample/repetition records")
    materials = []
    for sample in samples:
        annotation = sources.load(FROZEN / sample["annotation_path"])
        trials = []
        for repetition in [1, 2, 3]:
            key = (sample["id"], repetition)
            path = run / "trials" / sample["id"] / args.variant / str(repetition)
            record_path, analysis_path = path / "record.json", path / "analysis.json"
            record = sources.load(record_path) if record_path.is_file() else lookup.get(key, {"status": "not_run"})
            terminal = record.get("status") in review_results.TERMINAL
            if terminal and (record.get("case"), record.get("variant"), record.get("repetition")) != (sample["id"], args.variant, repetition):
                raise ValueError(f"Trial sample identifier mismatch: {record_path}")
            if not terminal and not args.allow_partial and not (interim and record.get("status") == "not_run"):
                raise ValueError(f"Trial is not terminal: {sample['id']} / {repetition}")
            if terminal:
                result_integrity.verify_trial_record(record, lookup.get(key), path, identities[sample["id"]])
            analysis = sources.load(analysis_path) if analysis_path.is_file() else None
            if record.get("status") in {"complete", "degraded"} and analysis is None:
                raise ValueError(f"Missing persisted analysis: {path}")
            if analysis and record.get("status") in {"complete", "degraded"} and analysis.get("status") != record["status"]:
                raise ValueError(f"Analysis/record status mismatch: {path}")
            if record.get("status") == "complete" and not analysis.get("cfg"):
                raise ValueError(f"Complete trial has no accepted CFG: {path}")
            for name, expected in record.get("artifact_sha256", {}).items():
                artifact = path / name
                if not artifact.is_file() or layout.sha(artifact) != expected:
                    raise ValueError(f"Trial artifact hash mismatch: {artifact}")
                sources.add(artifact)
            if analysis and analysis.get("cfg") and record.get("status") != "complete":
                raise ValueError(f"Unaccepted CFG cannot be presented as actual accepted CFG: {path}")
            trace_path = path / "trace.json"
            trace = sources.load(trace_path) if trace_path.is_file() else None
            if interim and record.get("status") == "not_run" and (analysis is not None or trace is not None):
                raise ValueError("Unrun trial has uncommitted artifacts; reconcile before interim delivery")
            trials.append({"repetition": repetition, "path": path, "record": record, "analysis": analysis, "trace": trace})
        review_path = run / "reviews" / f"{sample['id']}.json"
        review = sources.load(review_path) if review_path.is_file() else None
        all_terminal = all(t["record"].get("status") in review_results.TERMINAL for t in trials)
        if review is None and not args.allow_partial and (not interim or all_terminal):
            raise ValueError(f"Missing external semantic review: {review_path}")
        if review:
            review_results.validate_review(review, sample, run, base=BASE)
            if review["sample_id"] != sample["id"]:
                raise ValueError(f"Review sample ID mismatch: {review_path}")
            expected_facts = {fact["id"] for fact in annotation["facts"]}
            actual_facts = [fact["fact_id"] for fact in review["facts"]]
            if len(actual_facts) != len(expected_facts) or set(actual_facts) != expected_facts:
                raise ValueError(f"Incomplete or duplicate fact review: {sample['id']}")
            for fact in review["facts"]:
                assessments = fact["assessments"]
                if sorted(a["repetition"] for a in assessments) != [1, 2, 3]:
                    raise ValueError(f"Every fact must cover three repetitions: {fact['fact_id']}")
                if any(a["verdict"] not in VERDICTS or not a.get("reason") for a in assessments):
                    raise ValueError(f"Invalid fact assessment: {fact['fact_id']}")
            for trial in trials:
                rep = str(trial["repetition"])
                for kind in ["analysis", "record"]:
                    path = trial["path"] / f"{kind}.json"
                    actual = layout.sha(path) if path.is_file() else None
                    if review[f"{kind}_sha256"][rep] != actual:
                        raise ValueError(f"Stale review: {sample['id']} / {rep} / {kind}")
        materials.append({"sample": sample, "annotation": annotation, "trials": trials, "review": review})
    if not args.allow_partial and set(lookup) != {(s["id"], r) for s in samples for r in [1, 2, 3]}:
        raise ValueError("Final report must contain exactly 30 samples x 3 repetitions")
    for path in [Path(__file__), _SOURCE, _REVIEW_SOURCE, _INTEGRITY_SOURCE, _INTEGRITY_SOURCE.with_name("freeze.py"), BASE / "approval.json", BASE / "freeze_manifest.json", BASE / "contract_v2" / "migration.json"]:
        sources.add(path)
    sources.report_scope = result_integrity.result_report_scope(materials, "interim" if interim else "preview" if args.allow_partial else "final")
    return sources, report, materials


def show(value):
    return "未记录" if value is None else str(value)


def statistics_table(trials):
    metrics = [trial_metrics(t) for t in trials]
    rows = [["指标", "第 1 次", "第 2 次", "第 3 次"]]
    for key, label in [
        ("status", "结构状态"), ("blocks", "块数"), ("edges", "边数"),
        ("instructions", "操作数"), ("constraints", "三层约束条数"),
        ("generation_attempts", "生成尝试"), ("repair_attempts", "结构修复"),
        ("http_attempts", "HTTP 尝试"), ("http_retries", "HTTP 重试"),
        ("remote_unknown_http", "远端结果未知 HTTP"),
    ]:
        rows.append([label] + [show(m[key]) for m in metrics])
    return layout.table(rows, [3.4, 2.2, 2.2, 2.2])


def sample_review(material, interim=False):
    sample, annotation, review = material["sample"], material["annotation"], material["review"]
    sid = sample["id"]
    story = [PageBreak(), layout.heading(f"{sid}  {sample['title']}", sample=sid, toc=True),
             layout.p(layout.sample_meta(sample), "small"), statistics_table(material["trials"]), Spacer(1, 9)]
    story += [layout.heading("执行状态（未满三次，不作事实判定）" if interim and review is None else "三次运行差异与初审意见", 2)]
    if review:
        story += [layout.p(review["run_comparison"]), layout.p(review["overall"])]
    else:
        if interim:
            attempted = sum(t["record"].get("status") in review_results.TERMINAL for t in material["trials"])
            story += [layout.p(f"本样例已有 {attempted} 次终态记录，其余试验尚未运行。本节仅展示执行状态；没有三次完整记录，不生成或预填逐事实判定。已尝试记录见本册后半部分，未运行试验只保留在状态表中。")]
            return story
        story += [layout.p("排版预览：尚无外置人工初审，不预填语义结论。")]
    cfgs = [(t["analysis"] or {}).get("cfg") for t in material["trials"]]
    digest_count = len({json.dumps(cfg, sort_keys=True, ensure_ascii=False) for cfg in cfgs if cfg})
    story += [layout.p(f"已接受 CFG 的精确 JSON 有 {digest_count} 种。编号、顺序、措辞变化均会造成差异，此统计不判定语义等价。全部节点、边与数据引用见后半册 {sid} 的三次明细。", "small")]
    findings = (review or {}).get("additional_findings", [])
    if findings:
        story += [layout.heading("事实表以外的发现", 2)]
        for finding in findings:
            text = f"运行 {', '.join(map(str, finding['repetitions']))} | " + finding["reason"]
            story += [layout.p(text), layout.p("引用：" + (", ".join(finding.get("references", [])) or "无局部引用"), "small")]
    fact_heading = layout.heading("逐事实初审（参考事实已确认，结果判定待共同复核）", 2)
    reviewed = {f["fact_id"]: f for f in (review or {}).get("facts", [])}
    for fact_index, fact in enumerate(annotation["facts"]):
        scope = fact.get("scope", {})
        source_refs = "; ".join(layout.evidence_ref(e) for e in fact.get("evidence", []))
        prefix = [
            layout.heading(f"{fact['id']} | {layout.KINDS.get(fact['kind'], fact['kind'])}", 3),
            layout.p(fact["statement"]),
            layout.p(f"归属：{scope.get('level')} / {scope.get('target')} | 原文：{source_refs}", "small"),
        ]
        if fact_index == 0:
            prefix.insert(0, fact_heading)
        checks = reviewed.get(fact["id"], {}).get("assessments", [])
        if checks:
            rows = [["运行", "初审", "理由与实际输出引用"]]
            for check in sorted(checks, key=lambda a: a["repetition"]):
                refs = ", ".join(check.get("references", [])) or "无局部引用"
                rows.append([str(check["repetition"]), VERDICTS[check["verdict"]], check["reason"] + "\n引用：" + refs])
            story += [KeepTogether([*prefix, layout.table(rows, [0.7, 1.3, 8])])]
            if fact_index + 1 < len(annotation["facts"]):
                story.append(Spacer(1, 8))
        else:
            story += [KeepTogether([*prefix, layout.p("初审未提供（仅排版预览）", "small")])]
    return story


def constraints_story(values, label):
    return [layout.p(f"{label}：[]", "small")] if not values else [
        layout.p(f"{label}[{index}]：{value}", "small") for index, value in enumerate(values)
    ]


def instruction_flowables(block_intro, instruction_story, instruction_index, opcode):
    if opcode in {"dispatch", "return"} and len(instruction_story) <= 6:
        return [KeepTogether([*block_intro, *instruction_story] if instruction_index == 0 else instruction_story)]
    if instruction_index == 0:
        return [KeepTogether([*block_intro, *instruction_story[:2]]), *instruction_story[2:]]
    return instruction_story


def trial_detail(material, trial, requested_model=None):
    sample, sid, repetition = material["sample"], material["sample"]["id"], trial["repetition"]
    record, analysis = trial["record"], trial["analysis"]
    title_text = f"{sid} / 第 {repetition} 次  实际输出明细"
    title = layout.heading(title_text, sample=f"{sid} / R{repetition}", toc=False)
    title.trial_key = f"{sid}/run-{repetition}"
    title.trial_title = title_text
    story = [PageBreak(), title, layout.p(sample["title"], "small"),
             layout.p(f"产物目录：{trial['path'].relative_to(BASE).as_posix()}", "small"),
             layout.p(f"结构状态：{record.get('status', 'not_run')} | 生成 {show(record.get('generation_attempts'))} | 修复 {show(record.get('repair_attempts'))} | HTTP 尝试 {show(record.get('http_attempts'))} | HTTP 重试 {show(record.get('http_retries'))}", "small")]
    if requested_model is not None:
        story.append(layout.p(f"请求模型：{requested_model}。以下返回名称逐项来自 trace，不用请求名称补齐。", "small"))
    for call in result_integrity.model_return_observations(trial.get("trace")):
        http_names = "；".join(
            f"HTTP {item['attempt']} ({show(item['http_status'])})：{show(item['returned_model'])}"
            for item in call["http_attempts"])
        story.append(layout.p(
            f"生成 {show(call['generation'])} 返回模型：{show(call['returned_model'])}"
            + (f" | {http_names}" if http_names else " | 没有 HTTP 尝试记录"), "small"))
    diagnostics = (analysis or {}).get("diagnostics", record.get("diagnostics", []))
    if record.get("error"):
        diagnostics = [*diagnostics, record["error"]]
    story += [layout.heading("诊断与失败边界", 2)]
    story += [layout.p(item, "small") for item in diagnostics] or [layout.p("diagnostics：[]。无结构诊断并不表示语义通过。", "small")]
    unknown_http = result_integrity.remote_unknown_attempts(trial.get("trace"))
    if unknown_http:
        story += [layout.p("流式请求的远端最终结果未知：" + "；".join(
            f"生成 {item['generation']} / HTTP 尝试 {item['http_attempt']} / 已接收 HTTP {item['http_status']}"
            for item in unknown_http), "h3"),
            layout.p("已收到成功响应头后，SSE 未达到完整结束条件；本地 error 不代表远端未生成结果，也不代表模型语义失败。未完成的流不能作为有效响应或有效 CFG，远端用量和最终处理结果以原始记录为准。", "small")]
    cfg = (analysis or {}).get("cfg")
    if not cfg:
        story += [layout.p("本次没有已接受的实际 CFG；不能补画或将候选当作有效图。原始响应／候选保存在同目录 trace.json、candidate.json 和 analysis.json（如生成）。")]
        if analysis and analysis.get("raw_candidate"):
            candidate = analysis["raw_candidate"]
            story += [layout.heading("未接受候选的结构化原文", 2)]
            # Keep rejected output inspectable without silently translating its IDs.
            text = json.dumps(candidate, ensure_ascii=False, indent=2)
            story += [layout.source(text.splitlines())]
        return story
    story += [layout.heading("Skill 层约束与上下文声明", 2),
              layout.p("declared_context_keys = " + json.dumps(cfg.get("declared_context_keys", []), ensure_ascii=False), "small")]
    story += constraints_story(cfg.get("constraints", []), "skill.constraints")
    story += [layout.heading("实际 CFG：分页邻接图", 2),
              layout.p("每个左框是实际 block ID；箭头连接到右框标明的目标 ID。目标可位于其他行／页，回边和独立组件保留原貌。edge_001 等按 analysis.cfg.edges 原数组顺序编为 1 起的检索标识；完整条件见紧随的边表。节点名称与操作见后续逐块明细。", "small")]
    edges = [(f"edge_{index:03d}", edge) for index, edge in enumerate(cfg.get("edges", []), 1)]
    outgoing = defaultdict(list)
    for edge_id, edge in edges:
        outgoing[edge["source_block_id"]].append((edge_id, edge["target_block_id"]))
    for block_id in cfg["blocks"]:
        targets = outgoing[block_id]
        chunks = [targets[index:index + 12] for index in range(0, len(targets), 12)] or [[]]
        for index, chunk in enumerate(chunks):
            story.append(GraphRow(block_id, chunk, entry=block_id == cfg["entry_block_id"] and not index, continuation=bool(index)))
    story += [layout.heading("完整控制流边与条件", 2)]
    story += [layout.table([["边标识", "源块 -> 目标块", "condition_text"]] + [
        [edge_id, f"{edge['source_block_id']} -> {edge['target_block_id']}", json.dumps(edge.get("condition_text"), ensure_ascii=False)]
        for edge_id, edge in edges
    ], [1.65, 3.6, 4.75])] if edges else [layout.p("edges：[]", "small")]
    operation_heading = layout.heading("全部操作、数据引用与约束落点", 2)
    for block_index, (block_id, block) in enumerate(cfg["blocks"].items()):
        block_intro = [layout.heading(f"{block_id}  {block['block_name']}", 3),
                       layout.p(f"data_source_kind = {json.dumps(block.get('data_source_kind'))}", "small")]
        if block_index == 0:
            block_intro.insert(0, operation_heading)
        block_intro += constraints_story(block.get("constraints", []), f"{block_id}.constraints")
        for instruction_index, instruction in enumerate(block["instructions"]):
            iid = instruction["id"]
            instruction_story = [layout.heading(f"{iid}  {instruction['opcode']}", 3)]
            for key in ["inputs", "outputs"]:
                operands = instruction.get(key, [])
                if not operands:
                    instruction_story += [layout.p(f"{key} = []", "small")]
                for index, operand in enumerate(operands):
                    instruction_story += [layout.p(f"{key}[{index}]  {operand_text(operand)}", "small")]
            instruction_story += constraints_story(instruction.get("constraints", []), f"{iid}.constraints")
            if instruction.get("draft_instruction_id"):
                instruction_story += [layout.p(f"draft_instruction_id = {instruction['draft_instruction_id']}", "small")]
            metadata = dict(instruction.get("metadata", {}))
            if "script_content" in metadata:
                script = metadata.pop("script_content")
                instruction_story += [layout.p(script_content_summary(script), "small")]
            if metadata:
                instruction_story += [layout.p("metadata = " + json.dumps(metadata, ensure_ascii=False, sort_keys=True), "small")]
            # Include a short terminator's final fields even when it opens a block.
            # Long operations keep only their opening with the block introduction.
            story += instruction_flowables(block_intro, instruction_story, instruction_index, instruction["opcode"])
        if not block["instructions"]:
            story += [KeepTogether(block_intro)]
    return story


def verify_content(path, materials, page_index, interim=False):
    """Check IDs and every operand/constraint in its own trial's page interval."""
    from pypdf import PdfReader

    reader = PdfReader(path)
    result_integrity.verify_page_bodies(reader.pages, margin=layout.MARGIN)
    pages = [page.extract_text() or "" for page in reader.pages]
    normalize = lambda value: "".join(str(value).split())
    whole = normalize("\n".join(pages))
    for material in materials:
        if interim and not material.get("review"):
            continue
        for fact in material["annotation"]["facts"]:
            if fact["id"] not in whole:
                raise ValueError(f"PDF omitted fact identifier: {fact['id']}")
    bounds = sorted((page, key) for key, page in page_index.items() if "/run-" in key)
    spans = {
        key: normalize("\n".join(pages[start - 1:(bounds[index + 1][0] - 1) if index + 1 < len(bounds) else len(pages)]))
        for index, (start, key) in enumerate(bounds)
    }
    counts = {"blocks": 0, "edges": 0, "instructions": 0, "operands": 0, "constraints": 0}
    for material in materials:
        for trial in material["trials"]:
            if interim and trial["record"].get("status") == "not_run":
                continue
            key = f"{material['sample']['id']}/run-{trial['repetition']}"
            text = spans[key]
            cfg = (trial["analysis"] or {}).get("cfg")
            if not cfg:
                continue
            expected = [cfg["entry_block_id"]]
            for index, edge in enumerate(cfg.get("edges", []), 1):
                expected += [f"edge_{index:03d}", edge["source_block_id"], edge["target_block_id"], json.dumps(edge.get("condition_text"), ensure_ascii=False)]
                counts["edges"] += 1
            constraint_values = list(cfg.get("constraints", []))
            for block_id, block in cfg["blocks"].items():
                expected += [block_id, block["block_name"]]
                counts["blocks"] += 1
                constraint_values += block.get("constraints", [])
                for instruction in block["instructions"]:
                    expected += [instruction["id"], instruction["opcode"]]
                    counts["instructions"] += 1
                    for operand in [*instruction.get("inputs", []), *instruction.get("outputs", [])]:
                        expected.append(operand_text(operand))
                        counts["operands"] += 1
                    constraint_values += instruction.get("constraints", [])
            counts["constraints"] += len(constraint_values)
            expected += constraint_values
            for value in expected:
                if normalize(value) not in text:
                    raise ValueError(f"PDF content missing in {key}: {str(value)[:160]}")
    for index, text in enumerate(pages, 1):
        if not text.rstrip().endswith(str(index)):
            raise ValueError(f"PDF footer page number mismatch: {index}")
    return {"status": "passed", "trial_scoped_ids_operands_constraints": counts, "visual_review": "required"}


if _PDF_IMPORT_ERROR is None and getattr(layout, "_PDF_IMPORT_ERROR", None) is None:
    class ExecutionDoc(ResultsDoc):
        def __init__(self, filename):
            super().__init__(filename)
            self.label = "Skill-IR 基线执行状态 | 未完成"
            self.title = "Skill-IR 基线执行状态报告"
            self.subject = "Interrupted baseline execution; no accepted model results or semantic assessments"
            self.footer_text = "基线执行未完成 | 未取得可复核模型结果"


def load_execution_status(args):
    sources = Sources()
    run = args.run_dir.resolve()
    report = sources.load(run / "report.json")
    if report.get("mode") != "online" or report.get("status") != "needs_attention":
        raise ValueError("Execution-status report requires a stopped needs_attention run")
    reconciliation = report.get("reconciliation", {})
    if reconciliation.get("offline") is not True or reconciliation.get("trace_bytes_unchanged") is not True:
        raise ValueError("Wait for offline reconciliation before generating the execution report")
    audit = sources.load(run / "reconciliation.json")
    if audit.get("reconciled_at") != reconciliation.get("reconciled_at") or audit.get("trace_sha256") != reconciliation.get("trace_sha256"):
        raise ValueError("Report and offline reconciliation audit disagree")
    samples = sources.load(FROZEN / "corpus.json")["samples"]
    freeze = sources.load(BASE / "freeze_manifest.json")
    approval = sources.load(BASE / "approval.json")
    migration = sources.load(BASE / "contract_v2" / "migration.json")
    sources.load(run / "experiment.json")
    sources.load(run / "dataset.json")
    expected = {(s["id"], r) for s in samples for r in [1, 2, 3]}
    lookup = {(t["case"], t["repetition"]): t for t in report["trials"] if t["variant"] == args.variant}
    if set(lookup) != expected or len(lookup) != 90:
        raise ValueError("Execution plan must preserve all 30 x 3 trials")
    affected = []
    for key, trial in lookup.items():
        if trial["status"] not in {"not_run", "uncertain"}:
            raise ValueError("This status-only mode is for interrupted execution without accepted results")
        path = run / trial["artifacts"]
        if (path / "analysis.json").exists():
            raise ValueError("Existing analysis requires the full results review mode")
        if trial["status"] == "not_run":
            continue
        record = sources.load(path / "record.json")
        if (record["case"], record["repetition"], record["status"]) != (*key, "uncertain"):
            raise ValueError(f"Reconciled record mismatch: {path}")
        trace = sources.load(path / "trace.json")
        for name, digest in record.get("artifact_sha256", {}).items():
            artifact = path / name
            if not artifact.is_file() or layout.sha(artifact) != digest:
                raise ValueError(f"Trial artifact mismatch: {artifact}")
            sources.add(artifact)
        affected.append({"record": record, "trace": trace, "path": path})
    for path in [Path(__file__), _SOURCE, _REVIEW_SOURCE]:
        sources.add(path)
    return sources, report, samples, freeze, approval, migration, affected


def build_execution_status(args):
    _require_pdf()
    sources, report, samples, freeze, approval, migration, affected = load_execution_status(args)
    layout.register_fonts(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    calls = [call for t in affected for call in t["trace"].get("calls", [])]
    http = [attempt for call in calls for attempt in call.get("http_attempts", [])]
    outcomes = Counter(a["status"] for a in http)
    known_failed = outcomes["error"]
    unknown = sum(count for state, count in outcomes.items() if state not in {"error", "complete"})
    not_run = sum(t["status"] == "not_run" for t in report["trials"])
    returned = sum(call.get("status") == "complete" for call in calls)
    if returned or any(a.get("usage") is not None for a in http):
        raise ValueError("This interruption report expects no returned result and unavailable usage")
    interruption = report.get("interruption", {})
    status_rows = [
        ["口径", "本次记录", "解释"],
        ["计划提取", "90", "30 份样例，每份重复 3 次"],
        ["受影响试验", str(len(affected)), "本地已停止，远端最终结果未知"],
        ["生成会话发起", str(len(calls)), "每个受影响试验均只发起首轮生成"],
        ["HTTP 尝试记录", str(len(http)), f"{known_failed} 条已失败；{unknown} 条中断时仍在进行"],
        ["返回结果 / 已接受 CFG", "0 / 0", "没有可做事实初审的模型输出"],
        ["结构修复", "0", "未收到候选，未进入结构修复"],
        ["尚未运行", str(not_run), "保留原计划，不填造结果"],
        ["Token 用量", "不可用（null）", "不是 0；没有收到用量记录"],
    ]
    story = [layout.p("Skill-IR 基线\n执行状态报告", "title"),
             layout.p("服务调用未完成，尚未形成语义基线结果", "h1"),
             layout.p(f"运行：{report['run_id']} | 版本：{args.variant} | 约束契约 v2", "small"),
             layout.p("本批次因服务响应失败和读取超时停止。已持久化记录只用于说明执行状态；本册没有事实通过率、逐事实初审或补造的 CFG。参考语料与判断依据已经共同确认，本地尚未收到可复核的模型提取结果。"),
             layout.table(status_rows, [2.5, 2.0, 5.5]), Spacer(1, 9),
             layout.p(f"{len(http)} 指 HTTP 尝试记录数量，不是 {len(http)} 次生成。最后 {unknown} 条记录在本地中断时仍为 running，远端是否完成未知。不可将中断视为远端已取消，也不可将缺少用量视为零消耗。"),
             layout.p("本报告由已停止批次的离线核对产物生成，生成过程不发送请求，也不执行 Skill 包内指令或脚本。", "small")]
    story += [PageBreak(), layout.heading("冻结材料与表达契约", sample="冻结与契约"),
              layout.p(f"已确认快照：{freeze['snapshot_id']}", "small"),
              layout.p(f"冻结日期：{freeze['frozen_on']} | 参考事实：{freeze['fact_count']} 条 | 输入包：24 个控制包 + 6 个真实包"),
              layout.p("真实包固定提交：49f948faa9258a0c61caceaf225e179651397431", "small"),
              layout.p("冻结包含全部语料、外置标注、共同确认记录、来源清单和迁移前生产 Prompt。输入与标注保持隔离，生产 Prompt 不读取事实标注。冻结记录使用工作目录文件字节摘要，不能只用仓库 HEAD 代替。"),
              layout.p("冻结内容摘要：" + freeze["content_sha256"], "small"),
              layout.heading("v1 到 v2：已确认的约束表达迁移", 2),
              layout.table([
                  ["作用范围", "候选 / 正式 IR", "字段"],
                  ["整份 Skill", "IRAnalysisCandidate / ControlFlowGraph", "constraints: list[str]"],
                  ["基本块", "CandidateBlock / BasicBlock", "constraints: list[str]"],
                  ["操作", "CandidateInstruction / IRInstruction", "constraints: list[str]"],
              ], [1.6, 5.8, 2.6]), Spacer(1, 8),
              layout.p("约束以原文和所在层级表达归属；默认空列表兼容旧 JSON，编译与序列化保留原层级。没有新增 effect、约束分类或复杂规则语言。Prompt 只追加最小契约说明，原有两份示例保持不变。真实读取、处理和传递仍须体现在操作数与控制流中。"),
              layout.p("正式基线与后续 Prompt 均采用 v2；字段新增本身不算 Prompt 优化收益。生产提取流程与 LLM 客户端未因本轮服务失败而改写。", "small"),
              layout.heading("试验计划与当前边界", 2),
              layout.p("开发集 22 份，共 66 次计划；保留验证集 8 份，共 24 次计划。本次只启动开发集的前 4 个试验。未产生可用于 Prompt 调整的语义证据，保留集仍未执行。")]
    matrix = [["样例", "划分", "第 1 次", "第 2 次", "第 3 次"]]
    lookup = {(t["case"], t["repetition"]): t for t in report["trials"]}
    for sample in samples:
        matrix.append([sample["id"], "开发" if sample["split"] == "development" else "保留"] + [
            "远端结果未知" if lookup[(sample["id"], rep)]["status"] == "uncertain" else "未运行" for rep in [1, 2, 3]
        ])
    matrix_table = layout.table(matrix, [1.0, 1.1, 2.65, 2.65, 2.6])
    matrix_table.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story += [PageBreak(), layout.heading("全部 90 次计划的状态矩阵", sample="试验计划"),
              layout.p("未知表示本地中断后未获得远端最终状态；未运行表示尚未发起生成。没有把任何一次记录当作已完成的语义提取。", "small"), matrix_table]
    for index, item in enumerate(affected):
        record, trace = item["record"], item["trace"]
        if index % 2 == 0:
            story.append(PageBreak())
        sid, rep = record["case"], record["repetition"]
        story += [layout.heading(f"{sid} / 第 {rep} 次：HTTP 执行记录", sample="HTTP 执行记录"),
                  layout.p(f"持久化状态：{record['status']} | 试验开始（UTC）：{record.get('started_at', '未记录')}", "small")]
        for call in trace.get("calls", []):
            story += [layout.p(f"生成 #{call['generation']} 开始（UTC）：{call.get('started_at', '未记录')} | 原始调用记录状态：{call['status']}", "small")]
            rows = [["HTTP", "状态", "代码", "已记录耗时", "错误类型 / 说明"]]
            for number, attempt in enumerate(call.get("http_attempts", []), 1):
                elapsed = attempt.get("elapsed_seconds")
                state = "已失败" if attempt["status"] == "error" else "最终结果未知"
                explanation = (attempt.get("error_type", "未记录") + "\n" + attempt.get("error", "本地中断时仍在进行；未收到状态、错误或用量记录。"))
                rows.append([str(number), state, show(attempt.get("http_status")), f"{elapsed:.3f} s" if elapsed is not None else "不可用", explanation])
            story += [layout.table(rows, [0.65, 1.35, 0.75, 1.35, 5.9]), Spacer(1, 12)]
        story += [layout.p(f"来源：{item['path'].relative_to(BASE).as_posix()}/trace.json", "small")]
    story += [PageBreak(), layout.heading("中断核对与后续边界", sample="后续边界"),
              layout.p("当前状态由离线核对生成，保留原始 trace 字节。四个原 running 试验标为 uncertain，未运行的 86 个试验保留 not_run，没有伪造服务器响应或初审文件。"),
              layout.p("中断说明：" + interruption.get("description", "未记录")),
              layout.p("精确中断时刻：" + show(interruption.get("occurred_at")) + "。原始记录没有精确 Ctrl-C 时间，不据耗时推算。", "small"),
              layout.p("观察时间（UTC）：" + show(interruption.get("observed_at")), "small"),
              layout.p("离线核对时间（UTC）：" + show(report["reconciliation"].get("reconciled_at")), "small"),
              layout.heading("恢复条件与结果复核", 2),
              layout.p("服务可用且四个在途请求的处置方式明确后，才继续本批次或显式建立重跑记录。保留每次请求的生成、结构修复与 HTTP 重试分层计数；未知请求不能被默默重放后当作原试验完成。"),
              layout.p("完成同一契约 v2 下每份 3 次、共 90 次提取后，再生成真正的结果复核 PDF。该模式已经实现：展示实际 CFG、全部操作与数据引用、约束落点、三次差异和外置逐事实初审；必须通过初审引用／摘要校验，再做逐页渲染检查。"),
              layout.p("当前没有可支持 Prompt 优化的语义结果，不作事实通过率判断、不编写样例专有补丁、不读取保留集结果反复调参。后续优化应以开发集的明确问题为依据，并在相同契约下检查保留集。"),
              layout.p("本册仅交付已核实的执行状态。它不表示基线运行或语义结果共同复核已经完成。", "h2")]
    doc = ExecutionDoc(args.output)
    doc.multiBuild(story, canvasmaker=layout.invariant_canvas)
    sources.check()
    from pypdf import PdfReader
    pages = [page.extract_text() or "" for page in PdfReader(args.output).pages]
    text = "".join("".join(pages).split())
    for sample in samples:
        if sample["id"] not in text:
            raise ValueError(f"Missing plan identifier: {sample['id']}")
    for index, page in enumerate(pages, 1):
        if not page.rstrip().endswith(str(index)):
            raise ValueError(f"Footer page mismatch: {index}")
    manifest = {
        "schema_version": 1, "report_kind": "execution_status_only", "run_id": report["run_id"],
        "pdf": args.output.name, "pdf_sha256": layout.sha(args.output), "pages": doc.page,
        "planned_trials": 90, "affected_trials": len(affected), "not_run": not_run,
        "initiated_generation_sessions": len(calls), "recorded_http_attempts": len(http),
        "known_failed_http_attempts": known_failed, "unknown_http_outcomes": unknown,
        "returned_results": returned, "accepted_cfgs": 0, "token_usage": None,
        "semantic_reviews_created": 0, "reportlab_version": REPORTLAB_VERSION,
        "fonts": layout.FONT_FILES,
        "source_sha256": {Path(path).relative_to(REPO).as_posix(): digest for path, digest in sorted(sources.hashes.items())},
        "content_verification": {"status": "passed", "sample_identifiers": 30, "page_numbers": doc.page, "visual_review": "required"},
    }
    args.output.with_name("execution_build_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"pdf": str(args.output), "pages": doc.page, "kind": "execution_status_only"}, ensure_ascii=False))


def model_identity_story(metadata):
    requested, change = metadata["requested"], metadata["provider_change"]
    story = [PageBreak(), layout.heading("运行身份与模型返回", sample="运行身份", toc=True),
             layout.p("有效请求配置来自本批次 experiment.json；返回模型名称来自已提交 trial 的 trace。请求名称和返回名称分别保留，不据名称差异推断等价模型、版本映射或服务器实现。"),
             layout.table([
                 ["字段", "本批次记录"],
                 ["版本 / 请求模型", f"{show(requested['id'])} / {show(requested['model'])}"],
                 ["Endpoint", show(requested["endpoint"])],
                 ["reasoning_effort", show(requested["reasoning_effort"])],
                 ["读取超时 / HTTP 额外重试", f"{show(requested['timeout_ms'])} ms / {show(requested['max_retries'])}"],
                 ["结构修复上限", show(requested["max_repair_rounds"])],
             ], [2.8, 7.2]), Spacer(1, 8),
             layout.heading("实际返回模型名称", 2),
             layout.table([["HTTP 返回名称", "尝试记录数"]] + [
                 [name, str(count)] for name, count in metadata["http_returned_model_counts"].items()
             ] + [["未返回 / 未记录（null）", str(metadata["http_attempts_without_returned_model"])]], [7.2, 2.8]),
             layout.p("计数单位是 HTTP 尝试记录，包含结构修复所发请求；不是样例数或三次重复数。缺少返回名称保持未记录，不能视为使用了请求模型。每次生成及 HTTP 的原始名称见试验明细。", "small")]
    if metadata["returned_names_differ_from_requested"]:
        story.append(layout.p("存在与请求字符串不同的返回名称：" + ", ".join(metadata["returned_names_differ_from_requested"]) + "。本报告不静默改写任一名称。", "h3"))
    if change:
        story += [PageBreak(), layout.heading("服务与模型变更来源", 2, sample="来源变更"),
                  layout.p(f"变更记录：{show(change['provider_change_id'])} | 授权日期：{show(change['authorized_on'])} | 继承旧 trial：{show(change['inherited_trials'])}", "small"),
                  layout.p("这是独立服务/模型基线。与旧批次的比较同时包含模型和服务变化，不能当作仅切换传输方式的收益，也不能合并旧批次补齐三次重复。"),
                  layout.p(f"来源记录的输入/Prompt 一致性：{show(change['case_and_prompt_identity_equal'])}；生产源码一致性：{show(change['production_source_identity_equal'])}。", "small")]
        for label, key in [("推理模式记录", "thinking_mode"), ("请求与返回名称说明", "requested_returned_model_note"),
                           ("预检计数边界", "preflight_not_baseline")]:
            if change.get(key) is not None:
                story.append(layout.p(label + "：" + str(change[key]), "small"))
        story += [layout.p("变更清单 SHA256：" + show(change["manifest_sha256"]), "small"),
                  layout.p("配置 SHA256：" + show(change["config_sha256"]), "small")]
        for prior in change["prior_runs"]:
            story.append(layout.p("关联旧批次：" + show(prior["directory"])
                                  + "\nexperiment SHA256：" + show(prior["experiment_sha256"])
                                  + "\nreport SHA256：" + show(prior["report_sha256"]), "small"))
    return story


def results_toc():
    story = layout.toc()[:-1]
    story[0].review_sample = "目录"
    return story


def build(args):
    _require_pdf()
    sources, report, materials = load_materials(args)
    interim = getattr(args, "interim_results", False)
    scope = sources.report_scope
    displayed = [m for m in materials if m["sample"]["id"] in scope["sample_ids"]]
    layout.register_fonts(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    trials = [trial for material in materials for trial in material["trials"]]
    states = Counter(t["record"].get("status", "not_run") for t in trials)
    transport = result_integrity.transport_metadata(sources.run_identity)
    model_identity = result_integrity.model_identity_metadata(sources.run_identity, args.variant, trials)
    unknown_http = sum(len(result_integrity.remote_unknown_attempts(t.get("trace"))) for t in trials)
    verdicts = Counter(a["verdict"] for m in materials for f in (m["review"] or {}).get("facts", []) for a in f["assessments"])
    attempted = sum(t["record"].get("status") in review_results.TERMINAL for t in trials)
    accepted_cfgs = result_integrity.accepted_cfg_count(trials)
    story = [layout.p("Skill-IR 阶段性结果复核\n基线未完成" if interim else "Skill-IR 语义基线\n实际结果复核", "title"),
             layout.p("完整计划：30 份冻结样例 x 3 次 = 90 次 | 约束契约 v2", "h1"),
             layout.p(f"运行：{report['run_id']} | 版本：{args.variant}", "small"),
             layout.p("传输协议：" + (transport["protocol"] or "未单独记录（旧批次）") + " | 请求传输参数：" + (json.dumps(transport["parameters"], ensure_ascii=False, sort_keys=True) if transport["parameters"] is not None else "未记录"), "small"),
             layout.p(f"收到成功响应头后仍未完成的流式请求：{unknown_http} 次。此类 trace 标为 remote_outcome_unknown；试验的 error 是本地传输状态，不能当作模型语义失败。流式与非流式运行按各自身份和协议分别呈现，不混合为同一批次。", "small"),
             layout.p("本文展示已持久化的模型输出和外置逐事实初审。参考事实已于 2026-09-10 共同确认；本册的模型结果仍待共同复核。结构校验成功、块数变化或一次成功都不是语义正确的证据。"),
             layout.p((f"本阶段已尝试 {attempted} 次，尚未运行 {states.get('not_run', 0)} 次；仅展开 {len(displayed)} 份已尝试样例及其终态记录。已有三次终态的 {len(scope['reviewed_sample_ids'])} 份样例给出逐事实初审；不足三次的样例仅报告执行状态，未运行项不填判定。" if interim else "前半册集中显示各样例三次运行的结构状态、修复和 HTTP 统计、差异及逐事实初审。") + "后半册提供已展示试验的实际 CFG、完整边条件、全部操作与输入输出、三层 constraints。参考原文的文件行号对应冻结语料，完整原文见已确认复核材料。"),
             layout.p("CFG 使用矢量分页邻接图：所有源节点和出边均保留；右框通过真实目标 ID 跨行／跨页引用。图不推断连边。操作数中的资源、上下文键、结果与字面量逐项区分。脚本原文仍存于 analysis.json，图和本册不会执行脚本或触发工具。"),
             layout.p("v1 到 v2 的三层约束字段只属于已确认表达契约迁移；本基线与后续 Prompt 使用相同契约，字段新增不计作优化收益。开发集 22 份、保留集 8 份；人工初审会保留无法判断和原文未决边界。"),
             layout.p("结构状态计数：" + json.dumps(dict(states), ensure_ascii=False)),
             layout.p("逐事实初审计数：" + "；".join(f"{VERDICTS[key]} {value}" for key, value in sorted(verdicts.items())), "small")]
    if args.allow_partial:
        story += [layout.p("排版预览：允许缺少试验或初审，不是最终交付。", "h1")]
    story += model_identity_story(model_identity)
    if interim:
        story += [PageBreak(), layout.heading("全量计划与当前执行状态", sample="全量计划", toc=True),
                  layout.p(f"完整计划保留 30 份 / 90 次。已接受 CFG 为 {accepted_cfgs} 个，error 为 {states.get('error', 0)} 次；两者都不直接代表语义通过率。开发集与保留集仍按已确认的 22 / 8 划分。"),
                  layout.table([["样例", "划分", "第 1 次", "第 2 次", "第 3 次", "本册范围"]] + [
                      [m["sample"]["id"], "开发" if m["sample"]["split"] == "development" else "保留",
                       *[t["record"].get("status", "not_run") for t in m["trials"]],
                       "事实初审" if m.get("review") else "执行状态" if m["sample"]["id"] in scope["sample_ids"] else "计划保留"]
                      for m in materials], [1.0, 1.0, 1.5, 1.5, 1.5, 2.0]),
                  layout.p("未运行试验不具有模型输出或语义判定；不同模型、服务或传输方式的批次相互独立，本册不拼入其他批次的结果。", "small")]
    story += [PageBreak(), *results_toc()]
    for material in displayed:
        story += sample_review(material, interim=interim)
    trial_index = TrialIndex()
    trial_index.levelStyles = [ParagraphStyle("trial-index", parent=layout.STYLES["small"], leading=13, spaceBefore=1)]
    trial_index.dotsMinLevel = 0
    story += [PageBreak(), layout.heading(f"附录：{len(scope['detail_trials'])} 次已尝试记录的实际输出" if interim else "附录：90 次提取的实际 CFG 与全部操作", sample="操作明细", toc=True),
              layout.p("按下列页码或 PDF 书签定位本册已展示的明细。正式 CFG 缺失时明确显示失败边界；不自动修饰候选或补造图。每条边的编号仅是本册按原边数组生成的可追溯索引。"), trial_index]
    detail_keys = set(scope["detail_trials"])
    for material in displayed:
        for trial in material["trials"]:
            if (material["sample"]["id"], trial["repetition"]) in detail_keys:
                story += trial_detail(material, trial, requested_model=model_identity["requested"]["model"])
    doc = ResultsDoc(args.output, interim=interim)
    doc.multiBuild(story, canvasmaker=layout.invariant_canvas)
    sources.check()
    content_verification = verify_content(args.output, displayed, doc.page_index, interim=interim)
    if interim:
        from pypdf import PdfReader
        all_text = "\n".join(page.extract_text() or "" for page in PdfReader(args.output).pages)
        if "阶段性结果" not in all_text or "基线未完成" not in all_text or "排版预览" in all_text or "布局预览" in all_text:
            raise ValueError("Interim PDF must be labelled as unfinished results, never a layout preview")
        if any(m["sample"]["id"] not in all_text for m in materials):
            raise ValueError("Interim PDF omitted a planned sample identifier")
    manifest = {
        "schema_version": 1, "run_id": report["run_id"], "variant": args.variant,
        "layout_preview": args.allow_partial, "pdf": args.output.name, "pdf_sha256": layout.sha(args.output),
        "report_kind": "interim_results" if interim else "layout_preview" if args.allow_partial else "full_results",
        "baseline_complete": not interim and not args.allow_partial,
        "pages": doc.page, "page_index": doc.page_index, "samples": len(materials), "trials": len(trials),
        "displayed_samples": scope["sample_ids"], "detailed_trials": len(scope["detail_trials"]),
        "reviewed_samples": scope["reviewed_sample_ids"], "attempted_trials": attempted,
        "accepted_cfgs": accepted_cfgs, "unrun_trials": states.get("not_run", 0),
        "fact_assessments": sum(verdicts.values()), "structural_status_counts": dict(states),
        "preliminary_verdict_counts": dict(verdicts), "reportlab_version": REPORTLAB_VERSION,
        "transport": transport, "remote_outcome_unknown_http_attempts": unknown_http,
        "model_identity": model_identity,
        "fonts": layout.FONT_FILES,
        "content_verification": content_verification,
        "source_sha256": {str(Path(path).relative_to(REPO).as_posix()): digest for path, digest in sorted(sources.hashes.items())},
        "verification": "Requires rendering and manual visual review; no automatic semantic approval",
    }
    args.output.with_name("build_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"pdf": str(args.output), "pages": doc.page, "samples": len(materials), "trials": len(trials), "fact_assessments": sum(verdicts.values())}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=BASE / "runs" / "baseline-sol-max-v1")
    parser.add_argument("--variant", help="Recorded variant ID; defaults to the run's sole variant")
    parser.add_argument("--output", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execution-status-only", action="store_true", help="Report a reconciled interruption without fabricating result reviews")
    mode.add_argument("--allow-partial", action="store_true", help="Layout preview only; prominently label missing trials and reviews")
    mode.add_argument("--interim-results", action="store_true", help="Deliver clearly unfinished actual results; retain the 90-trial plan and detail only attempted trials")
    parser.add_argument("--cjk-font")
    parser.add_argument("--mono-font")
    parser.add_argument("--fallback-font", action="append", default=[])
    args = parser.parse_args()
    _require_pdf()
    args.variant = result_integrity.select_result_variant(read_json(args.run_dir / "experiment.json"), args.variant)
    if args.output is None:
        filename = "skill-ir-baseline-execution-status.pdf" if args.execution_status_only else "skill-ir-baseline-interim-review.pdf" if args.interim_results else "skill-ir-baseline-results.pdf"
        args.output = REPO / "output" / "pdf" / "skill-ir-semantics-baseline" / filename
    (build_execution_status if args.execution_status_only else build)(args)


if __name__ == "__main__":
    main()
