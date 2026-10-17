"""One bounded annotation replacement, isolated re-review and durable replay."""
from copy import deepcopy
import json
from threading import Event

import pytest

from skillflow.propagation.review import refinement
from skillflow.propagation.review import runner as review_runner
from skillflow.propagation.review.material import prepare_review_material
from skillflow.common.recording import read_json
from skillflow.propagation.annotation import runner as annotation_runner
from skillflow.propagation.annotation.inputs import load_prepared_material
from skillflow.propagation.annotation.requests import load_repair_context
from tests.propagation.annotation.helpers import valid_raw_response
from tests.propagation.annotation.test_security_runner import setup_run
from tests.propagation.review.test_core import fixture, empty_response, one_issue, cannot_assess
from tests.propagation.review.test_runner import response_for, material_from_prompt, forbidden


@pytest.fixture(autouse=True)
def import_all_refinement_producers():
    """Load every stage before freezing a run; source identity checks stay strict."""
    import skillflow.task.runner
    import skillflow.task.prompts
    import skillflow.propagation.annotation.loading
    import skillflow.propagation.annotation.requests
    import skillflow.propagation.review.report


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
            evidence = {"target": {"instruction_id": "ir_read", "path": []}, "reason": "The read instruction is the necessary target."}
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
        if self.mode == "bad" and len(self.prompts) == 1: return "{not json"
        if self.mode == "error": raise RuntimeError("transport failure")
        return deepcopy(self.raw)


def prepared(tmp_path):
    upstream, source, analysis = setup_run(tmp_path)
    material = load_prepared_material(upstream)
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
    (["bad", "ok"], None, "review_passed", 2, "original"),
    (["error"], None, "execution_error", 1, "original"),
    (["issue", "ok"], "bad", "review_passed", 4, "repair"),
    (["issue"], "error", "execution_error", 2, "original"),
    (["issue", "cannot"], None, "semantic_failure", 3, "repair"),
    (["issue", "bad", "ok"], None, "review_passed", 4, "repair"),
])
def test_one_repair_stop_rules_resume_and_zero_api_replay(tmp_path, monkeypatch, modes,repair_mode,expected,calls,selected):
    directory, material, raw = prepared(tmp_path)
    review, repair = SequenceReview(modes), Repair(raw, mode=repair_mode)
    result = refinement.run_refinement(directory, review_client=review, repair_client=repair)
    assert result["status"] == expected, result
    assert result["selected"] == selected
    assert result["counts"]["logical_calls"] == calls
    assert len(review.prompts) + len(repair.prompts) == calls
    assert result["counts"]["stage_calls"] <= 3
    saved = refinement._unseal(read_json(directory / 'result.json'))
    for name in ('initial_review', 'repair', 'final_review'):
        if saved[name] is not None:
            assert set(saved[name]) == {'path', 'manifest_sha256', 'result_sha256', 'status', 'reason', 'counts'}
    for field, folder in (("initial_review", "initial-review"), ("final_review", "final-review")):
        if result[field] is not None:
            assert "resolved_findings" in result[field]
            assert "resolved_findings" not in read_json(directory / folder / "result.json")
    if result["final_review"]:
        first, final = map(material_from_prompt, (review.prompts[0], review.prompts[-1]))
        assert final["source"] == first["source"] == material["source"]
        assert final["cfg"] == first["cfg"]
        assert set(final) == set(first)
        for forbidden_key in ("review_response", "resolved_targets", "repair_context", "expected"):
            assert forbidden_key not in final
        assert final["raw_annotation"] == raw
    if repair.prompts:
        assert not (directory / "repair/inputs/repair-context.json").exists()
        assert "original" not in load_repair_context(directory / "repair").get("identities", {})
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


