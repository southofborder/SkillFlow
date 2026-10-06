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

from skill_ir.data import Data, validate_data_records
from skill_ir.inputs.skill_package import _classify_file
from skill_ir.inputs.snapshot import _member_path
from skill_ir.ir.cfg import ControlFlowGraph
from skill_ir.recording import canonical_sha256
from skill_ir.security_profile.evidence import checked_cfg
from skill_ir.security_profile.models import AnnotationPayload, Operator, Role, Unresolved
from skill_ir.source_evidence import (
    Digest, SourceBundle, Text, _checked_source, _json_object, source_units,
)

from .models import FlowLocation, IRFlowRecord
from .compatibility import INTERACTION_EFFECTS, validate_event_operations, validate_operation_boundary
from .specs import LocationSpec

SCHEMA_VERSION = "skillflow-doe-input-v2"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


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
    op_index: Annotated[int, Field(ge=0)]


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


class _AnnotationUnresolved(_Strict):
    code: Literal["annotation_unresolved"]
    reason: Text
    items: Annotated[list[Unresolved], Field(min_length=1)]


class _MissingPart(_OperationPosition):
    code: Literal["missing_part"]
    reason: Text
    data_id: Text


Diagnostic = Annotated[_Unsupported | _UnresolvedBinding | _Failure | _AnnotationUnresolved | _MissingPart,
                       Field(discriminator="code")]


class _Handoff(_Strict):
    schema_version: Literal["skillflow-doe-input-v2"]
    source: _Source
    cfg: dict
    locations: dict[Text, LocationSpec]
    actions: dict[Text, _Action]
    data: list[Data]
    records: dict[Text, IRFlowRecord]
    status: Status
    coverage: dict[Text, Coverage]
    unresolved: list[Unresolved]
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


def _validate_records(records, instructions, ids, declared):
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
        for event in record.events:
            validate_event_operations(event.effect, [op.op for op in event.atomic_ops])
            for op in event.atomic_ops:
                if len(op.outputs) != int(op.op not in {"deliver", "write"}):
                    raise ValueError("recorded atomic output arity differs from the operation")
                if ((op.op == "read" and op.inputs) or (op.op == "deliver" and not op.inputs)
                        or (op.op == "write" and len(op.inputs) > 1)
                        or (op.op in {"select_part", "exclude_parts"} and len(op.inputs) != 1)
                        or (op.op == "update_fields" and len(op.inputs) < 2)):
                    raise ValueError("recorded atomic input arity differs from the operation")
                for binding in [*op.inputs, *op.outputs]:
                    data_refs(binding)
                if len(op.endpoints) != int(op.op in INTERACTION_EFFECTS):
                    raise ValueError("recorded interaction endpoint arity differs")
                validate_operation_boundary(op.op, event.effect, op.endpoints[0].kind if op.endpoints else None)
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


def _validate_diagnostics(diagnostics, instructions, blocks, data_ids, records):
    # Local shape is checked by the diagnostic union; these are cross-references.
    for item in diagnostics:
        if "instruction_id" in item and item["instruction_id"] not in instructions:
            raise ValueError("diagnostic refers to an unknown IR")
        if "data_id" in item and item["data_id"] not in data_ids:
            raise ValueError("diagnostic refers to unknown Data")
        if item["code"] == "missing_part" and item["instruction_id"] in records:
            events = records[item["instruction_id"]].events
            if (item["event_index"] >= len(events)
                    or item["op_index"] >= len(events[item["event_index"]].atomic_ops)
                    or events[item["event_index"]].atomic_ops[item["op_index"]].op != "select_part"):
                raise ValueError("missing-part diagnostic does not point to a recorded selection")
        if "blocks" in item and any(block not in blocks for block in item["blocks"]):
            raise ValueError("diagnostic refers to an unknown block")
        if any(position["instruction_id"] not in instructions for position in item.get("operations", [])):
            raise ValueError("diagnostic operation refers to unknown IR")
        if any(unresolved["instruction_id"] not in instructions for unresolved in item.get("items", [])):
            raise ValueError("diagnostic unresolved IR does not exist")


def validate_doe_input(raw) -> dict:
    """Validate a standalone business file without allocation/audit metadata."""
    parsed = _Handoff.model_validate(_json_object(raw))
    result = parsed.model_dump(mode="json")
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
    fields = [(item.instruction_id, item.field) for item in parsed.unresolved]
    if any(ir not in expected for ir, _ in fields) or len(fields) != len(set(fields)):
        raise ValueError("unresolved must refer to unique real IR fields")
    declared = _validate_locations(parsed.locations, instructions)
    _validate_records(parsed.records, instructions, {item.id for item in parsed.data}, declared)
    _validate_diagnostics(result["diagnostics"], instructions, normalized_cfg["blocks"], {item.id for item in parsed.data}, parsed.records)
    diagnostic_codes = {item["code"] for item in result["diagnostics"]}
    if parsed.status == "complete" and diagnostic_codes - {"missing_part", "annotation_unresolved"}:
        raise ValueError("complete propagation contradicts a failure diagnostic")
    if parsed.status in {"unsupported_feedback", "resource_limit", "execution_error"} and parsed.status not in diagnostic_codes:
        raise ValueError("failed propagation status requires its recorded diagnostic")
    if parsed.status == "incomplete":
        missing = {ir for ir, state in parsed.coverage.items() if state == "unresolved_binding"}
        reported = {item["instruction_id"] for item in result["diagnostics"] if item["code"] == "unresolved_binding"}
        if not missing or missing != reported:
            raise ValueError("incomplete coverage and unresolved binding diagnostics must agree")
    for diagnostic in result["diagnostics"]:
        if diagnostic["code"] == "annotation_unresolved" and diagnostic["items"] != result["unresolved"]:
            raise ValueError("annotation unresolved diagnostic differs from retained unresolved items")
    return result


def build_doe_input(source, cfg, annotation, solved, *, source_metadata) -> dict:
    """Project one solved run without copying identities, specs or evidence."""
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
    return validate_doe_input({
        "schema_version": SCHEMA_VERSION,
        "source": build_doe_source(source, source_metadata), "cfg": graph,
        "locations": {key: value.model_dump(mode="json") for key, value in payload.locations.items()},
        "actions": {key: {"operator": list(value.operator), "roles": list(value.roles)}
                    for key, value in payload.profiles.items()},
        "data": [entry["data"] for entry in solved.registry.to_dict()["records"]],
        "records": solved.records.records_dict(), "status": solved.status,
        "coverage": deepcopy(solved.coverage),
        "unresolved": [item.model_dump(mode="json") for item in payload.unresolved],
        "diagnostics": deepcopy(solved.diagnostics),
    })


def load_doe_input(path: str | Path) -> dict:
    """Load only the specified business JSON; never require adjacent files."""
    return validate_doe_input(Path(path).read_text(encoding="utf-8"))
