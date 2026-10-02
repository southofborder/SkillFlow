"""Validate external Markdown pairing and preservation; no Skill execution."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / 'tmp/skill-ir-review-set'
OUT = ROOT / 'result/advice_for_doe'
samples = json.loads((TMP / 'render-input.json').read_text('utf-8'))['samples']
expected = {s['basename'] + '.md' for s in samples} | {'README.md'}
assert {p.name for p in OUT.iterdir()} == expected, 'Unexpected/missing deliverable'
assert all(p.is_file() for p in OUT.iterdir()), 'Unexpected directory'
assert len(samples) == 30

lock = json.loads((TMP / 'advice-input-lock.json').read_text('utf-8'))
protected = ['dataset/skills', 'result/ir-IPP', 'result/suggestions', 'packages/skill-ir/src',
             'packages/skill-ir/experiments/semantics_baseline/frozen']
current = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for directory in protected for p in (ROOT / directory).rglob('*')
           if p.is_file() and '__pycache__' not in p.parts}
assert current == lock, 'Protected inputs or originals changed'

links = 0
identifier_count = 0
stats = []
for number, s in enumerate(samples, 1):
    stem = s['basename']
    assert stem.startswith(f'{number:03}-')
    sid = s['sample_id']
    expected_id = ('NQFDR'[(number - 1) // 6] + f'{(number - 1) % 6 + 1:02}')
    assert sid == expected_id
    assert s['repetition'] == (3 if sid == 'F03' else 1)
    assert hashlib.sha256(Path(s['analysis_path']).read_bytes()).hexdigest() == s['analysis_sha256']
    path = OUT / (stem + '.md')
    text = path.read_text('utf-8')
    assert f'**{sid}**' in text
    assert f'第 {s["repetition"]} 次' in text
    assert (ROOT / 'result/suggestions' / (stem + '.md')).as_posix() in text
    assert (ROOT / 'dataset/skills' / (stem + '.zip')).as_posix() in text
    assert (ROOT / 'result/ir-IPP' / (stem + '.png')).as_posix() in text
    valid = set(s['cfg']['blocks'])
    for block in s['cfg']['blocks'].values():
        for instruction in block['instructions']:
            valid.add(instruction['id'])
            valid.update(operand['identifier'] for operand in instruction['outputs'])
    refs = re.findall(r'\b(?:ir|block|result)_\d+\b', text)
    assert set(refs) <= valid, (sid, set(refs) - valid)
    identifier_count += len(refs)
    old = (ROOT / 'result/suggestions' / (stem + '.md')).read_text('utf-8')
    old_han = len(re.findall(r'[\u4e00-\u9fff]', old))
    new_han = len(re.findall(r'[\u4e00-\u9fff]', text))
    assert new_han < old_han, sid
    stats.append({'sample_id': sid, 'basename': stem, 'repetition': s['repetition'],
                  'original_han': old_han, 'condensed_han': new_han,
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

for path in sorted(OUT.glob('*.md')):
    text = path.read_text('utf-8')
    assert '\ufffd' not in text, f'Broken Unicode: {path}'
    assert text.count('```') % 2 == 0, f'Unclosed fence: {path}'
    for target in re.findall(r'\]\(([^)]+)\)', text):
        match = re.fullmatch(r'([A-Za-z]:/.*?)(?::(\d+))?', target)
        assert match, (path.name, 'Non-absolute local link', target)
        linked = Path(match[1])
        assert linked.is_file(), (path.name, 'Missing link', target)
        if match[2]:
            assert 0 < int(match[2]) <= len(linked.read_text('utf-8').splitlines()), target
        links += 1

old_total = sum(s['original_han'] for s in stats)
new_total = sum(s['condensed_han'] for s in stats)
report = {'sample_count': len(stats), 'markdown_count': len(expected),
          'protected_files_unchanged': len(lock), 'verified_links': links,
          'verified_cfg_identifiers': identifier_count, 'original_han': old_total,
          'condensed_han': new_total, 'reduction_percent': round(100 * (1 - new_total / old_total), 1),
          'samples': stats}
(TMP / 'advice-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'samples'}, ensure_ascii=False, indent=2))
