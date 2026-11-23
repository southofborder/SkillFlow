"""Seal the report for this controller's terminal run using the published receipts."""
from datetime import datetime, timezone
from pathlib import Path
import json

from lifecycle_guard import read, sha


def main():
    verify = Path(__file__).resolve().parent
    project = verify.parents[2]
    run = Path(read(verify / "prepared-run.json")["run_directory"])
    controller = read(run / "controller-finished.json")
    replay = read(run / "replay-check.json")
    integrity = read(verify / "integrity.json")
    summary = read(verify / "run-summary.json")
    if (read(run / "continuation-state.json")["status"] != "generation_closed"
            or controller["replay"] != replay or summary["run"] != run.name
            or integrity["status"] != "closed" or integrity["recorded_pids_still_present"]):
        raise ValueError("The report is not bound to a terminal run with a closed controller")
    for name in ("assessment.zh.md", "assessment.en.md", "final-request-audit.json", "final-backend-audit.json"):
        if not (verify / name).is_file():
            raise ValueError("Missing report: " + name)
    closeout = {"status": "closed", "sealed_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(run), "analysis_status": controller["status"], "dispatches": 1,
        "implementation_sha256": read(run / "run-protocol.json")["implementation_sha256"],
        "github_commit": read(verify / "github-sync.json")["commit"], "authorization_consumed": True,
        "controller_owned_zero_call_replays": int((run / "replay-started.json").is_file()), "replay": replay,
        "reports_and_helpers_sha256": {p.name: sha(p) for p in sorted(verify.iterdir()) if p.is_file()
                                      and p.name not in {"report-closeout.json", "continuation-state.json"}},
        "run_evidence_sha256": {p.relative_to(project).as_posix(): sha(p) for p in sorted(run.rglob("*"))
                                if p.is_file() and "__pycache__" not in p.parts}}
    with (verify / "report-closeout.json").open("x", encoding="utf-8") as stream:
        json.dump(closeout, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