def test_repair_freezes_the_original_independent_request_once(tmp_path):
    from tests.propagation.annotation.helpers import prepare_material
    upstream, source, analysis = setup_run(tmp_path)
    original = load_prepared_material(upstream)
    material = prepare_material(original["source"], original["cfg"],
        user_request="Return only the requested original value.")
    raw = valid_raw_response(material)
    directory = tmp_path / "task-policy-refinement"
    refinement.prepare_refinement_run(source, analysis, material, raw, run_dir=directory,
                                     provenance={"kind": "authored_test_candidate"})
    review, repair = SequenceReview(["issue", "ok"]), Repair(raw)
    result = refinement.run_refinement(directory, review_client=review, repair_client=repair)
    assert result["status"] == "review_passed", result
    assert load_prepared_material(directory / "repair") == material
    assert not (directory / "repair/inputs/material.json").exists()
    assert not (directory / "repair/inputs/package").exists()
    assert read_json(directory / "repair/manifest.json")["upstream"]["path"] == ".."
    assert not (directory / "repair/inputs/semantic-context.json").exists()
    assert not (directory / "repair/inputs/user-request.json").exists()
    assert material_from_prompt(review.prompts[-1])["user_request"] == material["user_request"]
    assert refinement.replay_refinement(directory) == result


@pytest.mark.parametrize("point", ["before", "repair_accept"])
def test_interrupt_does_not_start_later_calls_and_accepted_repair_is_not_resent(tmp_path, monkeypatch, point):
    directory, material, raw = prepared(tmp_path)
    stop = Event()
    if point == "before": stop.set()
    review = SequenceReview(["issue", "ok"])
    repair = Repair(raw, stop=stop if point == "repair_accept" else None)
    result = refinement.run_refinement(directory, review_client=review, repair_client=repair, stop_event=stop)
    assert result["status"] == "interrupted", result
    assert result["interrupt_point"] == ("before_initial" if point == "before" else "during_repair")
    if point == "repair_accept":
        assert result["repair"]["status"] == "interrupted"
        assert result["counts"]["logical_calls"] == 2
    assert refinement.replay_refinement(directory) == result
    if point == "before": assert not review.prompts and not repair.prompts
    else: assert len(review.prompts) == 1 and len(repair.prompts) == 1
    stop.clear()
    resumed = refinement.run_refinement(directory, review_client=review, repair_client=repair,
                                        stop_event=stop)
    assert resumed["status"] == "review_passed", resumed
    assert len(repair.prompts) == 1
    assert len(review.prompts) == 2


@pytest.mark.parametrize("relative", ["inputs/candidate.json", "inputs/provenance.json", "inputs/runtime-contract.json",
                                       "initial-review/inputs/prompt.txt", "repair/inputs/prompt.txt"])
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
    evidence = deepcopy(raw["ir_semantics"]["ir_read"]["events"][0]["evidences"][0])
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


def test_local_repair_factory_failure_replays_without_sending_request(tmp_path, monkeypatch):
    directory, material, raw = prepared(tmp_path)
    def broken(*args, **kwargs): raise ValueError("credential environment missing")
    monkeypatch.setattr(refinement, "streaming_factory", broken)
    result = refinement.run_refinement(directory, review_client=SequenceReview(["issue"]))
    assert result["status"] == "execution_error", result
    assert result["counts"]["logical_calls"] == 1
    # The lazily loaded factory now belongs to the annotation child. A pending
    # request identity may be prepared, but no transport was started or counted.
    assert result["local_failure"] is None
    assert result["stage"] == "repair"
    assert result["repair"]["status"] == "execution_error"
    assert result["repair"]["counts"]["logical_calls"] == 0
    assert (directory / "repair/calls/annotation/a001/request.json").is_file()
    assert not list((directory / "repair/calls").rglob("call.json"))
    assert not list((directory / "repair/calls").rglob("response.json"))
    monkeypatch.setattr(refinement, "streaming_factory", forbidden)
    assert refinement.replay_refinement(directory) == result
    assert refinement.run_refinement(directory, review_client_factory=forbidden) == result


