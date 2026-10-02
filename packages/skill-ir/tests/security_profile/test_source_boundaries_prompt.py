"""Prompt/input contracts, not a claim that an LLM always follows these rules."""

import json
import re

import pytest

from security_profile.helpers import graph, source_bundle
from skill_ir.runtime_contract import execution_model
from skill_ir.security_profile.evidence import prepare_material
from skill_ir.security_profile.prompts import INSTRUCTIONS, build_prompt


def test_source_rules_replace_stale_read_only_stage_and_keep_english_instructions():
    assert execution_model()["version"] == "skillflow-abstract-runtime-v5"
    rules = {item["id"]: item["text"] for item in execution_model()["rules"]}
    assert len(rules) == len(execution_model()["rules"])
    assert "This stage only labels the read effect" not in rules["EM01"]
    assert "does not establish a key-only read mechanism" in rules["EM01"]
    assert "do not invent other fields" in rules["EM01"]
    assert "not proof that an actual execution reads the whole" in rules["EM01"]
    assert "not to everything the tool internally read" in rules["EM02"]
    assert "scan alone does not expose the whole file" in rules["EM02"]
    assert "Local reading and LLM scheduling alone" in rules["EM03"]
    assert "Defaults apply normally when execution details are absent" in rules["EM03"]
    assert "whose result alone is returned" in rules["EM04"]
    assert "model-invisible credential proxy or isolated handle" in rules["EM04"]
    assert "Unknown content in an identified source is not an unknown address" in rules["EM08"]
    assert "does not broaden later API arguments" in rules["EM06"]
    assert "receive at a tool location in a null-effect event" in rules["EM09"]
    assert "An explicitly pure calculation remains compute" in rules["EM09"]
    assert not re.search(r"[\u3400-\u9fff]", INSTRUCTIONS)
    assert all(not re.search(r"[\u3400-\u9fff]", text) for text in rules.values())


@pytest.mark.parametrize("phrases", [
    ("unspecified request keeps a possible whole-request read", "an evidenced local key-only getter"),
    ("Model filtering declares model mode", "explicit local filtering declares local mode with only the selected result returned"),
    ("only its returns", "are outbound parameters still limited to their actual bindings"),
    ("EM09 independently of network classification", "network claim"),
    ("symbolic: only for dynamic or non-unique target identity", "Unknown content inside an identified container is not an unknown location"),
    ("Reuse an identified container across acquisitions of different fields", "Do not replace a source whole by an unrelated field source"),
])

def test_prompt_carries_paired_positive_and_restrictive_boundaries(phrases):
    for phrase in phrases:
        assert phrase in INSTRUCTIONS


def test_payload_preserves_complete_source_graph_and_uses_one_execution_model():
    text = "# 来源\n从请求取得城市。明确本地取值例：getter('city')。\n"
    prepared = prepare_material(source_bundle(text), graph())
    prompt = build_prompt(prepared)
    payload = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
    assert payload == prepared
    assert payload["source"]["files"][0]["content"] == text
    assert payload["cfg"] == graph()
    assert payload["execution_model"] == execution_model()
    assert "Write all inference reasons and failure explanations in Chinese" in INSTRUCTIONS
    assert "FINAL CONSISTENCY CHECK" in INSTRUCTIONS
    assert "Data IDs" in INSTRUCTIONS


def test_operand_relation_is_not_ancestor_alias_and_null_receive_not_network():
    for phrase in (
        "not any ancestor source of that value",
        "container may have operand_refs=[]",
        "A single operand may have several supported possible locations",
        "tool is a content-acquisition or delivery boundary without a network claim",
        "It must not hide a known network effect",
        "A null event must not introduce reads, non-tool deliveries, writes, selections, exclusions, updates, or builds",
    ):
        assert phrase in INSTRUCTIONS
