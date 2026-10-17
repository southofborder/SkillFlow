"""DOE material selects recorded facts without changing data or judging necessity."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from skillflow.common.paths import project_root
from tests.doe.helpers import fact_fixture
from skillflow.common.source_evidence import _digest
from skillflow.doe.material import prepare_doe_material, validate_doe_material
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from skillflow.propagation.contracts.runtime_contract import runtime_contract_binding
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.facts import resolved_sink_boundaries
from tests.doe.components import Components
from skillflow.propagation.material import prepare_material


CASES = project_root() / "experiments/propagation/runs/sink-tightening-v1-20261002-205045/cases"


def _source():
    text = "# 测试任务\n\n保留正文原值；不得传递令牌。\n"
    digest = hashlib.sha256(text.encode()).hexdigest()
    source = {"files": [{"path": "SKILL.md", "content": text, "sha256": digest}],
              "source_sha256": _digest([{"path": "SKILL.md", "sha256": digest}])}
    metadata = {"files": [{"path": "SKILL.md", "size": len(text.encode()), "kind": "markdown",
                           "raw_sha256": digest, "decoded_sha256": digest}],
                "boundaries": {"binary_files": [], "uninterpreted_code_files": [],
                               "notice": "未执行 Skill。"}}
    return source


def _data(identity, content=None, origin=None):
    return {"id": identity, "content": content or {"form": "opaque"},
            "origin": {"at": None, "acquired_from": None, "part_of": None, "path": None,
                       "inputs": [], "dependencies": [], **(origin or {})},
            "annotations": {"description": None, "sensitivity": [], "evidences": []}}


def _state(**positions):
    return {"bindings": [{"location": {"kind": kind, "name": name}, "data_ids": values}
                          for key, values in positions.items() for kind, name in [key.split(":", 1)] if values]}


def _instruction(identity, opcode="abstract", *, inputs=None, outputs=None):
    return {"id": identity, "opcode": opcode, "inputs": inputs or [], "outputs": outputs or []}


def _op(op, inputs=(), outputs=(), endpoints=(), changes=(), **extra):
    return {"op": op, "inputs": list(inputs), "outputs": list(outputs),
            "endpoints": list(endpoints), "changes": list(changes), **extra}


def _record(events, entry=None, exit=None, order="fixed", precedence=None):
    return {"order": order, "precedence": precedence or [], "entry_state": entry or {"bindings": []},
            "exit_state": exit or {"bindings": []}, "events": events}


def _event(effect, *ops):
    return {"effect": effect, "atomic_ops": list(ops)}


def _handoff(instructions, records, data, *, locations=None):
    locations = locations or {"model": {"kind": "model_context", "name": "processor",
                                        "access_scope": "recipient", "retention": None, "operand_refs": []}}
    cfg={"entry_block_id": "main", "blocks": {"main": {
        "block_id": "main", "block_name": "main", "instructions": instructions}}, "edges": []}
    from tests.doe.helpers import source_task
    material=prepare_material(_source(), cfg, task_baseline=source_task(_source()))
    return Components(source=_source(),cfg=cfg,locations=locations,
        runtime_contract=runtime_contract(), sinks=resolved_sink_boundaries(locations,records),
        actions={ir["id"]:{"operator":[]} for ir in instructions},data=data,records=records,
        status="complete",coverage={ir["id"]:"processed" for ir in instructions}, diagnostics=[],
        material=material, source_metadata={}, annotation={})


def _versions_fixture():
    whole = _data("whole", {"form": "known_parts", "parts": [{"path": ["token"], "data": "token"}],
                            "parts_complete": False}, {"acquired_from": "storage:document"})
    token = _data("token", origin={"part_of": "whole", "path": ["token"]})
    clean = _data("clean", {"form": "whole_except", "base": "whole", "excluded_parts": [["token"]]},
                  {"at": "opaque descriptive text, not a JSON operation coordinate", "inputs": ["whole"],
                   "dependencies": [{"data": "whole", "relation": "derived"}]})
    result = {"type": "result", "identifier": "selected_result"}
    model = {"kind": "model_context", "name": "processor"}
    entry = _state(**{"runtime_context:document": ["whole"]})
    exit = _state(**{"runtime_context:document": ["whole"], "result:selected_result": ["clean"]})
    records = {
        "ir_process": _record([
            _event("model_observe", _op("deliver", [["whole"], ["whole"]], endpoints=[model])),
            _event("transform", _op("exclude_parts", [["whole"]], [["clean"]])),
            _event("model_observe", _op("deliver", [["clean"]], endpoints=[model]))], entry, exit),
        "ir_return": _record([], exit, exit)}
    return _handoff([_instruction("ir_process", outputs=[result]),
                     _instruction("ir_return", "return", inputs=[result])], records, [whole, token, clean])


def _plain(material):
    return material.model_dump(mode="json")


def _operation_material(material, instruction_id=None, op=None):
    return {key: value for key, value in material["shared_info"]["operations"].items()
            if (instruction_id is None or value["position"]["instruction_id"] == instruction_id)
            and (op is None or value["record"]["op"] == op)}


def _memory_fixture(update="strong", *, partial=False):
    target = {"kind": "storage", "name": "cache"}
    model = {"kind": "model_context", "name": "processor"}
    before = _state(**{"storage:cache": ["old"]})
    current = ["old", "new"] if update == "weak" else (["new"] if update == "strong" else [])
    after = _state(**{"storage:cache": current})
    change = {"location": target, "before": ["old"], "after": current, "update": update}
    events = [_event("fs_write", _op("write", [["old"]], endpoints=[target], changes=[{
        "location": target, "before": [], "after": ["old"], "update": "strong"}]))]
    records = {"ir_first": _record(events, exit=before),
               "ir_change": _record([_event("fs_write", _op("write", [] if update == "delete" else [["new"]],
                                                                          endpoints=[target], changes=[change]))], before, after),
               "ir_return": _record([], after, after)}
    instructions = [_instruction("ir_first"), _instruction("ir_change")]
    if current:
        result = {"type": "result", "identifier": "read_result"}
        read_exit = _state(**{"storage:cache": current, "result:read_result": current})
        records["ir_read"] = _record([_event("fs_read", _op("read", outputs=[current], endpoints=[target])),
                                       _event("model_observe", _op("deliver", [current], endpoints=[model]))],
                                      after, read_exit, order="partial" if partial else "fixed")
        records["ir_return"] = _record([], read_exit, read_exit)
        instructions.append(_instruction("ir_read", outputs=[result]))
        instructions.append(_instruction("ir_return", "return", inputs=[result]))
    else:
        instructions.append(_instruction("ir_return", "return"))
    locations = {"cache": {**target, "access_scope": "task", "retention": "persistent", "operand_refs": []},
                 "model": {**model, "access_scope": "recipient", "retention": None, "operand_refs": []}}
    return _handoff(instructions, records, [_data("old"), _data("new")], locations=locations)


@pytest.mark.parametrize("case", ["001", "010", "013"])
def test_fixed_cases_are_standalone_deterministic_and_do_not_mutate_sources(case, tmp_path, monkeypatch):
    path = CASES / case / "propagation/doe-input.json"
    original = path.read_bytes()
    raw = fact_fixture(path)
    baseline = deepcopy(raw)
    monkeypatch.setattr(DataRegistry, "resolve_part", lambda *args, **kwargs: pytest.fail("slice must be read-only"))
    first = _plain(prepare_doe_material(raw))
    assert first == _plain(prepare_doe_material(raw))
    assert baseline.data == raw.data and baseline.records == raw.records
    assert path.read_bytes() == original
    assert len(first["sinks"]) == len(raw.sinks)
    assert first["source"] == raw.source
    assert first["task"]["basis"] == "declared_skill"
    assert first["runtime_contract"] == {**runtime_contract(), "sha256": runtime_contract_binding(runtime_contract())["sha256"]}
    assert "entry_state" not in first["shared_info"] and "exit_state" not in first["shared_info"]
    assert not {"reviews", "sensitivity", "findings", "task_basis"}.intersection(first)
    validate_doe_material(first)


def test_user_task_is_preserved_without_extracting_requirements():
    text = "只处理订阅用户；不得改变正文。\n保留空行：\n\n"
    facts = _versions_fixture()
    facts.material["user_request"] = text
    material = _plain(prepare_doe_material(facts))
    assert material["task"] == {"basis": "user_request", "text": text}
    assert material["source"]["files"][0]["content"] == _source()["files"][0]["content"]


def test_zero_argument_external_delivery_keeps_boundary_without_fabricated_data():
    target = {"kind": "tool", "name": "service"}
    raw = _handoff([_instruction("ir_call"), _instruction("ir_return", "return")],
                   {"ir_call": _record([_event(None, _op("deliver", endpoints=[target]))]),
                    "ir_return": _record([])}, [], locations={
                        "tool": {**target, "access_scope": "recipient", "retention": None, "operand_refs": []}})
    material = _plain(prepare_doe_material(raw))
    assert len(material["sinks"]) == 1
    sink = material["sinks"][0]
    assert sink["sink"]["boundary"]["sink_type"] == "external_tool"
    assert sink["backward_slice"]["data"] == []
    assert material["shared_info"]["operations"][sink["sink"]["operations"][0]]["record"]["inputs"] == []


def test_same_ir_observations_keep_versions_duplicate_arguments_and_return_identity():
    material = _plain(prepare_doe_material(_versions_fixture()))
    operations = _operation_material(material)
    assert len(material["sinks"]) == 2
    first, second = sorted(material["sinks"], key=lambda item: item["sink"]["boundary"]["event_index"])
    first_record = operations[first["sink"]["operations"][0]]["record"]
    second_record = operations[second["sink"]["operations"][0]]["record"]
    assert first_record["inputs"] == [["whole"], ["whole"]]
    assert second_record["inputs"] == [["clean"]]
    assert "whole" in second["backward_slice"]["data"]  # source explanation, not payload
    assert material["shared_info"]["data"]["clean"]["content"]["excluded_parts"] == [["token"]]
    returns = [link for link in material["shared_info"]["links"].values() if link["kind"] == "result_use"
               and link["target"] == "ir_return"]
    assert returns and returns[0]["result"] == "selected_result" and returns[0]["data_ids"] == ["clean"]
    assert not _operation_material(material, "ir_return")
    assert "ir_return" in second["usage_context"]["instructions"]


def test_possible_dependencies_remain_influence_and_do_not_claim_plaintext():
    raw = _versions_fixture()
    unknown = _data("unknown", origin={"inputs": ["token"],
                                        "dependencies": [{"data": "token", "relation": "possible"}]})
    raw.data.append(unknown)
    process = raw.records["ir_process"]
    process["events"][1] = _event("transform", _op("compute", [["token"]], [["unknown"]]))
    process["events"][2]["atomic_ops"][0]["inputs"] = [["unknown"]]
    for record in raw.records.values():
        for state in (record["entry_state"], record["exit_state"]):
            for binding in state["bindings"]:
                if binding["location"]["kind"] == "result": binding["data_ids"] = ["unknown"]
    material = _plain(prepare_doe_material(raw))
    sink = next(item for item in material["sinks"] if item["sink"]["boundary"]["event_index"] == 2)
    assert {"unknown", "token", "whole"}.issubset(sink["backward_slice"]["data"])
    assert material["shared_info"]["data"]["unknown"]["content"] == {"form": "opaque"}
    assert material["shared_info"]["data"]["unknown"]["origin"]["dependencies"] == [{"data": "token", "relation": "possible"}]


def test_conditional_observation_control_is_context_not_payload():
    raw = _versions_fixture()
    raw.data.append(_data("guard"))
    operation = raw.records["ir_process"]["events"][2]["atomic_ops"][0]
    operation["inputs"] = [["clean"], ["guard"]]
    operation["when_input_index"] = 1
    material = _plain(prepare_doe_material(raw))
    sink = next(item for item in material["sinks"] if item["sink"]["boundary"]["event_index"] == 2)
    actual = material["shared_info"]["operations"][sink["sink"]["operations"][0]]["record"]
    from skillflow.propagation.conditions import payload_inputs
    assert payload_inputs(actual) == [["clean"]]
    assert actual["inputs"][actual["when_input_index"]] == ["guard"]
    assert "guard" in material["shared_info"]["data"]


def test_actual_for_each_keeps_instance_and_same_element_parameter_pairing():
    raw = fact_fixture(CASES / "001/propagation/doe-input.json")
    material = _plain(prepare_doe_material(raw))
    item = next(s for s in material["sinks"] if s["sink"]["boundary"]["sink_type"] == "external_tool")
    scoped = [material["shared_info"]["operations"][op] for op in item["sink"]["operations"]]
    assert scoped and all(op["position"]["instance_index"] is not None for op in scoped)
    for operation in scoped:
        position = operation["position"]
        original = raw.records[position["instruction_id"]]["events"][position["event_index"]]["instances"][position["instance_index"]]
        expected = original["body"][position["body_event_index"]]["atomic_ops"][position["op_index"]]
        assert operation["record"]["inputs"] == expected["inputs"] and len(expected["inputs"]) == 2
        recipient, body = [values[0] for values in expected["inputs"]]
        data = material["shared_info"]["data"]
        assert data[recipient]["origin"]["path"][:-1] == data[body]["origin"]["path"][:-1]
        assert data[recipient]["origin"]["part_of"] == data[body]["origin"]["part_of"]
    assert item["context"]["scope_ids"]


def test_two_candidate_instances_with_same_element_are_not_collapsed():
    raw = fact_fixture(CASES / "001/propagation/doe-input.json")
    ir_id, event_index, event = next((ir, index, event) for ir, record in raw.records.items()
                                    for index, event in enumerate(record["events"])
                                    if event.get("kind") == "for_each")
    alternate = deepcopy(event["instances"][0])
    # These are two recorded candidate bodies, not actual collection members.
    # Keep the whole body so no independent parameter unions recreate a third pair.
    alternate["body"][-1]["atomic_ops"][0]["inputs"].reverse()
    event["instances"].append(alternate)
    material = _plain(prepare_doe_material(raw))
    sink = next(s for s in material["sinks"] if s["sink"]["boundary"]["sink_type"] == "external_tool")
    operations = [material["shared_info"]["operations"][identity] for identity in sink["sink"]["operations"]]
    assert {op["position"]["instance_index"] for op in operations} == {0, 1}
    for operation in operations:
        position = operation["position"]
        expected = raw.records[ir_id]["events"][event_index]["instances"][position["instance_index"]]["body"][-1]["atomic_ops"][0]
        assert operation["record"]["inputs"] == expected["inputs"]
    indexed = material["shared_info"]["operations"]
    for link in material["shared_info"]["links"].values():
        if link["kind"] != "produces_consumes": continue
        source, target = indexed[link["source"]]["position"], indexed[link["target"]]["position"]
        if source["instruction_id"] == target["instruction_id"] == ir_id and source["instance_index"] is not None and target["instance_index"] is not None:
            assert source["instance_index"] == target["instance_index"]


@pytest.mark.parametrize("update,expected", [("strong", {"ir_change"}), ("weak", {"ir_first", "ir_change"})])
def test_saved_reads_use_reaching_definitions_not_only_shared_data_ids(update, expected):
    material = _plain(prepare_doe_material(_memory_fixture(update)))
    operations = material["shared_info"]["operations"]
    reads = {key for key, op in operations.items() if op["record"]["op"] == "read"}
    links = [link for link in material["shared_info"]["links"].values() if link["kind"] == "saved_read" and link["target"] in reads]
    assert {operations[link["source"]]["position"]["instruction_id"] for link in links} == expected
    assert all(link["data_ids"] for link in links)


def test_overwriting_with_identical_data_still_ends_old_write_identity():
    raw = _memory_fixture("strong")
    # Equal values do not make these two static writes the same reaching definition.
    for record in raw.records.values():
        for state in (record["entry_state"], record["exit_state"]):
            for binding in state["bindings"]:
                binding["data_ids"] = ["old" if value == "new" else value for value in binding["data_ids"]]
        for event in record["events"]:
            for operation in event["atomic_ops"]:
                operation["inputs"] = [["old" if value == "new" else value for value in values] for values in operation["inputs"]]
                operation["outputs"] = [["old" if value == "new" else value for value in values] for values in operation["outputs"]]
                for change in operation["changes"]:
                    change["after"] = ["old" if value == "new" else value for value in change["after"]]
    material = _plain(prepare_doe_material(raw))
    operations = material["shared_info"]["operations"]
    links = [link for link in material["shared_info"]["links"].values() if link["kind"] == "saved_read"]
    assert links
    assert {operations[link["source"]]["position"]["instruction_id"] for link in links} == {"ir_change"}


def test_delete_has_no_sink_and_no_fabricated_future_read():
    raw = _memory_fixture("delete")
    material = _plain(prepare_doe_material(raw))
    assert len(material["sinks"]) == 1
    assert all(s["sink"]["boundary"]["instruction_id"] != "ir_change" for s in material["sinks"])
    assert not any(link["kind"] == "saved_read" for link in material["shared_info"]["links"].values())
    assert material["sinks"][0]["sink"]["boundary"]["sink_type"] == "storage_write"


def test_partial_order_is_retained_not_relabelled_fixed():
    material = _plain(prepare_doe_material(_memory_fixture("weak", partial=True)))
    observed = next(s for s in material["sinks"] if s["sink"]["boundary"]["instruction_id"] == "ir_read")
    assert "ir_read" in observed["context"]["partial_ir_ids"]


def test_partial_events_still_respect_atomic_order_when_matching_requests():
    endpoint = {"kind": "tool", "name": "service"}
    result = {"type": "result", "identifier": "response"}
    state = _state(**{"result:response": ["response_data"]})
    # A response followed by a later identical request does not belong to that request.
    # Partial event order does not reverse an event's intrinsic atomic-op order.
    record = _record([_event(None,
                            _op("receive", [["request"]], [["response_data"]], [endpoint]),
                            _op("deliver", [["request"]], endpoints=[endpoint]))],
                     exit=state, order="partial")
    data = [_data("request"), _data("response_data", origin={"acquired_from": "tool:service",
            "inputs": ["request"], "dependencies": [{"data": "request", "relation": "possible"}]})]
    raw = _handoff([_instruction("ir_call", outputs=[result]), _instruction("ir_return", "return", inputs=[result])],
                   {"ir_call": record, "ir_return": _record([], state, state)}, data,
                   locations={"service": {**endpoint, "access_scope": "recipient", "retention": None, "operand_refs": []}})
    material = _plain(prepare_doe_material(raw))
    assert not any(link["kind"] == "request_response" for link in material["shared_info"]["links"].values())


@pytest.mark.parametrize("barrier", ["strong", "delete"])
def test_required_partial_memory_barriers_end_previous_write_identity(barrier):
    target = {"kind": "storage", "name": "cache"}
    state = _state(**{"storage:cache": ["same"]})
    end = _state(**{"storage:cache": ["same"], "result:r": ["same"]})
    first = _record([_event("fs_write", _op("write", [["same"]], endpoints=[target], changes=[{
        "location": target, "before": [], "after": ["same"], "update": "strong"}]))], exit=state)
    events = [_event("fs_write", _op("write", [["same"]] if barrier == "strong" else [], endpoints=[target],
                                      changes=[{"location": target, "before": ["same"],
                                                "after": ["same"] if barrier == "strong" else [], "update": barrier}]))]
    if barrier == "delete":
        # Reintroducing a previously existing value does not revive a deleted write.
        events.append(_event("fs_write", _op("write", [["same"]], endpoints=[target], changes=[{
            "location": target, "before": [], "after": ["same"], "update": "weak"}])))
    events.append(_event("fs_read", _op("read", outputs=[["same"]], endpoints=[target])))
    precedence = [{"before": {"event_index": index, "op_index": 0, "body_event_index": None},
                   "after": {"event_index": index + 1, "op_index": 0, "body_event_index": None}}
                  for index in range(len(events) - 1)]
    second = _record(events, state, end, order="partial", precedence=precedence)
    result = {"type": "result", "identifier": "r"}
    raw = _handoff([_instruction("ir_first"), _instruction("ir_second", outputs=[result]),
                     _instruction("ir_return", "return", inputs=[result])],
                    {"ir_first": first, "ir_second": second, "ir_return": _record([], end, end)},
                    [_data("same")], locations={
                        "cache": {**target, "access_scope": "task", "retention": "persistent", "operand_refs": []}})
    material = _plain(prepare_doe_material(raw))
    operations = material["shared_info"]["operations"]
    links = [link for link in material["shared_info"]["links"].values() if link["kind"] == "saved_read"]
    assert links
    assert {operations[link["source"]]["position"]["instruction_id"] for link in links} == {"ir_second"}
    assert {operations[link["source"]]["position"]["event_index"] for link in links} == {0 if barrier == "strong" else 1}


def test_partial_input_preserves_missing_coverage_without_inventing_sinks():
    raw = _versions_fixture()
    raw.status = "incomplete"
    del raw.records["ir_return"]
    raw.coverage["ir_return"] = "unresolved_binding"
    raw.diagnostics = [{"code": "unresolved_binding", "instruction_id": "ir_return", "reason": "待解析返回值"}]
    material = _plain(prepare_doe_material(raw))
    assert len(material["sinks"]) == 2
    assert not _operation_material(material, "ir_return")
    assert any(d["instruction_id"] == "ir_return" for s in material["sinks"] for d in s["context"]["diagnostics"])


@pytest.mark.parametrize("mutation", ["unknown_data", "unknown_op", "missing_sink", "unknown_ir", "runtime", "old_version"])
def test_material_reference_or_contract_tampering_is_rejected(mutation):
    raw = _plain(prepare_doe_material(_versions_fixture()))
    if mutation == "unknown_data": raw["sinks"][0]["backward_slice"]["data"].append("missing")
    if mutation == "unknown_op": raw["sinks"][0]["sink"]["operations"].append("missing")
    if mutation == "missing_sink": raw["sinks"] = raw["sinks"][:-1]
    if mutation == "unknown_ir": raw["sinks"][0]["usage_context"]["instructions"].append("ir_missing")
    if mutation == "runtime": raw["runtime_contract"]["sha256"] = "0" * 64
    if mutation == "old_version": raw["schema_version"] = "skillflow-doe-material-v0"
    with pytest.raises(ValueError): validate_doe_material(raw)


def test_invalid_upstream_fact_is_not_silently_repaired():
    raw = _versions_fixture()
    raw.records["ir_process"]["events"][0]["atomic_ops"][0]["inputs"] = [["absent"]]
    with pytest.raises(ValueError): prepare_doe_material(raw)


@pytest.mark.parametrize("mutation", ["source_content", "retired_source_index", "location_operand", "missing_action",
                                      "duplicate_operator", "block_membership", "result_identifier"])
def test_standalone_material_checks_source_and_projected_reference_closure(mutation):
    raw = _plain(prepare_doe_material(_versions_fixture()))
    if mutation == "source_content": raw["source"]["files"][0]["content"] = "Changed task with original digest retained."
    if mutation == "retired_source_index": raw["source"]["source_index"] = []
    if mutation == "location_operand":
        raw["shared_info"]["locations"]["model"]["operand_refs"] = [{"instruction_id": "ir_process", "side": "input", "index": 500}]
    if mutation == "missing_action": del raw["shared_info"]["actions"]["ir_process"]
    if mutation == "duplicate_operator": raw["shared_info"]["actions"]["ir_process"]["operator"] = ["llm", "llm"]
    if mutation == "block_membership": raw["shared_info"]["blocks"]["main"]["instruction_ids"].remove("ir_process")
    if mutation == "result_identifier":
        from skillflow.doe.material import _id
        key, link = next((key, link) for key, link in raw["shared_info"]["links"].items() if link["kind"] == "result_use")
        del raw["shared_info"]["links"][key]
        link["result"] = "nonexistent_result"
        new_key = _id("link_", link)
        raw["shared_info"]["links"][new_key] = link
        for sink in raw["sinks"]:
            sink["usage_context"]["links"] = [new_key if value == key else value for value in sink["usage_context"]["links"]]
    with pytest.raises(ValueError): validate_doe_material(raw)


@pytest.mark.parametrize("mutation", ["classification", "target"])
def test_resealed_sink_coordinates_do_not_override_real_boundary_rules(mutation):
    from skillflow.doe.material import _id
    raw = _plain(prepare_doe_material(_versions_fixture()))
    sink = raw["sinks"][0]["sink"]
    if mutation == "classification":
        sink["boundary"]["sink_type"] = "network_send"
        sink["boundary"]["exposure_level"] = 3
    else:
        raw["shared_info"]["locations"]["other"] = {"kind": "remote", "name": "elsewhere", "access_scope": "recipient", "retention": None, "operand_refs": []}
        sink["boundary"]["target"] = "other"
    # Integrity identifiers cannot substitute for semantic structural consistency.
    sink["id"] = _id("sink_", sink["boundary"])
    with pytest.raises(ValueError): validate_doe_material(raw)


def test_member_scope_cannot_relabel_a_field_as_its_collection_element():
    raw = _plain(prepare_doe_material(fact_fixture(CASES / "001/propagation/doe-input.json")))
    scope = next(iter(raw["shared_info"]["scopes"].values()))
    scope["element"] = next(identity for identity, data in raw["shared_info"]["data"].items()
                            if data["origin"].get("path") and data["origin"]["path"][-1] == "recipient")
    with pytest.raises(ValueError): validate_doe_material(raw)
