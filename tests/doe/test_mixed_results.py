"""Synthetic dispute and execution gating, with no target/reference reads."""
from copy import deepcopy

from tools.doe.real_comparison import mixed_results as mixed
from tools.doe.real_comparison.semantic_metrics import GRADING_SCHEMA_VERSION


def record(candidate='c', judgment='satisfies_reference'):
    grade = {'candidate_id': candidate, 'judgment': judgment,
        'grading_schema_version': GRADING_SCHEMA_VERSION,
        'check_results': [{'check_id': 'check', 'status': 'pass'}], 'claim_units': [],
        'receiving_point_coverage': [], 'reduction_assessments': [], 'error_records': [],
        'findings': [], 'reference_correction_proposals': [], 'chain_assessment': None}
    return {'validated_grade': grade, 'protocol_eligible': True, 'execution_status': 'complete'}


def test_required_recheck_missing_blocks_content_pass():
    result = mixed.reconcile_record(record(), None, True)
    assert result['judgment'] == 'indeterminate'
    assert result['assistant_adjudication_complete'] is False
    assert 'mandatory_primary_recheck_missing' in result['primary_disputes']


def test_matching_fresh_recheck_resolves_a_pass():
    result = mixed.reconcile_record(record(), record(), True)
    assert result['judgment'] == 'satisfies_reference'
    assert result['assistant_adjudication_complete'] is True


def test_same_coarse_label_does_not_hide_detailed_disagreement():
    second = record()
    second['validated_grade']['receiving_point_coverage'] = [{'receiving_point_id': 'r', 'status': 'missed'}]
    result = mixed.reconcile_record(record(), second, True)
    assert result['judgment'] == 'indeterminate'
    assert 'receiving_point_coverage' in result['metric_disputes']


def test_check_disagreement_alone_blocks_pass():
    second = record()
    second['validated_grade']['check_results'][0]['status'] = 'fail'
    result = mixed.reconcile_record(record(), second, True)
    assert result['judgment'] == 'indeterminate'
    assert 'mandatory_check_disagreement' in result['metric_disputes']


def test_reference_proposal_is_unknown_even_when_both_graders_agree():
    first, second = record(judgment='indeterminate'), record(judgment='indeterminate')
    for r in (first, second):
        r['validated_grade']['reference_correction_proposals'] = [{'reason': 'Invented source-grounded proposal'}]
    result = mixed.reconcile_record(first, second, True)
    assert result['judgment'] == 'indeterminate' and result['adjudicated_grade'] is None


def test_protocol_failure_remains_known_independent_of_content_dispute():
    first = record(judgment='indeterminate')
    first['protocol_eligible'] = False
    result = mixed.reconcile_record(first, None, True)
    assert result['judgment'] == 'workflow_failure'
    assert result['content_judgment'] == 'indeterminate'
    assert result['assistant_adjudication_complete'] is False
    assert result['execution_endpoint_known'] is True


def test_native_partial_status_alone_does_not_fail_source_content():
    first = record()
    first['execution_status'] = 'failed'
    result = mixed.reconcile_record(first, record(), True)
    assert result['judgment'] == 'satisfies_reference'


def test_selection_all_errors_disputes_protocol_failures_and_seeded20percent():
    records = {str(n): record(str(n)) for n in range(10)}
    records['error'] = record('error', 'substantive_error')
    records['dispute'] = record('dispute', 'indeterminate')
    records['protocol'] = record('protocol')
    records['protocol']['protocol_eligible'] = False
    records['partial'] = record('partial')
    records['partial']['execution_status'] = 'failed'
    selected = mixed.selected_rechecks(records)
    assert {'error', 'dispute', 'protocol', 'partial'}.issubset(selected)
    assert selected == mixed.selected_rechecks(deepcopy(records))
    assert len(selected) >= 4


def test_mixed_epoch_blocks_nested_efficiency_even_with_all_quality_resolved():
    evidence = {'comparisons': [{'quality_noninferiority_supported': True, 'efficiency_supported': True,
        'quality_bounds': [0.1, 0.2], 'resource_ratio_upper_bound': 0.5,
        'descriptive_resource_ratio': 0.4, 'status': 'secondary_cluster_bootstrap_evidence',
        'nested': {'efficiency_supported': True, 'practical_advantage_method': 'skillflow'}}]}
    result = mixed.block_resource_inference(evidence)
    row = result['comparisons'][0]
    assert row['quality_noninferiority_supported'] is False and row['efficiency_supported'] is False
    assert row['nested']['efficiency_supported'] is False and row['nested']['practical_advantage_method'] is None
    assert row['quality_bounds'] is None and row['resource_ratio_upper_bound'] is None
    assert row['descriptive_resource_ratio'] == 0.4
    assert evidence['comparisons'][0]['efficiency_supported'] is True


def test_chain_source_correction_blocks_primary_but_missing_chain_alone_does_not():
    resolved = mixed.reconcile_record(record(), record(), True)
    assert mixed.apply_chain_source_dispute(resolved, None, protocol_eligible=True)['judgment'] == 'satisfies_reference'
    chain = {'reference_correction_proposals': [{'reason': 'Invented unresolved source-reference correction'}]}
    changed = mixed.apply_chain_source_dispute(resolved, chain, protocol_eligible=True)
    assert changed['judgment'] == 'indeterminate' and changed['adjudicated_grade'] is None
    assert changed['assistant_adjudication_complete'] is False
    assert 'chain_source_reference_correction_proposed' in changed['primary_disputes']
    failed = mixed.apply_chain_source_dispute(resolved, chain, protocol_eligible=False)
    assert failed['judgment'] == 'workflow_failure' and failed['content_judgment'] == 'indeterminate'
