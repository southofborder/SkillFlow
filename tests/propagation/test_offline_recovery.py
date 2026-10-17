"""Formal recovery keeps upstream ownership; no historical report-only runner."""
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.paths import project_root
from skillflow.common.recording import read_json, sha_file
from tests.propagation.annotation.helpers import authored_prepare_run as prepare_run
from skillflow.propagation.annotation.runner import run_annotation
from skillflow.propagation.runner import load_propagation_materials, replay_propagation, run_propagation
from tests.propagation.annotation.helpers import FakeClient
from tests.propagation.test_runner import annotation_run, components


def test_old_report_recovery_and_doe_comparison_wrappers_are_retired():
    for name in ("recover_reports_offline.py", "doe_changes.py"):
        assert not (project_root() / "tools/propagation" / name).exists()


@pytest.fixture(params=["ordinary", "normalized"])
def accepted_run(annotation_run, tmp_path, request):
    if request.param == "ordinary":
        return annotation_run

    class TrailingBraceClient(FakeClient):
        def complete(self, prompt):
            return json.dumps(super().complete(prompt), ensure_ascii=False) + "}\n"

    directory = tmp_path / "normalized-annotation"
    analysis = tmp_path / "normalized-analysis.json"
    ArtifactWriter(()).json(analysis, {"cfg": read_json(annotation_run / "inputs/cfg.json")})
    prepare_run(annotation_run / "inputs/package", analysis, run_dir=directory)
    client = TrailingBraceClient()
    result = run_annotation(directory, client=client)
    assert result["status"] == "complete" and len(client.prompts) == 1
    assert (directory / "calls/annotation/a001/normalization.json").is_file()
    return directory


def test_report_interruption_resumes_same_preparation_without_model_or_input_copies(accepted_run, tmp_path, monkeypatch):
    import skillflow.propagation.runner as runner
    directory = tmp_path / "propagation"
    before = {str(p.relative_to(accepted_run)): sha_file(p) for p in accepted_run.rglob("*") if p.is_file()}
    with monkeypatch.context() as scoped:
        scoped.setattr(runner, "write_reports", lambda *a, **kw: (_ for _ in ()).throw(KeyboardInterrupt()))
        with pytest.raises(KeyboardInterrupt):
            run_propagation(accepted_run, run_dir=directory)
    assert (directory / "preparation.json").is_file()
    assert not (directory / "manifest.json").exists()
    facts = run_propagation(accepted_run, run_dir=directory)
    assert facts.status == "complete"
    assert not (directory / "preparation.json").exists()
    assert not (directory / "audit/accepted-call").exists()
    assert not (directory / "audit/material.json").exists()
    assert components(replay_propagation(directory)) == components(facts)
    assert read_json(directory / "replay/summary.json")["model_calls"] == 0
    assert before == {str(p.relative_to(accepted_run)): sha_file(p) for p in accepted_run.rglob("*") if p.is_file()}


def test_partial_artifact_cannot_be_silently_overwritten(accepted_run, tmp_path, monkeypatch):
    import skillflow.propagation.runner as runner
    directory = tmp_path / "partial"
    with monkeypatch.context() as scoped:
        scoped.setattr(runner, "write_reports", lambda *a, **kw: (_ for _ in ()).throw(OSError("report unavailable")))
        with pytest.raises(OSError):
            run_propagation(accepted_run, run_dir=directory)
    ArtifactWriter(()).json(directory / "data.json", [])
    with pytest.raises(ValueError, match="Interrupted propagation artifact differs"):
        run_propagation(accepted_run, run_dir=directory)
    assert not (directory / "manifest.json").exists()


@pytest.mark.parametrize("relative", ["calls/annotation/a001/response.json", "calls/annotation/a001/call.json",
    "calls/annotation/a001/validation.json", "audit/raw-annotation.json", "audit/compiled-response.json"])
def test_upstream_response_chain_tampering_prevents_recovery(accepted_run, tmp_path, relative):
    directory = tmp_path / "checked"
    run_propagation(accepted_run, run_dir=directory)
    path = accepted_run / relative
    assert path.is_file()
    value = read_json(path)
    if isinstance(value, str):
        value += " altered candidate"
    else:
        value["unexpected_edit"] = True
    ArtifactWriter(()).json(path, value)
    with pytest.raises(ValueError):
        load_propagation_materials(directory)


def test_normalization_receipt_is_owned_and_checked_upstream(accepted_run, tmp_path):
    receipt = accepted_run / "calls/annotation/a001/normalization.json"
    if not receipt.exists():
        return
    directory = tmp_path / "normalized"
    run_propagation(accepted_run, run_dir=directory)
    value = read_json(receipt)
    value["raw_sha256"] = "0" * 64
    ArtifactWriter(()).json(receipt, value)
    with pytest.raises(ValueError):
        replay_propagation(directory)
