"""Current-selector dependency guards using synthetic source-only input trees."""
from copy import deepcopy
import json

import pytest

from tools.doe.real_comparison import selection_readiness as readiness
from tools.doe.real_comparison.protocol import sha256


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture
def selection_inputs(tmp_path, monkeypatch):
    proposal, corpus = tmp_path / "proposal", tmp_path / "corpus"
    rows = [{"canonical_id": f"test/skill-{i}", "version": "1.0", "source_sha256": f"source-{i}",
             "source_tree_sha256": f"tree-{i}", "bundle_sha256": f"bundle-{i}",
             "source_dir": f"packages/{i}", "source_view_path": f"views/{i}.json"} for i in range(30)]
    for row in rows:
        dump(corpus / row["source_dir"] / "SKILL.md", {"source": "真实原文 {literal}"})
        dump(corpus / row["source_view_path"], {"source": "Synthetic source provenance."})
    evidence = dump(corpus / "screening.json", {"synthetic": True})
    rules = dump(proposal / "rules.json", {"evidence_inputs": [{"path": str(evidence), "sha256": sha256(evidence)}]})
    queue = dump(proposal / "candidate-queue.json", {"candidates": rows})
    dump(proposal / "rules-freeze.json", {"files": {"rules.json": sha256(rules), "candidate-queue.json": sha256(queue)}})
    dump(proposal / "reviews/test.json", {"synthetic": True})
    expected = {"selected": rows[:24], "reserves": rows[24:], "rules_sha256": sha256(rules),
                "candidate_queue_sha256": sha256(queue)}
    result = {**deepcopy(expected), "status": "selection_complete_pending_human_reference",
              "accepted_count": 30, "shortfall": 0, "thresholds_relaxed": False,
              "order_reshuffled": False, "frozen_source_inputs": [{"path": str(evidence), "sha256": sha256(evidence)}]}
    calls = []
    def select(*args, **kwargs):
        calls.append((args, kwargs))
        assert kwargs == {"write": False}
        return deepcopy(result)
    monkeypatch.setattr(readiness.long_selection, "select_long_cases", select)
    return proposal, corpus, expected, result, calls


def test_recompute_binds_all_exact_identities_and_never_writes(selection_inputs):
    proposal, corpus, expected, _, calls = selection_inputs
    before = {p: p.read_bytes() for p in proposal.rglob("*") if p.is_file()}
    binding = readiness.inspect_current_selection(proposal, corpus, expected)
    assert len(binding["expected_case_identities"]) == 30 and len(calls) == 1
    assert binding["state"] == "validated_current_selector" and binding["model_calls"] == 0
    assert readiness.verify_saved_binding(binding, expected) == binding
    assert len(calls) == 1  # Saved closure checks do not rerun expensive proof/tokenization.
    assert before == {p: p.read_bytes() for p in proposal.rglob("*") if p.is_file()}


def test_dependency_saved_after_proof_work_cannot_be_bound_as_validated(selection_inputs, monkeypatch):
    proposal, corpus, expected, result, _ = selection_inputs
    def concurrent_save(*args, **kwargs):
        assert kwargs == {"write": False}
        dump(proposal / "reviews/test.json", {"changed_after_proof": True})
        return deepcopy(result)
    monkeypatch.setattr(readiness.long_selection, "select_long_cases", concurrent_save)
    with pytest.raises(ValueError, match="dependencies changed during validation"):
        readiness.inspect_current_selection(proposal, corpus, expected)


def test_expected_cohort_cannot_change_during_validation(selection_inputs, monkeypatch):
    proposal, corpus, expected, result, _ = selection_inputs
    def concurrent_cohort_change(*args, **kwargs):
        expected["selected"][0]["version"] = "changed"
        return deepcopy(result)
    monkeypatch.setattr(readiness.long_selection, "select_long_cases", concurrent_cohort_change)
    with pytest.raises(ValueError, match="dependencies changed during validation"):
        readiness.inspect_current_selection(proposal, corpus, expected)


@pytest.mark.parametrize("field", readiness.IDENTITY_FIELDS)
def test_current_proof_cannot_substitute_any_one_source_identity(selection_inputs, field):
    proposal, corpus, expected, result, _ = selection_inputs
    result["reserves"][-1][field] = "different"
    with pytest.raises(ValueError, match="fixed ordered cohort"):
        readiness.inspect_current_selection(proposal, corpus, expected)


@pytest.mark.parametrize("field, value", [("status", "needs_review_correction"), ("shortfall", 1),
    ("thresholds_relaxed", True), ("order_reshuffled", True), ("rules_sha256", "different"),
    ("candidate_queue_sha256", "different")])
def test_historical_pass_or_different_policy_cannot_establish_current_readiness(selection_inputs, field, value):
    proposal, corpus, expected, result, _ = selection_inputs
    result[field] = value
    with pytest.raises(ValueError):
        readiness.inspect_current_selection(proposal, corpus, expected)


@pytest.mark.parametrize("target", ["review", "source", "view", "rule", "new_review", "supersession", "omitted_closure", "implementation"])
def test_saved_binding_rejects_any_changed_or_omitted_dependency(selection_inputs, target):
    proposal, corpus, expected, _, _ = selection_inputs
    binding = readiness.inspect_current_selection(proposal, corpus, expected)
    if target == "review":
        dump(proposal / "reviews/test.json", {"changed": True})
    elif target == "new_review":
        dump(proposal / "reviews/new.json", {"new": True})
    elif target == "source":
        dump(corpus / "packages/0/SKILL.md", {"changed": True})
    elif target == "view":
        dump(corpus / "views/0.json", {"changed": True})
    elif target == "rule":
        dump(proposal / "rules.json", {"changed": True})
    elif target == "supersession":
        dump(proposal / "review-supersessions.json", {"new": True})
    elif target == "omitted_closure":
        binding["input_trees"] = {}
    else:
        binding["implementation_files"][readiness.IMPLEMENTATION[0]] = "different"
    with pytest.raises(ValueError):
        readiness.verify_saved_binding(binding, expected)
