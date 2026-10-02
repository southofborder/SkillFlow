"""Read-only comparison of business facts; never migrate a prior DOE artifact."""
from collections import Counter
from html import escape
import json
from pathlib import Path

from skill_ir.experiments.report import ArtifactWriter
from skill_ir.recording import read_json
from skill_ir.propagation.conditions import payload_inputs


def operation_rows(doe):
    for ir_id, record in doe.get('records', {}).items():
        for e, event in enumerate(record['events']):
            if event.get('kind') == 'for_each':
                for group, instance in enumerate(event['instances']):
                    for b, child in enumerate(instance['body']):
                        for o, op in enumerate(child['atomic_ops']):
                            yield ir_id, f'{e}.{b}.{o} / 元素候选 {group}', child['effect'], op
            else:
                for o, op in enumerate(event['atomic_ops']):
                    yield ir_id, f'{e}.{o}', event['effect'], op


def _data_relation(doe, data_id):
    data = {item['id']: item for item in doe['data']}[data_id]
    content, origin = data['content'], data['origin']
    if origin.get('part_of'):
        return '原部分 ' + json.dumps(origin['path'], ensure_ascii=False)
    if content['form'] == 'literal':
        return '字面值 ' + json.dumps(content['value'], ensure_ascii=False)
    return content['form'] + (('；来源 ' + origin['acquired_from']) if origin.get('acquired_from') else '')


