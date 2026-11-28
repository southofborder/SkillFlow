"""Inspect saved initial processing JSON and source; never invoke the analyzer."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RUN = ROOT/'experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209'
SOURCE = RUN/'source/inputs/package'
RESPONSE = RUN/'steps/processing/calls/a001/response.json'
P = json.loads(RESPONSE.read_text(encoding='utf-8'))
P = json.loads(P) if isinstance(P, str) else P
CFG = json.loads((RUN/'graph/initial.json').read_text(encoding='utf-8'))['cfg']
IRS = {ir['id']: ir for block in CFG['blocks'].values() for ir in block['instructions']}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value, path):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk(child, path+'/'+str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path+'/'+str(index))


def spec(ir):
    return {'instruction_id': ir, 'opcode': IRS[ir]['opcode'],
            'candidate_pointer': '/ir_semantics/'+ir, 'processing': P['ir_semantics'][ir]}


def src(file, start, end):
    lines = (SOURCE/file).read_text(encoding='utf-8').splitlines()
    assert 1 <= start <= end <= len(lines)
    return {'file': file, 'start_line': start, 'end_line': end, 'quote': '\n'.join(lines[start-1:end])}


ops = [(path, row) for path, row in walk(P['ir_semantics'], '/ir_semantics') if 'op' in row]
transfers = [(path, row['demand_transfer']) for path, row in ops if 'demand_transfer' in row]
tools = [(path, row['input_contract']) for path, row in ops if 'input_contract' in row]
selectors = Counter(json.dumps(rule['output'], sort_keys=True) for _, contract in transfers for rule in contract['rules'])
save_rows = []
for ir, row in IRS.items():
    if row['opcode'] != 'save_result':
        continue
    processing = P['ir_semantics'][ir]
    op_rows = [x for _, x in walk(processing, '') if 'op' in x]
    save_rows.append({'instruction_id': ir, 'cfg_inputs': row['inputs'],
                     'only_payload_write': op_rows == [{'op': 'write', 'target': 'saved', 'input': {'kind': 'input', 'index': 0}}],
                     'processing': processing})
assert len(save_rows) == 25

findings = [
    {'id': 'PROC-SEM-01', 'status': 'supported_relation', 'topic': 'Consumer-specific settings fields preserve actual acquisitions',
     'candidate': [spec(ir) for ir in ['ir_026', 'ir_029', 'ir_039', 'ir_066', 'ir_067', 'ir_076', 'ir_092']],
     'source': [src('scripts/src/config/settings.ts', 40, 48), src('scripts/src/core/client.ts', 33, 53), src('scripts/src/core/storage.ts', 64, 94)],
     'assessment': 'The property, site, credential-creation, save and listing call-site computations contain exact field rules. ir_066 separates propertyId from resultsDir; its former input needs only GA4_PROPERTY_ID while the latter needs cwd and explicitly no environment fields. ir_076 deterministically selects propertyId and builds the wrapper. Actual env/cwd reads are retained, so semantic narrowing has not erased those forward acquisitions.',
     'next_check': 'Review the field relations and all uses before judging any slot/range deletable. This is candidate relation quality, not a selected or reviewed deletion result.'},
    {'id': 'PROC-SEM-02', 'status': 'specific_output_rule_gap_risk', 'topic': 'Validation object has a whole rule but its consumers select valid',
     'candidate': [spec(ir) for ir in ['ir_023', 'ir_024', 'ir_035', 'ir_036', 'ir_045', 'ir_046', 'ir_055', 'ir_056']],
     'source': [src('scripts/src/config/settings.ts', 54, 74), src('scripts/src/core/client.ts', 23, 33), src('scripts/src/core/client.ts', 87, 98), src('scripts/src/core/client.ts', 109, 120)],
     'assessment': 'Opaque validation producers ir_035/045/055 have only output={property:value}; immediate consumers ir_036/046/056 select valid and branch on it. If these required guards produce a field/truth demand, no exact rule for valid exists. Likewise ir_024 requests truth of three settings fields from ir_023, whose settings-object computation has only a whole-value rule. These are concrete producer-consumer mismatches, not a claim that every whole-value rule is erroneous.',
     'exact_consumer_scopes': [{'producer': 'ir_035', 'consumer': 'ir_036', 'selector': {'property': 'truth', 'path': ['valid']}},
                               {'producer': 'ir_045', 'consumer': 'ir_046', 'selector': {'property': 'truth', 'path': ['valid']}},
                               {'producer': 'ir_055', 'consumer': 'ir_056', 'selector': {'property': 'truth', 'path': ['valid']}},
                               {'producer': 'ir_023', 'consumer': 'ir_024', 'selectors': [{'property': 'truth', 'path': [p]} for p in ['propertyId', 'clientEmail', 'privateKey']]}],
     'next_check': 'After selection/review, inspect the actual demanded selectors. Add/review exact relations through the authorized semantic process or retain localized output-contract gaps; do not repurpose the whole-output rule as a precise valid/field rule.'},
    {'id': 'PROC-SEM-03', 'status': 'scope_watchpoint', 'topic': 'Selective metadata and inspection output rules',
     'candidate': [spec(ir) for ir in ['ir_346', 'ir_358', 'ir_415', 'ir_551', 'ir_553']],
     'source': [src('scripts/src/api/metadata.ts', 38, 95), src('scripts/src/api/indexing.ts', 159, 192), src('scripts/src/index.ts', 328, 340)],
     'assessment': 'ir_346/358 correctly exclude the other metadata collection for their whole wrapper output. Their contracts still lack exact output paths dimensions or metrics and finer entry fields; this matters only if such partial outputs are demanded. ir_415 similarly has only a whole base-projection rule. In contrast, ir_551 explicitly supplies an indexStatus output rule, and ir_553 uses deterministic selection/expression/build for status/verdict. The latter is a positive selective-consumer example.',
     'next_check': 'Check selected demand paths and preserve deterministic rules. Whole wrappers demanded as whole may use their existing rule; partial fields require corresponding rules. Do not infer remote response projection merely from local field exclusion.'},
    {'id': 'PROC-SEM-04', 'status': 'source_dependency_coverage_risk', 'topic': 'Internal saves collapse wrapper and path dependencies',
     'candidate': [spec('ir_077'), spec('ir_174'), spec('ir_348'), spec('ir_451')],
     'source': [src('scripts/src/core/storage.ts', 58, 94), src('scripts/src/api/reports.ts', 102, 105), src('scripts/src/api/metadata.ts', 50, 52), src('scripts/src/index.ts', 71, 76)],
     'assessment': 'Every one of the 25 save_result call-site records reduces to write(input0, saved). CFG category/operation/optional-extra inputs are not referenced by these processing records; save-time settings, clock, wrapper and path construction are not expanded there. The shared saved location refers to the public saver ir_077 input1 rather than each call-specific path. The standalone saveResult body does model its wrapper, but that alone does not supply all separate invocation dependencies.',
     'explicit_limitation': [gap for gap in P['processing_gaps'] if gap['instruction_id'] == 'ir_077'],
     'assessment_qualification': 'The candidate explicitly records a storage identity/serialization gap at ir_077. Therefore this is not an assertion that a final report will falsely delete these fields; it is a source coverage and gap-localization risk requiring selected review and preservation checks.',
     'next_check': 'Demand and deletion assessment must not treat category/operation/extra as irrelevant merely because call-site processing omitted them. Check per-call wrapper/payload/path and how the authored saved-location gap applies to all 25 uses.'},
    {'id': 'PROC-SEM-05', 'status': 'interface_evidence_review_required', 'topic': 'Several tool reasons establish actual arguments rather than independent necessity',
     'candidate': [spec(ir) for ir in ['ir_040', 'ir_049', 'ir_050', 'ir_171', 'ir_344', 'ir_413']],
     'source': [src('scripts/src/core/client.ts', 33, 40), src('scripts/src/core/client.ts', 67, 79), src('scripts/src/api/metadata.ts', 42, 48), src('references/api-reference.md', 31, 45)],
     'assessment': 'ir_171 and ir_273 include public query-interface references in addition to the call construction. By contrast, several constructors, realtime calls, metadata and inspection contracts cite only actual argument construction, with reasons such as Constructor arguments, Request only sends name, or Exact request. Such evidence establishes what was passed; the final source review must separately establish why each required range is necessary. The shared auth contract marks the entire two-scope list required for both service constructors without a separate per-service scope rationale.',
     'next_check': 'Check the semantic interface obligation, including field scopes and literal lists, rather than approving from operand presence. This audit does not claim every code-only reference is invalid; source semantics can establish an interface relation when the rationale actually explains it.'},
    {'id': 'PROC-SEM-06', 'status': 'conditional_necessity_concern', 'topic': 'Type-conditioned save labels receive inconsistent precision',
     'candidate': [spec('ir_173'), spec('ir_248')],
     'source': [src('scripts/src/api/reports.ts', 102, 105), src('scripts/src/api/bulk-lookup.ts', 185, 188)],
     'assessment': 'ir_173 explicitly identifies a type-conditioned value-transfer gap for retaining a string or undefined. ir_248 performs the analogous string-or-custom operation but marks the whole input value required, even while saying nonstring object fields are not copied. On the DateRange-object branch, startDate/endDate do not determine custom; type does. A whole-value sufficient rule does not by itself demonstrate field necessity on that branch.',
     'next_check': 'Review conditional field scope using supported deterministic structure or a justified local gap. Do not turn the object branch into a whole-dateRange requirement merely to avoid uncertainty.'},
    {'id': 'PROC-SEM-07', 'status': 'mixed_gap_quality', 'topic': 'Concrete limits versus runtime-unknown explanations',
     'candidate': [spec('ir_010'), spec('ir_114'), spec('ir_173')],
     'source': [src('scripts/setup.sh', 1, 2), src('scripts/src/core/storage.ts', 141, 143), src('scripts/src/api/reports.ts', 104, 104)],
     'assessment': 'The dynamic-slice gap names the missing end-index-dependent input selector and affected values; the label gap names the type-conditioned relation. Both are specific expressiveness claims that review must verify. The cd-status gap instead requests the concrete invocation path, resolved access outcome and cd result because directory access can fail. Unknown runtime outcomes alone do not explain why static input necessity cannot be decided, so this reason needs stronger relation-level justification.',
     'next_check': 'Do not reject all gaps categorically or accept detailed wording automatically. Verify the claimed representational limits and keep each gap local; do not require execution merely to decide static necessity.'},
    {'id': 'PROC-SEM-08', 'status': 'source_error_review_pending', 'topic': 'Ignored filters and ordering remain source errors to check at review',
     'candidate': [spec('ir_150'), spec('ir_171')],
     'source': [src('references/api-reference.md', 31, 45), src('scripts/src/api/reports.ts', 77, 108)],
     'assessment': 'Processing preserves the actual reads of filters/orderBy and does not invent their transmission. Their source-declared behavior remains missing. Typed source_input_findings belong to the later source-review material, which is not available here; absence from this processing fragment is not itself a schema or semantic error.',
     'next_check': 'Verify final review reports the missing required behavior/input at the actual request boundary and preserves both the actual read fact and task obligation. A no-use finding alone must not be presented as successful filtered/ordered reporting.'}
]

data = {'identity': 'ga4-r2-initial-processing-semantic-audit-v1',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'status': 'provisional_rejected_initial_candidate_only', 'run_directory': str(RUN),
        'identities': {'response_file_sha256': sha(RESPONSE),
                       'validation_file_sha256': sha(RUN/'steps/processing/calls/a001/validation.json'),
                       'canonical_cfg_file_sha256': sha(RUN/'graph/initial.json'),
                       'source_inventory_sha256': sha(OUT/'source-boundary-inventory.json')},
        'descriptive_inventory': {'contracts': len(transfers), 'rules': sum(len(c['rules']) for _, c in transfers),
            'tool_contracts': len(tools), 'output_selector_counts': dict(selectors),
            'contracts_with_output_parts': sum('output_parts' in c for _, c in transfers),
            'save_result_sites': len(save_rows), 'payload_only_save_specs': sum(row['only_payload_write'] for row in save_rows),
            'count_qualification': 'Counts alone do not establish errors. Scalar output whole-value rules and deterministic expression/select/build operations can be appropriate. Only concrete opaque producer-consumer scopes are flagged.'},
        'findings': findings, 'internal_save_records': save_rows, 'saved_location': P['locations']['saved'],
        'limits': ['The initial response is structurally invalid and the bounded correction may replace any affected record. This is not selected processing or final source-review evidence.',
                   'No Task-correspondence, reviewed contract material, actual demanded selector, propagation, input assessment, preservation result or DOE outcome is inferred from candidate presence.',
                   'No model request, Skill execution, analysis backend, renderer or replay was invoked. Only standard-library reads and sibling audit writes were used.',
                   'No whole-rule count alone is classified as wrong, and no deletable input is established by this audit.']}
target=OUT/'initial-processing-semantic-audit.json'
with target.open('x',encoding='utf-8') as handle:
    json.dump(data,handle,ensure_ascii=False,indent=2);handle.write('\n')
md=['# Initial processing semantic audit', '', '**Provisional:** this inspects the rejected initial candidate. The bounded correction and later source review may supersede it. No deletion or DOE conclusion is established.', '',
    f"The candidate contains {len(transfers)} demand-transfer contracts and {len(tools)} tool contracts. Its output-rule histogram is descriptive only: scalar whole-output rules and deterministic operations are not errors merely for lacking subfield rules.", '', '## Focused source-backed checks', '']
for row in findings:
    md += [f"- **{row['id']} — {row['status']} — {row['topic']}.** {row['assessment']} Next check: {row['next_check']}"]
md+=['', 'Exact producer/consumer records, source quotes, all 25 internal save records and artifact identities are in `initial-processing-semantic-audit.json`.', '']
with (OUT/'initial-processing-semantic-audit.en.md').open('x',encoding='utf-8') as handle:handle.write('\n'.join(md))
print(json.dumps({'audit_sha256':sha(target),'descriptive_inventory':data['descriptive_inventory'],'findings':len(findings)},indent=2))
