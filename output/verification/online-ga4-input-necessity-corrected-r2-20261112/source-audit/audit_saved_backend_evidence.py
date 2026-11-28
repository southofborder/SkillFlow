"""Summarize already saved backend evidence; never invoke the backend itself."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path('D:/Projects/SkillFlow')
RUN = ROOT / 'experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209'
OUT = ROOT / 'output/verification/online-ga4-input-necessity-corrected-r2-20261112/source-audit'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def identity(path):
    return {'path': str(path), 'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


support = read(RUN / 'doe/audit/demand-support.json')
doe = read(RUN / 'doe/doe-result.json')
receipt = read(RUN / 'audit/input-contract-review.json')
compiled = read(RUN / 'annotation/audit/compiled-response.json')
graph_audit = read(OUT / 'selected-graph-audit.json')
assembly_audit = read(OUT / 'selected-assembly-source-audit.json')
task = read(RUN / 'task/task.json')
assessment_rows = support['input_assessments']
range_rows = [row for assessment in assessment_rows for row in assessment['ranges']]
required = [row for row in range_rows if row['status'] == 'required']
unresolved = [row for row in range_rows if row['status'] == 'unresolved']
diagnostics = {row['id']: row for row in support['diagnostics']}
global_diagnostics = [row for row in support['diagnostics'] if row.get('instruction_id') is None and row['blocking']]
global_ids = {row['id'] for row in global_diagnostics}
data_reviews = [row for sink in doe['sinks'] for row in sink['data_reviews']]
derivations = {**support['extra_derivations'], **doe['derivations']['demand']}
goals = {row['id']: row for row in compiled['demands']}
upstream = support['coverage']['upstream']
assert support['input_contract_review_sha256'] == receipt['receipt_sha256']
assert receipt['source_review_complete'] is False
assert len(assessment_rows) == 1509
assert len(range_rows) == 4271
assert len(required) == 1100 and len(unresolved) == 3171
assert all(row['modification'] is None for row in range_rows)
assert len(data_reviews) == 83 and all(row['reduction'] is None for row in data_reviews)


def instruction_summary(ir):
    rows = [x for x in assessment_rows if x['instruction_id'] == ir]
    return {
        'instruction_id': ir,
        'upstream_status': upstream.get(ir),
        'assessment_ids': [x['id'] for x in rows],
        'assessment_count': len(rows),
        'range_status_counts': dict(collections.Counter(y['status'] for x in rows for y in x['ranges'])),
        'required_selectors': [{'assessment_id': x['id'], 'node_kind': x['node_kind'],
                               'operation_id': x.get('operation_id'), 'input_index': x['input_index'],
                               'range': y} for x in rows for y in x['ranges'] if y['status'] == 'required'],
        'local_diagnostics': [x for x in support['diagnostics'] if x.get('instruction_id') == ir],
    }


def saved_chain(demand_id):
    """Follow stored parent identifiers only, without deriving any new demand."""
    pending, seen, rows = [demand_id], set(), {}
    while pending:
        item = pending.pop()
        if item in seen:
            continue
        seen.add(item)
        assert item in derivations, item
        row = derivations[item]
        rows[item] = row
        pending.extend(row['parents'])
    seeds = {row['seed_goal_id'] for row in rows.values()}
    return {'start_demand': demand_id, 'stored_derivations': rows,
            'selected_goals': {key: goals[key] for key in seeds},
            'matching_assessments': [{'id': x['id'], 'instruction_id': x['instruction_id'],
                                     'node_kind': x['node_kind'], 'location': x['location'], 'range': y}
                                    for x in assessment_rows for y in x['ranges']
                                    if demand_id in y['demand_refs']]}


boundaries = {}
for kind in ['api_sites', 'save_sites']:
    boundaries[kind] = [{'site_id': x['site_id'], 'source': x['source'],
                         'instruction_id': x['representation']['canonical_ir_id'],
                         'upstream_status': upstream[x['representation']['canonical_ir_id']]}
                        for x in graph_audit[kind]]

missing_save_ids = [x['instruction_id'] for x in assembly_audit['save_action_seed_inventory']
                    if not x['direct_action_seed']]
required_examples = {
    'validation_property_truth': saved_chain('demand_a0785d7c68a29b640287'),
    'ga4_private_key_field': saved_chain('demand_c852f04f208c257f54a0'),
    'status_row_index_status': saved_chain('demand_eacf47ee70139a0982f4'),
    'report_acquisition_metric_value': saved_chain('demand_5e833f90e0fc381e32bb'),
}
source_concerns = [
    {'id': 'BACKEND-01', 'source_audit_check': 'ASSEMBLY-01',
     'title': 'Missing save seeds are not converted into deletion',
     'saved_evidence': [instruction_summary(ir) for ir in missing_save_ids],
     'finding': 'Each of the 14 default/low-level save boundaries without a direct demand target remains unresolved in the saved assessments. No modification is produced. One of those saves, ir_426, is also blocked by the earlier unsupported optional-section branch. Missing seeds remain a source/mapping concern; unresolved retention is not proof that their obligations were correctly expressed.'},
    {'id': 'BACKEND-02', 'source_audit_check': 'ASSEMBLY-02',
     'title': 'Missing review precedes the metadata selector problem',
     'saved_evidence': [instruction_summary('ir_346'), instruction_summary('ir_358')],
     'finding': 'Each metadata wrapper has six assessed input nodes and 30 unresolved range records, with no required range. The saved diagnostics are input_contract_unavailable for the actual cardinality and entry-field demands. The independent source audit also found only whole-output rules, but this run did not reach an accepted-review transfer that could diagnose the later exact-selector issue. Do not relabel the observed blocker as an output-rule-gap error.'},
    {'id': 'BACKEND-03', 'source_audit_check': 'ASSEMBLY-03',
     'title': 'Overbroad bulk label contract does not establish necessity',
     'saved_evidence': [instruction_summary('ir_248')],
     'finding': 'The two assessed input nodes at ir_248 are unresolved. The selected candidate overstates nonstring dateRange value necessity for the custom label, but no accepted review or required output propagation applies that contract here. Other date consumers can still need the actual range fields.'},
    {'id': 'BACKEND-04', 'source_audit_check': 'ASSEMBLY-04',
     'title': 'Ignored filters remain observed without a fabricated semantic fix',
     'saved_evidence': [instruction_summary('ir_150'), instruction_summary('ir_171')],
     'finding': 'The actual report request fields have required rows through selected Task seeds and deterministic construction. No required selector for filters or orderBy appears at ir_150. Their actual read/select facts and sensitivity declarations remain in the selected inputs. Zero typed source-input findings results from the unavailable source review; it does not establish that these documented but unused controls are correct or deletable.'},
    {'id': 'BACKEND-05', 'source_audit_check': 'ASSEMBLY-05',
     'title': 'Deterministic validation and credential precision survives',
     'saved_evidence': [instruction_summary('ir_024'), instruction_summary('ir_040')],
     'finding': 'The ir_024 input has truth requirements for propertyId, clientEmail and privateKey. The ir_040 input has field-value requirements for clientEmail and privateKey through task_value, constructed_member, selected_path and actual_operand. The stored chains preserve requirement and seed IDs. These are positive deterministic results conditional on unreviewed semantic seeds, not successful black-box input-contract verification.'},
    {'id': 'BACKEND-06', 'source_audit_check': 'ASSEMBLY-06',
     'title': 'Index-status consumer projection is recorded but upstream necessity is limited',
     'saved_evidence': [instruction_summary('ir_551'), instruction_summary('ir_553')],
     'finding': 'The successful status-row consumer ir_553 has 16 required range records, including value.indexStatus and value.indexStatus.verdict, and nine unresolved records. Its stored demand chain keeps index_check_urls and the selected result goal. Upstream ir_551 retains 100 unresolved records and local review/processing gaps. This is not a reviewed proof that acquired mobile, rich-result or link data can be removed.'},
    {'id': 'BACKEND-07', 'source_audit_check': 'ASSEMBLY-08',
     'title': 'The public saver and absent summary retain distinct evidence',
     'saved_evidence': [instruction_summary('ir_077'), instruction_summary('ir_135')],
     'finding': 'The public saver has direct required whole-value rows for its supplied wrapper and destination, while serialization/write transfer remains limited. The summary requirement has an unbound_requirement diagnostic, and the concrete missing summary successor/file-association/projection/writer is retained at ir_135. No invented summary input projection or output file appears in the backend result.'},
]

projection_rows = [x['retrieval_projection'] for x in assessment_rows if x.get('retrieval_projection')]
report = {
    'identity': 'ga4-r2-saved-backend-source-audit-v1',
    'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'read_only_audit_of_saved_partial_backend',
    'run_directory': str(RUN),
    'identities': {p: identity(RUN / p) for p in [
        'doe/audit/demand-support.json', 'doe/doe-result.json', 'doe/manifest.json',
        'audit/input-contract-review.json', 'annotation/audit/compiled-response.json',
        'steps/task-correspondence/value.json', 'steps/sensitivity/value.json',
        'task/task.json', 'graph/initial.json', 'propagation/manifest.json',
    ]},
    'independent_source_audit': identity(OUT / 'selected-assembly-source-audit.json'),
    'review_receipt': {'sha256': receipt['receipt_sha256'], 'review_status': receipt['review_status'],
                       'source_review_complete': receipt['source_review_complete'], 'checks': len(receipt['checks'])},
    'counts': {
        'input_assessments': len(assessment_rows), 'range_records': len(range_rows),
        'range_status': {status: sum(row['status'] == status for row in range_rows)
                         for status in ['required', 'unresolved', 'deletable']},
        'assessment_node_kinds': dict(collections.Counter(row['node_kind'] for row in assessment_rows)),
        'assessment_coverage': dict(collections.Counter(row['coverage'] for row in assessment_rows)),
        'assessments_with_unresolved_range': sum(any(y['status'] == 'unresolved' for y in x['ranges']) for x in assessment_rows),
        'required_ranges_with_contract_refs': sum(bool(row['contract_refs']) for row in required),
        'modifications': sum(row['modification'] is not None for row in range_rows),
        'typed_input_findings': len(support['input_findings']),
        'doe_sinks': len(doe['sinks']), 'data_reviews': len(data_reviews),
        'data_review_conclusions': dict(collections.Counter(row['conclusion'] for row in data_reviews)),
        'reductions': sum(row['reduction'] is not None for row in data_reviews),
        'retrieval_projection_status': dict(collections.Counter(row['status'] for row in projection_rows)),
        'upstream_ir_status': dict(collections.Counter(upstream.values())),
        'demand_diagnostic_codes': dict(collections.Counter(row['code'] for row in support['diagnostics'])),
        'doe_diagnostic_codes': dict(collections.Counter(row['code'] for row in doe['diagnostics'])),
    },
    'program_positive_evidence': {
        'required_range_rule_reasons': dict(collections.Counter(row['reason'] for row in required)),
        'examples': required_examples,
        'constraint_checks': doe['constraints']['checks'],
        'constraint_modification_preservation_checks': len(doe['constraints']['preservation']),
        'qualification': 'Counts are records over IR and operation inputs, acquisition outputs, information properties, requirements and seeds. They are not 1,100 unique semantic fields proven minimally necessary. None of the required rows cites an accepted semantic input contract; the source review never completed. Three constraints are satisfied only within the selected static model, and no deletion-preservation test was established.',
    },
    'localization': {
        'global_blocking_diagnostics': global_diagnostics,
        'global_count': len(global_diagnostics),
        'all_global_ids_on_sinks': sum(global_ids.issubset(set(row['limitations'])) for row in doe['sinks']),
        'range_rows_with_any_global_diagnostic': sum(bool(global_ids.intersection(row['diagnostic_refs'])) for row in unresolved),
        'assessment_rows_with_any_global_diagnostic': sum(any(global_ids.intersection(y['diagnostic_refs']) for y in x['ranges']) for x in assessment_rows),
        'contract_unavailable_count': sum(row['code'] == 'input_contract_unavailable' for row in support['diagnostics']),
        'contract_unavailable_affected_ir_count_distribution': dict(collections.Counter(len(row.get('affected_instruction_ids', [])) for row in support['diagnostics'] if row['code'] == 'input_contract_unavailable')),
        'not_processed_ir': {key: value for key, value in upstream.items() if value != 'processed'},
        'qualification': 'Every unavailable-contract diagnostic names one affected IR. Independently, 24 mapping expression gaps, three retained Task issues and the unbound summary requirement remain global under the current Task/mapping policy and occur at every sink. Their presence must not be explained as one local opaque compute gap indiscriminately spreading to the whole report.',
    },
    'source_boundary_processing': boundaries,
    'source_concerns_and_actual_backend_evidence': source_concerns,
    'acquisition_note': 'All 135 assessed acquisition outputs carry unestablished retrieval projection, with no accepted capability. This is not proof that the underlying interface cannot project fields; it means this run established no permissible fetch-side clipping.',
    'overall_conclusion': 'The saved backend demonstrates finite processing coverage, explicit input enumeration and some field-level deterministic requirement propagation. It establishes no deletable input, no sensitive-payload reduction and no reviewed black-box necessity result. no_excess_established is unresolved evidence, not a safe verdict or proof of no excess.',
    'limits': ['This audit only reads already saved evidence and selected source-audit material.',
               'Root owns the sole active replay; its outcome and token cost are outside this audit.',
               'All historical artifacts and run records are unchanged; no extra analysis execution, model call, Skill execution or replay was performed.'],
}
target = OUT / 'saved-backend-source-audit.json'
target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
md = [
    '# Saved GA4 r2 backend: source-bound evidence audit', '',
    'The saved demand and DOE results are partial. The source review did not start because its input exceeded the CLI limit. Its bound failure receipt has zero accepted checks. This independent audit cannot replace that review.', '',
    '| Saved measure | Result |', '|---|---|',
    '| Input assessment records | 1,509: 665 CFG inputs, 709 operation inputs, 135 acquisition outputs |',
    '| Range records | 4,271: 1,100 required, 3,171 unresolved, 0 deletable |',
    '| Assessment coverage | 1,497 processed, 11 blocked, 1 unmodeled |',
    '| Records containing unresolved ranges | All 1,509 |',
    '| Required rows citing an accepted input contract | 0 |',
    '| Modifications and reductions | 0 and 0 |',
    '| DOE | 20 sinks, 83 comparisons, all no_excess_established |',
    '| Acquisition projection | 135 unestablished, no accepted capability |',
    '| Upstream IR | 553 processed, 1 unmodeled, 9 blocked |',
    '| Enumerated source boundaries processed | 13/13 remote API sites; 24/25 save sites |', '',
    'The blocked save is inspectUrl\'s ir_426. Source representation and static processing do not establish actual runtime success or complete source semantics.', '',
    'Positive program evidence is concrete: ir_024 retains truth of the three validation fields; ir_040 traces privateKey through deterministic construction and selection to the credentials slot; ir_553 retains the original status-row projection; ir_171 reports requested analytics value fields at the acquisition output. The JSON contains saved chains, requirement IDs, seed goals and exact assessment locations. These are conditional results from unreviewed Task/mapping seeds, not 1,100 unique fields proven minimally necessary.', '',
    'All 243 input_contract_unavailable diagnostics name one affected IR. Separately, all 20 sinks carry 28 global limitations: 24 requirement-expression gaps, three Task issues, and the unbound summary requirement. Those global diagnostics occur on 1,466 unresolved range records across 1,466 assessments. Their broad effect is distinct from the localized contract gaps.', '',
]
for check in source_concerns:
    md += [f"## {check['id']}: {check['title']}", '', check['finding'], '']
md += [
    '## What the saved result establishes', '',
    report['overall_conclusion'], '',
    'The three supported constraint checks are satisfied within the selected static model; no modification-preservation result was published. Zero typed input findings reflects unavailable source review, not absence of ignored filters, wrong fields or other semantic errors.', '',
    f"Demand support: `{report['identities']['doe/audit/demand-support.json']['path']}`; SHA256 `{report['identities']['doe/audit/demand-support.json']['file_sha256']}`.", '',
    f"DOE result: `{report['identities']['doe/doe-result.json']['path']}`; SHA256 `{report['identities']['doe/doe-result.json']['file_sha256']}`.", '',
    f"Input-review receipt semantic SHA256: `{receipt['receipt_sha256']}`.", '',
    'The JSON companion binds all source and selected artifact identities, counts, saved derivation chains, localized/global diagnostics and per-source-boundary processing states. Replay and costs remain with the root controller audit.', '',
    'Audit execution: zero model calls, Skill executions, backend runs, replays or production/run-record edits.', '',
]
(OUT / 'saved-backend-source-audit.en.md').write_text('\n'.join(md), encoding='utf-8')
print(json.dumps({'audit': str(target), 'sha256': identity(target)['file_sha256'],
                  'counts': report['counts'], 'global_diagnostics': len(global_diagnostics)}, ensure_ascii=False))
