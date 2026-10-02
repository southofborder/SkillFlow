"""One business view model for Chinese Markdown and HTML propagation review."""
from __future__ import annotations
from html import escape
import json
from pathlib import Path


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)


def _changes(record):
    states = [{(b['location']['kind'], b['location']['name']): b['data_ids'] for b in record[key]['bindings']}
              for key in ('entry_state', 'exit_state')]
    return [{'location': {'kind': k[0], 'name': k[1]}, 'before': states[0].get(k, []), 'after': states[1].get(k, [])}
            for k in sorted(set(states[0]) | set(states[1])) if states[0].get(k) != states[1].get(k)]


def _location(value):
    return value['kind'] + ': ' + value['name']


def _operands(values):
    return ', '.join(str(i) + ': ' + (v['identifier'] if 'identifier' in v else json.dumps(v.get('literal_value'), ensure_ascii=False))
                     for i, v in enumerate(values)) or '[]'


def build_view(doe, *, audit=None):
    """Resolve presentation positions from the current record and optional source specs."""
    labels = {d['id']: f'D{i:03}' for i, d in enumerate(sorted(doe['data'], key=lambda d: d['id']), 1)}
    annotation = audit['annotation'] if audit is not None else None
    rows = []
    for block_id, block in doe['cfg']['blocks'].items():
        for ir in block['instructions']:
            ir_id = ir['id']
            record = doe['records'].get(ir_id)
            if record is None:
                continue
            spec = annotation['transfer_specs'][ir_id] if annotation is not None else None
            stages = []
            for i, event in enumerate(record['events']):
                for j, op in enumerate(event['atomic_ops']):
                    declaration = spec['events'][i]['atomic_ops'][j] if spec is not None else None
                    stages.append({'position': f'{i + 1}.{j + 1}', 'effect': event['effect'], 'op': op, 'spec': declaration})
            rows.append({'id': ir_id, 'block': block_id, 'ir': ir, 'record': record, 'action': doe['actions'][ir_id],
                         'stages': stages, 'changes': _changes(record),
                         'unresolved': [u for u in doe['unresolved'] if u['instruction_id'] == ir_id],
                         'profile': annotation['profiles'][ir_id] if annotation is not None else None,
                         'output_bindings': spec['output_bindings'] if spec is not None else None})
    return {**{key: doe[key] for key in ('status', 'source', 'locations', 'coverage', 'diagnostics', 'unresolved')},
            'data': sorted(doe['data'], key=lambda d: d['id']), 'labels': labels, 'rows': rows, 'audit': audit,
            'ir_total': sum(len(block['instructions']) for block in doe['cfg']['blocks'].values())}


def _parameters(spec):
    names = {'path': '选取路径', 'paths': '排除路径', 'dependencies': '依赖', 'updates': '字段覆盖',
             'parts': '组成', 'mode': '写入方式', 'container': '容器'}
    return {names[key]: spec[key] for key in names if key in spec}


