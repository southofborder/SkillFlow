"""Corpus drivers require explicit source-only Task ownership, without new calls."""
import json

import pytest

from skillflow.task.runner import prepare_task_run, run_task
from tests.task.test_protocol import source, candidate, Client, inventory
from tools.propagation.task_runs import bind_task_runs, task_owner, read_task_runs


def test_missing_or_incomplete_task_mapping_is_rejected_without_preparation(tmp_path):
    output = tmp_path / "not-created"
    with pytest.raises(ValueError, match="Independent Task runs are required"):
        bind_task_runs(output, [{"case_id": "001"}])
    assert not output.exists()
    with pytest.raises(ValueError, match="exactly one"):
        bind_task_runs(output, [{"case_id": "001"}], {})


def test_completed_task_mapping_is_digest_bound_and_read_only(tmp_path):
    owner, output = tmp_path / "source-only-task", tmp_path / "driver"
    prepare_task_run(owner, source())
    assert run_task(owner, client=Client(candidate()))["status"] == "complete"
    cases = [{"case_id": "001", "source_sha256": source()["source_sha256"]}]
    before = inventory(owner)
    references = bind_task_runs(output, cases, {"001": owner})
    assert inventory(owner) == before
    output.mkdir()
    (output / "manifest.json").write_text(json.dumps({"task_runs": references}), encoding="utf-8")
    assert bind_task_runs(output, cases) == references
    assert task_owner(output, {"task_runs": references}, "001") == owner
    with pytest.raises(ValueError, match="source differs"):
        bind_task_runs(output, [{"case_id": "001", "source_sha256": "0" * 64}])


def test_task_mapping_json_paths_are_relative_to_its_file(tmp_path):
    path = tmp_path / "task-map.json"
    path.write_text(json.dumps({"001": "independent-task"}), encoding="utf-8")
    assert read_task_runs(path) == {"001": str(tmp_path / "independent-task")}
    path.write_text(json.dumps({"001": {"task": "inline baselines are not accepted"}}), encoding="utf-8")
    with pytest.raises(ValueError, match="completed independent"):
        read_task_runs(path)
