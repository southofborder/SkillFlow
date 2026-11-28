"""Audit the currently selected a002 processing, without rerunning analysis."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RUN = ROOT/'experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209'
SOURCE = RUN/'source/inputs/package'
VALUE = RUN/'steps/processing/value.json'
EXPECTED = '533595e3e761dc816c965817bcbe8497c1a8d9f5c505170bf09308b95376d8d0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(VALUE) == EXPECTED
P = json.loads(VALUE.read_text(encoding='utf-8'))
RESULT = json.loads((RUN/'steps/processing/result.json').read_text(encoding='utf-8'))
VALIDATION = json.loads((RUN/'steps/processing/calls/a002/validation.json').read_text(encoding='utf-8'))
CFG = json.loads((RUN/'graph/initial.json').read_text(encoding='utf-8'))['cfg']
IRS = {ir['id']: ir for block in CFG['blocks'].values() for ir in block['instructions']}


def walk(value, path):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():yield from walk(child,path+'/'+str(key))
    elif isinstance(value,list):
        for index,child in enumerate(value):yield from walk(child,path+'/'+str(index))


def spec(ir):
    return {'instruction_id': ir, 'opcode': IRS[ir]['opcode'], 'pointer': '/ir_semantics/'+ir,
            'processing': P['ir_semantics'][ir]}


def src(file,start,end):
    lines=(SOURCE/file).read_text(encoding='utf-8').splitlines()
    assert 1<=start<=end<=len(lines)
    return {'file':file,'start_line':start,'end_line':end,'quote':'\n'.join(lines[start-1:end])}


ops=[(path,row) for path,row in walk(P['ir_semantics'],'/ir_semantics') if 'op' in row]
contracts=[(path,row['demand_transfer']) for path,row in ops if 'demand_transfer' in row]
tools=[(path,row['input_contract']) for path,row in ops if 'input_contract' in row]
zero_calls=[{'pointer':path,'location':row['location'],'processing':row} for path,row in ops
            if row['op']=='call' and not row.get('inputs')]
saves=[]
for ir,row in IRS.items():
    if row['opcode']!='save_result':continue
    actual=[x for _,x in walk(P['ir_semantics'][ir],'') if 'op'in x]
    assert len(actual)==1 and actual[0]['op']=='deliver' and actual[0]['target']=='save'
    assert actual[0]['inputs']==[{'kind':'input','index':i} for i in range(len(row['inputs']))]
    saves.append({'instruction_id':ir,'input_count':len(row['inputs']),'processing':actual[0]})
assert len(saves)==25

checks=[
 {'id':'SELECTED-01','status':'supported_local_field_precision','topic':'Specific downstream fields remain visible',
  'candidate':[spec(ir) for ir in ['ir_027','ir_030','ir_040','ir_067','ir_076','ir_551','ir_553']],
  'source':[src('scripts/src/core/client.ts',33,53),src('scripts/src/core/storage.ts',64,94),src('scripts/src/index.ts',328,340)],
  'assessment':'Selected ir_027 depends only on settings.propertyId; ir_030 selects siteUrl; ir_040 deterministically selects credential fields; ir_067 depends on resultsDir plus category; ir_076 builds a field-addressable wrapper with conditional extraInfo. ir_551 has an exact indexStatus transfer and ir_553 deterministically builds the status row. These are supported local relations independent of later Task selection.',
  'qualification':'They do not establish deletable inputs without final source review, all-use demand aggregation and preservation checks.'},
 {'id':'SELECTED-02','status':'prior_specific_mismatch_cleared_by_boundary_change','topic':'Validation/getSettings are now local helper acquisitions',
  'candidate':[spec(ir) for ir in ['ir_023','ir_026','ir_029','ir_035','ir_036','ir_039','ir_045','ir_055','ir_066','ir_092']],
  'source':[src('scripts/src/config/settings.ts',40,74),src('scripts/src/core/client.ts',23,43),src('scripts/src/core/storage.ts',64,65)],
  'assessment':'The selected ir_035/045/055 use zero-input Local validateSettings calls; they are no longer opaque computes with a whole-object demand_transfer. Thus the earlier specific ir_035-to-ir_036 rule mismatch is not present in this selected representation. Settings callers similarly acquire a Local getSettings result rather than inline env/cwd computation.',
  'remaining_boundary_limit':'A zero-explicit-argument interface is consistent with the function signature, but does not mean the source has no implicit environment, cwd or credential dependencies. At these helper call sites the selected representation does not provide the earlier explicit env-to-settings field transfers. Distinguish demand on acquired settings result fields from a proved trace to environment inputs; review must assess that summary boundary and actual acquisition facts.',
  'qualification':'Do not reuse the rejected candidate\'s env/cwd precision as evidence for this selected version. The public getSettings and validation bodies remain separate CFG operations.'},
 {'id':'SELECTED-03','status':'prior_argument_omission_cleared_at_call_boundary','topic':'Every internal save now retains all declared operands',
  'candidate':[spec('ir_174'),spec('ir_348'),spec('ir_451'),spec('ir_077')],
  'source':[src('scripts/src/core/storage.ts',58,95),src('scripts/src/api/reports.ts',102,105),src('scripts/src/index.ts',71,76)],
  'assessment':'All 25 selected save_result records deliver every CFG operand, in order, to Local saveResult. Data, category, operation and optional extra are covered by input_contract rows; there is no invented return path at these call sites. This clears the prior payload-only argument omission. The public saver now also includes JSON.stringify before its persistent write.',
  'remaining_boundary_limit':'The Local saveResult target has task access/retention and summarizes its persistence internals. Per-invocation clock/settings/wrapper/path relationships are described by evidence and the ir_077 gap rather than expanded at each call site. Final review and report must distinguish this local helper boundary from an established serialized-file/recipient identity.',
  'qualification':'Retained whole data for the saver has explicit source support. It does not by itself prove every upstream acquisition field is necessary for every task.'},
 {'id':'SELECTED-04','status':'conditional_necessity_concern_unchanged','topic':'String-or-custom still demands a whole optional value',
  'candidate':[spec('ir_173'),spec('ir_248')],
  'source':[src('scripts/src/api/reports.ts',102,105),src('scripts/src/api/bulk-lookup.ts',185,188)],
  'assessment':'ir_173 now has a structurally valid localized type-conditioned value gap. ir_248 still marks the whole optional input value required while explicitly saying nonstring contents are irrelevant. For a DateRange-object input, custom depends on the type, not its startDate/endDate contents. The full-value sufficient rule does not establish necessity of those object fields.',
  'next_check':'Check conditional demand support or a justified localized gap in source review. Do not treat object-field preservation as established solely by the current whole-value row.'},
 {'id':'SELECTED-05','status':'partial_output_scope_watchpoint_unchanged','topic':'Selective wrappers still need exact rules when a subfield is demanded',
  'candidate':[spec('ir_024'),spec('ir_346'),spec('ir_358'),spec('ir_415')],
  'source':[src('scripts/src/config/settings.ts',54,74),src('scripts/src/api/metadata.ts',38,95),src('scripts/src/api/indexing.ts',159,185)],
  'assessment':'The metadata wrapper rules correctly need only the selected response collection when preserving the entire wrapper. They do not provide exact output paths dimensions/metrics or finer entry fields. The public validation and inspection-base computes also retain whole-object rules. These are watchpoints only where final mapping actually demands partial outputs; the former direct validation-call mismatch was cleared by the helper-call change.',
  'qualification':'Scalar whole-value rules and deterministic selection/build/expression operations are not errors merely for lacking field rules. This audit performs no backward propagation and makes no claim that all listed partial selectors are demanded.'},
 {'id':'SELECTED-06','status':'interface_necessity_review_still_required','topic':'Source signatures and actual operands need semantic interface review',
  'candidate':[spec(ir) for ir in ['ir_040','ir_049','ir_171','ir_344','ir_413']],
  'source':[src('scripts/src/core/client.ts',33,42),src('scripts/src/core/client.ts',67,79),src('scripts/src/api/metadata.ts',42,48),src('references/api-reference.md',31,45)],
  'assessment':'Remote query contracts still need independent source/interface semantics for necessity, not only exact-call evidence. Several reasons remain short actual-operand explanations. Auth is now a zero-argument Local getGoogleAuth call, so the earlier explicit entire-scopes input row is absent; credential/scope dependencies instead lie inside that summarized helper. This changes the audit target rather than proving scope minimization.',
  'next_check':'Review each actual selected contract inventory entry, its required scope and independent evidence. The 146 tool contracts include local helpers and deliveries, not 146 remote APIs.'},
 {'id':'SELECTED-07','status':'runtime_unknown_gap_replaced_with_specific_relation','topic':'cd and dynamic demand gaps',
  'candidate':[spec('ir_010'),spec('ir_114'),spec('ir_173')],
  'source':[src('scripts/setup.sh',1,2),src('scripts/src/core/storage.ts',141,143),src('scripts/src/api/reports.ts',104,104)],
  'assessment':'cd is now a directory-operand call and its separate processing gap names the missing success-conditioned cwd post-state binding. It no longer asks for concrete runtime success as the input-necessity reason. The dynamic-slice and type-conditioned-label gaps identify precise affected relations and potential resolutions; source review still must verify that these are genuine supported-format limits.',
  'next_check':'Keep each gap scoped to its affected state or value range. Structured validity is not semantic approval.'},
 {'id':'SELECTED-08','status':'source_error_and_summary_review_pending','topic':'Ignored report controls and absent summary linkage remain visible',
  'candidate':[spec('ir_150'),spec('ir_171'),spec('ir_135')],
  'source':[src('references/api-reference.md',31,45),src('scripts/src/api/reports.ts',77,108),src('SKILL.md',53,64)],
  'assessment':'Selected processing retains actual filters/orderBy reads without inventing their effect. It explicitly records the source-declared summary duty and absent executable file association/writer. Typed source-input findings and corresponding requirement gaps belong to later source review, which is not yet available.',
  'next_check':'Check missing required control behavior separately from unused-input assessments, and audit the summary boundary separately from finite API/save representation counts.'}
]

review_path=RUN/'review/result.json'
assert not review_path.exists(), 'Review appeared; inspect before publishing a review-pending audit.'
data={'identity':'ga4-r2-selected-processing-semantic-audit-v1', 'created_at':datetime.now(timezone.utc).isoformat(),
      'status':'selected_initial_processing_pending_source_review','run_directory':str(RUN),
      'identities':{'selected_processing_sha256':sha(VALUE),'selected_result_sha256':sha(RUN/'steps/processing/result.json'),
                    'a002_validation_sha256':sha(RUN/'steps/processing/calls/a002/validation.json'),
                    'canonical_cfg_file_sha256':sha(RUN/'graph/initial.json')},
      'selected_accepted_call':RESULT['accepted_call'], 'validation_status':VALIDATION['status'],
      'diagnostic_count':len(VALIDATION.get('diagnostics',[])),
      'descriptive_counts':{'demand_transfer_contracts':len(contracts),'tool_input_contracts':len(tools),
                            'zero_explicit_input_calls':len(zero_calls),'all_argument_saver_deliveries':len(saves)},
      'checks':checks,'internal_saver_deliveries':saves,'zero_explicit_input_calls':zero_calls,
      'selected_helper_locations':{k:P['locations'][k] for k in ['settings','validate','auth','save','saved']},
      'selected_processing_gaps':P['processing_gaps'],
      'limits':['Every quoted candidate record was freshly read from selected a002 value.json, not from the rejected response.',
                'Status is current selection, not final approval; shared semantic repair may supersede it.',
                'Source review, final mapping, demand, preservation and DOE were not assessed. No deletable input is established.',
                'No model calls, Skill execution, backend analysis, renderer or replay ran; production and historical artifacts were not changed.']}
target=OUT/'selected-processing-semantic-audit.json'
with target.open('x',encoding='utf-8') as handle:json.dump(data,handle,ensure_ascii=False,indent=2);handle.write('\n')
md=['# Selected processing semantic audit', '',
    f"Selected a002 processing SHA: `{EXPECTED}`. Structural validation passed with no diagnostics. Source review is not yet available; semantic repair can still supersede this selection.", '',
    '## Source-backed re-evaluation', '']
for row in checks:
    md += [f"- **{row['id']} — {row['status']} — {row['topic']}.** {row['assessment']} {row.get('remaining_boundary_limit','')} {row.get('next_check','')} {row.get('qualification','')}"]
md+=['', 'Exact selected records, helper locations, all 25 saver deliveries and artifact identities are in `selected-processing-semantic-audit.json`. No final deletion or DOE conclusion is made.', '']
with (OUT/'selected-processing-semantic-audit.en.md').open('x',encoding='utf-8') as handle:handle.write('\n'.join(md))
print(json.dumps({'status':data['status'],'counts':data['descriptive_counts'],'audit_sha256':sha(target)},indent=2))
