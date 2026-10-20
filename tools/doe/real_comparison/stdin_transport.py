"""Proposed fresh-CLI calibration transport, not an approved formal adapter.

Preparing a launch is read-only. Executing a probe would be a protocol amendment:
fresh CLI sessions do not have the collaboration tool's fork_turns field. This
module is deliberately disconnected from the formal workflow dispatcher.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from .protocol import SCHEMA, sha256, utc_now, write_json


def prepare_launch(executable, prompt_path, output_dir):
    executable, prompt = Path(executable).resolve(), Path(prompt_path).resolve()
    output = Path(output_dir).resolve()
    raw = prompt.read_bytes()
    raw.decode("utf-8")
    command = [str(executable), "exec", "--ignore-user-config", "--ignore-rules",
               "--skip-git-repo-check", "--sandbox", "read-only", "--color", "never",
               "--json", "--model", "gpt-6.1-sol", "-c", 'model_reasoning_effort="ultra"',
               "-c", 'model_provider="openai"', "-c", "project_doc_max_bytes=0",
               "--output-last-message", str(output / "last-message.txt"), "-"]
    return {"schema_version": SCHEMA, "transport": "proposed_fresh_codex_cli_stdin",
            "formal_approved": False, "command": command, "executable_sha256": sha256(executable),
            "stdin_file": str(prompt), "stdin_sha256": hashlib.sha256(raw).hexdigest(),
            "stdin_bytes": len(raw), "output_dir": str(output),
            "runtime_expectation": {"model": "gpt-6.1-sol", "effort": "ultra", "provider": "openai"},
            "configuration_is_verified": False,
            "deviation": "A fresh CLI process replaces collaboration.spawn_agent(fork_turns=none); its harness differs. All arms would require the same newly preregistered path. No effort substitution is permitted."}


def execute_calibration_probe(prepared, *, empty_workdir):
    """Execute only after explicit authorization of the proposed amendment.

    The supervisor must import the actual persisted session receipt separately.
    JSON stdout is not treated as per-response accounting or model verification.
    No automatic retry, formal request import or successful calibration is created.
    """
    output, cwd = Path(prepared["output_dir"]), Path(empty_workdir)
    if any(cwd.iterdir()):
        raise ValueError("A proposed CLI probe requires an empty working directory")
    prompt = Path(prepared["stdin_file"])
    if sha256(prompt) != prepared["stdin_sha256"] or sha256(prepared["command"][0]) != prepared["executable_sha256"]:
        raise ValueError("The prepared executable or exact stdin changed")
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "launch.json", {**prepared, "started_at": utc_now()}, immutable=True)
    with (output / "stdout.jsonl").open("wb") as stdout, (output / "stderr.txt").open("wb") as stderr:
        process = subprocess.Popen(prepared["command"], cwd=cwd, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
        try:
            process.communicate(input=prompt.read_bytes(), timeout=2700)
            status = "process_exited"
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            status = "timeout"
    result = {"status": status, "returncode": process.returncode, "finished_at": utc_now(),
              "receipt_configuration": "not_yet_verified", "per_response_usage": None,
              "formal_requests": 0, "retries": 0, "launch_sha256": sha256(output / "launch.json")}
    write_json(output / "process-result.json", result, immutable=True)
    return result
