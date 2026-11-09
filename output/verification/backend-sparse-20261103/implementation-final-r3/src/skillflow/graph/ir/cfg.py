"""Control-flow graph model with first-stage structure and reference checks.

Edges come from the candidate. Validation checks only the relationships written
in that graph; it does not infer edges, classify operations, or propagate effects.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from skillflow.graph.ir.basic_block import BasicBlock
from skillflow.graph.ir.operand import OperandType
from skillflow.graph.ir.validation import structure_issues
from skillflow.graph.ir.validation import validate_cfg_integrity


class CFGEdge(BaseModel):
    """A directed control-flow edge between two basic blocks."""

    model_config = ConfigDict(extra="forbid")

    source_block_id: str
    target_block_id: str
    condition_text: str | None = None

    @field_validator("source_block_id", "target_block_id")
    @classmethod
    def normalize_block_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("block ID must not be empty")
        return value

    @field_validator("condition_text")
    @classmethod
    def normalize_condition_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class ControlFlowGraph(BaseModel):
    """Basic blocks, their jumps, and the result references to check for integrity."""

    model_config = ConfigDict(extra="forbid")

    entry_block_id: str
    constraints: list[str] = Field(default_factory=list)
    blocks: dict[str, BasicBlock]
    edges: list[CFGEdge] = Field(default_factory=list)
    declared_context_keys: list[str] = Field(default_factory=list)

    @field_validator("entry_block_id")
    @classmethod
    def normalize_entry_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("entry_block_id must not be empty")
        return value

    @field_validator("declared_context_keys")
    @classmethod
    def normalize_declared_context_keys(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for index, value in enumerate(values):
            if not isinstance(value, str):
                raise ValueError(
                    f"declared context key at index {index} must be a string"
                )
            key = value.strip()
            if not key:
                raise ValueError(
                    f"declared context key at index {index} must not be empty"
                )
            if key in seen:
                raise ValueError(f"duplicate declared context key {key!r}")
            seen.add(key)
            normalized.append(key)
        return normalized

    @model_validator(mode="after")
    def validate_structure(self) -> "ControlFlowGraph":
        errors = self._structural_errors()
        if errors:
            raise ValueError("; ".join(errors))
        return self

    def _structural_errors(self) -> list[str]:
        return [f"{issue.code}: {issue.message}" for issue in structure_issues(self)]

    def validate_integrity(self) -> bool:
        """Recheck current fields, structure, and references without changing them.

        Construction may normalize incoming values; this check rejects stored
        values that would need normalization. It performs no data propagation.
        """
        return validate_cfg_integrity(self)

    def result_semantic_names(self) -> dict[str, str]:
        """Map each result ID to the wording the extractor used for it.

        Canonical result IDs are assigned by compilation and mean nothing on
        their own, so anything that has to be read back -- an audit, or
        backtranslating the graph into sentences to compare against the Skill --
        needs the original label to say what ``result_004`` was.

        Definition sites win: a result is identified by where it comes from, and
        a use that worded it differently still refers to that one definition.
        Results whose wording is already their ID are left out, so a caller can
        print the semantic name whenever this map has one. Derived on demand and
        never stored, so it cannot drift from the operands it summarizes.
        """

        names: dict[str, str] = {}
        for operands in (self._result_operands(False), self._result_operands(True)):
            for operand in operands:
                if operand.identifier is not None and operand.semantic_name:
                    names.setdefault(operand.identifier, operand.semantic_name)
        return {
            result_id: semantic_name
            for result_id, semantic_name in names.items()
            if semantic_name != result_id
        }

    def _result_operands(self, reads: bool) -> list[Operand]:
        """Return every result operand in the graph's outputs (or inputs)."""

        return [
            operand
            for block in self.blocks.values()
            for instruction in block.instructions
            for operand in (instruction.inputs if reads else instruction.outputs)
            if operand.type is OperandType.RESULT
        ]

    def to_json(self) -> str:
        """Validate the current graph before serializing its canonical fields."""

        self.validate_integrity()
        payload: dict[str, Any] = self.model_dump(mode="json")
        for block in payload["blocks"].values():
            for instruction in block["instructions"]:
                for operand in [*instruction["inputs"], *instruction["outputs"]]:
                    if operand["type"] != OperandType.LITERAL.value:
                        operand.pop("literal_value", None)
                    if operand.get("semantic_name") is None:
                        operand.pop("semantic_name", None)
        return json.dumps(payload, indent=2, ensure_ascii=False)
