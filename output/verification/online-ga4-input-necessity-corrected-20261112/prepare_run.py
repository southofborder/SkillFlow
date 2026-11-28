"""Prepare the one newly authorized GA4 run without any model calls."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from skillflow.common.inputs.snapshot import inspect_input, read_snapshot
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import prepare
from tools.doe.document_guided_client import resolve_executable

VERIFY = Path(__file__).resolve().parent
PRIOR = VERIFY.parent / "online-input-necessity-20261111"
OFFLINE = VERIFY.parent / "input-necessity-completeness-20261111"
OLD_RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-high-20261111-173347"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def create(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    current = implementation_provenance()
    accepted = read(OFFLINE / "offline-acceptance.json")
    old = read(OLD_RUN / "run-protocol.json")
    if accepted["status"] != "passed" or accepted["implementation_sha256"] != current["sha256"]:
        raise ValueError("Current implementation differs from corrected offline acceptance")
    if read(PRIOR / "queue-live.json")["phase"] != "all_four_closed":
        raise ValueError("The previous batch is not closed")
    cli = resolve_executable()
    if sha(Path(old["renderer_executable"])) != old["renderer_executable_sha256"]:
        raise ValueError("Verified renderer changed")
    tag = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
    run = PROJECT / f"experiments/doe/runs/document-guided-ga4-input-necessity-corrected-high-{tag}"
    authorization = "2026-11-12 user explicitly requested one new GA4 online test after the previous timeout; corrected implementation, fresh generation and one controller-owned zero-call replay."
    create(VERIFY / "preparation-intent.json", {"authorization": authorization,
        "run_directory": str(run), "created_at": datetime.now(timezone.utc).isoformat(),
        "implementation_sha256": current["sha256"], "maximum_new_runs": 1})
    source = Path(old["source_donor"])
    staged = VERIFY / "source-package"
    staged.mkdir(exist_ok=False)
    source_files = old["source_file_sha256"]
    for name, digest in source_files.items():
        original, target = source / name, staged / name
        if sha(original) != digest:
            raise ValueError("Original source changed: " + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
    _, readable, _ = inspect_input(staged)
    if readable["source_sha256"] != old["source_sha256"] or len(readable["files"]) != 16:
        raise ValueError("The complete source package differs from the previous GA4 input")
    prepare(staged, run_dir=run, config={"reasoning_effort": "high"})
    frozen = read_snapshot(run / "source")[1]
    frozen_files = {p.relative_to(run / "source/inputs/package").as_posix(): sha(p)
        for p in (run / "source/inputs/package").rglob("*") if p.is_file()}
    if frozen != readable or frozen_files != source_files:
        raise ValueError("Frozen source is not byte-identical to the verified input")
    inventory = dict(current["files"])
    for name in ("tools/doe/document_guided_client.py", "tools/doe/document_guided_metrics.py",
                 "tools/doe/document_guided_pilot.py", "formal/.lake/build/bin/skill_ir_retell.exe"):
        inventory[name] = sha(PROJECT / name)
    for name in inventory:
        target = run / "implementation-snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT / name, target)
    for original, target in (("controller-template.py", "controller.py"), ("local_timing.py", "local_timing.py")):
        shutil.copyfile(PRIOR / original, run / target)
        shutil.copyfile(PRIOR / original, VERIFY / original)
    create(run / "implementation-snapshot/snapshot.json", {"files": inventory,
        "implementation_sha256": current["sha256"], "controller_sha256": sha(run / "controller.py"),
        "local_timing_sha256": sha(run / "local_timing.py")})
    protocol = {**old, "authorization": authorization,
        "interface_revision": "source_reviewed_input_necessity_corrected",
        "implementation_sha256": current["sha256"], "source_staging": str(staged),
        "cli_executable": str(cli), "cli_executable_sha256": sha(cli),
        "cli_change_from_previous_run": {"previous_executable": old["cli_executable"],
            "previous_sha256": old["cli_executable_sha256"],
            "reason": "The installed Codex application updated and the old executable path no longer exists. Current installed CLI flags were checked using local --help only; no model probe was made."},
        "offline_acceptance": str(OFFLINE / "offline-acceptance.json"),
        "queue_policy": "Root owns exactly one fresh GA4 controller and its sole zero-call replay; no additional cases or resampling.",
        "freeze_policy": "Freeze corrected implementation, prompts, transport and renderer throughout this analysis and replay.",
        "previous_run_reference_only": str(OLD_RUN)}
    create(run / "run-protocol.json", protocol)
    item = {"case_id": "ga4", "run_directory": str(run), "source_root": str(source),
        "source_staging": str(staged), "source_sha256": frozen["source_sha256"], "files": 16}
    state = {"status": "prepared_not_started", "authorization": authorization, **item,
        "implementation_sha256": current["sha256"], "maximum_new_runs": 1,
        "instructions": "Root alone dispatches this fresh controller exactly once. Do not resume old runs, execute Skills, alter frozen implementation, launch probes or duplicate controllers."}
    create(run / "continuation-state.json", state)
    create(VERIFY / "continuation-state.json", state)
    create(VERIFY / "prepared-run.json", {**item, "implementation_sha256": current["sha256"],
        "model": "gpt-6.1-sol", "effort": "high", "provider": "openai", "workers": 2,
        "normal_semantic_calls": 7, "native_timeout_seconds": 2700, "sole_owner": "/root"})
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
