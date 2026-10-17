from copy import deepcopy
import json
from pathlib import Path
import re
from threading import Event

import pytest

from skillflow.common.recording import canonical_sha256, sha_file
from tools.doe.prompt_comparison_fixtures import evaluation_fixtures as prompt_examples
from tools.doe.compare_prompts import prepare_comparison, run_comparison, replay_comparison, load_comparison
from tools.doe.compare_prompts import _old_prefix_projection, _OLD_REASON_TRANSLATIONS, _OLD_LANGUAGE, _NEW_LANGUAGE


CONFIG = {"endpoint": "https://example.invalid/v1/chat/completions", "model": "comparison-test",
          "reasoning_effort": "max", "timeout_ms": 1000, "max_retries": 0,
          "retry_base_ms": 1, "retry_max_backoff_ms": 1, "response_format": "json_object"}


@pytest.fixture
def prepared(tmp_path):
    baseline = tmp_path / "baseline"
    source = baseline / "src/skillflow/common/structural_correction.py"
    source.parent.mkdir(parents=True)
    source.write_text('VERSION = "old-experiment-v3"\nCORRECTION_MARKER = "\\nOLD_CORRECTION\\n"\ndef correction_prompt(base_prompt, response, diagnostics):\n    context = {"protocol": VERSION, "candidate": response, "diagnostics": diagnostics}\n    return base_prompt + CORRECTION_MARKER + "Return complete JSON." + "\\nCANDIDATE\\n" + json.dumps(context, ensure_ascii=False, separators=(",", ":"), allow_nan=False)\n', encoding="utf-8")
    prompt = baseline / "annotation-prefix.txt"
    prompt.write_bytes(b"Frozen old annotation instructions.\nINPUT_JSON\n")
    (baseline / "baseline.json").write_text(json.dumps({"files": {"src/skillflow/common/structural_correction.py": sha_file(source)}, "annotation_prefix_sha256": sha_file(prompt)}), encoding="utf-8")
    directory = tmp_path / "comparison"
    prepare_comparison(directory, baseline_dir=baseline, config=CONFIG)
    return directory


class Client:
    def __init__(self, responses, event=None):
        self.responses = list(responses)
        self.prompts = []
        self.event = event

    def complete(self, prompt):
        self.prompts.append(prompt)
        value = self.responses.pop(0)
        if self.event:
            self.event.set()
        if isinstance(value, BaseException):
            raise value
        return deepcopy(value)


def clients(*, first_responses=None):
    result = {}
    for fixture in prompt_examples():
        for arm in ("old", "new"):
            result[(fixture["name"], arm)] = Client([fixture["annotation"]])
    if first_responses:
        result[(prompt_examples()[0]["name"], "old")] = Client(first_responses)
    return result


def test_six_chains_share_inputs_config_and_replay_without_api(prepared):
    live = clients()
    summary = run_comparison(prepared, clients=live)
    assert summary["status"] == "complete"
    assert len(summary["results"]) == 6
    assert all(row["status"] == "complete" and row["counts"]["logical_calls"] == 1 for row in summary["results"])
    assert all(row["semantic_acceptance"] == "not_assessed" for row in summary["results"])
    assert all(row["calls"][0]["total_tokens"] is None for row in summary["results"])
    before = {str(p): sha_file(p) for p in prepared.rglob("*") if p.is_file() and p.name not in {".runner.lock", "replay.json"}}
    assert replay_comparison(prepared)["status"] == "matched"
    assert before == {name: sha_file(Path(name)) for name in before}
    assert all(len(client.prompts) == 1 for client in live.values())
    assert not re.search(r"[\u4e00-\u9fff]", (prepared / "report.md").read_text(encoding="utf-8"))


