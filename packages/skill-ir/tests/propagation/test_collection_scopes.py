"""Collection views and member scopes preserve paired values without execution."""
from copy import deepcopy

import pytest

from skill_ir.data import DataPart, DataRegistry, FieldUpdatesContent, LiteralContent, Origin, SubsetViewContent, WholeExceptContent
from skill_ir.propagation.models import FlowLocation, FlowState, IRFlowRecord, ForEachRecord
from skill_ir.propagation.records import PropagationRecords
from skill_ir.propagation.solver import propagate
from skill_ir.security_profile.evidence import checked_cfg
from skill_ir.security_profile.boundaries import derive_sink_boundaries


EVIDENCE = {"basis": "cfg", "ref_id": "G.fixture", "quote": "fixture", "reason": "人工构造的离线结构测试。"}


def local(name):
    return {"kind": "local", "name": name}


def input_ref(index=0):
    return {"kind": "input", "index": index}


def operation(op, **kwargs):
    return {"op": op, **kwargs, "evidences": [deepcopy(EVIDENCE)]}


def profile(effects):
    result = {"operator": ["agent_runtime"], "roles": [], "effects": effects, "evidences": []}
    for field in ("operator", "roles", "effects"):
        for index, value in enumerate(result[field] or [None]):
            result["evidences"].append({**EVIDENCE, "field": field, "value": value,
                                       "effect_index": index if field == "effects" and value else None})
    return result


def fixture(*, filtered=False, uncertain=False, body=None, effects=None):
    cfg = checked_cfg({"entry_block_id": "source", "declared_context_keys": ["collection"], "blocks": {
        "source": {"block_id": "source", "block_name": "source", "data_source_kind": "context", "instructions": [
            {"id": "ir_read", "opcode": "read_collection", "inputs": [{"type": "context_key", "identifier": "collection"}],
             "outputs": [{"type": "result", "identifier": "items"}]},
            {"id": "ir_dispatch", "opcode": "dispatch", "inputs": [], "outputs": []}]},
        "main": {"block_id": "main", "block_name": "process", "instructions": [
            {"id": "ir_process", "opcode": "process_members", "inputs": [{"type": "result", "identifier": "items"}], "outputs": []},
            {"id": "ir_return", "opcode": "return", "inputs": [], "outputs": []}]}},
        "edges": [{"source_block_id": "source", "target_block_id": "main"}]})
    offset = int(filtered)
    if body is None:
        body = [{"effect_index": offset, "atomic_ops": [
                    operation("select_part", input=local("item"), path=["recipient"], output="recipient"),
                    operation("select_part", input=local("item"), path=["payload"], output="payload")]},
                {"effect_index": offset + 1, "atomic_ops": [
                    operation("deliver", inputs=[local("recipient"), local("payload"), local("recipient")], target="service")]}]
    processing_effects = (["transform"] if filtered else []) + (effects or ["transform", "net_send"])
    events = ([{"effect_index": 0, "atomic_ops": [operation("filter_items", input=input_ref(), predicate="keep == true", output="selected")]}]
              if filtered else [])
    events.append({"kind": "for_each", "collection": local("selected") if filtered else input_ref(),
                   "item": "item", "body": body, "evidences": [deepcopy(EVIDENCE)]})
    annotation = {"profiles": {key: profile(labels) for key, labels in {
        "ir_read": ["context_read"], "ir_dispatch": [], "ir_process": processing_effects, "ir_return": []}.items()},
        "locations": {"collection": {"kind": "runtime_context", "name": "collection", "operand_refs": [],
                                     "access_scope": "task", "retention": "task"},
                      "service": {"kind": "remote", "name": "service", "operand_refs": [],
                                  "access_scope": "recipient", "retention": None},
                      "model": {"kind": "model_context", "name": "model", "operand_refs": [],
                                "access_scope": "recipient", "retention": None}},
        "transfer_specs": {
            "ir_read": {"order": "fixed", "precedence": [], "events": [{"effect_index": 0, "atomic_ops": [operation("read", location="collection", output="value")]}],
                        "output_bindings": [{"output_index": 0, "value": local("value"), "evidences": [deepcopy(EVIDENCE)]}]},
            "ir_dispatch": {"order": "fixed", "precedence": [], "events": [], "output_bindings": []},
            "ir_process": {"order": "fixed", "precedence": [], "events": events, "output_bindings": []},
            "ir_return": {"order": "fixed", "precedence": [], "events": [], "output_bindings": []}}}
    annotation["transfer_specs"]["ir_process"]["order"] = "partial" if uncertain else "fixed"
    annotation["sink_boundaries"] = [row.model_dump(mode="json") for row in
        derive_sink_boundaries(annotation["locations"], annotation["transfer_specs"], annotation["profiles"])]
    return cfg, annotation