def write_comparison(base: Path, case: dict):
    """Display changed field families and actual requests, keeping evidence aside."""
    current_path = base / 'propagation/doe-input.json'
    prior_path = Path(case['prior_run']) / 'propagation/doe-input.json'
    result_path = base / 'result.json'
    if not result_path.exists():
        return
    outcome = read_json(result_path)
    current = read_json(current_path) if (base / 'propagation/manifest.json').exists() else None
    prior = read_json(prior_path) if case['prior_doe_sha256'] is not None else None
    lines = ['# DOE 变化对照：' + case['case_id'] + ' / ' + case['sample_id'], '',
             '本页只比较实际事实文件。历史文件按原始 JSON 只读查看，不用新版加载器迁移；数据按来源和关系对应，不要求跨运行 ID 相同。', '',
             '## 文件结构', '',
             '```text', 'DOE 顶层业务区：保持不变',
             'locations：继续保留 access_scope、retention',
             'sink_boundaries：继续保留操作坐标、目标、类型和固定等级',
             'records[IR].events[].atomic_ops[]',
             '├─ build.members[]', '│  ├─ path：原业务字段位置',
             '│  ├─ value_input_index：原值输入槽；确定省略时 null',
             '│  └─ when_input_index：控制槽；无条件时 null',
             '└─ 条件 model_observe.when_input_index：控制槽，不能计入观察载荷',
             '```', '', '这些字段只出现在适用操作。Data 保持 v4 的四个外层字段；证据链不进入 DOE。', '']
    if current is None:
        lines += ['## 最新状态', '', '未生成可用的新 DOE 文件。', '',
                  '标注：`' + outcome['annotation']['status'] + '`；传播：`' + outcome['propagation'] + '`。', '',
                  str(outcome['annotation'].get('reason') or outcome.get('propagation_error') or '本阶段未完成。'), '',
                  '未生成不能解释为没有 sink，也不以历史成功文件代替。']
    else:
        if prior is not None and prior['cfg'] != current['cfg']:
            raise ValueError('comparison detected a changed frozen CFG')
        lines += ['## 边界及记录变化', '',
                  '| 项目 | 上轮 | 本轮 |', '|---|---|---|',
                  '| DOE 版本 | ' + (prior['schema_version'] if prior else '上轮无有效 DOE') + ' | ' + current['schema_version'] + ' |',
                  '| 传播状态 | ' + (prior['status'] if prior else '未执行') + ' | ' + current['status'] + ' |',
                  '| Data 数量 | ' + (str(len(prior['data'])) if prior else '—') + ' | ' + str(len(current['data'])) + ' |',
                  '| sink 类型数量 | ' + (str(dict(Counter(x['sink_type'] for x in prior['sink_boundaries']))) if prior else '—')
                  + ' | ' + str(dict(Counter(x['sink_type'] for x in current['sink_boundaries']))) + ' |', '',
                  '| IR / 操作坐标 | 目标 | 类型 | 等级 |', '|---|---|---|---|']
        for sink in current['sink_boundaries']:
            pos = '.'.join(str(v) for v in (sink['event_index'], sink['body_event_index'], sink['op_index']) if v is not None)
            lines.append('| ' + ' | '.join([sink['instruction_id'] + ' / ' + pos, sink['target'], sink['sink_type'], str(sink['exposure_level'])]) + ' |')
        lines += ['', '## 实际构造与控制关系', '',
                  '下表槽位来自新 DOE 本身；参数原值与存在性控制分开。抽象布尔保留出现／省略候选，不表示所有候选同时发出。', '',
                  '| IR / 操作 | 字段 | 原值槽及关系 | 条件槽及关系 |', '|---|---|---|---|']
        builds, guards = 0, 0
        for ir_id, position, effect, op in operation_rows(current):
            for member in op.get('members', []):
                builds += 1
                def slot(index):
                    if index is None: return 'null'
                    return str(index) + '：' + '、'.join(_data_relation(current, data) for data in op['inputs'][index])
                values = [ir_id + ' / ' + position, json.dumps(member['path'], ensure_ascii=False),
                          slot(member['value_input_index']), slot(member['when_input_index'])]
                lines.append('| ' + ' | '.join(escape(value).replace('|', '&#124;') for value in values) + ' |')
            if op.get('when_input_index') is not None:
                guards += 1
        if not builds: lines.append('| — | 本轮没有构造成员记录 | — | — |')
        lines += ['', f'程序生成的条件观察记录：{guards} 项。只有载荷槽进入 sink；确定省略时不生成实际 sink。', '',
                  '## 请求交付与响应获取', '',
                  '| IR | 交付参数关系 | 获取请求关系 | 是否复用同一实际绑定 |', '|---|---|---|---|']
        pairs = 0
        for ir_id, record in current['records'].items():
            pending = {}
            for rid, position, effect, op in operation_rows({'records': {ir_id: record}}):
                if len(op['endpoints']) != 1: continue
                endpoint = op['endpoints'][0]
                if endpoint['kind'] not in {'tool', 'remote'}: continue
                key = endpoint['kind'], endpoint['name']
                if op['op'] == 'deliver': pending.setdefault(key, []).append(op)
                elif op['op'] == 'receive':
                    matched = [item for item in pending.get(key, []) if payload_inputs(item) == op['inputs']]
                    if len(matched) != 1: continue
                    pairs += 1
                    pending[key].remove(matched[0])
                    relations = '; '.join(str(i) + ': ' + '、'.join(_data_relation(current, value) for value in ids)
                                          for i, ids in enumerate(op['inputs'])) or '零参数'
                    lines.append('| ' + ir_id + ' | ' + escape(relations).replace('|', '&#124;') + ' | 同左 | 是 |')
        if not pairs: lines.append('| — | 无已求值的精确配对 | — | 不按相似名称推断 |')
        lines += ['', '## 仍需注意', '',
                  '文件加载、编译和传播一致不证明模型关系判断正确。具体漏标、误标及本轮剩余问题见 [助手复核](assistant-review.md)。', '',
                  '[新 DOE 原始文件](propagation/doe-input.json) · [数据与边界审查](propagation/report.html)', '']
    writer = ArtifactWriter(())
    writer.text(base / 'doe-input-change.md', '\n'.join(lines) + '\n')
    # Escaped preformatted comparison preserves exact rows without interpreting
    # Skill content as HTML. The primary propagation report stays interactive.
    writer.text(base / 'doe-input-change.html', '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>DOE 变化对照</title>'
        '<style>body{font:16px/1.6 "Microsoft YaHei",sans-serif;margin:30px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'
        '<body><p><a href="../../index.html">返回总览</a> · <a href="doe-input-change.md">Markdown</a></p><pre>'
        + escape('\n'.join(lines)) + '</pre></body></html>')
