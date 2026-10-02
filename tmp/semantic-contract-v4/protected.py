"""Bind protected inputs, historical outputs, production IR and Lean sources."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = HERE / "protected-before.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if sys.argv[1] == "capture":
    files = set()
    for directory in ("dataset", "result", "packages/skill-ir/src/skill_ir/ir",
                      "packages/skill-ir/src/skill_ir/extraction", "packages/skill-ir/formal",
                      "packages/skill-ir/experiments"):
        for path in (ROOT / directory).rglob("*"):
            if not path.is_file() or any(x in path.parts for x in ("__pycache__", ".lake", "tools")):
                continue
            relative = path.relative_to(ROOT)
            if "experiments" in relative.parts and path.name == "README.md" and "runs" not in relative.parts:
                continue
            files.add(relative.as_posix())
    BASE.write_text(json.dumps({p: digest(ROOT / p) for p in sorted(files)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Bound {len(files)} pre-existing protected files")
elif sys.argv[1] == "verify":
    before = json.loads(BASE.read_text(encoding="utf-8"))
    changes = [p for p, sha in before.items() if not (ROOT / p).is_file() or digest(ROOT / p) != sha]
    result = {"checked_files": len(before), "changed": changes, "status": "passed" if not changes else "failed"}
    (HERE / "protected-final.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(bool(changes))
