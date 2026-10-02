"""Compact V6 records, explicit material identity and ordered atomic events."""
import pytest
from skill_ir.data import DataRegistry, Origin, WholeExceptContent
from skill_ir.propagation.models import AtomicOpRecord, EffectEvent, FlowLocation, FlowState, IRFlowRecord
from skill_ir.propagation.records import PropagationRecords, cfg_sha256
from skill_ir.security_profile.boundaries import derive_sink_boundaries


def graph_payload():
    return {"entry_block_id": "entry", "blocks": {"entry": {
        "block_id": "entry", "block_name": "处理", "instructions": [
            {"id": "ir_action", "opcode": "open_action", "inputs": [
                {"type": "literal", "literal_value": "A"}, {"type": "literal", "literal_value": "B"}],
             "outputs": [{"type": "result", "identifier": "clean"}]},
            {"id": "ir_done", "opcode": "return", "inputs": [{"type": "result", "identifier": "clean"}]},
        ]}}, "edges": []}


def ev(field=None, value=None, index=None):
    base = {"basis": "cfg", "ref_id": "g001", "quote": "open_action", "reason": "测试数据"}
    return base if field is None else {**base, "field": field, "value": value, "effect_index": index}


def profile(effects):
    return {"operator": ["agent_runtime"], "roles": [], "effects": effects,
            "evidences": [ev("operator", "agent_runtime"), ev("roles")]
            + ([ev("effects", value, index) for index, value in enumerate(effects)] if effects else [ev("effects")])}


def annotation_payload():
    value = {"profiles": {"ir_action": profile(["model_observe", "transform", "model_observe"]), "ir_done": profile([])},
            "locations": {"model": {"kind": "model_context", "name": "llm", "access_scope": "recipient", "retention": None,
                                    "operand_refs": [{"instruction_id": "ir_action", "side": "input", "index": 0}]}},
            "transfer_specs": {
                "ir_action": {"order": "fixed", "precedence": [], "events": [
                    {"effect_index": 0, "atomic_ops": [{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "model", "evidences": [ev()]}]},
                    {"effect_index": 1, "atomic_ops": [{"op": "exclude_parts", "input": {"kind": "input", "index": 0}, "paths": [["api_key"]], "output": "filtered", "evidences": [ev()]}]},
                    {"effect_index": 2, "atomic_ops": [{"op": "deliver", "inputs": [{"kind": "local", "name": "filtered"}], "target": "model", "evidences": [ev()]}]},
                ], "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "filtered"}, "evidences": [ev()]}]},
                "ir_done": {"order": "fixed", "precedence": [], "events": [], "output_bindings": []}}}
    value["sink_boundaries"] = [row.model_dump(mode="json") for row in
        derive_sink_boundaries(value["locations"], value["transfer_specs"], value["profiles"])]
    return value


def materials(store):
    return {"cfg": store.cfg, "annotation": store.annotation,
            "data_registry": store.data_registry, "initial_data": store.initial_data,
            "initial_state": store.initial_state}


@pytest.fixture
def records_case():
    registry = DataRegistry("record-v4")
    raw = registry.register_source("A", acquired_from="source-A")
    seed = registry.to_dict()
    clean = registry.create_result("clean", content=WholeExceptContent(base=raw.id, excluded_parts=[["api_key"]]), origin=Origin(at="ir_action", inputs=[raw.id]))
    cfg, annotation = graph_payload(), annotation_payload()
    entry = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="A"): frozenset({raw.id})})
    store = PropagationRecords(cfg, annotation, registry, profile_schema_version="security-profile-v10", annotation_cfg_sha256=cfg_sha256(cfg), initial_data=seed, initial_state=entry)
    target = FlowLocation(kind="model_context", name="llm")
    record = IRFlowRecord(order="fixed", precedence=[], entry_state=entry, exit_state=FlowState.from_mapping({
        FlowLocation(kind="runtime_context", name="A"): frozenset({raw.id}),
        FlowLocation(kind="result", name="clean"): frozenset({clean.id})}), events=[
        EffectEvent(effect="model_observe", atomic_ops=[AtomicOpRecord(op="deliver", inputs=[frozenset({raw.id})], endpoints=[target])]),
        EffectEvent(effect="transform", atomic_ops=[AtomicOpRecord(op="exclude_parts", inputs=[frozenset({raw.id})], outputs=[frozenset({clean.id})])]),
        EffectEvent(effect="model_observe", atomic_ops=[AtomicOpRecord(op="deliver", inputs=[frozenset({clean.id})], endpoints=[target])]),
    ])
    return store, registry, cfg, annotation, raw, clean, record


