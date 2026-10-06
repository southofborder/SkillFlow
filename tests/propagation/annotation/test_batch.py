"""Pinned corpus selection and bounded isolated one-call batch scheduling."""

from skillflow.common.paths import project_root, resolve_material_path

from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace

import pytest


PACKAGE = project_root()
SCRIPT = PACKAGE / "tools/propagation/annotation/run_review_set.py"


@pytest.fixture(scope="module")
def driver():
    spec = importlib.util.spec_from_file_location("security_profile_batch_test_driver", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pinned_plan(driver):
    return driver.build_plan()


@pytest.fixture
def stubbed(driver, pinned_plan, monkeypatch):
    prepared, executed, replayed = [], [], []
    created_clients = []

    def result(identifier, status="complete"):
        return {"status": status, "reason": "", "profiles": {
            f"ir_{identifier}": {"operator": ["tool", "llm"], "roles": ["source", "sink"],
                                "effects": ["net_send", "net_receive", "model_observe"], "evidences": []}},
                 "validation": {"status": "passed"},
                "counts": {"logical_calls": 1, "http_attempts": 1, "http_retries": 0}}

    def prepare(source, analysis, *, run_dir, config=None, **kwargs):
        prepared.append((source, analysis, run_dir, config))
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "manifest.json").write_text("{}", encoding="utf-8")
        return {"preparation_status": "ready"}

    def run(run_dir, **kwargs):
        executed.append((run_dir, kwargs))
        value = result(run_dir.name)
        (run_dir / "calls/annotation/a001").mkdir(parents=True, exist_ok=True)
        (run_dir / "calls/annotation/a001/call.json").write_text("{}", encoding="utf-8")
        (run_dir / "result.json").write_text(json.dumps(value), encoding="utf-8")
        return value

    def replay(run_dir):
        replayed.append(run_dir)
        return json.loads((run_dir / "result.json").read_text(encoding="utf-8"))

    runner = SimpleNamespace(prepare_run=prepare, run_annotation=run, replay_run=replay,
                             verify_prepared=lambda *args, **kwargs: {"preparation_status": "ready"})
    monkeypatch.setitem(sys.modules, "skillflow.propagation.annotation.runner", runner)
    monkeypatch.setattr(driver, "build_plan", lambda: pinned_plan)
    import skillflow.common.recording as recording

    def factory(config, *, env_file=None):
        created_clients.append((config, env_file))
        return object(), ("test-only-credential",)

    monkeypatch.setattr(recording, "streaming_factory", factory)
    return SimpleNamespace(runner=runner, prepared=prepared, executed=executed, replayed=replayed,
                           created_clients=created_clients, result=result)


def test_source_selection_is_exact_frozen_30_and_f03_third_round(driver, pinned_plan):
    assert len(pinned_plan) == 30
    assert [item["index"] for item in pinned_plan] == list(range(1, 31))
    assert tuple(item["sample_id"] for item in pinned_plan) == driver.SAMPLE_IDS
    assert [item["sample_id"] for item in pinned_plan if item["repetition"] != 1] == ["F03"]
    assert pinned_plan[14]["repetition"] == 3
    for item in pinned_plan:
        assert "/frozen/corpus/inputs/" in Path(item["package_path"]).as_posix()
        assert "/graph/baseline/runs/" in Path(item["analysis_path"]).as_posix()
        assert "semantic_feedback" not in item["analysis_path"]
        assert driver.sha_file(Path(item["analysis_path"])) == item["analysis_sha256"]


def test_prepare_freezes_all_selected_cases_without_credentials_or_client(driver, stubbed, tmp_path):
    result = driver.execute(tmp_path / "prepared", mode="prepare")
    assert result["summary"]["statuses"] == {"prepared": 30}
    assert len(stubbed.prepared) == 30
    assert not stubbed.executed and not stubbed.created_clients
    manifest = driver.read_json(tmp_path / "prepared/manifest.json")
    assert manifest["workers"] == 3
    assert manifest["limits"] == {"logical_calls_per_case": 1, "logical_calls_total": 30}
    for case, (source, analysis, _, _) in zip(manifest["cases"], stubbed.prepared):
        assert source == driver.REPOSITORY_ROOT / case["package_path"]
        assert analysis == driver.REPOSITORY_ROOT / case["analysis_path"]
        assert case["analysis_sha256"]
        assert case["source_inventory_sha256"]
        assert case["instruction_count"] > 0
    assert "api_key" not in json.dumps(manifest).lower()


