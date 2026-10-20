"""Human-source references, common grading, assignments and paired statistics.

This module cannot convert an assistant draft into human approval. Human records
are explicit submissions, independently attributed and bound to exact bytes.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path

from .protocol import SCHEMA, SEED, METHODS, canonical_hash, sha256, utc_now, write_json

REFERENCE_FIELDS = ("declared_purpose", "required_behavior", "receiving_points",
                    "necessary_sensitive_uses", "supported_excesses", "unknowns",
                    "preservation_checks", "mandatory_checks")
EXPOSURE_FIELDS = ("source", "sensitive_scope", "version", "condition", "recipient", "boundary_event")
JUDGMENTS = {"satisfies_reference", "substantive_error", "indeterminate"}
CONFIRMATION = "I personally verified this source reference."


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def exposure_key(unit):
    """Hash human-normalized units, never infer equivalence from similar words."""
    if any(not isinstance(unit.get(k), str) or not unit[k].strip() for k in EXPOSURE_FIELDS):
        raise ValueError("A normalized exposure requires all six material identity fields")
    return canonical_hash({k: unit[k].strip() for k in EXPOSURE_FIELDS})


def validate_reference(reference):
    if reference.get("user_request") is not None:
        raise ValueError("An independent user task is outside this comparison")
    if reference.get("purpose_basis") != "skill_declared_purpose_only":
        raise ValueError("Reference must use declared-purpose-only auditing")
    if any(k not in reference or not isinstance(reference[k], list) for k in REFERENCE_FIELDS):
        raise ValueError("Reference ledger is missing a required list")
    if not reference["declared_purpose"] or not reference["receiving_points"] or not reference["mandatory_checks"]:
        raise ValueError("An empty reference template cannot be approved")
    identifiers = [item.get("id") for item in reference["mandatory_checks"]]
    if any(not value for value in identifiers) or len(set(identifiers)) != len(identifiers):
        raise ValueError("Mandatory reference checks require distinct IDs")
    for key in ("declared_purpose", "required_behavior", "receiving_points", "mandatory_checks"):
        if any(not item.get("evidence") for item in reference[key]):
            raise ValueError("Reference facts require original-source evidence")
    keys = [exposure_key(unit) for unit in reference["supported_excesses"]]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate normalized exposure units require consolidation")
    exposure_ids = [unit.get("id") for unit in reference["supported_excesses"]]
    if (any(not isinstance(value, str) or not value.strip() for value in exposure_ids)
            or len(exposure_ids) != len(set(exposure_ids))):
        raise ValueError("Distinct normalized excesses require nonempty, unique exposure IDs")
    return reference


def validate_reference_evidence(run_dir, reference):
    """Check human-review evidence against unchanged physical source lines.

    Exact quotation checking is an engineering safeguard, not a semantic
    judgment about whether the quotation supports the interpretation.
    """
    validate_reference(reference)
    contract_path = Path(run_dir) / "grading-contract.json"
    if contract_path.exists():
        expected = read_json(contract_path)["grading_schema_version"]
        if reference.get("grading_schema_version") != expected:
            raise ValueError("Reference differs from the frozen human grading contract")
        from .semantic_metrics import validate_grading_reference
        validate_grading_reference(reference)
    case_id = reference.get("case_id", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", case_id):
        raise ValueError("Unsafe reference case ID")
    if reference.get("coverage_state") != "complete_for_human_verification":
        raise ValueError("Complete the source-reference coverage before human confirmation")
    source = (Path(run_dir) / "cases" / case_id / "source").resolve()
    for group in REFERENCE_FIELDS:
        for fact in reference[group]:
            evidence = fact.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                raise ValueError("Every reference interpretation requires original-source evidence")
            for item in evidence:
                if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                    raise ValueError("Use physical path, start_line, end_line and exact quote evidence")
                path = (source / item["path"]).resolve()
                if not path.is_relative_to(source) or not path.is_file():
                    raise ValueError("Reference evidence is missing or escapes the frozen source")
                start, end = item.get("start_line"), item.get("end_line")
                if (isinstance(start, bool) or isinstance(end, bool)
                        or not isinstance(start, int) or not isinstance(end, int)
                        or start < 1 or end < start):
                    raise ValueError("Reference evidence requires a valid physical line interval")
                lines = path.read_text(encoding="utf-8-sig").splitlines()
                if end > len(lines) or item.get("quote") != "\n".join(lines[start - 1:end]):
                    raise ValueError("Reference quotation differs from the original source lines")
    return reference


def import_human_attestation(run_dir, submission_path):
    """Import an explicitly submitted human attestation, not an agent decision.

