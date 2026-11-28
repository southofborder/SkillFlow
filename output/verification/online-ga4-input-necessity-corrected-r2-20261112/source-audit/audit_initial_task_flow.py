"""Read the replacement run's own initial Task and flow; write sibling audit only."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RUN = ROOT / 'experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209'
SOURCE = RUN / 'source/inputs/package'
TASK = json.loads((RUN / 'task/task.json').read_text(encoding='utf-8'))
FLOW = (RUN / 'steps/flow/document.md').read_text(encoding='utf-8').splitlines()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def src(file, start, end):
    lines = (SOURCE / file).read_text(encoding='utf-8').splitlines()
    assert 1 <= start <= end <= len(lines)
    return {'file': file, 'start_line': start, 'end_line': end, 'quote': '\n'.join(lines[start - 1:end])}


def tasks(ids, kind='requirements'):
    rows = [{'artifact': 'task/task.json', 'json_pointer': f'/{kind}/{i}', **row}
            for i, row in enumerate(TASK[kind]) if row['id'] in ids]
    assert len(rows) == len(ids), ids
    return rows


def flow(needle):
    rows = [(i, text) for i, text in enumerate(FLOW, 1) if needle in text]
    assert len(rows) == 1, (needle, len(rows))
    line, text = rows[0]
    return {'artifact': 'steps/flow/document.md', 'start_line': line, 'end_line': line, 'quote': text}


checks = [
    {'id': 'R2-TF-01', 'status': 'supported', 'title': 'Public realtime operations and aggregate snapshot remain distinct',
     'task': tasks(['ga4_realtime_reports', 'ga4_live_snapshot']) + tasks(['realtime_identity_scope'], 'issues'),
     'flow': [flow('Each realtime function takes')],
     'source': [src('references/api-reference.md', 118, 159), src('scripts/src/api/realtime.ts', 24, 99)],
     'assessment': 'The replacement Task explicitly supports all four selected realtime report forms separately from the aggregate snapshot and rejects an unsupported individual-user identity interpretation. Flow preserves their distinct dimensions, metrics, saves and returns.',
     'next_check': 'Map the selected standalone operations without requiring execution of liveSnapshot or inventing individual user data.'},
    {'id': 'R2-TF-02', 'status': 'source_scope_concern', 'title': 'Empty bulk lookup no-save exception is absent from Task wording',
     'task': tasks(['bulk_path_matching', 'analysis_persistence', 'persistence_exceptions']) + tasks(['save_scope'], 'issues'),
     'flow': [flow('Empty input returns `{rows: [], rowCount: 0}` before client acquisition or saving.')],
     'source': [src('scripts/src/api/bulk-lookup.ts', 149, 164), src('scripts/src/api/bulk-lookup.ts', 183, 191)],
     'assessment': 'bulk_path_matching retains the empty report and no-API behavior, but does not say that this path also skips saving. analysis_persistence broadly requires default saves; persistence_exceptions lists save=false and aggregate-only cases but not the empty bulk return. Flow accurately preserves the early return before the save. This is a concrete initial-Task applicability omission to review, not evidence that the source writes an empty file.',
     'next_check': 'Check final Task/review and mapping for a localized empty-input no-save qualification. Do not invent a required empty-result write or suppress the actual nonempty save.'},
    {'id': 'R2-TF-03', 'status': 'review_reason_concern', 'title': 'Latest-operation ambiguity may instead be an implementation mismatch',
     'task': tasks(['storage_latest']) + tasks(['latest_operation_matching'], 'issues'),
     'flow': [flow('optionally filters by a sanitized path substring')],
     'source': [src('references/api-reference.md', 393, 403), src('scripts/src/core/storage.ts', 155, 171)],
     'assessment': 'The unresolved issue gives precise evidence and consequence: a substring can select a longer operation name. However, the public requirement is selection restricted by the requested operation, and no source text declares prefix matching as a required user option. The current substring implementation alone may not establish a competing Task obligation. Thus the reason merits semantic review rather than automatic acceptance as an unavoidable Task uncertainty.',
     'next_check': 'Determine whether the clear operation identity can be retained and collisions reported as source behavior mismatches. If uncertainty remains, identify the specific source-supported matching alternatives and confine their effect to this selection.'},
    {'id': 'R2-TF-04', 'status': 'supported_scoped_uncertainty', 'title': 'Ranking and keyword granularity have concrete competing source meanings',
     'task': tasks(['sc_top_pages', 'sc_overview', 'sc_seo_page_performance', 'sc_keyword_analysis']) + tasks(['search_pages_ranking', 'keyword_device_granularity'], 'issues'),
     'flow': [flow('The reference describes top pages by impressions; the index describes clicks; the request supplies no sort.'), flow('`keywordAnalysis(dateRange?)`; `seoPagePerformance(dateRange?)`')],
     'source': [src('SKILL.md', 79, 85), src('references/api-reference.md', 224, 233), src('scripts/src/index.ts', 260, 292), src('scripts/src/api/searchConsole.ts', 124, 154)],
     'assessment': 'Click and impression rankings can change selected rows. Per-query device information and separate sitewide device totals require different data. The issues identify these exact distinctions and sources; they do not invoke generic opacity or unknown values.',
     'next_check': 'Track the affected Search Console requirements and actual range propagation; these issues alone do not make unrelated GA4 or authentication inputs semantically unknown.'},
    {'id': 'R2-TF-05', 'status': 'supported', 'title': 'Ignored optional controls are not silently repaired',
     'task': tasks(['custom_ga4_report', 'custom_ga4_report_controls']) + tasks(['custom_report_controls_gap'], 'issues'),
     'flow': [flow('it accepts `filters` and `orderBy` without sending them.')],
     'source': [src('references/api-reference.md', 31, 45), src('scripts/src/api/reports.ts', 77, 108)],
     'assessment': 'Task keeps the documented filter/order/limit obligations and explicitly records implementation gaps; Flow preserves actual non-forwarding and truthy-limit control. Missing SDK translation details do not become an unsupported whole-Task refusal.',
     'next_check': 'The three controls share one requirement ID. Scope later missing/wrong-input findings to the actual control instead of treating valid limit handling as missing merely because filters and order are absent.'},
    {'id': 'R2-TF-06', 'status': 'scope_watchpoint', 'title': 'A public saved-path return must not become an output at every internal save',
     'task': tasks(['analysis_persistence', 'persistence_exceptions', 'storage_save']),
     'flow': [flow('The public saver returns the path; analysis callers discard it')],
     'source': [src('references/api-reference.md', 359, 371), src('scripts/src/core/storage.ts', 58, 95), src('scripts/src/index.ts', 71, 76)],
     'assessment': 'storage_save includes the documented public return contract; the replacement Flow explicitly says analysis callers discard that path and return their own payloads. The write action, write path and serialized payload remain distinct obligations. No erroneous internal output seed has been observed yet.',
     'next_check': 'For all 25 source save sites, inspect action versus output realizations and selected demand. Retain necessary writes while avoiding invented externally consumed return values.'},
    {'id': 'R2-TF-07', 'status': 'scope_watchpoint', 'title': 'Validation, settings fields and client state need separate demand scopes',
     'task': tasks(['google_setup', 'client_validation', 'service_targets']),
     'flow': [flow('Each client getter returns an existing handle with its creation-time credentials')],
     'source': [src('scripts/src/config/settings.ts', 40, 74), src('scripts/src/core/client.ts', 23, 53), src('scripts/src/core/client.ts', 67, 133)],
     'assessment': 'Task precisely states the actual three presence checks on initialization. Flow preserves cache hits, initialization credentials, separate current request targets and absence of siteUrl validation. These facts do not make all settings values necessary to every operation.',
     'next_check': 'Validate field-level transfer: credential values for construction; presence and errors for validation; propertyId for GA4 target formatting; siteUrl for Search Console target; resultsDir/propertyId for storage. Retain actual whole settings reads and cache-version facts even when one consumer has narrower demand.'},
    {'id': 'R2-TF-08', 'status': 'scope_watchpoint', 'title': 'Metadata collection selection and full-response scope',
     'task': tasks(['ga4_field_discovery']) + tasks(['metadata_collection_representation'], 'issues'),
     'flow': [flow('`getAvailableDimensions` and `getAvailableMetrics` return and optionally save objects containing the selected array')],
     'source': [src('references/api-reference.md', 164, 193), src('scripts/src/api/metadata.ts', 26, 95), src('scripts/src/index.ts', 355, 362)],
     'assessment': 'Task resolves the array-versus-wrapper conflict with the declared response type and both selective implementations. Flow preserves dimension-only and metric-only results versus full getPropertyMetadata and getAvailableFields responses. Task wording emphasizes requested collections; the reference also names a full metadata response for the full operation.',
     'next_check': 'Check output-specific contracts and any explicit whole-response obligation at the full operation. Do not propagate a whole-metadata demand to a selective operation, nor silently narrow a genuinely required full result. No remote response mask is established by this source.'},
    {'id': 'R2-TF-09', 'status': 'supported', 'title': 'Per-URL results retain action, count, identity and conditional fields',
     'task': tasks(['index_recrawl', 'index_removal', 'index_recrawl_batch', 'index_reindex_urls', 'index_inspect_url', 'index_check_urls']),
     'flow': [flow('success keeps the input URL and only the `indexStatus` projection')],
     'source': [src('scripts/src/api/indexing.ts', 57, 105), src('scripts/src/api/indexing.ts', 143, 193), src('scripts/src/index.ts', 301, 346)],
     'assessment': 'Task preserves submission versus actual indexing, per-item order and errors, distinct low-level/high-level failure handling, and detailed inspection versus status-check output. Flow explicitly preserves possible remote effects despite a caught failure, notification URL overwrite, and the narrower status projection.',
     'next_check': 'Verify member pairing, counts, exception scope and shared-call effects. Fields unnecessary to a status-only consumer can still be required by standalone inspection or another save; union uses before proposing deletion.'},
    {'id': 'R2-TF-10', 'status': 'supported', 'title': 'Summary remains a declared duty despite the missing implemented link',
     'task': tasks(['analysis_summary']) + tasks(['summary_trigger'], 'issues'),
     'flow': [flow('no summary writer or automatic handoff from an analysis return to a reader'), flow('the file selection for any particular analysis run remains unresolved.')],
     'source': [src('SKILL.md', 53, 64), src('SKILL.md', 129, 142), src('scripts/src/core/storage.ts', 103, 171)],
     'assessment': 'Task keeps summary creation and provenance from the analysis saved data without demanding that each standalone helper generate Markdown. Flow distinguishes independent file readers and the absent implemented invocation-to-file-to-summary link. Missing implementation does not erase the declared task.',
     'next_check': 'Check the source-declared summary boundary and precise file identity or local gap. Do not claim full workflow coverage solely because the 13 SDK sites and 25 source saves are represented.'}
]

task_result = json.loads((RUN/'task/result.json').read_text(encoding='utf-8'))
flow_result = json.loads((RUN/'steps/flow/result.json').read_text(encoding='utf-8'))
assert sha(RUN/'steps/flow/document.md') == flow_result['value_sha256']
paths = ['task/task.json', 'task/result.json', 'task/manifest.json', 'steps/flow/document.md',
         'steps/flow/result.json', 'steps/flow/manifest.json']
identities = {p: {'sha256': sha(RUN/p)} for p in paths}
identities['task/task.json'].update(schema_version=TASK['schema_version'], task_sha256=TASK['task_sha256'])
identities['steps/flow/document.md']['value_sha256'] = flow_result['value_sha256']
data = {'identity': 'ga4-r2-initial-task-flow-audit-v1', 'created_at': datetime.now(timezone.utc).isoformat(),
        'status': 'provisional_initial_material_only', 'run_directory': str(RUN),
        'source_sha256': TASK['source_sha256'], 'source_inventory_sha256': sha(OUT/'source-boundary-inventory.json'),
        'artifact_identities': identities, 'accepted_calls': {'task': task_result['accepted_call'], 'flow': flow_result['accepted_call']},
        'counts': {'requirements': len(TASK['requirements']), 'issues': len(TASK['issues']),
                   'issue_resolutions': dict(Counter(row['resolution'] for row in TASK['issues'])),
                   'check_statuses': dict(Counter(row['status'] for row in checks))},
        'checks': checks,
        'limits': ['Only this replacement run\'s Task and flow were read; no prior generated answers or conclusions were imported.',
                   'These initial artifacts can be superseded by the allowed repair. Recheck final selected identities before final reporting.',
                   'Task concerns and scope watchpoints are provisional source assessments, not observed final demand errors or deletion findings.',
                   'Generated CFG, annotation, processing, source review, demand and DOE were not assessed here.',
                   'No model requests, Skill execution, replay, production edits or historical edits were performed.']}
with (OUT/'task-flow-initial-audit.json').open('x', encoding='utf-8') as handle:
    json.dump(data, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
md = ['# Replacement GA4 initial Task and flow audit', '',
      '**Provisional:** derived from this replacement run only. Allowed repair can supersede these artifacts; final selected material has not been audited.', '',
      f"Task `{TASK['task_sha256']}`: {len(TASK['requirements'])} requirements, {len(TASK['issues'])} issues, three unresolved.", '',
      f"Flow `{flow_result['value_sha256']}`. Both accepted their first response without structural correction.", '',
      '## Source-backed checks', '']
for row in checks:
    md += [f"- **{row['id']} — {row['status']} — {row['title']}.** {row['assessment']} Next check: {row['next_check']}"]
md += ['', 'Exact source quotations, generated text locations and artifact hashes are in `task-flow-initial-audit.json`. No final input deletion or DOE conclusion is made.', '']
with (OUT/'task-flow-initial-audit.en.md').open('x', encoding='utf-8') as handle:
    handle.write('\n'.join(md))
print(json.dumps({'status': data['status'], 'counts': data['counts'], 'task_sha256': TASK['task_sha256'],
                  'flow_sha256': flow_result['value_sha256'], 'audit_sha256': sha(OUT/'task-flow-initial-audit.json')}, indent=2))
