"""Final experiment verification; deliberately block all Python network calls."""
import hashlib
import json
import socket
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
run = Path((Path(__file__).parent / 'run-path.txt').read_text(encoding='utf-8-sig').strip())
sys.path.insert(0, str(root / 'packages/skill-ir/experiments/annotation_review/tools'))
import run_repair_once as pilot

def digest_calls():
    return {p.relative_to(run).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in run.rglob('*') if p.is_file() and 'calls' in p.parts}

attempts = []
def deny(*args, **kwargs):
    attempts.append('blocked network or online factory construction')
    raise AssertionError('Offline replay must never use a network or online client')

socket.socket.connect = deny
socket.socket.connect_ex = deny
socket.create_connection = deny
pilot.streaming_factory = deny
import skill_ir.annotation_review.refinement as refinement
import skill_ir.annotation_review.runner as review_runner
import skill_ir.security_profile.runner as annotation_runner
refinement.streaming_factory = deny
review_runner.streaming_factory = deny
annotation_runner.streaming_factory = deny

before_calls = digest_calls()
before_summary = json.loads((run / 'summary.json').read_text(encoding='utf-8'))
after_summary = pilot.run(run, replay=True)
after_calls = digest_calls()
case_replays = {p.parent.name: json.loads(p.read_text(encoding='utf-8'))
                for p in (run / 'cases').glob('*/pilot-replay.json')}
errors = [key for key, value in case_replays.items() if value['status'] != 'completed']
cfg_errors = list((run / 'cfg-reviews').glob('*-driver-error.json'))
receipt = {
    'network_blocked': True, 'network_attempts': attempts,
    'logical_calls_added': 0 if before_calls == after_calls else None,
    'call_records_unchanged': before_calls == after_calls,
    'stopping_decisions_unchanged': before_summary == after_summary,
    'case_replays': case_replays,
    'cfg_driver_errors': [p.name for p in cfg_errors],
    'status': 'matched' if not errors and not cfg_errors and not attempts and
                          before_calls == after_calls and before_summary == after_summary else 'mismatch',
    'notice': 'The saved execution_error is reproduced as execution_error, not reclassified as success.'
}
(run / 'replay-validation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(receipt, ensure_ascii=False, indent=2))
raise SystemExit(0 if receipt['status'] == 'matched' else 1)
