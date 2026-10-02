"""Exercise the local SVG/PNG renderer with edge cases absent from the corpus."""
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import pytest


BASE = Path(__file__).resolve().parents[2] / "experiments/semantics_baseline"
RUNTIME = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node"
MODULES = RUNTIME / "node_modules"
NODE = RUNTIME / "bin/node.exe"
BROWSER = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
RENDERER_READY = (NODE.is_file() and BROWSER.is_file()
                  and (MODULES / "@viz-js/viz/package.json").is_file()
                  and (MODULES / "playwright/package.json").is_file())


@pytest.mark.skipif(not RENDERER_READY, reason="Optional bundled renderer and local browser not installed")
@pytest.mark.parametrize("compact", [False, True], ids=["branch-and-text-boundaries", "smaller-than-viewport"])
def test_offline_renderer_preserves_disconnected_nodes_parallel_edges_and_typed_literals(tmp_path, compact):
    def block(number, instructions, constraints=None):
        return {"block_id": f"block_{number:03}", "block_name": f"中文块 {number} <&> \"测试\"",
                "data_source_kind": None, "constraints": constraints or [], "instructions": instructions}

    def instruction(number, inputs, outputs=None, constraints=None):
        return {"id": f"ir_{number:03}", "opcode": "synthetic_operation",
                "inputs": inputs, "outputs": outputs or [], "constraints": constraints or [],
                "draft_instruction_id": f"synthetic_{number}",
                "metadata": {"script_content": "DO_NOT_RENDER_SCRIPT_SENTINEL"}}

    def edge(source, target, condition):
        return {"source_block_id": f"block_{source:03}", "target_block_id": f"block_{target:03}",
                "condition_text": condition}

    output = {"type": "result", "identifier": "result_001", "semantic_name": "中文结果 <&>"}
    cfg = {
        "entry_block_id": "block_001", "declared_context_keys": ["request"],
        "constraints": ["全局约束：<不得执行> & 保留真实范围。"],
        "blocks": {
            "block_001": block(1, [instruction(1, [{"type": "external_resource", "identifier": "资料<&>.md"}],
                                                     [output], ["保留中英文 mixed_field_" * 18])], ["块级约束：第一行\n第二行"]),
            "block_002": block(2, [instruction(2, [output])]),
            "block_003": block(3, [instruction(3, [])]),
            "block_004": block(4, [instruction(4, [{"type": "literal", "literal_value": False},
                                                     {"type": "literal", "literal_value": 0},
                                                     {"type": "literal", "literal_value": {"文本": "<&>\"", "list": []}}])]),
        },
        # Node 4 is disconnected. Edges 4/5 are exact duplicates. Null and empty
        # conditions are distinct, and the loop must not be discarded.
        "edges": [edge(1, 2, None), edge(2, 2, "继续循环 <&>"), edge(2, 3, ""),
                  edge(2, 3, "条件相同"), edge(2, 3, "条件相同")],
    }
    expected_counts = {"blocks": 4, "edges": 5, "instructions": 4,
                       "inputs": 5, "outputs": 1, "skill_constraints": 1,
                       "block_constraints": 1, "instruction_constraints": 1}
    if compact:
        cfg = {"entry_block_id": "block_001", "declared_context_keys": [], "constraints": [],
               "blocks": {"block_001": block(1, [instruction(1, [])])}, "edges": []}
        expected_counts = {"blocks": 1, "edges": 0, "instructions": 1,
                           "inputs": 0, "outputs": 0, "skill_constraints": 0,
                           "block_constraints": 0, "instruction_constraints": 0}
    sample = {"index": 1, "sample_id": "SYNTHETIC", "skill_name": "renderer-regression",
              "basename": "001-renderer-regression", "repetition": 1, "run_id": "synthetic-offline-fixture",
              "analysis_sha256": "0" * 64, "cfg": cfg}
    payload = tmp_path / "input.json"
    payload.write_text(json.dumps({"samples": [sample]}, ensure_ascii=False), encoding="utf-8")
    audit_path, pictures = tmp_path / "audit.json", tmp_path / "pictures"
    command = [str(NODE), str(BASE / "tools/render_review_cfg.mjs"), "--input", str(payload),
               "--output-dir", str(pictures), "--audit", str(audit_path),
               "--node-modules", str(MODULES), "--browser", str(BROWSER)]
    process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert process.returncode == 0, process.stderr + process.stdout
    rows = json.loads(audit_path.read_text(encoding="utf-8"))["samples"]
    assert len(rows) == 1 and rows[0]["basename"] == sample["basename"]
    assert rows[0]["counts"] == expected_counts
    assert rows[0]["kind"] == "cfg" and rows[0]["identity_checks_passed"]
    assert rows[0]["text_checks_passed"] and rows[0]["bounds_checks_passed"]
    assert any(item.get("expected") == "001  renderer-regression" for item in rows[0]["text_checks"])
    assert sorted(path.name for path in pictures.iterdir()) == [sample["basename"] + ".png"]
    from PIL import Image
    with Image.open(pictures / (sample["basename"] + ".png")) as image:
        image.load()
        assert image.format == "PNG"
        assert image.size == (rows[0]["width"], rows[0]["height"])
        assert image.width > 500 and image.height > 500
        if compact:
            assert image.width < 1280 and image.height < 960


