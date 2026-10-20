"""Pilot scheduling delegates stages and preserves pinned historical inputs."""
from pathlib import Path
import socket
from threading import Event

import pytest

from skillflow import pipeline
from skillflow.common.llm.config import LlmConfig
from skillflow.common.recording import sha_file
from tools.doe import run_joint_pipeline_pilot as pilot
from tools.doe import pilot_english


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *_a, **_kw: pytest.fail("Pilot test used network"))


@pytest.fixture
def config():
    return LlmConfig(api_key="test-secret", endpoint="https://api.deepseek.com/chat/completions",
                     model="deepseek-v4-flash", response_format="json_object")


@pytest.fixture
def prepared(tmp_path, monkeypatch, config):
    frozen = tmp_path / "historical"
    frozen.mkdir()
    original = frozen / "source.txt"
    original.write_text("Original source", encoding="utf8")
    records = {case: {"input": str(frozen), "analysis": str(original),
                     "source_sha256": sha_file(original)} for case in pilot.CASES}
    historical = {str(original): sha_file(original)}
    monkeypatch.setattr(pilot, "verify_baseline", lambda: (records, historical))
    def english_inputs(_records, directory):
        cases, files = {}, {}
        for case in pilot.CASES:
            source = directory / case / "package/source.txt"
            analysis = directory / case / "selected-analysis.json"
            source.parent.mkdir(parents=True, exist_ok=True)
            for path in (source, analysis):
                path.write_bytes(original.read_bytes())
                files[path.relative_to(directory).as_posix()] = sha_file(path)
            cases[case] = {"input": source.parent.relative_to(directory).as_posix(),
                           "analysis": analysis.relative_to(directory).as_posix()}
        return {"identity": "explicit_english_fixture", "cases": cases, "files": files}
    def verify_english(_records, directory, receipt):
        assert receipt["identity"] == "explicit_english_fixture"
        assert all(sha_file(directory / relative) == digest for relative, digest in receipt["files"].items())
    monkeypatch.setattr(pilot_english, "prepare_english_inputs", english_inputs)
    monkeypatch.setattr(pilot_english, "verify_english_inputs", verify_english)
    calls = []
    def prepare(input, analysis, **kwargs):
        calls.append((input, analysis, kwargs))
        directory = Path(kwargs["run_dir"])
        directory.mkdir(parents=True)
        return {"preparation_status": "ready"}
    monkeypatch.setattr(pipeline, "prepare_analysis_run", prepare)
    directory = tmp_path / "new-pilot"
    pilot.prepare_pilot(directory, config=config)
    return directory, original, calls


def test_pinned_three_case_inputs_have_exact_receipt_identities():
    records, preserved = pilot.verify_baseline()
    assert tuple(records) == pilot.CASES
    assert len(preserved) >= 70
    assert all(record["receipt_sha256"] == pilot.RECEIPT_SHA256[case] for case, record in records.items())


def test_preparation_delegates_only_new_production_inputs(prepared):
    directory, original, calls = prepared
    assert len(calls) == 3
    for _source, _analysis, kwargs in calls:
        assert "candidate" not in kwargs
        assert kwargs["config"]["response_format"] == "json_object"
        assert "api_key" not in kwargs["config"]
        assert Path(_source).is_relative_to(directory / "audit/english-inputs")
        assert Path(_analysis).is_relative_to(directory / "audit/english-inputs")
    assert "test-secret" not in (directory / "manifest.json").read_text(encoding="utf8")
    manifest = pilot._load(directory)
    assert manifest["identity"] == "skillflow-joint-pipeline-pilot-v8"
    assert manifest["schema_version"] == 8
    assert manifest["english_inputs"]["identity"] == "explicit_english_fixture"
    assert manifest["cases"]["001"]["input"] == str(original.parent)
    assert manifest["policy"]["task_source"] == "new_source_only_extraction_per_case"
    assert [manifest["policy"][name] for name in (
        "normal_semantic_calls_per_case", "annotation_repair_semantic_calls_per_case",
        "task_revision_semantic_calls_per_case")] == [3, 5, 6]
    assert original.read_text(encoding="utf8") == "Original source"


