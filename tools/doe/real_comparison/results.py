"""Common outcome aggregation, retaining all planned workflows and unknowns."""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path

from .assessment import (validate_grade, paired_judgment, second_review_sample,
                         paired_cluster_statistics, holm_adjust, verify_human_reference_freeze)
from .protocol import SCHEMA, SEED, canonical_hash, sha256, write_json


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fixed_review_comparisons(rows, cases):
    """Secondary paired R1 comparisons; never mix three repeats with one review."""
    output = []
    pending = {"not_generated", "unassessed", "pending_secondary_human", "indeterminate"}
    for method in ("audit", "chain"):
        pairs = []
        for case_id, case in sorted(cases.items()):
            def item(arm, kind):
                found = [r for r in rows if r["case_id"] == case_id and r["method"] == arm
                         and r["kind"] == kind and r["repeat"] == 1]
                return found[0] if len(found) == 1 else None
            original, reviewed, native = item(method, "main"), item(method, "review"), item("skillflow", "main")
            valid = all(r is not None and r.get("human_verification_complete")
                        and r["judgment"] not in pending for r in (original, reviewed, native))
            pair = {"case_id": case_id, "source_cluster": case["source_cluster"], "adjudicated": valid,
                    "original": original["judgment"] if original else "not_generated",
                    "fixed_review": reviewed["judgment"] if reviewed else "not_generated",
                    "skillflow_r1": native["judgment"] if native else "not_generated"}
            if valid:
                pair["review_uplift"] = int(reviewed["judgment"] == "satisfies_reference") - int(original["judgment"] == "satisfies_reference")
                pair["skillflow_minus_fixed_review"] = int(native["judgment"] == "satisfies_reference") - int(reviewed["judgment"] == "satisfies_reference")
            pairs.append(pair)
        complete = len(pairs) == 24 and all(p["adjudicated"] for p in pairs)
        entry = {"method": method, "planned_pairs": 24, "complete": complete, "pairs": pairs,
                 "comparison_basis": "Secondary: SkillFlow repeat one versus the prespecified reviewed repeat one, and original repeat one versus its review. No reviewed substitute is selected after failure.",
                 "cost_basis": "Use original answer plus fixed review, as retained in cost-ledger.json.",
                 "interpretation": "Incomplete or unresolved pairs cannot establish a review benefit, equivalence, or survival of a main-arm advantage."}
        if complete:
            entry["review_uplift"] = paired_cluster_statistics([
                {"source_cluster": p["source_cluster"], "difference": p["review_uplift"]} for p in pairs])
            entry["skillflow_vs_fixed_review"] = paired_cluster_statistics([
                {"source_cluster": p["source_cluster"], "difference": p["skillflow_minus_fixed_review"]} for p in pairs])
        output.append(entry)
    valid = [e for e in output if "two_sided_cluster_sign_flip_p" in e.get("skillflow_vs_fixed_review", {})]
    if len(valid) == 2:
        adjusted = holm_adjust([e["skillflow_vs_fixed_review"]["two_sided_cluster_sign_flip_p"] for e in valid])
        for entry, pvalue in zip(valid, adjusted):
            statistic = entry["skillflow_vs_fixed_review"]
            statistic["secondary_family_holm_adjusted_p"] = pvalue
            interval = statistic["simultaneous_97_5_percent_interval"]
            statistic["practical_advantage_method"] = (
                "skillflow" if statistic["difference"] >= .10 and interval[0] > 0 and pvalue < .05
                else entry["method"] + "+fixed_review" if statistic["difference"] <= -.10 and interval[1] < 0 and pvalue < .05 else None)
            entry["interpretation"] = ("A practical SkillFlow advantage remains established against this fixed-reviewed R1 baseline."
                if statistic["practical_advantage_method"] == "skillflow" else
                "A practical advantage is established for the fixed-reviewed R1 baseline."
                if statistic["practical_advantage_method"] else
                "A practical advantage against this fixed-reviewed R1 baseline is not established; this is not evidence of equivalence.")
    return output


