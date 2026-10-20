"""Inspect a cloud checkout without authenticating or dispatching any model.

Install the project first. This script works from any working directory and
does not import experimental dispatchers, read credential files, or enumerate
environment values. Raw process output is deliberately not put in the report.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

from skillflow.common.paths import project_root


_OFFLINE_GUARD = r'''
import json
from pathlib import Path
import runpy
import socket
import sys

def forbidden(*args, **kwargs):
    raise AssertionError("Network or model access is forbidden in the offline smoke check")

socket.socket.connect = forbidden
socket.socket.connect_ex = forbidden
socket.create_connection = forbidden
socket.getaddrinfo = forbidden

from skillflow.common.llm import LlmClient
LlmClient.__init__ = forbidden
LlmClient.complete = forbidden
'''

_HELP_CHECK = _OFFLINE_GUARD + '''
sys.argv = ["skillflow", "--help"]
runpy.run_module("skillflow", run_name="__main__")
'''
_GRAPH_CHECK = _OFFLINE_GUARD + '''
from skillflow.cli import main
from skillflow.graph.extraction.prompt import _EXAMPLES

work = Path.cwd()
source = work / "source"
source.mkdir()
(source / "SKILL.md").write_text(
    "Read the user's input text. Trim leading and trailing whitespace. "
    "Log progress and return the cleaned text.", encoding="utf-8")
candidate = work / "candidate.json"
candidate.write_text(json.dumps(_EXAMPLES[0][1]), encoding="utf-8")
analysis = work / "analysis.json"
diagram = work / "graph.mmd"
assert main(["analyze", "--input", str(source), "--candidate", str(candidate),
             "--output", str(analysis)]) == 0
result = json.loads(analysis.read_text(encoding="utf-8"))
assert result["status"] == "complete"
assert result["attempts"] == 0
assert main(["render", "--input", str(analysis), "--output", str(diagram)]) == 0
assert diagram.read_text(encoding="utf-8").startswith("flowchart TD")
'''


def _execute(command: list[str], *, cwd: Path, timeout: int = 45) -> subprocess.CompletedProcess:
    return subprocess.run(
        command, cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
        stdin=subprocess.DEVNULL, check=False,
    )


def inspect_codex(*, cwd: Path, executable: str | None = None, execute=_execute) -> dict:
    """Only --version and --help; this deliberately does not test authentication."""
    selected = executable or shutil.which("codex")
    if not selected:
        return {"available": False, "version": None, "help_available": False,
                "authentication": "not_checked", "model_access": "not_checked"}
    result = {
        "available": True, "executable": str(Path(selected).resolve()),
        "version": None, "help_available": False,
        "authentication": "not_checked", "model_access": "not_checked",
    }
    for argument, key in (("--version", "version"), ("--help", "help_available")):
        try:
            response = execute([selected, argument], cwd=cwd, timeout=15)
        except (OSError, subprocess.TimeoutExpired) as error:
            result[key + "_error"] = type(error).__name__
            continue
        if key == "version":
            # Never serialize arbitrary CLI output, even when a wrapper fails.
            match = re.fullmatch(
                r"codex(?:-cli)?\s+([0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?)\s*",
                response.stdout,
            )
            if response.returncode == 0 and match:
                result["version"] = match.group(1)
            else:
                result["version_error"] = "unrecognized_version_output"
        else:
            result["help_available"] = response.returncode == 0
    return result


def offline_checks(*, execute=_execute) -> list[dict]:
    """Use the installed package outside the checkout, with network guards."""
    checks = []
    with tempfile.TemporaryDirectory(prefix="skillflow-cloud-offline-") as temporary:
        work = Path(temporary)
        for name, code in (("installed_cli_help", _HELP_CHECK),
                           ("offline_candidate_compile_and_render", _GRAPH_CHECK)):
            try:
                response = execute([sys.executable, "-I", "-c", code], cwd=work)
                checks.append({"name": name, "passed": response.returncode == 0,
                               "returncode": response.returncode})
            except (OSError, subprocess.TimeoutExpired) as error:
                checks.append({"name": name, "passed": False, "error": type(error).__name__})
    return checks


def preflight(start: str | Path | None = None, *, executable: str | None = None,
              execute=_execute) -> dict:
    root = project_root(start if start is not None else Path(__file__))
    checks = offline_checks(execute=execute)
    toolchain = root / "formal" / "lean-toolchain"
    return {
        "schema_version": "skillflow-cloud-preflight-v1",
        "project": "skillflow",
        "project_root": str(root),
        "environment": {"os": platform.system(), "machine": platform.machine(),
                        "python": platform.python_version()},
        "offline_status": "passed" if all(item["passed"] for item in checks) else "failed",
        "checks": checks,
        "codex": inspect_codex(cwd=root, executable=executable, execute=execute),
        "formal": {"pinned_toolchain": toolchain.read_text(encoding="utf-8").strip()
                   if toolchain.is_file() else None,
                   "build": "not_run"},
        "model_requests": 0,
        "long_experiment": {
            "status": "not_ready",
            "reason": "The existing CLI transport pins a Windows executable, CLI version, "
                      "runtime envelopes and receipt identity. Cloud transport, authentication, "
                      "model availability and receipt compatibility require separate verification.",
            "adapter_modified": False,
            "calibration_started": False,
            "formal_experiment_started": False,
        },
        "limits": [
            "Only local installation, CLI help, candidate compilation and Mermaid rendering are tested.",
            "Codex help/version availability does not establish authentication or permission to invoke a model.",
            "No credential files or session receipts are read. No environment values are exported.",
            "No historical run is resumed, migrated or relabeled as a cloud run.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, help="A path within the SkillFlow checkout")
    parser.add_argument("--codex-executable", help="Explicit CLI path for help/version inspection only")
    args = parser.parse_args(argv)
    report = preflight(args.project, executable=args.codex_executable)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["offline_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
