"""Strict saved backward-demand records, without necessity or DOE verdicts."""
from __future__ import annotations

from skillflow.propagation.coverage import RECORDED_COVERAGE
from copy import deepcopy
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator, model_serializer

from skillflow.propagation.contracts.references import target_key
from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import Text, _require_json
from skillflow.propagation.contracts.boundaries import SinkBoundary
from skillflow.propagation.contracts.demand import DemandGoal, DemandPath, DemandProperty, GoalPath, EachDemandStep, _check_goal_path
from skillflow.propagation.contracts.specs import ValueRef
from skillflow.propagation.contracts.task import TaskReference, TaskBinding
from skillflow.propagation.contracts.realizations import RealizationGap
from skillflow.propagation.data.models import _check_json_value
from skillflow.propagation.models import OperationAlternative
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


class CollectionOutputNode(_Node):
    kind: Literal["collection_output"]
    operation_id: None
    slot: None
    event_index: Index
    reference: ValueRef
    yield_reference: ValueRef


DemandNode = Annotated[OperationNode | OperandNode | ActionNode | ElementNode | LiteralNode | CollectionOutputNode,
                       Field(discriminator="kind")]


class Derivation(Strict):
    node: DemandNode
    property: DemandProperty
    path: GoalPath
    each: bool
    excluded_paths: list[GoalPath]
    requirement_id: Text
    seed_goal_id: Text
    conservative: bool
    information_bound: bool = False
    selector_ref: Text | None = None
    rules: Annotated[list[Text], Field(min_length=1)]
    parents: list[Text]

    @model_serializer(mode="wrap")
    def omit_unbounded_default(self, handler):
        value = handler(self)
        if not self.information_bound:
            value.pop("information_bound", None)
        if self.selector_ref is None:
            value.pop("selector_ref", None)
        return value

    @model_validator(mode="after")
    def member_paths(self):
        if self.selector_ref and self.property not in {"truth", "presence"}:
            raise ValueError("A selector decision preserves truth or field presence")
        if self.information_bound and not self.conservative:
            raise ValueError("A bounded uncertain information scope must remain conservative")
        _check_goal_path(self.path)
        for path in self.excluded_paths:
            _check_goal_path(path)
        return self

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
    alternatives: list[OperationAlternative] = Field(default_factory=list)

    @model_serializer(mode="wrap")
    def omit_unpaired_legacy(self, handler):
        value = handler(self)
        if not self.alternatives:
            value.pop("alternatives", None)
        return value

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
    affected_instruction_ids: list[Text] | None = None

    @model_serializer(mode="wrap")
    def omit_legacy_scope(self, handler):
        result = handler(self)
        if self.affected_instruction_ids is None:
            result.pop("affected_instruction_ids", None)
        return result


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
    seeds: list[SeedTrace]


class Traceability(Strict):
    task_ref: TaskReference
    requirements: list[RequirementTrace]


class Coverage(Strict):
    requirements: dict[Text, RequirementCoverage]
    sinks: Index
    expected_sinks: Index
    upstream: dict[Text, Literal["processed", "processed_with_placeholder", "not_reached", "infeasible", "not_solved", "unresolved_binding", "unmodeled", "blocked", "execution_error"]]
    unresolved_boundaries: list[SinkBoundary] = Field(default_factory=list)

    @model_serializer(mode="wrap")
    def omit_empty_boundary_gaps(self, handler):
        result = handler(self)
        if not self.unresolved_boundaries:
            result.pop("unresolved_boundaries", None)
        return result


from .input_assessments import InputAssessment, InputSemanticFinding


