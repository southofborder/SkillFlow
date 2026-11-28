"""Build a finite audit checklist from this fresh frozen source, without execution.

This helper only reads the named source package and writes sibling audit files.
It does not import SkillFlow, generated model answers, or the Skill's code.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = ROOT / 'experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209'
SOURCE = RUN / 'source/inputs/package'
SNAPSHOT = json.loads((RUN / 'source/inputs/snapshot.json').read_text(encoding='utf-8'))
PROTOCOL = json.loads((RUN / 'run-protocol.json').read_text(encoding='utf-8'))
FILES = {p.relative_to(SOURCE).as_posix(): p.read_text(encoding='utf-8').splitlines()
         for p in SOURCE.rglob('*') if p.is_file()}


def ref(file, start, end=None):
    end = start if end is None else end
    lines = FILES[file]
    assert 1 <= start <= end <= len(lines), (file, start, end)
    return {'file': file, 'start_line': start, 'end_line': end,
            'quote': '\n'.join(lines[start - 1:end])}


def find(file, needle):
    matches = [i for i, line in enumerate(FILES[file], 1) if needle in line]
    assert len(matches) == 1, (file, needle, matches)
    return matches[0]


def range_ref(file, first, last=None):
    return ref(file, find(file, first), find(file, last) if last else None)


def function_at(file, line):
    matches = [(i, re.search(r'^(?:export )?(?:async )?function (\w+)', text))
               for i, text in enumerate(FILES[file], 1) if i <= line]
    return next((m.group(1) for _, m in reversed(matches) if m), '<module>')


remote = []
saves = []
loops = []
array_operations = []
exports = []
console = []
for file in sorted(FILES):
    if not file.startswith('scripts/src/') or not file.endswith('.ts'):
        continue
    for line, text in enumerate(FILES[file], 1):
        function = function_at(file, line)
        base = {'function': function, 'source': ref(file, line)}
        match = re.search(r'await (client\.[\w.]+)\(', text)
        if match:
            remote.append({**base, 'callee': match.group(1)})
        if re.match(r'\s*saveResult\(', text):
            saves.append(base)
        if re.match(r'\s*for\s*\(', text):
            loops.append(base)
        if re.search(r'\.(?:map|filter|sort|slice)\(', text):
            array_operations.append(base)
        if re.match(r'export (?:async )?function ', text):
            exports.append(base)
        if 'console.log(' in text:
            console.append({**base, 'interpolated': '${' in text})

assert len(remote) == 13, len(remote)
assert len(saves) == 25, len(saves)
assert len(loops) == 3, len(loops)

request_fields = {
    'runReport': ['property', 'dateRanges[].startDate', 'dateRanges[].endDate',
                  'dimensions[].name', 'metrics[].name', 'limit (only if truthy)'],
    'getMetricsForUrls': ['property', 'dateRanges[].startDate', 'dateRanges[].endDate',
                         'dimensions[].name', 'metrics[].name', 'dimensionFilter.filter.fieldName',
                         'dimensionFilter.filter.inListFilter.values[]',
                         'dimensionFilter.filter.inListFilter.caseSensitive'],
    'querySearchAnalytics': ['siteUrl', 'requestBody.startDate', 'requestBody.endDate',
                            'requestBody.dimensions[]', 'requestBody.rowLimit', 'requestBody.startRow'],
    'requestIndexing': ['requestBody.url', "requestBody.type = 'URL_UPDATED'"],
    'removeFromIndex': ['requestBody.url', "requestBody.type = 'URL_DELETED'"],
    'inspectUrl': ['requestBody.inspectionUrl', 'requestBody.siteUrl'],
}
realtime = {'getActiveUsers': ('unifiedScreenName', 'activeUsers'),
            'getRealtimeEvents': ('eventName', 'eventCount'),
            'getRealtimePages': ('unifiedScreenName', 'screenPageViews'),
            'getRealtimeSources': ('firstUserSource + firstUserMedium', 'activeUsers')}
for number, row in enumerate(remote, 1):
    row['id'] = f'API-{number:02}'
    fn = row['function']
    row['interface_evidence_status'] = 'source-observed request; current arguments alone do not prove interface necessity'
    row['coverage_status'] = 'awaiting_selected_material'
    row['response_projection_capability'] = 'No generic response-field mask is documented in this frozen source.'
    if fn in request_fields:
        row['observed_request_field_paths'] = request_fields[fn]
    elif fn in realtime:
        dimension, metric = realtime[fn]
        row['observed_request_field_paths'] = ['property', f'dimensions[].name = {dimension}', f'metrics[].name = {metric}']
    else:
        assert fn in {'getAvailableDimensions', 'getAvailableMetrics', 'getPropertyMetadata'}, fn
        row['observed_request_field_paths'] = ['name = properties/<propertyId>/metadata']
    if fn in {'runReport', 'getMetricsForUrls'}:
        row['acquisition_controls'] = 'Dimensions and metrics choose report columns; date range and optional limit/filter choose query scope. This is not a generic SDK response-field projection.'
    elif fn == 'querySearchAnalytics':
        row['acquisition_controls'] = 'Dimensions, date range, rowLimit and startRow choose query scope and pagination.'
    elif fn in realtime:
        row['acquisition_controls'] = 'The named wrapper fixes dimensions and metrics in its request.'
    else:
        row['acquisition_controls'] = 'Source shows a property, URL, or site selector; no selective response field mask.'
    if fn in {'getAvailableDimensions', 'getAvailableMetrics'}:
        row['local_response_selection'] = fn.removeprefix('getAvailable').lower() + ' || []'
    elif fn == 'inspectUrl':
        row['local_response_selection'] = 'inspectionResultLink, indexStatus, optional mobileUsability and richResults with explicit defaults'
    elif fn in {'requestIndexing', 'removeFromIndex'}:
        row['local_response_selection'] = 'url with original-url fallback, constant type, notification time with clock fallback'
    else:
        row['local_response_selection'] = 'Full selected SDK response object is returned; querySearchAnalytics uses response.data.'

for number, row in enumerate(saves, 1):
    row['id'] = f'SAVE-{number:02}'
    row['coverage_status'] = 'awaiting_selected_material'
    row['shared_write'] = 'scripts/src/core/storage.ts:92'
    row['effect'] = 'Serialize metadata wrapper and caller data to a timestamped JSON file; callers ignore saveResult return value at these 25 sites.'
    row['guard'] = 'unconditional at this function body point' if row['source']['file'] == 'scripts/src/index.ts' else 'save is true (default true; selected callers pass false)'

for number, row in enumerate(loops, 1):
    row['id'] = f'LOOP-{number:02}'
    row['coverage_status'] = 'awaiting_selected_material'
    row['members'] = 'urls[]; preserve each occurrence, ordering, count, and URL/result association'
    row['error_behavior'] = ('No local catch in requestIndexingBatch; propagate a failed member call.'
                             if row['function'] == 'requestIndexingBatch' else
                             'Per-member try/catch appends success or failure; preserve the current URL in either outcome.')

settings = 'scripts/src/config/settings.ts'
client = 'scripts/src/core/client.ts'
storage = 'scripts/src/core/storage.ts'
index = 'scripts/src/index.ts'
reports = 'scripts/src/api/reports.ts'
bulk = 'scripts/src/api/bulk-lookup.ts'
metadata = 'scripts/src/api/metadata.ts'
search = 'scripts/src/api/searchConsole.ts'
indexing = 'scripts/src/api/indexing.ts'
supplemental = [
    ('ENV-01', 'dotenv configuration acquisition', range_ref(settings, 'config();'),
     'An actual environment load must remain represented. No real .env or credential value is present or read by this audit.'),
    ('ENV-02', 'settings construction and environment reads', ref(settings, 40, 49),
     'Fields: propertyId, clientEmail, privateKey, defaultDateRange, resultsDir and siteUrl. Whole settings creation is an actual read; consumer-specific demand must not erase it.'),
    ('AUTH-01', 'GA4 credential-bearing client construction', ref(client, 27, 43),
     'Uses clientEmail/privateKey; validation also observes propertyId. Cache-hit path returns an existing instance.'),
    ('AUTH-02', 'shared GoogleAuth construction', ref(client, 67, 80),
     'Uses clientEmail/privateKey and both webmasters.readonly/indexing scopes; source does not prove both scopes necessary for each individual consumer.'),
    ('AUTH-03', 'Search Console client and validation', ref(client, 87, 102),
     'Shared validation observes propertyId even though this client construction takes version and auth. Do not silently remove that actual condition.'),
    ('AUTH-04', 'Indexing client and validation', ref(client, 109, 124),
     'Same validation/control and cache distinctions as Search Console; this construction takes version and auth.'),
    ('STATE-01', 'singleton identities and reset', ref(client, 13, 15),
     'Three distinct client state cells; resetClient at lines 58-62 resets all three. Preserve state versions and reuse, not repeated fresh acquisitions.'),
    ('FS-01', 'output directory identity and creation', ref(storage, 64, 70),
     'resultsDir and category determine directory identity; directory existence controls mkdir.'),
    ('FS-02', 'filename construction', ref(storage, 73, 77),
     'Clock, operation and conditional extraInfo affect path; path identity is distinct from serialized payload content.'),
    ('FS-03', 'write payload and file effect', ref(storage, 79, 94),
     'metadata.savedAt/category/operation/propertyId/extraInfo and data are serialized. Required write effect can survive when filepath return is not demanded.'),
    ('FS-04', 'saved-result acquisition', ref(storage, 103, 114),
     'Path existence, whole file read and JSON parse with null fallback. No read-side field projection is declared.'),
    ('FS-05', 'directory listing acquisition', ref(storage, 124, 149),
     'Directory existence, .json membership, path construction, descending ordering and optional limit are dependencies distinct from file body values.'),
    ('FS-06', 'latest-result selection and read', ref(storage, 155, 171),
     'Optional operation filtering and empty-list branch precede reading files[0]; order and membership must remain tied to selected path.'),
    ('DOC-01', 'declared analyze/save/summarize workflow', ref('SKILL.md', 55, 69),
     'Source declares reading saved JSON and writing markdown summaries; these TypeScript files have no dedicated markdown summary writer. Audit source-level coverage separately.'),
    ('SETUP-01', 'dependency installation', ref('scripts/setup.sh', 1, 2),
     'Setup command is source evidence only. It is excluded from the 13 awaited application SDK-site denominator and is never executed by this audit.'),
]
supplemental = [{'id': sid, 'kind': kind, 'source': evidence, 'audit_requirement': requirement,
                 'coverage_status': 'awaiting_selected_material'}
                for sid, kind, evidence, requirement in supplemental]

checks = [
    ('CHECK-01', 'Settings demand must distinguish consumers',
     [ref(settings, 40, 49), ref(client, 50, 53), ref(client, 130, 133), ref(storage, 64, 94)],
     'Formatting a property ID needs propertyId; choosing Search Console site needs siteUrl; storage needs resultsDir and the actually serialized propertyId. Neither full settings reads nor credential presence automatically establish demand for unrelated fields.'),
    ('CHECK-02', 'Validation conditions must survive semantic minimization',
     [ref(settings, 54, 73), ref(client, 91, 99), ref(client, 113, 121)],
     'propertyId/clientEmail/privateKey presence affects validation.valid and errors. If a validation requirement is semantically wrong for one client, report the mismatch explicitly instead of pretending the source never checks it.'),
    ('CHECK-03', 'Documented filters and orderBy are ignored by actual runReport',
     [ref('references/api-reference.md', 32, 48), ref(reports, 76, 108)],
     'filters/orderBy are destructured but absent from request and all later computations. If the declared task requires filtering/sorting, report unsupported or missing behavior; deletion of these source inputs does not repair that behavior.'),
    ('CHECK-04', 'Output-specific metadata dependency',
     [ref(metadata, 38, 55), ref(metadata, 60, 77), ref(metadata, 82, 95)],
     'getAvailableDimensions returns/saves only dimensions; getAvailableMetrics only metrics; getPropertyMetadata preserves the whole response. A whole-response transfer rule cannot stand in for either selective case. Source lacks a remote response projection parameter.'),
    ('CHECK-05', 'Inspection result demand is consumer-specific',
     [ref(indexing, 161, 192), ref(index, 324, 346)],
     'Standalone inspectUrl exposes indexStatus/mobileUsability/richResults/link. checkIndexStatus calls it with save=false and keeps verdict plus the whole indexStatus; other inspection fields have no use on this consumer path, but other consumers may require them.'),
    ('CHECK-06', 'Notification fallback and output pairing',
     [ref(indexing, 61, 79), ref(indexing, 118, 136), ref(index, 301, 319)],
     'Output URL can derive from response or original URL. Time can derive from response or clock. reindexUrls object spread can overwrite the earlier url field; do not assume a fixed input-output URL equality unsupported by the source.'),
    ('CHECK-07', 'Repeated URL calls and error branches',
     [ref(indexing, 89, 105), ref(index, 301, 346)],
     'Three loops require occurrence/cardinality/order identity. requestIndexingBatch has no local catch; the two high-level loops append per-member error outcomes. Removing a URL can alter count, effects, status and console observations.'),
    ('CHECK-08', 'Bulk lookup empty input and membership',
     [ref(bulk, 64, 97), ref(bulk, 149, 191)],
     'Empty normalized URLs return rows=[]/rowCount=0 before client/API/save. Nonempty normalized members feed the filter. Preserve membership, caseSensitive=false, optional metrics and date range.'),
    ('CHECK-09', 'Storage action and return-value demand are separate',
     [ref(storage, 58, 94)],
     'The 25 saveResult call sites do not use its filepath return. Required persistence must still retain filename, payload and write action; unused return does not mean unused side effect.'),
    ('CHECK-10', 'Other consumers and acquisition control',
     [ref(index, 173, 203), ref(search, 85, 122), ref(reports, 91, 105)],
     'compareDateRanges retains both ranges and reports while disabling two inner saves. Report/analytics selectors may constrain acquisition but do not establish arbitrary response-field trimming. Union all applicable uses before deleting an input.'),
    ('CHECK-11', 'Documented output mismatch remains visible',
     [ref('SKILL.md', 55, 69), ref(index, 261, 275), ref(search, 149, 154)],
     'Markdown summary generation is declared but not implemented as a TypeScript writer. keywordAnalysis describes a query/device breakdown but invokes separate query and device reports; do not invent joint query-device rows.'),
    ('CHECK-12', 'Sensitivity and necessity remain separate',
     [ref(settings, 42, 47), ref(reports, 158, 175), ref(search, 28, 44)],
     'Credential material, property/site identifiers, URLs/query strings, transactionId/revenue and analytics rows are candidate sensitivity boundaries. Source names alone do not establish actual sensitive values, unauthorized access or DOE.'),
]
checks = [{'id': sid, 'title': title, 'sources': evidence, 'expected_review': rule,
           'status': 'source_only_check_not_generated_conclusion'} for sid, title, evidence, rule in checks]

manifest = []
for item in SNAPSHOT['files']:
    path = SOURCE / item['path']
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == item['raw_sha256'], item['path']
    manifest.append({'file': item['path'], 'sha256': actual, 'bytes': path.stat().st_size,
                     'lines': len(FILES[item['path']])})
assert set(FILES) == {x['file'] for x in manifest}

data = {
    'identity': 'ga4-fresh-source-boundary-inventory-v1',
    'created_at': datetime.now(timezone.utc).isoformat(),
    'run_directory': str(RUN), 'source_directory': str(SOURCE),
    'source_sha256': PROTOCOL['source_sha256'], 'source_files': manifest,
    'method': 'Fresh-source static reading and enumerated lexical sites with manually reviewed field checks; no generated answers, Skill execution, model calls or replay. References use package-relative paths and one-based inclusive lines.',
    'coverage_denominators': {'source_files': len(manifest), 'awaited_application_sdk_sites': len(remote),
        'saveResult_call_sites': len(saves), 'explicit_url_loops': len(loops),
        'exported_function_declarations': len(exports), 'array_operation_sites': len(array_operations),
        'console_call_sites': len(console), 'interpolated_console_call_sites': sum(r['interpolated'] for r in console),
        'supplemental_boundaries': len(supplemental)},
    'limitations': ['This finite source checklist is not a human gold standard or a proof of exhaustive semantic coverage.',
        'Remote-site count excludes SDK internals, client/auth construction, setup package downloads and documentation examples.',
        'Save-site count excludes shared write internals and the declared markdown summary workflow.',
        'No actual secrets, runtime values, installed SDK implementation or external API documentation were accessed.',
        'Observed arguments are not used as proof that an interface requires every argument; necessity must have separate explicit source/interface semantics.',
        'No deletion or DOE finding is established before selected contracts, their review, demand and preservation evidence are checked.'],
    'api_sites': remote, 'save_sites': saves, 'url_loops': loops,
    'supplemental_boundaries': supplemental, 'field_necessity_checks': checks,
    'array_operation_sites': array_operations, 'exported_function_declarations': exports,
    'console_sites': console,
    'selected_material_audit_plan': [
        'Freeze selected source/CFG/processing/annotation/source-review/review-receipt identities after controller closure; provisional checks must be labeled.',
        'For each finite API/save/loop boundary, distinguish represented, modeled, reached, processed, unresolved, and absent. Broad overlapping citations alone do not establish correct semantics.',
        'Check request-response/auth/state/payload identities and scope, interface evidence separate from argument presence, and acquisition capabilities.',
        'Check complete contract inventory and per-input/output scoped review; inspect wrong/missing input findings independently of unresolved labels.',
        'Trace each required/deletable/unresolved input assessment to actual CFG inputs, task-output seeds, transfer rules, exact edit locations and preservation checks.',
        'Use the twelve field checks to verify local demand versus retained forward observations, and union conditions/count/membership/pairing/other-consumer uses.',
        'Report source-supported semantic limitations separately from generated-IR coverage; zero deletions or completed propagation does not prove no DOE.'
    ]
}
OUT.mkdir(parents=True, exist_ok=True)
target = OUT/'source-boundary-inventory.json'
target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
md = ['# GA4 fresh-source boundary inventory', '',
      'This inventory was derived from the new frozen source package before inspecting generated answers. It is an assistant-authored finite checklist, not a human gold standard.', '',
      f"Source SHA: `{data['source_sha256']}`. All 16 file hashes match the new source snapshot.", '',
      '## Denominators', '']
md += [f'- {key}: {value}' for key, value in data['coverage_denominators'].items()]
md += ['', '## API sites', '', '| ID | Function | Source |', '| --- | --- | --- |']
md += [f"| {r['id']} | {r['function']} | {r['source']['file']}:{r['source']['start_line']} |" for r in remote]
md += ['', '## Field necessity review checks', '']
md += [f"- **{r['id']} — {r['title']}:** {r['expected_review']}" for r in checks]
md += ['', '## Later selected-material audit', '']
md += [f'{i}. {rule}' for i, rule in enumerate(data['selected_material_audit_plan'], 1)]
md += ['', '## Limits', '']
md += ['- ' + limit for limit in data['limitations']]
md += ['', 'The JSON inventory includes all exact quotes, source hashes, 25 save sites, three URL loops, supplemental boundaries, exported functions, array operations and console sites. All coverage statuses await selected-material inspection.', '']
(OUT/'source-boundary-inventory.en.md').write_text('\n'.join(md), encoding='utf-8')
print(json.dumps({'inventory': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                  'counts': data['coverage_denominators']}, indent=2))
