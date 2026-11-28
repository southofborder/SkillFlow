"""Authored offline teaching slice. No model, HTTP, or Skill execution."""
from pathlib import Path
import hashlib
import json
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'src'))
from skillflow.common.source_evidence import _digest
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.task import validate_task_candidate, task_source_files
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.solver import propagate
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.loading import materials_from_result
from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.propagation.contracts.demand import validate_demand_candidate

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / 'source-package'

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def ev(start=6, end=14):
    return {'file': 'skill/scripts/search.py', 'start_line': start, 'end_line': end,
            'reason': 'Manually authored teaching correspondence to the original source; not an online annotation.'}

def inp(i=0): return {'kind':'input', 'index':i}
def local(n): return {'kind':'local', 'name':n}
def lit(v): return {'kind':'literal', 'value':v}
def operand(kind, value): return {'type':kind, 'identifier':value}

def main():
    files = [{'path':p.relative_to(SOURCE).as_posix(), 'content':p.read_text(encoding='utf-8'),
              'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(SOURCE.rglob('*')) if p.is_file()]
    source = {'files':files, 'source_sha256':_digest([{k:r[k] for k in ('path','sha256')} for r in files])}
    task = validate_task_candidate({'purpose':{'text':'Preserve the Google search request in this explicitly scoped teaching slice.',
        'evidences':[ev()]}, 'requirements':[{'id':'R_search',
        'text':'Send the requested query and the supplied API key and search-engine ID to the Custom Search endpoint.',
        'evidences':[ev(),ev(26,28)]}], 'issues':[]},
        source_files=task_source_files(source), source_sha256=source['source_sha256'])
    irs=[]
    def ir(name, opcode, inputs=(), outputs=()):
        row={'id':name,'opcode':opcode,'inputs':list(inputs),
             'outputs':[operand('result',o) for o in outputs], 'constraints':[], 'metadata':{}}
        irs.append(row)
        return row
    for name in ('key','cx','q'):
        ir('ir_'+name, 'read_'+name, [operand('external_resource',name)], [name])
    ir('ir_params','build_search_params',[operand('result',n) for n in ('q','key','cx')],['params'])
    ir('ir_call','request_google',[operand('result','params'),operand('external_resource','https://www.googleapis.com/customsearch/v1')],['response'])
    ir('ir_return','return',[operand('result','response')])
    cfg={'entry_block_id':'main','blocks':{'main':{'block_id':'main','block_name':'Authored successful request teaching slice',
        'instructions':irs,'constraints':[],'data_source_kind':None}},'edges':[], 'constraints':[], 'declared_context_keys':[]}
    material=prepare_material(source,cfg,task_baseline=task)
    locations={n:{'kind':'runtime_context','name':{'key':'GOOGLE_API_KEY','cx':'GOOGLE_CSE_ID','q':'argv.query'}[n],
        'operand_refs':[], 'access_scope':'task','retention':'task'} for n in ('key','cx','q')}
    locations['google']={'kind':'remote','name':'https://www.googleapis.com/customsearch/v1',
        'operand_refs':[{'instruction_id':'ir_call','side':'input','index':1}], 'access_scope':'recipient','retention':None}
    def op(**kw): return {**kw,'evidences':[ev()]}
    def event(effect, ops): return {'effect':effect,'atomic_ops':ops,'evidences':[ev()]}
    def spec(events, output=None):
        return {'operator':['agent_runtime'],'operator_evidences':[{'value':'agent_runtime',**ev()}],
            'order':'fixed','events':[{'kind':'processing','mode':'local','returns':[], 'events':events,'evidences':[ev()]}],
            'output_bindings':[] if output is None else [{'output_index':0,'value':local(output),'evidences':[ev()]}],
            'sensitivity':[]}
    specs={}
    for name in ('key','cx','q'):
        specs['ir_'+name]=spec([event('context_read',[op(op='read',location=name,output=name)])],name)
    specs['ir_key']['sensitivity']=[{'value':local('key'),'path':[],'property':'value',
        'label':'authentication credential','evidences':[ev(26,28)]}]
    specs['ir_params']=spec([event('transform',[op(op='build',container='object', parts=[
        {'path':[name], 'value':inp(i)} for i,name in enumerate(('q','key','cx'))]+[
        {'path':['num'],'value':lit(5)}],output='params')])],'params')
    specs['ir_call']=spec([event('net_send',[op(op='deliver',inputs=[inp()],target='google',request_id='search')]),
        event('net_receive',[op(op='receive',inputs=[inp()],location='google',output='response',request_id='search')])],'response')
    specs['ir_return']={'operator':['agent_runtime'],'operator_evidences':[{'value':'agent_runtime',**ev()}],
        'order':'fixed','events':[],'output_bindings':[],'sensitivity':[], 'empty_effect_evidences':[ev()]}
    raw={'outcome':'completed','task_revision_id':task.task_sha256,'ir_semantics':specs,
        'locations':locations,'location_evidences':{k:[ev()] for k in locations},
        'realizations':[{'requirement_id':'R_search','status':'expressed','bindings':[],'gaps':[]}],
        'demands':[{'requirement_id':'R_search','target':{'instruction_id':'ir_call','side':'input','index':0},
            'preserve':'value','path':[name],'reason':'Authored request-field preservation seed for this teaching slice.'}
            for name in ('q','key','cx')], 'expressions':[]}
    save('scope.json',{'kind':'hand_authored_offline_teaching_slice','not_online_annotation':True,
        'model_calls':0,'skill_executions':0,'http_requests':0,
        'source_sha256':source['source_sha256'], 'source_files':[{k:r[k] for k in ('path','sha256')} for r in files],
        'task_note':'R_search is an authored scoped requirement; it is not online R6. Online R6 concerns supplying env credentials.',
        'omissions':['input-validation exits','HTTP status/exception construction','stdout','source review','final DOE verdict'],
        'seed_note':'Request q/key/cx necessities are manually supplied preservation goals, not inferred or independently source-reviewed interface contracts.',
        'concrete_values':'All values below are artificial public placeholders; no environment values are read.'})
    save('task.json',task.model_dump(mode='json')); save('cfg.json',cfg); save('authored-raw-annotation.json',raw)
    checked,compiled,mapping=compile_response(raw,material)
    save('compiled-annotation.json',compiled); save('compilation-mapping.json',mapping)
    registry=DataRegistry('google-search-offline-teaching')
    state={}
    for name,value in {'key':'DEMO_API_KEY_NOT_A_SECRET','cx':'DEMO_CSE_ID','q':'OpenClaw documentation'}.items():
        data=registry.register_source(name, acquired_from=locations[name]['name'],at='public teaching input',content=LiteralContent(value=value))
        state[FlowLocation(kind='runtime_context',name=locations[name]['name'])]=frozenset([data.id])
    solved=propagate(cfg,to_payload(compiled),initial_registry=registry,initial_state=FlowState.from_mapping(state))
    save('propagation.json',{'status':solved.status,'coverage':solved.coverage,'diagnostics':solved.diagnostics,
        'records':solved.records.records_dict(),'data_registry':solved.registry.to_dict()})
    facts=materials_from_result(solved,material=material,raw_annotation=checked,compiled_annotation=compiled,mapping=mapping)
    targets=build_demand_target_index(cfg,checked)
    save('demand-targets.json',targets)
    target=next(row['target'] for row in targets.values() if row['kind']=='input_use' and row['instruction_id']=='ir_call'
        and row['target']['operation_path']==['events',0,'events',0,'atomic_ops',0] and row['slot']==0)
    candidate={'goals':[{'id':'G_'+name,'requirement_id':'R_search','preserve':'value','path':[name],
        'target':target,'reason':'Authored request-field preservation seed.'} for name in ('q','key','cx')], 'expressions':[]}
    requested=validate_demand_candidate(candidate,task,task_source_files(source),targets)
    save('authored-boundary-goals.json',requested.model_dump(mode='json'))
    engine=DemandEngine(facts,task,facts.annotation,requested.model_dump(mode='json'),targets)
    backward=engine.solve(); save('backward-demands.json',backward)
    bindings={}
    params_id=next(iter(solved.records.get('ir_params').exit_state.get(FlowLocation(kind='result',name='params'))))
    for name in ('q','key','cx','num'):
        vals=solved.registry.resolve_part_candidates(params_id,[name])
        bindings[name]=[v.model_dump(mode='json') for v in vals]
    key_rows={k:r for k,r in backward['derivations'].items() if r.get('seed_goal_id')=='G_key'}
    ordered_key=[]
    remaining=dict(key_rows)
    while remaining:
        ready=[k for k,r in remaining.items() if all(parent not in remaining for parent in r['parents'])]
        if not ready: raise AssertionError('Unexpected cycle in this linear teaching derivation')
        for k in sorted(ready):
            ordered_key.append({'id':k,**remaining.pop(k)})
    sink=backward['sinks'][0]
    sink_paths={tuple(backward['derivations'][k]['path']) for k in sink['demanded_information']}
    assert solved.status=='complete' and not solved.diagnostics
    assert sink_paths=={('q',),('key',),('cx',)}
    assert bindings['key'][0]['origin']['acquired_from']=='GOOGLE_API_KEY'
    assert bindings['key'][0]['content']['value']=='DEMO_API_KEY_NOT_A_SECRET'
    assert any(r['node']['instruction_id']=='ir_params' and r['node']['kind']=='op_input'
        and r['node']['slot']==1 and r['node']['data_ids']==[bindings['key'][0]['id']] for r in ordered_key)
    checks={'forward_complete':True,'diagnostics_empty':True,'exact_request_field_needs':['q','key','cx'],
        'params_key_is_original_env_key_identity':True,'build_slot_1_demands_the_key_value':True,
        'key_need_chain_nodes':len(ordered_key),'source_scoped_sensitivity':specs['ir_key']['sensitivity'],
        'unestablished_remainder':sink['unestablished_ranges']}
    save('checks.json',checks)
    summary={'status':'offline_teaching_slice_completed','forward_status':solved.status,'backward_status':backward['status'],
        'parameter_data_id':params_id,'parameter_fields':bindings,
        'backward_rule_counts':dict(Counter(rule for r in backward['derivations'].values() for rule in r['rules'])),
        'boundary_sinks':facts.sinks,'key_need_derivations':ordered_key,'checks':checks,
        'not_established':['automatic online semantic modeling','source-reviewed interface necessity','exception/stdout credential disclosure','DOE excess or reduction verdict']}
    save('summary.json',summary)
    online_task=ROOT/'experiments/doe/runs/document-guided-google-search-meeting-high-20261125-154844/task/task.json'
    original=json.loads(online_task.read_text(encoding='utf-8'))
    save('online-R6-reference-only.json',{'kind':'read_only_copy_of_extracted_requirement',
        'online_task_path':str(online_task),'task_sha256':original['task_sha256'],
        'requirement':next(r for r in original['requirements'] if r['id']=='R6'),
        'note':'Provenance reference only. This requirement does not itself state the request fields; the teaching run uses separately authored R_search and boundary goals.'})
    print(json.dumps({'forward_status':solved.status,'fields':list(bindings),'derivations':len(backward['derivations']),
        'sinks':len(facts.sinks),'output':str(OUT)},ensure_ascii=False))

if __name__=='__main__':
    main()
