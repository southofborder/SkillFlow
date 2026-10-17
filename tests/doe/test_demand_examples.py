"""Pinned offline demand authoring retains supported relationships and limits."""
import json

import pytest

from skillflow.common.paths import project_root
from skillflow.common.recording import canonical_sha256, sha_file
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.propagation.contracts.demand import validate_demand_candidate
from skillflow.propagation.contracts.task import task_source_files
from skillflow.propagation.contracts.references import target_key
from skillflow.doe.task_material import prepare_task_review
from tests.doe.fixtures.task_examples import authored_candidate
from tests.doe.helpers import fact_fixture, annotation_fixture
from tests.doe.fixtures.demand_examples import (
    BASELINE, EXPECTED_COUNTS, INPUT_SHA256, TASK_BASELINE, authored_demand_candidate,
)


def example(case):
    root = project_root()
    fact_path = root / BASELINE / case / "propagation/doe-input.json"
    assert sha_file(fact_path) == INPUT_SHA256[case]
    facts = fact_fixture(fact_path)
    raw = annotation_fixture(root / BASELINE / case / "annotation")
    task = prepare_task_review(facts, authored_candidate(case,facts.cfg)).task.model_dump(mode="json")
    candidate = authored_demand_candidate(case, facts.cfg, raw, task)
    targets = build_demand_target_index(facts.cfg, raw)
    typed = validate_demand_candidate(candidate, task, task_source_files(facts.source), targets)
    return facts, task, typed.model_dump(mode="json"), targets


@pytest.mark.parametrize("case", ["001", "010", "013"])
def test_only_positive_goals_have_genuine_targets_and_restrictions_remain_explicit(case):
    facts, task, candidate, targets = example(case)
    assert len(task["requirements"]) == EXPECTED_COUNTS[case][0]
    assert len(facts.sinks) == EXPECTED_COUNTS[case][1]
    assert {g["requirement_id"] for g in candidate["goals"]} < {r["id"] for r in task["requirements"]}
    assert {r["requirement_id"] for r in facts.annotation["compiled_annotation"]["realizations"]} == {r["id"] for r in task["requirements"]}
    assert all(target_key(g["target"]) in targets for g in candidate["goals"])
    assert not any(g["preserve"] == "value" and targets[target_key(g["target"])].get("kind") == "operation"
                   for g in candidate["goals"])


def test_notification_pair_is_original_fields_and_processed_count_stays_conservative():
    _, _, candidate, targets = example("001")
    pair = [g for g in candidate["goals"] if g["requirement_id"] == "R004"]
    assert {tuple(g["expected_path"]) for g in pair} == {("recipient",), ("summary",)}
    assert all(g["expected"] == {"kind": "local", "name": "event_record"} for g in pair)
    assert len({str(targets[target_key(g["target"])]["scope_path"]) for g in pair}) == 1
    assert {targets[target_key(e["target"])]["instruction_id"] for e in candidate["expressions"]} == {"ir_003"}
    assert not any(g["requirement_id"] == "R005" for g in candidate["goals"])
    assert not any(e["expression"]["op"] == "count" for e in candidate["expressions"])


def test_optional_request_preserves_fields_and_existence_separately():
    _, _, candidate, targets = example("010")
    for req, name, index in (("R003", "from_date", 2), ("R004", "limit", 4)):
        goals = [g for g in candidate["goals"] if g["requirement_id"] == req]
        assert {g["preserve"] for g in goals} == {"value", "presence"}
        value = next(g for g in goals if g["preserve"] == "value")
        assert value["path"] == [name]
        assert value["expected"] == {"kind": "input", "index": index}
        assert targets[target_key(value["target"])]["role"] != "control"
    assert all(e["expression"]["op"] == "present" for e in candidate["expressions"])
    assert any(targets[target_key(g["target"])].get("instruction_id") == "ir_012"
               and targets[target_key(g["target"])]["kind"] == "input"
               for g in candidate["goals"] if g["requirement_id"] == "R008")


def test_attempt_returns_status_writes_and_no_guessed_response_schema():
    _, _, candidate, targets = example("013")
    assert candidate["expressions"] == []
    returned = {targets[target_key(g["target"])].get("instruction_id") for g in candidate["goals"]
                if g["requirement_id"] in {"R006", "R007"} and g["preserve"] == "value"}
    assert returned == {"ir_020", "ir_022", "ir_024", "ir_026"}
    saved = {targets[target_key(g["target"])].get("instruction_id") for g in candidate["goals"]
             if g["requirement_id"] == "R009" and g["preserve"] == "action"}
    assert saved == {"ir_019", "ir_021", "ir_023", "ir_025"}
    assert not any(g["requirement_id"] == "R008" for g in candidate["goals"])


def test_pinned_baseline_offline_relations_and_original_bytes_are_preserved(monkeypatch):
    import socket
    from skillflow.doe.demand_material import prepare_demand_review
    monkeypatch.setattr(socket.socket, "connect", lambda *_a, **_k: pytest.fail("Unexpected API call"))
    for case in EXPECTED_COUNTS:
        facts,task,candidate,targets=example(case)
        result=prepare_demand_review(facts,task,facts.annotation,candidate).to_dict()
        assert len(result["sinks"])==EXPECTED_COUNTS[case][1]
        assert result==prepare_demand_review(facts,task,facts.annotation,candidate).to_dict()
        assert sha_file(project_root()/BASELINE/case/"propagation/doe-input.json")==INPUT_SHA256[case]


@pytest.mark.parametrize("case", ["001", "010", "013"])
def test_old_annotation_and_demand_runs_remain_rejected_by_production_loaders(case):
    from skillflow.doe.formal_runner import load_doe_run
    from skillflow.propagation.annotation.loading import load_annotation_run
    from tests.doe.fixtures.sensitivity_examples import DEMAND_BASELINE
    root = project_root()
    with pytest.raises(ValueError):
        load_annotation_run(root / BASELINE / case / "annotation")
    with pytest.raises(ValueError):
        load_doe_run(root / DEMAND_BASELINE / case)
    assert sha_file(root / BASELINE / case / "propagation/doe-input.json") == INPUT_SHA256[case]
