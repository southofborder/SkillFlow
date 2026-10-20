"""Rebuild final score/report views without target or assessor model calls."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    run = Path(__file__).resolve().parent
    root = run.parents[3]
    errors: list[str] = []
    comparisons: dict[str, int] = {}
    for manifest, base in [
        ("final-cohort-freeze.json", run),
        ("assessment-protocol-freeze.json", root),
        ("tooling-snapshot-manifest.json", root),
    ]:
        data = json.loads((run / manifest).read_text(encoding="utf-8"))
        for relative, expected in data["files"].items():
            path = base / relative
            if not path.is_file() or digest(path) != expected:
                errors.append(f"Frozen file mismatch: {manifest}: {relative}")
        comparisons[manifest] = len(data["files"])
        if manifest == "tooling-snapshot-manifest.json":
            for relative, expected in data["files"].items():
                path = run / "tooling-snapshot" / relative
                if not path.is_file() or digest(path) != expected:
                    errors.append(f"Tooling snapshot mismatch: {relative}")
            comparisons["tooling_snapshot_copies"] = len(data["files"])

    protected = sorted({
        path
        for folder in ["assessments", "trials", "references", "cases", "prompts"]
        for path in (run / folder).rglob("*")
        if path.is_file()
    })
    protected_before = {str(p.relative_to(run)): digest(p) for p in protected}
    generated = [
        "assessment-summary.json", "assessment-report.md", "assessment-report.html",
        "results.json", "report.md", "index.html",
    ]
    before = {name: digest(run / name) for name in generated}
    commands = [
        [sys.executable, "-m", "tools.doe.direct_assessment", "aggregate", "--run-dir", str(run)],
        [sys.executable, "-m", "tools.doe.direct_assessment", "report", "--run-dir", str(run)],
        [sys.executable, "-m", "tools.doe.direct_results", "--run-dir", str(run), "--require-complete"],
    ]
    receipts = []
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8")
        receipts.append({"command": command, "exit_code": result.returncode,
                         "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            errors.append(f"Replay command failed: {command[3]}")
            break
    after = {name: digest(run / name) for name in generated}
    if before != after:
        errors.append("Generated report or score view changed during deterministic replay.")
    changed = [name for name, sha in protected_before.items() if digest(run / name) != sha]
    if changed:
        errors.append("Protected inputs, raw outputs, or individual grades changed during replay.")

    summary = json.loads((run / "assessment-summary.json").read_text(encoding="utf-8"))
    candidates = summary["candidates"]
    individual_scores = sum(len(c["reviewers"]) for c in candidates)
    if len(candidates) != 120 or individual_scores != 240:
        errors.append("Final assessment cohort is incomplete.")
    final = json.loads((run / "results.json").read_text(encoding="utf-8"))
    if not final["complete"] or final["planned_calls"] != 120 or final["imported_calls"] != 120:
        errors.append("Final results are incomplete.")
    record = {
        "schema_version": "direct-baseline-final-replay-v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if not errors else "failed",
        "model_calls": 0,
        "scope": "Deterministic score/report replay and preservation checks; not semantic revalidation or model generation replay.",
        "frozen_hash_comparisons": comparisons,
        "protected_files_unchanged": len(protected_before) - len(changed),
        "changed_protected_files": changed,
        "assessment_files": len(list((run / "assessments").glob("*.json"))),
        "paired_candidates": len(candidates), "individual_scores": individual_scores,
        "commands": receipts,
        "deterministic_generated_hashes": after,
        "protected_file_hashes": protected_before,
        "errors": errors,
    }
    (run / "final-replay.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ["status", "model_calls", "paired_candidates", "individual_scores", "frozen_hash_comparisons", "protected_files_unchanged", "errors"]}, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
