"""One read-only accepted-parent compatibility check; never creates a child."""
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from skillflow.common.recording import canonical_sha256, implementation_provenance, sha_file
from skillflow.document_guided.accepted_upstream import describe_accepted_upstream


def main():
    verify = Path(__file__).resolve().parent
    destination = verify / "accepted-parent-pure-preflight-01.json"
    if destination.exists():
        raise ValueError("Preserve the existing preflight receipt")
    parent = ROOT / "experiments/doe/runs/document-guided-ga4-processing-restart-high-20261117-172228"
    def inventory():
        return {path.relative_to(parent).as_posix(): sha_file(path) for path in sorted(parent.rglob("*")) if path.is_file()}
    before = inventory()
    def forbidden(*args, **kwargs):
        raise AssertionError("A saved runner, Task semantic reader, response chain or subprocess must not execute in this preflight")
    with patch("skillflow.document_guided.runner.run", forbidden), patch("skillflow.document_guided.online.run_step", forbidden), \
            patch("skillflow.task.runner.run_task", forbidden), patch("skillflow.task.runner.load_task_run", forbidden), \
            patch("skillflow.common.structural_correction.ResponseChain.run", forbidden), patch("subprocess.Popen", forbidden):
        description = describe_accepted_upstream(parent)
    after = inventory()
    assert after == before
    lifecycle_path = verify / "accepted-parent-binding.json"
    lifecycle = json.loads(lifecycle_path.read_bytes().decode("utf-8"))
    assert description["files"] == lifecycle["inherited_files"]
    report = {"identity": "skillflow-accepted-parent-pure-preflight-v1", "status": "passed",
        "method": "Read-only source/Task structural artifacts and current accepted flow/CFG compatibility proof. Historical guided/step/Task runners, Task semantic reader, response-chain execution and subprocesses were explicitly blocked. No child created.",
        "parent": str(parent), "description": description,
        "parent_file_count": len(before), "parent_files_unchanged": before == after,
        "parent_inventory_sha256": canonical_sha256(before), "parent_files": before,
        "lifecycle_binding": {"path": str(lifecycle_path), "sha256": sha_file(lifecycle_path),
            "exact_inherited_inventory_equal": True, "inherited_files": len(description["files"])},
        "implementation": implementation_provenance(), "helper_sha256": sha_file(Path(__file__).resolve()),
        "limitations": "Task semantic verification remains mandatory on the future child copy. This check makes no source-review/processing/DOE success claim and starts no run."}
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "parent_file_count": len(before), "inherited_files": len(description["files"]), "inherited_inventory_equal": True, "no_child_created": True}))


if __name__ == "__main__":
    main()
