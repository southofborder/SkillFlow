"""Seal saved evidence after closure, without model calls or replay."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files(directory):
    return sorted(path for path in directory.rglob("*") if path.is_file()
                  and "__pycache__" not in path.parts and path.suffix != ".pyc")


def main():
    target = HERE / "report-closeout.json"
    if target.exists():
        raise ValueError("Report closeout already exists")
    summary = read(HERE / "run-summary.json")
    run = PROJECT / summary["run_directory"]
    integrity = read(HERE / "final-integrity.json")
    controller = read(run / "controller-finished.json")
    assert summary["status"] == "closed" and integrity["status"] == "closed"
    assert controller["status"] == "partial" and controller["controller_error"] is None
    assert controller["replay"]["status"] == "matched"
    assert controller["replay"]["new_native_markers"] == 0
    assert controller["replay"]["native_inventory_unchanged"]
    assert not integrity["recorded_pids_still_present"]
    assert summary["request_counts"]["native_process_starts"] == 8
    assert summary["usage"]["known_token_usage"]["total_tokens"] == 1597999
    assert summary["selected_cfg"]["instructions"] == 489
    assert summary["demand"]["range_statuses"] == {"required": 2942, "unresolved": 5077, "deletable": 0}
    assert summary["review"]["demand_receipt_matches"]
    required = ("assessment.en.md", "assessment.zh.md", "followup-plan.zh.md",
                "final-backend-interpretation.json", "independent-candidate-scale-forensics.json")
    for name in required:
        assert (HERE / name).is_file(), name
    reports = {path.relative_to(HERE).as_posix(): sha(path) for path in files(HERE)}
    evidence = {path.relative_to(PROJECT).as_posix(): sha(path) for path in files(run)}
    value = {
        "identity": "skillflow-ga4-lossless-delivery-report-closeout-v1",
        "status": "closed", "sealed_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": summary["run_directory"], "analysis_status": "partial",
        "implementation_sha256": summary["implementation_sha256"],
        "github_commit": summary["github_commit"],
        "dispatches": 1, "controller_owned_zero_call_replays": 1,
        "authorization_consumed": True, "followup_implemented": False,
        "replay": controller["replay"],
        "reports_and_helpers_sha256": reports,
        "run_evidence_sha256": evidence,
        "notice": "No second dispatch, resampling, Skill execution, historical replay/resume, automatic proposal implementation or artifact rewrite is authorized. Derived Python caches are excluded from the seal; source, runtime pins, native evidence and published reports are retained. This file is the seal and is not self-hashed."
    }
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"status": "sealed", "report_files": len(reports),
                      "run_evidence_files": len(evidence), "closeout_sha256": sha(target)}))


if __name__ == "__main__":
    main()
