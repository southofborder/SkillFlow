"""Regression boundaries for actual graph identity, interruption, and artifacts.

All model responses here are synthetic protocol fixtures. They establish no
semantic correctness claim, and no test constructs a network client.
"""

import hashlib
import json
from threading import Event

import pytest

from skill_ir.backtrace.controlled import render_controlled
from skill_ir.backtrace.evidence import json_pointer, normalize_cfg
from skill_ir.backtrace.fixtures import prepare_cases, REPOSITORY_ROOT
from skill_ir.backtrace.services import audit_source_controlled
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.extraction.pipeline import analyze_skill
from skill_ir.feedback import runner
from skill_ir.feedback.prompts import build_feedback_prompt, FEEDBACK_INSTRUCTIONS
from skill_ir.inputs.snapshot import freeze_input, read_snapshot
from skill_ir.ir.cfg import ControlFlowGraph

# conftest places this directory on sys.path. Reuse only the small synthetic
# protocol helpers; no recorded experiment or expected semantic answer is read.
from test_feedback_runner import answer, candidate, Client, material  # noqa: F401


def test_feedback_renamed_compiled_ids_keep_literal_target_mapping(material):
    source, _, directory = material
    literal = {"quoted": '中文"\\\n', "items": [None, True, 2, 2.5]}
    compiled = analyze_skill(source, candidate=candidate(literal)).cfg
    graph = normalize_cfg(compiled)
    old_id = graph["entry_block_id"]
    renamed = "renamed/中文~block"
    block = graph["blocks"].pop(old_id)
    block["block_id"] = renamed
    block["instructions"][0]["id"] = "ir_renamed_907"
    graph["blocks"][renamed] = block
    graph["entry_block_id"] = renamed
    cfg = ControlFlowGraph.model_validate(graph)
    cfg.validate_integrity()
    freeze_input(source, directory, ArtifactWriter(()))
    package, bundle, _ = read_snapshot(directory)
    document = render_controlled(cfg)
    pointer = json_pointer("blocks", renamed, "instructions", 0, "inputs", 0)
    target = next(unit["id"] for unit in document["units"] if unit["graph_refs"] == [pointer])

    def located_answer(prompt):
        response = answer(prompt, "mistranslated")
        response["findings"][0]["suggestions"][0]["target_ids"] = [target]
        return response

    audit = audit_source_controlled(bundle, document, Client([located_answer]))
    prompt = build_feedback_prompt(package, graph, audit)
    payload = json.loads(prompt.split(FEEDBACK_INSTRUCTIONS + "\n\n", 1)[1])
    location = payload["explicit_differences"][0]["suggestions"][0]["suggestion_targets"]
    assert location == [{"graph_pointer": pointer, "value":
                         normalize_cfg(cfg)["blocks"][renamed]["instructions"][0]["inputs"][0]}]
    assert location[0]["value"]["literal_value"] == literal
    assert payload["previous_cfg"] == normalize_cfg(cfg)
    assert payload["previous_cfg"]["blocks"][renamed]["instructions"][0]["id"] == "ir_renamed_907"
    assert old_id not in payload["previous_cfg"]["blocks"]


def test_f01_deleted_operation_uses_actual_variant_and_retains_only_real_operations(tmp_path):
    prepared = prepare_cases()
    original = prepared["cases"][0]["cfg"]
    variant = prepared["cases"][2]["cfg"]
    changed_key = next(key for key in original["blocks"]
                       if original["blocks"][key]["instructions"] != variant["blocks"][key]["instructions"])
    before = original["blocks"][changed_key]
    after = variant["blocks"][changed_key]
    assert after["block_name"] == before["block_name"]
    assert variant["constraints"] == original["constraints"]
    assert len(after["instructions"]) == len(before["instructions"]) - 1
    assert [item["opcode"] for item in after["instructions"]] == ["return"]
    absent_ids = {item["id"] for item in before["instructions"]} - {item["id"] for item in after["instructions"]}
    source = REPOSITORY_ROOT / prepared["provenance"]["source_root"]
    seed = tmp_path / "seed.json"
    # Deliberately stale material is present in the analysis envelope. It must
    # never influence the graph, its certified text, or targeted extraction.
    seed.write_text(json.dumps({"cfg": variant, "raw_candidate": {
        "marker": "STALE-CANDIDATE-FORBIDDEN", "graph": original,
    }}, ensure_ascii=False), encoding="utf-8")
    extraction = Client([RuntimeError("stop synthetic extraction after capturing feedback")])
    result = runner.refine_skill(source, run_dir=tmp_path / "run", initial_analysis=seed,
                                 extraction_client=extraction,
                                 audit_client=Client([lambda prompt: answer(prompt, "omitted")]))
    assert result["status"] == "extraction_error", result["reason"]
    assert len(extraction.prompts) == 1
    feedback = extraction.prompts[0]
    assert "STALE-CANDIDATE-FORBIDDEN" not in feedback
    payload = json.loads(feedback.split(FEEDBACK_INSTRUCTIONS + "\n\n", 1)[1])
    actual = payload["previous_cfg"]["blocks"][changed_key]
    assert actual == normalize_cfg(ControlFlowGraph.model_validate(variant))["blocks"][changed_key]
    assert actual["block_name"] == before["block_name"]
    assert [item["opcode"] for item in actual["instructions"]] == ["return"]
    document = json.loads((tmp_path / "run/rounds/r000/controlled.json").read_text(encoding="utf-8"))
    for absent in absent_ids:
        assert absent not in document["text"]
    saved = json.loads((tmp_path / "run/rounds/r000/cfg.json").read_text(encoding="utf-8"))
    assert saved["blocks"][changed_key]["instructions"] == actual["instructions"]