@pytest.mark.skipif(not RENDERER_READY, reason="Optional bundled renderer and local browser not installed")
def test_provenance_failure_cards_and_actual_instruction_ids_in_optional_svg(tmp_path):
    block_id, ir_id = 'block-<&>"中文', 'operation-<&>"结果'
    cfg = {
        "entry_block_id": block_id, "declared_context_keys": [], "constraints": [],
        "blocks": {block_id: {"block_id": block_id, "block_name": "使用实际编号定位",
            "data_source_kind": None, "constraints": [], "instructions": [{
                "id": ir_id, "opcode": "return", "inputs": [], "outputs": [],
                "constraints": ["原始操作声明：不得截断"], "metadata": {},
            }]}}, "edges": [],
    }
    provenance = ["run: full-pipeline-v4-example", "语义修复轮次：2；反馈状态：unresolved；标注状态：incomplete"]
    reason = ('保存失败：<&> "错误"，仅用于显示，禁止执行 <script>alert(1)</script>。\n' * 24) + "完整原因最后一行"
    samples = [
        {"index": 1, "sample_id": "CFG", "skill_name": "render-current-graph", "basename": "001-current",
         "repetition": 2, "run_id": "full-pipeline-v4-example", "analysis_sha256": "1" * 64,
         "cfg": cfg, "provenance_lines": provenance},
        {"index": 2, "sample_id": "FAILED", "skill_name": "render-failed-case", "basename": "002-failed",
         "cfg": None, "provenance_lines": ["run: full-pipeline-v4-example", "本例未选出结构有效图"],
         "failure": {"reason": reason, "feedback_status": "extraction_error", "annotation_status": "not_run"}},
    ]
    payload = tmp_path / "input.json"
    payload.write_text(json.dumps({"samples": samples}, ensure_ascii=False), encoding="utf-8")
    audit_path, pictures, vectors = tmp_path / "audit.json", tmp_path / "pictures", tmp_path / "vectors"
    command = [str(NODE), str(BASE / "tools/render_review_cfg.mjs"), "--input", str(payload),
               "--output-dir", str(pictures), "--svg-output-dir", str(vectors), "--audit", str(audit_path),
               "--node-modules", str(MODULES), "--browser", str(BROWSER)]
    process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert process.returncode == 0, process.stderr + process.stdout
    rows = json.loads(audit_path.read_text(encoding="utf-8"))["samples"]
    normal, failed = rows
    assert normal["kind"] == "cfg" and normal["provenance_lines"] == provenance
    assert any(item["kind"] == "sample" and "修复轮次 2" in item["expected"] for item in normal["text_checks"])
    assert normal["identity_checks_passed"] and normal["counts"]["instructions"] == 1
    assert [(item["instruction_id"], item["block_id"]) for item in normal["instruction_locations"]] == [(ir_id, block_id)]
    assert normal["instruction_locations"][0]["width"] > 0
    root = ET.fromstring((vectors / "001-current.svg").read_text(encoding="utf-8"))
    operations = [element for element in root.iter() if element.get("data-ir-id") is not None]
    assert len(operations) == 1
    assert operations[0].get("data-ir-id") == ir_id and operations[0].get("data-block-id") == block_id
    normal_text = "".join(root.itertext())
    assert all("".join(line.split()) in "".join(normal_text.split()) for line in provenance)
    assert failed["kind"] == "failure" and all(value == 0 for value in failed["counts"].values())
    assert failed["instruction_locations"] == failed["block_locations"] == []
    assert failed["text_checks_passed"] and failed["bounds_checks_passed"] and failed["identity_checks_passed"]
    failure_root = ET.fromstring((vectors / "002-failed.svg").read_text(encoding="utf-8"))
    failure_text = "".join(failure_root.itertext())
    assert "".join(reason.split()) in "".join(failure_text.split())
    assert "本轮无可用CFG" in "".join(failure_text.split())
    assert "不是控制流图" in failure_text
    assert not [element for element in failure_root.iter() if element.get("data-ir-id") or element.get("data-block-id")]
    assert not failure_root.findall('.//{http://www.w3.org/2000/svg}script')
    assert sorted(path.name for path in pictures.iterdir()) == ["001-current.png", "002-failed.png"]
    assert sorted(path.name for path in vectors.iterdir()) == ["001-current.svg", "002-failed.svg"]