def solve(*values, filtered=False, uncertain=False, **kwargs):
    cfg, annotation = fixture(filtered=filtered, uncertain=uncertain, **kwargs)
    registry = DataRegistry("collection-test")
    ids = []
    for index, value in enumerate(values):
        ids.append(registry.register_source(str(index), acquired_from="fixture:" + str(index),
                                           **({"content": LiteralContent(value=value)} if value is not None else {})).id)
    state = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset(ids)})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    return cfg, annotation, result, ids


def test_unknown_collection_has_one_scoped_member_and_keeps_field_pairing():
    _, _, result, source_ids = solve(None)
    assert result.status == "complete", result.diagnostics
    record = result.records.get("ir_process")
    assert record.entry_state == record.exit_state
    scope = record.events[0]
    assert isinstance(scope, ForEachRecord) and len(scope.instances) == 1
    assert scope.collections == frozenset(source_ids)
    instance = scope.instances[0]
    assert instance.collection == source_ids[0]
    member = result.registry.get(instance.element)
    assert member.origin.part_of == instance.collection
    send = instance.body[-1].atomic_ops[0]
    recipient, payload, repeated = [next(iter(ids)) for ids in send.inputs]
    assert recipient == repeated != payload
    assert result.registry.resolve_part(instance.element, ["recipient"]).id == recipient
    assert result.registry.resolve_part(instance.element, ["payload"]).id == payload


def test_multiple_collection_candidates_do_not_cross_pair_parameters():
    _, _, result, source_ids = solve(None, None)
    assert result.status == "complete", result.diagnostics
    instances = result.records.get("ir_process").events[0].instances
    assert result.records.get("ir_process").events[0].collections == frozenset(source_ids)
    assert {item.collection for item in instances} == set(source_ids)
    assert len(instances) == 2
    for instance in instances:
        send = instance.body[-1].atomic_ops[0]
        assert all(len(ids) == 1 for ids in send.inputs)
        assert result.registry.resolve_part(instance.element, ["recipient"]).id in send.inputs[0]
        assert result.registry.resolve_part(instance.element, ["payload"]).id in send.inputs[1]


def test_static_members_remain_paired_and_filter_does_not_evaluate_predicate():
    values = [{"recipient": "a", "payload": "alpha", "keep": True},
              {"recipient": "b", "payload": "beta", "keep": False}]
    _, _, result, original = solve(values, filtered=True)
    assert result.status == "complete", result.diagnostics
    record = result.records.get("ir_process")
    filtered = next(iter(record.events[0].atomic_ops[0].outputs[0]))
    assert result.registry.get(filtered).content == SubsetViewContent(base=original[0], predicate="keep == true")
    assert len(record.events[1].instances) == 2
    pairs = set()
    for instance in record.events[1].instances:
        assert instance.collection == filtered
        inputs = instance.body[-1].atomic_ops[0].inputs
        pairs.add(tuple(result.registry.get(next(iter(ids))).content.value for ids in inputs[:2]))
    assert pairs == {("a", "alpha"), ("b", "beta")}


def test_empty_collection_has_no_fabricated_member_or_delivery():
    _, _, result, sources = solve([])
    assert result.status == "complete", result.diagnostics
    record = result.records.get("ir_process")
    assert record.events[0].instances == []
    assert record.events[0].collections == frozenset(sources)
    assert record.entry_state == record.exit_state


@pytest.mark.parametrize("filtered", [False, True])
def test_all_static_members_removed_can_complete_empty_scope_without_fabricated_delivery(filtered):
    cfg, annotation = fixture(filtered=filtered)
    registry = DataRegistry("removed-members")
    base = registry.register_source("collection", acquired_from="fixture", content=LiteralContent(
        value=[{"recipient": "old", "payload": "old-payload"}]))
    replacement = registry.create_result("replacement", content=LiteralContent(value="updated"), origin=Origin(at="replacement"))
    updated = registry.create_result("updated", content=FieldUpdatesContent(base=base.id, updates=[
        DataPart(path=[0, "payload"], data=replacement.id)]), origin=Origin(at="update"))
    empty = registry.create_result("empty", content=WholeExceptContent(base=updated.id, excluded_parts=[[0]]), origin=Origin(at="remove"))
    state = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset([empty.id])})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    assert result.status == "complete", result.diagnostics
    scope = result.records.get("ir_process").events[int(filtered)]
    assert scope.instances == [] and len(scope.collections) == 1
    result.records.validate(require_complete=True)
    restored = PropagationRecords.from_dict(result.records.to_dict(), cfg=result.records.cfg, annotation=annotation,
        data_registry=result.registry, initial_data=result.initial_data, initial_state=result.initial_state)
    assert restored.to_dict() == result.records.to_dict()
    assert all(data.origin.part_of is None for data in [result.registry.get(entry["data"]["id"])
                                                      for entry in result.registry.to_dict()["records"]])


