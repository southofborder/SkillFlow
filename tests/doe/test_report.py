"""Readable audit reports retain actual payloads and keep embedded text inert."""
from copy import deepcopy
from html import escape, unescape
import json
import re

import pytest

from skillflow.doe.report import build_view, render_html, render_markdown


@pytest.fixture
def material():
    def data(identity, content, **origin):
        return {"id": identity, "content": content,
                "origin": {"at": None, "acquired_from": None, "part_of": None, "path": None,
                           "inputs": [], "dependencies": [], **origin},
                "annotations": {"description": None, "sensitivity": [], "evidences": []}}
    def operation(index, inputs, **record):
        return {"position": {"instruction_id": "ir_send", "event_index": index,
                             "op_index": 0, "body_event_index": None, "instance_index": None},
                "effect": "model_observe", "record": {"op": "deliver", "inputs": inputs,
                             "outputs": [], "endpoints": [{"kind": "model_context", "name": "model"}],
                             "changes": [], **record}}
    boundary = {"instruction_id": "ir_send", "event_index": 0, "op_index": 0,
                "body_event_index": None, "scope": None, "target": "model",
                "sink_type": "model_observe", "exposure_level": 2}
    return {"schema_version": "skillflow-doe-material-v2", "task": {"basis": "declared_skill", "text": None},
        "source": {"files": [{"path": "SKILL.md", "content": "容器含 access_token。\n正文应为 summary 原值。"}],
                   "inventory": [], "boundaries": {"binary_files": [], "uninterpreted_files": []}},
        "runtime_contract": {"version": "runtime-v1", "sha256": "0" * 64, "rules": [{"id": "EM01", "text": "static possible"}]},
        "shared_info": {"entry_block_id": "b", "instructions": {
            "ir_send": {"id": "ir_send", "opcode": "observe", "inputs": [{"type": "result", "identifier": "r"}],
                        "outputs": [], "constraints": ["保留原值"]},
            "ir_return": {"id": "ir_return", "opcode": "return", "inputs": [{"type": "result", "identifier": "r"}],
                          "outputs": [], "constraints": []}},
            "blocks": {"b": {"block_id": "b", "block_name": "发送", "instruction_ids": ["ir_send", "ir_return"],
                             "constraints": ["禁止附带其他字段"], "data_source_kind": "none"}},
            "edges": [], "constraints": ["全局限制"], "declared_context_keys": [],
            "data": {"D_whole": data("D_whole", {"form": "known_parts", "parts": [], "parts_complete": False}, acquired_from="storage:records"),
                     "D_body": data("D_body", {"form": "opaque"}, part_of="D_whole", path=["summary"]),
                     "D_control": data("D_control", {"form": "literal", "value": True})},
            "operations": {"op_first": operation(0, [["D_whole"], ["D_whole"]]),
                           "op_second": operation(1, [["D_body"], ["D_control"]], when_input_index=1)},
            "locations": {"model": {"kind": "model_context", "name": "model", "operand_refs": [],
                                    "access_scope": "recipient", "retention": None}},
            "actions": {"ir_send": {"operator": ["llm"]},
                        "ir_return": {"operator": ["agent_runtime"]}},
            "orders": {"ir_send": {"order": "partial", "precedence": []}, "ir_return": {"order": "fixed", "precedence": []}},
            "scopes": {"scope_1": {"instruction_id": "ir_send", "event_index": 0, "instance_index": 0,
                                    "collection": "D_whole", "element": "D_body"}},
            "links": {"l": {"kind": "result_use", "source": "ir_send", "target": "ir_return", "data_ids": ["D_body"], "result": "r"}}},
        "sinks": [{"sink": {"id": "S1", "boundary": boundary, "operations": ["op_first", "op_second"]},
                   "backward_slice": {"data": ["D_whole", "D_body"], "operations": []},
                   "usage_context": {"instructions": ["ir_send", "ir_return"], "operations": ["op_second"], "links": ["l"]},
                   "context": {"blocks": ["b"], "edge_indices": [], "scope_ids": ["scope_1"],
                               "diagnostics": [], "partial_ir_ids": ["ir_send"]}}]}


def test_view_preserves_versions_repeated_slots_and_excludes_controls(material):
    view = build_view(material)
    first, second = view["sinks"][0]["operations"]
    assert first["payload"] == [["D_whole"], ["D_whole"]]
    assert second["payload"] == [["D_body"]]
    assert second["control_indices"] == [1]
    assert view["sinks"][0]["scopes"][0]["instance_index"] == 0
    assert view["sinks"][0]["orders"]["ir_send"]["order"] == "partial"
    view["data"]["D_body"]["raw"]["origin"]["path"].append("edited")
    assert material["shared_info"]["data"]["D_body"]["origin"]["path"] == ["summary"]


