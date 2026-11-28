"""Record the new user-authorized scope and immutable closed-run baseline."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = 'experiments/doe/runs/document-guided-ga4-processing-restart-high-20261117-172228'
BASELINE = '694561928259d08c00492843a036ad0196460f785e6bd5d2fb1e07ba8ef59445'

def create(name, value):
    with (HERE/name).open('x', encoding='utf-8') as handle:
        json.dump(value,handle,ensure_ascii=False,indent=2)
        handle.write('\n')

if __name__ == '__main__':
    roots = [PARENT, 'output/verification/online-ga4-processing-restart-20261117',
        'experiments/doe/runs/document-guided-ga4-cfg-recovery-high-20261117-135205',
        'output/verification/online-ga4-cfg-recovery-20261117']
    pins = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for name in roots for p in sorted((ROOT/name).rglob('*')) if p.is_file()}
    create('historical-pins.json', {'roots':roots,'files':pins,'count':len(pins)})
    create('continuation-state.json', {
        'status':'offline_implementation','created_at':datetime.now(timezone.utc).isoformat(),
        'authorization':'User requests generic review correction/retention, value/address distinction, dependency-local execution failures, operation-contract rigor audit; after offline acceptance exactly one fresh GA4 from retained current CFG and its sole controller-owned zero-call replay.',
        'baseline_implementation_sha256':BASELINE,'accepted_cfg_parent':PARENT,
        'normal_stage_policy':7,'inherited_initial_stages':3,'fresh_normal_requests':4,'workers':2,
        'structural_corrections_per_stage':1,'shared_repair_rounds':1,'native_timeout_seconds':2700,
        'native_extra_transient_attempts':2,'runtime':'gpt-6.1-sol/high/openai',
        'historical_files_pinned':len(pins),'production_freeze':'After acceptance through sole fresh run and replay.',
        'instructions':'Root owns dispatch only after acceptance. No old resume/replay, Skill execution, additional models/probes/cases/resampling, historical mutation or staged-worktree imports.'})
    print(json.dumps({'historical_files_pinned':len(pins),'status':'offline_implementation'}))
