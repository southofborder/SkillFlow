"""Review-record invariants; these tests do not assert a model is semantically right."""

from copy import deepcopy
import hashlib
import json

import pytest

from skillflow.graph.audit.models import AuditResult
from skillflow.graph.audit.services import validate_audit
from skillflow.graph.audit.prompts import source_controlled_prompt
from skillflow.graph.audit.controlled import render_controlled
from skillflow.graph.semantic_contract import CONTRACT_SHA256
from skillflow.graph.semantic_contract import CONTRACT_TEXT
from skillflow.graph.semantic_contract import CONTRACT_VERSION
from skillflow.graph.semantic_contract import CHECKPOINTS
from skillflow.graph.semantic_contract import RULES
from skillflow.graph.semantic_contract import contract_binding


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def seal(document):
    document.setdefault("derived_links", [])
    document["certificate"] = {
        "status": "verified", "graph_sha256": document["graph_sha256"],
        "text_sha256": hashlib.sha256(document["text"].encode()).hexdigest(),
        "units_sha256": digest(document["units"]),
        "links_sha256": digest(document["derived_links"]),
    }


@pytest.fixture
def reviewed_merge():
    content = "按条件调用两个接口中的一个，后续使用实际得到的响应。"
    file = {"path": "SKILL.md", "content": content,
            "sha256": hashlib.sha256(content.encode()).hexdigest()}
    source = {"files": [file], "source_sha256": digest([
        {"path": file["path"], "sha256": file["sha256"]}])}
    units = [
        {"id": "left", "text": "left：第一个候选 result_alpha。", "basis": "explicit_graph",
         "graph_refs": ["/blocks/branch~1a/instructions/0/outputs/0"]},
        {"id": "right", "text": "right：第二个候选 result_beta。", "basis": "explicit_graph",
         "graph_refs": ["/blocks/branch_b/instructions/2/inputs/1/identifier"]},
    ]
    document = {"text": "\n".join(unit["text"] for unit in units),
                "graph_sha256": "a" * 64, "units": units,
                "derived_links": [{"identifier": "result_beta",
                                   "use_ref": "/blocks/branch_b/instructions/2/inputs/1",
                                   "definition_ref": "/blocks/origin_b/instructions/0/outputs/0"}]}
    seal(document)
    response = {
        "schema_version": 5, "outcome": "completed", "contract_version": CONTRACT_VERSION,
        "findings": [{
            "id": "binding", "kind": "semantic", "status": "represented",
            "conservative": {"rule_id": "DEP-MERGE", "candidate_fact_ids": ["left", "right"],
                             "lost_distinctions": ["未细分每次执行的来源选择。"],
                             "reason": "图记录两个来源候选；源文允许两个接口按条件产生实际响应。"},
            "source_requirement": "后续依赖实际响应。",
            "actual_representation": "保留可能来源集合，未宣称两者同时使用。",
            "reason": "本记录仅测试依赖保守表示的证据协议。",
            "source_refs": [{"unit_id": "src_001", "file": "SKILL.md", "start_line": 1,
                             "end_line": 1, "quote": content}],
            "controlled_refs": [{"unit_id": "left"}, {"unit_id": "right"}],
            "basis": ["explicit_graph"], "suggestions": [],
        }],
        "reviewed_source_unit_ids": ["src_001"],
        "reviewed_controlled_unit_ids": ["left", "right"], "notes": [],
    }
    return source, document, response


def test_contract_binding_covers_rules_checkpoints_and_provenance():
    expected = digest({"version": CONTRACT_VERSION,
                       "checkpoints": CHECKPOINTS,
                       "rules": RULES})
    assert CONTRACT_SHA256 == expected
    first = contract_binding()
    first["contract_sha256"] = "changed"
    assert contract_binding()["contract_sha256"] == expected
    assert len({rule["id"] for rule in RULES}) == len(RULES)
    assert all(rule["provenance"] and f"[{rule['id']}]" in CONTRACT_TEXT for rule in RULES)


