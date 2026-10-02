"""Carry explicitly unchanged graph/profile reviews with a visible origin note."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
parent = root / 'packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918'
child = parent.with_name('full-pipeline-v4-20260918-rerun-failed')
provenance = json.loads((child / 'rerun-provenance.json').read_text(encoding='utf-8'))
output = Path(__file__).parent / 'assistant-reviews'
output.mkdir(exist_ok=True)
for identifier in provenance['reused_cases']:
    original = root / 'tmp/full-pipeline-v4-20260918/assistant-reviews' / f'{identifier}.json'
    record = json.loads(original.read_text(encoding='utf-8'))
    old_case = json.loads((parent / f'cases/{identifier}/result.json').read_text(encoding='utf-8'))
    new_case = json.loads((child / f'cases/{identifier}/result.json').read_text(encoding='utf-8'))
    if old_case != new_case:
        raise ValueError(f'Reused case material changed: {identifier}')
    record['run_id'] = child.name
    for review in record['reviews']:
        review['observations'].insert(0, '本项复核继承自 full-pipeline-v4-20260918；本次复用样例的实际图、核对与标注记录逐字段相同，未新增模型调用。助手复核不等于用户人工确认。')
    target = output / f'{identifier}.json'
    if target.exists():
        raise ValueError(f'Review already exists: {target}')
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'carried {len(provenance["reused_cases"])} unchanged reviews')
