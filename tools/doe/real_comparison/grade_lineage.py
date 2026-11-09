"""Preserve fresh final grades of byte-identical, separately closed originals.

No label or supplied grade hash is rewritten. Interim grades are unsupported.
Only the stopped donor's unchanged outputs can carry a final primary into the
analysis-only logical cohort, with exact packet and source-origin evidence.
"""
from pathlib import Path

from . import exploratory_grading as grading
from . import exploratory_results as results
from .protocol import sha256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compare_packet_bytes(origin, target):
    original = {p.relative_to(origin).as_posix(): sha256(p) for p in origin.rglob('*') if p.is_file()}
    assembled = {p.relative_to(target).as_posix(): sha256(p) for p in target.rglob('*') if p.is_file()}
    require(set(original) == set(assembled), 'A grade origin packet has a different complete member set')
    require(all(assembled[name] == digest for name, digest in original.items() if name != 'grade.template.json'),
            'A grade origin candidate, source, reference, artifact or execution byte differs')
    before, after = results._read(origin / 'grade.template.json'), results._read(target / 'grade.template.json')
    require({k: v for k, v in before.items() if k != 'output_freeze_sha256'}
            == {k: v for k, v in after.items() if k != 'output_freeze_sha256'},
            'Only output-cohort wrapper binding may differ between grade templates')
    return {'identical_nontemplate_files': len(original) - 1,
            'origin_template_sha256': original['grade.template.json'],
            'analysis_template_sha256': assembled['grade.template.json'],
            'only_permitted_template_difference': 'output_freeze_sha256'}


def validate_origin_primary(analysis_grading_dir, submission_path, origin_grading_dir):
    root, origin = Path(analysis_grading_dir).resolve(), Path(origin_grading_dir).resolve()
    require(root != origin, 'Use ordinary validation for grades from this same packet epoch')
    record = results._grade_record(origin, submission_path, role='primary')
    grade = record['validated_grade']
    require(grade.get('chain_assessment') is None, 'Only a fresh final common primary may use original-output lineage')
    candidate = grade['candidate_id']
    private, old_private = results._read(root / 'private-map.json'), results._read(origin / 'private-map.json')
    mapping = {x['candidate_id']: x for x in private['assignments']}
    old_mapping = {x['candidate_id']: x for x in old_private['assignments']}
    require(candidate in mapping and candidate in old_mapping, 'The exact logical candidate must exist in both sealed epochs')
    item, old_item = mapping[candidate], old_mapping[candidate]
    require(all(item[k] == old_item[k] for k in ('workflow_id', 'case_id', 'method', 'kind', 'repeat')),
            'A grade origin identifies a different case, arm or repetition')
    run, old_run = Path(private['source_run']).resolve(), Path(old_private['source_run']).resolve()
    lineage = results._read(run / 'logical-cohort-lineage.json')
    require(lineage.get('analysis_only') is True and lineage.get('fixed_logical_outputs') == 264
            and Path(lineage['donor_run']).resolve() == old_run
            and lineage['donor_output_freeze_sha256'] == sha256(old_run / 'output-freeze.json'),
            'Only the exact closed stopped donor can supply original final grades')
    # The assembled cohort's closed lineage pins the already verified donor
    # seal. Rehash only that seal and the assigned immutable packet here; full
    # source-cohort verification is performed by the coordinator's context.
    original_seal_hash = sha256(old_run / 'output-freeze.json')
    require(grade['output_freeze_sha256'] == original_seal_hash
            == results._read(origin / 'packet-freeze.json')['source_output_freeze_sha256'],
            'The fresh original grade must bind the actual closed donor seal')
    wid = item['workflow_id']
    origin_row = next((x for x in lineage['workflow_origins'] if x['workflow_id'] == wid), None)
    require(origin_row is not None and origin_row['source_result_sha256'] == sha256(old_run / 'workflows' / wid / 'result.json')
            == sha256(run / 'workflows' / wid / 'result.json'),
            'The analysis outcome is not the unchanged closed original')
    if item['method'] != 'skillflow':
        direct = Path(lineage['direct_run']).resolve()
        require(Path(origin_row['source_run']).resolve() == direct,
                'A direct logical outcome must retain the prospective direct epoch origin')
        imported = results._read(direct / 'direct-continuation.json')['retained_original_outputs']
        require(any(x['workflow_id'] == wid and x['result_sha256'] == origin_row['source_result_sha256'] for x in imported),
                'A new prospective direct answer must never inherit an original answer grade')
    else:
        require(Path(origin_row['source_run']).resolve() == old_run,
                'A paused SkillFlow logical outcome must retain its stopped original origin')
    for name in grading.COMMON_RULES:
        require(sha256(origin / 'common-rules' / name) == sha256(root / 'common-rules' / name),
                'The source grading rules changed between closed epochs')
    proof = compare_packet_bytes(origin / old_item['packet'], root / item['packet'])
    record['grade_origin'] = {'schema_version': 'skillflow-unchanged-original-final-grade-lineage-v1',
        'origin_grading_workspace': str(origin), 'origin_source_run': str(old_run),
        'origin_output_freeze_sha256': grade['output_freeze_sha256'],
        'analysis_grading_workspace': str(root),
        'analysis_output_freeze_sha256': results._read(root / 'packet-freeze.json')['source_output_freeze_sha256'],
        'logical_lineage_sha256': sha256(run / 'logical-cohort-lineage.json'),
        'raw_grade_rewritten': False, 'interim_grade_reused': False, **proof}
    return record
