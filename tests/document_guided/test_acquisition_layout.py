from copy import deepcopy

import pytest

from skillflow.document_guided.graph_facts import (
    ARCHIVED_IDENTITY, BLOCK_KIND_RULES, PREVIOUS_IDENTITY, assemble_graph_facts, from_accepted_cfg,
    instruction_ref,
)
from skillflow.document_guided.prompts import build_graph_facts_prompt, build_graph_updates_prompt
from skillflow.graph.extraction.compiler import CompileDiagnostic, CompileResult
from tests.document_guided.test_program_graph_facts import FILES, facts, span


def acquisition_with_body():
    raw = facts()
    entry, done = raw["blocks"]
    entry["operations"].append({"ref": "use", "opcode": "value", "inputs": [{"result": "value"}],
                                "outputs": ["converted"], "source": span(2), "constraints": ["Use the actual value."]})
    done["exit"]["values"] = [{"result": "converted"}]
    return raw


def test_split_preserves_source_ports_and_original_refs_across_self_loop():
    raw = acquisition_with_body()
    raw["blocks"][0]["exit"] = {"kind": "branch", "conditions": [{"result": "converted"}], "source": span(2),
                                "arms": [{"target": "start", "condition": "again"}, {"target": "done", "condition": "finished"}]}
    raw["blocks"][1]["source_kind"] = "context"
    original = deepcopy(raw)
    result = assemble_graph_facts(raw, files=FILES)
    assert raw == result.facts == original
    assert result.cfg is not None and result.gaps == []
    assert result.block_layout == {"start": {"kind": "split", "continuation": "start.body"}, "done": {"kind": "control"}}
    assert result.to_receipt()["block_layout"] == result.block_layout
    acquire, body, done = result.candidate["blocks"]
    assert [b["data_source_kind"] for b in (acquire, body, done)] == ["context", None, None]
    receive, bridge = acquire["instructions"]
    use, branch = body["instructions"]
    assert [row["instruction_ref"] for row in (receive, use, branch)] == [
        instruction_ref("start", "collect"), instruction_ref("start", "use"), instruction_ref("start")]
    assert bridge == {"instruction_ref": "/blocks/start/continuation", "opcode": "dispatch", "inputs": [],
                      "outputs": [], "constraints": [], "metadata": {}}
    assert receive["inputs"] == [{"type": "context_key", "identifier": "request"}]
    assert use["inputs"] == receive["outputs"] and use["outputs"] == branch["inputs"]
    assert use["constraints"] == ["Use the actual value."]
    assert {(e["source_block_ref"], e["target_block_ref"], e["condition_text"]) for e in result.candidate["edges"]} == {
        ("start", "start.body", None), ("start.body", "start", "again"), ("start.body", "done", "finished")}
    assert assemble_graph_facts(result.facts, files=FILES, canonical_ids=result.id_map).to_receipt() == result.to_receipt()
    assert from_accepted_cfg(result.cfg, files=FILES).cfg == result.cfg


def test_generated_body_cannot_capture_authored_block_or_missing_target():
    raw = acquisition_with_body()
    raw["blocks"][0]["exit"]["target"] = raw["blocks"][1]["ref"] = "start.body"
    result = assemble_graph_facts(raw, files=FILES)
    assert result.cfg and result.block_layout["start"]["continuation"] == "start.body.2"
    raw["blocks"][0]["exit"]["target"] = "start.body.2"
    broken = assemble_graph_facts(raw, files=FILES)
    assert broken.cfg is None
    assert broken.block_layout["start"]["continuation"] == "start.body.3"
    assert [gap["path"] for gap in broken.gaps] == ["/blocks/0/exit/target"]


def test_addition_of_a_continuation_preserves_existing_canonical_ids():
    old = assemble_graph_facts(facts(), files=FILES, normalize_blocks=False)
    new = assemble_graph_facts(acquisition_with_body(), files=FILES, canonical_ids=old.id_map)
    assert old.cfg and new.cfg
    for table, previous in old.id_map.items():
        assert previous.items() <= new.id_map[table].items()
    graph = new.cfg["blocks"]
    first_id = old.id_map["blocks"]["start"]
    body_id = new.id_map["blocks"]["start.body"]
    assert graph[first_id]["instructions"][0]["id"] == old.id_map["instructions"][instruction_ref("start", "collect")]
    assert graph[body_id]["instructions"][-1]["id"] == old.id_map["instructions"][instruction_ref("start")]
    assert graph[first_id]["instructions"][-1]["id"] not in old.id_map["instructions"].values()
    assert from_accepted_cfg(new.cfg, files=FILES).cfg == new.cfg


