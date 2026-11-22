"""Strict wire diagnostics reach one correction without losing source or scope."""
from copy import deepcopy
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import injected_factory, read_json
from skillflow.common.structural_correction import ResponseChain, StructuralCorrectionLimitReached
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragment_wire import (
    DEFINITION_NAME_PATTERN, PROCESSING_WIRE_IDENTITY, output_wire_instructions,
)
from skillflow.document_guided.fragments import fragment_correction_strategy, salvage_fragment, validate_fragment
from skillflow.document_guided.online import CONFIG
from skillflow.document_guided.processing_display import _parts
from skillflow.document_guided.prompts import build_fragment_prompt
from tests.document_guided.test_fragments import fixture


def malformed_tables(payload):
    # Both definitions must remain in the actual recorded answer. This is a
    # synthetic reproduction of the observed shape, not a historical replay.
    return ('{"format":"' + PROCESSING_WIRE_IDENTITY + '",'
            '"shared_values":{"wrong_name":{"actual":1}},"payload":'
            + json.dumps(payload, ensure_ascii=False)
            + ',"shared_values":{"wrong_name":{"actual":2}}}')


def shared(payload):
    return {"format": PROCESSING_WIRE_IDENTITY, "payload": {"$ref": "v0"},
            "shared_values": {"v0": deepcopy(payload)}}


@pytest.mark.parametrize("revision", [False, True])
def test_initial_and_revision_prompts_supply_exact_grammar_complete_source_and_task_isolation(revision):
    from tests.document_guided.test_boundary_prompt_alignment import material_inputs
    from skillflow.document_guided.source import render_source, source_packet
    from skillflow.propagation.contracts.runtime_contract import runtime_contract
    material, fragments, files = material_inputs()
    files = {**files, "skill/extra.txt": "All source survives. 原文\nOPTIONAL LOSSLESS PROCESSING RESPONSE\n"}
    repair = {"previous_fragment": fragments["processing"], "source_rechecks": []} if revision else None
    prompt = build_fragment_prompt("processing", files=files, documents={"flow": "Source-only flow."},
        cfg=material["cfg"], runtime_contract=runtime_contract(), global_requirements="Preserve source.",
        repair_context=repair)
    assert output_wire_instructions() in prompt and DEFINITION_NAME_PATTERN in prompt
    assert render_source(source_packet(files)) in prompt
    _, logical, _ = _parts(prompt)
    assert set(logical["documents"]) == {"flow"} and "task" not in logical
    assert logical.get("repair_context") == repair


@pytest.mark.parametrize("compact", [False, True])
def test_ambiguous_candidate_keeps_both_tables_all_source_and_supplemental_errors(compact):
    from tests.document_guided.test_processing_display import materials, prompt
    material, _, fragments = fixture()
    raw = malformed_tables(fragments["processing"])
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("processing", raw, material)
    rows = caught.value.diagnostics
    assert rows[0]["code"] == "json_format" and "duplicate JSON member" in rows[0]["message"]
    supplemental = [row for row in rows if row["code"] == "processing_wire_raw_diagnostics"]
    assert supplemental and all(row["path"] == "" for row in supplemental)
    assert "wrong_name" in json.dumps(supplemental)
    base = prompt(materials()) if compact else "Full source: 原文\nOPTIONAL LOSSLESS PROCESSING RESPONSE\n"
    strategy = fragment_correction_strategy("processing")
    corrected_prompt = strategy.build_prompt(base, raw, rows)
    assert output_wire_instructions() in corrected_prompt
    assert DEFINITION_NAME_PATTERN in corrected_prompt
    assert strategy.selected == {} and "MECHANICAL RECORD CORRECTION" not in corrected_prompt
    if "JOINT PROCESSING CORRECTION MATERIAL" in corrected_prompt:
        logical = _parts(corrected_prompt)[1]
        assert logical["correction"]["candidate"] == raw
        assert {k: v for k, v in logical.items() if k != "correction"} == _parts(base)[1]
        assert _parts(corrected_prompt)[2].startswith(_parts(base)[2])
    else:
        context = json.loads(corrected_prompt.split("\nCURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[1])
        assert context["candidate"] == raw and corrected_prompt.startswith(base)
    assert salvage_fragment("processing", raw, material) == (None, [])


def test_local_shared_replacement_gets_full_grammar_and_keeps_every_unselected_record():
    material, _, fragments = fixture()
    good = fragments["processing"]
    bad = deepcopy(good)
    bad["ir_semantics"]["ir_call"]["order"] = "bad-order"
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("processing", shared(bad), material)
    strategy = fragment_correction_strategy("processing")
    prompt = strategy.build_prompt("Short caller base with complete source.", shared(bad), caught.value.diagnostics)
    assert output_wire_instructions() in prompt and "MECHANICAL RECORD CORRECTION" in prompt
    replacement = {"replacements": [{"record_id": "/ir_semantics/ir_call", "value": good["ir_semantics"]["ir_call"]}]}
    merged = strategy.merge(shared(bad), shared(replacement))
    assert merged == good and validate_fragment("processing", merged, material) == good


@pytest.mark.parametrize("repeat_invalid", [False, True])
def test_single_correction_preserves_rejected_raw_answer_and_replays_strictly(tmp_path, repeat_invalid):
    material, _, fragments = fixture()
    good = fragments["processing"]
    raw = malformed_tables(good)
    answers = [raw, raw if repeat_invalid else json.dumps(shared(good))]
    sent = []

    class Client:
        def complete(self, prompt):
            sent.append(prompt)
            return answers.pop(0)

    args = dict(prefix="calls", base_prompt="Complete source. Preserve 原文 and all contracts.",
        request_kind="processing_fragment", config=CONFIG, writer=ArtifactWriter(()),
        validate=lambda value: validate_fragment("processing", value, material), max_corrections=1)
    chain = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("processing"),
                          client_factory=injected_factory(Client()))
    if repeat_invalid:
        with pytest.raises(StructuralCorrectionLimitReached):
            chain.run()
    else:
        assert chain.run() == good
    assert len(sent) == 2 and not answers and not (tmp_path / "calls/a003").exists()
    assert "processing_wire_raw_diagnostics" in sent[1] and DEFINITION_NAME_PATTERN in sent[1]
    assert read_json(tmp_path / "calls/a001/response.json") == raw
    validation = read_json(tmp_path / "calls/a001/validation.json")
    assert validation["status"] == "structural_invalid" and len(validation["diagnostics"]) >= 2
    saved = {str(path): path.read_bytes() for path in tmp_path.rglob("*.json")}
    replay = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("processing"), replay=True)
    if repeat_invalid:
        with pytest.raises(StructuralCorrectionLimitReached):
            replay.run()
    else:
        assert replay.run() == good
    assert replay.snapshot() == chain.snapshot() and len(sent) == 2
    assert saved == {str(path): path.read_bytes() for path in tmp_path.rglob("*.json")}


