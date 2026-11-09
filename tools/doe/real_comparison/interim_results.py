"""Seal and summarize the separately authorized fixed interim assistant review.

This module never asserts full-cohort closure, changes references, or launches
models. Its labels cannot be used as the final comparison's fresh primary labels.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from . import interim_grading
from .assessment import second_review_sample
from .exploratory_results import _disputes, _primary_detail
from .protocol import SEED, sha256, utc_now, write_json

SCHEMA = "skillflow-interim-assistant-results-v1"
EVIDENCE = "assistant_exploratory_not_human_gold"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def verify_inputs(root):
    root = Path(root).resolve()
    seal = read(root / "interim-packet-freeze.json")
    snapshot = read(root / "interim-snapshot.json")
    if (seal.get("full_cohort_closed") is not False
            or snapshot.get("full_cohort_closed") is not False
            or snapshot.get("subset_outputs") != 27):
        raise ValueError("The interim review requires its explicit fixed27 open-cohort snapshot")
    for name, digest in seal["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or sha256(path) != digest:
            raise ValueError("A sealed interim input changed: " + name)
    assignments = read(root / "assignments.json")["assignments"]
    if len(assignments) != 27 or len({r["candidate_id"] for r in assignments}) != 27:
        raise ValueError("The complete fixed27 candidate roster is required")
    return root, {r["candidate_id"]: r for r in assignments}


def _record(root, relative, candidate, role, expected_agent=None):
    path = (root / relative).resolve()
    if not path.is_relative_to(root / "submissions"):
        raise ValueError("An interim grade must remain inside its submissions directory")
    interim_grading.validate(root, path)
    grade = read(path)
    if (grade.get("candidate_id") != candidate or grade.get("scoring_role") != role
            or grade.get("agent_id") != grade.get("reviewer_id")
            or (expected_agent is not None and grade.get("agent_id") != expected_agent)
            or grade.get("chain_assessment") is not None):
        raise ValueError("Interim grade identity, role or single-output scope mismatch")
    packet = root / "packets" / candidate
    template = read(packet / "grade.template.json")
    if grade.get("source_sha256") != template.get("source_sha256"):
        raise ValueError("Interim grade source identity differs from the sealed template")
    return {"path": path.relative_to(root).as_posix(), "sha256": sha256(path),
            "agent_id": grade["agent_id"], "grade": grade}


def seal_primary(root, out_path):
    root, assignments = verify_inputs(root)
    journal = read(root / "dispatch-progress.json")
    rows = {r["candidate_id"]: r for r in journal["assignments"]}
    if set(rows) != set(assignments):
        raise ValueError("Interim dispatch journal differs from the fixed roster")
    records = {}
    for candidate, row in sorted(rows.items()):
        if row.get("state") != "completed_validated":
            raise ValueError("Complete every fixed interim primary before sealing")
        records[candidate] = _record(root, row["submission"], candidate,
                                     "interim_primary", row["agent_name"])
    if len({r["agent_id"] for r in records.values()}) != 27:
        raise ValueError("Each interim output requires a different fresh primary agent")
    result = {"schema_version": SCHEMA, "kind": "primary_seal", "created_at": utc_now(),
              "evidence_level": EVIDENCE, "interim_snapshot_sha256": sha256(root / "interim-snapshot.json"),
              "packet_freeze_sha256": sha256(root / "interim-packet-freeze.json"),
              "full_cohort_closed": False, "fixed_denominator": 27,
              "human_verified": False, "actual_human_review_work_seconds": None,
              "records": records, "model_calls": 0}
    write_json(Path(out_path), result, immutable=True)
    return result


def _primary(root, path):
    primary = read(path)
    _, assignments = verify_inputs(root)
    if (primary.get("schema_version") != SCHEMA or primary.get("kind") != "primary_seal"
            or primary.get("full_cohort_closed") is not False
            or primary.get("interim_snapshot_sha256") != sha256(root / "interim-snapshot.json")
            or primary.get("packet_freeze_sha256") != sha256(root / "interim-packet-freeze.json")
            or set(primary.get("records", {})) != set(assignments)):
        raise ValueError("The full fixed27 primary seal does not bind this interim epoch")
    for candidate, item in primary["records"].items():
        record = _record(root, item["path"], candidate, "interim_primary", item["agent_id"])
        if record != item:
            raise ValueError("A sealed interim primary changed")
    return primary


def prepare_rechecks(root, primary_path, out_path):
    root = Path(root).resolve()
    primary = _primary(root, primary_path)
    grades = [r["grade"] for _, r in sorted(primary["records"].items())]
    selected = set(second_review_sample(grades, seed=SEED))
    selected.update(c for c, r in primary["records"].items() if _disputes(r["grade"]))
    result = {"schema_version": SCHEMA, "kind": "recheck_assignments", "created_at": utc_now(),
              "primary_seal_sha256": sha256(primary_path), "seed": SEED,
              "evidence_level": EVIDENCE, "full_cohort_closed": False,
              "selection_policy": "All initial errors and disputes plus ceil(20 percent of initial passes), selected only after all27 primary labels are sealed.",
              "assignments": [{"candidate_id": c, "packet": "packets/" + c,
                               "common_rules": "common-rules", "assignment_kind": "interim_recheck"}
                              for c in sorted(selected)], "model_calls": 0}
    write_json(Path(out_path), result, immutable=True)
    return result


def reconcile(primary, secondary=None, required=False):
    issues = list(_disputes(primary))
    if required and secondary is None:
        issues.append("mandatory_independent_recheck_missing")
    if secondary is not None:
        issues.extend("secondary_" + x for x in _disputes(secondary))
        if primary["judgment"] != secondary["judgment"]:
            issues.append("coarse_judgment_disagreement")
        if sorted((r["check_id"], r["status"]) for r in primary["check_results"]) != sorted(
                (r["check_id"], r["status"]) for r in secondary["check_results"]):
            issues.append("mandatory_check_disagreement")
    detail = _primary_detail(primary, secondary)
    issues.extend(detail["metric_disputes"])
    return {"judgment": "indeterminate" if issues else primary["judgment"],
            "disputes": sorted(set(issues)),
            "adjudicated_grade": None if issues else detail["adjudicated_grade"]}


def summarize(root, primary_path, recheck_path, secondary_paths=()):
    root = Path(root).resolve()
    primary = _primary(root, primary_path)
    selection = read(recheck_path)
    if (selection.get("primary_seal_sha256") != sha256(primary_path)
            or selection.get("schema_version") != SCHEMA or selection.get("seed") != SEED):
        raise ValueError("Independent rechecks require the exact sealed interim primary")
    expected = set(second_review_sample([r["grade"] for r in primary["records"].values()], seed=SEED))
    expected.update(c for c, r in primary["records"].items() if _disputes(r["grade"]))
    required = {r["candidate_id"] for r in selection["assignments"]}
    if required != expected:
        raise ValueError("Interim independent recheck selection changed")
    secondary = {}
    for path in secondary_paths:
        grade = read(path)
        candidate = grade.get("candidate_id")
        if candidate not in required or candidate in secondary:
            raise ValueError("Duplicate or unassigned independent interim recheck")
        record = _record(root, Path(path).resolve().relative_to(root), candidate, "interim_recheck")
        if record["agent_id"] == primary["records"][candidate]["agent_id"]:
            raise ValueError("An independent interim recheck requires a different agent")
        secondary[candidate] = record
    private = {r["candidate_id"]: r for r in read(root / "private-map.json")["assignments"]}
    rows, errors, disputes = [], [], []
    for candidate, record in sorted(primary["records"].items()):
        p = record["grade"]
        s = secondary.get(candidate, {}).get("grade")
        resolved = reconcile(p, s, candidate in required)
        item = private[candidate]
        row = {"candidate_id": candidate, "workflow_id": item["workflow_id"],
               "case_id": item["case_id"], "method": item["method"], "repeat": item["repeat"],
               "primary_judgment": p["judgment"], "secondary_judgment": s["judgment"] if s else None,
               "required_recheck": candidate in required, "primary_path": record["path"],
               "secondary_path": secondary[candidate]["path"] if candidate in secondary else None,
               **resolved}
        rows.append(row)
        if row["disputes"]:
            disputes.append({"candidate_id": candidate, "workflow_id": item["workflow_id"],
                             "issues": row["disputes"], "reference_correction_proposals": {
                                 "primary": p.get("reference_correction_proposals", []),
                                 "secondary": s.get("reference_correction_proposals", []) if s else []}})
        for role, grade in (("primary", p), ("independent_recheck", s)):
            if grade is None:
                continue
            for group in ("error_records", "findings"):
                errors.extend({"candidate_id": candidate, "workflow_id": item["workflow_id"],
                               "role": role, "record_kind": group, "record": error}
                              for error in grade.get(group, []))
            for group, field, bad in (("check_results", "status", {"fail"}),
                    ("claim_units", "assessment", {"unsupported"}),
                    ("receiving_point_coverage", "status", {"missed"}),
                    ("reduction_assessments", "status", {"missing", "harmful"})):
                errors.extend({"candidate_id": candidate, "workflow_id": item["workflow_id"],
                               "role": role, "record_kind": group, "record": error}
                              for error in grade.get(group, []) if error.get(field) in bad)
    counts = Counter(r["judgment"] for r in rows)
    passed, failed = counts["satisfies_reference"], counts["substantive_error"]
    unknown = 27 - passed - failed
    return {"schema_version": SCHEMA, "created_at": utc_now(), "evidence_level": EVIDENCE,
            "full_cohort_closed": False, "fixed_denominator": 27, "model_calls": 0,
            "human_verified": False, "actual_human_review_work_seconds": None,
            "interim_snapshot_sha256": sha256(root / "interim-snapshot.json"),
            "primary_seal_sha256": sha256(primary_path), "recheck_assignments_sha256": sha256(recheck_path),
            "primary_labels": dict(Counter(r["primary_judgment"] for r in rows)),
            "independent_rechecks_required": len(required), "independent_rechecks_valid": len(secondary),
            "resolved_passes": passed, "resolved_failures": failed, "unknown": unknown,
            "pass_fraction_bounds": [passed / 27, (passed + unknown) / 27],
            "population_or_method_advantage_inference": "Not available: readiness-selected interim subset, no closed final cohort, exploratory assistant references and labels.",
            "rows": rows, "individual_errors": errors, "disputes": disputes}


def write_summary(report, out_dir):
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "interim-results.json", report, immutable=True)
    for name, rows in (("individual-errors", report["individual_errors"]), ("disputes", report["disputes"])):
        write_json(out / (name + ".json"), rows, immutable=True)
    columns = ["candidate_id", "workflow_id", "case_id", "method", "repeat", "primary_judgment",
               "secondary_judgment", "judgment", "required_recheck", "primary_path", "secondary_path", "disputes"]
    with (out / "output-judgments.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in report["rows"]:
            writer.writerow({key: json.dumps(row[key], ensure_ascii=False) if isinstance(row[key], (dict, list))
                             else row[key] for key in columns})
    write_json(out / "derived-freeze.json", {"schema_version": SCHEMA, "created_at": utc_now(),
        "full_cohort_closed": False, "files": {p.name: sha256(p) for p in sorted(out.iterdir()) if p.is_file()}}, immutable=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("seal-primary", "prepare-rechecks", "summarize"):
        item = sub.add_parser(command)
        item.add_argument("--root", required=True)
        item.add_argument("--out", required=True)
        if command != "seal-primary":
            item.add_argument("--primary", required=True)
        if command == "summarize":
            item.add_argument("--rechecks", required=True)
            item.add_argument("--secondary", action="append", default=[])
    args = parser.parse_args()
    if args.command == "seal-primary":
        result = seal_primary(args.root, args.out)
    elif args.command == "prepare-rechecks":
        result = prepare_rechecks(args.root, args.primary, args.out)
    else:
        result = summarize(args.root, args.primary, args.rechecks, args.secondary)
        write_summary(result, args.out)
    print(json.dumps({"schema_version": SCHEMA, "command": args.command, "model_calls": 0,
                      "full_cohort_closed": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
