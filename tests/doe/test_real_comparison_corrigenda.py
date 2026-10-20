"""Fictional human-confirmed grading epochs; zero target/model calls."""
from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from tools.doe.real_comparison.assessment import import_human_attestation, finalize_human_references
from tools.doe.real_comparison.corrigenda import (prepare_corrigendum, import_corrigendum_confirmation,
    activate_corrigendum, resolve_grading_run, assert_active_grading_epoch, grading_epoch_lineage, lineage_human_cost)
from tools.doe.real_comparison.execution import prepare_schedule, run_workflow
from tools.doe.real_comparison.protocol import sha256, write_json, utc_now
from tools.doe.real_comparison.results import freeze_outputs, aggregate_scores
from tools.doe.real_comparison.review import (prepare_scoring_assignments, prepare_review_assignments,
                                             import_timed_submission, import_timed_adjudication)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_preformal_lineage_reports_open_targets_without_enabling_a_correction(tmp_path):
    lineage = grading_epoch_lineage(tmp_path)
    assert lineage["current_epoch_id"] == "original"
    assert lineage["target_generation"] == "not_closed"
    assert lineage["target_output_freeze_sha256"] is None
    assert lineage["epochs"] == [{"epoch_id": "original", "run_dir": str(tmp_path.resolve()), "target_generation": "not_closed"}]
    assert lineage["new_target_requests"] == 0
    with pytest.raises((ValueError, FileNotFoundError)):
        prepare_corrigendum(tmp_path, case_id="real-001", new_reference_path=tmp_path / "absent.json", reason="No closed cohort exists.")
    assert not (tmp_path / "corrigenda").exists()


def test_applicable_grading_contract_and_supplement_rules_are_protected(tmp_path, monkeypatch):
    from tools.doe.real_comparison import corrigenda
    for name in ("grading-contract.json", "evaluation-rules-supplement.md", "evaluation-rules-freeze.json"):
        (tmp_path / name).write_text("Exact grading contract bytes.\n", encoding="utf-8")
    monkeypatch.setattr(corrigenda, "_target_inventory", lambda run: {})
    names = corrigenda._grading_configuration(tmp_path)
    assert names == ["evaluation-rules-freeze.json", "evaluation-rules-supplement.md", "grading-contract.json"]
    protected = corrigenda._protected_inventory(tmp_path)
    assert set(names).issubset(protected)
    assert all(protected[name] == sha256(tmp_path / name) for name in names)


@pytest.mark.parametrize("command,api_name,arguments", [
    ("prepare-corrigendum", "prepare_corrigendum", ["--case-id", "real-001", "--submission", "new.json", "--reason", "Physical source correction"]),
    ("import-corrigendum", "import_corrigendum_confirmation", ["--corrigendum-id", "corr-test", "--submission", "confirmation.json"]),
    ("activate-corrigendum", "activate_corrigendum", ["--corrigendum-id", "corr-test"]),
])
def test_corrigendum_cli_routes_only_explicit_submissions(tmp_path, monkeypatch, capsys, command, api_name, arguments):
    from tools.doe.real_comparison import __main__ as cli, corrigenda
    calls = []
    def inert(*args, **kwargs):
        calls.append((args, kwargs))
        return {"state": "fictional_cli_route", "model_calls": 0}
    monkeypatch.setattr(corrigenda, api_name, inert)
    cli.main([command, "--run-dir", str(tmp_path), *arguments])
    assert json.loads(capsys.readouterr().out)["model_calls"] == 0
    assert len(calls) == 1 and calls[0][0][0] == tmp_path
    if command == "prepare-corrigendum":
        assert calls[0][1] == {"case_id": "real-001", "new_reference_path": "new.json", "reason": "Physical source correction"}
    else:
        assert calls[0][0][1] == "corr-test"