def test_run_calls_each_case_once_and_only_supplies_runner_configuration(driver, stubbed, tmp_path):
    result = driver.execute(tmp_path / "live", mode="run", env_file=tmp_path / ".env")
    assert result["summary"]["statuses"] == {"complete": 30}
    assert len(stubbed.executed) == 30
    assert len({path.name for path, _ in stubbed.executed}) == 30
    assert len(stubbed.created_clients) == 1
    for path, kwargs in stubbed.executed:
        assert path.name in {f"{index:03}" for index in range(1, 31)}
        assert set(kwargs) == {"client_factory", "config", "secrets", "stop_event", "progress"}
        assert kwargs["config"]["model"] == "deepseek-v4-flash"
    assert result["summary"]["known_counts"]["logical_calls"] == 30
    assert result["summary"]["effects"]["model_observe"] == 30
    assert result["assistant_review"] == "pending"
    assert result["user_confirmed"] is False


def test_single_case_failure_does_not_block_others_and_errors_are_redacted(driver, stubbed, tmp_path):
    original = stubbed.runner.run_annotation

    def run(path, **kwargs):
        if path.name == "005":
            raise ValueError("test-only-credential fixture failure")
        return original(path, **kwargs)

    stubbed.runner.run_annotation = run
    result = driver.execute(tmp_path / "failure", mode="run")
    assert result["cases"]["005"]["status"] == "execution_error"
    assert result["summary"]["statuses"] == {"complete": 29, "execution_error": 1}
    assert result["summary"]["unavailable_count_cases"] == ["005"]
    for path in (tmp_path / "failure").rglob("*"):
        if path.is_file():
            assert b"test-only-credential" not in path.read_bytes()


def test_interruption_stops_queued_cases_and_replay_replays_already_started(driver, stubbed, tmp_path):
    original = stubbed.runner.run_annotation
    barrier = threading.Barrier(3)

    def run(path, **kwargs):
        barrier.wait(timeout=5)
        value = original(path, **kwargs)
        value["status"] = "interrupted"
        kwargs["stop_event"].set()
        (path / "result.json").write_text(json.dumps(value), encoding="utf-8")
        return value

    stubbed.runner.run_annotation = run
    live = driver.execute(tmp_path / "interrupted", mode="run", workers=3)
    assert len(stubbed.executed) == 3
    assert live["summary"]["statuses"] == {"interrupted": 3, "not_run": 27}

    # The 27 prepared-but-not-called cases have manifests but no response.
    # Real per-case replay returns not_run in this case; mirror that boundary.
    old_replay = stubbed.runner.replay_run

    def replay(path):
        if not (path / "result.json").exists():
            return driver._missing("not_run", "此前已中断，未启动后续案例")
        return old_replay(path)

    stubbed.runner.replay_run = replay
    replayed = driver.execute(tmp_path / "interrupted", mode="replay")
    assert replayed["cases"] == live["cases"]
    assert len(stubbed.replayed) == 3
    assert len(stubbed.created_clients) == 1


def test_at_most_worker_limit_is_submitted_and_running(driver, stubbed, tmp_path, monkeypatch):
    peak = 0
    submitted = 0
    running = 0
    lock = threading.Lock()
    release = threading.Event()
    reached = threading.Event()
    original = stubbed.runner.run_annotation

    class ObservedExecutor(ThreadPoolExecutor):
        def submit(self, *args, **kwargs):
            nonlocal submitted
            submitted += 1
            return super().submit(*args, **kwargs)

    def run(path, **kwargs):
        nonlocal running, peak
        with lock:
            running += 1
            peak = max(peak, running)
            if running == 3:
                reached.set()
        assert release.wait(timeout=5)
        value = original(path, **kwargs)
        with lock:
            running -= 1
        return value

    monkeypatch.setattr(driver, "ThreadPoolExecutor", ObservedExecutor)
    stubbed.runner.run_annotation = run
    with ThreadPoolExecutor(max_workers=1) as outer:
        future = outer.submit(driver.execute, tmp_path / "bounded", mode="run", workers=3)
        try:
            assert reached.wait(timeout=5)
            time.sleep(0.05)
            assert submitted == 3
        finally:
            release.set()
        result = future.result(timeout=20)
    assert peak <= 3
    assert result["summary"]["statuses"] == {"complete": 30}