def test_nested_run_rejected_before_any_lock_or_input_mutation(material):
    source, seed, _ = material
    def inventory():
        return {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in source.rglob("*") if path.is_file()}
    before = inventory()
    nested = source / "not-created" / "run"
    with pytest.raises(ValueError, match="nested"):
        runner.refine_skill(source, run_dir=nested, initial_analysis=seed,
                            audit_client=Client([answer]))
    assert inventory() == before
    assert not (source / "not-created").exists()
    assert not list(source.rglob(".runner.lock"))


def test_before_start_interruption_replays_exact_decision_without_api(material, monkeypatch):
    source, seed, directory = material
    stopped = Event()
    stopped.set()
    initial = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, stop_event=stopped)
    assert initial["status"] == "interrupted"
    assert initial["rounds"] == [] and initial["counts"]["total_logical_calls"] == 0
    def no_api(*args, **kwargs):
        pytest.fail("offline replay must not create or invoke a model client")
    monkeypatch.setattr(runner, "RecordingClient", no_api)
    monkeypatch.setattr(runner, "injected_factory", no_api)
    assert runner.replay_run(directory) == initial


def test_between_round_interruption_replays_exact_stop_boundary(material, monkeypatch):
    source, seed, directory = material
    stopped = Event()
    def finish_audit_then_stop(prompt):
        stopped.set()
        return answer(prompt, "omitted")
    audit = Client([finish_audit_then_stop])
    extraction = Client([])
    initial = runner.refine_skill(source, run_dir=directory, initial_analysis=seed,
                                 audit_client=audit, extraction_client=extraction, stop_event=stopped)
    assert initial["status"] == "interrupted"
    assert len(initial["rounds"]) == 1 and initial["rounds"][0]["status"] == "revise"
    assert initial["counts"]["audit_logical_calls"] == 1
    assert not extraction.prompts
    def no_api(*args, **kwargs):
        pytest.fail("saved interruption must stop replay before any new call")
    monkeypatch.setattr(runner, "RecordingClient", no_api)
    monkeypatch.setattr(runner, "injected_factory", no_api)
    assert runner.replay_run(directory) == initial
    assert len(audit.prompts) == 1


def test_corrupted_audit_record_cannot_leave_a_stale_passed_graph(material):
    source, seed, directory = material
    audit = Client([answer])
    passed = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_client=audit)
    assert passed["status"] == "audit_passed"
    assert (directory / "passed-cfg.json").exists()
    assert runner.replay_run(directory) == passed
    assert (directory / "replay/passed-cfg.json").exists()
    transport = directory / "calls/r000/audit/a001/transport.json"
    records = json.loads(transport.read_text(encoding="utf-8"))
    records[0]["response"]["notes"] = ["corrupted after acceptance"]
    transport.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    failed = runner.refine_skill(source, run_dir=directory, initial_analysis=seed, audit_client=audit)
    assert failed["status"] == "audit_error", failed["reason"]
    assert failed["passed_cfg"] is None
    assert failed["counts"]["record_integrity_errors"]
    assert len(audit.prompts) == 1, "corrupt accepted calls must never be resent"
    assert not (directory / "passed-cfg.json").exists()
    replay = runner.replay_run(directory)
    assert replay == failed
    assert not (directory / "replay/passed-cfg.json").exists()
