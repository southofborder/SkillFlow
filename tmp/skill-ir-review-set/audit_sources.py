"""Read frozen inputs and committed CFGs only; emit an external scratch audit."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path('packages/skill-ir/experiments/semantics_baseline')
RUN = BASE / 'runs/baseline-deepseek-v4-flash-max-20260910'
FROZEN = BASE / 'frozen/corpus'
report = json.loads((RUN / 'report.json').read_text(encoding='utf-8'))
corpus = json.loads((FROZEN / 'corpus.json').read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def components(vertices, adjacency):
    remaining = set(vertices)
    result = []
    while remaining:
        todo = [min(remaining)]
        visited = set()
        while todo:
            current = todo.pop()
            if current in visited:
                continue
            visited.add(current)
            todo.extend(adjacency[current] - visited)
        result.append(sorted(visited))
        remaining -= visited
    return result


summary = Counter()
operand_types = Counter()
literal_types = Counter()
condition_types = Counter()
field_sets = defaultdict(set)
samples = []
sensitive_names = {'annotation', 'annotations', 'provenance', 'fact', 'facts', 'review', 'reviews', 'gold', 'expected'}
for sample in corpus['samples']:
    sid = sample['id']
    choices = [row for row in report['trials'] if row['case'] == sid and row['status'] == 'complete']
    chosen = min(choices, key=lambda row: row['repetition'])
    path = RUN / chosen['artifacts']
    record = json.loads((path / 'record.json').read_text(encoding='utf-8'))
    analysis = json.loads((path / 'analysis.json').read_text(encoding='utf-8'))
    assert record['status'] == analysis['status'] == 'complete'
    cfg = analysis['cfg']
    assert cfg['entry_block_id'] in cfg['blocks']
    assert record['artifact_sha256']['analysis.json'] == sha(path / 'analysis.json')
    for key in cfg:
        field_sets['cfg'].add(key)
    blocks = cfg['blocks']
    edges = cfg['edges']
    directed = defaultdict(set)
    weak = defaultdict(set)
    outgoing = Counter()
    pair_indices = defaultdict(list)
    exact_indices = defaultdict(list)
    conditions = Counter()
    self_loops = []
    empty_string_edges = []
    for number, edge in enumerate(edges, 1):
        field_sets['edge'].update(edge)
        source, target = edge['source_block_id'], edge['target_block_id']
        assert source in blocks and target in blocks
        directed[source].add(target)
        weak[source].add(target)
        weak[target].add(source)
        outgoing[source] += 1
        pair_indices[(source, target)].append(number)
        condition = edge.get('condition_text')
        conditions[type(condition).__name__] += 1
        if condition is None:
            conditions['null'] += 1
        elif condition == '':
            conditions['empty_string'] += 1
            empty_string_edges.append(number)
        elif isinstance(condition, str) and not condition.strip():
            conditions['whitespace_string'] += 1
        exact_indices[(source, target, json.dumps(condition, ensure_ascii=False))].append(number)
        if source == target:
            self_loops.append(number)
    reached = set()
    todo = [cfg['entry_block_id']]
    while todo:
        current = todo.pop()
        if current not in reached:
            reached.add(current)
            todo.extend(directed[current] - reached)

    counts = Counter(blocks=len(blocks), edges=len(edges), skill_constraints=len(cfg['constraints']))
    counts['empty_skill_constraints'] = not cfg['constraints']
    non_string_literals = []
    longest_fields = []
    script_contents = []
    for bid, block in blocks.items():
        field_sets['block'].update(block)
        counts['block_constraints'] += len(block['constraints'])
        counts['empty_block_constraints'] += not block['constraints']
        counts['empty_blocks'] += not block['instructions']
        for instruction in block['instructions']:
            iid = instruction['id']
            field_sets['instruction'].update(instruction)
            counts['instructions'] += 1
            counts['instruction_constraints'] += len(instruction['constraints'])
            counts['empty_instruction_constraints'] += not instruction['constraints']
            counts['empty_metadata'] += not instruction['metadata']
            counts['metadata_fields'] += len(instruction['metadata'])
            for direction in ('inputs', 'outputs'):
                counts[direction] += len(instruction[direction])
                counts['empty_' + direction] += not instruction[direction]
                for op in instruction[direction]:
                    field_sets['operand'].update(op)
                    operand_types[op['type']] += 1
                    if op['type'] == 'literal':
                        value = op.get('literal_value')
                        literal_types[type(value).__name__] += 1
                        if not isinstance(value, str):
                            non_string_literals.append({'block': bid, 'instruction': iid, 'direction': direction,
                                                        'type': type(value).__name__, 'value': value})
            for key, value in instruction['metadata'].items():
                field_sets['metadata'].add(key)
                text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
                longest_fields.append({'block': bid, 'instruction': iid, 'metadata_key': key,
                                       'json_type': type(value).__name__, 'characters': len(text),
                                       'lines': len(text.splitlines())})
                if key == 'script_content':
                    script_contents.append(longest_fields[-1])
    package = FROZEN / sample['package_path']
    files = sorted(p for p in package.rglob('*') if p.is_file())
    possible_collisions = []
    for file in files:
        relative = file.relative_to(package)
        tokens = {part.lower() for part in relative.parts} | {part.lower().split('.')[0] for part in relative.parts}
        if tokens & sensitive_names:
            possible_collisions.append(relative.as_posix())
    counts['input_files'] = len(files)
    summary.update(counts)
    condition_types.update(conditions)
    samples.append({
        'sample_id': sid,
        'selected_repetition': chosen['repetition'],
        'selection_rule': 'lowest repetition whose committed record and analysis status are complete',
        'record_sha256': sha(path / 'record.json'),
        'analysis_sha256': sha(path / 'analysis.json'),
        'cfg_json_sha256': hashlib.sha256(json.dumps(cfg, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest(),
        'counts': dict(counts),
        'self_loop_edge_indices_1based': self_loops,
        'duplicate_exact_edges_1based': [indices for indices in exact_indices.values() if len(indices) > 1],
        'parallel_same_pair_edges_1based': [indices for indices in pair_indices.values() if len(indices) > 1],
        'empty_string_edge_indices_1based': empty_string_edges,
        'edge_condition_types': dict(conditions),
        'max_outgoing_edges': max(outgoing.values(), default=0),
        'multi_branch_blocks': {bid: count for bid, count in outgoing.items() if count > 2},
        'weak_components': components(blocks, weak),
        'unreachable_from_entry': sorted(set(blocks) - reached),
        'non_string_literals': non_string_literals,
        'script_content_fields': script_contents,
        'largest_metadata_fields': sorted(longest_fields, key=lambda row: row['characters'], reverse=True)[:3],
        'package_path': sample['package_path'],
        'input_files': [p.relative_to(package).as_posix() for p in files],
        'legal_input_names_resembling_annotations': possible_collisions,
    })

audit = {
    'schema_version': 1,
    'read_only_source_audit': True,
    'run_id': report['run_id'],
    'report_sha256': sha(RUN / 'report.json'),
    'sample_count': len(samples),
    'totals': dict(summary),
    'operand_types': dict(operand_types),
    'literal_types': dict(literal_types),
    'edge_condition_types': dict(condition_types),
    'field_inventory': {key: sorted(values) for key, values in field_sets.items()},
    'render_preservation_notes': [
        'Render the actual selected CFG; keep entry_block_id, declared_context_keys, and all three constraint levels, including explicit empty lists.',
        'Preserve block and instruction order, all identifiers/names/opcodes, data_source_kind including null, draft_instruction_id, every ordered input/output operand, all metadata keys and values.',
        'Do not deduplicate parallel or exact duplicate edges, or conflate condition_text null with an empty string. Keep source/target direction, edge order and exact condition text.',
        'Keep independent components and entry-unreachable blocks visible; do not drop them as unreachable noise.',
        'Preserve JSON literal types (object, array, number, boolean, null) and nested structure; never flatten a literal object to a textual identifier.',
        'Inspect long raw constraints, metadata.script_content and command text for wrapping. If a digest summary is used, it must be explicitly a summary with original content retained outside the PNG.',
        'Source-package inclusion must be based on the frozen package root and inventory, not substring filters such as annotation/provenance/facts/review. This scratch audit is external and not a Skill input.',
    ],
    'samples': samples,
}
target = Path('tmp/skill-ir-review-set/source-audit.json')
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: audit[key] for key in ('sample_count', 'totals', 'operand_types', 'literal_types', 'edge_condition_types')}, ensure_ascii=False, indent=2))
for row in samples:
    print(row['sample_id'], 'r' + str(row['selected_repetition']), row['counts']['blocks'], row['counts']['edges'],
          row['counts']['instructions'], 'self', row['self_loop_edge_indices_1based'],
          'parallel', row['parallel_same_pair_edges_1based'], 'components', len(row['weak_components']),
          'unreachable', row['unreachable_from_entry'], 'emptycond', row['empty_string_edge_indices_1based'],
          'fanout', row['max_outgoing_edges'], 'name-collision', row['legal_input_names_resembling_annotations'])
print('audit:', target)
