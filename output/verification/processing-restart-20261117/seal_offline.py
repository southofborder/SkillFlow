"""Root-owned offline receipt seal; no model, stage or replay execution."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[3]
OFFLINE = Path(__file__).resolve().parent
VERIFY = PROJECT / 'output/verification/online-ga4-processing-restart-20261117'
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(VERIFY))
from lifecycle_guard import parent_binding, validate_acceptance
from skillflow.common.recording import implementation_provenance

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    readiness = read(OFFLINE / 'lifecycle-readiness.json')
    current = implementation_provenance()
    assert current['sha256'] == readiness['implementation_sha256']
    for name, digest in readiness['all_helper_file_sha256'].items():
        assert sha(PROJECT / name) == digest, name
    for name, digest in readiness['test_file_sha256'].items():
        assert sha(PROJECT / name) == digest, name
    inherited = parent_binding(PROJECT)
    assert inherited == read(OFFLINE / 'parent-binding-readonly.json')
    receipts, cases = [], set()
    for name in ('lifecycle-accounting.xml', 'restart-integration-initial.xml'):
        path = OFFLINE / name
        nodes = ET.parse(path).getroot().findall('.//testcase')
        for node in nodes:
            assert node.find('failure') is None and node.find('error') is None and node.find('skipped') is None
            key = (node.get('classname'), node.get('name'))
            assert key not in cases
            cases.add(key)
        receipts.append({'path': str(path.relative_to(PROJECT)), 'sha256': sha(path), 'passed': len(nodes)})
    assert len(cases) == 68
    prior = PROJECT / 'output/verification/cfg-recovery-20261117/offline-acceptance.json'
    prior_value = read(prior)
    assert prior_value['status'] == 'passed' and prior_value['implementation_sha256'] == current['sha256']
    peer = read(OFFLINE / 'reuse-lifecycle-peer-review.json')
    assert peer['unresolved_blockers'] == []
    value = {**readiness['acceptance_required'],
        'created_at': datetime.now(timezone.utc).isoformat(), 'implementation': current,
        'restart_parent': inherited,
        'prior_production_acceptance': {'path': str(prior.relative_to(PROJECT)), 'sha256': sha(prior),
            'distinct_latest_passed': 2593, 'skipped': 1, 'unresolved_failures': 0},
        'new_lifecycle_acceptance': {'distinct_passed': len(cases), 'skipped': 0, 'unresolved_failures': 0,
            'receipts': receipts, 'whole_repository_execution': False},
        'readiness_sha256': sha(OFFLINE / 'lifecycle-readiness.json'),
        'peer_review_sha256': sha(OFFLINE / 'reuse-lifecycle-peer-review.json'),
        'test_file_sha256': {**readiness['test_file_sha256'],
            'tests/document_guided/test_processing_restart_integration.py': sha(PROJECT / 'tests/document_guided/test_processing_restart_integration.py')},
        'scope': 'New lifecycle only. Production, prompts, transport and budgets unchanged. Fresh synthetic fixtures; no real model or Skill execution, parent replay or backend experiment during acceptance.',
        'request_accounting': {'normal_policy_stages': 7, 'inherited_initial_stages': 3,
            'fresh_normal_requests': 4, 'workers': 2, 'inherited_public_tokens_not_new': 303082},
        'authorization': 'One fresh GA4 descendant retaining accepted initial CFG/Task/flow and completing processing onward, with its sole controller-owned zero-call replay.'}
    with (OFFLINE / 'offline-acceptance.json').open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    validate_acceptance(PROJECT, VERIFY, current)
    print(json.dumps({'status':'passed','distinct_new_tests':len(cases),'implementation_sha256':current['sha256'],
        'acceptance_sha256':sha(OFFLINE / 'offline-acceptance.json'),'inherited_file_count':len(inherited['inherited_files'])}))

if __name__ == '__main__':
    main()
