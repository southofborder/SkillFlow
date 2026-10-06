"""Experimental drivers require committed main files and never repair on replay."""

from skillflow.common.paths import project_root, resolve_material_path
import importlib.util
from pathlib import Path
import runpy
from threading import Event

import pytest
from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import read_json


TOOLS = project_root() / 'tools/propagation'


def load_tool(name):
    spec = importlib.util.spec_from_file_location('propagation_test_' + name, TOOLS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pilot_does_not_publish_uncommitted_main_file(tmp_path, monkeypatch):
    tool, writer = load_tool('run_pilot'), ArtifactWriter(())
    monkeypatch.setattr(tool, 'PINS', {'001': ('N01', '', '')})
    base = tmp_path / 'cases/001/propagation'
    writer.json(base / 'doe-input.json', {'status': 'complete'})
    writer.text(base / 'report.html', '<p>not committed</p>')
    summary = tool.summarize(tmp_path, writer)
    row = summary['cases'][0]
    assert row['propagation'] == 'uncommitted' and not row['propagation_committed']
    assert 'propagation/doe-input.json' not in (tmp_path / 'report.md').read_text(encoding='utf-8')
    assert 'propagation/report.html' not in (tmp_path / 'index.html').read_text(encoding='utf-8')


def test_pilot_validates_committed_main_file_and_links_it(tmp_path, monkeypatch):
    tool = load_tool('run_pilot')
    monkeypatch.setattr(tool, 'PINS', {'001': ('N01', '', '')})
    demo = runpy.run_path(str(project_root() / 'examples/propagation/propagation_demo.py'))
    base = tmp_path / 'cases/001/propagation'
    demo['save_demo'](base)
    summary = tool.summarize(tmp_path, ArtifactWriter(()))
    row = summary['cases'][0]
    assert row['propagation'] == 'complete' and row['propagation_committed']
    assert 'propagation/doe-input.json' in (tmp_path / 'report.md').read_text(encoding='utf-8')
    value = read_json(base / 'doe-input.json')
    value['status'] = 'incomplete'
    ArtifactWriter(()).json(base / 'doe-input.json', value)
    summary = tool.summarize(tmp_path, ArtifactWriter(()))
    assert summary['cases'][0]['propagation'] == 'execution_error'
    assert not summary['cases'][0]['propagation_committed']
    assert 'propagation/doe-input.json' not in (tmp_path / 'report.md').read_text(encoding='utf-8')


def test_pilot_replay_missing_manifest_never_starts_new_propagation(tmp_path, monkeypatch):
    tool = load_tool('run_pilot')
    case = {'case_id': '001', 'sample_id': 'N01', 'source_inventory': {}}
    outcome = {'feedback': {'status': 'audit_passed'}, 'annotation': {'status': 'complete'}}
    ArtifactWriter(()).json(tmp_path / 'cases/001/replay/result.json', outcome)
    monkeypatch.setattr(tool._shared, '_case', lambda *a, **kw: outcome)
    monkeypatch.setattr(tool, 'run_propagation', lambda *a, **kw: pytest.fail('replay started a new solve'))
    with pytest.raises(ValueError, match='no committed manifest'):
        tool.run_case(tmp_path, case, config={}, renderer=None, factory=None, secrets=(), stopping=Event(), replay=True)
    assert not (tmp_path / 'cases/001/propagation/doe-input.json').exists()


def test_render_demo_delegates_to_shared_save(tmp_path):
    tool = load_tool('render_demo')
    result = tool.generate(tmp_path / 'demo')
    assert result['schema_version'] == 'skillflow-doe-input-v7'
    assert read_json(tmp_path / 'demo/doe-input.json') == result
    assert read_json(tmp_path / 'demo/audit/provenance.json')['kind'] == 'hand_authored_specification'
    assert not (tmp_path / 'demo/result.json').exists()
    with pytest.raises(ValueError, match='new or empty'):
        tool.generate(tmp_path / 'demo')


def verification_fixture(directory, *, status='invalid_response'):
    writer = ArtifactWriter(())
    writer.json(directory / 'verification/protected-before.json', {})
    writer.json(directory / 'manifest.json', {
        'schema_version': 4, 'identity': 'skill-ir-source-boundaries-pilot3-v4',
        'cases': [{'case_id': '001'}], 'policy': {'planned_logical_calls': 63},
    })
    result = {'status': status, 'reason': '非法标注证据，保持原始失败', 'counts': {'logical_calls': 1}}
    for path in ('annotation/result.json', 'annotation/replay/result.json'):
        writer.json(directory / 'cases/001' / path, result)
    feedback = {'status': 'audit_passed', 'reason': '核对器通过'}
    for path in ('feedback/result.json', 'feedback/replay/result.json'):
        writer.json(directory / 'cases/001' / path, feedback)
    counts = {'total_logical_calls': 3, 'extraction_logical_calls': 1, 'audit_logical_calls': 1,
              'annotation_logical_calls': 1, 'audit_execution_calls': 1, 'audit_execution_retries': 0,
              'total_execution_calls': 3, 'semantic_revisions': 0, 'structural_repairs': 0, 'http_attempts': 3}
    for path in ('result.json', 'replay/result.json'):
        writer.json(directory / 'cases/001' / path, {'feedback': feedback, 'annotation': result,
                                                    'selection': {'auditor_passed': True}, 'source_binding': {}, 'counts': counts})
    writer.json(directory / 'summary.json', {'logical_calls': 3, 'cases': [
        {'case_id': '001', 'logical_calls': 3, 'call_counts': counts}]})
    writer.json(directory / 'verification/network-guard.json', {'status': 'passed', 'network_attempts': 0})
    return writer


def stage_row(result, name):
    return next(row for row in result['replay_comparisons'] if row['stage'] == name)


@pytest.mark.parametrize("status", ["invalid_response", "semantic_failure"])
def test_verifier_accepts_preserved_annotation_failure_without_doe_or_visuals(tmp_path, monkeypatch, status):
    verification_fixture(tmp_path, status=status)
    tool = load_tool('verify_pilot')
    monkeypatch.setattr(tool, 'load_propagation_run', lambda *a: pytest.fail('failed annotation has no propagation to load'))
    result = tool.verify(tmp_path)
    assert result['passed'] and result['call_budget_ok']
    assert stage_row(result, 'annotation')['status'] == status
    propagation = stage_row(result, 'propagation')
    assert propagation['status'] == 'not_run' and propagation['equal'] is None
    assert '非法标注证据' in propagation['reason']
    assert all(value['status'] == 'not_performed' for value in result['visual_checks'].values())


def test_verifier_refuses_prior_pilot_identity(tmp_path):
    writer = verification_fixture(tmp_path)
    manifest = read_json(tmp_path / 'manifest.json')
    manifest.update(schema_version=3, identity='skill-ir-source-boundaries-pilot3-v3')
    writer.json(tmp_path / 'manifest.json', manifest)
    with pytest.raises(ValueError, match='unsupported propagation pilot'):
        load_tool('verify_pilot').verify(tmp_path)


def test_verifier_still_requires_failed_annotation_replay_match(tmp_path):
    writer = verification_fixture(tmp_path)
    writer.json(tmp_path / 'cases/001/annotation/replay/result.json', {'status': 'complete'})
    result = load_tool('verify_pilot').verify(tmp_path)
    assert not result['passed'] and stage_row(result, 'annotation')['equal'] is False


def test_verifier_missing_replay_is_reported_not_raised(tmp_path):
    verification_fixture(tmp_path)
    (tmp_path / 'cases/001/annotation/replay/result.json').unlink()
    result = load_tool('verify_pilot').verify(tmp_path)
    assert not result['passed'] and stage_row(result, 'annotation')['status'] == 'verification_error'


def test_verifier_usable_annotation_without_committed_doe_does_not_pass(tmp_path):
    verification_fixture(tmp_path, status='complete')
    result = load_tool('verify_pilot').verify(tmp_path)
    assert not result['passed']
    assert stage_row(result, 'propagation')['status'] == 'not_run'
    assert stage_row(result, 'propagation')['equal'] is False


def test_verifier_rejects_partial_doe_and_preserves_visual_failure(tmp_path):
    writer = verification_fixture(tmp_path)
    writer.json(tmp_path / 'cases/001/propagation/doe-input.json', {'status': 'complete'})
    writer.json(tmp_path / 'offline-demo/visual-review/checks.json', {'status': 'failed', 'reason': '文本溢出'})
    result = load_tool('verify_pilot').verify(tmp_path)
    assert not result['passed']
    assert stage_row(result, 'propagation')['status'] == 'uncommitted'
    assert result['visual_checks']['offline-demo']['status'] == 'failed'


def test_verifier_checks_feedback_and_selection_replay(tmp_path):
    writer = verification_fixture(tmp_path)
    writer.json(tmp_path / 'cases/001/feedback/replay/result.json', {'status': 'semantic_failure'})
    changed = read_json(tmp_path / 'cases/001/replay/result.json')
    changed['selection']['auditor_passed'] = False
    writer.json(tmp_path / 'cases/001/replay/result.json', changed)
    result = load_tool('verify_pilot').verify(tmp_path)
    assert not result['passed']
    assert stage_row(result, 'feedback')['equal'] is False
    assert stage_row(result, 'case')['equal'] is False


def test_verifier_requires_network_guard_and_distinct_call_budgets(tmp_path):
    writer = verification_fixture(tmp_path)
    writer.json(tmp_path / 'verification/network-guard.json', {'status': 'passed', 'network_attempts': 1})
    result = load_tool('verify_pilot').verify(tmp_path)
    assert not result['passed'] and not result['offline_network_guard_passed']
    writer.json(tmp_path / 'verification/network-guard.json', {'status': 'passed', 'network_attempts': 0})
    summary = read_json(tmp_path / 'summary.json')
    summary['cases'][0]['call_counts']['annotation_logical_calls'] = 2
    writer.json(tmp_path / 'summary.json', summary)
    assert not load_tool('verify_pilot').verify(tmp_path)['call_budget_ok']


def test_case_uses_new_snapshot_and_continues_diagnostic_graph(tmp_path, monkeypatch):
    tool = load_tool('run_pilot')
    case = {'case_id': '010', 'sample_id': 'Q04', 'source_inventory': {},
            'comparison': {'analysis': 'MUST_NOT_USE_OLD_GRAPH'}}
    seen = []
    def shared(directory, item, **kwargs):
        seen.append(item)
        assert 'analysis' not in item
        assert item['package_path'] == str(tmp_path / 'cases/010/source/inputs/package')
        return {'feedback': {'status': 'semantic_failure'}, 'annotation': {'status': 'complete'}}
    monkeypatch.setattr(tool._shared, '_case', shared)
    monkeypatch.setattr(tool, 'run_propagation', lambda ann, **kw: seen.append((ann, kw)) or {'status': 'complete'})
    tool.run_case(tmp_path, case, config={}, renderer=None, factory=object(), secrets=(), stopping=Event())
    assert len(seen) == 2 and seen[1][0] == tmp_path / 'cases/010/annotation'


@pytest.mark.parametrize('feedback,annotation', [('interrupted', 'not_run'), ('extraction_error', 'not_run'),
                                                ('audit_passed', 'invalid_response')])
def test_case_never_falls_back_after_missing_graph_or_invalid_annotation(tmp_path, monkeypatch, feedback, annotation):
    tool = load_tool('run_pilot')
    monkeypatch.setattr(tool._shared, '_case', lambda *a, **kw: {
        'feedback': {'status': feedback}, 'annotation': {'status': annotation}})
    monkeypatch.setattr(tool, 'run_propagation', lambda *a, **kw: pytest.fail('invalid stage started propagation'))
    stopping = Event()
    tool.run_case(tmp_path, {'case_id': '001', 'sample_id': 'N01', 'source_inventory': {}},
                  config={}, renderer=None, factory=None, secrets=(), stopping=stopping)
    assert stopping.is_set() == (feedback == 'interrupted')


def test_prepare_freezes_sources_without_model_or_old_cfg(tmp_path, monkeypatch):
    from skillflow.common.inputs.snapshot import freeze_input
    from skillflow.common.inputs.snapshot import read_snapshot
    tool = load_tool('run_pilot')
    source = tmp_path / 'skill'
    source.mkdir()
    (source / 'SKILL.md').write_text('Read town from the request and return it.', encoding='utf-8')
    freeze_input(source, tmp_path / 'reference', ArtifactWriter(()))
    _, bundle, metadata = read_snapshot(tmp_path / 'reference')
    case = {'case_id': '001', 'sample_id': 'N01', 'input': str(source),
            'source_sha256': bundle['source_sha256'], 'package_bytes_sha256': metadata['package_bytes_sha256'],
            'source_inventory': {e['path']: {'bytes': e['size'], 'sha256': e['raw_sha256']} for e in metadata['files']},
            'comparison': {'analysis': 'NEVER_READ'}}
    manifest = {'schema_version': tool.FORMAT_VERSION, 'identity': tool.IDENTITY, 'cases': [case],
                'renderer': {'path': 'printer'}, 'config': {}, 'policy': tool.POLICY}
    monkeypatch.setattr(tool, 'expected_manifest', lambda *a: manifest)
    monkeypatch.setattr(tool, 'streaming_factory', lambda *a, **kw: pytest.fail('prepare created online client'))
    monkeypatch.setattr(tool._shared, '_case', lambda *a, **kw: pytest.fail('prepare ran feedback'))
    directory = tmp_path / 'new-run'
    assert tool.main(['prepare', '--run-dir', str(directory)]) == 0
    assert read_json(directory / 'manifest.json') == manifest
    assert not (directory / 'cases/001/selected-analysis.json').exists()
    assert (directory / 'cases/001/source/inputs/package/SKILL.md').read_bytes() == (source / 'SKILL.md').read_bytes()
    (directory / 'cases/001/source/inputs/package/SKILL.md').write_text('changed', encoding='utf-8')
    with pytest.raises(ValueError, match='changed'):
        tool.main(['run', '--run-dir', str(directory)])


def test_pilot_rejects_old_identity_before_creating_client(tmp_path, monkeypatch):
    tool = load_tool('run_pilot')
    ArtifactWriter(()).json(tmp_path / 'manifest.json', {'schema_version': 3, 'identity': 'skill-ir-propagation-pilot3-v3'})
    monkeypatch.setattr(tool, 'streaming_factory', lambda *a, **kw: pytest.fail('old record created client'))
    with pytest.raises(ValueError, match='unsupported pilot version'):
        tool.main(['run', '--run-dir', str(tmp_path)])


def test_never_started_case_replay_persists_verified_outcome_without_calls(tmp_path, monkeypatch):
    tool = load_tool('run_pilot')
    missing = tool._shared._missing('用户中断；未启动此案例')
    saved = {'feedback': missing, 'annotation': missing, 'selection': None, 'source_binding': None,
             'counts': tool._shared._counts(missing, missing), 'scheduler_error': None}
    ArtifactWriter(()).json(tmp_path / 'cases/010/result.json', saved)
    monkeypatch.setattr(tool, 'streaming_factory', lambda *a, **kw: pytest.fail('replay created client'))
    monkeypatch.setattr(tool, 'run_propagation', lambda *a, **kw: pytest.fail('replay started propagation'))
    result = tool.run_case(tmp_path, {'case_id': '010', 'sample_id': 'Q04', 'source_inventory': {}},
                           config={}, renderer=None, factory=None, secrets=(), stopping=Event(), replay=True)
    assert result == saved == read_json(tmp_path / 'cases/010/replay/result.json')
    assert not (tmp_path / 'cases/010/feedback').exists()
    assert not (tmp_path / 'cases/010/annotation').exists()


def test_started_case_with_failed_local_summary_never_reports_zero_calls(tmp_path, monkeypatch):
    tool = load_tool('run_pilot')
    monkeypatch.setattr(tool, 'PINS', {'001': ('N01', '', '')})
    writer = ArtifactWriter(())
    writer.json(tmp_path / 'cases/001/feedback/manifest.json', {'started': True})
    summary = tool.summarize(tmp_path, writer)
    assert summary['cases'][0]['feedback'] == 'execution_error'
    assert summary['logical_calls'] is None
    writer.json(tmp_path / 'cases/001/feedback/result.json', {
        'status': 'audit_passed', 'counts': {'extraction_logical_calls': 2, 'audit_logical_calls': 1,
        'audit_execution_calls': 1, 'audit_execution_retries': 0, 'semantic_revisions': 0,
        'structural_repairs': 1, 'http_attempts': 3, 'http_retries': 0}})
    assert tool.summarize(tmp_path, writer)['logical_calls'] == 3