def test_invalid_candidates_keep_full_old_chain_and_continue_until_legal(prepared):
    fixture = prompt_examples()[0]
    live = clients(first_responses=["not json"] * 5 + [fixture["annotation"]])
    result = run_comparison(prepared, clients=live)
    first = result["results"][0]
    assert first["counts"]["structural_corrections"] == 5
    assert first["accepted_call"] == "calls/annotation/a006"
    prompts = live[(fixture["name"], "old")].prompts
    assert all("OLD_CORRECTION" in prompt for prompt in prompts[1:])
    assert replay_comparison(prepared)["status"] == "matched"


def test_new_arm_uses_current_correction_and_keeps_same_validator(prepared):
    fixture = prompt_examples()[0]
    live = clients()
    live[(fixture["name"], "new")] = Client(["not json", fixture["annotation"]])
    result = run_comparison(prepared, clients=live)
    row = next(row for row in result["results"] if row["case"] == fixture["name"] and row["arm"] == "new")
    assert row["counts"]["structural_corrections"] == 1
    sent = live[(fixture["name"], "new")].prompts
    assert "OLD_CORRECTION" not in sent[1]
    assert "STRUCTURAL_CORRECTION" in sent[1]
    assert replay_comparison(prepared)["status"] == "matched"


def test_evaluation_references_and_sources_do_not_enter_teaching_examples(prepared):
    from skillflow.propagation.annotation.prompt_examples import compact_prompt_examples
    teaching = json.dumps(compact_prompt_examples(), ensure_ascii=False)
    for fixture in prompt_examples():
        assert fixture["source"] not in teaching
        assert fixture["name"] not in teaching
        prompt = (prepared / "cases" / fixture["name"] / "new/base-prompt.txt").read_text(encoding="utf-8")
        assert "assistant_authored_fixture" not in prompt
        assert json.dumps(fixture["contrast"], ensure_ascii=False, separators=(",", ":")) not in prompt
    for marker in ("asset_tag", "batch_label", "diagnostic worksheet"):
        assert marker not in teaching


def test_evaluation_candidates_are_executable_and_sizes_are_measured(prepared):
    from skillflow.propagation.annotation.binding_examples import example_material
    from skillflow.propagation.annotation.compiler import compile_response
    for fixture in prompt_examples():
        material = example_material(fixture)
        for key in ("annotation", "contrast"):
            assert compile_response(fixture[key], material)[1]["demands"]
        new = json.loads((prepared / "cases" / fixture["name"] / "new/prompt-sizes.json").read_text(encoding="utf-8"))
        old = json.loads((prepared / "cases" / fixture["name"] / "old/prompt-sizes.json").read_text(encoding="utf-8"))
        assert new["input"] == old["input"]
        assert new["format"]["characters"] > 0 and new["examples"]["characters"] > 0


def test_english_projection_is_narrow_audited_and_preserves_common_input():
    examples = [{"reason": reason, "value": {"kind": "input", "index": index}}
                for index, reason in enumerate(_OLD_REASON_TRANSLATIONS)]
    text = (_OLD_LANGUAGE + "\r\nENDPOINT DEMAND EXAMPLES (SYNTHETIC, NOT INPUT DATA)\r\n"
            + json.dumps(examples, ensure_ascii=False, separators=(",", ":")) + "\r\nINPUT_JSON\r\n")
    projected, receipt = _old_prefix_projection(text)
    assert projected.startswith(_NEW_LANGUAGE + "\n")
    assert "\r" not in projected
    assert not re.search(r"[\u4e00-\u9fff]", projected)
    assert receipt["crlf_replacements"] == 4
    assert len(receipt["changes"]) == 4
    assert receipt["raw_sha256"] != receipt["normalized_sha256"] != receipt["projected_sha256"]
    actual = json.loads(projected.splitlines()[2])
    assert actual == [{**row, "reason": _OLD_REASON_TRANSLATIONS[row["reason"]]} for row in examples]
    assert [change["path"] for change in receipt["changes"] if change["kind"] == "teaching_reason"] == [[0, "reason"], [1, "reason"], [2, "reason"]]
    source_input = '{"source":"原始证据不能被翻译或改写。"}'
    assert (projected + source_input).endswith(source_input)
    assert _old_prefix_projection(text) == (projected, receipt)


