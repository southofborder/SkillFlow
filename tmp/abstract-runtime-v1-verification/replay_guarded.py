import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path('D:/projects/SkillFlow')
TOOLS = ROOT / 'packages/skill-ir/experiments/propagation/tools'
RUN = ROOT / 'packages/skill-ir/experiments/propagation/runs/abstract-runtime-v1-20260928-143306'
sys.path.insert(0, str(ROOT / 'packages/skill-ir/src'))

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

guard = load('offline_guard', TOOLS / 'recover_reports_offline.py')
pilot = load('runtime_pilot', TOOLS / 'run_runtime_pilot.py')
before = json.loads((RUN / 'summary.json').read_text(encoding='utf-8'))
with guard.network_guard() as attempts:
    after = pilot.execute(RUN, replay=True)
checks = []
for original, replay in zip(before['cases'], after['cases'], strict=True):
    keys = ('case_id', 'annotation', 'propagation', 'counts', 'unresolved')
    same = all(original[k] == replay[k] for k in keys)
    checks.append({'case_id': original['case_id'], 'same_status_counts_and_unresolved': same})
    assert same, checks[-1]
record = {**guard.guard_record(attempts), 'cases': checks,
          'replay_logical_calls_added': 0,
          'note': 'summary 中的调用数量是原运行累计次数；本次离线重放未建立在线客户端或触发网络。'}
(RUN / 'verification/zero-api-replay.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
