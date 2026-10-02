"""Strict propagation records, without transfer rules or execution semantics.

States contain may-bindings to Data identities.  Event order is the order of
Security Profile occurrences, not a claim that unresolved stages execute in
that order.  Cross-record references are checked by the record container.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Literal, TypeVar

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PrivateAttr,
    StringConstraints,
    field_serializer,
    model_validator,
)

from skill_ir.security_profile.models import Effect


Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
LocationKind = Literal[
    "result", "runtime_context", "storage", "model_context", "remote", "tool", "user",
    "intermediate",
]


def _require_list(value: object) -> object:
    if type(value) is not list:
        raise ValueError("expected a list")
    return value


def _data_ids(value: object) -> frozenset[str]:
    """Accept the native set or its explicit JSON-array representation.

    A repeated ID in the wire array is rejected rather than silently erased.
    Strings, mutable sets and arbitrary iterables are not collection inputs.
    """
    if type(value) not in (frozenset, list):
        raise ValueError("data_ids must be a frozenset or a JSON list")
    if not value:
        raise ValueError("data_ids must not be empty")
    if any(type(item) is not str for item in value):
        raise ValueError("data_ids must contain only strings")
    if len(value) != len(set(value)):
        raise ValueError("data_ids contains duplicate identities")
    return frozenset(value)


def _state_bindings(value: object) -> tuple:
    # Tuples are the internal representation.  Lists are the JSON and friendly
    # constructor representation; both are copied into the immutable sequence.
    if type(value) not in (list, tuple):
        raise ValueError("bindings must be a list or tuple")
    return tuple(value)


_Item = TypeVar("_Item")
StrictList = Annotated[list[_Item], BeforeValidator(_require_list)]
DataIDs = Annotated[frozenset[Text], BeforeValidator(_data_ids)]


class StrictRecord(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, frozen=True, revalidate_instances="always"
    )


class FlowLocation(StrictRecord):
    """A hashable location whose category is part of its identity."""

    kind: LocationKind
    name: Text


class StateBinding(StrictRecord):
    location: FlowLocation
    data_ids: DataIDs

    @field_serializer("data_ids", when_used="json")
    def serialize_data_ids(self, values: frozenset[str]) -> list[str]:
        return sorted(values)


class FlowState(StrictRecord):
    """An indexed may-state; empty bindings do not mean unreachable.

    The binding tuple, locations and ID sets are immutable, so the private
    index cannot become stale through a mutable public binding list.
    """

    bindings: Annotated[
        tuple[StateBinding, ...], BeforeValidator(_state_bindings)
    ] = ()
    _location_index: dict[FlowLocation, frozenset[str]] = PrivateAttr(
        default_factory=dict
    )

    @model_validator(mode="after")
    def index_bindings(self) -> "FlowState":
        index: dict[FlowLocation, frozenset[str]] = {}
        for binding in self.bindings:
            if binding.location in index:
                raise ValueError("duplicate state location")
            index[binding.location] = binding.data_ids
        ordered = tuple(sorted(
            self.bindings, key=lambda item: (item.location.kind, item.location.name)
        ))
        object.__setattr__(self, "bindings", ordered)
        self._location_index = index
        return self

    @field_serializer("bindings", when_used="json")
    def serialize_bindings(self, values: tuple[StateBinding, ...]) -> list[dict]:
        return [binding.model_dump(mode="json") for binding in values]

    def get(self, location: FlowLocation) -> frozenset[str] | None:
        """Return the candidate identities, or None for an unrecorded location."""
        checked = FlowLocation.model_validate(location)
        return self._location_index.get(checked)

    @classmethod
    def from_mapping(
        cls, mapping: Mapping[FlowLocation, frozenset[str]]
    ) -> "FlowState":
        if not isinstance(mapping, Mapping):
            raise ValueError("state bindings must be a mapping")
        return cls(bindings=[
            StateBinding(location=location, data_ids=data_ids)
            for location, data_ids in mapping.items()
        ])


def _candidate_ids(value: object) -> frozenset[str]:
    if type(value) not in (frozenset, list):
        raise ValueError("candidate IDs must be a frozenset or a JSON list")
    if not value:
        return frozenset()
    return _data_ids(value)


CandidateIDs = Annotated[frozenset[Text], BeforeValidator(_candidate_ids)]
AtomicOperation = Literal[
    "read", "receive", "deliver", "write", "select_part", "exclude_parts",
    "update_fields", "build", "compute",
]


class StateChange(StrictRecord):
    location: FlowLocation
    before: CandidateIDs
    after: CandidateIDs
    update: Literal["strong", "weak", "delete"]

    @field_serializer("before", "after", when_used="json")
    def serialize_candidates(self, values: frozenset[str]) -> list[str]:
        return sorted(values)


class AtomicOpRecord(StrictRecord):
    op: AtomicOperation
    inputs: StrictList[DataIDs] = Field(default_factory=list)
    outputs: StrictList[DataIDs] = Field(default_factory=list)
    endpoints: StrictList[FlowLocation] = Field(default_factory=list)
    changes: StrictList[StateChange] = Field(default_factory=list)

    @field_serializer("inputs", "outputs", when_used="json")
    def serialize_bindings(self, values: list[frozenset[str]]) -> list[list[str]]:
        # Slot order and repeated parameter uses matter; only each may-set sorts.
        return [sorted(ids) for ids in values]


class EffectEvent(StrictRecord):
    effect: Effect | None
    atomic_ops: StrictList[AtomicOpRecord] = Field(default_factory=list)


class IRFlowRecord(StrictRecord):
    """Complete IR states and per-spec events, never iteration logs.

    Null-effect events retain computations or tool acquisition without inventing
    security effects. Empty effects do not imply equal entry and exit states.
    """

    entry_state: FlowState
    exit_state: FlowState
    events: StrictList[EffectEvent] = Field(default_factory=list)
