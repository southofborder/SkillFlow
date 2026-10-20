"""Restriction review is semantic inspection, not a positive seed or a verdict."""
from copy import deepcopy
import json
import re

import pytest

from skillflow.propagation.annotation.binding_examples import example_material
from skillflow.propagation.annotation.constraint_examples import constraint_example, constraint_lesson
from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.contracts.realizations import TaskRealization
from skillflow.propagation.review.material import prepare_review_material, checked_review_material
from skillflow.propagation.review.prompts import build_prompt, constraint_review_lesson
from skillflow.propagation.review.models import RawDeclarationCheck, task_objections
from skillflow.propagation.review.services import validate_response, review_annotation
from skillflow.propagation.review.report import display_model, render_markdown, render_html
from tests.propagation.review.test_core import empty_response as base_empty_response


def empty_response(prepared):
    response = base_empty_response(prepared)
    for axis in ("source_checks", "requirement_checks", "declaration_checks"):
        for check in response[axis]:
            check["reason"] = "This fixture records inspection without proving semantic correctness."
    return response


def fixture():
    example = constraint_example()
    return example_material(example), example["annotation"]


def test_pure_restriction_is_indexed_without_positive_seed_or_duplicated_body():
    material, raw = fixture()
    before = deepcopy((material, raw))
    checked, compiled, mapping = compile_response(raw, material)
    assert not any(goal["requirement_id"] == "R2" for goal in compiled["demands"])
    assert compiled["realizations"][1]["status"] == "expressed"
    reviewed = prepare_review_material(material, raw)
    rows = [row for row in reviewed["declaration_index"] if row["kind"] == "constraint"]
    assert rows == [{"kind": "constraint", **mapping["constraints"][0]}]
    assert rows[0]["raw_pointer"] == "/realizations/1/constraints/0"
    assert set(rows[0]) == {"kind", "raw_pointer", "constraint_id", "requirement_id"}
    assert any(row["pointer"] == rows[0]["raw_pointer"] for row in reviewed["target_index"])
    assert checked_review_material(reviewed) == reviewed
    assert (material, raw) == before


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "unknown", "old_name"])
def test_declaration_axis_requires_exact_demand_and_constraint_coverage(mutation):
    prepared = prepare_review_material(*fixture())
    response = empty_response(prepared)
    if mutation == "missing":
        response["declaration_checks"] = [row for row in response["declaration_checks"]
                                            if "/constraints/" not in row["raw_pointer"]]
    elif mutation == "duplicate":
        response["declaration_checks"].append(deepcopy(response["declaration_checks"][-1]))
    elif mutation == "unknown":
        response["declaration_checks"][-1]["raw_pointer"] = "/realizations/1/constraints/99"
    else:
        response["goal_checks"] = response.pop("declaration_checks")
    with pytest.raises(ValueError):
        validate_response(response, prepared)


@pytest.mark.parametrize("key,value", [("requirement_id", "R1"), ("constraint_id", "tampered"),
                                        ("raw_pointer", "/realizations/0/constraints/0")])
def test_constraint_index_tamper_is_rejected(key, value):
    prepared = prepare_review_material(*fixture())
    row = next(row for row in prepared["declaration_index"] if row["kind"] == "constraint")
    row[key] = value
    with pytest.raises(ValueError):
        checked_review_material(prepared)


def test_constraint_finding_routes_to_fixed_task_repair_without_task_objection():
    material, raw = fixture()
    raw["realizations"][1]["constraints"][0]["path"] = ["label"]
    # Mechanically valid references do not prove that this is the forbidden field.
    prepared = prepare_review_material(material, raw)
    response = empty_response(prepared)
    declaration = next(row for row in prepared["declaration_index"] if row["kind"] == "constraint")
    target = next(row["id"] for row in prepared["target_index"]
                  if row["pointer"] == declaration["raw_pointer"])
    response["findings"] = [{"domain": "annotation", "target_ids": [target],
        "explanation": "The faithful Task forbids diagnostic_note, while this declaration selects label.",
        "suggestion": "Keep Task and processing unchanged; bind the restriction to diagnostic_note.",
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                       "reason": "The source names diagnostic_note as the prohibited information."}]}]
    response["requirement_checks"][1].update(status="issue", finding_indexes=[0])
    response["declaration_checks"][-1].update(status="issue", finding_indexes=[0])
    parsed = validate_response(response, prepared)
    assert parsed.declaration_checks[-1].finding_ids == ["F001"]
    assert task_objections(parsed) == []


