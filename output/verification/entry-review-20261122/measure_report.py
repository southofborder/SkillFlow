"""Measure indexed report publication on controlled repeated-evidence inputs."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
import tracemalloc

from skillflow.common.artifact_io import atomic_write_chunks
from skillflow.doe.sensitivity_material import SensitivityReview
from skillflow.doe.sensitivity_report import build_view, report_chunks
from tests.doe.test_sensitivity_report import fixture


def measure(count):
    base, metadata = fixture()
    result = base.to_dict()
    sink = result["sinks"][0]
    template, = sink["data_reviews"]
    sink["data_reviews"] = [dict(template, id=f"candidate-{i}") for i in range(count)]
    sink["limitations"] = ["shared"]
    result["diagnostics"] = [{"id": "shared", "reason": "frozen evidence " * 1000}]
    review = SensitivityReview(result, base.index_dict())
    outputs = {}
    with TemporaryDirectory() as work:
        tracemalloc.start()
        start = perf_counter()
        view = build_view(review, metadata=metadata, compact=True)
        for name in ("report.html", "report.md"):
            path = Path(work) / name
            atomic_write_chunks(path, report_chunks(view, markdown=name.endswith(".md")))
            outputs[name] = path.stat().st_size
        elapsed = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return {"candidates": count, "output_bytes": outputs, "seconds": elapsed,
            "peak_python_allocated_bytes_during_publication": peak}


if __name__ == "__main__":
    rows = [measure(count) for count in (100, 1000, 5000)]
    print(json.dumps({"basis": "controlled offline publication only, same shared evidence and candidate shape",
                      "measurements": rows}, indent=2))
