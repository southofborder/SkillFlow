"""Typed symbolic transfer specifications, before any Data identities exist.

These declarations describe one IR's single effect timeline.  Validation
checks syntax, references and coverage, never guesses an open opcode's meaning.
"""

from __future__ import annotations

from skillflow.common.validation import StructuralValidationError, structural_error, validation_at
from skillflow.common.source_evidence import json_pointer

from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, JsonValue, StrictStr, StringConstraints, field_validator, model_validator, model_serializer

from skillflow.propagation.data.models import _check_json_value
from skillflow.propagation.data.models import _require_list
from skillflow.propagation.contracts.compatibility import validate_event_operations
from skillflow.propagation.contracts.compatibility import validate_operation_boundary
from skillflow.propagation.contracts.sensitivity import SensitivityDeclaration
from skillflow.propagation.contracts.demand import OperationTaskGoal, OperationExpression
from skillflow.propagation.contracts.evidence import (
    SpecEvidence, Evidences, Operator, OperatorEvidence, Effect, RawEffect,
)


from skillflow.propagation.contracts.values import (
    Text, Index, StrictSpec, InputRef, LocalRef, LiteralRef, AlternativesRef, ValueRef,
)

# Source selectors are field/index paths. Element scopes remain program-owned.
SpecPath = Annotated[list[StrictStr | Index], BeforeValidator(_require_list), Field(min_length=1)]
LocationKind = Literal["runtime_context", "storage", "model_context", "remote", "tool", "user"]

from skillflow.propagation.contracts.references import OperandRef


class LocationSpec(StrictSpec):
    kind: LocationKind
    name: Text
    operand_refs: list[OperandRef]
    access_scope: Literal["task", "recipient", "shared", "public"]
    retention: Literal["task", "persistent"] | None

    @model_validator(mode="after")
    def boundary_attributes(self) -> "LocationSpec":
        if self.kind in {"storage", "runtime_context"} and self.retention is None:
            raise ValueError("storage and runtime context require an explicit retention")
        if self.kind in {"model_context", "remote", "user"} and self.access_scope == "task":
            raise ValueError("model, remote and user boundaries cannot be task-internal")
        return self

    @field_validator("operand_refs")
    @classmethod
    def unique_operand_refs(cls, value: list[OperandRef]) -> list[OperandRef]:
        identities = [(ref.instruction_id, ref.side, ref.index) for ref in value]
        if len(set(identities)) != len(identities):
            raise ValueError("duplicate location operand reference")
        return value


class AtomicSpec(StrictSpec):
    evidences: Evidences

    @model_serializer(mode="wrap")
    def omit_empty_task_attachments(self, handler):
        result = handler(self)
        if not result.get("demands"):
            result.pop("demands", None)
        if result.get("expression") is None:
            result.pop("expression", None)
        return result


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
    inputs: list[ValueRef]
    target: Text
    when: ValueRef | None = None

    @model_serializer(mode="wrap")
    def omit_absent_condition(self, handler):
        result = handler(self)
        if self.when is None:
            result.pop("when", None)
        return result


class RawDeliverOp(AtomicSpec):
    """Conditional observations belong to the compiler, not the model."""
    op: Literal["deliver"]
    inputs: list[ValueRef]
    target: Text
    demands: list[OperationTaskGoal] = Field(default_factory=list)


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
    path: SpecPath
    output: Text


class ExcludePartsOp(AtomicSpec):
    op: Literal["exclude_parts"]
    input: ValueRef
    paths: Annotated[list[SpecPath], Field(min_length=1)]
    output: Text

    @field_validator("paths")
    @classmethod
    def unique_paths(cls, value: list[SpecPath]) -> list[SpecPath]:
        if len({tuple(path) for path in value}) != len(value):
            raise ValueError("duplicate excluded path")
        return value


class FieldValue(StrictSpec):
    path: SpecPath
    value: ValueRef


class BuildMember(StrictSpec):
    path: SpecPath
    value: ValueRef
    when: ValueRef | None = None

    @model_validator(mode="after")
    def literal_condition(self):
        if isinstance(self.when, LiteralRef) and type(self.when.value) is not bool:
            raise ValueError("build member condition must be Boolean")
        return self