class DemandResult(Strict):
    schema_version: Literal["skillflow-demand-v14"]
    status: Literal["complete", "partial"]
    goals: list[DemandGoal]
    traceability: Traceability
    derivations: dict[Text, Derivation]
    sinks: list[SinkComparison]
    diagnostics: list[Diagnostic]
    coverage: Coverage
    input_assessments: list[InputAssessment]
    input_findings: list[InputSemanticFinding]
    input_contract_review_sha256: Text | None

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
        if any(row.information_bound for row in self.derivations.values()):
            _validate_information_bounds({key: row.model_dump(mode="json") for key, row in self.derivations.items()},
                {key: row.model_dump(mode="json") for key, row in diagnostics.items()}, self.input_contract_review_sha256)
        unique([item.id for item in self.input_assessments], "input assessment")
        assessments = {item.id: item for item in self.input_assessments}
        from collections import defaultdict
        derived_by_use, serialized_derivations = defaultdict(list), {}
        for key, derivation in self.derivations.items():
            node = derivation.node
            derived_by_use[(node.kind, node.instruction_id, node.operation_id, node.slot)].append(key)
        for item in self.input_assessments:
            if item.instruction_id not in self.coverage.upstream or item.coverage != self.coverage.upstream[item.instruction_id]:
                raise ValueError("Input assessment coverage differs from its instruction")
            if item.coverage == "infeasible" and item.ranges:
                raise ValueError("An inactive input cannot claim a deletion or need")
            for row in item.ranges:
                if row.contract_refs and self.input_contract_review_sha256 is None:
                    raise ValueError("Reviewed input contracts require a bound review receipt identity")
                if not set(row.demand_refs) <= self.derivations.keys() or not set(row.diagnostic_refs) <= diagnostics.keys():
                    raise ValueError("Input assessment has dangling evidence references")
                if row.status == "deletable" and (row.diagnostic_refs or item.coverage not in RECORDED_COVERAGE):
                    raise ValueError("An incomplete input assessment cannot authorize deletion")
                if row.status != "deletable" and (row.modification is not None or row.modification_limit is not None):
                    raise ValueError("Only an established deletion may have a modification recipe or edit limitation")
                if row.status == "deletable" and (row.modification is None) == (row.modification_limit is None):
                    raise ValueError("A deletion requires either a concrete semantic recipe or an explicit edit limitation")
                node_kind = "op_output" if item.node_kind == "acquisition_output" else item.node_kind
                for ref in row.demand_refs:
                    node = self.derivations[ref].node
                    if (node.kind, node.instruction_id, node.operation_id, node.slot) != (
                            node_kind, item.instruction_id, item.operation_id, item.input_index):
                        raise ValueError("Input assessment demand belongs to another actual use")
                if row.status == "deletable":
                    from .sensitivity_engine import demand_overlap
                    signal = {"property": row.property, "path": row.model_dump(mode="json")["path"],
                              "excluded_paths": row.model_dump(mode="json")["excluded_paths"]}
                    for key in derived_by_use[(node_kind, item.instruction_id, item.operation_id, item.input_index)]:
                        if key not in serialized_derivations:
                            serialized_derivations[key] = self.derivations[key].model_dump(mode="json")
                        if demand_overlap(signal, serialized_derivations[key]) != "none":
                            raise ValueError("Input deletion overlaps retained information at this actual use")
        unique([item.id for item in self.input_findings], "input semantic finding")
        for item in self.input_findings:
            if (not set(item.assessment_refs) <= assessments.keys() or not set(item.diagnostic_refs) <= diagnostics.keys()
                    or item.instruction_id not in self.coverage.upstream):
                raise ValueError("Input semantic finding has dangling evidence references")
            if item.origin == "source_review":
                if (self.input_contract_review_sha256 is None or item.source_finding is None
                        or item.source_review_refs != [item.id] or item.source_finding.id != item.id):
                    raise ValueError("Source-input findings require a bound immutable source-review identity")
                actual = item.source_finding.actual
                if item.input_index != getattr(actual, "input_index", None) or item.path != getattr(actual, "path", []):
                    raise ValueError("Source-input finding changes or invents the actual operand")
            elif item.source_review_refs or item.source_finding is not None:
                raise ValueError("Demand-derived findings cannot claim an authored source-review defect")
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


