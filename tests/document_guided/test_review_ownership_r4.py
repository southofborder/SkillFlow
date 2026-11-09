"""Concrete r3 review mislocation and unchanged finite repair routing."""
from copy import deepcopy
import json
from pathlib import Path

from skillflow.document_guided import runner
from skillflow.document_guided.source_review import (
    prepare_review_material, build_source_review_prompt, validate_source_review,
)
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


FIXTURE = Path(__file__).parents[1] / "fixtures/online_interface_r4/001/review-material.json"


def test_saved_token_prohibition_finding_targets_realization_not_sensitive_range():
    saved = json.loads(FIXTURE.read_text(encoding="utf-8"))
    material = prepare_review_material(**{k: saved[k] for k in ("files", "task", "cfg", "annotation")},
        mapping={"fragment_origins": saved["fragment_origins"]}, generation="fragment-v1")
    original = saved["original_finding"]
    assert original["owner"] == "sensitivity"
    assert original["target_ids"] == ["annotation:/ir_semantics/ir_001/sensitivity/0"]
    # Only the location is corrected. The saved source-backed issue/suggestion
    # remains the original; this test does not pretend the validator can infer it.
    fixed = {k: deepcopy(v) for k, v in original.items() if k not in {"owner", "id"}}
    index = next(i for i, r in enumerate(saved["annotation"]["realizations"]) if r["requirement_id"] == "R6")
    fixed["target_ids"] = [f"annotation:/realizations/{index}"]
    checked = validate_source_review({"outcome": "completed", "findings": [fixed]}, material)
    assert checked["findings"][0]["owner"] == "task-correspondence"
    assert runner._fragment_repair_findings(checked, "task-correspondence")
    assert not runner._fragment_repair_findings(checked, "sensitivity")
    assert not runner._fragment_repair_findings(checked, "processing")
    prompt = build_source_review_prompt(material)
    assert "For a missing\nrestriction, target the existing realization" in prompt
    assert "Sensitivity owns the source value, sensitive range" in prompt
    assert "unused whole-file output" in prompt
    assert original == saved["original_finding"]


def test_realization_finding_repairs_mapping_only_and_keeps_seven_call_normal_path(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)

    class CorrectOwner(Harness):
        def complete(self, stage, prompt):
            result = super().complete(stage, prompt)
            if stage == "review":
                result["findings"] = [{"domain": "annotation",
                    "target_ids": ["annotation:/realizations/0"],
                    "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}],
                    "explanation": "The source requirement needs a correspondence recheck, not a new sensitivity label.",
                    "suggestion": "Recheck the requirement's existing receiving operation and value binding."}]
            return result

    harness = CorrectOwner(tmp_path / "run", canaries=True)
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete", result
    assert result["counts"]["logical_calls"] == len(harness.calls) == 9
    assert len([x for x in harness.calls if not x.startswith("revision")]) == 7
    assert {x for x in harness.calls if x.startswith("revision")} == {
        "revision-task-correspondence", "revision/review"}
    assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts["revision-task-correspondence"]
    assert (harness.directory / "doe/doe-result.json").is_file()
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 9
