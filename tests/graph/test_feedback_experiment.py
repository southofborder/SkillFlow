"""F01 wrapper keeps new feedback runs separate from historical identities."""

from skillflow.common.paths import project_root, resolve_material_path

import importlib.util
from pathlib import Path

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import read_json
from skillflow.graph.semantic_contract import contract_binding


@pytest.fixture
def driver(monkeypatch):
    script = project_root() / "tools/graph/feedback/run_f01.py"
    spec = importlib.util.spec_from_file_location("test_feedback_f01_driver", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "prepare_cases", lambda: {
        "provenance": {"source_root": "fixture"},
        "source": {"source_sha256": "fixture-source"}, "cases": [],
    })
    return module


def test_f01_manifest_binds_v5_and_current_interpretation_contract(driver, tmp_path):
    writer = ArtifactWriter(())
    manifest = driver._verified_manifest(tmp_path, {"model": "offline-fixture"}, writer)
    assert manifest["schema_version"] == 5
    assert manifest["identity"] == "skill-ir-semantic-feedback-f01-v5"
    assert all(manifest[key] == value for key, value in contract_binding().items())
    assert driver._verified_manifest(tmp_path, manifest["config"], writer) == manifest
    assert read_json(tmp_path / "manifest.json") == manifest


@pytest.mark.parametrize("version", [1, 2, 3])
def test_f01_wrapper_refuses_historical_records_without_migration(driver, tmp_path, version):
    writer = ArtifactWriter(())
    old = {"schema_version": version, "identity": f"skill-ir-semantic-feedback-f01-v{version}"}
    writer.json(tmp_path / "manifest.json", old)
    with pytest.raises(ValueError, match="Unsupported"):
        driver._verified_manifest(tmp_path, {}, writer)
    with pytest.raises(ValueError, match="Unsupported"):
        driver.execute(tmp_path, replay=True)
    assert read_json(tmp_path / "manifest.json") == old


def test_f01_wrapper_refuses_changed_contract_identity(driver, tmp_path, monkeypatch):
    writer = ArtifactWriter(())
    original = driver._verified_manifest(tmp_path, {}, writer)
    monkeypatch.setattr(driver, "contract_binding", lambda: {
        **contract_binding(), "contract_sha256": "modified-contract",
    })
    with pytest.raises(ValueError, match="identity mismatch"):
        driver._verified_manifest(tmp_path, {}, writer)
    assert read_json(tmp_path / "manifest.json") == original
