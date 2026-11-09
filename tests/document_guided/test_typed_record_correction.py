"""Typed Task, CFG and review records use the same bounded text correction."""
from copy import deepcopy
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import injected_factory, read_json
from skillflow.common.structural_correction import ResponseChain, StructuralCorrectionLimitReached
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.document_guided.online import analysis_config, validate_step
from skillflow.document_guided.source_review import run_source_review, replay_saved_review
from skillflow.task.runner import prepare_task_run, run_task
from tests.document_guided.test_source_review import fixture as review_fixture, finding
from tests.task.test_protocol import source


class TextClient:
    def __init__(self, *values):
        self.values = [json.dumps(value) for value in values]
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return self.values.pop(0)


@pytest.fixture(autouse=True)
def offline_producer(monkeypatch):
    from tests.document_guided.test_parallel_runner import freeze_producer
    freeze_producer(monkeypatch)


def replacement(identity, value):
    return {"replacements": [{"record_id": identity, "value": value}]}


def task_candidate():
    span = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "reason": "The original source explicitly requires this behavior."}
    return {"purpose": {"text": "Return the original label.", "evidences": [deepcopy(span)]},
        "requirements": [{"id": "R1", "text": "Return label unchanged.", "evidences": [deepcopy(span)]},
                         {"id": "R2", "text": "Never send serial.", "evidences": [deepcopy(span)]}], "issues": []}


def test_task_source_citation_corrects_one_record_and_legacy_keeps_whole_default(tmp_path):
    good = task_candidate()
    bad = deepcopy(good)
    bad["requirements"][0]["evidences"][0]["end_line"] = 999
    fixed = replacement("/requirements/0", good["requirements"][0])
    directory = tmp_path / "new"
    prepare_task_run(directory, source(), max_corrections=1, allow_cannot_assess=False)
    client = TextClient(bad, fixed)
    result = run_task(directory, client=client)
    assert result["status"] == "complete", result
    assert result["counts"]["structural_corrections"] == 1 and len(client.prompts) == 2
    assert "MECHANICAL RECORD CORRECTION" in client.prompts[1]
    assert "unlisted record unchanged" in client.prompts[1]
    merged = read_json(directory / "calls/task/a002/merged-candidate.json")
    assert merged == good
    assert merged["purpose"] == bad["purpose"] and merged["requirements"][1] == bad["requirements"][1]
    assert read_json(directory / "calls/task/a002/response.json") == json.dumps(fixed)
    assert ":task:" in result["response_chain"]["correction_strategy"]
    assert run_task(directory, replay=True) == result
    assert run_task(directory) == result
    assert not (directory / "calls/task/a003").exists()
    legacy = tmp_path / "legacy"
    prepare_task_run(legacy, source(), max_corrections=1)
    old = run_task(legacy, client=TextClient(good))
    assert old["status"] == "complete" and "correction_strategy" not in old["response_chain"]


def cfg_candidate():
    return {"entry_block_ref": "read", "blocks": [
        {"block_ref": "read", "data_source_kind": "context", "instructions": [{"opcode": "read_request",
            "inputs": [{"type": "context_key", "identifier": "request"}],
            "outputs": [{"type": "result", "identifier": "request_value"}]},
            {"opcode": "dispatch", "inputs": [{"type": "result", "identifier": "request_value"}]}]},
        {"block_ref": "return", "instructions": [{"opcode": "return",
            "inputs": [{"type": "result", "identifier": "request_value"}]}]}],
        "edges": [{"source_block_ref": "read", "target_block_ref": "return"}]}


def cfg_chain(directory, client=None, *, replay=False):
    return ResponseChain(directory, prefix="calls", base_prompt="Return the supplied CFG wire format.",
        request_kind="cfg_wire_v5", config=analysis_config(), writer=ArtifactWriter(()),
        validate=lambda raw: validate_step("cfg_wire_v5", raw, context={"files": {
            "skill/SKILL.md": "Read the request and return its original value.\n"}}),
        max_corrections=1, correction_strategy=fragment_correction_strategy("cfg"),
        client_factory=injected_factory(client) if client else None, replay=replay)


@pytest.mark.parametrize("still_incompatible", [False, True])
def test_cfg_bad_input_record_replacement_keeps_other_blocks_and_revalidates_refs(tmp_path, still_incompatible):
    good = cfg_candidate()
    bad = deepcopy(good)
    bad["blocks"][1]["instructions"][0]["inputs"][0]["type"] = "invalid_operand_type"
    corrected = deepcopy(good["blocks"][1])
    if still_incompatible:
        corrected["instructions"][0]["inputs"][0]["identifier"] = "another_missing_result"
    client = TextClient(bad, replacement("/blocks/1", corrected))
    live = cfg_chain(tmp_path, client)
    if still_incompatible:
        with pytest.raises(StructuralCorrectionLimitReached):
            live.run()
    else:
        assert live.run()["blocks"][1]["instructions"][0]["inputs"][0]["identifier"] == "request_value"
    assert len(client.prompts) == 2 and "MECHANICAL RECORD CORRECTION" in client.prompts[1]
    assert live.last_candidate["blocks"][0] == good["blocks"][0]
    assert live.last_candidate["edges"] == good["edges"]
    assert live.last_candidate["entry_block_ref"] == good["entry_block_ref"]
    assert not (tmp_path / "calls/a003").exists()
    saved = cfg_chain(tmp_path, replay=True)
    if still_incompatible:
        with pytest.raises(StructuralCorrectionLimitReached):
            saved.run()
    else:
        assert saved.run() == live.value
    assert saved.last_candidate == live.last_candidate and saved.snapshot() == live.snapshot()


