"""Focused prompt guidance stays closed and preserves actual processing relations."""
from copy import deepcopy
import json
import re

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
from skillflow.propagation.annotation.requests import build_repair_context
from skillflow.propagation.review.models import (
    RawDeclarationCheck,
    RawRequirementCheck,
    RawSourceCheck,
)
from skillflow.propagation.review.prompts import build_prompt, review_example_material
from skillflow.propagation.review.services import validate_response
from tests.propagation.review.test_endpoint_review_example import rendered_lesson


CHECKS = {
    "source_checks": (RawSourceCheck, "file,start_line,end_line,status,reason,finding_indexes"),
    "requirement_checks": (RawRequirementCheck, "requirement_id,status,reason,finding_indexes"),
    "declaration_checks": (RawDeclarationCheck, "raw_pointer,status,reason,finding_indexes"),
}


def test_final_review_format_lists_exact_closed_check_keys_once():
    prompt = build_prompt(review_example_material())
    sections = re.findall(r"<!-- SKILLFLOW_PROMPT:([A-Z_]+):BEGIN -->", prompt)
    assert sections == ["AUTHORITY", "INPUT", "FORMAT", "WORKFLOW", "RULES", "EXAMPLES", "SELF_CHECK"]
    format_text = prompt.split("<!-- SKILLFLOW_PROMPT:FORMAT:BEGIN -->", 1)[1].split(
        "<!-- SKILLFLOW_PROMPT:FORMAT:END -->", 1)[0]
    assert format_text.count("CHECK KEYS (exact; no additional fields)") == 1
    for name, (model, shown) in CHECKS.items():
        assert set(shown.split(",")) == set(model.model_fields)
        assert f"{name}={{{shown}}}" in format_text
    assert "put explanations in reason, never new note fields" in prompt
    assert prompt.count("\nREVIEW_EXAMPLES\n") == 1


@pytest.mark.parametrize("axis", list(CHECKS))
def test_arbitrary_check_notes_still_fail_at_the_exact_candidate_field(axis):
    _, lesson, _, material = rendered_lesson()
    response = deepcopy(lesson["response"])
    note = "requirement_id_note" if axis == "requirement_checks" else "inspection_note"
    response[axis][0][note] = "Extra explanation must use the existing reason field."
    before = deepcopy(response)
    with pytest.raises(StructuralValidationError) as captured:
        validate_response(response, material)
    assert response == before
    assert any(row["path"] == f"/{axis}/0/{note}" for row in captured.value.diagnostics)


def test_extra_explanation_uses_reason_without_new_fields_or_lost_text():
    _, lesson, _, material = rendered_lesson()
    response = deepcopy(lesson["response"])
    for axis in CHECKS:
        response[axis][0]["reason"] += " Additional support stays in the existing reason field."
    accepted = validate_response(response, material)
    for axis in CHECKS:
        assert getattr(accepted, axis)[0].reason == response[axis][0]["reason"]


def test_rendered_suggestion_relocates_same_obligation_seeds_without_erasing_processing():
    prompt, lesson, material, review = rendered_lesson()
    accepted = validate_response(lesson["response"], review)
    assert len(accepted.findings) == 2
    suggestion = lesson["response"]["findings"][1]["suggestion"]
    assert "select_part/build/when operations unchanged" in suggestion
    assert "and remove its upstream copy" in suggestion
    assert "do not retain their upstream copies" in suggestion
    assert "independent upstream/return demands and conservative relations" in suggestion
    assert "controls are not payload" in suggestion
    assert len(lesson["response"]["findings"]) == 2
    assert "For each redundant upstream content demand, cite its supplied demand target ID or exact declaration_index.raw_pointer" in prompt

    context = build_repair_context(material, review["raw_annotation"], review,
                                   accepted.model_dump(mode="json"))
    sent = annotation_prompt(material, repair_context=context)
    shown = json.JSONDecoder().raw_decode(sent.split("\nREPAIR_CONTEXT\n", 1)[1])[0]
    assert shown["previous_raw_annotation"] == review["raw_annotation"]
    assert shown["review_response"]["findings"][1]["suggestion"] == suggestion


def test_teaching_relocation_keeps_selection_build_and_conditional_operations():
    from skillflow.propagation.annotation.prompt_examples import endpoint_example
    from skillflow.propagation.annotation.binding_examples import example_material

    example = endpoint_example()
    material = example_material(example)
    before = deepcopy(example)
    compile_response(example["contrast"], material)
    compile_response(example["annotation"], material)

    def operations(value):
        if isinstance(value, dict):
            if "op" in value:
                yield {key: deepcopy(child) for key, child in value.items() if key != "demands"}
            for child in value.values():
                yield from operations(child)
        elif isinstance(value, list):
            for child in value:
                yield from operations(child)

    assert list(operations(example["contrast"])) == list(operations(example["annotation"]))
    assert example == before
