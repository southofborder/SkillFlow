"""One business view model for Chinese Markdown and HTML propagation review."""
from __future__ import annotations
from html import escape
import json
from pathlib import Path

from skillflow.propagation.contracts.boundaries import exposure_level
from skillflow.propagation.conditions import guard_truths
from skillflow.propagation.conditions import payload_inputs


CONTRACT_NOTICE = (
    '以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。'
    'complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。'
    '默认补充的观察与明确例外共同约束分析范围；使用固定顺序或没有引用契约规则，都不能据此认定为确定执行事实。'
)


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
    return ', '.join(str(i) + ': ' + (json.dumps(v['literal_value'], ensure_ascii=False) if v['type'] == 'literal' else v['identifier'])
                     for i, v in enumerate(values)) or '[]'


def build_view(doe, *, audit=None):
    """Resolve presentation positions from the current record and optional source specs."""
    labels = {d['id']: f'D{i:03}' for i, d in enumerate(sorted(doe['data'], key=lambda d: d['id']), 1)}
    annotation = audit['annotation'] if audit is not None else None
    declarations = {(value['kind'], value['name']): key for key, value in doe['locations'].items()}
    sink_index = {(item['instruction_id'], item['event_index'], item['body_event_index'], item['op_index']): item
                  for item in doe['sink_boundaries']}
    boundary_rows = []
    rows = []
    for block_id, block in doe['cfg']['blocks'].items():
        for ir in block['instructions']:
            ir_id = ir['id']
            record = doe['records'].get(ir_id)
            if record is None:
                continue
            spec = annotation['transfer_specs'][ir_id] if annotation is not None else None
            stages = []
            scopes = []
            def add_event(event, declaration, prefix, scope=None, event_index=None, body_index=None):
                for j, op in enumerate(event['atomic_ops']):
                    atomic_spec = declaration['atomic_ops'][j] if declaration is not None else None
                    controls = {member['when_input_index'] for member in op.get('members', [])
                                if member['when_input_index'] is not None}
                    condition = op.get('when_input_index')
                    condition_state = None
                    if condition is not None:
                        controls.add(condition)
                        truths = guard_truths(doe['data'], op['inputs'][condition])
                        condition_state = ('加入／观察' if truths == {True} else '省略／不观察'
                                           if truths == {False} else '保留加入与省略的可能')
                    members = []
                    for member in op.get('members', []):
                        value, guard = member['value_input_index'], member['when_input_index']
                        truths = guard_truths(doe['data'], op['inputs'][guard]) if guard is not None else {True}
                        members.append({**member, 'presence': ('加入原值' if truths == {True} else '省略'
                                        if truths == {False} else '加入／省略两种候选')})
                    label = ('model_observe（程序生成，静态可能）' if event['effect'] == 'model_observe'
                             else event['effect'] or '无标签数据操作')
                    stages.append({'position': f'{prefix}.{j + 1}', 'effect': event['effect'],
                                   'effect_label': label, 'op': op, 'spec': atomic_spec, 'scope': scope,
                                   'controls': controls, 'members': members, 'condition_state': condition_state})
                    if op['op'] in {'deliver', 'write'}:
                        target = declarations[(op['endpoints'][0]['kind'], op['endpoints'][0]['name'])]
                        location = doe['locations'][target]
                        sink = sink_index.get((ir_id, event_index, body_index, j))
                        deleting = op['op'] == 'write' and not op['inputs']
                        omitted = condition is not None and not payload_inputs(op)
                        if omitted:
                            # The inventory coordinate represents a may-union
                            # across member candidates, not every instance.
                            sink = None
                        level = exposure_level(location)
                        if sink is not None:
                            rationale = {1: '任务内部、跨任务留存', 2: '另一接收主体或跨主体共享',
                                         3: '公开可读或公开发布'}[sink['exposure_level']]
                        else:
                            rationale = ('条件为假，未消费或观察成员值；控制槽不属于载荷' if omitted else
                                         '解除绑定或删除，不保存内容' if deleting else '任务内部且任务期限内，等级 0')
                        boundary_rows.append({'ir': ir_id, 'position': f'{prefix}.{j + 1}',
                            'target': target, 'location': location, 'effect': event['effect'],
                            'op': op['op'], 'inputs': payload_inputs(op), 'scope': scope,
                            'included': sink is not None, 'sink_type': sink['sink_type'] if sink else None,
                            'level': None if deleting or omitted else level, 'rationale': rationale,
                            'evidence_refs': [(value['basis'], value['ref_id']) for value in audit['location_evidences'][target]]
                                             if audit is not None else []})
            for i, event in enumerate(record['events']):
                declaration = spec['events'][i] if spec is not None else None
                if event.get('kind') == 'for_each':
                    scopes.append({'position': i + 1, 'collections': event['collections'], 'instances': event['instances']})
                    for k, instance in enumerate(event['instances']):
                        scope = {key: instance[key] for key in ('collection', 'element')}
                        for b, child in enumerate(instance['body']):
                            add_event(child, declaration['body'][b] if declaration is not None else None,
                                      f'{i + 1}.候选组{k + 1}.{b + 1}', scope, i, b)
                else:
                    add_event(event, declaration, str(i + 1), event_index=i)
            rows.append({'id': ir_id, 'block': block_id, 'ir': ir, 'record': record, 'action': doe['actions'][ir_id],
                         'stages': stages, 'scopes': scopes, 'changes': _changes(record),
                         'profile': annotation['profiles'][ir_id] if annotation is not None else None,
                         'output_bindings': spec['output_bindings'] if spec is not None else None})
    return {**{key: doe[key] for key in ('status', 'source', 'locations', 'coverage', 'diagnostics', 'execution_model')},
            'data': sorted(doe['data'], key=lambda d: d['id']), 'labels': labels, 'rows': rows, 'audit': audit,
            'boundary_rows': boundary_rows, 'sink_boundaries': doe['sink_boundaries'],
            'contract_notice': CONTRACT_NOTICE,
            'ir_total': sum(len(block['instructions']) for block in doe['cfg']['blocks'].values())}