def _validate_information_bounds(derivations, diagnostics, receipt_sha256):
    """Check finite scope ancestry, without re-proving semantic inference."""
    from .demand_engine import EXACT_INFORMATION_BOUND_RULES
    bounded = {key: row for key, row in derivations.items() if row.get("information_bound")}
    if bounded and receipt_sha256 is None:
        raise ValueError("A bounded uncertain information scope requires its review receipt")
    origins = set()
    for key, row in bounded.items():
        if not row["conservative"]:
            raise ValueError("A bounded uncertain information scope must remain conservative")
        for rule in row["rules"]:
            if rule in EXACT_INFORMATION_BOUND_RULES:
                continue
            if rule.startswith("input_contract_gap:"):
                diagnostic = diagnostics.get(rule.split(":", 1)[1], {})
                node = row["node"]
                if (diagnostic.get("code") == "input_contract_semantic_gap" and node["kind"] == "op_input"
                        and diagnostic.get("operation_id") == node["operation_id"]
                        and diagnostic.get("instruction_id") == node["instruction_id"]
                        and diagnostic.get("requirement_id") == row["requirement_id"]
                        and diagnostic.get("affected_instruction_ids") == [node["instruction_id"]]):
                    origins.add(key)
                    continue
            raise ValueError("Bounded information cannot pass through generic or unmodeled processing")
        if key not in origins and not any(parent in bounded for parent in row["parents"]):
            raise ValueError("A bounded information transfer requires a bounded exact-transfer parent")
    # Cycles cannot certify one another without reaching an actual scoped gap.
    from collections import defaultdict, deque
    children = defaultdict(set)
    for key, row in bounded.items():
        for parent in row["parents"]:
            children[parent].add(key)
    reached, pending = set(origins), deque(origins)
    while pending:
        for child in children[pending.popleft()]:
            if child not in reached:
                reached.add(child)
                pending.append(child)
    if reached != bounded.keys():
        raise ValueError("A bounded information scope lacks ancestry to a reviewed scoped gap")


def reject_archived_selectors(derivations):
    if isinstance(derivations, dict) and any(isinstance(row, dict) and "selector_ref" in row
                                             for row in derivations.values()):
        raise ValueError("Archived demand v12 derivations cannot carry selector_ref")


class ArchivedDemand13(DemandResult):
    schema_version: Literal["skillflow-demand-v13"]

    @model_validator(mode="after")
    def historical_coverage(self):
        if "processed_with_placeholder" in self.coverage.upstream.values():
            raise ValueError("Historical demand coverage cannot contain symbolic operations")
        return self


class ArchivedDemandResult(ArchivedDemand13):
    schema_version: Literal["skillflow-demand-v12"]

    @model_validator(mode="before")
    @classmethod
    def historical_derivations(cls, value):
        if isinstance(value, dict):
            reject_archived_selectors(value.get("derivations"))
        return value


def validate_result_shape(value, *, archived_v12=False, archived_v13=False):
    """Strict fields and internal references only; replay checks derivation truth."""
    _require_json(value, "")
    schema = ArchivedDemandResult if archived_v12 else ArchivedDemand13 if archived_v13 else DemandResult
    checked = schema.model_validate(value).model_dump(mode="json")
    if checked != value:
        raise ValueError("Demand result must preserve its explicit wire fields")
    return deepcopy(checked)


