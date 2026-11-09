"""Measure only CFG indexing over saved JSON; no historical analysis or replay."""
from pathlib import Path
from time import perf_counter
import hashlib
import importlib.util
import json
import statistics
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BEFORE = HERE / "before/src/skillflow/propagation/contracts/references.py"
GRAPH = ROOT / "experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/graph/revision.json"

spec = importlib.util.spec_from_file_location("_reference_index_before", BEFORE)
old = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = old
spec.loader.exec_module(old)
from skillflow.propagation.contracts import references as new

graph_bytes = GRAPH.read_bytes()
cfg = json.loads(graph_bytes)["cfg"]
timings = {"before": [], "after": []}
results = {}
for trial in range(3):
    for label, module in (("before", old), ("after", new)) if trial % 2 == 0 else (("after", new), ("before", old)):
        start = perf_counter()
        result = module.cfg_target_index(cfg)
        timings[label].append(perf_counter() - start)
        digest = hashlib.sha256(json.dumps(result, sort_keys=True, ensure_ascii=False,
            separators=(",", ":")).encode()).hexdigest()
        if label in results:
            assert digest == results[label]["sha256"]
        results[label] = {"targets": len(result), "sha256": digest}
assert results["before"] == results["after"]
assert GRAPH.read_bytes() == graph_bytes
out = {"scope": "Pure CFG index generation from saved GA4 JSON; no loader, compiler, solver, replay, target or Skill execution.",
    "graph_sha256": hashlib.sha256(graph_bytes).hexdigest(),
    "before_source_sha256": hashlib.sha256(BEFORE.read_bytes()).hexdigest(),
    "after_source_sha256": hashlib.sha256(Path(new.__file__).read_bytes()).hexdigest(),
    "ir_count": sum(len(b["instructions"]) for b in cfg["blocks"].values()),
    "results": results, "seconds": timings,
    "median_seconds": {k: statistics.median(v) for k, v in timings.items()},
    "equivalent_index": True, "historical_graph_unchanged": True,
    "new_model_calls": 0, "historical_replays": 0}
(HERE / "reference-index-benchmark.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2))
