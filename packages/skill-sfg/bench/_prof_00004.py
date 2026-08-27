"""One-shot cProfile of the Python FCG flood on 00004 (43 merge events, maxW=2110).
Measures whether storage-merge O(W^2) actually dominates Python runtime, or whether
the wall is elsewhere (flood volume / append_ids / cycle). Prints top cumulative +
tottime functions and the storage-merge trio's share explicitly."""
import cProfile, pstats, io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from skill_sfg.analyzer.pipeline import run_pipeline
from skill_sfg.output.json_generator import build_fcg_json

SKILL = r"D:/projects/SkillFlow/results/clawhub-top-k10000/corpus-src/00004_self-improving_1.2.16"

def _find_root(base):
    if os.path.isfile(os.path.join(base, "SKILL.md")):
        return base
    for e in sorted(os.listdir(base)):
        c = os.path.join(base, e)
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "SKILL.md")):
            return c
    return base

def run():
    root = _find_root(SKILL)
    result = run_pipeline(root, {"mode": "full", "cycle_expand": True})
    return build_fcg_json(result, input_source=SKILL)

pr = cProfile.Profile()
pr.enable()
fcg = run()
pr.disable()

st = fcg["security_profile"]["statistics"]
print("=== 00004 flood done ===")
print("  flow_state_count:", st.get("flow_state_count"))
print("  merge_event_count:", st.get("merge_event_count"))
print("  route_event_count:", st.get("route_event_count"))
print("  cycle_closure_count:", st.get("cycle_closure_count"))

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
ps.print_stats(30)
print("\n=== TOP 30 by tottime ===")
print(s.getvalue())

s2 = io.StringIO()
ps2 = pstats.Stats(pr, stream=s2).sort_stats("cumulative")
ps2.print_stats(30)
print("\n=== TOP 30 by cumulative ===")
print(s2.getvalue())

# explicit share of the storage-merge trio + append_ids
s3 = io.StringIO()
ps3 = pstats.Stats(pr, stream=s3)
ps3.stream = s3
for fn in ("_maybe_create_storage_merge_event", "_apply_merge_event_to_flows",
           "_update_merge_event_members", "_append_ids", "_unique_values",
           "build_flow_state_key", "_maybe_create_storage_read_flows"):
    ps3.print_stats(fn)
print("\n=== targeted functions ===")
print(s3.getvalue())
