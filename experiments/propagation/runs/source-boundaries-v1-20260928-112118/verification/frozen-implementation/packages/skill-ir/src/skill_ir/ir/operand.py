"""Typed instruction operands."""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class OperandType(str, Enum):
    """The source or destination kind of an operand."""

    LITERAL = "literal"
    CONTEXT_KEY = "context_key"
    RESULT = "result"
    EXTERNAL_RESOURCE = "external_resource"


class Operand(BaseModel):
    """One typed instruction input or output.

    RESULT identifies an instruction result; CONTEXT_KEY identifies a declared
    runtime entry; EXTERNAL_RESOURCE identifies a file, tool, API, or service.
    Only LITERAL stores a payload in ``literal_value``. ``semantic_name`` keeps
    the extractor's wording when compilation assigns a result identifier.
    Result identifiers are global; a single instruction can produce several.
    """

    model_config = ConfigDict(extra="forbid")

    type: OperandType
    identifier: str | None = None
    literal_value: Any | None = None
    semantic_name: str | None = None

    @field_validator("identifier", "semantic_name")
    @classmethod
    def normalize_operand_identifiers(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_source_fields(self) -> "Operand":
        if self.type is OperandType.LITERAL:
            if self.semantic_name is not None:
                raise ValueError("literal operand must not define 'semantic_name'")
            return self

        if self.identifier is None or not self.identifier.strip():
            raise ValueError(
                f"{self.type.value} operand requires a non-empty 'identifier'"
            )

        # ``model_fields_set`` lets us distinguish an omitted value from an
        # explicitly supplied ``literal_value=None``.  Only literals own a value.
        if "literal_value" in self.model_fields_set:
            raise ValueError(
                f"{self.type.value} operand must not define 'literal_value'; "
                "put resource/configuration details in 'identifier' or instruction metadata"
            )
        return self
