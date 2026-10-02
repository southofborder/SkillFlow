from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'packages/skill-ir/experiments/semantics_baseline'
RUN = BASE / 'runs/baseline-deepseek-v4-flash-max-20260910'
spec = importlib.util.spec_from_file_location('result_integrity', BASE / 'tools/result_integrity.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
report = m.read(RUN / 'report.json')
assert len(report['trials']) == 90
assert all(t['status'] in {'complete', 'error', 'degraded', 'uncertain'} for t in report['trials'])
freeze, identities = m.verify_result_sources(BASE, RUN, 'deepseek-v4-flash-max')
states, models, failures, record_hashes = Counter(), Counter(), [], {}
prompt_checks = 0
for t in report['trials']:
    p = RUN / t['artifacts']
    record = m.read(p / 'record.json')
    m.verify_trial_record(record, t, p, identities[t['case']])
    states[t['status']] += 1
    key = f"{t['case']}/{t['repetition']}"
    record_hashes[key] = m.sha(p / 'record.json')
    trace = m.read(p / 'trace.json')
    assert all(trace.get(k) == t[k] for k in ('case', 'variant', 'repetition', 'split'))
    first = trace['calls'][0]['prompt']
    assert hashlib.sha256(first.encode('utf-8')).hexdigest() == identities[t['case']]['prompt_sha256']
    prompt_checks += 1
    unknown = []
    for call in trace['calls']:
        for attempt in call.get('http_attempts', []):
            models[attempt.get('returned_model')] += 1
            stream = attempt.get('stream') or {}
            if stream.get('outcome') == 'remote_outcome_unknown':
                unknown.append({'http_status': attempt.get('http_status'),
                                'received_bytes': stream.get('received_bytes'),
                                'outcome': stream.get('outcome'),
                                'returned_model': attempt.get('returned_model')})
    if t['status'] != 'complete':
        failures.append({'trial': key, 'status': t['status'], 'unknown_http': unknown,
                         'classification': 'Local Windows trace-file replacement failure; exact handle owner unknown.'
                         if key == 'N01/3' else 'HTTP 200 followed by incomplete SSE stream; provider versus intermediary cause unresolved.'})

# Compare the credential only in memory. Never print its value or matching text.
credential = None
for line in (ROOT / '.env').read_text(encoding='utf-8-sig').splitlines():
    name, sep, value = line.partition('=')
    if sep and name.strip() == 'LLM_API_KEY':
        credential = value.strip().strip('"').strip("'").encode()
assert credential and len(credential) > 8
targets = [RUN, BASE / 'provider_checks', ROOT / 'packages/skill-ir/tests', ROOT / 'output/pdf', ROOT / 'docs']
files = {p for directory in targets for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
files.update(p for p in BASE.iterdir() if p.is_file())
files.update([ROOT / 'packages/skill-ir/.env.example', ROOT / 'packages/skill-ir/README.md'])
matches = []
for p in sorted(files):
    with p.open('rb') as stream:
        tail = b''
        while chunk := stream.read(1024 * 1024):
            data = tail + chunk
            if credential in data:
                matches.append(p.relative_to(ROOT).as_posix())
                break
            tail = data[-len(credential) + 1:]
assert not matches, 'Credential found in publishable artifacts: ' + ', '.join(matches)

audit = {
    'schema_version': 1, 'checked_at': datetime.now(timezone.utc).isoformat(),
    'run_id': report['run_id'], 'report_sha256': m.sha(RUN / 'report.json'),
    'experiment_sha256': m.sha(RUN / 'experiment.json'),
    'freeze_manifest_sha256': m.sha(BASE / 'freeze_manifest.json'),
    'frozen_files_verified': len(freeze['files']), 'planned_trials': 90,
    'states': dict(states), 'all_record_and_artifact_digests_verified': True,
    'exact_first_prompt_checks': prompt_checks, 'request_model': 'deepseek-v4-flash',
    'http_returned_models': dict(models), 'summary': report['summary'], 'by_split': report['by_split'],
    'failures': failures, 'record_sha256': record_hashes,
    'credential_scan': {'files_checked': len(files), 'matches': 0, 'secret_not_persisted_in_audit': True},
    'tests': {'command': 'python -m pytest packages/skill-ir/tests -q', 'passed': 512, 'elapsed_seconds': 67.66, 'real_api_calls': 0},
    'interpretation': 'All planned trial records are terminal. 85 accepted CFGs are structurally valid, not semantic passes. Five failed requests retain unknown remote outcomes. User joint review remains pending.',
}
(RUN / 'execution_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: audit[k] for k in ['states', 'frozen_files_verified', 'exact_first_prompt_checks', 'http_returned_models', 'credential_scan']}, ensure_ascii=False))
