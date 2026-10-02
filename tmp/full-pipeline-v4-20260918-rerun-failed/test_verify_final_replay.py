"""Focused synthetic acceptance tests; no real run or network is accessed."""
import importlib.util
import json
from pathlib import Path
import socket

import pytest

SPEC = importlib.util.spec_from_file_location("_oneoff_replay", Path(__file__).with_name("verify_final_replay.py"))
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def replay_fixture(tmp_path, monkeypatch):
    root = tmp_path / "synthetic-run"
    monkeypatch.setattr(mod, "RUN", root)
    cases = {}
    for identifier in sorted(mod.costs.CASES):
        feedback = {"status": "audit_passed", "counts": {"audit_logical_calls": 1},
                    "rounds": [{"revision": 0, "status": "audit_passed", "decision": {"status": "audit_passed"}}]}
        annotation = {"status": "complete", "counts": {"logical_calls": 1}, "profiles": {"ir1": {}}, "unresolved": []}
        cases[identifier] = {"feedback": feedback, "annotation": annotation,
                             "selection": {"revision": 0, "graph_sha256": "abc"}, "counts": {"total_logical_calls": 3}}
        case = root / "cases" / identifier
        put(case / "result.json", cases[identifier])
        put(case / "replay/result.json", cases[identifier])
        for role, value in (("feedback", feedback), ("annotation", annotation)):
            stage = case / role
            put(stage / "manifest.json", {"identity": "synthetic"})
            put(stage / "result.json", value)
            put(stage / "replay/result.json", value)
        round_path = case / "feedback/rounds/r000/round.json"
        put(round_path, feedback["rounds"][0])
        put(case / "feedback/replay/rounds/r000/round.json", feedback["rounds"][0])
        for sub in ("feedback/rounds/r000/controlled.txt", "feedback/replay/rounds/r000/controlled.txt"):
            (case / sub).write_text("实际中文事实\\n与顺序", encoding="utf-8")
        put(case / "annotation/profiles.json", annotation["profiles"])
        put(case / "annotation/replay/profiles.json", annotation["profiles"])
    outcome = {"schema_version": 4, "identity": mod.prep.PARENT_IDENTITY, "mode": "run", "cases": cases,
               "summary": {"cases": 30, "counts": {"total_logical_calls": 90}}}
    put(root / "experiment-result.json", outcome)
    put(root / "replay/experiment-result.json", {**outcome, "mode": "replay"})
    put(root / "replay/progress.json", cases)
    (root / "replay/report.md").write_text("离线重放", encoding="utf-8")
    monkeypatch.setattr(mod, "assert_snapshot_current", lambda value: outcome)
    return root, outcome


def test_actual_replay_layout_checks_all_thirty_and_stage_artifacts(replay_fixture):
    result = mod.verify_replay({})
    assert len(result["cases"]) == 30
    assert result["cases"]["001"]["stages"]["feedback"]["artifacts"] == 3
    assert "cases/030/feedback/replay/rounds/r000/controlled.txt" in result["derived_files"]


@pytest.mark.parametrize("change", ["status", "count", "revision"])
def test_terminal_semantics_cannot_change(replay_fixture, change):
    root, _ = replay_fixture
    path = root / "cases/012/replay/result.json"
    value = mod.read_json(path)
    if change == "status":
        value["feedback"]["status"] = "unresolved"
    elif change == "count":
        value["counts"]["total_logical_calls"] = 999
    else:
        value["selection"]["revision"] = 1
    put(path, value)
    with pytest.raises(ValueError, match="terminal result"):
        mod.verify_replay({})


def test_round_or_exact_controlled_text_tampering_is_rejected(replay_fixture):
    root, _ = replay_fixture
    target = root / "cases/008/feedback/replay/rounds/r000/controlled.txt"
    target.write_text("伪造事实", encoding="utf-8")
    with pytest.raises(ValueError, match="text bytes differ"):
        mod.verify_replay({})


def test_extra_or_missing_derived_record_is_rejected(replay_fixture):
    root, _ = replay_fixture
    put(root / "cases/002/annotation/replay/extra.json", {})
    with pytest.raises(ValueError, match="artifact set differs"):
        mod.verify_replay({})


def test_root_mode_is_the_only_allowed_aggregate_difference(replay_fixture):
    root, _ = replay_fixture
    path = root / "replay/experiment-result.json"
    value = mod.read_json(path)
    value["summary"]["counts"]["total_logical_calls"] = 89
    put(path, value)
    with pytest.raises(ValueError, match="only mode"):
        mod.verify_replay({})


def test_pending_gate_precedes_any_call_read_and_output_creation(tmp_path, monkeypatch):
    root = tmp_path / "pending-run"
    root.mkdir()
    monkeypatch.setattr(mod, "RUN", root)
    def forbidden(*args):
        pytest.fail("Calls were read before the terminal gate")
    monkeypatch.setattr(mod.costs, "call_files", forbidden)
    monkeypatch.setattr(mod.costs, "verify_lineage", forbidden)
    target = tmp_path / "must-not-exist"
    with pytest.raises(mod.costs.PendingRunError):
        mod.create_snapshot(target)
    assert not target.exists()


def test_offline_guard_refuses_dns_and_online_model_method():
    import skill_ir.llm.client as client
    with mod.offline_guard() as attempts:
        with pytest.raises(RuntimeError, match="forbids network"):
            socket.getaddrinfo("invalid.test", 443)
        with pytest.raises(RuntimeError, match="forbids network"):
            client.LlmClient.complete(object(), "no network")
    assert len(attempts) == 2


