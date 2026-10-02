"""Read-only concrete Lean printer/parser preflight for the old 30 fixed graphs."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/skill-ir/src"))
from skill_ir.backtrace.controlled import _executable, render_controlled, verify_controlled
from skill_ir.artifacts.analysis_json import load_analysis_cfg
from skill_ir.recording import sha_file

driver_path = ROOT / "packages/skill-ir/experiments/security_profile/tools/run_review_set.py"
spec = importlib.util.spec_from_file_location("preflight_source_selector", driver_path)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
started = perf_counter()
rows = []
for item in driver.build_plan():
    before = sha_file(Path(item["analysis_path"]))
    row = {"case_id": f"{item['index']:03}", "sample_id": item["sample_id"],
           "analysis_sha256": before, "repetition": item["repetition"]}
    try:
        graph = load_analysis_cfg(item["analysis_path"])
        graph.validate_integrity()
        document = render_controlled(graph)
        certificate = verify_controlled(document, cfg=graph)
        assert sha_file(Path(item["analysis_path"])) == before
        row.update(status="verified", certificate=certificate, units=len(document["units"]),
                   text_bytes=len(document["text"].encode("utf-8")))
    except Exception as error:
        row.update(status="error", error=f"{type(error).__name__}: {error}")
    rows.append(row)
    print(row["case_id"], row["sample_id"], row["status"], flush=True)
result = {"purpose": "Offline tool preflight only; old graphs are not the new extraction inputs.",
          "renderer": str(_executable(None)), "renderer_sha256": sha_file(_executable(None)),
          "cases": rows, "verified": sum(row["status"] == "verified" for row in rows),
          "seconds": round(perf_counter() - started, 3), "api_calls": 0}
Path(__file__).with_name("lean-preflight.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in result.items() if key != "cases"}, ensure_ascii=False))
raise SystemExit(0 if result["verified"] == 30 else 1)
