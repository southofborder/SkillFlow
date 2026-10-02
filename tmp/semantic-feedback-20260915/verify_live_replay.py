"""Replay actual F01 calls with network disabled and compare all derived results."""
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import urllib.request

import skill_ir.recording as recording

root = Path.cwd()
directory = root / "packages/skill-ir/experiments/semantic_feedback/runs/f01-feedback-20260915"
driver = root / "packages/skill-ir/experiments/semantic_feedback/tools/run_f01.py"
network_attempts = []


def forbidden(*args, **kwargs):
    network_attempts.append("attempt")
    raise AssertionError("Offline replay attempted to construct/use a network client")


def call_hashes():
    return {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for case in (directory / "cases").iterdir() for path in (case / "calls").rglob("*") if path.is_file()}


before = call_hashes()
live = json.loads((directory / "experiment-result.json").read_text(encoding="utf-8"))
urllib.request.urlopen = forbidden
socket.create_connection = forbidden
recording.streaming_factory = forbidden
spec = importlib.util.spec_from_file_location("feedback_f01_replay_verification", driver)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
replayed = module.execute(directory, replay=True)
matches = {case: live["cases"][case] == replayed["cases"][case] for case in live["cases"]}
checks = {
    "case_results_identical": matches,
    "external_evaluation_identical": live["evaluation"] == replayed["evaluation"],
    "call_artifacts_unchanged": before == call_hashes(),
    "network_attempts": len(network_attempts),
    "guard": "urllib urlopen, socket connection, and streaming factory replaced with rejecting functions",
    "recorded_call_artifact_files": len(before),
}
passed = all(matches.values()) and checks["external_evaluation_identical"] and checks["call_artifacts_unchanged"] and not network_attempts
checks["status"] = "passed" if passed else "failed"
(directory / "verification/live-replay.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(checks, ensure_ascii=False, indent=2))
assert passed
