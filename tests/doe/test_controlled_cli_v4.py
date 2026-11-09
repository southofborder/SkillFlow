"""Prospective CLI-profile transport tests; all process activity is synthetic."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import subprocess

import pytest

from tools.doe.real_comparison import cli_adapter_v3 as historical
from tools.doe.real_comparison import controlled_cli
from tools.doe.real_comparison import controlled_cli_v4 as adapter
from tools.doe.real_comparison.protocol import sha256

spec = importlib.util.spec_from_file_location("prospective_cli_fixture",
    Path(__file__).with_name("test_real_comparison_cli_adapter_v3.py"))
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)


@pytest.fixture
def receipt(tmp_path, monkeypatch):
    saved = fixture_module.receipt.__wrapped__(tmp_path, monkeypatch)
    executable = saved.prepared["command"][0]
    monkeypatch.setattr(adapter, "sha256", lambda path: adapter.PINNED_EXECUTABLE_SHA256
        if Path(path).resolve() == Path(executable).resolve() else sha256(path))
    saved.prepared = adapter.prepare_launch(executable, saved.prompt, saved.output, saved.cwd,
        base_instructions_sha256=saved.prepared["base_instructions_sha256"],
        developer_segment_sha256=saved.prepared["developer_segment_sha256"], request_id="synthetic-q001")
    saved.prepared["allowed_environment_dates"] = ["2026-10-20"]
    saved.rows[0]["payload"]["cli_version"] = adapter.PINNED_VERSION
    return saved


def inspect(saved, prepared=None):
    fixture_module.write_rows(saved.path, saved.rows)
    fixture_module.write_rows(saved.stdout, saved.stdout_rows)
    saved.last.write_bytes(fixture_module.ANSWER.encode("utf-8"))
    return adapter.inspect_receipt(saved.path, fixture_module.SESSION, prepared or saved.prepared,
        stdout_path=saved.stdout, last_message_path=saved.last)


def test_new_profile_keeps_old_pins_and_exact_command_unchanged(receipt):
    assert historical.PINNED_VERSION == "0.163.0-alpha.10.2"
    assert historical.PINNED_EXECUTABLE_SHA256 == "f6dbf48cb70f62649c645f26c87dc9bf84cc36986202dfad8e12fb5b8ca70312"
    assert receipt.prepared["command"] == controlled_cli.command(receipt.prepared["command"][0], receipt.output)
    assert receipt.prepared["request_id"] == "synthetic-q001"
    assert adapter.EXPECTED == historical.EXPECTED == {"model": "gpt-6.1-sol", "effort": "max", "provider": "openai"}
    answer, record = inspect(receipt)
    assert answer == fixture_module.ANSWER
    assert record["protocol_status"] == "conformant", record["violations"]


@pytest.mark.parametrize("field,value", [
    ("expected_cli_version", historical.PINNED_VERSION),
    ("executable_sha256", historical.PINNED_EXECUTABLE_SHA256),
    ("runtime_expectation", {"model": "gpt-6.1-sol", "effort": "high", "provider": "openai"}),
    ("disabled_features", ["plugins"]),
])
def test_profile_drift_prevents_any_launch(receipt, field, value):
    changed = deepcopy(receipt.prepared)
    changed[field] = value
    with pytest.raises(ValueError, match="Prospective CLI"):
        adapter.execute_launch(changed, popen=lambda *args, **kwargs: pytest.fail("Unexpected process"))


def test_exact_stdin_is_sent_once_with_no_retry(receipt):
    calls, inputs, timeouts = [], [], []
    class Process:
        pid, returncode = 321, 0
        def communicate(self, input=None, timeout=None):
            inputs.append(input)
            timeouts.append(timeout)
            if len(inputs) == 1:
                raise subprocess.TimeoutExpired(receipt.prepared["command"], timeout)
        def poll(self):
            return self.returncode
    def popen(command, **kwargs):
        calls.append(command)
        return Process()
    result = adapter.execute_launch(receipt.prepared, popen=popen)
    assert len(calls) == 1 and inputs == [receipt.prompt.read_bytes(), None]
    assert all(0 < timeout <= 30 for timeout in timeouts)
    assert result["actual_cli_process_started"] is True and result["retries"] == 0
    assert result["status"] == "process_exited"
    assert (receipt.output / "launch.json").is_file()
    assert (receipt.output / "process-start.json").is_file()
    with pytest.raises(ValueError, match="fresh output"):
        adapter.execute_launch(receipt.prepared, popen=popen)
    assert len(calls) == 1


def test_timeout_kills_one_process_and_preserves_unknown_outcome(receipt, monkeypatch):
    ticks = iter([0.0, 2701.0, 2702.0])
    monkeypatch.setattr(adapter.time, "perf_counter", lambda: next(ticks))
    calls = []
    class Process:
        pid, returncode = 322, None
        def kill(self):
            calls.append("kill")
            self.returncode = -1
        def communicate(self, input=None, timeout=None):
            calls.append((input, timeout))
        def poll(self):
            return self.returncode
    result = adapter.execute_launch(receipt.prepared, popen=lambda *args, **kwargs: Process())
    assert result["status"] == "timeout" and result["actual_cli_process_started"] is True
    assert result["retries"] == 0 and calls == ["kill", (None, 30)]
    assert "usage" not in result


@pytest.mark.parametrize("change,reason", [
    ("model", "model"), ("effort", "effort"), ("provider", "provider"),
    ("tools", "tool"), ("unknown_usage", "usage"), ("stdin", "stdin"),
])
def test_historical_strict_receipt_checks_still_reject(receipt, change, reason):
    if change in {"model", "effort"}:
        fixture_module.payload(receipt, "turn_context")[change] = "different"
    elif change == "provider":
        receipt.rows[0]["payload"]["model_provider"] = "different"
    elif change == "tools":
        receipt.rows.append(fixture_module.row("response_item", type="function_call", name="forbidden", call_id="synthetic-call"))
    elif change == "unknown_usage":
        receipt.rows = [row for row in receipt.rows if row["type"] != "token_usage_record"]
    else:
        task = next(row["payload"] for row in receipt.rows if row["type"] == "response_item"
            and row["payload"].get("id") == "synthetic-task-message")
        task["content"][0]["text"] += " Extra unapproved input."
    _, record = inspect(receipt)
    assert record["protocol_status"] == "violated"
    assert any(reason in violation.lower() for violation in record["violations"]), record["violations"]


def test_discovery_returns_only_verified_profile_and_usage(receipt):
    inspect(receipt)
    prepared = adapter.prepare_launch(receipt.prepared["command"][0], receipt.prompt, receipt.output,
        receipt.cwd, engineering_discovery=True)
    prepared["allowed_environment_dates"] = ["2026-10-20"]
    result = adapter.discover_harness(receipt.path, fixture_module.SESSION, prepared,
        stdout_path=receipt.stdout, last_message_path=receipt.last)
    assert result["engineering_checks_passed"] is True
    assert result["base_instructions_sha256"] == receipt.prepared["base_instructions_sha256"]
    assert result["developer_segment_sha256"] == receipt.prepared["developer_segment_sha256"]
    assert result["semantic_acceptance"] is False and result["answer_exported"] is False
    assert "answer" not in result and "SYNTHETIC_REASONING_CANARY" not in str(result)
    with pytest.raises(ValueError, match="cannot accept"):
        adapter.inspect_receipt(receipt.path, fixture_module.SESSION, prepared)
    receipt.rows.append(fixture_module.row("response_item", type="function_call", name="forbidden", call_id="synthetic-call"))
    fixture_module.write_rows(receipt.path, receipt.rows)
    with pytest.raises(ValueError, match="strict.*tool"):
        adapter.discover_harness(receipt.path, fixture_module.SESSION, prepared,
            stdout_path=receipt.stdout, last_message_path=receipt.last)
