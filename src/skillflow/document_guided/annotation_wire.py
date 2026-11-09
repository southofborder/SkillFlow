"""Compact model wire format, mechanically expanded into existing contracts.

Evidence inheritance copies references, never interprets source semantics. Call
pair IDs are generated from explicit wire coordinates, not argument matching.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Annotated, Literal, Union

from pydantic import Discriminator, Field, Tag, TypeAdapter, ValidationError, create_model, model_validator

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import _json_object, json_pointer
from skillflow.common.validation import StructuralValidationError, structural_error, schema_error
from skillflow.propagation.contracts import specs
from skillflow.propagation.contracts.values import StrictSpec, Text, ValueRef
from skillflow.propagation.contracts.evidence import SourceEvidence, CFGEvidence, RuleEvidence
from skillflow.propagation.contracts.demand import OperationTaskGoal, OperationExpression, RawDemandGoal, RawDemandSupplement
from skillflow.propagation.contracts.realizations import RealizationGap
from skillflow.propagation.contracts.task import TaskBinding
from skillflow.propagation.contracts.constraints import TaskConstraint
from skillflow.propagation.contracts.sensitivity import SensitivityDeclaration
from skillflow.propagation.contracts.profiles import FailureResponse


WIRE_VERSION = "skillflow-flat-annotation-v3"
_CITATION_NOTICE = "Declaration citation; semantic support is not independently verified."
_WIRE_EVIDENCE_TYPES = [create_model("Flat" + cls.__name__, __base__=cls,
    reason=(Text | None, None)) for cls in (SourceEvidence, CFGEvidence, RuleEvidence)]
WireEvidence = Union[tuple(_WIRE_EVIDENCE_TYPES)]
WireEvidences = Annotated[list[WireEvidence], Field(min_length=1)]

# Short descriptions of cross-field validators, not another executable schema.
# The fragment prompts select these by phase; the existing validators remain authoritative.
PROCESSING_RULES = {
    "segment_kind": "A segment with kind=cases or kind=for_each uses that exact form; ordinary processing omits kind. Unknown keys are invalid. A case may have segments=[] when it only yields an already available value; an ordinary segment must have operations or nonempty explicit local returns.",
    "local_returns": "Only mode=local accepts returns. Local segments explicitly supply returns, including [] for no model-visible result. Yield and output_bindings do not themselves observe a value. Never add returns or a fake operation to satisfy a format check.",
    "order": "Array order is fixed by default, also for multiple segments and for_each. Set order=partial only when source leaves operations unordered. Any cases summary requires fixed order. This does not make source-prose conditions executable.",
    "case_results": "Cases are nonrecursive alternatives with unique names. At least one candidate returns; an always-throw path belongs in the actual CFG. A summary output requires yield on every returning candidate and forbids yield on throwing candidates; without output, no candidate yields. pre_request_error has no network effects; post_request_error retains the actual preceding request. Obtain error values from the protected call's evidenced exception source, not a URL compute. Only a source catch can return an error record. Normal/error yields inside for_each are alternatives for one occurrence.",
    "evidence_inheritance": "IR evidence is nonempty. Child evidence may be omitted or []; it inherits the nearest applicable parent. Explicit expression and sensitivity evidence must cite source files and inclusive real lines; omitted source evidence skips CFG-only parents. A CFG/rule citation never becomes source evidence. Locations and source-backed gaps need their own applicable evidence.",
    "validate_ref": "input(index) reads the enclosing IR input, not the preceding operation. Indexes must exist; external_resource identifies a boundary, not payload. local(name) must be defined once in the current scope before use. Case/body locals do not escape except through declared output. Under partial order, alternatives may name a later local only while retaining an already available candidate; no cyclic local definitions.",
    "output_bindings": "Bind every actual public CFG output index exactly once to a real available value. A binding aliases that value; it does not compute, save or select content. Return/dispatch instructions have no invented public output 0. Preserve the actual producer and consumer versions.",
    "locations": "Operations name existing locations; each kind/name pair and each operand_refs coordinate is distinct. operand_refs use real CFG operands. Storage/runtime_context scope and retention describe the actual boundary; model/remote/user cannot be task-internal. An ordinary save/write defaults to mode=replace when omitted; this is the public runtime abstraction, not a claim that the source specifies overwrite. Source-explicit append/delete or another supported update takes priority. Delete writes have no input; replace/append writes have one. Unknown serialization alone does not remove a known write or its actual input. Only source-supported named task-local runtime_context replace writes inside cases may use may=true; keep existing/new handles separate with actual creation credentials, without claiming exact cache-hit counts.",
    "request_pair": "call supplies location, ordered request inputs and one response output; the program generates its exact deliver/receive pairing. For separate deliver/receive, use the same ordered request references, location and lexical scope with a unique pairing. Zero arguments are []; equal arguments do not merge distinct calls. Never supply request_id.",
    "collection_scope": "for_each names its real collection and one scoped item. Supply yield and output together or omit both. Only the yield escapes; repeated occurrences stay distinct and empty collections execute no body. Body-local references cannot escape, shadow or cross members, and must not directly read mutable CFG context_key operands. Nested for_each segments and shared writes remain unsupported except the explicit may state summary above; real CFG loops need not be collapsed into for_each. Do not encode iteration or append as opaque compute.",
    "validate_fields": "Build/update field paths cannot duplicate or overlap by prefix; excluded paths are also distinct. Object paths start with a field name; list paths start with an index and complete list construction uses consecutive indexes from 0. Do not mix field/index containers at one path. Conditional build members require an object and Boolean when. Field keys and integer indexes differ.",
    "compute_dependencies": "A compute has one dependency label per input when supplied; omission means possible for every input. Possible influence is not plaintext inclusion. Expressions reference actual operands/locals with source evidence. Preserve a real opaque computation without inventing external acquisition or input-to-error calculations.",
    "expression_target": "Expression supplements address an existing computation/control target with that target's real declared inputs. They cannot add an undeclared dependency, replace boundary acquisition, or turn prose into a Boolean fact. Inline operation expressions use that operation's declared values.",
    "loop_operations": "Use merge to associate each incoming value with a distinct actual predecessor block, member to select a source collection occurrence, and append with mode=item/items for real accumulation. branch belongs to the block terminator; its true/false targets exactly cover the actual outgoing successors. truthy requires an actual Boolean, not implicit truth conversion; nonempty/empty test collections, and has_member preserves collection traversal. The program derives loop regions and occurrence identities; never supply a loop ID, unfold iterations, or substitute unguarded alternatives/compute for predecessor/member relations.",
}


def _optional_evidence(name, base, *, source_only=False):
    evidence_type = _WIRE_EVIDENCE_TYPES[0] if source_only else WireEvidence
    if "request_id" in base.model_fields:
        fields = {key: (field.annotation, deepcopy(field)) for key, field in base.model_fields.items()
                  if key != "request_id"}
        fields["evidences"] = (list[evidence_type], Field(default_factory=list))
        return create_model(name, __base__=StrictSpec, **fields)
    return create_model(name, __base__=base,
                        evidences=(list[evidence_type], Field(default_factory=list)))


FlatExpression = _optional_evidence("FlatExpression", OperationExpression, source_only=True)
_OPS = [_optional_evidence("Flat" + cls.__name__, cls) for cls in (
    specs.RawReadOp, specs.RawReceiveOp, specs.RawDeliverOp, specs.RawWriteOp,
    specs.RawSelectPartOp, specs.RawExcludePartsOp, specs.RawUpdateFieldsOp,
    specs.RawBuildOp, specs.RawComputeOp, specs.RawFilterItemsOp,
    specs.RawMergeOp, specs.RawMemberOp, specs.RawBranchOp, specs.RawAppendOp)]
for index, cls in enumerate(_OPS):
    if cls.model_fields["op"].annotation == Literal["write"]:
        # Only the model wire has this default. The backend still receives an
        # explicit mode and retains its ordinary operand/update validation.
        _OPS[index] = create_model(cls.__name__, __base__=cls,
            mode=(Literal["replace", "append", "delete"], "replace"))
    if "expression" in cls.model_fields:
        fields = {"expression": (FlatExpression | None, None)}
        if cls.model_fields["op"].annotation == Literal["compute"]:
            fields["effect"] = (Literal["transform"] | None, "transform")
            fields["dependencies"] = (list[Literal["derived", "possible"]], Field(default_factory=list))
            def default_dependencies(value):
                if isinstance(value, dict) and "dependencies" not in value and isinstance(value.get("inputs"), list):
                    return {**value, "dependencies": ["possible"] * len(value["inputs"])}
                return value
            _OPS[index] = create_model(cls.__name__, __base__=cls, **fields,
                __validators__={"default_dependencies": model_validator(mode="before")(default_dependencies)})
        else:
            _OPS[index] = create_model(cls.__name__, __base__=cls, **fields)


class FlatCall(StrictSpec):
    op: Literal["call"]
    location: Text
    inputs: list[ValueRef]
    output: Text
    demands: list[OperationTaskGoal] = Field(default_factory=list)
    evidences: list[WireEvidence] = Field(default_factory=list)


FlatAtomicOp = Annotated[Union[tuple([*_OPS, FlatCall])], Field(discriminator="op")]


class FlatProcessing(StrictSpec):
    mode: Literal["default", "local", "model"] = "default"
    ops: list[FlatAtomicOp] = Field(default_factory=list)
    returns: list[ValueRef] = Field(default_factory=list)
    evidences: list[WireEvidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def explicit_returns(self):
        if self.mode == "local" and "returns" not in self.model_fields_set:
            raise ValueError("local processing requires an explicit returns list")
        if self.mode != "local" and self.returns:
            raise ValueError("returns belongs only to local processing")
        if not self.ops and not self.returns:
            raise ValueError("processing requires operations or explicit returned content")
        return self


FlatSensitivity = _optional_evidence("FlatSensitivity", SensitivityDeclaration, source_only=True)
FlatSensitivity = create_model("FlatSensitivity", __base__=FlatSensitivity,
    case_path=(list[str | int] | None, None))
FlatBinding = _optional_evidence("FlatOutputBinding", specs.OutputBinding)


class FlatCase(StrictSpec):
    name: Text
    phase: Literal["normal", "pre_request_error", "post_request_error", "local_error"]
    disposition: Literal["return", "throw"]
    condition: Text
    segments: list[FlatProcessing] = Field(default_factory=list,
        description="Actual additional processing only; omit or use [] when this candidate only yields an already available value.")
    yield_value: ValueRef | None = Field(default=None, alias="yield")
    evidences: list[WireEvidence] = Field(default_factory=list)


class FlatCaseSummary(StrictSpec):
    kind: Literal["cases"]
    cases: list[FlatCase] = Field(min_length=1)
    output: Text | None = None
    evidences: list[WireEvidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def case_results(self):
        if len({case.name for case in self.cases}) != len(self.cases):
            raise ValueError("case names must be unique within a summary")
        returned = [case for case in self.cases if case.disposition == "return"]
        if not returned:
            raise ValueError("bounded call cases require at least one return candidate; express an always-throw path as a terminal CFG path or an explicit local gap")
        if any(case.yield_value is not None for case in self.cases if case.disposition == "throw"):
            raise ValueError("throwing cases cannot yield a normal result")
        if self.output is not None and (not returned or any(case.yield_value is None for case in returned)):
            raise ValueError("summary output requires a yield from every returning case")
        if self.output is None and any(case.yield_value is not None for case in self.cases):
            raise ValueError("case yields require a summary output")
        return self


def segment_kind(value):
    """Dispatch on the existing tag; ordinary processing needs no extra field."""
    return value.get("kind", "processing") if isinstance(value, dict) else getattr(value, "kind", "processing")


FlatBodySegment = Annotated[Union[
    Annotated[FlatProcessing, Tag("processing")],
    Annotated[FlatCaseSummary, Tag("cases")]], Discriminator(segment_kind)]


class FlatForEach(StrictSpec):
    kind: Literal["for_each"]
    collection: ValueRef
    item: Text
    body: list[FlatBodySegment] = Field(min_length=1)
    yield_value: ValueRef | None = Field(default=None, alias="yield")
    output: Text | None = None
    sensitivity: list[FlatSensitivity] = Field(default_factory=list)
    evidences: list[WireEvidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def paired_result(self):
        if (self.yield_value is None) != (self.output is None):
            raise ValueError("for_each yield and output must be supplied together")
        return self


FlatSegment = Annotated[Union[
    Annotated[FlatProcessing, Tag("processing")],
    Annotated[FlatForEach, Tag("for_each")],
    Annotated[FlatCaseSummary, Tag("cases")]], Discriminator(segment_kind)]


class FlatIR(StrictSpec):
    order: Literal["fixed", "partial"] = "fixed"
    evidences: WireEvidences
    segments: list[FlatSegment] = Field(default_factory=list)
    output_bindings: list[FlatBinding] = Field(default_factory=list)
    sensitivity: list[FlatSensitivity] = Field(default_factory=list)

class FlatLocation(StrictSpec):
    kind: specs.LocationKind
    name: Text
    operand_refs: list[specs.OperandRef] = Field(default_factory=list)
    access_scope: Literal["task", "recipient", "shared", "public"] | None = None
    retention: Literal["task", "persistent"] | None = None
    evidences: WireEvidences


FlatGap = create_model("FlatRealizationGap", __base__=RealizationGap,
    evidences=(list[_WIRE_EVIDENCE_TYPES[0]], Field(min_length=1)))
FlatSupplement = create_model("FlatDemandSupplement", __base__=RawDemandSupplement,
    evidences=(list[_WIRE_EVIDENCE_TYPES[0]], Field(min_length=1)))


class FlatProcessingGap(StrictSpec):
    instruction_id: Text
    reason: Text
    evidences: Annotated[list[_WIRE_EVIDENCE_TYPES[0]], Field(min_length=1)]
    outputs: list[Annotated[int, Field(strict=True, ge=0)]] = Field(default_factory=list)
    locations: list[Text] = Field(default_factory=list)
    control: bool = False
    unmodeled: bool = False


class FlatRealization(StrictSpec):
    requirement_id: Text
    bindings: list[TaskBinding] = Field(default_factory=list)
    gaps: list[FlatGap] = Field(default_factory=list)
    constraints: list[TaskConstraint] = Field(default_factory=list)


class FlatAnnotationResponse(StrictSpec):
    outcome: Literal["completed"]
    realizations: list[FlatRealization]
    demands: list[RawDemandGoal] = Field(default_factory=list)
    expressions: list[FlatSupplement] = Field(default_factory=list)
    ir_semantics: dict[Text, FlatIR]
    locations: dict[Text, FlatLocation] = Field(default_factory=dict)
    processing_gaps: list[FlatProcessingGap] = Field(default_factory=list)


RESPONSE_ADAPTER = TypeAdapter(Annotated[FlatAnnotationResponse | FailureResponse, Field(discriminator="outcome")])


def nearest_source_evidence(value, path):
    """Find the nearest applicable authored source citations, skipping CFG-only parents."""
    ancestors, current, prefix = [(value, [])], value, []
    for key in path:
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            break
        prefix = [*prefix, key]
        ancestors.append((current, prefix))
    for ancestor, pointer in reversed(ancestors):
        citations = ancestor.get("evidences", []) if isinstance(ancestor, dict) else []
        if isinstance(citations, list):
            sources = [item for item in citations if isinstance(item, dict) and "file" in item]
            if sources:
                return deepcopy(sources), [*pointer, "evidences"]
    return [], []


def format_diagnostics(value):
    """Collect independent wire rules before a failed parent stops expansion."""
    rows = []
    if not isinstance(value, dict):
        return rows
    def error(code, path, message, **context):
        rows.extend(structural_error(code, json_pointer(*path), message, **context).diagnostics)
    def source_evidence(claim, fallback, path, inherited_from):
        if not isinstance(claim, dict):
            return
        fallback = fallback if isinstance(fallback, list) else []
        own = claim.get("evidences")
        inherited, source_path = nearest_source_evidence(value, path[:-1])
        values = own or inherited or [e for e in fallback if isinstance(e, dict) and "file" in e]
        if not isinstance(values, list) or not values or any(not isinstance(e, dict) or "file" not in e for e in values):
            error("evidence_kind", [*path, "evidences"], "sensitivity and expression evidence must cite frozen source",
                  inherited_from=json_pointer(*(source_path or inherited_from)), allowed="source evidence")
    def processing(segment, fallback, path, inherited_from):
        if not isinstance(segment, dict):
            return
        evidence = segment.get("evidences") or fallback
        evidence = evidence if isinstance(evidence, list) else []
        origin = [*path, "evidences"] if segment.get("evidences") else inherited_from
        if segment.get("kind") == "cases":
            for index, case in enumerate(segment.get("cases", []) if isinstance(segment.get("cases"), list) else []):
                if not isinstance(case, dict):
                    continue
                cp = [*path, "cases", index]
                inherited = case.get("evidences") or evidence
                inherited_origin = [*cp, "evidences"] if case.get("evidences") else origin
                for child_index, child in enumerate(case.get("segments", []) if isinstance(case.get("segments"), list) else []):
                    processing(child, inherited, [*cp, "segments", child_index], inherited_origin)
            return
        if segment.get("mode") == "local" and "returns" not in segment:
            error("local_returns", [*path, "returns"], "local processing requires an explicit returns list")
        for i, op in enumerate(segment.get("ops", []) if isinstance(segment.get("ops", []), list) else []):
            if isinstance(op, dict) and isinstance(op.get("expression"), dict):
                source_evidence(op["expression"], op.get("evidences") or evidence,
                                [*path, "ops", i, "expression"],
                                [*path, "ops", i, "evidences"] if op.get("evidences") else origin)
    specs_value = value.get("ir_semantics", {})
    for ir_id, spec in specs_value.items() if isinstance(specs_value, dict) else []:
        if not isinstance(spec, dict):
            continue
        path = ["ir_semantics", ir_id]
        evidence = spec.get("evidences", [])
        evidence = evidence if isinstance(evidence, list) else []
        segments = spec.get("segments", [])
        segments = segments if isinstance(segments, list) else []
        for i, sensitive in enumerate(spec.get("sensitivity", []) if isinstance(spec.get("sensitivity", []), list) else []):
            source_evidence(sensitive, evidence, [*path, "sensitivity", i], [*path, "evidences"])
        for i, segment in enumerate(segments):
            if not isinstance(segment, dict):
                continue
            child_path = [*path, "segments", i]
            if segment.get("kind") != "for_each":
                processing(segment, evidence, child_path, [*path, "evidences"])
            else:
                inherited = segment.get("evidences") or evidence
                origin = [*child_path, "evidences"] if segment.get("evidences") else [*path, "evidences"]
                for j, sensitive in enumerate(segment.get("sensitivity", []) if isinstance(segment.get("sensitivity", []), list) else []):
                    source_evidence(sensitive, inherited, [*child_path, "sensitivity", j], origin)
                for j, child in enumerate(segment.get("body", []) if isinstance(segment.get("body", []), list) else []):
                    processing(child, inherited, [*child_path, "body", j], origin)
    return rows


def _parse(raw):
    try:
        value = _json_object(raw)
    except (ValueError, TypeError) as error:
        raise structural_error("json_format", "", str(error)) from error
    diagnostics = format_diagnostics(value)
    try:
        parsed = RESPONSE_ADAPTER.validate_python(value)
    except ValidationError as error:
        diagnostics.extend(schema_error(error, candidate=value, schema=RESPONSE_ADAPTER.json_schema()).diagnostics)
        raise StructuralValidationError(diagnostics) from error
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    # Preserve submitted omission and order, rather than inventing defaults in
    # the model's saved answer. The validated backend owns normalization.
    return value, parsed


def _replace_local_refs(item, names):
    if isinstance(item, list):
        return [_replace_local_refs(child, names) for child in item]
    if not isinstance(item, dict) or item.get("kind") == "literal" or item.get("op") == "literal":
        return deepcopy(item)
    if item.get("kind") == "local" and item.get("name") in names:
        return deepcopy(names[item["name"]])
    return {key: _replace_local_refs(child, names) for key, child in item.items()}


def _lower_sensitivity(items, names, case_maps, scope_path=()):
    output = []
    for item in items:
        row = deepcopy(item)
        case_path = row.pop("case_path", None)
        selected = names
        if case_path is not None:
            if tuple(case_path) not in case_maps:
                raise structural_error("case_reference", "/case_path", "sensitivity case path does not exist")
            if (bool(scope_path) != ("body" in case_path)
                    or scope_path and case_path[:len(scope_path)] != list(scope_path)):
                raise structural_error("case_reference", "/case_path", "case-local sensitivity must remain in its member scope")
            selected = {**names, **case_maps[tuple(case_path)]}
        output.append(_replace_local_refs(row, selected))
    return output


def _expand(raw, material, *, processing_only=False, validation_gaps=(), _sensitivity_scopes=None):
    from skillflow.propagation.annotation.services import validate_raw_response
    wire, parsed = _parse(raw)
    if isinstance(parsed, FailureResponse):
        validate_raw_response(wire, material)
    paths, coordinates, scope_maps = {}, {}, {}
    def register(backend, origin):
        paths[json_pointer(*backend)] = json_pointer(*origin)
    def inherit(value, fallback, *, source_only=False, path=()):
        inherited = fallback
        if source_only and not value.get("evidences"):
            inherited = nearest_source_evidence(wire, path[:-1])[0] or [item for item in fallback if "file" in item]
        values = deepcopy(value.get("evidences") or inherited)
        if not values:
            raise structural_error("evidence_inheritance", json_pointer(*path, "evidences"), "an inherited evidence list must be nonempty")
        if source_only and any("file" not in item for item in values):
            raise structural_error("evidence_kind", json_pointer(*path, "evidences"), "sensitivity and expression evidence must cite frozen source")
        for item in values:
            if item.get("reason") is None:
                item["reason"] = _CITATION_NOTICE
        return values
    backend = {"outcome": "completed",
               "realizations": deepcopy(wire["realizations"]), "demands": deepcopy(wire.get("demands", [])),
               "expressions": deepcopy(wire.get("expressions", [])), "ir_semantics": {},
               "locations": {}, "location_evidences": {}}
    if not processing_only:
        backend["task_revision_id"] = material["task"]["task_sha256"]
    if wire.get("processing_gaps") or validation_gaps:
        backend["processing_gaps"] = [
            {**deepcopy(gap), "evidences": inherit(gap, [], source_only=True, path=["processing_gaps", i])}
            for i, gap in enumerate(wire.get("processing_gaps", []))] + deepcopy(list(validation_gaps))
    locations = backend["locations"]
    for name, model in parsed.locations.items():
        value = model.model_dump(mode="json", exclude_unset=True)
        backend["location_evidences"][name] = inherit({"evidences": value.pop("evidences")}, [])
        value.setdefault("operand_refs", [])
        value.setdefault("access_scope", "task" if value["kind"] in {"runtime_context", "storage"} else "recipient")
        value.setdefault("retention", "persistent" if value["kind"] == "storage" else "task" if value["kind"] == "runtime_context" else None)
        locations[name] = value
        register(["locations", name], ["locations", name])
        register(["location_evidences", name], ["locations", name, "evidences"])

    def effect(op):
        kind = op["op"]
        if kind == "branch":
            return None
        boundary = locations.get(op.get("location", op.get("target")), {}).get("kind")
        if kind in {"read", "write"}:
            if boundary == "runtime_context":
                return "context_read" if kind == "read" else "context_write"
            if boundary == "storage":
                return "fs_read" if kind == "read" else "fs_write"
        if kind == "receive":
            return "net_receive" if boundary == "remote" else None
        if kind == "deliver":
            return {"remote": "net_send", "user": "user_output"}.get(boundary)
        return "transform"

    def processing(value, fallback, bp, wp, ir_id, relative, fallback_path):
        evidence = inherit(value, fallback)
        evidence_path = [*wp, "evidences"] if value.get("evidences") else fallback_path
        result = {"kind": "processing", "mode": value.get("mode", "default"),
                  "events": [], "evidences": evidence}
        if "returns" in value:
            result["returns"] = deepcopy(value["returns"])
        register(bp, wp)
        register([*bp, "evidences"], evidence_path)
        for i, original in enumerate(value.get("ops", [])):
            op = deepcopy(original)
            if op["op"] == "write":
                op.setdefault("mode", "replace")
            declared_effect = op.pop("effect", "transform") if op["op"] == "compute" else None
            op["evidences"] = inherit(op, evidence)
            op_evidence_path = [*wp, "ops", i, "evidences"] if original.get("evidences") else evidence_path
            if "request_id" in op:
                raise structural_error("program_owned", json_pointer(*wp, "ops", i, "request_id"), "request_id is program owned")
            if op.get("expression") is not None:
                expression = op["expression"]
                expression["evidences"] = inherit(expression, op["evidences"], source_only=True, path=[*wp, "ops", i, "expression"])
            if op["op"] == "call":
                token = canonical_sha256([ir_id, *wp, "ops", i])
                request = {"op": "deliver", "target": op["location"], "inputs": deepcopy(op["inputs"]),
                           "request_id": token, "evidences": deepcopy(op["evidences"])}
                response = {"op": "receive", "location": op["location"], "inputs": deepcopy(op["inputs"]),
                            "output": op["output"], "request_id": token, "evidences": deepcopy(op["evidences"])}
                request_goals, response_goals = [], []
                request_indexes, response_indexes = [], []
                for goal_index, goal in enumerate(op.get("demands", [])):
                    (response_goals if goal["target"]["kind"] == "output" else request_goals).append(goal)
                    (response_indexes if goal["target"]["kind"] == "output" else request_indexes).append(goal_index)
                if request_goals:
                    request["demands"] = request_goals
                if response_goals:
                    response["demands"] = response_goals
                generated = [request, response]
            else:
                generated = [op]
            entries = {}
            for index, operation in enumerate(generated):
                j = len(result["events"])
                event = {"effect": declared_effect if operation["op"] == "compute" else effect(operation), "atomic_ops": [operation]}
                if event["effect"] is not None:
                    event["evidences"] = deepcopy(operation["evidences"])
                result["events"].append(event)
                op_bp = [*bp, "events", j, "atomic_ops", 0]
                op_wp = [*wp, "ops", i]
                register([*bp, "events", j], op_wp)
                register(op_bp, op_wp)
                register([*op_bp, "evidences"], op_evidence_path)
                for k, goal in enumerate(operation.get("demands", [])):
                    goal_indexes = (response_indexes if index else request_indexes) if original["op"] == "call" else list(range(len(original.get("demands", []))))
                    register([*op_bp, "demands", k], [*op_wp, "demands", goal_indexes[k]])
                entries["response" if len(generated) == 2 and index else "request"] = [*relative, "events", j, "atomic_ops", 0]
            coordinates[(ir_id, tuple([*wp[2:], "ops", i]))] = (original["op"] == "call", entries)
        return result

    for ir_id, model in parsed.ir_semantics.items():
        value = model.model_dump(mode="json", by_alias=True, exclude_unset=True)
        ir_evidence = inherit(value, [])
        def model_evidence(segments):
            for segment in segments:
                if segment.get("kind") == "for_each":
                    yield from model_evidence(segment["body"])
                elif segment.get("kind") == "cases":
                    for case in segment["cases"]:
                        yield from model_evidence(case.get("segments", []))
                elif segment.get("mode") == "model":
                    yield from (segment.get("evidences") or ir_evidence)
        model_sources = list(model_evidence(value.get("segments", [])))
        operator = ["llm"] if model_sources else None
        result = {"order": value.get("order", "fixed"), "operator": operator,
                  "operator_evidences": [{**deepcopy(e), "value": "llm"} for e in model_sources],
                  "events": [], "output_bindings": [], "sensitivity": []}
        for index, binding in enumerate(value.get("output_bindings", [])):
            result["output_bindings"].append({**binding, "evidences": inherit(binding, ir_evidence)})
            register(["ir_semantics", ir_id, "output_bindings", index], ["ir_semantics", ir_id, "output_bindings", index])
            register(["ir_semantics", ir_id, "output_bindings", index, "evidences"],
                ["ir_semantics", ir_id, "output_bindings", index, "evidences"] if binding.get("evidences") else ["ir_semantics", ir_id, "evidences"])
        for i, sensitive in enumerate(value.get("sensitivity", [])):
            result["sensitivity"].append({**sensitive, "evidences": inherit(sensitive, ir_evidence, source_only=True,
                path=["ir_semantics", ir_id, "sensitivity", i])})
        aliases, case_maps = {}, {}
        refs = _replace_local_refs
        def sensitivity(items, names, scope_path=()):
            return _lower_sensitivity(items, names, case_maps, scope_path)
        def emit_segments(segments, target, bp_prefix, wp_prefix, inherited, inherited_path, names):
            pending = []
            for si, original_segment in enumerate(segments):
                wp = [*wp_prefix, si]
                bp = [*bp_prefix, len(target)]
                segment = refs(original_segment, names)
                if segment.get("kind") == "cases":
                    group = "case_group_" + canonical_sha256([ir_id, wp])[:20]
                    yields = []
                    evidence = inherit(segment, inherited)
                    thrown = False
                    for ci, case in enumerate(segment["cases"]):
                        cp = [*wp, "cases", ci]
                        identity = "case_" + canonical_sha256([group, case["name"]])[:20]
                        case_segments = case.get("segments", [])
                        local_map = {op["output"]: {"kind": "local", "name": identity + "__" + op["output"]}
                                     for child in case_segments for op in child.get("ops", []) if "output" in op}
                        case_maps[tuple(cp[2:])] = local_map
                        label = {"group": group, "id": identity, **{key: case[key] for key in
                                 ("name", "phase", "disposition", "condition")}}
                        case_evidence = inherit(case, evidence)
                        if not case_segments:
                            # A source-backed candidate can select an existing value
                            # without performing another operation. Preserve its
                            # control/completion identity, never an observation.
                            carrier = {"kind": "processing", "mode": "local", "returns": [],
                                "evidences": case_evidence, "case": label,
                                "events": [{"effect": None, "atomic_ops": [], "case": label}]}
                            if pending:
                                carrier["requires_completion"] = list(pending)
                            register([*bp_prefix, len(target)], cp)
                            target.append(carrier)
                        for sj, original_child in enumerate(case_segments):
                            child = refs(original_child, local_map)
                            for op in child.get("ops", []):
                                if op.get("output") in local_map:
                                    op["output"] = local_map[op["output"]]["name"]
                            child_bp, child_wp = [*bp_prefix, len(target)], [*cp, "segments", sj]
                            expanded = processing(child, case_evidence, child_bp, child_wp, ir_id,
                                                  child_bp[2:], [*cp, "evidences"])
                            expanded["case"] = label
                            if pending:
                                expanded["requires_completion"] = list(pending)
                            target.append(expanded)
                        if case["disposition"] == "return" and case.get("yield") is not None:
                            yields.append(refs(case["yield"], local_map))
                        thrown |= case["disposition"] == "throw"
                    if segment.get("output") is not None:
                        names[segment["output"]] = yields[0] if len(yields) == 1 else {"kind": "alternatives", "items": yields}
                    if thrown:
                        pending.append(group)
                    continue
                if segment.get("kind") != "for_each":
                    expanded = processing(segment, inherited, bp, wp, ir_id, bp[2:], inherited_path)
                    if pending:
                        expanded["requires_completion"] = list(pending)
                    target.append(expanded)
                    continue
                evidence = inherit(segment, inherited)
                loop = {"kind": "for_each", "collection": deepcopy(segment["collection"]), "item": segment["item"],
                        "body": [], "evidences": evidence, "sensitivity": []}
                child_aliases = dict(names)
                completions = emit_segments(segment["body"], loop["body"], [*bp, "body"], [*wp, "body"],
                                            evidence, [*wp, "evidences"], child_aliases)
                if completions:
                    loop["completion_groups"] = completions
                if pending:
                    loop["requires_completion"] = list(pending)
                if segment.get("output") is not None:
                    loop.update(output=segment["output"], **{"yield": refs(segment["yield"], child_aliases)})
                for i, sensitive in enumerate(sensitivity(segment.get("sensitivity", []), child_aliases, wp[2:])):
                    loop["sensitivity"].append({**sensitive, "evidences": inherit(sensitive, evidence, source_only=True, path=[*wp, "sensitivity", i])})
                scope_maps[(ir_id, tuple(wp[2:]))] = bp[2:]
                if _sensitivity_scopes is not None:
                    _sensitivity_scopes[(ir_id, tuple(wp[2:]))] = (bp[2:], child_aliases, case_maps)
                register(bp, wp)
                target.append(loop)
                pending.extend(completions)
            return list(dict.fromkeys(pending))
        emit_segments(value.get("segments", []), result["events"], ["ir_semantics", ir_id, "events"],
                      ["ir_semantics", ir_id, "segments"], ir_evidence, ["ir_semantics", ir_id, "evidences"], aliases)
        result["output_bindings"] = refs(result["output_bindings"], aliases)
        result["sensitivity"] = sensitivity(result["sensitivity"], aliases)
        if _sensitivity_scopes is not None:
            _sensitivity_scopes[(ir_id, ())] = ([], aliases, case_maps)
        register(["ir_semantics", ir_id], ["ir_semantics", ir_id])
        backend["ir_semantics"][ir_id] = result

    def remap(value, path=()):
        if isinstance(value, list):
            return [remap(child, (*path, index)) for index, child in enumerate(value)]
        if not isinstance(value, dict):
            return value
        if value.get("kind") == "literal" or value.get("op") == "literal":
            return deepcopy(value)
        item = {key: remap(child, (*path, key)) for key, child in value.items()}
        if "instruction_id" in item and "operation_path" in item:
            key = (item["instruction_id"], tuple(item["operation_path"]))
            if key not in coordinates:
                raise structural_error("operation_reference", json_pointer(*path, "operation_path"), "flat operation target does not exist")
            is_call, entries = coordinates[key]
            phase = item.pop("phase", None)
            if phase is not None and not is_call:
                raise structural_error("operation_phase", json_pointer(*path, "phase"), "phase is permitted only on a call target")
            # This projection handles constraint references. Call demand slots
            # are routed separately when the call is expanded above.
            choice = (phase or "request") if is_call else "request"
            item["operation_path"] = entries[choice]
        if "scope_path" in item and item["scope_path"] and item["scope_path"][0] == "segments":
            item["scope_path"] = scope_maps.get((item.get("instruction_id"), tuple(item["scope_path"])),
                                                ["events", *item["scope_path"][1:]])
        return item
    backend["realizations"] = remap(backend["realizations"], ("realizations",))
    for row in backend["realizations"]:
        for gap in row.get("gaps", []):
            gap["evidences"] = inherit(gap, [], source_only=True)
    for expression in backend["expressions"]:
        expression["evidences"] = inherit(expression, [], source_only=True)
    seeded = {row["requirement_id"] for row in backend["demands"]}
    def find_demands(value):
        if isinstance(value, dict):
            for goal in value.get("demands", []):
                seeded.add(goal["requirement_id"])
            for child in value.values():
                find_demands(child)
        elif isinstance(value, list):
            for child in value:
                find_demands(child)
    find_demands(backend["ir_semantics"])
    for index, row in enumerate(backend["realizations"]):
        row.setdefault("bindings", [])
        row.setdefault("gaps", [])
        expressed = row["requirement_id"] in seeded or bool(row.get("constraints"))
        row["status"] = ("partial" if row["gaps"] else "expressed") if expressed else ("retained_only" if row["bindings"] else "unmapped")
        register(["realizations", index], ["realizations", index])
    try:
        if processing_only:
            _validate_processing_backend(backend, material)
            return wire, backend, paths
        return wire, validate_raw_response(backend, material), paths
    except StructuralValidationError as error:
        for row in error.diagnostics:
            pointer = row["path"]
            for prefix in sorted(paths, key=len, reverse=True):
                if pointer == prefix or pointer.startswith(prefix + "/"):
                    row["path"] = paths[prefix] + pointer[len(prefix):]
                    break
        raise


def _validate_processing_backend(backend, material):
    """Reuse processing checks with source and CFG only; no substitute Task."""
    from types import SimpleNamespace
    from skillflow.propagation.contracts.limitations import ProcessingGap
    from skillflow.propagation.contracts.runtime_contract import runtime_contract
    from skillflow.propagation.material import check_evidence
    from skillflow.propagation.contracts.demand_index import build_demand_target_index
    from skillflow.propagation.contracts.demand import (
        DemandExpression, expression_refs, _validate_ref, _literal_inputs, _ref_leaves,
    )
    from skillflow.propagation.contracts.references import target_key
    prepared = {**material, "runtime_contract": material.get("runtime_contract", runtime_contract())}
    class ProcessingCheck(SimpleNamespace):
        def model_dump(self, **kwargs):
            return {"ir_semantics": {key: value.model_dump(mode="json") for key, value in self.ir_semantics.items()},
                    "locations": {key: value.model_dump(mode="json") for key, value in self.locations.items()},
                    "processing_gaps": [value.model_dump(mode="json") for value in self.processing_gaps]}
    annotation = ProcessingCheck(
        ir_semantics={key: specs.RawIRSemantics.model_validate(value) for key, value in backend["ir_semantics"].items()},
        locations={key: specs.LocationSpec.model_validate(value) for key, value in backend["locations"].items()},
        processing_gaps=[ProcessingGap.model_validate(value) for value in backend.get("processing_gaps", [])])
    diagnostics = []
    try:
        specs.validate_specs(prepared["cfg"], annotation)
    except StructuralValidationError as error:
        diagnostics.extend(error.diagnostics)
    def mechanisms(events, prefix):
        for i, event in enumerate(events):
            pointer = prefix + f"/{i}"
            if isinstance(event, specs.RawForEachSpec):
                mechanisms(event.body, pointer + "/body")
            elif isinstance(event, specs.ProcessingSpec) and event.mode == "local" and not any(
                    hasattr(evidence, "file") or hasattr(evidence, "target") for evidence in event.evidences):
                diagnostics.extend(structural_error("mechanism_evidence_reference", pointer + "/evidences",
                    "local processing requires source or CFG mechanism evidence").diagnostics)
    for ir, spec in annotation.ir_semantics.items():
        mechanisms(spec.events, json_pointer("ir_semantics", ir, "events"))
    evidence_items = [(json_pointer("location_evidences", name, index), evidence)
        for name, values in backend["location_evidences"].items() for index, evidence in enumerate(values)]
    evidence_items += list(specs.iter_located_spec_evidence(annotation))
    evidence_items += [(json_pointer("expressions", i, "evidences", j), evidence)
        for i, expression in enumerate(backend["expressions"]) for j, evidence in enumerate(expression["evidences"])]
    evidence_items += [(json_pointer("processing_gaps", i, "evidences", j), evidence)
        for i, gap in enumerate(backend.get("processing_gaps", [])) for j, evidence in enumerate(gap["evidences"])]
    for pointer, evidence in evidence_items:
        try:
            check_evidence(evidence, prepared)
        except StructuralValidationError as error:
            diagnostics.extend({**row, "path": pointer + row["path"]} for row in error.diagnostics)
    if not diagnostics:
        targets = build_demand_target_index(prepared["cfg"], backend)
        expressions = [(f"/expressions/{i}", expression, targets.get(target_key(expression["target"])))
                       for i, expression in enumerate(backend["expressions"])]
        expressions += [(json_pointer("ir_semantics", target["instruction_id"], *target["raw_path"], "expression"),
                         target["value"]["expression"], target) for target in targets.values()
                        if target.get("domain") == "transfer" and target.get("kind") == "operation"
                        and target["value"].get("expression") is not None]
        for pointer, expression, target in expressions:
            if target is None or not target.get("supports_expression", False):
                diagnostics.extend(structural_error("expression_target_capability", pointer + "/target",
                    "expression supplements require an existing computation or control target").diagnostics)
                continue
            typed = TypeAdapter(DemandExpression).validate_python(expression["expression"])
            try:
                TypeAdapter(DemandExpression).validate_python(_literal_inputs(expression["expression"], target.get("input_literals", {})))
            except ValidationError as error:
                diagnostics.extend(schema_error(error, pointer + "/expression", candidate=expression["expression"],
                    schema=TypeAdapter(DemandExpression).json_schema()).diagnostics)
            for reference in expression_refs(typed):
                try:
                    _validate_ref(reference, target)
                except StructuralValidationError as error:
                    diagnostics.extend({**row, "path": pointer + "/expression" + row["path"]} for row in error.diagnostics)
                if target.get("declared_refs") is not None and any(not hasattr(leaf, "value") and
                        leaf.model_dump(mode="json") not in target["declared_refs"] for leaf in _ref_leaves(reference)):
                    diagnostics.extend(structural_error("expression_input", pointer + "/expression",
                        "expression supplements cannot introduce undeclared operation inputs").diagnostics)
            for i, evidence in enumerate(expression["evidences"]):
                try:
                    check_evidence(evidence, prepared)
                except StructuralValidationError as error:
                    diagnostics.extend({**row, "path": pointer + f"/evidences/{i}" + row["path"]} for row in error.diagnostics)
    if diagnostics:
        raise StructuralValidationError(diagnostics)


def expand_processing(raw, material, *, validation_gaps=()):
    """Return wire/backend/path projections without reading a Task."""
    return _expand(raw, material, processing_only=True, validation_gaps=validation_gaps)


def _processing_expansion(raw, material, *, validation_gaps=()):
    """One checked expansion and its short-lived sensitivity lookup tables."""
    scopes = {}
    expanded = _expand(raw, material, processing_only=True, validation_gaps=validation_gaps,
                       _sensitivity_scopes=scopes)
    return (*expanded, scopes)


def _project_expanded_sensitivity(scopes, instruction_id, scope_path, declaration):
    lowered_scope, aliases, case_maps = scopes[(instruction_id, tuple(scope_path))]
    return list(lowered_scope), _lower_sensitivity([declaration], aliases, case_maps, scope_path)[0]


def project_sensitivity(processing_fragment, instruction_id, scope_path, declaration, material, *, validation_gaps=()):
    """Use the same case/alias lowering as final annotation assembly."""
    wire = {"outcome": "completed", "realizations": [], **deepcopy(processing_fragment)}
    spec = wire["ir_semantics"][instruction_id]
    for record in wire["ir_semantics"].values():
        record["sensitivity"] = []
        for segment in record.get("segments", []):
            if segment.get("kind") == "for_each":
                segment["sensitivity"] = []
    scope = spec
    for step in scope_path:
        scope = scope[step]
    scope["sensitivity"] = [deepcopy(declaration)]
    _, backend, paths = expand_processing(wire, material, validation_gaps=validation_gaps)
    if not scope_path:
        return [], backend["ir_semantics"][instruction_id]["sensitivity"][0]
    original = json_pointer("ir_semantics", instruction_id, *scope_path)
    lowered = next(key for key, value in paths.items() if value == original)
    tokens = lowered.split("/")[3:]
    index = int(tokens[1])
    return ["events", index], backend["ir_semantics"][instruction_id]["events"][index]["sensitivity"][0]


def expression_reference_view(processing_fragment):
    """List existing expressions at their public constraint reference targets.

    The input is the accepted processing fragment. This is a display projection,
    not another expression validator or a repair of submitted correspondence.
    Inline expressions normalize at the operation itself, independently of its
    output slot. Keep the authored flat coordinates; the existing adapter owns
    their projection into backend atomic operations.
    """
    rows = [{"target": deepcopy(row["target"]), "expression": deepcopy(row["expression"])}
            for row in processing_fragment.get("expressions", [])]

    def segments(instruction_id, values, prefix):
        for index, segment in enumerate(values):
            path = [*prefix, index]
            if segment.get("kind") == "for_each":
                segments(instruction_id, segment["body"], [*path, "body"])
            elif segment.get("kind") == "cases":
                for case_index, case in enumerate(segment["cases"]):
                    segments(instruction_id, case.get("segments", []),
                             [*path, "cases", case_index, "segments"])
            else:
                for op_index, operation in enumerate(segment.get("ops", [])):
                    expression = operation.get("expression")
                    if expression is not None:
                        rows.append({"target": {"instruction_id": instruction_id,
                            "operation_path": [*path, "ops", op_index], "slot": {"kind": "self"}},
                            "expression": deepcopy(expression["expression"])})

    for instruction_id, record in processing_fragment["ir_semantics"].items():
        segments(instruction_id, record.get("segments", []), ["segments"])
    return rows


def normalize_flat_annotation(raw, material):
    """Validate one complete flat response and return canonical backend raw."""
    return _expand(raw, material)[1]


def compile_flat_response(raw, material, *, validation_gaps=()):
    """Return (submitted wire, backend raw, compiled, coordinate mapping)."""
    from skillflow.propagation.annotation.compiler import compile_response
    value = _json_object(raw)
    saved = deepcopy(value)
    internal = value.pop("_validation_gaps", [])
    origins = value.pop("_fragment_origins", None)
    if origins is not None and (not isinstance(origins, dict) or any(
            not isinstance(pointer, str) or not pointer.startswith("/") or not isinstance(origin, dict)
            or set(origin) != {"fragment", "path"} or origin["fragment"] not in {"processing", "task-correspondence", "sensitivity"}
            or not isinstance(origin["path"], str) or not origin["path"].startswith("/")
            for pointer, origin in origins.items())):
        raise ValueError("Invalid program fragment origin map")
    if internal and validation_gaps:
        raise ValueError("Program validation gaps must have one provenance owner")
    if internal:
        from skillflow.propagation.contracts.limitations import ProcessingGap
        for gap in internal:
            if ProcessingGap.model_validate(gap).origin != "validation":
                raise ValueError("Program gap envelope accepts validation origins only")
    wire, backend, paths = _expand(value, material, validation_gaps=internal or validation_gaps)
    if internal or origins is not None:
        wire = saved
    backend, compiled, mapping = compile_response(backend, material)
    mapping.update(wire_version=WIRE_VERSION, wire_sha256=canonical_sha256(wire), wire_paths=paths)
    def project(pointer):
        for prefix in sorted(paths, key=len, reverse=True):
            if pointer == prefix or pointer.startswith(prefix + "/"):
                return paths[prefix] + pointer[len(prefix):]
        return pointer
    for item in mapping["events"]:
        item["wire_path"] = project(json_pointer(*item["raw_path"]))
    for item in mapping["goals"]:
        item["wire_pointer"] = project(item["raw_pointer"])
    if origins is not None:
        mapping["fragment_origins"] = {pointer: item["fragment"] for pointer, item in origins.items()}
        mapping["fragment_paths"] = deepcopy(origins)
        mapping["processing_gaps"] = deepcopy(backend.get("processing_gaps", []))
    return wire, backend, compiled, mapping
