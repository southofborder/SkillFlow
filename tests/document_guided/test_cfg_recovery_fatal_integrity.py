"""Fatal recovery rederives meaning after all outer digest references are rebound."""
from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256, read_json
from skillflow.document_guided import runner
from skillflow.document_guided.fatal_frontier import PATH
from skillflow.document_guided.online import file_reference
from tests.document_guided.test_cfg_recovery_peer import run_fatal
from tests.document_guided.test_parallel_runner import freeze_producer


@pytest.fixture(autouse=True)
def offline_producer(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


def rebind_recovery(run, result, relative, altered):
    """Bypass only the outer digest mismatch, preserving original stage calls."""
    runner.WRITER.json(run / relative, altered)
    frontier = read_json(run / PATH)
    frontier["recovery"][relative] = file_reference(run, run / relative)
    runner.WRITER.json(run / PATH, frontier)
    rebound = deepcopy(result)
    rebound["fatal_frontier"] = file_reference(run, run / PATH)
    runner.WRITER.json(run / "result.json", rebound)
    assert read_json(run / PATH)["recovery"][relative] == file_reference(run, run / relative)
    assert read_json(run / "result.json")["fatal_frontier"] == file_reference(run, run / PATH)


@pytest.mark.parametrize("artifact,expected", [
    ("audit/shared-repair-decision.json", "shared-repair admission differs from verified"),
    ("audit/failed-stages/graph.json", "rejected-stage material differs from verified original calls"),
    ("audit/failed-stages/unobserved.json", "contains unverified recovery evidence"),
])
def test_rehashed_recovery_still_requires_semantic_reconstruction(tmp_path, monkeypatch, artifact, expected):
    # No revision graph owner exists, so its dependency hash cannot accidentally
    # supply the only rejection of altered original graph evidence.
    harness, result = run_fatal(tmp_path, monkeypatch, "task_before_graph_owner")
    run = harness.directory
    original_calls = {p.relative_to(run).as_posix(): p.read_bytes()
                      for p in run.rglob("*") if p.is_file() and "calls" in p.parts}
    if artifact.endswith("shared-repair-decision.json"):
        altered = read_json(run / artifact)
        assert altered["eligible"] and altered["mode"] == "missing_cfg_slots"
        altered.update(eligible=False, mode="not_admitted", domains=[])
    else:
        altered = read_json(run / "audit/failed-stages/graph.json")
        if artifact.endswith("graph.json"):
            material = altered["material"]
            assert "candidate" in material
            material["candidate"]["entry"] = "forged_rejected_entry"
            altered["material_sha256"] = canonical_sha256(material)
    rebind_recovery(run, result, artifact, altered)
    calls = len(harness.calls)
    with pytest.raises(ValueError, match=expected):
        runner.replay(run)
    assert len(harness.calls) == calls
    assert original_calls == {p.relative_to(run).as_posix(): p.read_bytes()
                              for p in run.rglob("*") if p.is_file() and "calls" in p.parts}
    assert not (run / "selection.json").exists()
    assert not (run / "propagation").exists() and not (run / "doe").exists()
