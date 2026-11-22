"""The existing seven-call flow repairs and seals concrete contract checks."""
from copy import deepcopy

from skillflow.document_guided import runner
from skillflow.document_guided.online import read
from skillflow.doe.formal_runner import load_doe_run, run_doe
from tests.document_guided.test_parallel_runner import Harness, freeze_producer
from tests.doe.input_review_helpers import review_prompt_payload


def test_rejected_contract_repairs_processing_and_seals_selected_review(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)

    class ContractHarness(Harness):
        def __init__(self, directory):
            super().__init__(directory, precise_repair=True)
            self.contract_ids = {}
            self.contract_ir = next(iter(self.fragments["processing"]["ir_semantics"]))
            evidence = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                "reason": "The source specifies displaying the calibration label, not the tolerance."}
            operation = {"op": "compute", "inputs": [{"kind": "input", "index": 0}],
                "dependencies": ["derived"], "output": "extra_label", "evidences": [evidence],
                "demand_transfer": {"rules": [{"output": {"property": "value", "path": []},
                    "inputs": [{"input_index": 0, "required": [
                        {"property": "value", "path": ["label"]},
                        {"property": "value", "path": ["tolerance"]}],
                        "remainder": "independent", "reason": "This draft incorrectly includes tolerance."}],
                    "reason": "The result is the calibration label.", "evidences": [evidence]}]}}
            self.fragments["processing"]["ir_semantics"][self.contract_ir]["segments"][0]["ops"].append(operation)

        def complete(self, stage, prompt):
            result = super().complete(stage, prompt)
            if stage == "revision-processing":
                slot, = result["coverage_slots"]
                assert slot["instruction_id"] == self.contract_ir
                operation = slot["modeled"]["segments"][0]["ops"][-1]
                row = operation["demand_transfer"]["rules"][0]["inputs"][0]
                row["required"] = [{"property": "value", "path": ["label"]}]
                row["reason"] = "Only the original label determines this local result; tolerance is independent."
            if stage in {"review", "revision/review"}:
                payload = review_prompt_payload(prompt)
                from tests.doe.input_review_helpers import checks_for_inventory
                inventory = payload["input_contract_inventory"]
                self.contract_ids[stage] = [entry["contract_id"] for entry in inventory["obligations"]]
                assert len(inventory["obligations"]) == 1
                result["input_contract_checks"] = checks_for_inventory(inventory,
                    [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                      "reason": "The source specifies the calibration label without tolerance."}],
                    status="rejected" if stage == "review" else "accepted")
            return result

    harness = ContractHarness(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete", result
    assert result["repair_used"]
    assert len(harness.calls) == result["counts"]["logical_calls"] == 11
    assert len([stage for stage in harness.calls if not stage.startswith("revision")]) == 7
    assert {stage for stage in harness.calls if stage.startswith("revision")} == {
        "revision-processing", "revision-task-correspondence", "revision-sensitivity", "revision/review"}
    assert harness.contract_ids["review"] != harness.contract_ids["revision/review"]
    receipt = read(harness.directory / "audit/input-contract-review.json")
    assert receipt["source_review_complete"]
    assert [row["contract_id"] for row in receipt["checks"]] == harness.contract_ids["revision/review"]
    assert all(row["status"] == "accepted" for row in receipt["checks"])
    assert load_doe_run(harness.directory / "doe")["input_contract_review"] == receipt
    assert run_doe(harness.directory / "propagation", run_dir=harness.directory / "doe")["input_contract_review"] == receipt
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 11
