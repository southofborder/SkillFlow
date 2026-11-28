"""Dispatch the requested fresh analysis of the original two source files once."""
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from skillflow.document_guided.runner import prepare


def load(path):
    return json.loads(path.read_bytes())


def main():
    owner = Path(__file__).resolve().parent
    project = owner.parents[2]
    old = project / "experiments/doe/runs/document-guided-google-search-call-routing-high-20261125-194132"
    old_selection = load(old / "selection.json")
    original = load(owner.parent / "google-search-call-routing-20261125/source-provenance.json")
    view = project / original["original_registry_view"]
    source = owner / "source-package"
    verified = {}
    for row in load(view)["files"]:
        if row["include_in_source"]:
            name = row["path"]
            blob = (view.parent / "files" / name).read_bytes()
            pin = {"bytes": len(blob), "sha256": sha256(blob).hexdigest()}
            assert pin == original["files"][name] and pin["sha256"] == row["sha256"]
            dst = source / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(blob)
            verified[name] = pin
    assert verified == original["files"]
    assert {p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file()} == set(verified)
    assert old_selection["task"]["sha256"] == sha256((old / "task/task.json").read_bytes()).hexdigest()
    assert load(owner / "offline-acceptance.json")["comparison_count"] > 0
    previous = next((old / "transport/graph").glob("*/attempt-001/launch.json"))
    executable = Path(load(previous)["command"][0])
    request = load(previous.parents[1] / "request.json")
    assert executable.is_file()
    now = datetime.now().astimezone()
    run_dir = old.parent / ("document-guided-google-search-outcome-dispatch-high-" + now.strftime("%Y%m%d-%H%M%S"))
    config = load(old / "manifest.json")["config"]
    # Exclusive creation prevents a second paid run from this verification directory.
    with (owner / "dispatch.json").open("x", encoding="utf-8") as receipt:
        json.dump({"time": now.isoformat(), "run": str(run_dir), "original_registry_view": str(view),
                   "files": verified, "config": config, "inherited_stages": 0,
                   "executable": str(executable), "timeout": request["timeout"],
                   "network_retries": request["network_retries"]}, receipt, indent=2)
    manifest = prepare(str(source), run_dir=run_dir, config=config)
    print(run_dir, manifest["implementation"]["sha256"], flush=True)
    cmd = [sys.executable, "-u", "-m", "tools.doe.document_guided_pilot", "run",
           "--executable", str(executable), "--timeout", str(request["timeout"]),
           "--retries", str(request["network_retries"]), "--run-dir", str(run_dir)]
    with (owner / "online.log").open("w", encoding="utf-8") as log:
        proc = subprocess.run(cmd, cwd=project, stdout=log, stderr=subprocess.STDOUT)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
