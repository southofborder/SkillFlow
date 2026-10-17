from tests.propagation.annotation.helpers import effects_of
"""Runtime identity and evidence transport checks, not a model truth oracle."""

from copy import deepcopy
import json

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.contracts.runtime_contract import CONTRACT_VERSION
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from skillflow.propagation.contracts.runtime_contract import runtime_contract_binding
from skillflow.propagation.contracts.runtime_contract import validate_runtime_contract
from skillflow.propagation.contracts.runtime_contract import validate_runtime_contract_binding
from skillflow.propagation.material import checked_material
from skillflow.propagation.material import check_evidence, evidence_reference, model_material
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.annotation.report import render_report
from tests.propagation.annotation.helpers import material, semantics


def test_one_isolated_contract_and_canonical_binding():
    current = runtime_contract()
    assert set(current) == {"version", "rules"}
    assert current["version"] == CONTRACT_VERSION == "skillflow-abstract-runtime-v7"
    assert [rule["id"] for rule in current["rules"]] == [f"EM{i:02}" for i in range(1, 16)]
    binding = runtime_contract_binding(current)
    assert binding == {"version": CONTRACT_VERSION, "sha256": canonical_sha256(current)}
    checked = validate_runtime_contract(current)
    checked["rules"][0]["text"] = "changed"
    assert current == runtime_contract()
    validated_binding = validate_runtime_contract_binding(binding)
    validated_binding["sha256"] = "changed"
    assert binding == runtime_contract_binding(runtime_contract())
    current["rules"].clear()
    assert len(runtime_contract()["rules"]) == 15


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
    model = runtime_contract()
    change(model)
    with pytest.raises(ValueError, match="runtime contract identity mismatch"):
        validate_runtime_contract(model)
    with pytest.raises(ValueError, match="runtime contract identity mismatch"):
        runtime_contract_binding(model)
    prepared = material()
    prepared["runtime_contract"] = model
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
        validate_runtime_contract_binding(binding)


def test_binding_does_not_accept_extra_fields_or_return_shared_storage():
    binding = runtime_contract_binding(runtime_contract())
    binding["rules"] = []
    with pytest.raises(ValueError, match="runtime contract binding mismatch"):
        validate_runtime_contract_binding(binding)


def test_prompt_transmits_one_authoritative_contract_and_exact_source():
    prepared = material()
    prompt = build_prompt(prepared)
    encoded = prompt.split("\nINPUT_JSON\n", 1)[1]
    payload = json.JSONDecoder().raw_decode(encoded)[0]
    instructions = prompt.split("<!-- SKILLFLOW_PROMPT:INPUT:BEGIN -->")[0] + prompt.split("<!-- SKILLFLOW_PROMPT:INPUT:END -->")[1]
    assert payload == model_material(prepared)
    assert payload["runtime_contract"] == runtime_contract()
    assert "runtime_contract" in instructions
    assert "default" in instructions and "cannot_assess" in instructions
    assert "not execution facts" in instructions
    for rule in runtime_contract()["rules"]:
        assert rule["text"] not in instructions
    assert "runtime" not in payload  # no per-Skill runtime selector


def test_default_evidence_resolves_exact_rule_without_model_written_quote():
    prepared = material()
    rule = runtime_contract()["rules"][1]
    evidence = {"rule_id": rule["id"], "reason": "The declared default applies here."}
    check_evidence(evidence, prepared)
    resolved = evidence_reference(evidence, prepared)
    assert resolved["kind"] == "runtime_contract"
    assert resolved["text"] == rule["text"]
    with pytest.raises(ValueError, match="does not exist"):
        check_evidence({**evidence, "rule_id": "not-a-rule"}, prepared)
    with pytest.raises(ValueError):
        check_evidence({**evidence, "basis": "runtime_contract", "quote": "fabricated"}, prepared)
    source = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
              "reason": "Exact source identity, not an execution-rule claim."}
    assert evidence_reference(source, prepared)["kind"] == "source"
    assert evidence_reference(source, prepared)["text"] == prepared["source"]["files"][0]["content"].splitlines(keepends=True)[0]


def test_report_distinguishes_contract_evidence_without_reason_keyword_inference():
    prepared = material()
    spec = semantics(prepared, "ir_read", operator=["llm"], effects=["model_observe"])
    spec["events"][0]["evidences"] = [{"rule_id": "EM03", "reason": "Arbitrary prose; category is resolved from the typed rule table."}]
    result = {
        "run_id": "contract", "status": "complete", "reason": "Complete record", "notice": "Not a semantic proof",
        "graph_sha256": "graph", "runtime_contract": runtime_contract_binding(runtime_contract()),
        "ir_semantics": {"ir_read": spec},
    }
    report = render_report(result, prepared)
    assert "static possibilities under the contract, not an execution trace" in report
    assert CONTRACT_VERSION in report and result["runtime_contract"]["sha256"] in report
    assert prepared["runtime_contract"]["rules"][2]["text"] in report
    assert "`EM03`" in report
    assert "泛化未决" not in report
    assert effects_of(result["ir_semantics"]["ir_read"]) == ["model_observe"]
    result["runtime_contract"]["sha256"] = "a" * 64
    with pytest.raises(ValueError, match="runtime contract binding mismatch"):
        render_report(result, prepared)
