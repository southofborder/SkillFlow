"""Synthetic offline aggregation tests; no research-run target is opened."""
from copy import deepcopy
from pathlib import Path
import shutil

import pytest

from tools.doe.real_comparison import exploratory_results as results
from tools.doe.real_comparison import exploratory_grading as grading
from tools.doe.real_comparison.protocol import sha256, write_json
from tools.doe.real_comparison.semantic_metrics import CHAIN_LAYERS, CHAIN_LINKS, GRADING_SCHEMA_VERSION
from tests.doe.test_exploratory_grading import closed_packets, _pass


@pytest.fixture(scope="module", autouse=True)
def cache_unchanged_synthetic_validation():
    """Reuse validated synthetic bytes across scenarios, never skip first checks.

    Windows filesystem resolution dominates repeated 264-packet validation.
    Every new workspace and every changed submission still uses the real path;
    this cache is confined to this test module and keyed by submission bytes.
    """
    contexts, grades = {}, {}
    original_context, original_grade = results._context, results._grade_record
    def context(root):
        key = str(Path(root).resolve())
        if key not in contexts:
            contexts[key] = original_context(root)
        return deepcopy(contexts[key])
    def grade(root, path, **kwargs):
        key = (str(Path(root).resolve()), str(Path(path).resolve()), sha256(path), tuple(sorted(kwargs.items())))
        if key not in grades:
            grades[key] = original_grade(root, path, **kwargs)
        return deepcopy(grades[key])
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(results, "_context", context)
        patch.setattr(results, "_grade_record", grade)
        yield