def test_scoring_packets_resolve_current_epoch_and_bind_its_identity(tmp_path, monkeypatch):
    from tools.doe.real_comparison import corrigenda, results, semantic_metrics
    from tools.doe.real_comparison.review import prepare_scoring_packets
    root, active = tmp_path / "original", tmp_path / "active"
    monkeypatch.setattr(corrigenda, "resolve_grading_run", lambda run: active)
    monkeypatch.setattr(corrigenda, "assert_active_grading_epoch", lambda run: {"epoch_id": "epoch-fixture"})
    monkeypatch.setattr(results, "verify_output_freeze", lambda run: {})
    monkeypatch.setattr(semantic_metrics, "grading_template", lambda reference, method: {})
    write_json(active / "review/private-scoring-map.json", {"assignments": [{"workflow_id": "real-001_audit_r1", "case_id": "real-001", "candidate_id": "anonymous", "primary_reviewer_id": "H1", "method": "audit"}]})
    write_json(active / "workflows/real-001_audit_r1/result.json", {"answer_sha256": "fixture-answer-hash"})
    source = active / "cases/real-001/source-bundle.txt"
    source.parent.mkdir(parents=True)
    source.write_text("Genuine source quotation: 原文.\n", encoding="utf-8")
    write_json(active / "references/real-001.json", {"mandatory_checks": [{"id": "C1"}]})
    prepared = prepare_scoring_packets(root)
    template = read(active / "review/scoring/anonymous/grade.template.json")
    assert prepared == {"scoring_packets": 1, "model_calls": 0}
    assert template["grading_epoch_id"] == "epoch-fixture"
    assert template["judgment"] == "pending_human" and template["human_verified"] is False
    assert not root.exists()


