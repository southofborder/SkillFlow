"""The source/text boundary, evidence validation, and single-call protocol."""

from copy import deepcopy
import hashlib
import json
import socket

import pytest

from skill_ir.backtrace.prompts import source_controlled_prompt, source_units
from skill_ir.backtrace.services import audit_source_controlled, parse_response, validate_audit
from skill_ir.semantic_contract import CONTRACT_VERSION


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def bind_source(source):
    for item in source["files"]:
        item["sha256"] = hashlib.sha256(item["content"].encode()).hexdigest()
    source["source_sha256"] = digest([{key: item[key] for key in ("path", "sha256")}
                                     for item in source["files"]])
    return source


def bind_document(document):
    document.setdefault("derived_links", [])
    document["certificate"] = {"status": "verified", "graph_sha256": document["graph_sha256"],
                               "text_sha256": hashlib.sha256(document["text"].encode()).hexdigest(),
                               "units_sha256": digest(document["units"]),
                               "links_sha256": digest(document["derived_links"]),
                               "private_marker": "certificate_only_marker"}
    return document


def bind_protocol(response):
    response.update(schema_version=5, outcome="completed", contract_version=CONTRACT_VERSION)
    return response


@pytest.fixture
def material():
    source = bind_source({"files": [{"path": "SKILL.md", "content": "# source_only_marker\n\n读取请求并返回。\n"}]})
    units = [
        {"id": "u_container", "text": "u_container：当前流程。", "basis": "explicit_graph", "graph_refs": [""]},
        {"id": "u_ops", "text": "u_ops：读取请求，返回该结果。", "basis": "explicit_graph",
         "graph_refs": ["/blocks/arbitrary/instructions"], "rich_ref": "private_rich_location"},
    ]
    document = bind_document({"text": "\n".join(unit["text"] for unit in units),
                              "graph_sha256": "1" * 64, "units": units,
                              "raw_cfg": {"secret_marker": "raw_graph_only_marker"},
                              "oracle": "oracle_only_marker", "variant": "mutation_only_marker",
                              "previous_result": "old_result_only_marker"})
    response = {"findings": [
        {"id": "f_context", "kind": "context", "status": "represented",
         "source_requirement": "标题是背景信息。", "actual_representation": "流程容器。",
         "reason": "本项仅记录非业务上下文，并非语义要求通过。",
         "source_refs": [{"unit_id": "src_001", "file": "SKILL.md", "start_line": 1, "end_line": 1,
                          "quote": "# source_only_marker"}],
         "controlled_refs": [{"unit_id": "u_container"}], "basis": ["interpretation"], "suggestions": []},
        {"id": "f_read", "kind": "semantic", "status": "represented",
         "source_requirement": "读取请求并返回。", "actual_representation": "读取后返回该结果。",
         "reason": "比较了动作、顺序与返回身份。",
         "source_refs": [{"unit_id": "src_002", "file": "SKILL.md", "start_line": 3, "end_line": 3,
                          "quote": "读取请求并返回。"}],
         "controlled_refs": [{"unit_id": "u_ops", "quote": "读取请求，返回该结果。"}],
         "basis": ["explicit_graph"], "suggestions": []}],
        "reviewed_source_unit_ids": ["src_001", "src_002"],
        "reviewed_controlled_unit_ids": ["u_container", "u_ops"], "notes": []}
    return source, document, bind_protocol(response)


class FakeClient:
    def __init__(self, response):
        self.response = deepcopy(response)
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return deepcopy(self.response)


def suggestion(unit="u_ops"):
    return {"target_ids": [unit], "change": "修正该位置的表示。", "reason": "保留原文要求。"}


def test_single_call_receives_only_complete_source_and_controlled_text(material):
    original = deepcopy(material)
    source, document, response = material
    client = FakeClient(response)
    parsed = audit_source_controlled(source, document, client)
    assert len(client.prompts) == 1
    payload = json.loads(client.prompts[0].split("\nINPUT_JSON\n")[1])
    assert payload["source_files"] == [{"path": "SKILL.md", "content": source["files"][0]["content"]}]
    assert payload["controlled_text"] == document["text"]
    assert payload["controlled_units"] == [{"id": u["id"], "basis": u["basis"]} for u in document["units"]]
    assert payload["source_line_index"]["SKILL.md"][2] == {"line": 3, "text": "读取请求并返回。"}
    for forbidden in ("raw_graph_only_marker", "oracle_only_marker", "mutation_only_marker", "old_result_only_marker",
                      "certificate_only_marker", "private_rich_location", "/blocks/arbitrary/instructions", "graph_sha256"):
        assert forbidden not in client.prompts[0]
    assert parsed["findings"][1]["graph_refs"] == ["/blocks/arbitrary/instructions"]
    assert "不是语义等价" in parsed["coverage_notice"]
    assert material == original


