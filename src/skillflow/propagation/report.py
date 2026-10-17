"""One business view model for Markdown and HTML propagation review."""
from __future__ import annotations
from html import escape
import json
import os
from pathlib import Path

from skillflow.common.upstream import checked_run_path
from skillflow.propagation.contracts.boundaries import exposure_level
from skillflow.propagation.conditions import guard_truths
from skillflow.propagation.conditions import payload_inputs


CONTRACT_NOTICE = (
    'These records describe static possible behavior under the shared abstract runtime contract, not execution logs. '
    'complete means only that solving finished under the contract, not that the model actually observed this content. '
    'Default observations and explicit exceptions jointly constrain analysis. Fixed ordering or absence of a contract citation does not establish an observed runtime fact.'
)


def _evidence_label(value):
    if 'rule_id' in value:
        return value['rule_id']
    if 'target' in value:
        return json.dumps(value['target'], ensure_ascii=False, separators=(',', ':'))
    return f"{value['file']}:{value['start_line']}-{value['end_line']}"


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


def _audit_view(facts):
    return {"material": facts.material, "annotation": facts.compiled_annotation,
            "location_evidences": facts.compiled_annotation["location_evidences"],
            "stats": facts.stats, "raw_annotation": facts.raw_annotation, "compilation_map": facts.mapping}


def build_view(facts):
    """Resolve presentation positions from the current record and optional source specs."""
    audit = _audit_view(facts)
    labels = {d['id']: f'D{i:03}' for i, d in enumerate(sorted(facts.data, key=lambda d: d['id']), 1)}
    annotation = audit['annotation'] if audit is not None else None
    declarations = {(value['kind'], value['name']): key for key, value in facts.locations.items()}
    sink_index = {(item['instruction_id'], item['event_index'], item['body_event_index'], item['op_index']): item
                  for item in facts.sinks}
    boundary_rows = []
    rows = []
    for block_id, block in facts.cfg['blocks'].items():
        for ir in block['instructions']:
            ir_id = ir['id']
            record = facts.records.get(ir_id)
            if record is None:
                continue
            spec = annotation['ir_semantics'][ir_id] if annotation is not None else None
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
                        truths = guard_truths(facts.data, op['inputs'][condition])
                        condition_state = ('Include / observe' if truths == {True} else 'Omit / do not observe'
                                           if truths == {False} else 'Retain both inclusion and omission possibilities')
                    members = []
                    for member in op.get('members', []):
                        value, guard = member['value_input_index'], member['when_input_index']
                        truths = guard_truths(facts.data, op['inputs'][guard]) if guard is not None else {True}
                        members.append({**member, 'presence': ('Include original value' if truths == {True} else 'Omit'
                                        if truths == {False} else 'Inclusion / omission candidates')})
                    label = ('model_observe (program-generated, statically possible)' if event['effect'] == 'model_observe'
                             else event['effect'] or 'Unlabeled data operation')
                    stages.append({'position': f'{prefix}.{j + 1}', 'effect': event['effect'],
                                   'effect_label': label, 'op': op, 'spec': atomic_spec, 'scope': scope,
                                   'controls': controls, 'members': members, 'condition_state': condition_state})
                    if op['op'] in {'deliver', 'write'}:
                        target = declarations[(op['endpoints'][0]['kind'], op['endpoints'][0]['name'])]
                        location = facts.locations[target]
                        sink = sink_index.get((ir_id, event_index, body_index, j))
                        deleting = op['op'] == 'write' and not op['inputs']
                        omitted = condition is not None and not payload_inputs(op)
                        if omitted:
                            # The inventory coordinate represents a may-union
                            # across member candidates, not every instance.
                            sink = None
                        level = exposure_level(location)
                        if sink is not None:
                            rationale = {1: 'Task-internal, retained across tasks', 2: 'Another recipient or cross-principal sharing',
                                         3: 'Publicly readable or published'}[sink['exposure_level']]
                        else:
                            rationale = ('Condition is false: member value is neither consumed nor observed; control slots are not payload' if omitted else
                                         'Unbind or delete; no content is saved' if deleting else 'Task-internal and task-lifetime, level 0')
                        boundary_rows.append({'ir': ir_id, 'position': f'{prefix}.{j + 1}',
                            'target': target, 'location': location, 'effect': event['effect'],
                            'op': op['op'], 'inputs': payload_inputs(op), 'scope': scope,
                            'included': sink is not None, 'sink_type': sink['sink_type'] if sink else None,
                            'level': None if deleting or omitted else level, 'rationale': rationale,
                            'evidence_refs': [_evidence_label(value) for value in audit['location_evidences'][target]]
                                             if audit is not None else []})
            for i, event in enumerate(record['events']):
                declaration = spec['events'][i] if spec is not None else None
                if event.get('kind') == 'for_each':
                    scopes.append({'position': i + 1, 'collections': event['collections'], 'instances': event['instances']})
                    for k, instance in enumerate(event['instances']):
                        scope = {key: instance[key] for key in ('collection', 'element')}
                        for b, child in enumerate(instance['body']):
                            add_event(child, declaration['body'][b] if declaration is not None else None,
                                      f'{i + 1}.Candidate group{k + 1}.{b + 1}', scope, i, b)
                else:
                    add_event(event, declaration, str(i + 1), event_index=i)
            rows.append({'id': ir_id, 'block': block_id, 'ir': ir, 'record': record, 'action': facts.actions[ir_id],
                         'stages': stages, 'scopes': scopes, 'changes': _changes(record),
                         'ir_semantics': annotation['ir_semantics'][ir_id] if annotation is not None else None,
                         'output_bindings': spec['output_bindings'] if spec is not None else None})
    from skillflow.propagation.contracts.runtime_contract import runtime_contract_binding
    return {**{key: getattr(facts, key) for key in ('status', 'source', 'locations', 'coverage', 'diagnostics')},
            'runtime_contract': runtime_contract_binding(facts.runtime_contract),
            'data': sorted(facts.data, key=lambda d: d['id']), 'labels': labels, 'rows': rows, 'audit': audit,
            'boundary_rows': boundary_rows, 'sink_boundaries': facts.sinks,
            'contract_notice': CONTRACT_NOTICE,
            'ir_total': sum(len(block['instructions']) for block in facts.cfg['blocks'].values())}


