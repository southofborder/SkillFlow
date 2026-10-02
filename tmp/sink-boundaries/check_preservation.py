"""Verify this task's frozen inputs and historical artifacts without rewriting them."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[2]
directory = Path((root / "tmp/sink-boundaries/run-path.txt").read_text(encoding="utf-8"))
before = json.loads((root / "tmp/sink-boundaries/protected-before.json").read_text(encoding="utf-8"))
receipt = json.loads((directory / "bootstrap.json").read_text(encoding="utf-8"))
unchanged_packages = ("ir/", "data/", "extraction/", "backtrace/", "feedback/", "llm/")
before_source = {name: digest for name, digest in receipt["old_implementation"]["files"].items()
                 if name.startswith("packages/skill-ir/src/skill_ir/")
                 and name.removeprefix("packages/skill-ir/src/skill_ir/").startswith(unchanged_packages)}
check = {**before, **before_source}
differences = []
for name, digest in check.items():
    path = root / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        differences.append(name)
result = {"status": "matched" if not differences else "mismatch",
          "protected_files": len(before), "additional_source_checks": len(before_source),
          "differences": differences}
(directory / "preservation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(bool(differences))
