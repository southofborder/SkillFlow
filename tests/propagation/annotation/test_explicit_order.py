"""Explicit calculable order and observation causality; no semantic oracle."""
from copy import deepcopy
import pytest

from skillflow.propagation.data import DataRegistry
from skillflow.propagation import propagate
from skillflow.propagation.interpreter import TransferInterpreter
from skillflow.propagation.contracts.specs import IRTransferSpec
from skillflow.propagation.contracts.specs import precedence_closure
from skillflow.propagation.contracts.specs import schedule_dependencies
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.annotation.services import validate_raw_response
from skillflow.propagation.annotation.services import validate_compiled_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.common.semantic_failure import SemanticFailure
from tests.propagation.annotation.helpers import material, valid_raw_response, profile


def candidate():
    prepared = material()
    raw = valid_raw_response(prepared)
    raw['transfer_specs']['ir_filter']['events'][0]['mode'] = 'default'
    return prepared, raw


def test_partial_observation_causality_is_explicit_and_survives_propagation():
    prepared, raw = candidate()
    for spec in raw['transfer_specs'].values():
        spec['order'] = 'partial'
    raw['transfer_specs']['ir_read']['events'][0]['mode'] = 'default'
    checked, compiled, mapping = compile_response(raw, prepared)
    assert mapping['compiler_version'].endswith('-v4')
    for ir, before, after in [('ir_read', (0,None,0), (1,None,0)),
                              ('ir_filter', (0,None,0), (1,None,0))]:
        spec = IRTransferSpec.model_validate(compiled['transfer_specs'][ir])
        assert after in precedence_closure(spec)[before]
        assert spec.precedence
    result = propagate(prepared['cfg'], to_payload(compiled))
    assert result.status == 'complete', result.diagnostics
    assert result.records.get('ir_filter').order == 'partial'
    assert result.records.get('ir_filter').precedence == IRTransferSpec.model_validate(compiled['transfer_specs']['ir_filter']).precedence
    assert not result.diagnostics


def test_local_returns_after_every_operation_without_original_observation():
    prepared, raw = candidate()
    spec = raw['transfer_specs']['ir_filter']
    spec['order'] = 'partial'
    segment = spec['events'][0]
    segment['mode'] = 'local'
    segment['returns'] = [{'kind':'local','name':'stage_0'}]
    first = segment['events'][0]['atomic_ops'][0]
    second = deepcopy(first)
    second.update(inputs=[{'kind':'literal','value':1}], output='irrelevant')
    segment['events'][0]['atomic_ops'].append(second)
    _, compiled, _ = compile_response(raw, prepared)
    spec = IRTransferSpec.model_validate(compiled['transfer_specs']['ir_filter'])
    closure = precedence_closure(spec)
    assert (1,None,0) in closure[(0,None,1)]
    assert compiled['profiles']['ir_filter']['effects'] == ['transform','model_observe']
    assert spec.events[1].atomic_ops[0].inputs[0].name == 'stage_0'


def test_partial_segments_interleave_at_primitive_operations():
    prepared, raw = candidate()
    spec = raw['transfer_specs']['ir_filter']
    spec['order'] = 'partial'
    segment = spec['events'][0]
    segment['mode'] = 'local'
    first = segment['events'][0]['atomic_ops'][0]
    first['inputs'] = [{'kind':'literal','value':1}]
    first['output'] = 'a1'
    second = deepcopy(first); second['output'] = 'a2'
    segment['events'][0]['atomic_ops'].append(second)
    other = deepcopy(segment)
    other['events'][0]['effect_index'] = 1
    other['events'][0]['atomic_ops'] = [deepcopy(first)]
    other['events'][0]['atomic_ops'][0]['output'] = 'b'
    spec['events'].append(other)
    spec['output_bindings'][0]['value'] = {'kind':'local','name':'a2'}
    raw['profiles']['ir_filter'] = profile(prepared,'ir_filter', operator=['agent_runtime'], roles=['transformer'], effects=['transform','transform'])
    _, compiled, _ = compile_response(raw, prepared)
    typed = IRTransferSpec.model_validate(compiled['transfer_specs']['ir_filter'])
    deps = schedule_dependencies(typed)
    assert deps[(0,1)] == {(0,0)} and not deps[(1,0)]
    interpreter = TransferInterpreter(prepared['cfg'],to_payload(compiled),DataRegistry('interleaving'))
    interpreter._current_spec = typed
    interpreter._attempts = 0
    interpreter._failed_diagnostics = []
    original = interpreter.execute
    def track(ir,e,o,operation,state,locals_,**kw):
        result = original(ir,e,o,operation,state,locals_,**kw)
        locals_['__trace__'] = (*locals_.get('__trace__',()),operation.output)
        return result
    interpreter.execute = track
    ir = prepared['cfg']['blocks']['entry']['instructions'][1]
    arrangements = interpreter._arrangements(ir, typed.events, {}, {}, uncertain=True)
    assert {out[1]['__trace__'] for out in arrangements} == {('a1','a2','b'),('a1','b','a2'),('b','a1','a2')}


