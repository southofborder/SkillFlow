"""Ordinary loading verifies calls without mutating or relaxing producer replay."""
from copy import deepcopy

import pytest

from skillflow.common.recording import read_json, canonical_sha256
from skillflow.propagation.review import runner, refinement
from skillflow.propagation.annotation import runner as annotation_runner
from skillflow.propagation.annotation.loading import load_annotation_attempt
from tests.propagation.review.test_refinement import prepared, SequenceReview, Repair
from tests.propagation.review.test_runner import file_bytes, forbidden


@pytest.mark.parametrize("modes,repair_mode", [
    (["ok"], None), (["issue", "ok"], None), (["issue", "issue"], None),
    (["bad", "ok"], None), (["cannot"], None), (["error"], None),
    (["issue", "ok"], "bad"), (["issue"], "error"), (["issue", "cannot"], None)])
def test_load_saved_decisions_readonly_with_different_current_source(tmp_path, monkeypatch, modes, repair_mode):
    directory, _, raw = prepared(tmp_path)
    result = refinement.run_refinement(directory, review_client=SequenceReview(modes),
                                       repair_client=Repair(raw, mode=repair_mode))
    before = file_bytes(directory)
    for module in (runner, refinement, annotation_runner):
        monkeypatch.setattr(module, "implementation_provenance", lambda: {"changed": True})
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    monkeypatch.setattr(annotation_runner, "RecordingClient", forbidden)
    monkeypatch.setattr(refinement, "streaming_factory", forbidden)
    loaded = refinement.load_refinement_run(directory)
    assert loaded["result"] == result
    assert loaded["selected"] == result["selected"]
    assert loaded["raw_annotation"] == raw
    assert loaded["upstream_identity"]["files"]
    assert runner.load_review_run(directory / "initial-review")["result"] == result["initial_review"]
    if result["repair"]:
        assert load_annotation_attempt(directory / "repair")["result"] == result["repair"]
    assert before == file_bytes(directory)
    with pytest.raises(ValueError, match="implementation|Implementation"):
        refinement.replay_refinement(directory)
    with pytest.raises(ValueError, match="implementation|Implementation"):
        runner.replay_run(directory / "initial-review")


@pytest.mark.parametrize("target", ["decision", "review", "repair_response", "repair_reason"])
def test_readonly_refinement_rejects_altered_decision_or_saved_stages(tmp_path, target):
    directory, _, raw = prepared(tmp_path)
    repair_mode = "bad" if target == "repair_reason" else None
    result = refinement.run_refinement(directory, review_client=SequenceReview(["issue", "ok"]),
                                       repair_client=Repair(raw, mode=repair_mode))
    if target == "repair_response":
        import json
        path = directory / "repair" / annotation_runner.CALL_PATH / "response.json"
        value = read_json(path)
        value["task_revision_id"] = "0" * 64
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    else:
        import json
        path = directory / ({"decision": "result.json", "review": "initial-review/result.json",
                             "repair_reason": "repair/result.json"}[target])
        value = read_json(path)
        if target == "repair_reason":
            value["reason"] = "Fabricated failure reason"
        else:
            owner = refinement if target == "decision" else runner
            value = owner._unseal(value)
            value["reason"] = "Fabricated decision"
            value = owner._seal(value)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError):
        refinement.load_refinement_run(directory)


@pytest.mark.parametrize('change', ['path', 'digest', 'embedded_business', 'bool_count', 'float_count', 'aggregate_bool_count'])
def test_refinement_stage_receipt_remains_exact_and_has_no_business_copy(tmp_path, change):
    import json
    directory, _, _ = prepared(tmp_path)
    refinement.run_refinement(directory, review_client=SequenceReview(['ok']))
    path = directory / 'result.json'
    result = refinement._unseal(read_json(path))
    receipt = result['initial_review']
    assert set(receipt) == {'path', 'manifest_sha256', 'result_sha256', 'status', 'reason', 'counts'}
    if change == 'path':
        receipt['path'] = 'different-review'
    elif change == 'digest':
        receipt['result_sha256'] = '0' * 64
    elif change == 'embedded_business':
        receipt['review'] = {'findings': []}
    elif change == 'bool_count':
        assert receipt['counts']['logical_calls'] == 1
        receipt['counts']['logical_calls'] = True
    elif change == 'float_count':
        receipt['counts']['logical_calls'] = float(receipt['counts']['logical_calls'])
    else:
        assert result['counts']['logical_calls'] == 1
        result['counts']['logical_calls'] = True
    path.write_text(json.dumps(refinement._seal(result)), encoding='utf8')
    with pytest.raises(ValueError):
        refinement.load_refinement_run(directory)
