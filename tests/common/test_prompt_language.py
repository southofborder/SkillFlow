"""English generated instructions and examples preserve original input languages."""
from copy import deepcopy
import json
import re

import pytest

from skillflow.common.prompt_format import compact_json
from skillflow.common.structural_correction import correction_prompt
from skillflow.graph.audit.prompts import AUDIT_CONTRACT, BOUNDARY, CONTROLLED_BOUNDARY
from skillflow.graph.extraction import prompt as extraction_prompt
from skillflow.graph.feedback.prompts import FEEDBACK_INSTRUCTIONS
from skillflow.propagation.annotation.binding_examples import binding_examples, example_material
from skillflow.propagation.annotation.prompt_examples import compact_prompt_examples, prompt_examples, coordinate_examples
from skillflow.propagation.annotation.prompts import (
    INSTRUCTIONS as ANNOTATION_INSTRUCTIONS,
    REPAIR_INSTRUCTIONS,
    build_prompt as annotation_prompt,
    response_format_example,
)
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.prompts import (
    INSTRUCTIONS as REVIEW_INSTRUCTIONS,
    build_prompt as review_prompt,
    review_examples,
)
from skillflow.task.material import prepare_task_material
from skillflow.task.prompts import (
    EXTRACTION_RULES, REVISION_RULES, TASK_CHECK, TASK_WORKFLOW, build_task_prompt,
)


HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U000323af]")
SECTIONS = re.compile(
    r"<!-- SKILLFLOW_PROMPT:([A-Z_]+):BEGIN -->\n(.*?)\n"
    r"<!-- SKILLFLOW_PROMPT:\1:END -->", re.DOTALL,
)


def assert_english_generated_text(text):
    assert HAN.search(text) is None
    assert "in Chinese" not in text


@pytest.mark.parametrize("examples", [binding_examples, prompt_examples, compact_prompt_examples, coordinate_examples, review_examples])
def test_independent_teaching_examples_are_english(examples):
    assert_english_generated_text(compact_json(examples()))


def test_complete_format_example_and_generated_prompt_sections_are_english():
    row = prompt_examples()[0]
    material = example_material(row)
    prompts = [
        annotation_prompt(material),
        review_prompt(prepare_review_material(material, row["annotation"])),
        build_task_prompt(prepare_task_material(material["source"])),
    ]
    assert_english_generated_text(compact_json(response_format_example()))
    for prompt in prompts:
        sections = dict(SECTIONS.findall(prompt))
        assert {"AUTHORITY", "FORMAT", "INPUT", "WORKFLOW", "SELF_CHECK"} <= sections.keys()
        for name, text in sections.items():
            if name != "INPUT":  # Real source and accepted responses may be any language.
                assert_english_generated_text(text)


def test_all_stage_output_policies_require_english_explanations():
    for instructions in (ANNOTATION_INSTRUCTIONS, REVIEW_INSTRUCTIONS, EXTRACTION_RULES,
                         BOUNDARY, AUDIT_CONTRACT, FEEDBACK_INSTRUCTIONS):
        assert "in English" in instructions
        assert_english_generated_text(instructions)
    for instructions in (REPAIR_INSTRUCTIONS, REVISION_RULES, TASK_CHECK, TASK_WORKFLOW,
                         CONTROLLED_BOUNDARY):
        assert_english_generated_text(instructions)
    # The graph extraction module has one generated instruction body, without
    # translating source data or changing its representation contract.
    instruction_values = [value for key, value in vars(extraction_prompt).items()
                          if key.isupper() and isinstance(value, str)]
    assert any("Write explanatory diagnostics in English" in value for value in instruction_values)
    for value in instruction_values:
        assert_english_generated_text(value)


def test_original_chinese_source_task_and_candidate_are_not_translated():
    row = deepcopy(prompt_examples()[0])
    source_text = "保留就绪的校准槽，统计数量并返回比较结果。"
    row["source"] = source_text
    row["task_candidate"]["purpose"]["text"] = "保持原文目的，不翻译保存材料。"
    row["task_candidate"]["purpose"]["evidences"][0]["reason"] = "真实输入依据仍保持原语言。"
    material = example_material(row)
    row["annotation"]["task_revision_id"] = material["task"]["task_sha256"]
    raw_reason = "已接受候选的中文理由不因提示词语言而改写。"
    next(iter(row["annotation"]["ir_semantics"].values()))["operator_evidences"][0]["reason"] = raw_reason

    annotation = annotation_prompt(material)
    sent = json.JSONDecoder().raw_decode(annotation.split("INPUT_JSON\n", 1)[1])[0]
    assert sent["source"]["files"][0]["lines"][0] == source_text
    assert sent["task"] == material["task"]

    prepared_review = prepare_review_material(material, row["annotation"])
    review = review_prompt(prepared_review)
    sent_review = json.JSONDecoder().raw_decode(
        review.split("REVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n", 1)[1])[0]
    assert sent_review["raw_annotation"] == prepared_review["raw_annotation"]
    assert raw_reason in review

    request = "请保留这份独立用户请求的原文。"
    task = build_task_prompt(prepare_task_material(material["source"], user_request=request))
    assert source_text in task and request in task

    candidate = {"reason": "当前候选的文字也不自动翻译。"}
    corrected = correction_prompt(annotation, compact_json(candidate), [{
        "category": "schema", "path": [], "message": "A required field is missing.",
    }])
    context = json.loads(corrected.split("CURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[1])
    assert context["candidate"] == candidate
    for name, text in SECTIONS.findall(corrected):
        if name != "INPUT":
            assert_english_generated_text(text)
    correction_instructions = corrected.split("MECHANICAL OUTPUT CORRECTION\n", 1)[1].split(
        "CURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[0]
    assert_english_generated_text(correction_instructions)
