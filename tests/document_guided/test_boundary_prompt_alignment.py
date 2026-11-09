"""Delivered contracts preserve full coverage, isolation and boundary granularity."""
import json

from skillflow.document_guided.prompts import build_flow_prompt, build_compact_graph_prompt, build_fragment_prompt
from skillflow.propagation.contracts.abstraction import BOUNDARY_GRANULARITY, NECESSITY_EXAMPLE
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from tests.document_guided.test_fragments import fixture


def material_inputs():
    material, _, fragments = fixture()
    files = {"skill/" + row["path"]: row["content"] for row in material["source"]["files"]}
    return material, fragments, files


def test_full_processing_repair_covers_terminators_and_current_graph_without_task():
    material, fragments, files = material_inputs()
    prompt = build_fragment_prompt("processing", files=files, documents={"flow": "Inspect skill/SKILL.md:1-3."},
        cfg=material["cfg"], runtime_contract=runtime_contract(), global_requirements="Preserve receiving versions.",
        repair_context={"previous_fragment": fragments["processing"], "source_rechecks": []})
    assert "including dispatch and return" in prompt
    assert "COMPLETE replacement fragment for the CURRENT CFG and Task version" in prompt
    assert "not an implicit merge" in prompt
    start = prompt.index("REQUIRED_IR_IDS\n") + len("REQUIRED_IR_IDS\n")
    ids, _ = json.JSONDecoder().raw_decode(prompt[start:])
    assert ids == [ir["id"] for b in material["cfg"]["blocks"].values() for ir in b["instructions"]]
    assert "SEALED_TASK" not in prompt
    assert BOUNDARY_GRANULARITY in prompt


def test_all_frontend_views_share_granularity_and_sensitivity_stays_task_isolated():
    material, fragments, files = material_inputs()
    flow = build_flow_prompt(files=files, global_requirements="Keep source boundaries.")
    graph = build_compact_graph_prompt(files=files, documents={"flow": "Inspect skill/SKILL.md:1-3."},
        global_requirements="Keep source boundaries.")
    sensitivity = build_fragment_prompt("sensitivity", files=files, documents={"processing": fragments["processing"]},
        cfg=material["cfg"], global_requirements="Keep source boundaries.")
    mapping = build_fragment_prompt("task-correspondence", files=files, documents={"processing": fragments["processing"]},
        cfg=material["cfg"], task=material["task"], global_requirements="Keep source boundaries.")
    for prompt in (flow, graph, sensitivity, mapping):
        assert BOUNDARY_GRANULARITY in prompt
        assert "Code bodies remain black boxes" not in prompt
    assert "SEALED_TASK" not in sensitivity
    assert NECESSITY_EXAMPLE not in sensitivity
    assert NECESSITY_EXAMPLE in mapping
    assert "rows -> each -> keys" in mapping
    assert any(BOUNDARY_GRANULARITY == rule["text"] for rule in runtime_contract()["rules"])
    rules = runtime_contract()["rules"]
    assert len({rule["id"] for rule in rules}) == len(rules)
