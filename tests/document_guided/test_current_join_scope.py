"""Scoped processing revisions see the executable predecessor IDs of the new graph."""
from copy import deepcopy

from skillflow.document_guided.fragment_revision import processing_scope
from skillflow.document_guided.fragment_display import fragment_prompt_parts
from skillflow.document_guided.prompts import build_processing_revision_prompt


def test_rewired_merge_is_delivered_with_current_predecessors_and_input_definitions():
    def instruction(name, inputs=(), outputs=()):
        def result(key):
            return {"type": "result", "identifier": key}
        return {"id": name, "opcode": "value", "inputs": list(map(result, inputs)),
                "outputs": list(map(result, outputs)), "metadata": {}, "constraints": []}

    def block(*instructions):
        return {"instructions": instructions, "data_source_kind": None}

    def edge(left, right, guard=None):
        return {"source_block_id": left, "target_block_id": right, "condition_text": guard}

    old = {"blocks": {
        "listing": block(instruction("list_files", outputs=["files"])),
        "filter": block(instruction("filter_files", inputs=["files"], outputs=["filtered"])),
        "unfiltered": block(instruction("continue")),
        "candidates": block(instruction("join", inputs=["files", "filtered"], outputs=["selected"])),
    }, "edges": [edge("listing", "filter", "by operation"), edge("listing", "unfiltered", "all"),
                 edge("filter", "candidates"), edge("unfiltered", "candidates")]}
    new = deepcopy(old)
    new["blocks"]["filter.done"] = new["blocks"]["filter"]
    new["blocks"]["filter"] = block(instruction("prepare_filter"))
    new["edges"][2:3] = [edge("filter", "filter.done"), edge("filter.done", "candidates")]
    prior = {"ir_semantics": {"join": {"segments": [{"mode": "local", "ops": [{"op": "merge",
        "incoming": [{"predecessor": "filter", "value": {"kind": "input", "index": 1}},
                     {"predecessor": "unfiltered", "value": {"kind": "input", "index": 0}}]}]}]}}}
    scope = processing_scope(old, new, [], prior)
    prompt = build_processing_revision_prompt(files={"skill/SKILL.md": "Filter the listing."},
        flow="Filter when an operation is supplied.", runtime_contract={}, scope=scope, global_requirements="")
    displayed = fragment_prompt_parts(prompt)[1]["scope"]
    joins = displayed["read_only"]["current_joins"]
    assert set(joins) == {"candidates"}
    assert joins["candidates"]["incoming_edges"] == new["edges"][-2:]
    inputs = joins["candidates"]["input_producers"]["join"]
    assert inputs["1"] == {"result": "filtered", "instruction_id": "filter_files", "block_id": "filter.done",
                           "output_index": 0, "reachable_predecessors": ["filter.done"]}
    assert inputs["0"]["reachable_predecessors"] == ["filter.done", "unfiltered"]
    assert displayed["slots"]["join"]["modeled"] == prior["ir_semantics"]["join"]
    assert "current_joins" not in processing_scope(old, new, [], prior, current_joins=False)["read_only"]