class UpdateFieldsOp(AtomicSpec):
    op: Literal["update_fields"]
    input: ValueRef
    updates: Annotated[list[FieldValue], Field(min_length=1)]
    output: Text


class BuildOp(AtomicSpec):
    op: Literal["build"]
    parts: list[BuildMember]
    output: Text
    container: Literal["object", "list"]

    @model_validator(mode="after")
    def conditional_members(self):
        if self.container == "list" and any(item.when is not None for item in self.parts):
            raise ValueError("conditional build members require an object container")
        return self


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


class FilterItemsOp(AtomicSpec):
    op: Literal["filter_items"]
    input: ValueRef
    predicate: Text
    output: Text


AtomicOp = Annotated[
    ReadOp | ReceiveOp | DeliverOp | WriteOp | SelectPartOp | ExcludePartsOp
    | UpdateFieldsOp | BuildOp | ComputeOp | FilterItemsOp,
    Field(discriminator="op"),
]

class RawReadOp(ReadOp):
    demands: list[OperationTaskGoal] = Field(default_factory=list)


class RawReceiveOp(ReceiveOp):
    demands: list[OperationTaskGoal] = Field(default_factory=list)


class RawWriteOp(WriteOp):
    demands: list[OperationTaskGoal] = Field(default_factory=list)


class RawSelectPartOp(SelectPartOp):
    demands: list[OperationTaskGoal] = Field(default_factory=list)


class RawExcludePartsOp(ExcludePartsOp):
    demands: list[OperationTaskGoal] = Field(default_factory=list)


class RawUpdateFieldsOp(UpdateFieldsOp):
    demands: list[OperationTaskGoal] = Field(default_factory=list)


class RawBuildOp(BuildOp):
    demands: list[OperationTaskGoal] = Field(default_factory=list)


class RawComputeOp(ComputeOp):
    demands: list[OperationTaskGoal] = Field(default_factory=list)
    expression: OperationExpression | None = None


class RawFilterItemsOp(FilterItemsOp):
    demands: list[OperationTaskGoal] = Field(default_factory=list)
    expression: OperationExpression | None = None


RawAtomicOp = Annotated[
    RawReadOp | RawReceiveOp | RawDeliverOp | RawWriteOp | RawSelectPartOp | RawExcludePartsOp
    | RawUpdateFieldsOp | RawBuildOp | RawComputeOp | RawFilterItemsOp,
    Field(discriminator="op"),
]

def compiled_operation(operation):
    """Task attachments are normalized once, not duplicated in compiled ops."""
    value = operation.model_dump(mode="json") if hasattr(operation, "model_dump") else dict(operation)
    return {key: item for key, item in value.items() if key not in {"demands", "expression"}}


class EffectSpec(StrictSpec):
    effect: Effect | None
    evidences: list[SpecEvidence] = Field(default_factory=list)
    atomic_ops: Annotated[list[AtomicOp], Field(min_length=1)]

    @model_validator(mode="after")
    def occurrence_evidence(self):
        if self.effect is not None and not self.evidences:
            raise ValueError("each nonempty effect occurrence requires its own evidence")
        if self.effect is None and self.evidences:
            raise ValueError("null-effect events use operation evidence, not effect evidence")
        return self

    @model_serializer(mode="wrap")
    def omit_null_effect_evidence(self, handler):
        result = handler(self)
        if self.effect is None:
            result.pop("evidences", None)
        return result


class RawEffectSpec(EffectSpec):
    effect: RawEffect | None
    atomic_ops: Annotated[list[RawAtomicOp], Field(min_length=1)]


class ProcessingSpec(StrictSpec):
    kind: Literal["processing"]
    mode: Literal["model", "local", "default"]
    events: Annotated[list[RawEffectSpec], Field(min_length=1)]
    returns: list[ValueRef] = Field(default_factory=list)
    evidences: Evidences

    @model_validator(mode="after")
    def explicit_local_boundary(self):
        if self.mode != "local" and self.returns:
            raise ValueError("returns belongs only to an explicit local processing boundary")
        if self.mode == "local":
            if "returns" not in self.model_fields_set:
                raise ValueError("local processing requires explicit returns, possibly empty")
            # Source/CFG mechanism categories are checked against the frozen
            # typed registry by the annotation service, never by ID spelling.
        return self


