"""One complete invented264-row mixed epoch; never read research outputs."""
from copy import deepcopy
import shutil

import pytest

from tools.doe.real_comparison import exploratory_grading as grading
from tools.doe.real_comparison import mixed_results as mixed
from tools.doe.real_comparison.protocol import sha256, write_json
from tests.doe.test_exploratory_grading import closed_packets, _pass, _seal


def test_complete_mixed_epoch_keeps_absence_machine_and_blocks_advantage(closed_packets, tmp_path):
    donor, _ = closed_packets
    run, root = tmp_path / 'invented-generation', tmp_path / 'invented-grading'
    shutil.copytree(donor, run)
    keep = {'synthetic-00_skillflow_1', 'synthetic-01_chain_1'}
    schedule = grading.read(run / 'schedule.json')
    for item in schedule['main'] + schedule['reviews']:
        directory = run / 'workflows' / item['workflow_id']
        if item['workflow_id'] not in keep:
            request = (directory / 'requests').resolve()
            assert request.is_relative_to((run / 'workflows').resolve())
            shutil.rmtree(request)
            (directory / 'answer.txt').unlink()
            write_json(directory / 'result.json', {'status': 'protocol_aborted'})
    frozen = grading.read(run / 'freeze.json')
    selected = []
    for i in range(24):
        case = f'synthetic-{i:02d}'
        source_hash = sha256(run / 'cases' / case / 'source/skill.txt')
        path = run / 'references' / (case + '.json')
        reference = grading.read(path)
        reference['source_sha256'] = source_hash
        write_json(path, reference)
        frozen['files'][path.relative_to(run).as_posix()] = sha256(path)
        selected.append({'case_id': case, 'source_cluster': 'cluster-' + str(i // 2 if i < 4 else i - 2),
                         'source_sha256': source_hash})
    write_json(run / 'selection.json', {'selected': selected})
    frozen['files']['selection.json'] = sha256(run / 'selection.json')
    write_json(run / 'freeze.json', frozen)
    write_json(run / 'output-freeze.json', {'schema_version': grading.OUTPUT_SCHEMA,
        'planned_outputs': 264, 'files': {'workflows/' + k: v for k, v in _seal(run / 'workflows').items()}})
    grading.prepare_packets(run, root)
    projection_path = root / 'eligibility.json'
    projection = mixed.eligibility(root, projection_path)
    assert len(projection['rows']) == 264
    assert sum(x['source_grade_required'] for x in projection['rows'].values()) == 2
    assert all(x['semantic_judgment_from_absence'] is None for x in projection['rows'].values())
    tampered = deepcopy(projection)
    visible_id = next(c for c, row in tampered['rows'].items() if row['source_grade_required'])
    tampered['rows'][visible_id]['source_grade_required'] = False
    write_json(projection_path, tampered)
    with pytest.raises(ValueError): mixed.load_eligibility(root, projection_path)
    write_json(projection_path, projection)
    private = {x['workflow_id']: x for x in grading.read(root / 'private-map.json')['assignments']}
    paths = []
    for wid in sorted(keep):
        item = private[wid]
        grade = _pass(root / item['packet'])
        grade.update(agent_id='synthetic-primary-' + wid, reviewer_id='synthetic-primary-' + wid)
        path = root / 'submissions' / (item['candidate_id'] + '.primary.json')
        write_json(path, grade)
        paths.append(path)
    primary_path = root / 'primary-seal.json'
    sealed = mixed.seal_primary(root, projection_path, paths, primary_path)
    assert sealed['assistant_primary_results'] == 2 and sealed['mechanical_absence_results'] == 262
    assert sealed['original_all264_fresh_assistant_requirement_fulfilled'] is False
    assignments_path = root / 'secondary-assignments.json'
    assignments = mixed.prepare_secondaries(root, projection_path, primary_path, assignments_path)
    assert all(x['candidate_id'] in sealed['records'] for x in assignments['assignments'])
    secondary = []
    for row in assignments['assignments']:
        if row['assignment_kind'] != 'primary_recheck': continue
        grade = deepcopy(sealed['records'][row['candidate_id']]['validated_grade'])
        grade.update(agent_id='synthetic-independent-' + row['candidate_id'],
                     reviewer_id='synthetic-independent-' + row['candidate_id'], scoring_role='secondary')
        path = root / 'submissions' / (row['candidate_id'] + '.secondary.json')
        write_json(path, grade)
        secondary.append(path)
    report = mixed.aggregate(root, projection_path, primary_path, assignments_path, secondary_paths=secondary,
                             bootstrap_samples=3)
    assert report['bounds']['planned'] == 264 and report['bounds']['known_fail'] == 262
    assert report['bounds']['known_pass'] == 2 and report['bounds']['unknown'] == 0
    assert report['method_advantage_demonstrated'] is False and report['intrinsic_skillflow_advantage'] == 'unknown'
    assert report['primary_comparisons'] == [] and report['planned_cases'] == 24 and report['source_clusters'] == 22
    assert report['actual_human_review_work_seconds'] is None
    assert len(report['resources']['comparisons']) == 20
    absent_ids = {c for c, row in projection['rows'].items() if not row['source_grade_required']}
    semantics = {x['candidate_id']: x for x in report['semantic_metrics']['rows']}
    assert all(semantics[c]['tp'] is None and semantics[c]['fn'] is None and semantics[c]['fp'] is None for c in absent_ids)
    out = tmp_path / 'invented-results'
    mixed.write_reports(report, out)
    assert (out / 'results.json').exists() and (out / 'report-freeze.json').exists()
    with pytest.raises(ValueError): mixed.write_reports(report, out)

    # A fresh final grade of an already closed original can be preserved when
    # its complete packet bytes are unchanged in a later logical assembly.
    # Its original output-seal hash is retained, never rewritten to the new one.
    assembled, logical_grading = tmp_path / 'invented-logical', tmp_path / 'invented-logical-grading'
    shutil.copytree(run, assembled)
    lineage = {'analysis_only': True, 'fixed_logical_outputs': 264, 'donor_run': str(run),
        'donor_output_freeze_sha256': sha256(run / 'output-freeze.json'),
        'direct_run': str(tmp_path / 'unused-invented-direct'),
        'workflow_origins': [{'workflow_id': x['workflow_id'], 'source_run': str(run),
            'source_result_sha256': sha256(run / 'workflows' / x['workflow_id'] / 'result.json')}
            for x in schedule['main'] + schedule['reviews']]}
    write_json(assembled / 'logical-cohort-lineage.json', lineage)
    assembled_input = grading.read(assembled / 'freeze.json')
    assembled_input['files']['logical-cohort-lineage.json'] = sha256(assembled / 'logical-cohort-lineage.json')
    write_json(assembled / 'freeze.json', assembled_input)
    assembled_output = grading.read(assembled / 'output-freeze.json')
    assembled_output['analysis_only'] = True
    write_json(assembled / 'output-freeze.json', assembled_output)
    grading.prepare_packets(assembled, logical_grading)
    logical_eligibility = logical_grading / 'eligibility.json'
    mixed.eligibility(logical_grading, logical_eligibility)
    native = private['synthetic-00_skillflow_1']
    original_path = next(p for p in paths if grading.read(p)['candidate_id'] == native['candidate_id'])
    raw_hash = sha256(original_path)
    logical_paths = [original_path]
    chain = private['synthetic-01_chain_1']
    fresh = _pass(logical_grading / chain['packet'])
    fresh.update(agent_id='synthetic-new-epoch-primary', reviewer_id='synthetic-new-epoch-primary')
    fresh_path = logical_grading / 'submissions/new-chain.primary.json'
    write_json(fresh_path, fresh)
    logical_paths.append(fresh_path)
    logical_primary = logical_grading / 'primary-seal.json'
    imported = mixed.seal_primary(logical_grading, logical_eligibility, logical_paths, logical_primary,
        origin_grading_dirs={native['candidate_id']: root})
    assert sha256(original_path) == raw_hash
    old_grade = imported['records'][native['candidate_id']]['validated_grade']
    assert old_grade['output_freeze_sha256'] == sha256(run / 'output-freeze.json')
    assert old_grade['output_freeze_sha256'] != sha256(assembled / 'output-freeze.json')
    assert imported['records'][native['candidate_id']]['grade_origin']['raw_grade_rewritten'] is False
    mixed.primary(logical_grading, logical_eligibility, logical_primary)
