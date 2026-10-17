"""Derived review views and receipts keep exact JSON primitive types."""
import json
import pytest

from skillflow.common.recording import read_json
from skillflow.propagation.review import runner
from tests.propagation.review.test_runner import ReviewClient, forbidden
from tests.propagation.review.test_core import fixture


@pytest.mark.parametrize("artifact", ["observations", "result"])
@pytest.mark.parametrize("number_kind", ["float", "bool"])
def test_resealed_equal_numeric_projection_cannot_replace_exact_json(tmp_path, monkeypatch, artifact, number_kind):
    directory = tmp_path / "review"
    material, candidate = fixture()
    runner.prepare_candidate_run(material, candidate, run_dir=directory,
                                 provenance={"kind": "explicit_structural_test"})
    assert runner.run_review(directory, client=ReviewClient())["status"] == "complete"
    if artifact == "result":
        path = directory / "result.json"
        value = runner._unseal(read_json(path))
        assert value["counts"]["logical_calls"] == 1
        value["counts"]["logical_calls"] = 1.0 if number_kind == "float" else True
        path.write_text(json.dumps(runner._seal(value)), encoding="utf-8")
    else:
        path = directory / "inputs" / (artifact + ".json")
        value = read_json(path)
        reference = next(ref for row in value for ref in row["values"] if ref.get("kind") == "input")
        assert reference["index"] == 0
        reference["index"] = 0.0 if number_kind == "float" else False
        path.write_text(json.dumps(value), encoding="utf-8")
        manifest = runner._unseal(read_json(directory / "manifest.json"))
        manifest["files"] = runner._files(directory)
        (directory / "manifest.json").write_text(json.dumps(runner._seal(manifest)), encoding="utf-8")
    before = (directory / "result.json").read_bytes()
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    with pytest.raises(ValueError, match="differ"):
        runner.replay_run(directory)
    with pytest.raises(ValueError, match="differ"):
        runner.load_review_run(directory)
    assert before == (directory / "result.json").read_bytes()


def test_review_persists_findings_without_resolved_annotation_copies(tmp_path):
    from tests.propagation.review.test_runner import response_for
    directory = tmp_path / "review"
    material, candidate = fixture()
    runner.prepare_candidate_run(material, candidate, run_dir=directory,
                                 provenance={"kind": "explicit_structural_test"})
    def issue(response, prepared):
        issue = response_for(prepared, finding=True)
        # Root targeting used to copy the entire candidate into resolved_findings.
        issue["findings"][0]["target_ids"] = [next(row["id"] for row in prepared["target_index"] if row["pointer"] == "")]
        return issue
    result = runner.run_review(directory, client=ReviewClient(issue))
    assert result["status"] == "complete"
    assert result["resolved_findings"][0]["targets"][0]["value"] == candidate
    saved = runner._unseal(read_json(directory / "result.json"))
    assert "resolved_findings" not in saved
    assert saved["review"] == result["review"]
    assert runner.load_review_run(directory)["result"] == result
    assert runner.replay_run(directory) == result
