"""Propagation components enforce references without a second fact-file format."""
from copy import deepcopy
import runpy

import pytest
from skillflow.common.paths import project_root
from skillflow.propagation.facts import validate_propagation_facts, resolved_sink_boundaries
from skillflow.propagation.data import DataRegistry


def component_fixture():
    demo = runpy.run_path(str(project_root() / 'examples/propagation/propagation_demo.py'))
    registry = DataRegistry('components')
    data = registry.register_source('document', acquired_from='runtime_context:document')
    state = {'bindings': [{'location': {'kind': 'runtime_context', 'name': 'document'}, 'data_ids': [data.id]}]}
    cfg = {'entry_block_id': 'main', 'blocks': {'main': {'block_id': 'main', 'block_name': 'main', 'instructions': [
        {'id': 'ir_view', 'opcode': 'view', 'inputs': [{'type': 'literal', 'literal_value': 'document'}], 'outputs': []},
        {'id': 'ir_return', 'opcode': 'return', 'inputs': [], 'outputs': []}]}}, 'edges': []}
    cfg, annotation = demo['fixture_annotation'](cfg, {'view': (['model_observe'], [(0, [{
        'op': 'deliver', 'inputs': [{'kind': 'input', 'index': 0}], 'target': 'model'}])], [])},
        {'doc': ('runtime_context', 'document'), 'model': ('model_context', 'model')})
    annotation['locations']['doc']['operand_refs'] = [{'instruction_id': 'ir_view', 'side': 'input', 'index': 0}]
    records = {'ir_view': {'order': 'fixed', 'precedence': [], 'entry_state': deepcopy(state), 'exit_state': deepcopy(state), 'events': [
        {'effect': 'model_observe', 'atomic_ops': [{'op': 'deliver', 'inputs': [[data.id]], 'outputs': [],
            'endpoints': [{'kind': 'model_context', 'name': 'model'}], 'changes': []}]}]},
        'ir_return': {'order': 'fixed', 'precedence': [], 'entry_state': deepcopy(state), 'exit_state': deepcopy(state), 'events': []}}
    return {'cfg': cfg, 'annotation': annotation, 'data': [data.model_dump(mode='json')], 'records': records,
        'sinks': resolved_sink_boundaries(annotation['locations'], records), 'status': 'complete',
        'coverage': {'ir_view': 'processed', 'ir_return': 'processed'}, 'diagnostics': []}


def validate(value):
    return validate_propagation_facts(**value)


def test_components_contain_no_serialized_source_or_contract_copy():
    value = component_fixture()
    assert validate(value)['status'] == 'complete'
    assert set(value['records']['ir_view']) == {'order', 'precedence', 'entry_state', 'events', 'exit_state'}
    assert all(set(data) == {'id', 'content', 'origin', 'annotations'} for data in value['data'])


@pytest.mark.parametrize('mutation', ['data_missing', 'data_duplicate', 'unknown_ir', 'coverage_missing', 'record_missing',
    'false_complete', 'location_operand', 'endpoint', 'arity', 'old_ref', 'old_notes', 'unknown_result'])
def test_inconsistent_components_rejected(mutation):
    value = component_fixture(); op = value['records']['ir_view']['events'][0]['atomic_ops'][0]
    if mutation == 'data_missing': value['data'] = []
    if mutation == 'data_duplicate': value['data'].append(deepcopy(value['data'][0]))
    if mutation == 'unknown_ir': value['annotation']['ir_semantics']['ir_fake'] = value['annotation']['ir_semantics']['ir_return']
    if mutation == 'coverage_missing': del value['coverage']['ir_return']
    if mutation == 'record_missing': del value['records']['ir_return']
    if mutation == 'false_complete': del value['records']['ir_return']; value['coverage']['ir_return'] = 'not_solved'
    if mutation == 'location_operand': value['annotation']['locations']['doc']['operand_refs'][0]['index'] = 5
    if mutation == 'endpoint': op['endpoints'][0]['name'] = 'other-model'
    if mutation == 'arity': op['outputs'] = [op['inputs'][0]]
    if mutation == 'old_ref': op['inputs'][0] = {'ref': {'kind': 'input', 'index': 0}, 'data_ids': op['inputs'][0]}
    if mutation == 'old_notes': op['notes'] = ['old']
    if mutation == 'unknown_result': value['records']['ir_view']['entry_state']['bindings'][0]['location'] = {'kind': 'result', 'name': 'missing'}
    with pytest.raises(ValueError): validate(value)


