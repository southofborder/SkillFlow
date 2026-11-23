"""Exercise the full-run controller offline with isolated pins and temporary inputs."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import subprocess

import pytest

from skillflow.common.inputs.snapshot import inspect_input


SCRIPT = Path(__file__).resolve().parents[2] / "output/verification/online-ga4-action-alignment-20261123/controller.py"


@pytest.fixture
def controller():
    spec = importlib.util.spec_from_file_location("full_ga4_controller", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepared(controller, tmp_path, monkeypatch):
    c = controller
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("# Small fixture\nReturn a value.\n", encoding="utf-8")
    for i in range(15):
        (source / f"part{i}.txt").write_text(str(i), encoding="utf-8")
    monkeypatch.setattr(c, "SOURCE", inspect_input(source)[1]["source_sha256"])
    monkeypatch.setattr(c, "RUNS", tmp_path / "runs")
    monkeypatch.setattr(c, "VERIFY", tmp_path / "verification")
    c.VERIFY.mkdir()
    # Git verification has its own local-repository regression below.
    monkeypatch.setattr(c, "verify_sync", lambda *args: None)
    cli, renderer = tmp_path / "cli", tmp_path / "renderer"
    cli.write_bytes(b"offline CLI fixture")
    renderer.write_bytes(b"offline renderer fixture")
    acceptance, sync = tmp_path / "acceptance.json", tmp_path / "sync.json"
    c.write(acceptance, {"status": "passed"})
    c.write(sync, {"commit": "abc", "tree": "def"})
    args = SimpleNamespace(source=source, suffix="20260101-181920", owner="/root", cli=cli, renderer=renderer,
                           acceptance=acceptance, sync=sync)
    receipt = c.prepare(args)
    return Path(receipt["run_directory"]), args


def test_full_experiment_allows_each_fresh_stage_and_owns_only_one_replay(controller, tmp_path, monkeypatch):
    c = controller
    run, args = prepared(c, tmp_path, monkeypatch)
    seen = []
    def analyze(directory, *, client_factory, renderer, progress):
        for name in c.NORMAL:
            client = client_factory(name, directory / name)
            assert client.timeout == 2700 and client.retries == 2
            seen.append(name)
        with pytest.raises(ValueError, match="Unexpected"):
            client_factory("probe", directory)
        result = {"status": "partial", "counts": {"logical_calls": 7}}
        c.write(directory / "result.json", result)
        return result
    def replay(directory, *, renderer):
        seen.append("replay")
        return c.read(directory / "result.json")
    monkeypatch.setattr(c.runner, "run", analyze)
    monkeypatch.setattr(c.runner, "replay", replay)
    result = c.run_once()
    assert seen == [*c.NORMAL, "replay"]
    assert result["replay"]["status"] == "matched" and result["replay"]["new_native_starts"] == 0
    assert not (run / "accepted-upstream.json").exists()
    with pytest.raises(ValueError, match="already started"):
        c.run_once()
    with pytest.raises(ValueError, match="already exists"):
        c.prepare(args)


@pytest.mark.parametrize("damage", ["cli", "renderer", "raw_source", "prior_stage"])
def test_runtime_or_inherited_material_change_prevents_native_start(controller, tmp_path, monkeypatch, damage):
    c = controller
    run, args = prepared(c, tmp_path, monkeypatch)
    if damage in {"cli", "renderer"}:
        getattr(args, damage).write_bytes(b"changed")
    elif damage == "raw_source":
        (run / "source/inputs/package/part7.txt").write_text("changed", encoding="utf-8")
    else:
        c.write(run / "accepted-upstream.json", {})
    with pytest.raises(ValueError):
        c.run_once()
    assert not (run / "controller-started.json").exists()


def test_git_receipt_requires_the_synced_tree_and_every_runtime_file(controller, tmp_path, monkeypatch):
    c = controller
    monkeypatch.setattr(c, "PROJECT", tmp_path)
    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args], text=True).strip()
    git("init", "-q")
    helper = tmp_path / "helper.py"
    helper.write_text("frozen = True\n", encoding="utf-8")
    git("add", "helper.py")
    git("-c", "user.name=test", "-c", "user.email=test@example.org", "commit", "-qm", "fixture")
    acceptance, sync = tmp_path / "acceptance.json", tmp_path / "sync.json"
    impl = {"files": {}, "sha256": "pinned"}
    c.write(acceptance, {"status": "passed", "implementation_sha256": "pinned"})
    c.write(sync, {"status": "pushed_verified", "local_and_remote_tree_equal": True, "implementation_sha256": "pinned",
                   "commit": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}")})
    c.verify_sync(acceptance, sync, impl, [helper])
    with pytest.raises(ValueError, match="missing from synced"):
        c.verify_sync(acceptance, sync, impl, [helper, tmp_path / "absent.py"])
    helper.write_text("frozen = False\n", encoding="utf-8")
    with pytest.raises(subprocess.CalledProcessError):
        c.verify_sync(acceptance, sync, impl, [helper])
