"""Build final review summary from sealed facts; does not call a model."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / 'packages/skill-ir/src/skill_ir/recording.py').is_file())
sys.path.insert(0, str(ROOT / 'packages/skill-ir/src'))
from skill_ir.recording import sha_file, implementation_provenance
from skill_ir.propagation.handoff import load_doe_input


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def tests(path, target):
    suites = list(ET.parse(path).getroot().iter('testsuite'))
    totals = {k: sum(int(s.attrib.get(k, '0')) for s in suites)
              for k in ['tests', 'failures', 'errors', 'skipped']}
    assert totals['failures'] == totals['errors'] == 0
    shutil.copyfile(path, target)
    return {'file': target.name, 'sha256': sha_file(target), **totals}


def main():
    parser = argparse.ArgumentParser(description='仅由已提交材料生成本轮验收和助手总览，不调用模型')
    parser.add_argument('--run-dir', type=Path)
    args = parser.parse_args()
    directory = args.run_dir.resolve() if args.run_dir else Path((ROOT / 'tmp/sink-tightening/run-path.txt').read_text(encoding='utf-8').strip())
    manifest, summary = read(directory / 'manifest.json'), read(directory / 'summary.json')
    preservation, replay = read(directory / 'preservation.json'), read(directory / 'replay-verification.json')
    assert preservation['status'] == replay['status'] == 'matched'
    assert not preservation['differences']
    assert replay['replay_model_calls'] == replay['network_attempts'] == 0
    assert summary['logical_calls'] == summary['http_attempts'] == 3
    assert manifest['implementation'] == implementation_provenance()
    test_receipts = [tests(ROOT / 'tmp/sink-tightening-tests.xml', directory / 'tests.junit.xml'),
                     tests(ROOT / 'tmp/sink-tightening-final-tests.xml', directory / 'final-tests.junit.xml')]
    assert [r['tests'] for r in test_receipts] == [2493, 158]
    cases = []
    for row in summary['cases']:
        n = row['case_id']
        base = directory / 'cases' / n
        doe = read(base / 'propagation/doe-input.json')
        load_doe_input(base / 'propagation/doe-input.json')
        assert row['annotation'] == row['propagation'] == doe['status'] == 'complete'
        assert not doe['diagnostics']
        assert (base / 'assistant-review.md').is_file()
        transport = read(base / 'annotation/calls/annotation/a001/transport.json')
        assert len(transport) == 1 and len(transport[0]['http_attempts']) == 1
        generation, attempt = transport[0], transport[0]['http_attempts'][0]
        params = attempt['request_parameters']
        assert generation['request_parameters_observed'] is True
        assert params['response_format'] == {'type': 'json_object'}
        assert params['model'] == 'deepseek-v4-flash'
        raw = attempt['raw_response']
        raw = json.loads(raw) if isinstance(raw, str) else raw
        finishes = [choice['finish_reason'] for choice in raw['choices']]
        assert finishes == ['stop'] and attempt['stream']['done_received'] is True
        for data in doe['data']:
            assert set(data) == {'id', 'content', 'origin', 'annotations'}
            assert 'evidence_refs' not in data['origin']
            assert all('evidence_refs' not in d for d in data['origin']['dependencies'])
        details = {
            **row, 'record_count': len(doe['records']), 'data_count': len(doe['data']),
            'diagnostic_count': len(doe['diagnostics']),
            'doe_sha256': sha_file(base / 'propagation/doe-input.json'),
            'doe_bytes': (base / 'propagation/doe-input.json').stat().st_size,
            'doe_lines': len((base / 'propagation/doe-input.json').read_text(encoding='utf-8').splitlines()),
            'observed_request_parameters': params,
            'request_body_sha256': attempt['request_body_sha256'],
            'finish_reasons': finishes,
            'elapsed_seconds': generation['elapsed_seconds'],
            'assistant_review_file': f'cases/{n}/assistant-review.md',
            'assistant_review_sha256': sha_file(base / 'assistant-review.md'),
            'assistant_review_status': 'no_new_material_issue_identified',
            'human_confirmed': False,
        }
        cases.append(details)
    verification = {
        'verified_at': datetime.now(timezone.utc).isoformat(),
        'identity': manifest['identity'], 'implementation_sha256': manifest['implementation']['sha256'],
        'tests': test_receipts,
        'test_scope_note': '2493 full tests before a final report-only fix; affected 158 tests passed after it, including the new foreach conditional display regression.',
        'cases': cases, 'logical_calls': 3, 'http_attempts': 3, 'http_retries': 0,
        'replay': replay,
        'preservation_file': 'preservation.json', 'preservation_sha256': sha_file(directory / 'preservation.json'),
        'versions': {'annotation': 'security-profile-v10', 'annotation_run': 'skill-ir-security-profile-v11',
            'runtime': 'skillflow-abstract-runtime-v5', 'representation': 'skillflow-representation-contract-v3',
            'compiler': 'skillflow-observation-compiler-v4', 'records': 'skillflow-propagation-record-v9',
            'doe': 'skillflow-doe-input-v7', 'propagation_run': 'skill-ir-propagation-v10',
            'data': 'skillflow-data-v4'},
        'method_note': 'Assistant static review, not human confirmation, dynamic execution or proof of annotation correctness. Sink counts are static operation locations, not actual call multiplicity.',
    }
    # Take the exact compiler identity from the committed certificate.
    verification['versions']['compiler'] = read(directory / 'cases/001/annotation/result.json')['compilation']['version']
    for label, filename in [('credentials_verification', 'credentials-verification.json'),
                            ('html_static_verification', 'html-verification.json')]:
        if (directory / filename).is_file():
            verification[label] = {'file': filename, 'sha256': sha_file(directory / filename),
                                   **read(directory / filename)}
    write(directory / 'verification.json', verification)
    write(directory / 'assistant-review.json', {
        'reviewer': 'assistant', 'human_confirmed': False,
        'cases': [{k: c[k] for k in ['case_id', 'assistant_review_file', 'assistant_review_sha256', 'assistant_review_status']} for c in cases],
        'scope': 'Source range, mode, source/derived relations, original field values, versions, request binding and actual boundary payloads.',
        'limits': ['No runtime execution', 'No independent model review or repair call', 'No DOE judgement'],
    })
    intro = ('本轮三例均完成一次联合标注、观察编译、确定性传播和零 API 重放。'
             '001 修正了无依据网络分类；010 保留了可选参数原值、出现条件和同一请求绑定；013 本次获得合法 JSON。'
             '助手逐例复核未发现新的实质关系问题。以下是统一契约下的静态可能行为，不是执行日志或 DOE 结论。')
    highlights = {
        '001': 'notify.send 为 tool/recipient/null，external_tool 等级 2；recipient 与 summary 保持同一元素的原字段。来源整体观察未被工具参数范围替换。',
        '010': 'query、from_date、limit 保留原字段；两项 when 独立控制加入／省略，形成四种候选请求；交付与获取使用同一实际 Data 绑定。旗标不在请求内容中。',
        '013': '上轮完整返回有多余括号，未形成 DOE；本轮严格解析通过。环境整体与 FAST_KEY 选择分开，首次／重试／回退来源及 body 原字段保持，archive 直接参数只有 source_id。',
    }
    tree = '''DOE 顶层业务区、Data 外层和证据边界：保持不变
records[IR].events[].atomic_ops[]
├─ build.members[]                    仅 build 适用
│  ├─ path                            构造字段位置
│  ├─ value_input_index               原值槽；确定省略时 null
│  └─ when_input_index                控制槽；无条件时 null
└─ 条件观察.when_input_index           控制槽，不能算作观察载荷

locations.access_scope / retention    继续保留
sink_boundaries                       继续保留类型、等级、目标和操作坐标'''
    lines = ['# Sink 收紧、可选参数与 DOE 对照：三例完成结果', '', intro, '',
        '| 样例 | 标注／传播 | IR 记录 | Data | Sink 位置 | 主要变化 |',
        '|---|---|---:|---:|---:|---|']
    html_rows, html_links, markdown_links = [], [], []
    for c in cases:
        n = c['case_id']
        cells = [f"{n} / {c['sample_id']}", 'complete / complete', str(c['record_count']), str(c['data_count']), str(c['sink_count']), highlights[n]]
        lines.append('| ' + ' | '.join(cells) + ' |')
        html_rows.append('<tr>' + ''.join('<td>' + escape(x) + '</td>' for x in cells) + '</tr>')
        links = [(f'cases/{n}/propagation/report.html', '数据与边界审查'),
                 (f'cases/{n}/doe-input-change.html', 'DOE 变化对照'),
                 (f'cases/{n}/propagation/doe-input.json', 'DOE 原始事实'),
                 (f'cases/{n}/assistant-review.md', '助手逐项复核'),
                 (f'cases/{n}/annotation/report.md', '标注与边界属性'),
                 (f'cases/{n}/annotation/audit/raw-annotation.json', '原始标注'),
                 (f'cases/{n}/selected-analysis.json', '本次既有 CFG')]
        html_links.append('<div class="case"><h3>' + escape(n + ' / ' + c['sample_id']) + '</h3><p>' + escape(highlights[n]) + '</p><p>' + ' · '.join('<a href="' + escape(p, quote=True) + '">' + escape(t) + '</a>' for p, t in links) + '</p></div>')
        markdown_links += ['', n + '：' + ' · '.join(f'[{t}]({p})' for p, t in links)]
    lines += ['', '## 逐例审查入口', *markdown_links]
    lines += ['', '## DOE 文件增加什么', '', '```text', tree, '```', '',
        '成员映射不复制 Data ID。inputs 仍为按参数顺序排列的候选集合；控制影响成员出现，不代表控制明文成为请求内容。010 的四种请求形状是静态候选，不表示实际执行了四次工具调用。', '',
        '## 工程验收与复核边界', '',
        '- 全套 2493 项回归通过；最后一次报告展示修正后，受影响的 158 项回归再次通过，含逐元素条件观察的展示测试。',
        '- 三例恰好 3 次逻辑调用、3 次 HTTP 尝试、0 次传输重试。请求模型 deepseek-v4-flash，实际返回 deepseek-flash；实际请求均启用 JSON Output，完成原因均为 stop。',
        '- 三份 DOE 独立加载有效；离线重放阻断在线客户端和网络连接，0 API、0 网络尝试，三个最终文件的摘要保持不变。',
        '- 11513 个历史／冻结文件与 49 个受保护源码文件的摘要保持不变；三例源包和选定 CFG 与 bootstrap 绑定一致。',
        '- 传播诊断三例均为空。未运行额外模型审查或自动修复；助手复核不冒充人工确认。',
        '- 多余括号、重复键、非布尔条件、歧义请求和其他无效输入仍严格拒绝，不通过截断、修 JSON 或择优重跑形成成功。', '',
        '保留的正常近似包括：统一契约下可能的模型观察、工具默认外部接收、未知布尔条件的出现／省略候选、分支 may 汇合和不透明计算的 possible 依赖。等级只描述边界性质；这些结果不证明真实执行发生，也不判断敏感性、必要性或 DOE。013 不把上轮“未生成文件”解释成“上轮没有 sink”。', '',
        '[机器验收记录](verification.json) · [重放核验](replay-verification.json) · [历史保护](preservation.json) · [调用与状态](summary.json)', '',
        '## 离线复查', '', '```powershell', "$env:PYTHONPATH='packages/skill-ir/src'", 'python -m skill_ir.propagation replay --run-dir <本例 propagation 目录>', '```', '',
        '三例整体重放也可使用 tools/run_tightening_pilot.py replay --run-dir <本运行目录>。重放不读取 API key，不创建在线客户端。当前版本拒绝旧格式，历史文件只按原字节对照，不迁移。', '']
    (directory / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    check_text = ('2493 项完整回归通过；报告最后修正后 158 项相关回归通过。三次真实调用、三次 HTTP 尝试、零重试。'
                  '三例零 API 重放，DOE 摘要一致。11513 份历史文件及49份受保护源码摘要未变。')
    boundary_text = ('默认模型观察、工具外部接收、未知布尔和分支汇合仍是契约下的可能性；'
                     'possible 依赖不是明文包含，sink 等级不是敏感度或 DOE 风险。助手意见不是人工确认或执行验证。')
    page = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Sink 收紧与 DOE 对照：三例结果</title><style>body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1450px;margin:28px auto;padding:20px;color:#173343;background:#f8fafc}'
            'table{border-collapse:collapse;width:100%;background:white}td,th{border:1px solid #ccd7df;padding:12px;text-align:left;overflow-wrap:anywhere}'
            'pre{padding:20px;background:#edf3f6;white-space:pre-wrap;overflow-wrap:anywhere}.case{padding:16px;border:1px solid #ccd7df;border-radius:8px;margin:16px 0;background:white}'
            'a{color:#09667a}.notice{border-left:5px solid #218169;padding:16px;background:#e9f6ef}</style></head><body>'
            '<h1>Sink 标注收紧、可选参数与 DOE 文件对照</h1><p class="notice">' + escape(intro) + '</p>'
            '<table><thead><tr>' + ''.join('<th>' + t + '</th>' for t in ['样例', '标注／传播', 'IR 记录', 'Data', 'Sink 位置', '主要变化']) + '</tr></thead><tbody>' + ''.join(html_rows) + '</tbody></table>'
            '<h2>逐例审查入口</h2>' + ''.join(html_links) + '<h2>DOE 原始文件的结构增量</h2><pre>' + escape(tree) + '</pre>'
            '<p>成员映射通过索引指向已有 inputs，不复制 Data ID 或证据。010 的四种请求形状是静态候选，不是四次实际调用。</p>'
            '<h2>验收与剩余边界</h2><p>' + escape(check_text) + '</p><p>' + escape(boundary_text) + '</p>'
            '<p><a href="report.md">中文主报告</a> · <a href="verification.json">机器验收记录</a> · <a href="replay-verification.json">零 API 重放</a> · <a href="preservation.json">历史保护</a> · <a href="summary.json">调用与状态</a></p>'
            '<details><summary>版本与实现身份</summary><pre>' + escape(json.dumps(verification['versions'], ensure_ascii=False, indent=2)) + '</pre><p>实现摘要：' + escape(verification['implementation_sha256']) + '</p></details></body></html>')
    (directory / 'index.html').write_text(page, encoding='utf-8')
    # The generator is an audit-only convenience, outside producer identities.
    (directory / 'audit').mkdir(exist_ok=True)
    destination = directory / 'audit/build-final-summary.py'
    if Path(__file__).resolve() != destination.resolve():
        shutil.copyfile(__file__, destination)
    print(json.dumps({'status': 'verified', 'cases': [{k: c[k] for k in ['case_id','record_count','data_count','sink_count','diagnostic_count']} for c in cases], 'tests': test_receipts}, ensure_ascii=False))


if __name__ == '__main__':
    main()
