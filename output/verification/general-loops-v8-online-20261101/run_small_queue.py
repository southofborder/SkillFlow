"""Run exactly the three authorized prepared cases after the GA4 controller exits."""
from pathlib import Path
from datetime import datetime, timezone
import ctypes
import json
import os
import subprocess
import sys
import time
import traceback

PROJECT = Path('D:/projects/SkillFlow')
sys.path.insert(0, str(PROJECT))
from skillflow.common.recording import implementation_provenance

VERIFY = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}

def save(value):
    value.update(observed_at=datetime.now(timezone.utc).isoformat(), supervisor_pid=os.getpid())
    p=VERIFY / 'queue-live.json'; t=p.with_suffix('.tmp')
    t.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');t.replace(p)

def alive(pid):
    k=ctypes.windll.kernel32;k.OpenProcess.restype=ctypes.c_void_p
    k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)];k.CloseHandle.argtypes=[ctypes.c_void_p]
    h=k.OpenProcess(0x1000,False,int(pid))
    if not h:return False
    try:
        code=ctypes.c_ulong();return bool(k.GetExitCodeProcess(h,ctypes.byref(code))) and code.value==259
    finally:k.CloseHandle(h)

def main():
    with (VERIFY / 'queue-started.json').open('x',encoding='utf-8') as f:
        json.dump({'pid':os.getpid(),'started_at':datetime.now(timezone.utc).isoformat()},f)
    q=read(VERIFY / 'small-queue.json');previous=Path(q['after_run']);pid=q['after_pid'];completed=[]
    try:
        for item in q['run_order']:
            while alive(pid):
                save({'phase':'waiting_for_previous_controller','previous_run':str(previous),'previous_pid':pid,'completed':completed})
                time.sleep(15)
            closed=read(previous / 'controller-finished.json')
            if not closed or read(previous / 'result.json').get('status')=='interrupted':
                raise RuntimeError('Prior controller did not close normally or was interrupted; no next run launched')
            if (VERIFY / 'queue-stop.json').exists():
                raise RuntimeError('Queue stop marker retained; no next run launched')
            if implementation_provenance()['sha256']!=q['implementation_sha256']:
                raise RuntimeError('Frozen implementation changed; no next run launched')
            directory=Path(item['run_directory'])
            if (directory / 'controller-started.json').exists():
                raise RuntimeError('Queued controller already started; refusing duplicate/resume')
            with (directory / 'controller-output.log').open('wb') as out:
                child=subprocess.Popen([sys.executable,'-B','-u',str(directory/'controller.py')],cwd=PROJECT,
                    stdout=out,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                save({'phase':'running_case','case_id':item['case_id'],'run_directory':str(directory),
                      'controller_pid':child.pid,'completed':completed})
                while child.poll() is None:
                    time.sleep(15)
                completed.append({'case_id':item['case_id'],'run_directory':str(directory),'returncode':child.returncode,
                                  'controller_finished':read(directory/'controller-finished.json')})
                previous,pid=directory,child.pid
        save({'phase':'queue_generation_closed','completed':completed,'report_pending':True})
    except BaseException as error:
        save({'phase':'queue_stopped','completed':completed,'error_type':type(error).__name__,'error':str(error)})
        (VERIFY/'queue-error.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise

if __name__=='__main__':main()
