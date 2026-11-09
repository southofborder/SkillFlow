"""Truthful mixed execution/source-grade results; no synthetic assistant labels.

Machine absence rows remain execution facts. Available model content requires a
fresh assistant grade and independently selected rechecks. The analysis-only
prospective cohort cannot establish a contemporaneous method advantage.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from . import exploratory_grading as grading
from . import exploratory_results as results
from .assessment import second_review_sample
from .protocol import SEED, sha256, utc_now, write_json
from .grading_quarantine import canonical_sidecar, validate_quarantined_attempt

SCHEMA = 'skillflow-mixed-execution-assistant-results-v1'


def read(path):
    return results._read(path)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eligibility_rows(root, mapping):
    """Deterministic saved-execution projection; no candidate semantics read."""
    run = Path(read(root / 'private-map.json')['source_run'])
    rows = {}
    for candidate, item in mapping.items():
        workflow = run / 'workflows' / item['workflow_id']
        requests = list(workflow.glob('requests/q*'))
        visible = [p.relative_to(run).as_posix() for request in requests
                   for p in [request / 'answer.txt'] if p.is_file() and p.stat().st_size > 0]
        rows[candidate] = {'workflow_id': item['workflow_id'], 'source_grade_required': bool(visible),
            'model_visible_answer_files': visible, 'request_directories': len(requests),
            'terminal_status': read(workflow / 'result.json')['status'],
            'provenance': 'fresh_assistant_source_grade_required' if visible else
                          'mechanical_execution_absence_not_assistant_semantic_grade',
            'semantic_judgment_from_absence': None,
            'mechanical_planned_endpoint_judgment': None if visible else 'workflow_failure'}
    return rows


def eligibility(grading_dir, out_path):
    root, mapping, _ = results._context(grading_dir)
    rows = eligibility_rows(root, mapping)
    value = {'schema_version': SCHEMA, 'kind': 'eligibility', 'created_at': utc_now(),
        **results._binding(root), 'planned_results': 264, 'model_calls': 0,
        'original_all264_fresh_assistant_requirement_fulfilled': False,
        'human_verified': False, 'actual_human_review_work_seconds': None, 'rows': rows,
        'scope': 'Absence proves no saved model audit and planned output unavailability, not semantic error or intrinsic method inability. Local diagnostic JSON does not replace a model answer.'}
    write_json(out_path, value, immutable=True)
    return value


def load_eligibility(root, path):
    value = read(path)
    mapping = {x['candidate_id']: x for x in read(root / 'private-map.json')['assignments']}
    require(value.get('schema_version') == SCHEMA and value.get('kind') == 'eligibility'
            and set(value['rows']) == set(mapping)
            and value['rows'] == eligibility_rows(root, mapping)
            and value.get('planned_results') == 264 and value.get('model_calls') == 0
            and value.get('human_verified') is False
            and value.get('actual_human_review_work_seconds') is None
            and all(value.get(k) == v for k, v in results._binding(root).items()),
            'Eligibility must bind every fixed logical identity and packet epoch')
    return value


def seal_primary(grading_dir, eligibility_path, submission_paths, out_path, *, origin_grading_dirs=None,
                 quarantine_sidecar_paths=()):
    root, mapping, _ = results._context(grading_dir)
    projection = load_eligibility(root, eligibility_path)
    expected = {c for c, row in projection['rows'].items() if row['source_grade_required']}
    records, quarantined = {}, {}
    for path in quarantine_sidecar_paths:
        record = validate_quarantined_attempt(root, path, mapping=mapping)
        candidate = record['candidate_id']
        require(candidate in expected and candidate not in quarantined,
                'A quarantined attempt is duplicated or substitutes for mechanical absence')
        quarantined[candidate] = record
    origins = origin_grading_dirs or {}
    for path in submission_paths:
        candidate = read(path).get('candidate_id')
        require(candidate in expected, 'A primary attempt does not identify available target content')
        require(candidate not in quarantined and not canonical_sidecar(root, candidate).exists()
                and not Path(path).with_name(Path(path).stem + '.grading-defect.json').exists(),
                'A quarantined scoring attempt cannot be imported as a valid primary')
        if candidate in origins:
            from .grade_lineage import validate_origin_primary
            record = validate_origin_primary(root, path, origins[candidate])
        else:
            record = results._grade_record(root, path, role='primary')
        candidate = record['validated_grade']['candidate_id']
        require(candidate in expected and candidate not in records,
                'A primary grade is duplicated or substitutes for mechanical absence')
        records[candidate] = record
    require(set(records) | set(quarantined) == expected,
            'Account for every available-content primary disposition before final primary sealing')
    require(set(origins).issubset(records), 'Every explicitly supplied original grade must identify an actual final primary')
    # A fresh batch may contain different cases, never two outputs of one case.
    agent_cases = set()
    for candidate in sorted(set(records) | set(quarantined)):
        grade = records[candidate]['validated_grade'] if candidate in records else quarantined[candidate]
        require(grade['agent_id'] == grade['reviewer_id'],
                'Record the actual canonical assistant identity in both identity fields')
        key = (grade['agent_id'], mapping[candidate]['case_id'])
        require(key not in agent_cases, 'One primary agent saw multiple outputs of the same source case')
        agent_cases.add(key)
    value = {'schema_version': SCHEMA, 'kind': 'primary_seal', 'created_at': utc_now(),
        **results._binding(root), 'eligibility_sha256': sha256(eligibility_path),
        'planned_results': 264, 'assistant_primary_results': len(records),
        'source_grade_required_results': len(expected), 'source_grade_attempt_results': len(records) + len(quarantined),
        'quarantined_source_grade_attempt_results': len(quarantined),
        'missing_valid_primary_results': len(quarantined),
        'mechanical_absence_results': 264 - len(expected), 'records': records,
        'quarantined_attempts': quarantined,
        'original_all264_fresh_assistant_requirement_fulfilled': len(records) == 264,
        'human_verified': False, 'actual_human_review_work_seconds': None, 'model_calls': 0}
    write_json(out_path, value, immutable=True)
    return value


def primary(root, eligibility_path, primary_path):
    projection = load_eligibility(root, eligibility_path)
    value = read(primary_path)
    expected = {c for c, row in projection['rows'].items() if row['source_grade_required']}
    quarantined = value.get('quarantined_attempts', {})
    require(value.get('schema_version') == SCHEMA and value.get('kind') == 'primary_seal'
            and value.get('eligibility_sha256') == sha256(eligibility_path)
            and value.get('planned_results') == 264 and value.get('model_calls') == 0
            and value.get('human_verified') is False
            and value.get('actual_human_review_work_seconds') is None
            and not set(value['records']).intersection(quarantined)
            and set(value['records']) | set(quarantined) == expected
            and all(value.get(k) == v for k, v in results._binding(root).items()),
            'The source-primary seal differs from its complete available-content cohort')
    for candidate, item in value['records'].items():
        require(not canonical_sidecar(root, candidate).exists()
                and not Path(item['path']).with_name(Path(item['path']).stem + '.grading-defect.json').exists(),
                'A quarantined scoring attempt cannot remain a valid primary')
        if item.get('grade_origin'):
            from .grade_lineage import validate_origin_primary
            checked = validate_origin_primary(root, item['path'], item['grade_origin']['origin_grading_workspace'])
        else:
            checked = results._grade_record(root, item['path'], role='primary')
        require(checked == item,
                'A frozen mixed-cohort primary changed')
    for candidate, item in quarantined.items():
        checked = validate_quarantined_attempt(root, item['sidecar_path'], mapping={x['candidate_id']: x for x in
            read(root / 'private-map.json')['assignments']}, expected_sidecar_sha256=item['sidecar_sha256'])
        require(candidate == checked['candidate_id'] and checked == item,
                'A frozen quarantined scoring attempt changed')
    require(value.get('assistant_primary_results') == len(value['records'])
            and value.get('mechanical_absence_results') == 264 - len(expected)
            and value.get('quarantined_source_grade_attempt_results', len(quarantined)) == len(quarantined)
            and value.get('source_grade_attempt_results', len(expected)) == len(expected)
            and value.get('source_grade_required_results', len(expected)) == len(expected)
            and value.get('missing_valid_primary_results', len(quarantined)) == len(quarantined)
            and value.get('original_all264_fresh_assistant_requirement_fulfilled') == (len(value['records']) == 264),
            'Mixed source-grading disposition counts changed')
    return projection, value


def selected_rechecks(records, quarantined_attempts=None):
    selected = set(second_review_sample([r['validated_grade'] for r in records.values()], seed=SEED))
    for candidate, record in records.items():
        if (results._disputes(record['validated_grade']) or not record['protocol_eligible']
                or record['execution_status'] in results.EXECUTION_FAILURES):
            selected.add(candidate)
    return selected | set(quarantined_attempts or {})


def primary_agent(sealed, candidate):
    if candidate in sealed['records']:
        return sealed['records'][candidate]['validated_grade']['agent_id']
    return sealed['quarantined_attempts'][candidate]['agent_id']


def prepare_secondaries(grading_dir, eligibility_path, primary_path, out_path):
    root, mapping, _ = results._context(grading_dir)
    projection, sealed = primary(root, eligibility_path, primary_path)
    rechecks = selected_rechecks(sealed['records'], sealed.get('quarantined_attempts'))
    chains = {c for c, item in mapping.items() if item['chain_secondary_required']
              and projection['rows'][c]['source_grade_required']}
    rows = []
    for kind, selected in [('primary_recheck', rechecks), ('chain_secondary', chains)]:
        for candidate in sorted(selected):
            rows.append({'candidate_id': candidate, 'assignment_kind': kind,
                'packet': mapping[candidate]['packet'], 'common_rules': 'common-rules',
                'excluded_agent_ids': [primary_agent(sealed, candidate)]})
    value = {'schema_version': SCHEMA, 'kind': 'secondary_assignments', 'created_at': utc_now(),
        **results._binding(root), 'eligibility_sha256': sha256(eligibility_path),
        'primary_seal_sha256': sha256(primary_path), 'seed': SEED, 'assignments': rows,
        'mechanical_absence_recheck_policy': 'Zero-call independent execution-evidence verification; no fabricated semantic grades or model calls merely to prove absence.',
        'planned_chain_outcomes': 168, 'available_content_chain_assignments': len(chains),
        'chain_absence_outcomes': 168 - len(chains), 'model_calls': 0}
    write_json(out_path, value, immutable=True)
    return value


def reconcile_record(original, secondary, required):
    grade = original['validated_grade']
    other = secondary['validated_grade'] if secondary else None
    issues = list(results._disputes(grade))
    if required and other is None: issues.append('mandatory_primary_recheck_missing')
    if other:
        issues.extend('secondary_' + x for x in results._disputes(other))
        if grade['judgment'] != other['judgment']: issues.append('coarse_judgment_disagreement')
        if sorted((x['check_id'], x['status']) for x in grade['check_results']) != sorted(
                (x['check_id'], x['status']) for x in other['check_results']):
            issues.append('mandatory_check_disagreement')
    detail = results._primary_detail(grade, other)
    issues.extend(detail['metric_disputes'])
    content = 'indeterminate' if issues else grade['judgment']
    # Delivery failure is known independently of an unresolved content judgment.
    endpoint = 'workflow_failure' if not original['protocol_eligible'] else content
    return {'judgment': endpoint, 'content_judgment': content,
            'primary_disputes': sorted(set(issues)), 'metric_disputes': sorted(set(issues)),
            'adjudicated_grade': None if issues else detail['adjudicated_grade'],
            'assistant_adjudication_complete': not issues,
            'execution_endpoint_known': endpoint in results.KNOWN}


def quarantined_resolution(attempt, secondary, required=True):
    """A recheck is diagnostic evidence; it cannot supply the missing primary."""
    issues = ['primary_scoring_attempt_quarantined', 'valid_primary_missing']
    if required and secondary is None:
        issues.append('mandatory_primary_recheck_missing')
    if secondary:
        issues.extend('secondary_' + item for item in results._disputes(secondary['validated_grade']))
    return {'judgment': 'indeterminate', 'content_judgment': 'indeterminate',
        'primary_disputes': sorted(set(issues)), 'metric_disputes': sorted(set(issues)),
        'adjudicated_grade': None, 'assistant_adjudication_complete': False,
        'execution_endpoint_known': False}


def frozen_protocol_eligible(root, item):
    """Read protocol eligibility from the sealed outcome, not the failed grader."""
    execution = read(root / item['packet'] / 'execution.json')
    states = execution.get('request_states', [])
    return bool(states) and all(r.get('accepted') is True and r.get('protocol_status') == 'conformant'
        and r.get('violation_count') == 0
        and all(r.get(k) is True for k in ('configuration_verified', 'provider_verified', 'completed'))
        for r in states)


def block_resource_inference(value):
    """Preserve observed costs; suppress every nested inferential decision."""
    if isinstance(value, list):
        return [block_resource_inference(x) for x in value]
    if not isinstance(value, dict):
        return value
    out = {key: block_resource_inference(item) for key, item in value.items()}
    flags = {'quality_noninferiority_supported', 'efficiency_supported'}
    if flags.intersection(out):
        for key in flags: out[key] = False
        out['status'] = 'blocked_stopped_paused_skillflow_and_prospective_direct_epoch'
        out['inference_blocked_reason'] = 'No contemporaneous complete three-method epoch or all264 fresh semantic grades. Observed resource costs remain descriptive.'
        for key in ('quality_difference', 'quality_bounds', 'resource_ratio_upper_bound'):
            if key in out: out[key] = None
    if 'practical_advantage_method' in out: out['practical_advantage_method'] = None
    return out


def apply_chain_source_dispute(resolved, chain_grade, *, protocol_eligible):
    """Only a source/reference correction affects the common primary verdict.

    Missing or disputed chain structure alone retains its separate metric gate.
    """
    if not chain_grade or not chain_grade.get('reference_correction_proposals'):
        return resolved
    issues = sorted(set(resolved['primary_disputes']) | {'chain_source_reference_correction_proposed'})
    return {**resolved, 'judgment': 'indeterminate' if protocol_eligible else 'workflow_failure',
            'content_judgment': 'indeterminate', 'primary_disputes': issues, 'metric_disputes': issues,
            'adjudicated_grade': None, 'assistant_adjudication_complete': False,
            'execution_endpoint_known': not protocol_eligible}


def aggregate(grading_dir, eligibility_path, primary_path, assignments_path, *,
              secondary_paths=(), chain_paths=(), costs=None, bootstrap_samples=10000):
    root, mapping, packet = results._context(grading_dir)
    projection, sealed = primary(root, eligibility_path, primary_path)
    assignments = read(assignments_path)
    quarantined = sealed.get('quarantined_attempts', {})
    rechecks = selected_rechecks(sealed['records'], quarantined)
    chains_expected = {c for c, item in mapping.items() if item['chain_secondary_required']
                       and projection['rows'][c]['source_grade_required']}
    expected = {('primary_recheck', c) for c in rechecks} | {('chain_secondary', c) for c in chains_expected}
    require(assignments.get('schema_version') == SCHEMA
            and assignments.get('primary_seal_sha256') == sha256(primary_path)
            and assignments.get('eligibility_sha256') == sha256(eligibility_path)
            and assignments.get('seed') == SEED
            and {(x['assignment_kind'], x['candidate_id']) for x in assignments['assignments']} == expected
            and len(assignments['assignments']) == len(expected)
            and all(x.get('excluded_agent_ids') == [primary_agent(sealed, x['candidate_id'])]
                    for x in assignments['assignments']), 'Secondary assignment cohort changed')
    secondary, chains = {}, {}
    for paths, destination, kind in [(secondary_paths, secondary, 'primary_recheck'),
                                      (chain_paths, chains, 'chain_secondary')]:
        for path in paths:
            record = (results._validate_chain_only(root, path, mapping) if kind == 'chain_secondary'
                      else results._grade_record(root, path, role='secondary'))
            grade = record['validated_grade']; candidate = grade['candidate_id']
            require((kind, candidate) in expected and candidate not in destination
                    and grade['agent_id'] == grade['reviewer_id']
                    and grade['agent_id'] != primary_agent(sealed, candidate),
                    'Duplicate, unassigned or nonindependent secondary grade')
            destination[candidate] = record
    cases, _ = results._cases(root, mapping, None)
    rows, references, errors, disputes = [], {}, [], []
    for candidate, item in sorted(mapping.items()):
        original, recheck = sealed['records'].get(candidate), secondary.get(candidate)
        attempt = quarantined.get(candidate)
        if original:
            resolved = reconcile_record(original, recheck, candidate in rechecks)
            provenance = 'fresh_assistant_source_grades'
        elif attempt:
            resolved = quarantined_resolution(attempt, recheck, candidate in rechecks)
            provenance = 'quarantined_unusable_source_grade_attempt_not_target_failure'
        else:
            resolved = {'judgment': 'workflow_failure', 'content_judgment': 'not_semantically_graded',
                'primary_disputes': [], 'metric_disputes': [], 'adjudicated_grade': None,
                'assistant_adjudication_complete': False, 'execution_endpoint_known': True}
            provenance = 'mechanical_execution_absence_not_assistant_semantic_grade'
        chain_grade = chains.get(candidate, {}).get('validated_grade')
        protocol_eligible = (original['protocol_eligible'] if original else
                             frozen_protocol_eligible(root, item) if attempt else False)
        resolved = apply_chain_source_dispute(resolved, chain_grade,
            protocol_eligible=protocol_eligible)
        if attempt:
            # Even a diagnostic recheck or chain label cannot rescue the missing
            # valid primary or attribute a scorer failure to target execution.
            resolved.update(judgment='indeterminate', content_judgment='indeterminate',
                            execution_endpoint_known=False, assistant_adjudication_complete=False,
                            adjudicated_grade=None)
        chain = chain_grade.get('chain_assessment') if chain_grade else None
        chain_issues = []
        if item['chain_secondary_required'] and chain is None: chain_issues.append('chain_secondary_unavailable_or_missing')
        if chain_grade and chain_grade.get('reference_correction_proposals'): chain_issues.append('chain_source_reference_dispute')
        if chain and any(x['status'] == 'disputed' for key in ('completeness', 'consistency') for x in chain[key]):
            chain_issues.append('chain_metric_dispute')
        row = {**item, **resolved, 'source_cluster': cases[item['case_id']]['source_cluster'],
            'provenance': provenance, 'mandatory_primary_recheck': candidate in rechecks,
            'protocol_eligible': protocol_eligible,
            'execution_status': projection['rows'][candidate]['terminal_status'],
            'primary_attempt_quarantined': bool(attempt),
            'quarantined_attempt': attempt,
            'chain_assessment': chain if not chain_issues else None,
            'chain_disputes': chain_issues, 'chain_assessment_complete': bool(chain) and not chain_issues,
            'assistant_agents': {role: record['validated_grade']['agent_id'] for role, record in
                [('primary', original), ('primary_recheck', recheck), ('chain_secondary', chains.get(candidate))] if record}}
        if attempt:
            row['assistant_agents']['quarantined_primary_attempt'] = attempt['agent_id']
        rows.append(row)
        references.setdefault(item['case_id'], read(root / item['packet'] / 'reference.json'))
        if row['primary_disputes'] or chain_issues:
            disputes.append({'candidate_id': candidate, 'workflow_id': item['workflow_id'],
                'primary': row['primary_disputes'], 'chain': chain_issues,
                'reference_correction_proposals': {role: record['validated_grade'].get('reference_correction_proposals', [])
                    for role, record in [('primary', original), ('primary_recheck', recheck), ('chain_secondary', chains.get(candidate))] if record}})
        for role, record in [('primary', original), ('primary_recheck', recheck)]:
            if not record: continue
            grade = record['validated_grade']
            for group in ('error_records', 'findings'):
                errors.extend({'candidate_id': candidate, 'workflow_id': item['workflow_id'],
                    'role': role, 'record_kind': group, 'record': x} for x in grade.get(group, []))
            for group, field, bad in [('check_results', 'status', {'fail'}), ('claim_units', 'assessment', {'unsupported'}),
                    ('receiving_point_coverage', 'status', {'missed'}), ('reduction_assessments', 'status', {'missing', 'harmful'})]:
                errors.extend({'candidate_id': candidate, 'workflow_id': item['workflow_id'],
                    'role': role, 'record_kind': group, 'record': x} for x in grade.get(group, []) if x.get(field) in bad)
    case_rows, groups, _ = results._comparisons(rows, cases, False, bootstrap_samples)
    resource_rows = [{**row, 'assistant_adjudication_complete': False} for row in rows]
    resources = block_resource_inference(results._resource_comparisons(resource_rows, cases, costs,
        bootstrap_samples, packet['source_output_freeze_sha256']))
    return {'schema_version': SCHEMA, 'created_at': utc_now(), 'evidence_level': grading.EVIDENCE_LEVEL,
        'grading_workspace': str(root), **results._binding(root),
        'eligibility_path': str(Path(eligibility_path).resolve()), 'eligibility_sha256': sha256(eligibility_path),
        'primary_seal_path': str(Path(primary_path).resolve()), 'primary_seal_sha256': sha256(primary_path),
        'secondary_assignments_path': str(Path(assignments_path).resolve()), 'secondary_assignments_sha256': sha256(assignments_path),
        'model_calls': 0, 'planned_results': 264, 'planned_main': 216, 'planned_reviews': 48,
        'planned_cases': 24, 'source_clusters': 22, 'all_planned_in_denominator': True,
        'assistant_primary_results': len(sealed['records']),
        'source_grade_required_results': sum(x['source_grade_required'] for x in projection['rows'].values()),
        'source_grade_attempt_results': len(sealed['records']) + len(quarantined),
        'quarantined_source_grade_attempt_results': len(quarantined),
        'missing_valid_primary_results': len(quarantined),
        'quarantined_attempts': quarantined,
        'mechanical_absence_results': sum(not x['source_grade_required'] for x in projection['rows'].values()),
        'original_all264_fresh_assistant_requirement_fulfilled': len(sealed['records']) == 264,
        'bounds': results._bounds(rows), 'main_bounds': results._bounds([x for x in rows if x['kind'] == 'main']),
        'review_bounds': results._bounds([x for x in rows if x['kind'] == 'review']),
        'groups': groups, 'case_results': case_rows, 'rows': rows,
        'mandatory_primary_rechecks': sorted(rechecks), 'missing_mandatory_primary_rechecks': sorted(rechecks - set(secondary)),
        'semantic_metrics': results._semantic(rows, references), 'stability': results._stability(rows),
        'individual_errors': errors, 'individual_disputes': disputes,
        'chain_status': {'planned': 168, 'available_content_assignments': len(chains_expected),
            'complete': sum(x['chain_assessment_complete'] for x in rows), 'missing_or_unavailable': 168 - sum(x['chain_assessment_complete'] for x in rows)},
        'resources': resources, 'primary_comparisons': [], 'fixed_review_comparisons': [],
        'inferential_status': 'blocked_stopped_paused_skillflow_and_prospective_direct_epoch',
        'method_advantage_demonstrated': False,
        'intrinsic_skillflow_advantage': 'unknown',
        'statistical_guard': 'No p-value or advantage decision from available-only or mechanically substituted semantic grades. Preserve24 equal cases/22clusters, repeat means, main2-testHolm family,10ppaccuracy threshold,5ppqualityNI then20percent resource threshold and20-direction efficiency family for any future eligible inference.',
        'human_reference_confirmation': 'pending', 'actual_human_scoring': 'pending',
        'actual_human_review_work_seconds': None,
        'limitations': ['Machine output absence is not an assistant semantic grade or proof of intrinsic method inability.',
            'A quarantined scorer attempt is unscored evidence, not a valid primary, a reference correction or target failure; fresh rechecks cannot substitute for its missing valid primary.',
            'All available-content primary grades are fresh and frozen before independent recheck selection; unresolved source/reference or detailed disagreements remain unknown.',
            'The stopped original SkillFlow arm and prospective direct epoch do not complete the original contemporaneous three-method comparison.',
            'Assistant references and judgments are not human gold. Reference changes require a preserved new version and a uniform fresh grading epoch, without target regeneration.']}


def write_reports(report, out_dir):
    require(report.get('schema_version') == SCHEMA and report.get('planned_results') == 264,
            'Only the full fixed logical denominator can be published')
    root, _, _ = results._context(report['grading_workspace'])
    require(all(report.get(k) == v for k, v in results._binding(root).items()),
            'Report packet binding changed')
    for path_key, hash_key in [('eligibility_path', 'eligibility_sha256'),
            ('primary_seal_path', 'primary_seal_sha256'),
            ('secondary_assignments_path', 'secondary_assignments_sha256')]:
        require(sha256(report[path_key]) == report[hash_key], 'A source grading seal changed')
    out = Path(out_dir).resolve()
    results._output_location(root, out)
    require(not out.exists(), 'Preserve earlier result versions; use a fresh report directory')
    out.mkdir(parents=True)
    write_json(out / 'results.json', report, immutable=True)
    for name, value in [('semantic-metrics', report['semantic_metrics']),
            ('individual-errors', report['individual_errors']), ('individual-disputes', report['individual_disputes']),
            ('quality-bounds', {'all': report['bounds'], 'main': report['main_bounds'], 'review': report['review_bounds'], 'groups': report['groups']})]:
        write_json(out / (name + '.json'), value, immutable=True)
    for name, rows in [('outcomes', report['rows']), ('case-results', report['case_results']),
            ('errors', report['individual_errors']), ('disputes', report['individual_disputes']),
            ('stability', report['stability']['rows']), ('resources', report['resources']['comparisons'])]:
        fields = sorted({key for row in rows for key in row})
        with (out / (name + '.csv')).open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (dict, list))
                    else 'null' if v is None else v for k, v in row.items()})
    write_json(out / 'report-freeze.json', {'schema_version': SCHEMA, 'created_at': utc_now(),
        'primary_seal_sha256': report['primary_seal_sha256'], 'packet_freeze_sha256': report['packet_freeze_sha256'],
        'all_planned_in_denominator': True, 'files': {p.name: sha256(p) for p in out.iterdir() if p.is_file()},
        'model_calls': 0, 'human_verified': False}, immutable=True)
