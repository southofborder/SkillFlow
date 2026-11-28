"""Read selected frozen artifacts; emit an independent source audit only.

No Skill, model, analyzer, propagation, demand, DOE, or replay is invoked.
"""
import collections
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path('D:/Projects/SkillFlow')
RUN = ROOT / 'experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209'
OUT = ROOT / 'output/verification/online-ga4-input-necessity-corrected-r2-20261112/source-audit'
SOURCE = RUN / 'source/inputs/package'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def identity(path):
    return {'path': str(path), 'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def evidence(file, start, end):
    path = SOURCE / file
    lines = path.read_text(encoding='utf-8').splitlines()
    return {'file': 'skill/' + file, 'start_line': start, 'end_line': end,
            'quote': '\n'.join(lines[start - 1:end]),
            'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


processing = read(RUN / 'steps/processing/value.json')
mapping = read(RUN / 'steps/task-correspondence/value.json')
sensitivity = read(RUN / 'steps/sensitivity/value.json')
compiled = read(RUN / 'annotation/audit/compiled-response.json')
review = read(RUN / 'review/result.json')
receipt = read(RUN / 'audit/input-contract-review.json')
graph_audit = read(OUT / 'selected-graph-audit.json')
inventory = read(OUT / 'source-boundary-inventory.json')
task = read(RUN / 'task/task.json')
assert identity(RUN / 'steps/processing/value.json')['file_sha256'] == '533595e3e761dc816c965817bcbe8497c1a8d9f5c505170bf09308b95376d8d0'
assert review['status'] == 'request_failure' and review['review'] is None
assert receipt['source_review_complete'] is False and receipt['checks'] == []

save_rows = []
for site in graph_audit['save_sites']:
    ir = site['representation']['canonical_ir_id']
    seeds = [x for x in compiled['demands'] if x['target'].get('instruction_id') == ir]
    save_rows.append({'site_id': site['site_id'], 'instruction_id': ir,
                     'source': site['source'], 'direct_compiled_demands': seeds,
                     'direct_action_seed': any(x['preserve'] == 'action' for x in seeds)})
missing_saves = [x['instruction_id'] for x in save_rows if not x['direct_action_seed']]
assert len(save_rows) == 25 and len(missing_saves) == 14

metadata_rows = []
for ir in ['ir_346', 'ir_358']:
    op = processing['ir_semantics'][ir]['segments'][0]['ops'][0]
    demanded = next(x for x in mapping['operation_demands'] if x['instruction_id'] == ir)
    metadata_rows.append({'instruction_id': ir, 'operation_path': ['segments', 0, 'ops', 0],
                          'operation': op, 'output_demands': demanded['demands']})

checks = [
    {'id': 'ASSEMBLY-01', 'inventory_checks': ['CHECK-09', 'CHECK-10'],
     'status': 'source_supported_missing_action_seed_concern',
     'title': 'Fourteen documented default or batch save sites lack a demand seed',
     'instructions': missing_saves,
     'finding': 'All 25 saveResult sites are represented and deliver their actual operands. Only the 11 high-level aggregate sites have any directly targeted compiled demand, all action demands. The 14 low-level/default/outer-batch save sites have no compiled demand target. Task analysis_persistence requires default saving, and mapping prose acknowledges these writes; binding the independent public saver ir_077 does not itself seed each helper invocation. A required response does not by itself preserve a separate save action.',
     'implication': 'The mapping needs an action obligation at each applicable save boundary, with its existing control path and opt-outs. This is an unreviewed missing-seed concern, not a deletion recommendation or a claim that this run deleted anything.',
     'evidences': [evidence('SKILL.md', 55, 64), evidence('scripts/src/api/reports.ts', 102, 108), evidence('scripts/src/api/metadata.ts', 46, 54), evidence('scripts/src/api/indexing.ts', 89, 104)]},
    {'id': 'ASSEMBLY-02', 'inventory_checks': ['CHECK-04'],
     'status': 'concrete_demanded_selector_contract_gap',
     'title': 'Metadata wrappers lack rules for their actually demanded subfields',
     'instructions': ['ir_346', 'ir_358'],
     'finding': 'Selected mapping asks each opaque wrapper output for collection cardinality and each entry apiName, uiName and description. Each selected compute has only a whole-value output rule. There is no deterministic select/build expression inside these opaque operations that supplies those exact rules.',
     'implication': 'Even with a subsequently accepted review, these exact selectors need matching semantic rules or a supported exhaustive decomposition; the whole-value rule cannot stand in for them. In this run missing review is the earlier blocker. No error is inferred from scalar whole-value rules or the aggregate count of whole rules.',
     'evidences': [evidence('scripts/src/api/metadata.ts', 46, 48), evidence('scripts/src/api/metadata.ts', 68, 70), evidence('references/api-reference.md', 165, 183)]},
    {'id': 'ASSEMBLY-03', 'inventory_checks': ['CHECK-08', 'CHECK-09'],
     'status': 'source_supported_conditional_necessity_concern',
     'title': 'Bulk save-label contract requires nonstring contents that its formula ignores',
     'instructions': ['ir_248'],
     'finding': 'The selected rule demands the whole present dateRange value while its reason says nonstring contents are irrelevant. The source copies a string but emits the literal custom for every nonstring date range. A nonstring object needs its type distinction for this output, not its startDate/endDate contents.',
     'implication': 'This local contract overstates necessity for this consumer. Date parsing and other consumers can still require the object fields; no global deletion follows.',
     'evidences': [evidence('scripts/src/api/bulk-lookup.ts', 169, 188)]},
    {'id': 'ASSEMBLY-04', 'inventory_checks': ['CHECK-03', 'CHECK-11', 'CHECK-12'],
     'status': 'source_mismatch_preserved_but_typed_review_unavailable',
     'title': 'Ignored filters and ordering remain recorded as a source mismatch',
     'instructions': ['ir_150', 'ir_166', 'ir_167', 'ir_171'],
     'finding': 'Task retains documented filter/order obligations. Mapping explicitly records that filters and orderBy are bound with no downstream request slot; sensitivity retains the actual supplied filter and sort values. Mapping only demands the actual limit inclusion test and supplied request.limit. It does not invent correct forwarding.',
     'implication': 'The source input problem is visible in prose, but no source review completed and the receipt contains zero source_input_findings. Absence of typed findings is unavailable review evidence, not evidence that no semantic input error exists.',
     'evidences': [evidence('references/api-reference.md', 35, 43), evidence('scripts/src/api/reports.ts', 77, 100)]},
    {'id': 'ASSEMBLY-05', 'inventory_checks': ['CHECK-01', 'CHECK-02', 'CHECK-12'],
     'status': 'positive_scope_distinction_with_helper_boundary_limit',
     'title': 'Validation truth and authentication values are distinguished',
     'instructions': ['ir_024', 'ir_040', 'ir_049', 'ir_050', 'ir_059', 'ir_060'],
     'finding': 'Mapping demands only truth of propertyId, clientEmail and privateKey for the missing-setting check, but actual email/key values for the GA4 credentials constructor. Sensitivity distinguishes fixed missing-setting messages and authentication capabilities from plaintext credentials. The compact GoogleAuth calls have zero explicit credential arguments; mapping explicitly records that limitation rather than fabricating operand slots.',
     'implication': 'These selected distinctions are source supported. They do not establish complete environment-to-authentication demand propagation through the summarized zero-argument helper boundaries.',
     'evidences': [evidence('scripts/src/config/settings.ts', 40, 74), evidence('scripts/src/core/client.ts', 67, 79)]},
    {'id': 'ASSEMBLY-06', 'inventory_checks': ['CHECK-05', 'CHECK-06', 'CHECK-07'],
     'status': 'positive_consumer_and_occurrence_distinctions',
     'title': 'Status rows retain their original URL and selected inspection projection',
     'instructions': ['ir_436', 'ir_531', 'ir_551', 'ir_553', 'ir_557', 'ir_562'],
     'finding': 'Mapping pairs success and error rows with the current original URL, describes ordered iteration, suppresses child saves, and retains the aggregate save. Sensitivity separately records pre-attempt and post-attempt exceptions and the full acquired inspection result. The successful checkIndexStatus row uses indexStatus and verdict === PASS, excluding link/mobile/rich sections from that row without claiming they were never acquired.',
     'implication': 'This is source-supported consumer-specific precision. Protected-call clock/error/effect gaps remain local and explicit. It is not a proof of complete loop execution or final deletability.',
     'evidences': [evidence('scripts/src/index.ts', 304, 345), evidence('scripts/src/api/indexing.ts', 149, 192)]},
    {'id': 'ASSEMBLY-07', 'inventory_checks': ['CHECK-08', 'CHECK-09', 'CHECK-11'],
     'status': 'task_scope_concern_partly_cleared_in_mapping',
     'title': 'Empty bulk persistence exception is recognized downstream',
     'instructions': ['ir_223', 'ir_224', 'ir_249'],
     'finding': 'Task does not explicitly list the empty-bulk no-save exception. Selected mapping now explicitly says the empty branch precedes filter building, acquisition and saving and demands only rowCount and rows cardinality there. analysis_persistence records the bypass as a concrete source gap.',
     'implication': 'The earlier concern is partly cleared at mapping, but Task wording and its declared exception set remain less precise than the source. There is no justification to invent an empty-result save or create a universal persistence blocker.',
     'evidences': [evidence('scripts/src/api/bulk-lookup.ts', 155, 164)]},
    {'id': 'ASSEMBLY-08', 'inventory_checks': ['CHECK-09', 'CHECK-11'],
     'status': 'positive_public_return_and_workflow_gap_distinction',
     'title': 'Unused internal save returns are not promoted to required outputs',
     'instructions': ['ir_077', 'ir_078', 'ir_083', 'ir_088', 'ir_134', 'ir_135'],
     'finding': 'storage_save demands the public saver action, destination, complete supplied wrapper, and its returned path. The 25 internal save sites still have no output. analysis_summary states the documented read-and-Markdown obligation and the missing executable successor, selected file association, input projection and writer; it adds no whole-file demand merely because a read could observe the whole object.',
     'implication': 'The summary gap has concrete source anchors and missing relationships. It is not an excuse to discard the documented summary obligation or claim the workflow has been completed.',
     'evidences': [evidence('SKILL.md', 53, 64), evidence('scripts/src/core/storage.ts', 79, 95), evidence('scripts/src/core/storage.ts', 155, 170)]},
    {'id': 'ASSEMBLY-09', 'inventory_checks': ['CHECK-09', 'CHECK-11'],
     'status': 'task_uncertainty_classification_concern',
     'title': 'Latest-result substring mismatch may be a source error rather than an ambiguous purpose',
     'instructions': ['ir_127', 'ir_134', 'ir_135'],
     'finding': 'Task retains the operation restriction but marks latest_operation_matching unresolved. Mapping precisely describes sanitized substring matching against a full path and the possible longer-name, suffix or directory collision. The API describes filtering by operation; no public text promises prefix collisions.',
     'implication': 'The cited conflict is concrete, but a failed implementation of a clear operation filter should be considered a semantic mismatch before treating the purpose itself as undecidable. This independent audit cannot supply the missing source-review classification.',
     'evidences': [evidence('references/api-reference.md', 393, 403), evidence('scripts/src/core/storage.ts', 155, 170)]},
    {'id': 'ASSEMBLY-10', 'inventory_checks': ['CHECK-10'],
     'status': 'interface_evidence_needs_unavailable_review',
     'title': 'Some local tool contracts cite actual operands without a necessary-interface argument',
     'instructions': ['ir_451', 'ir_456'],
     'finding': 'For example, ir_451 cites only the actual saver arguments at index.ts:71-76; ir_456 cites only actual report operands at index.ts:89-94. Those lines establish invocation facts. The separate saver/report definitions and public interfaces may support required scopes, but the attached evidence alone does not show why each listed input is necessary.',
     'implication': 'Do not certify these requirements solely from the fact that the implementation passes them. The absent source review was the step intended to check interface sufficiency/necessity, retained/excluded scopes and request/response pairing. No acquired-field narrowing capability is established: the receipt inventory has zero acquisition projections.',
     'evidences': [evidence('scripts/src/index.ts', 71, 76), evidence('scripts/src/index.ts', 89, 94), evidence('scripts/src/api/reports.ts', 20, 28), evidence('scripts/src/core/storage.ts', 58, 64)]},
]

paths = [
    'task/task.json', 'task/result.json', 'steps/flow/document.md',
    'graph/initial.json', 'steps/graph/value.json', 'steps/graph/result.json',
    'steps/processing/value.json', 'steps/processing/result.json',
    'steps/task-correspondence/value.json', 'steps/task-correspondence/result.json',
    'steps/sensitivity/value.json', 'steps/sensitivity/result.json',
    'annotation/manifest.json', 'annotation/audit/compiled-response.json',
    'annotation/audit/compilation-map.json', 'review/result.json',
    'review/calls/review/a001/call.json', 'audit/input-contract-review.json', 'selection.json',
]
doc = {
    'identity': 'ga4-r2-selected-assembly-source-audit-v1',
    'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'selected_generation_audit_complete_backend_outcomes_not_assessed',
    'run_directory': str(RUN),
    'identities': {name: identity(RUN / name) for name in paths},
    'source_inventory': identity(OUT / 'source-boundary-inventory.json'),
    'source_sha256': inventory['source_sha256'],
    'source_identity_note': 'File hashes, source-package identity and the canonical input-review binding hashes have different defined roles; they are not substituted for each other.',
    'selected_task_sha256': task['task_sha256'],
    'source_representation_coverage': graph_audit['counts'],
    'descriptive_counts': {
        'realizations': len(compiled['realizations']),
        'realization_status': dict(collections.Counter(x['status'] for x in compiled['realizations'])),
        'compiled_demands': len(compiled['demands']),
        'compiled_input_contracts': dict(collections.Counter(x['kind'] for x in compiled['input_contracts'])),
        'sensitivity_declarations': len(sensitivity['declarations']),
        'sensitivity_instruction_ids': len({x['instruction_id'] for x in sensitivity['declarations']}),
        'explicit_save_action_seeds': len(save_rows) - len(missing_saves),
        'save_sites_without_direct_demands': len(missing_saves),
    },
    'review_failure': {
        'status': review['status'], 'diagnostic_only': review['diagnostic_only'],
        'reason': review['reason'], 'error_type': review['error_type'],
        'source_review_complete': receipt['source_review_complete'],
        'receipt_sha256': receipt['receipt_sha256'],
        'binding': receipt['review_core']['binding'],
        'obligation_count': len(receipt['review_core']['inventory']['obligations']),
        'contract_count': len(receipt['review_core']['inventory']['contracts']),
        'checks': len(receipt['checks']),
        'source_input_findings': len(receipt['review_core']['source_input_findings']),
        'acquisition_projections': len(receipt['review_core']['inventory']['projections']),
        'consequences': [
            'A bound immutable failure receipt exists; it is not an accepted contract review.',
            'The 344 attached obligations have no accepted checks. Presence in the inventory does not certify necessity or exclusion.',
            'InputContracts.transfer returns an input_contract_unavailable gap where a demanded operation lacks accepted review (src/skillflow/doe/input_contracts.py:112-123). Exact deterministic rules remain distinct; this statement is not a claim that every report range is globally blocked.',
            'This assistant audit is separate evidence and cannot substitute for the required source review, create review decisions, or authorize deletion conclusions.',
        ],
    },
    'checks': checks,
    'save_action_seed_inventory': save_rows,
    'metadata_demanded_selector_evidence': metadata_rows,
    'limits': [
        'No backend report, input-assessment status, propagation reachability, DOE comparison, replay, cost or execution success is assessed here; root will bind their final artifacts separately.',
        'Thirteen API sites, 25 saves and three URL loops are finite source-boundary denominators. Representation is not processing, whole-source coverage, precision, recall or semantic correctness.',
        'Only selected r2 artifacts supply generated conclusions. Earlier rejected processing was not used as selected evidence.',
        'Positive findings and concerns are independent source-audit judgments, not model-review acceptance or a proof of minimal inputs.',
    ],
    'execution': {'model_calls': 0, 'skill_executions': 0, 'analysis_or_backend_runs': 0, 'replays': 0, 'production_edits': 0},
}
target = OUT / 'selected-assembly-source-audit.json'
target.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
lines = [
    '# Selected GA4 r2 generation and assembly: independent source audit', '',
    f'Run: `{RUN}`', '',
    'The selected graph represents all 13 enumerated remote API sites, 25 saveResult sites and three explicit URL loops. This is representation coverage only. Backend outcomes are deliberately outside this audit.', '',
    'The mandatory source review failed before a native process started: 1,079,505 input characters exceeded 1,048,576. A bound failure receipt exists, but source_review_complete is false and all 344 obligations have zero accepted checks. This assistant audit does not replace that review.', '',
    'Selected mapping has 45 realizations (21 expressed, 23 partial, one retained only), compiled to 191 demands. Sensitivity has 177 declarations across 135 IR. These are descriptive counts, not semantic acceptance.', '',
]
for check in checks:
    lines += [f"## {check['id']}: {check['title']}", '',
              f"Status: `{check['status']}`. IR: {', '.join(check['instructions'])}.", '',
              check['finding'], '', check['implication'], '',
              'Source: ' + '; '.join(f"{e['file']}:{e['start_line']}-{e['end_line']}" for e in check['evidences']) + '.', '']
lines += ['## Exact identities and limits', '',
          f"Selected processing file SHA256: `{doc['identities']['steps/processing/value.json']['file_sha256']}`.", '',
          f"Selected mapping file SHA256: `{doc['identities']['steps/task-correspondence/value.json']['file_sha256']}`.", '',
          f"Selected sensitivity file SHA256: `{doc['identities']['steps/sensitivity/value.json']['file_sha256']}`.", '',
          f"Failure receipt semantic SHA256: `{receipt['receipt_sha256']}`.", '',
          'The JSON companion contains every source quote, file hash, selected artifact hash, demanded metadata selector and all 25 save-seed checks. Canonical binding identities and file hashes are recorded separately.', '',
          *[f'- {x}' for x in doc['limits']], '',
          'Audit execution: zero model calls, Skill executions, backend runs, replays or production edits.', '']
(OUT / 'selected-assembly-source-audit.en.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'audit': str(target), 'sha256': identity(target)['file_sha256'],
                  'checks': len(checks), 'missing_save_action_seeds': missing_saves,
                  'mandatory_review': 'unavailable'}, ensure_ascii=False))
