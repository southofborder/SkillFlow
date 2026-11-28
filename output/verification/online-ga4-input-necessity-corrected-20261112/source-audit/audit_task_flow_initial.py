"""One read-only comparison of initial Task/flow with the new frozen source."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RUN = ROOT / 'experiments/doe/runs/document-guided-ga4-input-necessity-corrected-high-20261112-174538'
SOURCE = RUN / 'source/inputs/package'
TASK = json.loads((RUN / 'task/task.json').read_text(encoding='utf-8'))
FLOW = (RUN / 'steps/flow/document.md').read_text(encoding='utf-8').splitlines()
TASK_RESULT = json.loads((RUN / 'task/result.json').read_text(encoding='utf-8'))
FLOW_RESULT = json.loads((RUN / 'steps/flow/result.json').read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(file, start, end):
    lines = (SOURCE / file).read_text(encoding='utf-8').splitlines()
    assert 1 <= start <= end <= len(lines)
    return {'file': file, 'start_line': start, 'end_line': end,
            'quote': '\n'.join(lines[start - 1:end])}


def task(ids, kind='requirements'):
    return [{'artifact': 'task/task.json', 'json_pointer': f'/{kind}/{index}', **row}
            for index, row in enumerate(TASK[kind]) if row['id'] in ids]


def flow(needle):
    hits = [(index, text) for index, text in enumerate(FLOW, 1) if needle in text]
    assert len(hits) == 1, (needle, len(hits))
    line, text = hits[0]
    return {'artifact': 'steps/flow/document.md', 'start_line': line, 'end_line': line, 'quote': text}


checks = [
    {'id': 'TF-01', 'status': 'supported', 'topic': 'Filters and ordering remain real declared obligations',
     'task_evidence': task(['R08', 'R09']) + task(['I04'], 'issues'),
     'flow_evidence': [flow('It accepts `filters` and `orderBy` but sends neither.')],
     'source_evidence': [source('references/api-reference.md', 31, 45), source('scripts/src/api/reports.ts', 77, 108)],
     'assessment': 'Task preserves the two separately documented duties and treats their source implementation omission as a gap. Flow preserves the actual omission instead of inventing a corrected request.',
     'later_check': 'Task-correspondence/source review must expose missing filter/order behavior; unused extracted fields alone must not be presented as successful fulfillment of those duties.'},
    {'id': 'TF-02', 'status': 'scope_watchpoint', 'topic': 'Saved filepath return versus necessary write action',
     'task_evidence': task(['R40', 'R41', 'R42']),
     'flow_evidence': [flow('The analysis call sites discard the returned path.')],
     'source_evidence': [source('references/api-reference.md', 360, 371), source('scripts/src/core/storage.ts', 58, 94), source('scripts/src/index.ts', 71, 76)],
     'assessment': 'R41 includes the save utility return contract. This is supported for the public saveResult API, but the wording is broad. The 25 analysis call sites discard that return, which flow states explicitly. No erroneous output seed is established at this stage.',
     'later_check': 'Do not create a required external filepath output at every internal save invocation. Preserve the necessary write, path identity, payload and supported metadata requirements independently.'},
    {'id': 'TF-03', 'status': 'scope_watchpoint', 'topic': 'Validation and cached clients',
     'task_evidence': task(['R02', 'R03', 'R04']),
     'flow_evidence': [flow('Each of the three client getters returns its existing handle on a cache hit.')],
     'source_evidence': [source('scripts/src/config/settings.ts', 54, 74), source('scripts/src/core/client.ts', 23, 43), source('scripts/src/core/client.ts', 87, 123)],
     'assessment': 'R03 says initialization rejects three missing settings. Source supports those checks for each cache-miss initializer, including propertyId for Search Console and Indexing. Flow accurately preserves the cache-hit bypass. Actual validation is not evidence that every value is an interface input to every later request.',
     'later_check': 'Bind initialization validation only to cache misses and preserve the three distinct state identities. PropertyId presence checks and authentication field values have different demands; unrelated settings must not become whole-object requirements.'},
    {'id': 'TF-04', 'status': 'supported', 'topic': 'Metadata consumer separation',
     'task_evidence': task(['R23']) + task(['I10'], 'issues'),
     'flow_evidence': [flow('Each metadata call fetches')],
     'source_evidence': [source('scripts/src/api/metadata.ts', 38, 95), source('scripts/src/index.ts', 355, 361)],
     'assessment': 'Task distinguishes dimensions-only, metrics-only and combined metadata. Flow preserves the two single-field objects and empty-array defaults, versus a full response for getPropertyMetadata/getAvailableFields.',
     'later_check': 'Check output-specific contracts and selected-field demand; do not use the full-metadata rule for the selective consumers. Remote projection remains unsupported unless separate interface evidence establishes it.'},
    {'id': 'TF-05', 'status': 'supported', 'topic': 'Inspection field selection and loop association',
     'task_evidence': task(['R34', 'R35', 'R36', 'R37', 'R38', 'R39']),
     'flow_evidence': [flow('Its catch retains the input URL with `indexed: false`')],
     'source_evidence': [source('scripts/src/api/indexing.ts', 57, 105), source('scripts/src/api/indexing.ts', 143, 193), source('scripts/src/index.ts', 301, 346)],
     'assessment': 'Task separates single inspection fields from the high-level status check, preserves ordered per-URL outcomes and continuation on caught errors, and distinguishes submission from actual indexed status. Flow additionally preserves reindexUrls spread overwrite and absence of a local catch in requestIndexingBatch.',
     'later_check': 'Preserve member identity/count/order and the actual returned-URL fallback/overwrite. Status-check consumers require indexStatus; other standalone consumers can require the other inspection sections.'},
    {'id': 'TF-06', 'status': 'supported', 'topic': 'Save controls, empty input and summary duty',
     'task_evidence': task(['R33', 'R40', 'R46']) + task(['I07', 'I08'], 'issues'),
     'flow_evidence': [flow('No supplied implementation links a run to a later read or writes that summary.')],
     'source_evidence': [source('SKILL.md', 53, 64), source('scripts/src/api/bulk-lookup.ts', 149, 164), source('scripts/src/index.ts', 179, 203)],
     'assessment': 'Task preserves the summary duty without making every standalone helper a summary generator, honors save=false and the bulk-empty early return. Flow records the missing implemented invocation-to-file-to-summary link without discarding the source-declared phase.',
     'later_check': 'Do not convert missing implementation details alone into a Task ambiguity. Represent the source-declared summary action or report its exact modeling gap; local save=false must not suppress a required aggregate save.'},
    {'id': 'TF-07', 'status': 'supported', 'topic': 'Storage payload versus filename and selection',
     'task_evidence': task(['R41', 'R42', 'R43', 'R44', 'R45']) + task(['I09'], 'issues'),
     'flow_evidence': [flow('Metadata records ISO `savedAt`, category, operation')],
     'source_evidence': [source('scripts/src/core/storage.ts', 58, 94), source('scripts/src/core/storage.ts', 103, 171)],
     'assessment': 'Task preserves supported metadata and whole caller data for the explicit public save utility. Flow distinguishes sanitized filename from original metadata, same-path replacement, acquisition/read errors, listing order and operation-substring selection. I09 preserves exact operation selection as the documented duty rather than legitimizing prefix matches.',
     'later_check': 'Apply these obligations to actual consumers and retained data ranges. A current whole-data save is not by itself proof that all upstream analytics fields are necessary for every task; errors in operation matching remain source mismatches.'},
    {'id': 'TF-08', 'status': 'supported_scoped_uncertainty', 'topic': 'Task unresolved issues have concrete competing meanings',
     'task_evidence': task(['I03', 'I05', 'I06'], 'issues'),
     'flow_evidence': [flow('There is no query-by-device or page-by-country join.')],
     'source_evidence': [source('SKILL.md', 30, 37), source('SKILL.md', 79, 85), source('references/api-reference.md', 225, 233), source('scripts/src/api/searchConsole.ts', 138, 154), source('scripts/src/index.ts', 261, 292)],
     'assessment': 'Three unresolved issues identify rolling-versus-calendar month interpretation, clicks-versus-impressions page ranking, and joint query/device results versus separate sitewide totals. Each cites the conflicting or ambiguous source relation; none uses generic black-box or unknown-value language.',
     'later_check': 'These affect R20, R26/R28/R30 and R29 respectively. Report their actual downstream effect accurately; do not infer that every other input range is semantically unknown from these descriptions alone.'},
    {'id': 'TF-09', 'status': 'scope_watchpoint', 'topic': 'Standalone realtime consumers are not separately named in Task',
     'task_evidence': task(['R21', 'R22']),
     'flow_evidence': [flow('Each metadata call fetches')],
     'source_evidence': [source('references/api-reference.md', 119, 159), source('scripts/src/index.ts', 12, 18), source('scripts/src/api/realtime.ts', 24, 99)],
     'assessment': 'R21 expresses active-user/page/event data under liveSnapshot; R22 explicitly covers standalone realtime sources. The other three realtime helpers are public standalone entries in the source, and flow preserves them, but Task does not separately state their standalone applicability. This is a potential applicability omission, not yet an observed missing demand or deletion.',
     'later_check': 'Check whether task-correspondence/review retains the documented individual getActiveUsers/getRealtimePages/getRealtimeEvents obligations without making liveSnapshot execution a prerequisite. If it does not, report the precise omission.'}
]

files = ['task/task.json', 'task/result.json', 'task/manifest.json', 'steps/flow/document.md',
         'steps/flow/result.json', 'steps/flow/manifest.json']
artifact_identity = {name: {'sha256': digest(RUN / name)} for name in files}
artifact_identity['task/task.json'].update(schema_version=TASK['schema_version'], task_sha256=TASK['task_sha256'])
artifact_identity['steps/flow/document.md'].update(value_sha256=FLOW_RESULT['value_sha256'])
assert digest(RUN / 'steps/flow/document.md') == FLOW_RESULT['value_sha256']
data = {'identity': 'ga4-initial-task-flow-source-audit-v1', 'created_at': datetime.now(timezone.utc).isoformat(),
        'status': 'provisional_initial_material_only', 'run_directory': str(RUN),
        'source_sha256': TASK['source_sha256'], 'artifacts': artifact_identity,
        'accepted_calls': {'task': TASK_RESULT['accepted_call'], 'flow': FLOW_RESULT['accepted_call']},
        'counts': {'task_requirements': len(TASK['requirements']), 'task_issues': len(TASK['issues']),
                   'task_issue_resolution': dict(Counter(r['resolution'] for r in TASK['issues'])),
                   'audit_check_status': dict(Counter(r['status'] for r in checks))},
        'inventory_sha256': digest(OUT/'source-boundary-inventory.json'), 'checks': checks,
        'limitations': ['These initial Task and flow artifacts may be superseded by the allowed shared repair. Recheck selected final identities before using these conclusions.',
                       'Only source/Task/flow were inspected; no generated CFG, processing, mapping, demand, preservation or DOE conclusion is assessed here.',
                       'Scope watchpoints are follow-up questions for selected material, not established errors or deletion findings.',
                       'Stage counts labeled injected/http_attempts=0 describe the adapter boundary, not absence of real native model calls. Native process/usage audit belongs to the controller audit.',
                       'No production or original historical files were edited; no model request, Skill execution or replay was launched.']}
with (OUT/'task-flow-initial-audit.json').open('x', encoding='utf-8') as handle:
    json.dump(data, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
md = ['# Initial GA4 Task and flow source audit', '',
      '**Provisional:** the allowed shared repair may supersede these initial artifacts. No final generated-material, demand or DOE conclusion is established here.', '',
      f"Task: `{TASK['task_sha256']}` ({len(TASK['requirements'])} requirements, {len(TASK['issues'])} issues; three unresolved).", '',
      f"Flow: `{FLOW_RESULT['value_sha256']}`. Both accepted their first response without structural correction.", '',
      '## Findings and follow-up checks', '']
for row in checks:
    md += [f"- **{row['id']} — {row['status']} — {row['topic']}.** {row['assessment']} Follow-up: {row['later_check']}"]
md += ['', 'Exact source quotes, generated artifact locations and physical hashes are recorded in `task-flow-initial-audit.json`.', '']
with (OUT/'task-flow-initial-audit.en.md').open('x', encoding='utf-8') as handle:
    handle.write('\n'.join(md))
print(json.dumps({'status': data['status'], 'counts': data['counts'], 'task_sha256': TASK['task_sha256'],
                  'flow_sha256': FLOW_RESULT['value_sha256'], 'audit_sha256': digest(OUT/'task-flow-initial-audit.json')}, indent=2))
