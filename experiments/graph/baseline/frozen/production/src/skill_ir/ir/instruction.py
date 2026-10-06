"""Atomic IR instructions."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from .operand import Operand, OperandType


class IRInstruction(BaseModel):
    """One atomic operation in a basic block."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^ir_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*$")
    opcode: str
    inputs: list[Operand] = Field(default_factory=list)
    outputs: list[Operand] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    draft_instruction_id: str | None = None

    @field_validator("opcode")
    @classmethod
    def normalize_opcode(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("opcode must not be empty")
        return value

    @field_validator("draft_instruction_id")
    @classmethod
    def normalize_draft_instruction_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_outputs(self) -> "IRInstruction":
        errors: list[str] = []
        output_identifiers: set[str] = set()

        if self.opcode in {"dispatch", "return"} and self.outputs:
            errors.append(f"{self.opcode} must not produce outputs")

        for index, operand in enumerate(self.outputs):
            if operand.type is not OperandType.RESULT:
                errors.append(
                    f"output[{index}] must have type RESULT, "
                    f"got {operand.type.value}"
                )
                continue

            # Operand already checks this, but retain the instruction-local
            # diagnostic because output names are the SSA definition boundary.
            if operand.identifier is None or not operand.identifier.strip():
                errors.append(f"output[{index}] requires a non-empty SSA 'identifier'")
                continue

            if operand.identifier in output_identifiers:
                errors.append(
                    f"output[{index}] duplicates result identifier {operand.identifier!r} "
                    "within the same instruction"
                )
            output_identifiers.add(operand.identifier)

        if errors:
            raise ValueError(f"instruction {self.id!r}: " + "; ".join(errors))
        return self