def test_partial_order_is_computable_and_partial_coverage_remains_visible():
    value = component_fixture(); value['records']['ir_view']['order'] = 'partial'
    assert validate(value)['status'] == 'complete'
    value.update(status='incomplete', records={}, sinks=[], coverage={'ir_view': 'unresolved_binding', 'ir_return': 'not_reached'},
        diagnostics=[{'code': 'unresolved_binding', 'instruction_id': 'ir_view', 'reason': 'Input cannot resolve.'}])
    assert validate(value)['status'] == 'incomplete'


def test_repeated_slots_and_explicit_data_annotations_survive():
    value = component_fixture(); op = value['records']['ir_view']['events'][0]['atomic_ops'][0]
    op['inputs'] *= 2
    value['data'][0]['annotations'] = {'description': None, 'sensitivity': ['secret'], 'evidences': ['explicit:user']}
    validate(value)
    assert len(op['inputs']) == 2 and value['data'][0]['annotations']['evidences'] == ['explicit:user']


@pytest.mark.parametrize('mutation', ['missing', 'extra', 'target', 'type', 'grade', 'position', 'scope', 'duplicate', 'payload'])
def test_sink_inventory_is_exact(mutation):
    value = component_fixture(); item = value['sinks'][0]
    if mutation == 'missing': value['sinks'] = []
    if mutation == 'extra': value['sinks'].append({**item, 'instruction_id': 'ir_return'})
    if mutation == 'target': item['target'] = 'doc'
    if mutation == 'type': item['sink_type'] = 'external_tool'
    if mutation == 'grade': item['exposure_level'] = 1
    if mutation == 'position': item['op_index'] = 1
    if mutation == 'scope': item['body_event_index'] = 0; item['scope'] = 'element'
    if mutation == 'duplicate': value['sinks'].append(deepcopy(item))
    if mutation == 'payload': item['inputs'] = [[value['data'][0]['id']]]
    with pytest.raises(ValueError): validate(value)


@pytest.mark.parametrize('kind,scope,retention,effect,expected', [
    ('tool', 'task', None, None, None), ('tool', 'recipient', None, None, ('external_tool', 2)),
    ('storage', 'task', 'persistent', 'fs_write', ('storage_write', 1)), ('storage', 'task', 'task', 'fs_write', None),
    ('runtime_context', 'task', 'persistent', 'context_write', ('context_save', 1)),
    ('runtime_context', 'shared', 'task', 'context_write', ('context_save', 2)),
    ('storage', 'public', 'persistent', 'fs_write', ('storage_write', 3)),
    ('remote', 'recipient', None, 'net_send', ('network_send', 2)), ('user', 'recipient', None, 'user_output', ('user_output', 2))])
def test_boundary_rules_apply_to_evaluated_payload(kind, scope, retention, effect, expected):
    value = component_fixture()
    value['annotation']['locations']['target'] = {'kind': kind, 'name': 'destination', 'access_scope': scope,
                                               'retention': retention, 'operand_refs': []}
    event = value['records']['ir_view']['events'][0]; event['effect'] = effect
    op = event['atomic_ops'][0]; op['endpoints'] = [{'kind': kind, 'name': 'destination'}]
    if kind in {'storage', 'runtime_context'}:
        op['op'] = 'write'; op['changes'] = [{'location': deepcopy(op['endpoints'][0]), 'before': [], 'after': deepcopy(op['inputs'][0]), 'update': 'strong'}]
        value['records']['ir_view']['exit_state']['bindings'].append({'location': deepcopy(op['endpoints'][0]), 'data_ids': deepcopy(op['inputs'][0])})
    value['sinks'] = resolved_sink_boundaries(value['annotation']['locations'], value['records'])
    value['annotation']['sink_boundaries'] = deepcopy(value['sinks'])
    validate(value)
    assert [(s['sink_type'], s['exposure_level']) for s in value['sinks']] == ([] if expected is None else [expected])


