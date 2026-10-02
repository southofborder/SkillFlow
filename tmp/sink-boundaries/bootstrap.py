"""Validate old baseline inputs before changing supported contracts."""
import hashlib
import json
import shutil
import socket
from datetime import datetime, timezone, timedelta
from pathlib import Path

from skill_ir.propagation.runner import load_propagation_run
from skill_ir.recording import canonical_sha256, implementation_provenance

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "packages/skill-ir"
OLD = PACKAGE / "experiments/annotation_review/runs/repair-once-v1-20260929-132248"
stamp = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
OUT = PACKAGE / "experiments/propagation/runs" / ("sink-boundaries-v1-" + stamp)
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
prompt = PACKAGE / "src/skill_ir/prompts.py"
if prompt.exists():
    protected[prompt.relative_to(ROOT).as_posix()] = digest(prompt)
cases = []
for number, sample in (("001", "N01"), ("010", "Q04"), ("013", "F01")):
    prior = OLD / "cases" / (number + "-base")
    doe = load_propagation_run(prior / "propagation")
    assert doe["status"] == "complete" and not doe["diagnostics"]
    cfg_review = json.loads((OLD / "cfg-reviews" / number / "result.json").read_text(encoding="utf-8"))
    refinement = json.loads((prior / "refinement/result.json").read_text(encoding="utf-8"))
    assert cfg_review["status"] == "audit_passed" and cfg_review["passed_cfg"] == doe["cfg"]
    assert refinement["status"] == "review_passed"
    frozen = OUT / "frozen" / number
    frozen.mkdir(parents=True)
    source_package = prior / "refinement/inputs/package"
    shutil.copytree(source_package, frozen / "package")
    for name in ("material.json", "source-metadata.json"):
        shutil.copy2(prior / "propagation/audit" / name, frozen / name)
    (frozen / "analysis.json").write_text(json.dumps({"cfg": doe["cfg"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cases.append({"case_id": number, "sample_id": sample, "prior_run": str(prior),
                  "prior_doe_sha256": digest(prior / "propagation/doe-input.json"),
                  "graph_sha256": canonical_sha256(doe["cfg"]), "source_sha256": doe["source"]["source_sha256"],
                  "frozen_files": {p.relative_to(frozen).as_posix(): digest(p) for p in sorted(frozen.rglob("*")) if p.is_file()}})
receipt = {"status": "verified", "old_implementation": implementation_provenance(), "cases": cases, "model_calls": 0}
(OUT / "bootstrap.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "tmp/sink-boundaries/protected-before.json").write_text(json.dumps(protected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "tmp/sink-boundaries/run-path.txt").write_text(str(OUT), encoding="utf-8")
print(json.dumps({"status": "verified", "run_dir": str(OUT), "protected_files": len(protected), "cases": [c["case_id"] for c in cases]}, ensure_ascii=False))
