"""Freeze the authorized fresh batch after offline acceptance; no model calls."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from skillflow.common.inputs.snapshot import inspect_input, read_snapshot
from skillflow.common.recording import implementation_provenance, canonical_sha256
from skillflow.document_guided.runner import prepare

VERIFY = Path(__file__).resolve().parent
OFFLINE = VERIFY.parent / "input-necessity-20261111"


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
    acceptance = read(OFFLINE / "offline-acceptance.json")
    prior = read(OFFLINE / "continuation-state.json")
    current = implementation_provenance()
    if acceptance["status"] != "passed" or acceptance["implementation_sha256"] != current["sha256"]:
        raise ValueError("Current implementation does not match completed offline acceptance")
    if (VERIFY / "preparation-intent.json").exists() or (VERIFY / "prepared-runs.json").exists():
        raise ValueError("Preparation already recorded; inspect it instead of creating another batch")
    environment = prior["read_only_environment_check"]
    cli, renderer = Path(environment["native_cli"]), Path(environment["renderer"])
    if sha(cli) != environment["cli_sha256"] or sha(renderer) != environment["renderer_binary_sha256"]:
        raise ValueError("Prepared executable differs from the verified installation")
    tag = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
    sources = prior["verified_source_inputs"]
    if [row["case"] for row in sources] != ["ga4", "001", "010", "013"]:
        raise ValueError("Source order differs from authorization")
    planned = [{"case_id": row["case"], "source_root": row["source_root"],
        "run_directory": str(PROJECT / f"experiments/doe/runs/document-guided-{row['case']}-input-necessity-high-{tag}")}
        for row in sources]
    create(VERIFY / "preparation-intent.json", {"run_order": planned, "created_at": datetime.now(timezone.utc).isoformat(),
        "implementation_sha256": current["sha256"], "offline_acceptance": str(OFFLINE / "offline-acceptance.json")})
    inventory = dict(current["files"])
    for name in ["tools/doe/document_guided_client.py", "tools/doe/document_guided_metrics.py", "tools/doe/document_guided_pilot.py",
                 "formal/.lake/build/bin/skill_ir_retell.exe"]:
        inventory[name] = sha(PROJECT / name)
    rows = []
    for item, source_row in zip(planned, sources):
        original = Path(item["source_root"])
        staged = VERIFY / "source-packages" / item["case_id"]
        staged.mkdir(parents=True, exist_ok=False)
        omitted = set(source_row.get("excluded_files", []))
        original_files = {}
        for source in sorted(original.rglob("*")):
            if not source.is_file():
                continue
            relative = source.relative_to(original)
            if relative.as_posix() in omitted:
                continue
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            original_files[relative.as_posix()] = sha(source)
        _, readable, metadata = inspect_input(staged)
        if readable["source_sha256"] != source_row["content_sha256"]:
            raise ValueError("Source content differs from verified prior package: " + item["case_id"])
        if len(metadata["files"]) != source_row["file_count"] or sum(r["size"] for r in metadata["files"]) != source_row["total_bytes"]:
            raise ValueError("Source inventory differs: " + item["case_id"])
        run = Path(item["run_directory"])
        prepare(staged, run_dir=run, config={"reasoning_effort": "high"})
        frozen = read_snapshot(run / "source")[1]
        frozen_files = {p.relative_to(run / "source/inputs/package").as_posix(): sha(p)
                        for p in (run / "source/inputs/package").rglob("*") if p.is_file()}
        if frozen != readable or frozen_files != original_files:
            raise ValueError("Frozen source is not byte-identical: " + item["case_id"])
        for name in inventory:
            target = run / "implementation-snapshot" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PROJECT / name, target)
        shutil.copyfile(VERIFY / "controller-template.py", run / "controller.py")
        shutil.copyfile(VERIFY / "local_timing.py", run / "local_timing.py")
        create(run / "implementation-snapshot/snapshot.json", {"files": inventory,
            "implementation_sha256": current["sha256"], "controller_sha256": sha(run / "controller.py"),
            "local_timing_sha256": sha(run / "local_timing.py")})
        protocol = {"authorization": "2026-11-11 user authorized implementation, offline acceptance, then one fresh GA4 and three-small-Skill batch",
            "case_id": item["case_id"], "runtime": {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai"},
            "normal_semantic_requests": 7, "workers": 2, "semantic_repairs": 1,
            "structural_corrections_per_stage": 1, "native_timeout_seconds": 2700, "native_extra_transient_attempts": 2,
            "semantic_source_view": "complete_frozen_source", "interface_revision": "source_reviewed_input_necessity",
            "implementation_sha256": current["sha256"], "source_sha256": frozen["source_sha256"],
            "source_file_sha256": frozen_files, "readable_files": len(frozen["files"]),
            "source_utf8_bytes": sum(len(r["content"].encode("utf-8")) for r in frozen["files"]),
            "source_donor": str(original), "source_staging": str(staged), "source_byte_identical": True,
            "historical_answers_imported": False, "cli_executable": str(cli), "cli_executable_sha256": sha(cli),
            "renderer_executable": str(renderer), "renderer_executable_sha256": sha(renderer),
            "model_probe_calls": 0, "model_monitor_calls": 0, "skill_execution": False,
            "offline_acceptance": str(OFFLINE / "offline-acceptance.json"),
            "queue_policy": "Root owns one sequential batch; retain terminal failures without resampling; one zero-call replay per controller",
            "freeze_policy": "Identical accepted implementation, prompts, renderer and transport across all four analyses and replays"}
        create(run / "run-protocol.json", protocol)
        create(run / "continuation-state.json", {"status": "queued_not_started", "run_directory": str(run),
            "instructions": "Root's sole input-necessity queue owns launch. Do not launch independently or resume historical runs."})
        rows.append({**item, "source_staging": str(staged), "source_sha256": frozen["source_sha256"], "files": len(frozen["files"])})
    queue = {"run_order": rows, "batch_tag": tag, "implementation_sha256": current["sha256"],
             "global_analysis_workers": 2, "new_starts": 0, "sole_owner": "/root"}
    create(VERIFY / "prepared-runs.json", queue)
    create(VERIFY / "continuation-state.json", {"phase": "prepared_not_started", "prepared_runs": rows,
        "implementation_sha256": current["sha256"], "authorization": protocol["authorization"],
        "instructions": "Root alone launches run_four_queue.py once. Preserve all old runs; do not execute Skills."})
    print(json.dumps(queue, indent=2))


if __name__ == "__main__":
    main()