def test_source_contract_keeps_acquisition_and_value_without_security_assumptions(reviewed_merge):
    source, document, _ = reviewed_merge
    instructions = source_controlled_prompt(source, document).split("\nINPUT_JSON\n", 1)[0]
    normalized = " ".join(instructions.split())
    assert CONTRACT_VERSION == "skill-ir-semantic-contract-v4"
    assert '"schema_version":5' in instructions
    for phrase in (
        "source entry from the acquired value",
        "neither a whole-container read nor model visibility",
        "Preserve explicit key-only getters, local processing, and isolation boundaries",
        "A missing explicit source cannot be excused by conservative dependency rules",
        "An entry identifying a container is not evidence that the whole container was read, sent, or observed",
        "No security annotation or broad-read execution assumption is supplied here",
        "acquisition boundary distinct from its request dependencies",
    ):
        assert phrase in normalized


def test_conservative_evidence_is_mapped_without_rewriting_judgment(reviewed_merge):
    source, document, response = reviewed_merge
    original = deepcopy(reviewed_merge)
    checked = validate_audit(response, source, document)
    assert checked["representation_summary"] == {"represented_ids": ["binding"], "conservative_ids": ["binding"]}
    assert checked["findings"][0]["conservative"]["graph_refs"] == [
        "/blocks/branch~1a/instructions/0/outputs/0",
        "/blocks/branch_b/instructions/2/inputs/1/identifier",
    ]
    assert checked["contract_sha256"] == CONTRACT_SHA256
    assert reviewed_merge == original


@pytest.mark.parametrize("rule", ["DEP-MERGE", "DEP-SOURCE"])
def test_both_candidate_dependency_rules_are_supported(reviewed_merge, rule):
    source, document, response = reviewed_merge
    response["findings"][0]["conservative"]["rule_id"] = rule
    assert validate_audit(response, source, document)["findings"][0]["conservative"]["rule_id"] == rule


@pytest.mark.parametrize("mutate", [
    lambda r: r.pop("schema_version"),
    lambda r: r.update(schema_version=2),
    lambda r: r.update(contract_version="unreviewed-contract"),
    lambda r: r.update(schema_version=3),
    lambda r: r.update(dimension_reviews=[]),
    lambda r: r["findings"].append(deepcopy(r["findings"][0])),
])
def test_versions_and_record_identity_are_strict(reviewed_merge, mutate):
    source, document, response = reviewed_merge
    mutate(response)
    with pytest.raises(ValueError):
        validate_audit(response, source, document)


@pytest.mark.parametrize("change", [
    {"kind": "context"}, {"status": "unknown", "unknown_reason": "未知"},
    {"status": "omitted"}, {"status": "mistranslated"},
])
def test_conservative_fields_cannot_be_attached_to_other_judgments(reviewed_merge, change):
    response = reviewed_merge[2]
    response["findings"][0].update(change)
    with pytest.raises(ValueError):
        AuditResult.model_validate(response)


@pytest.mark.parametrize("change", [
    {"rule_id": "DEP-ANY"}, {"candidate_fact_ids": ["left"]},
    {"candidate_fact_ids": ["left", "left"]}, {"candidate_fact_ids": ["left", "invented"]},
    {"lost_distinctions": []}, {"lost_distinctions": [""]}, {"reason": ""},
    {"graph_refs": ["/blocks/x"]},
])
def test_bad_candidate_rules_and_evidence_are_rejected(reviewed_merge, change):
    source, document, response = reviewed_merge
    response["findings"][0]["conservative"].update(change)
    with pytest.raises(ValueError):
        validate_audit(response, source, document)


@pytest.mark.parametrize("pointer,basis", [
    ("", "explicit_graph"), ("/blocks/b", "explicit_graph"),
    ("/blocks/b/instructions/0", "explicit_graph"),
    ("/blocks/b/instructions/0/inputs", "explicit_graph"),
    ("/blocks/b/instructions/0/constraints/0", "declared_constraint"),
    ("/blocks/b/instructions/0/metadata/source", "embedded_content"),
    ("/blocks/b/instructions/0/outputs/0", "declared_constraint"),
    ("/blocks/b/instructions/0/inputs/0/type", "explicit_graph"),
    ("/blocks/b/instructions/0/inputs/0/semantic_name", "explicit_graph"),
])
def test_containers_and_declarations_cannot_stand_in_for_candidates(reviewed_merge, pointer, basis):
    source, document, response = reviewed_merge
    document["units"][0].update(graph_refs=[pointer], basis=basis)
    seal(document)
    with pytest.raises(ValueError, match="candidate"):
        validate_audit(response, source, document)


