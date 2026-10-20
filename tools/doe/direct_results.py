"""Build an honest progress or completed report from frozen experiment records."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import html
import json
from pathlib import Path
from statistics import median

from tools.doe.direct_baseline import TOKEN_FIELDS, verify
from tools.doe.direct_experiment import DEFAULT_RUN, ROOT, effective_schedule


def measurements(decisions):
    by_response = {}
    for decision in decisions:
        for rid, usage in decision["usage"]["by_response_id"].items():
            if rid in by_response and by_response[rid] != usage:
                raise ValueError("Conflicting per-response usage")
            by_response[rid] = usage
    fields = {}
    for key in TOKEN_FIELDS:
        known = [u[key] for u in by_response.values() if isinstance(u.get(key), int)]
        missing = len(by_response) - len(known)
        fields[key] = {"reported_subtotal": sum(known), "missing_response_fields": missing,
                       "complete_total": sum(known) if by_response and not missing and all(d["usage"]["response_count"] for d in decisions) else None}
    duration = [d["timing"].get("duration_ms") for d in decisions]
    known_duration = [v / 1000 for v in duration if isinstance(v, (int, float))]
    starts = [d["timing"].get("started_at") for d in decisions]
    ends = [d["timing"].get("completed_at") for d in decisions]
    timing_complete = bool(decisions) and all(isinstance(v, (int, float)) for v in starts + ends)
    return {"trials": len(decisions), "responses": len(by_response), "usage": fields,
            "trials_without_usage_receipts": sum(not d["usage"]["response_count"] for d in decisions),
            "summed_trial_seconds": sum(v for v in duration if isinstance(v, (int, float))) / 1000,
            "trial_duration_complete": all(isinstance(v, (int, float)) for v in duration),
            "trial_seconds": {"minimum": min(known_duration) if known_duration else None,
                              "median": median(known_duration) if known_duration else None,
                              "maximum": max(known_duration) if known_duration else None},
            "target_execution_window_seconds": max(ends) - min(starts) if timing_complete else None,
            "target_execution_window_basis": "Earliest target start to latest target completion, including orchestration gaps; concurrent trial durations are not summed here.",
            "protocol": dict(Counter(d["protocol_status"] for d in decisions)),
            "monetary_cost": None}


def build(run: Path, *, require_complete=False):
    schedule = effective_schedule(run)
    planned = schedule["pilot"] + schedule["heldout"]
    planned_ids = set(planned)
    decisions = {p.parent.name: json.loads(p.read_text(encoding="utf-8")) for p in (run / "trials").glob("*/decision.json")}
    registrations = {p.parent.name: json.loads(p.read_text(encoding="utf-8")) for p in (run / "trials").glob("*/registration.json")}
    assessment_path = run / "assessment-summary.json"
    assessed = json.loads(assessment_path.read_text(encoding="utf-8")) if assessment_path.exists() else {"groups": {}, "candidates": []}
    semantic = {c["trial_id"]: c for c in assessed["candidates"]}
    missing_calls = [t for t in planned if t not in decisions]
    missing_assessment = [t for t in planned if t not in semantic or len(semantic[t].get("reviewer_judgments", {})) != 2]
    integrity = verify(run)
    complete = not missing_calls and not missing_assessment and integrity["verified"]
    if require_complete and not complete:
        raise ValueError(f"Experiment incomplete: {len(missing_calls)} missing calls, {len(missing_assessment)} missing paired assessments")
    groups = defaultdict(list)
    eligible_scores = defaultdict(Counter)
    excluded = []
    exclusion_reasons = {}
    stability = defaultdict(list)
    criterion_profiles = defaultdict(list)
    pairs = []
    def capability_judgment(tid):
        if tid not in planned_ids:
            return "unplanned_trial"
        if tid in decisions and decisions[tid]["protocol_status"] != "conformant":
            return "protocol_invalid"
        return semantic.get(tid, {}).get("judgment", "unassessed")
    for tid, decision in sorted(decisions.items()):
        m = registrations[tid]["metadata"]
        group = f"{m['stage']}/{m['arm']}/{'review' if m['review'] else 'initial'}"
        groups[group].append(decision)
        if decision["protocol_status"] == "conformant" and tid in planned_ids:
            eligible_scores[group][semantic.get(tid, {}).get("judgment", "unassessed")] += 1
        else:
            excluded.append(tid)
            exclusion_reasons[tid] = (["not_in_effective_schedule"] if tid not in planned_ids else []) + ([decision["protocol_status"]] if decision["protocol_status"] != "conformant" else [])
        if m["stage"] == "heldout" and not m["review"]:
            key = (registrations[tid]["case_id"], m["arm"])
            stability[key].append(capability_judgment(tid))
            # Compare source-reference checks rather than lexical answer identity.
            # The two reviewers retain separate profiles; agreement is not gold.
            for reviewer, assessment in semantic.get(tid, {}).get("reviewers", {}).items():
                profile = tuple(sorted((c["reference_author"], c["check_id"], c["status"])
                                       for c in assessment.get("check_results", [])))
                criterion_profiles[(key[0], key[1], reviewer)].append({
                    "trial_id": tid, "profile": profile,
                    "exposure_counts": assessment.get("exposure_counts"),
                    "protocol_eligible": decision["protocol_status"] == "conformant",
                })
        if m["review"]:
            parent = m["parent_trial_id"]
            pairs.append({"parent_trial_id": parent, "review_trial_id": tid,
                          "stage": m["stage"], "arm": m["arm"], "case_id": registrations[tid]["case_id"],
                          "initial": capability_judgment(parent),
                          "review": capability_judgment(tid)})
    reviewed_workflows = defaultdict(list)
    for pair in pairs:
        original, reviewed = pair["parent_trial_id"], pair["review_trial_id"]
        if original in decisions:
            meta = registrations[reviewed]["metadata"]
            reviewed_workflows[f"{meta['stage']}/{meta['arm']}"] += [decisions[original], decisions[reviewed]]
    result = {"schema_version": "direct-baseline-results-v1", "complete": complete,
              "planned_calls": len(planned), "imported_calls": len(decisions),
              "unexpected_imported_trials": sorted(set(decisions) - planned_ids),
              "missing_calls": missing_calls, "missing_paired_assessments": missing_assessment,
              "integrity": integrity, "measurements": measurements(list(decisions.values())),
              "measurement_groups": {g: measurements(ds) for g, ds in groups.items()},
              "reviewed_workflow_measurements": {g: measurements(ds) for g, ds in reviewed_workflows.items()},
              "semantic_groups": assessed["groups"],
              "eligible_semantic_groups": {g: dict(c) for g, c in eligible_scores.items()},
              "excluded_from_capability_counts": excluded,
              "capability_exclusion_reasons": exclusion_reasons,
              "heldout_stability": [{"case_id": case, "arm": arm, "runs": len(states), "outcomes": dict(Counter(states)),
                                     "all_three_satisfy_reference": len(states) == 3 and set(states) == {"satisfies_reference"}}
                                    for (case, arm), states in sorted(stability.items())],
              "heldout_criterion_stability": [
                  {"case_id": case, "arm": arm, "reviewer": reviewer, "runs": len(profiles),
                   "same_mandatory_check_statuses": len(profiles) == 3 and all(p["protocol_eligible"] for p in profiles)
                   and len({p["profile"] for p in profiles}) == 1,
                   "profiles": profiles}
                  for (case, arm, reviewer), profiles in sorted(criterion_profiles.items())],
              "independent_review_pairs": pairs,
              "reference_status": "assistant_authored_exploratory", "same_model_method_comparison": False}
    (run / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Can a strong model directly replace SkillFlow?", "",
             f"**Experiment state: {'complete' if complete else 'in progress'}.** {len(decisions)} of {len(planned)} planned target trials are imported. {len(planned) - len(missing_assessment)} have paired semantic assessments.", "",
             "Two deliverables are tested: direct source-only DOE audit and full source-only semantic-chain reconstruction. Historical SkillFlow outputs are not gold. No same-model SkillFlow run was performed, so this experiment does not establish a causal advantage or disadvantage of the architecture.", "",
             ("One uniform development revision was used and frozen. Both pilot versions remain: 12 original and 12 revised target answers. Preparations of the superseded held-out prompt were never target calls and are not failures or extra samples. " if schedule.get("pilot_revision") else "No development rerun is recorded in the effective schedule. ")
             + "The held-out cohort contains 72 first answers (12 cases × 2 deliverables × 3 independent repeats) and 24 preselected independent reviews of repeat 1.", "",
             "## Semantic observations", "",
             "References and two separate assessments are assistant-authored exploratory evidence. Agreement is not independent human validation. Source-based disputes remain explicit. Trial names, repeats and execution order are hidden. Requested content is provided for fair scoring and reveals artifact kind; answer structure or correction notes may reveal review status. This is identity masking, not complete condition blinding.", "",
             "A source-grounded answer can satisfy the reference while explicitly leaving a DOE question unresolved because the source lacks sensitivity or recipient evidence. That is correct uncertainty handling, not a claim of safety. An indeterminate trial score instead means the assessors or references cannot resolve the answer's adequacy.", "",
             "| Stage / deliverable / response | Satisfies reference | Substantive error | Indeterminate/disagreement | Unassessed |", "|---|---:|---:|---:|---:|"]
    for group, counts in sorted(result["eligible_semantic_groups"].items()):
        lines.append(f"| {group} | {counts.get('satisfies_reference',0)} | {counts.get('substantive_error',0)} | {counts.get('indeterminate_or_reviewer_disagreement',0)} | {counts.get('unassessed',0)} |")
    lines += ["", f"Capability counts require observed protocol conformity and membership in the frozen effective schedule. Excluded for violated, unverified or unplanned execution: {len(excluded)}. Raw assessments remain preserved separately."]
    lines += ["", "## Repetition and one independent review", "",
              "Held-out first answers are sampled three times; only the preselected first repeat is independently reviewed. Reviews do not replace or erase first-answer scores.", ""]
    for arm in ("audit", "chain"):
        s = [v for v in result["heldout_stability"] if v["arm"] == arm and v["runs"] == 3
             and not ({"unassessed", "protocol_invalid", "unplanned_trial"} & set(v["outcomes"]))]
        lines.append(f"- {arm}: {sum(v['all_three_satisfy_reference'] for v in s)}/{len(s)} fully assessed, protocol-eligible case groups have all three answers satisfy the paired reference assessments.")
    lines.append("- Per-reviewer mandatory-check profiles and exposure counts are preserved in results.json. Identical check outcomes do not imply identical reasoning, proposals, or wording.")
    pair_counts = Counter((p["stage"], p["arm"], p["initial"], p["review"]) for p in pairs)
    if pair_counts:
        lines += ["", "| Stage | Deliverable | First-answer judgment | Reviewed judgment | Pairs |", "|---|---|---|---|---:|"]
        for (stage, arm, before, after), count in sorted(pair_counts.items()):
            lines.append(f"| {stage} | {arm} | {before} | {after} | {count} |")
    lines += ["", "## Measured target usage", "",
              "Usage includes the target subagent's base instructions and complete prompt. Reference authoring, scoring and root orchestration are excluded from target totals. Per-response records are deduplicated; reasoning/cache fields are not added again. Missing usage remains unknown. No currency amount is inferred.", "",
              "| Stage / deliverable / response | Calls | Reported total tokens | Complete token total | Sum of individual trial seconds |", "|---|---:|---:|---:|---:|"]
    for group, m in sorted(result["measurement_groups"].items()):
        token = m["usage"]["total_tokens"]
        lines.append(f"| {group} | {m['trials']} | {token['reported_subtotal']:,} | {token['complete_total'] if token['complete_total'] is not None else 'unknown'} | {m['summed_trial_seconds']:.1f} |")
    lines += ["", "The following cost groups include both the preselected original answer and its one independent review, rather than quoting only the review's incremental usage.", "",
              "| Stage / deliverable | Two-call workflows | Original + review total tokens |", "|---|---:|---:|"]
    for group, m in sorted(result["reviewed_workflow_measurements"].items()):
        total = m["usage"]["total_tokens"]["complete_total"]
        lines.append(f"| {group} | {m['trials'] // 2} | {total if total is not None else 'unknown'} |")
    lines += ["", "Individual times overlap during concurrent execution and must not be presented as workflow wall time or added to nested orchestration clocks.", "",
              f"Across all imported targets, median individual duration is {result['measurements']['trial_seconds']['median']} seconds. The earliest-start to latest-completion execution window is {result['measurements']['target_execution_window_seconds']} seconds and includes orchestration gaps. This is distinct from summed trial durations.", "",
              "## Scope and limitations", "",
              "- The three familiar pilots are development observations, not held-out accuracy. The existing historical semantic corpus is not reclassified as an unseen DOE gold standard.",
              "- Target, reference authors and assessors use separate contexts of the same configured model. Correlated interpretation errors can survive agreement; there is no independent human gold standard.",
              "- The twelve new assistant-authored synthetic cases form four controlled triplets. Their explicit controller, data and interface contracts reduce ambiguity relative to many real Skills. They are not twelve independent real-world domains.",
              "- Target runtime configuration is checked per trial. Tools are forbidden by protocol, not disabled by a hard sandbox; base runtime instructions remain present.",
              "- Collaboration task payloads are encrypted in local receipts. Exact delivery equality cannot be independently verified there; saved prompts and dispatcher records are retained without claiming that proof.",
              "- Zero-call replay verifies preserved artifacts and deterministic aggregation; it does not re-prove natural-language judgments or reproduce the model generation.",
              "- Competitive direct answers would leave SkillFlow's empirical advantage unestablished here. A same-model end-to-end method comparison is required before attributing differences to architecture.", "",
              "## Review material", "",
              f"- [Execution schedule]({'schedule-revision1.json' if (run / 'schedule-revision1.json').exists() else 'schedule.json'})", "- [Preregistration](preregistration.json)",
              "- [Measurements and completion state](results.json)", "- [Paired semantic assessment](assessment-report.md)",
              "- [Qualitative historical context](historical-context.md)",
              "- [Reusable direct-audit prompt](prompts/direct-audit-final.txt)",
              "- [Reusable full-chain prompt](prompts/full-chain-final.txt)",
              "- [Original references](references/)", "- [All original target trials](trials/)", ""]
    text = "\n".join(lines)
    (run / "report.md").write_text(text, encoding="utf-8")
    # Safe HTML with working source/output links; no source HTML is executed.
    items = []
    for tid in sorted(decisions):
        judgment = semantic.get(tid, {}).get("judgment", "unassessed")
        items.append(f'<tr><td><a href="trials/{html.escape(tid)}/answer.txt">{html.escape(tid)}</a></td><td>{html.escape(judgment)}</td><td>{html.escape(decisions[tid]["protocol_status"])}</td></tr>')
    rendered = '<!doctype html><meta charset="utf-8"><title>Strong-model direct baseline</title><style>body{max-width:1150px;margin:2em auto;padding:0 1em;font:16px/1.6 system-ui;color:#172b3a}pre{white-space:pre-wrap;background:#f4f7fa;padding:1.2em}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd6dd;padding:.5em}a{color:#1267a5}</style>'
    rendered += '<h1>Strong-model direct baseline</h1><p><a href="report.md">Full report</a> · <a href="results.json">Measurements</a> · <a href="assessment-report.md">Paired evidence</a></p><pre>' + html.escape(text) + '</pre><h2>Original answers</h2><table><tr><th>Trial</th><th>Paired semantic judgment</th><th>Protocol status</th></tr>' + ''.join(items) + '</table>'
    (run / "index.html").write_text(rendered, encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    r = build(args.run_dir, require_complete=args.require_complete)
    print(json.dumps({k: r[k] for k in ("complete", "planned_calls", "imported_calls")}, indent=2))
