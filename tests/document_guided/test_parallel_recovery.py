"""Offline dependency scheduling, partial review and durable interruption boundaries."""
from threading import Event

import pytest
from pydantic import ValidationError

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided import runner
from skillflow.document_guided.cfg_wire import normalize_cfg_wire
from skillflow.document_guided.online import validate_step
from skillflow.graph.extraction.compiler import compile_candidate


def cfg_wire():
    return {"entry_block_ref": "read", "blocks": [{"block_ref": "read", "data_source_kind": "context",
        "instructions": [{"opcode": "read_request", "inputs": [{"type": "context_key", "identifier": "request"}],
                          "outputs": [{"type": "result", "identifier": "request_value"}]},
                         {"opcode": "return", "inputs": [{"type": "result", "identifier": "request_value"}]}]}]}


@pytest.fixture(autouse=True)
def stable_producer_and_no_formal_subprocess(monkeypatch):
    from tests.document_guided.test_parallel_runner import freeze_producer
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args: None)


def test_cfg_wire_bookkeeping_omission_and_existing_semantics_are_preserved():
    wire = cfg_wire()
    normalized = normalize_cfg_wire(wire)
    assert wire == cfg_wire()
    assert normalized["declared_context_keys"] == ["request"]
    block = normalized["blocks"][0]
    assert block["block_name"] == "read"
    assert [row["instruction_ref"] for row in block["instructions"]] == ["instruction_0001", "instruction_0002"]
    result = compile_candidate(normalized)
    assert result.ok, result.diagnostics
    operand = result.cfg.blocks["block_001"].instructions[0].outputs[0]
    assert operand.identifier == "result_001" and operand.semantic_name == "request_value"


@pytest.mark.parametrize("change", ["name_null", "name_empty", "payload_null", "instruction_ref", "semantic_name", "context_inventory"])
def test_cfg_wire_rejects_explicit_bad_or_program_owned_fields(change):
    wire = cfg_wire()
    block = wire["blocks"][0]
    if change == "name_null":
        block["block_name"] = None
    elif change == "name_empty":
        block["block_name"] = ""
    elif change == "payload_null":
        block["instructions"][0]["inputs"][0]["literal_value"] = None
    elif change == "instruction_ref":
        block["instructions"][0]["instruction_ref"] = "model_owned"
    elif change == "semantic_name":
        block["instructions"][0]["outputs"][0]["semantic_name"] = "model_owned"
    else:
        wire["declared_context_keys"] = ["request"]
    with pytest.raises(ValidationError):
        normalize_cfg_wire(wire)


def test_cfg_wire_keeps_source_span_and_source_block_validators():
    text = "Return the requested value.\n"
    context = {"files": {"skill/SKILL.md": text}}
    wire = cfg_wire()
    wire["blocks"][0]["instructions"][0]["metadata"] = {
        "_source_span": {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}}
    value = validate_step("cfg_wire", wire, context=context)
    assert value["blocks"][0]["instructions"][0]["metadata"]["script_content"] == text
    wire["blocks"][0]["instructions"][0]["metadata"]["_source_span"]["end_line"] = 9
    with pytest.raises(StructuralValidationError, match="line"):
        validate_step("cfg_wire", wire, context=context)
    bad = cfg_wire()
    bad["blocks"][0]["instructions"].insert(1, {"opcode": "do_extra"})
    with pytest.raises(StructuralValidationError, match="source block"):
        validate_step("cfg_wire", bad, context=context)


