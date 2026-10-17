from copy import deepcopy
import pytest
from pydantic import TypeAdapter, ValidationError
from skillflow.propagation.contracts.evidence import SpecEvidence
from skillflow.propagation.contracts.references import CFGTarget
from skillflow.common.validation import schema_error, diagnostic_materials


def diagnose(candidate, schema_type=SpecEvidence):
    adapter = TypeAdapter(schema_type)
    before = deepcopy(candidate)
    with pytest.raises(ValidationError) as caught:
        adapter.validate_python(candidate)
    output = diagnostic_materials(schema_error(caught.value, candidate=candidate,
                                               schema=adapter.json_schema()).diagnostics)
    assert candidate == before
    assert len(output['raw_diagnostics']) == len(caught.value.errors())
    assert sorted(item['raw_index'] for item in output['diagnostic_mapping']) == list(range(len(output['raw_diagnostics'])))
    return output


@pytest.mark.parametrize('target', [
    {'block_id': 'block_probe'},
    {'instruction_id': 'ir_probe', 'side': 'input', 'index': True},
    {'instruction_id': 'ir_probe', 'path': [False]},
    {'block_id': 'block_probe', 'path': [], 'unexpected': 'field'},
    {'path': [-1]},
])
def test_nested_cfg_target_has_one_actual_target_diagnostic(target):
    result = diagnose({'target': target, 'reason': 'Existing CFG correspondence.'})
    assert len(result['diagnostics']) == 1
    row = result['diagnostics'][0]
    assert row['path'] == '/target'
    assert len(row['context']['allowed_forms']) == 4
    assert row['context']['current'] == target
    assert all(item['candidate_path'] == '/target' for item in result['diagnostic_mapping'])
    assert not any(item['path'] in {'/file', '/start_line', '/end_line'}
                   for item in result['diagnostics'])


def test_reversed_source_span_retains_its_specific_validator_constraint():
    result = diagnose({'file':'skill/SKILL.md','start_line':3,'end_line':1,'reason':'Source support.'})
    assert len(result['diagnostics']) == 1
    row = result['diagnostics'][0]
    assert row['path'] == ''
    assert any('end_line precedes start_line' in issue['message']
               for issue in row['context']['violations'])


def test_mixed_evidence_does_not_choose_or_rewrite_a_basis():
    result = diagnose({'file':'skill/SKILL.md','start_line':1,'end_line':1,
                       'target':{'block_id':'block_probe','path':[]},'reason':'Claim.'})
    assert len(result['diagnostics']) == 1
    row = result['diagnostics'][0]
    assert row['path'] == '' and len(row['context']['allowed_forms']) == 3
    assert 'violations' not in row['context']
    assert 'file' in row['context']['current'] and 'target' in row['context']['current']


def test_standalone_cfg_union_preserves_four_forms_and_original_errors():
    result = diagnose({'block_id':'block_probe'}, CFGTarget)
    assert len(result['diagnostics']) == 1
    assert len(result['diagnostics'][0]['context']['allowed_forms']) == 4


def test_large_evidence_context_keeps_the_same_nested_target_focus():
    result = diagnose({'target':{'block_id':'block_probe'}, 'reason':'Long existing claim. ' * 90})
    assert len(result['diagnostics']) == 1
    assert result['diagnostics'][0]['path'] == '/target'
