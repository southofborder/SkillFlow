"""Offline validation of review bookkeeping, never synthetic semantic approval."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest


BASE = Path(__file__).resolve().parents[2] / "experiments/semantics_baseline"
SPEC = importlib.util.spec_from_file_location("semantics_results_review", BASE / "tools/review_results.py")
reviewer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reviewer)
CORPUS = reviewer.read(BASE / "frozen/corpus/corpus.json")
SAMPLES = CORPUS["samples"]


def synthetic_analysis():
    return {
        "status": "complete", "diagnostics": [],
        "cfg": {
            "constraints": ["synthetic global constraint"],
            "blocks": {
                "block_001": {
                    "constraints": ["synthetic block constraint"],
                    "instructions": [{
                        "id": "ir_001", "constraints": ["synthetic instruction constraint"],
                        "metadata": {"script_content": "print('synthetic script; never executed')"},
                    }],
                },
            },
            "edges": [{"source": "block_001", "target": "block_001"}],
        },
    }


def add_trials(run, sample, *, status="complete"):
    trials = []
    for repetition in (1, 2, 3):
        artifacts = f"trials/{sample['id']}/sol-max/{repetition}"
        record = {
            "case": sample["id"], "variant": "sol-max", "repetition": repetition,
            "split": sample["split"], "artifacts": artifacts, "status": status,
        }
        reviewer.write(run / artifacts / "record.json", record)
        if status == "complete":
            reviewer.write(run / artifacts / "analysis.json", synthetic_analysis())
        trials.append(record)
    return trials


def synthetic_review(run, sample, *, verdict="preserved"):
    trials = reviewer.trials_for(run, sample["id"])
    annotation = reviewer.read(BASE / "frozen/corpus" / sample["annotation_path"])
    return {
        "schema_version": 1, "sample_id": sample["id"], "reviewer": "offline test fixture",
        "run_comparison": "Synthetic fixture only; this is not an actual corpus review.",
        "overall": "Only review bookkeeping is being tested.",
        "analysis_sha256": {
            str(trial["repetition"]): reviewer.sha(run / trial["artifacts"] / "analysis.json")
            for trial in trials
        },
        "record_sha256": {
            str(trial["repetition"]): reviewer.sha(run / trial["artifacts"] / "record.json")
            for trial in trials
        },
        "facts": [{
            "fact_id": fact["id"],
            "assessments": [{
                "repetition": repetition, "verdict": verdict,
                "reason": "测试用判定，只验证复核文件格式，不表示实际语义通过。",
                "references": ["block_001", "ir_001", "edge_001"] if verdict == "preserved" else ["diagnostics"],
            } for repetition in (1, 2, 3)],
        } for fact in annotation["facts"]],
    }


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Review validation tests must never send a network request")

    monkeypatch.setattr("urllib.request.urlopen", forbidden)


@pytest.fixture
def case(tmp_path):
    sample = SAMPLES[0]
    run = tmp_path / "run"
    reviewer.write(run / "report.json", {"trials": add_trials(run, sample)})
    return run, sample, synthetic_review(run, sample)


def test_all_297_frozen_facts_require_891_assessments(tmp_path):
    run = tmp_path / "run"
    trials = [trial for sample in SAMPLES for trial in add_trials(run, sample)]
    reviewer.write(run / "report.json", {"trials": trials})
    counts = []
    for sample in SAMPLES:
        review = synthetic_review(run, sample)
        count = reviewer.validate_review(review, sample, run, BASE)
        assert sum(count.values()) == len(review["facts"]) * 3
        counts.append(len(review["facts"]))
    assert len(SAMPLES) == 30 and len(trials) == 90
    assert sum(counts) == 297
    assert sum(counts) * 3 == 891


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "invented"])
def test_fact_inventory_must_match_frozen_annotation_exactly(case, mutation):
    run, sample, review = case
    if mutation == "missing":
        review["facts"].pop()
    elif mutation == "duplicate":
        review["facts"][-1] = deepcopy(review["facts"][0])
    else:
        review["facts"][-1]["fact_id"] = "N01-F999"
    with pytest.raises(ValueError, match="every frozen fact exactly once"):
        reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "out_of_range"])
def test_each_fact_requires_exactly_three_distinct_repetitions(case, mutation):
    run, sample, review = case
    assessments = review["facts"][0]["assessments"]
    if mutation == "missing":
        assessments.pop()
    elif mutation == "duplicate":
        assessments[-1] = deepcopy(assessments[0])
    else:
        assessments[-1]["repetition"] = 4
    with pytest.raises(ValueError, match="Three assessments required"):
        reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("artifact", ["analysis", "record"])
def test_review_of_old_artifact_hash_is_rejected(case, artifact):
    run, sample, review = case
    trial = reviewer.trials_for(run, sample["id"])[0]
    path = run / trial["artifacts"] / f"{artifact}.json"
    value = reviewer.read(path)
    value["changed_after_review"] = True
    reviewer.write(path, value)
    with pytest.raises(ValueError, match=f"Stale {artifact} review"):
        reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("reference", ["block_999", "ir_999", "edge_999", "block_999.constraints", "ir_999.constraints"])
def test_invented_cfg_references_are_rejected(case, reference):
    run, sample, review = case
    review["facts"][0]["assessments"][0]["references"] = [reference]
    with pytest.raises(ValueError, match="Unknown CFG reference"):
        reviewer.validate_review(review, sample, run, BASE)


def test_existing_block_operation_edge_and_constraint_references_are_accepted(case):
    run, sample, review = case
    review["facts"][0]["assessments"][0]["references"] = [
        "block_001", "ir_001", "edge_001", "skill.constraints",
        "block_001.constraints", "ir_001.constraints", "diagnostics",
    ]
    assert reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("status", ["degraded", "error", "uncertain"])
def test_failed_or_uncertain_extraction_cannot_be_marked_preserved(tmp_path, status):
    run, sample = tmp_path / "run", SAMPLES[0]
    reviewer.write(run / "report.json", {"trials": add_trials(run, sample, status=status)})
    review = synthetic_review(run, sample, verdict="unassessable")
    review["facts"][0]["assessments"][0]["verdict"] = "preserved"
    with pytest.raises(ValueError, match="No accepted CFG"):
        reviewer.validate_review(review, sample, run, BASE)


def test_failed_extraction_allows_only_explicit_unassessable_reason(tmp_path):
    run, sample = tmp_path / "run", SAMPLES[0]
    reviewer.write(run / "report.json", {"trials": add_trials(run, sample, status="error")})
    review = synthetic_review(run, sample, verdict="unassessable")
    counts = reviewer.validate_review(review, sample, run, BASE)
    assert counts == {"unassessable": len(review["facts"]) * 3}


@pytest.mark.parametrize("reason", ["", "   ", "\n\t", None, 12, []])
def test_manual_reason_cannot_be_empty_or_whitespace(case, reason):
    run, sample, review = case
    review["facts"][0]["assessments"][0]["reason"] = reason
    with pytest.raises(ValueError, match="Missing manual verdict or rationale"):
        reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("status", ["not_run", "running", "interrupted"])
def test_unfinished_trials_cannot_be_exported_or_reviewed(case, status):
    run, sample, review = case
    report = reviewer.read(run / "report.json")
    report["trials"][0]["status"] = status
    reviewer.write(run / "report.json", report)
    with pytest.raises(ValueError, match="Three terminal trials"):
        reviewer.packet_for(run, sample, BASE)
    with pytest.raises(ValueError, match="Unfinished trial"):
        reviewer.validate_review(review, sample, run, BASE)


def test_packet_labels_edges_and_omits_script_text_without_mutating_analysis(case):
    run, sample, _ = case
    trial = reviewer.trials_for(run, sample["id"])[0]
    path = run / trial["artifacts"] / "analysis.json"
    before = path.read_bytes()
    packet = reviewer.packet_for(run, sample, BASE)
    result = packet["runs"][0]
    assert result["analysis_sha256"] == reviewer.sha(path)
    assert result["record_sha256"] == reviewer.sha(run / trial["artifacts"] / "record.json")
    assert result["analysis"]["cfg"]["edges"][0]["review_edge_id"] == "edge_001"
    content = result["analysis"]["cfg"]["blocks"]["block_001"]["instructions"][0]["metadata"]["script_content"]
    assert content["omitted_from_packet_only"] is True and content["characters"] > 0
    assert path.read_bytes() == before
    assert packet["source_directory"] == str((BASE / "frozen/corpus" / sample["package_path"]).resolve())
    assert packet["annotation"]["sample_id"] == sample["id"]


def test_missing_or_duplicate_trial_repetitions_are_rejected(case):
    run, sample, _ = case
    report = reviewer.read(run / "report.json")
    report["trials"][2]["repetition"] = 1
    reviewer.write(run / "report.json", report)
    with pytest.raises(ValueError, match="exactly three trials"):
        reviewer.trials_for(run, sample["id"])


@pytest.mark.parametrize("field", ["reviewer", "run_comparison", "overall"])
@pytest.mark.parametrize("value", ["", " \n\t", None, 12])
def test_manual_review_metadata_requires_nonblank_text(case, field, value):
    run, sample, review = case
    review[field] = value
    with pytest.raises(ValueError, match="Review requires"):
        reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("mutation", ["missing_analysis", "absent_cfg", "empty_blocks", "degraded_analysis"])
def test_complete_record_does_not_substitute_for_an_accepted_cfg(case, mutation):
    run, sample, review = case
    trial = reviewer.trials_for(run, sample["id"])[0]
    path = run / trial["artifacts"] / "analysis.json"
    analysis = reviewer.read(path)
    if mutation == "missing_analysis":
        path.unlink()
    else:
        if mutation == "absent_cfg":
            analysis["cfg"] = None
        elif mutation == "empty_blocks":
            analysis["cfg"]["blocks"] = {}
        else:
            analysis["status"] = "degraded"
        reviewer.write(path, analysis)
    review["analysis_sha256"]["1"] = reviewer.sha(path)
    review["facts"][0]["assessments"][0]["references"] = ["diagnostics"]
    with pytest.raises(ValueError, match="No accepted CFG"):
        reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("references", [[], ["diagnostics"]])
def test_preserved_behavior_requires_an_actual_cfg_reference(case, references):
    run, sample, review = case
    review["facts"][0]["assessments"][0]["references"] = references
    with pytest.raises(ValueError, match="actual CFG evidence"):
        reviewer.validate_review(review, sample, run, BASE)


def test_missing_fact_may_have_no_local_reference(case):
    run, sample, review = case
    review["facts"][0]["assessments"][0].update(verdict="missing", references=[])
    assert reviewer.validate_review(review, sample, run, BASE)["missing"] == 1


def test_negative_fact_may_cite_diagnostics_or_a_covering_block(case):
    run, sample, review = case
    annotation = reviewer.read(BASE / "frozen/corpus" / sample["annotation_path"])
    negative = next(fact["id"] for fact in annotation["facts"] if fact["kind"] == "must_not_infer")
    fact = next(fact for fact in review["facts"] if fact["fact_id"] == negative)
    fact["assessments"][0]["references"] = ["diagnostics"]
    assert reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("sample_id", [f"D{number:02d}" for number in range(1, 7)])
def test_frozen_unresolved_constraint_may_be_preserved_in_diagnostics(tmp_path, sample_id):
    sample = next(sample for sample in SAMPLES if sample["id"] == sample_id)
    run = tmp_path / "run"
    trials = add_trials(run, sample)
    reviewer.write(run / "report.json", {"trials": trials})
    for trial in trials:
        path = run / trial["artifacts"] / "analysis.json"
        analysis = reviewer.read(path)
        analysis["diagnostics"] = ["“必要时保留原顺序”的条件与作用对象不明确，未提升为全局规则。"]
        reviewer.write(path, analysis)
    review = synthetic_review(run, sample)
    annotation = reviewer.read(BASE / "frozen/corpus" / sample["annotation_path"])
    frozen_fact = next(fact for fact in annotation["facts"] if fact["id"] == f"{sample_id}-F10")
    assert frozen_fact["kind"] == "constraint" and frozen_fact["scope"]["level"] == "unresolved"
    fact = next(fact for fact in review["facts"] if fact["fact_id"] == frozen_fact["id"])
    for assessment in fact["assessments"]:
        assessment["references"] = ["diagnostics"]
    assert reviewer.validate_review(review, sample, run, BASE)["preserved"] == len(review["facts"]) * 3


def test_unresolved_constraint_requires_nonempty_diagnostics_for_that_repetition(tmp_path):
    sample = next(sample for sample in SAMPLES if sample["id"] == "D01")
    run = tmp_path / "run"
    trials = add_trials(run, sample)
    reviewer.write(run / "report.json", {"trials": trials})
    path = run / trials[0]["artifacts"] / "analysis.json"
    analysis = reviewer.read(path)
    analysis["diagnostics"] = ["原顺序的适用范围未知。"]
    reviewer.write(path, analysis)
    review = synthetic_review(run, sample)
    fact = next(fact for fact in review["facts"] if fact["fact_id"] == "D01-F10")
    for assessment in fact["assessments"]:
        assessment["references"] = ["diagnostics"]
    # Repetition 1's diagnostic cannot provide evidence for repetition 2.
    with pytest.raises(ValueError, match="actual CFG evidence: D01-F10"):
        reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("sample_id,fact_id", [
    ("N01", "N01-F01"),  # behavior
    ("N01", "N01-F02"),  # condition
    ("N01", "N01-F05"),  # data_flow
    ("N01", "N01-F03"),  # block-scoped constraint
    ("N01", "N01-F07"),  # skill-scoped constraint
    ("D01", "D01-F03"),  # operation-scoped constraint
])
def test_known_scope_or_executable_fact_still_requires_cfg_evidence(tmp_path, sample_id, fact_id):
    sample = next(sample for sample in SAMPLES if sample["id"] == sample_id)
    run = tmp_path / "run"
    trials = add_trials(run, sample)
    reviewer.write(run / "report.json", {"trials": trials})
    path = run / trials[0]["artifacts"] / "analysis.json"
    analysis = reviewer.read(path)
    analysis["diagnostics"] = ["Synthetic diagnostic does not implement this fact."]
    reviewer.write(path, analysis)
    review = synthetic_review(run, sample)
    fact = next(fact for fact in review["facts"] if fact["fact_id"] == fact_id)
    fact["assessments"][0]["references"] = ["diagnostics"]
    with pytest.raises(ValueError, match="actual CFG evidence"):
        reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("kind", ["behavior", "condition", "data_flow"])
def test_unresolved_scope_alone_does_not_relax_executable_fact_evidence(case, tmp_path, kind):
    run, sample, review = case
    # Only a temporary annotation fixture changes; the frozen corpus is never written.
    fixture_base = tmp_path / "synthetic_annotation"
    annotation = reviewer.read(BASE / "frozen/corpus" / sample["annotation_path"])
    annotation["facts"][0].update(kind=kind, scope={"level": "unresolved"})
    reviewer.write(fixture_base / "frozen/corpus" / sample["annotation_path"], annotation)
    trial = reviewer.trials_for(run, sample["id"])[0]
    path = run / trial["artifacts"] / "analysis.json"
    analysis = reviewer.read(path)
    analysis["diagnostics"] = ["Synthetic unresolved scope."]
    reviewer.write(path, analysis)
    review["analysis_sha256"]["1"] = reviewer.sha(path)
    review["facts"][0]["assessments"][0]["references"] = ["diagnostics"]
    with pytest.raises(ValueError, match="actual CFG evidence"):
        reviewer.validate_review(review, sample, run, fixture_base)


@pytest.mark.parametrize("status", ["degraded", "error", "uncertain"])
def test_unresolved_constraint_does_not_make_failed_extraction_assessable(tmp_path, status):
    run = tmp_path / "run"
    sample = next(sample for sample in SAMPLES if sample["id"] == "D01")
    reviewer.write(run / "report.json", {"trials": add_trials(run, sample, status=status)})
    review = synthetic_review(run, sample, verdict="unassessable")
    fact = next(fact for fact in review["facts"] if fact["fact_id"] == "D01-F10")
    fact["assessments"][0]["verdict"] = "preserved"
    with pytest.raises(ValueError, match="No accepted CFG"):
        reviewer.validate_review(review, sample, run, BASE)


def test_additional_finding_refs_are_checked_for_each_named_repetition(case):
    run, sample, review = case
    review["additional_findings"] = [{
        "repetitions": [1, 2, 3], "reason": "Synthetic independent observation.",
        "references": ["edge_001"],
    }]
    assert reviewer.validate_review(review, sample, run, BASE)
    trial = reviewer.trials_for(run, sample["id"])[1]
    path = run / trial["artifacts"] / "analysis.json"
    analysis = reviewer.read(path)
    analysis["cfg"]["edges"] = []
    reviewer.write(path, analysis)
    review["analysis_sha256"]["2"] = reviewer.sha(path)
    for fact in review["facts"]:
        fact["assessments"][1]["references"] = ["block_001"]
    with pytest.raises(ValueError, match="Unknown CFG reference: additional finding 1 repeat 2"):
        reviewer.validate_review(review, sample, run, BASE)


@pytest.mark.parametrize("repetitions", [[], [1, 1], [4], [True], "1"])
def test_additional_finding_requires_valid_repetitions(case, repetitions):
    run, sample, review = case
    review["additional_findings"] = [{"repetitions": repetitions, "reason": "Synthetic observation."}]
    with pytest.raises(ValueError, match="valid repetitions"):
        reviewer.validate_review(review, sample, run, BASE)


def test_additional_finding_may_report_an_omission_without_a_reference(case):
    run, sample, review = case
    review["additional_findings"] = [{"repetitions": [1], "reason": "Synthetic omission observation.", "references": []}]
    assert reviewer.validate_review(review, sample, run, BASE)