def test_replay_never_loads_config_environment_or_online_factory(driver, stubbed, tmp_path, monkeypatch):
    directory = tmp_path / "replay"
    live = driver.execute(directory, mode="run", workers=1)

    def reject(*args, **kwargs):
        raise AssertionError("offline replay attempted online dependency")

    import skillflow.common.recording as recording
    monkeypatch.setattr(recording, "streaming_factory", reject)
    monkeypatch.setattr(driver, "public_config", reject)
    replayed = driver.execute(directory, mode="replay")
    assert replayed["cases"] == live["cases"]
    assert replayed["summary"] == live["summary"]
    assert len(stubbed.replayed) == 30


@pytest.mark.parametrize("field,value", [("workers", 8), ("identity", "old-flow"), ("schema_version", 0),
                                         ("profile_schema_version", "security-profile-v1"),
                                         ("profile_schema_version", "security-profile-v2")])
def test_manifest_identity_changes_refuse_resume(driver, stubbed, tmp_path, field, value):
    directory = tmp_path / "changed"
    driver.execute(directory, mode="prepare", workers=2)
    manifest = driver.read_json(directory / "manifest.json")
    manifest[field] = value
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    # An explicit worker count detects a tampered setting; all other identities
    # are reconstructed from current pinned sources, not trusted from manifest.
    with pytest.raises(ValueError, match="identity mismatch|Unsupported security-profile experiment version"):
        driver.execute(directory, mode="run", workers=2)
    assert not stubbed.created_clients


def test_effect_coverage_counts_each_ir_once_but_preserves_steps(driver):
    effects = ["model_observe", "context_write", "transform", "model_observe", "context_write"]
    outcome = {"status": "complete", "profiles": {"ir": {"effects": effects}}}
    result = driver._summary({"001": outcome})
    assert result["effects"]["model_observe"] == 1
    assert result["effects"]["transform"] == 1
    assert result["effects"]["context_write"] == 1
    assert outcome["profiles"]["ir"]["effects"] == effects


def test_output_cannot_overlap_frozen_baseline_or_delivery(driver, stubbed):
    for path in (driver.BASELINE / "runs/new", driver.REPOSITORY_ROOT / "result/security",
                 driver.REPOSITORY_ROOT / "dataset/security"):
        with pytest.raises(ValueError, match="overlap"):
            driver.execute(path, mode="prepare")


def test_report_keeps_semantic_failure_and_error_separate_from_record_complete(driver, stubbed, tmp_path):
    original = stubbed.runner.run_annotation

    def run(path, **kwargs):
        result = original(path, **kwargs)
        if path.name == "001":
            result["status"] = "semantic_failure"
            result["failure"] = {"reason": "必要判断存在明确材料冲突"}
        if path.name == "002":
            result["status"] = "invalid_response"
            result["profiles"] = {}
        return result

    stubbed.runner.run_annotation = run
    result = driver.execute(tmp_path / "report", mode="run")
    assert result["summary"]["statuses"] == {"semantic_failure": 1, "invalid_response": 1, "complete": 28}
    report = (tmp_path / "report/report.md").read_text(encoding="utf-8")
    assert "无法完成必要判断" in report and "响应无效" in report
    assert "标注记录完整" in report and "不保证模型" in report
    assert "助手复核尚待" in report
    assert "执行主体（operator）" in report
    assert "不等于空操作" in report and "入口与出口状态相同" in report
    assert "context_write（上下文写入）" in report


@pytest.mark.parametrize("workers", [0, 9, True, "3"])
def test_invalid_worker_counts_rejected(driver, stubbed, tmp_path, workers):
    with pytest.raises(ValueError, match="workers"):
        driver.execute(tmp_path / "unused", workers=workers)


def test_replay_rejects_env_file_and_missing_run(driver, stubbed, tmp_path):
    with pytest.raises(ValueError, match="environment"):
        driver.execute(tmp_path / "missing", mode="replay", env_file=tmp_path / ".env")
    with pytest.raises(ValueError, match="existing experiment"):
        driver.execute(tmp_path / "missing", mode="replay")
