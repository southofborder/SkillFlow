"""Scope-preserving constraints are descriptive text, not dataflow declarations."""

from copy import deepcopy
import json

import pytest
from pydantic import ValidationError

from skill_ir.artifacts.analysis_json import load_analysis_cfg, serialize_analysis_result
from skill_ir.extraction.candidate import (
    CandidateBlock,
    CandidateInstruction,
    IRAnalysisCandidate,
)
from skill_ir.extraction.compiler import compile_candidate
from skill_ir.extraction.pipeline import _candidate_dump, analyze_skill
from skill_ir.ir import BasicBlock, IRInstruction
from skill_ir.ir.cfg import ControlFlowGraph


def legacy_candidate() -> dict:
    """Use the existing result-reference contract without any new fields."""
    return {
        "entry_block_ref": "read",
        "declared_context_keys": ["message"],
        "blocks": [
            {
                "block_ref": "read",
                "block_name": "Read the request",
                "data_source_kind": "context",
                "instructions": [
                    {
                        "instruction_ref": "read_message",
                        "opcode": "read_message",
                        "inputs": [{"type": "context_key", "identifier": "message"}],
                        "outputs": [{"type": "result", "identifier": "message_text"}],
                    },
                    {"instruction_ref": "go", "opcode": "dispatch"},
                ],
            },
            {
                "block_ref": "reply",
                "block_name": "Return the request",
                "data_source_kind": None,
                "instructions": [
                    {
                        "instruction_ref": "done",
                        "opcode": "return",
                        "inputs": [{"type": "result", "identifier": "message_text"}],
                    }
                ],
            },
        ],
        "edges": [{"source_block_ref": "read", "target_block_ref": "reply"}],
    }


def with_constraints() -> dict:
    candidate = legacy_candidate()
    candidate["constraints"] = ["Keep the source wording.\n保留规则的原文。"]
    candidate["blocks"][0]["constraints"] = ["This rule applies to this read block."]
    candidate["blocks"][0]["instructions"][0]["constraints"] = [
        "  Preserve these spaces and the source's wording.  ",
        "Do not include unrequested fields.",
    ]
    return candidate


def scoped_models(candidate, cfg):
    return [
        candidate,
        candidate.blocks[0],
        candidate.blocks[0].instructions[0],
        cfg,
        cfg.blocks["block_001"],
        cfg.blocks["block_001"].instructions[0],
    ]


def test_legacy_candidate_and_cfg_default_to_independent_empty_constraints() -> None:
    candidate = IRAnalysisCandidate.model_validate(legacy_candidate())
    compiled = compile_candidate(candidate)
    assert compiled.ok, compiled.diagnostics
    models = scoped_models(candidate, compiled.cfg)
    assert all(model.constraints == [] for model in models)
    assert len({id(model.constraints) for model in models}) == len(models)

    payload = json.loads(compiled.cfg.to_json())
    payload.pop("constraints")
    for block in payload["blocks"].values():
        block.pop("constraints")
        for instruction in block["instructions"]:
            instruction.pop("constraints")
    restored = ControlFlowGraph.model_validate(payload)
    assert restored == compiled.cfg


def test_compilation_and_json_roundtrips_preserve_wording_and_exact_scope() -> None:
    raw = with_constraints()
    before = deepcopy(raw)
    candidate = IRAnalysisCandidate.model_validate(raw)
    candidate = IRAnalysisCandidate.model_validate_json(json.dumps(_candidate_dump(candidate)))
    compiled = compile_candidate(candidate)
    assert compiled.ok, compiled.diagnostics
    cfg = ControlFlowGraph.model_validate_json(compiled.cfg.to_json())

    assert raw == before
    assert cfg.constraints == raw["constraints"]
    read = cfg.blocks["block_001"]
    assert read.constraints == raw["blocks"][0]["constraints"]
    assert read.instructions[0].constraints == raw["blocks"][0]["instructions"][0]["constraints"]
    assert read.instructions[1].constraints == []
    assert cfg.blocks["block_002"].constraints == []
    assert cfg.blocks["block_002"].instructions[0].constraints == []
    assert BasicBlock.model_validate_json(read.to_json()) == read

    # Compilation creates independent containers and never propagates scope.
    read.instructions[0].constraints.append("A later edit")
    assert candidate.blocks[0].instructions[0].constraints == before["blocks"][0]["instructions"][0]["constraints"]
    assert cfg.constraints == before["constraints"]


@pytest.mark.parametrize(
    "model",
    [IRAnalysisCandidate, CandidateBlock, CandidateInstruction, ControlFlowGraph, BasicBlock, IRInstruction],
)
@pytest.mark.parametrize("invalid", ["one rule", {"rule": "text"}, [17], [None], None])
def test_constraints_require_a_list_of_strings_at_each_scope(model, invalid) -> None:
    candidate = IRAnalysisCandidate.model_validate(legacy_candidate())
    cfg = compile_candidate(candidate).cfg
    instance = next(item for item in scoped_models(candidate, cfg) if type(item) is model)
    payload = instance.model_dump(mode="json")
    payload["constraints"] = invalid
    with pytest.raises(ValidationError, match="constraints"):
        model.model_validate(payload)


def test_constraint_text_does_not_define_results_or_add_execution_steps() -> None:
    candidate = with_constraints()
    plain = compile_candidate(legacy_candidate()).cfg
    constrained = compile_candidate(candidate).cfg
    assert len(constrained.blocks) == len(plain.blocks)
    assert constrained.edges == plain.edges
    for block_id, block in plain.blocks.items():
        assert [item.opcode for item in constrained.blocks[block_id].instructions] == [
            item.opcode for item in block.instructions
        ]
        assert constrained.blocks[block_id].instructions[0].inputs == block.instructions[0].inputs

    candidate["constraints"].append("The result undeclared_value is available.")
    candidate["blocks"][1]["instructions"][0]["inputs"] = [
        {"type": "result", "identifier": "undeclared_value"}
    ]
    invalid = compile_candidate(candidate)
    assert not invalid.ok
    assert "RESULT_NOT_DEFINED" in {item.code for item in invalid.diagnostics}


def test_analysis_artifact_roundtrip_preserves_all_constraint_scopes(tmp_path) -> None:
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Read and return a message\n", encoding="utf-8")
    candidate = IRAnalysisCandidate.model_validate(with_constraints())
    result = analyze_skill(skill, candidate=candidate)
    assert result.status == "complete"
    payload = serialize_analysis_result(result)
    assert payload["raw_candidate"]["constraints"] == candidate.constraints
    assert payload["raw_candidate"]["blocks"][0]["constraints"] == candidate.blocks[0].constraints
    assert payload["raw_candidate"]["blocks"][0]["instructions"][0]["constraints"] == candidate.blocks[0].instructions[0].constraints
    artifact = tmp_path / "analysis.json"
    artifact.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    assert load_analysis_cfg(artifact) == result.cfg


def test_candidate_schema_exposes_constraints_only_at_the_three_scopes() -> None:
    schema = IRAnalysisCandidate.model_json_schema()
    for scope in [schema, schema["$defs"]["CandidateBlock"], schema["$defs"]["CandidateInstruction"]]:
        constraints = scope["properties"]["constraints"]
        assert constraints["type"] == "array"
        assert constraints["items"] == {"type": "string"}
        assert "constraints" not in scope.get("required", [])
    assert "constraints" not in schema["$defs"]["CandidateEdge"]["properties"]
