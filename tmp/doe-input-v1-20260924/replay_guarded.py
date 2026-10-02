from pathlib import Path
import importlib.util,json,socket
import skill_ir.recording as recording
from skill_ir.experiments.report import ArtifactWriter
r=Path.cwd(); run=Path((r/'tmp/doe-input-v1-20260924/selected-run.txt').read_text(encoding='utf-8-sig').strip()); calls=[]
def forbidden(*a,**kw):
 calls.append('network_or_client');raise AssertionError('offline replay must not access API')
socket.socket.connect=forbidden; socket.create_connection=forbidden; recording.streaming_factory=forbidden
p=r/'packages/skill-ir/experiments/propagation/tools/run_pilot.py'; spec=importlib.util.spec_from_file_location('pilot_replay',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.streaming_factory=forbidden
code=module.main(['replay','--run-dir',str(run)])
ArtifactWriter(()).json(run/'verification/network-guard.json',{'model_or_network_attempts':len(calls),'exit_code':code,'mode':'offline_replay_with_network_and_factory_blocked'})
assert not calls