def freeze_outputs(run_dir):
    """Close generation before reference-aware scoring; retain every failure."""
    from .artifacts import verify_candidate
    run = Path(run_dir)
    schedule = _read(run / "schedule.json")
    entries = schedule["main"] + schedule["reviews"]
    if len(entries) != 264 or len({e["workflow_id"] for e in entries}) != 264:
        raise ValueError("Output closure requires all 264 prespecified workflows")
    files = {}
    for item in entries:
        workflow = run / "workflows" / item["workflow_id"]
        path = workflow / "result.json"
        if not path.is_file():
            raise ValueError("All planned outputs, including failures, must exist before scoring")
        result = _read(path)
        if result.get("status") in {None, "running", "pending", "interrupted"}:
            raise ValueError("An active or resumable workflow cannot enter the output freeze")
        files[path.relative_to(run).as_posix()] = sha256(path)
        if result.get("artifact_manifest_sha256"):
            verify_candidate(run, item["workflow_id"], result)
            for name in ("candidate-manifest.json", "candidate-view.txt"):
                member = workflow / name
                files[member.relative_to(run).as_posix()] = sha256(member)
    for request in (run / "mailbox/requests").glob("*/request.json"):
        directory = request.parent
        if not (directory / "response.json").exists() and not (directory / "stop.json").exists():
            raise ValueError("An outstanding request prevents output closure")
    freeze = {"schema_version": SCHEMA, "schedule_sha256": sha256(run / "schedule.json"),
              "files": files, "planned_results": 264, "regeneration_after_freeze": False}
    write_json(run / "output-freeze.json", freeze, immutable=True)
    return freeze


def verify_output_freeze(run_dir):
    run = Path(run_dir)
    freeze = _read(run / "output-freeze.json")
    if freeze.get("planned_results") != 264 or freeze.get("schedule_sha256") != sha256(run / "schedule.json"):
        raise ValueError("Output freeze has a different planned cohort")
    for relative, expected in freeze["files"].items():
        path = (run / relative).resolve()
        if not path.is_relative_to(run.resolve()) or sha256(path) != expected:
            raise ValueError("A frozen candidate output changed")
    return freeze


