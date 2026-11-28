"""Seal scoped offline evidence only; this script does not launch analysis."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

VERIFY = Path(__file__).resolve().parent
ROOT = VERIFY.parents[2]
sys.path.insert(0, str(ROOT))
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import IDENTITY, POLICY


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create(name, value):
    with (VERIFY / name).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


current = implementation_provenance()
initial = read(VERIFY / 'final-test-result.json')
assert initial['implementation_unchanged'] and current['sha256'] == initial['implementation_sha256']
latest = {}
receipts = ['final-scoped.xml', 'final-interface-inventory-corrected.xml']
for name in receipts:
    for case in ET.parse(VERIFY / name).getroot().findall('.//testcase'):
        latest[(case.get('classname'), case.get('name'))] = {
            'status':next((tag for tag in ('failure','error','skipped') if case.find(tag) is not None), 'passed'),
            'receipt':name}
assert len(latest) == 886 and all(row['status'] == 'passed' for row in latest.values())
prior = ROOT / 'experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242'
preserved = read(VERIFY / 'preserved-artifact-hashes.json')
assert all(sha(prior / name) == digest for name, digest in preserved.items())
size = read(VERIFY / 'review-correction-size.json')
assert all(sha(ROOT / name) == digest for name, digest in size['code_file_sha256'].items())
assert all(sha(ROOT / name) == digest for name, digest in size['input_file_sha256'].items())
assert IDENTITY == 'skillflow-document-guided-run-v13'
assert tuple(POLICY[key] for key in ('normal_semantic_calls','workers','structural_corrections','semantic_repairs')) == (7,2,1,1)
assert POLICY['review_validation'] == 'strict-record-isolation-v1'
baseline = read(VERIFY / 'baseline-provenance.json')
acceptance = {'status':'passed','sealed_at':datetime.now(timezone.utc).isoformat(),
    'implementation_sha256':current['sha256'],'implementation_unchanged_during_final_scoped_run':True,
    'distinct_current_latest_tests':len(latest),'passed':len(latest),'skipped':0,'unresolved_failures':0,
    'whole_repository_all_green':False,'single_all_green_scoped_execution':False,
    'receipt_union':[{ 'file':name,'sha256':sha(VERIFY/name)} for name in receipts],
    'initial_final_scope':{'passed':885,'failed':1,'test_count':886,'receipt':'final-scoped.xml'},
    'correction':'Registered the already-visible review_correction_envelope diagnostic in the test documentation-coverage inventory; 24 targeted tests passed; no production change.',
    'changed_implementation_files':[name for name,digest in current['files'].items() if baseline['files'].get(name) != digest],
    'source_review_identity':'skillflow-document-source-review-fragment-v5',
    'input_contract_review_identity':'skillflow-input-contract-review-v3',
    'guided_run_identity':IDENTITY,'policy':POLICY,
    'demand_identity':'skillflow-demand-v10','doe_identity':'skillflow-doe-run-v10',
    'task_identity_unchanged':True,'model_calls':0,'skill_execution':False,'historic_run_replay':False,
    'historical_artifacts_preserved':True,'preserved_hash_count':len(preserved),
    'correction_size_audit_sha256':sha(VERIFY/'review-correction-size.json'),
    'remaining_authorization':'Root alone may prepare and start exactly one fresh GA4 and its sole controller-owned zero-call replay with the accepted frozen implementation.'}
create('offline-acceptance.json', acceptance)
create('accepted-provenance.json', current)
create('latest-scoped-test-index.json', [{'classname':key[0],'name':key[1],**value} for key,value in sorted(latest.items())])
state = read(VERIFY/'continuation-state.json')
state.update(status='offline_accepted',implementation_sha256=current['sha256'],offline_acceptance='offline-acceptance.json',
    model_starts=0, next_step=acceptance['remaining_authorization'])
(VERIFY/'continuation-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(VERIFY/'assessment.en.md').write_text(f'''# Offline acceptance: strict review locality

The accepted implementation is `{current['sha256']}`. There are **886 distinct
current scoped tests with latest passing evidence**, zero skips and zero
unresolved failures. This is not one all-green whole-repository execution. The
frozen final scoped run passed 885 and failed one documentation-coverage inventory
assertion; adding the new already-visible correction-envelope diagnostic to that
test inventory was followed by 24 targeted passes, without a production change.
All original failures and corrective receipts remain preserved.

The fix exposes kind/actual/path coupling in the schema, strictly validates all
review records and complete inventories, isolates invalid records with exact
barriers, revalidates immutable partial receipts, and allows independently valid
findings to use the existing repair round. Invalid records are not accepted or
converted into source-semantic findings. Zero surviving records retain structural
failure. Native demands, all-input assessments and deletion-impact checks share
the same barriers, including deterministic and zero-demand uses.

The three original missing-field failures had hidden sequential constraints and
two unestablished SDK encodings. Their correction format also could not move a
claim between review tables. Further candidate conflicts mean that correcting
those three rows alone would not validate the other authored accepted labels.
Broad actual CFG findings still block overlapping contracts; checks were not
weakened. See locator-diagnosis.en.md and architecture-audit.en.md.

The general correction path uses the existing full-response correction when
needed and lossless joint presentation. Derived offline deliveries for the two
saved candidates are 1,014,657 and 1,014,077 characters, below the unchanged
1,048,576 cap. All 307 conflict pairs, complete source and original logical
inputs/candidates are retained. This is a measured bound for these materials,
not a promise that arbitrary irreducible inputs fit. The historical run was not
executed, replayed or rewritten by that validation/render-only audit.

Injected tests exercise seven normal requests, two workers, the existing shared
repair/dependency closure, partial rereview and zero-new-call fresh replay. No
real model or Skill was executed during this offline work. All previously sealed
artifacts checked at task initialization remain byte-identical.

The user-authorized single fresh GA4 has not started at this seal. Its lifecycle
will be recorded separately under `online-ga4-source-review-locality-20261113`.
Semantic truth, complete source coverage and actual DOE findings remain subjects
of the new source-based run and report; these engineering checks do not prove
natural-language semantic equivalence or absence of DOE.
''',encoding='utf-8')
print(json.dumps(acceptance,ensure_ascii=False,indent=2))
