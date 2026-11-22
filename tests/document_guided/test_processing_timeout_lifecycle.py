"""Fresh-run ownership and frozen helpers, without launching a native process."""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

import pytest

from skillflow.document_guided.runner import POLICY


VERIFY = Path(__file__).resolve().parents[2] / "output/verification/online-ga4-processing-timeout-20261116"


def load(name):
    spec = spec_from_file_location("processing_timeout_" + name, VERIFY / (name + ".py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.mark.parametrize("status,marker", [
    ("partial", None), ("failed", None),
    ("prepared", "replay-started.json"),
    ("prepared", "transport/processing/a001/started.json"),
])
def test_controller_refuses_nonfresh_results_and_existing_attempts(tmp_path, monkeypatch, status, marker):
    monkeypatch.setitem(sys.modules, "local_timing", load("local_timing"))
    controller = load("controller-template")
    project, run = tmp_path, tmp_path / "experiments/doe/runs/fresh"
    monkeypatch.setattr(controller, "PROJECT", project)
    monkeypatch.setattr(controller, "RUN", run)
    def forbidden(*args, **kwargs):
        pytest.fail("Nonfresh controller reached analysis, source loading or a native client")
    for name in ("Client", "analyze", "read_snapshot"):
        monkeypatch.setattr(controller, name, forbidden)
    write(run / "manifest.json", {"config": controller.CONFIG, "policy": POLICY})
    write(run / "run-protocol.json", {})
    write(run / "result.json", {"status": status})
    if marker:
        write(run / marker, {})
    with pytest.raises(RuntimeError, match="fresh|already"):
        controller.main()
    assert not (run / "controller-started.json").exists()
    assert "tools/doe/document_guided_observation.py" in controller.TRANSPORT_FILES


def test_preparation_claim_is_exclusive_and_preserves_existing_intent(tmp_path):
    prepare = load("prepare_run")
    path = tmp_path / "preparation-intent.json"
    prepare.create(path, {"maximum_new_runs": 1, "run_directory": "first"})
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        prepare.create(path, {"run_directory": "second"})
    assert path.read_bytes() == before


def test_preparation_rejects_changed_tool_before_creating_a_run(tmp_path, monkeypatch):
    prepare = load("prepare_run")
    monkeypatch.setattr(prepare, "PROJECT", tmp_path)
    monkeypatch.setattr(prepare, "OFFLINE", tmp_path / "offline")
    monkeypatch.setattr(prepare, "OLD_RUN", tmp_path / "closed")
    monkeypatch.setattr(prepare, "PINNED_TOOLS", {"transport.py"})
    monkeypatch.setattr(prepare, "LIFECYCLE_NAMES", set())
    monkeypatch.setattr(prepare, "implementation_provenance", lambda: {"sha256": "accepted"})
    write(tmp_path / "offline/offline-acceptance.json", {
        "status": "passed", "implementation_sha256": "accepted",
        "tool_file_sha256": {"transport.py": "wrong"}, "lifecycle_file_sha256": {}})
    write(tmp_path / "closed/run-protocol.json", {})
    (tmp_path / "transport.py").write_text("changed", encoding="utf-8")
    monkeypatch.setattr(prepare, "prepare", lambda *a, **k: pytest.fail("Changed tool prepared a new run"))
    with pytest.raises(ValueError, match="differs from this fix acceptance"):
        prepare.main()
    assert not (tmp_path / "experiments").exists()


def test_preparation_rejects_an_incomplete_acceptance_inventory(tmp_path, monkeypatch):
    prepare = load("prepare_run")
    monkeypatch.setattr(prepare, "OFFLINE", tmp_path / "offline")
    monkeypatch.setattr(prepare, "OLD_RUN", tmp_path / "closed")
    write(tmp_path / "offline/offline-acceptance.json", {
        "tool_file_sha256": {}, "lifecycle_file_sha256": {}})
    write(tmp_path / "closed/run-protocol.json", {})
    monkeypatch.setattr(prepare, "prepare", lambda *a, **k: pytest.fail("Incomplete acceptance prepared a run"))
    with pytest.raises(ValueError, match="bind every current transport and lifecycle helper"):
        prepare.main()


def test_dispatch_claims_once_and_uses_hidden_window():
    dispatch = (VERIFY / "dispatch_once.ps1").read_text(encoding="utf-8")
    assert dispatch.index("[IO.FileMode]::CreateNew") < dispatch.index("Start-Process")
    assert "-WindowStyle Hidden" in dispatch
    assert "ga4-processing-shared-high-" in dispatch
    assert dispatch.count("Start-Process") == 1


@pytest.mark.parametrize("receipt,confirmed", [(None, False), ({"exited": False}, False),
                                              ({"exited": True}, True)])
def test_controller_never_equates_terminal_status_with_native_exit(tmp_path, monkeypatch, receipt, confirmed):
    monkeypatch.setitem(sys.modules, "local_timing", load("local_timing"))
    controller = load("controller-template")
    monkeypatch.setattr(controller, "RUN", tmp_path)
    attempt = tmp_path / "transport/processing/a001"
    write(attempt / "started.json", {})
    if receipt is not None:
        write(attempt / "process.json", receipt)
    result = controller.native_exit_report()
    assert result["all_attempt_exits_confirmed"] is confirmed
    assert result["attempt_markers"] == 1
    assert result["unconfirmed_attempts"] == ([] if confirmed else ["transport/processing/a001"])