def _parameters(spec):
    names = {'path': 'Selected path', 'paths': 'Excluded paths', 'dependencies': 'Dependencies', 'updates': 'Field overrides',
             'parts': 'Composition', 'mode': 'Write mode', 'container': 'Container', 'predicate': 'Filter condition (not evaluated)'}
    return {names[key]: spec[key] for key in names if key in spec}


def render_markdown(facts, *, facts_prefix='', material_href=None):
    view = build_view(facts)
    audit = view['audit']
    ids = lambda values: ', '.join(view['labels'][key] for key in values) or 'Unbound'
    cell = lambda value: escape(str(value)).replace('|', '&#124;').replace('\n', ' ')
    detail = lambda title, value: ['<details><summary>' + escape(title) + '</summary>', '', '<pre>' + escape(_json(value)) + '</pre>', '', '</details>', '']
    lines = ['# Basic data propagation records', '',
             '**' + view['contract_notice'] + '**', '',
             f"Shared contract: `{cell(view['runtime_contract']['version'])}`; SHA-256: `{cell(view['runtime_contract']['sha256'])}`.", '',
             f"Solver status: `{view['status']}`.", '',
             f"IR record coverage: {len(view['rows'])} / {view['ir_total']}.", '',
             f'[Local visual review](report.html) · [Data]({facts_prefix}data.json) · [Operation records]({facts_prefix}records.json) · [Sink list]({facts_prefix}sinks.json)', '',
             'D labels are report-local short names. Input/output indexes refer to atomic-operation arguments, not original IR operands. Control slots determine inclusion or observation and are not delivered payload. Candidate sets do not imply simultaneous occurrence; possible does not imply complete plaintext inclusion. This stage makes no risk, necessity or DOE judgment. Read scope, model observation, explicit selection and actual arguments are reviewed separately; a tool boundary does not imply networking.', '']
    if material_href is not None:
        lines += [f'[Frozen runtime contract text]({material_href}) (runtime_contract); Expand the audit section below for individual evidence.', '']
    lines += ['## Receiving and storage boundaries', '',
              f"Included positions: {len(view['sink_boundaries'])} operation positions; per-element candidate groups show arguments separately, using existing scope coordinates.",
              '', 'Levels describe boundary properties only: 0 task-local temporary, 1 task-local persistent, 2 another principal/shared, 3 public. They do not measure sensitivity, necessity or final risk. Coverage identifies unevaluated operations; empty arguments do not establish absence of unmodeled content.', '',
              '| IR / step | Included | Type / level | Target, access / retention | Actual arguments by slot | Rationale and property evidence |',
              '|---|---|---|---|---|---|']
    for boundary in view['boundary_rows']:
        loc = boundary['location']
        inputs = '; '.join(f'{i}: {ids(values)}' for i, values in enumerate(boundary['inputs'])) or 'No modeled arguments'
        if boundary['scope'] is not None:
            inputs = 'Same element ' + ids([boundary['scope']['element']]) + '; ' + inputs
        reason = boundary['rationale'] + '; ' + (', '.join(boundary['evidence_refs']) or 'Property evidence is in the separate audit materials')
        values = [boundary['ir'] + ' / ' + boundary['position'], 'Included' if boundary['included'] else 'Excluded',
                  (boundary['sink_type'] or '—') + ' / ' + str(boundary['level'] if boundary['level'] is not None else 'Not applicable'),
                  boundary['target'] + ' · ' + _location(loc) + ' · ' + loc['access_scope'] + ' / ' + (loc['retention'] or 'Retention period not modeled'), inputs, reason]
        lines.append('| ' + ' | '.join(cell(value) for value in values) + ' |')
    if not view['boundary_rows']:
        lines.append('| — | — | — | — | — | No delivery or storage operation has a record; this does not establish absence of exposure |')
    lines.append('')
    lines += detail('Complete source', view['source']) + detail('Coverage and diagnostics', {key: view[key] for key in ('coverage', 'diagnostics')})
    for row in view['rows']:
        lines += [f"## {cell(row['id'])} · {cell(row['ir']['opcode'])}", '',
                  f"Block: {cell(row['block'])}; Operator: {cell(', '.join(row['action']['operator']) or '[]')}.", '',
                  'IR inputs: ' + cell(_operands(row['ir'].get('inputs', []))), '', 'IR outputs: ' + cell(_operands(row['ir'].get('outputs', []))), '']
        if row['record']['order'] == 'partial':
            lines += ['**Partial order: possible permutations are joined subject to required precedence; table positions do not imply a unique execution order.**', '']
        lines += detail('Order and required precedence', {key: row['record'][key] for key in ('order', 'precedence')})
        for scope in row['scopes']:
            lines += [f"Per-element scope {scope['position']}: Collection candidates {ids(scope['collections'])}. Each candidate group independently binds the same element; arguments cannot be combined across groups. Groups are not actual execution counts.", '']
            for k, instance in enumerate(scope['instances']):
                lines += [f"- Candidate group {k + 1}: Collection {ids([instance['collection']])} → Element {ids([instance['element']])}."]
            if not scope['instances']:
                lines += ['- No member candidate; this does not establish that an unknown collection is empty.']
            lines += ['']
        lines += ['| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |', '|---|---|---|---|---|---|']
        for stage in row['stages']:
            op = stage['op']
            inputs = '; '.join(f'{i}{" (control)" if i in stage["controls"] else ""}: {ids(v)}'
                               for i, v in enumerate(op['inputs'])) or '—'
            if stage['condition_state']:
                inputs += '; Condition: ' + stage['condition_state']
            outputs = [f'{i}: {ids(v)}' for i, v in enumerate(op['outputs'])]
            outputs += [f"{_location(c['location'])}: {ids(c['before'])} → {ids(c['after'])} ({c['update']})" for c in op['changes']]
            values = [stage['position'], stage['effect_label'], op['op'], inputs,
                      '; '.join(_location(p) for p in op['endpoints']) or '—', '; '.join(outputs) or '—']
            lines.append('| ' + ' | '.join(cell(value) for value in values) + ' |')
            for member in stage['members']:
                lines.append('| ' + cell(stage['position'] + ' · Member') + ' | — | ' + cell(_json(member['path']))
                             + ' | ' + cell('Original-value slot ' + str(member['value_input_index']) + '; Condition slot '
                                           + str(member['when_input_index'])) + ' | — | ' + cell(member['presence']) + ' |')
        if not row['stages']:
            lines.append('| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |')
        lines += ['', 'Entry/exit changes: ', '']
        lines += [f"- `{cell(_location(c['location']))}`: {ids(c['before'])} → {ids(c['after'])}" for c in row['changes']] or ['- Location bindings are unchanged; this does not imply absence of observation or sending.']
        lines += ['', *detail('Complete entry and exit states', {k: row['record'][k] for k in ('entry_state', 'exit_state')})]
        if audit is not None:
            lines += detail('Original annotation audit: IR semantics, step arguments, output bindings and evidence',
                            {'ir_semantics': row['ir_semantics'], 'steps': [s['spec'] for s in row['stages']], 'output_bindings': row['output_bindings']})
    lines += ['## Data index', '', '| Short name | Complete ID | Content form |', '|---|---|---|']
    for data in view['data']:
        lines.append(f"| {view['labels'][data['id']]} | {cell(data['id'])} | {cell(data['content']['form'])} |")
    lines.append('')
    for data in view['data']:
        lines += detail(view['labels'][data['id']] + ': Complete Data content, origin and dependencies', data)
    if audit is not None:
        lines += ['', *detail('Separate audit materials: location evidence and solver statistics', {'location_evidences': audit['location_evidences'], 'stats': audit['stats']})]
        if 'raw_annotation' in audit:
            lines += detail('Compilation audit: original model processing segments and program-generated location mapping',
                            {k: audit[k] for k in ('raw_annotation', 'compilation_map')})
    return '\n'.join(lines) + '\n'


