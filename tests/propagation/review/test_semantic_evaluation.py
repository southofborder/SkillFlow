"""Offline benchmark plumbing is deliberately not a model performance result."""
from copy import deepcopy
import json

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.review.prompts import build_prompt
from skillflow.propagation.review.services import validate_response
from tools.doe.semantic_review_cases import evaluation_cases, CORPUS_VERSION
from tools.doe.evaluate_semantic_review import CaseAdjudication, prepare, score, score_case, run_cases, main
from tests.propagation.review.test_core import empty_response


def test_independent_corpus_covers_omission_breadth_identity_recipient_and_negative_controls():
    cases = evaluation_cases()
    assert {case["category"] for case in cases} == {
        "omitted_restriction", "overbroad_seed", "wrong_version", "inflated_task",
        "whole_value_control", "opaque_dependency_control", "precise_field_control", "wrong_recipient"}
    assert len({case["id"] for case in cases}) == len(cases)
    for case in cases:
        sent = json.JSONDecoder().raw_decode(build_prompt(case["review_material"]).split("\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n")[1])[0]
        assert "oracle" not in sent and "category" not in sent
        assert "case_id" not in sent
        assert sent["raw_annotation"] == case["annotation"]
        assert all("calibration" not in str(value) for value in (case["material"]["source"], case["annotation"]))


def test_no_model_results_produce_no_detection_metrics(tmp_path):
    result = score(tmp_path, {"corpus_version": CORPUS_VERSION, "cases": []})
    assert result["status_counts"] == {"not_run": 8}
    assert result["by_category"] == {}
    assert all(row["status"] == "not_run" for row in result["cases"])


def test_preparation_records_authored_candidates_and_keeps_oracle_outside_prompts(tmp_path):
    prepared = prepare(tmp_path / "evaluation")
    assert prepared["model_experiment"] == "not_run"
    for entry in prepared["cases"]:
        path = tmp_path / "evaluation/runs" / entry["case_id"]
        assert not (path / "calls").exists()
        prompt = (path / "inputs/prompt.txt").read_text(encoding="utf-8")
        assert "oracle" not in prompt and "rationale" not in prompt
        for oracle in entry["oracle"]:
            assert oracle["rationale"] not in prompt
    with pytest.raises(ValueError):
        prepare(tmp_path / "evaluation")


def test_adjudication_binds_exact_review_and_requires_every_finding_classified():
    case = next(case for case in evaluation_cases() if case["category"] == "overbroad_seed")
    prepared = case["review_material"]
    candidate = empty_response(prepared)
    target = next(row for row in prepared["target_index"] if row["kind"] == "annotation" and row["pointer"] == "/demands/0")
    candidate["findings"] = [{"domain": "annotation", "target_ids": [target["id"]],
        "explanation": "人工响应：将title需求扩大为完整notice。", "suggestion": "改在真实返回结果建立需求。",
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "reason": "只要求title。"}]}]
    candidate["goal_checks"][0].update(status="issue", finding_indexes=[0])
    review = validate_response(candidate, prepared).model_dump(mode="json")
    ledger = {"case_id": case["id"], "review_sha256": canonical_sha256(review), "reviewer": "工程测试人工响应",
        "judgments": [{"finding_id": "F001", "disposition": "matches_oracle", "oracle_ids": ["O1"],
                       "reason": "只验证账本匹配与计数；不是实际模型检出。"}]}
    scored = score_case(case, review, CaseAdjudication.model_validate(ledger))
    assert scored["true_positives"] == ["O1"]
    assert scored["false_negatives"] == [] and scored["false_positives"] == []
    for mutation in ("digest", "missing_finding", "wrong_domain", "unknown_oracle"):
        changed = deepcopy(ledger)
        if mutation == "digest": changed["review_sha256"] = "0" * 64
        elif mutation == "missing_finding": changed["judgments"] = []
        elif mutation == "unknown_oracle": changed["judgments"][0]["oracle_ids"] = ["absent"]
        else:
            changed["judgments"][0]["oracle_ids"] = ["O1"]
            broken = deepcopy(case)
            broken["oracle"][0]["domain"] = "task"
            with pytest.raises(ValueError):
                score_case(broken, review, CaseAdjudication.model_validate(changed))
            continue
        with pytest.raises(ValueError):
            score_case(case, review, CaseAdjudication.model_validate(changed))


def test_empty_reviews_count_missed_defects_only_after_human_adjudication():
    case = evaluation_cases()[0]
    review = validate_response(empty_response(case["review_material"]), case["review_material"]).model_dump(mode="json")
    ledger = CaseAdjudication(case_id=case["id"], review_sha256=canonical_sha256(review), reviewer="工程人工核对", judgments=[])
    scored = score_case(case, review, ledger)
    assert scored["false_negatives"] == ["O1"] and not scored["true_positives"]


def test_reference_gaps_are_not_forced_into_false_positive_or_detection_metrics():
    case = evaluation_cases()[0]
    prepared = case["review_material"]
    candidate = empty_response(prepared)
    target = next(row for row in prepared["target_index"] if row["kind"] == "annotation")
    candidate["findings"] = [{"domain": "annotation", "target_ids": [target["id"]],
        "explanation": "合成参考可能未覆盖额外实质问题。", "suggestion": "先复核参考，不改原始模型记录。",
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "reason": "需要复核源文。"}]}]
    review = validate_response(candidate, prepared).model_dump(mode="json")
    ledger = CaseAdjudication(case_id=case["id"], review_sha256=canonical_sha256(review), reviewer="助手核对",
        reviewer_kind="assistant", judgments=[{"finding_id": "F001", "disposition": "needs_baseline_review",
            "oracle_ids": [], "reason": "不能用未覆盖的参考标签强记为模型误报。"}])
    scored = score_case(case, review, ledger)
    assert scored["status"] == "oracle_gap"
    assert scored["needs_baseline_review"] == ["F001"]
    assert scored["false_positives"] == []
    assert scored["reviewer_kind"] == "assistant"


def test_online_execution_requires_explicit_flag_before_environment_or_model_access(tmp_path, monkeypatch):
    import tools.doe.evaluate_semantic_review as driver
    def forbidden(*args, **kwargs):
        raise AssertionError("online runner was not authorized")
    monkeypatch.setattr(driver, "run_review", forbidden)
    with pytest.raises(ValueError, match="run_online"):
        run_cases(tmp_path / "no-network")
    with pytest.raises(SystemExit):
        main(["run", "--output", str(tmp_path / "cli-no-network")])
    assert not (tmp_path / "no-network").exists()
    assert not (tmp_path / "cli-no-network").exists()


def test_injected_production_review_run_cannot_enter_real_model_metrics(tmp_path):
    class Client:
        def complete(self, prompt):
            return empty_response(json.JSONDecoder().raw_decode(prompt.split("\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n")[1])[0])
    path = tmp_path / "simulated"
    result = run_cases(path, client=Client(), case_ids=["sr005"])
    assert result["origin"] == "engineering_simulation"
    assert result["runs"][0]["status"] == "complete"
    assert not result["runs"][0]["request_observed"]
    scored = score(path / "runs", {"corpus_version": CORPUS_VERSION, "cases": []})
    assert scored["status_counts"] == {"not_run": 7, "engineering_simulation": 1}
    assert scored["by_category"] == {}
    with pytest.raises(ValueError, match="engineering simulations"):
        score(path / "runs", {"corpus_version": CORPUS_VERSION, "cases": [{"case_id": "sr005",
            "review_sha256": result["runs"][0]["review_sha256"], "reviewer": "人工工程样例", "judgments": []}]})
