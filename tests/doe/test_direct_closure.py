"""Invented metadata tests; no real outputs, launches, or frozen-code patches."""
from copy import deepcopy
import json

import pytest

from tools.doe.real_comparison import direct_closure as closure
from tools.doe.real_comparison.protocol import sha256


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


def conformant():
    receipt = {'violations': [], 'protocol_status': 'conformant',
        **{k: True for k in ('configuration_verified', 'provider_verified', 'usage_verified', 'completed')}}
    return receipt, {'status': 'process_exited', 'returncode': 0}


def test_only_fully_conformant_saved_response_is_accepted():
    receipt, process = conformant()
    assert closure.expected_acceptance(receipt, process, '原文 {evidence}') is True
    assert closure.expected_acceptance(receipt, process, None) is False


@pytest.mark.parametrize('field', ['configuration_verified', 'provider_verified', 'usage_verified', 'completed'])
def test_missing_invariant_preserves_rejection(field):
    receipt, process = conformant()
    receipt[field] = False
    assert closure.expected_acceptance(receipt, process, 'answer') is False


@pytest.mark.parametrize('change', ['violation', 'protocol', 'timeout', 'exit'])
def test_other_failed_delivery_cannot_become_accepted(change):
    receipt, process = conformant()
    if change == 'violation': receipt['violations'] = ['Retained transport error']
    if change == 'protocol': receipt['protocol_status'] = 'violated'
    if change == 'timeout': process['status'] = 'timeout'
    if change == 'exit': process['returncode'] = 1
    assert closure.expected_acceptance(receipt, process, 'answer') is False


def trees(tmp_path):
    run, donor = tmp_path / 'new', tmp_path / 'original'
    for root in (run, donor):
        path = root / 'workflows/w/answer.txt'
        path.parent.mkdir(parents=True)
        path.write_bytes('Complete 原文\r\n'.encode('utf-8'))
    seal = {'files': {'workflows/w/answer.txt': sha256(donor / 'workflows/w/answer.txt')}}
    return run, donor, seal


def test_import_is_exact_original_not_a_new_delivery(tmp_path):
    run, donor, seal = trees(tmp_path)
    assert closure.verify_origin_tree(run, donor, 'w', seal) == {'answer.txt': seal['files']['workflows/w/answer.txt']}


@pytest.mark.parametrize('change', ['new_changed', 'donor_changed', 'new_extra', 'seal_changed'])
def test_import_changes_fail_closed(tmp_path, change):
    run, donor, seal = trees(tmp_path)
    if change == 'new_changed': (run / 'workflows/w/answer.txt').write_text('different', encoding='utf-8')
    if change == 'donor_changed': (donor / 'workflows/w/answer.txt').write_text('different', encoding='utf-8')
    if change == 'new_extra': (run / 'workflows/w/extra.json').write_text('{}', encoding='utf-8')
    if change == 'seal_changed': seal['files']['workflows/w/answer.txt'] = '0' * 64
    with pytest.raises(ValueError): closure.verify_origin_tree(run, donor, 'w', seal)


def prepared(tmp_path):
    run = tmp_path / 'run'
    (run / 'prompts').mkdir(parents=True)
    (run / 'prompts/audit.txt').write_text('{source_bundle}', encoding='utf-8')
    (run / 'cases/c').mkdir(parents=True)
    (run / 'cases/c/source-bundle.txt').write_text('Original 原文 source', encoding='utf-8')
    item = {'kind': 'main', 'method': 'audit', 'case_id': 'c', 'workflow_id': 'w'}
    directory = run / 'workflows/w/requests/q001'
    directory.mkdir(parents=True)
    core = closure.base.render_direct(run, 'c', 'audit')
    (directory / 'core-prompt.txt').write_bytes(core.encode('utf-8'))
    (directory / 'prompt.txt').write_bytes(closure.base.native.ENVELOPE.replace('{core}', core).encode('utf-8'))
    save(directory / 'request.json', {'workflow_id': 'w', 'core_sha256': sha256(directory / 'core-prompt.txt'),
         'delivery_sha256': sha256(directory / 'prompt.txt'), 'references_or_scores_supplied': False})
    return run, item, directory


