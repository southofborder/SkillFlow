"""Validate preserved scorer-defect sidecars without importing their labels.

A mechanically valid submission can still be an unusable scoring attempt. This
metadata validator binds the original attempt and its explicit quarantine; it
does not read source/candidate semantics or create a replacement primary grade.
"""
from pathlib import Path

from . import exploratory_grading as grading
from . import exploratory_results as results
from .protocol import sha256

SCHEMA = 'skillflow-assistant-grading-defect-v1'
RECORD_SCHEMA = 'skillflow-quarantined-source-grade-attempt-v1'
IDENTITY_FIELDS = ('candidate_sha256', 'reference_sha256', 'source_sha256',
                   'source_bundle_sha256', 'output_freeze_sha256')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def submission_file(root, path):
    raw = Path(path)
    path = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    require(path.is_relative_to(root / 'submissions') and path.is_file()
            and not raw.is_symlink()
            and not any(p.is_symlink() for p in path.parents if p.is_relative_to(root)),
            'A quarantined grading file must remain inside its original submissions directory')
    return path


def canonical_sidecar(root, candidate):
    return root / 'submissions' / (candidate + '.primary.grading-defect.json')


def validate_quarantined_attempt(grading_dir, sidecar_path, *, mapping=None,
                                 expected_sidecar_sha256=None):
    """Return only unscored metadata; never return a validated semantic grade.

    With no mapping, verify the closed packet epoch first. Coordinators may
    supply their already verified mapping to avoid repeating full tree hashes.
    """
    root = Path(grading_dir).resolve()
    if mapping is None:
        root, mapping, _ = results._context(root)
    path = submission_file(root, sidecar_path)
    digest = sha256(path)
    require(expected_sidecar_sha256 is None or digest == expected_sidecar_sha256,
            'A preserved scorer-defect sidecar changed')
    sidecar = results._read(path)
    candidate = sidecar.get('candidate_id')
    require(candidate in mapping and sidecar.get('schema_version') == SCHEMA
            and sidecar.get('issue_kind') == 'scorer_label_defect'
            and sidecar.get('saved_primary_bytes_preserved') is True
            and sidecar.get('not_target_protocol_failure') is True
            and sidecar.get('not_reference_change') is True
            and sidecar.get('semantic_replacement_performed') is False
            and sidecar.get('human_verified') is False
            and sidecar.get('actual_human_review_work_seconds') is None,
            'A quarantine must explicitly identify unusable assistant scoring, not a changed target or reference')
    agent = sidecar.get('agent_id')
    require(isinstance(agent, str) and bool(agent.strip()) and agent == sidecar.get('reviewer_id')
            and isinstance(sidecar.get('CODEX_THREAD_ID'), str) and bool(sidecar['CODEX_THREAD_ID'].strip()),
            'A quarantine must preserve the original canonical scorer and actual thread identity')
    original = submission_file(root, sidecar.get('submitted_primary_path', ''))
    original_hash = sha256(original)
    require(original_hash == sidecar.get('submitted_primary_sha256'),
            'The original quarantined primary bytes changed')
    grade = results._read(original)
    template = results._read(root / mapping[candidate]['packet'] / 'grade.template.json')
    require(grade.get('schema_version') == grading.SCHEMA
            and grade.get('evidence_level') == grading.EVIDENCE_LEVEL
            and grade.get('candidate_id') == candidate and grade.get('scoring_role') == 'primary'
            and grade.get('agent_id') == grade.get('reviewer_id') == agent
            and grade.get('human_verified') is False
            and grade.get('actual_human_review_work_seconds') is None
            and grade.get('chain_assessment') is None
            and template.get('candidate_id') == candidate
            and all(grade.get(k) == template.get(k) for k in IDENTITY_FIELDS),
            'The quarantined attempt binds a different candidate, reference, cohort or canonical scorer')
    require(grade.get('CODEX_THREAD_ID') in (None, sidecar['CODEX_THREAD_ID']),
            'The attempt and quarantine disagree about the original thread identity')
    affected = sidecar.get('affected_records')
    fields = {'check_results': 'check_id', 'receiving_point_coverage': 'receiving_point_id',
              'reduction_assessments': 'reference_exposure_id', 'claim_units': 'claim_id',
              'error_records': 'error_id'}
    require(isinstance(affected, list) and bool(affected) and all(isinstance(x, str) for x in affected)
            and len(affected) == len(set(affected)),
            'A scorer-defect sidecar must identify distinct affected original records')
    affected_rows = []
    for item in affected:
        require(isinstance(item, str) and ':' in item, 'Invalid affected scoring-record identity')
        group, identity = item.split(':', 1)
        matches = [r for r in grade.get(group, []) if group in fields and r.get(fields[group]) == identity]
        require(group in fields and len(matches) == 1,
                'An affected scoring record is absent or ambiguous in the preserved attempt')
        affected_rows.extend(matches)
    snapshot = sidecar.get('affected_record_as_submitted')
    require(snapshot is None or snapshot in affected_rows,
            'A scorer-defect snapshot differs from the preserved original record')
    notes = sidecar.get('original_read_notes', {})
    require(isinstance(notes, dict) and notes.get('actual_reading_complete') is True,
            'Preserve the original scorer reading-completeness declaration')
    read_notes = {}
    if notes.get('read_notes_path') or notes.get('read_notes_sha256'):
        notes_path = submission_file(root, notes.get('read_notes_path', ''))
        require(sha256(notes_path) == notes.get('read_notes_sha256'),
                'The preserved original reading notes changed')
        read_notes = {'path': str(notes_path), 'sha256': notes['read_notes_sha256']}
    return {'schema_version': RECORD_SCHEMA, 'candidate_id': candidate,
        'disposition': 'quarantined_unusable_source_grade_attempt',
        'sidecar_path': str(path), 'sidecar_sha256': digest,
        'submitted_primary_path': str(original), 'submitted_primary_sha256': original_hash,
        **{k: grade.get(k) for k in IDENTITY_FIELDS},
        'agent_id': agent, 'reviewer_id': agent, 'CODEX_THREAD_ID': sidecar['CODEX_THREAD_ID'],
        'affected_records': affected, 'original_read_notes': read_notes,
        'original_reading_complete_declared': True,
        'reading_completeness_basis': 'Original scorer declaration; not independent verification of reading or semantic correctness.',
        'primary_semantic_judgment_imported': False, 'semantic_replacement_performed': False,
        'not_target_protocol_failure': True, 'not_reference_change': True,
        'human_verified': False, 'actual_human_review_work_seconds': None,
        'validation_model_calls': 0}
