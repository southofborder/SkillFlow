"""Restricted task constraints over existing raw references and lexical values.

These declarations are not positive demand seeds or model-authored verdicts.
Operation coordinates always address the original annotation, never its compiled
observation events. Deterministic compilation and replay own resolved identities.
"""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import AfterValidator, BeforeValidator, Field, model_validator

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import json_pointer
from skillflow.common.validation import StructuralValidationError, structural_error
from skillflow.propagation.contracts.references import (
    DemandTarget, InstructionTarget, OperationTarget, ReferencePath, target_key,
)
from skillflow.propagation.contracts.sensitivity import SensitivityPath, _scope_definitions
from skillflow.propagation.contracts.specs import LocationKind
from skillflow.propagation.contracts.values import (
    StrictSpec, Text, ValueRef, InputRef, LocalRef, AlternativesRef,
)
from skillflow.propagation.data.models import _require_list


def _scope_path(value):
    if value and not (len(value) == 2 and value[0] == "events" and type(value[1]) is int):
        raise ValueError("constraint scope must be the IR or one existing for_each")
    return value


ScopePath = Annotated[ReferencePath, BeforeValidator(_require_list), AfterValidator(_scope_path)]


class TaskScope(StrictSpec):
    kind: Literal["task"]


class ElementScope(StrictSpec):
    kind: Literal["element"]
    instruction_id: Text
    scope_path: ScopePath = Field(min_length=2, max_length=2)


ConstraintScope = Annotated[TaskScope | ElementScope, Field(discriminator="kind")]


class ScopedValue(StrictSpec):
    instruction_id: Text
    scope_path: ScopePath
    value: ValueRef


def _event_reference(value):
    if isinstance(value, InstructionTarget) and value.path:
        raise ValueError("constraint instruction event must use an empty path")
    if isinstance(value, OperationTarget) and value.slot.kind != "self":
        raise ValueError("constraint operation event must select the operation itself")
    return value


EventRef = Annotated[InstructionTarget | OperationTarget, AfterValidator(_event_reference)]
EventRefs = Annotated[list[EventRef], BeforeValidator(_require_list), Field(min_length=1)]


class AllReceivers(StrictSpec):
    kind: Literal["all"]


class LocationReceivers(StrictSpec):
    kind: Literal["locations"]
    ids: Annotated[list[Text], BeforeValidator(_require_list), Field(min_length=1)]

    @model_validator(mode="after")
    def distinct_locations(self):
        if len(self.ids) != len(set(self.ids)):
            raise ValueError("constraint receiver locations must be distinct")
        return self


class KindReceivers(StrictSpec):
    kind: Literal["kind"]
    value: LocationKind


ReceiverSelector = Annotated[AllReceivers | LocationReceivers | KindReceivers, Field(discriminator="kind")]


class ConstraintBase(StrictSpec):
    scope: ConstraintScope

    @model_validator(mode="after")
    def distinct_event_sites(self):
        for name in ("events", "before", "after", "triggers"):
            values = getattr(self, name, None)
            if values is not None and len({target_key(value) for value in values}) != len(values):
                raise ValueError("constraint event selectors must be distinct")
            if values is not None:
                instructions = {value.instruction_id for value in values if isinstance(value, InstructionTarget)}
                if any(isinstance(value, OperationTarget) and value.instruction_id in instructions for value in values):
                    raise ValueError("constraint event selectors cannot overlap an instruction and its atomic operations")
        return self


class ForbidInformation(ConstraintBase):
    kind: Literal["forbid_information"]
    source: ScopedValue
    path: SensitivityPath = Field(default_factory=list)
    receivers: ReceiverSelector
    events: EventRefs | None = None


class OnlyIf(ConstraintBase):
    kind: Literal["only_if"]
    events: EventRefs
    condition: DemandTarget


class AtMost(ConstraintBase):
    kind: Literal["at_most"]
    events: EventRefs
    limit: Annotated[int, Field(strict=True, ge=0)]
    unit: Literal["attempt", "success"]
    success: DemandTarget | None = None

    @model_validator(mode="after")
    def success_condition(self):
        if (self.unit == "success") != (self.success is not None):
            raise ValueError("a success expression is required only for success counting")
        return self


class RequiresPrior(ConstraintBase):
    kind: Literal["requires_prior"]
    before: EventRefs
    after: EventRefs
    matching: Literal["scope", "request"]


class ForbidAfter(ConstraintBase):
    kind: Literal["forbid_after"]
    triggers: EventRefs
    events: EventRefs


TaskConstraint = Annotated[
    ForbidInformation | OnlyIf | AtMost | RequiresPrior | ForbidAfter,
    Field(discriminator="kind"),
]


