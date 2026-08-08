"""Live counter probe (propagation-layer) for skill 00004 (Python FCG engine).

Prior run proved: run_pipeline=12s, storage-merge trio only ~13-20s of the flood,
and ~90% is in the UNINSTRUMENTED propagation loop. This version wraps the whole
propagation layer across analyzer/router/state/filter modules and reports INCLUSIVE
wall-time per function every 12s. Subtract children from parents to locate the leaf
hotspot. expand_label_flow's tot ~= whole flood loop; its heaviest child is the wall.
"""
import os
import sys
import time
import threading
import functools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# usage: python _time_00004.py <skill_dir_or_numeric_prefix> [hard_timeout_seconds]
_CORPUS = "D:/projects/SkillFlow/results/clawhub-top-k10000/corpus-src"
_arg = sys.argv[1] if len(sys.argv) > 1 else "00004"
if os.path.isdir(_arg):
    SKILL = _arg
else:
    # resolve numeric prefix like "00026" against corpus-src
    _match = [d for d in sorted(os.listdir(_CORPUS)) if d.startswith(_arg)]
    if not _match:
        print(f"[fatal] no skill dir matching prefix {_arg!r} in {_CORPUS}", flush=True)
        sys.exit(1)
    SKILL = os.path.join(_CORPUS, _match[0])

HARD_TIMEOUT = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0

from skill_fcg.analyzer.pipeline import run_pipeline
from skill_fcg.output.json_generator import build_fcg_json
from skill_fcg.flood import analyzer as A
from skill_fcg.flood import router as R
from skill_fcg.flood import state as S
from skill_fcg.flood import filter as F


def p(msg):
    print(msg, flush=True)


_stats = {}


def _wrap(mod, name, tag=None):
    if not hasattr(mod, name):
        p(f"[warn] no such fn: {mod.__name__}.{name}")
        return
    orig = getattr(mod, name)
    key = tag or name
    _stats[key] = [0, 0.0]

    @functools.wraps(orig)
    def wrapper(*a, **k):
        t0 = time.perf_counter()
        try:
            return orig(*a, **k)
        finally:
            dt = time.perf_counter() - t0
            s = _stats[key]
            s[0] += 1
            s[1] += dt
    setattr(mod, name, wrapper)


# top of loop body (inclusive ~= whole flood)
_wrap(A, "expand_label_flow")
# expand's direct children
_wrap(A, "_apply_action_steps_at_node")
_wrap(A, "_prioritize_edges")
_wrap(A, "_build_route_event")
_wrap(A, "emit_flows_for_label_at_edge")
# CRITICAL: these are `from X import Y` bare names in analyzer's namespace, so
# they MUST be wrapped on A (patching R/S/F is bypassed by the local binding).
_wrap(A, "classify_route_state")
_wrap(A, "ancestor_path")
_wrap(A, "build_flow_state_key")
_wrap(A, "apply_label_flow_filter")
# cycle closure path (also imported into A)
_wrap(A, "compute_cycle_closure")
_wrap(A, "record_cycle_periodic_observations")
# emit's children
_wrap(A, "_materialize_filter_events")
_wrap(A, "create_child_label_flow")
_wrap(A, "register_label_flow")
_wrap(A, "_merge_flow_into_representative")
# storage + merge (prior suspects, keep for comparison)
_wrap(A, "_record_storage_write")
_wrap(A, "_maybe_create_merge_relationships")
_wrap(A, "_process_pending_storage_reads")
_wrap(A, "_record_sink_observations_for_arrived")


_start = time.perf_counter()
_done = threading.Event()


def _dump(el, header):
    rows = sorted(_stats.items(), key=lambda kv: -kv[1][1])
    p(header)
    for name, (cnt, tot) in rows:
        if cnt:
            p(f"    {name:34s} cnt={cnt:>11d}  tot={tot:8.2f}s  avg={tot/cnt*1e6:8.2f}us")


def _monitor():
    while not _done.wait(12.0):
        el = time.perf_counter() - _start
        _dump(el, f"--- t={el:7.1f}s ---")
        if el >= HARD_TIMEOUT:
            _dump(el, f"=== HARD TIMEOUT @ {el:.1f}s (partial attribution) ===")
            os._exit(2)


mon = threading.Thread(target=_monitor, daemon=True)
mon.start()

p(f"[start] skill={SKILL}  exists={os.path.isdir(SKILL)}")

t0 = time.perf_counter()
result = run_pipeline(SKILL, {"mode": "full", "cycle_expand": True})
t1 = time.perf_counter()
p(f"[phase] run_pipeline   = {t1 - t0:8.2f}s")

fcg = build_fcg_json(result, input_source=SKILL)
t2 = time.perf_counter()
p(f"[phase] build_fcg_json = {t2 - t1:8.2f}s")
p(f"[phase] TOTAL          = {t2 - t0:8.2f}s")

_done.set()
p("")
p("=== FINAL (inclusive) ===")
for name, (cnt, tot) in sorted(_stats.items(), key=lambda kv: -kv[1][1]):
    if cnt:
        p(f"  {name:34s} cnt={cnt:>11d}  tot={tot:8.2f}s  avg={tot/cnt*1e6:8.2f}us")
