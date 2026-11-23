"""Seal the final scoped regression receipts and prepare an implementation binding."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from skillflow.common.recording import sha_file, implementation_provenance
from skillflow.document_guided.online import STEP_IDENTITY
from skillflow.document_guided.runner import IDENTITY, POLICY


def main(names, expected_implementation):
    folder = Path(__file__).resolve().parent
    records, suites, skipped = {}, {}, {}
    for name in names:
        path = folder / name
        suite = ET.parse(path).getroot()
        rows = list(suite.iter("testcase"))
        if not rows:
            raise ValueError(f"Empty JUnit suite: {name}")
        for row in rows:
            key = row.attrib["classname"], row.attrib["name"]
            records[key] = next((status for status in ("failure", "error", "skipped")
                                 if row.find(status) is not None), "passed")
            if records[key] == "skipped":
                skipped[key] = row.find("skipped").get("message")
            else:
                skipped.pop(key, None)
        suites[name] = {"tests": len(rows), "sha256": sha_file(path)}
    counts = Counter(records.values())
    if counts["error"] or counts["failure"]:
        raise ValueError(f"Scoped regressions still fail: {counts}")
    saved = json.loads((folder / "saved-material.json").read_text(encoding="utf-8-sig"))
    assert saved["status"] == "passed" and saved["source_files"] == 16 and saved["model_calls"] == 0
    metric = json.loads((folder / "report-publication.json").read_text(encoding="utf-8-sig"))
    assert metric["measurements"][-1]["candidates"] == 5000
    ingress = json.loads((folder / "ingress-identity-check.json").read_text(encoding="utf-8-sig"))["summary"]
    assert sorted(ingress["intrinsic_groups_by_field"].values()) == [50, 50] and ingress["access_groups"] == 0
    archived = json.loads((folder / "historical-v12-final.log").read_text(encoding="utf-8-sig"))
    assert (archived["manifest"], archived["demand"], archived["result"]) == (
        "skillflow-doe-run-v12", "skillflow-demand-v12", "skillflow-sensitivity-review-v10")
    assert archived["checks"] > 0 and archived["replays"] == archived["model_calls"] == 0
    implementation = implementation_provenance()["sha256"]
    if implementation != expected_implementation:
        raise ValueError("The implementation changed after the scoped regression suites started")
    portable = folder.parent / "portable-renderer-20261123/accepted-certificate.json"
    local = json.loads(portable.read_bytes())
    installed_path = portable.with_name("wheel-validation.json")
    installed = json.loads(installed_path.read_bytes())
    if (local["status"] != "passed" or local["implementation_sha256"] != implementation
            or local["graph_ir_count"] != 489 or not all(local["local_certificate"]["checks"].values())
            or local["local_certificate"]["binary_sha256"] != sha_file(Path(local["local_renderer"]))
            or local["python_sha256"] != sha_file(Path(sys.executable))):
        raise ValueError("The local renderer, Python runtime or donor certificate proof differs from the offline suite")
    proof = installed["second_cfg_verification"]
    if (installed["source_snapshot_sha256"] != implementation or proof["status"] != "verified"
            or not proof["tampered_text_rejected"] or not all(proof["checks"].values())
            or proof["external_pipeline_prepare"] != "ready" or installed["platform_artifacts_in_wheel"]):
        raise ValueError("The isolated wheel installation did not verify the accepted sources and native CFG proof")
    if json.loads(portable.with_name("source-delivery.json").read_bytes()) != saved:
        raise ValueError("Fresh delivery verification differs from the saved sixteen-file scope")
    data = {"status": "passed", "created_at": datetime.now(timezone.utc).isoformat(),
            "implementation_sha256": implementation, "guided_identity": IDENTITY,
            "step_identity": STEP_IDENTITY, "policy": POLICY,
            "latest_distinct_scoped_results": dict(counts), "suites": suites,
            "skips": {"::".join(key): reason for key, reason in skipped.items()},
            "previous_production_read": archived,
            "ingress_identity_sha256": sha_file(folder / "ingress-identity-check.json"),
            "limitation": "Offline scoped suites and named final rechecks, counted by latest test identity.",
            "portable_certificate_sha256": sha_file(portable),
            "wheel_validation_sha256": sha_file(installed_path),
            "saved_material_sha256": sha_file(folder / "saved-material.json"),
            "report_benchmark_sha256": sha_file(folder / "report-publication.json")}
    with (folder / "offline-acceptance.json").open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"status": "passed", "results": counts, "implementation": data["implementation_sha256"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-implementation", required=True)
    parser.add_argument("suites", nargs="+")
    args = parser.parse_args()
    main(args.suites, args.expected_implementation)
