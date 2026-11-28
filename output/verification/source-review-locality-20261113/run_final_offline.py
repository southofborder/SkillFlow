"""Run the final scoped, injected/offline acceptance on one frozen implementation."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

VERIFY = Path(__file__).resolve().parent
ROOT = VERIFY.parents[2]
sys.path.insert(0, str(ROOT))
from skillflow.common.recording import implementation_provenance


def create(name, value):
    with (VERIFY / name).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


before = implementation_provenance()
paths = ['tests/document_guided']
patterns = ('test_input_*.py', 'test_demand_*.py', 'test_constraint_*.py', 'test_sensitivity_*.py')
doe = {p.relative_to(ROOT).as_posix() for pattern in patterns for p in (ROOT / 'tests/doe').glob(pattern)}
doe.update('tests/doe/' + name for name in ('test_formal_runner.py', 'test_reviewed_input_necessity.py',
    'test_source_input_findings.py', 'test_review_validation_barriers.py', 'test_review_isolation_integrity.py'))
paths += sorted(doe)
paths += ['tests/common/test_structural_validation.py', 'tests/common/test_structural_correction.py',
          'tests/common/test_prompt_format.py']
xml = VERIFY / 'final-scoped.xml'
command = [sys.executable, '-B', '-m', 'pytest', *paths, '-q', '--junitxml=' + str(xml)]
create('final-test-start.json', {'started_at':datetime.now(timezone.utc).isoformat(), 'command':command,
    'implementation':before, 'model_calls':0, 'skill_execution':False, 'historic_replay':False})
started = time.perf_counter()
with (VERIFY / 'final-scoped.log').open('x', encoding='utf-8') as log:
    result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
after = implementation_provenance()
cases = ET.parse(xml).getroot().findall('.//testcase') if xml.is_file() else []
failures = [{'class':c.get('classname'),'name':c.get('name'),'failure':c.find('failure').get('message')}
            for c in cases if c.find('failure') is not None]
errors = [{'class':c.get('classname'),'name':c.get('name'),'error':c.find('error').get('message')}
          for c in cases if c.find('error') is not None]
summary = {'status':'passed' if result.returncode == 0 and before == after and cases else 'failed',
    'finished_at':datetime.now(timezone.utc).isoformat(), 'exit_code':result.returncode,
    'elapsed_seconds':time.perf_counter()-started, 'implementation_sha256':after['sha256'],
    'implementation_unchanged':before==after, 'test_count':len(cases),
    'passed':sum(not any(c.find(x) is not None for x in ('failure','error','skipped')) for c in cases),
    'skipped':sum(c.find('skipped') is not None for c in cases), 'failures':failures, 'errors':errors,
    'receipt':xml.relative_to(ROOT).as_posix(), 'xml_sha256':hashlib.sha256(xml.read_bytes()).hexdigest() if xml.is_file() else None,
    'scope':paths, 'whole_repository_all_green':False, 'model_calls':0, 'skill_execution':False, 'historic_replay':False}
create('final-test-result.json', summary)
print(json.dumps(summary, ensure_ascii=False, indent=2))
raise SystemExit(0 if summary['status']=='passed' else 1)
