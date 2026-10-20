"""Experiment orchestration integrity; these tests do not measure model quality."""
import json
from pathlib import Path

import pytest

from tools.doe.direct_baseline import package_bundle, prepare_trial, verify
from tools.doe.direct_experiment import _freeze_case, review
from tools.doe.direct_assessment import packets, aggregate, final_packets
from tools.doe.direct_results import measurements


def test_freeze_resume_checks_current_source_and_request(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "SKILL.md").write_text("Preserve the original value.\n", encoding="utf-8")
    run = tmp_path / "run"
    first = _freeze_case(source, run, "case", ["SKILL.md"], "Return the value unchanged.")
    assert _freeze_case(source, run, "case", ["SKILL.md"], "Return the value unchanged.") == first
    with pytest.raises(ValueError, match="request differs"):
        _freeze_case(source, run, "case", ["SKILL.md"], "Return a summary.")
    (source / "SKILL.md").write_text("Rewrite the value.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="source"):
        _freeze_case(source, run, "case", ["SKILL.md"], "Return the value unchanged.")


def test_independent_review_embeds_exact_answer_and_deliverable(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "SKILL.md").write_text("Send only record.summary.\n", encoding="utf-8")
    run = tmp_path / "run"
    package_bundle(source, run, "case", source_files=["SKILL.md"])
    root = Path(__file__).resolve().parents[2]
    prompts = root / "tools/doe/direct_prompts"
    prepare_trial(run, "original", "case", prompts / "chain.txt", shared_path=prompts / "shared.txt",
                  metadata={"stage": "pilot", "arm": "chain", "repeat": 1, "review": False})
    answer = "Candidate {source_bundle} remains literal.\nAn unsupported whole record claim.\n"
    (run / "trials/original/answer.txt").write_text(answer, encoding="utf-8")
    review(run, "original")
    prompt = (run / "trials/original_review/prompt.txt").read_text(encoding="utf-8")
    assert prompt.endswith("CANDIDATE ANSWER\n" + answer + "\n")
    assert "Control flow, including branches" in prompt
    assert (run / "trials/original_review/original_answer.txt").read_text(encoding="utf-8") == answer
    assert verify(run)["verified"]


def test_blind_packets_hide_identity_and_disagreement_is_not_pass(tmp_path):
    run = tmp_path / "run"
    trial = run / "trials/case_audit_r1"
    trial.mkdir(parents=True)
    reg = {"case_id": "case", "metadata": {"arm": "audit", "repeat": 1, "stage": "heldout", "review": False}}
    (trial / "registration.json").write_text(json.dumps(reg), encoding="utf-8")
    (trial / "decision.json").write_text("{}", encoding="utf-8")
    (trial / "answer.txt").write_text("Visible source-linked answer.", encoding="utf-8")
    assert packets(run) == {"cases": 1, "candidates": 1}
    identity = json.loads((run / "identity-map.json").read_text())
    cid = next(iter(identity))
    assert (run / "blind/case" / f"{cid}.txt").read_text() == "Visible source-linked answer."
    assert "audit" not in (run / "blind/case/index.json").read_text()
    (run / "assessments").mkdir()
    for reviewer, judgment in (("A", "satisfies_reference"), ("B", "substantive_error")):
        (run / "assessments" / f"{reviewer}.json").write_text(json.dumps({
            "reviewer": reviewer, "candidates": [{"candidate_id": cid, "judgment": judgment}]}), encoding="utf-8")
    result = aggregate(run)
    assert result["candidates"][0]["judgment"] == "indeterminate_or_reviewer_disagreement"


def test_measurements_deduplicate_and_preserve_unknown_cost():
    usage = {"input_tokens": 11, "output_tokens": 7, "total_tokens": 18,
             "cached_input_tokens": None, "cache_write_input_tokens": None,
             "reasoning_output_tokens": 4}
    decision = {"usage": {"by_response_id": {"r": usage}, "response_count": 1},
                "timing": {"duration_ms": 1000}, "protocol_status": "conformant"}
    measured = measurements([decision, decision])
    assert measured["responses"] == 1
    assert measured["usage"]["total_tokens"]["complete_total"] == 18
    assert measured["usage"]["reasoning_output_tokens"]["complete_total"] == 4
    assert measured["usage"]["cached_input_tokens"]["complete_total"] is None
    assert measured["monetary_cost"] is None
    missing = {"usage": {"by_response_id": {}, "response_count": 0},
               "timing": {}, "protocol_status": "unverified"}
    assert measurements([decision, missing])["usage"]["total_tokens"]["complete_total"] is None


def test_semantic_pass_requires_recorded_reference_coverage(tmp_path):
    run = tmp_path / "run"
    (run / "blind/case").mkdir(parents=True)
    (run / "assessments").mkdir()
    (run / "identity-map.json").write_text(json.dumps({"candidate": {
        "case_id": "case", "trial_id": "trial", "metadata": {"stage": "heldout", "arm": "audit", "review": False}}}), encoding="utf-8")
    (run / "blind/case/reference-a.json").write_text(json.dumps({
        "author": "A", "cases": [{"mandatory_checks": [{"id": "C1"}]}]}), encoding="utf-8")
    (run / "assessments/a.json").write_text(json.dumps({"reviewer": "A", "case_id": "case", "candidates": [{
        "candidate_id": "candidate", "judgment": "satisfies_reference", "reason": "All checked.", "check_results": []}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="every source-reference criterion"):
        aggregate(run)


def test_fresh_final_cohort_cannot_include_old_pilot_answers(tmp_path):
    run = tmp_path / "run"
    for name, stage, text in (("old_pilot", "pilot", "OLD_PILOT_CANARY"),
                              ("new_pilot", "pilot_revision", "Revised answer.")):
        trial = run / "trials" / name
        trial.mkdir(parents=True)
        (trial / "registration.json").write_text(json.dumps({"case_id": "case", "metadata": {
            "stage": stage, "arm": "audit", "review": False, "repeat": 1}}), encoding="utf-8")
        (trial / "decision.json").write_text("{}", encoding="utf-8")
        (trial / "answer.txt").write_text(text, encoding="utf-8")
    assert final_packets(run) == {"cases": 1, "candidates": 1}
    content = "\n".join(p.read_text(encoding="utf-8") for p in (run / "blind-final").rglob("*.txt"))
    assert "OLD_PILOT_CANARY" not in content
    assert "Revised answer." in content


@pytest.mark.parametrize("severity,coverage", [("substantive", "pass"), ("disputed", "pass"), ("minor", "fail"), ("minor", "disputed")])
def test_semantic_pass_cannot_hide_a_material_finding_or_failed_coverage(tmp_path, severity, coverage):
    run = tmp_path / "run"
    (run / "blind/case").mkdir(parents=True)
    (run / "assessments").mkdir()
    (run / "identity-map.json").write_text(json.dumps({"candidate": {
        "case_id": "case", "trial_id": "trial", "metadata": {"stage": "heldout", "arm": "audit", "review": False}}}), encoding="utf-8")
    (run / "blind/case/reference-a.json").write_text(json.dumps({
        "author": "A", "cases": [{"mandatory_checks": [{"id": "C1"}]}]}), encoding="utf-8")
    (run / "assessments/a.json").write_text(json.dumps({"reviewer": "A", "case_id": "case", "candidates": [{
        "candidate_id": "candidate", "judgment": "satisfies_reference", "reason": "Claims to pass.",
        "check_results": [{"reference_author": "A", "check_id": "C1", "status": "pass", "reason": "Checked."}],
        "coverage": {"functionality": coverage},
        "findings": [{"severity": severity, "reason": "A material contradiction remains."}]}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="A semantic pass cannot include"):
        aggregate(run)
