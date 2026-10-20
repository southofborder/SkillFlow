"""Rendered teaching inputs are executable; injected reviews are not model accuracy."""
from copy import deepcopy
import json
import re

from skillflow.propagation.annotation.binding_examples import example_material
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.prompt_examples import endpoint_example
from skillflow.propagation.material import prepare_material, evidence_reference
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.models import task_objections
from skillflow.propagation.review.prompts import build_prompt, review_examples, review_example_material
from skillflow.propagation.review.refinement import refine_annotation
from skillflow.propagation.review.services import validate_response
from tests.propagation.review.test_core import empty_response


def rendered_lesson():
    prompt = build_prompt(review_example_material())
    shown = json.JSONDecoder().raw_decode(prompt.split('\nREVIEW_EXAMPLES\n', 1)[1])[0][0]
    context = shown['context']
    material = prepare_material(context['source'], context['cfg'],
        task_baseline=context['task'], user_request=context['user_request'])
    # Only the runtime contract is shared with the actual input. The full
    # teaching candidate and all other inputs must come from rendered text.
    actual = json.JSONDecoder().raw_decode(prompt.split('\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n', 1)[1])[0]
    assert material['runtime_contract'] == actual['runtime_contract']
    compiled_review = prepare_review_material(material, context['raw_annotation'])
    assert context['target_index'] == {
        row['id']: {row['kind']: row['pointer']} for row in compiled_review['target_index']}
    for key in ('declaration_index', 'observations', 'source_line_universe'):
        assert context[key] == compiled_review[key]
    return prompt, shown, material, compiled_review


def test_complete_review_input_and_response_validate_from_sent_text_without_completion():
    prompt, shown, material, review = rendered_lesson()
    before = deepcopy(shown)
    response = validate_response(shown['response'], review)
    assert shown == before
    assert len(response.findings) == 2
    assert {f.domain for f in response.findings} == {'annotation'}
    assert task_objections(response) == []
    assert response.requirement_checks[0].finding_ids == ['F001', 'F002']
    supplied_goals = {g['raw_pointer'] for g in shown['context']['declaration_index']}
    assert {g.raw_pointer for g in response.declaration_checks} == supplied_goals
    issues = [g for g in response.declaration_checks if g.status == 'issue']
    assert len(issues) == 1 and issues[0].finding_ids == ['F001']
    assert all(g.finding_ids == [] for g in response.declaration_checks if g.status == 'accepted')
    assert all('target' not in evidence or 'events' not in evidence['target'].get('path', [])
               for finding in shown['response']['findings'] for evidence in finding['evidences'])
    for finding in shown['response']['findings']:
        for evidence in finding['evidences']:
            assert evidence_reference(evidence, material)['text']
    sections = re.findall(r'<!-- SKILLFLOW_PROMPT:([A-Z_]+):BEGIN -->', prompt)
    assert sections == ['AUTHORITY', 'INPUT', 'FORMAT', 'WORKFLOW', 'RULES', 'EXAMPLES', 'SELF_CHECK']
    assert prompt.count('REFERENCE SPACES (') == 1
    assert prompt.count('SHARED REPRESENTATION DECISIONS') == 1
    assert prompt.count('ENDPOINT DEMANDS.') == 1
    assert prompt.count('\nRESPONSE = ') == 1


def test_two_semantic_defects_remain_structurally_legal_not_automatically_repaired():
    example = endpoint_example()
    material = example_material(example)
    before = deepcopy(example)
    bad, _, _ = compile_response(example['contrast'], material)
    good, _, _ = compile_response(example['annotation'], material)
    assert bad != good and example == before
    prepared = prepare_review_material(material, bad)
    # An injected empty response is structurally legal, illustrating that
    # coverage/reference validation does not prove semantic detection.
    assert validate_response(empty_response(prepared), prepared).findings == []
    found = validate_response(review_examples()[0]['response'], prepared)
    assert len(found.findings) == 2
    assert task_objections(found) == []


def test_two_findings_route_to_one_fixed_task_repair_then_independent_review():
    example = endpoint_example()
    material = example_material(example)
    initial = deepcopy(example['contrast'])
    repaired = deepcopy(example['annotation'])
    reviews, repairs = [], []

    class Review:
        def complete(self, prompt):
            reviews.append(prompt)
            current = json.JSONDecoder().raw_decode(prompt.split('\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n', 1)[1])[0]
            return deepcopy(review_examples()[0]['response']) if len(reviews) == 1 else empty_response(current)

    class Repair:
        def complete(self, prompt):
            repairs.append(prompt)
            return deepcopy(repaired)

    class ForbiddenTaskRevision:
        def complete(self, prompt):
            raise AssertionError('These annotation errors must not revise the sealed Task')

    result = refine_annotation(material, initial, review_client=Review(), repair_client=Repair(),
                               task_repair_client=ForbiddenTaskRevision())
    assert result['status'] == 'review_passed'
    assert result['selected'] == 'repair' and result['task_revision'] is None
    assert result['counts']['logical_calls'] == 3
    assert result['counts']['structural_corrections'] == 0
    assert len(repairs) == 1 and len(reviews) == 2
    assert result['material']['task'] == material['task']
    assert initial == example['contrast']
    current = json.JSONDecoder().raw_decode(reviews[-1].split('\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n', 1)[1])[0]
    assert current['raw_annotation'] == result['raw_annotation']
    assert not {'repair_context', 'review_response', 'resolved_targets'} & current.keys()
    assert 'REPAIR_CONTEXT' in repairs[0]