def test_two_fields_of_one_operand_do_not_make_two_candidates(reviewed_merge):
    source, document, response = reviewed_merge
    document["units"][0]["graph_refs"] = ["/blocks/b/instructions/0/outputs/0/identifier"]
    document["units"][1]["graph_refs"] = ["/blocks/b/instructions/0/outputs/0"]
    seal(document)
    with pytest.raises(ValueError, match="two distinct"):
        validate_audit(response, source, document)


def test_definition_and_use_of_one_result_are_not_two_sources(reviewed_merge):
    source, document, response = reviewed_merge
    definition = document["units"][0]["graph_refs"][0]
    use = document["units"][1]["graph_refs"][0].removesuffix("/identifier")
    document["derived_links"] = [{"identifier": "same_result", "use_ref": use,
                                  "definition_ref": definition}]
    seal(document)
    with pytest.raises(ValueError, match="uses of one result do not count twice"):
        validate_audit(response, source, document)


def test_two_uses_of_one_result_are_not_two_sources(reviewed_merge):
    source, document, response = reviewed_merge
    first, second = "/blocks/a/instructions/0/inputs/0", "/blocks/b/instructions/1/inputs/0"
    document["units"][0]["graph_refs"] = [first]
    document["units"][1]["graph_refs"] = [second + "/identifier"]
    document["derived_links"] = [
        {"identifier": "shared", "use_ref": use, "definition_ref": "/blocks/origin/instructions/0/outputs/0"}
        for use in (first, second)]
    seal(document)
    with pytest.raises(ValueError, match="uses of one result"):
        validate_audit(response, source, document)


def test_certified_distinct_identifiers_remain_two_candidates(reviewed_merge):
    source, document, response = reviewed_merge
    first_definition = document["units"][0]["graph_refs"][0]
    second_use = document["units"][1]["graph_refs"][0].removesuffix("/identifier")
    document["derived_links"] = [
        {"identifier": "first", "use_ref": "/blocks/read/instructions/0/inputs/0", "definition_ref": first_definition},
        {"identifier": "second", "use_ref": second_use, "definition_ref": "/blocks/other/instructions/0/outputs/0"}]
    seal(document)
    assert validate_audit(response, source, document)["representation_summary"]["conservative_ids"] == ["binding"]


@pytest.mark.parametrize("mutation", ["missing", "changed", "hash"])
def test_derived_link_identity_is_bound_to_the_certificate(reviewed_merge, mutation):
    source, document, response = reviewed_merge
    if mutation == "missing":
        document.pop("derived_links")
    elif mutation == "hash":
        document["certificate"]["links_sha256"] = "0" * 64
    else:
        document["derived_links"].append({"identifier": "changed", "use_ref": "/x", "definition_ref": "/y"})
    with pytest.raises(ValueError, match="derived_links digest"):
        validate_audit(response, source, document)


@pytest.mark.parametrize("links", [
    [None], [{"identifier": "x"}],
    [{"identifier": "", "use_ref": "/blocks/a/instructions/0/inputs/0", "definition_ref": "/blocks/b/instructions/0/outputs/0"}],
    [{"identifier": "x", "use_ref": "/blocks/a/instructions/0/outputs/0", "definition_ref": "/blocks/b/instructions/0/outputs/0"}],
    [{"identifier": "x", "use_ref": "/blocks/a~2/instructions/0/inputs/0", "definition_ref": "/blocks/b/instructions/0/outputs/0"}],
    [{"identifier": "x", "use_ref": "/blocks/a/instructions/0/inputs/0", "definition_ref": "/blocks/b/instructions/0/outputs/0"}] * 2,
])
def test_malformed_links_are_rejected_even_with_a_matching_digest(reviewed_merge, links):
    source, document, response = reviewed_merge
    document["derived_links"] = links
    seal(document)
    with pytest.raises(ValueError, match="controlled"):
        validate_audit(response, source, document)