@pytest.mark.parametrize("relative", ["execution-boundary.json", "calls/annotation/a001/request.json"])
def test_terminal_repair_factory_failure_rejects_tampering(tmp_path, monkeypatch, relative):
    directory, material, raw = prepared(tmp_path)
    def broken(*args, **kwargs): raise ValueError("credential environment missing")
    monkeypatch.setattr(refinement, "streaming_factory", broken)
    result = refinement.run_refinement(directory, review_client=SequenceReview(["issue"]))
    assert result["status"] == "execution_error"
    path = directory / "repair" / relative
    saved = read_json(path)
    saved["unexpected"] = "tampered"
    path.write_text(json.dumps(saved), encoding="utf-8")
    monkeypatch.setattr(refinement, "streaming_factory", forbidden)
    with pytest.raises(ValueError):
        refinement.run_refinement(directory, review_client_factory=forbidden)


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


def test_request_span_finding_roundtrip_repair_and_independent_rereview(tmp_path):
    from tests.propagation.annotation.helpers import prepare_material
    upstream, source, analysis = setup_run(tmp_path)
    base = load_prepared_material(upstream)
    material = prepare_material(base["source"], base["cfg"],
        user_request="Return the selected original value.")
    raw = valid_raw_response(material)
    directory = tmp_path / "span-refinement"
    refinement.prepare_refinement_run(source, analysis, material, raw, run_dir=directory,
                                     provenance={"kind": "authored_test_candidate"})

    class SpanReview(SequenceReview):
        def complete(self, prompt):
            response = super().complete(prompt)
            if response["findings"]:
                response["findings"][0]["evidences"] = [
                    {"file": "task/user-request.txt", "start_line": 1, "end_line": 1,
                     "reason": "The user request specifies preservation of the selected original value."}]
            return response

    review, repair = SpanReview(["issue", "ok"]), Repair(raw)
    result = refinement.run_refinement(directory, review_client=review, repair_client=repair)
    assert result["status"] == "review_passed", result
    assert not (directory / "repair/inputs/repair-context.json").exists()
    context = load_repair_context(directory / "repair")
    assert "task/user-request.txt" in json.dumps(context)
    final = material_from_prompt(review.prompts[-1])
    assert "review_response" not in final and "repair_context" not in final
    assert final["user_request"] == material["user_request"]
    html = (directory / "initial-review/report.html").read_text(encoding="utf-8")
    assert "Return the selected original value." in html
    assert refinement.load_refinement_run(directory)["result"] == result
    assert refinement.replay_refinement(directory) == result


def test_accepted_task_revision_interruption_replays_child_receipt_and_resumes_once(tmp_path):
    from tests.test_source_task_pipeline import TaskClient, FirstIssue
    from tests.propagation.annotation.helpers import FakeClient
    directory, _, _ = prepared(tmp_path)
    stop = Event()
    class StopAfterRevision(TaskClient):
        def complete(self, prompt):
            value = super().complete(prompt)
            stop.set()
            return value
    task_repair, review, repair = StopAfterRevision(revised=True), FirstIssue("task"), FakeClient()
    result = refinement.run_refinement(directory, review_client=review, repair_client=repair,
        task_repair_client=task_repair, stop_event=stop)
    assert result["status"] == "interrupted", result
    assert result["interrupt_point"] == "during_task_revision"
    assert result["task_revision"]["status"] == "interrupted"
    assert result["repair"] is None and result["counts"]["logical_calls"] == 2
    assert refinement.replay_refinement(directory) == result
    assert len(task_repair.prompts) == 1 and len(review.prompts) == 1
    stop.clear()
    resumed = refinement.run_refinement(directory, review_client=review, repair_client=repair,
        task_repair_client=task_repair, stop_event=stop)
    assert resumed["status"] == "review_passed", resumed
    assert resumed["counts"]["logical_calls"] == 4
    assert len(task_repair.prompts) == 1 and len(review.prompts) == 2 and len(repair.prompts) == 1