def test_preparation_resume_verifies_finished_cases(prepared, monkeypatch, config):
    directory, _original, original_calls = prepared
    (directory / "cases/001/manifest.json").write_text("{}", encoding="utf8")
    verified, resumed = [], []
    def verify(path, **kwargs):
        verified.append(Path(path).name)
        return {"preparation_status": "ready"}
    def prepare(_source, _analysis, **kwargs):
        resumed.append(Path(kwargs["run_dir"]).name)
        return {"preparation_status": "ready"}
    monkeypatch.setattr(pipeline, "verify_analysis_prepared", verify)
    monkeypatch.setattr(pipeline, "prepare_analysis_run", prepare)
    pilot.prepare_pilot(directory, config=config)
    assert len(original_calls) == 3
    assert verified == ["001"]
    assert resumed == ["010", "013"]


def test_failure_continues_other_cases_and_secrets_are_redacted(prepared, monkeypatch, config):
    directory, _original, _calls = prepared
    calls = []
    def execute(path, **kwargs):
        calls.append(Path(path).name)
        assert kwargs["config"]["response_format"] == "json_object"
        if Path(path).name == "001":
            raise ValueError("test-secret failure")
        return {"status": "complete", "reason": "Done", "counts": {"logical_calls": 3}}
    monkeypatch.setattr(pipeline, "run_analysis", execute)
    result = pilot.run_pilot(directory, config=config, client_factory=lambda **_kw: None)
    assert calls == list(pilot.CASES)
    assert result["cases"]["001"]["reason"] == "[REDACTED] failure"
    assert result["history_unchanged"] is True
    assert "test-secret" not in (directory / "summary.json").read_text(encoding="utf8")


def test_interruption_stops_later_cases(prepared, monkeypatch, config):
    directory, _original, _calls = prepared
    visited = []
    def execute(path, **kwargs):
        visited.append(Path(path).name)
        return {"status": "interrupted", "reason": "User stopped"}
    monkeypatch.setattr(pipeline, "run_analysis", execute)
    result = pilot.run_pilot(directory, config=config, client_factory=lambda **_kw: None)
    assert visited == ["001"]
    assert result["not_started"] == ["010", "013"]
    assert result["interrupted"] is True


def test_preexisting_interruption_does_not_start_case(prepared, monkeypatch, config):
    directory, _original, _calls = prepared
    stop = Event()
    stop.set()
    monkeypatch.setattr(pipeline, "run_analysis", lambda *_a, **_kw: pytest.fail("Started after interruption"))
    result = pilot.run_pilot(directory, config=config, client_factory=lambda **_kw: None, stop_event=stop)
    assert result["not_started"] == list(pilot.CASES)


def test_replay_uses_only_public_replay_and_preserves_run_summary(prepared, monkeypatch):
    directory, _original, _calls = prepared
    existing = '{"previous":"execution"}\n'
    (directory / "summary.json").write_text(existing, encoding="utf8")
    visited = []
    def replay(path):
        visited.append(Path(path).name)
        return {"status": "matched", "api_calls": 0}
    monkeypatch.setattr(pipeline, "replay_analysis", replay)
    monkeypatch.setattr(pipeline, "run_analysis", lambda *_a, **_kw: pytest.fail("Replay selected online entry"))
    result = pilot.run_pilot(directory, replay=True)
    assert visited == list(pilot.CASES)
    assert result["api_calls"] == 0
    assert (directory / "summary.json").read_text(encoding="utf8") == existing


def test_historical_tamper_rejected_before_client(prepared, monkeypatch, config):
    directory, original, _calls = prepared
    original.write_text("tampered", encoding="utf8")
    monkeypatch.setattr(pipeline, "run_analysis", lambda *_a, **_kw: pytest.fail("Started with changed history"))
    with pytest.raises(ValueError, match="Historical file changed"):
        pilot.run_pilot(directory, config=config, client_factory=lambda **_kw: None)


