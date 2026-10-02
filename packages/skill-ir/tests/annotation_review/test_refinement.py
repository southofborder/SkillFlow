"""One bounded annotation replacement, isolated re-review and durable replay."""
from copy import deepcopy
import json
from threading import Event

import pytest

from skill_ir.annotation_review import refinement
from skill_ir.annotation_review import runner as review_runner
from skill_ir.annotation_review.material import prepare_review_material
from skill_ir.recording import read_json
from skill_ir.security_profile import runner as annotation_runner
from security_profile.helpers import valid_raw_response
from security_profile.test_security_runner import setup_run
from annotation_review.test_core import fixture, empty_response, one_issue, cannot_assess
from annotation_review.test_runner import response_for, material_from_prompt, forbidden


class SequenceReview:
    def __init__(self, modes):
        self.modes = list(modes)
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        material = material_from_prompt(prompt)
        mode = self.modes.pop(0)
        if mode == "bad": return "not JSON"
        if mode == "error": raise RuntimeError("temporary transport failure")
        if mode == "cannot":
            evidence = {"basis": "cfg", "ref_id": material["instruction_index"]["ir_read"]["ref_id"],
                        "quote": "read_local_config"}
            return {"outcome": "cannot_assess", "failure": {"reason": "必要材料冲突。",
                    "target_ids": [material["target_index"][0]["id"]], "evidences": [evidence]}}
        return response_for(material, finding=mode == "issue")


class Repair:
    def __init__(self, raw, *, mode=None, stop=None):
        self.raw = raw
        self.prompts = []
        self.mode = mode
        self.stop = stop

    def complete(self, prompt):
        self.prompts.append(prompt)
        if self.stop is not None: self.stop.set()
        if self.mode == "bad": return "{not json"
        if self.mode == "error": raise RuntimeError("transport failure")
        return deepcopy(self.raw)


def prepared(tmp_path):
    upstream, source, analysis = setup_run(tmp_path)
    material = read_json(upstream / "inputs/material.json")
    raw = valid_raw_response(material)
    directory = tmp_path / "refinement"
    refinement.prepare_refinement_run(source, analysis, material, raw, run_dir=directory,
                                     provenance={"kind": "authored_test_candidate"})
    return directory, material, raw


@pytest.mark.parametrize("modes,repair_mode,expected,calls,selected", [
    (["ok"], None, "review_passed", 1, "original"),
    (["issue", "ok"], None, "review_passed", 3, "repair"),
    (["issue", "issue"], None, "repair_limit", 3, "repair"),
    (["cannot"], None, "semantic_failure", 1, "original"),
    (["bad"], None, "invalid_response", 1, "original"),
    (["error"], None, "execution_error", 1, "original"),
    (["issue"], "bad", "invalid_response", 2, "original"),
    (["issue"], "error", "execution_error", 2, "original"),
    (["issue", "cannot"], None, "semantic_failure", 3, "repair"),
    (["issue", "bad"], None, "invalid_response", 3, "repair"),
])
def test_one_repair_stop_rules_resume_and_zero_api_replay(tmp_path, monkeypatch, modes,repair_mode,expected,calls,selected):
    directory, material, raw = prepared(tmp_path)
    review, repair = SequenceReview(modes), Repair(raw, mode=repair_mode)
    result = refinement.run_refinement(directory, review_client=review, repair_client=repair)
    assert result["status"] == expected, result
    assert result["selected"] == selected
    assert result["counts"]["logical_calls"] == calls
    assert len(review.prompts) + len(repair.prompts) == calls
    assert len(repair.prompts) <= 1
    if len(review.prompts) == 2:
        first, final = map(material_from_prompt, review.prompts)
        assert final["source"] == first["source"] == material["source"]
        assert final["cfg"] == first["cfg"]
        assert set(final) == set(first)
        for forbidden_key in ("review_response", "resolved_targets", "repair_context", "expected"):
            assert forbidden_key not in final
        assert final["raw_annotation"] == raw
    if repair.prompts:
        assert "original" not in read_json(directory / "repair/inputs/repair-context.json").get("identities", {})
        assert read_json(directory / "repair/manifest.json")["request_kind"] == "repair"
    monkeypatch.setattr(review_runner, "RecordingClient", forbidden)
    monkeypatch.setattr(annotation_runner, "RecordingClient", forbidden)
    monkeypatch.setattr(refinement, "streaming_factory", forbidden)
    assert refinement.run_refinement(directory, review_client_factory=forbidden,
                                     repair_client_factory=forbidden) == result
    assert refinement.replay_refinement(directory) == result


