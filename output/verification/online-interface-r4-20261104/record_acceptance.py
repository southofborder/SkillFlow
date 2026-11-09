"""Record focused offline receipts and the implementation accepted for one batch."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from skillflow.common.recording import canonical_sha256, implementation_provenance


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def main():
    paths = sorted(BASE.glob('*.xml'), key=lambda path: path.stat().st_mtime_ns)
    if not (BASE / 'integrated-regression.xml').is_file():
        raise RuntimeError('Integrated receipt is not yet available')
    cases, receipts = {}, []
    for path in paths:
        root = ET.parse(path).getroot()
        rows = []
        for case in root.iter('testcase'):
            key = (case.get('classname'), case.get('name'))
            state = ('failed' if case.find('failure') is not None or case.find('error') is not None
                     else 'skipped' if case.find('skipped') is not None else 'passed')
            row = {'class': key[0], 'name': key[1], 'status': state,
                   'receipt': path.name}
            cases[key] = row
            rows.append(row)
        receipts.append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'tests': len(rows), 'failed': sum(row['status'] == 'failed' for row in rows),
                         'skipped': sum(row['status'] == 'skipped' for row in rows)})
    unresolved = [row for row in cases.values() if row['status'] == 'failed']
    if unresolved:
        raise RuntimeError('Latest scoped receipts still have failures: ' + json.dumps(unresolved))
    files = {path.relative_to(ROOT / 'src').as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted((ROOT / 'src/skillflow').rglob('*.py'))}
    provenance = implementation_provenance()
    manifest = {'files': files, 'sha256': canonical_sha256(files)}
    write(BASE / 'implementation-accepted/manifest.json', manifest)
    for name in files:
        target = BASE / 'implementation-accepted/src' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'src' / name, target)
    write(BASE / 'offline-test-receipts.json', {'receipts': receipts,
          'distinct_latest_cases': sorted(cases.values(), key=lambda row: (row['class'], row['name'])),
          'unresolved': unresolved})
    result = {'status': 'passed', 'accepted_at': datetime.now(timezone.utc).isoformat(),
              'implementation_sha256': provenance['sha256'], 'python_source_sha256': manifest['sha256'],
              'distinct_latest_cases': len(cases),
              'passed': sum(row['status'] == 'passed' for row in cases.values()),
              'skipped': sum(row['status'] == 'skipped' for row in cases.values()),
              'unresolved': 0, 'receipts': receipts, 'new_real_model_calls': 0,
              'skill_execution': False, 'historical_replays': 0,
              'limitation': 'Scoped offline acceptance, not a whole-repository all-green run or online semantic accuracy evidence.'}
    write(BASE / 'offline-acceptance.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
