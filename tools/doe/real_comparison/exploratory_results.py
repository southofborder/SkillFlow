"""Offline assistant-only measurements for the closed 216 + 48 comparison.

These functions never launch targets, import human grades, or edit references.
The primary seal precedes deterministic recheck selection. Chain measurements
are separate: missing chain work cannot invalidate resolved common audit work.
All estimates describe assistant labels against assistant source references.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import csv
from itertools import combinations
import json
import math
from pathlib import Path

from . import exploratory_grading as grading
from .assessment import (holm_adjust, paired_cluster_statistics, paired_judgment,
                         second_review_sample)
from .efficiency import efficiency_decision
from .protocol import METHODS, SEED, canonical_hash, sha256, utc_now, write_json
from .semantic_metrics import (CHAIN_LAYERS, CHAIN_LINKS, EXPOSURE_FIELDS,
    _evidence, _unit_metrics, reconcile_semantic_grades, stratified_check_metrics,
    validate_grade_evidence, validate_semantic_grade)

SCHEMA = "skillflow-exploratory-assistant-results-v1"
CHAIN_SCHEMA = SCHEMA + "-chain-secondary-v1"
EVIDENCE_LEVEL = grading.EVIDENCE_LEVEL
KNOWN = {"satisfies_reference", "substantive_error", "workflow_failure"}
EXECUTION_FAILURES = {"failed", "budget_exhausted", "context_limit", "protocol_violation",
                      "protocol_aborted", "not_reviewable", "timeout"}


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _context(grading_dir):
    root = Path(grading_dir).resolve()
    # Identity metadata locates the run; no candidate is opened before closure.
    private = _read(root / "private-map.json")
    entries, _ = grading.verify_closed_outputs(private["source_run"])
    frozen = _read(root / "packet-freeze.json")
    if frozen.get("schema_version") != grading.SCHEMA or frozen.get("planned_outputs") != 264:
        raise ValueError("The complete assistant packet freeze is required")
    if frozen.get("source_output_freeze_sha256") != sha256(Path(private["source_run"]) / "output-freeze.json"):
        raise ValueError("The assistant packets bind a different output cohort")
    for relative, digest in frozen["files"].items():
        if sha256(grading.inside(root, relative)) != digest:
            raise ValueError("A frozen assistant grading input changed")
    rows = private["assignments"]
    cases = {r["case_id"] for r in rows}
    expected = {(c, m, "main", r) for c in cases for m in METHODS for r in (1, 2, 3)}
    expected |= {(c, m, "review", 1) for c in cases for m in ("audit", "chain")}
    identity = lambda r: (r["case_id"], r["method"], r["kind"], r["repeat"])
    if (len(cases) != 24 or len(rows) != 264 or {identity(r) for r in rows} != expected
            or len({r["candidate_id"] for r in rows}) != 264
            or len({r["workflow_id"] for r in rows}) != 264
            or {r["workflow_id"]: identity(r) for r in rows} != {r["workflow_id"]: identity(r) for r in entries}
            or any(r.get("chain_secondary_required") != (r["method"] != "audit") for r in rows)):
        raise ValueError("Preserve exactly the planned 216 main and 48 reviewed identities")
    return root, {r["candidate_id"]: r for r in rows}, frozen


def _binding(root):
    return {"packet_freeze_sha256": sha256(root / "packet-freeze.json"),
            "private_map_sha256": sha256(root / "private-map.json")}


def _output_location(root, path):
    target = Path(path).resolve()
    source_run = Path(_read(root / "private-map.json")["source_run"]).resolve()
    if (target.is_relative_to(source_run) or target.is_relative_to(root / "packets")
            or target.is_relative_to(root / "common-rules")):
        raise ValueError("Write new assistant records outside frozen inputs and generation outputs")


def _grade_record(root, path, *, role, chain=False):
    path = Path(path).resolve()
    result = grading.validate_submission(root, path)
    grade = result["validated_grade"]
    if grade.get("scoring_role") != role:
        raise ValueError("Submission scoring role differs from its assignment")
    if (grade.get("chain_assessment") is not None) != chain:
        raise ValueError("Common primary judgments and chain secondaries require separate submissions")
    return {"path": str(path), "sha256": sha256(path), **result}


def seal_primary_submissions(grading_dir, submission_paths, out_path):
    """Freeze the submitted primary set, including explicit missing identities.

    A partial seal supports a truthful pending report but cannot select checks.
    A completed epoch requires a fresh seal; existing seals are never replaced.
    """
    root, mapping, _ = _context(grading_dir)
    _output_location(root, out_path)
    records = {}
    for path in submission_paths:
        item = _grade_record(root, path, role="primary")
        candidate = item["validated_grade"]["candidate_id"]
        if candidate in records or candidate not in mapping:
            raise ValueError("Duplicate or unplanned primary submission")
        records[candidate] = item
    result = {"schema_version": SCHEMA, "kind": "primary_seal", "created_at": utc_now(),
        **_binding(root), "evidence_level": EVIDENCE_LEVEL,
        "planned_results": 264, "submitted_results": len(records),
        "missing_candidate_ids": sorted(set(mapping) - set(records)),
        "records": records, "human_reference_confirmation": "pending",
        "actual_human_scoring": "pending", "actual_human_review_work_seconds": None,
        "model_calls": 0}
    write_json(out_path, result, immutable=True)
    return result


def _load_primary(root, path):
    result = _read(path)
    if (result.get("schema_version") != SCHEMA or result.get("kind") != "primary_seal"
            or result.get("evidence_level") != EVIDENCE_LEVEL or result.get("planned_results") != 264
            or result.get("submitted_results") != len(result.get("records", {}))
            or any(result.get(k) != v for k, v in _binding(root).items())):
        raise ValueError("The primary seal does not bind this assistant grading epoch")
    for candidate, item in result["records"].items():
        if sha256(item["path"]) != item["sha256"]:
            raise ValueError("A sealed primary submission changed")
        checked = _grade_record(root, item["path"], role="primary")
        if checked["validated_grade"]["candidate_id"] != candidate or checked != item:
            raise ValueError("A primary seal contains an inconsistent validated submission")
    expected = {r["candidate_id"] for r in _read(root / "private-map.json")["assignments"]}
    if (not set(result["records"]).issubset(expected)
            or result.get("missing_candidate_ids") != sorted(expected - set(result["records"]))):
        raise ValueError("The primary seal lost its explicit planned missing identities")
    return result


def _disputes(grade):
    result = []
    if grade.get("judgment") == "indeterminate":
        result.append("indeterminate_content")
    if grade.get("reference_correction_proposals"):
        result.append("source_reference_correction_proposed")
    for group in ("check_results", "claim_units", "receiving_point_coverage",
                  "reduction_assessments", "error_records", "findings"):
        if any(any(r.get(k) == "disputed" for k in
                   ("status", "assessment", "severity", "functionality_impact")) for r in grade.get(group, [])):
            result.append(group)
    return result


def _primary_detail(primary, secondary=None):
    result = reconcile_semantic_grades(primary, secondary)
    if secondary is not None:
        def findings(grade):
            return sorted(tuple(str(r.get(k, "")) for k in ("category", "severity", "functionality_impact"))
                          for r in grade.get("findings", []))
        if findings(primary) != findings(secondary):
            result["metric_disputes"].append("findings_classification_disagreement")
            result["adjudicated_grade"] = None
    return result


def _selection(primary):
    records = primary["records"]
    grades = [{**r["validated_grade"], "candidate_id": c} for c, r in sorted(records.items())]
    selected = set(second_review_sample(grades, seed=SEED))
    for candidate, item in records.items():
        if (_disputes(item["validated_grade"]) or not item["protocol_eligible"]
                or item["workflow_primary_judgment"] == "workflow_failure"
                or item["execution_status"] in EXECUTION_FAILURES):
            selected.add(candidate)
    return sorted(selected)


def prepare_secondary_assignments(grading_dir, primary_seal, out_path, *,
                                  recheck_agents=None, chain_agents=None):
    """Select initial errors/disputes/failures and seeded 20 percent passes.

    Optional maps bind candidate IDs to actual independently assigned agent IDs.
    When absent, the receiving record must still identify a different agent;
    assignment identity is then self-reported rather than independently verified.
    No primary label or method is placed in the public assignment rows.
    """
    root, mapping, _ = _context(grading_dir)
    _output_location(root, out_path)
    primary = _load_primary(root, primary_seal)
    if set(primary["records"]) != set(mapping):
        raise ValueError("Seal all 264 primary submissions before secondary selection")
    rows = []
    for kind, candidates, agents in (
            ("primary_recheck", _selection(primary), recheck_agents or {}),
            ("chain_secondary", sorted(c for c, r in mapping.items() if r["chain_secondary_required"]), chain_agents or {})):
        for candidate in candidates:
            previous = primary["records"][candidate]["validated_grade"]["agent_id"]
            if agents.get(candidate) == previous:
                raise ValueError("An independent assistant check requires a different agent")
            rows.append({"candidate_id": candidate, "assignment_kind": kind,
                "packet": mapping[candidate]["packet"], "common_rules": "common-rules",
                "excluded_agent_ids": [previous], "assigned_agent_id": agents.get(candidate)})
    result = {"schema_version": SCHEMA, "kind": "secondary_assignments", "created_at": utc_now(),
        **_binding(root), "primary_seal_sha256": sha256(primary_seal), "seed": SEED,
        "selection_policy": "All initial errors/disputes/execution or protocol failures plus ceil(20 percent of initial content passes), sampled with the preserved seed.",
        "assignments": rows, "evidence_level": EVIDENCE_LEVEL, "model_calls": 0}
    write_json(out_path, result, immutable=True)
    return result


def chain_submission_template(grading_dir, candidate_id):
    """Return a chain-only form without exposing the sealed primary label."""
    root, mapping, _ = _context(grading_dir)
    item = mapping.get(candidate_id)
    if item is None or not item["chain_secondary_required"]:
        raise ValueError("A chain secondary requires one applicable planned candidate")
    packet = grading.inside(root, item["packet"])
    template = _read(packet / "grade.template.json")
    fields = ("candidate_id", "candidate_sha256", "reference_sha256", "source_sha256",
              "source_bundle_sha256", "output_freeze_sha256")
    def pending(field, value):
        return {field: value, "status": "pending", "reason": "", "source_evidence": [], "candidate_evidence": []}
    return {"schema_version": CHAIN_SCHEMA, "evidence_level": EVIDENCE_LEVEL,
        **{k: template[k] for k in fields}, "scoring_role": "secondary", "assessment_kind": "chain_secondary",
        "reviewer_id": "", "agent_id": "", "human_verified": False,
        "actual_human_review_work_seconds": None, "reference_correction_proposals": [],
        "chain_assessment": {"completeness": [pending("layer", k) for k in CHAIN_LAYERS],
                             "consistency": [pending("link", k) for k in CHAIN_LINKS]}}


def _validate_chain_only(root, path, mapping):
    path = Path(path).resolve()
    wrapper = _read(path)
    candidate = wrapper.get("candidate_id")
    if (wrapper.get("schema_version") != CHAIN_SCHEMA or candidate not in mapping
            or not mapping[candidate]["chain_secondary_required"] or wrapper.get("evidence_level") != EVIDENCE_LEVEL
            or wrapper.get("scoring_role") != "secondary" or wrapper.get("assessment_kind") != "chain_secondary"
            or wrapper.get("human_verified") is not False or wrapper.get("actual_human_review_work_seconds") is not None
            or not wrapper.get("agent_id") or not wrapper.get("reviewer_id")):
        raise ValueError("Chain-only records require bound nonhuman exploratory provenance")
    packet = grading.inside(root, mapping[candidate]["packet"])
    template = _read(packet / "grade.template.json")
    for field in ("candidate_sha256", "reference_sha256", "source_sha256", "source_bundle_sha256", "output_freeze_sha256"):
        if wrapper.get(field) != template.get(field):
            raise ValueError("The chain-only record binds a different packet or output cohort")
    if any(field in wrapper for field in ("judgment", "check_results", "matched_exposure_ids", "claim_units",
            "receiving_point_coverage", "reduction_assessments", "error_records", "findings")):
        raise ValueError("A chain-only record cannot supply replacement common primary judgments")
    chain = wrapper.get("chain_assessment")
    if not isinstance(chain, dict):
        raise ValueError("A chain-only submission requires its separate chain assessment")
    for group, field, expected in (("completeness", "layer", CHAIN_LAYERS), ("consistency", "link", CHAIN_LINKS)):
        records = chain.get(group)
        if (not isinstance(records, list) or any(not isinstance(r, dict) for r in records)
                or len(records) != len(expected) or {r.get(field) for r in records} != set(expected)):
            raise ValueError("Assess every chain layer and link exactly once")
        for record in records:
            if (record.get("status") not in {"pass", "fail", "disputed"}
                    or not isinstance(record.get("reason"), str) or not record["reason"].strip()):
                raise ValueError("A chain dimension requires a completed status and source-based reason")
            _evidence(record.get("source_evidence"), source=True)
            _evidence(record.get("candidate_evidence"), required=record["status"] == "pass")
    candidate_text = (packet / "candidate.txt").read_text(encoding="utf-8")
    validate_grade_evidence({"claim_units": [], "receiving_point_coverage": [], "reduction_assessments": [],
        "error_records": [], "chain_assessment": chain}, source_root=packet / "source", candidate_text=candidate_text)
    proposals = wrapper.get("reference_correction_proposals", [])
    if not isinstance(proposals, list):
        raise ValueError("Chain source-reference correction proposals must be a list")
    for proposal in proposals:
        if not isinstance(proposal, dict) or not proposal.get("reason"):
            raise ValueError("A chain source-reference correction requires a reason and source evidence")
        _evidence(proposal.get("source_evidence"), source=True)
        proposal = {**proposal, "candidate_evidence": proposal.get("candidate_evidence", [])}
        _evidence(proposal["candidate_evidence"], required=False)
        validate_grade_evidence({"claim_units": [], "receiving_point_coverage": [],
            "reduction_assessments": [], "error_records": [proposal], "chain_assessment": None},
            source_root=packet / "source", candidate_text=candidate_text)
    return {"path": str(path), "sha256": sha256(path), "validated_grade": wrapper,
            "human_verified": False, "evidence_level": EVIDENCE_LEVEL}


def validate_chain_submission(grading_dir, submission_path):
    """Validate one fresh chain-only result without loading any primary label.

    This is the leaf-grader entry point. The return value contains only the
    submitted chain wrapper and its provenance, never common primary labels.
    """
    root, mapping, _ = _context(grading_dir)
    record = _validate_chain_only(root, submission_path, mapping)
    return {"validated_chain_submission": record["validated_grade"], "path": record["path"],
            "sha256": record["sha256"], "human_verified": False, "evidence_level": EVIDENCE_LEVEL}


def _chain_record(root, path, primary, mapping):
    if _read(path).get("schema_version") != CHAIN_SCHEMA:
        return _grade_record(root, path, role="secondary", chain=True)
    record = _validate_chain_only(root, path, mapping)
    wrapper = record["validated_grade"]
    original = primary["records"].get(wrapper["candidate_id"])
    if original is None:
        raise ValueError("Seal the common primary before coordinating a chain secondary")
    # This temporary projection retains the sealed primary unchanged. It is
    # never sent to the fresh chain grader or used to overwrite primary labels.
    combined = deepcopy(original["validated_grade"])
    combined["chain_assessment"] = wrapper["chain_assessment"]
    item = mapping[wrapper["candidate_id"]]
    packet = grading.inside(root, item["packet"])
    validate_semantic_grade(combined, _read(packet / "reference.json"), method=item["method"])
    return record


def _secondary(root, primary_path, primary, mapping, assignments_path, paths, *, chain):
    if assignments_path is None:
        if paths:
            raise ValueError("Secondary results require sealed assignments")
        return {}
    assignments = _read(assignments_path)
    if (assignments.get("schema_version") != SCHEMA or assignments.get("kind") != "secondary_assignments"
            or assignments.get("primary_seal_sha256") != sha256(primary_path)
            or any(assignments.get(k) != v for k, v in _binding(root).items())
            or assignments.get("seed") != SEED or set(primary["records"]) != set(mapping)):
        raise ValueError("Secondary assignments require the complete preceding primary seal")
    expected = {("primary_recheck", c) for c in _selection(primary)}
    expected |= {("chain_secondary", c) for c, r in mapping.items() if r["chain_secondary_required"]}
    indexed = {(r["assignment_kind"], r["candidate_id"]): r for r in assignments["assignments"]}
    if len(indexed) != len(assignments["assignments"]) or set(indexed) != expected:
        raise ValueError("The mandatory seeded recheck or chain assignment cohort changed")
    for (_, candidate), assignment in indexed.items():
        previous = primary["records"][candidate]["validated_grade"]["agent_id"]
        if (assignment.get("packet") != mapping[candidate]["packet"]
                or assignment.get("excluded_agent_ids") != [previous]
                or assignment.get("assigned_agent_id") == previous):
            raise ValueError("An independent assignment cannot reuse the primary agent")
    records, kind = {}, "chain_secondary" if chain else "primary_recheck"
    for path in paths:
        item = _chain_record(root, path, primary, mapping) if chain else _grade_record(root, path, role="secondary")
        grade = item["validated_grade"]
        candidate = grade["candidate_id"]
        assignment = indexed.get((kind, candidate))
        if assignment is None or candidate in records:
            raise ValueError("Duplicate or unassigned independent assistant result")
        if (grade["agent_id"] in assignment["excluded_agent_ids"]
                or (assignment.get("assigned_agent_id") and grade["agent_id"] != assignment["assigned_agent_id"])):
            raise ValueError("A secondary result does not identify its independent assigned agent")
        if chain and grade.get("schema_version") != CHAIN_SCHEMA:
            packet = grading.inside(root, mapping[candidate]["packet"])
            validate_semantic_grade(grade, _read(packet / "reference.json"), method=mapping[candidate]["method"])
        records[candidate] = item
    return records


def _cases(root, mapping, source_metadata):
    private = _read(root / "private-map.json")
    source_run = Path(private["source_run"])
    authoritative_path = source_run / "selection.json"
    authoritative = _read(authoritative_path)
    authoritative_hash = sha256(authoritative_path)
    if _read(source_run / "freeze.json").get("files", {}).get("selection.json") != authoritative_hash:
        raise ValueError("Source clusters must come from the frozen authoritative selection")
    authoritative_rows = authoritative.get("selected", [])
    authoritative_cases = {r["case_id"]: r for r in authoritative_rows}
    if source_metadata is None:
        source_metadata = authoritative_path
    if isinstance(source_metadata, (str, Path)):
        path = Path(source_metadata).resolve()
        data = _read(path)
        metadata_hash = sha256(path)
    else:
        data, metadata_hash = source_metadata, canonical_hash(source_metadata)
    if isinstance(data, dict) and "selected" in data:
        rows = data["selected"]
    elif isinstance(data, dict):
        rows = [dict(value, case_id=key) if isinstance(value, dict)
                else {"case_id": key, "source_cluster": value} for key, value in data.items()]
    else:
        rows = data
    cases = {r["case_id"]: r for r in rows}
    if (len(rows) != 24 or len(cases) != 24 or set(cases) != {r["case_id"] for r in mapping.values()}
            or any(not isinstance(r.get("source_cluster"), str) or not r["source_cluster"].strip() for r in cases.values())
            or len({r["source_cluster"] for r in cases.values()}) != 22):
        raise ValueError("Supply the fixed 24 cases and their 22 source clusters")
    if (len(authoritative_rows) != 24 or set(authoritative_cases) != set(cases)
            or any(not isinstance(r.get("source_sha256"), str) or not r["source_sha256"].strip()
                   for r in authoritative_cases.values())):
        raise ValueError("The authoritative selected cases require their frozen source identities")
    for case_id, item in cases.items():
        original = authoritative_cases[case_id]
        if any(item.get(k) != original.get(k) for k in ("source_cluster", "source_sha256")):
            raise ValueError("Supplied source metadata differs from the frozen authoritative source clusters or identities")
    for item in mapping.values():
        case = cases[item["case_id"]]
        reference = _read(grading.inside(root, item["packet"]) / "reference.json")
        if (item.get("source_cluster", case["source_cluster"]) != case["source_cluster"]
                or (case.get("source_sha256") is not None and case["source_sha256"] != reference.get("source_sha256"))):
            raise ValueError("Source-cluster metadata differs from the sealed candidate source")
    return cases, {"supplied": metadata_hash, "authoritative": authoritative_hash}


def _bounds(rows):
    counts = Counter(r["judgment"] for r in rows)
    passed = counts["satisfies_reference"]
    failed = counts["substantive_error"] + counts["workflow_failure"]
    total = len(rows)
    unknown = total - passed - failed
    return {"planned": total, "known_pass": passed, "known_fail": failed, "unknown": unknown,
            "pass_fraction": passed / total if total and not unknown else None,
            "pass_fraction_bounds": [passed / total, (passed + unknown) / total] if total else None,
            "judgment_counts": dict(sorted(counts.items()))}


def _mean(values):
    return sum(values) / len(values) if values and all(v is not None for v in values) else None


def _adjust(comparisons, field="holm_adjusted_p"):
    if len(comparisons) != 2 or not all("two_sided_cluster_sign_flip_p" in c for c in comparisons):
        return
    for entry, adjusted in zip(comparisons, holm_adjust([c["two_sided_cluster_sign_flip_p"] for c in comparisons])):
        interval = entry["simultaneous_97_5_percent_interval"]
        entry[field] = adjusted
        entry["practical_advantage_method"] = (
            entry["methods"][0] if entry["difference"] >= .10 and interval[0] > 0 and adjusted < .05
            else entry["methods"][1] if entry["difference"] <= -.10 and interval[1] < 0 and adjusted < .05 else None)


def _comparisons(rows, cases, ready, bootstrap_samples):
    case_rows, groups = [], {}
    for case in sorted(cases):
        for method in METHODS:
            for kind in ("main", "review"):
                selected = [r for r in rows if (r["case_id"], r["method"], r["kind"]) == (case, method, kind)]
                if selected:
                    case_rows.append({"case_id": case, "source_cluster": cases[case]["source_cluster"],
                        "method": method, "kind": kind, **_bounds(selected)})
    for method, kind in sorted({(r["method"], r["kind"]) for r in rows}):
        selected = [r for r in rows if (r["method"], r["kind"]) == (method, kind)]
        means = [r["pass_fraction"] for r in case_rows if (r["method"], r["kind"]) == (method, kind)]
        groups[method + "/" + kind] = {**_bounds(selected), "planned_cases": 24,
            "case_averaged_pass_fraction": _mean(means)}
    comparisons = []
    if ready:
        means = {(r["case_id"], r["method"], r["kind"]): r["pass_fraction"] for r in case_rows}
        for other in ("audit", "chain"):
            stats = paired_cluster_statistics([{"source_cluster": cases[c]["source_cluster"],
                "difference": means[c, "skillflow", "main"] - means[c, other, "main"]} for c in sorted(cases)],
                bootstrap_samples=bootstrap_samples)
            comparisons.append({"methods": ["skillflow", other], **stats})
        _adjust(comparisons)
    return case_rows, groups, comparisons


def _review_comparisons(rows, cases, bootstrap_samples):
    index = {(r["case_id"], r["method"], r["kind"], r["repeat"]): r for r in rows}
    output, family = [], []
    for method in ("audit", "chain"):
        pairs = []
        for case, metadata in sorted(cases.items()):
            original, review, native = (index[case, m, k, 1] for m, k in
                ((method, "main"), (method, "review"), ("skillflow", "main")))
            pair = {"case_id": case, "source_cluster": metadata["source_cluster"],
                "original_r1": original["judgment"], "reviewed_r1": review["judgment"],
                "skillflow_r1": native["judgment"],
                "adjudicated": all(r["assistant_adjudication_complete"] for r in (original, review, native))}
            if pair["adjudicated"]:
                n, a, b = (int(r["judgment"] == "satisfies_reference") for r in (native, original, review))
                pair.update(review_uplift=b-a, original_gap=n-a, reviewed_gap=n-b, paired_gap_change=(n-b)-(n-a))
            pairs.append(pair)
        complete = all(p["adjudicated"] for p in pairs)
        entry = {"method": method, "planned_pairs": 24, "complete": complete, "pairs": pairs,
            "comparison_basis": "Original R1, its fixed reviewed R1, and SkillFlow R1; no replacements or three-repeat means.",
            "equivalence_established": False}
        if complete:
            for key in ("review_uplift", "original_gap", "reviewed_gap", "paired_gap_change"):
                entry[key] = paired_cluster_statistics([{"source_cluster": p["source_cluster"], "difference": p[key]} for p in pairs],
                    bootstrap_samples=bootstrap_samples)
            statistic = entry["reviewed_gap"]
            statistic["methods"] = ["skillflow_r1", method + "+fixed_review_r1"]
            family.append(statistic)
        output.append(entry)
    _adjust(family, "secondary_family_holm_adjusted_p")
    return output


def _assistant_unit_metrics(grade, reference, judgment):
    metrics = _unit_metrics(grade, reference, method=None, judgment=judgment)
    material = bool(grade and any(r.get("severity") in {"substantive", "disputed"}
        or r.get("functionality_impact") in {"breaks_required_behavior", "disputed"}
        for r in grade.get("findings", [])))
    if material:
        for field in ("substantive_errors", "functionality_errors", "error_categories"):
            metrics[field] = None
    metrics["unnormalized_findings_limitation"] = (
        "Material prose findings may duplicate normalized error records or describe additional errors. Affected error counts remain unknown; prose findings are not counted as extra errors."
        if material else None)
    return metrics


def _semantic(rows, references):
    observations, case_means = [], []
    for row in rows:
        metrics = _assistant_unit_metrics(row["adjudicated_grade"], references[row["case_id"]], row["judgment"])
        # The primary grade is intentionally chain-free. Chain data is derived
        # only from its separately assigned secondary submission.
        chain = row.get("chain_assessment")
        for group, name in (("completeness", "chain_completeness"), ("consistency", "chain_consistency")):
            metrics[name] = (sum(r["status"] == "pass" for r in chain[group]) / len(chain[group])
                if chain and not any(r["status"] == "disputed" for r in chain[group]) else None)
        observations.append({**{k: row[k] for k in ("candidate_id", "case_id", "source_cluster", "method", "kind", "repeat")}, **metrics})
    numeric = ("tp", "fn", "fp", "precision", "recall", "receiving_point_coverage", "reduction_coverage",
               "substantive_errors", "functionality_errors", "chain_completeness", "chain_consistency")
    grouped = defaultdict(list)
    for row in observations:
        grouped[row["case_id"], row["method"], row["kind"]].append(row)
    for (case, method, kind), values in sorted(grouped.items()):
        case_means.append({"case_id": case, "method": method, "kind": kind,
            "source_cluster": values[0]["source_cluster"], "planned_repetitions": len(values),
            "reference_positive_units": values[0]["reference_positive_units"],
            "reference_reducible_units": values[0]["reference_reducible_units"],
            **{k: _mean([r[k] for r in values]) for k in numeric}})
    groups = {}
    for method, kind in sorted({(r["method"], r["kind"]) for r in rows}):
        selected = [r for r in case_means if (r["method"], r["kind"]) == (method, kind)]
        groups[method + "/" + kind] = {"planned_cases": 24, "case_averaged": {
            k: _mean([r[k] for r in selected if (k != "recall" or r["reference_positive_units"] > 0)
                     and (k != "reduction_coverage" or r["reference_reducible_units"] > 0)]) for k in numeric}}
    return {"rows": observations, "case_means": case_means, "groups": groups,
        "source_defined_strata": stratified_check_metrics(rows, references),
        "interpretation": "Descriptive assistant measurements against assistant references. Undefined precision and unresolved assessments stay unknown; chain completeness never changes primary adequacy."}


def _stability(rows):
    output = []
    for case in sorted({r["case_id"] for r in rows}):
        for method in METHODS:
            selected = sorted((r for r in rows if r["case_id"] == case and r["method"] == method and r["kind"] == "main"), key=lambda r: r["repeat"])
            grades = [r["adjudicated_grade"] for r in selected]
            resolved = all(g is not None for g in grades)
            matches = [set(g["matched_exposure_ids"]) for g in grades] if resolved else []
            unsupported = [{canonical_hash({f: c[f].strip() for f in EXPOSURE_FIELDS}) for c in g["claim_units"] if c["assessment"] == "unsupported"} for g in grades] if resolved else []
            def jaccard(sets):
                return _mean([len(a & b) / len(a | b) if a | b else 1.0 for a, b in combinations(sets, 2)]) if len(sets) == 3 else None
            contradictions = []
            if resolved:
                for field, identity, status in (("check_results", "check_id", "status"),
                        ("receiving_point_coverage", "receiving_point_id", "status"),
                        ("reduction_assessments", "reference_exposure_id", "status")):
                    statuses = defaultdict(set)
                    for grade in grades:
                        for record in grade[field]:
                            statuses[record[identity]].add(record[status])
                    contradictions.extend({"dimension": field, "identity": key, "statuses": sorted(values)}
                        for key, values in sorted(statuses.items()) if len(values) > 1)
                statuses = defaultdict(set)
                for grade in grades:
                    for claim in grade["claim_units"]:
                        statuses[canonical_hash({f: claim[f].strip() for f in EXPOSURE_FIELDS})].add(claim["assessment"])
                contradictions.extend({"dimension": "claim_assessment", "identity": key, "statuses": sorted(values)}
                    for key, values in sorted(statuses.items()) if len(values) > 1)
            known = all(r["assistant_adjudication_complete"] for r in selected)
            output.append({"case_id": case, "method": method, "planned_repeats": 3,
                "all_three_satisfy": all(r["judgment"] == "satisfies_reference" for r in selected) if known else None,
                "matched_reference_unit_jaccard": jaccard(matches), "unsupported_claim_jaccard": jaccard(unsupported),
                "grade_classification_contradictions": contradictions if resolved else None,
                "contradiction_present": bool(contradictions) if resolved else None,
                "note": "Contradictions mean differing assistant classifications across repeats, not independently proven textual self-contradictions. Empty-set Jaccard is 1 and does not establish correctness."})
    groups = {}
    for method in METHODS:
        selected = [r for r in output if r["method"] == method]
        known_pass = sum(r["all_three_satisfy"] is True for r in selected)
        unknown = sum(r["all_three_satisfy"] is None for r in selected)
        groups[method] = {"planned_cases": 24, "all_three_satisfy_rate": _mean([r["all_three_satisfy"] for r in selected]),
            "all_three_satisfy_bounds": [known_pass / 24, (known_pass + unknown) / 24],
            "matched_reference_unit_jaccard": _mean([r["matched_reference_unit_jaccard"] for r in selected]),
            "unsupported_claim_jaccard": _mean([r["unsupported_claim_jaccard"] for r in selected]),
            "contradiction_rate": _mean([r["contradiction_present"] for r in selected])}
    return {"rows": output, "groups": groups}


def _resource_comparisons(rows, cases, costs, bootstrap_samples, output_freeze_sha256):
    costs = costs or {}
    if costs and costs.get("output_freeze_sha256") != output_freeze_sha256:
        raise ValueError("External costs must bind the same closed output cohort")
    work = costs.get("workflows", [])
    enhanced = costs.get("enhanced_original_plus_review_cost", [])
    if len({w["workflow_id"] for w in work}) != len(work) or len({w["workflow_id"] for w in enhanced}) != len(enhanced):
        raise ValueError("Duplicate workflow cost identities cannot enter resource ratios")
    by_id, reviewed_costs = ({w["workflow_id"]: w for w in values} for values in (work, enhanced))
    if not set(by_id).issubset({r["workflow_id"] for r in rows}):
        raise ValueError("External costs contain an unplanned workflow")
    if not set(reviewed_costs).issubset({r["workflow_id"] for r in rows if r["kind"] == "review"}):
        raise ValueError("Enhanced costs require a planned fixed-review identity")
    row_index = {r["workflow_id"]: r for r in rows}
    for item in work + enhanced:
        planned = row_index[item["workflow_id"]]
        if any(item.get(k, planned[k]) != planned[k] for k in ("case_id", "method", "kind", "repeat")):
            raise ValueError("External cost metadata differs from its planned workflow")
        if "original_workflow_id" in item:
            original = next((r["workflow_id"] for r in rows if (r["case_id"], r["method"], r["kind"], r["repeat"]) ==
                (planned["case_id"], planned["method"], "main", 1)), None)
            if item["original_workflow_id"] != original:
                raise ValueError("Enhanced costs bind the wrong original R1 workflow")
    def number(value):
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
            raise ValueError("Resource costs must be finite nonnegative observations or null")
        return value
    def cost(observed, resource, reviewed):
        values = []
        for row in observed:
            item = (reviewed_costs if reviewed else by_id).get(row["workflow_id"], {})
            if resource == "reported_total_tokens":
                usage = item.get("usage_original_plus_review" if reviewed else "usage", {})
                value = usage.get("totals", {}).get("total_tokens", item.get("reported_total_tokens"))
            else:
                value = item.get("additive_workflow_seconds" if reviewed else "workflow_elapsed_seconds")
            values.append(number(value))
        return _mean(values)
    comparisons = []
    global_primary_resolved = all(r["assistant_adjudication_complete"] for r in rows)
    for reviewed in (False, True):
        for other in ("audit", "chain"):
            for resource in ("reported_total_tokens", "workflow_elapsed_seconds"):
                pairs = []
                for case in sorted(cases):
                    def observed(method, kind):
                        return [r for r in rows if (r["case_id"], r["method"], r["kind"]) == (case, method, kind)
                                and (not reviewed or r["repeat"] == 1)]
                    native, direct = observed("skillflow", "main"), observed(other, "review" if reviewed else "main")
                    cost_records = [by_id.get(r["workflow_id"], {}) for r in native]
                    cost_records += [(reviewed_costs if reviewed else by_id).get(r["workflow_id"], {}) for r in direct]
                    pairs.append({"case_id": case, "source_cluster": cases[case]["source_cluster"],
                        "adjudicated": global_primary_resolved and all(r["assistant_adjudication_complete"] for r in native + direct),
                        "censored": any(c.get("censored") or c.get("right_censored") for c in cost_records),
                        "claimant_quality": _mean([int(r["judgment"] == "satisfies_reference") if r["assistant_adjudication_complete"] else None for r in native]),
                        "comparator_quality": _mean([int(r["judgment"] == "satisfies_reference") if r["assistant_adjudication_complete"] else None for r in direct]),
                        "claimant_cost": cost(native, resource, False), "comparator_cost": cost(direct, resource, reviewed)})
                arms = ["skillflow_r1" if reviewed else "skillflow", other + ("+fixed_review_r1" if reviewed else "")]
                for reverse in (False, True):
                    directed = [{**p, **({"claimant_quality": p["comparator_quality"], "comparator_quality": p["claimant_quality"],
                        "claimant_cost": p["comparator_cost"], "comparator_cost": p["claimant_cost"]} if reverse else {})} for p in pairs]
                    decision = efficiency_decision(directed, bootstrap_samples=bootstrap_samples)
                    if not global_primary_resolved:
                        decision["status"] = "blocked_global_unresolved_primary_quality"
                    complete_costs = all(p["claimant_cost"] is not None and p["comparator_cost"] is not None for p in directed)
                    denominator = sum(p["comparator_cost"] for p in directed) if complete_costs else None
                    comparisons.append({"methods": arms[::-1] if reverse else arms, "resource": resource,
                        "global_primary_resolved": global_primary_resolved,
                        "descriptive_resource_ratio": sum(p["claimant_cost"] for p in directed) / denominator
                            if denominator else None,
                        "case_cost_pairs": [{k: p[k] for k in ("case_id", "source_cluster", "claimant_cost", "comparator_cost", "censored")} for p in directed],
                        "adjudication_basis": EVIDENCE_LEVEL, **decision})
    for other in ("audit", "chain"):
        for arms in (["skillflow", other], [other, "skillflow"]):
            comparisons.append({"methods": arms, "resource": "all_planned_timed_review_active_seconds",
                **efficiency_decision([], bootstrap_samples=bootstrap_samples), "status": "actual_human_work_unobserved",
                "actual_human_review_work_seconds": None})
    elapsed = [number(by_id.get(r["workflow_id"], {}).get("workflow_elapsed_seconds")) for r in rows]
    usage = costs.get("target_usage", {})
    return {"comparisons": comparisons, "directional_claim_family": 20,
        "source_cost_ledger_sha256": canonical_hash(costs) if costs else None,
        "target_reported_total_tokens": usage.get("totals", {}).get("total_tokens"),
        "target_usage": {k: v for k, v in usage.items() if k not in {"by_response_id", "response_ledger"}},
        "sum_of_workflow_elapsed_seconds": sum(elapsed) if all(v is not None for v in elapsed) else None,
        "known_workflow_elapsed_seconds_subtotal": sum(v for v in elapsed if v is not None) if any(v is not None for v in elapsed) else None,
        "reported_workflows": len(work), "unreported_workflows": 264 - len(work),
        "actual_human_review_work_seconds": None, "currency_cost": None,
        "interpretation": "Externally supplied observed costs only. Repeat costs are averaged within case before equal-case sums and source-cluster resampling. Reviewed costs must include original and review with response identities deduplicated by the external cost ledger. Assistant adjudication is not human review time; four human-time directions stay unknown."}


def aggregate_results(grading_dir, primary_seal, secondary_assignments=None, *,
                      secondary_submission_paths=(), chain_submission_paths=(),
                      source_metadata=None, costs=None, bootstrap_samples=10000):
    """Build JSON-ready report inputs without writing or altering any label."""
    if type(bootstrap_samples) is not int or bootstrap_samples < 1:
        raise ValueError("Bootstrap sample count must be a positive integer")
    root, mapping, packet_freeze = _context(grading_dir)
    primary = _load_primary(root, primary_seal)
    if not set(primary["records"]).issubset(mapping):
        raise ValueError("A primary seal contains an unplanned candidate")
    rechecks = _secondary(root, primary_seal, primary, mapping, secondary_assignments,
                          secondary_submission_paths, chain=False)
    chains = _secondary(root, primary_seal, primary, mapping, secondary_assignments,
                        chain_submission_paths, chain=True)
    cases, metadata_hash = _cases(root, mapping, source_metadata)
    required = set(_selection(primary)) if len(primary["records"]) == 264 else set()
    rows, errors, disputes = [], [], []
    references = {}
    for candidate, item in sorted(mapping.items()):
        original = primary["records"].get(candidate)
        recheck = rechecks.get(candidate)
        grade = original["validated_grade"] if original else None
        secondary = recheck["validated_grade"] if recheck else None
        chain_grade = chains[candidate]["validated_grade"] if candidate in chains else None
        issues, detail, content = [], None, "unassessed"
        if grade is not None:
            issues.extend(_disputes(grade))
            if len(primary["records"]) != 264:
                issues.append("primary_cohort_seal_incomplete")
            if candidate in required and secondary is None:
                issues.append("mandatory_primary_recheck_missing")
            if secondary is not None:
                issues.extend("secondary_" + v for v in _disputes(secondary))
                if sorted((r["check_id"], r["status"]) for r in grade["check_results"]) != sorted((r["check_id"], r["status"]) for r in secondary["check_results"]):
                    issues.append("mandatory_check_disagreement")
                if grade["judgment"] != secondary["judgment"]:
                    issues.append("coarse_judgment_disagreement")
            content = paired_judgment(grade, secondary)
            reconciled = _primary_detail(grade, secondary)
            issues.extend(reconciled["metric_disputes"])
            if chain_grade and chain_grade.get("reference_correction_proposals"):
                issues.append("chain_source_reference_correction_proposed")
            detail = reconciled["adjudicated_grade"] if not issues else None
        else:
            issues.append("planned_primary_missing")
        judgment = ("pending_primary" if grade is None else "pending_primary_recheck"
            if "mandatory_primary_recheck_missing" in issues else "indeterminate" if issues else
            original["workflow_primary_judgment"] if content != "indeterminate" else "indeterminate")
        chain = chain_grade.get("chain_assessment") if chain_grade else None
        chain_issues = (["chain_secondary_missing"] if item["chain_secondary_required"] and chain is None else [])
        if chain_grade and chain_grade.get("reference_correction_proposals"):
            chain_issues.append("chain_source_reference_correction_proposed")
        if chain and any(r["status"] == "disputed" for key in ("completeness", "consistency") for r in chain[key]):
            chain_issues.append("chain_metric_dispute")
        row = {**item, "source_cluster": cases[item["case_id"]]["source_cluster"],
            "content_judgment": content, "judgment": judgment,
            "protocol_eligible": original["protocol_eligible"] if original else None,
            "execution_status": original["execution_status"] if original else None,
            "mandatory_primary_recheck": candidate in required, "primary_disputes": sorted(set(issues)),
            "metric_disputes": sorted(set(issues)), "assistant_adjudication_complete": judgment in KNOWN,
            "adjudicated_grade": detail, "chain_assessment": chain if not chain_issues else None,
            "chain_disputes": chain_issues, "chain_assessment_complete": bool(chain) and not chain_issues,
            "assistant_agents": {role: record["agent_id"] for role, record in
                (("primary", grade), ("primary_recheck", secondary), ("chain_secondary", chain_grade)) if record}}
        rows.append(row)
        references.setdefault(item["case_id"], _read(grading.inside(root, item["packet"]) / "reference.json"))
        if issues or chain_issues:
            disputes.append({"candidate_id": candidate, "workflow_id": item["workflow_id"],
                "primary": row["primary_disputes"], "chain": chain_issues,
                "reference_correction_proposals": {role: record.get("reference_correction_proposals", [])
                    for role, record in (("primary", grade), ("primary_recheck", secondary), ("chain_secondary", chain_grade)) if record}})
        for role, record in (("primary", grade), ("primary_recheck", secondary), ("chain_secondary", chain_grade)):
            if record:
                for group in ("error_records", "findings"):
                    errors.extend({"candidate_id": candidate, "workflow_id": item["workflow_id"],
                        "role": role, "record_kind": group, "record": error} for error in record.get(group, []))
                for group, field, bad in (("check_results", "status", {"fail"}),
                        ("claim_units", "assessment", {"unsupported"}),
                        ("receiving_point_coverage", "status", {"missed"}),
                        ("reduction_assessments", "status", {"missing", "harmful"})):
                    errors.extend({"candidate_id": candidate, "workflow_id": item["workflow_id"],
                        "role": role, "record_kind": group, "record": error}
                        for error in record.get(group, []) if error.get(field) in bad)
    ready = all(r["assistant_adjudication_complete"] for r in rows)
    case_rows, groups, comparisons = _comparisons(rows, cases, ready, bootstrap_samples)
    main, reviews = ([r for r in rows if r["kind"] == k] for k in ("main", "review"))
    return {"schema_version": SCHEMA, "evidence_level": EVIDENCE_LEVEL, "model_calls": 0,
        "grading_workspace": str(root),
        "primary_seal_path": str(Path(primary_seal).resolve()),
        "secondary_assignments_path": str(Path(secondary_assignments).resolve()) if secondary_assignments else None,
        **_binding(root), "primary_seal_sha256": sha256(primary_seal),
        "secondary_assignments_sha256": sha256(secondary_assignments) if secondary_assignments else None,
        "source_metadata_sha256": metadata_hash["supplied"],
        "authoritative_source_metadata_sha256": metadata_hash["authoritative"], "planned_results": 264, "planned_main": 216,
        "planned_reviews": 48, "planned_cases": 24, "source_clusters": 22,
        "all_planned_in_denominator": True, "bounds": _bounds(rows), "main_bounds": _bounds(main),
        "review_bounds": _bounds(reviews), "groups": groups, "case_results": case_rows, "rows": rows,
        "primary_seal_complete": len(primary["records"]) == 264,
        "mandatory_primary_rechecks": sorted(required), "missing_mandatory_primary_rechecks": sorted(required-set(rechecks)),
        "inferential_status": "assistant_exploratory_ready" if ready else "blocked_pending_or_disputed_primary",
        "primary_comparisons": comparisons,
        "fixed_review_comparisons": _review_comparisons(rows, cases, bootstrap_samples),
        "chain_status": {"planned": 168, "complete": sum(r["chain_assessment_complete"] for r in rows),
            "inference_ready": all(r["chain_assessment_complete"] for r in rows if r["chain_secondary_required"])
                and not any("source_reference" in issue for r in rows for issue in r["primary_disputes"])},
        "semantic_metrics": _semantic(rows, references), "stability": _stability(rows),
        "individual_errors": errors, "individual_disputes": disputes,
        "resources": _resource_comparisons(rows, cases, costs, bootstrap_samples, packet_freeze["source_output_freeze_sha256"]),
        "human_reference_confirmation": "pending", "actual_human_scoring": "pending",
        "actual_human_review_work_seconds": None,
        "limitations": ["Selected-cohort exploratory assistant labels and references are not independent human gold or population error rates.",
            "Any missing planned primary or mandatory primary recheck, source dispute, coarse disagreement or detailed primary dispute blocks main inference.",
            "Missing or disputed chain assessments block affected chain metrics independently of common primary inference.",
            "Source-reference corrections require a new independent all-264 grading epoch without target regeneration.",
            "Agent identity is recorded and compared; the software cannot independently verify context isolation or independence."]}


def write_reports(report, out_dir):
    """Write new JSON/CSV report inputs and seal them after cohort verification."""
    out = Path(out_dir).resolve()
    if report.get("schema_version") != SCHEMA or report.get("planned_results") != 264:
        raise ValueError("Only a complete planned-cohort report can be written")
    root, _, _ = _context(report["grading_workspace"])
    if any(report.get(k) != v for k, v in _binding(root).items()):
        raise ValueError("The report binds a different closed assistant workspace")
    _output_location(root, out)
    if (sha256(report["primary_seal_path"]) != report["primary_seal_sha256"]
            or (report.get("secondary_assignments_path") and sha256(report["secondary_assignments_path"]) != report["secondary_assignments_sha256"])):
        raise ValueError("A grading seal changed after report computation")
    if out.exists():
        raise ValueError("Use a fresh report directory; earlier reports remain preserved")
    out.mkdir(parents=True)
    write_json(out / "results.json", report, immutable=True)
    tables = {"outcomes": report["rows"], "case-results": report["case_results"],
              "errors": report["individual_errors"], "disputes": report["individual_disputes"],
              "stability": report["stability"]["rows"], "resources": report["resources"]["comparisons"]}
    for name, rows in tables.items():
        fields = sorted({key for row in rows for key in row})
        with (out / (name + ".csv")).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (dict, list))
                    else "null" if v is None else v for k, v in row.items()})
    seal = {"schema_version": SCHEMA, "kind": "report_seal", "created_at": utc_now(),
        "evidence_level": EVIDENCE_LEVEL, "primary_seal_sha256": report["primary_seal_sha256"],
        "packet_freeze_sha256": report["packet_freeze_sha256"], "model_calls": 0,
        "files": {p.name: sha256(p) for p in sorted(out.iterdir()) if p.is_file()}}
    write_json(out / "report-freeze.json", seal, immutable=True)
    return seal


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grading-dir", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    seal = sub.add_parser("seal-primary")
    seal.add_argument("--submissions", nargs="+", required=True)
    seal.add_argument("--out", required=True)
    select = sub.add_parser("select-secondary")
    select.add_argument("--primary-seal", required=True)
    select.add_argument("--out", required=True)
    aggregate = sub.add_parser("aggregate")
    aggregate.add_argument("--primary-seal", required=True)
    aggregate.add_argument("--secondary-assignments")
    aggregate.add_argument("--secondary-submissions", nargs="*", default=[])
    aggregate.add_argument("--chain-submissions", nargs="*", default=[])
    aggregate.add_argument("--source-metadata")
    aggregate.add_argument("--costs")
    aggregate.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.command == "seal-primary":
        result = seal_primary_submissions(args.grading_dir, args.submissions, args.out)
        result = {k: v for k, v in result.items() if k != "records"}
    elif args.command == "select-secondary":
        result = prepare_secondary_assignments(args.grading_dir, args.primary_seal, args.out)
        result = {k: v for k, v in result.items() if k != "assignments"}
    else:
        report = aggregate_results(args.grading_dir, args.primary_seal, args.secondary_assignments,
            secondary_submission_paths=args.secondary_submissions, chain_submission_paths=args.chain_submissions,
            source_metadata=args.source_metadata, costs=_read(args.costs) if args.costs else None)
        result = write_reports(report, args.out)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
