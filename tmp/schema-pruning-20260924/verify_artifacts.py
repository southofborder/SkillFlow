from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
before = json.loads((root / "tmp/schema-pruning-20260924/protected-before.json").read_text(encoding="utf-8"))
missing, changed = [], []
for relative, expected in before.items():
    path = root / relative
    if not path.is_file():
        missing.append(relative)
    elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        changed.append(relative)
output = root / "packages/skill-ir/experiments/propagation/runs/schema-pruning-v1-20260924"
output.mkdir(parents=True, exist_ok=True)
check = {"checked_files": len(before), "changed": changed, "missing": missing}
(output / "protected-check.json").write_text(json.dumps(check, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if changed or missing:
    raise SystemExit(json.dumps(check, ensure_ascii=False))
demo = subprocess.run([sys.executable, "-X", "utf8", str(root / "packages/skill-ir/examples/data_model_demo.py")],
                      check=True, capture_output=True, encoding="utf-8", cwd=root)
data = json.loads(demo.stdout)
(output / "data-demo.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
propagation = json.loads((output / "offline-demo/result.json").read_text(encoding="utf-8"))
manifest = json.loads((output / "offline-demo/manifest.json").read_text(encoding="utf-8"))
annotation = json.loads((output / "offline-demo/inputs/annotation.json").read_text(encoding="utf-8"))
audit = json.loads((output / "offline-demo/audit/location-evidences.json").read_text(encoding="utf-8"))
assert set(annotation) == {"profiles", "locations", "transfer_specs", "unresolved"}
assert set(audit) == set(annotation["locations"])
assert all(set(location) == {"kind", "name", "operand_refs"} for location in annotation["locations"].values())
assert "evidence_refs" not in json.dumps(propagation["registry"])
assert all(not record["data"]["annotations"]["evidences"] for record in propagation["registry"]["records"])
assert all(not record["data"]["annotations"]["sensitivity"] for record in propagation["registry"]["records"])
actual = hashlib.sha256(json.dumps(audit, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
assert actual == manifest["location_evidences_sha256"]
print(json.dumps({"protected": check, "data_version": data["schema_version"],
                  "data_records": len(data["records"]), "propagation_status": propagation["status"],
                  "ir_records": len(propagation["records"]["records"]), "locations": len(audit),
                  "model_calls": propagation["model_calls"]}, ensure_ascii=False))
