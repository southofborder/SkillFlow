"""Seal the sole closed run's reports with passive byte checks only."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summary = read(BASE / "run-summary.json")
    run = Path(summary["run_directory"])
    if summary["status"] != "closed_partial" or not summary["authorization_consumed"]:
        raise ValueError("Only the closed authorized result may be sealed")
    for relative, digest in summary["evidence_sha256"].items():
        path = ROOT / relative if relative.startswith(("experiments/", "output/")) else BASE / relative
        if not path.is_file() or sha(path) != digest:
            raise ValueError("Changed report evidence: " + relative)
    for directory in (BASE, ROOT / "output/verification/runtime-locality-20261117"):
        state = read(directory / "continuation-state.json")
        if state["status"] != "closed_partial" or state["pending"] or state["final_summary_sha256"] != sha(BASE / "run-summary.json"):
            raise ValueError("Continuation state differs from the final report")
    snapshot = read(run / "implementation-snapshot/snapshot.json")
    changed = [name for name, digest in snapshot["files"].items()
        if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
    if changed:
        raise ValueError("Frozen runtime changed during report preparation: " + repr(changed))
    historical = read(ROOT / "output/verification/runtime-locality-20261117/historical-pins.json")
    changed_history = [name for name, digest in historical["files"].items()
        if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
    if changed_history:
        raise ValueError("Protected history changed: " + repr(changed_history))
    for name in ("assessment.en.md", "assessment.zh.md", "followup-plan.zh.md"):
        for target in re.findall(r"\]\(([^)]+)\)", (BASE / name).read_text(encoding="utf-8")):
            if "://" not in target and not (BASE / target).is_file():
                raise ValueError("Missing report link: " + name + " -> " + target)
    artifacts = {path.name: sha(path) for path in sorted(BASE.iterdir())
        if path.is_file() and path.name != "report-closeout.json"}
    artifacts.update({path.relative_to(BASE).as_posix(): sha(path)
        for path in sorted((BASE / "cost-provenance-audit").glob("*")) if path.is_file()})
    navigation = {name: sha(ROOT / name) for name in ("AGENTS.md", "docs/current-version.md",
        "docs/doe/runtime-locality.md", "docs/doe/runtime-locality.zh.md",
        "output/verification/runtime-locality-20261117/continuation-state.json")}
    receipt = {"identity": "skillflow-runtime-locality-report-closeout-v1",
        "status": "sealed", "closed_at": datetime.now(timezone.utc).isoformat(),
        "reports_and_helpers_sha256": artifacts, "navigation_sha256": navigation,
        "run_evidence_sha256": summary["evidence_sha256"],
        "runtime_pins_rechecked": len(snapshot["files"]), "historical_pins_rechecked": len(historical["files"]),
        "changed_runtime_files": changed, "changed_historical_files": changed_history,
        "authorization_consumed": True, "followup_proposals_implemented": False,
        "method": "Passive JSON, byte/hash and local-link verification. No tests, project imports, stages, models, subprocess, Skill execution or replay."}
    with (BASE / "report-closeout.json").open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"status": receipt["status"], "report_files": len(artifacts),
        "runtime_pins": receipt["runtime_pins_rechecked"], "historical_pins": receipt["historical_pins_rechecked"],
        "closeout_sha256": sha(BASE / "report-closeout.json")}))


if __name__ == "__main__":
    main()