class RawForEachSpec(StrictSpec):
    sensitivity: list[SensitivityDeclaration] = Field(default_factory=list)
    kind: Literal["for_each"]
    collection: ValueRef
    item: Text
    body: Annotated[list[ProcessingSpec], Field(min_length=1)]
    evidences: Evidences


class ForEachSpec(StrictSpec):
    sensitivity: list[SensitivityDeclaration] = Field(default_factory=list)
    kind: Literal["for_each"]
    collection: ValueRef
    item: Text
    body: Annotated[list[EffectSpec], Field(min_length=1)]
    evidences: Evidences


class OutputBinding(StrictSpec):
    output_index: Index
    value: ValueRef
    evidences: Evidences


class OperationPosition(StrictSpec):
    event_index: Index
    op_index: Index
    body_event_index: Index | None = None


class Precedence(StrictSpec):
    before: OperationPosition
    after: OperationPosition


class IRTransferSpec(StrictSpec):
    sensitivity: list[SensitivityDeclaration] = Field(default_factory=list)
    order: Literal["fixed", "partial"]
    precedence: list[Precedence]
    events: list[EffectSpec | ForEachSpec]
    output_bindings: list[OutputBinding]


class RawIRTransferSpec(StrictSpec):
    sensitivity: list[SensitivityDeclaration] = Field(default_factory=list)
    order: Literal["fixed", "partial"]
    events: list[Annotated[ProcessingSpec | RawForEachSpec, Field(discriminator="kind")]]
    output_bindings: list[OutputBinding]


def _has_effect(events):
    for event in events:
        if isinstance(event, (ForEachSpec, RawForEachSpec)):
            if _has_effect(event.body):
                return True
        elif isinstance(event, ProcessingSpec):
            if _has_effect(event.events):
                return True
        elif event.effect is not None:
            return True
    return False


class ActionSemantics(StrictSpec):
    operator: list[Operator]
    operator_evidences: Annotated[list[OperatorEvidence], Field(min_length=1)]
    empty_effect_evidences: Evidences | None = None

    @model_validator(mode="after")
    def supported_action_labels(self):
        if len(self.operator) != len(set(self.operator)):
            raise ValueError("operator: duplicate labels")
        expected = set(self.operator) if self.operator else {None}
        supplied = {item.value for item in self.operator_evidences}
        if supplied != expected:
            raise ValueError("operator evidence must cover exactly the actual labels or confirmed empty list")
        has_effect = _has_effect(self.events)
        if has_effect and "empty_effect_evidences" in self.model_fields_set:
            raise ValueError("empty-effect evidence is forbidden when any event has an effect")
        if not has_effect and self.empty_effect_evidences is None:
            raise ValueError("an IR without nonempty effects requires empty_effect_evidences")
        return self

    @model_serializer(mode="wrap")
    def omit_inapplicable_empty_evidence(self, handler):
        result = handler(self)
        if self.empty_effect_evidences is None:
            result.pop("empty_effect_evidences", None)
        return result


class IRSemantics(IRTransferSpec, ActionSemantics):
    """One compiled IR record, including action labels and its only timeline."""


class RawIRSemantics(RawIRTransferSpec, ActionSemantics):
    """One model-declared IR record before observation compilation."""


def iter_scoped_events(spec: IRTransferSpec):
    """Yield (outer event index, body index or None, effect) in semantic order."""
    for index, event in enumerate(spec.events):
        if isinstance(event, ForEachSpec):
            for body_index, child in enumerate(event.body):
                yield index, body_index, child
        else:
            yield index, None, event


def iter_effect_events(spec: IRTransferSpec):
    for _, _, event in iter_scoped_events(spec):
        yield event


