"""Reconcile an interrupted baseline offline; never resend a request or edit trace.

The operator first stops the runner. An OS lock proves no runner currently owns
the directory. The existing recovery policy determines every trial's safe state;
unknown requests stay uncertain and can never become successful model results.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE.parents[1] / "src"))

from skill_ir.experiments.report import ArtifactWriter, aggregate, write_progress
from skill_ir.experiments.resumable import REVIEW_PENDING, _exclusive_run, _recover


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile(run: Path, *, reason: str, interrupted_at: str | None = None) -> dict:
    """Reconcile all 90 records without credentials, a client or extraction calls."""
    run = Path(run).resolve()
    if not run.is_dir() or not (run / "experiment.json").is_file():
        raise ValueError("An existing baseline run directory is required")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("A nonblank operator-provided interruption reason is required")
    if interrupted_at is not None:
        parsed = datetime.fromisoformat(interrupted_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("interrupted_at must include a timezone")
        interrupted_at = parsed.astimezone(timezone.utc).isoformat()
    with _exclusive_run(run):
        identity = read(run / "experiment.json")
        if (len(identity["cases"]) != 30 or identity["repetitions"] != 3
            or len(identity["variants"]) != 1
            or Counter(case["split"] for case in identity["cases"]) != {"development": 22, "held_out": 8}):
            raise ValueError("Expected the frozen 30-sample, three-repeat, 22/8 baseline")
        report_path = run / "report.json"
        report = read(report_path)
        trace_hashes = {
            path.relative_to(run).as_posix(): sha(path)
            for path in sorted((run / "trials").rglob("trace.json"))
        }
        latest = run / "reconciliation.json"
        if latest.exists():
            previous = read(latest)
            if (previous.get("trace_sha256") == trace_hashes
                and previous.get("report_sha256") == sha(report_path)
                and all((run / path).is_file() and sha(run / path) == digest
                        for path, digest in previous.get("record_sha256", {}).items())):
                return report
        before_report_sha = sha(report_path)
        expected = []
        for case in identity["cases"]:
            for variant in identity["variants"]:
                for repetition in (1, 2, 3):
                    expected.append({
                        "case": case["id"], "variant": variant["id"], "repetition": repetition,
                        "split": case["split"],
                        "artifacts": f"trials/{case['id']}/{variant['id']}/{repetition}",
                    })
        report_ids = [(t["case"], t["variant"], t["repetition"]) for t in report["trials"]]
        expected_ids = [(t["case"], t["variant"], t["repetition"]) for t in expected]
        if len(report_ids) != 90 or set(report_ids) != set(expected_ids):
            raise ValueError("The report must preserve all 90 unique trial identities")
        observed = datetime.now(timezone.utc).isoformat()
        interruption = {
            "description": reason.strip(),
            "occurred_at": interrupted_at,
            "observed_at": observed,
            "timestamp_basis": (
                "Operator supplied the interruption timestamp."
                if interrupted_at else
                "The precise interruption time was not recorded; observed_at is the offline reconciliation observation time."
            ),
        }
        writer = ArtifactWriter(())  # Inputs are already-redacted persisted artifacts.
        recovered, changed, replayable = [], [], []
        http_attempts, generations = [], []
        for item in expected:
            path = run / item["artifacts"] / "record.json"
            if not path.is_file():
                raise ValueError(f"Missing durable trial record: {item['artifacts']}")
            before = read(path)
            if any(before.get(key) != value for key, value in item.items()):
                raise ValueError(f"Trial identity mismatch: {item['artifacts']}")
            record, replay = _recover(deepcopy(before), run)
            if replay:
                replayable.append(item["artifacts"])
            if before["status"] != record["status"]:
                changed.append({**item, "before": before["status"], "after": record["status"]})
                record["interruption"] = interruption
                record["reconciled_at"] = observed
            record["semantic_review_status"] = REVIEW_PENDING
            trace = run / item["artifacts"] / "trace.json"
            if trace.exists():
                calls = read(trace)["calls"]
                generations.extend(calls)
                http_attempts.extend(attempt for call in calls for attempt in call["http_attempts"])
            recovered.append((path, before, record))
        # Validate the entire directory before committing any reconciled record.
        for relative, digest in trace_hashes.items():
            if sha(run / relative) != digest:
                raise ValueError("A trace changed during offline reconciliation")
        for path, before, record in recovered:
            if before != record:
                writer.json(path, record)
        statuses = Counter(record["status"] for _, _, record in recovered)
        outcomes = Counter(
            "unknown_after_interruption" if attempt["status"] in {"running", "interrupted"}
            else attempt["status"] for attempt in http_attempts
        )
        categories = Counter()
        for attempt in http_attempts:
            if attempt["status"] != "error":
                continue
            if attempt.get("http_status") is not None:
                categories[f"HTTP {attempt['http_status']}"] += 1
            elif "timed out" in attempt.get("error", "").lower() or "timeout" in attempt.get("error", "").lower():
                categories["network timeout"] += 1
            else:
                categories["network or transport error"] += 1
        event = {
            "schema_version": 1, "reconciled_at": observed, "offline": True,
            "network_requests_sent_by_reconciler": 0,
            "trace_bytes_unchanged": True, "trace_sha256": trace_hashes,
            "interruption": interruption, "affected_trials": changed,
            "replayable_trials_not_executed": replayable,
            "trial_status_counts": dict(statuses),
            "generation_sessions": len(generations),
            "completed_generation_responses": sum(call["status"] == "complete" for call in generations),
            "http_attempts": len(http_attempts), "http_outcome_counts": dict(outcomes),
            "http_status_counts": dict(Counter(str(a.get("http_status")) for a in http_attempts)),
            "http_error_categories": dict(categories),
            "before_report_sha256": before_report_sha,
            "record_sha256": {path.relative_to(run).as_posix(): sha(path) for path, _, _ in recovered},
        }
        report["trials"] = [record for _, _, record in recovered]
        report["status"] = "needs_attention"
        report["semantic_review_status"] = REVIEW_PENDING
        report["interruption"] = interruption
        report["reconciliation"] = deepcopy(event)
        report["by_split"] = {
            split: aggregate([record for record in report["trials"] if record["split"] == split])
            for split in ("development", "held_out")
        }
        write_progress(run, report, writer)
        event["report_sha256"] = sha(report_path)
        stamp = observed.replace(":", "").replace("+", "_")
        writer.json(run / "reconciliations" / f"{stamp}.json", event)
        writer.json(latest, event)
        return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=BASE / "runs/baseline-sol-max-v1")
    parser.add_argument("--reason", required=True)
    parser.add_argument("--interrupted-at", help="Optional actual ISO timestamp with timezone; never inferred")
    args = parser.parse_args(argv)
    result = reconcile(args.run_dir, reason=args.reason, interrupted_at=args.interrupted_at)
    print(json.dumps({
        "status": result["status"], "trial_status_counts": result["reconciliation"]["trial_status_counts"],
        "http_outcome_counts": result["reconciliation"]["http_outcome_counts"],
        "http_error_categories": result["reconciliation"]["http_error_categories"],
        "summary": result["summary"], "trace_bytes_unchanged": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
