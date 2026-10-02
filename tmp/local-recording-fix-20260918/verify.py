"""Collect local-only regression and immutable-input evidence for this fix."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = read(ROOT / "packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v4-seven-20260918/manifest.json")
allowed = {
    "packages/skill-ir/experiments/semantics_baseline/tools/stream_transport.py",
    "packages/skill-ir/src/skill_ir/audit_execution.py",
    "packages/skill-ir/src/skill_ir/experiments/report.py",
    "packages/skill-ir/src/skill_ir/llm/client.py",
    "packages/skill-ir/src/skill_ir/recording.py",
}
changed = [name for name, digest in old["implementation"]["files"].items()
           if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
assert set(changed) == allowed, changed
protected = read(ROOT / "tmp/semantic-contract-v4/protected-before.json")
protected.update(read(HERE / "history-before.json"))
mutated = [name for name, digest in protected.items()
           if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
assert not mutated, mutated
suites = {}
for label, filename in (("full_suite", "pytest.xml"), ("final_recording_guard", "guard-pytest.xml")):
    suite = ET.parse(HERE / filename).getroot().find("testsuite")
    values = {key: int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    assert values["failures"] == values["errors"] == values["skipped"] == 0, values
    suites[label] = {**values, "seconds": float(suite.attrib["time"]), "xml": filename}
new = ["packages/skill-ir/src/skill_ir/artifact_io.py", "packages/skill-ir/src/skill_ir/recording_errors.py"]
result = {
    "scope": "Local artifact persistence and error propagation; zero remote API calls.",
    "tests": suites,
    "test_order": "Full suite completed before the final retry-decision persistence guard; relevant tests rerun after that guard, including new tests.",
    "changed_implementation_files": changed,
    "new_implementation_files": new,
    "final_file_sha256": {name: sha(ROOT / name) for name in sorted(allowed | set(new))},
    "protected_files_checked": len(protected), "protected_files_changed": mutated,
    "network_calls": 0,
    "boundaries": [
        "No production prompt, IR fields, structural rules, semantic audit protocol or Lean changes.",
        "No historical response recovery or semantic reclassification performed.",
        "Native Windows sharing test and simulated failures are offline; no live-model performance claim.",
        "A retained temporary snapshot is not automatically a verified complete model response.",
    ],
}
(HERE / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
