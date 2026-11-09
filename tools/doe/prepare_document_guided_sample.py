"""Offline development material only; this module cannot construct a model client."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from skillflow.document_guided.source import source_packet, render_source
from skillflow.document_guided.prompts import build_flow_prompt, build_compact_graph_prompt, build_fragment_prompt
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.propagation.annotation.prompt_examples import endpoint_example
from skillflow.propagation.annotation.binding_examples import example_material
from skillflow.document_guided.cfg_wire import CFGWire, normalize_cfg_wire
from skillflow.document_guided.fragments import assemble_fragments, split_fragments, fragment_adapter, validate_fragment
from skillflow.document_guided.source_review import (
    build_source_review_prompt, prepare_review_material, validate_source_review,
    FRAGMENT_RESPONSE_ADAPTER,
)
from skillflow.task.material import prepare_task_material
from skillflow.task.prompts import build_task_prompt

RANGES = {
    "SKILL.md": [(1, 158)],
    "scripts/src/index.ts": [(1, 45), (278, 296)],
    "scripts/src/api/searchConsole.ts": [(1, 175)],
    "scripts/src/core/storage.ts": [(1, 171)],
    "scripts/src/config/settings.ts": [(1, 74)],
    "scripts/src/core/client.ts": [(1, 133)],
    "references/api-reference.md": [(197, 253), (356, 371)],
}

DOCS = {
    "flow": """# Flow — assistant-authored development notes

This document is not an accepted model response or a reference answer.

- The package offers independent capabilities; do not serialize every exported function into one task (SKILL.md:29-51).
- The selected path imports the Search Console helper under its actual alias, calls page performance first and country performance second, then returns their combined object (scripts/src/index.ts:1-45,278-296).
- Each helper has a separate query and response. Both queries can save their own result; the wrapper also saves the combined result. Keep three writes, not one (scripts/src/api/searchConsole.ts:89-175; scripts/src/index.ts:285-295).
- Saving is followed by reading the saved JSON and producing a Markdown summary in the declared workflow (SKILL.md:53-64).
- Unresolved: clicks versus impressions ranking language and Search Console versus GA4 date formats differ. Do not choose an interpretation silently (SKILL.md:85-112; references/api-reference.md:197-253; scripts/src/api/searchConsole.ts:48-83).
""",
    "processing": """# Processing — assistant-authored development notes

- Page and country requests use distinct dimensions and limits. Preserve their separate response identities and their association with the matching call (scripts/src/api/searchConsole.ts:89-175).
- Query storage defaults to enabled. The returned response is saved before returning to the wrapper; the wrapper separately stores an object containing both responses (scripts/src/api/searchConsole.ts:89-123; scripts/src/index.ts:285-295).
- saveResult writes a wrapper containing metadata (savedAt, category, operation, propertyId, optional extraInfo) and data. The file is not just the raw response (scripts/src/core/storage.ts:10-26,58-95).
- Settings and client construction obtain configuration and credentials; this does not establish that each credential is an explicit application query or saved-result field (scripts/src/config/settings.ts:1-74; scripts/src/core/client.ts:1-133).
- Acquisition and possible observation describe actual ranges. They do not establish a Task demand for the entire returned object. Runtime visibility defaults still apply unless an explicit supported mechanism narrows visibility.
- Unknown SDK internals, runtime filename collision occurrence, date compatibility and ranking semantics remain unresolved; do not invent mechanisms.
""",
    "task-correspondence": """# Task correspondence — assistant-authored development notes

This local note is not a new sealed Task and does not replace a complete Task.

- Relate the selected page-performance capability to the actual page and country calls, their separate parameters, and their combined return (SKILL.md:29-51,85-112; scripts/src/index.ts:278-296).
- Preserve the declared save/read/summarize workflow. Check the actual payload of each applicable write; an action demand alone does not express saved content (SKILL.md:53-64; scripts/src/api/searchConsole.ts:89-123; scripts/src/core/storage.ts:58-95).
- Distinguish automatic implementation metadata from independently required output. Do not make all currently saved metadata required solely because it is written.
- Keep rank wording and date-format conflicts explicit. Do not claim an exact ordering or date interpretation that the available material does not settle.
- No sensitivity document was used to decide these task correspondences. Whole reads do not seed whole-value requirements; missing supported bindings remain gaps.
""",
    "sensitivity": """# Sensitivity — assistant-authored development notes

