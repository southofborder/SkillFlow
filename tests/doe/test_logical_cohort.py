"""Analysis-origin tests on invented schedules only; no source/target access."""
from pathlib import Path

import pytest

from tools.doe.real_comparison.logical_cohort import select_origins


def schedule():
    return [{'workflow_id': f'{method}-{n}', 'method': method}
            for method, count in [('skillflow', 72), ('audit', 96), ('chain', 96)] for n in range(count)]


def test_only_paused_skillflow_comes_from_original_epoch():
    donor, direct = Path('original'), Path('direct')
    rows = schedule()
    selected = select_origins(rows, donor, direct)
    assert len(selected) == 264
    for item in rows:
        assert selected[item['workflow_id']] == (donor if item['method'] == 'skillflow' else direct)


@pytest.mark.parametrize('defect', ['missing', 'duplicate', 'extra', 'unknown_method', 'wrong_counts'])
def test_invalid_logical_rosters_fail_closed(defect):
    rows = schedule()
    if defect == 'missing': rows.pop()
    if defect == 'duplicate': rows[-1] = dict(rows[0])
    if defect == 'extra': rows.append({'workflow_id': 'extra', 'method': 'audit'})
    if defect == 'unknown_method': rows[-1]['method'] = 'unknown'
    if defect == 'wrong_counts': rows[0]['method'] = 'audit'
    with pytest.raises(ValueError): select_origins(rows, Path('original'), Path('direct'))
