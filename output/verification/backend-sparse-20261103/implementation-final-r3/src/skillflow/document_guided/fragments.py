"""Three isolated model records and pure assembly into the existing flat wire.

Processing validation reads source/CFG only. Correspondence cannot change that
processing, and sensitivity can only label its already declared lexical values.
"""
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Annotated, Literal, Union

from pydantic import Discriminator, Field, Tag, TypeAdapter, ValidationError, create_model, model_validator

from skillflow.common.source_evidence import _json_object, json_pointer, resolve_pointer
from skillflow.common.validation import StructuralValidationError, structural_error, schema_error
from skillflow.propagation.contracts.values import StrictSpec, Text, ValueRef
from skillflow.propagation.contracts.references import cfg_instructions
from skillflow.propagation.contracts.demand import OperationTaskGoal, RawDemandGoal
from . import annotation_wire as flat

VERSION = "skillflow-document-fragments-v3"

FRAGMENT_RULES = {
    "processing": {
        **flat.PROCESSING_RULES,
        "processing_coverage": "No Task demands or sensitivity fields belong in processing. A genuinely unrepresentable required operation uses a source-backed processing_gap with unmodeled=true instead of executable semantics. Name affected output indexes, locations or control; unspecified scope retains the control-reachable continuation. Precision limits on otherwise complete may facts use unmodeled=false, never to conceal a missing actual effect.",
    },
    "task-correspondence": {
        "realization_coverage": "Use each existing Task requirement_id exactly once in realizations. Keep its bindings, supported constraints and remaining gaps; do not repeat Task text or add status. A gap does not erase the representable part of a requirement.",
        "operation_reference": "An operation target names an existing instruction_id and complete operation_path using string keys and integer indexes. Use one operation_demands record per operation. input(index) in an operation demand selects that operation's consumed slot; output selects its output; action/self selects the action. On call, output means response and input/self means request. Constraint phase may be request or response only on call and defaults to request.",
        "target_forms": 'CFG targets are {"instruction_id":"ir_id","path":[]} or {"instruction_id":"ir_id","side":"input","index":0}; a block target uses block_id and path, and graph uses path alone. Do not mix these forms. Action/constraint events must select a real instruction or atomic operation, not a block, prose constraint or its arbitrary field path.',
        "constraint_expression": "A constraint condition/success references one existing normalized Boolean expression from processing, not arbitrary IR text, an operation without expression, or prose. Do not invent an expression or implicit truth conversion. Element-scoped references remain in that exact existing member scope.",
        "constraint_selectors": "Constraint event lists are distinct and cannot contain both an instruction and its child operations. Instruction events use path=[]; operation events use slot=self. Receiver location IDs are distinct and exist. at_most supplies success exactly when unit=success; unit=attempt omits it. Element scope names its existing for_each and cannot refer to another member scope.",
        "demand_paths": "value, presence, cardinality, shape, truth and action preserve different properties. Cardinality does not require all member contents; whole acquisition does not imply whole necessity. Field/index prefixes and each select actual nested members (rows -> each -> keys); repeated each selects corresponding nested collection levels, never a literal '*' field. Preserve scope and recipient. Do not move a selector, add processing or widen to whole content to bypass an unsupported relation.",
        "demand_evidence": "Use actual source evidence for requirements/gaps. expected names a supported original-value relation, not a transformation, conditional computation or substitute for a real operation. Different receivers need their own supported demands; a shared requirement ID does not copy necessity across sinks.",
    },
    "sensitivity": {
        "sensitivity_scope": "instruction_id must name modeled processing. scope_path is [] or [segments,index] selecting its existing for_each. case_path, when present, selects an exact existing [segments,index,cases,index] or [segments,index,body,index,cases,index] and stays in scope_path. Use that candidate's authored local name; private compiled names are generated.",
        "sensitivity_value": "Use existing input/local values with valid indexes and lexical scope. Do not refer to an unmodeled IR, another occurrence or a missing case local. Duplicate declarations in the same scope are invalid. Sensitive field/member ranges label the actual selected value, not every dependency or recipient.",
        "evidence_inheritance": flat.PROCESSING_RULES["evidence_inheritance"],
        "sensitivity_ownership": "Declare only sensitivity and its source support. Do not change processing, Task or demands. Possible/derived influence is not evidence of plaintext containment; no declaration does not prove nonsensitivity.",
    },
}


def fragment_contract_rules(kind):
    """Render only this owner phase's cross-field rules, alongside its real schema."""
    return "APPLICATION RULES (not response fields)\n" + "\n".join(
        f"- {name}: {description}" for name, description in FRAGMENT_RULES[_kind(kind)].items())


