"""Terminal analysis audit from saved JSON/source only; no project execution."""
from collections import Counter
from datetime import datetime, timezone
import ast
import json
import re
from audit_processing_material_v12 import ROOT, VERIFY, RUN, read, sha, compact
from audit_processing_first_response import walk


def operations(record):
    for event_index, event in enumerate(record.get('events', [])):
        for op_index, op in enumerate(event.get('atomic_ops', [])):
            yield {'event_index':event_index,'op_index':op_index},op
        for instance_index, instance in enumerate(event.get('instances', [])):
            for body_event_index, body in enumerate(instance.get('body', [])):
                for op_index,op in enumerate(body.get('atomic_ops', [])):
                    yield {'event_index':event_index,'instance_index':instance_index,'body_event_index':body_event_index,'op_index':op_index},op


def main():
    result=read(RUN/'result.json');selection=read(RUN/'selection.json')
    propagation=read(RUN/'propagation/manifest.json');records=read(RUN/'propagation/records.json')
    data={row['id']:row for row in read(RUN/'propagation/data.json')}
    support=read(RUN/'doe/audit/demand-support.json');doe=read(RUN/'doe/doe-result.json')
    receipt=read(RUN/'audit/input-contract-review.json');review=read(RUN/'review/result.json')
    raw=read(RUN/'steps/processing/value.json');compiled=read(RUN/'annotation/audit/compiled-response.json')
    cfg=read(RUN/'graph/selected.json')['cfg'];irs={x['id']:x for b in cfg['blocks'].values() for x in b['instructions']}
    wire_raw=read(RUN/'inherited/steps/graph/calls/a001/response.json');wire=json.loads(wire_raw) if isinstance(wire_raw,str) else wire_raw
    wire_rows=[]
    for block in wire['blocks']:
        for instruction in block['instructions']:
            iid=f'ir_{len(wire_rows)+1:03d}'
            assert iid in irs and irs[iid]['opcode']==instruction['opcode']
            wire_rows.append({'instruction_id':iid,'data_source_kind':block.get('data_source_kind'),**instruction})
    assert len(wire_rows)==len(irs)==489
    snapshot=read(RUN/'source/inputs/snapshot.json')
    sources={};source_refs=[]
    for row in snapshot['files']:
        path=RUN/'source/inputs/package'/row['path'];content=path.read_bytes()
        assert sha(content)==row['raw_sha256']
        sources['skill/'+row['path']]=content.decode('utf-8')
        source_refs.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(content),'bytes':len(content)})
    def matches(file,line,predicate):
        return [row for row in wire_rows if predicate(row)
            and (span:=row.get('metadata',{}).get('_source_span',{})).get('file')==file
            and span.get('start_line',0)<=line<=span.get('end_line',0)]
    remote_pattern=re.compile(r'\bawait\s+\w+\.(runReport|runRealtimeReport|getMetadata|searchanalytics\.query|urlNotifications\.publish|urlInspection\.index\.inspect)\s*\(')
    fs_ops={'existsSync':'acquire_path_existence','mkdirSync':'create_category_directory','writeFileSync':'write_file',
        'readFileSync':'acquire_file_content_or_read_exception','readdirSync':'acquire_directory_entries'}
    boundaries={'remote':[],'save':[],'filesystem':[]}
    def add(kind,file,line,text,method,found):
        row={'file':file,'line':line,'source_line':text,'method':method,'ir_ids':[x['instruction_id'] for x in found],
            'coverage':{x['instruction_id']:propagation['coverage'][x['instruction_id']] for x in found},'actions':[],'processing_calls':[]}
        for entry in found:
            ir=entry['instruction_id'];spec=raw['ir_semantics'].get(ir,{})
            for pointer,op in walk(spec):
                if isinstance(op,dict) and op.get('op')=='call':
                    loc=raw['locations'][op['location']]
                    row['processing_calls'].append({'instruction_id':ir,'pointer':'/ir_semantics/'+ir+pointer,
                        'location':{k:loc[k] for k in ('kind','name')},'inputs':op['inputs'],'output':op['output']})
            for position,op in operations(records.get(ir,{})):
                if op.get('endpoints'):
                    row['actions'].append({'instruction_id':ir,**position,'op':op['op'],'endpoints':op['endpoints'],
                        'inputs':op['inputs'],'outputs':op['outputs'],'alternative_count':len(op.get('alternatives',[]))})
        row['has_recorded_boundary']=any((kind!='remote' or any(e['kind']=='remote' for e in op['endpoints']))
            and (kind!='save' or op['op']=='write' and any(e['kind']=='storage' for e in op['endpoints'])) for op in row['actions'])
        row['is_source_faithful_boundary_proven']=False
        row['faithfulness_note']='Recorded endpoint presence does not establish exact source receiver, addressing, payload, condition, pairing or necessity. The selected review retains material findings.'
        if kind=='remote':
            row['local_client_getters'] = []
            for call in row['processing_calls']:
                if 'getClient:' not in call['location']['name']:
                    continue
                owner_spec = raw['ir_semantics'][call['instruction_id']]
                uses = ['/ir_semantics/'+call['instruction_id']+pointer for pointer, value in walk(owner_spec)
                    if isinstance(value, dict) and value.get('kind') == 'local' and value.get('name') == call['output']]
                row['local_client_getters'].append({'producer_pointer': call['pointer'], 'output': call['output'],
                    'local_value_reference_paths': uses})
            row['explicit_cfg_client_inputs']=[{'instruction_id':x['instruction_id'],'input_index':i,**operand}
                for x in found for i,operand in enumerate(irs[x['instruction_id']]['inputs']) if operand['type']=='result' and 'client' in operand.get('semantic_name','').lower()]
            direct=[]
            for client in row['explicit_cfg_client_inputs']:
                entries=records.get(client['instruction_id'],{}).get('entry_state',{}).get('bindings',[])
                ids=set().union(*(set(b['data_ids']) for b in entries if b['location']=={'kind':'result','name':client['identifier']}))
                used={v for op in row['actions'] if any(e['kind']=='remote' for e in op['endpoints']) for slot in op['inputs'] for v in slot}
                direct.append({'instruction_id':client['instruction_id'],'input_index':client['input_index'],'entry_client_data_ids':sorted(ids),'direct_remote_input_intersection':sorted(ids&used)})
            row['direct_client_record_checks']=direct
        boundaries[kind].append(row)
    for file,text in sources.items():
        if not file.endswith('.ts'):continue
        for line,content in enumerate(text.splitlines(),1):
            if found:=remote_pattern.search(content):
                add('remote',file,line,content,found[1],matches(file,line,lambda row:row['data_source_kind']=='external' and bool(row.get('outputs'))))
            if re.search(r'\bsaveResult\s*\(',content) and not re.search(r'\bfunction\s+saveResult',content):
                add('save',file,line,content,'saveResult',matches(file,line,lambda row:row['opcode']=='save_result'))
            if file.endswith('/core/storage.ts'):
                for method,opcode in fs_ops.items():
                    if re.search(r'\b'+method+r'\s*\(',content):
                        add('filesystem',file,line,content,method,matches(file,line,lambda row:row['opcode']==opcode))
    assert {k:len(v) for k,v in boundaries.items()}=={'remote':13,'save':25,'filesystem':7}
    missing=[]
    for diagnostic in propagation['diagnostics']:
        if diagnostic['code']!='missing_part':continue
        ir=diagnostic['instruction_id'];base=data[diagnostic['data_id']]
        parent='ir_456' if ir=='ir_457' else 'ir_458'
        branches=[{'position':position,'record':op} for position,op in operations(records[parent]) if op['op']=='branch']
        fields={str(part['path']):data[part['data']]['content'] for part in base['content'].get('parts',[]) if 'data'in part}
        missing.append({'diagnostic':diagnostic,'cfg_instruction':irs[ir],'processing_spec':raw['ir_semantics'][ir],
            'error_base':base,'known_field_contents':fields,'guard_ir':parent,'guard_processing_spec':raw['ir_semantics'][parent],
            'guard_branches':branches,'consumer_entry_state':records[ir]['entry_state'],
            'consumer_operations':[{'position':p,'op':op['op'],'inputs':op['inputs'],'outputs':op['outputs'],'alternatives':len(op.get('alternatives',[]))} for p,op in operations(records[ir])],
            'coverage':propagation['coverage'][ir],
            'demand_diagnostics':[x for x in support['diagnostics'] if x.get('instruction_id')==ir],
            'assessment_range_statuses':dict(Counter(x['status'] for a in support['input_assessments'] if a['instruction_id']==ir for x in a['ranges']))})
    assessments=support['input_assessments'];deletions=[{'assessment_id':a['id'],'instruction_id':a['instruction_id'],'node_kind':a['node_kind'],'range':x}
        for a in assessments for x in a['ranges'] if x['status']=='deletable']
    globals_=[x for x in support['diagnostics'] if x.get('instruction_id') is None and x.get('blocking')]
    output_gaps=[x for x in support['diagnostics'] if x['code']=='input_contract_output_gap']
    output_selectors=[ast.literal_eval(x['reason'].split('No rule covers output selector ',1)[1].split(' with exclusions ',1)[0]) for x in output_gaps]
    refs=[]
    names=['result.json','selection.json','graph/selected.json','steps/processing/value.json','annotation/manifest.json',
        'annotation/audit/compiled-response.json','propagation/manifest.json','propagation/records.json','propagation/data.json',
        'propagation/audit/stats.json','doe/doe-result.json','doe/audit/demand-support.json','audit/input-contract-review.json',
        'review/result.json','audit/shared-repair-decision.json','inherited/steps/graph/calls/a001/response.json',
        'inherited/task/task.json','revision/task/task.json']
    for name in names:
        b=(RUN/name).read_bytes();refs.append({'path':(RUN/name).relative_to(ROOT).as_posix(),'bytes':len(b),'sha256':sha(b)})
    for name in ['src/skillflow/propagation/solver.py','src/skillflow/propagation/interpreter.py','src/skillflow/doe/demand_engine.py','src/skillflow/doe/input_assessments.py','src/skillflow/doe/input_contract_review.py']:
        b=(ROOT/name).read_bytes();refs.append({'path':name,'bytes':len(b),'sha256':sha(b)})
    affected={row['diagnostic']['instruction_id'] for row in missing}
    binding_report=read(VERIFY/'correction-finding-origin-audit.json')
    wrong_bindings=[t['target'].split('/')[2] for f in binding_report['findings'] for t in f['targets'] if t['classification']=='response_to_date_range_binding_change']
    # Target begins annotation:/ir_semantics/<IR>/..., hence index two is IR.
    report={'audit':'terminal_analysis_passive_backend_and_source','created_utc':datetime.now(timezone.utc).isoformat(),
        'run_directory':RUN.relative_to(ROOT).as_posix(),'method':'Saved JSON, source text and code reads only; no project imports or computation replay.',
        'artifact_references':refs,'source_files':source_refs,'selection':selection,
        'task_selection': {'selected_requirement_count':len(read(RUN/selection['task']['path'])['requirements']),
            'revised_requirement_count':len(read(RUN/'revision/task/task.json')['requirements']),
            'revised_task_selected':selection['task']['path']=='revision/task/task.json'},
        'selection_hash_matches':{k:sha((RUN/v['path']).read_bytes())==v['sha256'] for k,v in selection.items()},
        'terminal_analysis_result':result,
        'propagation':{'status':propagation['status'],'coverage_counts':dict(Counter(propagation['coverage'].values())),
            'coverage_nonprocessed':{k:v for k,v in propagation['coverage'].items() if v!='processed'},
            'record_count':len(records),'data_count':len(data),'diagnostics':propagation['diagnostics'],
            'typed_operation_fault_count':sum(x['code']=='operation_execution_error' for x in propagation['diagnostics']),
            'missing_part_cases':missing,'previous_url_path_current_coverage':{x:propagation['coverage'][x] for x in ['ir_148','ir_151']},
            'wrong_output_binding_coverage':{x:propagation['coverage'][x] for x in wrong_bindings}},
        'source_boundaries':boundaries,'source_boundary_counts':{kind:{'physical_sites':len(rows),
            'single_cfg_site_matches':sum(len(x['ir_ids'])==1 for x in rows),'sites_with_recorded_boundary':sum(x['has_recorded_boundary'] for x in rows),
            'coverage_states':dict(Counter(v for row in rows for v in row['coverage'].values()))} for kind,rows in boundaries.items()},
        'review':{'status':receipt['review_status'],'source_review_complete':receipt['source_review_complete'],
            'core_partial':receipt['review_core']['partial'],'core_availability':receipt['review_core']['availability'],
            'check_count':len(receipt['checks']),'check_statuses':dict(Counter(x['status'] for x in receipt['checks'])),
            'scope_count':len(receipt['review_core']['scope_decisions']),
            'scope_statuses':dict(Counter(x['status'] for x in receipt['review_core']['scope_decisions'].values())),
            'findings':len(receipt['review_core']['findings']),'validation_barriers':receipt['review_core']['validation_barriers'],
            'receipt_sha256':receipt['receipt_sha256'],'demand_receipt_matches':support['input_contract_review_sha256']==receipt['receipt_sha256']},
        'demand':{'status':support['status'],'assessments':len(assessments),'assessment_node_kinds':dict(Counter(x['node_kind'] for x in assessments)),
            'assessment_coverage':dict(Counter(x['coverage'] for x in assessments)),
            'range_statuses':{s:sum(x['status']==s for a in assessments for x in a['ranges']) for s in ['required','unresolved','deletable']},
            'range_statuses_by_kind':{k:dict(Counter(x['status'] for a in assessments if a['node_kind']==k for x in a['ranges'])) for k in ['ir_input','op_input','acquisition_output']},
            'deletable_ranges':deletions,'non_null_modifications':sum(x.get('modification') is not None for a in assessments for x in a['ranges']),
            'input_findings':support['input_findings'],'diagnostic_counts':dict(Counter(x['code'] for x in support['diagnostics'])),
            'diagnostic_total':len(support['diagnostics']),
            'diagnostic_scope_counts':dict(Counter('global' if x.get('instruction_id') is None else 'IR_scoped' for x in support['diagnostics'])),
            'global_blocking_diagnostics':globals_,'global_blocking_count':len(globals_),
            'realization_statuses':dict(Counter(x['status'] for x in support['coverage']['requirements'].values())),
            'output_contract_gaps':output_gaps,'output_contract_gap_ir_count':len({x['instruction_id'] for x in output_gaps}),
            'output_gap_selector_properties':dict(Counter(x['property'] for x in output_selectors)),
            'output_gap_nonempty_path_count':sum(bool(x['path']) for x in output_selectors),
            'missing_part_affected_assessments':sum(x['instruction_id'] in affected for x in assessments)},
        'doe':{'status':doe['status'],'coverage':doe['coverage'],'sink_count':len(doe['sinks']),
            'sinks_with_actual_payload':sum(bool(x['actual_payload']) for x in doe['sinks']),
            'comparison_conclusions':dict(Counter(x['conclusion'] for s in doe['sinks'] for x in s['data_reviews'])),
            'constraints':doe['constraints'],'diagnostic_counts':dict(Counter(x['code'] for x in doe['diagnostics']))},
        'limits':['470 processed IR or a recorded physical boundary is not source-faithful semantic coverage; 44 review findings remain unresolved by repair.',
            'No typed operation fault is recorded in this run. The new isolation path therefore has offline evidence but no triggering online instance here.',
            'missing_part relates to false/exception wrappers retained on a true discriminator branch, not unknown addresses or a missing field in a valid success wrapper.',
            'IR148/151 now process, but annotation semantics changed and IR151 is an opaque tool exchange; this run is not an isolated causal experiment on the runtime fix.',
            'Range counts are entries across uses/requirements/properties, not unique data fields. Zero deletions is read from saved assessments, not inferred from partial status.',
            'The static missing-required-action deletion hypothesis was not exercised or confirmed by this run; global blockers apply and no deletions were published.',
            'Controller replay/closure is root-owned and outside this analysis snapshot; this audit never invokes replay.']}
    path=VERIFY/'final-backend-source-audit.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(compact({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),'propagation':report['propagation']['coverage_counts'],
        'boundaries':report['source_boundary_counts'],'ranges':report['demand']['range_statuses'],'global_blocking_count':len(globals_),
        'output_contract_gap_count':len(output_gaps),'output_contract_gap_ir_count':report['demand']['output_contract_gap_ir_count'],
        'comparisons':report['doe']['comparison_conclusions'],'review':report['review']}))


if __name__=='__main__':main()