@pytest.mark.parametrize('status,diagnostic', [('complete', {'code':'execution_error','reason':'failed'}), ('resource_limit',None), ('execution_error',None), ('incomplete',None)])
def test_status_and_diagnostics_cannot_hide_failure(status, diagnostic):
    value = component_fixture(); value.update(status=status, diagnostics=[] if diagnostic is None else [diagnostic])
    with pytest.raises(ValueError): validate(value)


def test_dynamic_missing_part_warning_retained():
    value = component_fixture()
    value['records']['ir_view']['events'][0] = {'effect':'transform', 'atomic_ops':[{'op':'select_part',
        'inputs':[[value['data'][0]['id']]],'outputs':[[value['data'][0]['id']]],'endpoints':[],'changes':[]}]}
    value['sinks'] = []
    value['diagnostics'] = [{'code':'missing_part','instruction_id':'ir_view','event_index':0,'op_index':0,
                           'data_id':value['data'][0]['id'],'reason':'A candidate excludes this field.'}]
    assert validate(value)['diagnostics'] == value['diagnostics']
    value['diagnostics'][0]['data_id'] = 'missing'
    with pytest.raises(ValueError, match='unknown Data'): validate(value)


def test_public_output_binding_required_but_omitted_cfg_defaults_allowed():
    value = component_fixture()
    del value['cfg']['blocks']['main']['instructions'][1]['inputs']
    del value['cfg']['blocks']['main']['instructions'][1]['outputs']
    validate(value)
    value['cfg']['blocks']['main']['instructions'][0]['outputs'] = [{'type':'result','identifier':'out'}]
    with pytest.raises(ValueError, match='public output binding'): validate(value)


def guarded_components(truth):
    value = component_fixture(); guard = deepcopy(value['data'][0]); guard['id'] = 'condition'
    guard['content'] = {'form':'opaque'} if truth is None else {'form':'literal','value':truth}
    value['data'].append(guard)
    op = value['records']['ir_view']['events'][0]['atomic_ops'][0]
    op['inputs'] = ([[value['data'][0]['id']]] if truth is not False else []) + [['condition']]
    op['when_input_index'] = len(op['inputs']) - 1
    value['sinks'] = resolved_sink_boundaries(value['annotation']['locations'], value['records'])
    return value


@pytest.mark.parametrize('truth', [True, False, None])
def test_condition_controls_same_payload_and_sink(truth):
    from skillflow.propagation.conditions import payload_inputs
    value = guarded_components(truth); validate(value)
    op = value['records']['ir_view']['events'][0]['atomic_ops'][0]
    assert len(value['sinks']) == int(truth is not False)
    assert payload_inputs(op) == ([[value['data'][0]['id']]] if truth is not False else [])


@pytest.mark.parametrize('mutation', ['bool_index','outside','wrong_effect','false_payload','true_empty','nonbool','missing_sink'])
def test_bad_conditions_and_fabricated_sink_rejected(mutation):
    value = guarded_components(False if mutation == 'false_payload' else True)
    op = value['records']['ir_view']['events'][0]['atomic_ops'][0]
    if mutation == 'bool_index': op['when_input_index'] = True
    if mutation == 'outside': op['when_input_index'] = 7
    if mutation == 'wrong_effect': value['records']['ir_view']['events'][0]['effect'] = None
    if mutation == 'false_payload': op['inputs'].insert(0,[value['data'][0]['id']]); op['when_input_index'] = 1
    if mutation == 'true_empty': op['inputs'] = [['condition']]; op['when_input_index'] = 0
    if mutation == 'nonbool': value['data'][-1]['content'] = {'form':'literal','value':1}
    if mutation == 'missing_sink': value['sinks'] = []
    with pytest.raises(ValueError): validate(value)
