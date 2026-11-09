"""Focused controlled-transport checks with the existing fictional receipt."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import subprocess

import pytest

from tools.doe.real_comparison import controlled_cli as controlled
from tools.doe.real_comparison import cli_adapter_v3 as v3

spec = importlib.util.spec_from_file_location("controlled_cli_fictional_fixture", Path(__file__).with_name("test_real_comparison_cli_adapter_v3.py"))
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)


@pytest.fixture
def receipt(tmp_path, monkeypatch):
    saved = fixture_module.receipt.__wrapped__(tmp_path, monkeypatch)
    monkeypatch.setattr(controlled, "sha256", v3.sha256)
    saved.prepared = controlled.prepare_launch(saved.prepared["command"][0], saved.prompt, saved.output, saved.cwd,
        base_instructions_sha256=saved.prepared["base_instructions_sha256"],
        developer_segment_sha256=saved.prepared["developer_segment_sha256"])
    saved.prepared["allowed_environment_dates"] = ["2026-10-20"]
    fixture_module.write_rows(saved.path, saved.rows)
    fixture_module.write_rows(saved.stdout, saved.stdout_rows)
    saved.last.write_bytes(fixture_module.ANSWER.encode("utf-8"))
    return saved


def inspect(receipt):
    return controlled.inspect_receipt(receipt.path, fixture_module.SESSION, receipt.prepared,
        stdout_path=receipt.stdout, last_message_path=receipt.last)


def test_exact_disable_flags_preserve_every_other_v3_argument(receipt):
    command = receipt.prepared["command"]
    assert command[1:7] == ["--disable", "plugins", "--disable", "remote_plugin", "--disable", "recommended_plugins"]
    assert [command[0], *command[7:]] == v3.command(command[0], receipt.output)
    assert inspect(receipt)[1]["protocol_status"] == "conformant"


def test_execute_sends_exact_stdin_once_and_preserves_process_evidence(receipt):
    calls, inputs = [], []
    class Process:
        pid, returncode = 123, 0
        def communicate(self, input=None, timeout=None):
            inputs.append(input)
            if len(inputs) == 1:
                raise subprocess.TimeoutExpired(receipt.prepared["command"], timeout)
        def poll(self):
            return self.returncode
    def fake_process(command, **kwargs):
        calls.append((command, kwargs))
        return Process()
    result = controlled.execute_launch(receipt.prepared, popen=fake_process)
    assert result["status"] == "process_exited" and result["actual_cli_process_started"] is True
    assert len(calls) == 1 and inputs == [receipt.prompt.read_bytes(), None]
    assert (receipt.output / "process-start.json").is_file() and (receipt.output / "launch.json").is_file()


def test_flag_or_pin_drift_rejects_before_any_process(receipt):
    changed = deepcopy(receipt.prepared)
    changed["command"].remove("remote_plugin")
    calls = []
    with pytest.raises(ValueError, match="flags"):
        controlled.execute_launch(changed, popen=lambda *a, **k: calls.append(a))
    assert calls == []
    with pytest.raises(ValueError, match="explicit"):
        controlled.prepare_launch(receipt.prepared["command"][0], receipt.prompt, receipt.output, receipt.cwd)
    changed = deepcopy(receipt.prepared)
    changed["base_instructions_sha256"] = "0" * 64
    answer, record = controlled.inspect_receipt(receipt.path, fixture_module.SESSION, changed,
        stdout_path=receipt.stdout, last_message_path=receipt.last)
    assert record["protocol_status"] == "violated" and any("base instructions" in reason for reason in record["violations"])


def test_discovery_exports_hashes_and_usage_but_never_semantic_answer(receipt):
    discovery = controlled.prepare_launch(receipt.prepared["command"][0], receipt.prompt, receipt.output,
        receipt.cwd, engineering_discovery=True)
    discovery["allowed_environment_dates"] = ["2026-10-20"]
    result = controlled.discover_harness(receipt.path, fixture_module.SESSION, discovery,
        stdout_path=receipt.stdout, last_message_path=receipt.last)
    assert result["base_instructions_sha256"] == receipt.prepared["base_instructions_sha256"]
    assert result["developer_segment_sha256"] == receipt.prepared["developer_segment_sha256"]
    assert result["semantic_acceptance"] is False and result["answer_exported"] is False
    assert "answer" not in result and "SYNTHETIC_REASONING_CANARY" not in str(result)
    with pytest.raises(ValueError, match="cannot accept"):
        controlled.inspect_receipt(receipt.path, fixture_module.SESSION, discovery)
