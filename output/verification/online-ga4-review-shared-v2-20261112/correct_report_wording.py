"""Correct a causal overstatement, preserving the prior report and seal."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

base = Path(__file__).resolve().parent
archive = base / "report-revisions/causal-wording-before"
archive.mkdir(parents=True, exist_ok=False)
names = ("final-cost-provenance.en.md", "cost-provenance-audit/final-cost-summary.json", "run-summary.json", "delivery-seal.json")
for name in names:
    target = archive / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((base / name).read_bytes())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

report = base / names[0]
old = "The delivery-size fix therefore allowed both complete review requests to be sent. It did not prevent the separate structural response failure after correction."
new = "Both complete requests were sent within the unchanged cap using shared-v2. This fresh material also fits compact-v1, so admission alone is not evidence that the old presentation would reject it. The separate same-material historical regression demonstrates the original overflow fix. Complete delivery did not prevent the structural response failure after correction."
content = report.read_text(encoding="utf-8")
assert content.count(old) == 1
report.write_text(content.replace(old, new), encoding="utf-8")
cost = read(base / names[1])
cost["report_sha256"] = sha(report)
save(base / names[1], cost)
summary = read(base / names[2])
summary["cost"] = cost
save(base / names[2], summary)
seal = read(base / names[3])
seal["sealed_at"] = datetime.now(timezone.utc).isoformat()
seal["previous_seal"] = {"path": "report-revisions/causal-wording-before/delivery-seal.json", "sha256": sha(archive / "delivery-seal.json")}
seal["revision_reason"] = "Clarify that fresh compact-v1 material also fits; no numeric result, raw run artifact or production change. Prior report and seals are preserved."
for name in (names[0], names[1], names[2]):
    seal["reports"][name] = sha(base / name)
save(base / names[3], seal)
for name, digest in seal["reports"].items():
    assert sha(base / name) == digest, name
print(json.dumps({"status": "wording_corrected_and_resealed", "numeric_results_changed": False, "raw_run_artifacts_changed": False, "report_sha256": sha(report)}))
