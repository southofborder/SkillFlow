"""Typed symbolic transfer specifications, before any Data identities exist.

These declarations describe one IR's single effect timeline.  Validation
checks syntax, references and coverage, never guesses an open opcode's meaning.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, StringConstraints, field_validator, model_validator

from skill_ir.data.models import Path, _check_json_value
from .compatibility import validate_event_operations, validate_operation_boundary


Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
Index = Annotated[int, Field(strict=True, ge=0)]
LocationKind = Literal["runtime_context", "storage", "model_context", "remote", "tool", "user"]


class StrictSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class SpecEvidence(StrictSpec):
    basis: Literal["source", "cfg", "execution_model"]
    ref_id: Text
    quote: Text
    reason: Text


Evidences = Annotated[list[SpecEvidence], Field(min_length=1)]


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
    def strict_json(cls, value: Any) -> Any:
        _check_json_value(value)
        return value


class AlternativesRef(StrictSpec):
    kind: Literal["alternatives"]
    items: list["ValueRef"]

    @field_validator("items")
    @classmethod
    def nonempty(cls, value: list["ValueRef"]) -> list["ValueRef"]:
        if not value:
            raise ValueError("alternatives must contain at least one candidate")
        return value


ValueRef = Annotated[InputRef | LocalRef | LiteralRef | AlternativesRef, Field(discriminator="kind")]
AlternativesRef.model_rebuild()


class OperandRef(StrictSpec):
    instruction_id: Text
    side: Literal["input", "output"]
    index: Index


class LocationSpec(StrictSpec):
    kind: LocationKind
    name: Text
    operand_refs: list[OperandRef]

    @field_validator("operand_refs")
    @classmethod
    def unique_operand_refs(cls, value: list[OperandRef]) -> list[OperandRef]:
        identities = [(ref.instruction_id, ref.side, ref.index) for ref in value]
        if len(set(identities)) != len(identities):
            raise ValueError("duplicate location operand reference")
        return value


class AtomicSpec(StrictSpec):
    evidences: Evidences


class ReadOp(AtomicSpec):
    op: Literal["read"]
    location: Text
    output: Text


class ReceiveOp(AtomicSpec):
    op: Literal["receive"]
    location: Text
    inputs: list[ValueRef]
    output: Text


class DeliverOp(AtomicSpec):
    op: Literal["deliver"]
    inputs: Annotated[list[ValueRef], Field(min_length=1)]
    target: Text


class WriteOp(AtomicSpec):
    op: Literal["write"]
    target: Text
    mode: Literal["replace", "append", "delete"]
    input: ValueRef | None = None

    @model_validator(mode="after")
    def write_operand(self) -> "WriteOp":
        if self.mode == "delete" and self.input is not None:
            raise ValueError("delete write must not read a value")
        if self.mode != "delete" and self.input is None:
            raise ValueError("replace/append write requires input")
        return self


class SelectPartOp(AtomicSpec):
    op: Literal["select_part"]
    input: ValueRef
    path: Path
    output: Text


class ExcludePartsOp(AtomicSpec):
    op: Literal["exclude_parts"]
    input: ValueRef
    paths: Annotated[list[Path], Field(min_length=1)]
    output: Text

    @field_validator("paths")
    @classmethod
    def unique_paths(cls, value: list[Path]) -> list[Path]:
        if len({tuple(path) for path in value}) != len(value):
            raise ValueError("duplicate excluded path")
        return value


class FieldValue(StrictSpec):
    path: Path
    value: ValueRef


class UpdateFieldsOp(AtomicSpec):
    op: Literal["update_fields"]
    input: ValueRef
    updates: Annotated[list[FieldValue], Field(min_length=1)]
    output: Text


class BuildOp(AtomicSpec):
    op: Literal["build"]
    parts: list[FieldValue]
    output: Text
    container: Literal["object", "list"]


class ComputeOp(AtomicSpec):
    op: Literal["compute"]
    inputs: list[ValueRef]
    dependencies: list[Literal["derived", "possible"]]
    output: Text

    @model_validator(mode="after")
    def dependency_arity(self) -> "ComputeOp":
        if len(self.inputs) != len(self.dependencies):
            raise ValueError("compute dependencies must match inputs one-to-one")
        return self


AtomicOp = Annotated[
    ReadOp | ReceiveOp | DeliverOp | WriteOp | SelectPartOp | ExcludePartsOp
    | UpdateFieldsOp | BuildOp | ComputeOp,
    Field(discriminator="op"),
]


class EffectSpec(StrictSpec):
    effect_index: Index | None
    atomic_ops: Annotated[list[AtomicOp], Field(min_length=1)]


class OutputBinding(StrictSpec):
    output_index: Index
    value: ValueRef
    evidences: Evidences


class IRTransferSpec(StrictSpec):
    events: list[EffectSpec]
    output_bindings: list[OutputBinding]


def value_refs(operation: AtomicOp) -> list[ValueRef]:
    """Return used symbolic values in operand order, preserving repetitions."""
    if isinstance(operation, (ReceiveOp, DeliverOp, ComputeOp)):
        return list(operation.inputs)
    if isinstance(operation, WriteOp):
        return [] if operation.input is None else [operation.input]
    if isinstance(operation, (SelectPartOp, ExcludePartsOp)):
        return [operation.input]
    if isinstance(operation, UpdateFieldsOp):
        return [operation.input, *(item.value for item in operation.updates)]
    if isinstance(operation, BuildOp):
        return [item.value for item in operation.parts]
    return []


def _local_names(ref: ValueRef) -> set[str]:
    if isinstance(ref, LocalRef):
        return {ref.name}
    if isinstance(ref, AlternativesRef):
        return set().union(*(_local_names(item) for item in ref.items))
    return set()


def _validate_ref(ref: ValueRef, instruction: dict, definitions: dict[str, int], position: int, *, uncertain: bool, inside_alternatives: bool = False) -> None:
    if isinstance(ref, InputRef):
        if ref.index >= len(instruction.get("inputs", [])):
            raise ValueError(f"input reference out of range: {instruction['id']}/{ref.index}")
        if instruction["inputs"][ref.index]["type"] == "external_resource":
            raise ValueError("resource identity is not a data payload; use an evidenced literal or read")
    elif isinstance(ref, LocalRef):
        if ref.name not in definitions:
            raise ValueError(f"undefined local reference: {instruction['id']}/{ref.name}")
        if definitions[ref.name] >= position and not (uncertain and inside_alternatives):
            raise ValueError(f"local reference precedes definition: {instruction['id']}/{ref.name}")
    elif isinstance(ref, AlternativesRef):
        for item in ref.items:
            _validate_ref(item, instruction, definitions, position, uncertain=uncertain, inside_alternatives=True)
        if uncertain and not any(not _local_names(item) or all(definitions[name] < position for name in _local_names(item)) for item in ref.items):
            raise ValueError("uncertain alternatives must preserve an already available candidate")


def _validate_fields(fields: list[FieldValue], *, container: str | None = None) -> None:
    paths = [tuple(item.path) for item in fields]
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate field path")
    for left in paths:
        for right in paths:
            if left != right and len(left) < len(right) and right[:len(left)] == left:
                raise ValueError("overlapping field paths require separate ordered operations")
        if container == "object" and not isinstance(left[0], str):
            raise ValueError("object construction requires field-name root paths")
        if container == "list" and type(left[0]) is not int:
            raise ValueError("list construction requires index root paths")
    if container is not None:
        children: dict[tuple, set] = {}
        for path in paths:
            for depth, member in enumerate(path):
                children.setdefault(path[:depth], set()).add(member)
        for members in children.values():
            indexes = {member for member in members if type(member) is int}
            if indexes and len(indexes) != len(members):
                raise ValueError("construction cannot mix object fields and list indexes at one path")
            if indexes and indexes != set(range(len(indexes))):
                raise ValueError("complete list construction requires consecutive indexes starting at zero")


def validate_specs(cfg: dict[str, Any], annotation: Any) -> None:
    """Validate a parsed joint annotation; quoted text is checked upstream."""
    if isinstance(annotation, dict):
        from skill_ir.security_profile.models import AnnotationPayload
        annotation = AnnotationPayload.model_validate(annotation)
    profiles = annotation.profiles
    locations = annotation.locations
    specs = annotation.transfer_specs
    instructions = {item["id"]: item for block in cfg["blocks"].values() for item in block["instructions"]}
    expected = set(instructions)
    if set(specs) != expected or set(profiles) != expected:
        raise ValueError("transfer/profile coverage must match every actual IR")
    identities: set[tuple[str, str]] = set()
    for location_id, location in locations.items():
        if not location_id.strip():
            raise ValueError("location ID must not be blank")
        identity = location.kind, location.name
        if identity in identities:
            raise ValueError("duplicate location identity")
        identities.add(identity)
        for ref in location.operand_refs:
            instruction = instructions.get(ref.instruction_id)
            if instruction is None or ref.index >= len(instruction.get(ref.side + "s", [])):
                raise ValueError("location operand reference does not exist")
    unknown_order = {item.instruction_id for item in annotation.unresolved if item.field == "effects"}
    for ir_id, spec in specs.items():
        instruction = instructions[ir_id]
        effects = profiles[ir_id].effects
        indices = [event.effect_index for event in spec.events if event.effect_index is not None]
        if indices != list(range(len(effects))):
            raise ValueError(f"event effect positions must match profile exactly: {ir_id}")
        for event in spec.events:
            effect = None if event.effect_index is None else effects[event.effect_index]
            validate_event_operations(effect, [operation.op for operation in event.atomic_ops])
        bindings = [item.output_index for item in spec.output_bindings]
        if sorted(bindings) != list(range(len(instruction.get("outputs", [])))):
            raise ValueError(f"output bindings must cover each actual output exactly once: {ir_id}")
        operations = [(event.effect_index, operation) for event in spec.events for operation in event.atomic_ops]
        definitions: dict[str, int] = {}
        for position, (_, operation) in enumerate(operations):
            output = getattr(operation, "output", None)
            if output is not None:
                if output in definitions:
                    raise ValueError(f"duplicate local definition: {ir_id}/{output}")
                definitions[output] = position
        dependency_graph: dict[str, set[str]] = {}
        for position, (effect_index, operation) in enumerate(operations):
            effect = None if effect_index is None else effects[effect_index]
            location_id = getattr(operation, "location", getattr(operation, "target", None))
            if location_id is not None:
                if location_id not in locations:
                    raise ValueError(f"undefined location: {location_id}")
            validate_operation_boundary(
                operation.op, effect, None if location_id is None else locations[location_id].kind,
                dependencies=operation.dependencies if isinstance(operation, ComputeOp) else None,
            )
            if isinstance(operation, UpdateFieldsOp):
                _validate_fields(operation.updates)
            if isinstance(operation, BuildOp):
                _validate_fields(operation.parts, container=operation.container)
            refs = value_refs(operation)
            for ref in refs:
                _validate_ref(ref, instruction, definitions, position, uncertain=ir_id in unknown_order)
            output = getattr(operation, "output", None)
            if output is not None:
                dependency_graph[output] = set().union(*(_local_names(ref) for ref in refs)) if refs else set()
        visiting: set[str] = set()
        visited: set[str] = set()
        def visit(name: str) -> None:
            if name in visiting:
                raise ValueError(f"cyclic local definitions: {ir_id}/{name}")
            if name in visited:
                return
            visiting.add(name)
            for parent in dependency_graph.get(name, set()):
                visit(parent)
            visiting.remove(name)
            visited.add(name)
        for name in definitions:
            visit(name)
        for binding in spec.output_bindings:
            _validate_ref(binding.value, instruction, definitions, len(operations), uncertain=False)


def iter_spec_evidence(annotation: Any):
    """Yield operation/output evidence from a business payload, not audit sidecars."""
    for spec in annotation.transfer_specs.values():
        for event in spec.events:
            for operation in event.atomic_ops:
                yield from operation.evidences
        for binding in spec.output_bindings:
            yield from binding.evidences
