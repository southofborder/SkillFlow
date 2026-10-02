"""Compact business reports share one view and keep source/audit text inert."""
from copy import deepcopy
from pathlib import Path
import re
import runpy

import pytest

from skill_ir.propagation import propagate
from skill_ir.propagation.handoff import build_doe_input
from skill_ir.propagation.report import build_view, render_html, render_markdown, write_reports
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.security_profile.services import to_payload
from skill_ir.security_profile.evidence import prepare_material


@pytest.fixture
def inputs():
    example = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'examples/propagation_demo.py'))
    source, metadata, cfg, response, registry, state = example['demo_inputs']()
    payload = to_payload(response)
    solved = propagate(cfg, payload, initial_registry=registry, initial_state=state)
    doe = build_doe_input(source, cfg, payload, solved, source_metadata=metadata,
                          execution_model=prepare_material(source, cfg)["execution_model"])
    audit = {'annotation': payload, 'location_evidences': response['location_evidences'], 'stats': solved.stats}
    return doe, audit


def test_business_report_only_needs_main_file_and_preserves_order(inputs):
    doe, _ = inputs
    view = build_view(doe)
    row = next(row for row in view['rows'] if row['id'] == 'ir_model_filter')
    assert [stage['effect'] for stage in row['stages']] == ['model_observe', 'transform']
    assert [stage['position'] for stage in row['stages']] == ['1.1', '2.1']
    assert all(stage['spec'] is None for stage in row['stages'])
    local_row = next(row for row in view['rows'] if row['id'] == 'ir_local_filter')
    observed = [row['stages'][0]['op']['inputs'][0], local_row['stages'][1]['op']['inputs'][0]]
    assert observed[0] != observed[1]
    html, markdown = render_html(doe), render_markdown(doe)
    assert 'doe-input.json' in html and 'doe-input.json' in markdown
    assert '原标注审计' not in html and '原标注审计' not in markdown
    assert 'records.json' not in html and 'data.json' not in html
    assert len(view['rows']) == 13
    assert 'IR 记录覆盖：13 / 13' in html and 'IR 记录覆盖：13 / 13' in markdown
    assert '完整 Data 内容、来源与依赖' in markdown and 'field_updates' in markdown
    assert '效果' in html and 'model_observe' in markdown


def test_both_formats_use_same_view(monkeypatch, inputs):
    import skill_ir.propagation.report as report
    calls, original = [], report.build_view
    def captured(doe, *, audit=None):
        calls.append((doe, audit))
        return original(doe, audit=audit)
    monkeypatch.setattr(report, 'build_view', captured)
    doe, audit = inputs
    render_html(doe, audit=audit)
    render_markdown(doe, audit=audit)
    assert calls == [(doe, audit), (doe, audit)]


def test_input_slots_and_repeated_use_are_not_coalesced(inputs):
    doe, _ = inputs
    doe = deepcopy(doe)
    op = doe['records']['ir_model_filter']['events'][0]['atomic_ops'][0]
    op['inputs'].append(deepcopy(op['inputs'][0]))
    view = build_view(doe)
    row = next(row for row in view['rows'] if row['id'] == 'ir_model_filter')
    assert len(row['stages'][0]['op']['inputs']) == 2
    html = render_html(doe)
    assert '<span class="muted">0:</span>' in html and '<span class="muted">1:</span>' in html
    assert '不是原 IR 操作数编号' in html


def test_original_spec_parameters_and_evidence_are_folded(inputs):
    doe, audit = inputs
    html, markdown = render_html(doe, audit=audit), render_markdown(doe, audit=audit)
    assert '<details class="annotation-audit"><summary>原标注审计' in html
    assert '<details class="location-evidence">' in html
    assert '<details open' not in html
    assert '排除路径' in html and 'api_key' in html and '公开 IR 输出绑定及依据' in html
    assert 'effect_index' not in render_html(doe)
    assert '原标注审计' in markdown and '位置依据与求解统计' in markdown


def test_html_and_markdown_escape_source_and_audit_strings(inputs):
    doe, audit = deepcopy(inputs)
    hostile = '</pre><script>alert(1)</script><img src=x onerror=alert(2)>'
    doe['source']['files'][0]['content'] = hostile
    next(iter(audit['location_evidences'].values()))[0]['quote'] = hostile
    for rendered in (render_html(doe, audit=audit), render_markdown(doe, audit=audit)):
        assert hostile not in rendered and '&lt;script&gt;' in rendered
    html = render_html(doe, audit=audit)
    assert "script-src 'none'" in html and "connect-src 'none'" in html
    assert '<script>' not in html and '<img' not in html


def test_data_links_and_field_update_paths_have_visible_targets(inputs):
    doe, _ = inputs
    html = render_html(doe)
    targets = set(re.findall(r'id="(data-D\d+)"', html))
    links = set(re.findall(r'href="#(data-D\d+)"', html))
    assert links and links <= targets and len(targets) == len(doe['data'])
    replacement = re.search(r'<table class="field-updates">(.*?)</table>', html, re.S).group(1)
    assert '替换路径' in replacement and 'api_key' in replacement
    assert 'href="#data-D' in replacement
    assert '未提及部分继续保留原整体内容' in html


def test_unresolved_is_not_shown_as_a_confirmed_order(inputs):
    doe, _ = deepcopy(inputs)
    doe['records']['ir_model_filter']['order'] = 'partial'
    for rendered in (render_html(doe), render_markdown(doe)):
        assert '不代表唯一执行次序' in rendered
        assert '按必要先后约束汇合可能排列' in rendered


def test_replay_report_links_original_business_file(tmp_path, inputs):
    doe, audit = inputs
    directory = tmp_path / 'replay'
    write_reports(directory, doe, ArtifactWriter(()), audit=audit)
    assert 'href="../doe-input.json"' in (directory / 'report.html').read_text(encoding='utf-8')
    assert '(../doe-input.json)' in (directory / 'report.md').read_text(encoding='utf-8')
    assert 'href="../audit/material.json"' in (directory / 'report.html').read_text(encoding='utf-8')
    assert '(../audit/material.json)' in (directory / 'report.md').read_text(encoding='utf-8')


def test_contract_notice_precedes_records_without_claiming_evidence_proves_visibility(inputs):
    doe, audit = inputs
    for context in (None, audit):
        for rendered in (render_html(doe, audit=context), render_markdown(doe, audit=context)):
            assert doe['execution_model']['version'] in rendered
            assert doe['execution_model']['sha256'] in rendered
            assert '静态可能行为，不是运行日志' in rendered
            assert '不证明模型实际观察了这些内容' in rendered
            assert '没有引用契约规则，都不能据此认定为确定执行事实' in rendered
            assert 'model_observe（程序生成，静态可能）' in rendered
            assert rendered.index('静态可能行为') < rendered.index('ir_model_filter')
    assert 'audit/material.json' not in render_html(doe)


def test_saved_report_links_existing_frozen_material_without_copying_rules(tmp_path, inputs):
    doe, audit = inputs
    write_reports(tmp_path, doe, ArtifactWriter(()), audit=audit)
    assert 'href="audit/material.json"' in (tmp_path / 'report.html').read_text(encoding='utf-8')
    assert '(audit/material.json)' in (tmp_path / 'report.md').read_text(encoding='utf-8')
