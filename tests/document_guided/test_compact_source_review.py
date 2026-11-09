"""Generic compact display, exact local targets and bounded delivery failures."""
from copy import deepcopy
import json

import pytest

from skillflow.common.llm.request_errors import InputTooLarge, ModelRequestFailure
from skillflow.common.recording import ResponseIntegrityError, canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.source import render_source, source_packet
from skillflow.document_guided.source_review import (
    build_source_review_prompt, prepare_review_material, replay_saved_review,
    run_source_review, validate_source_review,
)
from skillflow.propagation.contracts.task import validate_task_candidate
from tests.document_guided.test_case_source_review import reviewed_cases
from tests.document_guided.test_source_review import Client, finding, fixture


@pytest.fixture(autouse=True)
def stable_producer(monkeypatch):
    files = {"tests/document_guided/test_compact_source_review.py": "offline-fixture"}
    monkeypatch.setattr("skillflow.document_guided.source_review.implementation_provenance",
                        lambda: {"files": files, "sha256": canonical_sha256(files)})


def payload(prompt):
    return json.loads(prompt.split("\nINPUT_JSON\n", 1)[1].split("\nCOMPLETE SOURCE\n", 1)[0])


@pytest.mark.parametrize("count", [1, 25, 500])
def test_compact_display_is_generic_and_preserves_all_semantic_material(count):
    files, task, cfg = fixture()
    files["skill/跨语言.txt"] = "原样保存结果。\r\n保留重复成员。\r\n"
    task = validate_task_candidate({key: task[key] for key in ("purpose", "requirements", "issues")},
                                   source_files=files).model_dump(mode="json")
    annotation = {"ir_semantics": {
        f"source/{index}~record": {"segments": [{"ops": [{"op": "receive", "output": "response"}]}],
                                  "note": "Original response and receiving boundary."}
        for index in range(count)}, "processing_gaps": [{"reason": "Local unresolved source relation."}],
        "_fragment_origins": {"/ir_semantics": {"fragment": "processing", "path": "/ir_semantics"}}}
    material = prepare_review_material(files=files, task=task, cfg=cfg, annotation=annotation,
        generation="fragment-v1", runtime_contract={"rules": ["Preserve actual versions."]},
        processing_gaps=[{"reason": "Program-enriched local relation.", "origin": "source"}])
    before = deepcopy(material)
    prompt = build_source_review_prompt(material)
    shown = payload(prompt)
    assert material == before and material["target_index"]
    assert "target_index" not in shown
    expected = deepcopy(annotation)
    expected.pop("_fragment_origins")
    assert shown["annotation"] == expected
    for key in ("task", "observations", "runtime_contract", "stage_failures", "availability",
                "processing_gaps", "partial", "fragments"):
        assert shown[key] == material[key]
    assert prompt.endswith(render_source(source_packet(files)))
    assert "原样保存结果。" in prompt and "保留重复成员。" in prompt
    assert "SUBMISSION SELF-CHECK" in prompt and "without a self-check report" in prompt
    assert "Use only target_index IDs" not in prompt
    legacy = deepcopy(material)
    legacy.pop("prompt_view")
    old_prompt = build_source_review_prompt(legacy)
    old_shown = payload(old_prompt)
    assert old_shown["target_index"] == material["target_index"]
    assert old_shown["annotation"] == annotation
    assert "Use only target_index IDs" in old_prompt
    assert "SUBMISSION SELF-CHECK" not in old_prompt
    if count > 1:
        assert len(prompt) < len(old_prompt)
    # Escaped source-generated keys still locate their actual object locally.
    target = "annotation:/ir_semantics/source~10~0record/segments/0/ops/0"
    item = {"domain": "annotation", "target_ids": [target], "explanation": "Check the response identity.",
            "source_refs": [], "suggestion": "Preserve the actual response identity."}
    checked = validate_source_review({"outcome": "completed", "findings": [item]}, material)
    assert checked["findings"][0]["owner"] == "processing"


@pytest.mark.parametrize("partial", [False, True])
def test_compact_case_and_partial_targets_remain_locally_valid(partial):
    material = reviewed_cases(partial=partial)
    shown = payload(build_source_review_prompt(material))
    assert "target_index" not in shown
    if partial:
        assert shown["annotation"] is None and shown["fragments"] == material["fragments"]
    target = ("fragment:processing:" if partial else "annotation:") + (
        "/ir_semantics/ir_call/segments/0/body/0/cases/0/segments/0/ops/0")
    item = {"domain": "annotation", "target_ids": [target], "explanation": "Check this actual case.",
            "source_refs": [], "suggestion": "Retain the source-supported boundary."}
    assert validate_source_review({"outcome": "completed", "findings": [item]}, material)["findings"][0]["owner"] == "processing"


