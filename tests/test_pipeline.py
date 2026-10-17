"""The formal chain consumes a single accepted semantic response; no real APIs."""
from copy import deepcopy
import json
import sys
from threading import Event

import pytest

from skillflow import pipeline
from skillflow.common.recording import injected_factory, canonical_sha256
from tests.propagation.annotation.helpers import valid_raw_response, material_from_model_payload
from tests.propagation.annotation.test_security_runner import setup_run
from tests.propagation.review.test_refinement import SequenceReview


@pytest.fixture(autouse=True)
def offline_stable_implementation(monkeypatch):
    # Concurrent repository edits must not change an injected test's producer.
    import socket
    from skillflow.common import recording
    from skillflow.doe import formal_runner
    from skillflow.propagation import runner
    from skillflow.task import runner as task_runner
    from skillflow.propagation.review import refinement
    snapshot = recording.implementation_provenance()
    original = recording.implementation_provenance
    for name, module in list(sys.modules.items()):
        if name.startswith("skillflow") and getattr(module, "implementation_provenance", None) is original:
            monkeypatch.setattr(module, "implementation_provenance", lambda: deepcopy(snapshot))
    monkeypatch.setattr(socket.socket, "connect", lambda *_: pytest.fail("Pipeline test used network"))
    from tests.test_source_task_pipeline import TaskClient
    run = pipeline.run_analysis
    def with_task(*args, **kwargs):
        if not kwargs.get("replay"):
            kwargs.setdefault("task_client_factory", injected_factory(TaskClient()))
        return run(*args, **kwargs)
    monkeypatch.setattr(pipeline, "run_analysis", with_task)



class Annotation:
    def __init__(self, mode="ok", stop=None):
        self.mode, self.stop, self.prompts = mode, stop, []

    def complete(self, prompt):
        self.prompts.append(prompt)
        if self.mode == "error":
            raise RuntimeError("Transport failed without a complete candidate")
        if self.mode == "bad" and len(self.prompts) == 1:
            return "{not json"
        material = json.JSONDecoder().raw_decode(prompt.split("\nINPUT_JSON\n", 1)[1])[0]
        result = valid_raw_response(material_from_model_payload(material))
        if self.stop is not None:
            self.stop.set()
        return result


def prepared(tmp_path, **kwargs):
    _unused, source, graph = setup_run(tmp_path)
    directory = tmp_path / "pipeline"
    manifest = pipeline.prepare_analysis_run(source, graph, run_dir=directory, **kwargs)
    assert manifest["preparation_status"] == "ready", manifest
    return directory


def forbidden(*_a, **_kw):
    pytest.fail("Unexpected model call")


