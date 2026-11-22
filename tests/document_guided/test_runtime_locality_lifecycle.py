"""Fresh GA4 helper lifecycle uses only fake local fixtures, never native tools."""
from importlib.util import module_from_spec, spec_from_file_location
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

VERIFY = Path(__file__).resolve().parents[2] / "output/verification/online-ga4-runtime-locality-20261117"


def load(name):
    spec = spec_from_file_location("runtime_locality_test_" + name, VERIFY / (name + ".py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def file(path, value="fake bytes"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return path


@pytest.fixture
def guard(monkeypatch):
    module = load("lifecycle_guard")
    monkeypatch.setitem(sys.modules, "lifecycle_guard", module)
    return module


@pytest.fixture
def prepared(tmp_path, monkeypatch, guard):
    project = tmp_path
    verify = project / "output/verification" / guard.VERIFY_NAME
    run = project / "experiments/doe/runs" / (guard.RUN_PREFIX + "20261117-100000")
    current = {"sha256": "implementation", "files": {"src/skillflow/fake.py": ""}}
    for name in guard.TOOLS | set(current["files"]) | {guard.RENDERER}:
        file(project / name, name)
    current["files"] = {name: guard.sha(project / name) for name in current["files"]}
    for name in guard.HELPERS:
        file(verify / name, name)
    cli = file(project / "fake-cli.exe")
    monkeypatch.setattr(guard, "PINNED_CLI", cli)
    monkeypatch.setattr(guard, "PINNED_CLI_SHA256", guard.sha(cli))
    monkeypatch.setattr(guard, "SOURCE_SHA256", "source")
    acceptance_path = verify.parent / guard.OFFLINE_NAME / "offline-acceptance.json"
    accepted = {"status": "passed", "implementation_sha256": current["sha256"],
        "tool_file_sha256": {name: guard.sha(project / name) for name in guard.TOOLS},
        "lifecycle_file_sha256": {(verify / name).relative_to(project).as_posix(): guard.sha(verify / name)
            for name in guard.HELPERS}}
    write(acceptance_path, accepted)
    source_files = {}
    for index in range(16):
        name = f"source-{index}.txt"
        source_files[name] = guard.sha(file(verify / "source-package" / name, name))
        file(run / "source/inputs/package" / name, name)
    for name in ("task/calls/task/a001/call.json", "steps/flow/calls/a001/call.json",
                 "steps/graph/calls/a001/call.json", *guard.INHERITED_GRAPH, *guard.INHERITED_ROOT):
        write(run / name, {"inherited": name})
    inherited = {"run_directory": str(project / "fixed-parent"), "implementation_sha256":"parent-implementation",
        "inherited_files": guard.inherited_inventory(run)}
    copies = {"inherited/"+name:digest for name,digest in inherited["inherited_files"].items()}
    for name in inherited["inherited_files"]:
        target=run/"inherited"/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((run/name).read_bytes())
        if not name.startswith("source/") and name not in guard.INHERITED_GRAPH:
            (run/name).unlink()
        else:
            copies[name]=inherited["inherited_files"][name]
    # Remove now empty live stage owners; imported material belongs only under inherited/.
    for tree in (run/"task",run/"steps"):
        for directory in sorted((p for p in tree.rglob("*") if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
            directory.rmdir()
        tree.rmdir()
    write(run/"accepted-upstream.json", {"identity":"skillflow-accepted-upstream-v1",
        "parent_directory":inherited["run_directory"], "parent_implementation":{"sha256":"parent-implementation"},
        "files":inherited["inherited_files"], "copied_files":copies, "inherited_logical_calls":3,
        "owners":{"task":"inherited/task","flow":"inherited/steps/flow","graph":"inherited/steps/graph"}})
    monkeypatch.setattr(guard, "parent_binding", lambda project: deepcopy(inherited))
    accepted["restart_parent"] = inherited
    write(acceptance_path, accepted)
    write(run / "inherited-inputs.json", inherited)
    inventory = {name: guard.sha(project / name) for name in guard.TOOLS | set(current["files"]) | {guard.RENDERER}}
    for name in inventory:
        file(run / "implementation-snapshot" / name, (project / name).read_text(encoding="utf-8"))
    snapshot = {"files": inventory, "implementation_sha256": current["sha256"]}
    for source, target, key in (("controller-template.py", "controller.py", "controller_sha256"),
            ("local_timing.py", "local_timing.py", "local_timing_sha256"),
            ("lifecycle_guard.py", "lifecycle_guard.py", "lifecycle_guard_sha256")):
        file(run / target, source)
        snapshot[key] = guard.sha(run / target)
    write(run / "implementation-snapshot/snapshot.json", snapshot)
    protocol = {**guard.IDENTITIES, **guard.BUDGETS, **guard.POLICY_FIELDS,
        "inherited_inputs_sha256": guard.sha(run / "inherited-inputs.json"),
        "accepted_upstream_sha256": guard.sha(run / "accepted-upstream.json"),
        "inherited_initial_stages": ["task", "flow", "graph"],
        "fresh_normal_stages": ["processing", "task-correspondence", "sensitivity", "review"],
        "historical_answers_imported": True,
        "runtime": {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai"},
        "verification_directory": str(verify), "offline_acceptance": str(acceptance_path),
        "offline_acceptance_sha256": guard.sha(acceptance_path), "implementation_sha256": current["sha256"],
        "source_sha256": "source", "source_file_sha256": source_files, "readable_files": 16,
        "source_staging": str(verify / "source-package")}
    for field, path in (("cli_executable", cli), ("python_executable", file(project / "fake-python.exe")),
                        ("renderer_executable", project / guard.RENDERER)):
        protocol[field], protocol[field + "_sha256"] = str(path), guard.sha(path)
    write(run / "run-protocol.json", protocol)
    manifest = {"identity": guard.IDENTITIES["guided_run_identity"], "implementation":current,
        "accepted_upstream":{"path":"accepted-upstream.json", "sha256":guard.sha(run / "accepted-upstream.json")},
        "config": guard.CONFIG, "policy": {
        "normal_semantic_calls": 7, "workers": 2, "structural_corrections": 1, "semantic_repairs": 1,
        **guard.POLICY_FIELDS}}
    manifest["manifest_sha256"]=guard.canonical(manifest)
    write(run / "manifest.json", manifest)
    write(run / "result.json", {"status": "prepared"})
    write(verify / "preparation-intent.json", {"owner": "/root", "maximum_new_runs": 1, "run_directory": str(run)})
    receipt = {"sole_owner": "/root", "run_directory": str(run),
        "implementation_sha256": current["sha256"], "source_sha256": "source",
        "source_staging": protocol["source_staging"], "offline_acceptance_sha256": guard.sha(acceptance_path),
        "preparation_intent_sha256": guard.sha(verify / "preparation-intent.json"),
        "run_protocol_sha256": guard.sha(run / "run-protocol.json"),
        "run_manifest_sha256": guard.sha(run / "manifest.json"),
        "inherited_inputs_sha256": guard.sha(run / "inherited-inputs.json"),
        "accepted_upstream_sha256": guard.sha(run / "accepted-upstream.json"),
        "snapshot_sha256": guard.sha(run / "implementation-snapshot/snapshot.json")}
    write(verify / "prepared-run.json", receipt)
    return project, verify, run, current, protocol


def test_valid_preflight_is_read_only(prepared, guard):
    project, verify, run, current, protocol = prepared
    before = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    assert guard.validate_dispatch(project, verify, current=current) == (run, protocol)
    assert {p: p.read_bytes() for p in project.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize("owner", [None, "root", "/root/transport_audit", ""])
def test_explicit_root_owner_required(guard, owner):
    with pytest.raises(ValueError, match="explicitly named /root"):
        guard.require_owner(owner)


@pytest.mark.parametrize("path", ["old-run", "nested/document-guided-ga4-runtime-locality-high-20261117-100000",
    "document-guided-ga4-runtime-locality-high-invalid", "../document-guided-ga4-runtime-locality-high-20261117-100000"])
def test_exact_fresh_namespace(guard, tmp_path, path):
    with pytest.raises(ValueError, match="exact fresh"):
        guard.authorized_run(tmp_path, tmp_path / "experiments/doe/runs" / path)


@pytest.mark.parametrize("name", ["controller-started.json", "replay-started.json", "analysis-finished.json",
    "controller-finished.json", "transport/processing/a001/started.json", "transport/processing/a001/pid.json",
    "steps/processing/calls/0001/call.json"])
def test_existing_execution_blocks_fresh_preflight(prepared, guard, name):
    project, verify, run, current, _ = prepared
    write(run / name, {})
    with pytest.raises(ValueError, match="already contains"):
        guard.validate_dispatch(project, verify, current=current)


@pytest.mark.parametrize("name", ["dispatch-intent.json", "dispatch-started.json"])
def test_dispatch_claim_is_never_retried(prepared, guard, name):
    project, verify, _, current, _ = prepared
    file(verify / name, "")  # Even an incomplete crash marker consumes the claim.
    with pytest.raises(ValueError, match="second launch"):
        guard.validate_dispatch(project, verify, current=current)


@pytest.mark.parametrize("relative", ["offline", "protocol", "manifest", "snapshot", "source", "staging", "helper", "cli", "snapshot-bytes"])
def test_changed_bound_material_rejected(prepared, guard, relative):
    project, verify, run, current, protocol = prepared
    paths = {"offline": Path(protocol["offline_acceptance"]), "protocol": run / "run-protocol.json",
        "manifest": run / "manifest.json", "snapshot": run / "implementation-snapshot/snapshot.json",
        "source": run / "source/inputs/package/source-0.txt", "staging": verify / "source-package/source-0.txt",
        "helper": run / "lifecycle_guard.py", "cli": Path(protocol["cli_executable"]),
        "snapshot-bytes": run / "implementation-snapshot/src/skillflow/fake.py"}
    with paths[relative].open("a", encoding="utf-8") as handle:
        handle.write(" ")
    with pytest.raises(ValueError, match="changed"):
        guard.validate_prepared(project, verify, current=current)


def test_public_observer_pin_is_mandatory(prepared, guard):
    project, verify, _, current, protocol = prepared
    path = Path(protocol["offline_acceptance"])
    accepted = guard.read(path)
    del accepted["tool_file_sha256"]["tools/doe/document_guided_observation.py"]
    write(path, accepted)
    with pytest.raises(ValueError, match="including public observation"):
        guard.validate_acceptance(project, verify, current)


@pytest.mark.parametrize("field,value", [("guided_run_identity", "skillflow-document-guided-run-v15"),
    ("step_identity", "skillflow-document-step-v12"), ("fragments_identity", "skillflow-document-fragments-v7"),
    ("source_review_fragment_identity", "skillflow-document-source-review-fragment-v5"),
    ("processing_wire_identity", "other"), ("workers", 3), ("native_timeout_seconds", 3000),
    ("processing_wire_guidance", "obsolete"), ("processing_format_diagnostics", "obsolete"),
    ("cfg_correction_scope", "causal-dependency-records-v1"),
    ("cfg_validation", "obsolete"), ("failed_stage_review", "obsolete"),
    ("shared_repair_admission", "obsolete"),
    ("fatal_phase_replay", "recorded_artifact_bound_frontier_v1"),
    ("fatal_phase_replay", None), ("address_identity", "obsolete"),
    ("accepted_upstream", "obsolete"), ("execution_failure_scope", "obsolete"),
    ("review_request_failure", "obsolete"), ("review_correction_scope", "obsolete")])
def test_protocol_identity_or_budget_rejected_even_with_rebound_receipt(prepared, guard, field, value):
    project, verify, run, current, protocol = prepared
    protocol[field] = value
    write(run / "run-protocol.json", protocol)
    receipt = guard.read(verify / "prepared-run.json")
    receipt["run_protocol_sha256"] = guard.sha(run / "run-protocol.json")
    write(verify / "prepared-run.json", receipt)
    with pytest.raises(ValueError, match="identities or budgets"):
        guard.validate_prepared(project, verify, current=current)


@pytest.mark.parametrize("old_policy", [None, "recorded_artifact_bound_frontier_v1"])
def test_stale_manifest_fatal_policy_rejected_even_with_rebound_receipt(prepared, guard, old_policy):
    project, verify, run, current, _ = prepared
    manifest = guard.read(run / "manifest.json")
    if old_policy is None:
        del manifest["policy"]["fatal_phase_replay"]
    else:
        manifest["policy"]["fatal_phase_replay"] = old_policy
    write(run / "manifest.json", manifest)
    receipt = guard.read(verify / "prepared-run.json")
    receipt["run_manifest_sha256"] = guard.sha(run / "manifest.json")
    write(verify / "prepared-run.json", receipt)
    with pytest.raises(ValueError, match="configuration or budgets changed"):
        guard.validate_prepared(project, verify, current=current)


@pytest.fixture
def controller(tmp_path, monkeypatch, guard):
    monkeypatch.setitem(sys.modules, "local_timing", load("local_timing"))
    controller = load("controller-template")
    run = tmp_path / "experiments/doe/runs" / (guard.RUN_PREFIX + "20261117-100000")
    verify = tmp_path / "verification"
    protocol = {"verification_directory": str(verify), "source_sha256": "source",
        "offline_acceptance_sha256": "acceptance", "renderer_executable": "fake-renderer", "cli_executable": "fake-cli"}
    monkeypatch.setattr(controller, "PROJECT", tmp_path)
    monkeypatch.setattr(controller, "RUN", run)
    write(run / "manifest.json", {"config": controller.CONFIG, "policy": controller.POLICY})
    write(run / "run-protocol.json", protocol)
    write(run / "result.json", {"status": "prepared"})
    write(run / "inherited-inputs.json", {"run_directory": str(tmp_path / "parent"), "inherited_files": {}})
    write(run / "accepted-upstream.json", {"copied_files": {}, "inherited_logical_calls": 3})
    (run / "steps").mkdir(parents=True)
    write(verify / "prepared-run.json", {})
    write(verify / "dispatch-intent.json", {"owner": "/root", "maximum_launches": 1, "run_directory": str(run),
        "prepared_run_sha256": guard.sha(verify / "prepared-run.json"),
        "run_protocol_sha256": guard.sha(run / "run-protocol.json"), "offline_acceptance_sha256": "acceptance"})
    monkeypatch.setattr(controller, "implementation_provenance", lambda: {})
    def preflight(*args, **kwargs):
        guard.require_fresh(run)
        return run, protocol
    monkeypatch.setattr(controller, "validate_prepared", preflight)
    monkeypatch.setattr(controller, "read_snapshot", lambda *a: (None, {"source_sha256": "source"}, None))
    monkeypatch.setattr(controller, "require_frozen", lambda *a: {"unchanged": True})
    monkeypatch.setattr(controller, "dependency_report", lambda *a: {"unchanged": True})
    monkeypatch.setattr(controller, "transport_metrics", lambda *a: {"fake": True})
    class Timing:
        phase = "analysis"
        def install(self): return self
        def restore(self): pass
        def snapshot(self): return {"fake": True}
    monkeypatch.setattr(controller, "LocalTiming", Timing)
    class NoNative:
        def __init__(self, *args, **kwargs):
            pytest.fail("Fake lifecycle must not instantiate a native client")
    monkeypatch.setattr(controller, "Client", NoNative)
    monkeypatch.setattr(controller, "analyze", lambda *a, **k: {"status": "failed"})
    monkeypatch.setattr(controller, "replay", lambda *a, **k: pytest.fail("Replay must be explicitly faked"))
    return controller, run, verify


def test_controller_runs_exactly_one_fake_terminal_replay(controller, monkeypatch, guard):
    module, run, _ = controller
    calls = []
    monkeypatch.setattr(module, "replay", lambda *a, **k: calls.append("fake-replay") or {"status": "failed"})
    assert module.main(["--owner", "/root"]) == 1
    assert calls == ["fake-replay"]
    checked = guard.read(run / "replay-check.json")
    assert checked["status"] == "matched" and checked["new_native_markers"] == 0
    assert checked["native_inventory_unchanged"] is True
    with pytest.raises(ValueError, match="already contains"):
        module.main(["--owner", "/root"])
    assert calls == ["fake-replay"]


@pytest.mark.parametrize("orphan", [False, True])
def test_unconfirmed_native_exit_blocks_replay(controller, monkeypatch, guard, orphan):
    module, run, _ = controller
    def analyze(*args, **kwargs):
        write(run / "transport/processing/a001" / ("pid.json" if orphan else "started.json"), {"pid": 123})
        if orphan:
            write(run / "transport/processing/a001/process.json", {"exited": True})
        return {"status": "failed"}
    monkeypatch.setattr(module, "analyze", analyze)
    module.main(["--owner", "/root"])
    assert not (run / "replay-started.json").exists()
    assert guard.read(run / "replay-check.json")["status"] == "not_attempted"
    assert guard.read(run / "continuation-state.json")["status"] == "native_exit_unconfirmed"


def test_replay_same_count_native_marker_tampering_fails(controller, monkeypatch, guard):
    module, run, _ = controller
    marker = run / "transport/processing/a001/started.json"
    def analyze(*args, **kwargs):
        write(marker, {"attempt": 1})
        write(marker.parent / "process.json", {"exited": True})
        return {"status": "failed"}
    def replay(*args, **kwargs):
        write(marker, {"attempt": 2})
        return {"status": "failed"}
    monkeypatch.setattr(module, "analyze", analyze)
    monkeypatch.setattr(module, "replay", replay)
    module.main(["--owner", "/root"])
    result = guard.read(run / "replay-check.json")
    assert result["status"] == "failed" and result["new_native_markers"] == 0
    assert result["native_inventory_unchanged"] is False


def test_dispatch_claim_must_bind_prepared_receipt(controller):
    module, run, verify = controller
    write(verify / "prepared-run.json", {"changed": True})
    with pytest.raises(ValueError, match="valid sole root dispatch"):
        module.main(["--owner", "/root"])
    assert not (run / "controller-started.json").exists()


def test_frozen_change_prevents_replay_before_claim(controller, monkeypatch, guard):
    module, run, _ = controller
    checks = []
    def frozen(*args):
        checks.append(True)
        if len(checks) > 1:
            raise RuntimeError("Frozen accepted bytes changed")
        return {"unchanged": True}
    monkeypatch.setattr(module, "require_frozen", frozen)
    module.main(["--owner", "/root"])
    assert not (run / "replay-started.json").exists()
    result = guard.read(run / "replay-check.json")
    assert result["status"] == "failed" and "Frozen" in result["reason"]


def test_keyboard_interrupt_never_replays(controller, monkeypatch, guard):
    module, run, _ = controller
    def interrupted(*args, **kwargs):
        write(run / "result.json", {"status": "failed"})
        raise KeyboardInterrupt()
    monkeypatch.setattr(module, "analyze", interrupted)
    module.main(["--owner", "/root"])
    assert not (run / "replay-started.json").exists()
    assert guard.read(run / "controller-finished.json")["controller_error"]["type"] == "KeyboardInterrupt"


def test_preparation_refuses_unaccepted_files_without_creating_intent(tmp_path, monkeypatch, guard):
    prepare = load("prepare_run")
    verify = tmp_path / "output/verification" / guard.VERIFY_NAME
    monkeypatch.setattr(prepare, "PROJECT", tmp_path)
    monkeypatch.setattr(prepare, "VERIFY", verify)
    monkeypatch.setattr(prepare, "implementation_provenance", lambda: {"sha256": "current"})
    monkeypatch.setattr(prepare, "prepare_from_accepted_cfg", lambda *a, **k: pytest.fail("Unaccepted material reached preparation"))
    write(verify.parent / guard.OFFLINE_NAME / "offline-acceptance.json", {
        "status": "passed", "implementation_sha256": "current", "tool_file_sha256": {}, "lifecycle_file_sha256": {}})
    with pytest.raises(ValueError, match="every transport and lifecycle"):
        prepare.main(["--owner", "/root", "--suffix", "20261117-100000"])
    assert not (verify / "preparation-intent.json").exists()
    assert not (tmp_path / "experiments").exists()


def test_missing_pinned_cli_never_falls_back_or_claims_run(tmp_path, monkeypatch, guard):
    prepare = load("prepare_run")
    monkeypatch.setattr(prepare, "POLICY", {**prepare.POLICY, **guard.POLICY_FIELDS})
    verify = tmp_path / "output/verification" / guard.VERIFY_NAME
    old_run = tmp_path / "closed-reference-only"
    inherited = {"run_directory": str(old_run), "inherited_files": {}}
    monkeypatch.setattr(guard, "parent_binding", lambda project: deepcopy(inherited))
    monkeypatch.setattr(prepare, "parent_binding", lambda project: deepcopy(inherited))
    monkeypatch.setattr(prepare, "PROJECT", tmp_path)
    monkeypatch.setattr(prepare, "VERIFY", verify)
    monkeypatch.setattr(prepare, "OLD_RUN", old_run)
    monkeypatch.setattr(prepare, "OFFLINE", verify.parent / guard.OFFLINE_NAME)
    monkeypatch.setattr(prepare, "implementation_provenance", lambda: {"sha256": "current"})
    monkeypatch.setattr(prepare.skillflow, "__file__", str(tmp_path / "src/skillflow/__init__.py"))
    for name, value in (("IDENTITY", guard.IDENTITIES["guided_run_identity"]),
        ("STEP_IDENTITY", guard.IDENTITIES["step_identity"]),
        ("FRAGMENTS_IDENTITY", guard.IDENTITIES["fragments_identity"]),
        ("SOURCE_REVIEW_FRAGMENT_IDENTITY", guard.IDENTITIES["source_review_fragment_identity"]),
        ("PROCESSING_WIRE_IDENTITY", guard.IDENTITIES["processing_wire_identity"])):
        monkeypatch.setattr(prepare, name, value)
    for name in guard.TOOLS:
        file(tmp_path / name, name)
    for name in guard.HELPERS:
        file(verify / name, name)
    write(prepare.OFFLINE / "offline-acceptance.json", {"status": "passed", "implementation_sha256": "current", "restart_parent": inherited,
        "tool_file_sha256": {name: guard.sha(tmp_path / name) for name in guard.TOOLS},
        "lifecycle_file_sha256": {(verify / name).relative_to(tmp_path).as_posix(): guard.sha(verify / name)
            for name in guard.HELPERS}})
    missing = tmp_path / "missing-pinned-cli.exe"
    monkeypatch.setattr(prepare, "PINNED_CLI", missing)
    monkeypatch.setattr(prepare, "PINNED_CLI_SHA256", "unchanged-pin")
    renderer = file(tmp_path / "fake-renderer.exe")
    write(old_run / "run-protocol.json", {"cli_executable": str(missing), "cli_executable_sha256": "unchanged-pin",
        "renderer_executable": str(renderer), "renderer_executable_sha256": guard.sha(renderer)})
    write(old_run / "continuation-state.json", {"status": "generation_closed"})
    write(old_run / "controller-finished.json", {"status": "failed"})
    monkeypatch.setattr(prepare, "prepare_from_accepted_cfg", lambda *a, **k: pytest.fail("Missing pinned CLI reached preparation"))
    with pytest.raises(ValueError, match="pinned CLI is unavailable or changed"):
        prepare.main(["--owner", "/root", "--suffix", "20261117-100000"])
    assert not (verify / "preparation-intent.json").exists()
    assert not (tmp_path / "experiments").exists()


def test_helper_imports_do_not_claim_or_launch(guard, monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "local_timing", load("local_timing"))
    monkeypatch.chdir(tmp_path)
    for name in ("prepare_run", "controller-template", "observe_run", "audit_cost_provenance", "audit_public_surface"):
        load(name)
    assert list(tmp_path.iterdir()) == []


def test_dispatch_is_explicit_exclusive_and_hidden():
    dispatch = (VERIFY / "dispatch_once.ps1").read_text(encoding="utf-8")
    assert "[ValidateSet('/root')]" in dispatch
    assert dispatch.index("--owner $Owner --verify") < dispatch.index("[IO.FileMode]::CreateNew") < dispatch.index("Start-Process")
    assert dispatch.count("Start-Process") == 1
    assert "-WindowStyle Hidden" in dispatch
    assert "offline_acceptance_sha256" in dispatch and "prepared_run_sha256" in dispatch


@pytest.mark.parametrize("stage", ["task", "flow", "graph"])
def test_initial_upstream_cannot_construct_or_send_native_client(guard, monkeypatch, stage):
    monkeypatch.setitem(sys.modules, "local_timing", load("local_timing"))
    controller = load("controller-template")
    def forbidden(*args):
        pytest.fail("Initial upstream constructed a new native client")
    client = controller.restart_client_factory(forbidden)(stage, Path(stage))
    with pytest.raises(RuntimeError, match="cannot be requested again"):
        client.complete("A missing inherited response must fail closed")


def test_new_downstream_and_existing_revision_stage_clients_remain_available(guard, monkeypatch):
    monkeypatch.setitem(sys.modules, "local_timing", load("local_timing"))
    controller = load("controller-template")
    observed = []
    factory = controller.restart_client_factory(lambda name, owner: observed.append(name) or object())
    for name in sorted(controller.FRESH_STAGES):
        assert factory(name, Path(name)) is not None
    assert set(observed) == set(controller.FRESH_STAGES)
    with pytest.raises(ValueError, match="outside the authorized"):
        factory("revision-flow", Path("revision-flow"))


@pytest.mark.parametrize("name", ["inherited/task/calls/task/a001/call.json", "graph/initial.json", "inherited/steps/graph/calls/a002/call.json"])
def test_changed_or_extra_inherited_input_fails_before_dispatch(prepared, guard, name):
    project, verify, run, current, _ = prepared
    write(run / name, {"changed":True})
    with pytest.raises(ValueError, match="Inherited accepted input inventory or bytes changed"):
        guard.validate_prepared(project, verify, current=current)


def test_rebound_missing_inheritance_protocol_is_rejected(prepared, guard):
    project, verify, run, current, protocol = prepared
    protocol["historical_answers_imported"] = False
    write(run / "run-protocol.json", protocol)
    receipt = guard.read(verify / "prepared-run.json")
    receipt["run_protocol_sha256"] = guard.sha(run / "run-protocol.json")
    write(verify / "prepared-run.json", receipt)
    with pytest.raises(ValueError, match="explicit inherited upstream inventory"):
        guard.validate_prepared(project, verify, current=current)


def test_new_accounting_separates_imported_calls_from_fresh_transports(controller, monkeypatch, guard):
    module, run, _ = controller
    def analyze(*args, **kwargs):
        for name in ("task/calls/task/a001", "steps/flow/calls/a001", "steps/graph/calls/a001"):
            write(run / "inherited" / name / "call.json", {"origin":"parent"})
        for name in ("processing", "task-correspondence", "sensitivity", "review"):
            write(run / "steps" / name / "calls/a001/call.json", {"origin":"new"})
            write(run / "transport" / name / "attempt-001/started.json", {"fake":True})
            write(run / "transport" / name / "attempt-001/process.json", {"exited":True})
        # A logical input rejection has no native start; it is still a new call.
        write(run / "review/calls/a002/call.json", {"status":"failed"})
        return {"status":"partial", "counts":{"logical_calls":8}}
    monkeypatch.setattr(module,"analyze",analyze)
    monkeypatch.setattr(module,"replay",lambda *a,**k:{"status":"partial", "counts":{"logical_calls":8}})
    assert module.main(["--owner","/root"]) == 0
    receipt=guard.read(run/"restart-accounting.json")
    assert receipt["inherited_logical_calls"] == 3
    assert receipt["new_logical_calls"] == 5
    assert receipt["new_native_starts"] == 4
    assert receipt["recorded_logical_calls_including_inherited"] == 8


def test_failed_controller_accounting_uses_durable_terminal_counts(controller,monkeypatch,guard):
    module,run,_=controller
    terminal={"status":"failed","counts":{"logical_calls":4}}
    def failed(*args,**kwargs):
        write(run/"result.json",terminal)
        write(run/"steps/processing/calls/a001/call.json",{"status":"failed"})
        raise RuntimeError("recorded failure")
    monkeypatch.setattr(module,"analyze",failed)
    monkeypatch.setattr(module,"replay",lambda *a,**k:terminal)
    assert module.main(["--owner","/root"])==1
    receipt=guard.read(run/"restart-accounting.json")
    assert receipt["recorded_logical_calls_including_inherited"]==4
    assert receipt["new_logical_calls"]==1 and receipt["inherited_logical_calls"]==3


def test_bound_inventory_never_imports_downstream_or_operational_material(tmp_path,guard):
    parent=tmp_path/"parent"
    good=["source/manifest.json", "source/inputs/package/report.md", "source/inputs/package/replay/doc.txt",
          "source/inputs/package/.runner.lock", "source/inputs/package/execution-boundary.json",
          "task/task.json","task/calls/task/a001/call.json",
          "steps/flow/result.json","steps/graph/result.json",*guard.INHERITED_GRAPH,*guard.INHERITED_ROOT]
    bad=["task/.runner.lock","task/execution-boundary.json","task/report.md",
         "task/replay/result.json","steps/processing/calls/a001/call.json",
         "transport/processing/a001/started.json","annotation/result.json"]
    for name in good+bad:
        file(parent/name,name)
    before={p:p.read_bytes() for p in parent.rglob("*") if p.is_file()}
    assert set(guard.inherited_inventory(parent)) == set(good)
    assert before == {p:p.read_bytes() for p in parent.rglob("*") if p.is_file()}


@pytest.mark.parametrize("key",["files","copied_files","owners","inherited_logical_calls"])
def test_rehashed_import_inventory_cannot_change_accepted_boundary(prepared,guard,key):
    project,verify,run,current,_=prepared
    receipt=guard.read(run/"accepted-upstream.json")
    receipt[key]=0 if key=="inherited_logical_calls" else {}
    write(run/"accepted-upstream.json",receipt)
    with pytest.raises(ValueError,match="Inherited accepted input inventory"):
        guard.validate_inheritance(project,run,guard.read(run/"inherited-inputs.json"))


def test_preparation_calls_import_api_once_after_acceptance_and_preserves_donor(prepared,guard,monkeypatch):
    project,verify,parent,current,protocol=prepared
    prepare=load("prepare_run")
    # The sealed helper tests its original accepted identities. Supply them
    # only inside this synthetic fixture, without updating the historical file.
    for attr, key in (("IDENTITY", "guided_run_identity"), ("STEP_IDENTITY", "step_identity"),
                      ("FRAGMENTS_IDENTITY", "fragments_identity"),
                      ("PROCESSING_WIRE_IDENTITY", "processing_wire_identity"),
                      ("SOURCE_REVIEW_FRAGMENT_IDENTITY", "source_review_fragment_identity")):
        monkeypatch.setattr(prepare, attr, prepare.IDENTITIES[key])
    monkeypatch.setattr(prepare, "POLICY", {**prepare.POLICY, **prepare.POLICY_FIELDS})
    inherited=guard.read(parent/"inherited-inputs.json")
    inherited["run_directory"]=str(parent)
    monkeypatch.setattr(guard,"parent_binding",lambda project:deepcopy(inherited))
    monkeypatch.setattr(prepare,"parent_binding",lambda project:deepcopy(inherited))
    for name,value in (("PROJECT",project),("VERIFY",verify),("OLD_RUN",parent),
        ("OFFLINE",verify.parent/guard.OFFLINE_NAME),("SOURCE_SHA256","source")):
        monkeypatch.setattr(prepare,name,value)
    monkeypatch.setattr(prepare,"implementation_provenance",lambda:deepcopy(current))
    monkeypatch.setattr(prepare.skillflow,"__file__",str(project/"src/skillflow/__init__.py"))
    snapshot={"source_sha256":"source","files":list(protocol["source_file_sha256"])}
    monkeypatch.setattr(prepare,"inspect_input",lambda *a:(None,snapshot,None))
    monkeypatch.setattr(prepare,"read_snapshot",lambda *a:(None,snapshot,None))
    accepted=guard.read(prepare.OFFLINE/"offline-acceptance.json")
    accepted["restart_parent"]=inherited
    write(prepare.OFFLINE/"offline-acceptance.json",accepted)
    # Only fake temporary fixtures are cleared; a real helper never clears claims.
    for name in ("prepared-run.json","preparation-intent.json"):
        (verify/name).unlink()
    for path in (verify/"source-package").iterdir():
        path.unlink()
    (verify/"source-package").rmdir()
    protocol["source_utf8_bytes"]=100
    write(parent/"run-protocol.json",protocol)
    write(parent/"continuation-state.json",{"status":"generation_closed"})
    write(parent/"controller-finished.json",{"status":"partial"})
    original={p:p.read_bytes() for p in parent.rglob("*") if p.is_file()}
    called=[]
    def fake_import(owner,*,run_dir,config):
        assert owner==parent and config==guard.CONFIG
        assert (verify/"preparation-intent.json").is_file()
        assert not run_dir.exists()
        called.append(run_dir)
        receipt=guard.read(parent/"accepted-upstream.json")
        receipt["parent_directory"]=str(parent)
        for name in receipt["copied_files"]:
            target=run_dir/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((parent/name).read_bytes())
        write(run_dir/"accepted-upstream.json",receipt)
        manifest={"identity":prepare.IDENTITY,"implementation":current,"policy":prepare.POLICY,
            "config":config,"accepted_upstream":{"path":"accepted-upstream.json","sha256":guard.sha(run_dir/"accepted-upstream.json")}}
        manifest["manifest_sha256"]=guard.canonical(manifest)
        write(run_dir/"manifest.json",manifest)
        write(run_dir/"result.json",{"status":"prepared"})
    monkeypatch.setattr(prepare,"prepare_from_accepted_cfg",fake_import)
    prepare.main(["--owner","/root","--suffix","20261117-100001"])
    assert len(called)==1
    child=called[0]
    assert not (child/"task").exists() and not (child/"steps").exists()
    assert not (child/"transport").exists()
    assert original=={p:p.read_bytes() for p in parent.rglob("*") if p.is_file()}
    assert guard.validate_prepared(project,verify,current=current)[0]==child
    with pytest.raises(ValueError,match="already claimed"):
        prepare.main(["--owner","/root","--suffix","20261117-100002"])
    assert len(called)==1