def test_protected_inventory_rejects_extra_file(tmp_path, monkeypatch):
    root = tmp_path / "repository"
    folder = root / "dataset/skills"
    folder.mkdir(parents=True)
    expected = {}
    for number in range(203):
        name = f"{number:03}.zip"
        target = folder / name
        target.write_bytes(b"source")
        expected["dataset/skills/" + name] = mod.sha_file(target)
    baseline = tmp_path / "protection.json"
    put(baseline, expected)
    monkeypatch.setattr(mod, "ROOT", root)
    monkeypatch.setattr(mod, "PROTECTION", baseline)
    monkeypatch.setattr(mod, "PROTECTED_ROOTS", ("dataset/skills",))
    assert mod.protected_inventory() == expected
    (folder / "extra.zip").write_bytes(b"unexpected")
    with pytest.raises(ValueError, match="set or file bytes"):
        mod.protected_inventory()


def test_snapshot_seal_rejects_modified_record():
    value = mod.seal({"call_files": {"response.json": "old"}})
    mod.assert_seal(value)
    value["call_files"]["response.json"] = "new"
    with pytest.raises(ValueError, match="seal mismatch"):
        mod.assert_seal(value)


@pytest.fixture
def inventory_fixture(tmp_path, monkeypatch):
    """Exercise real hashing and comparison, with no access to the real batch."""
    child = tmp_path / "child"
    parent = tmp_path / "parent"
    protection = tmp_path / "protection.json"
    protected_file = tmp_path / "protected.zip"
    protected_file.write_bytes(b"frozen input")
    put(protection, {"protected.zip": mod.sha_file(protected_file)})
    put(parent / "manifest.json", {"identity": "original"})
    call_path = child / "cases/001/feedback/calls/r000/audit/a001/call.json"
    put(call_path, {"accepted": True, "response": "original"})
    for identifier in mod.costs.CASES:
        (child / "cases" / identifier).mkdir(parents=True, exist_ok=True)
    outcome = {"mode": "run", "cases": {
        "001": {"feedback": {"status": "audit_passed", "rounds": []},
                "annotation": {"status": "complete", "profiles": {"ir1": {"actor": ["tool"]}}, "unresolved": []},
                "selection": {"revision": 0, "graph_sha256": "abc"},
                "counts": {"total_logical_calls": 3}, "scheduler_error": None}},
        "summary": {"cases": 1}}
    put(child / "experiment-result.json", outcome)
    monkeypatch.setattr(mod, "RUN", child)
    monkeypatch.setattr(mod, "PROTECTION", protection)
    monkeypatch.setattr(mod, "source_identity", lambda: {"synthetic.py": "fixed"})
    monkeypatch.setattr(mod.costs, "terminal_material", lambda directory: ({}, mod.read_json(directory / "experiment-result.json")))
    monkeypatch.setattr(mod, "protected_inventory", lambda: {"protected.zip": mod.sha_file(protected_file)})
    value = mod.seal({
        "schema_version": 1, "identity": mod.IDENTITY, "phase": "before_replay",
        "run_path": str(child), "parent_path": str(parent),
        "implementation_files": mod.source_identity(), "case_summaries": mod.summaries(outcome),
        "summary": outcome["summary"], "root_result_sha256": mod.sha_file(child / "experiment-result.json"),
        "child_files": mod.prep.inventory(child), "call_files": mod.costs.call_files(child, mod.costs.CASES),
        "parent_files": mod.prep.inventory(parent), "protection_manifest_sha256": mod.sha_file(protection),
        "protected_files": mod.protected_inventory(),
    })
    return child, parent, protected_file, call_path, value


def test_snapshot_accepts_only_replay_and_exact_lock_additions(inventory_fixture):
    child, parent, _, _, value = inventory_fixture
    put(child / "cases/001/feedback/replay/result.json", {"derived": True})
    (child / ".runner.lock").write_bytes(b"ephemeral")
    put(parent / "replay/result.json", {"derived": True})
    assert mod.assert_snapshot_current(value)["summary"]["cases"] == 1


@pytest.mark.parametrize("change", ["extra_child_report", "original_call", "parent_file", "protected_file", "root_counts"])
def test_snapshot_rejects_original_artifact_or_result_changes(inventory_fixture, change):
    child, parent, protected_file, call_path, value = inventory_fixture
    if change == "extra_child_report":
        (child / "assistant-report.md").write_text("added during replay", encoding="utf-8")
    elif change == "original_call":
        put(call_path, {"accepted": True, "response": "changed"})
    elif change == "parent_file":
        put(parent / "manifest.json", {"identity": "changed"})
    elif change == "protected_file":
        protected_file.write_bytes(b"changed frozen input")
    else:
        outcome = mod.read_json(child / "experiment-result.json")
        outcome["cases"]["001"]["counts"]["total_logical_calls"] = 4
        put(child / "experiment-result.json", outcome)
    with pytest.raises(ValueError):
        mod.assert_snapshot_current(value)


def test_missing_derived_profile_is_rejected(replay_fixture):
    root, _ = replay_fixture
    (root / "cases/030/annotation/replay/profiles.json").unlink()
    with pytest.raises(ValueError, match="artifact set differs"):
        mod.verify_replay({})


def test_changed_profile_content_is_rejected(replay_fixture):
    root, _ = replay_fixture
    put(root / "cases/030/annotation/replay/profiles.json", {"ir1": {"actor": ["llm"]}})
    with pytest.raises(ValueError, match="Offline replay JSON differs"):
        mod.verify_replay({})


def test_offline_guard_refuses_factory_and_direct_connection():
    import skill_ir.recording as recording
    with socket.socket() as connection:
        with mod.offline_guard() as attempts:
            with pytest.raises(RuntimeError, match="forbids network"):
                recording.streaming_factory({})
            with pytest.raises(RuntimeError, match="forbids network"):
                connection.connect(("127.0.0.1", 1))
    assert len(attempts) == 2
