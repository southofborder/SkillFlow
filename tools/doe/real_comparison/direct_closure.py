"""Zero-call lineage-aware closure for the prospective direct-only continuation.

Imported workflows retain their original launch paths and receipt bytes. They are
verified against the separately closed donor, never rewritten into new calls.
New requests are replayed with the exact generation arguments, including None
when a last-message file is absent. This does not accept a rejected response.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from . import direct_continuation as continuation
from . import exploratory_cli as base
from .exploratory_grading import verify_closed_outputs
from .formal_cli import tree_hashes
from .protocol import sha256, utc_now, write_json

SCHEMA = 'skillflow-direct-lineage-closure-v1'
TERMINAL = {'complete', 'failed', 'protocol_aborted', 'not_reviewable'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def expected_acceptance(receipt, process, answer):
    return bool(not receipt['violations'] and receipt.get('protocol_status') == 'conformant'
        and all(receipt.get(k) is True for k in
                ('configuration_verified', 'provider_verified', 'usage_verified', 'completed'))
        and answer is not None and process.get('status') == 'process_exited'
        and process.get('returncode') == 0)


def verify_origin_tree(run, donor, workflow_id, donor_seal):
    """Imported bytes must match both the donor seal and current original tree."""
    prefix = 'workflows/' + workflow_id + '/'
    expected = {name[len(prefix):]: digest for name, digest in donor_seal['files'].items()
                if name.startswith(prefix)}
    require(bool(expected), 'Imported workflow lacks donor output-seal evidence')
    require(tree_hashes(run / 'workflows' / workflow_id) == expected
            == tree_hashes(donor / 'workflows' / workflow_id),
            'An imported workflow changed or acquired new evidence: ' + workflow_id)
    return expected


def verify_complete_answer_binding(run, directory, result, request_reports):
    """One-shot complete means the final/view is the one accepted delivery."""
    require(len(request_reports) == 1 and request_reports[0]['accepted'] is True,
            'A complete direct workflow requires exactly one accepted request')
    requests = list(directory.glob('requests/q*'))
    require(len(requests) == 1 and requests[0].name == 'q001',
            'A complete direct workflow requires exactly its original q001')
    answer = directory / 'answer.txt'
    request_answer = requests[0] / 'answer.txt'
    require(answer.is_file() and request_answer.is_file()
            and answer.read_bytes() == request_answer.read_bytes()
            and (directory / 'candidate-view.txt').read_bytes()
            == answer.read_text(encoding='utf-8').encode('utf-8')
            and result.get('answer_sha256') == sha256(request_answer),
            'Complete direct final, candidate view and replayed request answer differ')
    relative = answer.relative_to(run).as_posix()
    candidate = read(directory / 'candidate-manifest.json')
    require(candidate.get('files') == {relative: sha256(answer)}
            and candidate.get('reading_view_files') == [relative],
            'Complete direct candidate lineage differs from its sole final answer')


def inspect_new_request(run, item, directory, manifest):
    """Pure saved-byte replay; never execute launch or alter receipt/response."""
    req = read(directory / 'request.json')
    core = (directory / 'core-prompt.txt').read_bytes().decode('utf-8')
    expected = (base.render_review(run, item['case_id'], item['method'], base.original_answer(run, item))
                if item['kind'] == 'review' else base.render_direct(run, item['case_id'], item['method']))
    require(core == expected and sha256(directory / 'core-prompt.txt') == req['core_sha256']
            and (directory / 'prompt.txt').read_bytes() == base.native.ENVELOPE.replace('{core}', core).encode('utf-8')
            and sha256(directory / 'prompt.txt') == req['delivery_sha256']
            and req.get('workflow_id') == item['workflow_id']
            and req.get('references_or_scores_supplied') is False,
            'Complete direct/review prompt no longer matches frozen input')
    process_path = directory / 'cli/process-result.json'
    if not process_path.exists():
        never_dispatched = (not (directory / 'dispatch.json').exists()
                            and not (directory / 'cli/process-start.json').exists())
        require(never_dispatched and not any((directory / name).exists() for name in
                ('receipt.json', 'response.json', 'answer.txt', 'cli/last-message.txt')),
                'A dispatched request lacks terminal process evidence')
        return {'request': directory.relative_to(run).as_posix(), 'receipt_available': False,
                'accepted': False, 'usage_known': True, 'session_id': None, 'response_ids': [],
                'disposition': 'Prepared but no dispatch or process start; zero target calls'}
    process = read(process_path)
    if not (directory / 'receipt.json').exists():
        require((directory / 'failure.json').exists(), 'Unfinished request lacks retained failure evidence')
        return {'request': directory.relative_to(run).as_posix(), 'receipt_available': False,
                'accepted': False, 'usage_known': False, 'session_id': None, 'response_ids': []}
    saved, launch = read(directory / 'receipt.json'), read(directory / 'cli/launch.json')
    require(sha256(saved['raw_receipt_path']) == saved['raw_receipt_sha256']
            and launch['command'] == base.cli.command(manifest['executable'], directory / 'cli')
            and launch['base_instructions_sha256'] == manifest['base_instructions_sha256']
            and launch['developer_segment_sha256'] == manifest['developer_segment_sha256']
            and launch['stdin_sha256'] == req['delivery_sha256']
            and saved['stdout_sha256'] == sha256(directory / 'cli/stdout.jsonl')
            and saved['process_result_sha256'] == sha256(process_path),
            'Saved direct launch/receipt evidence changed')
    last = directory / 'cli/last-message.txt'
    answer, replayed = base.cli.inspect_receipt(saved['raw_receipt_path'], saved['cli_session_id'], launch,
        stdout_path=directory / 'cli/stdout.jsonl', last_message_path=last if last.exists() else None)
    require(all(saved.get(k) == v for k, v in replayed.items()),
            'Generation-equivalent direct receipt replay differs from saved facts')
    response = read(directory / 'response.json')
    require(response.get('accepted') is expected_acceptance(saved, process, answer)
            and response.get('process_status') == process.get('status')
            and response.get('answer_sha256') == (base.v3.digest(answer) if answer is not None else None),
            'Saved acceptance or answer attribution changed')
    require((directory / 'answer.txt').exists() == (answer is not None),
            'Visible answer absence/presence changed')
    if answer is not None:
        require((directory / 'answer.txt').read_bytes() == answer.encode('utf-8'),
                'Complete visible answer changed')
    return {'request': directory.relative_to(run).as_posix(), 'receipt_available': True,
            'accepted': response['accepted'], 'usage_known': saved.get('usage_verified') is True,
            'session_id': saved['cli_session_id'], 'response_ids': sorted(saved['usage']['by_response_id']),
            'protocol_status': saved['protocol_status'], 'violations': saved['violations'],
            'last_message_argument': 'existing Path' if last.exists() else None}


def verify_lineage(run_dir):
    run = Path(run_dir).resolve()
    manifest = base.verify_run(run, generation=False)
    lineage, plan = read(run / 'direct-continuation.json'), read(run / 'plan.json')
    donor = Path(lineage['donor_run']).resolve()
    _, donor_seal = verify_closed_outputs(donor)
    require(lineage['schema_version'] == continuation.SCHEMA
            and lineage['paused_method'] == 'skillflow'
            and lineage['user_quotation'] == continuation.USER_QUOTE
            and lineage.get('other_user_process_controlled') is False
            and lineage.get('target_resampling') is False
            and lineage['donor_freeze_sha256'] == sha256(donor / 'freeze.json')
            and lineage['donor_stop_sha256'] == sha256(donor / 'dispatch-stop.json')
            and plan['continuation_manifest_sha256'] == sha256(run / 'direct-continuation.json'),
            'Prospective continuation lineage differs from its frozen steering')
    schedule = read(run / 'schedule.json')
    items = schedule['main'] + schedule['reviews']
    imported = {x['workflow_id']: x for x in lineage['retained_original_outputs']}
    new = set(lineage['new_workflow_ids'])
    require(len(schedule['main']) == 144 and len(schedule['reviews']) == 48
            and len(imported) == 28 and len(new) == 164 and not new.intersection(imported)
            and len({x['workflow_id'] for x in items}) == 192
            and {x['workflow_id'] for x in items} == new | set(imported)
            and all(x['method'] in {'audit', 'chain'} for x in items)
            and plan['planned_outputs'] == 192,
            'Direct-only identities, counts or allowlist changed')
    require((run / 'controller-finished.json').exists(), 'The direct controller has not finished')
    require({p.name for p in (run / 'workflows').iterdir() if p.is_dir()}
            == {x['workflow_id'] for x in items}, 'Unplanned or missing direct workflow directory')
    reports, sessions, responses = [], set(), set()
    statuses = Counter()
    starts = 0
    for item in items:
        wid = item['workflow_id']
        directory = run / 'workflows' / wid
        result = read(directory / 'result.json')
        require(result.get('status') in TERMINAL and result.get('workflow_id') == wid
                and not result.get('native'), 'A direct identity lacks a terminal direct-only result')
        statuses[result['status']] += 1
        if wid in imported:
            verify_origin_tree(run, donor, wid, donor_seal)
            origin = imported[wid]
            require(result['status'] == 'complete' and sha256(directory / 'result.json') == origin['result_sha256']
                    and sha256(directory / 'answer.txt') == origin['answer_sha256'],
                    'Imported original identity or final answer changed')
        if result.get('artifact_manifest_sha256'):
            base.verify_candidate(run, wid, result)
        workflow_reports = []
        for request in base.requests(run, wid):
            if wid in imported:
                saved = read(request / 'receipt.json')
                record = {'request': request.relative_to(run).as_posix(), 'receipt_available': True,
                    'accepted': read(request / 'response.json')['accepted'], 'usage_known': saved.get('usage_verified') is True,
                    'session_id': saved['cli_session_id'], 'response_ids': sorted(saved['usage']['by_response_id']),
                    'origin': 'sealed_donor_original_not_a_new_call'}
            else:
                record = inspect_new_request(run, item, request, manifest)
                start = request / 'cli/process-start.json'
                starts += start.exists() and read(start).get('actual_cli_process_started') is True
            sid, ids = record['session_id'], set(record['response_ids'])
            require((sid is None or sid not in sessions) and not ids.intersection(responses),
                    'A direct session or response identity is reused')
            if sid is not None: sessions.add(sid)
            responses.update(ids)
            reports.append(record)
            workflow_reports.append(record)
        if result['status'] == 'complete':
            verify_complete_answer_binding(run, directory, result, workflow_reports)
    return {'schema_version': SCHEMA, 'verified_at': utc_now(), 'status': 'matched', 'model_calls': 0,
        'semantic_grading_participation': False, 'logical_direct_outputs': 192,
        'inherited_completed_outputs': 28, 'new_planned_workflows': 164,
        'new_actual_cli_starts': starts, 'terminal_statuses': dict(statuses),
        'donor_run': str(donor), 'donor_output_freeze_sha256': sha256(donor / 'output-freeze.json'),
        'continuation_manifest_sha256': sha256(run / 'direct-continuation.json'),
        'donor_closure_compatibility': donor_seal.get('closure_compatibility'),
        'new_receipt_replay_uses_exact_generation_absent_last_message_argument': True,
        'unknown_usage_preserved': [x['request'] for x in reports if not x['usage_known']],
        'request_evidence': reports, 'usage_including_imports': base.usage(run),
        'scope': 'Byte integrity and terminal closure only. Imported calls remain original costs. Prospective direct epoch does not complete the interrupted same-epoch three-method comparison.'}


def close(run_dir):
    run = Path(run_dir).resolve()
    for name in ('output-freeze.json', 'summary.json', 'lineage-verification.json'):
        require(not (run / name).exists(), 'Direct closure never replaces existing evidence')
    before = tree_hashes(run)
    verification = verify_lineage(run)
    require(tree_hashes(run) == before, 'Direct verification changed generation evidence')
    result = continuation.summary(run)
    require(result['closed_results'] == 192, 'All192 direct logical outcomes must be terminal')
    write_json(run / 'lineage-verification.json', verification, immutable=True)
    provenance = {'schema_version': SCHEMA, 'verifier_path': Path(__file__).relative_to(base.ROOT).as_posix(),
        'verifier_sha256': sha256(__file__), 'verification_sha256': sha256(run / 'lineage-verification.json'),
        'donor_output_freeze_sha256': verification['donor_output_freeze_sha256'],
        'model_calls': 0, 'imported_calls_are_not_new_calls': True}
    result['closure_lineage'] = provenance
    write_json(run / 'summary.json', result, immutable=True)
    write_json(run / 'output-freeze.json', {'schema_version': SCHEMA, 'closed_at': utc_now(),
        'planned_outputs': 192, 'files': {'workflows/' + k: v for k, v in tree_hashes(run / 'workflows').items()},
        'failed_results_remain_in_denominator': True, 'closure_lineage': provenance,
        'summary_sha256': sha256(run / 'summary.json')}, immutable=True)
    return {'status': 'closed_direct_continuation', 'planned_outputs': 192, 'model_calls': 0,
            'output_freeze_sha256': sha256(run / 'output-freeze.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('verify', 'close'))
    parser.add_argument('--run-dir', required=True)
    args = parser.parse_args()
    value = close(args.run_dir) if args.command == 'close' else verify_lineage(args.run_dir)
    print(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