def validate_constraints(realizations, *, cfg, raw, targets, expressions, locations):
    """Validate raw correspondence, not satisfaction or occurrence feasibility."""
    from skillflow.propagation.contracts.demand import _known_literals
    instructions = {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}
    expression_index = {target_key(row.target): row.expression for row in expressions}
    diagnostics, expressed = [], set()

    def fail(code, pointer, message):
        diagnostics.extend(structural_error(code, pointer, message).diagnostics)

    def scoped_definitions(owner, path, pointer):
        if owner not in instructions or owner not in raw["ir_semantics"]:
            fail("constraint_scope", pointer, "Constraint scope references an absent instruction.")
            return None
        try:
            return _scope_definitions(raw["ir_semantics"][owner], path)
        except (ValueError, IndexError, KeyError) as error:
            fail("constraint_scope", pointer, str(error))
            return None

    for row_index, realization in enumerate(realizations):
        for index, constraint in enumerate(realization.constraints):
            pointer = json_pointer("realizations", row_index, "constraints", index)
            scope = constraint.scope
            if isinstance(scope, ElementScope):
                scoped_definitions(scope.instruction_id, scope.scope_path, pointer + "/scope")

            def check_target(reference, at, *, event=False):
                target = targets.get(target_key(reference))
                if target is None:
                    fail("constraint_reference", at, "Constraint reference does not resolve to the frozen CFG or original annotation.")
                    return None
                if event and target["kind"] not in {"instruction", "operation"}:
                    fail("constraint_event", at, "Constraint event must reference a real instruction or atomic operation.")
                if isinstance(scope, ElementScope) and (
                    target.get("instruction_id") != scope.instruction_id
                    or target.get("scope_path") != scope.scope_path
                ):
                    fail("constraint_scope", at, "Constraint event or expression escapes its declared element scope.")
                return target

            for name in ("events", "before", "after", "triggers"):
                for event_index, reference in enumerate(getattr(constraint, name, None) or []):
                    check_target(reference, pointer + f"/{name}/{event_index}", event=True)
            for name in ("condition", "success"):
                reference = getattr(constraint, name, None)
                if reference is None:
                    continue
                check_target(reference, pointer + "/" + name)
                expression = expression_index.get(target_key(reference))
                if expression is None:
                    fail("constraint_expression", pointer + "/" + name,
                         "Constraint condition must reference one existing normalized expression.")
                elif any(type(value) is not bool for value in _known_literals(expression)):
                    fail("constraint_expression", pointer + "/" + name,
                         "Constraint condition must be Boolean, without implicit truth conversion.")
            if isinstance(constraint, ForbidInformation):
                source = constraint.source
                definitions = scoped_definitions(source.instruction_id, source.scope_path, pointer + "/source")
                if isinstance(scope, ElementScope) and source.scope_path and (
                    source.instruction_id != scope.instruction_id or source.scope_path != scope.scope_path
                ):
                    fail("constraint_scope", pointer + "/source", "Constraint source belongs to a different element scope.")
                def check_value(ref):
                    if isinstance(ref, InputRef):
                        inputs = instructions[source.instruction_id]["inputs"]
                        if ref.index >= len(inputs):
                            fail("constraint_value", pointer + "/source/value", "Constraint references an absent input operand.")
                        elif inputs[ref.index]["type"] == "external_resource":
                            fail("constraint_value", pointer + "/source/value", "Resource identity is not acquired information; reference its actual content value.")
                    elif isinstance(ref, LocalRef) and ref.name not in definitions:
                        fail("constraint_value", pointer + "/source/value", "Constraint local is absent or escapes its lexical scope.")
                    elif isinstance(ref, AlternativesRef):
                        for child in ref.items:
                            check_value(child)
                if definitions is not None:
                    check_value(source.value)
                if isinstance(constraint.receivers, LocationReceivers) and not set(constraint.receivers.ids) <= set(locations):
                    fail("constraint_receiver", pointer + "/receivers", "Constraint receiver references an absent declared location.")
            expressed.add(realization.requirement_id)
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    return expressed


def constraint_mapping(raw, task_ref):
    """Give raw declarations stable program-owned identities without copying them."""
    result = []
    for row_index, realization in enumerate(raw["realizations"]):
        for index, _ in enumerate(realization.get("constraints", [])):
            pointer = json_pointer("realizations", row_index, "constraints", index)
            result.append({"constraint_id": "constraint_" + canonical_sha256([task_ref["task_sha256"], pointer])[:20],
                           "requirement_id": realization["requirement_id"], "raw_pointer": pointer})
    return result
