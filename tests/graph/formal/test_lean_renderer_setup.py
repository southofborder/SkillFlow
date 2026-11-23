"""Offline installer contract tests. Subprocess doubles never execute a native tool."""
import hashlib
import json
import os
from pathlib import Path

import pytest

from skillflow import lean_renderer as setup
from skillflow.graph.audit import controlled


@pytest.fixture
def installation(tmp_path, monkeypatch):
    root = tmp_path / "formal"
    for name, path in setup.source_files(setup.formal_root()).items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    tool_bin = tmp_path / "official lean" / "bin"
    tool_bin.mkdir(parents=True)
    for name in ("lean", "lake"):
        (tool_bin / (name + (".exe" if os.name == "nt" else ""))).touch()
    monkeypatch.setattr(setup, "formal_root", lambda: root)
    monkeypatch.setattr(setup, "_default_build", lambda source_id: tmp_path / "cache" / source_id)
    monkeypatch.delenv(setup.RENDERER_ENV, raising=False)
    calls = []

    def run(command, cwd, env):
        calls.append((command, cwd))
        assert Path(command[0]).parent == tool_bin
        if command[-1] == "--version":
            return ("Lean (version 4.33.1, test, Release)" if Path(command[0]).stem == "lean"
                    else "Lake version TEST (Lean version 4.33.1)")
        assert command[1:] == ["build", "skill_ir_retell"]
        assert env["PATH"].split(os.pathsep)[0] == str(tool_bin)
        assert not (cwd / ".lake").exists()
        assert setup._source_id(setup.source_files(cwd)) == setup._source_id(setup.source_files(root))
        binary = setup._product(cwd)
        binary.parent.mkdir(parents=True)
        binary.write_bytes(b"synthetic product")
        return ""

    monkeypatch.setattr(setup, "_run", run)
    monkeypatch.setattr(setup, "_verify", lambda binary: {"binary_sha256": setup.file_sha256(binary),
                                                          "graph_sha256": "0" * 64})
    return root, tool_bin, calls


def test_cache_is_per_source_reuses_checked_build_and_preserves_old_binary(installation):
    root, tool_bin, calls = installation
    legacy = setup._product(root)
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(b"historically selected")
    assert setup.renderer_path() == legacy
    first = setup.build_renderer(tool_bin)
    assert setup.build_renderer(tool_bin) == setup.renderer_path() == first
    assert len(calls) == 3
    config = root / "lakefile.toml"
    config.write_bytes(config.read_bytes() + b"\n")
    second = setup.build_renderer(tool_bin)
    assert second != first
    assert setup.renderer_path() == second
    assert first.is_file() and legacy.read_bytes() == b"historically selected"
    assert len(calls) == 6


def test_explicit_and_environment_selection_do_not_fall_back(installation, tmp_path, monkeypatch):
    _, tool_bin, _ = installation
    custom = setup.build_renderer(tool_bin, tmp_path / "custom path")
    assert custom.is_file()
    missing = tmp_path / "missing"
    monkeypatch.setenv(setup.RENDERER_ENV, str(missing))
    assert controlled._executable(custom) == custom
    with pytest.raises(controlled.ControlledVerificationError, match="missing.*python -m skillflow"):
        controlled._executable(None)
    monkeypatch.setenv(setup.RENDERER_ENV, str(custom))
    assert controlled._executable(None) == custom
    with pytest.raises(controlled.ControlledVerificationError, match="missing"):
        controlled._executable(missing)


@pytest.mark.parametrize("damage", ["binary", "receipt"])
def test_corrupted_cache_fails_closed_and_is_never_overwritten(installation, damage):
    _, tool_bin, calls = installation
    binary = setup.build_renderer(tool_bin)
    directory = next(path for path in binary.parents if (path / "build.json").exists())
    path = binary if damage == "binary" else directory / "build.json"
    path.write_text("corrupted", encoding="utf-8")
    with pytest.raises(ValueError, match="mismatched Lean build receipt"):
        setup.renderer_path()
    with pytest.raises(ValueError, match="mismatched Lean build receipt"):
        setup.build_renderer(tool_bin)
    assert path.read_text(encoding="utf-8") == "corrupted"
    assert len(calls) == 3


def test_unrelated_existing_directory_is_untouched(installation, tmp_path):
    _, tool_bin, calls = installation
    with pytest.raises(ValueError, match="build receipt"):
        setup.build_renderer(tool_bin, tmp_path)
    assert not calls


def test_setup_requires_installed_compiler_and_matching_lean_and_lake_versions(installation, monkeypatch, tmp_path):
    _, tool_bin, _ = installation
    with pytest.raises(ValueError, match="elan toolchain install leanprover/lean4:v4.33.1"):
        setup.build_renderer(tmp_path / "absent")
    monkeypatch.setattr(setup, "_run", lambda *args: "Lean (version 4.33.10, test, Release)")
    with pytest.raises(ValueError, match="Expected leanprover/lean4:v4.33.1"):
        setup.build_renderer(tool_bin)
    monkeypatch.setattr(setup, "_run", lambda *args: "Lean (version 4.33.1, test, Release)")
    with pytest.raises(ValueError, match="Expected Lake built for"):
        setup.build_renderer(tool_bin)


def test_elan_only_runs_installed_pinned_tools(monkeypatch):
    monkeypatch.setattr(setup.shutil, "which", lambda name: "/tools/elan" if name == "elan" else None)
    pin = "leanprover/lean4:v4.33.1"
    assert setup._tool_commands(None, pin, {}) == (["/tools/elan", "run", pin, "lean"],
                                                   ["/tools/elan", "run", pin, "lake"])


def test_failed_roundtrip_never_publishes_success(installation, monkeypatch, tmp_path):
    _, tool_bin, _ = installation
    def reject(binary):
        raise controlled.ControlledVerificationError("Lean rejected the round trip")
    monkeypatch.setattr(setup, "_verify", reject)
    directory = tmp_path / "publishing target"
    with pytest.raises(ValueError, match="round trip"):
        setup.build_renderer(tool_bin, directory)
    assert not directory.exists()
    unpublished, = tmp_path.glob("build-*")
    assert setup._product(unpublished).is_file()
    assert not (unpublished / "build.json").exists()


def test_policy_denial_is_distinct_from_missing_executable_and_build_failure(monkeypatch, tmp_path):
    def blocked(*args, **kwargs):
        error = OSError("access denied")
        error.winerror = 4551
        raise error
    monkeypatch.setattr(setup.subprocess, "run", blocked)
    with pytest.raises(ValueError, match="application control blocked .*lean.*WinError 4551"):
        setup._run(["lean", "--version"], tmp_path, {})
    with pytest.raises(controlled.ControlledVerificationError, match="application control blocked .*renderer"):
        controlled._lean(tmp_path / "renderer", {})
    assert "application control" not in setup.launch_error("renderer", FileNotFoundError("absent"))


def test_build_contains_only_declared_lean_inputs_and_records_verified_digest(installation, tmp_path):
    _, tool_bin, _ = installation
    directory = tmp_path / "custom"
    binary = setup.build_renderer(tool_bin, directory)
    receipt = json.loads((directory / "build.json").read_bytes())
    assert receipt["toolchain"] == "leanprover/lean4:v4.33.1"
    assert receipt["binary_sha256"] == hashlib.sha256(binary.read_bytes()).hexdigest()
    assert not (directory / "tools").exists()
