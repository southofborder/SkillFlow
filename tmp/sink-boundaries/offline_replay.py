"""Replay the frozen pilot while denying network and online client creation."""
import json
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/skill-ir/src"))
sys.path.insert(0, str(ROOT / "packages/skill-ir/experiments/propagation/tools"))
import run_sink_pilot as pilot
from skill_ir.recording import canonical_sha256

run_dir = ROOT / "packages/skill-ir/experiments/propagation/runs/sink-boundaries-v1-20261002-185934"
attempts = []

def blocked(*args, **kwargs):
    attempts.append("network_or_online_client")
    raise AssertionError("offline replay attempted network or online client creation")

socket.socket.connect = blocked
socket.socket.connect_ex = blocked
socket.create_connection = blocked
pilot.streaming_factory = blocked

before = {}
for case_id in ("001", "010"):
    p = run_dir / "cases" / case_id / "propagation/doe-input.json"
    before[case_id] = canonical_sha256(json.loads(p.read_text(encoding="utf-8")))
summary = pilot.execute(run_dir, replay=True)
after = {}
for case_id in ("001", "010"):
    p = run_dir / "cases" / case_id / "propagation/doe-input.json"
    after[case_id] = canonical_sha256(json.loads(p.read_text(encoding="utf-8")))
assert before == after
assert not attempts
assert [(c["case_id"], c["annotation"], c["propagation"]) for c in summary["cases"]] == [
    ("001", "complete", "complete"),
    ("010", "complete", "complete"),
    ("013", "invalid_response", "not_run"),
]
receipt = {
    "status": "matched", "replay_model_calls": 0, "network_attempts": len(attempts),
    "blocked_network_and_online_client_creation": True,
    "final_doe_sha256": after,
    "case_statuses": [{k: c[k] for k in ("case_id", "annotation", "propagation")} for c in summary["cases"]],
    "historical_logical_calls": summary["logical_calls"],
}
(run_dir / "replay-verification.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, ensure_ascii=False))
