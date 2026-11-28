"""Seal current scoped offline evidence; never prepare or start a model run."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib.util
import json
import xml.etree.ElementTree as ET

from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import IDENTITY, POLICY

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ONLINE = HERE.parent / 'online-ga4-runtime-locality-20261117'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target = HERE / 'offline-acceptance.json'
    if target.exists():
        raise ValueError('Acceptance already sealed')
    plan = read(HERE / 'final-validation-plan.json')
    current = implementation_provenance()
    if current != plan['implementation']:
        raise ValueError('Implementation changed after final validation began')
    for name, digest in plan['test_file_sha256'].items():
        if sha(ROOT / name) != digest:
            raise ValueError('Scoped test changed after final validation: ' + name)
    receipts = sorted(HERE.glob('*.xml'), key=lambda path: (path.stat().st_mtime_ns, path.name))
    latest, executions = {}, []
    for path in receipts:
        rows = ET.parse(path).findall('.//testcase')
        if not rows or len(rows) != len({(r.get('classname'),r.get('name')) for r in rows}):
            raise ValueError('Invalid receipt: ' + path.name)
        counts = {label:sum(r.find(label) is not None for r in rows)
                  for label in ('failure','error','skipped')}
        executions.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
            'tests':len(rows),'passed':len(rows)-sum(counts.values()),**counts})
        for row in rows:
            latest[(row.get('classname'),row.get('name'))] = (row,path.name)
    replacements=plan.get('replaced_test_identities',[])
    for replacement in replacements:
        old=(replacement['classname'],replacement['name'])
        if old not in latest or not replacement.get('reason') or not replacement.get('replacements'):
            raise ValueError('Invalid test identity replacement evidence')
        for new in replacement['replacements']:
            identity=(new['classname'],new['name'])
            if identity not in latest or any(latest[identity][0].find(tag) is not None for tag in ('failure','error','skipped')):
                raise ValueError('Replacement test lacks a current passing receipt')
        del latest[old]
    unresolved = [{**row.attrib,'receipt':receipt} for row,receipt in latest.values()
                  if row.find('failure') is not None or row.find('error') is not None]
    if unresolved:
        raise ValueError('Unresolved latest scoped failures: ' + repr(unresolved))
    reviewed_skips=read(HERE/'reviewed-skips.json')
    if sha(ROOT/reviewed_skips['source_receipt']) != reviewed_skips['source_receipt_sha256']:
        raise ValueError('Reviewed skip source receipt changed')
    allowed_skips={(row['classname'],row['name']):row['reason'] for row in reviewed_skips['reviewed_skips']}
    skips = []
    for row,receipt in latest.values():
        skipped = row.find('skipped')
        if skipped is not None:
            if allowed_skips.get((row.get('classname'),row.get('name'))) != skipped.get('message',''):
                raise ValueError('Unreviewed skip: ' + repr(row.attrib))
            skips.append({**row.attrib,'reason':skipped.get('message'),'receipt':receipt})
    for name,digest in read(HERE/'historical-pins.json')['files'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Historical artifact changed: ' + name)
    if any(ONLINE.glob('*.json')):
        raise ValueError('Online namespace already prepared or dispatched')
    if tuple(POLICY[key] for key in ('normal_semantic_calls','workers','structural_corrections','semantic_repairs')) != (7,2,1,1):
        raise ValueError('Authorized schedule/budgets changed')
    spec=importlib.util.spec_from_file_location('runtime_locality_lifecycle_guard',ONLINE/'lifecycle_guard.py')
    guard=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    ready=read(HERE/'lifecycle-readiness.json')
    helpers={str((ONLINE/name).relative_to(ROOT)).replace('\\','/'):sha(ONLINE/name)
             for name in guard.HELPERS}
    if ready['lifecycle_file_sha256'] != helpers:
        raise ValueError('Lifecycle helpers changed after their reviewed readiness receipt')
    parent=guard.parent_binding(ROOT)
    render=read(HERE/plan['review_render_measurement'])
    if (render.get('identity') != 'skillflow-pure-review-render-measurement-v1'
            or len(render.get('cases',[])) != 2
            or any(row['headroom'] < 0 or row['complete_logical_input_equal'] is not True
                   or row['original_source_suffix_equal'] is not True for row in render['cases'])):
        raise ValueError('Complete review correction measurement is not accepted')
    for name,digest in render['code_hashes'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Review rendering code changed after its complete-input measurement')
    value={'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),
        'implementation_sha256':current['sha256'],'implementation':current,
        'guided_run_identity':IDENTITY,'policy':POLICY,'restart_parent':parent,
        'latest_scoped_result':{'tests':len(latest),'passed':len(latest)-len(skips),
            'failures':0,'errors':0,'skipped':len(skips),'skip_details':skips,'scope':plan['scope']},
        'ordered_acceptance_executions':executions,
        'latest_case_receipts':[{'classname':identity[0],'name':identity[1],'receipt':record[1]}
            for identity,record in sorted(latest.items())],
        'test_file_sha256':plan['test_file_sha256'],
        'whole_repository_execution':False,'one_all_green_execution':False,
        'prior_receipts_preserved':{p.name:sha(p) for p in receipts},
        'explicit_test_identity_replacements':replacements,
        'review_render_measurement':{'path':plan['review_render_measurement'],
                                    'sha256':sha(HERE/plan['review_render_measurement'])},
        'tool_file_sha256':{name:sha(ROOT/name) for name in sorted(guard.TOOLS)},
        'lifecycle_file_sha256':helpers,
        'historical_integrity':{'protected_files':len(read(HERE/'historical-pins.json')['files']),
            'pins_sha256':sha(HERE/'historical-pins.json'),'changed':[]},
        'real_model_calls':0,'skill_executions':0,'historical_replays':0,
        'next_authorized_action':'Root may prepare and dispatch exactly one fresh GA4 from retained current CFG and its sole controller-owned zero-call replay. Freeze accepted production, prompts, transport, lifecycle and executables through closure.'}
    with target.open('x',encoding='utf-8') as handle:
        json.dump(value,handle,ensure_ascii=False,indent=2,allow_nan=False)
        handle.write('\n')
    state=read(HERE/'continuation-state.json')
    state.update(status='offline_accepted',implementation_sha256=current['sha256'],
        updated_at=value['created_at'],latest_scoped_result=value['latest_scoped_result'],
        offline_acceptance_sha256=sha(target))
    (HERE/'continuation-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value[key] for key in ('status','implementation_sha256','latest_scoped_result')},indent=2))


if __name__ == '__main__':
    main()
