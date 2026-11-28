"""Record the narrow corrective executions after the preserved broad receipts."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from skillflow.common.recording import implementation_provenance

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent

if __name__=='__main__':
    path=HERE/'final-validation-plan.json'
    original=path.read_bytes()
    with (HERE/'final-validation-plan.initial.json').open('xb') as handle:
        handle.write(original)
    plan=json.loads(original)
    current=implementation_provenance()
    delta={name:{'before':plan['implementation']['files'].get(name),'after':current['files'].get(name)}
        for name in sorted(set(plan['implementation']['files'])|set(current['files']))
        if plan['implementation']['files'].get(name)!=current['files'].get(name)}
    expected={'src/skillflow/document_guided/accepted_upstream.py',
        'src/skillflow/document_guided/accepted_stage_reader.py','src/skillflow/doe/material.py'}
    if set(delta)!=expected:
        raise ValueError('Unexpected production change during corrective validation')
    plan['corrective_validation']={'updated_at':datetime.now(timezone.utc).isoformat(),
        'initial_plan_sha256':hashlib.sha256(original).hexdigest(),
        'production_changes':delta,
        'reason':'Strict parent result identity, raw-response flow correction binding, and complete runtime operation-contract validation in DOE.',
        'receipt':'corrective-material-reader.xml',
        'other_corrections':'See preserved diagnostic receipts: short test paths resolve Windows MAX_PATH; current synthetic fixtures and coverage assertions explicitly encode the new address/infeasible policy. Historical artifacts were not converted.',
        'scope':'Current changed readers and DOE consumer, plus targeted fixtures and unchanged short-path suites. No second whole scoped broad run.'}
    plan['implementation']=current
    plan['test_file_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for scope in plan['scope'] for p in sorted((ROOT/scope).rglob('*.py'))}
    name='test_previous_review_generation_cannot_be_used_for_current_contract_acceptance'
    module='tests.document_guided.test_failed_stage_review_targets'
    plan['replaced_test_identities']=[{'classname':module,'name':name,
        'reason':'The original single previous-generation assertion was expanded into explicit v5 and v6 rejection under current source-review v7; the original failed XML remains preserved.',
        'replacements':[{'classname':module,'name':name+'['+version+']'} for version in ('v5','v6')]}]
    path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'implementation_sha256':current['sha256'],'changed_production_files':list(delta),
        'test_files':len(plan['test_file_sha256'])},indent=2))
