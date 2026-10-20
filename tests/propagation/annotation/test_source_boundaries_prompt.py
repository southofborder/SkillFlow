"""Prompt/input contracts, not a claim that an LLM always follows these rules."""

import json
import re

import pytest

from tests.propagation.annotation.helpers import graph, source_bundle
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from tests.propagation.annotation.helpers import prepare_material
from skillflow.propagation.material import model_material
from skillflow.propagation.annotation.prompts import INSTRUCTIONS
from skillflow.propagation.annotation.prompts import build_prompt


def test_source_rules_replace_stale_read_only_stage_and_keep_english_instructions():
    assert runtime_contract()["version"] == "skillflow-abstract-runtime-v7"
    rules = {item["id"]: item["text"] for item in runtime_contract()["rules"]}
    assert len(rules) == len(runtime_contract()["rules"])
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
    ("retain the declared source and target value separately", "Apply runtime defaults or explicit local mechanisms"),
    ("Explicit model content processing uses mode=model", "Only explicit local execution AND its content-visibility/return boundary"),
    ("State returns explicitly", "bind public outputs and actual arguments"),
    ("Receiving tool content is acquisition, not query-only computation", "networking is a separate claim"),
    ("An identified source may remain opaque without fabricated fields", "Reuse identities and supported aliases"),
    ("A selected field operand does not identify its entire source container", "read/local/select_part"),
])
def test_prompt_carries_paired_positive_and_restrictive_boundaries(phrases):
    for phrase in phrases:
        assert phrase in INSTRUCTIONS


def test_payload_preserves_complete_source_graph_and_uses_one_runtime_contract():
    text = "# 来源\n从请求取得城市。明确本地取值例：getter('city')。\n"
    prepared = prepare_material(source_bundle(text), graph())
    prompt = build_prompt(prepared)
    payload = json.JSONDecoder().raw_decode(prompt.split("\nINPUT_JSON\n", 1)[1])[0]
    assert payload == model_material(prepared)
    assert "".join(payload["source"]["files"][0]["lines"]) == text
    assert payload["cfg"] == graph()
    assert payload["runtime_contract"] == runtime_contract()
    assert "failure reasons in English" in INSTRUCTIONS
    assert "COMPLETE RESPONSE AND FAILURE" in INSTRUCTIONS
    assert "Data IDs" in INSTRUCTIONS


def test_operand_relation_is_not_ancestor_alias_and_null_receive_not_network():
    for phrase in (
        "Do not invent an operand for an implicit boundary or confuse an ancestor source",
        "unanchored source location may use operand_refs=[]",
        "Reuse identities and supported aliases",
        "networking is a separate claim",
        "it cannot hide reads, writes, field transformations or known networking",
    ):
        assert phrase in INSTRUCTIONS
