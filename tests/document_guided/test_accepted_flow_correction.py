"""Accepted flow corrections preserve raw-response versus candidate identity."""
import json

import pytest

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.document_guided import accepted_upstream, runner
from skillflow.document_guided.online import inventory, prepare_step, read, run_step
from tests.document_guided.test_accepted_upstream_integrity import old_stage
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


@pytest.mark.parametrize("old", [False, True])
@pytest.mark.parametrize("normalized", [False, True])
def test_accepted_flow_correction_reconstructs_raw_prior_response(tmp_path, monkeypatch, old, normalized):
    harness = Harness(tmp_path / "donor")
    harness.prepare(tmp_path / "package")
    source = read_snapshot(harness.directory / "source")[1]
    owner = harness.directory / "steps/flow"
    prepare_step(owner, "Complete synthetic flow source and obligations.", kind="flow_document",
        context={"source_owner": harness.directory / "source"},
        dependencies=[harness.directory / "source/manifest.json"], max_corrections=1)
    raw = json.dumps({"outcome": "cannot_assess"}) + ("}" if normalized else "")
    expected = "Read the known source and return its supported flow; retain located uncertainty."
    replies = [raw, expected]

    class Client:
        def complete(self, prompt):
            return replies.pop(0)

    assert run_step(owner, client=Client()) == expected
    assert not replies
    if old:
        old_stage(owner)
    before = inventory(owner)
    assert (owner / "calls/a001/normalization.json").is_file() is normalized
    monkeypatch.setattr("skillflow.document_guided.online.run_step",
        lambda *args, **kwargs: pytest.fail("Accepted reader executed the saved stage"))
    monkeypatch.setattr("skillflow.common.structural_correction.ResponseChain.run",
        lambda *args, **kwargs: pytest.fail("Accepted reader replayed the response chain"))
    manifest = read(owner / "manifest.json")
    assert accepted_upstream._accepted_step(owner, kind="flow_document",
        config=manifest["config"], source=source) == expected
    assert inventory(owner) == before