@pytest.mark.parametrize('mutation',['duplicate','nonexistent','cycle','bool','reversed_fixed'])
def test_compiled_precedence_rejects_illegal_coordinates(mutation):
    prepared, raw = candidate()
    _, compiled, _ = compile_response(raw,prepared)
    spec = compiled['transfer_specs']['ir_filter']
    edge = spec['precedence'][0]
    if mutation=='duplicate': spec['precedence'].append(deepcopy(edge))
    if mutation=='nonexistent': edge['after']['op_index']=99
    if mutation=='bool': edge['before']['event_index']=True
    if mutation=='cycle': spec['order']='partial'; spec['precedence'].append({'before':edge['after'],'after':edge['before']})
    if mutation=='reversed_fixed': edge['before'],edge['after']=edge['after'],edge['before']
    with pytest.raises(ValueError): validate_compiled_response(compiled,prepared)


@pytest.mark.parametrize('field',['order','outcome'])
def test_required_order_and_outcome_cannot_be_omitted(field):
    prepared, raw = candidate()
    if field=='order': raw['transfer_specs']['ir_filter'].pop('order')
    else: raw.pop('outcome')
    with pytest.raises(ValueError): validate_raw_response(raw,prepared)


def test_semantic_failure_is_separate_validated_and_never_completed():
    prepared, raw = candidate()
    evidence = raw['transfer_specs']['ir_filter']['events'][0]['evidences']
    failure = {'outcome':'cannot_assess','failure':{'reason':'必要关系超出当前可表达边界。','instruction_ids':['ir_filter'],'evidences':evidence}}
    with pytest.raises(SemanticFailure): validate_raw_response(failure,prepared)
    for change in ['quote','id','normal_fields']:
        altered=deepcopy(failure)
        if change=='quote': altered['failure']['evidences'][0]['quote']='fabricated'
        if change=='id': altered['failure']['instruction_ids']=['absent']
        if change=='normal_fields': altered['profiles']={}
        with pytest.raises(ValueError): validate_raw_response(altered,prepared)


@pytest.mark.parametrize('scoped',[False,True])
def test_standalone_record_partial_order_rejects_reverse_atomic_list_order(scoped):
    from skillflow.propagation.models import IRFlowRecord
    from skillflow.propagation.models import EffectEvent
    from skillflow.propagation.models import AtomicOpRecord
    from skillflow.propagation.models import FlowState
    from skillflow.propagation.models import ForEachRecord
    from skillflow.propagation.models import ForEachInstance
    effect=EffectEvent(effect='transform',atomic_ops=[AtomicOpRecord(op='compute'),AtomicOpRecord(op='compute')])
    events=[ForEachRecord(kind='for_each',collections=frozenset(['collection']),instances=[ForEachInstance(collection='collection',element='member',body=[effect])])] if scoped else [effect]
    body=0 if scoped else None
    reverse={'before':{'event_index':0,'body_event_index':body,'op_index':1},
             'after':{'event_index':0,'body_event_index':body,'op_index':0}}
    with pytest.raises(ValueError,match='cyclic'):
        IRFlowRecord(order='partial',precedence=[reverse],entry_state=FlowState(),exit_state=FlowState(),events=events)
