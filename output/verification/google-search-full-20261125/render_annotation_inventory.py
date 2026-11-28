"""Render a standalone annotation and evidence inventory from saved SkillFlow artifacts."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re


def load(path, digest=None):
    raw = path.read_bytes()
    if digest and sha256(raw).hexdigest() != digest:
        raise ValueError(f"Artifact digest differs: {path}")
    return json.loads(raw)


def anchor(kind, name):
    name = str(name)
    if re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        return f"{kind}-{name}"
    return f"{kind}-{sha256(name.encode()).hexdigest()[:24]}"


def link(kind, name, label=None):
    return f'<a href="#{anchor(kind, name)}">{escape(str(label or name))}</a>'


def dump(value):
    return escape(json.dumps(value, ensure_ascii=False, indent=2))


def panel(title, value, *, identifier=None):
    if value is None or value == [] or value == {}:
        return ''
    attr = f' id="{identifier}"' if identifier else ''
    return f'<details{attr}><summary>{escape(title)}</summary><pre>{dump(value)}</pre></details>'


def descendants(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from descendants(item)
    elif isinstance(value, list):
        for item in value:
            yield from descendants(item)


def evidence(value):
    spans = {}
    for row in descendants(value):
        start, end = row.get('start_line'), row.get('end_line')
        if isinstance(row.get('file'), str) and type(start) is int and type(end) is int:
            key = (row['file'], start, end)
            spans.setdefault(key, set())
            if row.get('reason'):
                spans[key].add(row['reason'])
    return spans


def excerpt_rows(value, sources, missing):
    result = []
    for (name, start, end), reasons in sorted(evidence(value).items()):
        lines = sources.get(name, [])
        label = f'{name}:{start}–{end}'
        if not 1 <= start <= end <= len(lines):
            missing.add(label)
            result.append(f'<li><code>{escape(label)}</code> · excerpt unavailable</li>')
            continue
        location = link('line', f'{name}:{start}', label)
        text = '\n'.join(f'{i:>3}  {lines[i - 1]}' for i in range(start, end + 1))
        description = ''.join(f'<p>{escape(reason)}</p>' for reason in sorted(reasons))
        result.append(f'<li>{location}{description}<pre>{escape(text)}</pre></li>')
    if not result:
        return ''
    return '<details><summary>Source references and excerpts</summary><ul>' + ''.join(result) + '</ul></details>'


def ids_in(value, known):
    result = set()
    for row in descendants(value):
        for key in ('instruction_id', 'instruction', 'ir_id'):
            identifier = row.get(key)
            if isinstance(identifier, str) and identifier in known:
                result.add(identifier)
        for key in ('targets', 'target_ids', 'raw_pointer', 'cfg_pointer', 'raw_path', 'compiled_path', 'affected_instruction_ids'):
            if key in row:
                result.update(known.intersection(re.findall(r'\bir_[\w.-]+\b', json.dumps(row[key]))))
    return result


def data_ids_in(value, known):
    return set(re.findall(r'\bdata_[A-Za-z0-9]+\b', json.dumps(value))).intersection(known)


def group_rows(rows, known, join_counts, name, extra_owners=None):
    grouped, unjoined = defaultdict(list), []
    for row in rows:
        owners = ids_in(row, known) | (extra_owners(row) if extra_owners else set())
        if not owners:
            unjoined.append(row)
        for owner in owners:
            grouped[owner].append(row)
    join_counts[name] = {'rows': len(rows), 'joined': len(rows) - len(unjoined), 'global': len(unjoined), 'omitted': 0}
    return grouped, unjoined


def load_group(directory, names):
    manifest_file = directory / 'manifest.json'
    if not manifest_file.is_file():
        return None, {}
    manifest = load(manifest_file)
    return manifest, {name: load(directory / name, manifest['artifacts'][name]) for name in names}


def confirm_input(owner, ref, expected):
    path = (owner / ref['path']).resolve()
    if path != expected.resolve():
        raise ValueError(f'Analysis references {path}, expected {expected}')
    actual = load(path / 'manifest.json')['manifest_sha256']
    if actual != ref['manifest_sha256']:
        raise ValueError(f'Upstream manifest differs: {path}')


def read_sources(run):
    directory = run / 'source'
    sources = {}
    if not (directory / 'manifest.json').is_file():
        return sources
    manifest = load(directory / 'manifest.json')
    for relative, digest in sorted(manifest.get('files', {}).items()):
        if not relative.startswith('inputs/package/'):
            continue
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory.resolve()):
            raise ValueError(f'Invalid source path: {relative}')
        raw = path.read_bytes()
        if digest != sha256(raw).hexdigest():
            raise ValueError(f'Frozen source changed: {path}')
        sources['skill/' + relative.removeprefix('inputs/package/')] = raw.decode('utf-8-sig').splitlines()
    return sources


def load_inventory(run, analysis):
    selection_path = run / 'selection.json'
    result = load(run / 'result.json')
    if not selection_path.is_file():
        raise ValueError(f'The run has no selected Task, CFG and annotation ({result.get("status")} at {result.get("stage")}).')
    selection = load(selection_path)
    selected = {}
    paths = {}
    for name in ('task', 'cfg', 'annotation'):
        ref = selection[name]
        path = (run / ref['path']).resolve()
        if not path.is_relative_to(run):
            raise ValueError(f'Selected {name} is outside the run')
        paths[name] = path
        selected[name] = load(path, ref['sha256'])
    graph = selected['cfg']['cfg']
    annotation = paths['annotation'].parent
    _, artifacts = load_group(annotation, (
        'audit/compiled-response.json', 'audit/compilation-map.json',
        'audit/raw-annotation.json', 'audit/wire-annotation.json',
    ))
    review_dir = annotation.parent / 'review'
    review, review_material = {}, {}
    if (review_dir / 'result.json').is_file() and (review_dir / 'inputs.json').is_file():
        material = load(review_dir / 'inputs.json')
        if (material.get('cfg') == graph and material.get('task') == selected['task']
                and material.get('annotation') == artifacts.get('audit/wire-annotation.json')):
            review = load(review_dir / 'result.json')
            review_material = material
    propagation_dir = analysis / 'propagation'
    prop, forward = load_group(propagation_dir, ('records.json', 'data.json', 'sinks.json'))
    doe_dir = analysis / 'doe'
    doe, backward = load_group(doe_dir, ('doe-result.json', 'audit/demand-support.json', 'audit/index.json'))
    if prop:
        confirm_input(propagation_dir, prop['upstream'], annotation)
    if doe:
        if not prop:
            raise ValueError('A DOE record requires its propagation record.')
        confirm_input(doe_dir, doe['upstream'], propagation_dir)
    return {
        'selection': selection, 'result': result, 'task': selected['task'], 'graph': graph,
        'annotation': selected['annotation'], 'artifacts': artifacts, 'review': review, 'review_material': review_material,
        'propagation': prop or {}, 'forward': forward, 'doe': doe or {}, 'backward': backward,
    }


def data_panel(rows, all_data):
    ids = data_ids_in(rows, all_data)
    if not ids:
        return ''
    return '<p class="inline-links">Data versions: ' + ' · '.join(
        link('data', name, name[:19] + '…') for name in sorted(ids)
    ) + '</p>'


def format_operands(values, definitions):
    rows = []
    for value in values:
        source = definitions.get(value.get('identifier')) if value.get('type') == 'result' else None
        suffix = ' · defined by ' + link('ir', source) if source else ''
        rows.append('<li><code>' + escape(json.dumps(value, ensure_ascii=False, separators=(', ', ': ')))
                    + '</code>' + suffix + '</li>')
    return ''.join(rows) or '<li>None</li>'


def resolve_pointer(value, pointer):
    for token in pointer.split('/')[1:]:
        part = token.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def owner_lookup(material, graph, wire, known):
    result = {}
    for row in material.get('target_index', []):
        root = {'cfg': graph, 'annotation': wire}.get(row.get('domain'))
        if root is None:
            continue
        pointer = row.get('pointer', '')
        match = re.match(r'^/blocks/([^/]+)/instructions/(\d+)(?:/|$)', pointer)
        if row['domain'] == 'cfg' and match:
            block_id, index = match.groups()
            block = graph['blocks'].get(block_id)
            if block and int(index) < len(block['instructions']):
                result[row['id']] = {block['instructions'][int(index)]['id']}
                continue
        if not pointer:
            continue
        try:
            target = resolve_pointer(root, pointer)
        except (KeyError, IndexError, ValueError, TypeError):
            continue
        result[row['id']] = ids_in(target, known)
    return result


def action_list(actions):
    return ''.join(f'<li><code>{escape(row["ref"])}</code> · {escape(row.get("role", row["kind"]))}</li>'
                   for row in actions) or '<li>None recorded</li>'


def op_summary(spec):
    rows = []

    def visit(events, base):
        for i, event in enumerate(events):
            prefix = f'{base}{i}'
            for j, operation in enumerate(event.get('atomic_ops', [])):
                detail = [f'output: {operation["output"]}'] if 'output' in operation else []
                for key in ('target', 'location', 'path', 'reason'):
                    if key in operation:
                        detail.append(f'{key}: {operation[key]}')
                rows.append(f'<li><code>{escape(prefix + "." + str(j))}</code> '
                            f'<strong>{escape(operation["op"])}</strong> '
                            f'{escape(" · ".join(detail))}</li>')
            visit(event.get('body', []), f'{prefix}.body.')
            visit(event.get('events', []), f'{prefix}.event.')

    visit(spec.get('events', []), 'e')
    return rows


STYLE = '''
:root{font-family:system-ui,sans-serif;color:#17263c;background:#f5f8fb;line-height:1.5;--line:#d8e2eb}
*{box-sizing:border-box} body{margin:0} main{max-width:1220px;margin:auto;padding:22px}
header{background:#142b42;color:#fff;padding:26px 22px}header h1{margin:0;font-size:2rem}header p{margin:7px 0 0}
header div{max-width:1175px;margin:auto} a{color:#075e86;overflow-wrap:anywhere}a:hover{text-decoration-thickness:2px}
nav{position:sticky;top:0;z-index:2;background:#f5f8fb;border-bottom:1px solid var(--line);padding:10px 0;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
input,button{font:inherit;padding:7px 11px;background:#fff;border:1px solid #a8b9c9;border-radius:5px}input{min-width:min(100%,320px)}
button{cursor:pointer;color:#17374d}button:focus-visible,input:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid #167b9d;outline-offset:2px}
section{scroll-margin-top:74px;margin:23px 0;background:#fff;padding:16px 18px;border:1px solid var(--line);border-radius:9px}
section h2{margin:0 0 8px;font-size:1.23rem}h3{margin:16px 0 8px}details{margin:8px 0 8px;padding:7px 10px;background:#f8fafc;border:1px solid var(--line);border-radius:5px;scroll-margin-top:74px}
summary{cursor:pointer;font-weight:600;overflow-wrap:anywhere}summary .badge{margin-left:7px}details details{background:#fff}
pre{margin:6px 0 10px;border-left:3px solid #b8cedd;background:#eff4f8;padding:9px 12px;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.35}
code{font-family:Consolas,monospace;overflow-wrap:anywhere}p{overflow-wrap:anywhere}li{margin:3px 0}ul{padding-left:22px}
.badge{display:inline-block;border-radius:4px;background:#e5eef4;color:#26465a;padding:0 6px;font-size:.8rem;font-weight:500}
.positive{background:#dbf2e9;color:#185945}.uncertain{background:#fff0d9;color:#754600}.inline-links{font-size:.88rem}
.columns{display:grid;grid-template-columns:1fr 1fr;gap:13px}.columns h3{font-size:.95rem}.columns>div{min-width:0}
.muted{color:#4c6273;font-size:.9rem} [hidden]{display:none!important}
@media(max-width:700px){.columns{grid-template-columns:1fr}main{padding:12px}}@media print{nav{display:none}section{break-inside:auto}}
'''


SCRIPT = '''
const box = document.querySelector('#search');
const cards = [...document.querySelectorAll('.instruction')];
const groups = [...document.querySelectorAll('.block')];
function filter() {
  const terms = box.value.toLowerCase().trim().split(/\\s+/).filter(Boolean);
  let visible = 0;
  for (const card of cards) {
    card.hidden = !terms.every(term => card.textContent.toLowerCase().includes(term));
    if (!card.hidden) visible++;
  }
  for (const group of groups) group.hidden = ![...group.querySelectorAll('.instruction')].some(card => !card.hidden);
  document.querySelector('#count').textContent = `${visible} of ${cards.length} IR instructions`;
}
box.addEventListener('input', filter);
document.querySelector('#expand').addEventListener('click', () => cards.filter(card => !card.hidden).forEach(card => card.open = true));
document.querySelector('#collapse').addEventListener('click', () => cards.forEach(card => card.open = false));
function showAnchor() {
  const id = decodeURIComponent(location.hash.slice(1));
  const target = document.getElementById(id);
  if (!target) return;
  if (target.closest('[hidden]')) { box.value = ''; filter(); }
  for (let node = target; node; node = node.parentElement) if (node.tagName === 'DETAILS') node.open = true;
  target.scrollIntoView({block: 'start'});
}
window.addEventListener('hashchange', showAnchor);
filter();
if (location.hash) showAnchor();
'''


def render(run, analysis):
    inv = load_inventory(run, analysis)
    graph, task = inv['graph'], inv['task']
    blocks = graph['blocks']
    known = {ir['id'] for block in blocks.values() for ir in block['instructions']}
    if sum(len(block['instructions']) for block in blocks.values()) != len(known):
        raise ValueError('Duplicate IR identity in selected CFG')
    sources = read_sources(run)
    artifacts = inv['artifacts']
    compiled = artifacts['audit/compiled-response.json']
    mapping = artifacts['audit/compilation-map.json']
    raw = artifacts['audit/raw-annotation.json']['ir_semantics']
    full_wire = artifacts['audit/wire-annotation.json']
    wire = full_wire['ir_semantics']
    records = inv['forward'].get('records.json', {})
    cover = inv['propagation'].get('coverage', {})
    data = {row['id']: row for row in inv['forward'].get('data.json', [])}
    result = inv['backward'].get('doe-result.json', {})
    support = inv['backward'].get('audit/demand-support.json', {})
    trace = {row['requirement_id']: row for row in support.get('traceability', {}).get('requirements', [])}
    derivations = {**result.get('derivations', {}).get('demand', {}), **support.get('extra_derivations', {})}
    all_sensitivity = result.get('derivations', {}).get('sensitivity', {})
    review = inv['review'].get('review') or {}
    definitions = {row['identifier']: ir['id'] for block in blocks.values() for ir in block['instructions']
                   for row in ir.get('outputs', []) if row['type'] == 'result'}
    review_targets = owner_lookup(inv['review_material'], graph, full_wire, known)
    sink_owners = {row['id']: ids_in(row, known) for row in result.get('sinks', [])}

    def additional_join(row):
        owners = set(sink_owners.get(row.get('id'), ()))
        for item in descendants(row):
            for target in item.get('target_ids', []):
                owners.update(review_targets.get(target, ()))
        return owners

    joins, global_rows, counts = {}, {}, {}
    for name, rows in {
        'Compiled event mapping': mapping.get('events', []),
        'Task realizations': compiled.get('realizations', []),
        'Compiled demand goals': compiled.get('demands', []),
        'Compiled input contracts': compiled.get('input_contracts', []),
        'Processing gaps': mapping.get('processing_gaps', []),
        'Sensitivity ingress gaps': mapping.get('sensitivity_entry_gaps', []),
        'Selected source review findings': review.get('findings', []),
        'Selected source review input findings': review.get('source_input_findings', []),
        'Selected source review gap checks': review.get('gap_checks', []),
        'Selected source review input-contract checks': review.get('input_contract_checks', []),
        'Forward diagnostics': inv['propagation'].get('diagnostics', []),
        'Declared sink boundaries': compiled.get('sink_boundaries', []),
        'Recorded sink boundaries': inv['forward'].get('sinks.json', []),
        'Backward demand derivations': [{'id': key, **row} for key, row in derivations.items()],
        'Backward input assessments': support.get('input_assessments', []),
        'Backward input findings': support.get('input_findings', []),
        'Backward sink demands': support.get('sinks', []),
        'DOE sink comparisons': result.get('sinks', []),
        'DOE diagnostics': result.get('diagnostics', []),
    }.items():
        joins[name], global_rows[name] = group_rows(rows, known, counts, name, additional_join)
    for name, values in {'Raw annotation': raw, 'Wire annotation': wire, 'Compiled annotation': compiled['ir_semantics'],
                         'Source-action bindings': mapping.get('source_action_bindings', {}),
                         'Forward records': records, 'Propagation coverage': cover}.items():
        unjoined = {key: values[key] for key in values.keys() - known}
        global_rows[name] = unjoined
        counts[name] = {'rows': len(values), 'joined': len(values) - len(unjoined), 'global': len(unjoined), 'omitted': 0}
    missing = set()
    outgoing, incoming = defaultdict(list), defaultdict(list)
    for edge in graph['edges']:
        outgoing[edge['source_block_id']].append(edge)
        incoming[edge['target_block_id']].append(edge)
    yield '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SkillFlow · Full Annotation Inventory</title><style>' + STYLE + '</style></head><body>'
    yield '<header><div><h1>SkillFlow annotation inventory</h1><p>' + escape(run.name) + '</p></div></header><main>'
    yield '<nav><label for="search">Find an instruction</label><input type="search" id="search" placeholder="IR ID, operation, source or requirement"><button type="button" id="expand">Expand matches</button><button type="button" id="collapse">Collapse all</button><span id="count" aria-live="polite"></span> · <a href="#task">Task</a> · <a href="#references">Evidence index</a> · <a href="#coverage">Coverage audit</a></nav>'
    result_status = inv['result'].get('status', 'unavailable')
    notes = [('Selected CFG', f'{len(blocks)} blocks, {len(known)} IR instructions, {len(graph["edges"])} edges'),
             ('Recorded run', f'{result_status} · {inv["result"].get("stage", "unknown stage")}'),
             ('Forward analysis', inv['propagation'].get('status', 'unavailable')),
             ('Backward / DOE', inv['doe'].get('status', 'unavailable')),
             ('Selected source review', inv['review'].get('status', 'unavailable'))]
    yield '<section><h2>Material and status</h2><ul>' + ''.join(f'<li><strong>{escape(key)}</strong> · {escape(value)}</li>' for key, value in notes) + '</ul>'
    if analysis != run:
        yield '<p>Forward and DOE records come from a separately linked analysis directory: <code>' + escape(str(analysis)) + '</code>.</p>'
    for name in ('reason', 'limitations'):
        yield panel('Run ' + name, inv['result'].get(name))
    yield panel('Selected bundle and digests', inv['selection'])
    yield panel('Graph declarations and constraints', {key: value for key, value in graph.items() if key not in {'blocks', 'edges'}})
    yield '</section>'
    yield '<section id="task"><h2>Task and source evidence</h2><p>' + escape(task['purpose']['text']) + '</p>'
    yield excerpt_rows(task['purpose'], sources, missing)
    for requirement in task.get('requirements', []):
        req = requirement['id']
        yield f'<details id="{anchor("requirement", req)}"><summary>{escape(req)} · {escape(requirement["text"])}</summary>'
        yield excerpt_rows(requirement, sources, missing)
        yield panel('Recorded backward trace and seed IDs', trace.get(req))
        for seed in (trace.get(req) or {}).get('seeds', []):
            positions = {derivations[key].get('node', {}).get('instruction_id')
                         for key in seed.get('derivation_ids', []) if key in derivations}
            if positions & known:
                yield '<p class="inline-links"><code>' + escape(seed['goal_id']) + '</code> · Derivation locations: ' + ' · '.join(
                    link('ir', ir) for ir in sorted(positions & known)) + '</p>'
        yield '</details>'
    yield panel('Task issues', task.get('issues')) + '</section>'
    for block_id, block in blocks.items():
        name = block.get('block_name') or block_id
        yield f'<section class="block" id="{anchor("block", block_id)}"><h2><code>{escape(block_id)}</code> · {escape(name)}</h2>'
        for direction, edges, endpoint in [('Predecessors', incoming[block_id], 'source_block_id'),
                                            ('Successors', outgoing[block_id], 'target_block_id')]:
            overview = '; '.join(link('block', e[endpoint]) + ' · ' + escape(e.get('condition_text') or 'unconditional') for e in edges)
            yield f'<p class="muted"><strong>{direction}</strong> · {overview or "None"}</p>'
        yield panel('Block metadata', {key: value for key, value in block.items() if key != 'instructions'})
        for ir in block['instructions']:
            identifier = ir['id']
            spec = compiled['ir_semantics'].get(identifier)
            source_actions = ir.get('metadata', {}).get('source_actions', [])
            bindings = mapping.get('source_action_bindings', {}).get(identifier)
            relevant = {key: values[identifier] for key, values in joins.items() if values[identifier]}
            selected_raw = raw.get(identifier)
            labels = [row for node in descendants(selected_raw) for row in node.get('sensitivity', [])]
            reqs = {row['requirement_id'] for row in descendants(relevant) if row.get('requirement_id')}
            status = cover.get(identifier, 'no forward record')
            style = 'positive' if status == 'processed' else 'uncertain'
            yield f'<details class="instruction" id="{anchor("ir", identifier)}"><summary><code>{escape(identifier)}</code> · {escape(ir["opcode"])} <span class="badge {style}">{escape(status)}</span></summary>'
            yield '<div class="columns"><div><h3>IR inputs</h3><ul>' + format_operands(ir.get('inputs', []), definitions) + '</ul></div><div><h3>IR outputs</h3><ul>' + format_operands(ir.get('outputs', []), {}) + '</ul></div></div>'
            if reqs:
                yield '<p>Task references: ' + ', '.join(link('requirement', req) for req in sorted(reqs)) + '</p>'
            yield '<h3>Source actions</h3><ul>' + action_list(source_actions) + '</ul>'
            if spec:
                operations = op_summary(spec)
                if operations:
                    yield '<h3>Compiled operations</h3><ul>' + ''.join(operations) + '</ul>'
                else:
                    yield '<p class="muted">The compiled record contains no atomic operation.</p>'
            else:
                yield '<p class="muted">No compiled operation record for this instruction.</p>'
            yield excerpt_rows([ir, spec, selected_raw, relevant, bindings], sources, missing)
            yield panel('Exact IR record', ir)
            yield panel('Exact action and processing bindings', bindings)
            yield panel('Exact compiled operation record', spec)
            yield panel('Accepted annotation · normalized', selected_raw)
            yield panel('Accepted annotation · wire', wire.get(identifier))
            yield panel('Sensitive source declarations', labels)
            yield data_panel([records.get(identifier), relevant], data.keys())
            yield panel('Forward inputs, outputs, alternatives and state', records.get(identifier))
            for key, rows in relevant.items():
                yield panel(f'{key} ({len(rows)})', rows)
            yield '</details>'
        yield '</section>'
    yield '<section id="references"><h2>Evidence index</h2>'
    yield panel('Exact compiled locations and source evidence', {key: compiled.get(key) for key in ('locations', 'location_evidences')})
    yield panel('Full compilation mapping', mapping)
    yield panel('Global annotation metadata', {key: value for key, value in compiled.items() if key != 'ir_semantics'})
    yield panel('Global wire and normalized annotation metadata', {
        'wire': {key: value for key, value in full_wire.items() if key != 'ir_semantics'},
        'normalized': {key: value for key, value in artifacts['audit/raw-annotation.json'].items() if key != 'ir_semantics'},
    })
    yield panel('Selected source review', inv['review'])
    yield panel('Backward coverage and requirements', support.get('coverage'))
    yield panel('Shared sensitivity derivations', all_sensitivity)
    yield panel('Constraint checks and change impact', result.get('constraints'))
    yield panel('Sensitivity declaration index', inv['backward'].get('audit/index.json'))
    yield panel('Unlinked or whole-run records', {key: value for key, value in global_rows.items() if value})
    for name, row in sorted(data.items()):
        yield panel(f'Data version {name}', row, identifier=anchor('data', name))
    yield '</section><section id="sources"><h2>Frozen source files</h2>'
    for name, lines in sorted(sources.items()):
        yield '<details><summary>' + escape(name) + '</summary><pre>'
        for number, line in enumerate(lines, 1):
            yield f'<span id="{anchor("line", f"{name}:{number}")}">{number:>3}  {escape(line)}</span>\n'
        yield '</pre></details>'
    yield '</section>'
    qa = {'run': str(run), 'analysis': str(analysis), 'blocks': len(blocks), 'instructions': len(known),
          'cfg_edges': len(graph['edges']), 'source_files': len(sources),
          'forward_status': inv['propagation'].get('status'), 'doe_status': inv['doe'].get('status'),
          'forward_coverage': dict(sorted(Counter(cover.values()).items())),
          'ir_rows': {'rendered': len(known), 'omitted': 0}, 'artifact_rows': counts,
          'data_versions': len(data), 'sensitivity_derivations': len(all_sensitivity),
          'source_references_without_excerpt': sorted(missing)}
    yield '<section id="coverage"><h2>Coverage audit</h2><p>Global rows appear in the evidence index. An unavailable calculation is left unresolved.</p><pre>' + dump(qa) + '</pre></section>'
    yield '</main><script>' + SCRIPT + '</script></body></html>'
    yield qa


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True, help='Existing selected run to read')
    parser.add_argument('--analysis-dir', type=Path, help='Optional separate directory with manifest-linked propagation and DOE')
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('google-search-full-annotation.html'))
    args = parser.parse_args()
    output = args.output.resolve()
    if output.parent != Path(__file__).resolve().parent or output.suffix != '.html':
        parser.error('The output must be an HTML file next to this generator.')
    run = args.run_dir.resolve()
    analysis = args.analysis_dir.resolve() if args.analysis_dir else run
    chunks = list(render(run, analysis))
    qa = chunks.pop()
    output.write_text(''.join(chunks), encoding='utf-8')
    output.with_suffix('.qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{qa["blocks"]} blocks, {qa["instructions"]} IR instructions, {qa["ir_rows"]["omitted"]} omitted · {output}')


if __name__ == '__main__':
    main()
