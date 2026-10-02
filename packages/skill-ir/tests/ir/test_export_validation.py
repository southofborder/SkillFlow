"""Accepted exports must not erase illegal fields before full validation."""
from copy import deepcopy

import pytest

from skill_ir import compile_candidate
from skill_ir.extraction.prompt import _EXAMPLES
from skill_ir.ir.validation import CFGIntegrityError


def test_export_rejects_mutated_nonliteral_payload_without_erasing_it():
    graph = compile_candidate(deepcopy(_EXAMPLES[0][1])).cfg
    assert graph is not None
    operand = next(
        operand
        for block in graph.blocks.values()
        for instruction in block.instructions
        for operand in instruction.inputs
        if operand.type.value != "literal"
    )
    operand.literal_value = "not a resource payload"
    with pytest.raises(CFGIntegrityError, match="CFG_SCHEMA_INVALID"):
        graph.to_json()
    assert operand.literal_value == "not a resource payload"


def test_export_rejects_dangling_result_before_serialization():
    graph = compile_candidate(deepcopy(_EXAMPLES[0][1])).cfg
    assert graph is not None
    operand = next(
        operand
        for block in graph.blocks.values()
        for instruction in block.instructions
        for operand in instruction.inputs
        if operand.type.value == "result"
    )
    operand.identifier = "undefined_result"
    with pytest.raises(CFGIntegrityError, match="RESULT_NOT_DEFINED"):
        graph.to_json()
    assert operand.identifier == "undefined_result"