def render_markdown(doe, *, audit=None, doe_href='doe-input.json'):
    view = build_view(doe, audit=audit)
    ids = lambda values: ', '.join(view['labels'][key] for key in values) or '未绑定'
    cell = lambda value: escape(str(value)).replace('|', '&#124;').replace('\n', ' ')
    detail = lambda title, value: ['<details><summary>' + escape(title) + '</summary>', '', '<pre>' + escape(_json(value)) + '</pre>', '', '</details>', '']
    lines = ['# 基础数据传播记录', '', f"执行状态：`{view['status']}`。", '',
             f"IR 记录覆盖：{len(view['rows'])} / {view['ir_total']}。", '',
             f'[本地可视化审查](report.html) · [唯一业务结果]({doe_href})', '',
             'D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。', '']
    lines += detail('完整源文', view['source']) + detail('覆盖与诊断', {key: view[key] for key in ('coverage', 'diagnostics')})
    if view['unresolved']:
        lines += ['**标注仍有未决，传播完成不消除这些未决。**', ''] + detail('未决项', view['unresolved'])
    for row in view['rows']:
        lines += [f"## {cell(row['id'])} · {cell(row['ir']['opcode'])}", '',
                  f"块：{cell(row['block'])}；执行主体：{cell(', '.join(row['action']['operator']) or '[]')}；角色：{cell(', '.join(row['action']['roles']) or '[]')}。", '',
                  'IR 输入：' + cell(_operands(row['ir'].get('inputs', []))), '', 'IR 输出：' + cell(_operands(row['ir'].get('outputs', []))), '']
        if any(u['field'] == 'effects' for u in row['unresolved']):
            lines += ['**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**', '']
        lines += ['| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |', '|---|---|---|---|---|---|']
        for stage in row['stages']:
            op = stage['op']
            inputs = '; '.join(f'{i}: {ids(v)}' for i, v in enumerate(op['inputs'])) or '—'
            outputs = [f'{i}: {ids(v)}' for i, v in enumerate(op['outputs'])]
            outputs += [f"{_location(c['location'])}: {ids(c['before'])} → {ids(c['after'])} ({c['update']})" for c in op['changes']]
            values = [stage['position'], stage['effect'] or '无标签数据操作', op['op'], inputs,
                      '; '.join(_location(p) for p in op['endpoints']) or '—', '; '.join(outputs) or '—']
            lines.append('| ' + ' | '.join(cell(value) for value in values) + ' |')
        if not row['stages']:
            lines.append('| — | 无效果事件 | — | — | — | 仍保留入口、出口与结果绑定 |')
        lines += ['', '入口／出口变化：', '']
        lines += [f"- `{cell(_location(c['location']))}`：{ids(c['before'])} → {ids(c['after'])}" for c in row['changes']] or ['- 位置绑定没有变化；不代表没有观察或发送。']
        lines += ['', *detail('完整入口与出口', {k: row['record'][k] for k in ('entry_state', 'exit_state')})]
        if audit is not None:
            lines += detail('原标注审计：profile、步骤参数、输出绑定与依据',
                            {'profile': row['profile'], 'steps': [s['spec'] for s in row['stages']], 'output_bindings': row['output_bindings']})
    lines += ['## 数据索引', '', '| 短名 | 完整 ID | 内容形态 |', '|---|---|---|']
    for data in view['data']:
        lines.append(f"| {view['labels'][data['id']]} | {cell(data['id'])} | {cell(data['content']['form'])} |")
    lines.append('')
    for data in view['data']:
        lines += detail(view['labels'][data['id']] + '：完整 Data 内容、来源与依赖', data)
    if audit is not None:
        lines += ['', *detail('独立审计材料：位置依据与求解统计', {'location_evidences': audit['location_evidences'], 'stats': audit['stats']})]
    return '\n'.join(lines) + '\n'