def validate_result_references(value, facts, targets, *, input_contract_review=None, engine=None, archived_v12=False, archived_v13=False):
    """Bind saved references to facts without re-solving preservation semantics."""
    from types import SimpleNamespace
    from .material import _Index, _id, payload_alternatives
    from skillflow.propagation.conditions import payload_inputs
    checked = validate_result_shape(value, archived_v12=archived_v12, archived_v13=archived_v13)
    index = _Index(facts)
    annotation = facts.annotation
    task = annotation["task"]
    if checked["input_contract_review_sha256"] != (input_contract_review or {}).get("receipt_sha256"):
        raise ValueError("Demand input-contract review identity differs from the validated review receipt")
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
    data_ids = set(index.data)
    actual_boundaries = {canonical_sha256(item) for item in index.sinks}
    if {canonical_sha256(item["boundary"]) for item in checked["sinks"]} != actual_boundaries:
        raise ValueError("Demand sink coverage differs from upstream facts")
    if checked["coverage"]["upstream"] != index.coverage:
        raise ValueError("Demand upstream coverage differs from facts")
    from skillflow.propagation.facts import declared_boundary_coverage
    unresolved = [row["boundary"] for row in declared_boundary_coverage(annotation["compiled_annotation"], index.sinks, index.coverage)
                  if row["status"] == "unresolved"]
    if checked["coverage"].get("unresolved_boundaries", []) != unresolved:
        raise ValueError("Demand unresolved boundary coverage differs from declared but unevaluated operations")
    from skillflow.propagation.contracts.limitations import processing_impacts, gap_id, diagnostic_applies
    expected_gaps = processing_impacts(index.cfg, annotation["compiled_annotation"])
    gaps = {gap_id(g): g for g in annotation["compiled_annotation"].get("processing_gaps", [])
            if index.coverage[g["instruction_id"]] != "infeasible"}
    actual_gaps = {}
    for diagnostic in checked["diagnostics"]:
        affected = diagnostic.get("affected_instruction_ids")
        if affected is not None:
            if diagnostic["code"] == "upstream_diagnostic":
                if not any(row.get("affected_instruction_ids") == affected
                           and row.get("instruction_id") == diagnostic["instruction_id"]
                           and row.get("reason") == diagnostic["reason"] for row in index.diagnostics):
                    raise ValueError("Upstream diagnostic scope differs from its recorded execution evidence")
                continue
            if diagnostic["code"].startswith("input_contract_"):
                if (diagnostic["code"] == "input_contract_review_validation"
                        and diagnostic["operation_id"] is None
                        and diagnostic["instruction_id"] in index.instructions
                        and affected == [diagnostic["instruction_id"]]):
                    # An actual CFG operand may alias a quarantined consumer.
                    # The exact barrier/operand proof is rechecked below.
                    continue
                if (affected != [diagnostic["instruction_id"]] or diagnostic["operation_id"] not in index.operations
                        or index.operations[diagnostic["operation_id"]]["position"]["instruction_id"] != diagnostic["instruction_id"]):
                    raise ValueError("Input-contract diagnostic has an unsupported local footprint")
                if (diagnostic["code"] == "input_contract_placeholder"
                        and index.operations[diagnostic["operation_id"]]["record"]["op"] != "placeholder"):
                    raise ValueError("Symbolic demand diagnostic must identify its placeholder operation")
                continue
            if diagnostic["code"] != "processing_gap" or not set(affected) <= set(index.instructions):
                raise ValueError("Demand diagnostic has an unsupported scoped footprint")
            identity = diagnostic["reason"].split(": ", 1)[0]
            if (identity not in gaps or diagnostic["instruction_id"] != gaps[identity]["instruction_id"]
                    or affected != expected_gaps[identity] or not diagnostic["blocking"]
                    or diagnostic["reason"] != identity + ": " + gaps[identity]["reason"]):
                raise ValueError("Processing limitation differs from its program-computed dependency closure")
            actual_gaps[identity] = diagnostic
        elif diagnostic["code"] == "processing_gap":
            raise ValueError("Processing limitation lacks its dependency footprint")
    if set(actual_gaps) != set(gaps):
        raise ValueError("Demand result drops declared processing limitations")
    if any(target_key(goal["target"]) not in targets for goal in checked["goals"]):
        raise ValueError("Demand goal target is absent")
    expected_inputs = {("ir_input", ir, None, slot) for ir, instruction in index.instructions.items()
                       for slot in range(len(instruction["inputs"]))}
    for key, operation in index.operations.items():
        ir, record = operation["position"]["instruction_id"], operation["record"]
        expected_inputs.update(("op_input", ir, key, slot) for slot in range(len(record["inputs"])))
        if record["op"] in {"read", "receive"}:
            expected_inputs.update(("acquisition_output", ir, key, slot) for slot in range(len(record["outputs"])))
    actual_inputs = {(a["node_kind"], a["instruction_id"], a["operation_id"], a["input_index"])
                     for a in checked["input_assessments"]}
    if actual_inputs != expected_inputs or len(actual_inputs) != len(checked["input_assessments"]):
        raise ValueError("Input assessments must cover the exact complete input inventory")
    contract_ids = {entry["id"] for entry in annotation["compiled_annotation"].get("input_contracts", [])}
    for item in checked["input_assessments"]:
        if not set(item["data_ids"]) <= data_ids:
            raise ValueError("Input assessment references absent Data")
        if item["operation_id"] is not None:
            record = index.operations[item["operation_id"]]["record"]
            side = "outputs" if item["node_kind"] == "acquisition_output" else "inputs"
            if item["data_ids"] != sorted(set(record[side][item["input_index"]])):
                raise ValueError("Input assessment changes actual operand candidates")
        if any(not set(row["contract_refs"]) <= contract_ids for row in item["ranges"]):
            raise ValueError("Input assessment references an absent semantic contract")
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
        elif node["kind"] == "collection_output":
            ir, event_index = node["instruction_id"], node["event_index"]
            events = index.records.get(ir, {}).get("events", [])
            if event_index >= len(events) or events[event_index].get("kind") != "for_each":
                raise ValueError("Demand collection output has no recorded member scope")
            declared = annotation["compiled_annotation"]["ir_semantics"][ir]["events"][event_index]
            if (sorted(node["data_ids"]) != sorted(events[event_index].get("outputs", []))
                    or node["reference"] != declared["collection"] or node["yield_reference"] != declared.get("yield")):
                raise ValueError("Demand collection output differs from its recorded yields")
    for sink in checked["sinks"]:
        sliced = index.slice(sink["boundary"])
        relevant = set(sliced["usage_context"]["instructions"])
        relevant.update(index.operations[key]["position"]["instruction_id"] for key in sliced["backward_slice"]["operations"])
        from .input_assessments import applicable_contract_diagnostics
        contract_limits = applicable_contract_diagnostics(checked["derivations"],
            sink["demanded_information"] + sink["conservative_retention"])
        expected_limits = sorted(d["id"] for d in checked["diagnostics"] if d["blocking"] and (
            d["id"] in contract_limits if d["code"].startswith("input_contract_") else diagnostic_applies(d, relevant,
                                scoped_instructions=sliced["usage_context"]["instructions"])))
        if sink["limitations"] != expected_limits:
            raise ValueError("Demand sink changes relevant analysis limitations")
        operations = index.sink_operations(sink["boundary"])
        payload = [{"operation_id": key, "position": index.operations[key]["position"],
                    "inputs": payload_inputs(index.operations[key]["record"]),
                    **({"alternatives": payload_alternatives(index.operations[key]["record"])}
                       if index.operations[key]["record"].get("alternatives") else {})} for key in operations]
        if sink["actual_payload"] != payload:
            raise ValueError("Demand sink actual payload differs from recorded facts")
        for item in sink["unestablished_ranges"]:
            record = index.operations[item["operation_id"]]["record"]
            slot = item["input_index"]
            if (slot >= len(record["inputs"]) or slot == record.get("when_input_index")
                    or item["data_ids"] != record["inputs"][slot]):
                raise ValueError("Demand unestablished range differs from its actual payload slot")
    # Reconstruct only the actual coordinate index when not already supplied by
    # preparation. Never solve demands again or turn a saved result into a seed.
    if engine is None:
        from .demand_engine import DemandEngine
        from skillflow.propagation.contracts.task import Task
        engine = DemandEngine(facts, Task.model_validate(task), annotation,
            {"goals": checked["goals"], "expressions": []}, targets, input_contract_review=input_contract_review)
    elif (engine.facts is not facts
            or (engine.contracts.receipt or {}).get("receipt_sha256") != checked["input_contract_review_sha256"]):
        raise ValueError("Reused demand index belongs to different facts or source-review material")
    from .selector_demands import validate_bindings
    validate_bindings(checked["derivations"], engine)
    from .input_assessments import InputReviewBarrierIndex
    from .review_barriers import barrier_reason, barrier_diagnostic_value, operation_barriers
    barriers = InputReviewBarrierIndex(engine)
    diagnostics = {row["id"]: row for row in checked["diagnostics"]}
    unavailable = {}
    for goal in checked["goals"]:
        target = targets[target_key(goal["target"])]
        evidence = engine.unavailable_dependencies.evidence(goal, target)
        if evidence is not None:
            identity = _id("diagnostic_", evidence)
            unavailable[goal["id"]] = identity
            if diagnostics.get(identity) != {"id": identity, **evidence}:
                raise ValueError("Demand result omits or changes a required action's unavailable occurrence")
    if set(unavailable.values()) != {key for key, row in diagnostics.items()
                                     if row["code"] == "unavailable_required_action"}:
        raise ValueError("Demand result invents an unavailable required action")
    linked = set()
    for row in checked["derivations"].values():
        seed = row["seed_goal_id"]
        expected = unavailable.get(seed)
        for rule in row["rules"]:
            if not rule.startswith("unavailable_dependency:"):
                continue
            node = row["node"]
            if (expected is None or rule != "unavailable_dependency:" + expected
                    or node["kind"] != "action" or node["operation_id"] is not None or not row["conservative"]
                    or node["instruction_id"] != diagnostics[expected]["instruction_id"] or row["parents"]):
                raise ValueError("Required action uncertainty must begin at its actual declared target, without a fabricated occurrence")
            linked.add(seed)
    if linked != set(unavailable):
        raise ValueError("Demand result omits an unavailable required action's protection root")
    if unavailable:
        from .input_assessments import derivation_problem_refs
        ancestry = derivation_problem_refs(SimpleNamespace(derivations=checked["derivations"]))
        by_use = {(item["node_kind"] if item["node_kind"] != "acquisition_output" else "op_output",
                   item["instruction_id"], item["operation_id"], item["input_index"]): item
                  for item in checked["input_assessments"]}
        evidence_ids = set(unavailable.values())
        for ref, references in ancestry.items():
            expected = references & evidence_ids
            if not expected:
                continue
            derive = checked["derivations"][ref]
            node = derive["node"]
            assessment = by_use.get((node["kind"], node["instruction_id"], node["operation_id"], node["slot"]))
            if assessment is None or assessment["coverage"] == "infeasible":
                continue
            if not any(row["status"] == ("unresolved" if derive["conservative"] else "required")
                       and ref in row["demand_refs"] and expected <= set(row["diagnostic_refs"])
                       for row in assessment["ranges"]):
                raise ValueError("Input assessment omits its unavailable required action's dependency evidence")
    expected_barrier_diagnostics = set()
    for assessment in checked["input_assessments"]:
        if assessment["coverage"] == "infeasible":
            continue
        applicable = barriers.for_assessment(assessment)
        if not applicable:
            continue
        expected = set()
        for barrier in applicable:
            expected_diagnostic = barrier_diagnostic_value(barrier, assessment["instruction_id"], assessment["operation_id"])
            identity = expected_diagnostic["id"]
            if diagnostics.get(identity) != expected_diagnostic:
                raise ValueError("Input assessment omits or changes an applicable source-review validation barrier")
            expected.add(identity)
        expected_barrier_diagnostics.update(expected)
        if (any(row["status"] == "deletable" for row in assessment["ranges"])
                or not any(row["status"] == "unresolved" and row["property"] == "value"
                    and row["path"] == [] and row["excluded_paths"] == []
                    and expected <= set(row["diagnostic_refs"]) for row in assessment["ranges"])):
            raise ValueError("Input assessment clears an unvalidated actual-operation range")
    for diagnostic in checked["diagnostics"]:
        if diagnostic["code"] != "input_contract_review_validation" or diagnostic["id"] in expected_barrier_diagnostics:
            continue
        operation = diagnostic["operation_id"]
        if operation is None or not any(diagnostic["reason"] == barrier_reason(barrier)
                                       for barrier in operation_barriers(engine, operation)):
            raise ValueError("Source-review diagnostic lacks its exact validated operation barrier")
    from .input_locations import InputLocationBuilder
    builder = getattr(engine, "input_location_builder", None) or InputLocationBuilder(engine)
    enriched = builder.enrich(deepcopy(checked["input_assessments"]))
    if enriched != checked["input_assessments"]:
        raise ValueError("Input assessment modification or location differs from its bound actual use")
    from .input_assessments import source_input_semantic_findings
    from .source_input_findings import SourceInputMismatchIndex
    source_view = SimpleNamespace(source_input_mismatches=SourceInputMismatchIndex(input_contract_review),
        ops=engine.ops, diagnostics={d["id"]: d for d in checked["diagnostics"]})
    expected_findings = source_input_semantic_findings(source_view, checked["input_assessments"])
    if sorted(expected_findings, key=lambda r:r["id"]) != [r for r in checked["input_findings"] if r["origin"] == "source_review"]:
        raise ValueError("Source-input findings differ from the immutable reviewed source and actual inputs")
    return checked