def flatten_raw_spec(spec: RawIRTransferSpec) -> IRTransferSpec:
    """Remove processing boundaries solely for shared reference validation."""
    events = []
    edges = set()
    def extend_segment(segment, target, outer=None):
        start = len(target)
        target.extend(EffectSpec(effect=child.effect, evidences=child.evidences,
                                atomic_ops=[compiled_operation(op) for op in child.atomic_ops]) for child in segment.events)
        positions = [(e if outer is None else outer, None if outer is None else e, o)
                     for e in range(start, len(target)) for o in range(len(target[e].atomic_ops))]
        edges.update(zip(positions, positions[1:]))
    for event in spec.events:
        if isinstance(event, ProcessingSpec):
            extend_segment(event, events)
        else:
            body = []
            for processing in event.body:
                extend_segment(processing, body, outer=len(events))
            events.append(ForEachSpec(kind="for_each", collection=event.collection, item=event.item,
                                     body=body, sensitivity=event.sensitivity,
                                     evidences=event.evidences))
    def coordinate(key):
        return (key[0], -1 if key[1] is None else key[1], key[2])
    precedence = [Precedence(before=position_value(before), after=position_value(after))
                  for before, after in sorted(edges, key=lambda pair: (coordinate(pair[0]), coordinate(pair[1])))]
    return IRTransferSpec(order=spec.order, precedence=precedence, events=events, output_bindings=spec.output_bindings, sensitivity=spec.sensitivity)


def value_refs(operation: AtomicOp) -> list[ValueRef]:
    """Return used symbolic values in operand order, preserving repetitions."""
    from skillflow.propagation.contracts.uses import value_uses
    return [use.value for use in value_uses(operation)]


def _local_names(ref: ValueRef) -> set[str]:
    if isinstance(ref, LocalRef):
        return {ref.name}
    if isinstance(ref, AlternativesRef):
        return set().union(*(_local_names(item) for item in ref.items))
    return set()


def _validate_ref(ref: ValueRef, instruction: dict, definitions: dict[str, int], position: int, *, uncertain: bool, inside_alternatives: bool = False) -> None:
    if isinstance(ref, InputRef):
        if ref.index >= len(instruction.get("inputs", [])):
            raise structural_error("validate_ref", "", f"input reference out of range: {instruction['id']}/{ref.index}",
                                   current=ref.model_dump(mode="json"),
                                   allowed_input_indexes=[index for index, value in enumerate(instruction.get("inputs", []))
                                                          if value["type"] != "external_resource"])
        if instruction["inputs"][ref.index]["type"] == "external_resource":
            raise structural_error("validate_ref", "", "resource identity is not a data payload; use an evidenced literal or read")
    elif isinstance(ref, LocalRef):
        if ref.name not in definitions:
            raise structural_error("validate_ref", "", f"undefined local reference: {instruction['id']}/{ref.name}",
                                   current=ref.model_dump(mode="json"),
                                   available_locals=sorted(name for name, at in definitions.items() if at < position))
        if definitions[ref.name] >= position and not (uncertain and inside_alternatives):
            raise structural_error("validate_ref", "", f"local reference precedes definition: {instruction['id']}/{ref.name}")
    elif isinstance(ref, AlternativesRef):
        for item in ref.items:
            _validate_ref(item, instruction, definitions, position, uncertain=uncertain, inside_alternatives=True)
        if uncertain and not any(not _local_names(item) or all(definitions[name] < position for name in _local_names(item)) for item in ref.items):
            raise structural_error("validate_ref", "", "uncertain alternatives must preserve an already available candidate")


def _validate_fields(fields: list[FieldValue], *, container: str | None = None) -> None:
    paths = [tuple(item.path) for item in fields]
    if len(paths) != len(set(paths)):
        raise structural_error("validate_fields", "", "duplicate field path")
    for left in paths:
        for right in paths:
            if left != right and len(left) < len(right) and right[:len(left)] == left:
                raise structural_error("validate_fields", "", "overlapping field paths require separate ordered operations")
        if container == "object" and not isinstance(left[0], str):
            raise structural_error("validate_fields", "", "object construction requires field-name root paths")
        if container == "list" and type(left[0]) is not int:
            raise structural_error("validate_fields", "", "list construction requires index root paths")
    if container is not None:
        children: dict[tuple, set] = {}
        for path in paths:
            for depth, member in enumerate(path):
                children.setdefault(path[:depth], set()).add(member)
        for members in children.values():
            indexes = {member for member in members if type(member) is int}
            if indexes and len(indexes) != len(members):
                raise structural_error("validate_fields", "", "construction cannot mix object fields and list indexes at one path")
            if indexes and indexes != set(range(len(indexes))):
                raise structural_error("validate_fields", "", "complete list construction requires consecutive indexes starting at zero")