def test_pure_service_stops_after_one_full_repair_and_isolates_rereview():
    material, raw = fixture()
    review, repair = SequenceReview(["issue", "issue"]), Repair(raw)
    result = refinement.refine_annotation(material, raw, review_client=review, repair_client=repair)
    assert result["status"] == "repair_limit", result
    assert result["counts"]["logical_calls"] == 3
    assert len(repair.prompts) == 1
    final = material_from_prompt(review.prompts[-1])
    assert "review_response" not in final and final["raw_annotation"] == raw


@pytest.mark.parametrize("point", ["before", "repair_accept"])
def test_interrupt_does_not_start_later_calls_and_accepted_repair_is_not_resent(tmp_path, monkeypatch, point):
    directory, material, raw = prepared(tmp_path)
    stop = Event()
    if point == "before": stop.set()
    review = SequenceReview(["issue", "ok"])
    repair = Repair(raw, stop=stop if point == "repair_accept" else None)
    result = refinement.run_refinement(directory, review_client=review, repair_client=repair, stop_event=stop)
    assert result["status"] == "interrupted", result
    assert refinement.replay_refinement(directory) == result
    if point == "before": assert not review.prompts and not repair.prompts
    else: assert len(review.prompts) == 1 and len(repair.prompts) == 1
    stop.clear()
    resumed = refinement.run_refinement(directory, review_client=review, repair_client=repair,
                                        stop_event=stop)
    assert resumed["status"] == "review_passed", resumed
    assert len(repair.prompts) == 1
    assert len(review.prompts) == 2


@pytest.mark.parametrize("relative", ["inputs/candidate.json", "inputs/provenance.json", "inputs/material.json",
                                       "initial-review/inputs/prompt.txt", "repair/inputs/repair-context.json"])
def test_material_or_repair_context_tampering_rejected(tmp_path, relative):
    directory, material, raw = prepared(tmp_path)
    result = refinement.run_refinement(directory, review_client=SequenceReview(["issue", "ok"]), repair_client=Repair(raw))
    assert result["status"] == "review_passed", result
    path = directory / relative
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError):
        refinement.replay_refinement(directory)


def test_explicit_candidate_run_keeps_external_provenance_out_of_prompt(tmp_path):
    material, raw = fixture()
    directory = tmp_path / "review"
    review_runner.prepare_candidate_run(material, raw, run_dir=directory,
        provenance={"mutation": "EXPECTED_DEFECT_CANARY", "history": "authored candidate"})
    assert "EXPECTED_DEFECT_CANARY" not in (directory / "inputs/prompt.txt").read_text(encoding="utf-8")
    result = review_runner.run_review(directory, client=SequenceReview(["ok"]))
    assert result["status"] == "complete"
    assert review_runner.replay_run(directory) == result


def test_repair_semantic_failure_has_no_rereview_and_retains_original(tmp_path):
    directory, material, raw = prepared(tmp_path)
    evidence = deepcopy(raw["transfer_specs"]["ir_read"]["events"][0]["evidences"][0])
    class CannotRepair:
        def complete(self, prompt):
            return {"outcome": "cannot_assess", "failure": {"reason": "必要表示冲突。",
                    "instruction_ids": ["ir_read"], "evidences": [evidence]}}
    review = SequenceReview(["issue"])
    result = refinement.run_refinement(directory, review_client=review, repair_client=CannotRepair())
    assert result["status"] == "semantic_failure", result
    assert result["selected"] == "original" and result["final_review"] is None
    assert result["counts"]["logical_calls"] == 2
    assert refinement.replay_refinement(directory) == result


def test_local_repair_factory_failure_replays_without_creating_request(tmp_path, monkeypatch):
    directory, material, raw = prepared(tmp_path)
    def broken(*args, **kwargs): raise ValueError("credential environment missing")
    monkeypatch.setattr(refinement, "streaming_factory", broken)
    result = refinement.run_refinement(directory, review_client=SequenceReview(["issue"]))
    assert result["status"] == "execution_error", result
    assert result["counts"]["logical_calls"] == 1
    assert result["local_failure"]["stage"] == "repair"
    assert not (directory / "repair/calls").exists()
    monkeypatch.setattr(refinement, "streaming_factory", forbidden)
    assert refinement.replay_refinement(directory) == result
    assert refinement.run_refinement(directory, review_client_factory=forbidden) == result


def test_refinement_report_links_resolve(tmp_path):
    import re
    directory, material, raw = prepared(tmp_path)
    result = refinement.run_refinement(directory, review_client=SequenceReview(["issue", "ok"]), repair_client=Repair(raw))
    assert result["status"] == "review_passed", result
    refinement.replay_refinement(directory)
    for folder in (directory, directory / "replay"):
        text = (folder / "report.html").read_text(encoding="utf-8")
        for href in re.findall(r"href='([^']+)'", text):
            assert (folder / href).is_file(), href