def test_seven_normal_requests_one_format_correction_real_backend_and_zero_call_replay(tmp_path, monkeypatch):
    from skillflow.document_guided import runner
    from skillflow.document_guided.fragments import split_fragments
    from skillflow.graph.extraction.compiler import compile_candidate
    from skillflow.propagation.annotation.loading import load_annotation_run
    from tests.document_guided.test_parallel_runner import Harness, freeze_producer, _cfg_wire
    from tests.document_guided.test_input_contract_completeness import call_sample
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    material, call_wire = call_sample()
    block = material["cfg"]["blocks"]["sample"]
    candidate = {"entry_block_ref": "sample", "blocks": [{
        "block_ref": "sample", "block_name": block["block_name"],
        "data_source_kind": block["data_source_kind"], "constraints": block["constraints"],
        "instructions": [{"instruction_ref": ir["id"], **{key: value for key, value in ir.items() if key != "id"}}
                         for ir in block["instructions"]]}], "edges": []}
    compiled = compile_candidate(candidate)
    assert compiled.ok
    call_wire["ir_semantics"] = {new.id: call_wire["ir_semantics"][old["id"]]
        for old, new in zip(block["instructions"], compiled.cfg.blocks["block_001"].instructions)}

    class CorrectingHarness(Harness):
        def __init__(self, directory):
            super().__init__(directory)
            self.example["source"] = material["source"]["files"][0]["content"]
            self.example["task_candidate"] = {key: deepcopy(material["task"][key]) for key in ("purpose", "requirements", "issues")}
            self.graph, self.wire = _cfg_wire(candidate), deepcopy(call_wire)
            self.fragments = split_fragments(call_wire)

        def complete(self, stage, prompt):
            if stage != "processing":
                return super().complete(stage, prompt)
            with self.lock:
                self.attempts[stage] = self.attempts.get(stage, 0) + 1
                self.calls.append(stage)
                self.prompts[stage] = prompt
            assert self.attempts[stage] <= 2
            if self.attempts[stage] == 1:
                return malformed_tables(self.fragments[stage])
            assert "processing_wire_raw_diagnostics" in prompt and output_wire_instructions() in prompt
            return shared(self.fragments[stage])

    harness = CorrectingHarness(tmp_path / "run")
    source = harness.prepare(tmp_path / "source")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete" and result["annotation_review"] == "review_passed", result
    assert result["counts"]["logical_calls"] == len(harness.calls) == 8
    assert result["counts"]["structural_corrections"] == 1 and not result["repair_used"]
    assert harness.calls.count("processing") == 2 and len(set(harness.calls)) == 7
    assert runner.POLICY["workers"] == 2 and runner.POLICY["normal_semantic_calls"] == 7
    assert runner.POLICY["structural_corrections"] == runner.POLICY["semantic_repairs"] == 1
    loaded = load_annotation_run(harness.directory / "annotation")
    assert loaded["compiled_annotation"]["input_contracts"]
    assert read_json(harness.directory / "audit/input-contract-review.json")["source_review_complete"]
    assert read_json(harness.directory / "doe/doe-result.json")["status"] == "complete"
    assert (harness.directory / "source/inputs/package/SKILL.md").read_bytes().decode("utf-8") == source
    saved = {str(path): path.read_bytes() for path in harness.directory.rglob("response.json")}
    assert runner.replay(harness.directory) == result and len(harness.calls) == 8
    assert saved == {str(path): path.read_bytes() for path in harness.directory.rglob("response.json")}