def render_html(doe, *, audit=None, doe_href='doe-input.json'):
    view = build_view(doe, audit=audit)
    labels = view['labels']
    def pre(value): return '<pre>' + escape(_json(value)) + '</pre>'
    def details(title, content, css=''):
        return '<details class="' + escape(css, quote=True) + '"><summary>' + escape(title) + '</summary>' + content + '</details>'
    def ids(values):
        return ', '.join(f'<a class="data" href="#data-{labels[k]}" title="{escape(k, quote=True)}">{labels[k]}</a>' for k in values) or '<span class="muted">未绑定</span>'
    def bindings(values):
        return '<br>'.join(f'<span class="muted">{i}:</span> ' + ids(v) for i, v in enumerate(values)) or '—'
    def evidence(values):
        return ''.join('<p class="muted">' + escape(e['basis'] + ' / ' + e['ref_id']) + '</p><blockquote>' + escape(e['quote']) + '</blockquote><p>' + escape(e['reason']) + '</p>' for e in values)
    body = ['<h1>基础数据传播审查</h1><p>执行状态：<strong>' + escape(view['status']) + '</strong></p>',
            f"<p>IR 记录覆盖：{len(view['rows'])} / {view['ir_total']}。</p>",
            '<p><a href="' + escape(doe_href, quote=True) + '">唯一业务结果 doe-input.json</a></p>',
            '<p>点击 D 编号查看数据版本。表中参数编号属于原子操作，不是原 IR 操作数编号。候选集合不表示同时发生，possible 依赖不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。</p>',
            details('完整源文', pre(view['source']), 'source'), details('覆盖与诊断', pre({k: view[k] for k in ('coverage', 'diagnostics')}))]
    if view['unresolved']:
        body += ['<p class="notice">标注仍有未决；传播完成不消除这些未决。</p>', details('未决项', pre(view['unresolved']))]
    for row in view['rows']:
        ir, action = row['ir'], row['action']
        body += ['<section><h2>' + escape(row['id'] + ' · ' + ir['opcode']) + '</h2><p class="muted">块 ' + escape(row['block']) + '</p>',
                 '<p><b>IR 输入：</b>' + escape(_operands(ir.get('inputs', []))) + '<br><b>IR 输出：</b>' + escape(_operands(ir.get('outputs', []))) + '</p>',
                 '<p><b>执行主体（operator）：</b>' + escape(', '.join(action['operator']) or '[]') + '　<b>roles：</b>' + escape(', '.join(action['roles']) or '[]') + '</p>']
        if any(u['field'] == 'effects' for u in row['unresolved']):
            body.append('<p class="notice">效果存在未决；表中位置用于对应记录，不能当作已确认的完整执行顺序。</p>')
        body.append('<table class="stages"><thead><tr>' + ''.join('<th>' + s + '</th>' for s in ('位置', '效果', 'op', '实际输入数据', '交互边界', '输出或状态变化')) + '</tr></thead><tbody>')
        audits = []
        for stage in row['stages']:
            op = stage['op']
            changes = [escape(_location(c['location'])) + '<br>' + ids(c['before']) + ' → ' + ids(c['after']) + ' <small>' + escape(c['update']) + '</small>' for c in op['changes']]
            outputs = '<br>'.join(([bindings(op['outputs'])] if op['outputs'] else []) + changes) or '—'
            cells = [stage['position'], escape(stage['effect'] or '无标签数据操作'), escape(op['op']), bindings(op['inputs']),
                     '<br>'.join(escape(_location(p)) for p in op['endpoints']) or '—', outputs]
            body.append('<tr>' + ''.join('<td>' + value + '</td>' for value in cells) + '</tr>')
            if audit is not None:
                audits.append(details(stage['position'] + ' · ' + op['op'] + '：参数与依据', pre(_parameters(stage['spec'])) + evidence(stage['spec']['evidences']) + pre(stage['spec'])))
        if not row['stages']:
            body.append('<tr><td colspan="6">没有效果事件；仍保留公开结果位置和完整 IN / OUT。空效果不等于空操作。</td></tr>')
        body += ['</tbody></table><h3>IN / OUT 差异</h3>']
        if row['changes']:
            body.append('<table><tr><th>位置</th><th>入口</th><th>出口</th></tr>')
            for c in row['changes']:
                body.append('<tr><td>' + escape(_location(c['location'])) + '</td><td>' + ids(c['before']) + '</td><td>' + ids(c['after']) + '</td></tr>')
            body.append('</table>')
        else:
            body.append('<p class="muted">位置绑定没有变化；不表示未发生观察或发送。</p>')
        body.append(details('完整入口与出口', pre({k: row['record'][k] for k in ('entry_state', 'exit_state')})))
        if audit is not None:
            inner = [*audits, details('公开 IR 输出绑定及依据', pre(row['output_bindings']))]
            for e in row['profile']['evidences']:
                pos = f" · 效果索引 {e['effect_index']}" if e.get('effect_index') is not None else ''
                inner += ['<h4>' + escape(e['field'] + pos + ' · ' + (e['value'] or '空标签说明')) + '</h4>', evidence([e])]
            body.append(details('原标注审计：规格、输出绑定及 Security Profile 依据', ''.join(inner), 'annotation-audit'))
        body.append('</section>')
    body += ['<h2>Data 内容与来源</h2><p>组成与内容保留、明确派生和可能依赖分别记录。后续删减不撤销此前观察。</p>']
    for data in view['data']:
        content, label = data['content'], labels[data['id']]
        body += [f'<details id="data-{label}" class="data-card"><summary>' + label + ' · ' + escape(content['form']) + '</summary><p class="identifier">' + escape(data['id']) + '</p>']
        if 'base' in content: body.append('<p>原整体：' + ids([content['base']]) + '</p>')
        for key, title in (('parts', '组成位置'), ('updates', '替换路径')):
            if key in content:
                if key == 'updates': body.append('<p>指定路径使用新数据替换；未提及部分继续保留原整体内容。</p>')
                body.append('<table class="' + ('field-updates' if key == 'updates' else 'parts') + '"><tr><th>' + title + '</th><th>Data</th></tr>')
                for part in content[key]: body.append('<tr><td>' + escape(_json(part['path'])) + '</td><td>' + ids([part['data']]) + '</td></tr>')
                body.append('</table>')
        if 'excluded_parts' in content: body += ['<p>明确排除：</p>', pre(content['excluded_parts'])]
        for key, title in (('acquired_from', '外部来源'), ('at', '登记位置')):
            if data['origin'].get(key): body.append('<p>' + title + '：' + escape(data['origin'][key]) + '</p>')
        body.append('<p>实际输入：' + ids(data['origin']['inputs']) + '</p>')
        for dep in data['origin']['dependencies']: body.append('<p>' + escape(dep['relation']) + '：' + ids([dep['data']]) + '</p>')
        body += [details('完整 Data', pre(data)), '</details>']
    if audit is not None:
        content = []
        for loc_id, values in audit['location_evidences'].items():
            loc = view['locations'][loc_id]
            content += ['<h3>' + escape(loc_id + ' · ' + _location(loc)) + '</h3>', pre(loc['operand_refs']), evidence(values)]
        body += [details('位置身份依据（独立审计材料）', ''.join(content), 'location-evidence'), details('求解统计（工程材料）', pre(audit['stats']))]
    return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'none'; connect-src 'none'">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>基础数据传播审查</title>