def test_empty_and_open_candidate_collections_keep_both_scope_bindings():
    _, _, result, sources = solve([], None, filtered=True)
    assert result.status == "complete", result.diagnostics
    scope = result.records.get("ir_process").events[1]
    assert len(scope.collections) == 2 and len(scope.instances) == 1
    assert {result.registry.get(value).content.base for value in scope.collections} == set(sources)


def test_partial_known_members_and_unknown_remainder_both_propagate():
    cfg, annotation = fixture()
    registry = DataRegistry("partial-members")
    collection = registry.register_source("collection", acquired_from="fixture")
    member = registry.register_part(collection.id, [0], content=LiteralContent(
        value={"recipient": "known-recipient", "payload": "known-payload"}))
    state = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset([collection.id])})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    assert result.status == "complete", result.diagnostics
    instances = result.records.get("ir_process").events[0].instances
    assert len(instances) == 2 and member.id in {instance.element for instance in instances}
    known = next(instance for instance in instances if instance.element == member.id)
    inputs = known.body[-1].atomic_ops[0].inputs
    assert [result.registry.get(next(iter(value))).content.value for value in inputs[:2]] == ["known-recipient", "known-payload"]


def test_collection_overlay_retains_updated_member_fields():
    cfg, annotation = fixture()
    registry = DataRegistry("overlay-members")
    base = registry.register_source("collection", acquired_from="fixture", content=LiteralContent(
        value=[{"recipient": "original-recipient", "payload": "original-payload"}]))
    replacement = registry.create_result("replacement", content=LiteralContent(value="changed-payload"), origin=Origin(at="replacement"))
    collection = registry.create_result("updated", content=FieldUpdatesContent(base=base.id, updates=[
        DataPart(path=[0, "payload"], data=replacement.id)]), origin=Origin(at="update", inputs=[base.id, replacement.id]))
    state = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset([collection.id])})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    assert result.status == "complete", result.diagnostics
    instance = result.records.get("ir_process").events[0].instances[0]
    assert instance.collection == collection.id
    values = instance.body[-1].atomic_ops[0].inputs
    assert [result.registry.get(next(iter(value))).content.value for value in values[:2]] == ["original-recipient", "changed-payload"]


def test_missing_member_field_keeps_nested_diagnostic_and_does_not_drop_candidate():
    _, _, result, _ = solve([{"recipient": "a", "payload": "alpha"}, {"recipient": "b"}])
    assert result.status == "incomplete"
    assert result.coverage["ir_process"] == "unresolved_binding"
    missing = [item for item in result.diagnostics if item["code"] == "missing_part"]
    assert missing and all(item["instruction_id"] == "ir_process" for item in missing)
    assert all(item["event_index"] == 0 and item["body_event_index"] == 0
               and item["op_index"] == 1 for item in missing)
    assert "ir_process" not in result.records.records_dict()


def test_uncertain_effect_order_keeps_raw_and_clean_versions_per_member():
    body = [
        {"effect_index": 0, "atomic_ops": [operation("deliver", inputs=[local("item")], target="model")]},
        {"effect_index": 1, "atomic_ops": [operation("exclude_parts", input=local("item"), paths=[["secret"]], output="clean")]},
        {"effect_index": 2, "atomic_ops": [operation("deliver", inputs=[local("clean")], target="model")]},
    ]
    _, _, result, _ = solve(None, None, body=body, effects=["model_observe", "transform", "model_observe"], uncertain=True)
    assert result.status == "complete", result.diagnostics
    instances = result.records.get("ir_process").events[0].instances
    assert len(instances) == 2
    for instance in instances:
        raw = next(iter(instance.body[0].atomic_ops[0].inputs[0]))
        clean = next(iter(instance.body[2].atomic_ops[0].inputs[0]))
        assert raw == instance.element and raw != clean
        assert result.registry.get(clean).content.base == raw
    assert result.records.get("ir_process").order == "partial"