def test_both_renderers_use_the_same_view(monkeypatch, material):
    import skillflow.doe.report as report
    original, calls = report.build_view, []
    def captured(value, *, metrics=None):
        calls.append((value, metrics))
        return original(value, metrics=metrics)
    monkeypatch.setattr(report, "build_view", captured)
    metrics = {"input_chars": 400, "input_bytes": 800, "material_chars": 200, "material_bytes": 400}
    report.render_html(material, metrics=metrics)
    report.render_markdown(material, metrics=metrics)
    assert calls == [(material, metrics), (material, metrics)]


def test_source_unregistered_fields_return_and_partial_order_remain_visible(material):
    for rendered in (render_html(material), render_markdown(material)):
        assert "access_token" in rendered
        assert "summary" in rendered
        assert "ir_return" in rendered and "return" in rendered
        assert "Partial order" in rendered
        assert "not execution logs" in rendered
        assert "makes no sensitivity, necessity or DOE judgment" in rendered
        assert "instance_index" in rendered
        assert "doe-material.json" not in rendered
        assert "源文单元定位" not in rendered and "已有文本单元索引" not in rendered
        assert "D_whole" in rendered and "D_body" in rendered
        assert "risk_score" not in rendered and "data_reviews" not in rendered


def test_escape_arbitrary_source_identifiers_and_valid_local_anchors(material):
    hostile = '</pre><script>alert(1)</script><img src=x onerror=alert(2)>|`[x]'
    material["source"]["files"][0]["content"] = hostile
    material["task"] = {"basis": "user_request", "text": hostile}
    material["shared_info"]["locations"]["model"]["name"] = hostile
    material["sinks"][0]["sink"]["id"] = hostile
    for rendered in (render_html(material), render_markdown(material)):
        assert hostile not in rendered
        assert "&lt;script&gt;" in rendered
        assert "<script>" not in rendered and "<img" not in rendered
    html = render_html(material)
    targets = re.findall(r'id="([^"]+)"', html)
    links = re.findall(r'href="#([^"]+)"', html)
    assert len(targets) == len(set(targets))
    assert set(links) <= set(targets)
    assert "script-src 'none'" in html and "connect-src 'none'" in html


def test_each_data_content_shape_has_a_human_explanation(material):
    records = material["shared_info"]["data"]
    for identity, content in {
        "D_excluded": {"form": "whole_except", "base": "D_whole", "excluded_parts": [["credential"]]},
        "D_updated": {"form": "field_updates", "base": "D_whole", "updates": [{"path": ["summary"], "data": "D_body"}]},
        "D_subset": {"form": "subset_view", "base": "D_whole", "predicate": "allowed == true"},
        "D_null": {"form": "literal", "value": None},
    }.items():
        records[identity] = deepcopy(records["D_whole"])
        records[identity]["id"] = identity
        records[identity]["content"] = content
    view = build_view(material)
    assert "unknown remainder" in " ".join(view["data"]["D_whole"]["lines"])
    assert "Excluded" in " ".join(view["data"]["D_excluded"]["lines"])
    assert "updated to" in " ".join(view["data"]["D_updated"]["lines"])
    assert "member content identity is retained" in " ".join(view["data"]["D_subset"]["lines"])
    assert "null" in " ".join(view["data"]["D_null"]["lines"])


def test_metrics_are_character_byte_counts_and_no_token_claim(material):
    metrics = {"input_chars": 400, "input_bytes": 800, "material_chars": 200, "material_bytes": 400}
    for rendered in (render_html(material, metrics=metrics), render_markdown(material, metrics=metrics)):
        assert "Full-fact characters" in rendered and "Review-material UTF-8 bytes" in rendered
        assert "token" in rendered


def test_partial_coverage_is_visible_without_reclassifying_sinks(material):
    metrics = {"material_status": "partial", "missing_ir_ids": ["ir_missing"]}
    for rendered in (render_html(material, metrics=metrics), render_markdown(material, metrics=metrics)):
        assert "These review materials are partial" in rendered and "ir_missing" in unescape(rendered)
        assert "Missing slices do not establish absence of exposure" in rendered


def test_raw_ir_is_shared_once_and_sink_display_has_a_short_name(material):
    original = deepcopy(material["sinks"][0])
    material["sinks"].append(original)
    material["sinks"][1]["sink"]["id"] = "S2-long-original-identity"
    html, markdown = render_html(material), render_markdown(material)
    raw = escape(json.dumps(material["shared_info"]["instructions"]["ir_send"],
                            ensure_ascii=False, sort_keys=True, indent=2))
    assert html.count(raw) == 1 and markdown.count(raw) == 1
    assert "S001" in html and "S002" in html
    assert "S2-long-original-identity" in html and "S2-long-original-identity" in markdown
    assert '"backward_slice"' not in unescape(html)


def test_compact_json_and_rule_cost_labels(material):
    metrics = {"input_compact_characters": 200, "material_compact_characters": 100,
               "runtime_contract_characters": 80}
    for rendered in (render_html(material, metrics=metrics), render_markdown(material, metrics=metrics)):
        assert "canonical compact JSON characters" in rendered and "Runtime-contract text characters" in rendered
