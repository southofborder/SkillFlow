"""Passive provenance of review findings across saved processing responses."""
from collections import Counter
from datetime import datetime, timezone
import json
from audit_processing_material_v12 import ROOT, VERIFY, RUN, compact, read, sha
from audit_processing_first_response import response_value, walk
from audit_review_first_correction import canonical


def locate(value, pointer):
    for raw in pointer.lstrip('/').split('/'):
        key = raw.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def changes(before, after, path=''):
    if before == after:
        return []
    if isinstance(before, dict) and isinstance(after, dict):
        return [part for key in sorted(before.keys() | after.keys()) for part in (
            changes(before[key], after[key], path + '/' + key) if key in before and key in after else [path + '/' + key])]
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        return [part for i,(a,b) in enumerate(zip(before,after)) for part in changes(a,b,path+'/'+str(i))]
    return [path]


def producer_evidence(document, ir):
    record = document['ir_semantics'][ir]
    producers = {}
    for name in ('x', 'tuple', 'reply'):
        found = [(path, value) for path,value in walk(record) if isinstance(value,dict) and value.get('output') == name]
        assert len(found) == 1, (ir,name)
        path, value = found[0]
        picked = {key:value[key] for key in ('op','location','input','inputs','path','output') if key in value}
        if 'location' in value:
            loc = document['locations'][value['location']]
            picked['location_identity'] = {key:loc[key] for key in ('kind','name')}
        producers[name] = {'record_pointer':'/ir_semantics/'+ir+path, 'value_flow':picked}
    writes = [{'record_pointer':'/ir_semantics/'+ir+path,'target':value['target'],'input':value.get('input')}
        for path,value in walk(record) if isinstance(value,dict) and value.get('op') == 'write']
    return {'producers':producers,'writes':writes}


def main():
    before, _ = response_value(read(RUN/'steps/processing/calls/a001/response.json'))
    after, _ = response_value(read(RUN/'steps/processing/calls/a002/response.json'))
    result = read(RUN/'review/result.json')['review']
    findings = [row for row in result['findings'] if row['domain']=='annotation' and 'input_contract_obligation_id' not in row]
    cfg = read(RUN/'graph/initial.json')['cfg']
    irs = {ir['id']:ir for block in cfg['blocks'].values() for ir in block['instructions']}
    rows, counts = [], Counter()
    for finding in findings:
        targets = []
        for target in finding['target_ids']:
            pointer = target.split(':',1)[1]
            item = {'target':target}
            if finding.get('owner') != 'processing':
                item.update(classification='external_fragment_not_comparable',
                    reason='This assembled annotation target belongs to '+str(finding.get('owner'))+'; the two processing responses do not contain that owning fragment.')
            else:
                old, new = locate(before,pointer), locate(after,pointer)
                item.update(before_sha256=canonical(old),after_sha256=canonical(new),exact_target_equal=old==new,
                    changed_relative_paths=changes(old,new))
                ir = pointer.split('/')[2]
                item['cfg_instruction']={'id':ir,'opcode':irs[ir]['opcode'],'inputs':irs[ir]['inputs'],'outputs':irs[ir]['outputs']}
                if '/output_bindings/' in pointer:
                    a,b=producer_evidence(before,ir),producer_evidence(after,ir)
                    assert old['value']=={'kind':'local','name':'reply'} and new['value']=={'kind':'local','name':'x'}
                    for context in (a,b):
                        p=context['producers']
                        assert p['x']['value_flow']['location']=='parseGA'
                        assert p['tuple']['value_flow']['location']=='report'
                        assert p['reply']['value_flow']['input']=={'kind':'local','name':'tuple'}
                        assert p['reply']['value_flow']['path']==[0]
                        assert any(w['input']=={'kind':'local','name':'reply'} for w in context['writes'])
                    item.update(classification='response_to_date_range_binding_change',before=old,after=new,
                        before_producer_context=a,after_producer_context=b,
                        interpretation='The declared output changed from the still-existing report reply to the still-existing parseDateRange result; child saving still uses reply. This is not just a local-name rename. Other semantics in either whole candidate are not certified.')
                elif old==new:
                    item.update(classification='exact_target_preexists',
                        interpretation='The exact defect-bearing target identified by the later finding was already present. This equality alone does not certify all ancestor records, location declarations or other referenced values.')
                else:
                    keys=('op','location','target','inputs','input','output','outputs')
                    old_kernel={k:old[k] for k in keys if k in old};new_kernel={k:new[k] for k in keys if k in new}
                    assert old_kernel==new_kernel
                    item.update(classification='changed_record_same_call_binding',call_binding=old_kernel,
                        interpretation='The call record changed in other fields, but op, address declaration key, input references and output binding are identical. The specific receiver omission or opaque-storage-call representation predates replacement; no general semantic-regression claim follows from the full record difference.')
                    if ir in {'ir_479','ir_488'}:
                        item['both_ir_operation_vocabulary']={label:sorted({value['op'] for _,value in walk(doc['ir_semantics'][ir]) if isinstance(value,dict) and isinstance(value.get('op'),str)}) for label,doc in [('a001',before),('a002',after)]}
            counts[item['classification']]+=1
            targets.append(item)
        rows.append({'finding_id':finding['id'],'owner':finding.get('owner'),'explanation':finding['explanation'],
            'source_refs':finding['source_refs'],'targets':targets})
    refs=[]
    for path in [RUN/'steps/processing/calls/a001/response.json',RUN/'steps/processing/calls/a001/validation.json',
                 RUN/'steps/processing/calls/a002/response.json',RUN/'steps/processing/calls/a002/validation.json',
                 RUN/'review/result.json',RUN/'graph/initial.json',
                 RUN/'source/inputs/package/scripts/src/api/reports.ts',RUN/'source/inputs/package/scripts/src/index.ts']:
        data=path.read_bytes();refs.append({'path':path.relative_to(ROOT).as_posix(),'bytes':len(data),'sha256':sha(data)})
    report={'audit':'passive_correction_finding_origin','created_utc':datetime.now(timezone.utc).isoformat(),
        'run_directory':RUN.relative_to(ROOT).as_posix(),'original_annotation_findings':len(rows),'target_classification_counts':dict(counts),
        'references':refs,'findings':rows,
        'source_relation_evidence':[
            {'file':'skill/scripts/src/api/reports.ts','lines':[90,94],'relation':'parseDateRange feeds request.dateRanges'},
            {'file':'skill/scripts/src/api/reports.ts','lines':[100,108],'relation':'SDK tuple response is saved and returned'},
            {'file':'skill/scripts/src/api/reports.ts','lines':[114,175],'relation':'six wrappers return runReport results'},
            {'file':'skill/scripts/src/index.ts','lines':[55,166],'relation':'higher-level reports receive wrapper results into aggregate report slots'}],
        'limits':['Only this new run is compared; no historical candidate was executed or imported.',
            'The initial processing a001 was structurally invalid. Evidence that its reply binding matched this source relation does not certify that whole candidate.',
            'No counterfactual local-patch success, review outcome, runtime accuracy, deletion consequence, or model-generation mechanism is established.',
            'Exact target equality is not equality of all ancestor and external references. Other-owner targets are explicitly incomparable to processing.',
            'No project imports, stages, validators, backend, model, Skill, test, replay or frozen writes occurred.']}
    path=VERIFY/'correction-finding-origin-audit.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(compact({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),'counts':dict(counts),'findings':len(rows)}))


if __name__=='__main__':
    main()