@pytest.fixture(scope="module")
def base_study(tmp_path_factory):
    run = tmp_path_factory.mktemp("fictional-corrigendum-original")
    people = [{"reviewer_id": person, "human": True, "role": "reference_verifier", "declared_at": "2026-10-20T00:00:00+00:00"} for person in ("H1", "H2")]
    people += [{"reviewer_id": person, "human": True, "role": "timed_reviewer"} for person in ("R1", "R2", "R3")]
    write_json(run / "human-roster.json", {"fixture_only": True, "reviewers": people})
    cases = []
    for i in range(30):
        case_id = f"real-{i+1:03d}"
        case = {"case_id": case_id, "source_sha256": "fixture-source-" + case_id, "source_cluster": "cluster-" + str(i // 3)}
        cases.append(case)
        source = run / "cases" / case_id / "source/SKILL.md"
        source.parent.mkdir(parents=True)
        source.write_text("Return the approved summary.\nThe ordinary caller is unspecified.\n", encoding="utf-8")
        (source.parent.parent / "source-bundle.txt").write_bytes(source.read_bytes())
        evidence = [{"path": "SKILL.md", "start_line": 2, "end_line": 2, "quote": "The ordinary caller is unspecified."}]
        reference = {"case_id": case_id, "source_sha256": case["source_sha256"], "state": "approved",
                     "coverage_state": "complete_for_human_verification", "purpose_basis": "skill_declared_purpose_only", "user_request": None,
                     "declared_purpose": [{"id": "P1", "evidence": evidence}], "required_behavior": [],
                     "receiving_points": [{"id": "B1", "evidence": evidence}], "necessary_sensitive_uses": [],
                     "supported_excesses": [], "unknowns": [], "preservation_checks": [], "mandatory_checks": [{"id": "M1", "evidence": evidence}]}
        path = run / "references" / (case_id + ".json")
        write_json(path, reference)
        for person in ("H1", "H2"):
            record = {"case_id": case_id, "reviewer_id": person, "human": True, "approved": True, "role": "reference_verifier",
                      "source_sha256": case["source_sha256"], "reference_sha256": sha256(path),
                      "attestation_id": "fictional-original-" + case_id + person, "attested_at": utc_now(),
                      "confirmation": "I personally verified this source reference."}
            submission = run / "fictional-submissions" / (case_id + person + ".json")
            write_json(submission, record)
            import_human_attestation(run, submission)
    write_json(run / "selection.json", {"selected": cases[:24], "reserves": cases[24:]})
    finalize_human_references(run, cases)
    schedule = prepare_schedule(run, cases[:24])
    prepare_scoring_assignments(run)
    assignments = prepare_review_assignments(run, [c["case_id"] for c in cases[:24]])
    for item in schedule["main"] + schedule["reviews"]:
        write_json(run / "workflows" / item["workflow_id"] / "result.json", {"workflow_id": item["workflow_id"], "status": "failed", "answer_sha256": None})
    freeze_outputs(run)
    aggregate_scores(run)
    assignment = assignments[0]
    record = {"assignment_id": assignment["assignment_id"], "case_id": assignment["case_id"], "reviewer_id": assignment["reviewer_id"],
              "human": True, "status": "finished", "active_seconds": 70, "started_at": utc_now(), "finished_at": utc_now(),
              "corrected_conclusion": "The caller remains unspecified.", "final_quality": "pending_independent_adjudication",
              "attestation": "I personally performed this timed review without consulting this case reference or another method answer."}
    submission = run / "fictional-timed.json"
    write_json(submission, record)
    imported = import_timed_submission(run, submission)
    judgment = {"assignment_id": assignment["assignment_id"], "reviewer_id": "H1", "human_verified": True,
                "submission_sha256": imported["sha256"], "quality": "correct", "evidence": ["SKILL.md:2"],
                "reason": "Fictional independent source judgment.", "attested_at": utc_now(), "active_seconds": 4}
    path = run / "fictional-quality.json"
    write_json(path, judgment)
    import_timed_adjudication(run, path)
    return run


@pytest.fixture
def study(base_study, tmp_path):
    target = tmp_path / "logical-study"
    shutil.copytree(base_study, target)
    return target


def proposal(run, *, revision=1):
    parent = resolve_grading_run(run)
    reference = read(parent / "references/real-001.json")
    reference["unknowns"] = [{"id": "U1", "reason": f"Source recipient uncertainty clarification version {revision}.",
                              "evidence": deepcopy(reference["receiving_points"][0]["evidence"])}]
    path = run / f"proposed-{revision}.json"
    write_json(path, reference)
    return prepare_corrigendum(run, case_id="real-001", new_reference_path=path,
                               reason=f"Clarify the physical source's unresolved ordinary caller, version {revision}.")


def confirm(run, request, person):
    submission = {"case_id": request["case_id"], "reviewer_id": person, "human": True, "approved": True,
                  "role": "reference_verifier", "source_sha256": request["source_sha256"],
                  "reference_sha256": request["new_reference_sha256"], "attestation_id": "fictional-" + request["corrigendum_id"] + person,
                  "attested_at": utc_now(), "confirmation": "I personally verified this source reference."}
    path = run / "fictional-new-confirmations" / (request["corrigendum_id"] + person + ".json")
    write_json(path, submission)
    return import_corrigendum_confirmation(run, request["corrigendum_id"], path)


def original_hashes(run):
    return {p.relative_to(run).as_posix(): sha256(p) for folder in ("references", "workflows", "grades", "review/submissions", "review/adjudications")
            for p in (run / folder).rglob("*") if p.is_file()} | {name: sha256(run / name) for name in ("reference-freeze.json", "references.json", "scores.json", "output-freeze.json")}


def test_prepared_correction_preserves_originals_and_cannot_activate_or_regenerate(study):
    before = original_hashes(study)
    request = proposal(study)
    child = study / request["workspace"]
    assert request["state"] == "prepared_pending_two_actual_human_confirmations"
    assert resolve_grading_run(study) == study.resolve()
    with pytest.raises(ValueError, match="Two distinct human|Two frozen personal"):
        activate_corrigendum(study, request["corrigendum_id"])
    with pytest.raises(ValueError, match="activated current"):
        assert_active_grading_epoch(child)
    with pytest.raises(Exception, match="regeneration is forbidden"):
        run_workflow(child, "unused", source_path="unused")
    assert read(child / "grades/import-manifest.json")["records"] == []
    assert read(child / "review/adjudications/import-manifest.json")["records"] == []
    assert len(read(child / "review/import-manifest.json")["records"]) == 1
    assert original_hashes(study) == before


def test_two_confirmations_activate_all264_pending_and_retain_same_target_bytes(study):
    before = original_hashes(study)
    request = proposal(study)
    confirm(study, request, "H1")
    with pytest.raises(ValueError, match="Two distinct human"):
        activate_corrigendum(study, request["corrigendum_id"])
    confirm(study, request, "H2")
    activation = activate_corrigendum(study, request["corrigendum_id"])
    child = resolve_grading_run(study)
    scores = read(child / "scores.json")
    assert activation["new_target_requests"] == 0 and activation["new_timed_reviews"] == 0
    assert scores["planned_results"] == 264 and scores["complete"] is False
    assert all(row["judgment"] == "unassessed" for row in scores["rows"])
    assert scores["primary_comparisons"] == []
    assert sha256(child / "output-freeze.json") == sha256(study / "output-freeze.json")
    assert original_hashes(study) == before
    assert assert_active_grading_epoch(child)["epoch_id"] == request["epoch_id"]
    history = lineage_human_cost(study)
    assert history["unique_observed_human_work"]["source_reference_work"]["unique_records"] == 62
    assert history["unique_observed_human_work"]["practical_timed_review"]["unique_records"] == 1
    assert history["epochs"][1]["copied_records_not_counted_again"]["source_reference_work"] == 58
    assert history["epochs"][1]["incremental_human_work"]["practical_timed_review"]["new_records"] == 0


def test_multiple_corrections_use_current_reference_not_original_and_never_repeat_timed_reading(study):
    first = proposal(study, revision=1)
    confirm(study, first, "H1"); confirm(study, first, "H2")
    activate_corrigendum(study, first["corrigendum_id"])
    prior_child = resolve_grading_run(study)
    second = proposal(study, revision=2)
    assert second["old_reference_sha256"] == first["new_reference_sha256"]
    assert second["parent_grading_run"] == str(prior_child)
    confirm(study, second, "H1"); confirm(study, second, "H2")
    activate_corrigendum(study, second["corrigendum_id"])
    assert len(grading_epoch_lineage(study)["epochs"]) == 3
    with pytest.raises(ValueError, match="activated current"):
        assert_active_grading_epoch(prior_child)
    history = lineage_human_cost(study)
    assert history["unique_observed_human_work"]["source_reference_work"]["unique_records"] == 64
    assert history["unique_observed_human_work"]["practical_timed_review"]["unique_records"] == 1
    assert history["unique_observed_human_work"]["timed_quality_adjudication"]["unique_records"] == 1


def test_child_source_copies_are_independent_but_tampering_prevents_activation(study):
    request = proposal(study)
    source = study / "cases/real-001/source/SKILL.md"
    before = source.read_bytes()
    copied = study / request["workspace"] / "cases/real-001/source/SKILL.md"
    copied.write_bytes(before + b"Changed only in the child copy.\n")
    assert source.read_bytes() == before
    with pytest.raises(ValueError, match="copied target, source"):
        confirm(study, request, "H1")


def test_changed_original_output_is_not_silently_rebased(study):
    request = proposal(study)
    original = next((study / "workflows").glob("*/result.json"))
    value = read(original)
    write_json(original, {**value, "reason": "Changed original target"})
    with pytest.raises(ValueError, match="Original reference, score, source or target bytes changed"):
        activate_corrigendum(study, request["corrigendum_id"])
