"""Honest staged reports for acquisition, human readiness and formal results."""
from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

from .protocol import SCHEMA, sha256, write_json


def _load(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def corpus_manifest(corpus_root):
    """An owner-qualified list of all roster entries, including missing ones."""
    corpus = Path(corpus_root).resolve()
    roster_path = corpus / "roster/entries.json"
    roster = _load(roster_path)
    seal = _load(corpus / "roster/manifest.json")
    if sha256(roster_path) != seal["entries_sha256"]:
        raise ValueError("The frozen downloads roster changed")
    index = _load(corpus / "acquisition-index.json", {"items": []})
    acquired = {r["identity"]: r for r in index["items"]}
    entries, starts, ends = [], [], []
    for source in roster:
        item = {k: source[k] for k in ("rank", "identity", "ownerHandle", "slug", "downloads", "version_pin", "observed_page", "observed_position")}
        row = acquired.get(source["identity"])
        item["acquisition_status"] = row["status"] if row else "not_yet_attempted"
        if row:
            path = (corpus / row["result_path"]).resolve()
            if not path.is_relative_to(corpus) or sha256(path) != row["result_sha256"]:
                raise ValueError("An acquisition result changed before source-manifest export")
            result = _load(path)
            item.update({"result_path": row["result_path"], "result_sha256": row["result_sha256"],
                         "source_kind": result.get("source_kind"), "source_resolution": result.get("source_resolution"),
                         "archive_sha256": result.get("archive_sha256"),
                         "source_view_path": result.get("source_view_path"), "source_view_sha256": result.get("source_view_sha256"),
                         "file_integrity": result.get("file_integrity"), "errors": result.get("errors", []),
                         "attempts": [{"path": p.relative_to(corpus).as_posix(), "sha256": sha256(p)}
                                      for p in sorted(path.parent.parent.glob("*/result.json"))]})
            if result.get("started_at"):
                starts.append(result["started_at"])
            if result.get("ended_at"):
                ends.append(result["ended_at"])
        entries.append(item)
    counts = dict(Counter(e["acquisition_status"] for e in entries))
    output = {"schema_version": SCHEMA, "roster_entries": len(entries),
              "ranking": "Official Skills cumulative downloads, collection-window ordering; not an atomic snapshot.",
              "roster_started_at": seal["started_at"], "roster_ended_at": seal["ended_at"],
              "roster_sha256": sha256(roster_path), "package_observed_start": min(starts) if starts else None,
              "package_latest_recorded_end": max(ends) if ends else None,
              "status_counts": counts, "all_roster_entries_attempted": "not_yet_attempted" not in counts,
              "hash_scope": "Archive hashes describe original archives; file hashes and common-input hashes are distinct and are never substituted.",
              "entries": entries}
    deviations = corpus / "acquisition-protocol-deviations.json"
    if deviations.exists():
        output["acquisition_protocol_deviations"] = {
            "path": deviations.relative_to(corpus).as_posix(), "sha256": sha256(deviations),
            "affected_count": _load(deviations).get("affected_count"),
            "accepted_into_common_source": False}
    write_json(corpus / "source-manifest.json", output)
    lines = ["# ClawHub package availability and integrity record", "",
             f"The sealed roster contains **{len(entries)}** owner-qualified Skills. Counts: `{json.dumps(counts, sort_keys=True)}`.", "",
             "The public list was captured over the saved roster interval, before package downloads. It is not an instantaneous atomic ranking. All 1,000 ranked identities remain in the source manifest; no lower-ranked substitute or newer version is selected for a missing item.", "",
             "Archives and binaries are retained without installation or execution. Availability and integrity failures are not DOE judgments or model failures. Prior failed attempts remain preserved when a documented exact-version recovery succeeds.", "",
             "| Rank | Canonical identity | Version | Current acquisition status | Evidence |", "|---:|---|---|---|---|"]
    for e in entries:
        if e["acquisition_status"] != "complete_verified":
            evidence = f"[Result]({e['result_path']})" if e.get("result_path") else "No completed acquisition attempt yet"
            lines.append(f"| {e['rank']} | {e['identity']} | {e['version_pin']} | {e['acquisition_status']} | {evidence} |")
    if deviations.exists():
        lines += ["", "## Disclosed acquisition deviation", "",
                  "Four hosted entries with no frozen version pin received an unversioned download request before a later check rejected the archive. They have no accepted source view and do not enter eligibility or selection. The collector now rejects missing pins before issuing download requests. Original attempts and the earlier misleading rejection wording remain preserved in the [deviation record](acquisition-protocol-deviations.json). No lower rank or newer source was accepted."]
    (corpus / "missing-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {k: v for k, v in output.items() if k != "entries"}


def report(run_dir, corpus_root):
    run, corpus = Path(run_dir), Path(corpus_root)
    roster = _load(corpus / "roster" / "entries.json", [])
    if isinstance(roster, dict):
        roster = roster.get("entries", roster.get("items", []))
    acquisition_index = _load(corpus / "acquisition-index.json", {})
    acquired_items = acquisition_index.get("items", [])
    acquisition = {"attempted": len(acquired_items), "planned": len(roster),
                   "not_yet_attempted": max(0, len(roster) - len(acquired_items)),
                   "status_counts": dict(Counter(i.get("status", "unknown") for i in acquired_items)),
                   "started_at": acquisition_index.get("started_at"),
                   "updated_at": acquisition_index.get("updated_at"),
                   "offline_verification": _load(corpus / "acquisition-verification-final.json",
                        _load(corpus / "acquisition-verification.json", {})).get("status", "not_recorded")}
    selection = _load(run / "selection.json", {})
    cases = selection.get("selected", selection.get("cases", []))
    reserves = selection.get("reserves", [])
    approvals = _load(run / "approvals" / "import-manifest.json", {"records": []})
    gate = _load(run / "gate.json", {"state": "not_approved"})
    calibration = _load(run / "calibration.json", {"status": "not_started"})
    transport = _load(run / "transport-inspection" / "finding-v2.json",
                      _load(run / "transport-inspection" / "finding.json", {}))
    feasibility = _load(run / "transport-inspection" / "feasibility-result.json", {})
    transport_note = ("The separately authorized fresh-CLI exact-stdin feasibility probe passed identity, visible prompt equality, no-tool and per-response accounting checks. Formal CLI adoption remains unapproved; the original collaboration protocol and three full engineering calibration requirements remain unresolved."
                      if feasibility.get("status") == "passed_feasibility_only" else
                      transport.get("conclusion", "Exact delivery and runtime verification must be demonstrated before formal generation."))
    from .corrigenda import resolve_grading_run, grading_epoch_lineage
    grading_run = resolve_grading_run(run)
    scores = _load(grading_run / "scores.json", {})
    costs = _load(run / "cost-ledger.json", {})
    from .efficiency import efficiency_comparisons
    efficiency = efficiency_comparisons(scores, costs)
    write_json(run / "efficiency-comparisons.json", efficiency)
    semantics = ("measured_with_unresolved_results" if scores.get("complete") and scores.get("unresolved_results")
                 else "measured" if scores.get("complete") else "incomplete" if scores else "not_yet_measured")
    winners = [c.get("practical_advantage_method") for c in scores.get("primary_comparisons", [])
               if c.get("practical_advantage_method")]
    conclusion = ("Preregistered practical accuracy criterion met by: " + ", ".join(winners) + ". Inspect paired case and source-cluster evidence and cost separately."
                  if scores.get("complete") and winners else
                  "No practical comparative advantage is established by the current adjudicated evidence."
                  if scores.get("complete") else
                  "No comparative advantage can be inferred before the preregistered formal experiment and human checks.")
    requests = list((run / "mailbox" / "requests").glob("*/request.json"))
    formal, calibration_requests = 0, 0
    for path in requests:
        item = _load(path, {})
        if item.get("mode") == "formal":
            formal += 1
        elif item.get("mode") == "calibration":
            calibration_requests += 1
    status = {"schema_version": SCHEMA, "stage": "awaiting_human_reference_confirmation" if len(cases) == 24 else "source_acquisition_and_screening",
              "ranked_roster_entries": len(roster), "acquisition": acquisition,
              "selected_cases": len(cases), "reserve_cases": len(reserves),
              "imported_human_reference_confirmations": len(approvals.get("records", [])),
              "formal_gate_state": gate.get("state", "not_approved"),
              "formal_requests_created": formal, "calibration_requests_created": calibration_requests,
              "calibration": calibration, "semantic_comparison": semantics,
              "transport_inspection": transport,
              "authorized_cli_feasibility": feasibility,
              "grading_epoch_lineage": grading_epoch_lineage(run),
              "acquisition_protocol_deviations": _load(corpus / "acquisition-protocol-deviations.json", {}),
              "advantage_conclusion": conclusion,
              "human_authorship_limit": "Registration and submissions are self-attested human records, not cryptographic personhood verification."}
    write_json(run / "readiness.json", status)
    lines = ["# Real-Skill same-runtime comparison: first-delivery record", "",
             "This report records data and engineering readiness. It is not a comparative result and does not establish an advantage for SkillFlow or a direct model.", "",
             f"- Ranked ClawHub roster entries: **{len(roster)}**.",
             f"- Package attempts: **{acquisition['attempted']}**; not yet attempted: **{acquisition['not_yet_attempted']}**. Status counts: `{json.dumps(acquisition['status_counts'], sort_keys=True)}`.",
             f"- Selected formal cases: **{len(cases)}/24**; reserves: **{len(reserves)}/6**.",
             f"- Imported actual-human reference confirmations: **{len(approvals.get('records', []))}**.",
             f"- Formal request records created: **{formal}**; calibration request records: **{calibration_requests}**.",
             f"- Formal gate: **{gate.get('state', 'not_approved')}**; calibration: **{calibration.get('status', 'not_started')}**.", "",
             "## Frozen comparison", "",
             "Three native methods, 24 cases and three independent repeats yield 216 primary workflows. Forty-eight preselected first-repeat independent direct reviews yield 264 result artifacts. SkillFlow starts from source for every workflow; no historical CFG or semantic fact cache is free. All semantic requests use the same observed runtime model/provider/effort and fresh contexts, subject to receipt limitations.", "",
             "The audit purpose is the Skill's declared purpose. There is no independent user task. Author declarations are not independently verified authorization. Fixtures, if any, instantiate existing input interfaces and are explicitly labeled; they do not invent purpose, isolation or protection.", "",
             "## Human action required before formal generation", "",
             "Two actual human source-reference verifiers must independently inspect and confirm the completed ledgers and exact source hashes. Register their pseudonyms and three separate timed-review participants; do not substitute assistant agents. Fill source references before importing confirmation records. No placeholder or assistant draft is human approval.", "",
             "Every result receives a primary human score; all errors/disputes and a seeded 20 percent sample of initial passes receive a second independent human check. Three separate participants later perform 72 balanced timed reviews, capped at 30 minutes each. Source-reference work, scoring work and practical timed review are recorded separately.", "",
             "## Source collection and limitations", "",
             "The raw pool is the official public downloads-ranked Skills catalog captured over the saved collection interval. Pagination is live rather than atomic. Rankings and counts are frozen before package downloads. Unavailable ranked entries remain in the roster; lower ranks are not silently substituted. Popularity and registry security signals are not DOE labels.", "",
             "Raw archives and binaries are preserved without installation or execution. The common readable input excludes only proven registry-injected material and preserves original source/quotations. Source closure gaps and externally unspecified contracts stay explicit. Selection is source-based and precedes method output.", "",
             "## Current evidence", "",
             "Engineering tests and replay can establish preserved bytes, attribution and deterministic reporting. They cannot establish the correctness or completeness of source interpretations. Formal semantic accuracy, stability, operational cost and human review efficiency remain unmeasured until the approved gate and complete cohort are evaluated.", "",
             calibration.get("interpretation", "The engineering calibration state is recorded above. It does not itself establish semantic audit accuracy."), "",
             transport_note, "",
             "## Artifacts", "",
             "- [Frozen protocol](protocol.json) and [common rubric](rubric.md)",
             "- [Readiness state](readiness.json)",
             "- [Selection](selection.json)",
             "- [Human registration template](human-roster.template.json)",
             "- [Reference packets](references/)",
             "- [Engineering calibration](calibration.json)", ""]
    if status["acquisition_protocol_deviations"]:
        lines += ["## Disclosed acquisition deviation", "",
                  status["acquisition_protocol_deviations"]["issue"], "",
                  status["acquisition_protocol_deviations"]["selection_effect"], "",
                  status["acquisition_protocol_deviations"]["remedy"], ""]
    if scores:
        lines += ["## Common semantic outcomes", "", conclusion, "",
                  "Every planned workflow remains in the denominator. Unresolved disagreements are retained as unresolved; they are not definite misses. Native partial status is judged by content. Engineering completion is not semantic success.", "",
                  "| Method / output | Judgment counts |", "|---|---|"]
        for group, counts in sorted(scores.get("groups", {}).items()):
            lines.append(f"| {group} | `{json.dumps(counts, sort_keys=True)}` |")
        lines += ["", "The two primary comparisons average repeats within cases and account for source clusters. Practical thresholds and multiplicity are symmetric for either method.", "",
                  "```json", json.dumps(scores.get("primary_comparisons", []), indent=2), "```", "",
                  "Original direct answers and their fixed independent reviews are separate outcomes. Enhanced cost includes the original answer plus review. A direct-review answer eliminating an apparent SkillFlow advantage must be described explicitly; a review-only token count cannot establish that conclusion.", ""]
        lines += ["## Fixed independent review: secondary paired R1 comparisons", "",
                  "These comparisons pair repeat one with repeat one. The original three-repeat primary comparisons remain unchanged. Incomplete or unresolved results cannot establish equivalence or a self-review benefit.", ""]
        for comparison in scores.get("fixed_review_comparisons", []):
            lines += [f"### {comparison['method']} plus its fixed review", "", comparison["interpretation"], "",
                      "```json", json.dumps({k: v for k, v in comparison.items() if k != "pairs"}, indent=2), "```", ""]
        details = scores.get("semantic_metrics", {})
        lines += ["## Human semantic measurements", "", details.get("interpretation", "Awaiting detailed human adjudication."), "",
                  "Reference state: **" + scores.get("reference_approval_state", "not_recorded") + "**. Counts derived from unapproved drafts are preparation metadata and are not adjudicated DOE prevalence or validated denominators.", "",
                  "```json", json.dumps(details.get("groups", {}), indent=2), "```", "",
                  "Necessary sensitive use, excess payload on a necessary action, exposure from an unnecessary action, and genuine source uncertainty have separate source-defined mandatory-check strata. Missing strata are undefined; repetitions remain inside cases.", "",
                  "```json", json.dumps([{k: v for k, v in g.items() if k != "case_means"} for g in details.get("source_defined_strata", {}).get("groups", [])], indent=2), "```", "",
                  "## Secondary efficiency evidence", "", efficiency["interpretation"], "",
                  "Twenty directional efficiency claims use a separate conservative Bonferroni family for forty one-sided bounds. The primary accuracy comparisons and their Holm correction are unchanged. Degenerate quality intervals cannot support noninferiority.", "",
                  "```json", json.dumps(efficiency["comparisons"], indent=2), "```", ""]
        if grading_run != run:
            lines += ["## Preserved reference correction epochs", "",
                      "Current scores use the active corrected source reference. Earlier references, scores and reasons remain preserved. Every one of the same 264 target outputs requires new-epoch scoring; target generation is closed. Original first-read timed work is retained and its quality is re-adjudicated against the current reference. Target requests are costed once; incremental human work is recorded separately.", "",
                      "```json", json.dumps(grading_epoch_lineage(run), indent=2), "```", ""]
    if feasibility:
        lines += ["## Separately authorized CLI feasibility probe", "",
                  f"Probe status: **{feasibility.get('status')}**. This is an engineering transport result, not a semantic comparison or a replacement for the original failed collaboration attempt.", "",
                  "The saved visible user prompt matched the frozen UTF-8 prompt hash. Actual receipt metadata, tool behavior, per-response usage and response duration are retained in the feasibility record. Hidden reasoning was not exported. The original failed calibration still has unknown usage and is not erased by the successful probe.", "",
                  feasibility.get("remaining_gate", "Formal adoption and human source-reference confirmation remain separate requirements."), "",
                  "```json", json.dumps({"usage": feasibility.get("usage", {}).get("totals"), "timing": feasibility.get("timing")}, indent=2), "```", ""]
    if costs:
        lines += ["## Observed cost and missing cost evidence", "",
                  "Per-response tokens are deduplicated by response ID. Null is unknown, not zero. Response duration, dispatch waiting, deterministic processing and complete workflow elapsed time have separate ledger fields. No currency amount is inferred.", "",
                  "```json", json.dumps(costs.get("target_usage", {}).get("totals", {}), indent=2), "```", "",
                  costs.get("study_preparation_cost", {}).get("reason", "Preparation costs remain separate."), "",
                  "Human source-reference construction, scoring and timed review are separate. Review speed alone does not establish efficiency when corrected conclusions are wrong or unresolved, and timeouts remain censored. Quality noninferiority must be supported before a resource or review-time efficiency claim.", ""]
    text = "\n".join(lines)
    (run / "report.md").write_text(text, encoding="utf-8")
    (run / "index.html").write_text("<!doctype html><meta charset='utf-8'><title>Real-Skill comparison readiness</title><style>body{font:16px system-ui;max-width:1100px;margin:32px auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>Real-Skill comparison readiness</h1><p><a href='report.md'>English report</a> · <a href='selection.json'>Case selection</a> · <a href='readiness.json'>Readiness record</a></p><pre>" + html.escape(text) + "</pre>", encoding="utf-8")
    return status