def test_combined_behavior_order_and_binding_need_no_classification_or_optional_fields(material):
    source, document, response = material
    # A coherent comparison may cover several perspectives; no classifier or
    # programmatic atomicity heuristic decides how to split its semantics.
    assert "conservative" not in response["findings"][1]
    assert "unknown_reason" not in response["findings"][1]
    checked = validate_audit(response, source, document)
    assert checked["representation_summary"] == {
        "represented_ids": ["f_read"], "conservative_ids": []}
    assert "未填写保守说明不代表精确保留" in checked["coverage_notice"]
    for field in ("precision", "dimension", "unknown_cause"):
        assert field not in checked["findings"][1]
    assert "dimension_reviews" not in checked
    assert "precision_summary" not in checked


@pytest.mark.parametrize("field,value", [
    ("dimension", "data_bindings"), ("precision", "precise"),
    ("unknown_cause", None),
])
def test_removed_classification_fields_are_rejected_in_v5(material, field, value):
    source, document, response = material
    response["findings"][1][field] = value
    with pytest.raises(ValueError, match="Extra inputs"):
        validate_audit(response, source, document)


def test_unknown_requires_only_reason_not_an_extra_cause_category(material):
    source, document, response = material
    response["findings"][1].update(status="unknown", unknown_reason="材料中没有给出操作效果。")
    with pytest.raises(ValueError):
        validate_audit(response, source, document)


def test_source_unit_index_preserves_fences_and_all_nonempty_lines():
    content = "首段\r\n\r\n```python\r\nprint('x')\r\n\r\nprint('y')\r\n```\r\n\r\n末段\r\n"
    source = bind_source({"files": [{"path": "a.md", "content": content}, {"path": "b.md", "content": "尾文件"}]})
    units = source_units(source)
    assert [(u["file"], u["start_line"], u["end_line"]) for u in units] == [
        ("a.md", 1, 1), ("a.md", 3, 7), ("a.md", 9, 9), ("b.md", 1, 1)]
    assert "print('x')\n\nprint('y')" in units[1]["text"]
    assert [u["id"] for u in units] == ["src_001", "src_002", "src_003", "src_004"]


def test_auxiliary_kind_is_not_a_second_model_visible_classification(material):
    from skill_ir.backtrace.prompts import source_controlled_prompt
    source, document, _ = material
    document["units"][0]["kind"] = "unverified_auxiliary_kind"
    prompt = source_controlled_prompt(source, document)
    assert "unverified_auxiliary_kind" not in prompt
    payload = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
    assert all(set(unit) == {"id", "basis"} for unit in payload["controlled_units"])


def test_auditor_receives_fixed_ir_roles_without_case_specific_answers(material):
    source, document, _ = material
    prompt = source_controlled_prompt(source, document)
    contract, payload = prompt.split("\nINPUT_JSON\n", 1)
    assert "dispatch and return are fixed control terminators" in contract
    assert "return alone does not mean displaying or sending content to the user" in contract
    assert "Local files may also use this type" in contract
    assert "does not necessarily mean a remote or network resource" in contract
    assert "still check the actual inputs, outgoing edges, conditions, and returned-value identities" in contract
    for historical_detail in ("finding_8", "finding_11", "result_006", "ir_012",
                              "count.txt", "index.search", "full-pipeline-20260917"):
        assert historical_detail not in contract
    # Definitions are shared instructions, not a second graph, source summary,
    # or an unverified alteration of the certified controlled text.
    payload = json.loads(payload)
    assert payload["controlled_text"] == document["text"]
    assert set(payload) == {"source_files", "source_line_index", "source_units",
                            "controlled_text", "controlled_units", "required_coverage"}


def test_audit_boundary_does_not_invent_path_selection_or_strengthen_wf(material):
    prompt = source_controlled_prompt(material[0], material[1])
    contract = prompt.split("\nINPUT_JSON\n", 1)[0]
    normalized = " ".join(contract.split())
    assert "does not guarantee that all inputs are simultaneously available on every path" in contract
    assert "Do not invent implicit phi" in contract
    assert "Do not infer a semantic error merely because a result is produced on only some paths" in contract
    assert "Do not classify a lack of more precise value selection alone as omitted or mistranslated" in contract
    assert "do not demand invented operand fields, types, or built-in phi rules" in normalized
    assert "Use the separate cannot_assess outcome" in contract
    assert "这是可定位的表示缺口" not in contract
    assert "'An action is not required' does not automatically mean 'the action is prohibited'" in contract
    assert "does not automatically mean format/validity checking or normalization" in contract