def complete(case):
    store, *_, record = case
    store.put("ir_action", record)
    store.put("ir_done", IRFlowRecord(order="fixed", precedence=[], entry_state=record.exit_state, exit_state=record.exit_state, events=[]))
    return store


def test_missing_and_committed_empty_record_differ(records_case):
    store, *_, record = records_case
    with pytest.raises(KeyError):
        store.get("ir_done")
    store.put("ir_done", IRFlowRecord(order="fixed", precedence=[], entry_state=FlowState(), exit_state=FlowState(), events=[]))
    assert len(store) == 1 and not store.is_complete
    store.validate()
    with pytest.raises(ValueError, match="incomplete"):
        store.validate(require_complete=True)


def test_actual_pre_and_post_versions_are_preserved(records_case):
    store, registry, cfg, annotation, raw, clean, record = records_case
    store.put("ir_action", record)
    events = store.get("ir_action").events
    assert events[0].atomic_ops[0].inputs[0] == frozenset({raw.id})
    assert events[2].atomic_ops[0].inputs[0] == frozenset({clean.id})
    registry.register_part(raw.id, ["later_field"])
    assert store.get("ir_action").events == events
    assert registry.get(clean.id).content.base == raw.id


def test_snapshot_roundtrip_binds_seed_annotation_and_new_versions(records_case):
    store = complete(records_case)
    store.validate(require_complete=True)
    payload = store.to_dict()
    assert payload["schema_version"] == "skillflow-propagation-record-v9"
    assert payload["profile_schema_version"] == "security-profile-v10"
    assert not {"cfg", "annotation", "data", "initial_data", "initial_state"} & set(payload)
    assert len(store.initial_data["records"]) == 1
    restored = PropagationRecords.from_json(store.to_json(), **materials(store))
    assert restored.to_json() == store.to_json()


def test_queries_exports_and_put_are_isolated(records_case):
    store, *_, record = records_case
    store.put("ir_action", record)
    record.events.clear()
    item = store.get("ir_action")
    item.events[0].atomic_ops[0].inputs.clear()
    payload = store.to_dict()
    annotation = store.annotation
    annotation["profiles"].clear()
    cfg = store.cfg
    cfg["blocks"].clear()
    seed = store.initial_data
    seed["records"].clear()
    state = store.initial_state
    state["bindings"].clear()
    detached = store.records_dict()
    detached["ir_action"]["events"].clear()
    payload["records"]["ir_action"]["events"].clear()
    assert len(store.get("ir_action").events) == 3
    assert len(store.get("ir_action").events[0].atomic_ops[0].inputs) == 1
    assert store.annotation["profiles"] and store.cfg["blocks"]
    assert store.initial_data["records"] and store.initial_state["bindings"]


@pytest.mark.parametrize("change", ["event_missing", "effect", "event_index", "op", "op_index", "notes", "op_missing", "inputs", "input_reference", "missing_data", "output", "endpoint"])
def test_invalid_whole_replacements_leave_old_record_untouched(records_case, change):
    store, *_, record = records_case
    store.put("ir_action", record)
    original = store.get("ir_action")
    value = record.model_dump(mode="json")
    event, operation = value["events"][0], value["events"][0]["atomic_ops"][0]
    if change == "event_missing": value["events"].pop()
    elif change == "effect": event["effect"] = "net_send"
    elif change == "event_index": event["effect_index"] = 1
    elif change == "op": operation["op"] = "compute"
    elif change == "op_index": operation["op_index"] = 0
    elif change == "notes": operation["notes"] = []
    elif change == "op_missing": event["atomic_ops"] = []
    elif change == "inputs": operation["inputs"] *= 2
    elif change == "input_reference": operation["inputs"][0] = {"ref": {"kind": "input", "index": 0}, "data_ids": operation["inputs"][0]}
    elif change == "missing_data": operation["inputs"][0] = ["missing"]
    elif change == "output": value["events"][1]["atomic_ops"][0]["outputs"] = []
    else: operation["endpoints"][0]["name"] = "wrong"
    with pytest.raises(ValueError):
        store.put("ir_action", IRFlowRecord.model_validate(value))
    assert store.get("ir_action") == original


