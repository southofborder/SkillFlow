"""The Python boundary preserves normalized fields without interpreting them."""

from copy import deepcopy
from datetime import datetime
import json

import pytest

from skillflow.graph.audit.evidence import canonical_graph_sha256
from skillflow.graph.audit.evidence import definition_refs
from skillflow.graph.audit.evidence import json_pointer
from skillflow.graph.audit.evidence import normalize_cfg
from skillflow.graph.audit.evidence import resolve_pointer
from skillflow.graph.ir.cfg import ControlFlowGraph


def example_cfg():
    def result(identifier):
        return {"type": "result", "identifier": identifier, "semantic_name": "同名结果"}

    return ControlFlowGraph.model_validate({
        "entry_block_id": "start/~one", "declared_context_keys": ["request"],
        "constraints": ["全局声明", "全局声明"],
        "blocks": {
            "start/~one": {
                "block_id": "start/~one", "block_name": "首次读取", "data_source_kind": "context",
                "constraints": ["块级声明"], "instructions": [
                    {"id": "ir_first", "opcode": "acquire", "draft_instruction_id": "draft_original",
                     "inputs": [{"type": "context_key", "identifier": "request"}],
                     "outputs": [result("first")], "constraints": ["指令声明"]},
                    {"id": "ir_go_first", "opcode": "dispatch", "inputs": [result("first")]},
                ],
            },
            "retry": {"block_id": "retry", "block_name": "重试读取", "data_source_kind": "external", "instructions": [
                {"id": "ir_retry", "opcode": "fetch", "inputs": [
                    {"type": "external_resource", "identifier": "tool.fetch"}, result("first")],
                 "outputs": [result("second")], "metadata": {"script_content": "# opaque\nprint('not run')", "nested": [None, True, 2, 2.5]}},
                {"id": "ir_go_retry", "opcode": "dispatch"},
            ]},
            "end": {"block_id": "end", "block_name": "追加最终状态并返回", "instructions": [
                {"id": "ir_append", "opcode": "append_status", "inputs": [
                    {"type": "external_resource", "identifier": "status.txt"}, {"type": "literal", "literal_value": "success"}]},
                {"id": "ir_return", "opcode": "return", "inputs": [result("second"), result("second"), {"type": "literal", "literal_value": None}]},
            ]},
        },
        "edges": [
            {"source_block_id": "start/~one", "target_block_id": "retry", "condition_text": None},
            {"source_block_id": "start/~one", "target_block_id": "retry", "condition_text": "条件 \"带引号\"\n第二行"},
            {"source_block_id": "retry", "target_block_id": "end", "condition_text": None},
        ],
    })


def test_normalized_copy_retains_all_fields_and_does_not_mutate_input():
    cfg = example_cfg()
    before = deepcopy(cfg.model_dump(mode="python"))
    graph = normalize_cfg(cfg)
    assert graph == json.loads(cfg.to_json())
    graph["blocks"]["retry"]["instructions"][0]["metadata"]["script_content"] = "changed copy"
    assert cfg.model_dump(mode="python") == before


def test_identical_result_labels_do_not_merge_definition_identities():
    graph = normalize_cfg(example_cfg())
    assert definition_refs(graph) == {
        "first": ["/blocks/start~1~0one/instructions/0/outputs/0"],
        "second": ["/blocks/retry/instructions/0/outputs/0"],
    }
    for refs in definition_refs(graph).values():
        assert resolve_pointer(graph, refs[0])["semantic_name"] == "同名结果"
    assert json_pointer("blocks", "start/~one") == "/blocks/start~1~0one"


@pytest.mark.parametrize("pointer", ["blocks", "/blocks/no-such-block", "/blocks/~2", "/edges/-1", "/edges/01", "/edges/20", "/edges/０"])
def test_pointer_rejects_nonexistent_or_noncanonical_locations(pointer):
    with pytest.raises(ValueError):
        resolve_pointer(normalize_cfg(example_cfg()), pointer)


@pytest.mark.parametrize("payload", [float("nan"), float("inf"), {"bad": {1, 2}}, {"bad": (1, 2)}, {"bad": datetime(2026, 1, 1)}, {1: "numeric key"}])
def test_non_json_payload_cannot_be_coerced_before_retelling(payload):
    cfg = example_cfg()
    cfg.blocks["retry"].instructions[0].metadata = {"payload": payload}
    with pytest.raises(ValueError, match="Non-JSON"):
        normalize_cfg(cfg)


def test_cyclic_payload_and_invalid_result_binding_are_rejected():
    cfg = example_cfg()
    cyclic = {}
    cyclic["self"] = cyclic
    cfg.blocks["retry"].instructions[0].metadata = cyclic
    with pytest.raises(ValueError, match="cyclic"):
        normalize_cfg(cfg)
    cfg = example_cfg()
    cfg.blocks["end"].instructions[-1].inputs[0].identifier = "undefined"
    with pytest.raises(ValueError, match="RESULT_NOT_DEFINED"):
        normalize_cfg(cfg)


def test_hash_preserves_json_types_list_order_and_negative_zero():
    assert len({canonical_graph_sha256(value) for value in [False, 0, 0.0, -0.0]}) == 4
    assert canonical_graph_sha256({"a": 1, "b": 2}) == canonical_graph_sha256({"b": 2, "a": 1})
    assert canonical_graph_sha256([1, 2]) != canonical_graph_sha256([2, 1])