def test_unlinked_definition_retains_location_boundary_without_name_guessing(reviewed_merge):
    source, document, response = reviewed_merge
    document["units"][1]["graph_refs"] = ["/blocks/unused/instructions/0/outputs/0"]
    # Neither result participates in derived links. The validator can establish
    # distinct recorded operand locations, not distinct semantic provenance.
    seal(document)
    checked = validate_audit(response, source, document)
    assert checked["findings"][0]["conservative"]["rule_id"] == "DEP-MERGE"
    assert "保守候选的依据" in checked["coverage_notice"]


@pytest.fixture(scope="module")
def actual_lean_document():
    from tests.graph.audit.test_evidence import example_cfg

    return render_controlled(example_cfg())


def _actual_fact(document, operand_location):
    # The current authoritative printer anchors whole operands, rather than
    # giving each identifier subfield an independent evidence unit.
    suffix = "/".join(operand_location.split("/")[-2:])
    return next(unit["id"] for unit in document["units"]
                if unit["graph_refs"][0] == operand_location
                and unit["rich_ref"].endswith("/" + suffix)
                and not unit["id"].endswith(":link"))


def _response_for_actual_units(response, document, candidate_ids):
    response = deepcopy(response)
    response["findings"][0]["conservative"]["candidate_fact_ids"] = candidate_ids
    response["findings"][0]["controlled_refs"] = [{"unit_id": value} for value in candidate_ids]
    response["findings"].append({
        "id": "other_units", "kind": "context", "status": "represented",
        "source_requirement": "服务格式测试剩余事实。", "actual_representation": "只测试证据覆盖协议。",
        "reason": "不将本测试响应当作真实语义评测结论。", "source_refs": [],
        "controlled_refs": [{"unit_id": unit["id"]} for unit in document["units"]
                            if unit["id"] not in candidate_ids],
        "basis": ["interpretation"], "suggestions": [],
    })
    response["reviewed_controlled_unit_ids"] = [unit["id"] for unit in document["units"]]
    return response


@pytest.mark.parametrize("operand_location", [
    "/blocks/end/instructions/0/inputs/1",               # literal success
    "/blocks/end/instructions/1/inputs/2",               # literal null
    "/blocks/retry/instructions/0/inputs/0",             # external_resource
    "/blocks/start~1~0one/instructions/0/inputs/0",       # context_key
])
def test_real_lean_nonresult_inputs_cannot_masquerade_as_merge_results(
    reviewed_merge, actual_lean_document, operand_location,
):
    source, _, response = reviewed_merge
    document = actual_lean_document
    candidate = _actual_fact(document, operand_location)
    actual_result = _actual_fact(document, "/blocks/retry/instructions/0/outputs/0")
    response = _response_for_actual_units(response, document, [candidate, actual_result])
    with pytest.raises(ValueError, match="DEP-MERGE input candidates require a certified result"):
        validate_audit(response, source, document)


def test_real_lean_result_inputs_and_definitions_remain_eligible(
    reviewed_merge, actual_lean_document,
):
    source, _, response = reviewed_merge
    document = actual_lean_document
    candidate_ids = [
        _actual_fact(document, "/blocks/retry/instructions/0/inputs/1"),
        _actual_fact(document, "/blocks/retry/instructions/0/outputs/0"),
    ]
    response = _response_for_actual_units(response, document, candidate_ids)
    assert validate_audit(response, source, document)["representation_summary"]["conservative_ids"] == ["binding"]


def test_two_full_literal_operands_in_frozen_f01_cannot_form_a_merge(reviewed_merge):
    from skillflow.graph.audit.fixtures import prepare_cases
    from skillflow.graph.audit.evidence import normalize_cfg
    from skillflow.graph.audit.evidence import resolve_pointer
    from skillflow.graph.ir.cfg import ControlFlowGraph

    source, _, response = reviewed_merge
    cfg = ControlFlowGraph.model_validate(prepare_cases()["cases"][0]["cfg"])
    graph = normalize_cfg(cfg)
    document = render_controlled(cfg)
    candidate_ids = []
    for unit in document["units"]:
        value = resolve_pointer(graph, unit["graph_refs"][0])
        if (isinstance(value, dict) and value.get("type") == "literal"
                and value.get("literal_value") == "success"):
            candidate_ids.append(unit["id"])
    assert len(candidate_ids) >= 2
    response = _response_for_actual_units(response, document, candidate_ids[:2])
    with pytest.raises(ValueError, match="DEP-MERGE input candidates require a certified result"):
        validate_audit(response, source, document)