def test_all_four_stages_normalize_without_model_correction_and_freeze_audit(tmp_path):
    from skillflow.common.recording import read_json
    from skillflow.propagation.annotation.loading import load_annotation_run
    from skillflow.propagation.runner import load_propagation_materials

    class Wrapped:
        def __init__(self, client):
            self.client = client
        def complete(self, prompt):
            return json.dumps(self.client.complete(prompt), ensure_ascii=False) + "}\r\n"

    directory = prepared(tmp_path)
    first, review, repair = Annotation(), SequenceReview(["issue", "ok"]), Annotation()
    result = pipeline.run_analysis(directory, client_factory=injected_factory(Wrapped(first)),
        review_client_factory=injected_factory(Wrapped(review)),
        repair_client_factory=injected_factory(Wrapped(repair)))
    # This deliberately incomplete fixture retains its existing unbound Task
    # requirement: normalization must not manufacture a demand or erase it.
    assert result["status"] == "diagnostic", result
    assert result["annotation"]["status"] == "complete"
    assert result["refinement"]["status"] == "review_passed"
    assert result["propagation"]["status"] == "complete"
    assert result["doe"]["status"] == "partial"
    assert {item["code"] for item in read_json(directory / "doe/doe-result.json")["diagnostics"]} >= {"unbound_requirement"}
    assert result["counts"]["logical_calls"] == 5
    assert result["counts"]["structural_corrections"] == 0
    assert result["counts"]["json_normalizations"] == 4
    assert (len(first.prompts), len(review.prompts), len(repair.prompts)) == (1, 2, 1)
    # Frozen source and semantic inputs have one owner. Prompts/calls retain
    # their exact sent bytes, but stages do not persist another material DTO.
    assert not list(directory.rglob('material.json'))
    assert not list(directory.rglob('annotation-material.json'))
    assert len(list(directory.rglob('snapshot.json'))) == 1
    assert len(list(directory.rglob('cfg.json'))) == 1
    assert len(list(directory.rglob('runtime-contract.json'))) == 1
    assert len(list(directory.rglob('user-request.json'))) == 1
    for relative in ('refinement', 'refinement/initial-review', 'refinement/final-review'):
        assert not (directory / relative / 'inputs/candidate.json').exists()
    from skillflow.propagation.annotation.requests import load_repair_context
    assert not list(directory.rglob('repair-context.json'))
    assert 'review_material' not in load_repair_context(directory / 'refinement/repair')
    for stage in ('initial_review', 'repair', 'final_review'):
        receipt = read_json(directory / 'refinement/result.json')[stage]
        assert set(receipt) == {'path', 'manifest_sha256', 'result_sha256', 'status', 'reason', 'counts'}
    for stage in ('initial-review', 'final-review'):
        assert 'resolved_findings' not in read_json(directory / 'refinement' / stage / 'result.json')
    stages = (("annotation", "annotation"), ("refinement/initial-review", "review"),
              ("refinement/repair", "annotation"), ("refinement/final-review", "review"))
    for relative, kind in stages:
        call = directory / relative / "calls" / kind / "a001"
        raw = read_json(call / "response.json")
        receipt, validation = map(read_json, (call / "normalization.json", call / "validation.json"))
        assert raw.endswith("}}\r\n")
        assert read_json(call / "call.json")["response"] == raw
        assert validation["response_sha256"] == canonical_sha256(raw) == receipt["raw_sha256"]
        assert validation["candidate_sha256"] == receipt["normalized_sha256"]
        assert validation["normalization_sha256"] == canonical_sha256(receipt)
    selected = load_annotation_run(directory / "refinement/repair")
    assert selected["accepted_response"].endswith("}}\r\n")
    assert selected["raw_annotation"]["outcome"] == "completed"
    frozen = directory / "refinement/repair/calls/annotation/a001/normalization.json"
    assert not (directory / "propagation/audit/accepted-call").exists()
    assert read_json(directory / "propagation/manifest.json")["upstream"]["path"] == "../refinement/repair"
    assert pipeline.load_analysis_run(directory)["result"] == result
    assert pipeline.run_analysis(directory, client_factory=forbidden) == result
    assert pipeline.replay_analysis(directory) == result
    assert (len(first.prompts), len(review.prompts), len(repair.prompts)) == (1, 2, 1)
    receipt = read_json(frozen)
    receipt["removed_offset"] += 1
    frozen.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ValueError):
        load_propagation_materials(directory / "propagation")


@pytest.mark.parametrize("review_modes,repair_mode,calls,selected,review_status", [
    (["ok"], "ok", 2, "annotation", "review_passed"),
    (["issue", "ok"], "ok", 4, "refinement/repair", "review_passed"),
    (["issue", "issue"], "ok", 4, "refinement/repair", "repair_limit"),
    (["cannot"], "ok", 2, "annotation", "semantic_failure"),
    (["bad", "ok"], "ok", 3, "annotation", "review_passed"),
    (["issue", "ok"], "bad", 5, "refinement/repair", "review_passed"),
])
def test_recorded_chain_selection_and_offline_replay(tmp_path, review_modes,repair_mode,calls,selected,review_status):
    directory = prepared(tmp_path)
    first, review, repair = Annotation(), SequenceReview(review_modes), Annotation(repair_mode)
    result = pipeline.run_analysis(directory, client_factory=injected_factory(first),
        review_client_factory=injected_factory(review), repair_client_factory=injected_factory(repair))
    assert result["status"] in {"complete", "diagnostic"}, result
    assert result["refinement"]["status"] == review_status
    assert result["selected_annotation"]["path"] == selected
    assert result["counts"]["logical_calls"] == calls + 1
    assert len(first.prompts) == 1
    assert len(first.prompts) + len(review.prompts) + len(repair.prompts) == calls
    assert (directory / "doe/doe-result.json").is_file()
    assert not (directory / "doe/task").exists()
    assert not (directory / "doe/demand").exists()
    assert pipeline.load_analysis_run(directory)["result"] == result
    assert pipeline.run_analysis(directory, client_factory=forbidden) == result
    assert pipeline.replay_analysis(directory) == result


def test_failed_initial_transport_stops_and_replays_without_review(tmp_path):
    directory = prepared(tmp_path)
    first = Annotation("error")
    result = pipeline.run_analysis(directory, client_factory=injected_factory(first), review_client_factory=forbidden)
    assert result["status"] == "failed"
    assert result["annotation"]["status"] == "execution_error"
    assert result["counts"]["logical_calls"] == 2
    assert result["refinement"] is result["propagation"] is result["doe"] is None
    assert pipeline.load_analysis_run(directory)["result"] == result
    assert pipeline.replay_analysis(directory) == result


