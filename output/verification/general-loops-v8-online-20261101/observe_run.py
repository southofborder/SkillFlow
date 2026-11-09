"""Passive local observation of this authorization's single run."""
from pathlib import Path
from datetime import datetime, timezone
import ctypes
import json

VERIFY = Path(__file__).resolve().parent
RUN = Path(json.loads((VERIFY / 'prepared-run.json').read_text(encoding='utf-8'))['run_directory'])

def read(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}

def alive(pid):
    if not pid:
        return False
    kernel = ctypes.windll.kernel32
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x1000, False, int(pid))
    if not handle:
        return False
    try:
        code = ctypes.c_ulong()
        return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
    finally:
        kernel.CloseHandle(handle)

result = read(RUN / 'result.json')
start = read(RUN / 'controller-started.json')
finish = read(RUN / 'controller-finished.json')
active = []
starts = list((RUN / 'transport').rglob('started.json'))
for path in starts:
    if not (path.parent / 'process.json').exists():
        pid = read(path.parent / 'pid.json').get('pid')
        active.append({'attempt': path.parent.relative_to(RUN).as_posix(), 'pid': pid, 'alive': alive(pid),
                       'started_at': read(path).get('started_at')})
snapshot = {'observed_at': datetime.now(timezone.utc).isoformat(), 'run_directory': str(RUN),
    'controller_pid': start.get('pid'), 'controller_alive': alive(start.get('pid')),
    'controller_finished': finish, 'analysis_finished': read(RUN / 'analysis-finished.json'),
    'status': result.get('status'), 'stage': result.get('stage'),
    'stages': {key: value.get('status') for key, value in result.get('stages', {}).items()},
    'counts': result.get('counts'), 'native_starts': len(starts),
    'accepted_answers': len(list((RUN / 'transport').rglob('accepted.json'))),
    'active_attempts': active, 'doe_result_exists': (RUN / 'doe/doe-result.json').is_file()}
target = VERIFY / 'live.json'
temporary = target.with_suffix('.tmp')
temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
temporary.replace(target)
print(json.dumps(snapshot, ensure_ascii=False))
