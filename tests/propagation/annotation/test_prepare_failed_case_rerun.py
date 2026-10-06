"""Explicit failed-case rerun preparation, with no model or network access."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.graph.feedback.runner import _RoundClient
from skillflow.common.recording import canonical_sha256
from skillflow.graph.semantic_contract import contract_binding

SCRIPT = project_root() / "tools/propagation/annotation/prepare_failed_case_rerun.py"


@pytest.fixture(scope="module")
def tool():
    spec = importlib.util.spec_from_file_location("test_explicit_failed_rerun", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def parent(tool, tmp_path, monkeypatch):
    root = tmp_path / "parent-run"
    root.mkdir()
    manifest = {"schema_version": 10, "profile_schema_version": "security-profile-v10", "identity": tool.PARENT_IDENTITY, **contract_binding(), "cases": []}
    result = {"schema_version": 10, "profile_schema_version": "security-profile-v10", "identity": tool.PARENT_IDENTITY, **contract_binding(), "cases": {}, "summary": {"cases": 30}}
    for number in range(1, 31):
        identifier = f"{number:03}"
        failed = identifier in tool.EXPECTED_RERUN_CASES
        manifest["cases"].append({"case_id": identifier, "run_dir": f"cases/{identifier}", "package_path": f"inputs/{identifier}"})
        value = {"feedback": {"status": "audit_error" if failed else "audit_passed"},
                 "annotation": {"status": "complete", "transfer_specs": {"ir": {"order": "partial"}} if identifier == "007" else {}}, "scheduler_error": None}
        result["cases"][identifier] = value
        case = root / "cases" / identifier
        tool.write_json(case / "result.json", value)
        prompt = "prompt " + identifier
        response = {"fixture_response": identifier}
        record = {"status": "complete", "prompt": prompt, "prompt_sha256": canonical_sha256(prompt),
                  "response": response, "response_sha256": canonical_sha256(response)}
        trace = {"status": "complete", "prompt": prompt, "response": response,
                 "http_attempts": [{"status": "complete", "http_status": 200}]}
        trace["record_sha256"] = canonical_sha256(trace)
        directory = case / "feedback/calls/r000/extraction/a001"
        tool.write_json(directory / "call.json", record)
        tool.write_json(directory / "transport.json", [trace])
        tool.write_json(case / "feedback/inputs/snapshot.json", {"snapshot_marker": identifier})
        tool.write_json(case / "feedback/replay/result.json", {"exclude": True})
        (case / "feedback/.runner.lock").write_bytes(b"lock")
        (case / "feedback/dependencies.lock").write_bytes(b"must keep")
    tool.write_json(root / "manifest.json", manifest)
    tool.write_json(root / "experiment-result.json", result)
    tool.write_json(root / "replay/experiment-result.json", {"exclude": True})
    (root / ".runner.lock").write_bytes(b"lock")
    rerun, reuse = tool.classify_cases(manifest, result)
    monkeypatch.setattr(tool, "validate_parent", lambda path: (manifest, result, rerun, reuse))
    return SimpleNamespace(root=root, manifest=manifest, result=result, rerun=rerun, reuse=reuse)


def test_exact_failure_set_and_partial_order_is_not_failure(tool, parent):
    rerun, reuse = tool.classify_cases(parent.manifest, parent.result)
    assert rerun == ["008", "009", *[f"{i:03}" for i in range(18, 31)]]
    assert len(reuse) == 15 and "007" in reuse
    changed = deepcopy(parent.result)
    changed["cases"]["001"]["annotation"]["status"] = "invalid_response"
    with pytest.raises(ValueError, match="authorized fifteen"):
        tool.classify_cases(parent.manifest, changed)


def test_preparation_copies_only_complete_success_cases_and_seals_parent(tool, parent, tmp_path):
    before = tool.inventory(parent.root)
    target = tmp_path / "rerun"
    result = tool.prepare(parent.root, target)
    assert tool.inventory(parent.root) == before
    assert (target / "manifest.json").read_bytes() == (parent.root / "manifest.json").read_bytes()
    for identifier in parent.rerun:
        assert not (target / "cases" / identifier).exists()  # No accepted/bad/DNS stage is inherited.
    for identifier in parent.reuse:
        assert (target / "cases" / identifier / "result.json").read_bytes() == (parent.root / "cases" / identifier / "result.json").read_bytes()
        assert not (target / "cases" / identifier / "feedback/replay").exists()
        assert not (target / "cases" / identifier / "feedback/.runner.lock").exists()
        assert (target / "cases" / identifier / "feedback/dependencies.lock").read_bytes() == b"must keep"
    assert result["authorization"]["user_request"] == "失败的全部重跑一下"
    assert result["parent_run"]["files"] == before
    unsigned = {key: value for key, value in result.items() if key != "provenance_sha256"}
    assert result["provenance_sha256"] == canonical_sha256(unsigned)
    assert len(result["parent_call_ledger"]) == 30 and len(result["reused_call_origins"]) == 15
    assert result["cost_accounting"]["parent_http_attempts"] == 30


def test_copied_accepted_call_uses_real_saved_response_without_factory(tool, parent, tmp_path):
    target = tmp_path / "rerun"
    tool.prepare(parent.root, target)
    state = SimpleNamespace(directory=target / "cases/001/feedback", replay=False,
                            writer=ArtifactWriter(()), used_calls=[], progress=None, config={"extraction": {}, "audit": {}},
                            should_pause=lambda *args: False)
    def forbidden_factory(*args, **kwargs):
        pytest.fail("A copied successful call must not create an online client")
    client = _RoundClient(state, 0, "extraction", forbidden_factory, 4)
    assert client.complete("prompt 001") == {"fixture_response": "001"}
    assert client.calls == 1 and len(state.used_calls) == 1


def test_existing_target_and_same_run_id_are_rejected_without_mutation(tool, parent, tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "keep.txt").write_text("keep")
    with pytest.raises(ValueError, match="already exists"):
        tool.prepare(parent.root, target)
    assert (target / "keep.txt").read_text() == "keep"
    with pytest.raises(ValueError, match="distinct run ID"):
        tool.prepare(parent.root, tmp_path / "other" / parent.root.name)
    assert not (tmp_path / "other").exists()


def test_frozen_skill_subdirectory_is_rejected_before_creation(tool, parent, tmp_path, monkeypatch):
    monkeypatch.setattr(tool, "REPOSITORY_ROOT", tmp_path)
    package = tmp_path / "inputs/001"
    package.mkdir(parents=True)
    (package / "SKILL.md").write_text("frozen")
    target = package / "new-rerun"
    with pytest.raises(ValueError, match="frozen Skill package"):
        tool.prepare(parent.root, target)
    assert not target.exists() and (package / "SKILL.md").read_text() == "frozen"


def test_parent_mutation_during_copy_aborts_before_root_manifest(tool, parent, tmp_path, monkeypatch):
    original = tool.shutil.copyfile
    changed = False
    def copy_then_change(source, target):
        nonlocal changed
        result = original(source, target)
        if not changed:
            changed = True
            (parent.root / "unexpected.txt").write_text("change during copy")
        return result
    monkeypatch.setattr(tool.shutil, "copyfile", copy_then_change)
    target = tmp_path / "rerun"
    with pytest.raises(ValueError, match="Parent run changed"):
        tool.prepare(parent.root, target)
    assert not (target / "manifest.json").exists()


def test_call_integrity_is_checked_before_destination_creation(tool, parent, tmp_path):
    path = parent.root / "cases/001/feedback/calls/r000/extraction/a001/call.json"
    value = tool.read_json(path)
    value["response"] = {"corrupt": True}
    tool.write_json(path, value)
    with pytest.raises(ValueError, match="durable binding"):
        tool.prepare(parent.root, tmp_path / "rerun")
    assert not (tmp_path / "rerun").exists()


def test_missing_http_inventory_cannot_be_counted_as_known_zero(tool, parent):
    path = parent.root / "cases/001/feedback/calls/r000/extraction/a001/transport.json"
    trace = tool.read_json(path)
    trace[0].pop("http_attempts")
    trace[0].pop("record_sha256")
    trace[0]["record_sha256"] = canonical_sha256(trace[0])
    tool.write_json(path, trace)
    with pytest.raises(ValueError, match="explicit HTTP attempt inventory"):
        tool.call_ledger(parent.root, tool.inventory(parent.root))


def test_unknown_http_inventory_remains_unknown(tool, parent):
    path = parent.root / "cases/001/feedback/calls/r000/extraction/a001/transport.json"
    trace = tool.read_json(path)
    trace[0].update(http_attempts=[], http_attempts_observed=False)
    trace[0].pop("record_sha256")
    trace[0]["record_sha256"] = canonical_sha256(trace[0])
    tool.write_json(path, trace)
    ledger = tool.call_ledger(parent.root, tool.inventory(parent.root))
    first = next(row for row in ledger if row["case_id"] == "001")
    assert first["http_attempts"] is None and first["http_attempts_observed"] is False
