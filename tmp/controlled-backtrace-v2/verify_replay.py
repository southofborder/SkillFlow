"""Post-run acceptance of the actual v2 replay CLI; not a model/runtime module."""
import hashlib
import json
from pathlib import Path
import socket
import urllib.request
from unittest.mock import patch

from skill_ir.backtrace import __main__ as cli
from skill_ir.backtrace import runner


root = Path(__file__).resolve().parents[2]
directory = Path((root / "tmp/controlled-backtrace-v2/current-run.txt").read_text().strip())
live = json.loads((directory / "report.json").read_text(encoding="utf-8"))


def digests():
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((directory / "calls").rglob("*")) if p.is_file()}


before = digests()
attempts = {"client_factory": 0, "network": 0, "credential_read": 0}


def forbidden(kind):
    def fail(*args, **kwargs):
        attempts[kind] += 1
        raise AssertionError(f"Offline replay attempted {kind}")
    return fail


with patch.object(cli, "streaming_factory", forbidden("client_factory")), \
     patch.object(runner, "streaming_factory", forbidden("client_factory")), \
     patch.object(runner, "load_environment", forbidden("credential_read")), \
     patch.object(socket, "create_connection", forbidden("network")), \
     patch.object(socket.socket, "connect", forbidden("network")), \
     patch.object(urllib.request, "urlopen", forbidden("network")):
    exit_code = cli.main(["replay", "--run-dir", str(directory)])

replay = json.loads((directory / "replay/report.json").read_text(encoding="utf-8"))
after = digests()
checks = {
    "schema_version": 2,
    "command": "python -m skill_ir.backtrace replay --run-dir <current-run>",
    "invocation": "actual CLI main with network, factory and credential guards",
    "exit_code": exit_code,
    "forbidden_attempts": attempts,
    "stages_identical": live["stages"] == replay["stages"],
    "evaluation_identical": live["evaluation"] == replay["evaluation"],
    "conversion_identical": live["conversion"] == replay["conversion"],
    "call_summary_identical": live["calls"] == replay["calls"],
    "original_call_files_unchanged": before == after,
    "original_call_file_count": len(before),
    "live_report_sha256": hashlib.sha256((directory / "report.json").read_bytes()).hexdigest(),
    "replay_report_sha256": hashlib.sha256((directory / "replay/report.json").read_bytes()).hexdigest(),
    "calls_sha256": runner.canonical_sha256(before),
}
checks["passed"] = (exit_code == 0 and not any(attempts.values()) and all(
    checks[key] for key in ("stages_identical", "evaluation_identical", "conversion_identical",
                           "call_summary_identical", "original_call_files_unchanged")))
(directory / "verification/replay.json").write_text(
    json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(checks, ensure_ascii=False, indent=2))
raise SystemExit(0 if checks["passed"] else 1)