Identity is self-attested; this is not a biometric or cryptographic personhood
verification service. The study record must preserve this boundary.
"""
    run, submission = Path(run_dir), read_json(submission_path)
    roster = read_json(run / "human-roster.json").get("reviewers", [])
    people = {p["reviewer_id"]: p for p in roster}
    person = people.get(submission.get("reviewer_id"))
    if not person or person.get("human") is not True or person.get("role") != "reference_verifier":
        raise ValueError("Register the actual human reference verifier before importing an attestation")
    required = ("case_id", "reviewer_id", "source_sha256", "reference_sha256", "attestation_id", "attested_at")
    if any(not isinstance(submission.get(k), str) or not submission[k].strip() for k in required):
        raise ValueError("Incomplete human attestation identity")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", submission["case_id"]):
        raise ValueError("Unsafe reference case ID")
    if submission.get("human") is not True or submission.get("approved") is not True:
        raise ValueError("Assistant or pending records cannot approve a reference")
    if submission.get("confirmation") != CONFIRMATION:
        raise ValueError("The explicit personal human confirmation is required")
    if submission.get("role") != "reference_verifier":
        raise ValueError("Unexpected attestation role")
    ref_path = run / "references" / f"{submission['case_id']}.json"
    reference = validate_reference_evidence(run, read_json(ref_path))
    if reference.get("state") in {"template", "draft_pending", "placeholder"}:
        raise ValueError("Fill the reference ledger before confirming it")
    if sha256(ref_path) != submission["reference_sha256"] or reference.get("source_sha256") != submission["source_sha256"]:
        raise ValueError("Human confirmation does not match the exact source/reference version")
    safe_id = hashlib.sha256(submission["attestation_id"].encode()).hexdigest()[:24]
    path = run / "approvals" / "submissions" / f"{safe_id}.json"
    write_json(path, submission, immutable=True)
    manifest_path = run / "approvals" / "import-manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {"schema_version": SCHEMA, "records": []}
    item = {"path": str(path.relative_to(run)).replace("\\", "/"), "sha256": sha256(path),
            "case_id": submission["case_id"], "reviewer_id": submission["reviewer_id"],
            "import_source": "human_user_submission"}
    if item not in manifest["records"]:
        manifest["records"].append(item)
        write_json(manifest_path, manifest)
    return item


def finalize_human_references(run_dir, case_records):
    run = Path(run_dir)
    manifest = read_json(run / "approvals" / "import-manifest.json")
    attestations = []
    for item in manifest["records"]:
        path = run / item["path"]
        if sha256(path) != item["sha256"] or item["import_source"] != "human_user_submission":
            raise ValueError("Imported human attestation identity changed")
        attestations.append(read_json(path))
    references = []
    for case in case_records:
        case_id = case["case_id"]
        path = run / "references" / f"{case_id}.json"
        reference = validate_reference_evidence(run, read_json(path))
        digest = sha256(path)
        matches = [a for a in attestations if a["case_id"] == case_id and a["reference_sha256"] == digest
                   and a["source_sha256"] == case["source_sha256"] and a.get("human") is True
                   and a.get("approved") is True and a.get("confirmation") == CONFIRMATION]
        if len({a["reviewer_id"] for a in matches}) != 2:
            raise ValueError(f"Two distinct human confirmations are required: {case_id}")
        references.append({"case_id": case_id, "source_sha256": case["source_sha256"],
                           "reference_sha256": digest, "path": str(path.relative_to(run)).replace("\\", "/"),
                           "state": "approved"})
    write_json(run / "references.json", {"schema_version": SCHEMA, "entries": references}, immutable=True)
    freeze = {"schema_version": SCHEMA, "files": {item["path"]: item["reference_sha256"] for item in references},
              "references_sha256": sha256(run / "references.json"),
              "attestations_sha256": sha256(run / "approvals" / "import-manifest.json")}
    write_json(run / "reference-freeze.json", freeze, immutable=True)
    return freeze


def verify_human_reference_freeze(run_dir, case_id=None):
    """Verify the frozen, personally confirmed reference before accepting scores."""
    run = Path(run_dir).resolve()
    freeze = read_json(run / "reference-freeze.json")
    index_path = run / "references.json"
    imports_path = run / "approvals/import-manifest.json"
    if (freeze.get("references_sha256") != sha256(index_path)
            or freeze.get("attestations_sha256") != sha256(imports_path)):
        raise ValueError("The approved reference freeze or human attestations changed")
    people = {p["reviewer_id"]: p for p in read_json(run / "human-roster.json")["reviewers"]}
    attestations = []
    for item in read_json(imports_path)["records"]:
        path = (run / item["path"]).resolve()
        if (not path.is_relative_to((run / "approvals/submissions").resolve())
                or item.get("import_source") != "human_user_submission"
                or sha256(path) != item.get("sha256")):
            raise ValueError("A frozen personal source-reference confirmation changed")
        attestation = read_json(path)
        person = people.get(attestation.get("reviewer_id"), {})
        if person.get("human") is True and person.get("role") == "reference_verifier":
            attestations.append(attestation)
    entries = read_json(index_path)["entries"]
    if len({e["case_id"] for e in entries}) != len(entries):
        raise ValueError("The approved reference index contains duplicate cases")
    selected = [e for e in entries if case_id is None or e["case_id"] == case_id]
    if not selected:
        raise ValueError("No approved frozen source reference exists for this candidate")
    for entry in selected:
        path = (run / entry["path"]).resolve()
        if (not path.is_relative_to((run / "references").resolve())
                or entry.get("state") != "approved"
                or freeze.get("files", {}).get(entry["path"]) != entry.get("reference_sha256")
                or sha256(path) != entry.get("reference_sha256")):
            raise ValueError("A score requires the exact approved frozen reference")
        reference = validate_reference_evidence(run, read_json(path))
        if (reference.get("case_id") != entry["case_id"]
                or reference.get("source_sha256") != entry.get("source_sha256")):
            raise ValueError("The approved reference source identity changed")
        matches = {a["reviewer_id"] for a in attestations
                   if a.get("case_id") == entry["case_id"]
                   and a.get("source_sha256") == entry["source_sha256"]
                   and a.get("reference_sha256") == entry["reference_sha256"]
                   and a.get("human") is True and a.get("approved") is True
                   and a.get("confirmation") == CONFIRMATION
                   and a.get("attestation_id") and a.get("attested_at")}
        if len(matches) != 2:
            raise ValueError("Two frozen personal human confirmations are required for scoring")
    return selected


def validate_grade(grade, reference, *, method=None):
    """Validate evidence-based human grading without imposing an output schema."""
    if grade.get("human_verified") is not True or not grade.get("reviewer_id"):
        raise ValueError("An assistant draft is not a human-verified score")
    if grade.get("judgment") not in JUDGMENTS:
        raise ValueError("Unknown semantic judgment")
    checks = grade.get("check_results", [])
    expected = {item["id"] for item in reference["mandatory_checks"]}
    actual = [item.get("check_id") for item in checks]
    if set(actual) != expected or len(actual) != len(expected):
        raise ValueError("Every mandatory source check must be scored exactly once")
    if any(item.get("status") not in {"pass", "fail", "disputed"} or not item.get("reason") for item in checks):
        raise ValueError("Each check requires a status and source-based reason")
    findings = grade.get("findings", [])
    if grade["judgment"] == "satisfies_reference" and (
        any(item["status"] != "pass" for item in checks)
        or any(item.get("severity") in {"substantive", "disputed"} for item in findings)
    ):
        raise ValueError("A passing judgment contradicts a material check or finding")
    matched = grade.get("matched_exposure_ids", [])
    if len(matched) != len(set(matched)):
        raise ValueError("Duplicate exposure descriptions cannot receive additional credit")
    known = {unit["id"] for unit in reference["supported_excesses"]}
    if not set(matched).issubset(known):
        raise ValueError("Additional source-supported claims require an explicit reference corrigendum")
    if grade["judgment"] == "satisfies_reference" and set(matched) != known:
        raise ValueError("Abstaining on an adjudicated supported excess is a miss")
    if reference.get("grading_schema_version") or grade.get("grading_schema_version"):
        from .semantic_metrics import GRADING_SCHEMA_VERSION, validate_semantic_grade
        if reference.get("grading_schema_version") not in {None, GRADING_SCHEMA_VERSION}:
            raise ValueError("Unknown frozen human grading schema version")
        validate_semantic_grade(grade, reference, method=method)
    return grade


def paired_judgment(primary, secondary=None):
    if secondary is None:
        return primary["judgment"]
    return primary["judgment"] if primary["judgment"] == secondary["judgment"] else "indeterminate"


def second_review_sample(primary_grades, seed=SEED):
    failures = {g["candidate_id"] for g in primary_grades if g["judgment"] != "satisfies_reference"}
    passes = sorted(g["candidate_id"] for g in primary_grades if g["judgment"] == "satisfies_reference")
    random.Random(seed).shuffle(passes)
    return sorted(failures | set(passes[:math.ceil(len(passes) * .2)]))


def timed_assignments(case_ids, reviewers=("R1", "R2", "R3"), seed=SEED):
    if len(case_ids) != 24 or len(set(case_ids)) != 24 or len(set(reviewers)) != 3:
        raise ValueError("Timed review requires 24 distinct cases and three distinct reviewers")
    order = sorted(case_ids)
    random.Random(seed).shuffle(order)
    result = []
    for i, case_id in enumerate(order):
        for j, reviewer in enumerate(reviewers):
            method = METHODS[(i + j) % 3]
            anonymous = canonical_hash({"case": case_id, "reviewer": reviewer, "seed": seed})[:16]
            result.append({"assignment_id": anonymous, "case_id": case_id, "reviewer_id": reviewer,
                           "method": method, "repeat": 1, "seconds_cap": 1800,
                           "status": "pending_human", "source_reference_access": False})
    return result


def validate_timed_record(record, assignment, reference_reviewers):
    if record.get("human") is not True or record.get("reviewer_id") != assignment["reviewer_id"]:
        raise ValueError("Timed review requires an explicit record from its assigned human")
    if record["reviewer_id"] in set(reference_reviewers):
        raise ValueError("A reference author cannot provide the independent timed review")
    if record.get("assignment_id") != assignment["assignment_id"]:
        raise ValueError("Timed review assignment identity differs")
    seconds = record.get("active_seconds")
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not 0 <= seconds <= 1800:
        raise ValueError("Invalid active review duration")
    if record.get("status") not in {"finished", "timeout", "abandoned"}:
        raise ValueError("Unknown timed-review status")
    if record.get("status") == "timeout" and seconds != 1800:
        raise ValueError("A timeout is right-censored at the fixed active-time cap")
    return {**record, "censored": record["status"] != "finished",
            "correct_within_cap": record["status"] == "finished" and record.get("final_quality") == "correct"}


def holm_adjust(p_values):
    ordered = sorted(enumerate(p_values), key=lambda pair: pair[1])
    adjusted, running = [0.0] * len(p_values), 0.0
    for rank, (original, value) in enumerate(ordered):
        running = max(running, min(1.0, value * (len(p_values) - rank)))
        adjusted[original] = running
    return adjusted


def _quantile(values, probability):
    values = sorted(values)
    location = probability * (len(values) - 1)
    lo, hi = math.floor(location), math.ceil(location)
    return values[lo] + (values[hi] - values[lo]) * (location - lo)


def paired_cluster_statistics(case_differences, *, seed=SEED, bootstrap_samples=10000):
    """Equal case weight; repeats must already be averaged inside each case."""
    if not case_differences:
        return {"status": "insufficient_cases"}
    groups = defaultdict(list)
    for case in case_differences:
        groups[case["source_cluster"]].append(float(case["difference"]))
    ordered = [groups[k] for k in sorted(groups)]
    mean = sum(sum(g) for g in ordered) / sum(map(len, ordered))
    if len(ordered) < 8:
        return {"status": "insufficient_source_clusters", "difference": mean,
                "cases": len(case_differences), "clusters": len(ordered)}
    rng = random.Random(seed)
    samples = []
    for _ in range(bootstrap_samples):
        chosen = [rng.choice(ordered) for _ in ordered]
        samples.append(sum(sum(g) for g in chosen) / sum(map(len, chosen)))
    sums = [sum(g) for g in ordered]
    observed = abs(sum(sums))
    if len(ordered) <= 18:
        permutations = itertools.product((-1, 1), repeat=len(ordered))
        total = 2 ** len(ordered)
        count = sum(abs(sum(v * sign for v, sign in zip(sums, signs))) >= observed - 1e-12 for signs in permutations)
        p_value = count / total
    else:
        total = 100000
        count = sum(abs(sum(v * rng.choice((-1, 1)) for v in sums)) >= observed - 1e-12 for _ in range(total))
        p_value = (count + 1) / (total + 1)
    return {"status": "descriptive_with_cluster_uncertainty", "difference": mean,
            "cases": len(case_differences), "clusters": len(ordered), "bootstrap_samples": bootstrap_samples,
            "simultaneous_97_5_percent_interval": [_quantile(samples, .0125), _quantile(samples, .9875)],
            "two_sided_cluster_sign_flip_p": p_value,
            "limitations": "A small selected hard-Skill cohort does not establish a population error rate. Bootstrap intervals may degenerate when all observed paired differences are identical."}


def build_review_template(run_dir):
    run = Path(run_dir)
    template = {"schema_version": SCHEMA, "state": "requires_actual_human_registration",
                "reviewers": [], "required_roles": {"reference_verifier": 2, "timed_reviewer": 3},
                "assignment_slot_ids": {"reference_verifier": ["H1", "H2"], "timed_reviewer": ["R1", "R2", "R3"]},
                "note": "Register real human pseudonyms and role declarations. Assistant agents are not people and cannot submit human approvals."}
    write_json(run / "human-roster.template.json", template, immutable=True)
    return template
