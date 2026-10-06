"""The sole evidence-free business handoff for subsequent DOE review.

This validates recorded facts and references, not task necessity or privacy.
Allocation identities and model-annotation evidence stay in the audit run.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from skillflow.propagation.data import Data
from skillflow.propagation.data import validate_data_records
from skillflow.propagation.data import validate_element_membership
from skillflow.propagation.data import is_definitely_empty_collection
from skillflow.common.inputs.skill_package import _classify_file
from skillflow.common.inputs.snapshot import _member_path
from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.common.recording import canonical_sha256
from skillflow.propagation.contracts.runtime_contract import execution_model_binding
from skillflow.propagation.contracts.runtime_contract import validate_execution_model_binding
from skillflow.graph.validation import checked_cfg
from skillflow.propagation.contracts.profiles import AnnotationPayload
from skillflow.propagation.contracts.profiles import Operator
from skillflow.propagation.contracts.profiles import Role
from skillflow.propagation.contracts.boundaries import SinkBoundary
from skillflow.propagation.contracts.boundaries import classify_sink
from skillflow.common.source_evidence import Digest
from skillflow.common.source_evidence import SourceBundle
from skillflow.common.source_evidence import Text
from skillflow.common.source_evidence import _checked_source
from skillflow.common.source_evidence import _json_object
from skillflow.common.source_evidence import source_units

from skillflow.propagation.models import FlowLocation
from skillflow.propagation.models import IRFlowRecord
from skillflow.propagation.models import ForEachRecord
from skillflow.propagation.contracts.compatibility import INTERACTION_EFFECTS
from skillflow.propagation.contracts.compatibility import validate_event_operations
from skillflow.propagation.contracts.compatibility import validate_operation_boundary
from skillflow.propagation.contracts.specs import LocationSpec
from skillflow.propagation.conditions import payload_inputs
from skillflow.propagation.conditions import validate_record_consumption
from skillflow.propagation.conditions import record_consumption_shape

SCHEMA_VERSION = "skillflow-doe-input-v7"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class _ExecutionModelBinding(_Strict):
    version: Text
    sha256: Digest


class _SourceIndex(_Strict):
    id: Text
    file: Text
    start_line: Annotated[int, Field(ge=1)]
    end_line: Annotated[int, Field(ge=1)]


class _InventoryEntry(_Strict):
    path: Text
    size: Annotated[int, Field(ge=0)]
    kind: Literal["markdown", "code", "text", "binary"]
    raw_sha256: Digest
    decoded_sha256: Digest | None


class _Boundaries(_Strict):
    binary_files: list[Text]
    uninterpreted_code_files: list[Text]
    notice: Text


class _Source(SourceBundle):
    index: list[_SourceIndex]
    inventory: list[_InventoryEntry]
    boundaries: _Boundaries


class _Action(_Strict):
    operator: list[Operator]
    roles: list[Role]

    @model_validator(mode="after")
    def unique(self):
        if len(set(self.operator)) != len(self.operator) or len(set(self.roles)) != len(self.roles):
            raise ValueError("action labels must not repeat")
        return self


Status = Literal["complete", "incomplete", "unsupported_feedback", "resource_limit", "execution_error"]
Coverage = Literal["processed", "not_reached", "not_solved", "unresolved_binding"]


class _OperationPosition(_Strict):
    instruction_id: Text
    event_index: Annotated[int, Field(ge=0)]
    op_index: Annotated[int, Field(ge=0)] | None = None
    body_event_index: Annotated[int, Field(ge=0)] | None = None
    scope: Literal["element"] | None = None

    @model_validator(mode="after")
    def position_kind(self):
        if (self.op_index is None) != (self.scope == "element"):
            raise ValueError("diagnostic position must identify an operation or element scope")
        return self


class _Unsupported(_Strict):
    code: Literal["unsupported_feedback"]
    reason: Text
    blocks: list[Text]
    operations: list[_OperationPosition]


class _UnresolvedBinding(_Strict):
    code: Literal["unresolved_binding"]
    reason: Text
    instruction_id: Text


class _Failure(_Strict):
    code: Literal["resource_limit", "execution_error"]
    reason: Text


class _MissingPart(_OperationPosition):
    code: Literal["missing_part"]
    reason: Text
    data_id: Text


Diagnostic = Annotated[_Unsupported | _UnresolvedBinding | _Failure | _MissingPart,
                       Field(discriminator="code")]


class _Handoff(_Strict):
    schema_version: Literal["skillflow-doe-input-v7"]
    execution_model: _ExecutionModelBinding
    source: _Source
    cfg: dict
    locations: dict[Text, LocationSpec]
    sink_boundaries: list[SinkBoundary]
    actions: dict[Text, _Action]
    data: list[Data]
    records: dict[Text, IRFlowRecord]
    status: Status
    coverage: dict[Text, Coverage]
    diagnostics: list[Diagnostic]


def _validate_source(raw: dict) -> dict:
    parsed = _Source.model_validate(raw).model_dump(mode="json")
    source = _checked_source({key: parsed[key] for key in ("files", "source_sha256")})
    expected_index = [{key: unit[key] for key in ("id", "file", "start_line", "end_line")}
                      for unit in source_units(source)]
    if parsed["index"] != expected_index:
        raise ValueError("source index differs from the complete readable source")
    inventory = parsed["inventory"]
    paths = [_member_path(item["path"]) for item in inventory]
    if len(set(path.casefold() for path in paths)) != len(paths):
        raise ValueError("source inventory contains duplicate package paths")
    readable = {item["path"]: item for item in source["files"]}
    if set(readable) != {item["path"] for item in inventory if item["decoded_sha256"] is not None}:
        raise ValueError("source inventory must cover every readable file exactly")
    for item in inventory:
        if (item["kind"] == "binary") != (item["decoded_sha256"] is None):
            raise ValueError("binary inventory must not claim decoded text")
        if item["decoded_sha256"] is None:
            continue
        file = readable[item["path"]]
        if item["decoded_sha256"] != file["sha256"]:
            raise ValueError("source inventory decoded hash differs from source text")
        encoded = file["content"].encode("utf-8")
        candidates = (encoded, b"\xef\xbb\xbf" + encoded)
        if not any(len(value) == item["size"] and hashlib.sha256(value).hexdigest() == item["raw_sha256"]
                   and _classify_file(item["path"], value) == (item["kind"], file["content"]) for value in candidates):
            raise ValueError("readable inventory bytes/type differ from UTF-8 source text")
    boundary = parsed["boundaries"]
    if (boundary["binary_files"] != [item["path"] for item in inventory if item["decoded_sha256"] is None]
            or boundary["uninterpreted_code_files"] != [item["path"] for item in inventory if item["kind"] == "code"]):
        raise ValueError("source boundary inventory differs from package inventory")
    return parsed


def build_doe_source(source: dict, source_metadata: dict) -> dict:
    """Preserve readable text plus the explicitly supplied package inventory."""
    checked = _checked_source(source)
    if "source_sha256" in source_metadata and source_metadata["source_sha256"] != checked["source_sha256"]:
        raise ValueError("source metadata refers to a different readable bundle")
    return _validate_source({**checked,
        "index": [{key: unit[key] for key in ("id", "file", "start_line", "end_line")}
                  for unit in source_units(checked)],
        "inventory": deepcopy(source_metadata["files"]),
        "boundaries": deepcopy(source_metadata["boundaries"]),
    })


def _instructions(cfg):
    return {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}


def _normalized_cfg(cfg):
    return json.loads(ControlFlowGraph.model_validate_json(json.dumps(cfg)).to_json())


def _reachable_instructions(cfg):
    incoming = {block: 0 for block in cfg["blocks"]}
    successors = {block: set() for block in cfg["blocks"]}
    for edge in cfg["edges"]:
        incoming[edge["target_block_id"]] += 1
        successors[edge["source_block_id"]].add(edge["target_block_id"])
    pending = [cfg["entry_block_id"], *(block for block, count in incoming.items() if count == 0)]
    visited = set()
    while pending:
        block = pending.pop()
        if block not in visited:
            visited.add(block)
            pending.extend(successors[block])
    return {ir["id"] for block in visited for ir in cfg["blocks"][block]["instructions"]}


def _validate_locations(locations, instructions):
    identities = set()
    for location in locations.values():
        identity = location.kind, location.name
        if identity in identities:
            raise ValueError("duplicate location identity")
        identities.add(identity)
        for ref in location.operand_refs:
            if (ref.instruction_id not in instructions
                    or ref.index >= len(instructions[ref.instruction_id][ref.side + "s"])):
                raise ValueError("location operand reference is outside the selected CFG")
    return identities


def _validate_records(records, instructions, data, declared):
    ids = {item.id for item in data}
    result_names = {operand["identifier"] for ir in instructions.values() for operand in ir["outputs"]}

    def data_refs(values):
        if not set(values) <= ids:
            raise ValueError("propagation record contains dangling Data references")

    def location(value):
        if value.kind == "result" and value.name not in result_names:
            raise ValueError("result location does not occur in the selected CFG")

    for ir_id, record in records.items():
        if any(record.exit_state.get(FlowLocation(kind="result", name=operand["identifier"])) is None
               for operand in instructions[ir_id]["outputs"]):
            raise ValueError("processed IR is missing a public output binding in its exit state")
        for state in (record.entry_state, record.exit_state):
            for binding in state.bindings:
                location(binding.location)
                data_refs(binding.data_ids)
        def effect_events():
            for event in record.events:
                if isinstance(event, ForEachRecord):
                    data_refs(event.collections)
                    for collection in event.collections:
                        if not any(instance.collection == collection for instance in event.instances) and not is_definitely_empty_collection(data, collection):
                            raise ValueError("for_each cannot discard members of an unknown or nonempty collection")
                    body_shape = None
                    for instance in event.instances:
                        shape = [(child.effect, [(record_consumption_shape(op), len(op.outputs),
                            [(endpoint.kind, endpoint.name) for endpoint in op.endpoints])
                            for op in child.atomic_ops]) for child in instance.body]
                        if body_shape is not None and shape != body_shape:
                            raise ValueError("for_each candidates must retain the same operation and boundary template")
                        body_shape = shape
                        if instance.collection not in event.collections:
                            raise ValueError("for_each instance collection is outside resolved candidates")
                        data_refs([instance.collection, instance.element])
                        validate_element_membership(data, instance.collection, instance.element)
                        for child in instance.body:
                            if any(op.op in {"read", "receive", "write"} for op in child.atomic_ops):
                                raise ValueError("for_each cannot contain shared-state interactions")
                            yield child
                else:
                    yield event

        for event in effect_events():
            validate_event_operations(event.effect, [op.op for op in event.atomic_ops])
            for op in event.atomic_ops:
                validate_record_consumption(op, data=data)
                if op.when_input_index is not None and event.effect != "model_observe":
                    raise ValueError("conditional delivery must be a compiled model observation")
                if len(op.outputs) != int(op.op not in {"deliver", "write"}):
                    raise ValueError("recorded atomic output arity differs from the operation")
                if ((op.op == "read" and op.inputs)
                        or (op.op == "write" and len(op.inputs) > 1)
                        or (op.op in {"select_part", "exclude_parts", "filter_items"} and len(op.inputs) != 1)
                        or (op.op == "update_fields" and len(op.inputs) < 2)):
                    raise ValueError("recorded atomic input arity differs from the operation")
                for binding in [*op.inputs, *op.outputs]:
                    data_refs(binding)
                if len(op.endpoints) != int(op.op in INTERACTION_EFFECTS):
                    raise ValueError("recorded interaction endpoint arity differs")
                validate_operation_boundary(op.op, event.effect, op.endpoints[0].kind if op.endpoints else None,
                                            input_count=(None if op.when_input_index is not None and not payload_inputs(op)
                                                         else len(payload_inputs(op))))
                for endpoint in op.endpoints:
                    if (endpoint.kind, endpoint.name) not in declared:
                        raise ValueError("recorded endpoint has no location declaration")
                if bool(op.changes) != (op.op == "write"):
                    raise ValueError("only write records contain state changes")
                for change in op.changes:
                    location(change.location)
                    data_refs(change.before)
                    data_refs(change.after)
                    if (change.location.kind, change.location.name) not in declared:
                        raise ValueError("changed location has no declaration")
                    if change.location.kind != op.endpoints[0].kind:
                        raise ValueError("write changed an incompatible boundary kind")
                    if change.update == "delete" and (change.after or op.inputs):
                        raise ValueError("exact deletion must have no after binding or content input")
                    if change.update == "weak" and not change.before <= change.after:
                        raise ValueError("weak update cannot remove prior candidates")


def resolved_sink_boundaries(locations, records) -> list[dict]:
    """Derive only boundaries whose operations have actual static records.

    Each coordinate identifies the existing operation, not a duplicate payload.
    Member instances share a template coordinate; their paired data remain in
    the original for_each records. Unsolved IRs and empty member scopes are not
    disguised as evaluated operations. Full-run loading also compares these
    coordinates against the complete compiled annotation inventory.
    """
    locations = {key: LocationSpec.model_validate(value) for key, value in locations.items()}
    by_identity = {(value.kind, value.name): key for key, value in locations.items()}
    if len(by_identity) != len(locations):
        raise ValueError("duplicate location identity")
    found = {}

    def collect(ir_id, event_index, event, body_index=None):
        for op_index, op in enumerate(event.atomic_ops):
            if op.op not in {"deliver", "write"}:
                continue
            # A false conditional observation retains its control input for
            # audit, but has no observed payload and is not a sink occurrence.
            if op.when_input_index is not None and not payload_inputs(op):
                continue
            if len(op.endpoints) != 1:
                raise ValueError("sink operation must retain its single boundary")
            endpoint = op.endpoints[0]
            target = by_identity.get((endpoint.kind, endpoint.name))
            if target is None:
                raise ValueError("sink operation has no location declaration")
            selected = classify_sink(op.op, event.effect, locations[target],
                                     write_mode=("replace" if op.inputs else "delete") if op.op == "write" else None)
            if selected is None:
                continue
            sink_type, level = selected
            item = SinkBoundary(instruction_id=ir_id, event_index=event_index,
                                op_index=op_index, body_event_index=body_index,
                                scope="element" if body_index is not None else None,
                                target=target, sink_type=sink_type, exposure_level=level)
            key = (ir_id, event_index, body_index, op_index)
            if key in found and found[key] != item:
                raise ValueError("member candidates disagree on a sink operation boundary")
            found[key] = item

    for ir_id in sorted(records):
        record = IRFlowRecord.model_validate(records[ir_id])
        for event_index, event in enumerate(record.events):
            if isinstance(event, ForEachRecord):
                for instance in event.instances:
                    for body_index, child in enumerate(instance.body):
                        collect(ir_id, event_index, child, body_index)
            else:
                collect(ir_id, event_index, event)
    return [found[key].model_dump(mode="json") for key in sorted(
        found, key=lambda key: (key[0], key[1], -1 if key[2] is None else key[2], key[3]))]


def _validate_diagnostics(diagnostics, instructions, blocks, data_ids, records):
    # Local shape is checked by the diagnostic union; these are cross-references.
    for item in diagnostics:
        if "instruction_id" in item and item["instruction_id"] not in instructions:
            raise ValueError("diagnostic refers to an unknown IR")
        if "data_id" in item and item["data_id"] not in data_ids:
            raise ValueError("diagnostic refers to unknown Data")
        if item["code"] == "missing_part" and item["instruction_id"] in records:
            events = records[item["instruction_id"]].events
            if item["event_index"] >= len(events):
                raise ValueError("missing-part diagnostic event is outside record")
            event = events[item["event_index"]]
            body_index = item.get("body_event_index")
            if isinstance(event, ForEachRecord):
                candidates = [instance.body[body_index] for instance in event.instances
                              if body_index is not None and body_index < len(instance.body)]
            else:
                candidates = [event] if body_index is None else []
            if not candidates or not all(item["op_index"] is not None
                    and item["op_index"] < len(candidate.atomic_ops)
                    and candidate.atomic_ops[item["op_index"]].op == "select_part" for candidate in candidates):
                raise ValueError("missing-part diagnostic does not point to a recorded selection")
        if "blocks" in item and any(block not in blocks for block in item["blocks"]):
            raise ValueError("diagnostic refers to an unknown block")
        if any(position["instruction_id"] not in instructions for position in item.get("operations", [])):
            raise ValueError("diagnostic operation refers to unknown IR")



def validate_doe_input(raw) -> dict:
    """Validate a standalone business file without allocation/audit metadata."""
    parsed = _Handoff.model_validate(_json_object(raw))
    result = parsed.model_dump(mode="json")
    # Optional nested coordinates are absent outside an element scope.
    for diagnostic in result["diagnostics"]:
        for position in [diagnostic, *diagnostic.get("operations", [])]:
            for key in ("body_event_index", "scope"):
                if position.get(key) is None:
                    position.pop(key, None)
    validate_execution_model_binding(result["execution_model"])
    result["source"] = _validate_source(result["source"])
    result["cfg"] = checked_cfg(result["cfg"])
    result["data"] = validate_data_records(parsed.data)
    normalized_cfg = _normalized_cfg(result["cfg"])
    instructions = _instructions(normalized_cfg)
    expected = set(instructions)
    if set(parsed.actions) != expected or set(parsed.coverage) != expected:
        raise ValueError("actions and coverage must cover all real IRs exactly")
    if set(parsed.records) - expected:
        raise ValueError("propagation record refers to an unknown IR")
    processed = {ir for ir, state in parsed.coverage.items() if state == "processed"}
    if set(parsed.records) != processed:
        raise ValueError("records must match processed coverage exactly")
    reachable = _reachable_instructions(normalized_cfg)
    if any(ir not in reachable and state != "not_reached" for ir, state in parsed.coverage.items()):
        raise ValueError("coverage reachability differs from the selected CFG")
    if parsed.status == "complete" and processed != reachable:
        raise ValueError("complete propagation must process every reachable IR")
    if parsed.status == "unsupported_feedback" and processed:
        raise ValueError("unsupported feedback must not claim solved records")
    declared = _validate_locations(parsed.locations, instructions)
    _validate_records(parsed.records, instructions, parsed.data, declared)
    if result["sink_boundaries"] != resolved_sink_boundaries(parsed.locations, parsed.records):
        raise ValueError("sink boundaries differ from recorded operations, targets or fixed levels")
    _validate_diagnostics(result["diagnostics"], instructions, normalized_cfg["blocks"], {item.id for item in parsed.data}, parsed.records)
    diagnostic_codes = {item["code"] for item in result["diagnostics"]}
    if parsed.status == "complete" and diagnostic_codes - {"missing_part"}:
        raise ValueError("complete propagation contradicts a failure diagnostic")
    if parsed.status in {"unsupported_feedback", "resource_limit", "execution_error"} and parsed.status not in diagnostic_codes:
        raise ValueError("failed propagation status requires its recorded diagnostic")
    if parsed.status == "incomplete":
        missing = {ir for ir, state in parsed.coverage.items() if state == "unresolved_binding"}
        reported = {item["instruction_id"] for item in result["diagnostics"] if item["code"] == "unresolved_binding"}
        if not missing or missing != reported:
            raise ValueError("incomplete coverage and unresolved binding diagnostics must agree")
    return result


def build_doe_input(source, cfg, annotation, solved, *, source_metadata, execution_model) -> dict:
    """Bind the actual contract without copying allocation identities or evidence."""
    payload = AnnotationPayload.model_validate(
        annotation.model_dump(mode="json") if hasattr(annotation, "model_dump") else annotation)
    solved.records.validate()
    identity = solved.records.to_dict()
    graph = checked_cfg(cfg)
    normalized_graph = _normalized_cfg(graph)
    if (canonical_sha256(normalized_graph) != identity["cfg_sha256"]
            or canonical_sha256(payload.model_dump(mode="json")) != identity["annotation_sha256"]
            or canonical_sha256(solved.registry.to_dict()) != identity["data_sha256"]):
        raise ValueError("solved records do not match the supplied graph, annotation or Data registry")
    sinks = resolved_sink_boundaries(payload.locations, solved.records.records_dict())
    compiled_sinks = [item.model_dump(mode="json") for item in payload.sink_boundaries]
    if any(item not in compiled_sinks for item in sinks):
        raise ValueError("recorded sink boundary is absent from the compiled annotation")
    return validate_doe_input({
        "schema_version": SCHEMA_VERSION,
        "execution_model": execution_model_binding(execution_model),
        "source": build_doe_source(source, source_metadata), "cfg": graph,
        "locations": {key: value.model_dump(mode="json") for key, value in payload.locations.items()},
        "sink_boundaries": sinks,
        "actions": {key: {"operator": list(value.operator), "roles": list(value.roles)}
                    for key, value in payload.profiles.items()},
        "data": [entry["data"] for entry in solved.registry.to_dict()["records"]],
        "records": solved.records.records_dict(), "status": solved.status,
        "coverage": deepcopy(solved.coverage),
        "diagnostics": deepcopy(solved.diagnostics),
    })


def load_doe_input(path: str | Path) -> dict:
    """Load only the specified business JSON; never require adjacent files."""
    return validate_doe_input(Path(path).read_text(encoding="utf-8"))