def test_english_projection_tamper_rejected_before_client(prepared, monkeypatch, config):
    directory, _original, _calls = prepared
    (directory / "audit/english-inputs/001/package/source.txt").write_text("changed", encoding="utf-8")
    monkeypatch.setattr(pipeline, "run_analysis", lambda *_a, **_kw: pytest.fail("Started with changed projection"))
    with pytest.raises(ValueError, match="inventory"):
        pilot.run_pilot(directory, config=config, client_factory=lambda **_kw: None)


def test_incomplete_english_preparation_cannot_execute_and_can_resume(prepared, monkeypatch, config):
    directory, _original, _calls = prepared
    manifest = pilot._read(directory / "manifest.json")
    manifest.pop("manifest_sha256")
    manifest["english_inputs"] = None
    manifest["files"] = {name: digest for name, digest in manifest["files"].items()
                         if not name.startswith("audit/english-inputs/")}
    (directory / "manifest.json").write_text(pilot._json(pilot._seal(manifest)), encoding="utf-8")
    with pytest.raises(ValueError, match="not fully prepared"):
        pilot._load(directory)
    # Existing case contents are mocked stage inputs, so resume just verifies them.
    for case in pilot.CASES:
        (directory / "cases" / case / "manifest.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(pipeline, "verify_analysis_prepared", lambda *_a, **_kw: {"preparation_status": "ready"})
    pilot.prepare_pilot(directory, config=config)
    assert pilot._load(directory)["english_inputs"] is not None


def test_reports_escape_reasons_and_do_not_link_missing_results(prepared):
    directory, _original, _calls = prepared
    pilot._write_reports(directory, {}, {"001": {"status": "failed", "reason": '<script>alert("x")</script>'}})
    page = (directory / "index.html").read_text(encoding="utf8")
    assert "<script>" not in page
    assert "&lt;script&gt;" in page
    assert 'href="cases/001/doe/doe-result.json"' not in page


def test_report_separates_task_repair_review_and_downstream_status(prepared):
    directory, _original, _calls = prepared
    for relative in ("cases/001/task/report.html", "cases/001/task/task.json",
                     "cases/001/refinement/task-revision/report.html",
                     "cases/001/refinement/task-revision/task.json",
                     "cases/001/refinement/task-revision/manifest.json",
                     "cases/001/refinement/repair/audit/raw-annotation.json", "metrics.md"):
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
    pilot._write_reports(directory, {}, {"001": {
        "status": "diagnostic", "task": {"status": "complete"},
        "selected_annotation": {"path": "refinement/repair"},
        "refinement": {"status": "repair_limit"}, "propagation": {"status": "complete"},
        "doe": {"status": "complete"}, "counts": {"logical_calls": 6}, "reason": "Findings remain"}})
    page = (directory / "index.html").read_text(encoding="utf8")
    assert "New source-only Task extraction" in page
    assert "3 / 5 / 6" in page
    assert "Task revision and reannotation" in page
    assert "Revised Task" in page
    assert "repair_limit" in page
    assert 'href="cases/001/refinement/task-revision/task.json"' in page
    assert 'href="metrics.md"' in page
    assert 'href="cases/001/doe/doe-result.json"' not in page
    assert 'href="cases/010/task/report.html"' not in page


def test_pilot_rejects_older_scheduler_without_migration(prepared):
    directory, _original, _calls = prepared
    manifest = pilot._read(directory / "manifest.json")
    manifest.pop("manifest_sha256")
    manifest.update(identity="skillflow-joint-pipeline-pilot-v6", schema_version=6)
    (directory / "manifest.json").write_text(pilot._json(pilot._seal(manifest)), encoding="utf-8")
    with pytest.raises(ValueError, match="identity"):
        pilot._load(directory)
