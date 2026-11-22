"""Read saved GA4 evidence and print JSON; never execute SkillFlow or write files.

Usage: python -B source_boundary_audit.py --run PATH [--summary]
Source-site counts are lexical inventory counts, not semantic coverage claims.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys


def digest(content):
    return hashlib.sha256(content).hexdigest()


class Evidence:
    def __init__(self, run):
        self.run = Path(run).resolve()
        self.artifacts = {}
        self.issues = []

    def inside(self, base, name):
        path = (base / name).resolve()
        if not path.is_relative_to(self.run):
            raise ValueError('Artifact reference escapes the audited run: ' + str(path))
        return path

    def read(self, path, expected=None):
        data = path.read_bytes()
        actual = digest(data)
        self.artifacts[path.relative_to(self.run).as_posix()] = actual
        if expected is not None and actual != expected:
            raise ValueError('Artifact hash mismatch: ' + str(path))
        return json.loads(data.decode('utf-8'))

    def optional(self, path):
        return self.read(path) if path.is_file() else None


def mask_comments_strings(text):
    """Preserve offsets/newlines; mask comments and quoted/template text.

    This finite scanner is not a TypeScript parser. Template interpolations are
    masked too; the frozen GA4 API/save/filesystem calls do not occur in them.
    """
    out = list(text)
    i = 0
    while i < len(text):
        if text.startswith('//', i):
            end = text.find('\n', i)
            end = len(text) if end < 0 else end
        elif text.startswith('/*', i):
            close = text.find('*/', i + 2)
            end = len(text) if close < 0 else close + 2
        elif text[i] in "'\"`":
            quote, end = text[i], i + 1
            while end < len(text):
                if text[end] == '\\':
                    end += 2
                elif text[end] == quote:
                    end += 1
                    break
                else:
                    end += 1
        else:
            i += 1
            continue
        for at in range(i, min(end, len(text))):
            if text[at] not in '\r\n':
                out[at] = ' '
        i = end
    return ''.join(out)


REMOTE = re.compile(r'\bawait\s+([\w$]+)\s*\.\s*'
                    r'(runReport|runRealtimeReport|getMetadata|searchanalytics\s*\.\s*query|'
                    r'urlNotifications\s*\.\s*publish|urlInspection\s*\.\s*index\s*\.\s*inspect)\s*\(')
SAVE = re.compile(r'\bsaveResult\s*\(')
FILESYSTEM = re.compile(r'\b(existsSync|mkdirSync|writeFileSync|readFileSync|readdirSync)\s*\(')
FUNCTION = re.compile(r'\bfunction\s+([\w$]+)\s*[(<]')


def source_sites(sources):
    sites = []
    for file, source in sorted(sources.items()):
        if not file.endswith('.ts'):
            continue
        text, sha = source['text'], source['sha256']
        masked = mask_comments_strings(text)
        functions = list(FUNCTION.finditer(masked))
        patterns = [('remote', REMOTE), ('save', SAVE)]
        if file.endswith('/core/storage.ts'):
            patterns.append(('filesystem', FILESYSTEM))
        occurrences = Counter()
        for category, pattern in patterns:
            for match in pattern.finditer(masked):
                if category == 'save' and re.search(r'\bfunction\s*$', masked[max(0, match.start()-50):match.start()]):
                    continue
                function = next((x.group(1) for x in reversed(functions) if x.start() < match.start()), '<module>')
                method = re.sub(r'\s+', '', match.group(2) if category == 'remote' else match.group(1) if category == 'filesystem' else 'saveResult')
                end, depth = match.end(), 1
                while end < len(masked) and depth:
                    depth += (masked[end] == '(') - (masked[end] == ')')
                    end += 1
                start_line = text.count('\n', 0, match.start()) + 1
                end_line = text.count('\n', 0, end) + 1
                occurrence = (function, category, method)
                occurrences[occurrence] += 1
                call_text = text[match.start():end]
                anchor = {'file': file, 'file_sha256': sha, 'function': function,
                          'category': category, 'method': method, 'start_line': start_line,
                          'end_line': end_line, 'occurrence': occurrences[occurrence],
                          'call_sha256': digest(call_text.encode('utf-8'))}
                sites.append({'anchor_id': digest(json.dumps(anchor, sort_keys=True).encode())[:24],
                              **anchor, 'source_call': call_text,
                              'receiver_text': match.group(1) if category == 'remote' else None})
    return sorted(sites, key=lambda x: (x['category'], x['file'], x['start_line']))


def instructions(cfg):
    return {row['id']: row for block in cfg.get('blocks', {}).values() for row in block.get('instructions', [])}


def signature(row, canonical=False):
    def operand(value):
        kind = value.get('type')
        if kind == 'literal':
            return (kind, value.get('literal_value'))
        return (kind, value.get('semantic_name', value.get('identifier')) if canonical else value.get('identifier'))
    return (row.get('opcode'), [operand(x) for x in row.get('inputs', [])],
            [operand(x) for x in row.get('outputs', [])])


def checked_span(span, sources):
    if not isinstance(span, dict):
        return None
    file = span.get('file', '').replace('\\', '/')
    if file.startswith('skill/'):
        file = file[6:]
    start, end = span.get('start_line'), span.get('end_line')
    if file not in sources or type(start) is not int or type(end) is not int:
        return None
    if not 1 <= start <= end <= len(sources[file]['text'].splitlines()):
        return None
    return {'file': file, 'start_line': start, 'end_line': end}


def legacy_spans(ev, base_cfg, sources):
    """Recover omitted legacy spans through bound draft IDs, never ir_N order."""
    receipt = ev.optional(ev.run / 'accepted-upstream.json')
    owner = ev.inside(ev.run, receipt['owners']['graph']) if receipt else ev.run / 'steps/graph'
    if not (owner / 'result.json').is_file():
        return {}
    result = ev.read(owner / 'result.json')
    if not result.get('accepted_call'):
        return {}
    value = ev.read(ev.inside(owner, result.get('value_file', 'value.json')), result.get('value_sha256'))
    if not isinstance(value.get('blocks'), list):
        return {}  # New GraphFacts emits source spans directly into canonical metadata.
    raw = ev.read(ev.inside(owner, result['accepted_call'] + '/response.json'))
    raw = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(raw.get('blocks'), list):
        ev.issues.append('Accepted graph response has no full legacy block list; legacy span recovery unavailable.')
        return {}
    normalized = {block['block_ref']: block for block in value['blocks']}
    by_draft = defaultdict(list)
    for iid, row in instructions(base_cfg).items():
        by_draft[row.get('draft_instruction_id')].append((iid, row))
    recovered = {}
    for block in raw['blocks']:
        other = normalized.get(block.get('block_ref'))
        rows = block.get('instructions', [])
        values = (other or {}).get('instructions', [])
        if len(rows) != len(values) or any(signature(a) != signature(b) for a, b in zip(rows, values)):
            ev.issues.append('Legacy raw/normalized block signature mismatch: ' + str(block.get('block_ref')))
            continue
        for raw_row, value_row in zip(rows, values):
            span = checked_span(raw_row.get('metadata', {}).get('_source_span'), sources)
            if span is None:
                continue
            matches = by_draft.get(value_row.get('instruction_ref'), [])
            if len(matches) != 1 or signature(matches[0][1], True) != signature(value_row):
                ev.issues.append('Legacy draft-ID join is missing or ambiguous: ' + str(value_row.get('instruction_ref')))
                continue
            excerpt = '\n'.join(sources[span['file']]['text'].splitlines()[span['start_line']-1:span['end_line']])
            script = matches[0][1].get('metadata', {}).get('script_content')
            if script is None or script.rstrip('\r\n') != excerpt:
                ev.issues.append('Legacy source excerpt differs from canonical script_content: ' + matches[0][0])
                continue
            recovered[matches[0][0]] = {**span, 'basis': 'accepted_raw_to_value_draft_id',
                                       'source_artifact': (owner.relative_to(ev.run) / result['accepted_call'] / 'response.json').as_posix()}
    return recovered


def selected_spans(cfg, base_cfg, initial_spans, sources):
    base_irs = instructions(base_cfg)
    spans = {}
    for iid, row in instructions(cfg).items():
        meta = row.get('metadata', {})
        direct = checked_span(meta.get('source_span', meta.get('_source_span')), sources)
        if direct:
            spans[iid] = {**direct, 'basis': 'selected_cfg_source_span'}
        elif row == base_irs.get(iid) and iid in initial_spans:
            spans[iid] = initial_spans[iid]
    return spans


def operation_records(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == 'atomic_ops' and isinstance(child, list):
                for index, op in enumerate(child):
                    yield path + (key, index), op
            else:
                yield from operation_records(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from operation_records(child, path + (index,))


def record_evidence(iid, records, coverage):
    record = records.get(iid)
    actions = []
    if record is not None:
        for path, op in operation_records(record):
            if op.get('endpoints'):
                actions.append({'record_pointer': '/' + iid + '/' + '/'.join(map(str, path)),
                                'op': op.get('op'), 'endpoints': op['endpoints'],
                                'inputs': op.get('inputs'), 'outputs': op.get('outputs'),
                                'request_id': op.get('request_id'),
                                'request_pair_id': op.get('request_pair_id'),
                                'alternative_count': len(op.get('alternatives', []))})
    return {'instruction_id': iid, 'coverage': coverage.get(iid), 'record_present': record is not None,
            'endpoint_operations': actions}


def audit(run):
    ev = Evidence(run)
    sources = {}
    snapshot = ev.optional(ev.run / 'source/inputs/snapshot.json')
    if snapshot:
        for row in snapshot['files']:
            path = ev.inside(ev.run / 'source/inputs/package', row['path'])
            data = path.read_bytes()
            sha = digest(data)
            if sha != row['raw_sha256']:
                raise ValueError('Frozen source file hash mismatch: ' + row['path'])
            sources[row['path']] = {'text': data.decode('utf-8'), 'sha256': sha}
    selection = ev.optional(ev.run / 'selection.json')
    cfg, cfg_path, cfg_status = None, None, 'not_run'
    if selection and selection.get('cfg'):
        ref = selection['cfg']
        cfg_path = ev.inside(ev.run, ref['path'])
        cfg = ev.read(cfg_path, ref['sha256'])['cfg']
        cfg_status = 'selected'
    elif (ev.run / 'graph/initial.json').is_file():
        cfg_path = ev.run / 'graph/initial.json'
        cfg = ev.read(cfg_path)['cfg']
        cfg_status = 'provisional_initial_no_selection'
    base = ev.optional(ev.run / 'graph/initial.json')
    base_cfg = (base or {}).get('cfg', {})
    initial_spans = legacy_spans(ev, base_cfg, sources) if sources and base_cfg else {}
    irs = instructions(cfg or {})
    spans = selected_spans(cfg or {}, base_cfg, initial_spans, sources)

    manifest = ev.optional(ev.run / 'propagation/manifest.json')
    records_path = ev.run / 'propagation/records.json'
    records, coverage, record_status = {}, {}, 'not_run'
    if manifest and records_path.is_file():
        expected = manifest.get('artifacts', {}).get('records.json')
        if expected is None:
            raise ValueError('Propagation manifest does not bind records.json')
        if cfg_status != 'selected' or not selection.get('annotation'):
            record_status = 'unbound_to_selected_bundle'
        else:
            ref = selection['annotation']
            annotation_path = ev.inside(ev.run, ref['path'])
            annotation = ev.read(annotation_path, ref['sha256'])
            upstream = manifest.get('upstream', {})
            upstream_dir = ev.inside(ev.run / 'propagation', upstream.get('path', ''))
            references = ev.read(annotation_path.parent / 'inputs/references.json')
            graph_ref = references['cfg']
            if (upstream_dir != annotation_path.parent or upstream.get('manifest_sha256') != annotation.get('manifest_sha256')
                    or ev.inside(annotation_path.parent, graph_ref['path']) != cfg_path
                    or graph_ref['sha256'] != selection['cfg']['sha256']):
                raise ValueError('Saved records, selected annotation and selected CFG do not share a bound bundle')
            records = ev.read(records_path, expected)
            coverage = manifest.get('coverage', {})
            record_status = 'available'
    elif manifest or records_path.is_file():
        record_status = 'incomplete_material'

    sites = source_sites(sources)
    for site in sites:
        candidates = [(iid, span) for iid, span in spans.items() if span['file'] == site['file']
                      and span['start_line'] <= site['start_line'] <= span['end_line']]
        # A narrower source span is a locator preference, not a semantic proof.
        width = min((s['end_line'] - s['start_line'] for _, s in candidates), default=None)
        preferred = [(iid, span) for iid, span in candidates if span['end_line'] - span['start_line'] == width]
        site['join_status'] = ('not_run' if cfg is None else 'missing' if not preferred
                               else 'matched' if len(preferred) == 1 else 'ambiguous')
        site['candidate_spans'] = [{'instruction_id': iid, **span} for iid, span in candidates]
        site['preferred_ir_ids'] = [iid for iid, _ in preferred]
        site['records_status'] = record_status
        site['records'] = [record_evidence(iid, records, coverage) for iid, _ in preferred] if record_status == 'available' else None
        site['has_recorded_boundary'] = None
        if site['join_status'] == 'matched' and record_status == 'available':
            actions = site['records'][0]['endpoint_operations']
            def relevant(op):
                if site['category'] == 'remote':
                    return any(x.get('kind') == 'remote' for x in op['endpoints'])
                if site['category'] == 'save':
                    return op['op'] == 'write' and any(x.get('kind') == 'storage' for x in op['endpoints'])
                return bool(op['endpoints'])
            site['has_recorded_boundary'] = any(relevant(op) for op in actions)
        site['semantic_correctness'] = 'not_established_by_this_helper'
    categories = {}
    for category, reference_count in [('remote', 13), ('save', 25), ('filesystem', 7)]:
        rows = [x for x in sites if x['category'] == category]
        categories[category] = {
            'source_site_count': len(rows) if snapshot else None,
            'previous_frozen_ga4_reference_count': reference_count,
            'reference_count_matches': len(rows) == reference_count if snapshot else None,
            'join_status_counts': {status: sum(x['join_status'] == status for x in rows)
                                   for status in ['matched', 'ambiguous', 'missing', 'not_run']} if cfg else None,
            'recorded_boundary_sites': sum(x['has_recorded_boundary'] is True for x in rows) if record_status == 'available' else None,
            'boundary_observation_unresolved_sites': sum(x['has_recorded_boundary'] is None for x in rows) if record_status == 'available' else None,
            'sites': rows,
        }
    return {'audit': 'ga4-source-boundary-readonly-v1', 'run_directory': str(ev.run),
            'source_status': 'available' if snapshot else 'not_run',
            'source_sha256': (snapshot or {}).get('source_sha256'),
            'source_file_count': len(sources) if snapshot else None,
            'source_file_hashes': {key: value['sha256'] for key, value in sources.items()},
            'cfg_status': cfg_status, 'cfg_path': str(cfg_path) if cfg_path else None,
            'cfg_instruction_count': len(irs) if cfg else None,
            'source_located_instruction_count': len(spans) if cfg else None,
            'records_status': record_status, 'propagation_status': (manifest or {}).get('status'),
            'categories': categories, 'artifact_hashes': ev.artifacts, 'issues': ev.issues,
            'caveats': [
                'Reference counts 13/25/7 describe this frozen GA4 package; a mismatch is reported, never normalized or asserted away.',
                'Lexical scanning masks comments and strings, including template interpolation. It is not a general TypeScript parser.',
                'Legacy spans use accepted response/value signatures and draft IDs. Changed revised instructions cannot inherit a span merely because their IR ID matches.',
                'Minimal source span is only a locator preference. Multiple equal candidates remain ambiguous; missing locators are not missing execution claims.',
                'A false recorded-boundary flag means no matching boundary was found in these saved records; it is not proof that the source action cannot execute.',
                'A recorded endpoint does not establish the actual receiver/auth handle, request address, input fields, response pairing, conditions or occurrence identity.',
                'Filesystem observation counts any endpoint at the matched statement; exact API/path/content semantics still require source-backed inspection.',
                'Report return must trace to the corresponding SDK response, not the date-range local. This helper does not infer correctness from variable or endpoint names.',
                'No absent input, action, response or source review is synthesized. No deletion or necessity conclusion is produced.',
                'Only saved JSON and source bytes are read. No model, Skill, compiler, renderer, analyzer, backend or replay is executed; no files are written.',
            ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--summary', action='store_true', help='Omit per-site and artifact details from stdout')
    args = parser.parse_args()
    try:
        result = audit(args.run)
        if args.summary:
            result = {key: value for key, value in result.items() if key not in ['artifact_hashes', 'source_file_hashes']}
            result['categories'] = {key: {k: v for k, v in row.items() if k != 'sites'} for key, row in result['categories'].items()}
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({'audit': 'ga4-source-boundary-readonly-v1', 'status': 'audit_material_error',
                          'run_directory': str(args.run.resolve()), 'error_type': type(error).__name__,
                          'reason': str(error)}, ensure_ascii=False, indent=2))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
