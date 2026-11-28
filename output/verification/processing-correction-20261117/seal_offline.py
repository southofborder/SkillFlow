"""Root's one-time offline evidence seal; no preparation, model or replay."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import IDENTITY, POLICY
from skillflow.document_guided.online import STEP_IDENTITY
from skillflow.document_guided.fragments import VERSION

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
VERIFY = BASE.parent / 'online-ga4-processing-correction-20261117'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (BASE / 'offline-acceptance.json').exists():
        raise ValueError('Offline acceptance is already sealed')
    receipts = [BASE / 'final-affected-scope.xml', BASE / 'corrective-renderer.xml']
    latest, executions = {}, []
    for receipt in receipts:
        rows = ET.parse(receipt).findall('.//testcase')
        identities = {(row.get('classname'), row.get('name')) for row in rows}
        if not rows or len(identities) != len(rows):
            raise ValueError('Missing cases or duplicate testcase identities: ' + str(receipt))
        executions.append({'path': receipt.relative_to(ROOT).as_posix(), 'sha256': sha(receipt),
            'tests': len(rows), 'passed': sum(all(row.find(tag) is None for tag in ('failure', 'error', 'skipped')) for row in rows),
            **{tag + 's' if tag != 'skipped' else tag: sum(row.find(tag) is not None for row in rows)
               for tag in ('failure', 'error', 'skipped')}})
        for row in rows:
            latest[(row.get('classname'), row.get('name'))] = (row, receipt.name)
    cases = [item[0] for item in latest.values()]
    if not cases or any(row.find(tag) is not None for row in cases for tag in ('failure', 'error')):
        raise ValueError('Latest affected-scope union contains an unresolved failure or error')
    skipped = []
    for row in cases:
        mark = row.find('skipped')
        if mark is None:
            continue
        reason = mark.get('message', '')
        if not (row.get('classname') == 'tests.common.test_upstream'
                and row.get('name') == 'test_symlink_input_or_parent_rejected'
                and reason.startswith('Symlink privilege unavailable:')):
            raise ValueError('Unreviewed skipped test: ' + repr((row.attrib, reason)))
        skipped.append({'classname': row.get('classname'), 'name': row.get('name'),
            'reason': reason, 'acceptance': 'Unchanged upstream symlink test requires unavailable Windows privilege; no changed code or new mandatory regression is skipped.'})
    baseline = read(BASE / 'baseline.json')
    changed = [name for name, digest in baseline['historical_files'].items()
               if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
    if changed:
        raise ValueError('Protected historical files changed: ' + repr(changed))
    ready = read(BASE / 'lifecycle-readiness.json')
    helpers = ready['acceptance_lifecycle_file_sha256']
    for name, digest in helpers.items():
        if sha(ROOT / name) != digest:
            raise ValueError('Reviewed lifecycle helper changed: ' + name)
    if any(VERIFY.glob('*.json')):
        raise ValueError('New online namespace already has a preparation or run record')
    if (POLICY['normal_semantic_calls'], POLICY['workers'], POLICY['structural_corrections'], POLICY['semantic_repairs']) != (7, 2, 1, 1):
        raise ValueError('Call schedule or correction budgets changed')
    current = implementation_provenance()
    if current['sha256'] != 'ce895cd759ec42da20bb93a2f1efcf8699078f7233047f7caf4f31908f1cdc69':
        raise ValueError('Production changed since the final affected-scope execution')
    before = baseline['implementation']['files']
    implementation_delta = {name: {'before': before.get(name), 'after': current['files'].get(name)}
        for name in sorted(set(before) | set(current['files']))
        if before.get(name) != current['files'].get(name)}
    tool_files = {name: sha(ROOT / name) for name in ready['required_transport_files']}
    test_files = {p.relative_to(ROOT).as_posix(): sha(p) for directory in
        ('tests/document_guided', 'tests/task', 'tests/common', 'tests/graph')
        for p in sorted((ROOT / directory).rglob('*.py'))}
    for name in ('tests/doe/test_reviewed_input_necessity.py', 'tests/doe/test_input_contract_review.py'):
        test_files[name] = sha(ROOT / name)
    value = {'status': 'passed', 'created_at': datetime.now(timezone.utc).isoformat(),
        'implementation_sha256': current['sha256'], 'implementation': current,
        'implementation_changes_from_task_baseline': implementation_delta,
        'guided_run_identity': IDENTITY, 'step_identity': STEP_IDENTITY, 'fragments_identity': VERSION,
        'policy': POLICY, 'latest_scoped_result': {'tests': len(cases), 'passed': len(cases) - len(skipped),
            'failures': 0, 'errors': 0, 'skipped': len(skipped), 'skip_details': skipped,
            'scope': ['tests/document_guided', 'tests/task', 'tests/common', 'tests/graph',
                'tests/doe/test_reviewed_input_necessity.py', 'tests/doe/test_input_contract_review.py']},
        'ordered_acceptance_executions': executions,
        'latest_case_receipts': [{'classname': identity[0], 'name': identity[1], 'receipt': item[1]}
            for identity, item in sorted(latest.items())],
        'whole_repository_execution': False,
        'one_all_green_execution': False,
        'prior_receipts_preserved': {p.name: sha(p) for p in sorted(BASE.glob('*.xml'))},
        'initial_failures': [
            'raw-wire-compatibility-01.xml retains one outdated exact prompt suffix expectation; updated to include the complete program-owned grammar and passed in the affected-scope execution.',
            'final-affected-scope.xml retains two PNG renderer tests failing only at import PIL. Pillow 13.0.0 was installed into the isolated test venv; unchanged renderer tests passed in corrective-renderer.xml. No production or assertion change was made for these failures.'],
        'test_environment_dependency_added': {'package': 'Pillow', 'version': '13.0.0',
            'purpose': 'Unchanged optional PNG renderer assertions', 'production_change': False},
        'tool_file_sha256': tool_files, 'lifecycle_file_sha256': helpers, 'test_file_sha256': test_files,
        'historical_integrity': {'baseline_sha256': sha(BASE / 'baseline.json'),
            'protected_files': len(baseline['historical_files']), 'changed': []},
        'real_model_calls': 0, 'skill_executions': 0, 'historical_replays': 0,
        'next_authorized_action': 'Root alone may prepare and dispatch exactly one fresh GA4 and its sole controller-owned zero-call replay. Freeze accepted production, prompts, transport, helpers and executables through closure.'}
    with (BASE / 'offline-acceptance.json').open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
    state = read(BASE / 'continuation-state.json')
    state.update(status='offline_accepted', updated_at=value['created_at'],
        implementation_sha256=current['sha256'], final_scoped_tests=len(cases),
        passed=len(cases) - len(skipped), skipped=len(skipped),
        offline_acceptance_sha256=sha(BASE / 'offline-acceptance.json'))
    (BASE / 'continuation-state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'tests': len(cases), 'passed': len(cases) - len(skipped), 'skipped': len(skipped), 'implementation_sha256': current['sha256'],
        'historical_files_unchanged': len(baseline['historical_files'])}, indent=2))


if __name__ == '__main__':
    main()
