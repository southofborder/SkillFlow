"""Verify current three inputs before changing supported contracts."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import shutil
import socket

from skill_ir.inputs.snapshot import read_snapshot
from skill_ir.security_profile.loading import load_annotation_run
from skill_ir.security_profile.runner import verify_prepared
from skill_ir.propagation.runner import load_propagation_run
from skill_ir.recording import canonical_sha256, implementation_provenance

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "packages/skill-ir"
OLD = PACKAGE / "experiments/propagation/runs/sink-boundaries-v1-20261002-185934"
stamp = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
OUT = PACKAGE / "experiments/propagation/runs" / ("sink-tightening-v1-" + stamp)
OUT.mkdir(parents=True, exist_ok=False)
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(AssertionError("bootstrap must be offline"))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

protected = {}
targets = [ROOT / "dataset", ROOT / "result", PACKAGE / "src/skill_ir/ir", PACKAGE / "src/skill_ir/data", PACKAGE / "formal"]
targets += list((PACKAGE / "experiments").glob("*/runs"))
for target in targets:
    for path in target.rglob("*"):
        if path.is_file() and not path.is_relative_to(OUT) and not set(path.parts) & {".lake", "__pycache__"}:
            protected[path.relative_to(ROOT).as_posix()] = digest(path)
cases = []
for number, sample in (("001", "N01"), ("010", "Q04"), ("013", "F01")):
    prior = OLD / "cases" / number
    annotation_dir = prior / "annotation"
    prepared = verify_prepared(annotation_dir, replay=True)
    _, source, metadata = read_snapshot(annotation_dir)
    cfg = json.loads((prior / "selected-analysis.json").read_text(encoding="utf-8"))["cfg"]
    result = json.loads((annotation_dir / "result.json").read_text(encoding="utf-8"))
    assert prepared["preparation_status"] == "ready"
    assert prepared["graph_sha256"] == canonical_sha256(cfg)
    assert prepared["source_sha256"] == source["source_sha256"]
    prior_doe = prior / "propagation/doe-input.json"
    if number != "013":
        loaded = load_annotation_run(annotation_dir)
        doe = load_propagation_run(prior / "propagation")
        assert result["status"] == "complete" and doe["cfg"] == cfg
        assert doe["source"]["source_sha256"] == source["source_sha256"]
        assert loaded["material"]["cfg"] == cfg
    else:
        assert result["status"] == "invalid_response" and result["error_kind"] == "json_format"
        assert not prior_doe.exists()
    frozen = OUT / "frozen" / number
    frozen.mkdir(parents=True)
    shutil.copytree(annotation_dir / "inputs/package", frozen / "package")
    shutil.copy2(annotation_dir / "inputs/material.json", frozen / "material.json")
    (frozen / "source-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(prior / "selected-analysis.json", frozen / "analysis.json")
    cases.append({"case_id": number, "sample_id": sample, "prior_run": str(prior),
                  "prior_status": result["status"], "prior_result_sha256": digest(annotation_dir / "result.json"),
                  "prior_doe_sha256": digest(prior_doe) if prior_doe.exists() else None,
                  "graph_sha256": canonical_sha256(cfg), "source_sha256": source["source_sha256"],
                  "frozen_files": {p.relative_to(frozen).as_posix(): digest(p) for p in sorted(frozen.rglob("*")) if p.is_file()}})
receipt = {"status": "verified", "old_implementation": implementation_provenance(), "cases": cases, "model_calls": 0}
(OUT / "bootstrap.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
work = ROOT / "tmp/sink-tightening"
(work / "protected-before.json").write_text(json.dumps(protected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(work / "run-path.txt").write_text(str(OUT), encoding="utf-8")
print(json.dumps({"status": "verified", "run_dir": str(OUT), "protected_files": len(protected), "cases": [c["case_id"] for c in cases]}, ensure_ascii=False))
