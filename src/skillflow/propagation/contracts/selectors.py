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


class PythonExceptionTest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    kind: Literal["python_exception"]
    classes: list[StrictStr] = Field(min_length=1)

    @model_validator(mode="after")
    def builtin_classes(self):
        from skillflow.propagation.python_exceptions import builtin_exception
        if any(builtin_exception(name) is None for name in self.classes) or len(set(self.classes)) != len(self.classes):
            raise ValueError("Python handler selector requires distinct built-in exception classes")
        return self


class Selector(BaseModel):
    """First matching test wins. Index len(tests) is the remaining domain."""
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    path: list[StrictStr | Index]
    tests: list[Annotated[TypeTest | EqualsTest | PythonExceptionTest, Field(discriminator="kind")]] = Field(min_length=1)
    outcome: Index

    @model_validator(mode="after")
    def bounded_choice(self):
        if any(isinstance(test, PythonExceptionTest) for test in self.tests) and (self.path or len(self.tests) != 1):
            raise ValueError("Python exception matching applies one handler test to the thrown value itself")
        if self.outcome > len(self.tests):
            raise ValueError("selector.outcome must index a test or the final remainder")
        if len({test.model_dump_json() for test in self.tests}) != len(self.tests):
            raise ValueError("selector.tests must not repeat a test")
        return self


class CaseGuard(Selector):
    input_index: Index

    @model_validator(mode="after")
    def json_guard(self):
        if any(isinstance(test, PythonExceptionTest) for test in self.tests):
            raise ValueError("Python exception selectors belong to a typed handler dispatch")
        return self