@pytest.mark.parametrize("payload", [
    [{"reason": "未知的教学解释。"}],
    [{"source": next(iter(_OLD_REASON_TRANSLATIONS))}],
])
def test_english_projection_rejects_unknown_or_non_reason_han(payload):
    text = "BINDING_EXAMPLES\n" + json.dumps(payload, ensure_ascii=False) + "\nINPUT_JSON\n"
    with pytest.raises(ValueError, match="historical|Historical"):
        _old_prefix_projection(text)


def test_english_projection_does_not_silently_accept_other_language_policy():
    with pytest.raises(ValueError, match="output-language"):
        _old_prefix_projection("Write all answers in Chinese.\nINPUT_JSON\n")


def test_held_out_authored_material_is_english():
    for fixture in prompt_examples():
        assert not re.search(r"[\u4e00-\u9fff]", json.dumps(fixture, ensure_ascii=False))


def test_semantic_failure_is_not_structural_success_and_does_not_retry(prepared):
    failure = {"outcome": "cannot_assess", "failure": {
        "reason": "The source is insufficient for the required judgment.", "instruction_ids": ["ir_inventory_overview"],
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "reason": "The source span is valid; the failure interpretation still requires semantic review."}]}}
    result = run_comparison(prepared, clients=clients(first_responses=[failure]))
    assert result["results"][0]["status"] == "semantic_failure"
    assert result["results"][0]["counts"]["structural_corrections"] == 0
    assert replay_comparison(prepared)["status"] == "matched"


def test_accepted_response_interruption_resumes_without_resending(prepared):
    stop = Event()
    fixture = prompt_examples()[0]
    live = clients()
    live[(fixture["name"], "old")].event = stop
    result = run_comparison(prepared, clients=live, stop_event=stop)
    assert result["status"] == "interrupted" and len(result["results"]) == 1
    stop.clear()
    live[(fixture["name"], "old")].event = None
    resumed = run_comparison(prepared, clients=live, stop_event=stop)
    assert resumed["status"] == "complete"
    assert len(live[(fixture["name"], "old")].prompts) == 1
    assert replay_comparison(prepared)["status"] == "matched"


def test_transport_failure_does_not_trigger_correction_or_hide_other_cases(prepared):
    result = run_comparison(prepared, clients=clients(first_responses=[RuntimeError("connection closed")]))
    assert result["results"][0]["status"] == "execution_error"
    assert result["results"][0]["counts"]["logical_calls"] == 1
    assert all(row["status"] == "complete" for row in result["results"][1:])
    assert replay_comparison(prepared)["status"] == "matched"


def test_transport_interruption_and_pre_call_interruption_replay_without_api(prepared):
    result = run_comparison(prepared, clients=clients(first_responses=[KeyboardInterrupt()]))
    assert result["status"] == "interrupted" and len(result["results"]) == 1
    assert result["results"][0]["status"] == "interrupted"
    assert replay_comparison(prepared)["status"] == "matched"


def test_interruption_before_any_call_can_be_replayed(prepared):
    event = Event()
    event.set()
    result = run_comparison(prepared, clients=clients(), stop_event=event)
    assert result["status"] == "interrupted" and not result["results"]
    assert replay_comparison(prepared)["status"] == "matched"


@pytest.mark.parametrize("relative", ["audit/old-prefix.txt", "cases/capacity_overview/material.json", "cases/capacity_overview/new/base-prompt.txt"])
def test_frozen_input_tampering_is_rejected(prepared, relative):
    path = prepared / relative
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="Frozen comparison input changed"):
        load_comparison(prepared)


def test_actual_request_tamper_is_rejected_on_replay(prepared):
    run_comparison(prepared, clients=clients())
    path = prepared / "cases/capacity_overview/old/calls/annotation/a001/prompt.txt"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="prompt differs"):
        replay_comparison(prepared)
