"""A retained partial source review drives the existing repair and real backend."""
from copy import deepcopy

import pytest

from skillflow.common.llm.request_errors import InputTooLarge
from skillflow.document_guided import runner
from skillflow.document_guided.online import read
from tests.document_guided.test_parallel_runner import Harness, freeze_producer
from tests.document_guided.test_source_review_locality import bad_source_records
from tests.doe.input_review_helpers import checks_for_inventory, review_prompt_payload
from tests.doe.test_demand_engine import inp
from tests.doe.test_reviewed_input_necessity import compute, rule, row


@pytest.fixture(autouse=True)
def offline_producer(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


class RetainedReviewHarness(Harness):
    def __init__(self, directory):
        super().__init__(directory, precise_repair=True)
        operations = self.fragments["processing"]["ir_semantics"]["ir_001"]["segments"][0]["ops"]
        added = []
        for index in range(4):
            operation = compute([inp()], [rule([], [row(0, ["label"])])])
            operation.update(output="review_fixture_" + str(index), effect="transform")
            operation["evidences"] = deepcopy(operations[0]["evidences"])
            operation["demand_transfer"]["rules"][0]["evidences"] = deepcopy(operations[0]["evidences"])
            added.append(operation)
        operations[:0] = added
        self.first_review = None
        self.obligation_ids = []

    def complete(self, stage, prompt):
        if stage == "review" and self.attempts.get(stage):
            with self.lock:
                self.attempts[stage] += 1
                self.calls.append(stage)
                self.prompts[stage + "-correction"] = prompt
            assert self.attempts[stage] == 2
            raise InputTooLarge("Synthetic complete correction rejected before any native start.")
        answer = super().complete(stage, prompt)
        if stage == "revision-processing":
            slot, = answer["coverage_slots"]
            assert slot["instruction_id"] == "ir_001"
            operation = slot["modeled"]["segments"][0]["ops"][0]
            operation["demand_transfer"]["rules"][0]["reason"] += " The input range was rechecked against this source span."
        if stage != "review":
            return answer
        material = review_prompt_payload(prompt)
        inventory = material["input_contract_inventory"]
        obligations = inventory["obligations"]
        assert len(obligations) == 4
        self.obligation_ids = [item["id"] for item in obligations]
        cited = deepcopy(answer["input_contract_checks"][0]["evidences"])
        rejected = checks_for_inventory(inventory, cited, status="rejected")
        answer["input_contract_checks"][0] = rejected[0]
        answer["input_contract_checks"].pop(1)
        answer["findings"] = [{"domain": "annotation", "target_ids": [obligations[0]["target_id"]],
            "explanation": "The local operation needs its source-supported field relationship rechecked.",
            "source_refs": [{key: cited[0][key] for key in ("file", "start_line", "end_line")}],
            "suggestion": "Rebuild this processing relationship and its dependent fragments."}]
        answer["source_input_findings"] = bad_source_records(obligations[2]["target_id"])[:1]
        self.first_review = deepcopy(answer)
        return answer


def test_retained_partial_review_repairs_only_its_closure_then_reaches_backend_and_replay(tmp_path):
    harness = RetainedReviewHarness(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete", result
    assert result["repair_used"] and result["selected_annotation"] == "revision/annotation"
    initial = read(harness.directory / "review/result.json")
    assert initial["status"] == "partial"
    assert initial["request_failure"]["error_type"] == "InputTooLarge"
    assert initial["request_failure"]["failure_call"]["call"] == "calls/review/a002"
    assert initial["delivery_retention"]["artifacts"]
    assert initial["validation"]["candidate"] == harness.first_review
    retained = initial["review"]["findings"][0]
    assert {key: retained[key] for key in harness.first_review["findings"][0]} == harness.first_review["findings"][0]
    assert retained["owner"] == "processing"
    assert initial["review"]["source_input_findings"] == []
    coverage = {item["obligation_id"]: item["status"] for item in initial["validation"]["contract_coverage"]}
    assert coverage[harness.obligation_ids[3]] == "validated"
    assert coverage[harness.obligation_ids[1]] == "missing"
    assert coverage[harness.obligation_ids[2]] == "blocked"
    expected = {"revision-processing", "revision-task-correspondence", "revision-sensitivity", "revision/review"}
    assert {name for name in harness.calls if name.startswith("revision")} == expected
    assert harness.calls.count("task") == harness.calls.count("flow") == harness.calls.count("graph") == 1
    assert harness.calls.count("review") == 2
    assert result["counts"]["logical_calls"] == len(harness.calls) == 12
    assert result["counts"]["structural_corrections"] == 1
    assert result["stages"]["propagation"]["status"] == "complete"
    assert (harness.directory / "propagation/records.json").is_file()
    assert (harness.directory / "doe/doe-result.json").is_file()
    calls = list(harness.calls)
    responses = {path: path.read_bytes() for path in harness.directory.rglob("response.json")}
    assert runner.replay(harness.directory) == result
    assert harness.calls == calls
    assert responses == {path: path.read_bytes() for path in harness.directory.rglob("response.json")}
