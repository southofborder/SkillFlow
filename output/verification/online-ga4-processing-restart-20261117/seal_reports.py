"""Seal closed-run reports from immutable receipts; no analysis or replay."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
RUN = PROJECT / 'experiments/doe/runs/document-guided-ga4-processing-restart-high-20261117-172228'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def create(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')

def main():
    finished = read(RUN / 'controller-finished.json')
    replay = read(RUN / 'replay-check.json')
    closure = read(VERIFY / 'process-closure-observation.json')
    result = read(RUN / 'result.json')
    inheritance = read(RUN / 'inherited-inputs.json')
    accounting = read(RUN / 'restart-accounting.json')
    propagation = read(RUN / 'propagation/manifest.json')
    demand = read(RUN / 'doe/audit/demand-support.json')
    doe = read(RUN / 'doe/doe-result.json')
    assert finished['status'] == result['status'] == 'partial'
    assert finished['controller_error'] is None
    assert replay['status'] == 'matched' and replay['new_native_markers'] == 0 and replay['native_inventory_unchanged']
    assert finished['native_exits']['all_attempt_exits_confirmed']
    assert closure['all_recorded_pids_absent'] and closure['pid_count'] == 8
    assert accounting['new_native_starts'] == 6 and accounting['new_logical_calls'] == 7
    assert accounting['inherited_logical_calls'] == 3 and accounting['recorded_logical_calls_including_inherited'] == 10
    assert sha(RUN / 'graph/initial.json') == inheritance['inherited_files']['graph/initial.json']
    assert (RUN / 'graph/initial.json').read_bytes() == (RUN / 'graph/selected.json').read_bytes()
    coverage = dict(Counter(propagation['coverage'].values()))
    assert coverage == {'processed':162, 'not_reached':326, 'not_solved':1}
    rows = demand['input_assessments']
    ranges = [scope for row in rows for scope in row['ranges']]
    range_counts = dict(Counter(scope['status'] for scope in ranges))
    assert len(rows) == 826 and range_counts == {'required':31, 'unresolved':531}
    assert all(scope['modification'] is None for scope in ranges)
    comparisons = [entry for sink in doe['sinks'] for entry in sink['data_reviews']]
    assert len(doe['sinks']) == 10 and len(comparisons) == 390
    assert Counter(x['conclusion'] for x in comparisons) == {'no_excess_established':390}
    assert all(x['reduction'] is None for x in comparisons)
    assert len(doe['coverage']['unresolved_boundaries']) == 52
    evidence_names = [
        'initial-reuse-audit.json', 'processing-correction-complete-audit-20261117T094602Z.json',
        'processing-snapshot-assessment-20261117T094356Z.json', 'assembly-review-input-supplement.json',
        'review-failure-final.json', 'final-cost-provenance.json', 'final-backend-source-audit.json',
        'process-closure-observation.json']
    evidence = {name:sha(VERIFY/name) for name in evidence_names}
    run_names = ['controller-started.json','analysis-finished.json','controller-finished.json',
        'replay-check.json','implementation-check.json','native-exit-check.json','restart-accounting.json',
        'inherited-inputs.json','run-protocol.json','result.json','selection.json','graph/initial.json',
        'graph/selected.json','review/result.json','propagation/manifest.json','doe/doe-result.json',
        'doe/audit/demand-support.json']
    evidence.update({str((RUN/name).relative_to(PROJECT)).replace('\\','/'):sha(RUN/name) for name in run_names})
    summary = {
        'identity':'skillflow-processing-restart-closure-report-v1', 'status':'closed_partial',
        'run_directory':str(RUN), 'parent_run':inheritance['run_directory'],
        'implementation_sha256':'694561928259d08c00492843a036ad0196460f785e6bd5d2fb1e07ba8ef59445',
        'production_changed_for_restart':False, 'complete_source_files':16, 'inherited_files':54,
        'selected_cfg':{'origin':'inherited_initial','blocks':215,'ir':489,'edges':192,'byte_identical':True},
        'stages':result['stages'], 'shared_repair_used':False,
        'processing':{'accepted_after_local_correction':True,'retained_ir':489,'operations_before_lowering':753,
            'opaque_contracts':202,'whole_value_rules':173,'truth_rules':29,'nonempty_output_field_selectors':0,
            'processing_gaps':8,'source_review_accepted':False},
        'review':{'inventory_obligations':684,'inventory_scopes':2540,'authored_checks':453,
            'missing_checks':231,'accepted_checks':0,'grouped_diagnostics':245,
            'initial_delivery_characters':992486,'correction_delivery_characters':1206286,
            'adapter_limit_characters':1048576,'excess_characters':157710,
            'failure_type':'InputTooLarge_before_native_start','response_omission_cause':'not_established'},
        'propagation':{'status':propagation['status'],'coverage':coverage,'diagnostics':propagation['diagnostics'],
            'failure_ir':'ir_151','source_identity_issue':'Unknown exception content represented as unknown runtime-context address; symbolic aliases pollute bulk URL input.'},
        'input_assessments':{'rows':len(rows),'node_kinds':dict(Counter(x['node_kind'] for x in rows)),
            'coverage':dict(Counter(x['coverage'] for x in rows)),
            'ranges':{**range_counts,'deletable':0},'modifications':0,
            'required_caveat':'Conditional task derivations under unavailable source review, not certified necessity.'},
        'doe':{'status':doe['status'],'reached_sinks':10,'comparisons':390,'no_excess_established':390,
            'reductions':0,'unresolved_boundaries':52},
        'source_boundary_record_reach':{'direct_remote':{'processed':0,'total':13},
            'save_result_callers':{'processed':1,'total':25},'filesystem':{'processed':0,'total':7},
            'caveat':'Abstract records only; no Skill execution or full semantic accuracy claim.'},
        'cost':{'new_native_starts':6,'new_normal_starts':4,'new_structural_correction_starts':2,
            'new_logical_calls':7,'recorded_logical_calls_including_inherited':10,'inherited_logical_calls':3,
            'known_public_input_tokens':1416824,'known_public_output_tokens':141122,
            'known_public_total_tokens':1557946,'inherited_tokens_excluded':303082,
            'all_new_final_usages_present':True,'outer_retries':0,'shared_repair_starts':0,
            'unreported_provider_usage':'unknown','primary_timeout_evidence':False},
        'analysis_seconds':finished['analysis_seconds'],'replay':replay,
        'controller_finished_at':finished['finished_at'],'all_recorded_pids_absent':True,
        'offline_restart_acceptance':{'distinct_passed':68,'skipped':0,'unresolved_failures':0,'production_changes':False},
        'authorization_consumed':True,'no_further_run_or_replay_started':True,
        'evidence_sha256':evidence}
    create(VERIFY/'run-summary.json',summary)
    state = read(VERIFY/'continuation-state.json')
    state.update(status='closed_partial',observed_at=datetime.now(timezone.utc).isoformat(),active_stage='closed',
        native_starts_observed=6,review='request_failure',propagation='execution_error',doe='partial',
        replay=replay,all_recorded_pids_absent=True,report='assessment.zh.md',authorization_consumed=True,
        instructions='This sole fresh descendant and its sole replay are closed. Preserve all parent/new artifacts. No restart, resume, extra replay, model/Skill/probe/case/resampling, production changes or staged import without a new user instruction.')
    (VERIFY/'continuation-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    reports = ['run-summary.json','assessment.en.md','assessment.zh.md','followup-plan.zh.md','continuation-state.json',
        'final-backend-source-audit.en.md','final-backend-source-audit.zh.md','review-failure-final.en.md',
        'review-failure-final.zh.md','final-cost-provenance.en.txt','final-cost-provenance.zh.txt']
    report_hashes = {name:sha(VERIFY/name) for name in reports}
    create(VERIFY/'report-closeout.json',{'identity':'skillflow-processing-restart-report-closeout-v1',
        'closed_at':datetime.now(timezone.utc).isoformat(),'status':'sealed','reports_sha256':report_hashes,
        'evidence_sha256':evidence,'method':'Read-only receipt/hash/count verification; no stage, model, Skill, tests, backend or replay execution.',
        'authorization_consumed':True})
    print(json.dumps({'status':'sealed','summary_sha256':sha(VERIFY/'run-summary.json'),
        'closeout_sha256':sha(VERIFY/'report-closeout.json'),'new_native_starts':6,'new_public_tokens':1557946}))

if __name__ == '__main__':
    main()
