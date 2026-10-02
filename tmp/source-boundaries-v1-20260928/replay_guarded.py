from pathlib import Path
import json, socket, runpy
import skill_ir.recording as recording
root = Path.cwd()
run = Path((root / "tmp/source-boundaries-v1-20260928/selected-run.txt").read_text(encoding="utf-8")).resolve()
attempts = []
def forbidden(*args, **kwargs):
    attempts.append("network_or_online_factory")
    raise AssertionError("offline replay attempted online activity")
socket.socket.connect = forbidden
socket.socket.connect_ex = forbidden
socket.create_connection = forbidden
recording.streaming_factory = forbidden
module = runpy.run_path(str(root / "packages/skill-ir/experiments/propagation/tools/run_pilot.py"))
result = module["main"](["replay", "--run-dir", str(run)])
output = {"status": "passed" if result == 0 and not attempts else "failed", "network_attempts": len(attempts), "exit_code": result}
(run / "verification").mkdir(exist_ok=True)
(run / "verification/network-guard.json").write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(output))
raise SystemExit(result)