def _parameters(spec):
    names = {'path': '选取路径', 'paths': '排除路径', 'dependencies': '依赖', 'updates': '字段覆盖',
             'parts': '组成', 'mode': '写入方式', 'container': '容器', 'predicate': '筛选条件（未求值）'}
    return {names[key]: spec[key] for key in names if key in spec}


def render_markdown(doe, *, audit=None, doe_href='doe-input.json', material_href=None):
    view = build_view(doe, audit=audit)
    ids = lambda values: ', '.join(view['labels'][key] for key in values) or '未绑定'
    cell = lambda value: escape(str(value)).replace('|', '&#124;').replace('\n', ' ')
    detail = lambda title, value: ['<details><summary>' + escape(title) + '</summary>', '', '<pre>' + escape(_json(value)) + '</pre>', '', '</details>', '']
    lines = ['# 基础数据传播记录', '',
             '**' + view['contract_notice'] + '**', '',
             f"统一契约：`{cell(view['execution_model']['version'])}`；SHA-256：`{cell(view['execution_model']['sha256'])}`。", '',
             f"求解状态：`{view['status']}`。", '',
             f"IR 记录覆盖：{len(view['rows'])} / {view['ir_total']}。", '',
             f'[本地可视化审查](report.html) · [唯一业务结果]({doe_href})', '',
             'D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。标为“控制”的槽只决定字段加入或观察是否发生，不属于该交付的载荷。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。', '']
    if material_href is not None:
        lines += [f'[冻结契约全文与标注输入]({material_href})（execution_model）；逐项依据在下方审计区展开。', '']
    lines += ['## 接收与保存边界', '',
              f"纳入清单 {len(view['sink_boundaries'])} 个操作位置；逐元素候选组分别显示参数，清单按既有作用域位置登记。",
              '', '等级仅表示边界性质：0 任务内临时，1 任务内持久，2 另一主体／共享，3 公开。它不表示数据敏感度、必要性或最终风险。未求值操作由覆盖表指明；空参数不等于未建模内容不存在。', '',
              '| IR / 步骤 | 纳入 | 类型 / 等级 | 目标、访问 / 留存 | 实际参数（逐位置） | 原因与属性依据 |',
              '|---|---|---|---|---|---|']
    for boundary in view['boundary_rows']:
        loc = boundary['location']
        inputs = '; '.join(f'{i}: {ids(values)}' for i, values in enumerate(boundary['inputs'])) or '无已建模参数'
        if boundary['scope'] is not None:
            inputs = '同一元素 ' + ids([boundary['scope']['element']]) + '；' + inputs
        reason = boundary['rationale'] + '；' + (', '.join(basis + '/' + ref for basis, ref in boundary['evidence_refs']) or '属性依据见独立审计材料')
        values = [boundary['ir'] + ' / ' + boundary['position'], '纳入' if boundary['included'] else '排除',
                  (boundary['sink_type'] or '—') + ' / ' + str(boundary['level'] if boundary['level'] is not None else '不适用'),
                  boundary['target'] + ' · ' + _location(loc) + ' · ' + loc['access_scope'] + ' / ' + (loc['retention'] or '未建模期限'), inputs, reason]
        lines.append('| ' + ' | '.join(cell(value) for value in values) + ' |')
    if not view['boundary_rows']:
        lines.append('| — | — | — | — | — | 没有形成记录的交付或保存操作，不据此宣布无暴露 |')
    lines.append('')
    lines += detail('完整源文', view['source']) + detail('覆盖与诊断', {key: view[key] for key in ('coverage', 'diagnostics')})
    for row in view['rows']:
        lines += [f"## {cell(row['id'])} · {cell(row['ir']['opcode'])}", '',
                  f"块：{cell(row['block'])}；执行主体：{cell(', '.join(row['action']['operator']) or '[]')}；角色：{cell(', '.join(row['action']['roles']) or '[]')}。", '',
                  'IR 输入：' + cell(_operands(row['ir'].get('inputs', []))), '', 'IR 输出：' + cell(_operands(row['ir'].get('outputs', []))), '']
        if row['record']['order'] == 'partial':
            lines += ['**部分顺序：按必要先后约束汇合可能排列，表中位置不代表唯一执行次序。**', '']
        lines += detail('顺序及必要先后约束', {key: row['record'][key] for key in ('order', 'precedence')})
        for scope in row['scopes']:
            lines += [f"逐元素作用域 {scope['position']}：集合候选 {ids(scope['collections'])}。以下各候选组单独绑定同一个元素，不能跨组组合参数；不是实际执行次数。", '']
            for k, instance in enumerate(scope['instances']):
                lines += [f"- 候选组 {k + 1}：集合 {ids([instance['collection']])} → 元素 {ids([instance['element']])}。"]
            if not scope['instances']:
                lines += ['- 没有成员候选；不能据此泛化为未知集合为空。']
            lines += ['']
        lines += ['| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |', '|---|---|---|---|---|---|']
        for stage in row['stages']:
            op = stage['op']
            inputs = '; '.join(f'{i}{"（控制）" if i in stage["controls"] else ""}: {ids(v)}'
                               for i, v in enumerate(op['inputs'])) or '—'
            if stage['condition_state']:
                inputs += '；条件：' + stage['condition_state']
            outputs = [f'{i}: {ids(v)}' for i, v in enumerate(op['outputs'])]
            outputs += [f"{_location(c['location'])}: {ids(c['before'])} → {ids(c['after'])} ({c['update']})" for c in op['changes']]
            values = [stage['position'], stage['effect_label'], op['op'], inputs,
                      '; '.join(_location(p) for p in op['endpoints']) or '—', '; '.join(outputs) or '—']
            lines.append('| ' + ' | '.join(cell(value) for value in values) + ' |')
            for member in stage['members']:
                lines.append('| ' + cell(stage['position'] + ' · 成员') + ' | — | ' + cell(_json(member['path']))
                             + ' | ' + cell('原值槽 ' + str(member['value_input_index']) + '；条件槽 '
                                           + str(member['when_input_index'])) + ' | — | ' + cell(member['presence']) + ' |')
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
        if 'raw_annotation' in audit:
            lines += detail('编译审计：模型原始处理段与程序生成位置映射',
                            {k: audit[k] for k in ('raw_annotation', 'compilation_map', 'compilation')})
    return '\n'.join(lines) + '\n'


