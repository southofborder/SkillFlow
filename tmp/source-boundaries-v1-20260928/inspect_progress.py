from pathlib import Path
import json

root = Path.cwd()
run = root / (root / 'tmp/source-boundaries-v1-20260928/selected-run.txt').read_text(encoding='utf-8').strip()
for case in ('001', '010', '013'):
    base = run / 'cases' / case
    for phase in ('feedback', 'annotation'):
        path = base / phase / 'result.json'
        if path.exists():
            value = json.loads(path.read_text(encoding='utf-8'))
            print(case, phase, {key: value.get(key) for key in ('status', 'reason')})
    for path in sorted(base.glob('**/call.json')):
        if 'replay' in path.parts:
            continue
        call = json.loads(path.read_text(encoding='utf-8'))
        if call.get('status') != 'running':
            continue
        print(case, str(path.relative_to(base)), {'status': call.get('status'), 'started_at': call.get('started_at')})
        transport_path = path.with_name('transport.json')
        if transport_path.exists():
            generations = json.loads(transport_path.read_text(encoding='utf-8'))
            attempts = generations[-1].get('http_attempts', [])
            stream = attempts[-1].get('stream', {}) if attempts else {}
            print('stream', {key: stream.get(key) for key in ('last_event_at', 'event_count', 'done_received', 'finish_reason')}, 'http_attempts', len(attempts))
