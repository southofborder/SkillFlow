"""Offline-derived, bounded backend comparison. No historical runner or replay API.

The parent owns exactly the child it creates. Full-input dispatch belongs to the
root operator; preparing this harness does not authorize a full-input execution.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import traceback


ROOT = Path(__file__).resolve().parent
POLICY = {"classification": "offline-derived", "model_calls": 0, "model_tokens": 0,
          "execute_skill": False, "historical_replay": False, "resume_controller": False}


def now():
    return datetime.now(timezone.utc).isoformat()


def checked_output(path):
    path = Path(path).resolve()
    if path == ROOT or not path.is_relative_to(ROOT):
        raise ValueError("benchmark outputs must be new children of the verification directory")
    return path


def write_json(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def implementation(src, micro=False):
    selected = (
        "propagation/data/registry.py", "propagation/data/models.py", "propagation/data/_computation.py",
        "propagation/loop_domain.py", "common/recording.py",
    )
    files = ([src / "skillflow" / name for name in selected] if micro else
             sorted((src / "skillflow").rglob("*.py")))
    hashes = {path.relative_to(src).as_posix(): digest(path) for path in files if path.is_file()}
    encoded = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()
    return {"source_directory": str(src), "files": hashes, "sha256": hashlib.sha256(encoded).hexdigest()}


class ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t)]


def process_counters(handle=None):
    """Only the worker itself or the Popen handle owned by this parent is read."""
    if os.name != "nt":
        return {"available": False, "reason": "Windows process counters unavailable"}
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessMemoryCounters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.FILETIME),
                                      ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME),
                                      ctypes.POINTER(wintypes.FILETIME)]
    kernel.GetProcessTimes.restype = wintypes.BOOL
    handle = kernel.GetCurrentProcess() if handle is None else wintypes.HANDLE(int(handle))
    memory = ProcessMemoryCounters()
    memory.cb = ctypes.sizeof(memory)
    if psapi.GetProcessMemoryInfo(handle, ctypes.byref(memory), memory.cb):
        result = {"available": True, "working_set_bytes": memory.WorkingSetSize,
                  "native_peak_working_set_bytes": memory.PeakWorkingSetSize,
                  "private_bytes": memory.PrivateUsage, "commit_bytes": memory.PagefileUsage,
                  "native_peak_commit_bytes": memory.PeakPagefileUsage, "page_faults": memory.PageFaultCount}
    else:
        result = {"available": False, "winerror": ctypes.get_last_error()}
    values = [wintypes.FILETIME() for _ in range(4)]
    if kernel.GetProcessTimes(handle, *(ctypes.byref(value) for value in values)):
        ticks = [(value.dwHighDateTime << 32) | value.dwLowDateTime for value in values]
        result["cpu_seconds"] = (ticks[2] + ticks[3]) / 10_000_000
    return result


class Measurements:
    def __init__(self, output):
        self.output = output
        self.lock = threading.RLock()
        self.started = time.perf_counter()
        self.phase = "preparation"
        self.phase_started = self.started
        self.phase_cpu = time.process_time()
        self.intervals = []
        self.validators = {}
        self.ir_counts = Counter()
        self.latest = None
        self.maxima = {}
        self.block_maxima = {}
        self.block_attempt_counts = Counter()
        self.last_attempt = None
        self.finished = threading.Event()
        self.thread = None
        self.status = "running"
        self.result = {}

    @contextmanager
    def stage(self, name):
        with self.lock:
            self.phase, self.phase_started, self.phase_cpu = name, time.perf_counter(), time.process_time()
        self.flush()
        try:
            yield
        finally:
            with self.lock:
                self.intervals.append({"stage": name, "wall_seconds": time.perf_counter() - self.phase_started,
                                       "cpu_seconds": time.process_time() - self.phase_cpu})
            self.flush()

    def validation(self, name, size):
        with self.lock:
            bucket = self.validators.setdefault(self.phase, {}).setdefault(name, {
                "calls": 0, "total_input_rows": 0, "max_input_rows": 0, "last_input_rows": 0})
            bucket["calls"] += 1
            bucket["total_input_rows"] += size
            bucket["max_input_rows"] = max(bucket["max_input_rows"], size)
            bucket["last_input_rows"] = size

    def evaluation(self, interpreter, ir, state, caller):
        values = caller.f_locals
        environments = values.get("environments")
        rows = values.get("rows")
        registry = interpreter.registry
        latest = {"instruction_id": ir["id"], "block_id": interpreter.current_block,
                  "incoming_environment_rows": len(environments) if environments is not None else None,
                  "partition_rows": len(rows) if rows is not None else None,
                  "entry_state_bindings": len(state.bindings), "ordinary_data_records": len(registry._records),
                  "loop_families": len(getattr(registry, "facts", {})),
                  "loop_relation_facts": getattr(registry, "_fact_count", getattr(registry, "fact_revision", 0))}
        latest["registry_records"] = latest["ordinary_data_records"] + latest["loop_families"]
        stats = values.get("stats", getattr(values.get("result"), "stats", None))
        if isinstance(stats, dict):
            latest["current_solver_stats"] = json.loads(json.dumps(stats))
        with self.lock:
            self.ir_counts[ir["id"]] += 1
            self.latest = latest
            block = interpreter.current_block
            block_maxima = self.block_maxima.setdefault(block, {})
            for name in ("incoming_environment_rows", "partition_rows", "entry_state_bindings",
                         "ordinary_data_records", "loop_families", "loop_relation_facts", "registry_records"):
                number = latest[name]
                if number is not None:
                    self.maxima[name] = max(self.maxima.get(name, 0), number)
                    block_maxima[name] = max(block_maxima.get(name, 0), number)
            if isinstance(stats, dict) and "block_evaluations" in stats:
                sequence = stats["block_evaluations"] + 1
                latest["block_attempt_sequence"] = sequence
                marker = (block, sequence)
                if marker != self.last_attempt:
                    self.block_attempt_counts[block] += 1
                    self.last_attempt = marker

    def snapshot(self):
        with self.lock:
            return {**POLICY, "pid": os.getpid(), "recorded_at": now(), "status": self.status,
                    "stage": self.phase, "wall_seconds_since_worker_start": time.perf_counter() - self.started,
                    "cpu_seconds_since_process_start": time.process_time(),
                    "current_stage_wall_seconds": time.perf_counter() - self.phase_started,
                    "completed_stages": list(self.intervals), "validators_by_stage": json.loads(json.dumps(self.validators)),
                    "ir_evaluation_count": sum(self.ir_counts.values()), "ir_evaluations": dict(self.ir_counts),
                    "observed_maxima": dict(self.maxima), "observed_block_maxima": json.loads(json.dumps(self.block_maxima)),
                    "observed_block_attempt_count": sum(self.block_attempt_counts.values()),
                    "observed_block_attempt_counts": dict(self.block_attempt_counts),
                    "observation_scope": "Maxima are sampled at every IR entry. Attempt counts use the solver's completed-block counter plus one; attempts with no IR evaluation are absent. Returned solver statistics remain authoritative when available.",
                    "latest_evaluation": self.latest, "process": process_counters(), "result": self.result}

    def flush(self):
        with self.lock:
            write_json(self.output / "worker-progress.json", self.snapshot())

    def start(self):
        def observe():
            while not self.finished.wait(2.0):
                self.flush()
        self.thread = threading.Thread(target=observe, daemon=True, name="offline-local-progress")
        self.thread.start()

    def stop(self):
        self.finished.set()
        if self.thread:
            self.thread.join(timeout=5)
        self.flush()


def install_instrumentation(measure):
    from skillflow.propagation.data.registry import DataRegistry
    from skillflow.propagation.records import PropagationRecords
    from skillflow.propagation.interpreter import TransferInterpreter
    from skillflow.propagation import facts
    from skillflow.propagation.data import registry as registry_module

    original = DataRegistry._validate_records
    def registry_records(self, records):
        measure.validation("DataRegistry._validate_records", len(records))
        return original(self, records)
    DataRegistry._validate_records = registry_records

    original_values = DataRegistry._validate_data_values
    def data_values(records):
        measure.validation("DataRegistry._validate_data_values", len(records))
        return original_values(records)
    DataRegistry._validate_data_values = staticmethod(data_values)

    original_store = PropagationRecords.validate
    def record_store(self):
        measure.validation("PropagationRecords.validate", len(self._records))
        return original_store(self)
    PropagationRecords.validate = record_store

    if hasattr(PropagationRecords, "check_references"):
        original_references = PropagationRecords.check_references
        def references(self):
            measure.validation("PropagationRecords.check_references", len(self._records))
            return original_references(self)
        PropagationRecords.check_references = references

    original_evaluate = TransferInterpreter.evaluate
    def evaluate(self, ir, spec, state):
        frame = sys._getframe(1)
        try:
            measure.evaluation(self, ir, state, frame)
        finally:
            del frame
        return original_evaluate(self, ir, spec, state)
    TransferInterpreter.evaluate = evaluate

    original_data = registry_module.validate_data_records
    def data_records(records, *args, **kwargs):
        measure.validation("validate_data_records", len(records))
        return original_data(records, *args, **kwargs)
    original_facts = facts.validate_propagation_facts
    def fact_records(*args, **kwargs):
        measure.validation("validate_propagation_facts", len(kwargs.get("records", {})))
        return original_facts(*args, **kwargs)
    replacements = [(original_data, data_records), (original_facts, fact_records)]
    # Bind aliases already imported by the selected pipeline to the same wrappers.
    for module_name, module in tuple(sys.modules.items()):
        if module is None or not module_name.startswith("skillflow."):
            continue
        for name, value in tuple(vars(module).items()):
            for source, replacement in replacements:
                if value is source:
                    setattr(module, name, replacement)


def block_external_execution():
    def forbidden(*args, **kwargs):
        raise RuntimeError("offline-derived benchmark forbids network and child execution")
    socket.socket.connect = forbidden
    socket.socket.connect_ex = forbidden
    socket.create_connection = forbidden
    subprocess.Popen = forbidden


def load_pipeline(src):
    sys.path.insert(0, str(src))
    from skillflow.propagation.solver import propagate
    from skillflow.propagation.loading import materials_from_result
    from skillflow.doe.formal_runner import _compute
    import skillflow
    if not Path(skillflow.__file__).resolve().is_relative_to(src):
        raise RuntimeError("worker imported a different implementation")
    for name, module in tuple(sys.modules.items()):
        location = getattr(module, "__file__", None)
        if name.startswith("skillflow.") and location and not Path(location).resolve().is_relative_to(src):
            raise RuntimeError("mixed implementation import: " + name)
    return propagate, materials_from_result, _compute


def full_worker(args, measure, pipeline):
    propagate, materials_from_result, compute = pipeline
    input_path = Path(args.input).resolve()
    with measure.stage("input-preparation"):
        value = json.loads(input_path.read_text(encoding="utf-8"))
        if args.input_sha256 and digest(input_path) != args.input_sha256:
            raise ValueError("fixed input digest differs")
        from skillflow.propagation.contracts.limitations import unmodeled_ids
        source_gaps = sorted(unmodeled_ids(value["payload"]))
        measure.result.update({"input_sha256": digest(input_path), "input_unmodeled_ids": source_gaps,
                               "source_unmodeled_ids": sorted({item["instruction_id"]
                                   for item in value["payload"].get("processing_gaps", [])
                                   if item.get("unmodeled") and item.get("origin", "source") == "source"}),
                               "instruction_count": sum(len(block["instructions"]) for block in value["material"]["cfg"]["blocks"].values())})
    with measure.stage("propagation"):
        solved = propagate(value["material"]["cfg"], value["payload"], max_variants=args.max_variants)
        measure.result.update({"propagation_status": solved.status, "propagation_stats": dict(solved.stats),
                               "coverage_counts": dict(Counter(solved.coverage.values())),
                               "propagation_diagnostics": solved.diagnostics})
    with measure.stage("materials"):
        facts = materials_from_result(solved, material=value["material"], raw_annotation=value["raw_annotation"],
            compiled_annotation=value["compiled_annotation"], mapping=value["mapping"],
            source_metadata=value.get("source_metadata"), wire_annotation=value.get("wire_annotation"),
            _validated_annotation=True, provenance={"kind": "offline-derived"})
    with measure.stage("doe"):
        review, result, index, support = compute(facts, facts.annotation)
        measure.result.update({"doe_status": result.get("status"), "sink_count": len(result.get("sinks", []))})
    with measure.stage("json-save"):
        output = Path(args.output)
        write_json(output / "propagation-output.json", {**POLICY, "status": facts.status,
            "coverage": facts.coverage, "diagnostics": facts.diagnostics, "stats": facts.stats,
            "data": facts.data, "records": facts.records, "sinks": facts.sinks,
            "initial_data": facts.initial_data, "initial_state": facts.initial_state})
        write_json(output / "doe-output.json", {**POLICY, "result": result, "index": index, "support": support})


def micro_worker(args, measure, pipeline):
    from skillflow.propagation.data import DataRegistry, LiteralContent, Origin
    from skillflow.propagation.data.registry import _Identity, SCHEMA_VERSION
    from skillflow.propagation.loop_domain import LoopFactRegistry
    with measure.stage("micro-preparation"):
        seed = DataRegistry("offline-literal-959")
        rows = []
        for index in range(args.records):
            name = f"literal:{index}"
            allocation = _Identity(kind="result", key=name)
            rows.append({"identity": allocation.model_dump(mode="python"),
                         "data": {"id": seed._id(allocation), "content": {"form": "literal", "value": True},
                                  "origin": {"at": name}}})
        seed = DataRegistry.from_dict({"schema_version": SCHEMA_VERSION, "namespace": seed.namespace, "records": rows})
        registry = LoopFactRegistry(seed, {})
        if hasattr(registry, "enable_computation"):
            registry.enable_computation()
        repeated_key = f"literal:{args.records - 1}"
        before_count, before_revision = len(registry), registry.revision
    with measure.stage("literal-repeat"):
        for _ in range(args.repeats):
            registry.create_result(repeated_key, content=LiteralContent(value=True), origin=Origin(at=repeated_key))
    measure.result.update({"record_count": len(registry), "literal_repetitions": args.repeats,
                           "ordinary_records": args.records, "loop_families": 0,
                           "record_count_unchanged": len(registry) == before_count,
                           "revision_unchanged": registry.revision == before_revision,
                           "fixture_limit": "No loop variants; measures repeated ordinary literal validation only."})


def worker(args):
    output = checked_output(args.output)
    src = Path(args.src).resolve()
    measure = Measurements(output)
    measure.start()
    code_identity = implementation(src, micro=args.kind == "micro")
    write_json(output / "worker-provenance.json", {**POLICY, "created_at": now(), "variant": args.variant,
        "python": sys.version, "executable": sys.executable, "kind": args.kind, "implementation": code_identity,
        "input": str(Path(args.input).resolve()) if args.input else None,
        "benchmark_file_sha256": digest(__file__), "limit_seconds": args.limit_seconds})
    try:
        block_external_execution()
        with measure.stage("imports"):
            pipeline = load_pipeline(src)
            install_instrumentation(measure)
        if args.kind == "micro":
            micro_worker(args, measure, pipeline)
        else:
            full_worker(args, measure, pipeline)
        measure.status = "complete"
    except BaseException as error:
        measure.status = "failed"
        measure.result["error"] = {"type": type(error).__name__, "message": str(error)}
        (output / "worker-traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
    finally:
        measure.result["implementation_unchanged"] = implementation(src, micro=args.kind == "micro")["sha256"] == code_identity["sha256"]
        measure.stop()
        write_json(output / "worker-result.json", measure.snapshot())
    return 0 if measure.status == "complete" else 1


def run_parent(args):
    output = checked_output(args.output)
    if output.exists():
        raise ValueError("benchmark output must be new; existing evidence is never overwritten")
    output.mkdir(parents=True)
    lock_path = ROOT / "offline-benchmark-owner.lock"
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(lock_fd, json.dumps({"pid": os.getpid(), "output": str(output), "created_at": now()}).encode())
    os.close(lock_fd)
    command = [sys.executable, "-B", str(Path(__file__).resolve()), "_worker", "--src", str(Path(args.src).resolve()),
               "--variant", args.variant, "--kind", args.kind, "--output", str(output),
               "--limit-seconds", str(args.limit_seconds), "--records", str(args.records),
               "--repeats", str(args.repeats), "--max-variants", str(args.max_variants)]
    if args.input:
        command += ["--input", str(Path(args.input).resolve())]
    if args.input_sha256:
        command += ["--input-sha256", args.input_sha256]
    started = time.perf_counter()
    peak_private, peak_working, peak_commit, sampled_cpu, samples = 0, 0, 0, 0, 0
    child = None
    timed_out = False
    try:
        with (output / "worker-stdout.txt").open("wb") as stdout, (output / "worker-stderr.txt").open("wb") as stderr:
            child = subprocess.Popen(command, stdout=stdout, stderr=stderr,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            write_json(output / "parent-start.json", {**POLICY, "parent_pid": os.getpid(), "owned_child_pid": child.pid,
                "command": command, "created_at": now(), "limit_seconds": args.limit_seconds,
                "limit_scope": "Child startup, imports, preparation, propagation, DOE, and JSON save."})
            while True:
                counters = process_counters(getattr(child, "_handle", None))
                samples += 1
                peak_private = max(peak_private, counters.get("private_bytes", 0))
                peak_working = max(peak_working, counters.get("native_peak_working_set_bytes", 0))
                peak_commit = max(peak_commit, counters.get("native_peak_commit_bytes", 0))
                sampled_cpu = max(sampled_cpu, counters.get("cpu_seconds", 0))
                elapsed = time.perf_counter() - started
                if child.poll() is not None:
                    break
                if elapsed >= args.limit_seconds:
                    timed_out = True
                    child.terminate()  # Only the exact Popen child owned above.
                    child.wait(timeout=10)
                    break
                write_json(output / "parent-progress.json", {**POLICY, "owned_child_pid": child.pid,
                    "wall_seconds": elapsed, "process": counters, "sampled_peak_private_bytes": peak_private,
                    "native_peak_working_set_bytes": peak_working, "native_peak_commit_bytes": peak_commit})
                time.sleep(min(0.5, max(0.001, args.limit_seconds - elapsed)))
        latest_path = output / "worker-progress.json"
        latest = json.loads(latest_path.read_text(encoding="utf-8")) if latest_path.exists() else None
        receipt = {**POLICY, "variant": args.variant, "kind": args.kind,
            "status": "timeout" if timed_out else "complete" if child.returncode == 0 else "failed",
            "parent_pid": os.getpid(), "owned_child_pid": child.pid, "child_exit_code": child.returncode,
            "limit_seconds": args.limit_seconds, "wall_seconds": time.perf_counter() - started,
            "child_cpu_seconds": sampled_cpu, "sampled_peak_private_bytes": peak_private,
            "native_peak_working_set_bytes": peak_working, "native_peak_commit_bytes": peak_commit,
            "process_samples": samples, "memory_note": "Private peak is a 0.5-second sampled lower bound; working-set/commit peaks are native Windows counters.",
            "terminated_owned_child_at_cap": timed_out, "latest_worker_observation": latest}
        write_json(output / "parent-result.json", receipt)
        print(json.dumps({key: receipt[key] for key in ("variant", "kind", "status", "wall_seconds", "child_cpu_seconds")}), flush=True)
        return 124 if timed_out else child.returncode
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            child.wait(timeout=10)
        lock_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "_worker"))
    parser.add_argument("--src", required=True)
    parser.add_argument("--variant", required=True, choices=("baseline", "current"))
    parser.add_argument("--kind", choices=("full", "micro"), default="full")
    parser.add_argument("--input")
    parser.add_argument("--input-sha256")
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit-seconds", type=float, default=1800)
    parser.add_argument("--records", type=int, default=959)
    parser.add_argument("--repeats", type=int, default=1486)
    parser.add_argument("--max-variants", type=int, default=100000)
    args = parser.parse_args()
    if not 0 < args.limit_seconds <= 1800:
        parser.error("the total parent-enforced limit must be in (0, 1800]")
    if args.records < 1 or args.repeats < 1:
        parser.error("micro fixture counts must be positive")
    if args.kind == "full" and not args.input:
        parser.error("full workers require a fixed offline input")
    return worker(args) if args.mode == "_worker" else run_parent(args)


if __name__ == "__main__":
    raise SystemExit(main())
