"""Prospective transport profile for the separately adopted October 24 CLI.

This module leaves all historical transport pins and frozen runs unchanged. It
reuses the strict v3 receipt inspector with an explicitly prepared new executable
profile; import, preparation and receipt inspection never start a process.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import time

from . import cli_adapter_v3 as v3
from . import controlled_cli as historical
from .protocol import sha256, utc_now, write_json

SCHEMA = "skillflow-controlled-cli-v4"
PINNED_VERSION = "0.163.0-alpha.11.2"
PINNED_EXECUTABLE_SHA256 = "c81ed464e5e7cafd09a5fa26af390c480bed8e9fab2a87a54b285fbd56e7122a"
EXPECTED = {"model": "gpt-6.1-sol", "effort": "max", "provider": "openai"}
DISABLED_FEATURES = historical.DISABLED_FEATURES


def command(executable, output_dir):
    """Preserve every inspected command argument, including disabled catalogs."""
    return historical.command(executable, output_dir)


def prepare_launch(executable, prompt_path, output_dir, empty_workdir, *,
                   base_instructions_sha256=None, developer_segment_sha256=None,
                   engineering_discovery=False, request_id=None):
    if engineering_discovery:
        if base_instructions_sha256 is not None or developer_segment_sha256 is not None:
            raise ValueError("Engineering discovery has no previously adopted semantic harness pins")
    else:
        historical._pins(base_instructions_sha256, developer_segment_sha256)
    executable, prompt = Path(executable).resolve(), Path(prompt_path).resolve()
    output, cwd = Path(output_dir).resolve(), Path(empty_workdir).resolve()
    raw = prompt.read_bytes()
    raw.decode("utf-8")
    if sha256(executable) != PINNED_EXECUTABLE_SHA256:
        raise ValueError("The prospective CLI executable differs from its exact adopted SHA-256")
    if not cwd.is_dir() or any(cwd.iterdir()):
        raise ValueError("A fresh CLI request requires its own empty working directory")
    date_start = datetime.now(timezone(timedelta(hours=8)))
    prepared = {"schema_version": SCHEMA, "transport": v3.TRANSPORT,
        "command": command(executable, output), "executable_sha256": PINNED_EXECUTABLE_SHA256,
        "expected_cli_version": PINNED_VERSION, "stdin_file": str(prompt),
        "stdin_sha256": sha256(prompt), "stdin_bytes": len(raw),
        "output_dir": str(output), "empty_workdir": str(cwd),
        "runtime_expectation": dict(EXPECTED), "configuration_is_verified": False,
        "disabled_features": list(DISABLED_FEATURES),
        "engineering_discovery_only": engineering_discovery,
        "base_instructions_sha256": base_instructions_sha256,
        "developer_segment_sha256": deepcopy(developer_segment_sha256),
        "allowed_environment_dates": sorted({date_start.date().isoformat(),
            (date_start + timedelta(seconds=2700)).date().isoformat()})}
    if request_id is not None:
        if not isinstance(request_id, str) or not request_id:
            raise ValueError("A supplied request identity must be a nonempty string")
        prepared["request_id"] = request_id
    return prepared


def _validate(prepared):
    output, cwd = Path(prepared["output_dir"]), Path(prepared["empty_workdir"])
    if (prepared.get("schema_version") != SCHEMA
            or prepared.get("disabled_features") != list(DISABLED_FEATURES)
            or prepared["command"] != command(prepared["command"][0], output)
            or prepared.get("executable_sha256") != PINNED_EXECUTABLE_SHA256
            or sha256(prepared["command"][0]) != PINNED_EXECUTABLE_SHA256
            or prepared.get("expected_cli_version") != PINNED_VERSION
            or prepared.get("runtime_expectation") != EXPECTED
            or prepared.get("transport") != v3.TRANSPORT
            or sha256(prepared["stdin_file"]) != prepared["stdin_sha256"]
            or len(Path(prepared["stdin_file"]).read_bytes()) != prepared["stdin_bytes"]
            or not cwd.is_dir() or any(cwd.iterdir())):
        raise ValueError("Prospective CLI executable, flags, runtime, complete stdin or empty cwd changed")
    if prepared.get("engineering_discovery_only") is not True:
        historical._pins(prepared["base_instructions_sha256"], prepared["developer_segment_sha256"])


def execute_launch(prepared, *, timeout_seconds=2700, popen=None):
    """Start one explicitly authorized process with the unchanged bounded waits."""
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
    """Use the historical strict checks with prospectively explicit harness pins."""
    _validate(prepared)
    if prepared.get("engineering_discovery_only") is True:
        raise ValueError("Engineering discovery cannot accept a semantic answer")
    return v3.inspect_receipt(path, session_id, prepared,
        stdout_path=stdout_path, last_message_path=last_message_path)


def discover_harness(path, session_id, prepared, *, stdout_path=None, last_message_path=None):
    """Export only hashes and usage after every strict protocol check succeeds."""
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
    historical._pins(base, developers)
    observed = {**prepared, "base_instructions_sha256": base, "developer_segment_sha256": developers}
    _, receipt = v3.inspect_receipt(path, session_id, observed,
        stdout_path=stdout_path, last_message_path=last_message_path)
    if (receipt.get("protocol_status") != "conformant" or any(receipt.get(key) is not True for key in
            ("configuration_verified", "provider_verified", "usage_verified", "completed"))):
        raise ValueError("Engineering discovery failed strict runtime, input, no-tool or usage checks: "
                         + "; ".join(receipt.get("violations", [])))
    return {"schema_version": SCHEMA + "-harness-discovery", "base_instructions_sha256": base,
        "developer_segment_sha256": developers, "disabled_features": list(DISABLED_FEATURES),
        "cli_version": PINNED_VERSION, "executable_sha256": PINNED_EXECUTABLE_SHA256,
        "runtime": dict(EXPECTED), "usage": receipt["usage"], "engineering_checks_passed": True,
        "semantic_acceptance": False, "answer_exported": False,
        "scope": "Metadata-only engineering probe; freeze these pins prospectively before semantic dispatch."}