def test_records_snapshot_roundtrip_and_scope_reference_validation():
    cfg, annotation, result, _ = solve(None, filtered=True)
    assert result.status == "complete", result.diagnostics
    snapshot = result.records.to_dict()
    assert snapshot["schema_version"] == "skillflow-propagation-record-v9"
    restored = PropagationRecords.from_dict(snapshot, cfg=result.records.cfg, annotation=annotation,
        data_registry=result.registry, initial_data=result.initial_data, initial_state=result.initial_state)
    assert restored.to_dict() == snapshot
    # Validation reads Data relationships; it must not create fresh member or
    # part identities while checking an already completed record.
    data_before = result.registry.to_dict()
    result.records.validate(require_complete=True)
    assert result.registry.to_dict() == data_before
    damaged = result.records.get("ir_process").model_dump(mode="json")
    damaged["events"][1]["instances"][0]["element"] = "missing"
    with pytest.raises(ValueError, match="unknown Data"):
        result.records.put("ir_process", IRFlowRecord.model_validate(damaged))
    damaged = result.records.get("ir_process").model_dump(mode="json")
    instance = damaged["events"][1]["instances"][0]
    instance["element"] = instance["collection"]
    with pytest.raises(ValueError, match="member|element"):
        result.records.put("ir_process", IRFlowRecord.model_validate(damaged))
    damaged = result.records.get("ir_process").model_dump(mode="json")
    damaged["events"][1]["instances"][0]["body"].pop()
    with pytest.raises(ValueError, match="body event coverage"):
        result.records.put("ir_process", IRFlowRecord.model_validate(damaged))
    damaged = result.records.get("ir_process").model_dump(mode="json")
    damaged["events"][1]["instances"] = []
    with pytest.raises(ValueError, match="not explicitly empty"):
        result.records.put("ir_process", IRFlowRecord.model_validate(damaged))
    damaged = result.records.get("ir_process").model_dump(mode="json")
    damaged["events"][1]["collections"] = [damaged["events"][1]["instances"][0]["element"]]
    with pytest.raises(ValueError, match="absent from scope candidates"):
        result.records.put("ir_process", IRFlowRecord.model_validate(damaged))


def test_worklist_order_and_control_cycle_reach_same_stable_member_records():
    cfg, annotation, result, _ = solve(None, filtered=True)
    assert result.status == "complete", result.diagnostics
    cfg["blocks"]["main"]["instructions"][-1]["opcode"] = "dispatch"
    cfg["edges"].append({"source_block_id": "main", "target_block_id": "main"})
    first = propagate(cfg, annotation)
    second = propagate(cfg, annotation, schedule="lifo")
    assert first.status == second.status == "complete"
    assert first.registry.to_dict() == second.registry.to_dict()
    assert first.records.records_dict() == second.records.records_dict()


def test_member_scope_cannot_escape_as_public_output():
    cfg, annotation = fixture()
    cfg["blocks"]["main"]["instructions"][0]["outputs"] = [{"type": "result", "identifier": "escaped"}]
    annotation["transfer_specs"]["ir_process"]["output_bindings"] = [
        {"output_index": 0, "value": local("payload"), "evidences": [deepcopy(EVIDENCE)]}]
    with pytest.raises(ValueError, match="undefined local"):
        propagate(cfg, annotation)


def test_filter_result_feedback_is_still_rejected_before_solving():
    cfg, annotation = fixture(filtered=True)
    cfg["blocks"]["main"]["instructions"][-1]["opcode"] = "dispatch"
    cfg["edges"].append({"source_block_id": "main", "target_block_id": "source"})
    annotation["profiles"]["ir_process"] = profile(["transform", "transform", "net_send", "context_write"])
    annotation["transfer_specs"]["ir_process"]["events"].append({"effect_index": 3, "atomic_ops": [
        operation("write", target="collection", mode="replace", input=local("selected"))]})
    result = propagate(cfg, annotation)
    assert result.status == "unsupported_feedback"
    assert result.stats["block_evaluations"] == 0
    assert any(position.get("op_index") == 0 for diagnostic in result.diagnostics
               for position in diagnostic.get("operations", []))


def test_full_collection_scope_input_can_seed_a_context_operand():
    cfg, annotation = fixture()
    cfg["blocks"]["main"]["instructions"][0]["inputs"] = [{"type": "context_key", "identifier": "collection"}]
    cfg["blocks"]["main"]["data_source_kind"] = "context"
    cfg["blocks"]["main"]["instructions"][0]["outputs"] = [{"type": "result", "identifier": "read_again"}]
    annotation["transfer_specs"]["ir_process"]["output_bindings"] = [
        {"output_index": 0, "value": input_ref(), "evidences": [deepcopy(EVIDENCE)]}]
    # for_each reads the collection input; the body only consumes its item.
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    assert len(result.records.get("ir_process").events[0].instances) == 1


def test_scope_body_has_no_dynamic_context_reads_or_shared_writes():
    cfg, annotation = fixture()
    cfg["blocks"]["main"]["instructions"][0]["inputs"].append({"type": "context_key", "identifier": "collection"})
    annotation["transfer_specs"]["ir_process"]["events"][0]["body"][1]["atomic_ops"][0]["inputs"] = [input_ref(1)]
    with pytest.raises(ValueError, match="context"):
        propagate(cfg, annotation)
