"""Strict propagation records, without transfer rules or execution semantics.

States contain may-bindings to Data identities.  Event order is the order of
Security Profile occurrences, not a claim that partial-order stages execute in
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
    model_serializer,
    model_validator,
)

from skillflow.propagation.contracts.profiles import Effect
from skillflow.propagation.contracts.specs import Precedence
from skillflow.propagation.contracts.specs import SpecPath


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
    "filter_items",
]


class StateChange(StrictRecord):
    location: FlowLocation
    before: CandidateIDs
    after: CandidateIDs
    update: Literal["strong", "weak", "delete"]

    @field_serializer("before", "after", when_used="json")
    def serialize_candidates(self, values: frozenset[str]) -> list[str]:
        return sorted(values)


class BuildMemberRecord(StrictRecord):
    """A member's payload/control slots; omitted values have no payload slot."""

    path: SpecPath
    value_input_index: Annotated[int, Field(strict=True, ge=0)] | None
    when_input_index: Annotated[int, Field(strict=True, ge=0)] | None


class AtomicOpRecord(StrictRecord):
    op: AtomicOperation
    inputs: StrictList[DataIDs] = Field(default_factory=list)
    outputs: StrictList[DataIDs] = Field(default_factory=list)
    endpoints: StrictList[FlowLocation] = Field(default_factory=list)
    changes: StrictList[StateChange] = Field(default_factory=list)
    members: StrictList[BuildMemberRecord] | None = None
    when_input_index: Annotated[int, Field(strict=True, ge=0)] | None = None

    @model_validator(mode="after")
    def validate_consumption(self):
        from skillflow.propagation.conditions import validate_record_consumption
        validate_record_consumption(self)
        return self

    @model_serializer(mode="wrap")
    def serialize_consumption(self, handler):
        data = handler(self)
        if self.members is None:
            data.pop("members", None)
        if self.when_input_index is None:
            data.pop("when_input_index", None)
        return data

    @field_serializer("inputs", "outputs", when_used="json")
    def serialize_bindings(self, values: list[frozenset[str]]) -> list[list[str]]:
        # Slot order and repeated parameter uses matter; only each may-set sorts.
        return [sorted(ids) for ids in values]


class EffectEvent(StrictRecord):
    effect: Effect | None
    atomic_ops: StrictList[AtomicOpRecord] = Field(default_factory=list)


class ForEachInstance(StrictRecord):
    """One collection candidate and one member, retaining paired body values."""

    collection: Text
    element: Text
    body: StrictList[EffectEvent]


class ForEachRecord(StrictRecord):
    """Symbolic member scopes, not runtime loop iterations or parameter unions."""

    kind: Literal["for_each"]
    collections: DataIDs
    instances: StrictList[ForEachInstance]

    @field_serializer("collections", when_used="json")
    def serialize_collections(self, values: frozenset[str]) -> list[str]:
        return sorted(values)


class IRFlowRecord(StrictRecord):
    """Complete IR states and per-spec events, never iteration logs.

    Null-effect events retain computations or tool acquisition without inventing
    security effects. Empty effects do not imply equal entry and exit states.
    """

    order: Literal["fixed", "partial"]
    precedence: StrictList[Precedence]
    entry_state: FlowState
    exit_state: FlowState
    events: StrictList[EffectEvent | ForEachRecord] = Field(default_factory=list)


    @model_validator(mode="after")
    def validate_order_coordinates(self):
        from skillflow.propagation.contracts.specs import operation_key
        edges = []
        def check(position):
            if position.event_index >= len(self.events):
                raise ValueError("precedence event position does not exist")
            event = self.events[position.event_index]
            if isinstance(event, ForEachRecord):
                if position.body_event_index is None:
                    raise ValueError("precedence on a member scope requires a body position")
                # An explicitly empty collection has no evaluated body. Its
                # frozen specification is checked by the full-run loader.
                for instance in event.instances:
                    if position.body_event_index >= len(instance.body) or position.op_index >= len(instance.body[position.body_event_index].atomic_ops):
                        raise ValueError("precedence body operation does not exist")
            elif position.body_event_index is not None or position.op_index >= len(event.atomic_ops):
                raise ValueError("precedence operation position does not exist")
        for item in self.precedence:
            check(item.before)
            check(item.after)
            edges.append((operation_key(item.before), operation_key(item.after)))
        if len(edges) != len(set(edges)):
            raise ValueError("duplicate precedence constraint")
        # Atomic list order remains mandatory even when other event order is
        # partial. Include these inherent edges in the standalone DOE check,
        # otherwise an explicit op[1] -> op[0] could bypass cycle rejection.
        inherent = set()
        for e, event in enumerate(self.events):
            children = ((b, child) for instance in event.instances for b, child in enumerate(instance.body)) if isinstance(event, ForEachRecord) else [(None, event)]
            for b, child in children:
                inherent.update(((e, b, o - 1), (e, b, o)) for o in range(1, len(child.atomic_ops)))
        graph = {}
        for before, after in set(edges) | inherent:
            graph.setdefault(before, set()).add(after)
        visiting, visited = set(), set()
        def visit(node):
            if node in visiting:
                raise ValueError("cyclic precedence constraints")
            if node in visited:
                return
            visiting.add(node)
            for child in graph.get(node, ()):
                visit(child)
            visiting.remove(node)
            visited.add(node)
        for node in graph:
            visit(node)
        if self.order == "fixed":
            def ordering(key):
                return (key[0], -1 if key[1] is None else key[1], key[2])
            if any(ordering(before) >= ordering(after) for before, after in edges):
                raise ValueError("precedence contradicts fixed event order")
        return self
