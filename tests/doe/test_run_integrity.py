"""Lifecycle coverage consolidated from the four retired DOE run wrappers.

The formal runner now owns interruption, identity, tamper detection and replay.
Algorithm coverage remains in Task, demand, sensitivity and slice unit tests.
"""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

from skillflow.common.recording import canonical_sha256, read_json, sha_file
from skillflow.doe import formal_runner as runner
from skillflow.doe.__main__ import main
from tests.doe.test_formal_runner import propagation_run, stable_test_implementation


@pytest.mark.parametrize("command", ["prepare", "task-prepare", "task-replay", "demand-prepare",
                                     "demand-replay", "sensitivity-prepare", "sensitivity-replay"])
def test_retired_commands_are_rejected(command, tmp_path):
    with pytest.raises(SystemExit) as error:
        main([command, "--run-dir", str(tmp_path / "absent")])
    assert error.value.code == 2
    assert not (tmp_path / "absent").exists()


@pytest.mark.parametrize("name", ["runner", "task_runner", "demand_runner", "sensitivity_runner"])
def test_retired_wrappers_have_no_importable_compatibility_module(name):
    assert importlib.util.find_spec("skillflow.doe." + name) is None


def test_formal_run_keeps_only_owned_results_and_relative_upstream(propagation_run, tmp_path):
    directory = tmp_path / "doe"
    runner.run_doe(propagation_run, run_dir=directory)
    manifest = read_json(directory / "manifest.json")
    assert manifest["upstream"]["path"] == "../propagation"
    assert set(manifest["artifacts"]) == runner._ARTIFACTS
    for path in ["audit/input.json", "audit/annotation.json", "audit/doe-input.json", "audit/demand"]:
        assert not (directory / path).exists()
    annotation = propagation_run.parent / "annotation"
    assert (annotation / "inputs/package/SKILL.md").is_file()
    assert not (annotation / "inputs/source.json").exists()
    assert not (annotation / "inputs/material.json").exists()
    assert not list(propagation_run.rglob("material.json"))
    assert not list(directory.rglob("material.json"))
    assert all(set(row) == {"instruction_id", "scope_path", "declaration_index"}
               for row in read_json(directory / "audit/index.json")["declarations"].values())
    # Evidence belongs to the selected raw annotation and is rebuilt for the
    # report without becoming another persisted declaration copy.
    loaded = runner.load_doe_run(directory)
    assert all("declaration" in row for row in loaded["review"].index_dict()["declarations"].values())
    assert runner.replay_doe(directory)["status"] == "matched"
    assert len(list(directory.rglob("doe-result.json"))) == 1


def test_entire_tree_can_move_and_missing_upstream_never_falls_back(propagation_run, tmp_path):
    directory = tmp_path / "doe"
    runner.run_doe(propagation_run, run_dir=directory)
    relocated = tmp_path / "relocated"
    relocated.mkdir()
    for name in ("annotation-task", "annotation", "propagation", "doe"):
        shutil.copytree(tmp_path / name, relocated / name)
    assert runner.load_doe_run(relocated / "doe")["result"] == runner.load_doe_run(directory)["result"]
    assert runner.replay_doe(relocated / "doe")["status"] == "matched"
    # Rename the referenced upstream; an identically named old tree still exists.
    (relocated / "propagation").rename(relocated / "unreferenced")
    with pytest.raises((ValueError, FileNotFoundError)):
        runner.load_doe_run(relocated / "doe")


def test_resealed_manifest_cannot_hide_status_or_upstream_changes(propagation_run, tmp_path):
    directory = tmp_path / "doe"
    runner.run_doe(propagation_run, run_dir=directory)
    path = directory / "manifest.json"
    original = read_json(path)
    for update in ({"status": "semantically_proven"}, {"upstream_identity": {}}):
        changed = {**deepcopy(original), **update}
        changed["manifest_sha256"] = canonical_sha256({k:v for k,v in changed.items() if k != "manifest_sha256"})
        path.write_text(json.dumps(changed), encoding="utf-8")
        with pytest.raises(ValueError):
            runner.load_doe_run(directory)
    path.write_text(json.dumps(original), encoding="utf-8")


