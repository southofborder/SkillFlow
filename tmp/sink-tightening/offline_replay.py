"""Replay current experiment with network and online factories prohibited."""
import json
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'packages/skill-ir/src'))
sys.path.insert(0, str(ROOT / 'packages/skill-ir/experiments/propagation/tools'))
import run_tightening_pilot as pilot
from skill_ir.recording import read_json, sha_file

run_dir = Path((ROOT / 'tmp/sink-tightening/run-path.txt').read_text(encoding='utf-8').strip())
attempts = []
def blocked(*args, **kwargs):
    attempts.append('network_or_online_client')
    raise AssertionError('offline replay attempted network or online client creation')
socket.socket.connect = blocked
socket.socket.connect_ex = blocked
socket.create_connection = blocked
pilot.streaming_factory = blocked

before_summary = read_json(run_dir / 'summary.json')
before = {p.relative_to(run_dir).as_posix(): sha_file(p)
          for p in run_dir.glob('cases/*/propagation/doe-input.json')
          if (p.parent / 'manifest.json').exists()}
summary = pilot.execute(run_dir, replay=True)
after = {p.relative_to(run_dir).as_posix(): sha_file(p)
         for p in run_dir.glob('cases/*/propagation/doe-input.json')
         if (p.parent / 'manifest.json').exists()}
assert before == after
assert not attempts
statuses = lambda value: [{key: row[key] for key in ('case_id', 'annotation', 'propagation')}
                         for row in value['cases']]
assert statuses(summary) == statuses(before_summary)
assert summary['logical_calls'] == before_summary['logical_calls'] == 3
receipt = {'status': 'matched', 'replay_model_calls': 0, 'network_attempts': len(attempts),
           'blocked_network_and_online_client_creation': True,
           'final_doe_file_sha256': after, 'case_statuses': statuses(summary),
           'historical_logical_calls': summary['logical_calls']}
(run_dir / 'replay-verification.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(receipt, ensure_ascii=False))
