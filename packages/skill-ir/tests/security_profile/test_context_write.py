"""Compiled action/write boundaries, not a semantic truth oracle."""

from copy import deepcopy
import json

import pytest

from skill_ir.security_profile.evidence import prepare_material
from skill_ir.security_profile.models import EFFECTS, OPERATORS
from skill_ir.security_profile.prompts import build_prompt
from skill_ir.security_profile.services import validate_compiled_response
from security_profile.helpers import graph, material, profile, source_bundle, valid_response, with_specs


@pytest.mark.parametrize("placement", ["profile", "profile_with_both", "evidence", "unresolved"])
def test_actor_is_rejected_everywhere_without_alias_migration(placement):
    prepared = material()
    response = valid_response(prepared)
    item = response["profiles"]["ir_read"]
    if placement == "profile":
        item["actor"] = item.pop("operator")
    elif placement == "profile_with_both":
        item["actor"] = item["operator"]
    elif placement == "evidence":
        item["evidences"][0]["field"] = "actor"
    else:
        response["unresolved"] = [{"instruction_id": "ir_read", "field": "actor", "reason": "未知执行主体"}]
    before = deepcopy(response)
    with pytest.raises(ValueError):
        validate_compiled_response(with_specs(prepared, response), prepared)
    assert response == before


def test_operator_is_multivalued_and_vocabularies_have_no_other_additions():
    prepared = material()
    response = valid_response(prepared)
    response["profiles"]["ir_read"] = profile(prepared, "ir_read", operator=list(reversed(OPERATORS)))
    accepted = validate_compiled_response(with_specs(prepared, response), prepared)
    assert accepted["profiles"]["ir_read"]["operator"] == ["human", "tool", "agent_runtime", "llm"]
    assert set(EFFECTS) == {"context_read", "context_write", "fs_read", "fs_write", "net_send",
                           "net_receive", "model_observe", "user_output", "transform"}


@pytest.mark.parametrize("source_text,effects,roles", [
    ("将 B 原样保存到共享上下文 cached_document，不提交给模型。", ["context_write"], ["sink"]),
    ("本地处理调用先删除字段，再将处理结果写回共享上下文。", ["transform", "context_write"], ["transformer", "sink"]),
    ("仅将 B 原样转交为本动作的结果，不修改共享状态。", [], []),
    ("把 B 写入本地文件，不修改运行时上下文。", ["fs_write"], ["sink"]),
    ("保存到尚未提交模型的会话缓存，不调用模型。", ["context_write"], ["sink"]),
    ("把 B 交给模型本次处理，不更新共享会话缓存。", ["model_observe"], ["sink"]),
    ("仅移除共享上下文中的绑定，不读取其内容。", ["context_write"], []),
])
def test_compiled_scenarios_preserve_labels_without_opcode_inference(source_text, effects, roles):
    # All scenarios deliberately have the same open opcode. The parser checks
    # records and quotations; it must not infer extra effects or roles itself.
    cfg = graph()
    cfg["blocks"]["entry"]["instructions"][1]["opcode"] = "perform_action"
    source = source_bundle(source_text)
    prepared = prepare_material(source, cfg)
    response = valid_response(prepared)
    response["profiles"]["ir_filter"] = profile(
        prepared, "ir_filter", operator=["agent_runtime"], roles=roles, effects=effects,
    )
    source_location = prepared["source_index"][0]["id"]
    for evidence in response["profiles"]["ir_filter"]["evidences"]:
        evidence.update(basis="source", ref_id=source_location, quote=source_text,
                        reason="离线注入的预期标注；验证保存与证据绑定，不证明模型语义判断。")
    with_specs(prepared, response)
    before = deepcopy((source, cfg, response))
    # These are final compiled-record fixtures. Raw model responses declare
    # processing boundaries; compiler/runner tests cover that entry point.
    accepted = validate_compiled_response(response, prepared)
    assert accepted == response
    assert accepted["profiles"]["ir_filter"]["effects"] == effects
    assert (source, cfg, response) == before


def test_context_write_occurrences_require_separate_matching_evidence():
    prepared = material()
    response = valid_response(prepared)
    item = profile(prepared, "ir_filter", operator=["agent_runtime"],
                   effects=["context_write", "transform", "context_write"])
    response["profiles"]["ir_filter"] = item
    assert validate_compiled_response(json.dumps(with_specs(prepared, response), ensure_ascii=False), prepared) == response
    item["evidences"][-1]["effect_index"] = 0
    with pytest.raises(ValueError, match="lacks evidence"):
        validate_compiled_response(with_specs(prepared, response), prepared)
    item["evidences"][-1]["effect_index"] = 1
    with pytest.raises(ValueError, match="label does not match"):
        validate_compiled_response(with_specs(prepared, response), prepared)


def test_old_execution_model_or_profile_material_cannot_be_reinterpreted():
    for key, value in (("version", "security-profile-v2"), ("execution_model", {"version": "wide-read-agent-v2", "rules": []})):
        prepared = material()
        prepared[key] = value
        with pytest.raises(ValueError):
            build_prompt(prepared)
