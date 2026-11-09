"""Assemble local human-review copies; never edit production or dispatch calls."""
from pathlib import Path
import ast
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


stages = [
    ("environment", "00 调用外壳与环境确认", "已调用", "隔离研究输入；确认本机 CLI 的实际配置。"),
    ("task", "01 独立 Task", "已完成", "只读完整 Skill 源文，提取目的、要求与冲突。"),
    ("flow", "02 流程理解", "已完成", "读完整源包，形成同一 Skill 的流程工作文档。"),
    ("relationships", "03 补全跨文件关系", "已完成", "更新同一流程文档，保留生产、消费、版本、控制与共享状态。"),
    ("graph", "04 完整 CFG 填写", "已完成；一次结构纠正", "提交一份完整图候选；程序复制明确的代码范围并编译。"),
    ("graph-review", "05 源文—图核对", "已完成；一次结构纠正", "完整源文与受控图事实比较，报告具体遗漏和误译。"),
    ("graph-repair", "06 图语义修复", "本次已执行", "相同构图模板附本次有效反馈，提交完整替换候选。"),
    ("graph-rereview", "07 图独立复审", "本次已执行", "相同核对模板；读取修复后的图，不读取初审意见。"),
    ("processing", "08 数据处理理解", "文档已完成；下一步交接失败", "解释获取、加工、观察、交付、保存和版本；读取运行时契约。"),
    ("task-correspondence", "09 任务对应", "尚未发出请求：当前模板", "固定 Task 对应实际使用位置和限制，不读取敏感性文档。"),
    ("sensitivity", "10 敏感性判断", "尚未发出请求：当前模板", "源文和处理文档支持敏感范围及版本，不改任务需求。"),
    ("annotation", "11 完整联合标注", "尚未发出请求：当前模板", "继承三份文档，填一份现有严格格式的完整标注。"),
    ("review", "12 全局语义初审", "尚未发出请求：当前模板", "检查源文、Task、需求／限制声明与 IR；不看 DOE 结果。"),
    ("annotation-repair", "13 固定 Task 标注修复", "条件分支；本次预算已用于图修复", "使用完整标注模板与受控反馈；不是另一份自由裁决。"),
    ("task-revision", "14 隔离 Task 修订", "条件分支；本次预算已用于图修复", "只接收源文、旧 Task 和有限异议，不接收图或载荷。"),
    ("rereview", "15 标注独立复审", "条件分支：当前模板", "与初审职责相同，独立读取当前候选。"),
    ("structural-correction", "16 结构纠正", "本次已发生两次", "同阶段材料、当前候选和机械诊断；完整替换，不补造语义。"),
    ("shared", "共用规则、显示与格式", "按使用阶段注入", "同一规则仅列一份。语义规则、格式图例和纯显示标签分别保留。"),
]
stages = [(key, title, "当前模板；本次未调用", description) for key, title, _status, description in stages]
manifest = read(HERE / "manifest.json")
blocks = []
for name in ("documents-task", "annotation-review", "audit-correction", "runtime-contract"):
    blocks.extend(read(HERE / "parts" / (name + ".json")))
assert len({row["id"] for row in blocks}) == len(blocks)
rank = {row[0]: i for i, row in enumerate(stages)}
for block in blocks:
    assert block["english"] and block["chinese"]
    assert "\ufffd" not in block["english"] + block["chinese"]
    assert set(block["stages"]) <= set(rank)
    source = ROOT / block["source_file"]
    assert source.is_file()
    block["source_link"] = Path(os.path.relpath(source, HERE)).as_posix()
    block["english_sha256"] = hashlib.sha256(block["english"].encode()).hexdigest()
    block["source_sha256"] = digest(source)
blocks.sort(key=lambda b: min(rank[s] for s in b["stages"]))

labels = {s[0]: s[1][3:] if s[1][:2].isdigit() else s[1] for s in stages}
requests = manifest["requests"]
counts = {}
for row in requests:
    stage = row["stage"]
    counts[stage] = counts.get(stage, 0) + 1
    row["label"] = "旧契约 · " + labels[stage] + (f" · 结构纠正 {counts[stage]-1}" if counts[stage] > 1 else "")
    # Decode bytes directly: text-mode newline normalization is inappropriate here.
    actual = (HERE / row["actual"]).resolve()
    row["characters"] = len(actual.read_bytes().decode("utf-8"))
    assert digest(actual) == row["actual_sha256"]
    assert digest((HERE / row["core"]).resolve()) == row["core_sha256"]

formats = [{"title": title, "text": f"formats/{name}.txt", "schema": f"formats/{name}.schema.json"}
           for name, title in [("task", "Task"), ("cfg", "完整 CFG"),
                               ("annotation", "完整标注"), ("review", "语义审查")]]
payload = {"stages": [dict(zip(("id", "title", "status", "description"), s)) for s in stages],
           "blocks": blocks, "requests": requests, "formats": formats,
           "examples": [{"title": "当前审查的完整合成样例 JSON", "path": "parts/review-examples.json"}]}
(HERE / "review-data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
(HERE / "review-data.js").write_text("window.SKILLFLOW_PROMPT_REVIEW=" +
    json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c") + ";\n", encoding="utf-8")
text = ["SkillFlow 当前提示词中英对照人工审阅稿", "2026-10-27；Skill-only 当前模板。页面编辑不会自动应用到生产。",
        "英文原文保持代码中的文本；中文为人工审阅译文。格式与完整实际输入见 index.html。",
        "请在各段英文、中文或人工备注中修改；不要改写冻结的历史请求。", ""]
for b in blocks:
    text.extend([f"{b['id']} · {b['title']}", f"来源：{b['source_file']} :: {b['symbol']}",
                 "使用阶段：" + "、".join(labels[s] for s in b["stages"]), "", "[ENGLISH]",
                 b["english"], "", "[中文对照]", b["chinese"], "", "[人工备注]", "", "="*75, ""])
(HERE / "review.txt").write_text("\n".join(text), encoding="utf-8")
changed = [name for name, value in manifest["production_source_hashes"].items() if digest(ROOT / name) != value]
changed += [name for name, value in manifest["tools"].items() if digest(ROOT / name) != value]
assert not changed, changed
assert len(list((Path(manifest["run"]) / "transport").rglob("started.json"))) == len(requests)
for f in formats:
    assert (HERE / f["text"]).is_file() and (HERE / f["schema"]).is_file()
for b in blocks:
    assert (HERE / b["source_link"]).is_file()
verification = {"bilingual_blocks": len(blocks), "english_characters_across_blocks": sum(len(b["english"]) for b in blocks),
    "chinese_characters_across_blocks": sum(len(b["chinese"]) for b in blocks),
    "actual_requests": len(requests), "current_templates_match_source_snapshot": True, "existing_requests_unchanged": True,
    "new_model_requests": 0, "format_references": len(formats),
    "notice": "Character counts describe this library, not one request or tokenizer cost. Full input data is linked, not translated.",
    "scope": "Active document-guided route; unused batch helpers and legacy monolithic graph prompts excluded."}
(HERE / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8")
(HERE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(verification, ensure_ascii=False, indent=2))