def import_grade(run_dir, submission_path):
    """Record a human's score only after all target generation has closed."""
    from .corrigenda import resolve_grading_run, assert_active_grading_epoch
    run = resolve_grading_run(run_dir)
    epoch = assert_active_grading_epoch(run)
    verify_output_freeze(run)
    grade = _read(submission_path)
    if epoch and grade.get("grading_epoch_id") != epoch["epoch_id"]:
        raise ValueError("A new grading epoch requires an explicitly current-epoch human score")
    if not grade.get("candidate_id"):
        raise ValueError("Human scores must use their frozen anonymous candidate identity")
    if grade.get("candidate_id"):
        assignments = _read(run / "review/private-scoring-map.json")["assignments"]
        mapped = [a for a in assignments if a["candidate_id"] == grade["candidate_id"]]
        if len(mapped) != 1 or (grade.get("workflow_id") and grade["workflow_id"] != mapped[0]["workflow_id"]):
            raise ValueError("Anonymous candidate identity differs from the frozen scoring map")
        grade = {**grade, "workflow_id": mapped[0]["workflow_id"]}
        expected_person = mapped[0]["primary_reviewer_id"]
        if grade.get("scoring_role", "primary") == "primary" and grade.get("reviewer_id") != expected_person:
            raise ValueError("The primary human score differs from its frozen assignment")
        if grade.get("scoring_role") == "secondary" and grade.get("reviewer_id") == expected_person:
            raise ValueError("The secondary score must be provided by the other human")
    people = {p["reviewer_id"]: p for p in _read(run / "human-roster.json")["reviewers"]}
    person = people.get(grade.get("reviewer_id"), {})
    if person.get("human") is not True or person.get("role") != "reference_verifier":
        raise ValueError("Score import requires a registered actual human reference verifier")
    if (grade.get("confirmation") != "I personally checked this candidate against the source reference."
            or not grade.get("attested_at") or not grade.get("submission_id")):
        raise ValueError("A human score requires an explicit personal confirmation and submission identity")
    schedule = _read(run / "schedule.json")
    items = {e["workflow_id"]: e for e in schedule["main"] + schedule["reviews"]}
    item = items.get(grade.get("workflow_id"))
    if not item:
        raise ValueError("A human score must match a prespecified candidate")
    verify_human_reference_freeze(run, item["case_id"])
    reference = run / "references" / (item["case_id"] + ".json")
    if grade.get("reference_sha256") != sha256(reference):
        raise ValueError("The score is bound to a different reference version")
    result = _read(run / "workflows" / item["workflow_id"] / "result.json")
    candidate = result.get("answer_sha256") or result.get("artifact_manifest_sha256")
    if grade.get("candidate_sha256") != candidate:
        raise ValueError("The score is bound to a different candidate version")
    validate_grade(grade, _read(reference), method=item["method"])
    if grade.get("grading_schema_version"):
        from .semantic_metrics import validate_grade_evidence
        candidate_view = run / "workflows" / item["workflow_id"] / "candidate-view.txt"
        validate_grade_evidence(grade, source_root=run / "cases" / item["case_id"] / "source",
                               candidate_text=candidate_view.read_text(encoding="utf-8") if candidate_view.exists() else "")
    role = grade.get("scoring_role", "primary")
    if role not in {"primary", "secondary"}:
        raise ValueError("Unknown human scoring role")
    safe = canonical_hash({"submission": grade["submission_id"]})[:24]
    path = run / "grades" / (safe + ".json")
    write_json(path, grade, immutable=True)
    manifest_path = run / "grades/import-manifest.json"
    manifest = _read(manifest_path) if manifest_path.exists() else {"records": []}
    record = {"path": path.relative_to(run).as_posix(), "sha256": sha256(path),
              "workflow_id": item["workflow_id"], "reviewer_id": grade["reviewer_id"],
              "scoring_role": role, "import_source": "human_user_submission"}
    if record not in manifest["records"]:
        if any(r["workflow_id"] == record["workflow_id"] and r["scoring_role"] == role for r in manifest["records"]):
            raise ValueError("Preserve a score revision explicitly instead of importing a second current score")
        manifest["records"].append(record)
        write_json(manifest_path, manifest)
    return record


