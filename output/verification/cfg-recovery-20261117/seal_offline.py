"""Seal root's scoped offline acceptance; never prepare or start an experiment."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import IDENTITY, POLICY
from skillflow.document_guided.online import STEP_IDENTITY
from skillflow.document_guided.fragments import VERSION
from skillflow.document_guided.source_review import FRAGMENT_IDENTITY
from skillflow.document_guided.fatal_frontier import IDENTITY as FATAL_IDENTITY

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
VERIFY = BASE.parent / 'online-ga4-cfg-recovery-20261117'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (BASE / 'offline-acceptance.json').exists():
        raise ValueError('Offline acceptance is already sealed')
    plan = read(BASE / 'final-validation-plan.json')
    current = implementation_provenance()
    if current != plan['implementation']:
        raise ValueError('Production changed since the final affected-scope execution')
    latest, executions = {}, []
    for filename in plan['ordered_receipts']:
        receipt = BASE / filename
        rows = ET.parse(receipt).findall('.//testcase')
        identities = {(row.get('classname'), row.get('name')) for row in rows}
        if not rows or len(rows) != len(identities):
            raise ValueError('Missing or duplicate test identities in ' + filename)
        statuses = {label: sum(row.find(label) is not None for row in rows)
                    for label in ('failure', 'error', 'skipped')}
        executions.append({'path': receipt.relative_to(ROOT).as_posix(), 'sha256': sha(receipt),
            'tests': len(rows), 'passed': len(rows) - sum(statuses.values()), **statuses})
        for row in rows:
            latest[(row.get('classname'), row.get('name'))] = (row, filename)
    if any(row.find(tag) is not None for row, _ in latest.values() for tag in ('failure', 'error')):
        raise ValueError('Latest scoped cases have unresolved failures')
    skips = []
    for row, receipt in latest.values():
        skipped = row.find('skipped')
        if skipped is None:
            continue
        if (row.get('classname') != 'tests.common.test_upstream'
                or row.get('name') != 'test_symlink_input_or_parent_rejected'
                or not skipped.get('message', '').startswith('Symlink privilege unavailable:')):
            raise ValueError('Unreviewed skip: ' + str(row.attrib))
        skips.append({**row.attrib, 'reason': skipped.get('message'), 'receipt': receipt})
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
        raise ValueError('Online namespace already contains a preparation or dispatch record')
    if tuple(POLICY[key] for key in ('normal_semantic_calls', 'workers', 'structural_corrections', 'semantic_repairs')) != (7, 2, 1, 1):
        raise ValueError('Authorized schedule or budgets changed')
    for name, digest in plan['test_file_sha256'].items():
        if sha(ROOT / name) != digest:
            raise ValueError('A scoped test changed after the execution plan: ' + name)
    before, after = baseline['implementation']['files'], current['files']
    delta = {name: {'before': before.get(name), 'after': after.get(name)}
        for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)}
    failures_not_retested = []
    for path in BASE.glob('*.xml'):
        for row in ET.parse(path).findall('.//testcase'):
            if any(row.find(tag) is not None for tag in ('failure', 'error')):
                identity = row.get('classname'), row.get('name')
                if identity not in latest:
                    failures_not_retested.append({'receipt': path.name, **row.attrib})
    if failures_not_retested:
        raise ValueError('Earlier failed identities lack current passing coverage: ' + repr(failures_not_retested))
    value = {'status': 'passed', 'created_at': datetime.now(timezone.utc).isoformat(),
        'implementation_sha256': current['sha256'], 'implementation': current,
        'implementation_changes_from_task_baseline': delta,
        'guided_run_identity': IDENTITY, 'step_identity': STEP_IDENTITY, 'fragments_identity': VERSION,
        'source_review_fragment_identity': FRAGMENT_IDENTITY, 'fatal_frontier_identity': FATAL_IDENTITY,
        'policy': POLICY, 'latest_scoped_result': {'tests': len(latest), 'passed': len(latest) - len(skips),
            'failures': 0, 'errors': 0, 'skipped': len(skips), 'skip_details': skips, 'scope': plan['scope']},
        'ordered_acceptance_executions': executions,
        'latest_case_receipts': [{'classname': identity[0], 'name': identity[1], 'receipt': record[1]}
            for identity, record in sorted(latest.items())],
        'whole_repository_execution': False,
        'one_all_green_execution': len(executions) == 1 and not skips,
        'prior_receipts_preserved': {p.name: sha(p) for p in sorted(BASE.glob('*.xml'))},
        'initial_failures_explanation': 'See offline-assessment.en.md; original receipts remain immutable. Final acceptance resolves every earlier failed test identity.',
        'tool_file_sha256': {name: sha(ROOT / name) for name in ready['required_transport_files']},
        'lifecycle_file_sha256': helpers, 'test_file_sha256': plan['test_file_sha256'],
        'historical_integrity': {'baseline_sha256': sha(BASE / 'baseline.json'),
            'protected_files': len(baseline['historical_files']), 'changed': []},
        'real_model_calls': 0, 'skill_executions': 0, 'historical_replays': 0,
        'next_authorized_action': 'Root alone may prepare and dispatch one fresh GA4 and its sole controller-owned zero-call replay. Freeze accepted production, prompts, transport, helpers and executables through closure.'}
    with (BASE / 'offline-acceptance.json').open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
    state = read(BASE / 'continuation-state.json')
    state.update(status='offline_accepted', updated_at=value['created_at'],
        implementation_sha256=current['sha256'], final_scoped_tests=len(latest),
        passed=len(latest) - len(skips), skipped=len(skips),
        offline_acceptance_sha256=sha(BASE / 'offline-acceptance.json'))
    (BASE / 'continuation-state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'tests': len(latest), 'passed': len(latest) - len(skips),
        'skipped': len(skips), 'implementation_sha256': current['sha256'],
        'historical_files_unchanged': len(baseline['historical_files'])}, indent=2))


if __name__ == '__main__':
    main()
