"""Strict saved backward-demand records, without necessity or DOE verdicts."""
from __future__ import annotations

from copy import deepcopy
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator

from skillflow.propagation.contracts.references import target_key
from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import Text, _require_json
from skillflow.propagation.contracts.boundaries import SinkBoundary
from skillflow.propagation.contracts.demand import DemandGoal, DemandPath, DemandProperty
from skillflow.propagation.contracts.specs import ValueRef
from skillflow.propagation.contracts.task import TaskReference, TaskBinding
from skillflow.propagation.contracts.realizations import RealizationGap
from skillflow.propagation.data.models import _check_json_value
from .models import Position


Index = Annotated[int, Field(strict=True, ge=0)]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class _Node(Strict):
    instruction_id: Text
    operation_id: Text | None
    slot: Index | None
    data_ids: list[Text]

    @field_validator("data_ids")
    @classmethod
    def unique_data(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Demand node candidate IDs must not repeat")
        return value


class OperationNode(_Node):
    kind: Literal["op_input", "op_output"]
    operation_id: Text
    slot: Index


class OperandNode(_Node):
    kind: Literal["ir_input", "ir_output"]
    operation_id: None
    slot: Index


class ActionNode(_Node):
    kind: Literal["action"]
    slot: None

    @model_validator(mode="after")
    def not_a_payload(self):
        if self.data_ids:
            raise ValueError("Action demand cannot claim a payload")
        return self


class ElementNode(_Node):
    kind: Literal["element"]
    operation_id: None
    slot: None
    scope: Annotated[list[Index], Field(min_length=2, max_length=2)]
    collection: Text
    reference: ValueRef

    @model_validator(mode="after")
    def single_element(self):
        if len(self.data_ids) != 1:
            raise ValueError("Element demand must retain one symbolic scope instance")
        return self


class LiteralNode(_Node):
    kind: Literal["literal"]
    operation_id: None
    slot: None
    value: JsonValue

    @field_validator("value", mode="before")
    @classmethod
    def exact_json(cls, value):
        _check_json_value(value)
        return value

    @model_validator(mode="after")
    def symbolic_literal(self):
        if self.data_ids:
            raise ValueError("Literal reference does not allocate or claim Data IDs")
        return self


DemandNode = Annotated[OperationNode | OperandNode | ActionNode | ElementNode | LiteralNode,
                       Field(discriminator="kind")]


class Derivation(Strict):
    node: DemandNode
    property: DemandProperty
    path: DemandPath
    each: bool
    excluded_paths: list[DemandPath]
    requirement_id: Text
    seed_goal_id: Text
    conservative: bool
    rules: Annotated[list[Text], Field(min_length=1)]
    parents: list[Text]

    @field_validator("rules", "parents")
    @classmethod
    def unique_refs(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Demand rule and parent references must not repeat")
        return value


class ActualPayload(Strict):
    operation_id: Text
    position: Position
    inputs: list[Annotated[list[Text], Field(min_length=1)]]

    @field_validator("inputs")
    @classmethod
    def candidate_sets(cls, values):
        if any(len(slot) != len(set(slot)) for slot in values):
            raise ValueError("Payload candidate set must not repeat IDs; repeated slots remain distinct")
        return values


class UnestablishedRange(Strict):
    operation_id: Text
    input_index: Index
    data_ids: list[Text]
    description: Text
    scope: Literal["whole_slot", "outside_listed_properties"]


class SinkComparison(Strict):
    id: Text
    boundary: SinkBoundary
    actual_payload: Annotated[list[ActualPayload], Field(min_length=1)]
    related_requirements: list[Text]
    demanded_information: list[Text]
    conservative_retention: list[Text]
    unestablished_ranges: list[UnestablishedRange]
    limitations: list[Text]

    @field_validator("related_requirements", "demanded_information", "conservative_retention", "limitations")
    @classmethod
    def unique_refs(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Sink demand references must not repeat")
        return value

    @model_validator(mode="after")
    def coordinates(self):
        operation_ids = [item.operation_id for item in self.actual_payload]
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("Sink payload must retain one row for each actual operation instance")
        for payload in self.actual_payload:
            position = payload.position
            if any(getattr(position, field) != getattr(self.boundary, field)
                   for field in ("instruction_id", "event_index", "op_index", "body_event_index")):
                raise ValueError("Sink payload position differs from its boundary")
            if (position.instance_index is None) != (self.boundary.scope is None):
                raise ValueError("Sink instance position differs from its element scope")
        return self


class Diagnostic(Strict):
    id: Text
    code: Text
    reason: Text
    instruction_id: Text | None
    requirement_id: Text | None
    operation_id: Text | None
    blocking: bool


class RequirementCoverage(Strict):
    requirement_id: Text
    status: Literal["expressed", "partial", "retained_only", "unmapped"]
    bindings: list[TaskBinding]
    gaps: list[RealizationGap]
    goal_ids: list[Text]
    constraint_ids: list[Text]
    has_applicable_goal: bool


class SeedTrace(Strict):
    goal_id: Text
    raw_pointer: Text | None
    derivation_ids: list[Text]


class RequirementTrace(Strict):
    requirement_id: Text
    source_accounting_indices: list[Index]
    seeds: list[SeedTrace]


class Traceability(Strict):
    task_ref: TaskReference
    requirements: list[RequirementTrace]


class Coverage(Strict):
    requirements: dict[Text, RequirementCoverage]
    sinks: Index
    expected_sinks: Index
    upstream: dict[Text, Literal["processed", "not_reached", "not_solved", "unresolved_binding"]]


class DemandResult(Strict):
    schema_version: Literal["skillflow-demand-v4"]
    status: Literal["complete", "partial"]
    goals: list[DemandGoal]
    traceability: Traceability
    derivations: dict[Text, Derivation]
    sinks: list[SinkComparison]
    diagnostics: list[Diagnostic]
    coverage: Coverage

    @model_validator(mode="after")
    def references(self):
        def unique(values, label):
            if len(values) != len(set(values)):
                raise ValueError("Duplicate " + label)
        requirements = set(self.coverage.requirements)
        unique([goal.id for goal in self.goals], "demand goal")
        if any(goal.requirement_id not in requirements for goal in self.goals):
            raise ValueError("Goal refers to an uncovered requirement")
        goals = {goal.id: goal for goal in self.goals}
        if set(self.coverage.requirements) != {r.requirement_id for r in self.traceability.requirements}:
            raise ValueError("Traceability requirement coverage differs")
        if len(self.traceability.requirements) != len(requirements):
            raise ValueError("Duplicate traceability requirement")
        traced_seeds = set()
        for trace in self.traceability.requirements:
            coverage = self.coverage.requirements[trace.requirement_id]
            expected = {key for key, goal in goals.items() if goal.requirement_id == trace.requirement_id}
            if coverage.requirement_id != trace.requirement_id or set(coverage.goal_ids) != expected or len(coverage.goal_ids) != len(expected):
                raise ValueError("Requirement realization goal projection differs")
            if {seed.goal_id for seed in trace.seeds} != expected or len(trace.seeds) != len(expected):
                raise ValueError("Traceability seed coverage differs")
            for seed in trace.seeds:
                traced_seeds.add(seed.goal_id)
                expected_derivations = {key for key, row in self.derivations.items() if row.seed_goal_id == seed.goal_id}
                if set(seed.derivation_ids) != expected_derivations or len(seed.derivation_ids) != len(expected_derivations):
                    raise ValueError("Traceability derivation projection differs")
        diagnostics = {item.id: item for item in self.diagnostics}
        unique([item.id for item in self.diagnostics], "demand diagnostic")
        if any(item.requirement_id is not None and item.requirement_id not in requirements for item in self.diagnostics):
            raise ValueError("Diagnostic refers to an uncovered requirement")
        for key, item in self.derivations.items():
            if item.requirement_id not in requirements:
                raise ValueError("Demand derivation requirement differs")
            if item.seed_goal_id not in goals or goals[item.seed_goal_id].requirement_id != item.requirement_id:
                raise ValueError("Demand derivation seed differs from its requirement")
            if any(self.derivations[p].seed_goal_id != item.seed_goal_id for p in item.parents if p in self.derivations):
                raise ValueError("Demand derivation crosses seed provenance")
            # The business ID is checked by deterministic replay. Parent/seed
            # links are validated here independently of inference truth.
            if not set(item.parents) <= self.derivations.keys() or key in item.parents:
                raise ValueError("Invalid demand parent reference")
            if item.node.instruction_id not in self.coverage.upstream:
                raise ValueError("Demand node references an unknown IR")
        unique([item.id for item in self.sinks], "sink comparison")
        unique([canonical_sha256(item.boundary.model_dump(mode="json")) for item in self.sinks], "sink boundary")
        if self.coverage.sinks != len(self.sinks) or self.coverage.expected_sinks != len(self.sinks):
            raise ValueError("Sink comparison coverage differs")
        for sink in self.sinks:
            all_refs = sink.demanded_information + sink.conservative_retention
            if len(all_refs) != len(set(all_refs)) or not set(all_refs) <= self.derivations.keys():
                raise ValueError("Dangling or multiply classified sink demand")
            if not set(sink.limitations) <= diagnostics.keys():
                raise ValueError("Dangling sink limitation")
            operations = {item.operation_id for item in sink.actual_payload}
            for ref in all_refs:
                item = self.derivations[ref]
                if (item.node.operation_id not in operations or item.node.kind not in {"op_input", "action"}
                        or item.conservative != (ref in sink.conservative_retention)):
                    raise ValueError("Sink demand belongs to another use or retention class")
            if set(sink.related_requirements) != {self.derivations[ref].requirement_id for ref in all_refs}:
                raise ValueError("Sink task requirement projection differs")
            if any(item.operation_id not in operations for item in sink.unestablished_ranges):
                raise ValueError("Unestablished range refers to another operation")
        partial = any(item.blocking for item in self.diagnostics)
        if (self.status == "partial") != partial:
            raise ValueError("Demand completion status differs from blocking diagnostics")
        return self


def validate_result_shape(value):
    """Strict fields and internal references only; replay checks derivation truth."""
    _require_json(value, "")
    checked = DemandResult.model_validate(value).model_dump(mode="json")
    if checked != value:
        raise ValueError("Demand result must preserve its explicit wire fields")
    return deepcopy(checked)


def validate_result_references(value, facts, targets):
    """Bind saved references to facts without re-solving preservation semantics."""
    from .material import _Index
    from skillflow.propagation.conditions import payload_inputs
    checked = validate_result_shape(value)
    index = _Index(facts)
    annotation = facts.annotation
    task = annotation["task"]
    if checked["traceability"]["task_ref"] != annotation["compiled_annotation"]["task_ref"]:
        raise ValueError("Demand traceability Task revision differs")
    expected_requirements = {r["id"] for r in task["requirements"]}
    if set(checked["coverage"]["requirements"]) != expected_requirements:
        raise ValueError("Demand realization requirement coverage differs")
    realizations = {r["requirement_id"]: r for r in annotation["compiled_annotation"]["realizations"]}
    mappings = {row["goal_id"]: row for row in annotation["mapping"]["goals"]}
    canonical_goals = {row["id"]: row for row in annotation["compiled_annotation"]["demands"]}
    goals = {row["id"]: row for row in checked["goals"]}
    for trace in checked["traceability"]["requirements"]:
        req = trace["requirement_id"]
        expected_indices = [i for i, row in enumerate(task["source_accounting"]) if req in row["requirement_ids"]]
        if trace["source_accounting_indices"] != expected_indices:
            raise ValueError("Demand source accounting projection differs")
        coverage = checked["coverage"]["requirements"][req]
        original = {k: v for k, v in realizations[req].items() if k != "constraints"}
        if {k: coverage[k] for k in original} != original:
            raise ValueError("Demand realization differs from immutable annotation")
        expected_constraints = [r["constraint_id"] for r in annotation["mapping"]["constraints"]
                                if r["requirement_id"] == req]
        if coverage["constraint_ids"] != expected_constraints:
            raise ValueError("Demand constraint references differ from annotation")
        for seed in trace["seeds"]:
            identity = seed["goal_id"]
            expected_pointer = mappings[identity]["raw_pointer"] if canonical_goals.get(identity) == goals[identity] else None
            if seed["raw_pointer"] != expected_pointer:
                raise ValueError("Demand raw declaration coordinate differs")
    data_ids = {item["id"] for item in facts.data}
    actual_boundaries = {canonical_sha256(item) for item in facts.sinks}
    if {canonical_sha256(item["boundary"]) for item in checked["sinks"]} != actual_boundaries:
        raise ValueError("Demand sink coverage differs from upstream facts")
    if checked["coverage"]["upstream"] != facts.coverage:
        raise ValueError("Demand upstream coverage differs from facts")
    if any(target_key(goal["target"]) not in targets for goal in checked["goals"]):
        raise ValueError("Demand goal target is absent")
    for derivation in checked["derivations"].values():
        node = derivation["node"]
        if not set(node["data_ids"]) <= data_ids:
            raise ValueError("Demand node references absent Data")
        operation_id = node["operation_id"]
        if operation_id is not None:
            if operation_id not in index.operations:
                raise ValueError("Demand node references an absent operation")
            operation = index.operations[operation_id]
            if operation["position"]["instruction_id"] != node["instruction_id"]:
                raise ValueError("Demand operation and IR binding differ")
            if node["kind"] in {"op_input", "op_output"}:
                values = operation["record"]["inputs" if node["kind"] == "op_input" else "outputs"]
                if node["slot"] >= len(values) or sorted(node["data_ids"]) != sorted(values[node["slot"]]):
                    raise ValueError("Demand node differs from the actual operand candidates")
        elif node["kind"] in {"ir_input", "ir_output"}:
            instruction = index.instructions[node["instruction_id"]]
            if node["slot"] >= len(instruction["inputs" if node["kind"] == "ir_input" else "outputs"]):
                raise ValueError("Demand IR operand does not exist")
        elif node["kind"] == "element":
            matches = [scope for scope in index.scopes.values()
                       if scope["instruction_id"] == node["instruction_id"]
                       and [scope["event_index"], scope["instance_index"]] == node["scope"]]
            if len(matches) != 1 or matches[0]["collection"] != node["collection"] or node["data_ids"] != [matches[0]["element"]]:
                raise ValueError("Demand element identity differs from its scope")
    for sink in checked["sinks"]:
        operations = index.sink_operations(sink["boundary"])
        payload = [{"operation_id": key, "position": index.operations[key]["position"],
                    "inputs": payload_inputs(index.operations[key]["record"])} for key in operations]
        if sink["actual_payload"] != payload:
            raise ValueError("Demand sink actual payload differs from recorded facts")
        for item in sink["unestablished_ranges"]:
            record = index.operations[item["operation_id"]]["record"]
            slot = item["input_index"]
            if (slot >= len(record["inputs"]) or slot == record.get("when_input_index")
                    or item["data_ids"] != record["inputs"][slot]):
                raise ValueError("Demand unestablished range differs from its actual payload slot")
    return checked