def aggregate_scores(run_dir):
    from .corrigenda import resolve_grading_run
    from .semantic_metrics import reconcile_semantic_grades, aggregate_semantic_metrics, validate_grade_evidence
    run = resolve_grading_run(run_dir)
    schedule = _read(run / "schedule.json")
    entries = schedule["main"] + schedule["reviews"]
    selection = _read(run / "selection.json")
    cases = {case["case_id"]: case for case in selection["selected"]}
    scores = defaultdict(dict)
    manifest = _read(run / "grades/import-manifest.json") if (run / "grades/import-manifest.json").exists() else {"records": []}
    if manifest["records"]:
        verify_output_freeze(run)
        verify_human_reference_freeze(run)
    for imported in manifest["records"]:
        path = (run / imported["path"]).resolve()
        if (not path.is_relative_to((run / "grades").resolve()) or sha256(path) != imported["sha256"]
                or imported.get("import_source") != "human_user_submission"):
            raise ValueError("An imported human score changed or escaped its directory")
        score = _read(path)
        key = score["workflow_id"]
        if key not in {e["workflow_id"] for e in entries}:
            raise ValueError("An unplanned workflow cannot enter the score table")
        role = score.get("scoring_role", "primary")
        if role not in {"primary", "secondary"} or role in scores[key]:
            raise ValueError("Duplicate or unknown scoring role")
        item = next(e for e in entries if e["workflow_id"] == key)
        reference_path = run / "references" / f"{item['case_id']}.json"
        if score.get("reference_sha256") != sha256(reference_path):
            raise ValueError("Score reference version changed; use a preserved corrigendum and regrade every method")
        validate_grade(score, _read(reference_path), method=item["method"])
        workflow = run / "workflows" / key
        if score.get("grading_schema_version"):
            view = workflow / "candidate-view.txt"
            validate_grade_evidence(score, source_root=run / "cases" / item["case_id"] / "source",
                                   candidate_text=view.read_text(encoding="utf-8") if view.exists() else "")
        result = _read(workflow / "result.json")
        if score.get("candidate_sha256") != (result.get("answer_sha256") or result.get("artifact_manifest_sha256")):
            raise ValueError("Scoring candidate identity changed")
        scores[key][role] = score
    primary_scores = [dict(v["primary"], candidate_id=key) for key, v in scores.items() if "primary" in v]
    double_check = set(second_review_sample(primary_scores)) if len(primary_scores) == len(entries) else set()
    rows = []
    terminal_failures = {"failed", "budget_exhausted", "context_limit", "protocol_violation", "not_reviewable", "timeout"}
    for item in entries:
        key = item["workflow_id"]
        path = run / "workflows" / key / "result.json"
        result = _read(path) if path.exists() else None
        views = scores.get(key, {})
        technical_failure = bool(result and result.get("status") in terminal_failures)
        from .execution import assess_request_protocol
        dispatched = [p for p in (run / "mailbox/requests").glob(key + "_q*") if (p / "dispatch.json").exists()]
        protocol_eligible = bool(dispatched) and all(
            _read(p / "response.json").get("accepted") is True
            and assess_request_protocol(p)["status"] == "conformant"
            for p in dispatched if (p / "response.json").exists()) and all((p / "response.json").exists() for p in dispatched)
        if result and (technical_failure or not protocol_eligible) and len(primary_scores) == len(entries):
            double_check.add(key)
        human_complete = "primary" in views and (key not in double_check or "secondary" in views)
        if "primary" not in views:
            judgment = "unassessed" if result is not None else "not_generated"
        elif key in double_check and "secondary" not in views:
            judgment = "pending_secondary_human"
        else:
            if "secondary" in views and views["secondary"]["reviewer_id"] == views["primary"]["reviewer_id"]:
                raise ValueError("Independent secondary scoring requires a different human")
            judgment = paired_judgment(views["primary"], views.get("secondary"))
            if not protocol_eligible or (technical_failure and not (result.get("answer_sha256") or result.get("artifact_manifest_sha256"))):
                judgment = "workflow_failure"
        detail = (reconcile_semantic_grades(views["primary"], views.get("secondary")) if human_complete
                  else {"adjudicated_grade": None, "metric_disputes": ["required_human_verification_pending"]})
        rows.append({**item, **detail, "judgment": judgment, "execution_status": result.get("status") if result else "not_started",
                     "technical_failure": technical_failure, "human_verification_complete": human_complete,
                     "protocol_eligible": protocol_eligible,
                     "source_cluster": cases[item["case_id"]]["source_cluster"],
                     "human_reviewers": {role: score["reviewer_id"] for role, score in views.items()},
                     "matched_exposure_ids": (detail.get("adjudicated_grade") or {}).get("matched_exposure_ids"),
                     "usage": result.get("usage") if result else None})
    groups = defaultdict(Counter)
    for row in rows:
        groups[f"{row['method']}/{row['kind']}"][row["judgment"]] += 1
    pending = {"not_generated", "unassessed", "pending_secondary_human"}
    complete = not any(r["judgment"] in pending or not r["human_verification_complete"] for r in rows)
    comparisons = []
    unresolved = sum(r["judgment"] == "indeterminate" for r in rows)
    if complete and unresolved == 0:
        for other in ("audit", "chain"):
            differences = []
            for case_id in sorted(cases):
                means = {}
                for method in ("skillflow", other):
                    observed = [r for r in rows if r["case_id"] == case_id and r["method"] == method and r["kind"] == "main"]
                    if len(observed) != 3:
                        raise ValueError("The complete-case table must retain all three planned repetitions")
                    means[method] = sum(r["judgment"] == "satisfies_reference" for r in observed) / 3
                differences.append({"source_cluster": cases[case_id]["source_cluster"],
                                    "difference": means["skillflow"] - means[other]})
            stats = paired_cluster_statistics(differences)
            comparisons.append({"methods": ["skillflow", other], **stats})
        if all("two_sided_cluster_sign_flip_p" in c for c in comparisons):
            values = holm_adjust([c["two_sided_cluster_sign_flip_p"] for c in comparisons])
            for comparison, adjusted in zip(comparisons, values):
                comparison["holm_adjusted_p"] = adjusted
                comparison["practical_accuracy_advantage"] = (
                    comparison["difference"] >= .10 and adjusted < .05
                    and comparison["simultaneous_97_5_percent_interval"][0] > 0)
                interval = comparison["simultaneous_97_5_percent_interval"]
                comparison["practical_advantage_method"] = (
                    comparison["methods"][0] if comparison["difference"] >= .10 and adjusted < .05 and interval[0] > 0
                    else comparison["methods"][1] if comparison["difference"] <= -.10 and adjusted < .05 and interval[1] < 0
                    else None)
    stability = []
    for case_id in sorted(cases):
        for method in ("skillflow", "audit", "chain"):
            observed = [r for r in rows if r["case_id"] == case_id and r["method"] == method and r["kind"] == "main"]
            assessed = all(r["judgment"] not in pending for r in observed)
            matches = [set(r["matched_exposure_ids"]) for r in observed if r["matched_exposure_ids"] is not None]
            jaccards = []
            if len(matches) == 3:
                for i, j in ((0, 1), (0, 2), (1, 2)):
                    union = matches[i] | matches[j]
                    jaccards.append(len(matches[i] & matches[j]) / len(union) if union else 1.0)
            stability.append({"case_id": case_id, "method": method, "assessed": assessed,
                              "all_three_satisfy": assessed and all(r["judgment"] == "satisfies_reference" for r in observed),
                              "matched_reference_unit_jaccard": sum(jaccards) / 3 if jaccards else None,
                              "note": "An empty-set match is not proof that an answer is correct; unknown or false extra claims need separate human assessment."})
    reference_paths = {case_id: run / "references" / (case_id + ".json") for case_id in cases}
    missing_references = sorted(case_id for case_id, path in reference_paths.items() if not path.is_file())
    semantic = ({"status": "reference_drafts_not_prepared", "missing_reference_case_ids": missing_references,
                 "groups": {}, "model_calls": 0} if missing_references else
                aggregate_semantic_metrics(rows, {case_id: _read(path) for case_id, path in reference_paths.items()}))
    output = {"schema_version": SCHEMA, "complete": complete, "planned_results": len(entries),
              "all_planned_in_denominator": True, "groups": {k: dict(v) for k, v in sorted(groups.items())},
              "secondary_human_required": sorted(double_check), "rows": rows,
              "unresolved_results": unresolved,
              "inferential_status": "ready" if complete and not unresolved else "pending_or_unresolved_adjudication",
              "unresolved_policy": "Unresolved semantic disagreements are not converted to definite errors or a definite accuracy point estimate.",
              "primary_comparisons": comparisons, "stability": stability,
              "fixed_review_comparisons": fixed_review_comparisons(rows, cases),
              "semantic_metrics": semantic,
              "reference_approval_state": "approved_frozen" if (run / "reference-freeze.json").exists() else "unapproved_drafts_only",
              "interpretation": "No method advantage is inferred while results or human checks remain incomplete. Indeterminate results remain visible; failures do not disappear from the denominator.",
              "human_identity_limit": "Human scores are explicit self-attested submissions. The software does not independently establish personhood.",
              "model_calls": 0}
    write_json(run / "scores.json", output)
    return {k: v for k, v in output.items() if k not in {"rows", "stability"}}
