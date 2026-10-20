"""Cross-component validation of propagation facts; no standalone handoff format."""
from __future__ import annotations

import json
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from skillflow.common.source_evidence import Text
from skillflow.propagation.data import Data, validate_data_records, validate_element_membership, is_definitely_empty_collection
from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.graph.validation import checked_cfg
from skillflow.propagation.contracts.profiles import AnnotationPayload
from skillflow.propagation.contracts.boundaries import SinkBoundary, classify_sink
from skillflow.propagation.contracts.compatibility import INTERACTION_EFFECTS, validate_event_operations, validate_operation_boundary
from skillflow.propagation.contracts.specs import LocationSpec
from skillflow.propagation.models import FlowLocation, IRFlowRecord, ForEachRecord
from skillflow.propagation.conditions import payload_inputs, validate_record_consumption, record_consumption_shape

class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

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


class PropagationOutcome(_Strict):
    status: Status
    coverage: dict[Text, Coverage]
    diagnostics: list[Diagnostic]


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



def validate_propagation_facts(*, cfg, annotation, data, records, sinks, status, coverage, diagnostics):
    """Check persisted components against one explicitly supplied upstream annotation."""
    if type(records) is not dict or type(sinks) is not list:
        raise ValueError("Propagation records must be an object and sinks must be a list")
    graph = _normalized_cfg(checked_cfg(cfg))
    payload = AnnotationPayload.model_validate(annotation)
    data_values = [Data.model_validate(item) for item in validate_data_records(data)]
    record_values = {key: IRFlowRecord.model_validate(value) for key, value in records.items()}
    outcome = PropagationOutcome.model_validate({"status": status, "coverage": coverage, "diagnostics": diagnostics})
    result = outcome.model_dump(mode="json")
    for diagnostic in result["diagnostics"]:
        for position in [diagnostic, *diagnostic.get("operations", [])]:
            for key in ("body_event_index", "scope"):
                if position.get(key) is None:
                    position.pop(key, None)
    instructions = _instructions(graph)
    expected = set(instructions)
    if set(payload.ir_semantics) != expected or set(outcome.coverage) != expected:
        raise ValueError("annotation and coverage must cover all real IRs exactly")
    if set(record_values) - expected:
        raise ValueError("propagation record refers to an unknown IR")
    processed = {ir for ir, state in outcome.coverage.items() if state == "processed"}
    if set(record_values) != processed:
        raise ValueError("records must match processed coverage exactly")
    reachable = _reachable_instructions(graph)
    if any(ir not in reachable and state != "not_reached" for ir, state in outcome.coverage.items()):
        raise ValueError("coverage reachability differs from the selected CFG")
    if outcome.status == "complete" and processed != reachable:
        raise ValueError("complete propagation must process every reachable IR")
    if outcome.status == "unsupported_feedback" and processed:
        raise ValueError("unsupported feedback must not claim solved records")
    declared = _validate_locations(payload.locations, instructions)
    _validate_records(record_values, instructions, data_values, declared)
    checked_sinks = [SinkBoundary.model_validate(item).model_dump(mode="json") for item in sinks]
    if checked_sinks != resolved_sink_boundaries(payload.locations, record_values):
        raise ValueError("sink boundaries differ from recorded operations, targets or fixed levels")
    compiled_sinks = [item.model_dump(mode="json") for item in payload.sink_boundaries]
    if any(item not in compiled_sinks for item in checked_sinks):
        raise ValueError("recorded sink boundary is absent from the compiled annotation")
    _validate_diagnostics(result["diagnostics"], instructions, graph["blocks"], {item.id for item in data_values}, record_values)
    codes = {item["code"] for item in result["diagnostics"]}
    if outcome.status == "complete" and codes - {"missing_part"}:
        raise ValueError("complete propagation contradicts a failure diagnostic")
    if outcome.status in {"unsupported_feedback", "resource_limit", "execution_error"} and outcome.status not in codes:
        raise ValueError("failed propagation status requires its recorded diagnostic")
    if outcome.status == "incomplete":
        missing = {ir for ir, state in outcome.coverage.items() if state == "unresolved_binding"}
        reported = {item["instruction_id"] for item in result["diagnostics"] if item["code"] == "unresolved_binding"}
        if not missing or missing != reported:
            raise ValueError("incomplete coverage and unresolved binding diagnostics must agree")
    return result
