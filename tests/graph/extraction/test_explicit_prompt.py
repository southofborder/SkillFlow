"""Explicit feedback prompts share the production structural repair machinery."""
import json

import pytest

from skillflow.graph.extraction import pipeline
from skillflow.graph.extraction.prompt import build_whole_skill_prompt
from skillflow.common.inputs.skill_package import load_skill_package


def candidate():
    return {
        "entry_block_ref": "finish",
        "blocks": [{"block_ref": "finish", "block_name": "结束", "instructions": [
            {"instruction_ref": "return_value", "opcode": "return", "inputs": [
                {"type": "literal", "literal_value": "ok"}
            ]}
        ]}],
        "edges": [],
    }


class Client:
    def __init__(self, responses):
        self.responses, self.prompts = iter(responses), []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return next(self.responses)


@pytest.fixture
def package(tmp_path):
    (tmp_path / "SKILL.md").write_text("# 样例\n返回 ok。\n", encoding="utf-8")
    return load_skill_package(tmp_path)


def test_explicit_prompt_is_reused_for_full_candidate_structural_repairs(package, monkeypatch):
    def forbidden(*args):
        pytest.fail("Explicit prompt extraction must not rebuild the base prompt")
    monkeypatch.setattr(pipeline, "build_whole_skill_prompt", forbidden)
    initial = "完整 Skill 和输出契约\n已核实的本样例反馈"
    client = Client(["invalid JSON", json.dumps(candidate())])
    result = pipeline.analyze_skill_with_prompt(
        package, initial_prompt=initial, client=client, max_repair_rounds=1,
    )
    assert result.status == "complete"
    assert result.attempts == 2
    assert result.prompt == initial
    assert client.prompts[0] == initial
    assert client.prompts[1].startswith(initial + "\n\n")
    assert "CANDIDATE_JSON_INVALID" in client.prompts[1]
    assert result.cfg.blocks["block_001"].instructions[0].opcode == "return"


def test_default_analyze_keeps_exact_base_prompt_and_result(package):
    ordinary = Client([json.dumps(candidate())])
    explicit = Client([json.dumps(candidate())])
    default_result = pipeline.analyze_skill(package, client=ordinary)
    expected = build_whole_skill_prompt(package)
    explicit_result = pipeline.analyze_skill_with_prompt(
        package, initial_prompt=expected, client=explicit,
    )
    assert ordinary.prompts == explicit.prompts == [expected]
    assert default_result.model_dump() == explicit_result.model_dump()


def test_explicit_prompt_exhaustion_counts_structural_calls(package):
    client = Client(["invalid"] * 4)
    result = pipeline.analyze_skill_with_prompt(package, initial_prompt="test", client=client)
    assert result.status == "degraded"
    assert result.cfg is None
    assert result.attempts == len(client.prompts) == 4


@pytest.mark.parametrize("prompt", ["", " \n", None, {}])
def test_invalid_explicit_prompt_fails_before_a_call(package, prompt):
    client = Client([])
    with pytest.raises(ValueError, match="initial_prompt"):
        pipeline.analyze_skill_with_prompt(package, initial_prompt=prompt, client=client)
    assert not client.prompts


def test_negative_structural_budget_fails_before_a_call(package):
    client = Client([])
    with pytest.raises(ValueError, match="max_repair_rounds"):
        pipeline.analyze_skill_with_prompt(
            package, initial_prompt="test", client=client, max_repair_rounds=-1,
        )
    assert not client.prompts


def test_attempt_observer_saves_failed_candidate_before_next_interrupted_call(package):
    records = []

    class InterruptedClient:
        calls = 0

        def complete(self, prompt):
            self.calls += 1
            if self.calls == 1:
                return "invalid JSON"
            assert len(records) == 1
            assert records[0]["status"] == "repair_needed"
            raise KeyboardInterrupt("second structural call interrupted")

    with pytest.raises(KeyboardInterrupt):
        pipeline.analyze_skill_with_prompt(
            package, initial_prompt="complete source and contract", client=InterruptedClient(),
            on_attempt=records.append,
        )
    assert records == [{"attempt": 1, "raw_candidate": {}, "raw_response": "invalid JSON",
                        "diagnostics": ["CANDIDATE_JSON_INVALID: LLM response did not contain a JSON object"],
                        "status": "repair_needed", "cfg": None}]


def test_attempt_observer_receives_finished_compile_and_cannot_mutate_the_result(package):
    observed = []

    def observe(record):
        observed.append(record["status"])
        record["raw_candidate"].clear()
        record["diagnostics"].append("observer-local mutation")
        if record["cfg"]:
            record["cfg"].clear()

    result = pipeline.analyze_skill_with_prompt(
        package, initial_prompt="checked", client=Client([json.dumps(candidate())]), on_attempt=observe,
    )
    assert observed == ["complete"]
    assert result.raw_candidate == candidate()
    assert result.cfg is not None and result.cfg.blocks
    assert "observer-local mutation" not in result.diagnostics


def test_failed_attempt_persistence_stops_before_another_model_request(package):
    client = Client(["invalid", json.dumps(candidate())])

    def failed_persistence(record):
        raise OSError("cannot persist attempt")

    with pytest.raises(OSError, match="persist"):
        pipeline.analyze_skill_with_prompt(
            package, initial_prompt="checked", client=client, on_attempt=failed_persistence,
        )
    assert len(client.prompts) == 1
