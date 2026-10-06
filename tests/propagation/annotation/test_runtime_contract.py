"""Runtime identity and evidence transport checks, not a model truth oracle."""

from copy import deepcopy
import json

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.contracts.runtime_contract import CONTRACT_VERSION
from skillflow.propagation.contracts.runtime_contract import execution_model
from skillflow.propagation.contracts.runtime_contract import execution_model_binding
from skillflow.propagation.contracts.runtime_contract import validate_execution_model
from skillflow.propagation.contracts.runtime_contract import validate_execution_model_binding
from skillflow.propagation.material import checked_material
from skillflow.propagation.material import check_evidence
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.annotation.report import render_report
from tests.propagation.annotation.helpers import material


def test_one_isolated_contract_and_canonical_binding():
    current = execution_model()
    assert set(current) == {"version", "rules"}
    assert current["version"] == CONTRACT_VERSION == "skillflow-abstract-runtime-v5"
    assert [rule["id"] for rule in current["rules"]] == [f"EM{i:02}" for i in range(1, 16)]
    binding = execution_model_binding(current)
    assert binding == {"version": CONTRACT_VERSION, "sha256": canonical_sha256(current)}
    checked = validate_execution_model(current)
    checked["rules"][0]["text"] = "changed"
    assert current == execution_model()
    validated_binding = validate_execution_model_binding(binding)
    validated_binding["sha256"] = "changed"
    assert binding == execution_model_binding(execution_model())
    current["rules"].clear()
    assert len(execution_model()["rules"]) == 15


@pytest.mark.parametrize("change", [
    lambda model: model.update(version="wide-read-agent-v6"),
    lambda model: model.update(runtime="another-agent"),
    lambda model: model.update(rules=tuple(model["rules"])),
    lambda model: model["rules"].reverse(),
    lambda model: model["rules"].append(deepcopy(model["rules"][0])),
    lambda model: model["rules"][0].update(text="always invisible"),
    lambda model: model["rules"][0].update(id=True),
    lambda model: model["rules"][0].update(extra="ignored?"),
])
def test_altered_contract_cannot_be_silently_substituted(change):
    model = execution_model()
    change(model)
    with pytest.raises(ValueError, match="runtime contract identity mismatch"):
        validate_execution_model(model)
    with pytest.raises(ValueError, match="runtime contract identity mismatch"):
        execution_model_binding(model)
    prepared = material()
    prepared["execution_model"] = model
    with pytest.raises(ValueError, match="runtime contract identity mismatch"):
        checked_material(prepared)


@pytest.mark.parametrize("binding", [
    None, {}, [],
    {"version": "wide-read-agent-v6", "sha256": "a" * 64},
    {"version": CONTRACT_VERSION, "sha256": "a" * 64},
    {"version": CONTRACT_VERSION, "sha256": True},
])
def test_invalid_or_old_bindings_are_rejected(binding):
    with pytest.raises(ValueError, match="runtime contract binding mismatch"):
        validate_execution_model_binding(binding)


def test_binding_does_not_accept_extra_fields_or_return_shared_storage():
    binding = execution_model_binding(execution_model())
    binding["rules"] = []
    with pytest.raises(ValueError, match="runtime contract binding mismatch"):
        validate_execution_model_binding(binding)


def test_prompt_transmits_one_authoritative_contract_and_exact_source():
    prepared = material()
    prompt = build_prompt(prepared)
    instructions, encoded = prompt.split("\nINPUT_JSON\n", 1)
    payload = json.loads(encoded)
    assert payload == prepared
    assert payload["execution_model"] == execution_model()
    assert "sole authoritative runtime contract" in instructions
    assert "Missing execution details covered by defaults permit normal annotation" in instructions
    assert "not measured execution" in instructions
    for rule in execution_model()["rules"]:
        assert rule["text"] not in instructions
    assert "runtime" not in payload  # no per-Skill runtime selector


def test_default_evidence_has_its_own_rule_quote_not_a_fabricated_source_quote():
    prepared = material()
    rule = execution_model()["rules"][1]
    quoted = "not to everything the tool internally read"
    check_evidence({"basis": "execution_model", "ref_id": rule["id"], "quote": quoted}, prepared)
    with pytest.raises(ValueError, match="quote"):
        check_evidence({"basis": "execution_model", "ref_id": "EM02", "quote": "verified actual execution"}, prepared)
    source_id = prepared["source_index"][0]["id"]
    with pytest.raises(ValueError, match="quote"):
        check_evidence({"basis": "source", "ref_id": source_id, "quote": quoted}, prepared)


def test_report_distinguishes_contract_evidence_without_reason_keyword_inference():
    prepared = material()
    rule = prepared["execution_model"]["rules"][2]
    result = {
        "run_id": "contract", "status": "complete", "reason": "记录完整", "notice": "不是语义证明",
        "graph_sha256": "graph", "execution_model": execution_model_binding(execution_model()),
        "profiles": {"ir_read": {"operator": ["llm"], "roles": ["sink"], "effects": ["model_observe"],
            "evidences": [{"field": "effects", "value": "model_observe", "effect_index": 0,
                           "basis": "execution_model", "ref_id": "EM03", "quote": rule["text"],
                           "reason": "测试任意理由文本，不据关键词判定事实。"}]}},
    }
    report = render_report(result, prepared)
    assert "静态可能性，不是执行轨迹" in report
    assert CONTRACT_VERSION in report and result["execution_model"]["sha256"] in report
    assert "契约依据，非实测" in report
    assert "泛化未决" not in report
    assert result["profiles"]["ir_read"]["effects"] == ["model_observe"]
    result["execution_model"]["sha256"] = "a" * 64
    with pytest.raises(ValueError, match="runtime contract binding mismatch"):
        render_report(result, prepared)
