"""Collect terminal read-only audits; never start an analysis or a replay."""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    prepared = read(HERE / "prepared-run.json")
    run = Path(prepared["run_directory"])
    if not run.is_absolute():
        run = PROJECT / run
    terminal = read(run / "controller-finished.json")
    state = read(run / "continuation-state.json")
    if state["status"] != "generation_closed":
        raise ValueError("The sole controller has not closed")
    if not terminal["native_exits"]["all_attempt_exits_confirmed"]:
        raise ValueError("Native exits are not confirmed")
    env = dict(os.environ, PYTHONPATH=str(PROJECT / "src"), PYTHONIOENCODING="utf-8")
    jobs = (
        ("final-request-audit.json", "request_audit.py", ["--run", str(run)]),
        ("final-backend-audit.json", "backend_audit.py", ["--run", str(run)]),
        ("final-source-boundary-audit.json", "source_boundary_audit.py", ["--run", str(run)]),
        ("final-integrity.json", "integrity_check.py", []),
    )
    if any((HERE / name).exists() for name, _, _ in jobs):
        raise ValueError("Final evidence already exists; do not overwrite it")
    collected = []
    for name, helper, args in jobs:
        result = subprocess.run([sys.executable, str(HERE / helper), *args], cwd=PROJECT,
                                env=env, capture_output=True, check=True, timeout=120)
        value = json.loads(result.stdout.decode("utf-8-sig"))
        collected.append((name, value))
    for name, value in collected:
        with (HERE / name).open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
    print(json.dumps({"status": "collected", "run": str(run),
                      "new_reports": [name for name, _ in collected]}))


if __name__ == "__main__":
    main()
