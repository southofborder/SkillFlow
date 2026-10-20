import hashlib
import json
from pathlib import Path
import stat
import subprocess
from types import SimpleNamespace

import pytest

from tools.cloud import materials


def _fixture(tmp_path):
    root = tmp_path / "checkout"
    root.mkdir()
    (root / "inputs").mkdir()
    (root / "inputs" / "raw.txt").write_bytes(b"source\r\ncontent\n")
    raw = (root / "inputs" / "raw.txt").read_bytes()
    manifest = {
        "schema_version": materials.SCHEMA, "roots": ["inputs"],
        "files": [{"path": "inputs/raw.txt", "bytes": len(raw),
                   "sha256": hashlib.sha256(raw).hexdigest()}],
    }
    path = root / "manifest.json"
    path.write_text(json.dumps(manifest))
    return root, path, manifest


def test_exact_bytes_verify_and_extra_files_do_not_change_scope(tmp_path):
    root, path, _ = _fixture(tmp_path)
    (root / "inputs" / "extra.txt").write_text("Not part of the declared seal.")
    assert materials.verify_manifest(root, path)["status"] == "passed"
    assert materials.verify_manifest(root, path)["file_count"] == 1
    (root / "inputs" / "raw.txt").write_bytes(b"source\ncontent\n")
    assert materials.verify_manifest(root, path)["errors"] == [
        {"path": "inputs/raw.txt", "error": "content_mismatch"}]


def test_missing_file_is_not_restored(tmp_path):
    root, path, _ = _fixture(tmp_path)
    (root / "inputs" / "raw.txt").unlink()
    assert materials.verify_manifest(root, path)["errors"] == [
        {"path": "inputs/raw.txt", "error": "missing_file"}]
    assert not (root / "inputs" / "raw.txt").exists()


@pytest.mark.parametrize("value", ["../secret", "/absolute", "C:/absolute", "a\\b", "a//b", "a/./b", ""])
def test_unsafe_paths_are_rejected(tmp_path, value):
    root, path, manifest = _fixture(tmp_path)
    manifest["files"][0]["path"] = value
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        materials.verify_manifest(root, path)


@pytest.mark.parametrize("names", [
    ["inputs/raw.txt", "inputs/raw.txt"],
    ["inputs/raw.txt", "inputs/RAW.txt"],
    ["inputs/raw.txt", "Inputs/other.txt"],
])
def test_duplicate_and_case_colliding_paths_are_rejected(tmp_path, names):
    root, path, manifest = _fixture(tmp_path)
    manifest["files"] = [{**manifest["files"][0], "path": name} for name in names]
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        materials.verify_manifest(root, path)


def test_symlink_is_rejected_even_if_its_bytes_match(tmp_path):
    root, path, _ = _fixture(tmp_path)
    original = root / "inputs" / "raw.txt"
    target = root / "actual.txt"
    original.replace(target)
    try:
        original.symlink_to(target)
    except OSError:
        pytest.skip("This host does not allow creating test symlinks")
    result = materials.verify_manifest(root, path)
    assert result["status"] == "failed"
    assert "links and reparse points" in result["errors"][0]["error"]


def test_link_detection_is_exercised_without_host_link_privilege(tmp_path, monkeypatch):
    root, path, _ = _fixture(tmp_path)
    original = Path.lstat

    def link_stat(self, *args, **kwargs):
        if self == root / "inputs" / "raw.txt":
            return SimpleNamespace(st_mode=stat.S_IFLNK)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", link_stat)
    result = materials.verify_manifest(root, path)
    assert result["status"] == "failed"
    assert "links and reparse points" in result["errors"][0]["error"]


def test_creation_selects_indexed_files_and_keeps_frozen_bytecode(tmp_path, monkeypatch):
    root = tmp_path / "checkout"
    evidence = root / "frozen" / "__pycache__" / "source.pyc"
    evidence.parent.mkdir(parents=True)
    evidence.write_bytes(b"\x00frozen evidence")
    (root / "frozen" / ".runner.lock").write_text("Local operational lock, not staged.")
    calls = []

    def indexed(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, b"frozen/__pycache__/source.pyc\x00", b"")

    monkeypatch.setattr(materials.subprocess, "run", indexed)
    path = root / "manifest.json"
    result = materials.create_manifest(root, ["frozen"], path)
    assert [item["path"] for item in result["files"]] == ["frozen/__pycache__/source.pyc"]
    assert calls == [["git", "-C", str(root.resolve()), "ls-files", "-z", "--cached", "--", "frozen"]]
    assert materials.verify_manifest(root, path)["status"] == "passed"
    with pytest.raises(FileExistsError):
        materials.create_manifest(root, ["frozen"], path)


def test_bad_manifest_types_and_duplicate_keys_are_rejected(tmp_path):
    root, path, manifest = _fixture(tmp_path)
    manifest["files"][0]["bytes"] = True
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="byte count"):
        materials.verify_manifest(root, path)
    path.write_text('{"schema_version":"a","schema_version":"b"}')
    with pytest.raises(ValueError, match="Duplicate manifest key"):
        materials.verify_manifest(root, path)


def test_manifest_entry_outside_declared_roots_is_rejected(tmp_path):
    root, path, manifest = _fixture(tmp_path)
    manifest["roots"] = ["somewhere-else"]
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="outside all declared roots"):
        materials.verify_manifest(root, path)


def test_create_does_not_write_outside_project(tmp_path):
    root, _, _ = _fixture(tmp_path)
    output = tmp_path / "outside.json"
    with pytest.raises(ValueError, match="within the project"):
        materials.create_manifest(root, ["inputs"], output)
    assert not output.exists()
