"""Compact business reports share one view and keep source/audit text inert."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
from pathlib import Path
import re
import runpy

import pytest

from skillflow.propagation import propagate
from skillflow.propagation.report import build_view
from skillflow.propagation.report import render_html
from skillflow.propagation.report import render_markdown
from skillflow.propagation.report import write_reports
from skillflow.common.artifacts import ArtifactWriter
from skillflow.propagation.annotation.services import to_payload
from tests.propagation.annotation.helpers import prepare_material


@pytest.fixture
def inputs():
    example = runpy.run_path(str(project_root() / 'examples/propagation/propagation_demo.py'))
    return example['demo_materials']()


def test_business_report_only_needs_main_file_and_preserves_order(inputs):
    doe = inputs
    view = build_view(doe)
    row = next(row for row in view['rows'] if row['id'] == 'ir_model_filter')
    assert [stage['effect'] for stage in row['stages']] == ['model_observe', 'transform']
    assert [stage['position'] for stage in row['stages']] == ['1.1', '2.1']
    assert all(stage['spec'] is not None for stage in row['stages'])
    local_row = next(row for row in view['rows'] if row['id'] == 'ir_local_filter')
    observed = [row['stages'][0]['op']['inputs'][0], local_row['stages'][1]['op']['inputs'][0]]
    assert observed[0] != observed[1]
    html, markdown = render_html(doe), render_markdown(doe)
    assert 'records.json' in html and 'data.json' in markdown and 'sinks.json' in html
    assert 'Original annotation audit' in html and 'Original annotation audit' in markdown
    assert 'doe-input.json' not in html and 'doe-input.json' not in markdown
    assert len(view['rows']) == 13
    assert 'IR record coverage: 13 / 13' in html and 'IR record coverage: 13 / 13' in markdown
    assert 'Complete Data content, origin and dependencies' in markdown and 'field_updates' in markdown
    assert 'Effect' in html and 'model_observe' in markdown


def test_both_formats_use_same_view(monkeypatch, inputs):
    import skillflow.propagation.report as report
    calls, original = [], report.build_view
    def captured(doe):
        calls.append(doe)
        return original(doe)
    monkeypatch.setattr(report, 'build_view', captured)
    doe = inputs
    render_html(doe)
    render_markdown(doe)
    assert calls == [doe, doe]


def test_input_slots_and_repeated_use_are_not_coalesced(inputs):
    doe = inputs
    doe = deepcopy(doe)
    op = doe._records['ir_model_filter']['events'][0]['atomic_ops'][0]
    op['inputs'].append(deepcopy(op['inputs'][0]))
    view = build_view(doe)
    row = next(row for row in view['rows'] if row['id'] == 'ir_model_filter')
    assert len(row['stages'][0]['op']['inputs']) == 2
    html = render_html(doe)
    assert '<span class="muted">0:</span>' in html and '<span class="muted">1:</span>' in html
    assert 'not original IR operands' in html


def test_original_spec_parameters_and_evidence_are_folded(inputs):
    doe = inputs
    html, markdown = render_html(doe), render_markdown(doe)
    assert '<details class="annotation-audit"><summary>Original annotation audit' in html
    assert '<details class="location-evidence">' in html
    assert '<details open' not in html
    assert 'Excluded paths' in html and 'api_key' in html and 'Public IR output bindings and evidence' in html
    assert 'effect_index' not in render_html(doe)
    assert 'Original annotation audit' in markdown and 'location evidence and solver statistics' in markdown


def test_html_and_markdown_escape_source_and_audit_strings(inputs):
    doe = deepcopy(inputs)
    hostile = '</pre><script>alert(1)</script><img src=x onerror=alert(2)>'
    doe._annotation['material']['source']['files'][0]['content'] = hostile
    next(iter(doe._annotation['compiled_annotation']['location_evidences'].values()))[0]['reason'] = hostile
    for rendered in (render_html(doe), render_markdown(doe)):
        assert hostile not in rendered and '&lt;script&gt;' in rendered
    html = render_html(doe)
    assert "script-src 'none'" in html and "connect-src 'none'" in html
    assert '<script>' not in html and '<img' not in html


def test_data_links_and_field_update_paths_have_visible_targets(inputs):
    doe = inputs
    html = render_html(doe)
    targets = set(re.findall(r'id="(data-D\d+)"', html))
    links = set(re.findall(r'href="#(data-D\d+)"', html))
    assert links and links <= targets and len(targets) == len(doe.data)
    replacement = re.search(r'<table class="field-updates">(.*?)</table>', html, re.S).group(1)
    assert 'Replacement paths' in replacement and 'api_key' in replacement
    assert 'href="#data-D' in replacement
    assert 'all other parts retain the original content' in html


def test_unresolved_is_not_shown_as_a_confirmed_order(inputs):
    doe = deepcopy(inputs)
    doe._records['ir_model_filter']['order'] = 'partial'
    for rendered in (render_html(doe), render_markdown(doe)):
        assert 'do not imply a unique execution order' in rendered
        assert 'possible permutations are joined subject to required precedence' in rendered


def test_replay_report_links_original_business_file(tmp_path, inputs):
    from tests.propagation.component_helpers import accepted_annotation
    doe = inputs
    accepted_annotation(tmp_path / 'annotation', doe.material, doe.raw_annotation)
    directory = tmp_path / 'replay'
    write_reports(directory, doe, ArtifactWriter(()), annotation_run=tmp_path / 'annotation')
    assert 'href="../records.json"' in (directory / 'report.html').read_text(encoding='utf-8')
    assert '(../records.json)' in (directory / 'report.md').read_text(encoding='utf-8')
    assert 'href="../annotation/inputs/runtime-contract.json"' in (directory / 'report.html').read_text(encoding='utf-8')
    assert '(../annotation/inputs/runtime-contract.json)' in (directory / 'report.md').read_text(encoding='utf-8')


def test_contract_notice_precedes_records_without_claiming_evidence_proves_visibility(inputs):
    from skillflow.propagation.contracts.runtime_contract import runtime_contract_binding
    binding = runtime_contract_binding(inputs.runtime_contract)
    for rendered in (render_html(inputs), render_markdown(inputs)):
        assert binding['version'] in rendered and binding['sha256'] in rendered
        assert 'static possible behavior under the shared abstract runtime contract, not execution logs' in rendered
        assert 'not that the model actually observed this content' in rendered
        assert 'absence of a contract citation does not establish an observed runtime fact' in rendered
        assert 'model_observe (program-generated, statically possible)' in rendered
        assert rendered.index('static possible behavior') < rendered.index('ir_model_filter')
    assert 'audit/material.json' not in render_html(inputs)


def test_saved_report_links_existing_frozen_material_without_copying_rules(tmp_path, inputs):
    from tests.propagation.component_helpers import accepted_annotation
    doe = inputs
    accepted_annotation(tmp_path / 'annotation', doe.material, doe.raw_annotation)
    write_reports(tmp_path, doe, ArtifactWriter(()), annotation_run=tmp_path / 'annotation')
    assert 'href="annotation/inputs/runtime-contract.json"' in (tmp_path / 'report.html').read_text(encoding='utf-8')
    assert '(annotation/inputs/runtime-contract.json)' in (tmp_path / 'report.md').read_text(encoding='utf-8')