def test_english_audit_instructions_keep_material_verbatim_and_check_granularity(material):
    import re

    source, document, _ = material
    prompt = source_controlled_prompt(source, document)
    instructions, payload_text = prompt.split("\nINPUT_JSON\n", 1)
    assert not re.search(r"[\u3400-\u9fff]", instructions)
    normalized = " ".join(instructions.split())
    assert "Write explanations and reasons in Chinese" in normalized
    assert "Preserve source and controlled quotes verbatim in their original language" in normalized
    for rule in (
        "separate source-specified actions must remain individually represented",
        "an intermediate data version affects processing, observation, writing, or transmission",
        "Verify both recorded order and the data version consumed by each action",
        "a compound name cannot replace missing ordered actions",
        "A single call may have multiple effects and need not be split by effect count",
        "Respect code and opaque-function black boxes",
        "Do not demand a source-level CFG instruction for implicit observation",
    ):
        assert rule in normalized
    payload = json.loads(payload_text)
    assert payload["source_files"] == [
        {"path": item["path"], "content": item["content"]} for item in source["files"]]
    assert payload["controlled_text"] == document["text"]


def test_new_interpretation_boundary_does_not_override_model_uncertainty(material):
    from skill_ir.semantic_failure import SemanticFailure
    source, document, response = material
    finding = response["findings"][1]
    failure = {"schema_version": 5, "contract_version": CONTRACT_VERSION, "outcome": "cannot_assess",
               "failure": {"reason": "引用的源文要求互相冲突，无法比较应保留的行为。",
                           "source_refs": finding["source_refs"], "controlled_refs": finding["controlled_refs"]}}
    client = FakeClient(failure)
    with pytest.raises(SemanticFailure) as caught:
        audit_source_controlled(source, document, client)
    assert len(client.prompts) == 1
    assert caught.value.failure["graph_refs"] == ["/blocks/arbitrary/instructions"]
    assert caught.value.failure["reason"] == failure["failure"]["reason"]


@pytest.mark.parametrize("raw", ["garbage", "[]", "{} trailing", "```json\n{}\n```",
                                     '{"findings":[],"findings":[]}', '{"value":{"x":1,"x":2}}',
                                     '{"findings":NaN}', '{"findings":Infinity}', 12, None])
def test_invalid_json_never_triggers_a_repair_call(material, raw):
    client = FakeClient(raw)
    with pytest.raises(ValueError):
        audit_source_controlled(material[0], material[1], client)
    assert len(client.prompts) == 1


@pytest.mark.parametrize("path,value", [
    (("source_refs", 0, "unit_id"), "absent"),
    (("source_refs", 0, "file"), "missing.md"),
    (("source_refs", 0, "start_line"), 1),
    (("source_refs", 0, "end_line"), 4),
    (("source_refs", 0, "quote"), "并没有这句话"),
    (("controlled_refs", 0, "unit_id"), "fabricated_missing_operation"),
    (("controlled_refs", 0, "quote"), "返回了不同结果"),
])
def test_bad_locations_and_quotes_are_rejected(material, path, value):
    source, document, response = material
    finding = response["findings"][1]
    finding[path[0]][path[1]][path[2]] = value
    with pytest.raises(ValueError):
        validate_audit(response, source, document)


@pytest.mark.parametrize("field", ["reviewed_source_unit_ids", "reviewed_controlled_unit_ids"])
def test_missing_or_repeated_coverage_is_rejected(material, field):
    source, document, response = material
    response[field].pop()
    with pytest.raises(ValueError, match=field):
        validate_audit(response, source, document)


@pytest.mark.parametrize("refs", ["source_refs", "controlled_refs"])
def test_complete_coverage_list_does_not_replace_findings(material, refs):
    source, document, response = material
    response["findings"][0][refs] = []
    with pytest.raises(ValueError, match="findings do not cover"):
        validate_audit(response, source, document)


@pytest.mark.parametrize("status", ["omitted", "mistranslated", "unsupported_addition"])
def test_actionable_judgments_derive_locations_from_existing_targets(material, status):
    source, document, response = material
    finding = response["findings"][1]
    finding["status"] = status
    finding["suggestions"] = [suggestion("u_container" if status == "omitted" else "u_ops")]
    output = validate_audit(response, source, document)
    assert output["findings"][1]["status"] == status
    assert output["findings"][1]["suggestions"][0]["graph_refs"] == (
        [""] if status == "omitted" else ["/blocks/arbitrary/instructions"])