def test_unknown_target_diagnostic_has_only_exact_parent_not_full_table_or_guessed_name():
    files, task, cfg = fixture()
    annotation = {"rows": [{"value": index} for index in range(1000)]}
    material = prepare_review_material(files=files, task=task, cfg=cfg, annotation=annotation)
    for invalid, parent in (("annotation:/rows/4/missing/deeper", "annotation:/rows/4"),
                            ("annotation:/rowz/4", "annotation:"), ("invented:/rows/4", None)):
        item = finding("annotation")
        item["target_ids"] = [invalid]
        with pytest.raises(StructuralValidationError) as caught:
            validate_source_review({"outcome": "completed", "findings": [item]}, material)
        context = caught.value.diagnostics[0]["context"]
        assert context == {"current": invalid, "nearest_parent": parent}
        assert len(json.dumps(caught.value.diagnostics)) < 500


def test_record_correction_does_not_reinsert_expanded_target_table(tmp_path):
    files, task, cfg = fixture()
    annotation = {"rows": [{"value": index} for index in range(1000)]}
    bad = finding("annotation")
    bad["target_ids"] = ["annotation:/rows/999/invented"]
    good = deepcopy(bad)
    good["target_ids"] = ["annotation:/rows/999"]
    client = Client({"outcome": "completed", "findings": [bad]},
                    {"replacements": [{"record_id": "/findings/0", "value": good}]})
    result = run_source_review(tmp_path, files=files, task=task, cfg=cfg, annotation=annotation,
                               generation="fragment-v1", client=client)
    assert result["status"] == "complete" and result["counts"]["structural_corrections"] == 1
    assert len(client.prompts) == 2
    assert "MECHANICAL RECORD CORRECTION" in client.prompts[1]
    assert '"nearest_parent":"annotation:/rows/999"' in client.prompts[1]
    assert all('"target_index":' not in prompt for prompt in client.prompts)
    assert len(client.prompts[1]) - len(client.prompts[0]) < 2500
    assert replay_saved_review(tmp_path) == result


class FailingClient:
    def __init__(self, error):
        self.error, self.calls = error, 0

    def complete(self, prompt):
        self.calls += 1
        raise self.error


@pytest.mark.parametrize("error_type", [InputTooLarge, ModelRequestFailure])
def test_confirmed_request_failure_is_unreviewed_and_replays_without_calls(tmp_path, error_type):
    files, task, cfg = fixture()
    client = FailingClient(error_type("The complete review request could not be delivered."))
    result = run_source_review(tmp_path, files=files, task=task, cfg=cfg, client=client)
    assert result["status"] == "request_failure" and result["review"] is None
    assert result["diagnostic_only"] and result["error_type"] == error_type.__name__
    assert result["reason"] == str(client.error) and result["objections"] == []
    assert result["failure_call"] == {"point": "call", "call": "calls/review/a001"}
    assert client.calls == 1 and result["counts"]["structural_corrections"] == 0
    before = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert replay_saved_review(tmp_path) == result
    assert run_source_review(tmp_path, files=files, task=task, cfg=cfg) == result
    assert client.calls == 1
    assert before == {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}


@pytest.mark.parametrize("error", [ValueError("Invalid configuration"), ResponseIntegrityError("Changed answer"),
                                   RuntimeError("Unknown pending process state")])
def test_other_errors_are_not_downgraded_to_request_failure(tmp_path, error):
    files, task, cfg = fixture()
    with pytest.raises(type(error), match=str(error)):
        run_source_review(tmp_path, files=files, task=task, cfg=cfg, client=FailingClient(error))
    assert not (tmp_path / "result.json").exists()


def test_recording_failure_marker_is_not_downgraded_live_or_replayed(tmp_path):
    files, task, cfg = fixture()
    error = ModelRequestFailure("Request ended without an answer")
    error.recording_failed = True
    error.recording_errors = [{"error_type": "OSError", "error": "Receipt persistence failed"}]
    with pytest.raises(ModelRequestFailure):
        run_source_review(tmp_path, files=files, task=task, cfg=cfg, client=FailingClient(error))
    with pytest.raises(ValueError, match="Request ended"):
        replay_saved_review(tmp_path)
    assert not (tmp_path / "result.json").exists()


def test_absent_saved_view_preserves_old_renderer_and_request_failure_behavior(tmp_path):
    files, task, cfg = fixture()
    legacy = prepare_review_material(files=files, task=task, cfg=cfg, prompt_view=None)
    assert "prompt_view" not in legacy and "target_index" in payload(build_source_review_prompt(legacy))
    with pytest.raises(InputTooLarge):
        run_source_review(tmp_path, files=files, task=task, cfg=cfg, prompt_view=None,
                          client=FailingClient(InputTooLarge("Legacy request rejected")))
    assert "prompt_view" not in json.loads((tmp_path / "inputs.json").read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="Legacy request rejected"):
        replay_saved_review(tmp_path)
    assert not (tmp_path / "result.json").exists()


def test_legacy_accepted_review_is_readonly_replayable(tmp_path):
    files, task, cfg = fixture()
    result = run_source_review(tmp_path, files=files, task=task, cfg=cfg, prompt_view=None,
                               client=Client({"outcome": "completed", "findings": []}))
    assert replay_saved_review(tmp_path) == result


def test_unknown_prompt_view_is_not_reinterpreted():
    files, task, cfg = fixture()
    material = prepare_review_material(files=files, task=task, cfg=cfg)
    material["prompt_view"] = "unrecognized"
    with pytest.raises(ValueError, match="prompt view"):
        build_source_review_prompt(material)
