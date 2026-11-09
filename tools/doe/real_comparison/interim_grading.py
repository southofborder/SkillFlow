"""Isolated, user-authorized interim review; never claims full cohort closure."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import shutil

from . import exploratory_grading as grading
from .protocol import canonical_hash, sha256, utc_now, write_json
from .semantic_metrics import grading_template

SCHEMA = "skillflow-interim-direct-review-v1"
CUTOFF = "2026-10-22T06:09:05.879527+00:00"
COHORT = (
    "real-018_chain_r2", "real-018_audit_r2", "real-016_chain_r1", "real-016_audit_r1",
    "real-011_audit_r2", "real-011_chain_r2", "real-008_chain_r3", "real-008_audit_r3",
    "real-009_chain_r1", "real-009_audit_r1", "real-008_audit_r1", "real-008_chain_r1",
    "real-020_chain_r1", "real-020_audit_r1", "real-014_chain_r3", "real-014_audit_r3",
    "real-006_audit_r2", "real-006_chain_r2", "real-014_chain_r1", "real-014_audit_r1",
    "real-018_audit_r1", "real-018_chain_r1", "real-024_audit_r3", "real-024_chain_r3",
    "real-013_audit_r2", "real-013_chain_r2", "real-003_chain_r3",
)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def prepare(run_dir, out_dir):
    run, out = Path(run_dir).resolve(), Path(out_dir).resolve()
    if out.exists() or out.is_relative_to(run) or run.is_relative_to(out):
        raise ValueError("A fresh interim directory outside the live run is required")
    frozen = read(run / "freeze.json")
    for name, digest in frozen["files"].items():
        if sha256(run / name) != digest:
            raise ValueError("Frozen input changed: " + name)
    rows = []
    for wid in COHORT:
        workflow = run / "workflows" / wid
        result = read(workflow / "result.json")
        registration = read(workflow / "registration.json")
        if (result["status"] != "complete" or registration["method"] not in {"audit", "chain"}
                or registration["kind"] != "main" or result["finished_at"] > CUTOFF
                or sha256(workflow / "answer.txt") != result["answer_sha256"]):
            raise ValueError("The fixed metadata-selected completed cohort does not match: " + wid)
        rows.append({"workflow_id": wid, "case_id": registration["case_id"],
                     "method": registration["method"], "repeat": registration["repeat"],
                     "result_sha256": sha256(workflow / "result.json"),
                     "answer_sha256": sha256(workflow / "answer.txt")})
    out.mkdir(parents=True)
    amendment = {"schema_version": SCHEMA, "recorded_at": utc_now(),
        "exact_user_instruction": "同时先对已有答案进行审核，看目前的ai直接生成的doe分析是否正确。",
        "superseded_gate": "For this separate interim review only, semantic review may begin before all 264 outcomes close.",
        "unchanged": "Target generation, source cases, references, prompts, schedule, limits, primary criteria and all failures.",
        "no_target_feedback": True, "target_regeneration_authorized": False,
        "full_cohort_closed": False, "human_verified": False,
        "subset_limit": "All 27 direct main outputs complete at the fixed metadata cutoff; readiness is not random sampling. No population accuracy or method-advantage inference.",
        "final_review_limit": "Keep these labels outside final fresh blinded graders. Disclose early review and incomplete method blinding."}
    write_json(out / "interim-amendment.json", amendment, immutable=True)
    snapshot = {"schema_version": SCHEMA, "created_at": utc_now(), "source_run": str(run),
        "metadata_cutoff": CUTOFF, "subset_outputs": len(rows), "full_planned_outcomes": 264,
        "full_cohort_closed": False, "source_freeze_sha256": sha256(run / "freeze.json"),
        "amendment_sha256": sha256(out / "interim-amendment.json"), "cohort": rows}
    write_json(out / "interim-snapshot.json", snapshot, immutable=True)
    for name in grading.COMMON_RULES:
        target = out / "common-rules" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run / name, target)
    shutil.copyfile(out / "interim-amendment.json", out / "common-rules/interim-amendment.json")
    order = list(rows)
    random.Random(20261020).shuffle(order)
    assignments, private = [], []
    for row in order:
        wid, cid = row["workflow_id"], row["case_id"]
        candidate_id = canonical_hash({"interim": SCHEMA, "workflow": wid})[:20]
        packet = out / "packets" / candidate_id
        packet.mkdir(parents=True)
        source = run / "cases" / cid
        shutil.copytree(source / "source", packet / "source")
        for name in ("source-bundle.txt", "source-manifest.json"):
            shutil.copyfile(source / name, packet / name)
        shutil.copyfile(run / "references" / (cid + ".json"), packet / "reference.json")
        shutil.copyfile(run / "workflows" / wid / "answer.txt", packet / "candidate.txt")
        reference = read(packet / "reference.json")
        if reference.get("human_verified") is not False:
            raise ValueError("Interim references must retain their exploratory nonhuman status")
        template = {"schema_version": grading.SCHEMA, "evidence_level": grading.EVIDENCE_LEVEL,
            "candidate_id": candidate_id, "candidate_sha256": sha256(packet / "candidate.txt"),
            "reference_sha256": sha256(packet / "reference.json"),
            "source_sha256": reference["source_sha256"], "source_bundle_sha256": sha256(packet / "source-bundle.txt"),
            "interim_snapshot_sha256": sha256(out / "interim-snapshot.json"),
            "reviewer_id": "", "agent_id": "", "scoring_role": "interim_primary",
            "human_verified": False, "actual_human_review_work_seconds": None,
            "judgment": "pending_assistant", "check_results": [
                {"check_id": c["id"], "status": "pending", "reason": "", "source_evidence": [], "candidate_evidence": []}
                for c in reference["mandatory_checks"]],
            "matched_exposure_ids": [], "findings": [], "reference_correction_proposals": []}
        template.update(grading_template(reference, "audit"))
        write_json(packet / "grade.template.json", template, immutable=True)
        public = {"candidate_id": candidate_id, "packet": "packets/" + candidate_id,
                  "common_rules": "common-rules", "single_candidate_per_fresh_agent": True}
        assignments.append(public)
        private.append({**row, **public})
    write_json(out / "assignments.json", {"schema_version": SCHEMA, "assignments": assignments}, immutable=True)
    write_json(out / "private-map.json", {"schema_version": SCHEMA, "assignments": private}, immutable=True)
    files = {p.relative_to(out).as_posix(): sha256(p) for p in out.rglob("*") if p.is_file()}
    write_json(out / "interim-packet-freeze.json", {"schema_version": SCHEMA, "created_at": utc_now(),
        "full_cohort_closed": False, "subset_outputs": len(rows), "files": files,
        "adapter_sha256": sha256(Path(__file__)), "model_calls": 0}, immutable=True)
    (out / "submissions").mkdir()
    return {"packets": len(rows), "model_calls": 0, "full_cohort_closed": False}


def validate(root, submission):
    root, submission = Path(root).resolve(), Path(submission).resolve()
    seal = read(root / "interim-packet-freeze.json")
    grade = read(submission)
    matches = [x for x in read(root / "assignments.json")["assignments"] if x["candidate_id"] == grade.get("candidate_id")]
    if len(matches) != 1:
        raise ValueError("Submission is not bound to one fixed interim packet")
    relative = matches[0]["packet"]
    for name, digest in seal["files"].items():
        if (name.startswith(relative + "/") or name.startswith("common-rules/")
                or name in {"assignments.json", "interim-snapshot.json", "interim-amendment.json"}):
            if sha256(root / name) != digest:
                raise ValueError("Interim input changed: " + name)
    packet = root / relative
    for key, name in (("candidate_sha256", "candidate.txt"), ("reference_sha256", "reference.json"),
                      ("source_bundle_sha256", "source-bundle.txt")):
        if grade.get(key) != sha256(packet / name):
            raise ValueError("Interim grade hash mismatch: " + key)
    if grade.get("interim_snapshot_sha256") != sha256(root / "interim-snapshot.json"):
        raise ValueError("Grade binds a different interim snapshot")
    grading.validate_assistant_grade(grade, read(packet / "reference.json"), source_root=packet / "source",
                                      candidate_text=(packet / "candidate.txt").read_text(encoding="utf-8"))
    return {"candidate_id": grade["candidate_id"], "judgment": grade["judgment"],
            "interim_only": True, "human_verified": False, "validation": "passed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare"); p.add_argument("--run-dir", required=True); p.add_argument("--out-dir", required=True)
    p = sub.add_parser("validate"); p.add_argument("--root", required=True); p.add_argument("--submission", required=True)
    args = parser.parse_args()
    result = prepare(args.run_dir, args.out_dir) if args.command == "prepare" else validate(args.root, args.submission)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
