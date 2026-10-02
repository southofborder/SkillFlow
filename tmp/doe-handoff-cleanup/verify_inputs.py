"""Read-only DOE handoff checks, with networking disabled."""
import hashlib
import json
import socket
from pathlib import Path

from skill_ir.propagation.handoff import load_doe_input
from skill_ir.propagation.runner import load_propagation_run
from skill_ir.recording import implementation_provenance

root = Path(__file__).resolve().parents[2]
run = root / 'packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248'
network_attempts = []

def deny(*args, **kwargs):
    network_attempts.append('blocked')
    raise AssertionError('Read-only handoff verification must never connect to a network')

socket.socket.connect = deny
socket.socket.connect_ex = deny
socket.create_connection = deny

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

cases = []
for case_dir in sorted((run/'cases').iterdir()):
    if not case_dir.is_dir():
        continue
    path = case_dir/'propagation/doe-input.json'
    standalone = load_doe_input(path)
    verified = load_propagation_run(path.parent)
    if standalone != verified:
        raise AssertionError('Standalone and complete-run projections differ')
    refinement = read(case_dir/'refinement/result.json')
    ir_ids = {i['id'] for b in verified['cfg']['blocks'].values() for i in b['instructions']}
    if set(verified['records']) != ir_ids or set(verified['actions']) != ir_ids:
        raise AssertionError('A completed case lost IR coverage')
    real_case = case_dir.name.endswith('-base')
    if real_case:
        cfg_review = read(run/'cfg-reviews'/case_dir.name[:3]/'result.json')
        if (refinement['status'] != 'review_passed' or cfg_review['status'] != 'audit_passed'
                or verified['status'] != 'complete' or verified['diagnostics']
                or cfg_review['passed_cfg'] != verified['cfg']):
            raise AssertionError('A baseline input is not the reviewed complete graph')
    cases.append({
        'case':case_dir.name,
        'doe_input':path.relative_to(root).as_posix(),
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'schema_version':verified['schema_version'],
        'standalone_and_full_run_verified':True,
        'propagation_status':verified['status'],
        'review_status':refinement['status'],
        'records':len(verified['records']), 'data':len(verified['data']),
        'next_doe_pilot_input':real_case,
        'boundary':'Actual baseline' if real_case else 'Controlled method experiment, not an additional real Skill',
    })

previous = read(Path(__file__).parent/'protected-before.json')
changed = [name for name,digest in previous.items()
           if not (root/name).is_file() or hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest]
result = {'status':'verified' if not changed and not network_attempts else 'failed',
          'verifier_implementation_sha256':implementation_provenance()['sha256'],
          'network_attempts':network_attempts, 'new_api_calls':0,
          'cases':cases, 'protected_existing_files':len(previous), 'changed_protected_files':changed,
          'boundary':'Read-only loading revalidates facts, audit and compilation. It does not resume or rewrite historical runs, nor replace their producer-source identity.'}
(Path(__file__).parent/'input-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if result['status']=='verified' else 1)