def test_all_stages_correct_structure_beyond_previous_caps_and_replay(tmp_path):
    class DelayedAnnotation(Annotation):
        def __init__(self, invalid):
            super().__init__()
            self.invalid = invalid

        def complete(self, prompt):
            if self.invalid:
                self.invalid -= 1
                self.prompts.append(prompt)
                return '{"duplicate":1,"duplicate":2}'
            return super().complete(prompt)

    directory = prepared(tmp_path)
    first, repair = DelayedAnnotation(5), DelayedAnnotation(4)
    review = SequenceReview(["bad", "bad", "issue", "bad", "bad", "ok"])
    result = pipeline.run_analysis(directory, client_factory=injected_factory(first),
        review_client_factory=injected_factory(review), repair_client_factory=injected_factory(repair))
    assert result["status"] in {"complete", "diagnostic"}, result
    assert result["refinement"]["status"] == "review_passed"
    assert result["selected_annotation"]["path"] == "refinement/repair"
    assert result["counts"]["logical_calls"] == 18
    assert result["counts"]["structural_corrections"] == 13
    from skillflow.propagation.annotation.loading import load_annotation_run
    selected = load_annotation_run(directory / "refinement/repair")
    assert selected["accepted_call"] == "calls/annotation/a005"
    assert (directory / "refinement/repair/calls/annotation/a001/validation.json").is_file()
    assert pipeline.load_analysis_run(directory)["result"] == result
    assert pipeline.replay_analysis(directory) == result
    assert len(first.prompts) == 6 and len(repair.prompts) == 5 and len(review.prompts) == 6

    # Even an early rejected response remains bound after a later valid response.
    prior = directory / "refinement/repair/calls/annotation/a002/response.json"
    prior.write_text('"changed"', encoding="utf-8")
    from skillflow.propagation.runner import load_propagation_materials
    with pytest.raises(ValueError, match="digest mismatch|changed|differs"):
        load_propagation_materials(directory / "propagation")


def test_user_request_is_frozen_through_repair_and_doe(tmp_path):
    from skillflow.doe.formal_runner import load_doe_run
    directory = prepared(tmp_path, user_request="Return the requested value only.")
    first, review, repair = Annotation(), SequenceReview(["issue", "ok"]), Annotation()
    result = pipeline.run_analysis(directory, client_factory=injected_factory(first),
        review_client_factory=injected_factory(review), repair_client_factory=injected_factory(repair))
    assert result["doe"] is not None, result
    for prompt in [*first.prompts, *review.prompts, *repair.prompts]:
        assert "Return the requested value only." in prompt
    checked = load_doe_run(directory / 'doe')['annotation']
    assert checked['task']['basis'] == 'user_request'
    assert checked['material']['user_request'] == 'Return the requested value only.'
    assert not (directory / 'doe/audit/annotation.json').exists()


def test_accepted_annotation_interrupt_resume_does_not_resend(tmp_path):
    directory = prepared(tmp_path)
    stop = Event()
    first, review = Annotation(stop=stop), SequenceReview(["ok"])
    result = pipeline.run_analysis(directory, client_factory=injected_factory(first),
        review_client_factory=injected_factory(review), stop_event=stop)
    assert result["status"] == "interrupted", result
    assert len(first.prompts) == 1 and not review.prompts
    assert pipeline.replay_analysis(directory) == result
    stop.clear()
    resumed = pipeline.run_analysis(directory, client_factory=forbidden,
        review_client_factory=injected_factory(review), stop_event=stop)
    assert resumed["doe"] is not None, resumed
    assert len(first.prompts) == len(review.prompts) == 1
    assert pipeline.replay_analysis(directory) == resumed


def test_tampered_selection_and_configuration_rejected(tmp_path):
    directory = prepared(tmp_path)
    result = pipeline.run_analysis(directory, client_factory=injected_factory(Annotation()),
        review_client_factory=injected_factory(SequenceReview(["ok"])))
    assert result["doe"] is not None, result
    with pytest.raises(ValueError, match="configuration"):
        pipeline.run_analysis(directory, config={"model": "different"})
    path = directory / "result.json"
    record = json.loads(path.read_bytes())
    record["selected_annotation"]["path"] = "refinement/repair"
    record["manifest_sha256"] = canonical_sha256({k: v for k, v in record.items() if k != "manifest_sha256"})
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="Selected candidate"):
        pipeline.load_analysis_run(directory)


def test_read_is_source_independent_but_replay_is_not(tmp_path, monkeypatch):
    directory = prepared(tmp_path)
    result = pipeline.run_analysis(directory, client_factory=injected_factory(Annotation()),
        review_client_factory=injected_factory(SequenceReview(["ok"])))
    assert result["doe"] is not None, result
    changed = {"files": {"changed.py": "a" * 64}, "sha256": canonical_sha256({"changed.py": "a" * 64}), "python": "test"}
    monkeypatch.setattr(pipeline, "implementation_provenance", lambda: changed)
    assert pipeline.load_analysis_run(directory)["result"] == result
    with pytest.raises(ValueError, match="implementation identity changed"):
        pipeline.replay_analysis(directory)
