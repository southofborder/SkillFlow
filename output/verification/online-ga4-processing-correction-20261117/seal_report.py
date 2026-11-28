"""Seal this closed run's reports and state; no analysis, transport or replay."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from lifecycle_guard import validate_prepared
from skillflow.common.recording import implementation_provenance

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
OFFLINE = VERIFY.parent / 'processing-correction-20261117'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write('\n')


def main():
    if (VERIFY / 'report-closeout.json').exists() or (VERIFY / 'run-summary.json').exists():
        raise ValueError('Final reporting is already sealed; no overwrite or historical rerun')
    current = implementation_provenance()
    run, protocol = validate_prepared(PROJECT, VERIFY, fresh=False, current=current)
    finished = read(run / 'controller-finished.json')
    result = read(run / 'result.json')
    replay = read(run / 'replay-check.json')
    cost = read(VERIFY / 'final-cost-provenance.json')
    exits = read(VERIFY / 'process-closure-observation.json')
    native_pids = [read(p)['pid'] for p in (run / 'transport').rglob('pid.json')]
    recorded = {*native_pids, read(run / 'controller-started.json')['pid'],
                read(VERIFY / 'dispatch-started.json')['wrapper_pid']}
    if (len(native_pids) != 6 or len(recorded) != 8 or exits.get('status') != 'checked'
            or set(exits['requested_pids']) != recorded or exits['processes']
            or exits['remaining_recorded_processes'] != 0):
        raise ValueError('Independent process closure is not exact or complete')
    if (result['status'] != 'failed' or result['selected_annotation'] is not None
            or result['repair_used'] or finished['controller_error'] is not None
            or not finished['native_exits']['all_attempt_exits_confirmed']
            or replay['status'] != 'matched' or replay['new_native_markers'] != 0
            or not replay['native_inventory_unchanged'] or cost['issues']):
        raise ValueError('The observed terminal/replay state differs from the assessed result')
    baseline = read(OFFLINE / 'baseline.json')
    changed = [name for name, digest in baseline['historical_files'].items()
               if not (PROJECT / name).is_file() or sha(PROJECT / name) != digest]
    if changed:
        raise ValueError('Protected historical files changed: ' + repr(changed))
    absence = ('propagation-result.json', 'doe-result.json', 'input-assessments.json')
    backend_files = [p.relative_to(run).as_posix() for p in run.rglob('*')
                     if p.is_file() and p.name in absence]
    if backend_files:
        raise ValueError('Unexpected backend artifacts require renewed assessment: ' + repr(backend_files))
    stamp = datetime.now(timezone.utc).isoformat()
    summary = {'status': 'closed_failed', 'reported_at': stamp, 'run_directory': str(run),
        'source_sha256': protocol['source_sha256'], 'source_files': 16,
        'source_utf8_bytes': protocol['source_utf8_bytes'],
        'implementation_sha256': current['sha256'],
        'runtime': protocol['runtime'], 'configured_budgets': cost['configured_budgets'],
        'offline_acceptance': {'path': str(OFFLINE / 'offline-acceptance.json'),
            'sha256': sha(OFFLINE / 'offline-acceptance.json'),
            'latest_distinct_passes': 2367, 'skipped': 1, 'unresolved_failures': 0,
            'whole_repository_execution': False, 'one_all_green_execution': False},
        'analysis_seconds': finished['analysis_seconds'], 'controller_finished_at': finished['finished_at'],
        'stages': result['stages'], 'repair_used': result['repair_used'],
        'selected_cfg': None, 'selected_annotation': result['selected_annotation'],
        'unaccepted_candidate': {'blocks': 258, 'instructions': 619, 'edges': 246,
            'selected': False, 'replacement_blocks': [183],
            'candidate_presence_only': {'remote_sites': 13, 'remote_source_sites': 13,
                'save_callers': 25, 'save_source_callers': 25, 'filesystem_sites': 7}},
        'review_locality': {'retained_task_findings': 5, 'quarantined_cfg_findings': 1,
            'input_contract_inventory_available': False,
            'notice': 'No input contracts were generated; this is not loss of an existing complete contract review.'},
        'unreached_results': {'processing': None, 'input_contract_review': None,
            'propagation': None, 'input_assessments': None, 'deletable_ranges': None, 'doe': None,
            'status': 'not_run', 'backend_result_files': backend_files},
        'actual_counts': cost['actual_counts'], 'known_public_usage': cost['known_public_usage'],
        'cost_limits': cost['limits'], 'timing': cost['timing'],
        'public_network_evidence': cost['public_network_evidence'],
        'replay': replay, 'native_exits': finished['native_exits'],
        'independent_process_closure': {'path': 'process-closure-observation.json',
            'sha256': sha(VERIFY / 'process-closure-observation.json'), 'requested_pids': sorted(recorded),
            'remaining_recorded_processes': 0, 'initial_invalid_receipt_preserved': True},
        'runtime_provenance': cost['provenance'],
        'historical_integrity': {'protected_files': len(baseline['historical_files']), 'changed': [],
            'baseline_sha256': sha(OFFLINE / 'baseline.json')},
        'blockers': [
            'Wire preflight hid pre-existing compiler errors until the only CFG correction was spent.',
            'Review guidance allowed a failed graph-stage target absent from the actual target index.',
            'Shared repair admission independently required an accepted CFG or selected annotation.'],
        'followup_status': 'proposal_only_no_second_implementation_or_run',
        'authorization': 'Sole fresh launch and sole controller-owned replay consumed; all historical runs remain closed.'}
    create(VERIFY / 'run-summary.json', summary)
    for location in (VERIFY, OFFLINE):
        state = read(location / 'continuation-state.json')
        state.update(status='closed_reported', updated_at=stamp, analysis_status='failed',
            new_online_runs_started=1, replay=replay, remaining_recorded_processes=0,
            report_summary=str(VERIFY / 'run-summary.json'),
            instructions='This sole new run and its sole zero-call replay are CLOSED. Preserve all raw failures and frozen artifacts. No restart, resume, extra replay, Skill execution, probe, extra case/resampling, staged import or automatic second fix. Further changes/run require new user instruction; followup-plan.zh.md is proposal only.')
        (location / 'continuation-state.json').write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    reports = {p.relative_to(PROJECT).as_posix(): sha(p) for p in sorted(VERIFY.rglob('*'))
               if p.is_file() and p.suffix in {'.json', '.md', '.txt', '.py', '.ps1'}
               and '__pycache__' not in p.parts and 'source-package' not in p.parts}
    frozen_run = {p.relative_to(run).as_posix(): sha(p) for p in sorted(run.rglob('*'))
                  if p.is_file()}
    create(VERIFY / 'report-closeout.json', {'status': 'closed', 'reported_at': stamp,
        'run_directory': str(run), 'implementation_sha256': current['sha256'],
        'source_sha256': protocol['source_sha256'], 'report_files': reports,
        'run_files': frozen_run, 'historical_files_unchanged': len(baseline['historical_files']),
        'final_result': 'failed', 'replay': replay,
        'process_absence_record': 'process-closure-observation.json',
        'note': 'All report writes are new-run evidence only; no analysis, model, replay, process control or Skill was executed by this seal.'})
    print(json.dumps({'status': 'closed', 'analysis_status': result['status'], 'replay': replay,
        'native_starts': 6, 'known_public_tokens': cost['known_public_usage']['total_tokens'],
        'historical_files_unchanged': len(baseline['historical_files']),
        'sealed_run_files': len(frozen_run), 'sealed_report_files': len(reports)}, indent=2))


if __name__ == '__main__':
    main()
