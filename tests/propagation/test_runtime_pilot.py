"""The runtime pilot reuses frozen graphs and never invokes graph extraction."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
import importlib.util
from pathlib import Path
from threading import Event

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.inputs.snapshot import freeze_input
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.common.recording import injected_factory
from tests.propagation.annotation.helpers import FakeClient, graph


@pytest.fixture
def pilot():
    path = project_root() / "tools/propagation/run_runtime_pilot.py"
    spec = importlib.util.spec_from_file_location("runtime_pilot_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def prepared(pilot, tmp_path, monkeypatch):
    writer = ArtifactWriter(())
    package = tmp_path / "package"
    package.mkdir()
    (package / "SKILL.md").write_text("---\nname: fixture\n---\n读取文件，在本地处理后返回。\n", encoding="utf-8")
    old = tmp_path / "historical"
    cfg = graph()
    cases = []
    for n in ("001", "010", "013"):
        base = old / n
        metadata = freeze_input(package, base / "source", writer)
        writer.json(base / "analysis.json", {"cfg": cfg})
        writer.json(base / "selection.json", {"graph_sha256": canonical_sha256(cfg)})
        cases.append({"case_id": n, "sample_id": "fixture", "input": str(base / "source/inputs/package"),
                      "analysis": str(base / "analysis.json"), "selection": str(base / "selection.json"),
                      "analysis_sha256": sha_file(base / "analysis.json"), "selection_sha256": sha_file(base / "selection.json"),
                      "source_sha256": metadata["source_sha256"], "graph_sha256": canonical_sha256(cfg),
                      "package_bytes_sha256": metadata["package_bytes_sha256"],
                      "source_inventory": {item["path"]: {"bytes": item["size"], "sha256": item["raw_sha256"]}
                                           for item in metadata["files"]}})
    monkeypatch.setattr(pilot, "plan", lambda: deepcopy(cases))
    run = tmp_path / "processing-v1-test"
    pilot.prepare(run)
    return pilot, run


def test_real_pins_check_frozen_selection_source_and_round_cfg(pilot):
    cases = pilot.plan()
    assert [case["case_id"] for case in cases] == ["001", "010", "013"]
    assert all("source-boundaries-v1-20260928-112118" in case["analysis"] for case in cases)
    assert len({case["graph_sha256"] for case in cases}) == 3
    assert pilot.POLICY["extract_cfg"] is False
    assert pilot.POLICY["planned_logical_calls"] == 3
    assert pilot.public_config()["response_format"] == "json_object"


def test_refresh_verifies_only_frozen_skeleton_without_deleting(prepared, tmp_path):
    pilot, previous = prepared
    target = tmp_path / "processing-v1-refreshed"
    for case in pilot.plan():
        destination = target / "cases" / case["case_id"]
        destination.mkdir(parents=True)
        for name in ("selected-analysis.json", "selection.json", "cfg-review.md"):
            (destination / name).write_bytes((previous / "cases" / case["case_id"] / name).read_bytes())
    preserved = {path: path.read_bytes() for path in target.rglob("selected-analysis.json")}
    manifest = pilot.prepare(target)
    assert manifest["schema_version"] == 4 and manifest["prepared_at"]
    assert all(path.read_bytes() == value for path, value in preserved.items())
    assert not list(target.rglob("call.json")) and not list(target.rglob("doe-input.json"))


def test_refresh_rejects_remaining_results_and_wrong_frozen_cfg(prepared, tmp_path):
    pilot, previous = prepared
    target = tmp_path / "processing-v1-rejected"
    for case in pilot.plan():
        destination = target / "cases" / case["case_id"]
        destination.mkdir(parents=True)
        for name in ("selected-analysis.json", "selection.json"):
            (destination / name).write_bytes((previous / "cases" / case["case_id"] / name).read_bytes())
    result = target / "cases/001/result.json"
    result.write_text("{}")
    with pytest.raises(ValueError, match="previous calls, results"):
        pilot.prepare(target)
    assert result.read_text() == "{}"
    result.unlink()
    (target / "cases/001/selected-analysis.json").write_text("{}")
    with pytest.raises(ValueError, match="differs from pinned inputs"):
        pilot.prepare(target)
    assert not (target / "manifest.json").exists()


def test_three_once_resume_and_offline_replay(prepared, monkeypatch):
    pilot, run = prepared
    clients = []
    def factory(writer, on_record):
        client = FakeClient()
        clients.append(client)
        return injected_factory(client)(writer, on_record)
    result = pilot.execute(run, client_factory=factory)
    assert result["logical_calls"] == 3
    assert result["annotation_statuses"] == {"complete": 3}
    assert len(clients) == 3 and all(len(client.prompts) == 1 for client in clients)
    def forbidden(*args, **kwargs):
        pytest.fail("offline/recovery must not create an online client")
    monkeypatch.setattr(pilot, "streaming_factory", forbidden)
    assert pilot.execute(run, client_factory=forbidden)["logical_calls"] == 3
    replay = pilot.execute(run, replay=True)
    assert replay["annotation_statuses"] == result["annotation_statuses"]
    assert replay["propagation_statuses"] == result["propagation_statuses"]
    assert replay["logical_calls"] == 3
    assert len(clients) == 3
    for n in ("001", "010", "013"):
        assert read_json(run / "cases" / n / "propagation/replay/summary.json")["status"] == "matched"
    assert "不是执行日志" in (run / "index.html").read_text("utf8")


def test_runtime_pilot_refuses_previous_outer_identity_before_calls(prepared, monkeypatch):
    pilot, run = prepared
    manifest = read_json(run / "manifest.json")
    manifest.update(schema_version=3, identity="skill-ir-processing-pilot3-v3")
    ArtifactWriter(()).json(run / "manifest.json", manifest)
    monkeypatch.setattr(pilot, "streaming_factory", lambda *a, **k: pytest.fail("prior run must not start calls"))
    with pytest.raises(ValueError, match="identity changed"):
        pilot.execute(run)


def test_bad_completed_response_does_not_rerun_or_stop_other_cases(prepared):
    pilot, run = prepared
    calls = []
    class Bad:
        def complete(self, prompt):
            calls.append(prompt)
            return "{}"
    first = pilot.execute(run, client_factory=injected_factory(Bad()))
    assert first["annotation_statuses"] == {"invalid_response": 3}
    assert all(not (run / "cases" / n / "propagation/doe-input.json").exists() for n in ("001", "010", "013"))
    pilot.execute(run, client_factory=lambda: pytest.fail("no quality retry"))
    assert len(calls) == 3


def test_saved_semantic_failure_without_call_uses_local_replay(prepared, monkeypatch):
    pilot, run = prepared
    case = pilot.plan()[0]
    failure = {"status": "semantic_failure", "reason": "已保存的材料能力失败。", "counts": {"logical_calls": 0}}
    annotation_dir = run / "cases" / case["case_id"] / "annotation"
    ArtifactWriter(()).json(annotation_dir / "result.json", failure)
    replayed = []
    monkeypatch.setattr(pilot, "replay_run", lambda path: replayed.append(path) or deepcopy(failure))
    monkeypatch.setattr(pilot, "run_annotation", lambda *a, **k: pytest.fail("semantic failure must not start a fresh call"))
    result = pilot.run_case(run, case, config=pilot.public_config(), factory=None, secrets=(), stopping=Event())
    assert replayed == [annotation_dir]
    assert result["annotation"] == failure and result["propagation"] == "not_run"


def test_interrupt_does_not_start_later_cases(prepared):
    pilot, run = prepared
    calls = []
    class Interrupted:
        def complete(self, prompt):
            calls.append(prompt)
            raise KeyboardInterrupt("test interrupted")
    result = pilot.execute(run, client_factory=injected_factory(Interrupted()))
    assert len(calls) == 1
    assert result["annotation_statuses"] == {"interrupted": 1, "not_run": 2}
    assert not (run / "cases/010/annotation/calls").exists()


def test_prepared_only_replay_has_no_calls(prepared, monkeypatch):
    pilot, run = prepared
    monkeypatch.setattr(pilot, "streaming_factory", lambda *a, **k: pytest.fail("network"))
    result = pilot.execute(run, replay=True)
    assert result["logical_calls"] == 0 and result["annotation_statuses"] == {"not_run": 3}


def test_existing_prepare_and_material_tampering_fail(prepared):
    pilot, run = prepared
    with pytest.raises(ValueError, match="new empty"):
        pilot.prepare(run)
    path = run / "cases/001/selected-analysis.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="analysis copy changed"):
        pilot.execute(run, client_factory=lambda: pytest.fail("network"))


def test_contract_and_source_identity_change_reject_before_client(prepared, monkeypatch):
    pilot, run = prepared
    original = pilot.expected_manifest
    def changed():
        manifest = original()
        manifest["execution_model"]["sha256"] = "0" * 64
        return manifest
    monkeypatch.setattr(pilot, "expected_manifest", changed)
    with pytest.raises(ValueError, match="identity changed"):
        pilot.execute(run, client_factory=lambda: pytest.fail("network"))


def test_output_protects_input_ancestors_and_old_run(pilot):
    for path in (pilot.ORIGIN, pilot.ORIGIN / "processing-v1-child", pilot.PACKAGE, pilot.ROOT):
        with pytest.raises(ValueError, match="overlaps"):
            pilot.checked_output(path)


def test_driver_failure_is_separate_and_other_cases_continue(prepared, monkeypatch):
    pilot, run = prepared
    original = pilot.run_case
    def first_fails(directory, case, **kwargs):
        if case["case_id"] == "001":
            raise OSError("local output failure")
        return original(directory, case, **kwargs)
    monkeypatch.setattr(pilot, "run_case", first_fails)
    result = pilot.execute(run, client_factory=injected_factory(FakeClient()))
    assert result["cases"][0]["driver_status"] == "execution_error"
    assert result["cases"][0]["annotation"] == "not_run"
    assert result["cases"][0]["driver_error"]["error"] == "OSError: local output failure"
    assert result["logical_calls"] == 2
    assert result["annotation_statuses"] == {"not_run": 1, "complete": 2}
    assert "local output failure" in (run / "report.md").read_text("utf8")


def test_driver_interrupt_is_saved_and_stops_the_batch(prepared, monkeypatch):
    pilot, run = prepared
    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt("driver interrupted")
    monkeypatch.setattr(pilot, "run_case", interrupt)
    result = pilot.execute(run, client_factory=lambda *a: pytest.fail("no call"))
    assert result["cases"][0]["driver_status"] == "interrupted"
    assert result["cases"][1]["driver_status"] == "not_run"
    assert "KeyboardInterrupt" in result["cases"][0]["driver_error"]["error"]


def test_uncertain_recorded_request_is_not_automatically_resent(prepared):
    pilot, run = prepared
    calls = []
    class Failed:
        def complete(self, prompt):
            calls.append(prompt)
            raise TimeoutError("uncertain request")
    result = pilot.execute(run, client_factory=injected_factory(Failed()))
    assert result["annotation_statuses"] == {"execution_error": 3}
    pilot.execute(run, client_factory=lambda *a: pytest.fail("uncertain request must not resend"))
    assert len(calls) == 3


def test_historical_selection_mismatch_is_not_reinterpreted(pilot, monkeypatch):
    original = pilot.read_json
    def changed(path):
        value = original(path)
        if Path(path).name == "selection.json":
            value["graph_sha256"] = "0" * 64
        return value
    monkeypatch.setattr(pilot, "read_json", changed)
    with pytest.raises(ValueError, match="historical source/selection/graph"):
        pilot.plan()
