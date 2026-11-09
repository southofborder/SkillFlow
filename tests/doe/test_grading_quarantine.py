"""Invented scorer quarantine; no study source, candidate or score is read."""
from copy import deepcopy
import hashlib
from pathlib import Path

import pytest

from tools.doe.real_comparison import exploratory_grading as grading
from tools.doe.real_comparison import mixed_results as mixed
from tools.doe.real_comparison import grading_quarantine as quarantine
from tools.doe.real_comparison.protocol import sha256, write_json
from tools.doe.real_comparison.semantic_metrics import GRADING_SCHEMA_VERSION


@pytest.fixture
def epoch(tmp_path, monkeypatch):
    root = tmp_path / 'synthetic-grading'
    root.mkdir()
    mapping = {}
    for case in range(24):
        for method, kind, repeat in ([(m, 'main', n) for m in ('skillflow', 'audit', 'chain') for n in (1, 2, 3)]
                                    + [(m, 'review', 1) for m in ('audit', 'chain')]):
            candidate = f'candidate-{len(mapping):03d}'
            mapping[candidate] = {'candidate_id': candidate, 'case_id': f'case-{case:02d}',
                'workflow_id': candidate + '-workflow', 'method': method, 'kind': kind, 'repeat': repeat,
                'packet': 'packets/' + candidate, 'chain_secondary_required': method != 'audit'}
    write_json(root / 'private-map.json', {'source_run': str(tmp_path / 'synthetic-run'), 'assignments': list(mapping.values())})
    write_json(root / 'packet-freeze.json', {'source_output_freeze_sha256': 'invented-closed-output'})
    monkeypatch.setattr(mixed.results, '_context', lambda path: (root, mapping, {'source_output_freeze_sha256': 'invented-closed-output'}))
    projection = {}
    paths = {}
    for index, (candidate, item) in enumerate(mapping.items()):
        available = index < 89
        projection[candidate] = {'source_grade_required': available, 'terminal_status': 'complete' if available else 'protocol_aborted'}
        hashes = {field: hashlib.sha256((candidate + field).encode()).hexdigest() for field in quarantine.IDENTITY_FIELDS}
        template = {'candidate_id': candidate, **hashes}
        packet = root / item['packet']
        write_json(packet / 'grade.template.json', template)
        write_json(packet / 'reference.json', {'supported_excesses': [], 'receiving_points': [],
                                             'mandatory_checks': [{'id': 'check'}]})
        write_json(packet / 'execution.json', {'status': projection[candidate]['terminal_status'],
            'request_states': [{'accepted': True, 'protocol_status': 'conformant', 'violation_count': 0,
                'configuration_verified': True, 'provider_verified': True, 'completed': True}] if available else []})
        if not available:
            continue
        agent = '/synthetic/primary-' + candidate
        grade = {'schema_version': grading.SCHEMA, 'grading_schema_version': GRADING_SCHEMA_VERSION,
            'evidence_level': grading.EVIDENCE_LEVEL, **template, 'scoring_role': 'primary',
            'agent_id': agent, 'reviewer_id': agent, 'human_verified': False,
            'actual_human_review_work_seconds': None, 'judgment': 'satisfies_reference',
            'check_results': [{'check_id': 'check', 'status': 'pass'}], 'matched_exposure_ids': [],
            'claim_units': [], 'receiving_point_coverage': [], 'reduction_assessments': [],
            'error_records': [], 'findings': [], 'reference_correction_proposals': [], 'chain_assessment': None}
        path = root / 'submissions' / (candidate + '.primary.json')
        write_json(path, grade)
        paths[candidate] = path
    monkeypatch.setattr(mixed, 'eligibility_rows', lambda root, mapping: deepcopy(projection))
    eligibility = root / 'eligibility.json'
    mixed.eligibility(root, eligibility)
    def grade_record(root, path, *, role, **kwargs):
        path = Path(path)
        grade = mixed.read(path)
        assert grade['scoring_role'] == role
        return {'path': str(path.resolve()), 'sha256': sha256(path), 'validated_grade': grade,
                'protocol_eligible': True, 'execution_status': 'complete', 'content_judgment': grade['judgment'],
                'workflow_primary_judgment': grade['judgment'], 'human_verified': False,
                'evidence_level': grading.EVIDENCE_LEVEL}
    monkeypatch.setattr(mixed.results, '_grade_record', grade_record)
    cases = {f'case-{i:02d}': {'source_cluster': 'cluster-' + str(i // 2 if i < 4 else i - 2)} for i in range(24)}
    monkeypatch.setattr(mixed.results, '_cases', lambda *args: (cases, {}))
    candidate = next(iter(paths))
    grade = mixed.read(paths[candidate])
    sidecar = {'schema_version': quarantine.SCHEMA, 'issue_kind': 'scorer_label_defect',
        'candidate_id': candidate, 'submitted_primary_path': str(paths[candidate]),
        'submitted_primary_sha256': sha256(paths[candidate]), 'saved_primary_bytes_preserved': True,
        'not_target_protocol_failure': True, 'not_reference_change': True, 'semantic_replacement_performed': False,
        'affected_records': ['check_results:check'], 'agent_id': grade['agent_id'], 'reviewer_id': grade['agent_id'],
        'CODEX_THREAD_ID': 'invented-original-scorer-thread', 'human_verified': False,
        'actual_human_review_work_seconds': None, 'original_read_notes': {'actual_reading_complete': True}}
    sidecar_path = quarantine.canonical_sidecar(root, candidate)
    write_json(sidecar_path, sidecar)
    return {'root': root, 'mapping': mapping, 'paths': paths, 'candidate': candidate,
        'sidecar': sidecar_path, 'eligibility': eligibility, 'projection': projection}


def seal(epoch):
    root = epoch['root']
    path = root / 'primary-seal.json'
    sealed = mixed.seal_primary(root, epoch['eligibility'],
        [p for c, p in epoch['paths'].items() if c != epoch['candidate']], path,
        quarantine_sidecar_paths=[epoch['sidecar']])
    assignments = root / 'secondary-assignments.json'
    selected = mixed.prepare_secondaries(root, epoch['eligibility'], path, assignments)
    return path, sealed, assignments, selected


def secondaries(epoch, assignments, *, quarantined_judgment='satisfies_reference', same_agent=False):
    paths = []
    for row in assignments['assignments']:
        if row['assignment_kind'] != 'primary_recheck':
            continue
        candidate = row['candidate_id']
        grade = mixed.read(epoch['paths'][candidate])
        agent = '/synthetic/independent-' + candidate
        if candidate == epoch['candidate']:
            grade['judgment'] = quarantined_judgment
            if same_agent:
                agent = grade['agent_id']
        grade.update(scoring_role='secondary', agent_id=agent, reviewer_id=agent)
        path = epoch['root'] / 'submissions' / (candidate + '.secondary.json')
        write_json(path, grade)
        paths.append(path)
    return paths


def test_disposition_counts_and_blind_fresh_assignments(epoch):
    _, sealed, _, assignments = seal(epoch)
    assert sealed['assistant_primary_results'] == 88
    assert sealed['source_grade_attempt_results'] == 89
    assert sealed['quarantined_source_grade_attempt_results'] == 1
    assert sealed['mechanical_absence_results'] == 175
    assert epoch['candidate'] not in sealed['records']
    attempt = sealed['quarantined_attempts'][epoch['candidate']]
    assert 'validated_grade' not in attempt and attempt['primary_semantic_judgment_imported'] is False
    relevant = [r for r in assignments['assignments'] if r['candidate_id'] == epoch['candidate']]
    assert {r['assignment_kind'] for r in relevant} == {'primary_recheck', 'chain_secondary'}
    assert all(r['excluded_agent_ids'] == [attempt['agent_id']] for r in relevant)
    assert all(not {'sidecar_path', 'judgment', 'quarantined_attempt'}.intersection(r) for r in relevant)


@pytest.mark.parametrize('judgment', ['satisfies_reference', 'substantive_error'])
def test_valid_target_quarantined_primary_stays_unknown_even_after_secondary(epoch, judgment):
    primary, _, assignments_path, assignments = seal(epoch)
    paths = secondaries(epoch, assignments, quarantined_judgment=judgment)
    report = mixed.aggregate(epoch['root'], epoch['eligibility'], primary, assignments_path,
                             secondary_paths=paths, bootstrap_samples=3)
    row = next(r for r in report['rows'] if r['candidate_id'] == epoch['candidate'])
    assert row['judgment'] == row['content_judgment'] == 'indeterminate'
    assert row['execution_status'] == 'complete' and row['protocol_eligible'] is True
    assert not row['assistant_adjudication_complete'] and not row['execution_endpoint_known']
    assert row['adjudicated_grade'] is None
    assert report['bounds']['known_pass'] == 88 and report['bounds']['known_fail'] == 175
    assert report['bounds']['unknown'] == 1 and report['bounds']['planned'] == 264
    assert report['assistant_primary_results'] == 88 and report['source_grade_attempt_results'] == 89
    assert report['quarantined_source_grade_attempt_results'] == 1 and report['mechanical_absence_results'] == 175
    metrics = next(r for r in report['semantic_metrics']['rows'] if r['candidate_id'] == epoch['candidate'])
    assert all(metrics[k] is None for k in ('tp', 'fn', 'fp', 'precision', 'recall', 'substantive_errors'))
    assert report['primary_comparisons'] == report['fixed_review_comparisons'] == []
    assert all(not r['efficiency_supported'] for r in report['resources']['comparisons'])


def test_quarantine_needs_secondary_and_cannot_reuse_original_scorer(epoch):
    primary, _, assignments_path, assignments = seal(epoch)
    row = mixed.quarantined_resolution({}, None)
    assert 'mandatory_primary_recheck_missing' in row['primary_disputes']
    with pytest.raises(ValueError, match='nonindependent secondary'):
        mixed.aggregate(epoch['root'], epoch['eligibility'], primary, assignments_path,
            secondary_paths=secondaries(epoch, assignments, same_agent=True), bootstrap_samples=3)
    paths = secondaries(epoch, assignments)
    path = next(p for p in paths if mixed.read(p)['candidate_id'] == epoch['candidate'])
    grade = mixed.read(path)
    grade['reviewer_id'] = mixed.read(epoch['paths'][epoch['candidate']])['agent_id']
    write_json(path, grade)
    with pytest.raises(ValueError, match='nonindependent secondary'):
        mixed.aggregate(epoch['root'], epoch['eligibility'], primary, assignments_path,
                        secondary_paths=paths, bootstrap_samples=3)


def test_bad_attempt_cannot_be_imported_even_when_quarantine_argument_is_omitted(epoch):
    with pytest.raises(ValueError, match='cannot be imported as a valid primary'):
        mixed.seal_primary(epoch['root'], epoch['eligibility'], list(epoch['paths'].values()),
                           epoch['root'] / 'wrong-seal.json')


def test_valid_and_quarantined_overlap_or_duplicate_sidecars_rejected(epoch):
    with pytest.raises(ValueError, match='cannot be imported as a valid primary'):
        mixed.seal_primary(epoch['root'], epoch['eligibility'], list(epoch['paths'].values()),
            epoch['root'] / 'overlap.json', quarantine_sidecar_paths=[epoch['sidecar']])
    with pytest.raises(ValueError, match='duplicated'):
        mixed.seal_primary(epoch['root'], epoch['eligibility'], [], epoch['root'] / 'duplicate.json',
                           quarantine_sidecar_paths=[epoch['sidecar'], epoch['sidecar']])


@pytest.mark.parametrize('field,value', [
    ('submitted_primary_sha256', '0' * 64), ('not_reference_change', False),
    ('not_target_protocol_failure', False), ('semantic_replacement_performed', True),
    ('human_verified', True), ('reviewer_id', '/synthetic/different-scorer')])
def test_invalid_quarantine_metadata_is_rejected(epoch, field, value):
    sidecar = mixed.read(epoch['sidecar'])
    sidecar[field] = value
    write_json(epoch['sidecar'], sidecar)
    with pytest.raises(ValueError):
        quarantine.validate_quarantined_attempt(epoch['root'], epoch['sidecar'], mapping=epoch['mapping'])


def test_sidecar_or_original_mutation_is_rejected_after_sealing(epoch):
    primary, _, _, _ = seal(epoch)
    sidecar = mixed.read(epoch['sidecar'])
    sidecar['reason'] = 'A changed note must not mutate the sealed quarantine.'
    write_json(epoch['sidecar'], sidecar)
    with pytest.raises(ValueError, match='sidecar changed'):
        mixed.primary(epoch['root'], epoch['eligibility'], primary)
    sidecar.pop('reason')
    write_json(epoch['sidecar'], sidecar)
    original = epoch['paths'][epoch['candidate']]
    original.write_bytes(original.read_bytes() + b'\n')
    with pytest.raises(ValueError, match='primary bytes changed'):
        mixed.primary(epoch['root'], epoch['eligibility'], primary)
