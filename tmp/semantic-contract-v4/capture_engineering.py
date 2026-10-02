"""Collect engineering evidence without changing model inputs or responses."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

from skill_ir.backtrace.runner import verify_run

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / "packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v4-seven-20260918"
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
manifest = verify_run(RUN, live=True)
suite = ET.parse(HERE / "pytest.xml").getroot().find("testsuite")
assert suite is not None
tests = {key: int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
assert tests["tests"] == 1264 and tests["failures"] == tests["errors"] == tests["skipped"] == 0
build = (HERE / "lean-build.log").read_text(encoding="utf-8-sig")
audit = (HERE / "lean-proof-audit.log").read_text(encoding="utf-8-sig")
assert "Build completed successfully" in build
assert "sorryAx" not in audit and "error:" not in audit
assert all(token.strip() in {"propext", "Classical.choice", "Quot.sound"}
           for line in audit.splitlines() if "depends on axioms:" in line
           for token in line.split("[", 1)[1].split("]", 1)[0].split(",") if token.strip())
before = read(HERE / "protected-before.json")
changed = [name for name, sha in before.items()
           if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha]
assert not changed
review30 = read(RUN / "verification/review30.json")
material = read(HERE / "material-comparison.json")
assert all(row["same_cfg"] and row["same_source"] and row["payload_text_matches_certified"] for row in material.values())
record = {
    "schema_version": 1, "run_id": RUN.name,
    "tests": {**tests, "passed": tests["tests"], "seconds": float(suite.attrib["time"]),
              "command": "python -X utf8 -m pytest packages/skill-ir/tests -q --junitxml=tmp/semantic-contract-v4/pytest.xml",
              "log": "tmp/semantic-contract-v4/pytest.log", "xml": "tmp/semantic-contract-v4/pytest.xml"},
    "lean": {"build": "passed", "audit": "passed", "build_jobs": 18,
             "allowed_base_axioms": ["propext", "Classical.choice", "Quot.sound"],
             "build_log": "tmp/semantic-contract-v4/lean-build.log", "audit_log": "tmp/semantic-contract-v4/lean-proof-audit.log"},
    "conversion": {"review30": {"passed": sum(s["status"] == "passed" for s in review30["samples"]),
                                "total": len(review30["samples"])},
                   "seven_cases": {c["case_id"]: c["fidelity_status"] for c in manifest["cases"]},
                   "note": "F01 original overlaps review30; four mutants are additional, 001/010 use the pinned paused-round graphs."},
    "protected": {"preexisting_files_checked": len(before), "changed": changed,
                  "manifest": "tmp/semantic-contract-v4/protected-before.json"},
    "material_comparison_with_v3": material,
    "boundaries": ["No IR schema or production extraction changes.", "No CFG regeneration, annotation or propagation run.",
                   "Checks and Lean roundtrips do not prove semantic judgments or source-to-CFG equivalence."]}
(RUN / "engineering.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed_tests": tests["tests"], "protected_files": len(before), "lean": "passed", "conversion": record["conversion"]}, ensure_ascii=False))