@pytest.mark.parametrize("field", ["cfg", "annotation", "data", "initial_data", "initial_state"])
def test_snapshot_digest_mismatch_rejected(records_case, field):
    store = complete(records_case)
    payload = store.to_dict()
    payload[field + "_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="identity does not match supplied material"):
        PropagationRecords.from_dict(payload, **materials(store))


@pytest.mark.parametrize("field,value", [("schema_version", "skillflow-propagation-record-v4"), ("profile_schema_version", "security-profile-v5"), ("complete", False)])
def test_old_versions_and_false_completion_rejected(records_case, field, value):
    store = complete(records_case)
    payload = store.to_dict()
    payload[field] = value
    with pytest.raises(ValueError):
        PropagationRecords.from_dict(payload, **materials(store))


def test_unknown_order_preserved_without_pretending_verified(records_case):
    _, registry, cfg, annotation, _, _, record = records_case
    annotation["transfer_specs"]["ir_action"]["order"] = "partial"
    record = record.model_copy(update={"order": "partial"})
    store = PropagationRecords(cfg, annotation, registry, profile_schema_version="security-profile-v10", annotation_cfg_sha256=cfg_sha256(cfg))
    store.put("ir_action", record)
    assert not store.effect_order_known("ir_action")
    assert PropagationRecords.from_json(store.to_json(), **materials(store)).get("ir_action").order == "partial"


def test_null_effect_event_keeps_possible_computation(records_case):
    _, registry, cfg, annotation, raw, clean, record = records_case
    annotation["profiles"]["ir_action"] = profile([])
    annotation["transfer_specs"]["ir_action"]["events"] = [{"effect_index": None, "atomic_ops": [{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["possible"], "output": "filtered", "evidences": [ev()]}]}]
    annotation["sink_boundaries"] = []
    store = PropagationRecords(cfg, annotation, registry, profile_schema_version="security-profile-v10", annotation_cfg_sha256=cfg_sha256(cfg))
    record = IRFlowRecord(order="fixed", precedence=[], entry_state=record.entry_state, exit_state=record.exit_state, events=[EffectEvent(effect=None, atomic_ops=[AtomicOpRecord(op="compute", inputs=[frozenset({raw.id})], outputs=[frozenset({clean.id})])])])
    store.put("ir_action", record)
    assert store.get("ir_action").events[0].effect is None
    assert store.get("ir_action").entry_state != store.get("ir_action").exit_state


def test_compact_slot_lists_preserve_repeated_parameters_and_json_order():
    record = AtomicOpRecord(op="compute", inputs=[frozenset({"B", "A"}), frozenset({"A", "B"})],
                            outputs=[frozenset({"C"})])
    payload = record.model_dump(mode="json")
    assert payload["inputs"] == [["A", "B"], ["A", "B"]]
    assert AtomicOpRecord.model_validate_json(record.model_dump_json()) == record
    for bad in ([[]], [["A", "A"]], [{"data_ids": ["A"]}]):
        with pytest.raises(ValueError):
            AtomicOpRecord(op="compute", inputs=bad)


def test_loading_requires_all_materials_and_rejects_embedded_legacy_copies(records_case):
    store = complete(records_case)
    with pytest.raises(TypeError):
        PropagationRecords.from_dict(store.to_dict())
    payload = store.to_dict()
    payload["data"] = store.data_registry.to_dict()
    with pytest.raises(ValueError):
        PropagationRecords.from_dict(payload, **materials(store))


@pytest.mark.parametrize("field", ["cfg", "annotation", "data_registry", "initial_data", "initial_state"])
def test_substituted_material_rejected_without_recomputing_expected_digest(records_case, field):
    store = complete(records_case)
    supplied = materials(store)
    if field == "cfg": supplied[field]["blocks"]["entry"]["block_name"] = "different"
    elif field == "annotation": supplied[field]["profiles"]["ir_action"]["evidences"][0]["reason"] = "different"
    elif field == "data_registry": supplied[field] = DataRegistry("different")
    elif field == "initial_data": supplied[field] = DataRegistry("different").to_dict()
    else: supplied[field] = FlowState()
    with pytest.raises(ValueError, match="identity does not match supplied material"):
        PropagationRecords.from_dict(store.to_dict(), **supplied)
