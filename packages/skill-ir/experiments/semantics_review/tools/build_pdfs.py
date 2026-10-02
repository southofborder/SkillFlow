"""Offline, deterministic review PDFs. This program never invokes Skill scripts or an LLM."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab import Version as REPORTLAB_VERSION
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, KeepTogether, LongTable, PageBreak, PageTemplate,
    Paragraph, Spacer, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
sys.path.insert(0, str(ROOT.parents[1] / "src"))
from skill_ir.inputs.skill_package import load_skill_package  # noqa: E402

PAGE_W, PAGE_H = A4
MARGIN = 46
WIDTH = PAGE_W - 2 * MARGIN
BLUE = colors.HexColor("#153B58")
TEAL = colors.HexColor("#136B70")
MUTED = colors.HexColor("#526271")
PALE = colors.HexColor("#F2F6F8")
RULE = colors.HexColor("#CCD8DE")
FONTS = []
FONT_FILES = []
GLYPH_CACHE = {}
STYLES = {}
GROUPS = {"notification": "条件通知与数据发送", "query": "查询调用与参数使用",
          "fallback": "工具选择与失败回退", "documents": "多文档处理与交付", "upstream": "真实 Skill"}
FORMS = {"numbered": "编号步骤", "prose": "自然语言段落", "table": "表格",
         "mixed": "跨文件混合", "purpose_delta": "最小差异：用途", "semantic_delta": "最小差异：语义", "original": "原始快照"}
KINDS = {"behavior": "行为", "condition": "条件", "data_flow": "数据流", "constraint": "约束", "must_not_infer": "不得凭空增加"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_fonts(args):
    candidates = [
        ("Body", args.cjk_font or os.environ.get("SKILL_REVIEW_CJK_FONT") or "C:/Windows/Fonts/simhei.ttf"),
        ("Code", args.mono_font or os.environ.get("SKILL_REVIEW_MONO_FONT") or "C:/Windows/Fonts/consola.ttf"),
    ]
    for optional in ["C:/Windows/Fonts/seguisym.ttf", "C:/Windows/Fonts/seguiemj.ttf"]:
        if Path(optional).exists():
            candidates.append((f"Symbol{len(candidates)}", optional))
    for optional in args.fallback_font:
        candidates.append((f"Fallback{len(candidates)}", optional))
    for name, path in candidates:
        path = Path(path)
        if not path.is_file():
            raise SystemExit(f"Font not found: {path}. Supply --cjk-font and --mono-font (TrueType outlines).")
        pdfmetrics.registerFont(TTFont(name, str(path)))
        FONTS.append(name)
        FONT_FILES.append({"role": name, "filename": path.name, "sha256": sha(path)})
    for name, size, leading, colour, space in [
        ("body", 10.2, 16, colors.black, 6), ("small", 8.7, 13, MUTED, 5),
        ("title", 26, 35, BLUE, 18), ("h1", 17, 25, BLUE, 12),
        ("h2", 12.5, 19, TEAL, 8), ("h3", 10.5, 16, BLUE, 6),
    ]:
        STYLES[name] = ParagraphStyle(name, fontName="Body", fontSize=size, leading=leading,
                                     textColor=colour, spaceAfter=space, wordWrap="CJK", alignment=TA_LEFT,
                                     keepWithNext=name in {"h1", "h2", "h3"})


def font_for(char, mono=False):
    key = (char, mono)
    if key not in GLYPH_CACHE:
        order = (["Code", "Body"] if mono else ["Body", "Code"]) + FONTS[2:]
        match = next((f for f in order if ord(char) in pdfmetrics.getFont(f).face.charToGlyph), None)
        if match is None:
            raise ValueError(f"No embedded font covers U+{ord(char):04X} {char!r}; provide --fallback-font.")
        GLYPH_CACHE[key] = match
    return GLYPH_CACHE[key]


def runs(value, mono=False):
    output = []
    for char in value:
        name = font_for(char, mono)
        if output and output[-1][0] == name:
            output[-1] = (name, output[-1][1] + char)
        else:
            output.append((name, char))
    return output


def markup(value, mono=False):
    value = str(value).replace("\t", "    ")
    return "<br/>".join("".join(f'<font name="{f}">{escape(t)}</font>' for f, t in runs(line, mono)) for line in value.split("\n"))


def p(value, style="body"):
    return Paragraph(markup(value), STYLES[style])


def label(value):
    item = p(value, "small")
    item.keepWithNext = True
    return item


def heading(value, level=1, sample=None, source=None, toc=False):
    item = p(value, f"h{level}")
    item.review_sample = sample
    item.review_source = source
    if toc:
        item.toc_title = value
    return item


class SourceLines(Flowable):
    """Lossless visible source, line-numbered and width-wrapped without reducing font size."""
    def __init__(self, lines=None, start=1, rows=None):
        super().__init__()
        self.lines = lines
        self.start = start
        self.rows = rows
        self.font_size = 9
        self.leading = 13
        self.gutter = 38
        self.spaceAfter = 8

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        if self.rows is None:
            self.rows = []
            limit = availWidth - self.gutter - 9
            for num, line in enumerate(self.lines, self.start):
                line = line.expandtabs(4)
                chunks, chunk, used = [], "", 0
                for char in line:
                    font = font_for(char, True)
                    width = pdfmetrics.stringWidth(char, font, self.font_size)
                    if used + width > limit and chunk:
                        chunks.append(chunk)
                        chunk, used = "", 0
                    chunk += char
                    used += width
                chunks.append(chunk)
                self.rows.extend([(str(num) if i == 0 else ">", text) for i, text in enumerate(chunks)])
        self.height = len(self.rows) * self.leading + 12
        return self.width, self.height

    def split(self, availWidth, availHeight):
        self.wrap(availWidth, availHeight)
        fit = int((availHeight - 12) // self.leading)
        if fit < min(3, len(self.rows)):
            return []
        if fit >= len(self.rows):
            return [self]
        # Avoid a one-line code start/end at a page boundary when a block can
        # provide at least three lines on both sides without changing font size.
        remaining = len(self.rows) - fit
        if remaining < 3 and fit >= 6:
            fit -= 3 - remaining
        return [SourceLines(rows=self.rows[:fit]), SourceLines(rows=self.rows[fit:])]

    def draw(self):
        c = self.canv
        c.setFillColor(PALE)
        c.rect(0, 0, self.width, self.height, stroke=0, fill=1)
        c.setStrokeColor(RULE)
        c.line(self.gutter - 6, 4, self.gutter - 6, self.height - 4)
        for index, (num, text) in enumerate(self.rows):
            y = self.height - 14 - index * self.leading
            c.setFillColor(MUTED)
            c.setFont("Code", 7.5)
            c.drawRightString(self.gutter - 11, y, num)
            x = self.gutter
            c.setFillColor(colors.HexColor("#1B2C39"))
            for font, part in runs(text, True):
                c.setFont(font, self.font_size)
                c.drawString(x, y, part)
                x += pdfmetrics.stringWidth(part, font, self.font_size)


def source(lines, start=1):
    return SourceLines(lines=lines, start=start)


def table(rows, ratios=None):
    # Cell paragraphs wrap; headers repeat and long rows may split at a page boundary.
    count = len(rows[0])
    widths = [WIDTH * r / sum(ratios) for r in ratios] if ratios else [WIDTH / count] * count
    data = [[p(cell, "small") for cell in row] for row in rows]
    item = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT", splitByRow=1, splitInRow=1)
    item.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EDF2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOX", (0, 0), (-1, -1), .4, RULE),
        ("INNERGRID", (0, 0), (-1, -1), .3, RULE), ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return item


def markdown_source(text):
    """Readable controlled Markdown; preserve fenced code, render genuine pipe tables."""
    lines = text.splitlines()
    story = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```") or (i == 0 and line.strip() == "---"):
            start = i
            marker = "```" if line.strip().startswith("```") else "---"
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith(marker):
                    i += 1
                    break
                i += 1
            story.extend([label(f"原文 L{start + 1}-L{i}"), source(lines[start:i], start + 1)])
        elif "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            start = i
            def cells(row):
                return [cell.strip() for cell in row.strip().strip("|").split("|")]
            rows = [cells(line)]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                row = cells(lines[i])
                if len(row) != len(rows[0]):
                    break
                rows.append(row)
                i += 1
            ratios = None
            if rows[0] in (["顺序", "作用", "要求"], ["Order", "Role", "Requirement"]):
                ratios = [0.8, 2.2, 7]
            elif rows[0][0] == "Argument" and len(rows[0]) == 3:
                ratios = [1.6, 4.2, 4.2]
            story.extend([label(f"原文表格 L{start + 1}-L{i}（保留表头与行关系）"), table(rows, ratios), Spacer(1, 8)])
        elif line.strip():
            # Retain Markdown markers as source cues, including list nesting and quotes.
            story.append(p(f"L{i + 1}  {line}", "small" if line.startswith("#") else "body"))
            i += 1
        else:
            story.append(Spacer(1, 5))
            i += 1
    return story


class ReviewDoc(BaseDocTemplate):
    def __init__(self, filename, label):
        super().__init__(str(filename), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=52, bottomMargin=48, title=label, author="SkillFlow",
                         subject="First-phase semantics review; all facts pending joint review")
        frame = Frame(MARGIN, 48, WIDTH, PAGE_H - 100, leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0, id="body")
        self.addPageTemplates(PageTemplate(id="normal", frames=frame))
        self.label = label
        self.sample_id = "规范与索引"
        self.source_name = ""
        self.page_index = {}

    def beforeDocument(self):
        self.sample_id = "规范与索引"
        self.source_name = ""
        self.page_index = {}

    def afterFlowable(self, item):
        if getattr(item, "review_sample", None):
            self.sample_id = item.review_sample
            self.source_name = ""
            self.page_index[self.sample_id] = self.page
        if getattr(item, "review_source", None):
            self.source_name = item.review_source
            self.page_index[f"{self.sample_id}/{self.source_name}"] = self.page
        if getattr(item, "toc_title", None):
            key = "section-" + str(len(self.page_index)) + "-" + str(self.page)
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(item.toc_title, key, 0, False)
            self.notify("TOCEntry", (0, markup(item.toc_title), self.page, key))

    def afterPage(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(RULE)
        c.line(MARGIN, PAGE_H - 34, PAGE_W - MARGIN, PAGE_H - 34)
        c.line(MARGIN, 35, PAGE_W - MARGIN, 35)
        c.setFont("Body", 8.2)
        c.setFillColor(MUTED)
        c.drawString(MARGIN, PAGE_H - 25, self.label)
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - 25, self.sample_id)
        # Long paths use a readable suffix in the footer; the full path is at the file boundary.
        footer = self.source_name
        if len(footer) > 75:
            footer = "..." + footer[-72:]
        c.drawString(MARGIN, 22, footer or "首阶段事实标注 | 待共同复核")
        c.drawRightString(PAGE_W - MARGIN, 22, f"{self.page}")
        c.restoreState()


def invariant_canvas(*args, **kwargs):
    kwargs["invariant"] = 1
    kwargs["pageCompression"] = 1
    return canvas.Canvas(*args, **kwargs)


def toc():
    item = TableOfContents()
    item.levelStyles = [ParagraphStyle("toc", parent=STYLES["body"], fontSize=9.5,
                                      leading=15, leftIndent=0, firstLineIndent=0, spaceBefore=3)]
    item.dotsMinLevel = 0
    return [heading("目录", 1), item, PageBreak()]


def sample_meta(sample):
    return (f"{sample['id']} | {GROUPS[sample['group']]} | {FORMS[sample['expression']]} | "
            f"{'开发集' if sample['split'] == 'development' else '保留验证集'} | {sample['language']}")


def build_appendix(samples, output):
    story = [p("Skill-IR 语义复核\n原文附册", "title"),
             p("六份真实 Skill 固定提交快照的全部可读取文本", "h1"),
             p("提交 49f948faa9258a0c61caceaf225e179651397431", "small"),
             p("本册通过当前生产加载器取得文本，逐文件、逐行完整呈现。灰底区为原文，左侧数字是文件原始行号；> 表示同一原始行的续行。代码采用 9 pt 字号并按页面宽度换行，不截断长行。制表符按 4 列展开。Markdown 表格保留原始表头、分隔符及行内容。"),
             p("每个文件从新页开始，页眉持续显示样例编号，页脚显示当前文件路径。二进制或不可解码文件只列清单，不进行 OCR；包外链接不自动下载。源文件字节及来源 manifest 是最终核对依据。本册不执行任何包内指令、代码、部署或 API 调用。"),
             p("每条事实初始状态为“待共同复核”。本册只提供原文，不包含模型输出或语义通过结论。"), PageBreak()]
    story += toc()
    counts = {}
    for sample in samples:
        if sample["kind"] != "upstream":
            continue
        package = load_skill_package(ROOT / sample["package_path"])
        readable = package.readable_files()
        counts[sample["id"]] = {"files": len(package.files), "readable_files": len(readable),
                                "source_lines": sum(len(f.content.splitlines()) for f in readable)}
        story += [heading(f"{sample['id']}  {sample['title']}", sample=sample["id"], toc=True),
                  p(sample_meta(sample), "small"), p(f"包路径：{sample['package_path']}", "small"),
                  p(f"文件共 {len(package.files)} 份；当前加载器可读取 {len(readable)} 份。", "body")]
        story.append(table([["包内文件", "字节数", "读取状态"]] +
                           [[f.path, str(f.size), "完整文本" if f.content is not None else "未读取：二进制/解码边界"] for f in package.files], [7, 1, 3]))
        for file in readable:
            story += [PageBreak(), heading(f"{sample['id']}  原文文件", 1, source=file.path),
                      p(file.path, "h2"), label(f"UTF-8 解码文本 | {file.size} 字节 | {len(file.content.splitlines())} 行"),
                      source(file.content.splitlines() or [""])]
        story.append(PageBreak())
    doc = ReviewDoc(output, "Skill-IR 语义复核 | 原文附册")
    doc.multiBuild(story, canvasmaker=invariant_canvas)
    return {"pages": doc.page, "page_index": doc.page_index, "packages": counts}


RULES = [
    ("实际读取、处理、调用、发送和返回", "提取操作、输入输出及控制流；数据获取与计算需分别保留。"),
    ("决定是否执行、执行哪个操作的条件", "保留条件及其读取的数据；条件文字不能代替结果引用。"),
    ("参数格式、前提、省略参数", "归属到具体调用；不能只因格式要求就新增转换或校验操作。"),
    ("工具优先级、禁止事项及例外", "保留规则与作用范围，不能等同于一次无条件调用。"),
    ("能力介绍与参数解释", "不单独制造执行；实际调用引用时保留相关要求。"),
    ("示例、引用、历史、反面教材", "依上下文判断是否参与当前执行，不能因命令句就加入执行路径。"),
    ("流程明确要求采用的示例", "保留被引用的实际行为，不能因章节名为示例就全部排除。"),
]


def evidence_ref(evidence):
    return f"{evidence['file']}:L{evidence['start_line']}-L{evidence['end_line']}"


def evidence_excerpts(annotation, package):
    intervals = defaultdict(list)
    for fact in annotation["facts"]:
        for e in fact["evidence"]:
            intervals[e["file"]].append((e["start_line"], e["end_line"]))
    lookup = {f.path: f for f in package.readable_files()}
    for path, ranges in sorted(intervals.items()):
        merged = []
        for first, last in sorted(ranges):
            if merged and first <= merged[-1][1] + 1:
                merged[-1] = (merged[-1][0], max(last, merged[-1][1]))
            else:
                merged.append((first, last))
        lines = lookup[path].content.splitlines()
        for first, last in merged:
            yield path, first, last, lines[first - 1:last]


def build_main(samples, matrix, appendix, output):
    story = [p("Skill-IR 语义复核\n首阶段主册", "title"),
             p("24 份控制样例 + 6 份真实 Skill", "h1"),
             p("先确认原文与事实，再开展提取实验。", "body"),
             p("所有事实：待共同复核", "h2"),
             p("范围：只制作与复核语料；不修改生产 Prompt、IR 模型或提取流程，不发起线上提取。已有三个独立回归示例不计入本批 30 份。图片、扫描 PDF、不可解码文件属于输入能力边界，不能计为 Prompt 漏提。"),
             p("阅读顺序：先核对判定规范与划分，再逐组比较 01-04 的等价表达以及 05、06 相对 01 的一句变化。真实 Skill 的证据摘录与事实表位于本册，完整可读文本见原文附册。"),
             p("来源：openai/skills，固定提交 49f948faa9258a0c61caceaf225e179651397431。所有注释与答案均放在 Skill 包外；本册属于复核材料，不得作为模型输入。", "small"), PageBreak()]
    story += toc()
    story += [heading("判定规范与约束归属", toc=True), table([["原文作用", "预期表达"]] + [list(r) for r in RULES], [3, 7]), Spacer(1, 10),
              p("约束采用“原文 + 作用范围”。拟议字段为 constraints: list[str]，放置层级表示整份 Skill、某个基本块或某条操作；本阶段只展示约定，不改生产模型。无法确定范围的事实标为 unresolved / 待共同确认，不擅自提升为全局规则。"),
              p("真实数据读取、处理及传递必须保留为操作数和控制流，不能只放在 constraints 中。简洁、语气与回答长度为低优先级，不能凭此新增流程步骤。文档确实要求的可疑行为也需描述和保留；分析器不执行它们，不添加攻击分类、effect 或审计结论。"),
              p("标注记录必须保留的事实与约束、不得凭空增加的行为、可接受表达及争议项。不固定 opcode、结果编号或唯一 CFG。表格证据保留表头，跨文件证据保留入口引用。空白复核意见供人工填写，任何结构检查成功均不代表语义已经通过。"), PageBreak(),
              heading("数据划分与后续边界", toc=True),
              table([["集合", "控制组", "真实 Skill", "份数"],
                     ["开发集", "通知 N / 回退 F / 多文档 D", "R01 pdf / R02 playwright / R03 gh-fix-ci / R04 netlify-deploy", "22"],
                     ["保留验证集", "查询参数 Q", "R05 linear / R06 transcribe", "8"]], [1.2, 2.7, 5, .6]), Spacer(1, 12),
              p("整组划分，禁止将等价版本分散到开发与保留集。保留集不得用于编写 Prompt 示例，也不用于当前轮反复调参。通知与多文档组使用中文，查询与回退组使用英文；同一组不混合语言因素。"),
              p("二次复核边界：additional_behavior 只检查依赖主流程结果的附加写入；本批未覆盖互不相关的独立行为组件及不凭空连边能力。04 版的 JSON/YAML 为已提供的固定规则，不能仅因跨文件声明就新增运行时读取。黑盒调用仍需保留可观察文件读写及返回值。真实包检查表不是所有可选工作流的穷举，未列出的行为仍须回到原文判断。"),
              p("共同确认样例与规则后才能冻结语料、标注和 Prompt 快照；单独处理约束契约变更；同契约下每样例每版本重复 3 次，全量每版 90 次。结构修复与 HTTP 重试分别记录。下一阶段复核实际 CFG、数据引用、约束落点、三次差异及人工初审。上述实验不在本次生成器中运行。"),
              heading("覆盖目标索引", 2)]
    target_samples = defaultdict(set)
    for row in matrix["rows"]:
        target_samples[row["target"]].add(row["sample_id"])
    story.append(table([["覆盖目标", "样例编号（逐事实证据见 coverage_matrix.json / .csv / .md）"]] +
                       [[target, ", ".join(sorted(ids))] for target, ids in sorted(target_samples.items())], [3, 7]))
    for sample in samples:
        ann = json.loads((ROOT / sample["annotation_path"]).read_text(encoding="utf-8"))
        package = load_skill_package(ROOT / sample["package_path"])
        story += [PageBreak(), heading(f"{sample['id']}  {sample['title']}", sample=sample["id"], toc=True),
                  p(sample_meta(sample), "small"), p(f"唯一输入目录：{sample['package_path']}", "small"),
                  p(f"包外标注：{sample['annotation_path']}", "small")]
        delta = ann.get("minimal_pair")
        if delta:
            story += [heading("与基准版本的一句差异", 2),
                      p(f"基准：{delta['base_id']}。{delta['change']}"),
                      p("应变化事实：" + ", ".join(delta["changed_fact_ids"]), "small"),
                      p("其余保持：" + ", ".join(delta["unchanged_fact_ids"]), "small")]
        elif sample["kind"] == "controlled":
            story.append(p("本组 01-04 保留相同核心事实；仅改变表达形式和文档组织。", "small"))
        if sample["kind"] == "controlled":
            story.append(heading("完整控制样例原文", 2))
            for file in package.readable_files():
                story += [heading(file.path, 3, source=file.path)]
                story += markdown_source(file.content) if file.kind == "markdown" else [source(file.content.splitlines() or [""])]
        else:
            story += [p("固定来源：https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431", "small"),
                      p(f"原文附册起始页：{appendix['page_index'][sample['id']]}。包内文件 {len(package.files)} 份，可读文本 {len(package.readable_files())} 份。完整字节哈希和未提供链接见 {sample['provenance_path']}。", "small"),
                      heading("事实证据原文摘录", 2)]
            for path, first, last, lines in evidence_excerpts(ann, package):
                page = appendix["page_index"].get(f"{sample['id']}/{path}")
                story += [heading(f"{path}  L{first}-L{last}", 3, source=path),
                          label(f"完整文件见原文附册第 {page} 页起。"), source(lines, first)]
        for index, fact in enumerate(ann["facts"]):
            scope = fact["scope"]
            prefix = [heading("外置事实检查表", 2)] if index == 0 else []
            story.append(KeepTogether(prefix + [heading(f"{fact['id']} | {KINDS[fact['kind']]} | 待共同复核", 3),
                      p(fact["statement"]), p(f"作用范围：{scope['level']} / {scope['target']}", "small"),
                      p("原文证据：" + "；".join(evidence_ref(e) for e in fact["evidence"]), "small"),
                      p("复核意见：________________________________________________", "small")]))
        notes = [heading("可接受表达与待确认项", 2)]
        for value in ann["acceptable_variants"]:
            notes.append(p("可接受：" + value))
        for value in ann["open_questions"]:
            notes.append(p("待共同确认：" + value))
        if not ann["open_questions"]:
            notes.append(p("尚未预设争议项；仍需逐条共同复核，不预填通过结论。", "small"))
        story.append(KeepTogether(notes))
    doc = ReviewDoc(output, "Skill-IR 语义复核 | 首阶段主册")
    doc.multiBuild(story, canvasmaker=invariant_canvas)
    return {"pages": doc.page, "page_index": doc.page_index}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPO / "output/pdf/skill-ir-semantics-review")
    parser.add_argument("--cjk-font")
    parser.add_argument("--mono-font")
    parser.add_argument("--fallback-font", action="append", default=[])
    args = parser.parse_args()
    register_fonts(args)
    corpus = json.loads((ROOT / "corpus.json").read_text(encoding="utf-8"))
    matrix = json.loads((ROOT / "coverage_matrix.json").read_text(encoding="utf-8"))
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    appendix_path = output / "skill-ir-full-source-appendix.pdf"
    main_path = output / "skill-ir-semantics-review.pdf"
    appendix = build_appendix(corpus["samples"], appendix_path)
    print(f"Appendix: {appendix['pages']} pages", flush=True)
    review = build_main(corpus["samples"], matrix, appendix, main_path)
    print(f"Review: {review['pages']} pages", flush=True)
    # Byte hashes pin both the generator's inputs and exact font environment.
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    manifest = {"schema_version": 1, "reportlab_version": REPORTLAB_VERSION,
                "fonts": FONT_FILES, "source_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in files},
                "production_loader_sha256": sha(ROOT.parents[1] / "src/skill_ir/inputs/skill_package.py"),
                "outputs": {main_path.name: {"sha256": sha(main_path), **review},
                            appendix_path.name: {"sha256": sha(appendix_path), **appendix}},
                "all_fact_status": "待共同复核", "online_extractions": 0}
    (output / "build_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(output, flush=True)


if __name__ == "__main__":
    main()
