"""Prepare exactly the four authorized v9 cases after offline acceptance; zero calls."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import prepare
from tools.doe.document_guided_client import resolve_executable

VERIFY = Path(__file__).resolve().parent
OLD_TAGS = {"ga4": "20261101-214322", "001": "20261101-214748",
            "010": "20261101-214748", "013": "20261101-214748"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def create(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    accepted = read(VERIFY / "offline-acceptance.json")
    current = implementation_provenance()
    if accepted["status"] != "passed" or current["sha256"] != accepted["implementation_sha256"]:
        raise ValueError("Final implementation does not have matching offline acceptance")
    if (VERIFY / "prepared-runs.json").exists() or (VERIFY / "preparation-intent.json").exists():
        raise ValueError("Preparation already recorded; inspect it, never prepare a duplicate batch")
    cli = resolve_executable()
    tag = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
    planned = [{"case_id": case,
        "old_run": str(PROJECT / f"experiments/doe/runs/document-guided-{case}-general-loops-high-v8-{old}"),
        "run_directory": str(PROJECT / f"experiments/doe/runs/document-guided-{case}-alignment-high-v9-{tag}")}
        for case, old in OLD_TAGS.items()]
    create(VERIFY / "preparation-intent.json", {"run_order": planned,
        "implementation_sha256": current["sha256"], "created_at": datetime.now(timezone.utc).isoformat()})
    inventory = dict(current["files"])
    for name in ["tools/doe/document_guided_client.py", "tools/doe/document_guided_metrics.py",
                 "formal/.lake/build/bin/skill_ir_retell.exe"]:
        inventory[name] = sha(PROJECT / name)
    rows = []
    for item in planned:
        old, run = Path(item["old_run"]), Path(item["run_directory"])
        original = read_snapshot(old / "source")[1]
        prepare(old / "source/inputs/package", run_dir=run, config={"reasoning_effort": "high"})
        frozen = read_snapshot(run / "source")[1]
        if original != frozen:
            raise ValueError("Frozen source metadata differs: " + item["case_id"])
        prior_files = {p.relative_to(old / "source/inputs/package").as_posix(): sha(p)
                       for p in (old / "source/inputs/package").rglob("*") if p.is_file()}
        new_files = {p.relative_to(run / "source/inputs/package").as_posix(): sha(p)
                     for p in (run / "source/inputs/package").rglob("*") if p.is_file()}
        if prior_files != new_files:
            raise ValueError("Frozen source bytes differ: " + item["case_id"])
        for name in inventory:
            target = run / "implementation-snapshot" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PROJECT / name, target)
        shutil.copyfile(VERIFY / "controller-template.py", run / "controller.py")
        shutil.copyfile(VERIFY / "local_timing.py", run / "local_timing.py")
        create(run / "implementation-snapshot/snapshot.json", {"files": inventory,
            "implementation_sha256": current["sha256"], "controller_sha256": sha(run / "controller.py"),
            "local_timing_sha256": sha(run / "local_timing.py")})
        protocol = {"authorization": "2026-11-02 approved CFG/processing alignment plan; one new run per case after offline acceptance",
            "case_id": item["case_id"], "runtime": {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai"},
            "normal_semantic_requests": 7, "workers": 2, "semantic_repairs": 1,
            "structural_corrections_per_stage": 1, "native_timeout_seconds": 2700,
            "native_extra_transient_attempts": 2, "semantic_source_view": "complete_frozen_source",
            "ordinary_write_default": "replace; explicit source append/delete/update wins; declared runtime abstraction, not source assertion",
            "implementation_sha256": current["sha256"], "source_sha256": frozen["source_sha256"],
            "readable_files": len(frozen["files"]), "source_file_sha256": new_files,
            "source_utf8_bytes": sum(len(row["content"].encode("utf-8")) for row in frozen["files"]),
            "source_donor": str(old / "source"), "source_byte_identical": True,
            "historical_answers_imported": False, "cli_executable": str(cli), "cli_executable_sha256": sha(cli),
            "renderer_executable": str(PROJECT / "formal/.lake/build/bin/skill_ir_retell.exe"),
            "model_probe_calls": 0, "model_monitor_calls": 0, "skill_execution": False,
            "offline_acceptance": str(VERIFY / "offline-acceptance.json"),
            "queue_policy": "One sole sequential supervisor; ordinary case failure retained; no resampling or duplicate launch",
            "review_policy": "Independent assistant source audit after closure; no human-gold or general accuracy claim",
            "freeze_policy": "One implementation and prompt snapshot across all four runs and sole zero-call replays"}
        create(run / "run-protocol.json", protocol)
        create(run / "continuation-state.json", {"status": "queued_not_started",
            "run_directory": str(run), "instructions": "Root's sole v9 queue owns launch; do not launch independently."})
        rows.append({**item, "source_sha256": frozen["source_sha256"], "files": len(frozen["files"])})
    queue = {"run_order": rows, "implementation_sha256": current["sha256"],
             "global_analysis_workers": 2, "new_starts": 0, "sole_owner": "/root"}
    create(VERIFY / "prepared-runs.json", queue)
    state = read(VERIFY / "continuation-state.json")
    state.update(phase="prepared_not_started", prepared_runs=rows,
                 implementation_sha256=current["sha256"])
    (VERIFY / "continuation-state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(queue, indent=2))


if __name__ == "__main__":
    main()