def prepared_harness(tmp_path, *, processing_gap=False):
    from tests.document_guided.test_parallel_runner import Harness
    harness = Harness(tmp_path / "run")
    if processing_gap:
        identity = next(iter(harness.fragments["processing"]["ir_semantics"]))
        harness.fragments["processing"]["processing_gaps"] = [{"instruction_id": identity,
            "reason": "Some internal member processing remains unknown despite the retained known operations.",
            "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]}]
    harness.prepare(tmp_path / "package")
    return harness


def add_synthetic_sensitivity(harness, label):
    """An explicit typed canary over an existing value, never semantic gold."""
    identity = next(iter(harness.fragments["processing"]["ir_semantics"]))
    harness.fragments["sensitivity"]["declarations"].append({"instruction_id": identity,
        "value": {"kind": "local", "name": "label"}, "label": label,
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]})


def test_explicit_processing_gap_replays_with_different_parallel_completion_order(tmp_path, monkeypatch):
    harness = prepared_harness(tmp_path, processing_gap=True)
    directory = harness.directory
    add_synthetic_sensitivity(harness, "SENSITIVITY_CANARY")
    flow_complete, replay_task_complete = Event(), Event()
    first_order, replay_order = [], []

    class Client:
        def __init__(self, stage):
            self.stage = stage
        def complete(self, prompt):
            if self.stage == "task":
                assert flow_complete.wait(10)
            return harness.complete(self.stage, prompt)

    def progress(state):
        name = state["stage"]
        if state["stages"][name]["status"] == "complete":
            first_order.append(name)
            if name == "flow":
                flow_complete.set()

    result = runner.run(directory, client_factory=lambda stage, owner: Client(stage), progress=progress)
    assert result["status"] == "partial", result
    assert result["diagnostic_only"] and not result["repair_used"] and len(harness.calls) == 7
    assert "annotation" not in harness.calls and not any(stage.startswith("revision") for stage in harness.calls)
    assert "SENSITIVITY_CANARY" not in harness.prompts["task-correspondence"]
    assert "SENSITIVITY_CANARY" in harness.prompts["review"]
    before = {str(path.relative_to(directory)): path.read_bytes() for path in directory.rglob("response.json")}
    original_step = runner.run_step
    def reversed_flow(owner, **kwargs):
        if kwargs.get("replay") and owner.name == "flow":
            assert replay_task_complete.wait(10)
        return original_step(owner, **kwargs)
    monkeypatch.setattr(runner, "run_step", reversed_flow)
    def replay_progress(state):
        name = state["stage"]
        if state["stages"][name]["status"] == "complete":
            replay_order.append(name)
            if name == "task":
                replay_task_complete.set()
    assert runner.run(directory, replay=True, progress=replay_progress) == result
    assert first_order.index("flow") < first_order.index("task")
    assert replay_order.index("task") < replay_order.index("flow")
    assert len(harness.calls) == 7
    assert {str(path.relative_to(directory)): path.read_bytes() for path in directory.rglob("response.json")} == before


def test_interrupt_with_an_independent_answer_pending_replays_without_dispatch(tmp_path, monkeypatch):
    harness = prepared_harness(tmp_path)
    directory = harness.directory
    stopping = Event()
    monkeypatch.setattr(runner, "Event", lambda: stopping)
    sensitivity_started = Event()
    class Client:
        def __init__(self, stage):
            self.stage = stage
        def complete(self, prompt):
            answer = harness.complete(self.stage, prompt)
            if self.stage == "task-correspondence":
                assert sensitivity_started.wait(10)
            if self.stage == "sensitivity":
                sensitivity_started.set()
                assert stopping.wait(10)
            return answer
    def interrupt(state):
        if state["stage"] == "task-correspondence" and state["stages"]["task-correspondence"]["status"] == "complete":
            raise KeyboardInterrupt("Stop with a second worker still producing its answer")
    result = runner.run(directory, client_factory=lambda stage, owner: Client(stage), progress=interrupt)
    assert result["status"] == "interrupted", result
    monkeypatch.setattr(runner, "Event", Event)
    before = len(harness.calls)
    assert runner.replay(directory) == result
    assert len(harness.calls) == before
    resumed = runner.run(directory, client_factory=lambda stage, owner: Client(stage))
    assert resumed["status"] == "complete", resumed
    assert harness.calls[before:] == ["review"]
    assert len(harness.calls) == 7


def test_passive_count_monitor_failure_does_not_change_analysis_or_replay(tmp_path, monkeypatch):
    harness = prepared_harness(tmp_path)
    directory = harness.directory
    original_counts = runner._counts
    monkeypatch.setattr(runner, "_counts", lambda run: {"status": "unavailable"})
    result = runner.run(directory, client_factory=harness.factory,
                        progress=lambda state: (_ for _ in ()).throw(ValueError("passive monitor unavailable")))
    assert result["status"] == "complete", result
    monkeypatch.setattr(runner, "_counts", original_counts)
    assert runner.replay(directory) == result