def test_predispatch_stop_is_zero_calls_not_unknown_billing(tmp_path):
    run, item, directory = prepared(tmp_path)
    result = closure.inspect_new_request(run, item, directory, {})
    assert result['usage_known'] is True and result['response_ids'] == [] and result['accepted'] is False
    assert 'zero target calls' in result['disposition']


@pytest.mark.parametrize('path', ['dispatch.json', 'cli/process-start.json', 'answer.txt', 'receipt.json'])
def test_dispatched_or_answered_request_cannot_be_called_predispatch(tmp_path, path):
    run, item, directory = prepared(tmp_path)
    save(directory / path, {})
    with pytest.raises(ValueError): closure.inspect_new_request(run, item, directory, {})


def test_complete_input_changed_before_replay_fails(tmp_path):
    run, item, directory = prepared(tmp_path)
    (directory / 'core-prompt.txt').write_text('Truncated', encoding='utf-8')
    with pytest.raises(ValueError): closure.inspect_new_request(run, item, directory, {})


def complete(tmp_path):
    run = tmp_path / 'run'
    directory = run / 'workflows/w'
    request = directory / 'requests/q001'
    request.mkdir(parents=True)
    for path in (directory / 'answer.txt', directory / 'candidate-view.txt', request / 'answer.txt'):
        path.write_bytes('Original visible answer 原文'.encode('utf-8'))
    result = {'answer_sha256': sha256(request / 'answer.txt')}
    relative = (directory / 'answer.txt').relative_to(run).as_posix()
    save(directory / 'candidate-manifest.json', {'files': {relative: result['answer_sha256']}, 'reading_view_files': [relative]})
    return run, directory, result, [{'accepted': True}]


def test_complete_final_is_the_actual_single_accepted_answer(tmp_path):
    closure.verify_complete_answer_binding(*complete(tmp_path))


def test_direct_view_preserves_exact_frozen_artifact_renderer_newline_behavior(tmp_path):
    run, directory, result, reports = complete(tmp_path)
    raw = 'First 原文\r\nSecond line\r\n'.encode('utf-8')
    (directory / 'answer.txt').write_bytes(raw)
    (directory / 'requests/q001/answer.txt').write_bytes(raw)
    (directory / 'candidate-view.txt').write_bytes('First 原文\nSecond line\n'.encode('utf-8'))
    result['answer_sha256'] = sha256(directory / 'answer.txt')
    relative = (directory / 'answer.txt').relative_to(run).as_posix()
    save(directory / 'candidate-manifest.json', {'files': {relative: result['answer_sha256']}, 'reading_view_files': [relative]})
    closure.verify_complete_answer_binding(run, directory, result, reports)


@pytest.mark.parametrize('defect', ['no_request', 'rejected', 'multiple', 'different_final', 'different_view', 'different_result', 'different_manifest'])
def test_self_consistent_candidate_cannot_replace_actual_delivery(tmp_path, defect):
    run, directory, result, reports = complete(tmp_path)
    if defect == 'no_request': reports = []
    if defect == 'rejected': reports[0]['accepted'] = False
    if defect == 'multiple': reports.append({'accepted': True})
    if defect == 'different_final':
        (directory / 'answer.txt').write_text('Different self-consistent final', encoding='utf-8')
        (directory / 'candidate-view.txt').write_text('Different self-consistent final', encoding='utf-8')
        result['answer_sha256'] = sha256(directory / 'answer.txt')
        relative = (directory / 'answer.txt').relative_to(run).as_posix()
        save(directory / 'candidate-manifest.json', {'files': {relative: result['answer_sha256']}, 'reading_view_files': [relative]})
    if defect == 'different_view': (directory / 'candidate-view.txt').write_text('different', encoding='utf-8')
    if defect == 'different_result': result['answer_sha256'] = '0' * 64
    if defect == 'different_manifest': save(directory / 'candidate-manifest.json', {'files': {}, 'reading_view_files': []})
    with pytest.raises(ValueError): closure.verify_complete_answer_binding(run, directory, result, reports)
