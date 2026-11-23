"""Source review and shared revision can identify real sites in a rejected draft."""
from copy import deepcopy
import json

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.graph_facts import assemble_graph_facts
from skillflow.document_guided.graph_slots import plan_graph_repair, apply_graph_updates
from skillflow.document_guided.source_review import prepare_review_material, validate_source_review
from tests.document_guided.test_failed_stage_review_targets import failure_evidence, response, stage_finding


FILES = {"skill/source": "Get mode.\nCreate the collection and item.\nAppend item and save the result.\nPrint help if directly invoked.\nReturn mode.\n"}


def span(line):
    return {"file": "skill/source", "start_line": line, "end_line": line}


def op(ref, role, inputs, outputs, line):
    return {"ref": ref, "opcode": role, "inputs": inputs, "outputs": outputs, "source": span(line)}


def draft():
    return {"entry": "absent", "blocks": [
        {"ref": "start", "source_kind": "context", "operations": [
            op("receive", "receive", [{"context_key": "direct"}], ["mode"], 1)],
         "exit": {"kind": "jump", "target": "work", "source": span(1)}},
        {"ref": "work", "source_kind": "normal", "operations": [
            op("collection", "value", [{"literal": []}], ["collection"], 2),
            op("item", "value", [{"literal": 1}], ["item"], 2),
            op("append", "value", [{"result": "collection"}], ["updated"], 3),
            op("save", "write", [{"result": "collection"}], [], 3)],
         "exit": {"kind": "jump", "target": "end", "source": span(3)}},
        {"ref": "end", "source_kind": "normal", "operations": [],
         "exit": {"kind": "return", "values": [{"result": "mode"}], "source": span(5)}}]}


@pytest.mark.parametrize("as_text", [False, True])
def test_failed_draft_sites_connect_updated_collection_and_add_conditional_delivery(as_text):
    facts = draft()
    failure = failure_evidence(FILES)
    envelope = failure["evidence"]
    value = json.dumps(facts) if as_text else facts
    envelope["material"]["candidate"] = value
    envelope["material_sha256"] = canonical_sha256(envelope["material"])
    material = prepare_review_material(files=FILES, stage_failures={"graph": failure}, generation="fragment-v1")
    prefix = "stage:graph/blocks/"
    collection = {**stage_finding(), "required_graph_edit": "field", "source_refs": [span(3)],
                  "target_ids": [prefix + "work/operations/append", prefix + "work/operations/save"]}
    console = {**stage_finding(), "required_graph_edit": "action_inventory", "source_refs": [span(4)],
               "target_ids": [prefix + "end/exit"]}
    findings = validate_source_review(response(collection, console), material)["findings"]
    base = assemble_graph_facts(facts, files=FILES)
    assert base.cfg is None
    plan = plan_graph_repair(base, findings=findings, files=FILES)
    assert not plan["unaddressable_findings"]
    slots = {tuple(s["path"]): s["slot_id"] for s in plan["slots"].values()}
    new_blocks = [
        {**facts["blocks"][2], "exit": {"kind": "branch", "conditions": [{"result": "mode"}],
         "arms": [{"condition": "direct", "target": "end.help"}, {"condition": "import", "target": "end.join"}],
         "source": span(4)}},
        {"ref": "end.help", "source_kind": "normal",
         "operations": [op("help", "deliver", [{"literal": "help"}], [], 4)],
         "exit": {"kind": "jump", "target": "end.join", "source": span(4)}},
        {**facts["blocks"][2], "ref": "end.join"}]
    edits = {("entry",): "start", ("blocks", 1, "operations", 2, "inputs"): [{"result": "collection"}, {"result": "item"}],
             ("blocks", 1, "operations", 3, "inputs"): [{"result": "updated"}],
             ("blocks", 2): new_blocks}
    result = apply_graph_updates(base, plan, {"plan_sha256": plan["plan_sha256"], "updates": [
        {"slot_id": slots[path], "value": value} for path, value in edits.items()]}, files=FILES)
    assert result.cfg and not result.patch_diagnostics
    work = result.facts["blocks"][1]
    assert work["operations"][2]["inputs"][-1] == {"result": "item"}
    assert work["operations"][3]["inputs"] == [{"result": "updated"}]
    assert result.facts["blocks"][2:] == new_blocks
    assert material["availability"]["cfg"] is False
    stale = deepcopy(material)
    stale["stage_failures"]["graph"]["reason"] += " (changed)"
    with pytest.raises(StructuralValidationError, match="stale|bound|differs"):
        validate_source_review(response(collection), stale)
    root_only = plan_graph_repair(base, findings=[{**collection, "target_ids": ["stage:graph"]}], files=FILES)
    assert root_only["unaddressable_findings"] and ("blocks", 1, "operations", 3, "inputs") not in {
        tuple(s["path"]) for s in root_only["slots"].values()}
