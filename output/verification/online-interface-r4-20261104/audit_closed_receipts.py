"""Independent saved-receipt arithmetic audit; no production imports or execution."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

V = Path(__file__).resolve().parent
ROOT = V.parents[2]
FIELDS = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'total_tokens')

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def audit(case):
    prepared = read(V / 'prepared-runs.json')
    row = next(x for x in prepared['run_order'] if x['case_id'] == case)
    run = Path(row['run_directory'])
    closed = read(run / 'controller-finished.json')  # closure gate
    metrics = read(run / 'metrics.json')
    issues, rows, notices = [], [], []
    def check(ok, label):
        if not ok: issues.append(label)
    marker_dirs = {p.parent for p in (run / 'transport').rglob('started.json')}
    pid_dirs = {p.parent for p in (run / 'transport').rglob('pid.json')}
    metric_dirs = {run / r['request'] for r in metrics['requests']}
    check(marker_dirs == pid_dirs == metric_dirs, 'Native markers and metric directories disagree')
    identities = set()
    total = Counter({f: 0 for f in FIELDS})
    groups, stages = defaultdict(Counter), defaultdict(Counter)
    for r in metrics['requests']:
        p = run / r['request']
        events = [json.loads(x) for x in (p / 'stdout.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
        thread = next((e.get('thread_id') for e in events if e.get('type') == 'thread.started'), None)
        turns = [e for e in events if e.get('type') == 'turn.completed']
        messages = [e['item']['text'] for e in events if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
        check(len(turns) == 1 and len(messages) == 1, r['request'] + ': not one public final turn; inspect manually')
        complete = Counter({f: 0 for f in FIELDS})
        request_ids = []
        for order, turn in enumerate(turns):
            ident = (thread, turn.get('turn_id'), order)
            if ident in identities:
                continue
            identities.add(ident); request_ids.append(ident)
            usage = turn.get('usage')
            if not isinstance(usage, dict):
                issues.append(r['request'] + ': missing public usage'); continue
            values = {f: usage.get(f, 0) for f in FIELDS}
            values['total_tokens'] = values['input_tokens'] + values['output_tokens']
            complete.update(values)
        check(dict(complete) == r.get('complete_token_usage'), r['request'] + ': public usage mismatch')
        if messages:
            check(messages[-1].strip() == (p / 'last-message.txt').read_text(encoding='utf-8').strip(), r['request'] + ': final answer mismatch')
        sidecar = read(p / 'usage.json')
        check(sidecar.get('known') and all(complete[k] == n for k, n in sidecar.get('usage', {}).items()), r['request'] + ': usage sidecar mismatch')
        check(thread == r.get('thread_id'), r['request'] + ': thread mismatch')
        process = read(p / 'process.json')
        check(process.get('exited') and process.get('returncode') == 0, r['request'] + ': non-success exit')
        stage = '/'.join(r['logical_request'].split('/')[1:-1])
        category = 'structural_correction' if r['structural_correction'] else 'semantic_repair_generation' if stage.startswith(('revision-', 'revision/')) else 'normal_generation'
        groups[category].update(complete); groups[category]['requests'] += 1
        stages[stage].update(complete); stages[stage]['requests'] += 1
        if r.get('elapsed_seconds') is not None: stages[stage]['request_seconds'] += r['elapsed_seconds']
        total.update(complete)
        error_events = [e for e in events if e.get('type') == 'error']
        if error_events: notices.append({'request': r['request'], 'events': error_events})
        rows.append({'request': r['request'], 'category': category, 'stage': stage, 'public_identities': request_ids, 'usage': dict(complete), 'elapsed_seconds': r.get('elapsed_seconds'), 'stdout_sha256': sha(p / 'stdout.jsonl')})
    check(dict(total) == metrics['known_token_usage'], 'Aggregate public usage differs from metrics')
    check(len(rows) == metrics['native_process_starts'], 'Native count mismatch')
    snapshot = read(run / 'implementation-snapshot/snapshot.json')
    frozen_changes = [n for n, h in snapshot['files'].items() if sha(run / 'implementation-snapshot' / n) != h]
    current_changes = [n for n, h in snapshot['files'].items() if not (ROOT / n).exists() or sha(ROOT / n) != h]
    check(not frozen_changes and not current_changes, 'Implementation changed')
    replay = read(run / 'replay-check.json')
    check(replay == closed['replay'] and replay['status'] == 'matched' and replay['new_native_markers'] == 0, 'Replay receipt mismatch')
    out = {'case_id': case, 'status': 'passed' if not issues else 'discrepancies_found', 'scope': 'Independent standard-library JSON/text arithmetic and hashes only. Saved public counters, not provider billing. No analysis/replay/model/Skill execution.', 'native_starts': len(rows), 'unique_public_identities': len(identities), 'known_public_usage': dict(total), 'groups': dict(groups), 'stages': dict(stages), 'requests': rows, 'internal_notices': notices, 'outer_retries': metrics['network_retry_attempts'], 'unknown_usage_requests': metrics['unknown_usage_requests'], 'partial_usage': metrics['partial_token_usage'], 'http_attempts': metrics['http_attempts'], 'replay': replay, 'pinned_files_checked': len(snapshot['files']), 'implementation_sha256': snapshot['implementation_sha256'], 'frozen_changes': frozen_changes, 'current_changes': current_changes, 'issues': issues, 'created_at': datetime.now(timezone.utc).isoformat()}
    dest = V / 'receipt-audit'; dest.mkdir(exist_ok=True)
    (dest / (case + '.json')).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: out[k] for k in ['case_id', 'status', 'native_starts', 'known_public_usage', 'outer_retries', 'unknown_usage_requests', 'issues']}, ensure_ascii=False))
    return out

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('cases', nargs='+', choices=['ga4', '001', '010', '013'])
    for case in p.parse_args().cases: audit(case)
