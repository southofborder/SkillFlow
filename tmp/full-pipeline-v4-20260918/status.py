"""Read only terminal case artifacts; never open active recording files."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918'
rows = []
for path in sorted((RUN / 'cases').glob('*/result.json')):
    data = json.loads(path.read_text(encoding='utf-8'))
    rows.append({
        'case': path.parent.name,
        'feedback': data['feedback']['status'],
        'revision': (data.get('selection') or {}).get('revision'),
        'annotation': data['annotation']['status'],
        'profiles': len(data['annotation'].get('profiles', {})),
        'unresolved': len(data['annotation'].get('unresolved', [])),
        'logical_calls': data.get('counts', {}).get('total_logical_calls'),
        'error': data.get('scheduler_error'),
    })
print(json.dumps({'completed': len(rows),
    'feedback': dict(Counter(row['feedback'] for row in rows)),
    'annotation': dict(Counter(row['annotation'] for row in rows)),
    'cases': rows}, ensure_ascii=False, indent=2))
