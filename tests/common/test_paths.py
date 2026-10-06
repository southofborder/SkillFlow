import hashlib
import json
from pathlib import Path

import pytest

from skillflow.common import paths


def project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    (root / "pyproject.toml").write_text('[project]\nname = "skillflow"\n', encoding="utf-8")
    monkeypatch.setattr(paths, "project_root", lambda: root)
    return root


def ledger(root, files, directories=()):
    directory = root / "experiments/migrations/layout-v1-test"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "manifest.json"
    path.write_text(json.dumps({"files": files, "directories": list(directories)}), encoding="utf-8")
    return path


def file_entry(root, old="packages/skill-ir/experiments/a/source.json", target="experiments/a/source.json"):
    result = root / target
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_bytes(b"frozen input")
    return {
        "old_relative": old, "old_absolute": str(root / old), "new_relative": target,
        "sha256": hashlib.sha256(result.read_bytes()).hexdigest(), "role": "history",
    }


def test_root_is_lazy_and_independent_of_nesting(tmp_path):
    root = tmp_path / "arbitrary"
    nested = root / "one/two/three"
    nested.mkdir(parents=True)
    (root / "pyproject.toml").write_text('[project]\nname = "skillflow"\n', encoding="utf-8")
    (root / "one/pyproject.toml").write_text('[project]\nname = "unrelated"\n', encoding="utf-8")
    assert paths.project_root(nested) == root


def test_exact_historical_relative_and_absolute_addresses(tmp_path, monkeypatch):
    root = project(tmp_path, monkeypatch)
    entry = file_entry(root)
    ledger(root, [entry])
    for address in (entry["old_relative"], entry["old_absolute"]):
        assert paths.resolve_material_path(address, expected_sha256=entry["sha256"]) == root / entry["new_relative"]
    with pytest.raises(FileNotFoundError, match="exact historical"):
        paths.resolve_material_path("packages/skill-ir/experiments/a/unknown.json")


def test_mapped_file_always_checks_digest_even_with_cached_ledger(tmp_path, monkeypatch):
    root = project(tmp_path, monkeypatch)
    entry = file_entry(root)
    ledger(root, [entry])
    paths.resolve_material_path(entry["old_relative"])
    (root / entry["new_relative"]).write_bytes(b"changed")
    with pytest.raises(ValueError, match="digest mismatch"):
        paths.resolve_material_path(entry["old_relative"])


def test_directory_checks_sealed_file_members_not_prefix_guessing(tmp_path, monkeypatch):
    root = project(tmp_path, monkeypatch)
    entry = file_entry(root)
    directory = {
        "old_relative": "packages/skill-ir/experiments/a",
        "old_absolute": str(root / "packages/skill-ir/experiments/a"), "new_relative": "experiments/a",
    }
    ledger(root, [entry], [directory])
    assert paths.resolve_material_path(directory["old_relative"]) == root / "experiments/a"
    (root / entry["new_relative"]).write_bytes(b"changed")
    with pytest.raises(ValueError, match="digest mismatch"):
        paths.resolve_material_path(directory["old_relative"])


def test_historical_target_cannot_leave_repository(tmp_path, monkeypatch):
    root = project(tmp_path, monkeypatch)
    entry = file_entry(root)
    entry["new_relative"] = "../outside.json"
    ledger(root, [entry])
    with pytest.raises(ValueError, match="safe repository"):
        paths.resolve_material_path(entry["old_relative"])


def test_ledger_changes_invalidate_address_cache(tmp_path, monkeypatch):
    root = project(tmp_path, monkeypatch)
    entry = file_entry(root)
    path = ledger(root, [entry])
    paths.resolve_material_path(entry["old_relative"])
    entry["sha256"] = "0" * 64
    path.write_text(json.dumps({"files": [entry], "directories": [], "changed": True}), encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        paths.resolve_material_path(entry["old_relative"])


def test_explicit_external_input_does_not_require_checkout(tmp_path, monkeypatch):
    external = tmp_path / "external.json"
    external.write_bytes(b"explicit")
    def missing():
        raise FileNotFoundError("no checkout")
    monkeypatch.setattr(paths, "project_root", missing)
    assert paths.resolve_material_path(external) == external
    assert paths.resolve_material_path(external.name, base=tmp_path) == external


def test_common_does_not_import_analysis_stages():
    import ast
    import skillflow.common.source_evidence as source
    for path in Path(source.__file__).parent.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            modules = [node.module or ""] if isinstance(node, ast.ImportFrom) else [
                alias.name for alias in node.names
            ] if isinstance(node, ast.Import) else []
            assert not any(module.startswith(("skillflow.graph", "skillflow.propagation")) for module in modules), path
