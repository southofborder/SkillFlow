"""Completed annotation loading is read-only and independent of producer code hash."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from skillflow.propagation.annotation import load_annotation_run
from skillflow.propagation.annotation import runner
from skillflow.propagation.annotation import loading
from tests.propagation.annotation.helpers import FakeClient
from tests.propagation.annotation.test_security_runner import setup_run


def _bytes(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes()
            for p in directory.rglob("*") if p.is_file()}


def _completed(tmp_path, client=None):
    directory, source, analysis = setup_run(tmp_path)
    result = runner.run_annotation(directory, client=client or FakeClient())
    assert result["status"] in {"complete"}
    return directory, source, analysis


def test_readonly_load_keeps_old_producer_and_strict_resume_boundary(tmp_path, monkeypatch):
    directory, _, _ = _completed(tmp_path)
    (directory / ".runner.lock").unlink()
    before = _bytes(directory)
    monkeypatch.setattr(runner, "implementation_provenance", lambda: {"new": "reviewer added"})
    loaded = load_annotation_run(directory)
    assert loaded["upstream_identity"]["implementation"] == loaded["manifest"]["implementation"]
    assert loaded["raw_annotation"] == json.loads((directory / "audit/raw-annotation.json").read_text(encoding="utf-8"))
    assert loaded["result"]["request_validation"] == loaded["request_validation"]
    assert before == _bytes(directory)
    # Existing execution/replay identity checks have not gained an opt-out.
    with pytest.raises(runner.RunIdentityError, match="Implementation identity changed"):
        runner.run_annotation(directory)
    with pytest.raises(runner.RunIdentityError, match="Implementation identity changed"):
        runner.replay_run(directory)


def test_relocated_run_needs_no_original_source_or_reports(tmp_path):
    directory, source, analysis = _completed(tmp_path)
    copied = tmp_path / "another-name"
    shutil.copytree(directory, copied)
    shutil.rmtree(source)
    analysis.unlink()
    (copied / "report.md").unlink()
    (copied / ".runner.lock").unlink()
    before = _bytes(copied)
    assert load_annotation_run(copied)["upstream_identity"] == load_annotation_run(directory)["upstream_identity"]
    assert before == _bytes(copied)


def test_partial_order_is_loadable_without_generic_unresolved(tmp_path):
    class Partial(FakeClient):
        def complete(self, prompt):
            response = super().complete(prompt)
            response["transfer_specs"]["ir_filter"]["order"] = "partial"
            return response
    directory, _, _ = _completed(tmp_path, Partial())
    loaded = load_annotation_run(directory)
    assert loaded["result"]["status"] == "complete"
    assert loaded["compiled_annotation"]["transfer_specs"]["ir_filter"]["order"] == "partial"
    assert "unresolved" not in loaded["compiled_annotation"]


@pytest.mark.parametrize("name", [
    "inputs/package/SKILL.md", "inputs/material.json", "inputs/cfg.json", "inputs/prompt.txt",
    "audit/raw-annotation.json", "audit/compiled-response.json", "audit/compilation-map.json",
    "audit/location-evidences.json", "profiles.json", "locations.json", "transfer-specs.json", "sink-boundaries.json",
    "inputs/repair-context.json", "validation.json", "result.json", "manifest.json",
    "calls/annotation/a001/call.json", "calls/annotation/a001/transport.json",
    "calls/annotation/a001/response.json", "calls/annotation/a001/prompt.txt",
])
def test_tampered_critical_file_is_rejected_without_writing(tmp_path, name):
    directory, _, _ = _completed(tmp_path)
    path = directory / name
    path.write_text("{}" if name.endswith(".json") else "changed", encoding="utf-8")
    before = _bytes(directory)
    with pytest.raises(runner.RunIdentityError):
        load_annotation_run(directory)
    assert before == _bytes(directory)


@pytest.mark.parametrize("field,value", [("status", "interrupted"), ("status", "invalid_response"),
                                         ("status", "incomplete"), ("schema_version", 7)])
def test_invalid_status_or_version_cannot_masquerade_as_completed(tmp_path, field, value):
    directory, _, _ = _completed(tmp_path)
    path = directory / "result.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    result[field] = value
    path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(runner.RunIdentityError):
        load_annotation_run(directory)


def test_resealed_changed_request_config_is_still_rejected(tmp_path):
    directory, _, _ = _completed(tmp_path)
    path = directory / "manifest.json"
    manifest = runner._unseal(json.loads(path.read_text(encoding="utf-8")))
    manifest["config"]["model"] = "tampered-model"
    path.write_text(json.dumps(runner._seal(manifest)), encoding="utf-8")
    with pytest.raises(runner.RunIdentityError, match="request identity"):
        load_annotation_run(directory)


def test_rehashed_compilation_cannot_override_accepted_response(tmp_path):
    directory, _, _ = _completed(tmp_path)
    path = directory / "audit/raw-annotation.json"
    annotation = json.loads(path.read_text(encoding="utf-8"))
    annotation["profiles"]["ir_read"]["evidences"][0]["reason"] = "改写理由"
    path.write_text(json.dumps(annotation, ensure_ascii=False), encoding="utf-8")
    result_path = directory / "result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["compilation"]["raw_sha256"] = runner.canonical_sha256(annotation)
    result_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(runner.RunIdentityError, match="compilation identity"):
        load_annotation_run(directory)


def test_read_rejects_mid_verification_change(tmp_path, monkeypatch):
    directory, _, _ = _completed(tmp_path)
    original = loading.compile_response
    def changing(*args):
        compiled = original(*args)
        path = directory / "profiles.json"
        path.write_bytes(path.read_bytes() + b"\n")
        return compiled
    monkeypatch.setattr(loading, "compile_response", changing)
    with pytest.raises(runner.RunIdentityError, match="changed during"):
        load_annotation_run(directory)


def test_historical_three_v8_annotations_rejected_without_changes():
    root = project_root() / "experiments/propagation/runs/processing-v1-20260928-204710/cases"
    if not root.is_dir():
        pytest.skip("historical local experiment is not present in this checkout")
    for case in ("001", "010", "013"):
        directory = root / case / "annotation"
        before = _bytes(directory)
        with pytest.raises(runner.RunIdentityError, match="Unsupported"):
            load_annotation_run(directory)
        assert before == _bytes(directory)