@pytest.fixture(scope="module")
def cohort(closed_packets, tmp_path_factory):
    base_run, _ = closed_packets
    out = tmp_path_factory.mktemp("assistant-results")
    # Derive a new synthetic cohort whose selection is sealed before packet
    # preparation. The base fixture and every historical artifact stay intact.
    run, root = out / "synthetic-generation", out / "synthetic-grading"
    shutil.copytree(base_run, run)
    schedule = grading.read(run / "schedule.json")
    case_ids = sorted({r["case_id"] for r in schedule["main"]})
    selected = []
    frozen = grading.read(run / "freeze.json")
    for i, case in enumerate(case_ids):
        source_hash = sha256(run / "cases" / case / "source" / "skill.txt")
        selected.append({"case_id": case, "source_cluster": "cluster-" + str(i // 2 if i < 4 else i - 2),
                         "source_sha256": source_hash})
        path = run / "references" / (case + ".json")
        reference = grading.read(path)
        reference["source_sha256"] = source_hash
        write_json(path, reference)
        frozen["files"][path.relative_to(run).as_posix()] = sha256(path)
    write_json(run / "selection.json", {"selected": selected})
    frozen["files"]["selection.json"] = sha256(run / "selection.json")
    write_json(run / "freeze.json", frozen)
    grading.prepare_packets(run, root)
    mapping = grading.read(root / "private-map.json")["assignments"]
    cases = sorted({r["case_id"] for r in mapping})
    metadata = {row["case_id"]: row for row in selected}
    paths = {}
    for item in mapping:
        grade = _pass(root / item["packet"])
        grade.update(agent_id="primary-" + item["candidate_id"], reviewer_id="assistant-primary")
        path = out / "primary" / (item["candidate_id"] + ".json")
        write_json(path, grade)
        paths[item["candidate_id"]] = path
    seal = out / "primary-seal.json"
    results.seal_primary_submissions(root, list(paths.values()), seal)
    assignments = out / "secondary-assignments.json"
    selected = results.prepare_secondary_assignments(root, seal, assignments)
    secondaries, chains = {}, {}
    for item in selected["assignments"]:
        candidate = item["candidate_id"]
        grade = deepcopy(grading.read(paths[candidate]))
        grade.update(scoring_role="secondary", agent_id=item["assignment_kind"] + "-" + candidate,
                     reviewer_id="assistant-independent")
        if item["assignment_kind"] == "chain_secondary":
            evidence = grade["check_results"][0]
            record = {k: deepcopy(evidence[k]) for k in ("reason", "source_evidence", "candidate_evidence")}
            grade["chain_assessment"] = {
                "completeness": [{**deepcopy(record), "layer": key, "status": "pass"} for key in CHAIN_LAYERS],
                "consistency": [{**deepcopy(record), "link": key, "status": "pass"} for key in CHAIN_LINKS]}
        path = out / item["assignment_kind"] / (candidate + ".json")
        write_json(path, grade)
        (chains if item["assignment_kind"] == "chain_secondary" else secondaries)[candidate] = path
    return {"root": root, "out": out, "mapping": mapping, "paths": paths, "seal": seal,
            "assignments": assignments, "secondary": secondaries, "chain": chains, "metadata": metadata}


@pytest.fixture
def fast_statistics(monkeypatch):
    calls = []
    def statistics(rows, **kwargs):
        calls.append(deepcopy(rows))
        value = sum(r["difference"] for r in rows) / len(rows)
        return {"status": "synthetic_statistic", "difference": value,
            "cases": len(rows), "clusters": len({r["source_cluster"] for r in rows}),
            "simultaneous_97_5_percent_interval": [min(0, value), max(0, value)],
            "two_sided_cluster_sign_flip_p": 1.0}
    monkeypatch.setattr(results, "paired_cluster_statistics", statistics)
    return calls


def _aggregate(cohort, **kwargs):
    arguments = {"secondary_submission_paths": list(cohort["secondary"].values()),
        "source_metadata": cohort["metadata"], "bootstrap_samples": 17}
    arguments.update(kwargs)
    return results.aggregate_results(cohort["root"], cohort["seal"], cohort["assignments"], **arguments)


def test_closure_precedes_candidate_validation(tmp_path, monkeypatch):
    root = tmp_path / "unclosed"
    write_json(root / "private-map.json", {"source_run": str(tmp_path / "generation")})
    seen = []
    def forbidden(*args, **kwargs):
        seen.append(True)
        pytest.fail("A candidate was opened before output closure")
    monkeypatch.setattr(grading, "validate_submission", forbidden)
    with pytest.raises(FileNotFoundError, match="output-freeze"):
        results.seal_primary_submissions(root, [tmp_path / "label.json"], tmp_path / "seal.json")
    assert not seen


def test_missing_primary_keeps_all_planned_denominators(cohort, tmp_path, fast_statistics):
    paths = list(cohort["paths"].values())[:-1]
    seal = tmp_path / "partial.json"
    results.seal_primary_submissions(cohort["root"], paths, seal)
    with pytest.raises(ValueError, match="all 264"):
        results.prepare_secondary_assignments(cohort["root"], seal, tmp_path / "selected.json")
    report = results.aggregate_results(cohort["root"], seal, source_metadata=cohort["metadata"], bootstrap_samples=2)
    assert report["planned_results"] == len(report["rows"]) == 264
    assert report["main_bounds"]["planned"] == 216 and report["review_bounds"]["planned"] == 48
    assert report["inferential_status"].startswith("blocked")
    assert report["primary_comparisons"] == []
    assert report["bounds"]["unknown"] >= 1
    assert report["bounds"]["pass_fraction"] is None
    assert report["bounds"]["pass_fraction_bounds"][1] <= 1


def test_seeded_selection_follows_primary_seal_and_includes_failures(cohort):
    selection = grading.read(cohort["assignments"])
    assert selection["primary_seal_sha256"] == sha256(cohort["seal"])
    selected = {r["candidate_id"] for r in selection["assignments"] if r["assignment_kind"] == "primary_recheck"}
    seal = grading.read(cohort["seal"])
    assert selected == set(results._selection(seal))
    failures = {c for c, r in seal["records"].items() if r["execution_status"] == "failed" or not r["protocol_eligible"]}
    assert failures.issubset(selected)
    assert len(selected) >= 53
    assert sum(r["assignment_kind"] == "chain_secondary" for r in selection["assignments"]) == 168
    assert all(not {"judgment", "method", "repeat", "kind"}.intersection(r) for r in selection["assignments"])


def test_missing_recheck_blocks_main_but_chain_missing_does_not(cohort, fast_statistics):
    report = _aggregate(cohort)
    assert report["inferential_status"] == "assistant_exploratory_ready"
    assert len(report["primary_comparisons"]) == 2
    assert report["chain_status"] == {"planned": 168, "complete": 0, "inference_ready": False}
    assert all(r["chain_completeness"] is None for r in report["semantic_metrics"]["rows"])
    missing = _aggregate(cohort, secondary_submission_paths=list(cohort["secondary"].values())[1:])
    assert missing["inferential_status"].startswith("blocked")
    assert len(missing["missing_mandatory_primary_rechecks"]) == 1
    assert missing["primary_comparisons"] == []


def test_eligible_partial_content_and_protocol_invalid_content_are_distinct(cohort, fast_statistics):
    report = _aggregate(cohort)
    rows = {r["workflow_id"]: r for r in report["rows"]}
    partial = rows["synthetic-00_skillflow_1"]
    assert partial["execution_status"] == "failed"
    assert partial["content_judgment"] == partial["judgment"] == "satisfies_reference"
    invalid = rows["synthetic-00_skillflow_2"]
    assert invalid["content_judgment"] == "satisfies_reference"
    assert invalid["judgment"] == "workflow_failure"
    assert report["bounds"]["known_pass"] == 263 and report["bounds"]["known_fail"] == 1
    assert all("human_verification_complete" not in r for r in report["rows"])
    assert report["actual_human_review_work_seconds"] is None


def test_repeat_averaging_and_fixed_review_r1_are_separate(cohort, fast_statistics):
    report = _aggregate(cohort)
    selected = next(r for r in report["case_results"] if r["case_id"] == "synthetic-00" and r["method"] == "skillflow" and r["kind"] == "main")
    assert selected["planned"] == 3 and selected["pass_fraction"] == pytest.approx(2 / 3)
    assert any(any(r["difference"] == pytest.approx(-1 / 3) for r in call) for call in fast_statistics)
    for comparison in report["fixed_review_comparisons"]:
        assert comparison["complete"]
        assert all(p["original_gap"] == p["reviewed_gap"] == p["paired_gap_change"] == 0 for p in comparison["pairs"])
        assert "secondary_family_holm_adjusted_p" in comparison["reviewed_gap"]
        assert comparison["equivalence_established"] is False


def test_detailed_disagreement_blocks_even_with_same_coarse_label(cohort, tmp_path, fast_statistics):
    candidate = next(iter(cohort["secondary"]))
    paths = dict(cohort["paths"])
    original = grading.read(paths[candidate])
    original["judgment"] = "substantive_error"
    paths[candidate] = tmp_path / "changed-primary.json"
    write_json(paths[candidate], original)
    seal, assignments = tmp_path / "primary.json", tmp_path / "assignments.json"
    results.seal_primary_submissions(cohort["root"], list(paths.values()), seal)
    chosen = results.prepare_secondary_assignments(cohort["root"], seal, assignments)
    secondaries = []
    for row in chosen["assignments"]:
        if row["assignment_kind"] != "primary_recheck":
            continue
        grade = grading.read(paths[row["candidate_id"]])
        grade.update(scoring_role="secondary", agent_id="independent-" + row["candidate_id"])
        if row["candidate_id"] == candidate:
            grade["receiving_point_coverage"][0]["status"] = "missed"
        path = tmp_path / ("secondary-" + row["candidate_id"] + ".json")
        write_json(path, grade)
        secondaries.append(path)
    report = results.aggregate_results(cohort["root"], seal, assignments,
        secondary_submission_paths=secondaries, source_metadata=cohort["metadata"], bootstrap_samples=2)
    affected = next(r for r in report["rows"] if r["candidate_id"] == candidate)
    assert affected["content_judgment"] == "substantive_error"
    assert affected["judgment"] == "indeterminate"
    assert "receiving_point_coverage" in affected["primary_disputes"]
    assert affected["adjudicated_grade"] is None and report["primary_comparisons"] == []


def test_same_agent_and_tampered_primary_are_rejected(cohort, tmp_path):
    candidate, path = next(iter(cohort["secondary"].items()))
    grade = grading.read(path)
    grade["agent_id"] = grading.read(cohort["paths"][candidate])["agent_id"]
    replacement = tmp_path / "same-agent.json"
    write_json(replacement, grade)
    with pytest.raises(ValueError, match="independent assigned agent"):
        _aggregate(cohort, secondary_submission_paths=[replacement])
    seal = grading.read(cohort["seal"])
    seal["records"][candidate]["sha256"] = "0" * 64
    tampered = tmp_path / "tampered.json"
    write_json(tampered, seal)
    with pytest.raises(ValueError, match="sealed primary submission changed"):
        results.aggregate_results(cohort["root"], tampered, source_metadata=cohort["metadata"])


def test_source_cluster_metadata_is_not_invented(cohort):
    incorrect = {c: "one-cluster" for c in cohort["metadata"]}
    with pytest.raises(ValueError, match="22 source clusters"):
        _aggregate(cohort, source_metadata=incorrect)
    incorrect = deepcopy(cohort["metadata"])
    cases = sorted(incorrect)
    # Keep exactly 22 clusters while changing which case shares a cluster.
    incorrect[cases[1]]["source_cluster"], incorrect[cases[4]]["source_cluster"] = (
        incorrect[cases[4]]["source_cluster"], incorrect[cases[1]]["source_cluster"])
    with pytest.raises(ValueError, match="frozen authoritative source clusters"):
        _aggregate(cohort, source_metadata=incorrect)


def test_legacy_findings_disagreement_is_not_hidden_by_equal_coarse_errors():
    grade = {"grading_schema_version": GRADING_SCHEMA_VERSION, "judgment": "substantive_error",
        "claim_units": [], "receiving_point_coverage": [], "reduction_assessments": [],
        "error_records": [], "chain_assessment": None, "findings": [{"severity": "substantive"}]}
    secondary = deepcopy(grade)
    secondary["findings"][0]["severity"] = "minor"
    detail = results._primary_detail(grade, secondary)
    assert detail["adjudicated_grade"] is None
    assert detail["metric_disputes"] == ["findings_classification_disagreement"]
    same = results._primary_detail(grade, deepcopy(grade))
    assert same["adjudicated_grade"] == grade and not same["metric_disputes"]


def test_material_prose_findings_do_not_become_zero_or_double_counted_errors():
    reference = {"supported_excesses": [], "receiving_points": []}
    grade = {"grading_schema_version": GRADING_SCHEMA_VERSION, "judgment": "substantive_error",
        "matched_exposure_ids": [], "claim_units": [], "receiving_point_coverage": [],
        "reduction_assessments": [], "error_records": [], "chain_assessment": None,
        "findings": [{"severity": "substantive", "reason": "Unnormalized material observation."}]}
    metrics = results._assistant_unit_metrics(grade, reference, "substantive_error")
    assert metrics["substantive_errors"] is metrics["functionality_errors"] is metrics["error_categories"] is None
    assert metrics["unnormalized_findings_limitation"]


def test_chain_secondary_is_separate_and_complete(cohort, fast_statistics):
    report = _aggregate(cohort, chain_submission_paths=list(cohort["chain"].values()))
    assert report["chain_status"] == {"planned": 168, "complete": 168, "inference_ready": True}
    assert report["inferential_status"] == "assistant_exploratory_ready"
    chain_rows = [r for r in report["semantic_metrics"]["rows"] if r["method"] != "audit"]
    assert len(chain_rows) == 168 and all(r["chain_completeness"] == r["chain_consistency"] == 1 for r in chain_rows)
    assert all(r["adjudicated_grade"]["chain_assessment"] is None for r in report["rows"])


def test_chain_only_wrapper_does_not_require_or_replace_primary_labels(cohort, tmp_path, fast_statistics):
    candidate, path = next(iter(cohort["chain"].items()))
    combined = grading.read(path)
    wrapper = results.chain_submission_template(cohort["root"], candidate)
    assert not {"judgment", "claim_units", "check_results"}.intersection(wrapper)
    wrapper.update(agent_id="fresh-chain-only-agent", reviewer_id="assistant-chain-only",
                   chain_assessment=combined["chain_assessment"])
    target = tmp_path / "chain-only.json"
    write_json(target, wrapper)
    validated = results.validate_chain_submission(cohort["root"], target)
    assert validated["validated_chain_submission"] == wrapper
    assert not {"judgment", "check_results"}.intersection(validated)
    report = _aggregate(cohort, chain_submission_paths=[target])
    row = next(r for r in report["rows"] if r["candidate_id"] == candidate)
    expected = grading.read(cohort["seal"])["records"][candidate]["workflow_primary_judgment"]
    assert row["chain_assessment_complete"] and row["judgment"] == expected
    assert row["adjudicated_grade"]["chain_assessment"] is None
    assert row["assistant_agents"]["chain_secondary"] == "fresh-chain-only-agent"
    wrapper["reference_correction_proposals"] = [{
        "reason": "Independent source review must resolve this reference interpretation.",
        "source_evidence": wrapper["chain_assessment"]["completeness"][0]["source_evidence"]}]
    write_json(target, wrapper)
    disputed = _aggregate(cohort, chain_submission_paths=[target])
    disputed_row = next(r for r in disputed["rows"] if r["candidate_id"] == candidate)
    assert "chain_source_reference_correction_proposed" in disputed_row["chain_disputes"]
    assert disputed["inferential_status"].startswith("blocked")
    assert not disputed["chain_status"]["inference_ready"]
    wrapper["reference_correction_proposals"] = []
    wrapper["judgment"] = "substantive_error"
    write_json(target, wrapper)
    with pytest.raises(ValueError, match="cannot supply replacement"):
        _aggregate(cohort, chain_submission_paths=[target])


def test_chain_dispute_blocks_chain_without_changing_primary(cohort, tmp_path, fast_statistics):
    candidate, path = next(iter(cohort["chain"].items()))
    grade = grading.read(path)
    grade["chain_assessment"]["completeness"][0]["status"] = "disputed"
    target = tmp_path / "chain-dispute.json"
    write_json(target, grade)
    report = _aggregate(cohort, chain_submission_paths=[target])
    row = next(r for r in report["rows"] if r["candidate_id"] == candidate)
    assert report["inferential_status"] == "assistant_exploratory_ready"
    assert row["chain_disputes"] == ["chain_metric_dispute"]
    assert row["chain_assessment"] is None


def test_source_dispute_cannot_be_converted_to_a_definite_error(cohort, tmp_path, fast_statistics):
    candidate, path = next(iter(cohort["secondary"].items()))
    grade = grading.read(path)
    grade.update(judgment="indeterminate", reference_correction_proposals=[{
        "reason": "The reference interpretation requires independent source review.",
        "source_evidence": grade["check_results"][0]["source_evidence"]}])
    target = tmp_path / "source-dispute.json"
    write_json(target, grade)
    secondaries = [target if c == candidate else p for c, p in cohort["secondary"].items()]
    report = _aggregate(cohort, secondary_submission_paths=secondaries)
    row = next(r for r in report["rows"] if r["candidate_id"] == candidate)
    assert row["judgment"] == "indeterminate"
    assert "secondary_source_reference_correction_proposed" in row["primary_disputes"]
    assert report["primary_comparisons"] == [] and report["bounds"]["unknown"] == 1


def test_practical_advantage_is_symmetric_with_a_holm_family():
    comparisons = [
        {"methods": ["skillflow", "audit"], "difference": -.2,
         "simultaneous_97_5_percent_interval": [-.3, -.1], "two_sided_cluster_sign_flip_p": .001},
        {"methods": ["skillflow", "chain"], "difference": .2,
         "simultaneous_97_5_percent_interval": [.1, .3], "two_sided_cluster_sign_flip_p": .002}]
    results._adjust(comparisons)
    assert [r["practical_advantage_method"] for r in comparisons] == ["audit", "skillflow"]
    assert [r["holm_adjusted_p"] for r in comparisons] == [.002, .002]


def test_resource_unknowns_and_quality_gate_remain_truthful(cohort, fast_statistics):
    report = _aggregate(cohort)
    resources = report["resources"]
    assert len(resources["comparisons"]) == 20
    assert resources["unreported_workflows"] == 264
    assert all(r["efficiency_supported"] is False for r in resources["comparisons"])
    assert sum(r["status"] == "actual_human_work_unobserved" for r in resources["comparisons"]) == 4
    assert all(r["directional_claim_family"] == 20 and r["one_sided_tail"] == .05 / 40 for r in resources["comparisons"])


def test_costs_from_a_different_or_unbound_cohort_are_rejected(cohort, fast_statistics):
    for supplied in ({"workflows": [{}]}, {"output_freeze_sha256": "0" * 64, "workflows": []}):
        with pytest.raises(ValueError, match="same closed output cohort"):
            _aggregate(cohort, costs=supplied)


def test_global_primary_dispute_blocks_efficiency_even_for_complete_main_pairs():
    cases = {"case-" + str(i): {"source_cluster": "cluster-" + str(i // 2 if i < 4 else i - 2)} for i in range(24)}
    rows, workflows, enhanced = [], [], []
    for case in cases:
        for method in ("skillflow", "audit", "chain"):
            for repeat in (1, 2, 3):
                rows.append({"workflow_id": f"{case}-{method}-{repeat}", "case_id": case,
                    "source_cluster": cases[case]["source_cluster"], "method": method, "kind": "main", "repeat": repeat,
                    "assistant_adjudication_complete": True, "judgment": "satisfies_reference"})
        for method in ("audit", "chain"):
            rows.append({"workflow_id": f"{case}-{method}-review", "case_id": case,
                "source_cluster": cases[case]["source_cluster"], "method": method, "kind": "review", "repeat": 1,
                "assistant_adjudication_complete": True, "judgment": "satisfies_reference"})
    rows[-1].update(assistant_adjudication_complete=False, judgment="indeterminate")
    for row in rows:
        workflows.append({"workflow_id": row["workflow_id"], "reported_total_tokens": 10, "workflow_elapsed_seconds": 2})
        if row["kind"] == "review":
            enhanced.append({"workflow_id": row["workflow_id"], "reported_total_tokens": 20, "additive_workflow_seconds": 4})
    supplied = {"output_freeze_sha256": "synthetic-output-cohort", "workflows": workflows,
                "enhanced_original_plus_review_cost": enhanced}
    resource = results._resource_comparisons(rows, cases, supplied, 17, "synthetic-output-cohort")
    model_claims = [r for r in resource["comparisons"] if r["resource"] != "all_planned_timed_review_active_seconds"]
    assert len(model_claims) == 16
    assert all(r["status"] == "blocked_global_unresolved_primary_quality" and not r["efficiency_supported"] for r in model_claims)
    main = next(r for r in model_claims if r["methods"] == ["skillflow", "audit"] and r["resource"] == "reported_total_tokens")
    assert main["descriptive_resource_ratio"] == 1
    assert len(main["case_cost_pairs"]) == 24


def test_external_cost_ratio_uses_original_plus_review_and_case_means(cohort, fast_statistics):
    workflows, enhanced = [], []
    for row in cohort["mapping"]:
        workflows.append({"workflow_id": row["workflow_id"], "usage": {"totals": {"total_tokens": 10}},
                          "workflow_elapsed_seconds": 2})
        if row["kind"] == "review":
            enhanced.append({"workflow_id": row["workflow_id"], "usage_original_plus_review": {"totals": {"total_tokens": 20}},
                             "additive_workflow_seconds": 4})
    cohort_hash = grading.read(cohort["root"] / "packet-freeze.json")["source_output_freeze_sha256"]
    report = _aggregate(cohort, costs={"output_freeze_sha256": cohort_hash,
        "workflows": workflows, "enhanced_original_plus_review_cost": enhanced})
    native_reviewed = next(r for r in report["resources"]["comparisons"]
        if r["methods"] == ["skillflow_r1", "audit+fixed_review_r1"] and r["resource"] == "reported_total_tokens")
    assert native_reviewed["resource_ratio"] == .5
    assert native_reviewed["status"] == "degenerate_quality_interval_noninferiority_unestablished"
    assert not native_reviewed["efficiency_supported"]


def test_stability_and_json_csv_report_seal(cohort, tmp_path, fast_statistics):
    report = _aggregate(cohort)
    stable = next(r for r in report["stability"]["rows"] if r["case_id"] == "synthetic-00" and r["method"] == "skillflow")
    assert stable["matched_reference_unit_jaccard"] == stable["unsupported_claim_jaccard"] == 1
    assert stable["all_three_satisfy"] is False
    assert report["semantic_metrics"]["groups"]["audit/main"]["case_averaged"]["precision"] is None
    target = tmp_path / "report"
    seal = results.write_reports(report, target)
    assert set(seal["files"]) == {"results.json", "outcomes.csv", "case-results.csv", "errors.csv", "disputes.csv", "stability.csv", "resources.csv"}
    assert all(sha256(target / name) == digest for name, digest in seal["files"].items())
    with pytest.raises(ValueError, match="fresh report directory"):
        results.write_reports(report, target)