def render_html(facts, *, facts_prefix='', material_href=None):
    view = build_view(facts)
    audit = view['audit']
    labels = view['labels']
    def pre(value): return '<pre>' + escape(_json(value)) + '</pre>'
    def details(title, content, css=''):
        return '<details class="' + escape(css, quote=True) + '"><summary>' + escape(title) + '</summary>' + content + '</details>'
    def ids(values):
        return ', '.join(f'<a class="data" href="#data-{labels[k]}" title="{escape(k, quote=True)}">{labels[k]}</a>' for k in values) or '<span class="muted">Unbound</span>'
    def bindings(values):
        return '<br>'.join(f'<span class="muted">{i}:</span> ' + ids(v) for i, v in enumerate(values)) or '—'
    def evidence(values):
        from skillflow.propagation.material import evidence_reference
        rendered = []
        for e in values:
            excerpt = (evidence_reference(e, audit['material'])['text']
                       if audit is not None and 'material' in audit else 'See the source locations in the frozen materials.')
            rendered.append('<p class="muted">' + escape(_evidence_label(e))
                            + '</p><blockquote>' + escape(excerpt)
                            + '</blockquote><p>' + escape(e['reason']) + '</p>')
        return ''.join(rendered)
    body = ['<h1>Basic data propagation review</h1><p class="notice">' + escape(view['contract_notice']) + '</p>',
            '<p>Shared contract: <code>' + escape(view['runtime_contract']['version']) + '</code>; SHA-256: <code>'
            + escape(view['runtime_contract']['sha256']) + '</code>.</p>',
            '<p>Solver status: <strong>' + escape(view['status']) + '</strong></p>',
            f"<p>IR record coverage: {len(view['rows'])} / {view['ir_total']}.</p>",
            '<p>' + ' · '.join('<a href="' + escape(facts_prefix + name + '.json', quote=True) + '">' + label + '</a>' for name, label in [('data', 'Data'), ('records', 'Operation records'), ('sinks', 'Sink list')]) + '</p>',
            '<p>Select a D label to view its data version. Argument indexes belong to atomic operations, not original IR operands. Control slots determine member inclusion or observation and are not delivered payload. Candidate sets do not imply simultaneous occurrence; possible dependencies do not imply complete plaintext inclusion. This stage makes no risk, necessity or DOE judgment. Read scope, model observation, explicit selection and actual arguments are reviewed separately; tool boundaries do not imply networking.</p>',
            details('Complete source', pre(view['source']), 'source'), details('Coverage and diagnostics', pre({k: view[k] for k in ('coverage', 'diagnostics')}))]
    if material_href is not None:
        body.append('<p><a href="' + escape(material_href, quote=True) + '">Frozen runtime contract text</a>'
                    ' (runtime_contract); Expand the audit section below for individual evidence.</p>')
    body += ['<h2>Receiving and storage boundaries</h2>',
             '<p>Included positions: ' + str(len(view['sink_boundaries'])) + ' operation positions. Levels describe boundary properties: 0 task-local temporary, 1 task-local persistent, 2 another principal/shared, 3 public; they are not sensitivity, necessity or final risk. Default possible tool receipt does not imply networking. See coverage for unevaluated operations.</p>',
             '<table class="boundaries"><thead><tr>' + ''.join('<th>' + value + '</th>' for value in ('IR / Step', 'Included / Type / Level', 'Target, access / retention', 'Actual arguments and data versions', 'Rationale and property evidence')) + '</tr></thead><tbody>']
    for boundary in view['boundary_rows']:
        loc = boundary['location']
        inputs = bindings(boundary['inputs']) if boundary['inputs'] else 'No modeled arguments'
        if boundary['scope'] is not None:
            inputs = 'Same element ' + ids([boundary['scope']['element']]) + '<br>' + inputs
        refs = ', '.join(boundary['evidence_refs']) or 'Property evidence is in the separate audit materials'
        values = [escape(boundary['ir'] + ' / ' + boundary['position']),
                  ('Included' if boundary['included'] else 'Excluded') + '<br>' + escape(boundary['sink_type'] or '—') + '<br>Level ' + str(boundary['level'] if boundary['level'] is not None else 'Not applicable'),
                  escape(boundary['target'] + ' · ' + _location(loc)) + '<br>' + escape(loc['access_scope'] + ' / ' + (loc['retention'] or 'Retention period not modeled')),
                  inputs, escape(boundary['rationale']) + '<br><small>' + escape(refs) + '</small>']
        body.append('<tr>' + ''.join('<td>' + value + '</td>' for value in values) + '</tr>')
    if not view['boundary_rows']:
        body.append('<tr><td colspan="5">No delivery or storage operation has a record; this does not establish absence of exposure.</td></tr>')
    body.append('</tbody></table>')
    for row in view['rows']:
        ir, action = row['ir'], row['action']
        body += ['<section><h2>' + escape(row['id'] + ' · ' + ir['opcode']) + '</h2><p class="muted">Block ' + escape(row['block']) + '</p>',
                 '<p><b>IR inputs: </b>' + escape(_operands(ir.get('inputs', []))) + '<br><b>IR outputs: </b>' + escape(_operands(ir.get('outputs', []))) + '</p>',
                 '<p><b>Operator: </b>' + escape(', '.join(action['operator']) or '[]') + '</p>']
        if row['record']['order'] == 'partial':
            body.append('<p class="notice">Partial order: possible permutations are joined subject to required precedence; table positions do not imply a unique execution order.</p>')
        body.append(details('Order and required precedence', pre({key: row['record'][key] for key in ('order', 'precedence')})))
        for scope in row['scopes']:
            body.append('<div class="notice"><b>Per-element scope ' + str(scope['position']) + '</b>: Collection candidates ' + ids(scope['collections']) + '. Each candidate group preserves same-element pairing without cross-group arguments; groups are not actual execution counts.<ul>')
            for k, instance in enumerate(scope['instances']):
                body.append('<li>Candidate group ' + str(k + 1) + ': Collection ' + ids([instance['collection']]) + ' → Element ' + ids([instance['element']]) + '</li>')
            body.append('</ul></div>')
        body.append('<table class="stages"><thead><tr>' + ''.join('<th>' + s + '</th>' for s in ('Position', 'Effect', 'op', 'Actual input Data', 'Interaction boundary', 'Output or state change')) + '</tr></thead><tbody>')
        audits = []
        for stage in row['stages']:
            op = stage['op']
            changes = [escape(_location(c['location'])) + '<br>' + ids(c['before']) + ' → ' + ids(c['after']) + ' <small>' + escape(c['update']) + '</small>' for c in op['changes']]
            outputs = '<br>'.join(([bindings(op['outputs'])] if op['outputs'] else []) + changes) or '—'
            inputs = '<br>'.join(f'<span class="muted">{i}{" (control)" if i in stage["controls"] else ""}:</span> '
                                + ids(values) for i, values in enumerate(op['inputs'])) or '—'
            if stage['condition_state']:
                inputs += '<br>Condition: ' + escape(stage['condition_state'])
            cells = [stage['position'], escape(stage['effect_label']), escape(op['op']), inputs,
                     '<br>'.join(escape(_location(p)) for p in op['endpoints']) or '—', outputs]
            body.append('<tr>' + ''.join('<td>' + value + '</td>' for value in cells) + '</tr>')
            for member in stage['members']:
                body.append('<tr><td>' + escape(stage['position'] + ' · Member') + '</td><td>—</td><td>'
                            + escape(_json(member['path'])) + '</td><td>'
                            + escape('Original-value slot ' + str(member['value_input_index']) + '; Condition slot '
                                     + str(member['when_input_index'])) + '</td><td>—</td><td>'
                            + escape(member['presence']) + '</td></tr>')
            if audit is not None:
                audits.append(details(stage['position'] + ' · ' + op['op'] + ': Arguments and evidence', pre(_parameters(stage['spec'])) + evidence(stage['spec']['evidences']) + pre(stage['spec'])))
        if not row['stages']:
            body.append('<tr><td colspan="6">No effect events; public result locations and complete IN / OUT states remain available. Empty effects do not imply an empty operation.</td></tr>')
        body += ['</tbody></table><h3>IN / OUT differences</h3>']
        if row['changes']:
            body.append('<table><tr><th>Position</th><th>Entry</th><th>Exit</th></tr>')
            for c in row['changes']:
                body.append('<tr><td>' + escape(_location(c['location'])) + '</td><td>' + ids(c['before']) + '</td><td>' + ids(c['after']) + '</td></tr>')
            body.append('</table>')
        else:
            body.append('<p class="muted">Location bindings are unchanged; this does not imply absence of observation or sending.</p>')
        body.append(details('Complete entry and exit states', pre({k: row['record'][k] for k in ('entry_state', 'exit_state')})))
        if audit is not None:
            inner = [*audits, details('Public IR output bindings and evidence', pre(row['output_bindings']))]
            semantics = row['ir_semantics']
            for e in semantics['operator_evidences']:
                inner += ['<h4>Operator · ' + escape(e['value'] or 'Empty-label rationale') + '</h4>', evidence([e])]
            if semantics.get('empty_effect_evidences', []):
                inner += ['<h4>No-applicable-effect rationale</h4>', evidence(semantics.get('empty_effect_evidences', []))]
            for event in semantics['events']:
                events = event['body'] if event.get('kind') == 'for_each' else [event]
                for child in events:
                    if child.get('evidences', []):
                        inner += ['<h4>Effect · ' + escape(child['effect'] or 'Unlabeled') + '</h4>', evidence(child.get('evidences', []))]
            body.append(details('Original annotation audit: IR semantics, output bindings and evidence', ''.join(inner), 'annotation-audit'))
        body.append('</section>')
    body += ['<h2>Data content and origin</h2><p>Composition/content retention, explicit derivation and possible dependencies are recorded separately. Later removal does not revoke earlier observation.</p>']
    for data in view['data']:
        content, label = data['content'], labels[data['id']]
        body += [f'<details id="data-{label}" class="data-card"><summary>' + label + ' · ' + escape(content['form']) + '</summary><p class="identifier">' + escape(data['id']) + '</p>']
        if 'base' in content: body.append('<p>Original whole: ' + ids([content['base']]) + '</p>')
        for key, title in (('parts', 'Component paths'), ('updates', 'Replacement paths')):
            if key in content:
                if key == 'updates': body.append('<p>Specified paths use replacement data; all other parts retain the original content.</p>')
                body.append('<table class="' + ('field-updates' if key == 'updates' else 'parts') + '"><tr><th>' + title + '</th><th>Data</th></tr>')
                for part in content[key]: body.append('<tr><td>' + escape(_json(part['path'])) + '</td><td>' + ids([part['data']]) + '</td></tr>')
                body.append('</table>')
        if 'excluded_parts' in content: body += ['<p>Explicitly excluded: </p>', pre(content['excluded_parts'])]
        if content['form'] == 'subset_view':
            body += ['<p>Subset view of the original collection: member content is retained; the predicate is unevaluated and no specific selection is asserted.</p>', pre(content['predicate'])]
        if data['origin'].get('part_of'):
            body += ['<p>Parent whole: ' + ids([data['origin']['part_of']]) + '</p>', pre(data['origin']['path'])]
        for key, title in (('acquired_from', 'External origin'), ('at', 'Registration position')):
            if data['origin'].get(key): body.append('<p>' + title + ': ' + escape(data['origin'][key]) + '</p>')
        body.append('<p>Actual inputs: ' + ids(data['origin']['inputs']) + '</p>')
        for dep in data['origin']['dependencies']: body.append('<p>' + escape(dep['relation']) + ': ' + ids([dep['data']]) + '</p>')
        body += [details('Complete Data', pre(data)), '</details>']
    if audit is not None:
        content = []
        for loc_id, values in audit['location_evidences'].items():
            loc = view['locations'][loc_id]
            content += ['<h3>' + escape(loc_id + ' · ' + _location(loc)) + '</h3>', pre(loc['operand_refs']), evidence(values)]
        body += [details('Location identity evidence (separate audit materials)', ''.join(content), 'location-evidence'), details('Solver statistics (execution materials)', pre(audit['stats']))]
        if 'raw_annotation' in audit:
            body += [details('Compilation audit: original model processing segments and program-generated location mapping',
                             pre({k: audit[k] for k in ('raw_annotation', 'compilation_map')}))]
    return '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'none'; connect-src 'none'">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Basic data propagation review</title>
