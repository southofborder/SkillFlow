"""Typed data descriptions, independent of CFG execution and propagation.

Sensitivity evidences are reserved for the later DOE assessment, not provenance
for propagation. The registry owns identity and cross-record consistency; these
models check only the shape and local invariants of each record.
"""

from __future__ import annotations

import math
from typing import Annotated, Literal, TypeVar

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    JsonValue,
    StringConstraints,
    field_validator,
    model_validator,
)


def _require_list(value: object) -> object:
    # Pydantic 2.5 still coerces tuples for lists despite model strict=True.
    if type(value) is not list:
        raise ValueError("expected a list")
    return value


_Item = TypeVar("_Item")
_StrictList = Annotated[list[_Item], BeforeValidator(_require_list)]
Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
PathStep = str | Annotated[int, Field(ge=0)]
Path = Annotated[_StrictList[PathStep], Field(min_length=1)]


def path_key(path: Path) -> tuple[str | int, ...]:
    """Return a hashable key for an already validated, typed location."""
    return tuple(path)


def _require_unique(values: list, field_name: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{field_name}: duplicate values")


def _check_json_value(value: object, ancestors: set[int] | None = None) -> None:
    """Reject Python-only values before JsonValue can coerce them.

    Repeated references to the same container are legal JSON trees when
    serialized; references back to an ancestor are cycles and are rejected.
    """
    value_type = type(value)
    if value is None or value_type in (str, bool, int):
        return
    if value_type is float:
        if not math.isfinite(value):
            raise ValueError("literal value must not contain NaN or Infinity")
        return
    if value_type not in (dict, list):
        raise ValueError("literal value must contain only JSON types")
    if ancestors is None:
        ancestors = set()
    identity = id(value)
    if identity in ancestors:
        raise ValueError("literal value must not contain a reference cycle")
    ancestors.add(identity)
    try:
        if value_type is dict:
            for key, child in value.items():
                if type(key) is not str:
                    raise ValueError("literal object keys must be strings")
                _check_json_value(child, ancestors)
        else:
            for child in value:
                _check_json_value(child, ancestors)
    finally:
        ancestors.remove(identity)


class StrictRecord(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, frozen=True, revalidate_instances="always"
    )


class DataPart(StrictRecord):
    path: Path
    data: Text


class OpaqueContent(StrictRecord):
    form: Literal["opaque"] = "opaque"


class KnownPartsContent(StrictRecord):
    form: Literal["known_parts"] = "known_parts"
    parts: _StrictList[DataPart] = Field(default_factory=list)
    parts_complete: bool = False

    @model_validator(mode="after")
    def unique_paths(self) -> "KnownPartsContent":
        _require_unique([path_key(part.path) for part in self.parts], "parts.path")
        return self


class WholeExceptContent(StrictRecord):
    form: Literal["whole_except"] = "whole_except"
    base: Text
    excluded_parts: Annotated[_StrictList[Path], Field(min_length=1)]

    @model_validator(mode="after")
    def unique_exclusions(self) -> "WholeExceptContent":
        _require_unique([path_key(path) for path in self.excluded_parts], "excluded_parts")
        return self


class FieldUpdatesContent(StrictRecord):
    """An overlay on a whole value; unmentioned content remains in the base.

    Updates are simultaneous non-overlapping path assignments. Sequential or
    overlapping assignments require separate Data versions, not list order.
    """

    form: Literal["field_updates"] = "field_updates"
    base: Text
    updates: Annotated[_StrictList[DataPart], Field(min_length=1)]

    @model_validator(mode="after")
    def nonoverlapping_updates(self) -> "FieldUpdatesContent":
        paths = [path_key(part.path) for part in self.updates]
        for index, left in enumerate(paths):
            for right in paths[index + 1:]:
                if left == right[:len(left)] or right == left[:len(right)]:
                    raise ValueError("updates paths must not overlap or repeat")
        return self


class LiteralContent(StrictRecord):
    form: Literal["literal"] = "literal"
    value: JsonValue

    @field_validator("value", mode="before")
    @classmethod
    def strict_json_value(cls, value: object) -> object:
        _check_json_value(value)
        return value


Content = Annotated[
    OpaqueContent | KnownPartsContent | WholeExceptContent | FieldUpdatesContent | LiteralContent,
    Field(discriminator="form"),
]


class Dependency(StrictRecord):
    data: Text
    relation: Literal["derived", "possible"]


class Origin(StrictRecord):
    at: Text | None = None
    acquired_from: Text | None = None
    part_of: Text | None = None
    path: Path | None = None
    inputs: _StrictList[Text] = Field(default_factory=list)
    dependencies: _StrictList[Dependency] = Field(default_factory=list)

    @model_validator(mode="after")
    def consistent_origin(self) -> "Origin":
        if (self.part_of is None) != (self.path is None):
            raise ValueError("part_of and path must be supplied together")
        if self.part_of is not None and (
            self.at is not None
            or self.acquired_from is not None
            or self.inputs
            or self.dependencies
        ):
            raise ValueError("part origin cannot also describe an acquisition or operation")
        _require_unique(
            [(item.data, item.relation) for item in self.dependencies], "dependencies"
        )
        return self


class Annotations(StrictRecord):
    """Descriptions and sensitivity labels; evidences support only sensitivity.

    The module stores these strings without performing a DOE assessment or
    verifying their semantic truth. Propagation does not populate them.
    """

    description: Text | None = None
    sensitivity: _StrictList[Text] = Field(default_factory=list)
    evidences: _StrictList[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_annotations(self) -> "Annotations":
        _require_unique(self.sensitivity, "sensitivity")
        _require_unique(self.evidences, "evidences")
        return self


class Data(StrictRecord):
    id: Text
    content: Content
    origin: Origin = Field(default_factory=Origin)
    annotations: Annotations = Field(default_factory=Annotations)
