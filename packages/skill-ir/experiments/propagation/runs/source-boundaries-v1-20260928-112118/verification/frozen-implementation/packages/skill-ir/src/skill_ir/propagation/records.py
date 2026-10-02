"""External, replaceable static IR records; no transfer rules or execution.

The supplied annotation must already have passed the security-profile service's
quote checks. Here we recheck its v6 structure, coverage and occurrence evidence,
not the truth of annotations or the meaning of caller-supplied data bindings.
"""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from skill_ir.backtrace.evidence import _require_json, canonical_graph_sha256
from skill_ir.data import DataRegistry
from skill_ir.ir.cfg import ControlFlowGraph
from skill_ir.security_profile.evidence import checked_cfg
from skill_ir.security_profile.models import AnnotationPayload, PROFILE_FIELDS
from skill_ir.security_profile.models import SCHEMA_VERSION as PROFILE_SCHEMA_VERSION
from skill_ir.source_evidence import _json_object

from .models import FlowLocation, FlowState, IRFlowRecord
from .specs import AtomicOp, validate_specs, value_refs

SCHEMA_VERSION = "skillflow-propagation-record-v5"


class PropagationRecordError(ValueError):
    """Invalid structure, identity or reference; not a semantic audit result."""


def _digest(value: object) -> str:
    # Same canonical UTF-8 algorithm as the upstream annotation manifest.
    return canonical_graph_sha256(value)


def _graph_payload(cfg: ControlFlowGraph | dict) -> dict:
    if isinstance(cfg, ControlFlowGraph):
        cfg.validate_integrity()
        # The public serializer omits literal_value on non-literal operands.
        # A raw model_dump would introduce a supplied null rejected by the IR.
        cfg = json.loads(cfg.to_json())
    return checked_cfg(cfg)


def cfg_sha256(cfg: ControlFlowGraph | dict) -> str:
    """Digest a chosen CFG, using the security-profile manifest convention.

    Synthetic callers can use this helper when constructing their annotations.
    Real runs must carry forward the annotation manifest's graph_sha256 instead
    of calculating a fresh value to paper over a mismatched annotation.
    """
    return _digest(_graph_payload(cfg))


def _annotation_payload(annotation: AnnotationPayload | dict) -> dict:
    if isinstance(annotation, AnnotationPayload):
        # Reparse dumped fields: a Pydantic instance may have been mutated.
        annotation = annotation.model_dump(mode="python")
    if type(annotation) is not dict:
        raise PropagationRecordError("annotation must include profiles, locations, transfer_specs and unresolved")
    _require_json(annotation, "")
    return AnnotationPayload.model_validate(annotation).model_dump(mode="json")


def _validate_annotation(annotation: dict, expected: set[str]) -> None:
    actual = set(annotation["profiles"])
    if actual != expected:
        raise PropagationRecordError(
            f"profile coverage mismatch: missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
        )
    unresolved: set[tuple[str, str]] = set()
    for item in annotation["unresolved"]:
        key = item["instruction_id"], item["field"]
        if key[0] not in expected or key in unresolved:
            raise PropagationRecordError(f"invalid or duplicate unresolved reference: {key}")
        unresolved.add(key)
    for ir_id, profile in annotation["profiles"].items():
        supported = set()
        for evidence in profile["evidences"]:
            field, value = evidence["field"], evidence["value"]
            if value is None:
                if profile[field] or (ir_id, field) in unresolved:
                    raise PropagationRecordError(f"invalid empty-field evidence: {ir_id}/{field}")
            elif value not in profile[field]:
                raise PropagationRecordError(f"evidence label absent from profile: {ir_id}/{field}/{value}")
            supported.add((field, value, evidence["effect_index"]))
        for field in PROFILE_FIELDS:
            for index, value in enumerate(profile[field]):
                occurrence = index if field == "effects" else None
                if (field, value, occurrence) not in supported:
                    raise PropagationRecordError(f"missing label occurrence evidence: {ir_id}/{field}/{index}")
            if not profile[field] and (field, None, None) not in supported and (ir_id, field) not in unresolved:
                raise PropagationRecordError(f"empty field lacks evidence or unresolved: {ir_id}/{field}")


class _Snapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal["skillflow-propagation-record-v5"]
    profile_schema_version: Literal["security-profile-v6"]
    annotation_cfg_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    cfg_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    annotation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    data_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    initial_data_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    initial_state_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    records: dict[str, IRFlowRecord]
    complete: bool