def _raw_event_paths(raw_spec):
    """Map temporary flattened coordinates back to actual raw JSON paths."""
    paths, outer = {}, 0
    for index, event in enumerate(raw_spec.events):
        if isinstance(event, ProcessingSpec):
            for child in range(len(event.events)):
                paths[f"/events/{outer}"] = f"/events/{index}/events/{child}"
                outer += 1
        else:
            paths[f"/events/{outer}"] = f"/events/{index}"
            body = 0
            for segment_index, segment in enumerate(event.body):
                for child in range(len(segment.events)):
                    paths[f"/events/{outer}/body/{body}"] = f"/events/{index}/body/{segment_index}/events/{child}"
                    body += 1
            outer += 1
    return paths


def validate_specs(cfg: dict[str, Any], annotation: Any) -> None:
    """Validate independent IRs together; retain prerequisite scope failures."""
    if isinstance(annotation, dict):
        from skillflow.propagation.contracts.profiles import AnnotationPayload
        annotation = AnnotationPayload.model_validate(annotation)
    locations, specs = annotation.locations, annotation.ir_semantics
    instructions = {item["id"]: item for block in cfg["blocks"].values() for item in block["instructions"]}
    if set(specs) != set(instructions):
        raise structural_error("validate_specs", "/ir_semantics", "IR semantics coverage must match every actual IR")
    diagnostics, identities = [], set()
    for location_id, location in locations.items():
        prefix = json_pointer("locations", location_id)
        if not location_id.strip():
            diagnostics.extend(structural_error("validate_specs", prefix, "location ID must not be blank").diagnostics)
        identity = location.kind, location.name
        if identity in identities:
            diagnostics.extend(structural_error("validate_specs", prefix, "duplicate location identity").diagnostics)
        identities.add(identity)
        for index, ref in enumerate(location.operand_refs):
            instruction = instructions.get(ref.instruction_id)
            if instruction is None or ref.index >= len(instruction.get(ref.side + "s", [])):
                diagnostics.extend(structural_error("validate_specs", prefix + f"/operand_refs/{index}",
                    "location operand reference does not exist", current=ref.model_dump(mode="json")).diagnostics)
    for ir_id, original in specs.items():
        paths = _raw_event_paths(original) if isinstance(original, RawIRTransferSpec) else {}
        try:
            spec = flatten_raw_spec(original) if paths or isinstance(original, RawIRTransferSpec) else original
            if not isinstance(original, RawIRTransferSpec):
                validate_precedence(spec)
            instruction = instructions[ir_id]
            local_errors = []
            for e, b, event in iter_scoped_events(spec):
                event_path = f"/events/{e}" + (f"/body/{b}" if b is not None else "")
                try:
                    with validation_at(event_path):
                        validate_event_operations(event.effect, [operation.op for operation in event.atomic_ops])
                except StructuralValidationError as error:
                    local_errors.extend(error.diagnostics)
            bindings = [item.output_index for item in spec.output_bindings]
            if sorted(bindings) != list(range(len(instruction.get("outputs", [])))):
                local_errors.extend(structural_error("validate_specs", "/output_bindings",
                    "output bindings must cover each actual output exactly once: " + ir_id,
                    current=bindings, allowed=list(range(len(instruction.get("outputs", []))))).diagnostics)
            try:
                definitions, count = _validate_scope(spec.events, instruction, locations,
                                                    uncertain=spec.order == "partial")
            except StructuralValidationError as error:
                local_errors.extend(error.diagnostics)
            else:
                for index, binding in enumerate(spec.output_bindings):
                    try:
                        with validation_at(f"/output_bindings/{index}/value"):
                            _validate_ref(binding.value, instruction, definitions, count, uncertain=False)
                    except StructuralValidationError as error:
                        local_errors.extend(error.diagnostics)
                from skillflow.propagation.contracts.uses import request_pairs
                try:
                    request_pairs(spec)
                except StructuralValidationError as error:
                    local_errors.extend(error.diagnostics)
            if local_errors:
                raise StructuralValidationError(local_errors)
        except StructuralValidationError as error:
            for row in error.diagnostics:
                path = row["path"]
                for old in sorted(paths, key=len, reverse=True):
                    if path == old or path.startswith(old + "/"):
                        path = paths[old] + path[len(old):]
                        break
                diagnostics.append({**row, "path": json_pointer("ir_semantics", ir_id) + path})
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    if hasattr(annotation, "sink_boundaries"):
        from skillflow.propagation.contracts.boundaries import derive_sink_boundaries
        if annotation.sink_boundaries != derive_sink_boundaries(locations, specs):
            raise structural_error("validate_specs", "/sink_boundaries", "sink boundaries must match the deterministic compiled derivation")


