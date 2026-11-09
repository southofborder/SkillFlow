"""External, replaceable static IR records; no transfer rules or execution.

The supplied annotation must already have passed the security-profile service's
evidence checks. Here we recheck its current structure, coverage and occurrence evidence,
not the truth of annotations or the meaning of caller-supplied data bindings.
"""

from __future__ import annotations

from copy import deepcopy
import json

from pydantic import TypeAdapter

from skillflow.common.source_evidence import _require_json
from skillflow.common.source_evidence import canonical_graph_sha256
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.data import validate_element_membership
from skillflow.propagation.data import is_definitely_empty_collection
from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.graph.validation import checked_cfg
from skillflow.propagation.contracts.profiles import AnnotationPayload
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION as PROFILE_SCHEMA_VERSION

from skillflow.propagation.models import FlowLocation
from skillflow.propagation.models import FlowState
from skillflow.propagation.models import IRFlowRecord
from skillflow.propagation.models import EffectEvent
from skillflow.propagation.models import ForEachRecord
from skillflow.propagation.contracts.specs import AtomicOp
from skillflow.propagation.contracts.specs import validate_specs
from skillflow.propagation.contracts.specs import value_refs
from skillflow.propagation.conditions import guard_truths
from skillflow.propagation.conditions import payload_input_indices
from skillflow.propagation.conditions import validate_record_consumption

SCHEMA_VERSION = "skillflow-propagation-record-v16"
LEGACY_SCHEMA_VERSION = "skillflow-propagation-record-v15"


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
        raise PropagationRecordError("annotation must include task, demands, expressions, locations, ir_semantics and sink_boundaries")
    _require_json(annotation, "")
    return AnnotationPayload.model_validate(annotation).model_dump(mode="json")


def _validate_annotation(annotation: dict, expected: set[str]) -> None:
    actual = set(annotation["ir_semantics"])
    from skillflow.propagation.contracts.limitations import unmodeled_ids
    unmodeled = unmodeled_ids(annotation)
    if actual & unmodeled or actual | unmodeled != expected:
        raise PropagationRecordError(
            f"profile coverage mismatch: missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
        )
    # The merged strict type checks operator coverage, each effect's own
    # evidence, and the conditional absence-of-effects declaration.
    AnnotationPayload.model_validate(annotation)


