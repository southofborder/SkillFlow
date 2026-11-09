"""Untrusted, LLM-produced candidate models for Skill analysis."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from skillflow.graph.ir import Operand
from skillflow.graph.ir import DataSourceKind


def _non_empty(value: str, field_name: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} must not be empty")
    return value


class CandidateInstruction(BaseModel):
    """An instruction proposed by the LLM before canonical compilation."""

    model_config = ConfigDict(extra="forbid")

    instruction_ref: str
    opcode: str
    inputs: list[Operand] = Field(default_factory=list)
    outputs: list[Operand] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("instruction_ref", "opcode")
    @classmethod
    def normalize_required_names(cls, value: str, info) -> str:
        return _non_empty(value, info.field_name)


class CandidateBlock(BaseModel):
    """A behavior unit proposed by the LLM.

    A block states only what happens inside it.  Which of its values are
    readable elsewhere is a property of the paths through the graph, so it is
    checked against CFG paths rather than declared here.
    """

    model_config = ConfigDict(extra="forbid")

    block_ref: str
    block_name: str
    data_source_kind: DataSourceKind = None
    instructions: list[CandidateInstruction] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

    @field_validator("block_ref", "block_name")
    @classmethod
    def normalize_required_names(cls, value: str, info) -> str:
        return _non_empty(value, info.field_name)


class CandidateEdge(BaseModel):
    """A control-flow edge proposed by the LLM."""

    model_config = ConfigDict(extra="forbid")

    source_block_ref: str
    target_block_ref: str
    condition_text: str | None = None

    @field_validator("source_block_ref", "target_block_ref")
    @classmethod
    def normalize_block_refs(cls, value: str, info) -> str:
        return _non_empty(value, info.field_name)

    @field_validator("condition_text")
    @classmethod
    def normalize_condition_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class IRAnalysisCandidate(BaseModel):
    """The complete untrusted analysis returned by the LLM."""

    model_config = ConfigDict(extra="forbid")

    entry_block_ref: str
    constraints: list[str] = Field(default_factory=list)
    declared_context_keys: list[str] = Field(default_factory=list)
    blocks: list[CandidateBlock] = Field(default_factory=list)
    edges: list[CandidateEdge] = Field(default_factory=list)
    diagnostics: list[str] = Field(default_factory=list)

    @field_validator("entry_block_ref")
    @classmethod
    def normalize_entry_ref(cls, value: str) -> str:
        return _non_empty(value, "entry_block_ref")

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
