"""Exact byte-origin rules on invented packet files only."""
import json

import pytest

from tools.doe.real_comparison.grade_lineage import compare_packet_bytes


def packets(tmp_path):
    old, new = tmp_path / 'old', tmp_path / 'new'
    for root, digest in [(old, 'original-seal'), (new, 'logical-seal')]:
        root.mkdir()
        for name in ('source-bundle.txt', 'candidate.txt', 'reference.json', 'execution.json', 'artifacts.json'):
            (root / name).write_text('Identical complete 原文\r\n', encoding='utf-8')
        (root / 'grade.template.json').write_text(json.dumps({'candidate_id': 'same', 'candidate_sha256': 'same',
            'source_sha256': 'same', 'output_freeze_sha256': digest}), encoding='utf-8')
    return old, new


def test_only_output_cohort_hash_may_differ_without_rewriting_grade(tmp_path):
    proof = compare_packet_bytes(*packets(tmp_path))
    assert proof['identical_nontemplate_files'] == 5
    assert proof['only_permitted_template_difference'] == 'output_freeze_sha256'


@pytest.mark.parametrize('changed', ['source-bundle.txt', 'candidate.txt', 'reference.json', 'execution.json', 'artifacts.json'])
def test_any_source_candidate_reference_execution_or_lineage_change_rejects_import(tmp_path, changed):
    old, new = packets(tmp_path)
    (new / changed).write_text('different', encoding='utf-8')
    with pytest.raises(ValueError): compare_packet_bytes(old, new)


def test_changed_template_identity_rejects_import(tmp_path):
    old, new = packets(tmp_path)
    path = new / 'grade.template.json'
    value = json.loads(path.read_text(encoding='utf-8'))
    value['source_sha256'] = 'different'
    path.write_text(json.dumps(value), encoding='utf-8')
    with pytest.raises(ValueError): compare_packet_bytes(old, new)


def test_extra_original_or_target_artifact_rejects_import(tmp_path):
    old, new = packets(tmp_path)
    (new / 'extra.txt').write_text('extra', encoding='utf-8')
    with pytest.raises(ValueError): compare_packet_bytes(old, new)