class PropagationRecords:
    """One isolated static record per actual IR in a selected, fixed graph.

    CFG and annotation are copied. The DataRegistry is deliberately live so a
    later description refinement keeps its identity and existing observations.
    The owning run binds material digests; this component stores only IR records
    and never introduces a second serialized Data authority.
    """

    def __init__(
        self, cfg: ControlFlowGraph | dict, annotation: AnnotationPayload | dict,
        data_registry: DataRegistry, *, profile_schema_version: str,
        annotation_cfg_sha256: str,
        initial_data: DataRegistry | dict | None = None,
        initial_state: FlowState | None = None,
    ) -> None:
        if profile_schema_version != PROFILE_SCHEMA_VERSION:
            raise PropagationRecordError("requires explicit " + PROFILE_SCHEMA_VERSION + " annotation identity")
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
        self._computation_owned = False

    @classmethod
    def from_computation(
        cls, cfg: dict, annotation: dict, data_registry: DataRegistry, *,
        profile_schema_version: str, annotation_cfg_sha256: str,
        initial_data: DataRegistry | dict | None = None,
        initial_state: FlowState | None = None,
    ) -> "PropagationRecords":
        """Own already checked solver inputs without repeating whole validation.

        This is an internal producer boundary. External records and callers use
        the checked constructor and ``put``. The solver supplies its normalized
        graph, compiled annotation and computation-owned registry; finalization
        checks references, while ``validate`` remains the explicit full audit.
        """
        if profile_schema_version != PROFILE_SCHEMA_VERSION:
            raise PropagationRecordError("requires explicit " + PROFILE_SCHEMA_VERSION + " annotation identity")
        if type(cfg) is not dict or type(annotation) is not dict or not isinstance(data_registry, DataRegistry):
            raise PropagationRecordError("computed records require checked graph, annotation and registry inputs")
        if annotation_cfg_sha256 != _digest(cfg):
            raise PropagationRecordError("annotation CFG identity does not match the selected graph")
        store = cls.__new__(cls)
        store._cfg, store._annotation = deepcopy(cfg), deepcopy(annotation)
        store._annotation_cfg_sha256 = annotation_cfg_sha256
        store._instructions = {ir["id"]: ir for block in store._cfg["blocks"].values()
                               for ir in block.get("instructions", [])}
        store._result_ids = {operand["identifier"] for ir in store._instructions.values()
                             for operand in ir.get("outputs", [])}
        store._data_registry = data_registry
        seed = (initial_data.snapshot_computed() if isinstance(initial_data, DataRegistry)
                else initial_data if initial_data is not None else data_registry.snapshot_computed())
        store._initial_data = deepcopy(seed)
        if initial_state is not None and not isinstance(initial_state, FlowState):
            raise PropagationRecordError("computed initial state must be a checked FlowState")
        store._initial_state = (initial_state if initial_state is not None else FlowState()).model_copy(deep=True)
        store._records = {}
        store._computation_owned = True
        store.check_references()
        return store

    @property
    def computation_owned(self) -> bool:
        """Whether the records were assembled through the internal solver path."""
        return self._computation_owned

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
    def is_complete(self) -> bool:
        """Record coverage only; does not resolve effects or certify semantics."""
        from skillflow.propagation.loop_guards import admitted_instructions
        expected = admitted_instructions(self._cfg, self._annotation, self._records, self._data_registry)
        return set(self._records) == expected

    def __len__(self) -> int:
        return len(self._records)

    def _require_ir(self, ir_id: str) -> None:
        if type(ir_id) is not str or ir_id not in self._instructions:
            raise PropagationRecordError(f"IR does not exist in the selected CFG: {ir_id!r}")

    def effect_order_known(self, ir_id: str) -> bool:
        """Whether the specification asserts fixed order, not its truth."""
        self._require_ir(ir_id)
        return self._annotation["ir_semantics"][ir_id]["order"] == "fixed"

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
        transfer = self._annotation["ir_semantics"][ir_id]
        if record.order != transfer["order"] or [item.model_dump(mode="json") for item in record.precedence] != transfer["precedence"]:
            raise PropagationRecordError("record order/precedence differs from compiled transfer specification")
        specifications = transfer["events"]
        if len(record.events) != len(specifications):
            raise PropagationRecordError(f"event coverage mismatch for {ir_id}: expected {len(specifications)}")
        def validate_effect(event, spec, position):
            if not isinstance(event, EffectEvent):
                raise PropagationRecordError(f"effect record required at {ir_id}/{position}")
            expected_effect = spec["effect"]
            if event.effect != expected_effect:
                raise PropagationRecordError(f"event position/label mismatch at {ir_id}/{position}")
            if ((event.case.model_dump(mode="json") if event.case else None) != spec.get("case")
                    or event.requires_completion != spec.get("requires_completion", [])):
                raise PropagationRecordError("call case or completion condition differs from specification")
            if len(event.atomic_ops) != len(spec["atomic_ops"]):
                raise PropagationRecordError(f"atomic operation coverage mismatch at {ir_id}/{position}")
            for op_index, (operation, op_spec) in enumerate(zip(event.atomic_ops, spec["atomic_ops"])):
                if operation.op != op_spec["op"]:
                    raise PropagationRecordError(f"atomic operation identity mismatch at {ir_id}/{position}/{op_index}")
                if operation.may_state != op_spec.get("may", False):
                    raise PropagationRecordError("state summary differs from the declared may write")
                validate_record_consumption(operation, self._data_registry)
                if operation.op == "build":
                    if len(operation.members) != len(op_spec["parts"]):
                        raise PropagationRecordError("build member coverage differs from specification")
                    for member, declaration in zip(operation.members, op_spec["parts"]):
                        if member.path != declaration["path"] or (member.when_input_index is None) != (declaration.get("when") is None):
                            raise PropagationRecordError("build member path/control differs from specification")
                elif op_spec.get("when") is not None:
                    if event.effect != "model_observe" or operation.when_input_index is None:
                        raise PropagationRecordError("conditional observation requires its compiled control input")
                    truths = guard_truths(self._data_registry, operation.inputs[operation.when_input_index])
                    expected = len(op_spec["inputs"]) if True in truths else 0
                    if len(payload_input_indices(operation)) != expected:
                        raise PropagationRecordError("conditional observation payload differs from active specification")
                else:
                    if operation.when_input_index is not None:
                        raise PropagationRecordError("record invents a condition absent from its specification")
                    expected_refs = value_refs(TypeAdapter(AtomicOp).validate_python(op_spec))
                    if len(operation.inputs) != len(expected_refs):
                        raise PropagationRecordError(f"resolved input coverage differs from ordered spec references at {ir_id}/{position}/{op_index}")
                if len(operation.outputs) != int("output" in op_spec):
                    raise PropagationRecordError(f"local output coverage mismatch at {ir_id}/{position}/{op_index}")
                if operation.op in {"read", "receive", "deliver", "write"} and not operation.endpoints:
                    raise PropagationRecordError(f"interaction operation requires an endpoint at {ir_id}/{position}/{op_index}")
                boundary_id = op_spec.get("location", op_spec.get("target"))
                if boundary_id is not None:
                    boundary = self._annotation["locations"][boundary_id]
                    expected_endpoint = FlowLocation(kind=boundary["kind"], name=boundary["name"])
                    if operation.endpoints != [expected_endpoint]:
                        raise PropagationRecordError(f"operation endpoint differs from spec at {ir_id}/{position}/{op_index}")
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

        for event_index, (event, spec) in enumerate(zip(record.events, specifications)):
            if spec.get("kind") == "for_each":
                if not isinstance(event, ForEachRecord):
                    raise PropagationRecordError(f"for_each record required at {ir_id}/{event_index}")
                check_data(event.collections)
                if (event.completion_groups != spec.get("completion_groups", [])
                        or event.requires_completion != spec.get("requires_completion", [])):
                    raise PropagationRecordError("collection completion condition differs from specification")
                collection_data = [self._data_registry.get(identity) for identity in data_ids]
                represented = {instance.collection for instance in event.instances}
                if not represented <= event.collections:
                    raise PropagationRecordError("for_each instance collection is absent from scope candidates")
                for collection in event.collections - represented:
                    if not is_definitely_empty_collection(collection_data, collection):
                        raise PropagationRecordError("for_each collection has no instance and is not explicitly empty")
                seen = set()
                for instance in event.instances:
                    check_data(frozenset([instance.collection, instance.element]))
                    validate_element_membership(
                        collection_data,
                        instance.collection, instance.element,
                    )
                    identity = _digest(instance.model_dump(mode="json"))
                    if identity in seen:
                        raise PropagationRecordError("duplicate for_each instance arrangement")
                    seen.add(identity)
                    if len(instance.body) != len(spec["body"]):
                        raise PropagationRecordError("for_each body event coverage mismatch")
                    for body_index, (body_event, body_spec) in enumerate(zip(instance.body, spec["body"])):
                        validate_effect(body_event, body_spec, f"{event_index}/body/{body_index}")
                        if any(op.changes and not op.may_state for op in body_event.atomic_ops):
                            raise PropagationRecordError("for_each body must not modify shared state")
            else:
                validate_effect(event, spec, str(event_index))

    def put(self, ir_id: str, record: IRFlowRecord) -> None:
        """Validate before committing one whole replacement; never merge events."""
        self._require_ir(ir_id)
        if not isinstance(record, IRFlowRecord):
            raise PropagationRecordError("record must be an IRFlowRecord")
        candidate = IRFlowRecord.model_validate(record.model_dump(mode="python"))
        self._validate_record(ir_id, candidate, set(self._data_registry.data_ids()))
        self._records[ir_id] = candidate.model_copy(deep=True)

    def put_computed(self, ir_id: str, record: IRFlowRecord) -> None:
        """Detach an interpreter-produced record without reparsing its events."""
        if not self._computation_owned:
            raise PropagationRecordError("computed records require the internal computation owner")
        self._require_ir(ir_id)
        if not isinstance(record, IRFlowRecord):
            raise PropagationRecordError("record must be an IRFlowRecord")
        self._records[ir_id] = record.model_copy(deep=True)

    def check_references(self, require_complete: bool = False) -> None:
        """Check final coordinates and Data references, without whole revalidation.

        Projected state snapshots must retain their actual referenced values;
        absence never creates a guessed binding. Atomic evidence is independent
        of state liveness and is checked even when its result is no longer live.
        """
        if type(require_complete) is not bool:
            raise PropagationRecordError("require_complete must be a bool")
        ids = set(self._data_registry.data_ids())

        def data_refs(values):
            missing = set(values) - ids
            if missing:
                raise PropagationRecordError("unknown Data reference: " + repr(sorted(missing)))

        def state_refs(state):
            for binding in state.bindings:
                self._check_location(binding.location)
                data_refs(binding.data_ids)

        seed_ids = {entry["data"]["id"] for entry in self._initial_data["records"]}
        if seed_ids - ids:
            raise PropagationRecordError("final registry lost seed Data identities")
        state_refs(self._initial_state)
        if any(binding.data_ids - seed_ids for binding in self._initial_state.bindings):
            raise PropagationRecordError("initial state has an unknown seed Data reference")
        for ir_id, record in self._records.items():
            self._require_ir(ir_id)
            state_refs(record.entry_state)
            state_refs(record.exit_state)
            for operand in self._instructions[ir_id].get("outputs", []):
                if record.exit_state.get(FlowLocation(kind="result", name=operand["identifier"])) is None:
                    raise PropagationRecordError("processed IR is missing a public output binding in its exit state")
            events = []
            for event in record.events:
                if isinstance(event, ForEachRecord):
                    data_refs(event.collections)
                    data_refs(event.outputs)
                    for instance in event.instances:
                        data_refs((instance.collection, instance.element))
                        data_refs(instance.yielded)
                        events.extend(instance.body)
                else:
                    events.append(event)
            for event in events:
                for operation in event.atomic_ops:
                    for values in [*operation.inputs, *operation.outputs]:
                        data_refs(values)
                    for alternative in operation.alternatives:
                        for values in [*alternative.inputs, *alternative.outputs]:
                            data_refs(values)
                    for location in operation.endpoints:
                        self._check_location(location)
                    for change in operation.changes:
                        self._check_location(change.location)
                        data_refs(change.before)
                        data_refs(change.after)
        if require_complete and not self.is_complete:
            raise PropagationRecordError(f"incomplete IR coverage: {sorted(set(self._instructions) - set(self._records))}")

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

    def records_dict(self) -> dict[str, dict]:
        """Return detached JSON records; array positions locate events and ops."""
        return {
            ir_id: self._records[ir_id].model_dump(mode="json") for ir_id in sorted(self._records)
        }

    @classmethod
    def from_records(cls, records, *, cfg, annotation, data_registry, initial_data, initial_state,
                     _validated_inputs=False):
        """Restore pure records after the owning run verified artifact identities.

        This method validates material relationships. It does not manufacture
        expected digests from supplied values or interpret an old snapshot.
        """
        if type(records) is not dict:
            raise PropagationRecordError("records must be an IR-to-record object")
        _require_json(records, "")
        state = initial_state if _validated_inputs and isinstance(initial_state, FlowState) else FlowState.model_validate(initial_state)
        if _validated_inputs:
            # The run loader owns the checked annotation and restored registry.
            # This flag does not bypass validation of any imported IR record.
            store = cls.from_computation(cfg, annotation, data_registry,
                profile_schema_version=PROFILE_SCHEMA_VERSION, annotation_cfg_sha256=_digest(cfg),
                initial_data=initial_data, initial_state=state)
            store._computation_owned = False
        else:
            store = cls(cfg, annotation, data_registry, profile_schema_version=PROFILE_SCHEMA_VERSION,
                        annotation_cfg_sha256=cfg_sha256(cfg), initial_data=initial_data,
                        initial_state=state)
        data_ids = set(data_registry.data_ids())
        for ir_id, record in records.items():
            candidate = IRFlowRecord.model_validate(record)
            store._validate_record(ir_id, candidate, data_ids)
            store._records[ir_id] = candidate
        return store