def _located_refs(value, path=""):
    """Locations of existing ValueRefs, excluding literal contents/evidence."""
    if isinstance(value, (InputRef, LocalRef, LiteralRef, AlternativesRef)):
        yield path, value
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _located_refs(child, path + f"/{index}")
    elif isinstance(value, BaseModel):
        for name in type(value).model_fields:
            if name not in {"evidences", "demands", "expression"}:
                yield from _located_refs(getattr(value, name), path + "/" + name)


def _validate_scope(events, instruction, locations, *, uncertain, external=None,
                    in_foreach=False, path_prefix="/events"):
    definitions, positions, diagnostics = dict(external or {}), [], []
    count = 0
    for event_index, event in enumerate(events):
        event_path = path_prefix + f"/{event_index}"
        if isinstance(event, ForEachSpec):
            if in_foreach:
                diagnostics.extend(structural_error("validate_scope", event_path, "nested for_each is not supported").diagnostics)
            positions.append((count, event, None, event_path))
            count += 1
        else:
            for op_index, operation in enumerate(event.atomic_ops):
                op_path = event_path + f"/atomic_ops/{op_index}"
                positions.append((count, event, operation, op_path))
                output = getattr(operation, "output", None)
                if output is not None:
                    if output in definitions:
                        diagnostics.extend(structural_error("validate_scope", op_path + "/output",
                            f"duplicate local definition: {instruction['id']}/{output}").diagnostics)
                    definitions[output] = count
                count += 1
    if diagnostics:
        # Scope identities must be unambiguous before reference/dependency checks.
        raise StructuralValidationError(diagnostics)
    dependencies = {}
    def check(path, function, *args, **kwargs):
        try:
            with validation_at(path):
                return function(*args, **kwargs)
        except StructuralValidationError as error:
            diagnostics.extend(error.diagnostics)
    for position, event, operation, path in positions:
        if isinstance(event, ForEachSpec):
            before = len(diagnostics)
            check(path + "/collection", _validate_ref, event.collection, instruction, definitions, position, uncertain=False)
            if event.item in definitions:
                diagnostics.extend(structural_error("validate_scope", path + "/item", "for_each item must not shadow an outer local").diagnostics)
            if len(diagnostics) == before:
                outer = {name: -1 for name, at in definitions.items() if at < position}
                outer[event.item] = -1
                check("", _validate_scope, event.body, instruction, locations, uncertain=uncertain,
                      external=outer, in_foreach=True, path_prefix=path + "/body")
            continue
        if in_foreach and isinstance(operation, (ReadOp, ReceiveOp, WriteOp)):
            diagnostics.extend(structural_error("validate_scope", path, "for_each body must not read, receive, or write shared state").diagnostics)
        effect = event.effect
        location_id = getattr(operation, "location", getattr(operation, "target", None))
        if location_id is not None and location_id not in locations:
            field = "location" if hasattr(operation, "location") else "target"
            diagnostics.extend(structural_error("validate_scope", path + "/" + field,
                f"undefined location: {location_id}", current=location_id, allowed=sorted(locations)).diagnostics)
        else:
            check(path, validate_operation_boundary, operation.op, effect,
                  None if location_id is None else locations[location_id].kind,
                  dependencies=operation.dependencies if isinstance(operation, ComputeOp) else None,
                  input_count=len(operation.inputs) if isinstance(operation, DeliverOp) else None)
        if isinstance(operation, DeliverOp) and operation.when is not None:
            if effect != "model_observe":
                diagnostics.extend(structural_error("validate_scope", path + "/when", "conditional delivery is reserved for compiled model observation").diagnostics)
            if isinstance(operation.when, LiteralRef) and type(operation.when.value) is not bool:
                diagnostics.extend(structural_error("validate_scope", path + "/when", "observation condition must be Boolean").diagnostics)
        if isinstance(operation, UpdateFieldsOp):
            check(path + "/updates", _validate_fields, operation.updates)
        if isinstance(operation, BuildOp):
            check(path + "/parts", _validate_fields, operation.parts, container=operation.container)
        refs = value_refs(operation)
        refs_valid = True
        for ref_path, ref in _located_refs(operation):
            before = len(diagnostics)
            check(path + ref_path, _validate_ref, ref, instruction, definitions, position, uncertain=uncertain)
            if in_foreach and len(diagnostics) == before:
                check(path + ref_path, _reject_context_input, ref, instruction)
            refs_valid &= len(diagnostics) == before
        if refs_valid:
            from skillflow.propagation.contracts.uses import value_uses, static_condition
            for use in value_uses(operation):
                if use.role == "control":
                    check(path, static_condition, use.value, instruction)
        output = getattr(operation, "output", None)
        if output is not None and refs_valid:
            dependencies[output] = set().union(*(_local_names(ref) for ref in refs)) if refs else set()
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    visiting, visited = set(), set()
    def visit(name):
        if name in visiting:
            raise structural_error("validate_scope", path_prefix, f"cyclic local definitions: {instruction['id']}/{name}")
        if name in visited:
            return
        visiting.add(name)
        for parent in dependencies.get(name, set()):
            visit(parent)
        visiting.remove(name)
        visited.add(name)
    for name in definitions:
        visit(name)
    return definitions, count


