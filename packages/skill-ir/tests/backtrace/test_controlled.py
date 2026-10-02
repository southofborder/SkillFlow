"""Use the actual Lean printer/parser; no Python substitute retelling template."""

from copy import deepcopy
import json

import pytest

from skill_ir.backtrace import controlled
from skill_ir.backtrace.controlled import (
    ControlledVerificationError, from_rich, render_controlled, to_rich, verify_controlled,
)
from skill_ir.backtrace.evidence import canonical_graph_sha256, normalize_cfg, resolve_pointer
from skill_ir.ir.cfg import ControlFlowGraph

from backtrace.test_evidence import example_cfg


@pytest.fixture(scope="module")
def executable():
    return controlled._executable(None)


@pytest.fixture(scope="module")
def document(executable):
    return render_controlled(example_cfg(), executable=executable)


@pytest.mark.parametrize("value", [None, False, 0, 0.0, -0.0, 1.25, "原文\n\"引号\"\\", ["a", None], {"嵌套": [3, {}, []]}])
def test_rich_bridge_retains_every_literal_type_and_value(value):
    cfg = example_cfg()
    cfg.blocks["end"].instructions[-1].inputs[-1].literal_value = value
    graph = normalize_cfg(cfg)
    restored = from_rich(to_rich(graph))
    assert canonical_graph_sha256(restored) == canonical_graph_sha256(graph)
    actual = restored["blocks"]["end"]["instructions"][-1]["inputs"][-1]["literal_value"]
    assert type(actual) is type(value)
    assert json.dumps(actual, sort_keys=True, ensure_ascii=False) == json.dumps(value, sort_keys=True, ensure_ascii=False)


def test_rich_bridge_rejects_extra_missing_or_noncanonical_payload_fields():
    rich = to_rich(normalize_cfg(example_cfg()))
    rich["blocks"][0]["instructions"][0]["extra"] = "not allowed"
    with pytest.raises(ControlledVerificationError, match="fields"):
        from_rich(rich)
    rich = to_rich(normalize_cfg(example_cfg()))
    rich["blocks"][0]["instructions"][0]["metadata_json"] = '{ "x": 1 }'
    with pytest.raises(ControlledVerificationError, match="noncanonical"):
        from_rich(rich)
    rich = to_rich(normalize_cfg(example_cfg()))
    rich["blocks"].append(deepcopy(rich["blocks"][0]))
    with pytest.raises(ControlledVerificationError, match="Duplicate"):
        from_rich(rich)


def test_actual_lean_text_and_complete_certificate_roundtrip(document, executable):
    cert = verify_controlled(document, cfg=example_cfg(), executable=executable)
    assert cert == document["certificate"]
    assert cert["status"] == "verified"
    assert all(cert["checks"].values())
    assert {"graph_sha256", "rich_sha256", "text_sha256", "source_sha256", "binary_sha256"} <= cert.keys()
    assert cert["source_files"]
    assert "graph" not in document and "rich" not in document
    assert len({unit["id"] for unit in document["units"]}) == len(document["units"])
    graph = normalize_cfg(example_cfg())
    for unit in document["units"]:
        assert unit["text"] in document["text"] and unit["id"] in unit["text"]
        for ref in unit["graph_refs"]:
            resolve_pointer(graph, ref)
    assert {unit["basis"] for unit in document["units"]} >= {"explicit_graph", "declared_constraint", "embedded_content"}


@pytest.mark.parametrize("field", ["text", "units", "derived_links", "graph_sha256", "certificate"])
def test_document_tampering_cannot_pass_verification(document, executable, field):
    changed = deepcopy(document)
    if field == "text":
        changed[field] += "\n未经依据追加内容"
    elif field == "units":
        changed[field][0]["text"] += "假"
    elif field == "derived_links":
        changed[field][0]["definition_ref"] = "/blocks/end"
    elif field == "graph_sha256":
        changed[field] = "0" * 64
    else:
        changed[field]["binary_sha256"] = "0" * 64
    with pytest.raises(ControlledVerificationError):
        verify_controlled(changed, executable=executable)


def test_recovered_text_cannot_be_completed_from_supplied_cfg(document, executable):
    cfg = example_cfg()
    cfg.blocks["end"].instructions[-1].inputs[0].identifier = "first"
    with pytest.raises(ControlledVerificationError, match="supplied CFG"):
        verify_controlled(document, cfg=cfg, executable=executable)


def test_render_uses_actual_printed_text_not_hidden_recovered_graph(executable, monkeypatch):
    real = controlled._lean
    first = True

    def changed_initial_text(binary, payload):
        nonlocal first
        response = real(binary, payload)
        if first:
            first = False
            assert payload["command"] == "render"
            # Leave the alleged recovered_graph untouched. Only the printed
            # operation changes, so a hidden-graph-based check would miss it.
            response["text"] = response["text"].replace("append_status", "unexpected_side_effect")
        return response

    monkeypatch.setattr(controlled, "_lean", changed_initial_text)
    with pytest.raises(ControlledVerificationError, match="complete input CFG"):
        render_controlled(example_cfg(), executable=executable)


