"""Pinned CLI transport with plugin catalog injection explicitly disabled.

Historical adapters and in-flight calibration freezes remain unchanged. A tiny
engineering discovery may observe new common-harness hashes, but its answer is
never accepted as a semantic result. Semantic calls require exact supplied pins.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
import subprocess
import time

from . import cli_adapter_v3 as v3
from .protocol import sha256, utc_now, write_json

SCHEMA = "skillflow-controlled-cli-v1"
DISABLED_FEATURES = ("plugins", "remote_plugin", "recommended_plugins")


def command(executable, output_dir):
    original = v3.command(executable, output_dir)
    flags = [value for name in DISABLED_FEATURES for value in ("--disable", name)]
    return [original[0], *flags, *original[1:]]


def _pins(base, developers):
    if not isinstance(developers, list) or not developers or any(not isinstance(row, list) or not row for row in developers):
        raise ValueError("Semantic requests require a complete explicit developer hash matrix")
    values = [base] + [value for row in developers for value in row]
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in values):
        raise ValueError("Semantic requests require exact explicit common-harness SHA-256 pins")


def prepare_launch(executable, prompt_path, output_dir, empty_workdir, *,
                   base_instructions_sha256=None, developer_segment_sha256=None,
                   engineering_discovery=False):
    if engineering_discovery:
        if base_instructions_sha256 is not None or developer_segment_sha256 is not None:
            raise ValueError("Engineering discovery has no previously approved semantic harness pins")
    else:
        _pins(base_instructions_sha256, developer_segment_sha256)
    prepared = v3.prepare_launch(executable, prompt_path, output_dir, empty_workdir)
    prepared.update(schema_version=SCHEMA, command=command(executable, output_dir),
        disabled_features=list(DISABLED_FEATURES), engineering_discovery_only=engineering_discovery,
        base_instructions_sha256=base_instructions_sha256,
        developer_segment_sha256=deepcopy(developer_segment_sha256))
    return prepared


def _validate(prepared):
    output, cwd = Path(prepared["output_dir"]), Path(prepared["empty_workdir"])
    if (prepared.get("schema_version") != SCHEMA or prepared.get("disabled_features") != list(DISABLED_FEATURES)
            or prepared["command"] != command(prepared["command"][0], output)
            or prepared.get("executable_sha256") != v3.PINNED_EXECUTABLE_SHA256
            or sha256(prepared["command"][0]) != v3.PINNED_EXECUTABLE_SHA256
            or prepared.get("expected_cli_version") != v3.PINNED_VERSION
            or prepared.get("runtime_expectation") != v3.EXPECTED
            or sha256(prepared["stdin_file"]) != prepared["stdin_sha256"]
            or len(Path(prepared["stdin_file"]).read_bytes()) != prepared["stdin_bytes"]
            or not cwd.is_dir() or any(cwd.iterdir())):
        raise ValueError("Controlled CLI executable, flags, runtime, complete stdin or empty cwd changed")
    if prepared.get("engineering_discovery_only") is not True:
        _pins(prepared["base_instructions_sha256"], prepared["developer_segment_sha256"])


def execute_launch(prepared, *, timeout_seconds=2700, popen=None):
    """One controlled process; preserve exact stdin and bounded waits, never retry."""
    _validate(prepared)
    output, cwd = Path(prepared["output_dir"]), Path(prepared["empty_workdir"])
    if timeout_seconds <= 0 or timeout_seconds > 2700 or output.exists():
        raise ValueError("A fresh output directory and a positive timeout of at most 45 minutes are required")
    output.mkdir(parents=True)
    write_json(output / "launch.json", {**prepared, "started_at": utc_now()}, immutable=True)
    start, waits, status, process, error = time.perf_counter(), [], "launch_failed", None, None
    with (output / "stdout.jsonl").open("wb") as stdout, (output / "stderr.txt").open("wb") as stderr:
        try:
            process = (popen or subprocess.Popen)(prepared["command"], cwd=cwd,
                stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
            write_json(output / "process-start.json", {"pid": process.pid, "started_at": utc_now(),
                "actual_cli_process_started": True}, immutable=True)
            first = True
            while True:
                remaining = timeout_seconds - (time.perf_counter() - start)
                if remaining <= 0:
                    status = "timeout"
                    process.kill()
                    process.communicate(timeout=30)
                    break
                before = time.perf_counter()
                try:
                    process.communicate(input=Path(prepared["stdin_file"]).read_bytes() if first else None,
                        timeout=min(30, remaining))
                    waits.append({"wait_seconds": time.perf_counter() - before, "result": "process_exited"})
                    status = "process_exited"
                    break
                except subprocess.TimeoutExpired:
                    waits.append({"wait_seconds": time.perf_counter() - before, "result": "still_running"})
                finally:
                    first = False
        except BaseException as caught:
            error = f"{type(caught).__name__}: {caught}"
            if process is not None and process.poll() is None:
                process.kill()
                process.communicate(timeout=30)
            status = "process_error" if process is not None else "launch_failed"
    result = {"schema_version": SCHEMA, "status": status,
        "returncode": process.returncode if process is not None else None, "error": error,
        "finished_at": utc_now(), "supervisor_waits": waits,
        "supervisor_elapsed_seconds": time.perf_counter() - start,
        "actual_cli_process_started": process is not None, "retries": 0,
        "launch_sha256": sha256(output / "launch.json")}
    write_json(output / "process-result.json", result, immutable=True)
    return result


def inspect_receipt(path, session_id, prepared, *, stdout_path=None, last_message_path=None):
    """Semantic acceptance requires exact caller-supplied common-harness pins."""
    _validate(prepared)
    if prepared.get("engineering_discovery_only") is True:
        raise ValueError("Engineering discovery cannot accept a semantic answer")
    return v3.inspect_receipt(path, session_id, prepared,
        stdout_path=stdout_path, last_message_path=last_message_path)


def discover_harness(path, session_id, prepared, *, stdout_path=None, last_message_path=None):
    """Return common-text hashes/usage only; never a semantic answer or pass."""
    _validate(prepared)
    if prepared.get("engineering_discovery_only") is not True:
        raise ValueError("Harness discovery requires an explicitly engineering-only launch")
    rows = v3.read_rows(path)
    metas = [row["payload"] for row in rows if row.get("type") == "session_meta"]
    if len(metas) != 1:
        raise ValueError("Exactly one fresh CLI session is required for engineering discovery")
    base = v3.digest((metas[0].get("base_instructions") or {}).get("text", ""))
    developers = [[v3.digest(part) for part in v3._text_parts(row["payload"], "input_text")]
        for row in rows if row.get("type") == "response_item" and row.get("payload", {}).get("type") == "message"
        and row["payload"].get("role") == "developer"]
    _pins(base, developers)
    observed = {**prepared, "base_instructions_sha256": base, "developer_segment_sha256": developers}
    _, receipt = v3.inspect_receipt(path, session_id, observed,
        stdout_path=stdout_path, last_message_path=last_message_path)
    if (receipt.get("protocol_status") != "conformant" or receipt.get("configuration_verified") is not True
            or receipt.get("provider_verified") is not True or receipt.get("usage_verified") is not True
            or receipt.get("completed") is not True):
        raise ValueError("Engineering discovery failed runtime, input, no-tool or accountable-receipt checks: " + "; ".join(receipt.get("violations", [])))
    return {"schema_version": SCHEMA + "-harness-discovery", "base_instructions_sha256": base,
        "developer_segment_sha256": developers, "disabled_features": list(DISABLED_FEATURES),
        "usage": receipt["usage"], "engineering_checks_passed": True,
        "semantic_acceptance": False, "answer_exported": False,
        "scope": "Metadata-only engineering probe; freeze these pins prospectively before any semantic request."}