@pytest.mark.parametrize("field", ["", "/identifier"])
def test_nonresult_input_location_or_identifier_cannot_bypass_certified_links(reviewed_merge, field):
    source, document, response = reviewed_merge
    document["units"][1]["graph_refs"] = ["/blocks/nonresult/instructions/0/inputs/0" + field]
    seal(document)
    with pytest.raises(ValueError, match="DEP-MERGE input candidates require a certified result"):
        validate_audit(response, source, document)


def test_unknown_is_preserved_not_automatically_made_conservative(reviewed_merge):
    source, document, response = reviewed_merge
    response["findings"][0].update(status="unknown", conservative=None, unknown_reason="给定材料无法裁决。")
    with pytest.raises(ValueError):
        validate_audit(response, source, document)


def test_unknown_requires_a_reason_and_nonunknown_cannot_carry_one(reviewed_merge):
    response = reviewed_merge[2]
    response["findings"][0]["unknown_reason"] = "源文冲突。"
    with pytest.raises(ValueError, match="unknown_reason"):
        AuditResult.model_validate(response)
    response["findings"][0].update(status="unknown", conservative=None, unknown_reason=None)
    with pytest.raises(ValueError, match="unknown_reason"):
        AuditResult.model_validate(response)


def test_actual_differences_keep_their_status_and_located_suggestions(reviewed_merge):
    source, document, response = reviewed_merge
    response["findings"][0].update(
        status="mistranslated", conservative=None,
        source_requirement="使用实际成功响应。", actual_representation="绑定了明确不同的旧结果。",
        suggestions=[{"target_ids": ["right"], "change": "使用原文要求的结果。", "reason": "结果身份不一致。"}])
    checked = validate_audit(response, source, document)
    assert checked["findings"][0]["status"] == "mistranslated"
    assert checked["findings"][0]["suggestions"][0]["graph_refs"] == document["units"][1]["graph_refs"]


def test_legitimate_renaming_and_storage_reorder_preserve_mapping(reviewed_merge):
    source, document, response = reviewed_merge
    for index, unit in enumerate(document["units"]):
        old, new = unit["id"], f"unique_fact_{index * 71}"
        unit["id"] = new
        unit["text"] = unit["text"].replace(old, new)
        response["reviewed_controlled_unit_ids"][index] = new
        response["findings"][0]["controlled_refs"][index]["unit_id"] = new
        response["findings"][0]["conservative"]["candidate_fact_ids"][index] = new
    document["units"].reverse()
    document["text"] = "\n".join(unit["text"] for unit in document["units"])
    seal(document)
    result = validate_audit(response, source, document)
    assert result["findings"][0]["conservative"]["candidate_fact_ids"] == ["unique_fact_0", "unique_fact_71"]
    assert result["findings"][0]["conservative"]["graph_refs"][0].endswith("/outputs/0")


def test_prompt_shares_contract_without_private_inputs_or_second_graph(reviewed_merge):
    source, document, _ = reviewed_merge
    document.update(oracle="private_expected", graph={"secret": "private_raw_graph"},
                    history="private_judgment", mutation="private_label")
    prompt = source_controlled_prompt(source, document)
    instructions, payload = prompt.split("\nINPUT_JSON\n", 1)
    assert CONTRACT_TEXT in instructions
    normalized = " ".join(instructions.split())
    assert "related behavior, conditions, and results may be grouped" in normalized
    assert "do not mark the whole finding represented" in normalized
    assert "check each conclusion against its own evidence and the other findings for consistency" in normalized
    assert "missing correct sources, explicitly wrong returned results, explicit extra arguments, or prohibited transfers" in normalized
    assert "Use the separate cannot_assess outcome" in normalized
    assert "这是可定位的表示缺口" not in instructions
    for secret in ("private_expected", "private_raw_graph", "private_judgment", "private_label"):
        assert secret not in prompt
    assert json.loads(payload)["controlled_text"] == document["text"]
