"""Offline acceptance: actual Lean text round trips for 30 frozen graphs + 4 variants."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from skill_ir.backtrace.controlled import normalize_cfg, render_controlled, verify_controlled
from skill_ir.backtrace.fixtures import canonical_sha256, prepare_cases
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.ir.cfg import ControlFlowGraph


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "packages/skill-ir/formal/fixtures/review30.json"
DATASET = ROOT / "packages/skill-ir/experiments/semantics_baseline/dataset.json"
PROTECTED = ROOT / "tmp/semantic-feedback-20260915/protected-before.json"
OUTPUT = ROOT / "packages/skill-ir/experiments/semantic_feedback/runs/f01-feedback-20260915/verification/controlled-roundtrips.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_identity(directory, protected):
    rows = []
    expected_paths = {path for path in protected if path.startswith(directory.relative_to(ROOT).as_posix() + "/")}
    current_paths = {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}
    if current_paths != expected_paths:
        raise ValueError(f"Frozen Skill source inventory mismatch: {directory.relative_to(ROOT)}")
    for relative in sorted(current_paths):
        raw = (ROOT / relative).read_bytes()
        digest = sha(raw)
        if digest != protected[relative]:
            raise ValueError(f"Frozen Skill source bytes changed: {relative}")
        rows.append({"path": (ROOT / relative).relative_to(directory).as_posix(), "sha256": digest})
    return {
        "source_root": directory.relative_to(ROOT).as_posix(),
        "source_sha256": canonical_sha256(rows),
        "source_file_count": len(rows),
        "source_byte_sha256_bound_to_preimplementation_snapshot": True,
    }


def check_case(task):
    start = time.perf_counter()
    evidence = {key: value for key, value in task.items() if key != "cfg"}
    try:
        cfg = ControlFlowGraph.model_validate(task["cfg"])
        cfg.validate_integrity()
        document = render_controlled(cfg)
        certificate = verify_controlled(document, cfg)
        normalized_sha = canonical_sha256(normalize_cfg(cfg))
        assert certificate == document["certificate"]
        assert normalized_sha == document["graph_sha256"] == certificate["graph_sha256"]
        evidence.update({
            "status": "passed",
            "current_graph_sha256": normalized_sha,
            "text_sha256": sha(document["text"].encode("utf-8")),
            "certificate_sha256": canonical_sha256(certificate),
            "printer_source_sha256": certificate["source_sha256"],
            "printer_binary_sha256": certificate["binary_sha256"],
            "checks": certificate["checks"],
            "text_characters": len(document["text"]),
            "controlled_facts": len(document["units"]),
            "definition_links": len(document["derived_links"]),
        })
    except Exception as error:
        evidence.update({"status": "failed", "error": {"type": type(error).__name__, "message": str(error)}})
    evidence["elapsed_seconds"] = round(time.perf_counter() - start, 3)
    return evidence


def main():
    started = datetime.now(timezone.utc).isoformat()
    protected = read(PROTECTED)
    review = read(REVIEW)
    assert review["path_base"] == "repository"
    assert len(review["samples"]) == 30
    assert [item["index"] for item in review["samples"]] == list(range(1, 31))
    dataset = {case["id"]: (DATASET.parent / case["input"]).resolve() for case in read(DATASET)["cases"]}
    source_hashes = {identifier: source_identity(path, protected) for identifier, path in dataset.items()}
    tasks = []
    for item in review["samples"]:
        raw = (ROOT / item["analysis_path"]).read_bytes()
        if sha(raw) != item["analysis_sha256"]:
            raise ValueError(f"Review analysis hash mismatch: {item['sample_id']}")
        cfg = json.loads(raw)["cfg"]
        tasks.append({
            "identifier": item["sample_id"], "index": item["index"], "kind": "frozen_review30",
            "repetition": item["repetition"], "analysis_path": item["analysis_path"],
            "source_analysis_sha256": item["analysis_sha256"], "input_graph_sha256": canonical_sha256(cfg),
            **source_hashes[item["sample_id"]], "cfg": cfg,
        })
    prepared = prepare_cases()
    for case in prepared["cases"][1:]:
        tasks.append({
            "identifier": "F01-" + case["case_id"], "kind": "controlled_f01_variant",
            "analysis_path": prepared["provenance"]["analysis"]["path"],
            "source_analysis_sha256": prepared["provenance"]["analysis"]["sha256"],
            "input_graph_sha256": case["graph_sha256"],
            "fixture_manifest_sha256": prepared["provenance"]["fixture_manifest_sha256"],
            **source_hashes["F01"], "cfg": case["cfg"],
        })
    assert len(tasks) == 34
    results = {}
    with ProcessPoolExecutor(max_workers=4) as pool:
        future_ids = {pool.submit(check_case, task): task["identifier"] for task in tasks}
        for future in as_completed(future_ids):
            row = future.result()
            results[row["identifier"]] = row
            print(f"{len(results)}/34 {row['identifier']}: {row['status']}", flush=True)
    ordered = [results[task["identifier"]] for task in tasks]
    output = {
        "schema_version": 1,
        "identity": "semantic-feedback-offline-controlled-roundtrips-v1",
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "script_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "script_sha256": sha(Path(__file__).read_bytes()),
        "review_manifest_sha256": sha(REVIEW.read_bytes()),
        "protected_source_snapshot_sha256": sha(PROTECTED.read_bytes()),
        "status": "passed" if all(item["status"] == "passed" for item in ordered) else "failed",
        "counts": {"total": len(ordered), "passed": sum(item["status"] == "passed" for item in ordered),
                   "frozen_review30": 30, "f01_variants": 4, "api_calls": 0, "skill_execution_calls": 0},
        "method": "Each actual frozen CFG is structurally validated, rendered by Lean, parsed from the emitted text, fully reconstructed and field-compared; then verify_controlled independently reparses that same text against the CFG and exact certificate.",
        "boundaries": "Explicit normalized CFG facts only; no source-to-graph correctness, predicate feasibility, runtime-success or opaque-code interpretation claim.",
        "samples": ordered,
    }
    ArtifactWriter(()).json(OUTPUT, output)
    print(json.dumps({"status": output["status"], "counts": output["counts"], "output": str(OUTPUT)}, ensure_ascii=False), flush=True)
    return 0 if output["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