class PropagationRecords:
    """One isolated static record per actual IR in a selected, fixed graph.

    CFG and annotation are copied. The DataRegistry is deliberately live so a
    later description refinement keeps its identity and existing observations.
    Exports bind its current digest; material payloads are supplied explicitly
    on load, so records never introduce a second serialized Data authority.
    """

    def __init__(
        self, cfg: ControlFlowGraph | dict, annotation: AnnotationPayload | dict,
        data_registry: DataRegistry, *, profile_schema_version: str,
        annotation_cfg_sha256: str,
        initial_data: DataRegistry | dict | None = None,
        initial_state: FlowState | None = None,
    ) -> None:
        if profile_schema_version != PROFILE_SCHEMA_VERSION:
            raise PropagationRecordError("requires explicit security-profile-v6 annotation identity")
        if not isinstance(data_registry, DataRegistry):
            raise PropagationRecordError("data_registry must be a DataRegistry")
        self._cfg = _graph_payload(cfg)
        if type(annotation_cfg_sha256) is not str or annotation_cfg_sha256 != _digest(self._cfg):
            raise PropagationRecordError("annotation CFG identity does not match the selected graph")
        self._annotation_cfg_sha256 = annotation_cfg_sha256
        self._instructions = {
            instruction["id"]: instruction
            for block in self._cfg["blocks"].values()
            for instruction in block.get("instructions", [])
        }
        self._result_ids = {
            operand["identifier"]
            for instruction in self._instructions.values()
            for operand in instruction.get("outputs", [])
        }
        self._annotation = _annotation_payload(annotation)
        _validate_annotation(self._annotation, set(self._instructions))
        validate_specs(self._cfg, AnnotationPayload.model_validate(self._annotation))
        data_registry.validate()
        self._data_registry = data_registry
        seed = (initial_data.to_dict() if isinstance(initial_data, DataRegistry)
                else initial_data if initial_data is not None else data_registry.to_dict())
        self._initial_data = DataRegistry.from_dict(deepcopy(seed)).to_dict()
        self._initial_state = FlowState.model_validate(
            (initial_state if initial_state is not None else FlowState()).model_dump(mode="python")
        )
        seed_ids = {entry["data"]["id"] for entry in self._initial_data["records"]}
        if seed_ids - {entry["data"]["id"] for entry in data_registry.to_dict()["records"]}:
            raise PropagationRecordError("registry does not contain the declared seed Data identities")
        for binding in self._initial_state.bindings:
            self._check_location(binding.location)
            if binding.data_ids - seed_ids:
                raise PropagationRecordError("initial state has an unknown seed Data reference")
        self._records: dict[str, IRFlowRecord] = {}

    @property
    def data_registry(self) -> DataRegistry:
        """The shared registry, writable only through its existing public API."""
        return self._data_registry

    @property
    def cfg(self) -> dict:
        """Detached selected graph used to validate these records."""
        return deepcopy(self._cfg)

    @property
    def annotation(self) -> dict:
        """Detached operational annotation, without the audit-only evidence table."""
        return deepcopy(self._annotation)

    @property
    def initial_data(self) -> dict:
        """Detached seed Data snapshot, distinct from the live final registry."""
        return deepcopy(self._initial_data)

    @property
    def initial_state(self) -> dict:
        """Detached JSON representation of the authoritative seed state."""
        return self._initial_state.model_dump(mode="json")

    @property
    def unresolved(self) -> list[dict]:
        return deepcopy(self._annotation["unresolved"])

    @property
    def is_complete(self) -> bool:
        """Record coverage only; does not resolve effects or certify semantics."""
        return set(self._records) == set(self._instructions)

    def __len__(self) -> int:
        return len(self._records)

    def _require_ir(self, ir_id: str) -> None:
        if type(ir_id) is not str or ir_id not in self._instructions:
            raise PropagationRecordError(f"IR does not exist in the selected CFG: {ir_id!r}")

    def effect_order_known(self, ir_id: str) -> bool:
        """Whether the supplied profile has no unresolved effects for this IR.

        True describes the annotation's assertion, not a proof of its order.
        """
        self._require_ir(ir_id)
        return not any(
            item["instruction_id"] == ir_id and item["field"] == "effects"
            for item in self._annotation["unresolved"]
        )

    def _check_location(self, location: FlowLocation) -> None:
        if location.kind == "result" and location.name not in self._result_ids:
            raise PropagationRecordError(f"result location does not exist: {location.name}")

    def _validate_record(self, ir_id: str, record: IRFlowRecord, data_ids: set[str]) -> None:
        self._require_ir(ir_id)

        def check_data(ids: frozenset[str]) -> None:
            missing = ids - data_ids
            if missing:
                raise PropagationRecordError(f"unknown Data reference at {ir_id}: {sorted(missing)}")

        for state in (record.entry_state, record.exit_state):
            for binding in state.bindings:
                self._check_location(binding.location)
                check_data(binding.data_ids)
        specifications = self._annotation["transfer_specs"][ir_id]["events"]
        if len(record.events) != len(specifications):
            raise PropagationRecordError(f"event coverage mismatch for {ir_id}: expected {len(specifications)}")
        for event_index, (event, spec) in enumerate(zip(record.events, specifications)):
            effect_index = spec["effect_index"]
            expected_effect = None if effect_index is None else self._annotation["profiles"][ir_id]["effects"][effect_index]
            if event.effect != expected_effect:
                raise PropagationRecordError(f"event position/label mismatch at {ir_id}/{event_index}")
            if len(event.atomic_ops) != len(spec["atomic_ops"]):
                raise PropagationRecordError(f"atomic operation coverage mismatch at {ir_id}/{event_index}")
            for op_index, (operation, op_spec) in enumerate(zip(event.atomic_ops, spec["atomic_ops"])):
                if operation.op != op_spec["op"]:
                    raise PropagationRecordError(f"atomic operation identity mismatch at {ir_id}/{event_index}/{op_index}")
                expected_refs = value_refs(TypeAdapter(AtomicOp).validate_python(op_spec))
                if len(operation.inputs) != len(expected_refs):
                    raise PropagationRecordError(f"resolved input coverage differs from ordered spec references at {ir_id}/{event_index}/{op_index}")
                if len(operation.outputs) != int("output" in op_spec):
                    raise PropagationRecordError(f"local output coverage mismatch at {ir_id}/{event_index}/{op_index}")
                if operation.op in {"read", "receive", "deliver", "write"} and not operation.endpoints:
                    raise PropagationRecordError(f"interaction operation requires an endpoint at {ir_id}/{event_index}/{op_index}")
                boundary_id = op_spec.get("location", op_spec.get("target"))
                if boundary_id is not None:
                    boundary = self._annotation["locations"][boundary_id]
                    expected_endpoint = FlowLocation(kind=boundary["kind"], name=boundary["name"])
                    if operation.endpoints != [expected_endpoint]:
                        raise PropagationRecordError(f"operation endpoint differs from spec at {ir_id}/{event_index}/{op_index}")
                for location in operation.endpoints:
                    self._check_location(location)
                for ids in [*operation.inputs, *operation.outputs]:
                    check_data(ids)
                for change in operation.changes:
                    self._check_location(change.location)
                    check_data(change.before)
                    check_data(change.after)
                    if change.update == "delete" and change.after:
                        raise PropagationRecordError("an exact deletion must leave no binding")
                    if change.update == "weak" and not change.before <= change.after:
                        raise PropagationRecordError("weak updates cannot discard existing candidates")

    def put(self, ir_id: str, record: IRFlowRecord) -> None:
        """Validate before committing one whole replacement; never merge events."""
        self._require_ir(ir_id)
        if not isinstance(record, IRFlowRecord):
            raise PropagationRecordError("record must be an IRFlowRecord")
        candidate = IRFlowRecord.model_validate(record.model_dump(mode="python"))
        data = self._data_registry.to_dict()
        self._validate_record(ir_id, candidate, {entry["data"]["id"] for entry in data["records"]})
        self._records[ir_id] = candidate.model_copy(deep=True)

    def get(self, ir_id: str) -> IRFlowRecord:
        """Return a detached record; an unsubmitted record raises KeyError."""
        return self._records[ir_id].model_copy(deep=True)

    def validate(self, require_complete: bool = False) -> None:
        if type(require_complete) is not bool:
            raise PropagationRecordError("require_complete must be a bool")
        data = self._data_registry.to_dict()
        data_ids = {entry["data"]["id"] for entry in data["records"]}
        if {entry["data"]["id"] for entry in self._initial_data["records"]} - data_ids:
            raise PropagationRecordError("final registry lost seed Data identities")
        for ir_id, record in self._records.items():
            checked = IRFlowRecord.model_validate(record.model_dump(mode="python"))
            self._validate_record(ir_id, checked, data_ids)
        if require_complete and not self.is_complete:
            raise PropagationRecordError(f"incomplete IR coverage: {sorted(set(self._instructions) - set(self._records))}")

    def to_dict(self) -> dict:
        self.validate()
        data = self._data_registry.to_dict()
        return deepcopy({
            "schema_version": SCHEMA_VERSION,
            "profile_schema_version": PROFILE_SCHEMA_VERSION,
            "annotation_cfg_sha256": self._annotation_cfg_sha256,
            "cfg_sha256": _digest(self._cfg),
            "annotation_sha256": _digest(self._annotation),
            "data_sha256": _digest(data),
            "initial_data_sha256": _digest(self._initial_data),
            "initial_state_sha256": _digest(self._initial_state.model_dump(mode="json")),
            "records": self.records_dict(),
            "complete": self.is_complete,
        })

    def records_dict(self) -> dict[str, dict]:
        """Return detached JSON records; array positions locate events and ops."""
        return {
            ir_id: self._records[ir_id].model_dump(mode="json") for ir_id in sorted(self._records)
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, sort_keys=True, allow_nan=False, indent=indent)

    @classmethod
    def from_dict(
        cls, payload: dict, *, cfg: ControlFlowGraph | dict,
        annotation: AnnotationPayload | dict, data_registry: DataRegistry,
        initial_data: DataRegistry | dict, initial_state: FlowState | dict,
    ) -> "PropagationRecords":
        """Attach a compact snapshot to explicit materials and verify every digest.

        The supplied registry remains the one live Data authority. Digests check
        material identity, not the semantic truth of either records or rules.
        """
        if type(payload) is not dict:
            raise PropagationRecordError("snapshot must be a JSON object")
        _require_json(payload, "")
        snapshot = _Snapshot.model_validate(payload)
        if not isinstance(data_registry, DataRegistry):
            raise PropagationRecordError("data_registry must be a DataRegistry")
        materials = {
            "cfg": _graph_payload(cfg),
            "annotation": _annotation_payload(annotation),
            "data": data_registry.to_dict(),
            "initial_data": initial_data.to_dict() if isinstance(initial_data, DataRegistry) else initial_data,
            "initial_state": initial_state.model_dump(mode="json") if isinstance(initial_state, FlowState) else initial_state,
        }
        for field, value in materials.items():
            if _digest(value) != getattr(snapshot, field + "_sha256"):
                raise PropagationRecordError(f"{field} identity does not match supplied material")
        store = cls(
            materials["cfg"], materials["annotation"], data_registry,
            profile_schema_version=snapshot.profile_schema_version,
            annotation_cfg_sha256=snapshot.annotation_cfg_sha256,
            initial_data=materials["initial_data"], initial_state=FlowState.model_validate(materials["initial_state"]),
        )
        # Require the exported representation to retain the same identities;
        # importing must not silently reinterpret a malformed source snapshot.
        if _digest(store._cfg) != snapshot.cfg_sha256:
            raise PropagationRecordError("CFG snapshot is not its validated representation")
        if _digest(store._annotation) != snapshot.annotation_sha256:
            raise PropagationRecordError("annotation snapshot is not its validated representation")
        if _digest(store.data_registry.to_dict()) != snapshot.data_sha256:
            raise PropagationRecordError("data snapshot is not its validated representation")
        if (_digest(store._initial_data) != snapshot.initial_data_sha256
                or _digest(store._initial_state.model_dump(mode="json")) != snapshot.initial_state_sha256):
            raise PropagationRecordError("seed snapshot is not its validated representation")
        for ir_id, record in snapshot.records.items():
            store.put(ir_id, record)
        store.validate(require_complete=snapshot.complete)
        if snapshot.complete != store.is_complete:
            raise PropagationRecordError("snapshot complete flag disagrees with actual IR coverage")
        return store

    @classmethod
    def from_json(
        cls, text: str, *, cfg: ControlFlowGraph | dict,
        annotation: AnnotationPayload | dict, data_registry: DataRegistry,
        initial_data: DataRegistry | dict, initial_state: FlowState | dict,
    ) -> "PropagationRecords":
        if type(text) is not str:
            raise PropagationRecordError("JSON input must be a string")
        return cls.from_dict(_json_object(text), cfg=cfg, annotation=annotation,
                             data_registry=data_registry, initial_data=initial_data,
                             initial_state=initial_state)