def test_unknown_requires_reason_and_is_not_changed_to_pass(material):
    source, document, response = material
    finding = response["findings"][1]
    finding["status"] = "unknown"
    with pytest.raises(ValueError):
        validate_audit(response, source, document)
    finding["unknown_reason"] = "操作运行效果未规定。"
    with pytest.raises(ValueError):
        validate_audit(response, source, document)


def test_conflict_can_use_two_controlled_units_without_fabricated_source(material):
    source, document, response = material
    conflict = deepcopy(response["findings"][1])
    conflict.update(id="f_conflict", status="internal_conflict", source_refs=[],
                    controlled_refs=[{"unit_id": "u_ops"}, {"unit_id": "u_container"}],
                    suggestions=[suggestion()], basis=["explicit_graph", "declared_constraint"])
    response["findings"].append(conflict)
    bind_protocol(response)
    assert validate_audit(response, source, document)["findings"][-1]["source_refs"] == []
    conflict["controlled_refs"].pop()
    with pytest.raises(ValueError, match="two distinct"):
        validate_audit(response, source, document)


@pytest.mark.parametrize("target", ["missing", "u_ops/inputs/0", "/blocks/arbitrary/instructions"])
def test_suggestion_targets_are_existing_controlled_ids_only(material, target):
    source, document, response = material
    response["findings"][1]["suggestions"] = [suggestion(target)]
    with pytest.raises(ValueError, match="controlled unit does not exist"):
        validate_audit(response, source, document)


@pytest.mark.parametrize("level", ["finding", "suggestion", "root"])
def test_model_cannot_supply_graph_pointers(material, level):
    source, document, response = material
    if level == "root":
        response["graph_refs"] = [""]
    elif level == "finding":
        response["findings"][1]["graph_refs"] = [""]
    else:
        response["findings"][1]["suggestions"] = [{**suggestion(), "graph_refs": [""]}]
    with pytest.raises(ValueError):
        validate_audit(response, source, document)


@pytest.mark.parametrize("change", ["source_text", "source_hash", "text", "units", "links", "certificate"])
def test_changed_bound_inputs_fail_before_model_call(material, change):
    source, document, response = material
    if change == "source_text":
        source["files"][0]["content"] += "changed"
    elif change == "source_hash":
        source["source_sha256"] = "0" * 64
    elif change == "text":
        document["text"] += "changed"
    elif change == "units":
        document["units"][0]["graph_refs"] = ["/changed"]
    elif change == "links":
        document["derived_links"].append({"identifier": "forged", "use_ref": "/invalid", "definition_ref": "/invalid"})
    else:
        document["certificate"]["status"] = "unverified"
    client = FakeClient(response)
    with pytest.raises(ValueError):
        audit_source_controlled(source, document, client)
    assert client.prompts == []


def test_offline_parse_uses_no_network_and_matches_live_service(material, monkeypatch):
    source, document, response = material
    monkeypatch.setattr(socket, "create_connection", lambda *a, **kw: pytest.fail("network called"))
    assert parse_response(json.dumps(response), source=source, document=document) == audit_source_controlled(
        source, document, FakeClient(response))


def test_renaming_units_needs_no_identifier_specific_detection(material):
    source, document, response = material
    old, new = "u_ops", "arbitrary_unit_99"
    document["text"] = document["text"].replace(old, new)
    document["units"][1]["id"] = new
    document["units"][1]["text"] = document["units"][1]["text"].replace(old, new)
    bind_document(document)
    response["reviewed_controlled_unit_ids"][1] = new
    response["findings"][1]["controlled_refs"][0]["unit_id"] = new
    assert validate_audit(response, source, document)["findings"][1]["graph_refs"] == ["/blocks/arbitrary/instructions"]


def test_mixed_units_keep_their_evidence_classification(material):
    source, document, response = material
    document["units"][1]["basis"] = "mixed"
    bind_document(document)
    client = FakeClient(response)
    audit_source_controlled(source, document, client)
    payload = json.loads(client.prompts[0].split("\nINPUT_JSON\n")[1])
    assert payload["controlled_units"][1]["basis"] == "mixed"


def test_prior_role_fields_are_not_accepted(material):
    source, document, response = material
    response["direction"] = "source_to_graph"
    with pytest.raises(ValueError):
        validate_audit(response, source, document)


def test_source_and_controlled_order_do_not_rewrite_model_judgment(material):
    source, document, response = material
    response["findings"].reverse()
    response["reviewed_controlled_unit_ids"].reverse()
    response["reviewed_source_unit_ids"].reverse()
    parsed = validate_audit(response, source, document)
    assert [f["id"] for f in parsed["findings"]] == ["f_read", "f_context"]