def render_html(doe, *, audit=None, doe_href='doe-input.json', material_href=None):
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
    body = ['<h1>基础数据传播审查</h1><p class="notice">' + escape(view['contract_notice']) + '</p>',
            '<p>统一契约：<code>' + escape(view['execution_model']['version']) + '</code>；SHA-256：<code>'
            + escape(view['execution_model']['sha256']) + '</code>。</p>',
            '<p>求解状态：<strong>' + escape(view['status']) + '</strong></p>',
            f"<p>IR 记录覆盖：{len(view['rows'])} / {view['ir_total']}。</p>",
            '<p><a href="' + escape(doe_href, quote=True) + '">唯一业务结果 doe-input.json</a></p>',
            '<p>点击 D 编号查看数据版本。表中参数编号属于原子操作，不是原 IR 操作数编号。控制槽只决定成员加入或观察是否发生，不属于该交付的载荷。候选集合不表示同时发生，possible 依赖不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。</p>',
            details('完整源文', pre(view['source']), 'source'), details('覆盖与诊断', pre({k: view[k] for k in ('coverage', 'diagnostics')}))]
    if material_href is not None:
        body.append('<p><a href="' + escape(material_href, quote=True) + '">冻结契约全文与标注输入</a>'
                    '（execution_model）；逐项依据在下方审计区展开。</p>')
    body += ['<h2>接收与保存边界</h2>',
             '<p>纳入清单 ' + str(len(view['sink_boundaries'])) + ' 个操作位置。等级仅表示边界性质：0 任务内临时，1 任务内持久，2 另一主体／共享，3 公开；不是敏感度、必要性或最终风险。工具默认接收可能性不等于网络通信。未求值操作见覆盖表。</p>',
             '<table class="boundaries"><thead><tr>' + ''.join('<th>' + value + '</th>' for value in ('IR / 步骤', '纳入 / 类型 / 等级', '目标、访问 / 留存', '实际参数与数据版本', '原因与属性依据')) + '</tr></thead><tbody>']
    for boundary in view['boundary_rows']:
        loc = boundary['location']
        inputs = bindings(boundary['inputs']) if boundary['inputs'] else '无已建模参数'
        if boundary['scope'] is not None:
            inputs = '同一元素 ' + ids([boundary['scope']['element']]) + '<br>' + inputs
        refs = ', '.join(basis + '/' + ref for basis, ref in boundary['evidence_refs']) or '属性依据见独立审计材料'
        values = [escape(boundary['ir'] + ' / ' + boundary['position']),
                  ('纳入' if boundary['included'] else '排除') + '<br>' + escape(boundary['sink_type'] or '—') + '<br>等级 ' + str(boundary['level'] if boundary['level'] is not None else '不适用'),
                  escape(boundary['target'] + ' · ' + _location(loc)) + '<br>' + escape(loc['access_scope'] + ' / ' + (loc['retention'] or '未建模期限')),
                  inputs, escape(boundary['rationale']) + '<br><small>' + escape(refs) + '</small>']
        body.append('<tr>' + ''.join('<td>' + value + '</td>' for value in values) + '</tr>')
    if not view['boundary_rows']:
        body.append('<tr><td colspan="5">没有形成记录的交付或保存操作；不能据此宣布无暴露。</td></tr>')
    body.append('</tbody></table>')
    for row in view['rows']:
        ir, action = row['ir'], row['action']
        body += ['<section><h2>' + escape(row['id'] + ' · ' + ir['opcode']) + '</h2><p class="muted">块 ' + escape(row['block']) + '</p>',
                 '<p><b>IR 输入：</b>' + escape(_operands(ir.get('inputs', []))) + '<br><b>IR 输出：</b>' + escape(_operands(ir.get('outputs', []))) + '</p>',
                 '<p><b>执行主体（operator）：</b>' + escape(', '.join(action['operator']) or '[]') + '　<b>roles：</b>' + escape(', '.join(action['roles']) or '[]') + '</p>']
        if row['record']['order'] == 'partial':
            body.append('<p class="notice">部分顺序：按必要先后约束汇合可能排列，表中位置不代表唯一执行次序。</p>')
        body.append(details('顺序及必要先后约束', pre({key: row['record'][key] for key in ('order', 'precedence')})))
        for scope in row['scopes']:
            body.append('<div class="notice"><b>逐元素作用域 ' + str(scope['position']) + '</b>：集合候选 ' + ids(scope['collections']) + '。每个候选组保持同一元素配对，不跨组拼接参数；候选组不是实际执行次数。<ul>')
            for k, instance in enumerate(scope['instances']):
                body.append('<li>候选组 ' + str(k + 1) + '：集合 ' + ids([instance['collection']]) + ' → 元素 ' + ids([instance['element']]) + '</li>')
            body.append('</ul></div>')
        body.append('<table class="stages"><thead><tr>' + ''.join('<th>' + s + '</th>' for s in ('位置', '效果', 'op', '实际输入数据', '交互边界', '输出或状态变化')) + '</tr></thead><tbody>')
        audits = []
        for stage in row['stages']:
            op = stage['op']
            changes = [escape(_location(c['location'])) + '<br>' + ids(c['before']) + ' → ' + ids(c['after']) + ' <small>' + escape(c['update']) + '</small>' for c in op['changes']]
            outputs = '<br>'.join(([bindings(op['outputs'])] if op['outputs'] else []) + changes) or '—'
            inputs = '<br>'.join(f'<span class="muted">{i}{"（控制）" if i in stage["controls"] else ""}:</span> '
                                + ids(values) for i, values in enumerate(op['inputs'])) or '—'
            if stage['condition_state']:
                inputs += '<br>条件：' + escape(stage['condition_state'])
            cells = [stage['position'], escape(stage['effect_label']), escape(op['op']), inputs,
                     '<br>'.join(escape(_location(p)) for p in op['endpoints']) or '—', outputs]
            body.append('<tr>' + ''.join('<td>' + value + '</td>' for value in cells) + '</tr>')
            for member in stage['members']:
                body.append('<tr><td>' + escape(stage['position'] + ' · 成员') + '</td><td>—</td><td>'
                            + escape(_json(member['path'])) + '</td><td>'
                            + escape('原值槽 ' + str(member['value_input_index']) + '；条件槽 '
                                     + str(member['when_input_index'])) + '</td><td>—</td><td>'
                            + escape(member['presence']) + '</td></tr>')
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
        if content['form'] == 'subset_view':
            body += ['<p>原集合的子集视图：成员内容保持，筛选条件尚未求值，不表示已确定哪些成员被选中。</p>', pre(content['predicate'])]
        if data['origin'].get('part_of'):
            body += ['<p>所属整体：' + ids([data['origin']['part_of']]) + '</p>', pre(data['origin']['path'])]
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
        if 'raw_annotation' in audit:
            body += [details('编译审计：模型原始处理段与程序生成位置映射',
                             pre({k: audit[k] for k in ('raw_annotation', 'compilation_map', 'compilation')}))]
    return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'none'; connect-src 'none'">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>基础数据传播审查</title>