- The source identifies service-account configuration including a private key; classify the actual credential value and its version using the setup and client evidence, not a guessed field in a response (SKILL.md:16-27; scripts/src/config/settings.ts:1-74; scripts/src/core/client.ts:1-133).
- Aggregate analytics dimensions and counts require contextual judgment. This note does not declare every response field sensitive or presume unknown personal identifiers.
- Credential use in client initialization is not proof of credential plaintext in response data or saved metadata. Preserve possible influence separately from explicit content.
- Saved property identifiers and returned analytics should be tied to their actual source and saved version before any final declaration. These notes neither modify processing nor decide DOE.
""",
}


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _write(root, name, value, *, refresh=False):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    raw = text.encode("utf-8")
    if path.exists():
        if path.read_bytes() == raw:
            return
        if not refresh:
            raise ValueError("Saved offline sample differs: " + str(path))
    path.write_bytes(raw)


def synthetic_material(root, *, refresh=False):
    """Author current model wire and expanded synthetic artifacts, never GA4 answers."""
    root = Path(root)
    fixture = deepcopy(endpoint_example())
    original = fixture["cfg"]
    wire = {"entry_block_ref": original["entry_block_id"],
        "constraints": original["constraints"], "blocks": [], "edges": []}
    for key, block in original["blocks"].items():
        instructions = [{name: deepcopy(value) for name, value in ir.items()
                         if name not in {"id", "draft_instruction_id"}}
                        for ir in block["instructions"]]
        for instruction in instructions:
            for operand in [*instruction.get("inputs", []), *instruction.get("outputs", [])]:
                operand.pop("semantic_name", None)
        wire["blocks"].append({"block_ref": key, "block_name": block["block_name"],
            "data_source_kind": block["data_source_kind"], "constraints": block["constraints"],
            "instructions": instructions})
    wire["edges"] = [{"source_block_ref": edge["source_block_id"],
        "target_block_ref": edge["target_block_id"], "condition_text": edge["condition_text"]}
        for edge in original["edges"]]
    CFGWire.model_validate(wire)
    candidate = normalize_cfg_wire(wire)
    graph = compile_candidate(candidate)
    if not graph.ok:
        raise ValueError("Synthetic whole graph failed compilation: " + repr(graph.diagnostics))
    cfg = json.loads(graph.cfg.to_json())
    ir_ids = {old["id"]: current["id"]
              for old_block, new_block in zip(original["blocks"].values(), cfg["blocks"].values(), strict=True)
              for old, current in zip(old_block["instructions"], new_block["instructions"], strict=True)}
    block_ids = dict(zip(original["blocks"], cfg["blocks"], strict=True))
    def relabel(value):
        if isinstance(value, list):
            return [relabel(item) for item in value]
        if isinstance(value, dict):
            return {key: ir_ids[item] if key == "instruction_id" else
                block_ids[item] if key == "block_id" else relabel(item)
                for key, item in value.items()}
        return value
    raw = relabel(fixture["annotation"])
    raw["ir_semantics"] = {ir_ids[key]: value for key, value in raw["ir_semantics"].items()}
    fixture["cfg"] = cfg
    material = example_material(fixture)
    evidence = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                "reason": "The authored synthetic source states this relationship."}
    annotation = {"outcome": "completed", "realizations": [
        {key: deepcopy(value) for key, value in row.items() if key != "status"}
        for row in raw["realizations"]], "ir_semantics": {},
        "locations": {name: {**deepcopy(location), "evidences": deepcopy(raw["location_evidences"][name])}
                      for name, location in raw["locations"].items()}}
    for ir_id, spec in raw["ir_semantics"].items():
        current = {"evidences": [deepcopy(evidence)]}
        segments = []
        for event in spec["events"]:
            if event.get("kind") != "processing":
                raise ValueError("This authored sample only converts its existing processing segments")
            segments.append({"mode": event["mode"], "ops": [deepcopy(operation)
                for child in event["events"] for operation in child["atomic_ops"]]})
        if segments:
            current["segments"] = segments
        if len(segments) > 1:
            current["order"] = spec["order"]
        for key in ("output_bindings", "sensitivity"):
            if spec.get(key):
                current[key] = deepcopy(spec[key])
        annotation["ir_semantics"][ir_id] = current
    fragments = split_fragments(annotation)
    for name, value in fragments.items():
        validate_fragment(name, value, material, processing=fragments["processing"])
    saved_wire, checked, compiled, mapping = assemble_fragments(fragments["processing"],
        fragments["task-correspondence"], fragments["sensitivity"], material)
    files = {"skill/" + row["path"]: row["content"] for row in material["source"]["files"]}
    global_text = "Preserve all obligations and unresolved statements in the supplied source; do not invent missing requirements or local mechanisms."
    flow = "# Flow understanding\nRead the session packet, prepare one calibration record, deliver it, and return internally. The interface deployment is unspecified (skill/SKILL.md:1).\nThe request uses the same acquired packet: preserve badge and conditionally include offset when adjustment is true. The acquisition result is consumed by the preparation step, not reacquired from another source (skill/SKILL.md:1)."
    # Reproduce the delivered v6 format fixture byte-for-byte. New v7 runs
    # explicitly select compact-v1; do not migrate this stored example.
    review_material = prepare_review_material(files=files, task=material["task"], cfg=cfg,
        annotation=saved_wire, compiled=compiled, mapping=mapping, runtime_contract=material["runtime_contract"],
        generation="fragment-v1", prompt_view=None)
    review_wire = {"outcome": "completed", "findings": []}
    review = validate_source_review(review_wire, review_material)
    prompts = {
        "01-task": build_task_prompt(prepare_task_material(material["source"]), allow_cannot_assess=False),
        "02-flow": build_flow_prompt(files=files, global_requirements=global_text),
        "03-cfg": build_compact_graph_prompt(files=files, documents={"flow": flow}, global_requirements=global_text),
        "04-processing": build_fragment_prompt("processing", files=files, cfg=cfg,
            documents={"flow": flow}, runtime_contract=material["runtime_contract"], global_requirements=global_text),
        "05-task-correspondence": build_fragment_prompt("task-correspondence", files=files, cfg=cfg,
            documents={"processing": fragments["processing"]}, task=material["task"], global_requirements=global_text),
        "06-sensitivity": build_fragment_prompt("sensitivity", files=files, cfg=cfg,
            documents={"processing": fragments["processing"]}, global_requirements=global_text),
        "07-source-review": build_source_review_prompt(review_material),
    }
    artifacts = {"context.json": material, "cfg-wire.json": wire, "graph-candidate.json": candidate,
        "cfg.json": cfg, "task-candidate.json": fixture["task_candidate"], "task.json": material["task"],
        "assembled-annotation.json": saved_wire, "flat-annotation.json": saved_wire,
        "backend-annotation.json": checked, "annotation.json": checked,
        "compiled-annotation.json": compiled, "source-review-wire.json": review_wire,
        "source-review.json": review, "source-review-input.json": review_material,
        "compilation-map.json": mapping, "flow.md": flow,
        "cfg-wire-schema.json": CFGWire.model_json_schema(),
        "source-review-schema.json": FRAGMENT_RESPONSE_ADAPTER.json_schema(),
        **{name + ".json": value for name, value in fragments.items()},
        **{name + "-schema.json": fragment_adapter(name).json_schema() for name in fragments},
        **{name + "-prompt.txt": value for name, value in prompts.items()}}
    for name, value in artifacts.items():
        _write(root, "synthetic/" + name, value, refresh=refresh)
    if refresh:
        for name in ("01-flow-prompt.txt", "02-relationships-prompt.txt", "flow-initial.md",
                     "07-annotation-prompt.txt", "08-source-review-prompt.txt",
                     "processing.md", "task-correspondence.md", "sensitivity.md"):
            path = root / "synthetic" / name
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError("Retired authored sample must remain inside its output directory")
            path.unlink(missing_ok=True)
    return {"annotation_compilation": "passed", "graph_compilation": "passed",
        "whole_graph_candidates": 1, "whole_annotations": 1,
        "program_assembled_annotations": 1, "annotation_model_calls": 0, "semantic_fragments": 3,
        "prompt_steps": {name: {"characters": len(value), "utf8_bytes": len(value.encode())}
                         for name, value in prompts.items()},
        "origin": "author-prepared typed fragments with actual program assembly; not model responses",
        "artifact_roles": {"cfg-wire.json": "authored model-facing CFG input",
            "graph-candidate.json": "program-expanded canonical candidate",
            "processing.json": "authored model-facing processing fragment",
            "task-correspondence.json": "authored model-facing correspondence fragment",
            "sensitivity.json": "authored model-facing sensitivity fragment",
            "assembled-annotation.json": "program assembly of the three typed fragments",
            "flat-annotation.json": "same program assembly, compatibility filename; not a model response",
            "backend-annotation.json": "program expansion", "annotation.json": "same program expansion, compatibility filename",
            "source-review-wire.json": "authored empty-finding shape demonstration, not a semantic pass"}}


def audit_sizes(run):
    """Render saved source/facts read-only; never replay or reclassify the run."""
    from skillflow.common.inputs.snapshot import read_snapshot
    from skillflow.graph.audit.prompts import source_controlled_prompt
    run = Path(run).resolve()
    old = run / "calls/r000/audit/a001/prompt.txt"
    controlled = run / "rounds/r000/controlled.json"
    old_bytes, document_bytes = old.read_bytes(), controlled.read_bytes()
    text = source_controlled_prompt(read_snapshot(run)[1], json.loads(document_bytes))
    return {"saved_prompt": str(old), "saved_prompt_sha256": digest(old_bytes),
        "controlled_sha256": digest(document_bytes),
        "old_logical_characters": len(old_bytes.decode("utf-8")), "old_logical_utf8_bytes": len(old_bytes),
        "new_rendered_characters": len(text), "new_rendered_utf8_bytes": len(text.encode()),
        "boundary": "Offline logical-prompt comparison only; not a new accepted response, transported request or token-cost measurement."}


def presentation(manifest):
    steps = manifest["validation"]["prompt_steps"]
    rows = "".join(f'<tr><td><a href="synthetic/{name}-prompt.txt">{name}</a></td>'
        f'<td>{size["characters"]:,}</td><td>{size["utf8_bytes"]:,}</td></tr>' for name, size in steps.items())
    audit = manifest.get("audit_prompt_comparison")
    comparison = (f'<p>GA4 保存的旧逻辑 Prompt：{audit["old_logical_characters"]:,} 字符／{audit["old_logical_utf8_bytes"]:,} 字节；'
        f'同一冻结材料的新渲染：{audit["new_rendered_characters"]:,} 字符／{audit["new_rendered_utf8_bytes"]:,} 字节。'
        '这里只比较完整逻辑输入；旧传输端可能另有重编码，不代表实际 token 或费用已经下降。</p>') if audit else ''
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SkillFlow · 同一分析的分步 Prompt</title>
<style>body{{font:17px/1.75 system-ui;margin:40px auto;max-width:1100px;padding:0 24px;color:#182536}}a{{color:#205fa8}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccd5e0;padding:10px;text-align:left}}pre{{white-space:pre-wrap;background:#eff4fa;padding:20px}}.note{{background:#fff5d9;padding:16px}}</style>
<h1>同一分析的分步 Prompt：离线样张</h1>
<p class="note">拆分的是每次请求的职责；分析对象始终是同一个完整 Skill。这里没有业务分组、子图拼接或标注批次合成。全部文档和输出都是明确标记的开发材料，不是新模型响应或 GA4 结论。</p>
<p><a href="../../docs/doe/document-guided-analysis.md">当前设计</a> · <a href="manifest.json">来源与规模</a> · <a href="README.md">样张说明</a></p>
<pre>源文 → 独立 Task（保持源文隔离）
源文 → 一份流程文档 → 一份完整 CFG wire → 程序编号与校验
完整 CFG + 完整冻结原文 → processing 类型化片段
固定 Task + processing → task-correspondence 类型化片段（不读取敏感性）
processing + 完整冻结原文 → sensitivity 类型化片段（不读取 Task）
三份片段 → 程序组装完整标注 → 统一 source review → 确定性后端
正常共七次请求；没有 annotation 模型调用；本样张没有启动模型</pre>
<p>Task 仅接收完整源文；processing 不接收 Task；任务对应和敏感性分别接收封存 processing。程序校验并组装三份实际片段，保留明确缺口，复制选定代码范围；不推断业务连接或生成任务需求。</p>
<h2>历史 GA4 开发笔记与原文样张</h2>
<p><a href="ga4/source-packet.md">带物理行号的局部原文</a> · <a href="ga4/source-selection.json">完整文件导航及选择范围</a></p>
<p><a href="ga4/README.md">历史笔记边界</a> · <a href="ga4/flow.md">流程</a> · <a href="ga4/processing.md">处理</a> · <a href="ga4/task-correspondence.md">任务对应</a> · <a href="ga4/sensitivity.md">敏感性</a>。这些旧版文字笔记不是当前类型化输出，也不是接受过的 GA4 答案。</p>
<p>选取原文 25,062 字符／25,115 UTF-8 字节；完整可读源包 154,973 字符／155,170 字节。局部样张保留独立查询及其返回、单项保存和合并保存、metadata、后续总结以及排名和日期冲突，不声称覆盖整个 Skill。历史 Task 删除逐行表的规模投影为 27,913 → 13,072 字符；没有把投影保存成合法的新 Task。</p>
{comparison}
<h2>独立合成示例：完整输入与完整输出</h2>
<p>同一设备校准示例贯穿下列步骤。源文、Task、CFG 和三个片段均由作者合成；实际程序组装与编译结果保存供复核，没有执行模型。</p>
<table><tr><th>实际渲染 Prompt</th><th>字符</th><th>UTF-8 字节</th></tr>{rows}</table>
<p><a href="synthetic/task-candidate.json">独立 Task 合成声明</a> → <a href="synthetic/task.json">程序封存 Task</a>；<a href="synthetic/flow.md">流程文档</a> → <a href="synthetic/cfg-wire.json">模型 CFG wire</a> → <a href="synthetic/graph-candidate.json">程序展开候选</a> → <a href="synthetic/cfg.json">编译 CFG</a></p>
<p><a href="synthetic/processing.json">processing 片段</a>（<a href="synthetic/processing-schema.json">schema</a>） · <a href="synthetic/task-correspondence.json">任务对应片段</a>（<a href="synthetic/task-correspondence-schema.json">schema</a>） · <a href="synthetic/sensitivity.json">敏感性片段</a>（<a href="synthetic/sensitivity-schema.json">schema</a>） → <a href="synthetic/assembled-annotation.json">程序组装标注</a> → <a href="synthetic/backend-annotation.json">程序展开标注</a> → <a href="synthetic/compiled-annotation.json">编译标注</a> · <a href="synthetic/compilation-map.json">含片段归属与 wire 坐标的映射</a></p>
<p><a href="synthetic/source-review-input.json">统一审查输入</a> · <a href="synthetic/source-review-wire.json">空 findings 格式演示</a>。空数组只是作者合成的格式示例，不是模型核对通过，也不是缺陷或 DOE 穷尽证明。</p>
<p><a href="synthetic/context.json">合成上下文（含独立 Task fixture）</a></p>
<h2>验证边界</h2><p>验证当前七份模板的职责、隔离、类型和程序组装关系；不以格式合法证明源文理解正确，不以输入较短预测成本。本生成器不生成 GA4 CFG、Task、标注或 DOE 答案，历史实验保持原样。</p>
<footer>2026-10-28 · 原 SkillFlow 目录 · 零模型调用</footer></html>'''


def prepare(source_root, legacy_task, output, *, refresh=False, audit_run=None):
    source_root, legacy_task, output = Path(source_root).resolve(), Path(legacy_task).resolve(), Path(output).resolve()
    if (output / "manifest.json").exists() and not refresh:
        raise ValueError("Use --refresh to replace these generated active samples; historical inputs remain read-only")
    files = {p.relative_to(source_root).as_posix(): p.read_bytes().decode("utf-8")
             for p in sorted(source_root.rglob("*")) if p.is_file()}
    original = {name: digest((source_root / name).read_bytes()) for name in files}
    task_bytes = legacy_task.read_bytes()
    spans = [{"file": "skill/" + name, "start_line": start, "end_line": end}
             for name, ranges in RANGES.items() for start, end in ranges]
    packet = source_packet({"skill/" + name: text for name, text in files.items()}, spans)
    raw = "".join(row["text"] for row in packet["ranges"])
    task = json.loads(task_bytes)
    projection = {key: value for key, value in task.items() if key != "source_accounting"}
    sizes = {"source_characters": len(raw), "source_utf8_bytes": len(raw.encode()),
             "full_readable_source_characters": sum(len(text) for text in files.values()),
             "full_readable_source_utf8_bytes": sum(len(text.encode()) for text in files.values()),
             "legacy_task_compact_characters": len(compact(task)),
             "task_projection_compact_characters": len(compact(projection))}
    expected = (25062, 25115, 154973, 27913, 13072)
    actual = tuple(sizes[key] for key in ("source_characters", "source_utf8_bytes",
                   "full_readable_source_characters", "legacy_task_compact_characters", "task_projection_compact_characters"))
    if actual != expected:
        raise ValueError(f"Frozen GA4 sample sizes differ: {actual!r}")
    output.mkdir(parents=True, exist_ok=True)
    _write(output, "ga4/source-packet.md", render_source(packet), refresh=refresh)
    _write(output, "ga4/source-selection.json", {key: packet[key] for key in ("files", "unreferenced_ranges")}
           | {"selected_ranges": spans, "coverage_is_semantic_proof": False}, refresh=refresh)
    for name, doc in DOCS.items():
        doc = doc.replace("SKILL.md", "skill/SKILL.md").replace("scripts/", "skill/scripts/").replace("references/", "skill/references/")
        doc = ("Historical prose notes from the earlier document prototype. These are not current typed fragment targets, accepted GA4 responses, or complete reference answers.\n\n" + doc)
        _write(output, f"ga4/{name}.md", doc, refresh=refresh)
    _write(output, "ga4/README.md", "# Historical GA4 development material\n\n"
        "The prose notes and local source selection are retained from an earlier prototype. They are not the current seven-call typed-fragment interface, accepted model responses, or GA4 reference answers. "
        "Current authored fragment shapes, seven prompts, schemas, and actual program assembly are illustrated only by the independent synthetic example. "
        "This generator reads the frozen GA4 source and historical Task without modifying them; it does not generate real GA4 analysis answers.\n", refresh=refresh)
    _write(output, "ga4/task-size-projection.txt", "SIZE-ONLY PROJECTION. Not a valid sealed Task or accepted response.\n"
           "No projected Task object is saved; original identity and bytes remain unchanged.\n" + json.dumps(sizes, indent=2), refresh=refresh)
    validation = synthetic_material(output, refresh=refresh)
    after = {name: digest((source_root / name).read_bytes()) for name in files}
    if original != after or legacy_task.read_bytes() != task_bytes:
        raise ValueError("Frozen source or historical Task changed during preparation")
    manifest = {"purpose": "offline development sample, not an experiment or model-accepted result",
                "source_root": str(source_root), "source_files_sha256": original,
                "historical_task": str(legacy_task), "historical_task_sha256": digest(task_bytes),
                "sizes": sizes, "validation": validation, "model_calls": 0,
                "historical_bytes_unchanged": True,
                "sample_schema": "skillflow-document-guided-authored-sample-v5"}
    if audit_run is not None:
        manifest["audit_prompt_comparison"] = audit_sizes(audit_run)
    if refresh:
        # Exact generated filenames from the retired sample, not a directory sweep.
        retired = ("combined-annotation.json", "combined-graph-candidate.json", "globals.json",
            "graph-1.json", "graph-2.json", "graph-globals.json", "ir-1.json", "ir-2.json",
            "locations-prompt.txt", "locations.json")
        for name in retired:
            path = output / "synthetic" / name
            if path.is_symlink() or not path.resolve().is_relative_to(output):
                raise ValueError("Retired sample path is not an ordinary generated file")
            if path.exists():
                path.unlink()
    _write(output, "index.html", presentation(manifest), refresh=refresh)
    _write(output, "README.md", "# 同一分析的分步 Prompt：离线样张\n\n"
        "请从[中文入口](index.html)开始。七次请求是独立 Task、流程文档、完整 CFG wire、processing 片段、任务对应片段、敏感性片段和统一 source review。"
        "程序从三份实际类型化片段组装 annotation，没有 annotation 模型调用；不按业务分组拼接 CFG 或标注批次。\n\n"
        "GA4 部分保留历史文字开发笔记，明确不是当前 typed fragment target，也不是接受的模型响应；synthetic/ 是独立设备校准 fixture 的作者合成片段、schemas、程序组装与七份实际模板。"
        "assembled-annotation.json 与兼容文件 flat-annotation.json 都是程序组装，annotation.json/backend-annotation.json 是程序展开；空 findings 是格式演示，不是审查通过。"
        "源文与历史 Task 保持原字节，原文样张范围保持；旧生成批次文件已从当前样张中移除，历史实验未修改。\n\n"
        "规模使用字符和 UTF-8 字节，不预测 token 或成本。复现命令为 `python -m tools.doe.prepare_document_guided_sample "
        "--source-root <frozen-package> --legacy-task <historical-task.json> --output examples/document-guided --refresh`，"
        "可附 `--audit-run <saved-graph-audit>` 只读比较逻辑 Prompt 规模。生成器不构造模型客户端。\n",
        refresh=refresh)
    _write(output, "manifest.json", manifest, refresh=refresh)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--legacy-task", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--refresh", action="store_true", help="Replace generated active examples only; never changes source inputs")
    parser.add_argument("--audit-run", help="Read-only saved graph audit for logical prompt-size comparison")
    args = parser.parse_args()
    print(json.dumps(prepare(args.source_root, args.legacy_task, args.output, refresh=args.refresh, audit_run=args.audit_run), ensure_ascii=False, indent=2))