def test_cfg_entry_singleton_replacement_preserves_block_and_edge_records(tmp_path):
    good = cfg_candidate()
    bad = {**deepcopy(good), "entry_block_ref": "absent"}
    client = TextClient(bad, replacement("/entry_block_ref", "read"))
    live = cfg_chain(tmp_path, client)
    assert live.run()["entry_block_ref"] == "read"
    assert "MECHANICAL RECORD CORRECTION" in client.prompts[1]
    assert live.last_candidate == good
    assert cfg_chain(tmp_path, replay=True).run() == live.value


def test_binary_dispatch_correction_can_add_needed_block_and_rewire_once(tmp_path):
    from skillflow.document_guided.interface_examples import alignment_examples
    good = alignment_examples()["binary_outcome_routing"]["cfg"]
    bad = deepcopy(good)
    bad["blocks"] = [block for block in bad["blocks"] if block["block_ref"] != "retry_check"]
    bad["edges"] = [edge for edge in bad["edges"]
                    if edge["source_block_ref"] != "retry_check" and edge["target_block_ref"] != "retry_check"]
    bad["edges"] += [{"source_block_ref": "ready_check", "target_block_ref": target}
                     for target in ("retry", "stop")]
    client = TextClient(bad, good)
    live = cfg_chain(tmp_path, client)
    result = live.run()
    assert result["entry_block_ref"] == "ready_check"
    assert len(client.prompts) == 2
    assert "MECHANICAL RECORD CORRECTION" not in client.prompts[1]
    assert "binary_dispatch" in client.prompts[1]
    assert live.last_candidate == good
    assert any(block["block_ref"] == "retry_check" for block in live.last_candidate["blocks"])
    assert not (tmp_path / "calls/a003").exists()
    replayed = cfg_chain(tmp_path, replay=True)
    assert replayed.run() == result
    assert replayed.last_candidate == good and replayed.snapshot() == live.snapshot()


@pytest.mark.parametrize("bad_singleton", [False, True])
def test_fragment_review_corrects_one_finding_or_outcome_with_other_records_unchanged(tmp_path, bad_singleton):
    files, task, cfg = review_fixture()
    first, second = finding(), finding()
    second["explanation"] = "A second independent source-supported relationship is absent."
    good = {"outcome": "completed", "findings": [first, second]}
    bad = deepcopy(good)
    if bad_singleton:
        bad["outcome"] = "invalid_outcome"
        fix = replacement("/outcome", "completed")
    else:
        bad["findings"][0]["source_refs"][0]["end_line"] = 999
        fix = replacement("/findings/0", first)
    client = TextClient(bad, fix)
    args = {"files": files, "task": task, "cfg": cfg, "generation": "fragment-v1"}
    result = run_source_review(tmp_path, **args, client=client)
    assert result["status"] == "complete", result
    assert result["counts"]["structural_corrections"] == 1 and len(client.prompts) == 2
    assert "MECHANICAL RECORD CORRECTION" in client.prompts[1]
    assert read_json(tmp_path / "calls/review/a002/merged-candidate.json") == good
    assert ":review:" in result["response_chain"]["correction_strategy"]
    assert len(result["review"]["findings"]) == 2
    assert replay_saved_review(tmp_path) == result
    assert run_source_review(tmp_path, **args, replay=True) == result
    assert not (tmp_path / "calls/review/a003").exists()


@pytest.mark.parametrize("kind,candidate,record,value", [
    ("task", {"purpose": {"text": "original"}, "requirements": [], "issues": []}, "/purpose", {"text": "corrected"}),
    ("task", {"purpose": {}, "requirements": [], "issues": [{"text": "original"}]}, "/issues/0", {"text": "corrected"}),
    ("cfg", cfg_candidate(), "/edges/0", {"source_block_ref": "read", "target_block_ref": "return"}),
])
def test_additional_typed_record_coordinates_use_existing_replacement_grammar(kind, candidate, record, value):
    strategy = fragment_correction_strategy(kind)
    prompt = strategy.build_prompt("Use the actual stage format.", json.dumps(candidate), [
        {"code": "shape", "path": record, "message": "Correct this existing record."}])
    assert "MECHANICAL RECORD CORRECTION" in prompt
    assert strategy.merge(json.dumps(candidate), json.dumps(replacement(record, value)))
