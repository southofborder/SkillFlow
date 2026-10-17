"""Pinned authoring examples preserve requirements without inferring necessity."""
import json

import pytest

from skillflow.common.paths import project_root
from skillflow.common.recording import sha_file
from skillflow.common.source_evidence import resolve_pointer
from skillflow.doe.task_material import prepare_task_review
from tests.doe.fixtures.task_examples import BASELINE, INPUT_SHA256, authored_candidate
from skillflow.propagation.contracts.references import target_key
from tests.doe.helpers import fact_fixture


def example(case):
    path = project_root() / BASELINE / case / "propagation/doe-input.json"
    assert sha_file(path) == INPUT_SHA256[case]
    raw = fact_fixture(path)
    candidate = authored_candidate(case, raw.cfg)
    review = prepare_task_review(raw, candidate)
    return raw, candidate, review


@pytest.mark.parametrize("case,count", [("001", 7), ("010", 8), ("013", 9)])
def test_authored_candidates_keep_exact_references_and_no_judgments(case, count):
    _, candidate, review = example(case)
    assert set(candidate) == {"purpose", "requirements", "source_accounting", "issues"}
    assert len(review.task.requirements) == count
    assert review.task.basis == "declared_skill"
    for realization in review.realizations:
        assert realization["bindings"]
        for binding in realization["bindings"]:
            resolve_pointer(review.cfg, review.targets[target_key(binding["target"])]["pointer"])


def bound_targets(review, requirement_id):
    realization = next(r for r in review.realizations if r["requirement_id"] == requirement_id)
    return [review.targets[target_key(b["target"])] for b in realization["bindings"]]


def test_count_and_prohibition_do_not_collapse_into_notification_payload():
    _, _, review = example("001")
    assert any(t["pointer"] == "/constraints/0" for t in bound_targets(review, "R005"))
    assert {t.get("instruction_id") for t in bound_targets(review, "R007")} == {"ir_007", "ir_009"}
    selectors = [resolve_pointer(review.cfg, t["pointer"]) for t in bound_targets(review, "R004")
                 if t["kind"] == "input"]
    assert {s["literal_value"] for s in selectors} == {"recipient", "summary"}


def test_cross_file_optional_arguments_and_real_return_are_separate():
    _, _, review = example("010")
    optional = review.task.requirements[2]
    assert {e.file for e in optional.evidences} == {"skill/references/workflow.md", "skill/query.yaml"}
    assert any(t["instruction_id"] == "ir_012" and t["kind"] == "input"
               for t in bound_targets(review, "R008"))
    assert not any(t.get("instruction_id") == "ir_012" and t["kind"] == "output"
                   for t in review.targets.values())


def test_attempt_identity_and_all_terminal_status_paths_are_retained():
    _, _, review = example("013")
    returned = {t.get("instruction_id") for t in bound_targets(review, "R006") if t["kind"] == "input"}
    assert returned == {"ir_020", "ir_022", "ir_024"}
    terminal = {t.get("instruction_id") for t in bound_targets(review, "R009") if t["kind"] == "input"}
    assert terminal == {"ir_019", "ir_021", "ir_023", "ir_025"}
    assert any(t["kind"] == "input" and t["instruction_id"] == "ir_026"
               for t in bound_targets(review, "R007"))


def test_complete_offline_baseline_is_replayable_and_idempotent(tmp_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket.socket, "connect", lambda *_a, **_k: pytest.fail("Unexpected API call"))
    before = {case: sha_file(project_root() / BASELINE / case / "propagation/doe-input.json") for case in INPUT_SHA256}
    reviews = [example(case)[2] for case in ("001","010","013")]
    assert [len(r.task.requirements) for r in reviews] == [7,8,9]
    assert reviews == [example(case)[2] for case in ("001","010","013")]
    assert before == {case: sha_file(project_root() / BASELINE / case / "propagation/doe-input.json") for case in INPUT_SHA256}
