"""Standalone DOE input preserves facts, not annotation evidence or judgments."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy

import pytest

from skillflow.propagation.data import DataRegistry
from skillflow.propagation.handoff import build_doe_input
from skillflow.propagation.handoff import build_doe_source
from skillflow.propagation.handoff import load_doe_input
from skillflow.propagation.handoff import validate_doe_input
from skillflow.propagation.handoff import resolved_sink_boundaries
from skillflow.common.source_evidence import _digest
from skillflow.propagation.contracts.runtime_contract import execution_model
from skillflow.propagation.contracts.runtime_contract import execution_model_binding
from skillflow.propagation.material import prepare_material


def source_material():
    text = "# 测试\r\n\r\n读取文档并交给模型。\n"
    digest = hashlib.sha256(text.encode()).hexdigest()
    source = {"files": [{"path": "SKILL.md", "content": text, "sha256": digest}],
              "source_sha256": _digest([{"path": "SKILL.md", "sha256": digest}])}
    metadata = {"files": [
        {"path": "SKILL.md", "size": len(text.encode()), "kind": "markdown", "raw_sha256": digest,
         "decoded_sha256": digest},
        {"path": "asset.bin", "size": 2, "kind": "binary", "raw_sha256": hashlib.sha256(b"\x00\x01").hexdigest(),
         "decoded_sha256": None}],
        "boundaries": {"binary_files": ["asset.bin"], "uninterpreted_code_files": [], "notice": "二进制不进入文本分析。"}}
    return source, metadata


def handoff():
    source, metadata = source_material()
    registry = DataRegistry("handoff")
    data = registry.register_source("read", acquired_from="runtime_context:document")
    state = {"bindings": [{"location": {"kind": "runtime_context", "name": "document"}, "data_ids": [data.id]}]}
    cfg = {"entry_block_id": "main", "blocks": {"main": {"block_id": "main", "block_name": "main", "instructions": [
        {"id": "ir_view", "opcode": "view", "inputs": [{"type": "literal", "literal_value": "document"}], "outputs": []},
        {"id": "ir_return", "opcode": "return", "inputs": [], "outputs": []}]}}, "edges": []}
    locations = {"doc": {"kind": "runtime_context", "name": "document", "access_scope": "task", "retention": "task", "operand_refs": [
        {"instruction_id": "ir_view", "side": "input", "index": 0}]},
        "model": {"kind": "model_context", "name": "model", "access_scope": "recipient", "retention": None, "operand_refs": []}}
    return {"schema_version": "skillflow-doe-input-v7", "execution_model": execution_model_binding(execution_model()),
            "source": build_doe_source(source, metadata), "cfg": cfg,
            "locations": locations, "sink_boundaries": [{"instruction_id": "ir_view", "event_index": 0,
                "op_index": 0, "body_event_index": None, "scope": None, "target": "model", "sink_type": "model_observe", "exposure_level": 2}],
            "actions": {"ir_view": {"operator": ["llm"], "roles": ["sink"]},
                                                   "ir_return": {"operator": [], "roles": []}},
            "data": [data.model_dump(mode="json")], "status": "complete", "coverage": {"ir_view": "processed", "ir_return": "processed"},
            "diagnostics": [], "records": {
                "ir_view": {"order": "fixed", "precedence": [], "entry_state": deepcopy(state), "exit_state": deepcopy(state), "events": [
                    {"effect": "model_observe", "atomic_ops": [{"op": "deliver", "inputs": [[data.id]], "outputs": [],
                        "endpoints": [{"kind": "model_context", "name": "model"}], "changes": []}]}]},
                "ir_return": {"order": "fixed", "precedence": [], "entry_state": deepcopy(state), "exit_state": deepcopy(state), "events": []}}}


def test_standalone_load_preserves_source_binary_boundary_and_compact_records(tmp_path):
    raw = handoff()
    path = tmp_path / "doe-input.json"
    path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    checked = load_doe_input(path)
    assert checked == raw
    assert checked["source"]["files"][0]["content"].startswith("# 测试\r\n")
    assert checked["source"]["boundaries"]["binary_files"] == ["asset.bin"]
    assert list(tmp_path.iterdir()) == [path]
    assert set(checked) == {"schema_version", "execution_model", "source", "cfg", "locations", "sink_boundaries", "actions", "data", "records", "status", "coverage", "diagnostics"}


@pytest.mark.parametrize("field", ["annotation", "stats", "identity", "evidences", "transfer_specs"])
def test_business_file_rejects_audit_and_duplicate_wrappers(field):
    raw = handoff(); raw[field] = {}
    with pytest.raises(ValueError): validate_doe_input(raw)


@pytest.mark.parametrize("mutation", ["missing", "old_version", "digest", "full_rules", "old_doe"])
def test_standalone_contract_binding_rejects_missing_old_or_altered_identity(mutation):
    raw = handoff()
    if mutation == "missing": del raw["execution_model"]
    if mutation == "old_version": raw["execution_model"]["version"] = "wide-read-agent-v6"
    if mutation == "digest": raw["execution_model"]["sha256"] = "0" * 64
    if mutation == "full_rules": raw["execution_model"]["rules"] = execution_model()["rules"]
    if mutation == "old_doe": raw["schema_version"] = "skillflow-doe-input-v2"
    with pytest.raises(ValueError): validate_doe_input(raw)


def test_handoff_requires_explicit_actual_contract_without_default_substitution():
    demo = runpy.run_path(str(project_root() / "examples/propagation/propagation_demo.py"))
    from skillflow.propagation import propagate
    from skillflow.propagation.annotation.services import to_payload
    source, metadata, cfg, response, registry, state = demo["demo_inputs"]()
    payload = to_payload(response)
    solved = propagate(cfg, payload, initial_registry=registry, initial_state=state)
    with pytest.raises(TypeError, match="execution_model"):
        build_doe_input(source, cfg, payload, solved, source_metadata=metadata)
    contract = prepare_material(source, cfg)["execution_model"]
    changed = deepcopy(contract)
    changed["rules"][0]["text"] += " altered"
    with pytest.raises(ValueError, match="contract identity"):
        build_doe_input(source, cfg, payload, solved, source_metadata=metadata, execution_model=changed)
    actual = build_doe_input(source, cfg, payload, solved, source_metadata=metadata, execution_model=contract)
    assert actual["execution_model"] == execution_model_binding(contract)
    assert set(actual["execution_model"]) == {"version", "sha256"}
    assert "rules" not in actual["execution_model"]


@pytest.mark.parametrize("mutation", ["data_missing", "data_duplicate", "unknown_ir", "coverage_missing", "record_missing",
                                     "false_complete", "location_operand", "endpoint", "arity", "old_ref", "old_notes", "unknown_result"])
def test_handoff_rejects_inconsistent_records(mutation):
    raw = handoff(); op = raw["records"]["ir_view"]["events"][0]["atomic_ops"][0]
    if mutation == "data_missing": raw["data"] = []
    if mutation == "data_duplicate": raw["data"].append(deepcopy(raw["data"][0]))
    if mutation == "unknown_ir": raw["actions"]["ir_fake"] = raw["actions"]["ir_return"]
    if mutation == "coverage_missing": del raw["coverage"]["ir_return"]
    if mutation == "record_missing": del raw["records"]["ir_return"]
    if mutation == "false_complete":
        del raw["records"]["ir_return"]; raw["coverage"]["ir_return"] = "not_solved"
    if mutation == "location_operand": raw["locations"]["doc"]["operand_refs"][0]["index"] = 5
    if mutation == "endpoint": op["endpoints"][0]["name"] = "other-model"
    if mutation == "arity": op["outputs"] = [op["inputs"][0]]
    if mutation == "old_ref": op["inputs"][0] = {"ref": {"kind": "input", "index": 0}, "data_ids": op["inputs"][0]}
    if mutation == "old_notes": op["notes"] = ["old"]
    if mutation == "unknown_result": raw["records"]["ir_view"]["entry_state"]["bindings"][0]["location"] = {"kind": "result", "name": "missing"}
    with pytest.raises(ValueError): validate_doe_input(raw)


@pytest.mark.parametrize("mutation", ["missing_inventory", "decoded", "raw", "size", "boundary", "index", "missing_readable", "binary_text"])
def test_source_inventory_and_index_are_not_silently_normalized(mutation):
    raw = handoff(); source = raw["source"]
    if mutation == "missing_inventory": del source["inventory"]
    if mutation == "decoded": source["inventory"][0]["decoded_sha256"] = "0" * 64
    if mutation == "raw": source["inventory"][0]["raw_sha256"] = "0" * 64
    if mutation == "size": source["inventory"][0]["size"] += 1
    if mutation == "boundary": source["boundaries"]["binary_files"] = []
    if mutation == "index": source["index"][0]["start_line"] += 1
    if mutation == "missing_readable": source["inventory"] = source["inventory"][1:]
    if mutation == "binary_text": source["inventory"][1]["kind"] = "text"
    with pytest.raises(ValueError): validate_doe_input(raw)


def test_partial_order_does_not_make_a_converged_run_unsuccessful():
    raw = handoff()
    raw["records"]["ir_view"]["order"] = "partial"
    assert validate_doe_input(raw)["status"] == "complete"


def test_partial_run_keeps_unvisited_reachable_records_distinct_from_complete():
    raw = handoff(); raw["status"] = "incomplete"
    raw["records"] = {}; raw["coverage"] = {"ir_view": "unresolved_binding", "ir_return": "not_reached"}
    raw["sink_boundaries"] = []
    raw["diagnostics"] = [{"code": "unresolved_binding", "instruction_id": "ir_view", "reason": "输入尚未解析"}]
    assert validate_doe_input(raw)["records"] == {}


def test_duplicate_inputs_and_data_sensitivity_evidence_are_preserved():
    raw = handoff()
    op = raw["records"]["ir_view"]["events"][0]["atomic_ops"][0]
    op["inputs"] *= 2
    raw["data"][0]["annotations"] = {"description": None, "sensitivity": ["secret"], "evidences": ["user:label"]}
    checked = validate_doe_input(raw)
    assert len(checked["records"]["ir_view"]["events"][0]["atomic_ops"][0]["inputs"]) == 2
    assert checked["data"][0]["annotations"]["evidences"] == ["user:label"]


def test_invalid_json_duplicate_keys_and_wrong_version_fail():
    for value in ['{"schema_version": "x", "schema_version":"y"}', '{"n":NaN}', '[]']:
        with pytest.raises(ValueError): validate_doe_input(value)
    raw = handoff(); raw["schema_version"] = "skillflow-doe-input-v0"
    with pytest.raises(ValueError): validate_doe_input(raw)


@pytest.mark.parametrize("mutation", ["missing", "extra", "target", "type", "grade", "position", "scope", "duplicate", "payload"])
def test_standalone_sink_inventory_is_exact_and_program_derived(mutation):
    raw = handoff()
    item = raw["sink_boundaries"][0]
    if mutation == "missing": raw["sink_boundaries"] = []
    if mutation == "extra": raw["sink_boundaries"].append({**item, "instruction_id": "ir_return"})
    if mutation == "target": item["target"] = "doc"
    if mutation == "type": item["sink_type"] = "external_tool"
    if mutation == "grade": item["exposure_level"] = 1
    if mutation == "position": item["op_index"] = 1
    if mutation == "scope": item["body_event_index"] = 0; item["scope"] = "element"
    if mutation == "duplicate": raw["sink_boundaries"].append(deepcopy(item))
    if mutation == "payload": item["inputs"] = [[raw["data"][0]["id"]]]
    with pytest.raises(ValueError): validate_doe_input(raw)


@pytest.mark.parametrize("kind,scope,retention,effect,expected", [
    ("tool", "task", None, None, None),
    ("tool", "recipient", None, None, ("external_tool", 2)),
    ("storage", "task", "persistent", "fs_write", ("storage_write", 1)),
    ("storage", "task", "task", "fs_write", None),
    ("runtime_context", "task", "persistent", "context_write", ("context_save", 1)),
    ("runtime_context", "shared", "task", "context_write", ("context_save", 2)),
    ("storage", "public", "persistent", "fs_write", ("storage_write", 3)),
    ("remote", "recipient", None, "net_send", ("network_send", 2)),
    ("user", "recipient", None, "user_output", ("user_output", 2)),
])
def test_resolved_boundaries_apply_same_fixed_rules_to_real_data(kind, scope, retention, effect, expected):
    raw = handoff()
    target = {"kind": kind, "name": "destination", "access_scope": scope, "retention": retention, "operand_refs": []}
    raw["locations"]["target"] = target
    event = raw["records"]["ir_view"]["events"][0]
    event["effect"] = effect
    op = event["atomic_ops"][0]
    op["endpoints"] = [{"kind": kind, "name": "destination"}]
    if kind in {"storage", "runtime_context"}:
        op["op"] = "write"
        op["changes"] = [{"location": deepcopy(op["endpoints"][0]), "before": [],
                          "after": deepcopy(op["inputs"][0]), "update": "strong"}]
        raw["records"]["ir_view"]["exit_state"]["bindings"].append({"location": deepcopy(op["endpoints"][0]), "data_ids": deepcopy(op["inputs"][0])})
    raw["sink_boundaries"] = resolved_sink_boundaries(raw["locations"], raw["records"])
    checked = validate_doe_input(raw)
    if expected is None:
        assert checked["sink_boundaries"] == []
    else:
        assert [(item["sink_type"], item["exposure_level"]) for item in checked["sink_boundaries"]] == [expected]
        assert checked["records"]["ir_view"]["events"][0]["atomic_ops"][0]["inputs"] == op["inputs"]


def test_zero_argument_tool_delivery_and_delete_have_no_fabricated_payload():
    raw = handoff()
    raw["locations"]["tool"] = {"kind": "tool", "name": "service", "access_scope": "recipient", "retention": None, "operand_refs": []}
    event = raw["records"]["ir_view"]["events"][0]
    event["effect"] = None
    op = event["atomic_ops"][0]
    op["inputs"] = []
    op["endpoints"] = [{"kind": "tool", "name": "service"}]
    raw["sink_boundaries"] = resolved_sink_boundaries(raw["locations"], raw["records"])
    assert validate_doe_input(raw)["sink_boundaries"][0]["sink_type"] == "external_tool"
    event["effect"] = "context_write"
    raw["locations"]["doc"]["retention"] = "persistent"
    op.update(op="write", endpoints=[{"kind": "runtime_context", "name": "document"}],
              changes=[{"location": {"kind": "runtime_context", "name": "document"},
                        "before": [raw["data"][0]["id"]], "after": [], "update": "delete"}])
    raw["records"]["ir_view"]["exit_state"] = {"bindings": []}
    raw["sink_boundaries"] = []
    assert validate_doe_input(raw)["sink_boundaries"] == []


def test_build_projects_actual_solved_graph_and_retains_no_allocation_index():
    demo = runpy.run_path(str(project_root() / "examples/propagation/propagation_demo.py"))
    from skillflow.propagation import propagate
    from skillflow.propagation.annotation.services import to_payload
    source, metadata, cfg, response, registry, state = demo["demo_inputs"]()
    annotation = to_payload(response)
    solved = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    material = prepare_material(source, cfg)
    output = build_doe_input(source, cfg, annotation, solved, source_metadata=metadata,
                             execution_model=material["execution_model"])
    assert output["status"] == "complete"
    assert all(set(item) == {"id", "content", "origin", "annotations"} for item in output["data"])
    assert "evidences" not in output["actions"][next(iter(output["actions"]))]
    altered = deepcopy(annotation)
    altered["profiles"][next(iter(altered["profiles"]))]["operator"] = ["human"]
    with pytest.raises(ValueError, match="do not match"):
        build_doe_input(source, cfg, altered, solved, source_metadata=metadata,
                        execution_model=material["execution_model"])


def test_actual_unsupported_feedback_keeps_structured_operation_diagnostics():
    demo = runpy.run_path(str(project_root() / "examples/propagation/propagation_demo.py"))
    from skillflow.propagation import propagate
    ir, operand, local, input_ref = (demo[key] for key in ("instruction", "operand", "local", "input_ref"))
    cfg = {"entry_block_id": "loop", "blocks": {
        "loop": {"block_id": "loop", "block_name": "loop", "instructions": [
            ir("read", outputs=["B"]), ir("compute", [operand("B")], ["C"]), ir("write", [operand("C")]),
            ir("repeat", [{"type": "literal", "literal_value": True}], opcode="dispatch")]},
        "end": {"block_id": "end", "block_name": "end", "instructions": [ir("return", opcode="return")]}},
        "edges": [{"source_block_id": "loop", "target_block_id": target} for target in ("loop", "end")]}
    cfg, annotation = demo["fixture_annotation"](cfg, {
        "read": (["context_read"], [(0, [{"op": "read", "location": "doc", "output": "b"}])], [local("b")]),
        "compute": (["transform"], [(0, [{"op": "compute", "inputs": [input_ref()], "dependencies": ["possible"], "output": "c"}])], [local("c")]),
        "write": (["context_write"], [(0, [{"op": "write", "mode": "replace", "target": "doc", "input": input_ref()}])], [])},
        {"doc": ("runtime_context", "document")})
    solved = propagate(cfg, annotation)
    assert solved.status == "unsupported_feedback"
    source, metadata = demo["demo_source"]()
    material = prepare_material(source, cfg)
    output = build_doe_input(source, cfg, annotation, solved, source_metadata=metadata,
                             execution_model=material["execution_model"])
    assert output["records"] == {}
    assert set(output["diagnostics"][0]["operations"][0]) == {"instruction_id", "event_index", "op_index"}


@pytest.mark.parametrize("status,diagnostic", [
    ("complete", {"code": "execution_error", "reason": "失败"}),
    ("resource_limit", None),
    ("execution_error", None),
    ("incomplete", None),
])
def test_status_and_diagnostics_must_not_hide_execution_failures(status, diagnostic):
    raw = handoff(); raw["status"] = status
    raw["diagnostics"] = [] if diagnostic is None else [diagnostic]
    with pytest.raises(ValueError): validate_doe_input(raw)


def test_dynamic_missing_part_warning_survives_without_op_notes():
    raw = handoff()
    raw["records"]["ir_view"]["events"][0] = {"effect": "transform", "atomic_ops": [{
        "op": "select_part", "inputs": [[raw["data"][0]["id"]]], "outputs": [[raw["data"][0]["id"]]],
        "endpoints": [], "changes": []}]}
    raw["diagnostics"] = [{"code": "missing_part", "instruction_id": "ir_view", "event_index": 0,
                           "op_index": 0, "data_id": raw["data"][0]["id"], "reason": "部分候选已排除字段"}]
    raw["sink_boundaries"] = []
    assert validate_doe_input(raw)["diagnostics"] == raw["diagnostics"]
    raw["diagnostics"][0]["data_id"] = "missing"
    with pytest.raises(ValueError, match="unknown Data"): validate_doe_input(raw)


def test_legal_omitted_cfg_defaults_are_preserved_not_rejected():
    raw = handoff()
    del raw["cfg"]["blocks"]["main"]["instructions"][1]["inputs"]
    del raw["cfg"]["blocks"]["main"]["instructions"][1]["outputs"]
    checked = validate_doe_input(raw)
    assert checked["cfg"] == raw["cfg"]


def test_processed_ir_must_include_its_public_output_binding():
    raw = handoff()
    raw["cfg"]["blocks"]["main"]["instructions"][0]["outputs"] = [{"type": "result", "identifier": "out"}]
    with pytest.raises(ValueError, match="public output binding"): validate_doe_input(raw)


def test_source_inventory_accepts_the_original_utf8_bom_identity():
    source, metadata = source_material()
    original = b"\xef\xbb\xbf" + source["files"][0]["content"].encode()
    metadata["files"][0]["raw_sha256"] = hashlib.sha256(original).hexdigest()
    metadata["files"][0]["size"] = len(original)
    checked = build_doe_source(source, metadata)
    assert checked["files"][0]["content"] == source["files"][0]["content"]
    assert checked["inventory"][0] == metadata["files"][0]


def test_inventory_byte_candidate_must_decode_to_the_exact_retained_text():
    source, metadata = source_material()
    file = source["files"][0]
    file["content"] = "\ufeff" + file["content"]
    file["sha256"] = hashlib.sha256(file["content"].encode()).hexdigest()
    source["source_sha256"] = _digest([{"path": file["path"], "sha256": file["sha256"]}])
    entry = metadata["files"][0]
    entry["decoded_sha256"] = file["sha256"]
    entry["raw_sha256"] = file["sha256"]
    entry["size"] = len(file["content"].encode())
    with pytest.raises(ValueError, match="UTF-8 source text"): build_doe_source(source, metadata)
    raw = b"\xef\xbb\xbf" + file["content"].encode()
    entry["raw_sha256"] = hashlib.sha256(raw).hexdigest(); entry["size"] = len(raw)
    assert build_doe_source(source, metadata)["files"][0]["content"] == file["content"]


def guarded_handoff(truth):
    raw = handoff()
    guard = deepcopy(raw['data'][0])
    guard['id'] = 'condition'
    guard['content'] = {'form': 'opaque'} if truth is None else {'form': 'literal', 'value': truth}
    raw['data'].append(guard)
    op = raw['records']['ir_view']['events'][0]['atomic_ops'][0]
    op['inputs'] = ([[raw['data'][0]['id']]] if truth is not False else []) + [['condition']]
    op['when_input_index'] = len(op['inputs']) - 1
    raw['sink_boundaries'] = resolved_sink_boundaries(raw['locations'], raw['records'])
    return raw


@pytest.mark.parametrize('truth', [True, False, None])
def test_conditional_observation_payload_and_sink_share_one_consumption_rule(truth):
    from skillflow.propagation.conditions import payload_inputs
    from skillflow.propagation.report import build_view
    from skillflow.propagation.report import render_html
    from skillflow.propagation.report import render_markdown
    raw = guarded_handoff(truth)
    checked = validate_doe_input(raw)
    op = checked['records']['ir_view']['events'][0]['atomic_ops'][0]
    assert len(checked['sink_boundaries']) == int(truth is not False)
    assert payload_inputs(op) == ([[raw['data'][0]['id']]] if truth is not False else [])
    assert build_view(checked)['boundary_rows'][0]['inputs'] == payload_inputs(op)
    assert '（控制）' in render_markdown(checked)
    assert '（控制）' in render_html(checked)
    assert '省略／不观察' in render_html(checked) if truth is False else True


@pytest.mark.parametrize('mutation', ['bool_index', 'outside', 'wrong_effect', 'false_payload', 'true_empty', 'nonbool', 'missing_sink'])
def test_conditional_observation_rejects_bad_control_mapping_or_fabricated_sink(mutation):
    raw = guarded_handoff(False if mutation == 'false_payload' else True)
    op = raw['records']['ir_view']['events'][0]['atomic_ops'][0]
    if mutation == 'bool_index': op['when_input_index'] = True
    if mutation == 'outside': op['when_input_index'] = 7
    if mutation == 'wrong_effect': raw['records']['ir_view']['events'][0]['effect'] = None
    if mutation == 'false_payload':
        op['inputs'].insert(0, [raw['data'][0]['id']]); op['when_input_index'] = 1
    if mutation == 'true_empty': op['inputs'] = [['condition']]; op['when_input_index'] = 0
    if mutation == 'nonbool': raw['data'][-1]['content'] = {'form': 'literal', 'value': 1}
    if mutation == 'missing_sink': raw['sink_boundaries'] = []
    with pytest.raises(ValueError): validate_doe_input(raw)


def test_build_member_mapping_exposes_original_fields_and_controls_without_new_business_sections():
    from skillflow.propagation.conditions import payload_inputs
    from skillflow.propagation.report import render_html
    from skillflow.propagation.report import render_markdown
    raw = guarded_handoff(False)
    op = raw['records']['ir_view']['events'][0]['atomic_ops'][0]
    op.update(op='build', inputs=[[raw['data'][0]['id']], ['condition']],
              outputs=[[raw['data'][0]['id']]], endpoints=[], members=[
                  {'path': ['query'], 'value_input_index': 0, 'when_input_index': None},
                  {'path': ['optional'], 'value_input_index': None, 'when_input_index': 1}])
    del op['when_input_index']
    raw['records']['ir_view']['events'][0]['effect'] = 'transform'
    checked = validate_doe_input(raw)
    assert payload_inputs(op) == [[raw['data'][0]['id']]]
    assert '原值槽 None；条件槽 1' in render_markdown(checked)
    assert '原值槽 None；条件槽 1' in render_html(checked)
    assert set(checked) == set(handoff())
    op['members'][1]['value_input_index'] = 0
    with pytest.raises(ValueError): validate_doe_input(raw)


def test_member_candidate_display_does_not_apply_shared_sink_union_to_false_instance():
    from skillflow.propagation.report import build_view
    from skillflow.propagation.report import render_html
    from skillflow.propagation.report import render_markdown
    fixture = runpy.run_path(str(Path(__file__).with_name('test_collection_scopes.py')))
    operation, local = fixture['operation'], fixture['local']
    body = [{'effect_index': 0, 'atomic_ops': [
        operation('select_part', input=local('item'), path=['flag'], output='flag'),
        operation('select_part', input=local('item'), path=['payload'], output='payload')]},
        {'effect_index': 1, 'atomic_ops': [operation('deliver', inputs=[local('payload')],
                                                   target='model', when=local('flag'))]}]
    cfg, annotation, solved, _ = fixture['solve'](
        [{'flag': False, 'payload': 'omitted'}], [{'flag': True, 'payload': 'included'}],
        body=body, effects=['transform', 'model_observe'])
    assert solved.status == 'complete', solved.diagnostics
    source, metadata = source_material()
    doe = build_doe_input(source, cfg, annotation, solved, source_metadata=metadata,
                          execution_model=execution_model())
    assert len(doe['sink_boundaries']) == 1
    rows = build_view(doe)['boundary_rows']
    assert len(rows) == 2 and sum(row['included'] for row in rows) == 1
    omitted = next(row for row in rows if not row['inputs'])
    assert omitted['included'] is False and omitted['level'] is None
    assert '条件为假' in omitted['rationale']
    assert '条件为假' in render_html(doe) and '条件为假' in render_markdown(doe)
