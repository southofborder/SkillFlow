"""Report-only recovery preserves original calls and facts without identity bypass."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
import importlib.util
from pathlib import Path
import shutil
import socket

import pytest

from tests.propagation.test_runner import annotation_run
from skillflow.common.artifacts import ArtifactWriter
from skillflow.propagation.runner import run_propagation
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import implementation_provenance
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file


def tool():
    path = project_root() / "tools/propagation/recover_reports_offline.py"
    spec = importlib.util.spec_from_file_location("test_offline_recovery_tool", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def captured_case(annotation_run, tmp_path, monkeypatch):
    import skillflow.propagation.runner as runner
    module = tool()
    root = tmp_path / "original"
    case = root / "cases/001"
    shutil.copytree(annotation_run, case / "annotation")
    writer = ArtifactWriter(())
    annotated = read_json(case / "annotation/result.json")
    cfg = read_json(case / "annotation/inputs/cfg.json")
    snapshot = read_json(case / "annotation/inputs/snapshot.json")
    for stage in ("source", "feedback"):
        shutil.copytree(case / "annotation/inputs", case / stage / "inputs")
    feedback = {"status": "audit_passed", "last_valid_cfg": cfg}
    selection = {"graph_sha256": canonical_sha256(cfg), "auditor_passed": True}
    binding = {"status": "passed", "source_sha256": snapshot["source_sha256"],
               "package_bytes_sha256": snapshot["package_bytes_sha256"]}
    writer.json(case / "feedback/manifest.json", {"renderer": {"path": "mocked-printer"}})
    writer.json(case / "feedback/result.json", feedback)
    writer.json(case / "selection.json", selection)
    writer.json(case / "selected-analysis.json", {"cfg": cfg})
    writer.json(case / "source-binding.json", binding)
    writer.json(case / "result.json", {"feedback": feedback, "annotation": annotated, "selection": selection,
                                       "source_binding": binding})
    writer.json(root / "manifest.json", {
        "identity": module.PILOT_IDENTITY, "schema_version": module.PILOT_FORMAT_VERSION,
        "profile_schema_version": module.PROFILE_VERSION,
        "implementation": implementation_provenance(),
        "cases": [{"case_id": "001", "source_sha256": snapshot["source_sha256"],
                   "package_bytes_sha256": snapshot["package_bytes_sha256"],
                   "source_inventory": {e["path"]: {"bytes": e["size"], "sha256": e["raw_sha256"]} for e in snapshot["files"]}}],
        "driver_sha256": sha_file(module.PACKAGE / "tools/propagation/run_pilot.py"),
        "shared_case_driver_sha256": sha_file(module.PACKAGE / "tools/propagation/annotation/run_full_pipeline.py"),
    })
    with monkeypatch.context() as scoped:
        scoped.setattr(runner, "write_reports", lambda *a, **kw: (_ for _ in ()).throw(TypeError("report failure")))
        with pytest.raises(TypeError, match="report failure"):
            run_propagation(case / "annotation", run_dir=case / "propagation")
    assert not (case / "propagation/manifest.json").exists()
    writer.json(case / "driver-error.json", {"error": "TypeError: report failure"})
    monkeypatch.setattr(module, "replay_feedback", lambda *a, **kw: deepcopy(feedback))
    receipt_dir = root / "offline-recovery/cases/001/capture"
    module.capture(case, receipt_dir)
    return module, case, receipt_dir


def corrected_identity(module, receipt_dir, monkeypatch):
    import skillflow.propagation.runner as runner
    identity = deepcopy(read_json(receipt_dir / "receipt.json")["capture_implementation"])
    identity["files"][module.REPORT_SOURCE] = "simulated-corrected-report-hash"
    identity["sha256"] = canonical_sha256(identity["files"])
    monkeypatch.setattr(module, "implementation_provenance", lambda: identity)
    monkeypatch.setattr(runner, "implementation_provenance", lambda: identity)
    return identity


def test_report_only_recovery_keeps_original_uncommitted_and_copies_exact_calls(captured_case, monkeypatch):
    module, case, receipt_dir = captured_case
    receipt = read_json(receipt_dir / "receipt.json")
    assert receipt["stage_replay"]["feedback_equal"] and receipt["stage_replay"]["annotation_equal"]
    assert receipt["schema_version"] == module.FORMAT_VERSION == 3
    accepted = module.accepted_material(case, check_current_implementation=True)
    assert accepted[4]["sink_boundaries"] == accepted[3]["sink_boundaries"]
    before = module.material_hashes(case)
    corrected_identity(module, receipt_dir, monkeypatch)
    out = receipt_dir.parent / "propagation"
    checks = module.recover(receipt_dir, out)
    assert checks["status"] == "matched" and checks["original_doe_equal"] is True
    assert checks["model_calls"] == 0 and checks["network_guard"]["network_attempts"] == 0
    assert not checks["original_propagation_committed"]
    assert read_json(out / "doe-input.json") == read_json(case / "propagation/doe-input.json")
    assert not (case / "propagation/manifest.json").exists()
    assert module.material_hashes(case) == before
    for name in ("call.json", "transport.json"):
        assert read_json(out / "audit/accepted-call" / name) == read_json(case / "annotation/calls/annotation/a001" / name)
    saved = read_json(out / "audit/provenance.json")
    assert saved["annotation_manifest"] == read_json(case / "annotation/manifest.json")
    assert saved["recovery"]["capture_receipt"] == receipt
    assert saved["recovery"]["new_model_calls"] == 0
    assert read_json(out / "replay/summary.json")["status"] == "matched"


@pytest.mark.parametrize("change", ["unchanged", "other", "both", "missing", "python"])
def test_recovery_rejects_any_non_report_source_delta(change):
    module = tool()
    before = {"files": {module.REPORT_SOURCE: "old", "other.py": "same"}, "python": "3", "sha256": "old"}
    after = deepcopy(before)
    if change in {"both", "missing", "python"}:
        after["files"][module.REPORT_SOURCE] = "new"
    if change in {"other", "both"}:
        after["files"]["other.py"] = "changed"
    if change == "missing":
        del after["files"]["other.py"]
    if change == "python":
        after["python"] = "4"
    with pytest.raises(ValueError):
        module.source_change(before, after)


@pytest.mark.parametrize("relative", ["annotation/calls/annotation/a001/call.json", "selected-analysis.json",
                                     "propagation/doe-input.json", "annotation/audit/location-evidences.json",
                                     "annotation/sink-boundaries.json"])
def test_recovery_refuses_changed_original_even_when_json_equal(captured_case, monkeypatch, relative):
    module, case, receipt_dir = captured_case
    corrected_identity(module, receipt_dir, monkeypatch)
    target = case / relative
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(ValueError, match="original captured"):
        module.recover(receipt_dir, receipt_dir.parent / "propagation")
    assert not (receipt_dir.parent / "propagation").exists()


def test_recovery_refuses_old_or_modified_receipt(captured_case):
    module, _, receipt_dir = captured_case
    value = read_json(receipt_dir / "receipt.json")
    value["schema_version"] = 0
    ArtifactWriter(()).json(receipt_dir / "receipt.json", value)
    with pytest.raises(ValueError, match="unsupported or altered"):
        module.recover(receipt_dir, receipt_dir.parent / "propagation")


def test_capture_rejects_interrupted_or_unaccepted_annotations(captured_case, tmp_path):
    module, case, _ = captured_case
    call = read_json(case / "annotation/calls/annotation/a001/call.json")
    call["status"] = "interrupted"
    ArtifactWriter(()).json(case / "annotation/calls/annotation/a001/call.json", call)
    with pytest.raises(ValueError, match="not durably accepted"):
        module.accepted_material(case, check_current_implementation=True)


def test_network_guard_blocks_and_restores_online_surfaces():
    import skillflow.common.recording as recording
    module = tool()
    original = socket.create_connection
    with module.network_guard() as attempts:
        with pytest.raises(RuntimeError, match="forbids"):
            socket.create_connection(("example.invalid", 443))
        with pytest.raises(RuntimeError, match="forbids"):
            recording.streaming_factory({})
    assert socket.create_connection is original
    assert module.guard_record(attempts)["status"] == "failed"
    assert module.guard_record(attempts)["network_attempts"] == 2


def test_recovery_refuses_old_annotation_identity_before_reading_inputs(tmp_path):
    module = tool()
    value = {"identity": "skill-ir-security-profile-v9", "schema_version": 9,
             "profile_schema_version": "security-profile-v8"}
    value["manifest_sha256"] = canonical_sha256(value)
    ArtifactWriter(()).json(tmp_path / "annotation/manifest.json", value)
    with pytest.raises(ValueError, match="unsupported or altered original annotation"):
        module.accepted_material(tmp_path, check_current_implementation=False)


def test_recovery_refuses_changed_business_facts_before_saving(captured_case, monkeypatch):
    module, _, receipt_dir = captured_case
    corrected_identity(module, receipt_dir, monkeypatch)
    build = module.build_doe_input
    def change(*args, **kwargs):
        result = build(*args, **kwargs)
        result["data"][0]["annotations"]["description"] = "altered fact"
        return result
    monkeypatch.setattr(module, "build_doe_input", change)
    output = receipt_dir.parent / "propagation"
    with pytest.raises(ValueError, match="changed the original DOE"):
        module.recover(receipt_dir, output)
    assert not output.exists()
