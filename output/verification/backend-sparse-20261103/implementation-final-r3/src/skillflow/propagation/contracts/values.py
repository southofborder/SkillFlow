"""Lexical symbolic values shared by transfer and semantic declarations."""
from __future__ import annotations
from typing import Annotated, Any, Literal
from pydantic import BaseModel, ConfigDict, Field, JsonValue, StringConstraints, field_validator
from skillflow.propagation.data.models import _check_json_value

Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
Index = Annotated[int, Field(strict=True, ge=0)]

class StrictSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

class InputRef(StrictSpec):
    kind: Literal["input"]
    index: Index

class LocalRef(StrictSpec):
    kind: Literal["local"]
    name: Text

class LiteralRef(StrictSpec):
    kind: Literal["literal"]
    value: JsonValue

    @field_validator("value", mode="before")
    @classmethod
    def strict_json(cls, value: Any):
        _check_json_value(value)
        return value

class AlternativesRef(StrictSpec):
    kind: Literal["alternatives"]
    items: list["ValueRef"]

    @field_validator("items")
    @classmethod
    def nonempty(cls, value):
        if not value:
            raise ValueError("alternatives must contain at least one candidate")
        return value

ValueRef = Annotated[InputRef | LocalRef | LiteralRef | AlternativesRef, Field(discriminator="kind")]
AlternativesRef.model_rebuild()