<style>body{font:15px/1.65 'Microsoft YaHei',sans-serif;max-width:1450px;margin:26px auto;padding:0 22px;color:#23364a;background:#f5f8fa}section{background:white;border:1px solid #d8e2ec;padding:22px;margin:24px 0}h1,h2{color:#123f55}table{border-collapse:collapse;width:100%;table-layout:fixed;margin:14px 0}th,td{text-align:left;vertical-align:top;border:1px solid #d8e2ec;padding:10px;overflow-wrap:anywhere;white-space:pre-wrap}th{background:#e9f1f6;font-size:13px}td{font-size:13px}.stages th:first-child{width:5%}.stages th:nth-child(2){width:12%}.stages th:nth-child(3){width:13%}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.6 Consolas,'Microsoft YaHei',monospace;background:#edf2f7;padding:14px}details{margin:12px 0}summary{cursor:pointer;font-weight:600;overflow-wrap:anywhere}.notice{background:#fff3d4;padding:12px}.muted,small{color:#60788b}.data{font-family:Consolas,monospace;font-weight:bold;color:#087284}.identifier{font:12px Consolas,monospace;overflow-wrap:anywhere}.data-card{background:white;border:1px solid #d8e2ec;padding:16px}.data-card:target{border:3px solid #e4a73a}blockquote{white-space:pre-wrap;overflow-wrap:anywhere;border-left:3px solid #769eb1;padding:10px;background:#f1f6fa}a{color:#126980}</style><body>''' + ''.join(body) + '</body></html>'


def write_reports(directory: Path, doe, writer, *, audit=None):
    href = '../doe-input.json' if directory.name == 'replay' else 'doe-input.json'
    material_href = (('../' if directory.name == 'replay' else '') + 'audit/material.json') if audit is not None else None
    writer.text(directory / 'report.md', render_markdown(doe, audit=audit, doe_href=href, material_href=material_href))
    writer.text(directory / 'report.html', render_html(doe, audit=audit, doe_href=href, material_href=material_href))
