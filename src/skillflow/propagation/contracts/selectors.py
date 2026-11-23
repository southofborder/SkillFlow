"""Finite, source-declared partitions of an immutable input or wrapper field."""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, StrictStr, model_validator

Index = Annotated[int, Field(strict=True, ge=0)]


class TypeTest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    kind: Literal["object", "array", "string", "nonempty_string", "null", "missing"]


class EqualsTest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    kind: Literal["equals"]
    value: str | int | FiniteFloat | bool | None


class Selector(BaseModel):
    """First matching test wins. Index len(tests) is the remaining domain."""
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    path: list[StrictStr | Index]
    tests: list[Annotated[TypeTest | EqualsTest, Field(discriminator="kind")]] = Field(min_length=1)
    outcome: Index

    @model_validator(mode="after")
    def bounded_choice(self):
        if self.outcome > len(self.tests):
            raise ValueError("selector.outcome must index a test or the final remainder")
        if len({test.model_dump_json() for test in self.tests}) != len(self.tests):
            raise ValueError("selector.tests must not repeat a test")
        return self


class CaseGuard(Selector):
    input_index: Index