def _reject_context_input(ref, instruction):
    if isinstance(ref, InputRef) and instruction["inputs"][ref.index]["type"] == "context_key":
        raise structural_error("reject_context_input", "", "for_each body must not depend on mutable context_key operands")
    if isinstance(ref, AlternativesRef):
        for child in ref.items:
            _reject_context_input(child, instruction)


def iter_located_spec_evidence(annotation: Any):
    """Yield each actual source/CFG/rule evidence with its candidate path."""
    def listed(items, path):
        for index, evidence in enumerate(items):
            yield path + f"/{index}", evidence
    def effects(events, path):
        for index, event in enumerate(events):
            position = path + f"/{index}"
            yield from listed(event.evidences, position + "/evidences")
            if isinstance(event, (RawForEachSpec, ForEachSpec)):
                yield from effects(event.body, position + "/body")
            elif isinstance(event, ProcessingSpec):
                yield from effects(event.events, position + "/events")
            else:
                for op_index, operation in enumerate(event.atomic_ops):
                    yield from listed(operation.evidences, position + f"/atomic_ops/{op_index}/evidences")
    for ir_id, spec in annotation.ir_semantics.items():
        prefix = json_pointer("ir_semantics", ir_id)
        yield from listed(spec.operator_evidences, prefix + "/operator_evidences")
        yield from listed(spec.empty_effect_evidences or [], prefix + "/empty_effect_evidences")
        yield from effects(spec.events, prefix + "/events")
        for index, binding in enumerate(spec.output_bindings):
            yield from listed(binding.evidences, prefix + f"/output_bindings/{index}/evidences")


def iter_spec_evidence(annotation: Any):
    """Yield evidence values, retaining the existing enumeration order."""
    for _, evidence in iter_located_spec_evidence(annotation):
        yield evidence


def operation_key(position):
    """Stable coordinates; None marks the ordinary (non-member) scope."""
    if isinstance(position, dict):
        position = OperationPosition.model_validate(position)
    return (position.event_index, position.body_event_index, position.op_index)


def position_value(key):
    event, body, op = key
    return {"event_index": event, "body_event_index": body, "op_index": op}


