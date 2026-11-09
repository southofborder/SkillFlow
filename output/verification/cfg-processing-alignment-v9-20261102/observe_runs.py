"""Read local progress metadata for this four-case batch, without dispatch."""
from datetime import datetime, timezone
from pathlib import Path
import ctypes
import json

BASE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


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


def main():
    queue = read(BASE / "prepared-runs.json")
    rows = []
    for item in queue.get("run_order", []):
        run = Path(item["run_directory"])
        result, started = read(run / "result.json"), read(run / "controller-started.json")
        attempts = list((run / "transport").rglob("started.json"))
        active = []
        for marker in attempts:
            if not (marker.parent / "process.json").exists():
                pid = read(marker.parent / "pid.json").get("pid")
                active.append({"attempt":marker.parent.relative_to(run).as_posix(),
                               "pid":pid,"alive":alive(pid),"started_at":read(marker).get("started_at")})
        rows.append({"case_id":item["case_id"],"run_directory":str(run),
            "controller_pid":started.get("pid"),"controller_alive":alive(started.get("pid")),
            "controller_finished":read(run / "controller-finished.json"),
            "analysis_finished":read(run / "analysis-finished.json"),
            "status":result.get("status"),"stage":result.get("stage"),"counts":result.get("counts"),
            "stages":{key:value.get("status") for key,value in result.get("stages",{}).items()},
            "native_starts":len(attempts),"accepted_answers":len(list((run / "transport").rglob("accepted.json"))),
            "active_attempts":active,"doe_result_exists":(run / "doe/doe-result.json").is_file()})
    supervisor = read(BASE / "queue-started.json")
    snapshot = {"observed_at":datetime.now(timezone.utc).isoformat(),
        "supervisor_alive":alive(supervisor.get("pid")),"queue":read(BASE / "queue-live.json"),"runs":rows}
    path = BASE / "live.json";temp=path.with_suffix(".tmp")
    temp.write_text(json.dumps(snapshot,indent=2)+"\n",encoding="utf-8");temp.replace(path)
    print(json.dumps(snapshot,indent=2))


if __name__ == "__main__":
    main()
