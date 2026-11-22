"""Fresh downstream generation from byte-bound local copies of accepted upstreams."""
import pytest

from skillflow.common.recording import sha_file
from skillflow.document_guided import runner
from skillflow.document_guided.online import read, inventory
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


def cloned_prefix(parent, child):
    runner.prepare_from_accepted_cfg(parent, run_dir=child)
    return read(child / "accepted-upstream.json")["copied_files"]


class DownstreamHarness(Harness):
    def complete(self, stage, prompt):
        if stage in {"task", "flow", "graph"}:
            raise AssertionError("Inherited upstream must never acquire a new response: " + stage)
        return super().complete(stage, prompt)


@pytest.mark.parametrize("repair", [False, True])
def test_fresh_downstream_uses_exact_cfg_without_resampling_upstreams(tmp_path, repair):
    parent = Harness(tmp_path / "parent")
    parent.prepare(tmp_path / "source")
    original = runner.run(parent.directory, client_factory=parent.factory)
    assert original["status"] == "complete"
    parent_bytes = inventory(parent.directory)
    child = DownstreamHarness(tmp_path / "child", domains=("cfg",) if repair else (), precise_repair=True)
    inherited = cloned_prefix(parent.directory, child.directory)
    assert not any((child.directory / name).exists() for name in (
        "steps/processing", "steps/task-correspondence", "steps/sensitivity", "review", "annotation",
        "selection.json", "propagation", "doe", "transport"))
    result = runner.run(child.directory, client_factory=child.factory)
    assert result["status"] == "complete", result
    assert not set(child.calls) & {"task", "flow", "graph"}
    assert child.calls.count("processing") == child.calls.count("review") == 1
    assert len(child.calls) == (9 if repair else 4)
    assert result["counts"]["logical_calls"] == len(child.calls) + 3
    assert result["repair_used"] is repair
    assert child.prompts["processing"] == parent.prompts["processing"]
    assert {name: sha_file(child.directory / name) for name in inherited} == inherited
    assert read(child.directory / "graph/initial.json") == read(parent.directory / "graph/initial.json")
    assert (child.directory / "propagation/data.json").is_file()
    assert (child.directory / "doe/doe-result.json").is_file()
    assert result["selected_annotation"] == ("revision/annotation" if repair else "annotation")
    calls = list(child.calls)
    assert runner.replay(child.directory) == result
    assert child.calls == calls
    assert inventory(parent.directory) == parent_bytes
    assert {name: sha_file(child.directory / name) for name in inherited} == inherited


def test_changed_inherited_cfg_is_rejected_without_regenerating_it(tmp_path):
    parent = Harness(tmp_path / "parent")
    parent.prepare(tmp_path / "source")
    assert runner.run(parent.directory, client_factory=parent.factory)["status"] == "complete"
    before = inventory(parent.directory)
    child = DownstreamHarness(tmp_path / "child")
    cloned_prefix(parent.directory, child.directory)
    graph = read(child.directory / "graph/initial.json")
    graph["unexpected_mutation"] = True
    runner.WRITER.json(child.directory / "graph/initial.json", graph)
    with pytest.raises(ValueError, match="changed|differs"):
        runner.run(child.directory, client_factory=child.factory)
    assert not child.calls
    assert inventory(parent.directory) == before
