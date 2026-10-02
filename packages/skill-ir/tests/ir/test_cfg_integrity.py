"""Acceptance tests for the first-stage boundary and strict result format."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest
from pydantic import ValidationError

from skill_ir import (
    BasicBlock,
    CFGEdge,
    ControlFlowGraph,
    IRInstruction,
    Operand,
    compile_candidate,
)
from skill_ir.ir.validation import CFGIntegrityError
from skill_ir.extraction.prompt import _EXAMPLES


def make_block(block_id, *, reads=(), produces=(), opcode="compute", ending="dispatch"):
    return BasicBlock(
        block_id=block_id,
        block_name=f"Block {block_id}",
        instructions=[
            IRInstruction(
                id=f"ir_{block_id}_work",
                opcode=opcode,
                inputs=[Operand(type="result", identifier=item) for item in reads],
                outputs=[Operand(type="result", identifier=item) for item in produces],
            ),
            IRInstruction(
                id=f"ir_{block_id}_end",
                opcode=ending,
                inputs=[Operand(type="literal", literal_value=True)],
            ),
        ],
    )


def test_first_stage_compiles_serializes_and_renders_when_analysis_cannot_be_imported():
    source_root = Path(__file__).resolve().parents[2] / "src"
    script = r"""
import importlib.abc
import json
import sys
sys.path.insert(0, sys.argv[1])
class NoAnalysis(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {"skill_ir.analysis.availability", "skill_ir.propagate"}:
            raise AssertionError("First-stage code imported an optional analysis")
sys.meta_path.insert(0, NoAnalysis())
import skill_ir
from skill_ir.extraction.prompt import _EXAMPLES
for _, candidate in _EXAMPLES:
    compiled = skill_ir.compile_candidate(candidate)
    assert compiled.ok, compiled.diagnostics
    graph = skill_ir.ControlFlowGraph.model_validate(json.loads(compiled.cfg.to_json()))
    assert graph.validate_integrity()
    assert "flowchart TD" in skill_ir.render_mermaid(graph)
for retired in ("Opcode", "propagate", "PropagationResult", "ExposureCandidate"):
    assert not hasattr(skill_ir, retired)
assert not hasattr(graph, "analyze_dataflow")
"""
    run = subprocess.run(
        [sys.executable, "-c", script, str(source_root)], capture_output=True, text=True
    )
    assert run.returncode == 0, run.stdout + run.stderr


def test_ids_semantic_names_and_literals_round_trip_without_aliases():
    compiled = compile_candidate(deepcopy(_EXAMPLES[0][1]))
    assert compiled.ok, compiled.diagnostics
    payload = json.loads(compiled.cfg.to_json())
    source = payload["blocks"]["block_001"]
    acquisition = source["instructions"][0]
    assert acquisition["id"] == "ir_001"
    assert acquisition["outputs"][0] == {
        "type": "result",
        "identifier": "result_001",
        "semantic_name": "raw_message",
    }
    for block in payload["blocks"].values():
        assert "data_source_kind" in block
        assert "source_kind" not in block and "ir_sequence" not in block
        for instruction in block["instructions"]:
            assert "metadata" in instruction and "draft_instruction_id" in instruction
            for operand in instruction["inputs"] + instruction["outputs"]:
                assert not ({"name", "value", "llm_name"} & operand.keys())
                if operand["type"] != "literal":
                    assert "literal_value" not in operand
    assert ControlFlowGraph.model_validate(payload).validate_integrity()
    literal = Operand(type="literal", literal_value={"temperature": 18, "note": None})
    assert literal.literal_value == {"temperature": 18, "note": None}


@pytest.mark.parametrize(
    "legacy",
    [
        {"type": "value_ref", "name": "value_004"},
        {"type": "result", "identifier": "result_004", "llm_name": "weather"},
        {"type": "literal", "value": 18},
    ],
)
def test_retired_operand_format_is_rejected(legacy):
    with pytest.raises(ValidationError):
        Operand.model_validate(legacy)


@pytest.mark.parametrize(
    "opcode", ["http_get", "read_db", "call_llm", "read_context", "任意语义操作"]
)
def test_business_names_have_identical_first_stage_behavior(opcode):
    candidate = deepcopy(_EXAMPLES[0][1])
    candidate["blocks"][0]["instructions"][0]["opcode"] = opcode
    candidate["blocks"][1]["instructions"][0]["opcode"] = opcode
    result = compile_candidate(candidate)
    assert result.ok, result.diagnostics
    assert result.cfg.blocks["block_001"].read_context_keys() == ["user_input"]


def test_candidate_block_order_is_not_execution_order():
    candidate = deepcopy(_EXAMPLES[0][1])
    candidate["blocks"].reverse()
    result = compile_candidate(candidate)
    assert result.ok, result.diagnostics
    assert result.cfg.entry_block_id == "block_003"
    assert result.cfg.validate_integrity()


def test_integrity_rejects_duplicate_results_across_blocks():
    graph = ControlFlowGraph(
        entry_block_id="A",
        blocks={
            "A": make_block("A", produces=["same"]),
            "B": make_block("B", produces=["same"], ending="return"),
        },
        edges=[CFGEdge(source_block_id="A", target_block_id="B")],
    )
    with pytest.raises(CFGIntegrityError) as caught:
        graph.validate_integrity()
    assert "DUPLICATE_RESULT_IDENTIFIER" in {
        issue.code for issue in caught.value.issues
    }


def test_integrity_rejects_duplicate_instruction_ids_across_blocks():
    first = make_block("A", produces=["one"])
    second = make_block("B", produces=["two"], ending="return")
    second.instructions[0].id = first.instructions[0].id
    with pytest.raises(ValueError, match="DUPLICATE_INSTRUCTION_ID"):
        ControlFlowGraph(
            entry_block_id="A",
            blocks={"A": first, "B": second},
            edges=[CFGEdge(source_block_id="A", target_block_id="B")],
        )


def test_integrity_caches_reachability_once_per_producer(monkeypatch):
    import skill_ir.ir.validation as validation

    graph = ControlFlowGraph(
        entry_block_id="A",
        blocks={
            "A": make_block("A", produces=["one", "two"]),
            "B": make_block("B", reads=["one", "two", "one"]),
            "C": make_block("C", reads=["two", "one"], ending="return"),
        },
        edges=[
            CFGEdge(source_block_id="A", target_block_id="B"),
            CFGEdge(source_block_id="B", target_block_id="C"),
        ],
    )
    calls = []
    original = validation.reachable_blocks

    def record(starts, successors):
        calls.append(tuple(starts))
        return original(starts, successors)

    monkeypatch.setattr(validation, "reachable_blocks", record)
    assert graph.validate_integrity()
    # One traversal establishes reachable components; one checks all A's results.
    assert calls == [("A",), ("A",)]


def test_same_block_read_before_production_is_rejected_even_in_a_loop():
    block = make_block("A", produces=["later"])
    block.instructions.insert(
        0,
        IRInstruction(
            id="ir_A_early",
            opcode="use",
            inputs=[Operand(type="result", identifier="later")],
        ),
    )
    graph = ControlFlowGraph.model_construct(
        entry_block_id="A",
        blocks={"A": block},
        declared_context_keys=[],
        edges=[CFGEdge(source_block_id="A", target_block_id="A")],
    )
    with pytest.raises(CFGIntegrityError) as caught:
        graph.validate_integrity()
    assert "RESULT_READ_BEFORE_DEFINITION" in {
        issue.code for issue in caught.value.issues
    }