<style>body{font:15px/1.65 'Microsoft YaHei',sans-serif;max-width:1450px;margin:26px auto;padding:0 22px;color:#23364a;background:#f5f8fa}section{background:white;border:1px solid #d8e2ec;padding:22px;margin:24px 0}h1,h2{color:#123f55}table{border-collapse:collapse;width:100%;table-layout:fixed;margin:14px 0}th,td{text-align:left;vertical-align:top;border:1px solid #d8e2ec;padding:10px;overflow-wrap:anywhere;white-space:pre-wrap}th{background:#e9f1f6;font-size:13px}td{font-size:13px}.stages th:first-child{width:5%}.stages th:nth-child(2){width:12%}.stages th:nth-child(3){width:13%}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.6 Consolas,'Microsoft YaHei',monospace;background:#edf2f7;padding:14px}details{margin:12px 0}summary{cursor:pointer;font-weight:600;overflow-wrap:anywhere}.notice{background:#fff3d4;padding:12px}.muted,small{color:#60788b}.data{font-family:Consolas,monospace;font-weight:bold;color:#087284}.identifier{font:12px Consolas,monospace;overflow-wrap:anywhere}.data-card{background:white;border:1px solid #d8e2ec;padding:16px}.data-card:target{border:3px solid #e4a73a}blockquote{white-space:pre-wrap;overflow-wrap:anywhere;border-left:3px solid #769eb1;padding:10px;background:#f1f6fa}a{color:#126980}</style><body>''' + ''.join(body) + '</body></html>'


def write_reports(directory: Path, facts, writer, *, annotation_run=None):
    directory = checked_run_path(directory)
    prefix = '../' if directory.name == 'replay' else ''
    material_href = None
    if annotation_run is not None:
        from skillflow.propagation.annotation.inputs import resolve_material_owner
        material_file = resolve_material_owner(annotation_run) / 'inputs/runtime-contract.json'
        try:
            material_href = Path(os.path.relpath(material_file, directory)).as_posix()
        except ValueError:  # Explicit upstream on another Windows drive.
            material_href = material_file.resolve().as_uri()
    writer.text(checked_run_path(directory / 'report.md'), render_markdown(facts, facts_prefix=prefix, material_href=material_href))
    writer.text(checked_run_path(directory / 'report.html'), render_html(facts, facts_prefix=prefix, material_href=material_href))