def operation_items(spec):
    return {(e, b, o): op for e, b, event in iter_scoped_events(spec)
            for o, op in enumerate(event.atomic_ops)}


def _required_local_names(ref):
    # Alternatives are may-values: an early observation may use the already
    # available candidate while another arrangement can include a later value.
    return {ref.name} if isinstance(ref, LocalRef) else set()


def structural_precedence(spec):
    """Causal constraints derivable without interpreting free-form text."""
    operations = operation_items(spec)
    edges = set()
    definitions = {}
    for (e, b, o), op in operations.items():
        if o:
            edges.add(((e, b, o - 1), (e, b, o)))
        if hasattr(op, "output"):
            definitions[(None if b is None else e, op.output)] = (e, b, o)
    for key, op in operations.items():
        scope = None if key[1] is None else key[0]
        for ref in value_refs(op):
            for name in _required_local_names(ref):
                origin = definitions.get((scope, name), definitions.get((None, name)))
                if origin is not None:
                    edges.add((origin, key))
    # A collection and every outer value used by a member scope must be ready
    # before that scope starts. No artificial operation is added to the wire.
    for e, event in enumerate(spec.events):
        if isinstance(event, ForEachSpec):
            for name in _local_names(event.collection):
                origin = definitions.get((None, name))
                if origin is not None:
                    for key in operations:
                        if key[0] == e and key[1] is not None:
                            edges.add((origin, key))
    return edges


def precedence_edges(spec):
    edges = {(operation_key(item.before), operation_key(item.after)) for item in spec.precedence}
    edges |= structural_precedence(spec)
    from skillflow.propagation.contracts.uses import request_precedence
    edges |= request_precedence(spec)
    if spec.order == "fixed":
        keys = list(operation_items(spec))
        edges.update(zip(keys, keys[1:]))
    return edges


def precedence_closure(spec):
    nodes = set(operation_items(spec))
    edges = precedence_edges(spec)
    following = {node: set() for node in nodes}
    for before, after in edges:
        following[before].add(after)
    changed = True
    while changed:
        changed = False
        for node in nodes:
            expanded = following[node] | set().union(*(following[child] for child in following[node]))
            if expanded != following[node]:
                following[node] = expanded
                changed = True
    return following


def validate_precedence(spec):
    nodes = set(operation_items(spec))
    pairs = [(operation_key(item.before), operation_key(item.after)) for item in spec.precedence]
    if len(pairs) != len(set(pairs)):
        raise structural_error("validate_precedence", "", "duplicate precedence constraint")
    if any(before not in nodes or after not in nodes for before, after in pairs):
        raise structural_error("validate_precedence", "", "precedence references a nonexistent operation")
    if any(before == after for before, after in pairs):
        raise structural_error("validate_precedence", "", "precedence cannot order an operation before itself")
    closure = precedence_closure(spec)
    if any(node in after for node, after in closure.items()):
        raise structural_error("validate_precedence", "", "cyclic precedence constraints")
    # References to the same member scope remain local. A body cannot depend
    # on a later external operation while earlier body work must precede it;
    # this would require interleaving a symbolic collection with shared state,
    # outside the single-level member model.
    for e, event in enumerate(spec.events):
        if isinstance(event, ForEachSpec):
            members = {key for key in nodes if key[0] == e and key[1] is not None}
            for outer in nodes - members:
                if any(outer in closure[member] for member in members) and any(member in closure[outer] for member in members):
                    raise structural_error("validate_precedence", "", "precedence requires unsupported scope/shared-state interleaving")


def schedule_dependencies(spec, *, outer_event=None):
    """Collapse member scopes for outer scheduling, retaining atomic granularity.

    Processing segments are never scheduling atoms: their primitive operations
    can interleave with operations of other segments if no constraint forbids it.
    """
    result = {}
    def project(key):
        e, b, o = key
        if outer_event is None:
            return (e, -1) if b is not None else (e, o)
        return (b, o) if e == outer_event and b is not None else None
    for key in operation_items(spec):
        target = project(key)
        if target is not None:
            result.setdefault(target, set())
    for before, after in precedence_edges(spec):
        left, right = project(before), project(after)
        if left is not None and right is not None and left != right:
            result[right].add(left)
    return result