@pytest.mark.parametrize("change", ["constraints", "mixed_inputs", "extra_context", "call", "composite"])
def test_no_automatic_split_when_roles_or_scope_do_not_establish_a_pure_acquisition(change):
    raw = acquisition_with_body()
    entry = raw["blocks"][0]
    first, second = entry["operations"]
    if change == "constraints":
        entry["constraints"] = ["Omit the optional property on this operation."]
    elif change == "mixed_inputs":
        first["inputs"].append({"literal": 1})
    elif change == "extra_context":
        second["inputs"].append({"context_key": "second"})
    elif change == "call":
        first.update(opcode="call", role="call")
    else:
        first["source_actions"] = [{"ref": "read", "kind": "read", "source": span()},
                                   {"ref": "call", "kind": "call", "source": span(2)}]
    result = assemble_graph_facts(raw, files=FILES)
    assert result.cfg is None and result.block_layout == {}
    assert ("acquisition_shape", "/blocks/0/operations") in {(row["code"], row["path"]) for row in result.gaps}


def test_raw_exit_operand_is_retained_for_repair():
    raw = facts()
    raw["blocks"][1].update(source_kind="context")
    raw["blocks"][1]["exit"]["values"] = [{"context_key": "missing producer"}]
    draft = assemble_graph_facts(raw, files=FILES)
    assert not draft.block_layout and draft.cfg is None
    assert any(row["path"] == "/blocks/1/exit/values/0" for row in draft.gaps)


def test_compiler_diagnostic_after_split_still_addresses_original_operand(monkeypatch):
    raw = acquisition_with_body()

    def diagnostic(candidate, *, canonical_ids):
        assert candidate.blocks[1].instructions[0].instruction_ref == instruction_ref("start", "use")
        return CompileResult(diagnostics=[CompileDiagnostic(code="invalid", path="blocks[1].instructions[0].inputs[0]",
                                                            message="Invalid operation input")])

    monkeypatch.setattr("skillflow.document_guided.graph_facts.compile_candidate", diagnostic)
    draft = assemble_graph_facts(raw, files=FILES)
    assert [gap["path"] for gap in draft.gaps] == ["/blocks/0/operations/1/inputs/0"]


def test_duplicate_edge_after_split_maps_back_to_authored_arm():
    raw = acquisition_with_body()
    raw["blocks"][0]["exit"] = {"kind": "branch", "conditions": [{"result": "converted"}], "source": span(2),
                                "arms": [{"target": "done", "condition": "same"}] * 2}
    draft = assemble_graph_facts(raw, files=FILES)
    assert ("DUPLICATE_EDGE", "/blocks/0/exit/arms/1/target") in {(gap["code"], gap["path"]) for gap in draft.gaps}


def test_external_acquisition_keeps_real_resource_and_one_version():
    raw = acquisition_with_body()
    entry = raw["blocks"][0]
    entry.update(source_kind="external")
    entry["operations"][0].update(inputs=[{"external_resource": "config.json"}])
    assembled = assemble_graph_facts(raw, files=FILES)
    assert assembled.cfg
    assert [(b["data_source_kind"], len(b["instructions"])) for b in assembled.candidate["blocks"]] == [
        ("external", 2), (None, 2), (None, 1)]


def test_previous_fact_and_prompt_contracts_keep_their_acquisition_behavior():
    raw = acquisition_with_body()
    prior = assemble_graph_facts(raw, files=FILES, normalize_blocks=False)
    assert prior.cfg is None and prior.to_receipt()["identity"] == PREVIOUS_IDENTITY
    assert "block_layout" not in prior.to_receipt()
    del raw["blocks"][0]["operations"][0]["role"]
    archived = assemble_graph_facts(raw, files=FILES, archived=True)
    assert archived.cfg is None and archived.to_receipt()["identity"] == ARCHIVED_IDENTITY
    prompt = dict(files=FILES, documents={"flow": "Read and return."}, global_requirements="Complete source.")
    assert BLOCK_KIND_RULES in build_graph_facts_prompt(**prompt)
    assert BLOCK_KIND_RULES not in build_graph_facts_prompt(**prompt, normalize_blocks=False)
    assert BLOCK_KIND_RULES in build_graph_updates_prompt(files=FILES, plan={})
    assert BLOCK_KIND_RULES not in build_graph_updates_prompt(files=FILES, plan={}, normalize_blocks=False)