def test_final_prompts_include_complete_legal_restriction_fragment_and_check():
    material, raw = fixture()
    prepared = prepare_review_material(material, raw)
    annotation_text = annotation_prompt(material)
    review_text = build_prompt(prepared)
    shown = json.JSONDecoder().raw_decode(annotation_text.split("\nCONSTRAINT_LESSON\n", 1)[1])[0]
    review_shown = json.JSONDecoder().raw_decode(review_text.split("\nCONSTRAINT_REVIEW_LESSON\n", 1)[1])[0]
    assert shown == constraint_lesson() and review_shown == constraint_review_lesson()
    parsed = TaskRealization.model_validate(shown["realization"])
    assert parsed.requirement_id == "R2" and parsed.status == "expressed"
    assert shown["realization"] == raw["realizations"][1]
    assert shown["context"]["instruction"] == material["cfg"]["blocks"]["sample"]["instructions"][0]
    compile_response(raw, material)
    check = RawDeclarationCheck.model_validate(review_shown["check"])
    assert check.raw_pointer == "/realizations/1/constraints/0"
    response = empty_response(prepared)
    response["declaration_checks"][-1] = review_shown["check"]
    assert validate_response(response, prepared).declaration_checks[-1].status == "accepted"
    for text in (annotation_text, review_text):
        sections = re.findall(r"<!-- SKILLFLOW_PROMPT:([A-Z_]+):BEGIN -->", text)
        assert sections == ["AUTHORITY", "INPUT", "FORMAT", "WORKFLOW", "RULES", "EXAMPLES", "SELF_CHECK"]
        assert "Do not remove prohibited fields" in text
        assert not any(word in text for word in ("FAST_KEY", "access_token", "notify.send", "from_date"))
    assert "Pure restrictions need no positive seed" in annotation_text
    assert "A pure restriction needs no positive demand" in review_text


def test_one_injected_review_call_accepts_pure_restriction_and_reports_it_separately():
    material, raw = fixture()
    prepared = prepare_review_material(material, raw)
    calls = []
    class Client:
        def complete(self, prompt):
            calls.append(prompt)
            return empty_response(prepared)
    review = review_annotation(material, raw, client=Client())
    assert len(calls) == 1 and not review.findings
    result = {"status": "complete", "summary": "no_material_issue", "reason": "Injected protocol check.",
              "review": review.model_dump(mode="json")}
    model = display_model(result, prepared)
    row = next(row for row in model["crosswalk"] if row["requirement_id"] == "R2")
    assert len(row["declarations"]) == 1 and row["declarations"][0]["kind"] == "constraint"
    for output in (render_markdown(model), render_html(model)):
        assert "constraint_" in output
        assert "do not prove requirement satisfaction" in output


def test_constraint_review_correction_interruption_and_zero_api_replay(tmp_path, monkeypatch):
    from threading import Event
    from skillflow.propagation.review import runner
    from tests.propagation.review.test_runner import forbidden

    material, raw = fixture()
    prepared = prepare_review_material(material, raw)
    directory = tmp_path / "restriction-review"
    runner.prepare_candidate_run(material, raw, run_dir=directory,
                                 provenance={"kind": "authored_fixture", "purpose": "restriction accounting"})
    stop, calls = Event(), []
    class Client:
        def complete(self, prompt):
            calls.append(prompt)
            response = empty_response(prepared)
            if len(calls) == 1:
                response["declaration_checks"].pop()
            else:
                stop.set()
            return response

    interrupted = runner.run_review(directory, client=Client(), stop_event=stop)
    assert interrupted["status"] == "interrupted"
    assert len(calls) == 2
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    resumed = runner.run_review(directory, client_factory=forbidden)
    assert resumed["status"] == "complete" and resumed["counts"]["logical_calls"] == 2
    assert runner.load_review_run(directory)["result"] == resumed
    assert runner.replay_run(directory) == resumed
    assert any("/constraints/" in row["raw_pointer"] for row in resumed["review"]["declaration_checks"])