def _without_demands(base):
    return create_model("Processing" + base.__name__, __base__=StrictSpec,
        **{key: (item.annotation, deepcopy(item)) for key, item in base.model_fields.items() if key != "demands"})


ProcessingOp = Annotated[Union[tuple(
    [_without_demands(cls) for cls in [*flat._OPS, flat.FlatCall]])], Field(discriminator="op")]


class ProcessingSegment(StrictSpec):
    mode: Literal["default", "local", "model"] = "default"
    ops: list[ProcessingOp] = Field(default_factory=list)
    returns: list[ValueRef] = Field(default_factory=list)
    evidences: list[flat.WireEvidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def explicit_returns(self):
        return flat.FlatProcessing.explicit_returns(self)


class ProcessingCase(flat.FlatCase):
    segments: list[ProcessingSegment] = Field(default_factory=list,
        description="Actual additional processing only; [] is valid for a candidate that yields an existing value.")


class ProcessingCases(flat.FlatCaseSummary):
    cases: list[ProcessingCase] = Field(min_length=1)


ProcessingBodySegment = Annotated[Union[
    Annotated[ProcessingSegment, Tag("processing")],
    Annotated[ProcessingCases, Tag("cases")]], Discriminator(flat.segment_kind)]


class ProcessingForEach(StrictSpec):
    kind: Literal["for_each"]
    collection: ValueRef
    item: Text
    body: list[ProcessingBodySegment] = Field(min_length=1)
    yield_value: ValueRef | None = Field(default=None, alias="yield")
    output: Text | None = None
    evidences: list[flat.WireEvidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def paired_result(self):
        return flat.FlatForEach.paired_result(self)


ProcessingTopSegment = Annotated[Union[
    Annotated[ProcessingSegment, Tag("processing")],
    Annotated[ProcessingForEach, Tag("for_each")],
    Annotated[ProcessingCases, Tag("cases")]], Discriminator(flat.segment_kind)]


class ProcessingIR(StrictSpec):
    order: Literal["fixed", "partial"] = "fixed"
    evidences: flat.WireEvidences
    segments: list[ProcessingTopSegment] = Field(default_factory=list)
    output_bindings: list[flat.FlatBinding] = Field(default_factory=list)

class ProcessingFragment(StrictSpec):
    ir_semantics: dict[Text, ProcessingIR]
    locations: dict[Text, flat.FlatLocation] = Field(default_factory=dict)
    expressions: list[flat.FlatSupplement] = Field(default_factory=list)
    processing_gaps: list[flat.FlatProcessingGap] = Field(default_factory=list)


class OperationDemands(StrictSpec):
    instruction_id: Text
    operation_path: list[str | Annotated[int, Field(strict=True, ge=0)]]
    demands: list[OperationTaskGoal] = Field(min_length=1)


class CorrespondenceFragment(StrictSpec):
    realizations: list[flat.FlatRealization]
    demands: list[RawDemandGoal] = Field(default_factory=list)
    operation_demands: list[OperationDemands] = Field(default_factory=list)


class ScopedSensitivity(flat.FlatSensitivity):
    instruction_id: Text
    scope_path: list[str | Annotated[int, Field(strict=True, ge=0)]] = Field(default_factory=list)
    case_path: list[str | Annotated[int, Field(strict=True, ge=0)]] | None = None
    evidences: list[flat._WIRE_EVIDENCE_TYPES[0]] = Field(default_factory=list)

    @model_validator(mode="after")
    def scope_shape(self):
        if self.scope_path and not (len(self.scope_path) == 2 and self.scope_path[0] == "segments" and type(self.scope_path[1]) is int):
            raise ValueError("sensitivity scope is the IR or one existing for_each segment")
        if self.case_path is not None:
            path = self.case_path
            if not (path[::2] in (["segments", "cases"], ["segments", "body", "cases"])
                    and len(path) % 2 == 0 and all(type(index) is int for index in path[1::2])):
                raise ValueError("case_path must select one exact case in the IR or current for_each scope")
            if bool(self.scope_path) != (len(path) == 6) or self.scope_path and path[:2] != self.scope_path:
                raise ValueError("case_path must remain inside the declaration's exact lexical scope")
        return self


class SensitivityFragment(StrictSpec):
    declarations: list[ScopedSensitivity] = Field(default_factory=list)


_MODELS = {"processing": ProcessingFragment, "task-correspondence": CorrespondenceFragment,
           "sensitivity": SensitivityFragment}


def _kind(kind):
    return "task-correspondence" if kind == "mapping" else kind


def fragment_adapter(kind):
    return TypeAdapter(_MODELS[_kind(kind)])


def _parse(kind, raw, processing=None, *, diagnostics=None):
    try:
        value = _json_object(raw)
    except (ValueError, TypeError) as error:
        raise structural_error("json_format", "", str(error)) from error
    found = flat.format_diagnostics(value)
    if kind == "sensitivity" and processing is not None and isinstance(value.get("declarations"), list):
        for i, record in enumerate(value["declarations"]):
            if isinstance(record, dict) and isinstance(record.get("instruction_id"), str):
                try:
                    _sensitivity_evidence(record, processing, i)
                except StructuralValidationError as error:
                    found.extend(error.diagnostics)
    try:
        fragment_adapter(kind).validate_python(value)
    except ValidationError as error:
        found.extend(schema_error(error, candidate=value, schema=fragment_adapter(kind).json_schema()).diagnostics)
    if diagnostics is not None:
        diagnostics.extend(found)
    elif found:
        raise StructuralValidationError(found)
    return deepcopy(value)


def _checkable_records(kind, value, *, unavailable=()):
    """Diagnostic-only projection; it is never returned as an accepted answer.

    A malformed sibling must not prevent reference checks on a complete typed
    record. The original indexes are retained for every reported diagnostic.
    No record is repaired, and no semantic default is copied into the answer.
    """
    models = {
        "processing": {"ir_semantics": ProcessingIR, "locations": flat.FlatLocation,
            "expressions": flat.FlatSupplement, "processing_gaps": flat.FlatProcessingGap},
        "task-correspondence": {"realizations": flat.FlatRealization,
            "demands": RawDemandGoal, "operation_demands": OperationDemands},
        "sensitivity": {"declarations": ScopedSensitivity},
    }[kind]
    projected, origins = {}, {}
    for field_name, model in models.items():
        is_mapping = field_name in {"ir_semantics", "locations"}
        values = value.get(field_name)
        projected[field_name] = {} if is_mapping else []
        if not isinstance(values, dict if is_mapping else list):
            continue
        for key, record in (values.items() if is_mapping else enumerate(values)):
            pointer = json_pointer(field_name, key)
            if any(row["path"] == pointer or row["path"].startswith(pointer + "/") for row in unavailable):
                continue
            try:
                if is_mapping:
                    TypeAdapter(Text).validate_python(key)
                model.model_validate(record)
            except ValidationError:
                continue
            new_key = key if is_mapping else len(projected[field_name])
            if is_mapping:
                projected[field_name][key] = deepcopy(record)
            else:
                projected[field_name].append(deepcopy(record))
            origins[json_pointer(field_name, new_key)] = json_pointer(field_name, key)
    return projected, origins


def _reindex_diagnostics(rows, origins):
    result = []
    for diagnostic in rows:
        row = deepcopy(diagnostic)
        for prefix in sorted(origins, key=len, reverse=True):
            if row["path"] == prefix or row["path"].startswith(prefix + "/"):
                row["path"] = origins[prefix] + row["path"][len(prefix):]
                break
        result.append(row)
    return result


def _fragment_error(kind, value, diagnostics):
    """Attach stable owner/record/current-value context without rewriting input."""
    from skillflow.common.recording import canonical_sha256
    records, seen, rows = _records(kind, value), set(), []
    for diagnostic in diagnostics:
        row = deepcopy(diagnostic)
        context = row.setdefault("context", {})
        context.setdefault("fragment", kind)
        for pointer in sorted(records, key=len, reverse=True):
            if row["path"] == pointer or row["path"].startswith(pointer + "/"):
                context.setdefault("record_id", pointer)
                break
        if "current" not in context and row["path"]:
            try:
                current = resolve_pointer(value, row["path"])
            except (KeyError, IndexError, TypeError, ValueError):
                context.setdefault("present", False)
            else:
                context.setdefault("present", True)
                if current is None or isinstance(current, (bool, int, float)) or isinstance(current, str) and len(current) <= 200:
                    context["current"] = current
                else:
                    context.setdefault("current_type", type(current).__name__)
                    if isinstance(current, (dict, list, str)):
                        context.setdefault("current_length", len(current))
        identity = canonical_sha256(row)
        if identity not in seen:
            rows.append(row)
            seen.add(identity)
    return StructuralValidationError(rows)


def _base_wire(processing):
    return {"outcome": "completed", "realizations": [], "demands": [],
            **deepcopy(processing)}


def _operation(processing, instruction, path):
    pointer = json_pointer("ir_semantics", instruction, *path)
    allowed = (path[::2] in (["segments", "ops"], ["segments", "body", "ops"],
        ["segments", "cases", "segments", "ops"], ["segments", "body", "cases", "segments", "ops"])
        and len(path) % 2 == 0 and all(type(index) is int and index >= 0 for index in path[1::2]))
    try:
        value = resolve_pointer(processing, pointer) if allowed else None
    except (KeyError, IndexError, ValueError, TypeError):
        value = None
    if not isinstance(value, dict) or "op" not in value:
        raise structural_error("operation_reference", "", "operation target must address an existing processing operation",
                               target=pointer)
    return value


def _sensitivity_evidence(record, processing, index):
    if record.get("evidences"):
        return deepcopy(record["evidences"])
    scope = record.get("case_path") or record.get("scope_path", [])
    path = ["ir_semantics", record["instruction_id"], *(scope if isinstance(scope, list) else [])]
    sources, _ = flat.nearest_source_evidence(processing, path)
    if sources:
        return sources
    raise structural_error("evidence_kind", f"/declarations/{index}/evidences",
        "sensitivity needs explicit source evidence or an existing source citation at its processing scope",
        inherited_from=json_pointer("ir_semantics", record["instruction_id"], *record.get("scope_path", []), "evidences"))


def _wire(processing, correspondence, sensitivity):
    wire = _base_wire(processing)
    wire["realizations"] = deepcopy(correspondence.get("realizations", []))
    wire["demands"] = deepcopy(correspondence.get("demands", []))
    origins = {"/ir_semantics": {"fragment": "processing", "path": "/ir_semantics"},
               "/locations": {"fragment": "processing", "path": "/locations"},
               "/processing_gaps": {"fragment": "processing", "path": "/processing_gaps"},
               "/expressions": {"fragment": "processing", "path": "/expressions"},
               "/realizations": {"fragment": "task-correspondence", "path": "/realizations"},
               "/demands": {"fragment": "task-correspondence", "path": "/demands"}}
    # Empty program-owned containers locate omitted declarations for review;
    # they are neither model-written pass records nor nonsensitivity claims.
    for ir, spec in wire["ir_semantics"].items():
        scopes = [(spec, [])] + [(segment, ["segments", i])
            for i, segment in enumerate(spec.get("segments", [])) if segment.get("kind") == "for_each"]
        for scope, path in scopes:
            scope.setdefault("sensitivity", [])
            origins[json_pointer("ir_semantics", ir, *path, "sensitivity")] = {
                "fragment": "sensitivity", "path": "/declarations"}
    seen = set()
    for i, record in enumerate(correspondence.get("operation_demands", [])):
        key = record["instruction_id"], tuple(record["operation_path"])
        if key in seen:
            raise structural_error("operation_demands_duplicate", f"/operation_demands/{i}", "use one demand record per existing operation")
        seen.add(key)
        try:
            operation = _operation(wire, record["instruction_id"], record["operation_path"])
        except StructuralValidationError as error:
            raise StructuralValidationError([{**row, "path": f"/operation_demands/{i}/operation_path"} for row in error.diagnostics]) from error
        operation["demands"] = deepcopy(record["demands"])
        pointer = json_pointer("ir_semantics", record["instruction_id"], *record["operation_path"], "demands")
        origins[pointer] = {"fragment": "task-correspondence", "path": f"/operation_demands/{i}/demands"}
    for i, record in enumerate(sensitivity.get("declarations", [])):
        pointer = json_pointer("ir_semantics", record["instruction_id"], *record.get("scope_path", []))
        try:
            scope = resolve_pointer(wire, pointer)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise structural_error("sensitivity_scope", f"/declarations/{i}/scope_path", "scope is absent from the supplied processing") from error
        if record.get("scope_path") and scope.get("kind") != "for_each":
            raise structural_error("sensitivity_scope", f"/declarations/{i}/scope_path", "member sensitivity requires an existing for_each")
        values = scope.setdefault("sensitivity", [])
        origins[pointer + f"/sensitivity/{len(values)}"] = {"fragment": "sensitivity", "path": f"/declarations/{i}"}
        values.append({**{key: deepcopy(value) for key, value in record.items() if key not in {"instruction_id", "scope_path"}},
                       "evidences": _sensitivity_evidence(record, processing, i)})
    return wire, origins


def _project_errors(error, origins, kind=None):
    rows = []
    for diagnostic in error.diagnostics:
        row = deepcopy(diagnostic)
        for prefix in sorted(origins, key=len, reverse=True):
            if row["path"] == prefix or row["path"].startswith(prefix + "/"):
                origin = origins[prefix]
                row["path"] = origin["path"] + row["path"][len(prefix):]
                row.setdefault("context", {})["fragment"] = origin["fragment"]
                break
        if kind is None or row.get("context", {}).get("fragment", kind) == kind:
            rows.append(row)
    return StructuralValidationError(rows or error.diagnostics)


def validate_fragment(kind, raw, material, processing=None, *, validation_gaps=()):
    """Return the submitted fragment; all normalization remains program owned."""
    return _validate_fragment(kind, raw, material, processing, validation_gaps=validation_gaps)[0]


def _validate_fragment(kind, raw, material, processing=None, *, validation_gaps=(), processing_expansion=None):
    """Share checked processing only within this validation/assembly operation."""
    kind, diagnostics = _kind(kind), []
    value = _parse(kind, raw, processing, diagnostics=diagnostics)
    if kind == "processing":
        if not diagnostics:
            try:
                processing_expansion = flat._processing_expansion(_base_wire(value), material,
                                                                 validation_gaps=validation_gaps)
            except StructuralValidationError as error:
                raise _fragment_error(kind, value, error.diagnostics) from error
            return value, processing_expansion
        projected, origins = _checkable_records(kind, value, unavailable=diagnostics)
        expected = set(cfg_instructions(material["cfg"]))
        from skillflow.propagation.contracts.limitations import validation_gap, unmodeled_ids
        unavailable = (expected - set(projected["ir_semantics"]) - unmodeled_ids(projected)
            - unmodeled_ids({"processing_gaps": validation_gaps}))
        # Diagnostic probes cannot publish OUT or an accepted annotation. These
        # temporary barriers let independent, typed IR records be checked.
        probe_gaps = [*validation_gaps, *(validation_gap(ir, [{"code": "record_diagnostic_only",
            "path": json_pointer("ir_semantics", ir), "message": "The unavailable sibling is excluded from this diagnostic-only check."}])
            for ir in sorted(unavailable))]
        try:
            flat.expand_processing(_base_wire(projected), material, validation_gaps=probe_gaps)
        except StructuralValidationError as error:
            diagnostics.extend(_reindex_diagnostics(error.diagnostics, origins))
        raise _fragment_error(kind, value, diagnostics)
    if processing is None:
        raise ValueError(kind + " requires the accepted processing fragment")
    # Never read or create a Task when validating processing or sensitivity.
    if processing_expansion is None:
        processing_expansion = flat._processing_expansion(_base_wire(processing), material,
                                                         validation_gaps=validation_gaps)
    _, backend, _, sensitivity_scopes = processing_expansion
    if kind == "task-correspondence":
        projected, record_origins = _checkable_records(kind, value)
        seen, operations = set(), []
        for index, record in enumerate(projected["operation_demands"]):
            prefix = record_origins[json_pointer("operation_demands", index)]
            try:
                _operation(processing, record["instruction_id"], record["operation_path"])
                identity = (record["instruction_id"], tuple(record["operation_path"]))
                if identity in seen:
                    raise structural_error("operation_demand_duplicate", "", "operation demand records must be merged")
                seen.add(identity)
            except StructuralValidationError as error:
                diagnostics.extend({**row, "path": prefix + ("/operation_path" if row["code"] == "operation_reference" else row["path"])}
                    for row in error.diagnostics)
            else:
                record_origins[json_pointer("operation_demands", len(operations))] = prefix
                operations.append(record)
        projected["operation_demands"] = operations
        wire, origins = _wire(processing, projected, {})
        try:
            flat._expand(wire, material, validation_gaps=validation_gaps)
        except StructuralValidationError as error:
            projected_errors = _project_errors(error, origins, kind)
            diagnostics.extend(_reindex_diagnostics(projected_errors.diagnostics, record_origins))
    else:
        from skillflow.propagation.contracts.sensitivity import _scope_definitions, validate_scope_sensitivity
        from skillflow.propagation.contracts.task import task_source_files
        instructions, files = cfg_instructions(material["cfg"]), task_source_files(material["source"])
        identities = set()
        records = value.get("declarations", [])
        for i, record in enumerate(records if isinstance(records, list) else []):
            try:
                ScopedSensitivity.model_validate(record)
            except ValidationError:
                # Already diagnosed by the whole-fragment schema. Check the
                # next independent record at its original coordinate.
                continue
            try:
                identity = (record["instruction_id"], tuple(record.get("scope_path", [])))
                scope = ["events", record["scope_path"][1]] if record.get("scope_path") else []
                if identity[0] not in backend["ir_semantics"]:
                    raise structural_error("sensitivity_scope", "/instruction_id", "sensitivity must refer to an existing modeled processing IR")
                declaration = {key: deepcopy(item) for key, item in record.items() if key not in {"instruction_id", "scope_path"}}
                if declaration.get("case_path") is None:
                    declaration.pop("case_path", None)
                declaration["evidences"] = _sensitivity_evidence(record, processing, i)
                for citation in declaration["evidences"]:
                    if citation.get("reason") is None:
                        citation["reason"] = flat._CITATION_NOTICE
                spec = processing["ir_semantics"][identity[0]]
                has_cases = any(segment.get("kind") == "cases" or any(
                    child.get("kind") == "cases" for child in segment.get("body", []))
                    for segment in spec.get("segments", []))
                if has_cases or record.get("case_path") is not None:
                    scope, declaration = flat._project_expanded_sensitivity(sensitivity_scopes, identity[0],
                        record.get("scope_path", []), declaration)
                definitions = _scope_definitions(backend["ir_semantics"][identity[0]], scope)
                validate_scope_sensitivity([declaration], instructions[identity[0]], definitions, files)
                from skillflow.common.recording import canonical_sha256
                key = (identity, canonical_sha256({k: v for k, v in declaration.items() if k != "evidences"}))
                if key in identities:
                    raise structural_error("sensitivity_duplicate", "", "duplicate sensitivity declaration in the same scope")
                identities.add(key)
            except StructuralValidationError as error:
                original_scope = json_pointer("ir_semantics", record["instruction_id"],
                    *record.get("scope_path", []), "sensitivity", 0)
                rows = _reindex_diagnostics(error.diagnostics, {original_scope: ""})
                diagnostics.extend({**row, "path": row["path"] if row["path"].startswith("/declarations/") else
                    f"/declarations/{i}" + (row["path"][2:] if row["path"].startswith("/0") else row["path"])} for row in rows)
            except ValidationError as error:
                invalid = schema_error(error, candidate=declaration,
                    schema=flat.SensitivityDeclaration.model_json_schema())
                diagnostics.extend({**row, "path": f"/declarations/{i}" + row["path"]}
                                   for row in invalid.diagnostics)
    if diagnostics:
        raise _fragment_error(kind, value, diagnostics)
    return value, processing_expansion


def assemble_fragments(processing, correspondence, sensitivity, material, *, validation_gaps=()):
    """Assemble once; neither downstream fragment can rewrite processing facts."""
    p, expanded = _validate_fragment("processing", processing, material, validation_gaps=validation_gaps)
    m, _ = _validate_fragment("task-correspondence", correspondence, material, processing=p,
                             validation_gaps=validation_gaps, processing_expansion=expanded)
    s, _ = _validate_fragment("sensitivity", sensitivity, material, processing=p,
                             validation_gaps=validation_gaps, processing_expansion=expanded)
    wire, origins = _wire(p, m, s)
    wire["_fragment_origins"] = origins
    if validation_gaps:
        wire["_validation_gaps"] = deepcopy(list(validation_gaps))
    try:
        wire, backend, compiled, mapping = flat.compile_flat_response(wire, material)
    except StructuralValidationError as error:
        raise _project_errors(error, origins) from error
    mapping["fragment_origins"] = {pointer: value["fragment"] for pointer, value in origins.items()}
    mapping["fragment_paths"] = origins
    mapping["processing_gaps"] = deepcopy(backend.get("processing_gaps", []))
    return wire, backend, compiled, mapping


def split_fragments(wire):
    """Mechanical fixture/projection helper; does not invent missing semantics."""
    p = {key: deepcopy(wire[key]) for key in ("ir_semantics", "locations", "expressions", "processing_gaps") if key in wire}
    m = {"realizations": deepcopy(wire["realizations"]), "demands": deepcopy(wire.get("demands", [])), "operation_demands": []}
    s = {"declarations": []}
    for ir, spec in p["ir_semantics"].items():
        def declarations(scope, path):
            for declaration in scope.pop("sensitivity", []):
                evidence = declaration.get("evidences") or [e for e in scope.get("evidences", spec.get("evidences", [])) if "file" in e]
                s["declarations"].append({**deepcopy(declaration), "instruction_id": ir, "scope_path": path, "evidences": deepcopy(evidence)})
        def operations(segment, path):
            if segment.get("kind") == "cases":
                for case_index, case in enumerate(segment["cases"]):
                    for segment_index, child in enumerate(case["segments"]):
                        operations(child, [*path, "cases", case_index, "segments", segment_index])
                return
            for i, op in enumerate(segment.get("ops", [])):
                goals = op.pop("demands", [])
                if goals:
                    m["operation_demands"].append({"instruction_id": ir, "operation_path": [*path, "ops", i], "demands": goals})
        declarations(spec, [])
        for i, segment in enumerate(spec.get("segments", [])):
            if segment.get("kind") == "for_each":
                declarations(segment, ["segments", i])
                for j, child in enumerate(segment["body"]):
                    operations(child, ["segments", i, "body", j])
            else:
                operations(segment, ["segments", i])
    return {"processing": p, "task-correspondence": m, "sensitivity": s}


def _records(kind, candidate):
    fields = {"processing": ("ir_semantics", "locations", "expressions", "processing_gaps"),
              "task-correspondence": ("realizations", "demands", "operation_demands"),
              "sensitivity": ("declarations",), "task": ("requirements", "issues"),
              "cfg": ("blocks", "edges"), "review": ("findings",)}[_kind(kind)]
    result = {}
    if isinstance(candidate, dict):
        for name in fields:
            values = candidate.get(name)
            if isinstance(values, (dict, list)):
                result.update({json_pointer(name, key): value for key, value in (values.items() if isinstance(values, dict) else enumerate(values))})
        for name in {"task": ("purpose",), "cfg": ("entry_block_ref",),
                     "review": ("outcome",)}.get(_kind(kind), ()):
            if name in candidate:
                result[json_pointer(name)] = candidate[name]
    return result


@dataclass
class FragmentCorrectionStrategy:
    kind: str
    identity: str = field(init=False)
    selected: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.kind = _kind(self.kind)
        self.identity = VERSION + ":" + self.kind + ":record-replacement-v1"

    def build_prompt(self, base_prompt, candidate, diagnostics):
        from skillflow.common.structural_correction import correction_base_prompt, correction_prompt
        from skillflow.common.prompt_format import compact_json
        if self.kind == "cfg" and any(row.get("code") == "binary_dispatch" for row in diagnostics):
            # Splitting a dispatch changes the block/edge set. Existing-slot
            # replacement cannot express it; use the existing whole correction
            # within the same one-correction budget, never a new patch grammar.
            self.selected = {}
            return correction_prompt(base_prompt, candidate, diagnostics)
        try:
            parsed = _json_object(candidate)
        except (ValueError, TypeError):
            self.selected = {}
            return correction_prompt(base_prompt, candidate, diagnostics)
        records = _records(self.kind, parsed)
        self.selected = {key: value for key, value in records.items() if any(
            row["path"] == key or row["path"].startswith(key + "/") for row in diagnostics)}
        if not self.selected or any(not any(row["path"] == key or row["path"].startswith(key + "/") for key in records) for row in diagnostics):
            self.selected = {}
            return correction_prompt(base_prompt, candidate, diagnostics)
        return correction_base_prompt(base_prompt) + "\nMECHANICAL RECORD CORRECTION\n" + (
            'Reply only {"replacements":[{"record_id":"<exact supplied record_id>","value":<one complete replacement record>}]}. '
            "Replace only supplied existing record_id slots. Do not add/delete records or return generic patches. "
            "The slot record_id stays unchanged; erroneous instruction_id/requirement_id references inside its value may be corrected. "
            "All corrected references, source evidence, coverage and ownership are validated again. "
            "The program reuses every unlisted record unchanged. Preserve source-supported relationships and do not guess semantic fixes.\n") + compact_json(
                {"records": self.selected, "diagnostics": diagnostics})

    def merge(self, candidate, correction):
        try:
            value = _json_object(correction)
        except (ValueError, TypeError) as error:
            raise structural_error("correction_json", "", str(error)) from error
        if not self.selected:
            return value
        if set(value) != {"replacements"} or not isinstance(value["replacements"], list):
            raise structural_error("record_replacement", "", "return only the requested existing-record replacements")
        try:
            result = deepcopy(_json_object(candidate))
        except (ValueError, TypeError) as error:
            raise structural_error("correction_candidate", "", str(error)) from error
        seen = set()
        for i, replacement in enumerate(value["replacements"]):
            if not isinstance(replacement, dict) or set(replacement) != {"record_id", "value"}:
                raise structural_error("record_replacement", f"/replacements/{i}", "record replacement requires record_id and a complete value")
            identity = replacement["record_id"]
            if not isinstance(identity, str) or identity not in self.selected or identity in seen:
                raise structural_error("record_identity", f"/replacements/{i}/record_id", "record_id must be one supplied existing identity, once")
            seen.add(identity)
            parent, token = identity.rsplit("/", 1)
            container = resolve_pointer(result, parent)
            key = int(token) if isinstance(container, list) else token.replace("~1", "/").replace("~0", "~")
            updated = replacement["value"]
            container[key] = deepcopy(updated)
        return result


def fragment_correction_strategy(kind):
    return FragmentCorrectionStrategy(_kind(kind))


def salvage_fragment(kind, raw, material, processing=None, *, validation_gaps=()):
    """Quarantine invalid whole records and retain explicit validation limits."""
    from skillflow.propagation.contracts.limitations import validation_gap
    kind = _kind(kind)
    try:
        value = _json_object(raw)
    except (ValueError, TypeError):
        return None, []
    if not _records(kind, value) or value.get("outcome") == "cannot_assess":
        return None, []
    value, gaps, upstream_gaps = deepcopy(value), [], deepcopy(list(validation_gaps))
    instructions = cfg_instructions(material["cfg"])
    requirements = {r["id"]: r for r in material.get("task", {}).get("requirements", [])}
    def task_gap(requirement):
        return {"requirement_id": requirement, "gaps": [{"reason": "A correspondence record failed deterministic validation; its unsupported preservation claim remains unresolved.",
                "evidences": deepcopy(requirements[requirement]["evidences"])}]}
    def add_gap(ir, diagnostics, unmodeled=True):
        if ir in instructions and not any(item["instruction_id"] == ir and item.get("origin") == "validation" for item in gaps):
            gap = validation_gap(ir, diagnostics, unmodeled=unmodeled)
            gaps.append(gap)
    for _ in range(len(_records(kind, value)) + len(instructions) + len(requirements) + 2):
        if kind == "processing":
            modeled = set(value.get("ir_semantics", {})) if isinstance(value.get("ir_semantics"), dict) else set()
            declared = {g.get("instruction_id") for g in (value.get("processing_gaps") or []) if isinstance(g, dict) and g.get("unmodeled")}
            for ir in sorted(set(instructions) - modeled - declared):
                add_gap(ir, [{"code": "missing_processing", "path": json_pointer("ir_semantics", ir), "message": "No validated processing record is available."}])
        if kind == "task-correspondence":
            rows = value.setdefault("realizations", [])
            if isinstance(rows, list):
                known = {r.get("requirement_id") for r in rows if isinstance(r, dict)}
                rows.extend(task_gap(req) for req in requirements if req not in known)
        try:
            validated = validate_fragment(kind, value, material, processing, validation_gaps=[*upstream_gaps, *gaps])
            if kind == "processing" and not validated.get("ir_semantics") and not validated.get("processing_gaps"):
                return None, []
            return validated, gaps
        except StructuralValidationError as error:
            records = _records(kind, value)
            invalid = {key for key in records if any(row["path"] == key or row["path"].startswith(key + "/") for row in error.diagnostics)}
            if not invalid:
                return None, gaps
            def position(pointer):
                parent, token = pointer.rsplit("/", 1)
                return (parent, int(token) if isinstance(value.get(parent[1:]), list) else token)
            for pointer in sorted(invalid, key=position, reverse=True):
                record = records[pointer]
                field_name, token = pointer[1:].split("/", 1)
                container = value[field_name]
                key = int(token) if isinstance(container, list) else token.replace("~1", "/").replace("~0", "~")
                if kind == "processing" and field_name == "ir_semantics":
                    add_gap(key, error.diagnostics)
                elif kind == "sensitivity":
                    ir = record.get("instruction_id") if isinstance(record, dict) else None
                    for target in [ir] if ir in instructions else instructions:
                        add_gap(target, error.diagnostics, unmodeled=False)
                elif kind == "task-correspondence" and isinstance(record, dict):
                    reqs = {record.get("requirement_id")} | {g.get("requirement_id") for g in (record.get("demands") or []) if isinstance(g, dict)}
                    for req in reqs & requirements.keys():
                        rows = value.get("realizations", [])
                        rows[:] = [task_gap(req) if r.get("requirement_id") == req else r for r in rows]
                del container[key]
    return None, gaps