def test_evidence_identifier_cannot_be_remapped_to_another_existing_location(executable, monkeypatch):
    real = controlled._lean

    def bad_evidence(binary, payload):
        response = real(binary, payload)
        if payload["command"] == "render":
            response["units"][0]["ref"] = "/contexts"
        return response

    monkeypatch.setattr(controlled, "_lean", bad_evidence)
    with pytest.raises(ControlledVerificationError, match="exact evidence location"):
        render_controlled(example_cfg(), executable=executable)


def test_deleted_operation_is_not_reconstructed_from_its_remaining_title(executable):
    cfg = example_cfg()
    cfg.blocks["end"].instructions.pop(0)
    graph = normalize_cfg(cfg)
    text = render_controlled(cfg, executable=executable)["text"]
    assert "追加最终状态并返回" in text
    assert "append_status" not in text and "ir_append" not in text and "status.txt" not in text
    parsed = controlled._lean(executable, {"command": "parse", "text": text})
    assert canonical_graph_sha256(from_rich(parsed["recovered_graph"])) == canonical_graph_sha256(graph)


def test_actual_text_preserves_opaque_metadata_without_execution(executable, tmp_path):
    cfg = example_cfg()
    marker = tmp_path / "must-not-exist"
    source = f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n```\n原文"
    cfg.blocks["retry"].instructions[0].metadata = {"source": source, "payload": {"n": -0.0, "empty": []}}
    result = render_controlled(cfg, executable=executable)
    parsed = controlled._lean(executable, {"command": "parse", "text": result["text"]})
    restored = from_rich(parsed["recovered_graph"])
    assert restored["blocks"]["retry"]["instructions"][0]["metadata"]["source"] == source
    assert not marker.exists()


def test_actual_text_preserves_unicode_escaping_and_empty_values(executable):
    cfg = example_cfg()
    cfg.constraints.extend(['引号 " \\ 换行\n制表\t回车\r零字符\x00 😀', "", "重复", "重复"])
    cfg.blocks["end"].instructions[-1].inputs[-1].literal_value = {
        "float": 1.0, "int": 1, "false": False, "negative_zero": -0.0,
        "empty_list": [], "empty_object": {}, "empty_string": "", "null": None,
    }
    result = render_controlled(cfg, executable=executable)
    verify_controlled(result, cfg=cfg, executable=executable)


def test_repeated_uses_and_same_names_keep_exact_definition_links(document):
    graph = normalize_cfg(example_cfg())
    returns = [link for link in document["derived_links"] if link["use_ref"].startswith("/blocks/end/instructions/1/inputs/")]
    assert len(returns) == 2 and returns[0]["use_ref"] != returns[1]["use_ref"]
    for link in document["derived_links"]:
        assert resolve_pointer(graph, link["use_ref"])["identifier"] == link["identifier"]
        assert resolve_pointer(graph, link["definition_ref"])["identifier"] == link["identifier"]


def test_storage_order_and_identifier_renaming_keep_correspondence(executable):
    graph = normalize_cfg(example_cfg())
    original = render_controlled(ControlFlowGraph.model_validate(graph), executable=executable)
    graph["blocks"] = dict(reversed(list(graph["blocks"].items())))
    reordered = render_controlled(ControlFlowGraph.model_validate(graph), executable=executable)
    assert original["text"] == reordered["text"]
    graph["edges"].reverse()
    block_ids = {key: f"renamed/{index}~" for index, key in enumerate(graph["blocks"])}
    graph["entry_block_id"] = block_ids[graph["entry_block_id"]]
    rebuilt = {}
    for key, block in graph["blocks"].items():
        block["block_id"] = block_ids[key]
        for position, instruction in enumerate(block["instructions"]):
            instruction["id"] = f"ir_new_{len(rebuilt)}_{position}"
            for operand in instruction["inputs"] + instruction["outputs"]:
                if operand["type"] == "result":
                    operand["identifier"] = "new_" + operand["identifier"]
        rebuilt[block_ids[key]] = block
    graph["blocks"] = rebuilt
    for edge in graph["edges"]:
        edge["source_block_id"] = block_ids[edge["source_block_id"]]
        edge["target_block_id"] = block_ids[edge["target_block_id"]]
    cfg = ControlFlowGraph.model_validate(graph)
    result = render_controlled(cfg, executable=executable)
    verify_controlled(result, cfg=cfg, executable=executable)
    assert all(link["identifier"].startswith("new_") for link in result["derived_links"])
    assert all("start~1" not in link["use_ref"] for link in result["derived_links"])


def test_actual_condition_text_does_not_gain_truth_or_path_claims(document, executable):
    parsed = controlled._lean(executable, {"command": "parse", "text": document["text"]})
    graph = from_rich(parsed["recovered_graph"])
    assert graph["edges"] == normalize_cfg(example_cfg())["edges"]
    assert graph["edges"][0]["condition_text"] is None
    assert graph["edges"][1]["condition_text"] == '条件 "带引号"\n第二行'


def test_missing_binary_and_non_json_response_fail_closed(tmp_path):
    with pytest.raises(ControlledVerificationError, match="does not exist"):
        render_controlled(example_cfg(), executable=tmp_path / "absent.exe")
    for raw in ['{"ok":true,"ok":true}', '{"value":NaN}', '{} trailing']:
        with pytest.raises(ControlledVerificationError):
            controlled._json(raw)
