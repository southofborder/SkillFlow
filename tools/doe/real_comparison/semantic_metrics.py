"""Versioned human semantic measurements, independent of target answer format.

The additional schema belongs to human adjudication. No method is required to
emit these fields, and none of these descriptive endpoints changes the common
all-or-nothing primary judgment or its multiplicity family.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import PurePosixPath, PureWindowsPath

from .protocol import canonical_hash


GRADING_SCHEMA_VERSION = "skillflow-real-comparison-grading-v2"
EXPOSURE_FIELDS = ("source", "sensitive_scope", "version", "condition", "recipient", "boundary_event")
CHAIN_LAYERS = ("purpose", "sensitive_sources", "dataflow_and_versions", "processing",
                "conditions_and_pairing", "recipients_and_boundaries", "necessity", "reductions")
CHAIN_LINKS = ("purpose_to_necessity", "source_to_flow", "processing_to_payload",
               "condition_and_recipient_to_exposure", "necessity_to_reduction")
ERROR_CATEGORIES = {"unsupported_excess", "unsupported_recipient", "invented_protection",
                    "plaintext_from_possible_influence", "duplicate_boundary", "harmful_reduction",
                    "lost_required_value", "lost_condition", "lost_cardinality", "lost_quality",
                    "lost_recipient", "lost_required_side_effect", "other"}


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _unique_ids(records, field, label):
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError(label + " must be a list of human records")
    values = [r.get(field) for r in records]
    if any(not _nonempty(v) for v in values) or len(values) != len(set(values)):
        raise ValueError(label + " requires nonempty unique identities")
    return set(values)


def _evidence(items, *, source=False, required=True):
    if not isinstance(items, list) or (required and not items):
        raise ValueError("Human semantic assessments require source and candidate evidence lists")
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Evidence requires physical lines and an exact quotation")
        start, end = item.get("start_line"), item.get("end_line")
        if (type(start) is not int or type(end) is not int or start < 1 or end < start
                or not _nonempty(item.get("quote"))):
            raise ValueError("Evidence requires physical lines and an exact quotation")
        if source:
            path = item.get("path")
            if (not _nonempty(path) or PurePosixPath(path).is_absolute()
                    or PureWindowsPath(path).is_absolute() or ".." in path.replace("\\", "/").split("/")):
                raise ValueError("Source evidence must use a relative frozen-source path")


def _reason_evidence(record, *, candidate_required=True):
    if not _nonempty(record.get("reason")):
        raise ValueError("Each human semantic assessment requires a source-based reason")
    _evidence(record.get("source_evidence"), source=True)
    _evidence(record.get("candidate_evidence"), required=candidate_required)


def validate_grading_reference(reference):
    """Validate the denominators required by v2, without interpreting source text."""
    _unique_ids(reference.get("supported_excesses"), "id", "Reference exposure units")
    _unique_ids(reference.get("receiving_points"), "id", "Reference receiving points")
    keys = []
    for unit in reference["supported_excesses"]:
        if any(not _nonempty(unit.get(f)) for f in EXPOSURE_FIELDS):
            raise ValueError("Each reference exposure requires all six material identity fields")
        if "reduction_required" in unit and type(unit["reduction_required"]) is not bool:
            raise ValueError("Reference reduction_required must be an explicit boolean")
        keys.append(canonical_hash({f: unit[f].strip() for f in EXPOSURE_FIELDS}))
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate normalized reference units cannot inflate coverage")
    return reference


def grading_template(reference, method):
    """Pending human fields only; a template is never a completed assessment."""
    validate_grading_reference(reference)
    pending = lambda field, value: {field: value, "status": "pending", "reason": "",
                                    "source_evidence": [], "candidate_evidence": []}
    return {"grading_schema_version": GRADING_SCHEMA_VERSION,
            "claim_units": [],
            "receiving_point_coverage": [pending("receiving_point_id", p["id"])
                                         for p in reference["receiving_points"]],
            "reduction_assessments": [pending("reference_exposure_id", u["id"])
                                      for u in reference["supported_excesses"]],
            "error_records": [],
            "chain_assessment": None if method == "audit" else {
                "completeness": [pending("layer", layer) for layer in CHAIN_LAYERS],
                "consistency": [pending("link", link) for link in CHAIN_LINKS]}}


def validate_semantic_grade(grade, reference, *, method=None):
    """Validate human mappings; exact quote verification needs the sealed packet.

    Source/candidate evidence is preserved verbatim here. The importer can use
    ``validate_grade_evidence`` to compare its quotations to frozen input bytes.
    """
    if grade.get("grading_schema_version") != GRADING_SCHEMA_VERSION:
        raise ValueError("Formal human scoring requires grading schema v2")
    if method not in {None, "skillflow", "audit", "chain"}:
        raise ValueError("Unknown method for secondary semantic grading")
    validate_grading_reference(reference)
    known = {u["id"] for u in reference["supported_excesses"]}
    claims = grade.get("claim_units")
    _unique_ids(claims, "claim_id", "Normalized candidate claim units")
    keys, matched = set(), set()
    for claim in claims:
        if any(not _nonempty(claim.get(f)) for f in EXPOSURE_FIELDS):
            raise ValueError("A normalized claim requires all six material exposure identity fields")
        key = canonical_hash({f: claim[f].strip() for f in EXPOSURE_FIELDS})
        if key in keys:
            raise ValueError("Duplicate normalized candidate claims cannot inflate precision or credit")
        keys.add(key)
        refs = claim.get("matched_reference_ids")
        if (not isinstance(refs, list) or any(not _nonempty(v) for v in refs)
                or len(refs) != len(set(refs)) or not set(refs).issubset(known)):
            raise ValueError("Claim matches require distinct frozen reference exposure identities")
        status = claim.get("assessment")
        if status not in {"supported", "unsupported", "disputed"}:
            raise ValueError("A normalized claim requires a supported, unsupported or disputed assessment")
        if status == "supported":
            if len(refs) != 1 or matched.intersection(refs):
                raise ValueError("Normalize each supported exposure once; broad claims need separate unambiguous unit mappings")
            reference_unit = next(u for u in reference["supported_excesses"] if u["id"] == refs[0])
            if key != canonical_hash({f: reference_unit[f].strip() for f in EXPOSURE_FIELDS}):
                raise ValueError("A supported human-normalized claim must preserve its canonical reference's six dimensions")
            matched.update(refs)
        if status == "unsupported" and refs:
            raise ValueError("An unsupported claim cannot receive reference credit")
        _reason_evidence(claim)
    if matched != set(grade.get("matched_exposure_ids", [])):
        raise ValueError("Human claim mappings differ from matched_exposure_ids")
    coverage = grade.get("receiving_point_coverage")
    if _unique_ids(coverage, "receiving_point_id", "Receiving-point coverage") != {
            p["id"] for p in reference["receiving_points"]}:
        raise ValueError("Score every reference receiving point exactly once")
    for record in coverage:
        if record.get("status") not in {"covered", "missed", "disputed"}:
            raise ValueError("Unknown receiving-point coverage status")
        _reason_evidence(record, candidate_required=record["status"] == "covered")
    reductions = grade.get("reduction_assessments")
    if _unique_ids(reductions, "reference_exposure_id", "Reduction assessments") != known:
        raise ValueError("Assess a reduction for every established reference excess exactly once")
    for record in reductions:
        if record.get("status") not in {"adequate", "missing", "harmful", "disputed", "not_established_reducible"}:
            raise ValueError("Unknown reduction assessment status")
        reference_unit = next(u for u in reference["supported_excesses"] if u["id"] == record["reference_exposure_id"])
        if record["status"] == "not_established_reducible" and reference_unit.get("reduction_required") is not False:
            raise ValueError("A reduction exemption requires the source reference to explicitly mark reduction_required false")
        _reason_evidence(record, candidate_required=record["status"] in {"adequate", "harmful"})
    errors = grade.get("error_records")
    _unique_ids(errors, "error_id", "Semantic error records")
    for record in errors:
        if (record.get("category") not in ERROR_CATEGORIES
                or record.get("severity") not in {"minor", "substantive", "disputed"}
                or record.get("functionality_impact") not in {"none", "breaks_required_behavior", "disputed"}):
            raise ValueError("Semantic errors require a known category, severity and functionality impact")
        _reason_evidence(record, candidate_required=record["category"] not in {
            "lost_required_value", "lost_condition", "lost_cardinality", "lost_quality", "lost_recipient", "lost_required_side_effect"})
    chain = grade.get("chain_assessment")
    if method == "audit" and chain is not None:
        raise ValueError("The direct audit does not have a chain completeness endpoint")
    if method in {"skillflow", "chain"} and not isinstance(chain, dict):
        raise ValueError("SkillFlow and full-chain scoring require separate chain secondary assessments")
    if chain is not None:
        if not isinstance(chain, dict):
            raise ValueError("Invalid chain assessment")
        for group, field, expected in (("completeness", "layer", CHAIN_LAYERS),
                                       ("consistency", "link", CHAIN_LINKS)):
            records = chain.get(group)
            if _unique_ids(records, field, "Chain " + group) != set(expected):
                raise ValueError("Score every chain secondary dimension exactly once")
            for record in records:
                if record.get("status") not in {"pass", "fail", "disputed"}:
                    raise ValueError("Unknown chain secondary status")
                _reason_evidence(record, candidate_required=record["status"] == "pass")
    if grade.get("judgment") == "satisfies_reference" and (
            any(c["assessment"] != "supported" for c in claims)
            or any(r["status"] != "covered" for r in coverage)
            or any(r["status"] in {"missing", "harmful", "disputed"} for r in reductions)
            or any(r["severity"] in {"substantive", "disputed"}
                   or r["functionality_impact"] != "none" for r in errors)):
        raise ValueError("A passing primary judgment contradicts a material v2 semantic assessment")
    # Chain failure is secondary and deliberately does not invalidate a common
    # primary audit pass, including for SkillFlow and the full-chain prompt.
    return grade


def validate_grade_evidence(grade, *, source_root, candidate_text):
    """Check exact source/candidate quotations; never execute downloaded source."""
    from pathlib import Path
    source_root = Path(source_root).resolve()
    candidate_lines = candidate_text.splitlines()
    records = (grade["claim_units"] + grade["receiving_point_coverage"]
               + grade["reduction_assessments"] + grade["error_records"])
    if grade.get("chain_assessment") is not None:
        records += grade["chain_assessment"]["completeness"] + grade["chain_assessment"]["consistency"]
    for record in records:
        for evidence in record["source_evidence"]:
            path = (source_root / evidence["path"]).resolve()
            if not path.is_relative_to(source_root) or not path.is_file():
                raise ValueError("Grade source evidence is outside or absent from the frozen source")
            lines = path.read_text(encoding="utf-8-sig").splitlines()
            if evidence["end_line"] > len(lines) or evidence["quote"] != "\n".join(lines[evidence["start_line"] - 1:evidence["end_line"]]):
                raise ValueError("Grade source quotation differs from the frozen source")
        for evidence in record["candidate_evidence"]:
            if evidence["end_line"] > len(candidate_lines) or evidence["quote"] != "\n".join(candidate_lines[evidence["start_line"] - 1:evidence["end_line"]]):
                raise ValueError("Grade candidate quotation differs from the frozen anonymous candidate")
    return grade


def reconcile_semantic_grades(primary, secondary=None):
    """Preserve detailed human disagreement even when coarse judgments agree.

    Wording and evidence formatting can differ without creating a disagreement;
    normalized unit mappings, coverage, error classifications and secondary
    statuses must agree. This does not reconcile or replace primary judgments.
    """
    if primary is None:
        return {"adjudicated_grade": None, "metric_disputes": ["primary_human_score_missing"]}
    if secondary is None:
        return {"adjudicated_grade": primary, "metric_disputes": []}
    if (primary.get("grading_schema_version") != GRADING_SCHEMA_VERSION
            or secondary.get("grading_schema_version") != GRADING_SCHEMA_VERSION):
        return {"adjudicated_grade": None, "metric_disputes": ["v2_human_semantic_assessment_missing"]}
    def signature(grade):
        claims = sorted((canonical_hash({f: c[f].strip() for f in EXPOSURE_FIELDS}),
                         c["assessment"], tuple(sorted(c["matched_reference_ids"]))) for c in grade["claim_units"])
        chain = grade.get("chain_assessment")
        return {"claim_units": claims,
                "receiving_point_coverage": sorted((r["receiving_point_id"], r["status"]) for r in grade["receiving_point_coverage"]),
                "reduction_assessments": sorted((r["reference_exposure_id"], r["status"]) for r in grade["reduction_assessments"]),
                "error_records": sorted((r["category"], r["severity"], r["functionality_impact"]) for r in grade["error_records"]),
                "chain_assessment": None if chain is None else {
                    "completeness": sorted((r["layer"], r["status"]) for r in chain["completeness"]),
                    "consistency": sorted((r["link"], r["status"]) for r in chain["consistency"])}}
    left, right = signature(primary), signature(secondary)
    disputes = sorted(k for k in left if left[k] != right[k])
    return {"adjudicated_grade": None if disputes else primary, "metric_disputes": disputes}


def _mean(values):
    return sum(values) / len(values) if values and all(v is not None for v in values) else None


def _unit_metrics(grade, reference, *, method, judgment):
    positives = len(reference["supported_excesses"])
    receivers = len(reference["receiving_points"])
    reducible = {u["id"] for u in reference["supported_excesses"] if u.get("reduction_required") is not False}
    result = {"reference_positive_units": positives, "reference_receiving_points": receivers,
              "reference_reducible_units": len(reducible),
              "assessed": False, "unresolved": False}
    scalar = ("tp", "fn", "fp", "precision", "recall", "covered_receiving_points", "receiving_point_coverage",
              "adequate_reductions", "reduction_coverage", "substantive_errors", "functionality_errors",
              "chain_completeness", "chain_consistency", "disputed_claims")
    if grade is None or grade.get("grading_schema_version") != GRADING_SCHEMA_VERSION:
        return {**result, **dict.fromkeys(scalar), "error_categories": None, "unsupported_claim_keys": None}
    validate_semantic_grade(grade, reference, method=method)
    claims = grade["claim_units"]
    tp = len({ref for c in claims if c["assessment"] == "supported" for ref in c["matched_reference_ids"]})
    fp = sum(c["assessment"] == "unsupported" for c in claims)
    disputed = sum(c["assessment"] == "disputed" for c in claims)
    unresolved = judgment == "indeterminate" or disputed > 0
    coverage = grade["receiving_point_coverage"]
    reductions = grade["reduction_assessments"]
    errors = grade["error_records"]
    chain = grade["chain_assessment"]
    covered = sum(r["status"] == "covered" for r in coverage)
    adequate = sum(r["status"] == "adequate" and r["reference_exposure_id"] in reducible for r in reductions)
    result.update(assessed=True, unresolved=unresolved, tp=None if unresolved else tp,
                  fn=None if unresolved else positives - tp, fp=None if unresolved else fp,
                  precision=tp / (tp + fp) if tp + fp and not unresolved else None,
                  recall=tp / positives if positives and not unresolved else None,
                  disputed_claims=disputed, covered_receiving_points=covered,
                  receiving_point_coverage=covered / receivers if receivers and not any(r["status"] == "disputed" for r in coverage) else None,
                  adequate_reductions=adequate,
                  reduction_coverage=adequate / len(reducible) if reducible and not any(r["status"] == "disputed" for r in reductions) else None,
                  substantive_errors=None if any(r["severity"] == "disputed" for r in errors) else sum(r["severity"] == "substantive" for r in errors),
                  functionality_errors=None if any(r["functionality_impact"] == "disputed" for r in errors) else sum(r["functionality_impact"] == "breaks_required_behavior" for r in errors),
                  error_categories=None if any(r["severity"] == "disputed" for r in errors) else dict(Counter(r["category"] for r in errors if r["severity"] == "substantive")),
                  unsupported_claim_keys=None if unresolved else sorted(canonical_hash({f: c[f].strip() for f in EXPOSURE_FIELDS})
                                                for c in claims if c["assessment"] == "unsupported"))
    for group, name in (("completeness", "chain_completeness"), ("consistency", "chain_consistency")):
        result[name] = (sum(r["status"] == "pass" for r in chain[group]) / len(chain[group])
                        if chain and not any(r["status"] == "disputed" for r in chain[group]) else None)
    return result


def aggregate_semantic_metrics(rows, references):
    """Descriptive case means over all planned rows, preserving unknowns.

    ``rows`` must include the entire planned schedule. Each row supplies its
    final ``judgment`` and ``adjudicated_grade`` (None until human adjudication).
    No target output schema, model call, hypothesis test or primary decision is
    introduced. Unknown/disputed rates are not silently omitted from an average.
    """
    groups, seen, observations = defaultdict(list), set(), []
    for row in rows:
        key = (row["case_id"], row["method"], row["kind"], row["repeat"])
        if key in seen:
            raise ValueError("Duplicate planned repetitions cannot enter semantic metrics")
        seen.add(key)
        reference = references[row["case_id"]]
        metrics = _unit_metrics(row.get("adjudicated_grade"), reference, method=row["method"], judgment=row["judgment"])
        observation = {**{k: row[k] for k in ("case_id", "method", "kind", "repeat", "source_cluster")},
                       "metric_disputes": row.get("metric_disputes", []), **metrics}
        observations.append(observation)
        groups[(row["method"], row["kind"], row["case_id"])].append(observation)
    scalars = ("tp", "fn", "fp", "precision", "recall", "covered_receiving_points", "receiving_point_coverage",
               "adequate_reductions", "reduction_coverage", "substantive_errors", "functionality_errors",
               "chain_completeness", "chain_consistency", "disputed_claims")
    case_means, stability = [], []
    for (method, kind, case_id), observed in sorted(groups.items()):
        case = {"case_id": case_id, "method": method, "kind": kind,
                "source_cluster": observed[0]["source_cluster"], "planned_repetitions": len(observed),
                "assessed_repetitions": sum(r["assessed"] for r in observed),
                "reference_positive_units": observed[0]["reference_positive_units"],
                "reference_receiving_points": observed[0]["reference_receiving_points"],
                "reference_reducible_units": observed[0]["reference_reducible_units"],
                **{field: _mean([r[field] for r in observed]) for field in scalars}}
        categories = sorted({k for r in observed for k in (r["error_categories"] or {})})
        case["error_categories"] = None if any(r["error_categories"] is None for r in observed) else {
            k: _mean([r["error_categories"].get(k, 0) for r in observed]) for k in categories}
        case_means.append(case)
        if kind == "main":
            sets = [set(r["unsupported_claim_keys"]) for r in observed if r["unsupported_claim_keys"] is not None and not r["unresolved"]]
            pairs = [len(a & b) / len(a | b) if a | b else 1.0 for a, b in combinations(sets, 2)] if len(sets) == 3 and len(observed) == 3 else []
            stability.append({"case_id": case_id, "method": method,
                              "unsupported_claim_jaccard": _mean(pairs),
                              "all_three_have_no_unsupported_claims": all(not s for s in sets) if len(sets) == 3 and len(observed) == 3 else None})
    summaries = {}
    for method, kind in sorted({(r["method"], r["kind"]) for r in rows}):
        cases = [c for c in case_means if c["method"] == method and c["kind"] == kind]
        observed = [r for r in observations if r["method"] == method and r["kind"] == kind]
        categories = sorted({k for c in cases for k in (c["error_categories"] or {})})
        summaries[method + "/" + kind] = {
            "planned_cases": len(cases), "source_clusters": len({c["source_cluster"] for c in cases}),
            "planned_workflows": len(observed), "assessed_workflows": sum(r["assessed"] for r in observed),
            "unresolved_workflows": sum(r["unresolved"] for r in observed),
            "source_positive_cases": sum(c["reference_positive_units"] > 0 for c in cases),
            "source_positive_units": sum(c["reference_positive_units"] for c in cases),
            "source_receiving_points": sum(c["reference_receiving_points"] for c in cases),
            "source_reducible_units": sum(c["reference_reducible_units"] for c in cases),
            "case_averaged": {field: _mean([c[field] for c in cases
                if (field != "recall" or c["reference_positive_units"] > 0)
                and (field != "reduction_coverage" or c["reference_reducible_units"] > 0)]) for field in scalars},
            "case_averaged_error_categories": {k: _mean([c["error_categories"].get(k, 0) if c["error_categories"] is not None else None for c in cases]) for k in categories}}
    return {"grading_schema_version": GRADING_SCHEMA_VERSION, "groups": summaries,
            "source_defined_strata": stratified_check_metrics(rows, references),
            "case_means": case_means, "rows": observations, "unsupported_claim_stability": stability,
            "interpretation": "Descriptive secondary human measurements. Repetitions are averaged within cases; source cluster identities are retained. Recall uses source-positive cases and reduction coverage uses cases with reference-required reductions; these denominators are determined by the source reference. No inferential advantage or quality noninferiority is established by this table. Undefined precision and unresolved/missing assessments remain unknown; an empty unsupported-claim set is not proof of correctness.",
            "model_calls": 0}


def stratified_check_metrics(rows, references):
    """Required-use, excess type and true-uncertainty checks stay distinct.

    These are source-defined mandatory-check summaries, not extra independent
    samples, classifier predictions or replacements for exposure-unit metrics.
    """
    strata = ("necessary_sensitive_use", "excess_payload_on_necessary_action",
              "unnecessary_action_exposure", "source_uncertainty", "other", "unclassified")
    measurements = []
    for row in rows:
        reference = references[row["case_id"]]
        grade = row.get("adjudicated_grade")
        statuses = {c["check_id"]: c["status"] for c in grade.get("check_results", [])} if grade else {}
        for stratum in strata:
            checks = [c["id"] for c in reference["mandatory_checks"]
                      if c.get("stratum", "unclassified") == stratum]
            values = [statuses.get(c) for c in checks]
            rate = (sum(s == "pass" for s in values) / len(values)
                    if values and all(s in {"pass", "fail"} for s in values) else None)
            measurements.append({"case_id": row["case_id"], "source_cluster": row["source_cluster"],
                "method": row["method"], "kind": row["kind"], "repeat": row["repeat"],
                "stratum": stratum, "source_check_count": len(checks), "check_pass_fraction": rate})
    output = []
    for method, kind in sorted({(r["method"], r["kind"]) for r in rows}):
        for stratum in strata:
            case_values = []
            for case_id in sorted(references):
                observed = [m for m in measurements if m["case_id"] == case_id and m["method"] == method
                            and m["kind"] == kind and m["stratum"] == stratum]
                if observed and observed[0]["source_check_count"]:
                    case_values.append({"case_id": case_id, "source_cluster": observed[0]["source_cluster"],
                        "source_check_count": observed[0]["source_check_count"],
                        "planned_repetitions": len(observed),
                        "check_pass_fraction": _mean([m["check_pass_fraction"] for m in observed])})
            output.append({"method": method, "kind": kind, "stratum": stratum,
                           "source_eligible_cases": len(case_values),
                           "source_check_count": sum(c["source_check_count"] for c in case_values),
                           "case_averaged_check_pass_fraction": _mean([c["check_pass_fraction"] for c in case_values]),
                           "case_means": case_values})
    return {"groups": output, "interpretation": "Source-defined mandatory-check strata, averaged across repetitions within each eligible case and then across cases. An absent stratum is undefined, not a perfect score. Missing or disputed grading stays unknown. Unclassified source checks remain explicit; these checks are not independent samples or exposure-unit precision/recall."}