def test_occupied_directory_is_preserved(propagation_run, tmp_path):
    directory = tmp_path / "occupied"
    directory.mkdir()
    keep = directory / "keep.txt"
    keep.write_text("Keep this unrelated material.", encoding="utf-8")
    before = sha_file(keep)
    with pytest.raises(ValueError):
        runner.run_doe(propagation_run, run_dir=directory)
    assert sha_file(keep) == before


def test_resealed_manifest_preserves_boolean_and_number_types(propagation_run, tmp_path):
    directory = tmp_path / "doe"
    runner.run_doe(propagation_run, run_dir=directory)
    path = directory / "manifest.json"
    original = read_json(path)
    for section, field, replacement in (
        ("policy", "model_calls", False),
        ("policy", "global_minimality_proof", 0),
        ("metadata", "model_calls", False),
    ):
        changed = deepcopy(original)
        changed[section][field] = replacement
        changed["manifest_sha256"] = canonical_sha256({
            key: value for key, value in changed.items() if key != "manifest_sha256"})
        path.write_text(json.dumps(changed), encoding="utf-8")
        with pytest.raises(ValueError, match="policy|metadata"):
            runner.load_doe_run(directory)
    path.write_text(json.dumps(original), encoding="utf-8")
    assert runner.load_doe_run(directory)["manifest"] == original


def test_formal_entry_checks_supplied_link_before_resolving(tmp_path, monkeypatch):
    # Simulate only the OS link observation so the entry check is exercised even
    # on Windows accounts without symlink creation privileges.
    target, alias = tmp_path / "actual", tmp_path / "alias"
    target.mkdir()
    alias.mkdir()
    original_is_symlink, original_resolve = Path.is_symlink, Path.resolve
    monkeypatch.setattr(Path, "is_symlink", lambda path:
        path == alias or original_is_symlink(path))
    monkeypatch.setattr(Path, "resolve", lambda path, *args, **kwargs:
        target if path == alias else original_resolve(path, *args, **kwargs))
    monkeypatch.setattr(runner, "_model_bundle", lambda *_:
        pytest.fail("The supplied link was resolved before the entry check"))
    with pytest.raises(ValueError, match="links|reparse"):
        runner.run_doe(alias, run_dir=tmp_path / "doe")


def test_resealed_declaration_index_rejects_boolean_position(propagation_run, tmp_path):
    directory = tmp_path / "doe"
    runner.run_doe(propagation_run, run_dir=directory)
    index_path = directory / "audit/index.json"
    index = read_json(index_path)
    next(iter(index["declarations"].values()))["declaration_index"] = False
    index_path.write_text(json.dumps(index), encoding="utf-8")
    manifest_path = directory / "manifest.json"
    manifest = read_json(manifest_path)
    manifest["index_sha256"] = canonical_sha256(index)
    manifest["artifacts"]["audit/index.json"] = sha_file(index_path)
    manifest["manifest_sha256"] = canonical_sha256({
        key: value for key, value in manifest.items() if key != "manifest_sha256"})
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="declaration index"):
        runner.load_doe_run(directory)


def test_interrupted_marker_rejects_same_valued_float_version(propagation_run, tmp_path, monkeypatch):
    directory = tmp_path / "doe"
    with monkeypatch.context() as patch:
        def interrupt(*_args):
            raise KeyboardInterrupt()
        patch.setattr(runner, "prepare_joint_sensitivity_review", interrupt)
        with pytest.raises(KeyboardInterrupt):
            runner.run_doe(propagation_run, run_dir=directory)
    path = directory / runner._MARKER
    marker = read_json(path)
    marker["schema_version"] = float(marker["schema_version"])
    marker["manifest_sha256"] = canonical_sha256({
        key: value for key, value in marker.items() if key != "manifest_sha256"})
    path.write_text(json.dumps(marker), encoding="utf-8")
    with pytest.raises(ValueError, match="Interrupted formal DOE input"):
        runner.run_doe(propagation_run, run_dir=directory)
    assert not (directory / "manifest.json").exists()
