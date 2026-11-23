"""Exercise the actual seven-stage orchestration, selected artifacts and offline replay."""
from skillflow.document_guided import runner
from skillflow.doe.formal_runner import load_doe_run
from skillflow.propagation.runner import load_propagation_materials
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


class SourceActions(Harness):
    def __init__(self, directory):
        super().__init__(directory)
        self.example["source"] += " First invoke the local diagnostic callback, whose implementation is unavailable."
        self.span = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}
        record = self.fragments["processing"]["ir_semantics"]["ir_001"]
        record["segments"][0]["ops"].insert(0, {"op": "placeholder", "kind": "effect", "inputs": [],
            "reason": "The implementation of the local diagnostic callback is unavailable.",
            "evidences": [{**self.span, "reason": "The source invokes the callback before displaying the label."}]})
        record["action_bindings"] = {"log": [["segments", 0, "ops", 0]],
                                     "display": [["segments", 0, "ops", 1], ["segments", 1, "ops", 0]]}

    def complete(self, stage, prompt):
        response = super().complete(stage, prompt)
        if stage == "graph":
            action = response["blocks"][0]["operations"][0]
            action["source_actions"] = [{"ref": "log", "kind": "other", "source": self.span},
                                        {"ref": "display", "kind": "deliver", "source": self.span}]
        return response


def test_seven_fresh_stages_keep_known_sibling_with_symbolic_occurrence(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    harness = SourceActions(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "partial", result
    assert sorted(harness.calls) == sorted(("task", "flow", "graph", "processing", "sensitivity", "task-correspondence", "review"))
    facts = load_propagation_materials(harness.directory / "propagation")
    assert facts.coverage["ir_001"] == "processed_with_placeholder"
    assert facts.coverage["ir_002"] == "processed"
    assert facts.annotation["mapping"]["source_action_bindings"]["ir_001"]["bindings"]["log"] == [["segments", 0, "ops", 0]]
    assert load_doe_run(harness.directory / "doe")["support"]["coverage"]["upstream"] == facts.coverage
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 7