<style>body{font:15px/1.65 'Microsoft YaHei',sans-serif;max-width:1450px;margin:26px auto;padding:0 22px;color:#23364a;background:#f5f8fa}section{background:white;border:1px solid #d8e2ec;padding:22px;margin:24px 0}h1,h2{color:#123f55}table{border-collapse:collapse;width:100%;table-layout:fixed;margin:14px 0}th,td{text-align:left;vertical-align:top;border:1px solid #d8e2ec;padding:10px;overflow-wrap:anywhere;white-space:pre-wrap}th{background:#e9f1f6;font-size:13px}td{font-size:13px}.stages th:first-child{width:5%}.stages th:nth-child(2){width:12%}.stages th:nth-child(3){width:13%}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.6 Consolas,'Microsoft YaHei',monospace;background:#edf2f7;padding:14px}details{margin:12px 0}summary{cursor:pointer;font-weight:600;overflow-wrap:anywhere}.notice{background:#fff3d4;padding:12px}.muted,small{color:#60788b}.data{font-family:Consolas,monospace;font-weight:bold;color:#087284}.identifier{font:12px Consolas,monospace;overflow-wrap:anywhere}.data-card{background:white;border:1px solid #d8e2ec;padding:16px}.data-card:target{border:3px solid #e4a73a}blockquote{white-space:pre-wrap;overflow-wrap:anywhere;border-left:3px solid #769eb1;padding:10px;background:#f1f6fa}a{color:#126980}</style><body>''' + ''.join(body) + '</body></html>'


def write_reports(directory: Path, doe, writer, *, audit=None):
    href = '../doe-input.json' if directory.name == 'replay' else 'doe-input.json'
    writer.text(directory / 'report.md', render_markdown(doe, audit=audit, doe_href=href))
    writer.text(directory / 'report.html', render_html(doe, audit=audit, doe_href=href))
