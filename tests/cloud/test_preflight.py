"""Cloud readiness is an offline check, not authority to run an experiment."""
from __future__ import annotations

import json
import subprocess

from tools.cloud import preflight


def test_codex_inspection_never_dispatches_or_serializes_raw_output(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "private-environment-sentinel")
    calls = []

    def execute(command, **kwargs):
        calls.append(command)
        if command[-1] == "--version":
            return subprocess.CompletedProcess(command, 0, "codex-cli 0.163.0-alpha.10.2\n", "")
        return subprocess.CompletedProcess(command, 0, "private-cli-output-sentinel", "")

    result = preflight.inspect_codex(cwd=tmp_path, executable="/selected/codex", execute=execute)
    assert [call[1:] for call in calls] == [["--version"], ["--help"]]
    assert result["version"] == "0.163.0-alpha.10.2"
    assert result["authentication"] == result["model_access"] == "not_checked"
    assert "sentinel" not in json.dumps(result)


def test_unrecognized_version_and_failure_output_are_not_exported(tmp_path):
    def execute(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, "SECRET", "SECRET")

    result = preflight.inspect_codex(cwd=tmp_path, executable="codex", execute=execute)
    assert result["version"] is None
    assert result["help_available"] is False
    assert "SECRET" not in json.dumps(result)


def test_absent_codex_does_not_attempt_authentication(tmp_path, monkeypatch):
    monkeypatch.setattr(preflight.shutil, "which", lambda name: None)
    result = preflight.inspect_codex(cwd=tmp_path, execute=lambda *args, **kwargs: 1 / 0)
    assert result["available"] is False
    assert result["model_access"] == "not_checked"


def test_missing_codex_does_not_fail_an_offline_environment(monkeypatch):
    calls = []

    def execute(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "ignored", "")

    monkeypatch.setattr(preflight.shutil, "which", lambda name: None)
    root = preflight.project_root()
    result = preflight.preflight(root / "tests", execute=execute)
    assert result["project_root"] == str(root)
    assert result["offline_status"] == "passed"
    assert result["model_requests"] == 0
    assert result["long_experiment"]["status"] == "not_ready"
    assert result["long_experiment"]["calibration_started"] is False
    assert len(calls) == 2
    assert all(command[1:3] == ["-I", "-c"] for command in calls)
    assert all("socket.socket.connect = forbidden" in command[3] for command in calls)
    assert all("LlmClient.__init__ = forbidden" in command[3] for command in calls)


def test_real_installed_offline_graph_and_help():
    checks = preflight.offline_checks()
    assert len(checks) == 2
    assert all(check["passed"] for check in checks), checks


def test_offline_failure_cannot_report_ready():
    def execute(command, **kwargs):
        raise subprocess.TimeoutExpired(command, 1, output="PRIVATE", stderr="PRIVATE")

    checks = preflight.offline_checks(execute=execute)
    assert all(check["passed"] is False for check in checks)
    assert all(check["error"] == "TimeoutExpired" for check in checks)
    assert "PRIVATE" not in json.dumps(checks)


def test_model_and_network_guard_rejects_calls(tmp_path):
    code = preflight._OFFLINE_GUARD + """
import socket
for operation in (lambda: socket.create_connection(("example.test", 443)),
                  lambda: LlmClient(None)):
    try:
        operation()
    except AssertionError:
        pass
    else:
        raise AssertionError("The offline guard did not reject an external operation")
"""
    result = preflight._execute([preflight.sys.executable, "-I", "-c", code], cwd=tmp_path)
    assert result.returncode == 0


def test_project_marker_rejects_unrelated_checkout(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "unrelated"\n')
    try:
        preflight.preflight(tmp_path)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("An unrelated project was accepted")


def test_setup_has_no_experiment_or_authentication_commands():
    setup = preflight.project_root() / "tools/cloud/setup.sh"
    text = setup.read_text(encoding="utf-8")
    assert 'pip install --disable-pip-version-check -e "$root" pytest' in text
    assert "preflight.py" in text
    for prohibited in ("dispatch-next", "worker --", "codex exec", "codex login", "api_key"):
        assert prohibited not in text
