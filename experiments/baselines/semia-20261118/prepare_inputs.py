"""Materialize byte-identical, provenance-bound baseline inputs; never execute skills."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASES = {
    case: f"document-guided-{case}-input-necessity-high-20261111-173347"
    for case in ("001", "010", "013")
}
CASES["ga4"] = "document-guided-ga4-runtime-locality-high-20261117-205158"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Refusing to replace different bytes: {path}")
    else:
        with path.open("xb") as stream:
            stream.write(data)


def main() -> None:
    cases = []
    for case, run in CASES.items():
        parent = ROOT / "experiments/doe/runs" / run
        snapshot_path = parent / "source/inputs/snapshot.json"
        snapshot_bytes = snapshot_path.read_bytes()
        snapshot = json.loads(snapshot_bytes)
        package = parent / "source/inputs/package"
        expected = {item["path"] for item in snapshot["files"]}
        actual = {p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()}
        if actual != expected:
            raise ValueError(f"Incomplete parent package: {case}")
        files = []
        for item in snapshot["files"]:
            relative = PurePosixPath(item["path"])
            if relative.is_absolute() or ".." in relative.parts or ":" in str(relative):
                raise ValueError(f"Unsafe source path: {relative}")
            source = package / str(relative)
            if source.is_symlink() or not source.resolve().is_relative_to(package.resolve()):
                raise ValueError(f"Source escapes package: {source}")
            data = source.read_bytes()
            if sha(data) != item["raw_sha256"] or len(data) != item["size"]:
                raise ValueError(f"Parent source integrity mismatch: {source}")
            dest = HERE / "inputs" / case / str(relative)
            write_once(dest, data)
            files.append({"path": str(relative), "size": len(data), "sha256": sha(data)})
        destination_files = {
            p.relative_to(HERE / "inputs" / case).as_posix()
            for p in (HERE / "inputs" / case).rglob("*") if p.is_file()
        }
        if destination_files != expected:
            raise ValueError(f"Unexpected baseline input files: {case}")
        manifest_path = parent / "manifest.json"
        parent_manifest_bytes = manifest_path.read_bytes()
        cases.append({
            "case_id": case,
            "purpose": "engineering_pilot_not_representative_evaluation",
            "parent_run": parent.relative_to(ROOT).as_posix(),
            "parent_manifest_sha256": sha(parent_manifest_bytes),
            "parent_implementation_sha256": json.loads(parent_manifest_bytes)["implementation"]["sha256"],
            "parent_snapshot_sha256": sha(snapshot_bytes),
            "source_sha256": snapshot["source_sha256"],
            "package_bytes_sha256": snapshot["package_bytes_sha256"],
            "path": f"inputs/{case}", "files": files,
            "skill_executed": False,
            "labels": "unannotated_not_negative",
        })
    result = {
        "schema": "skillflow-semia-input-cohort-v1",
        "prepared_date": "2026-11-18",
        "timezone": "Asia/Shanghai",
        "selection": "existing_four_debug_cases_selected_before_semia_results",
        "comparison_status": "not_run",
        "historical_skillflow_outputs": "provenance_only_not_a_same_version_paired_baseline",
        "cases": cases,
    }
    write_once(HERE / "input-manifest.json", (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode())
    print(json.dumps({"cases": len(cases), "files": sum(len(c["files"]) for c in cases),
                      "status": "all_bytes_verified", "model_calls": 0, "skill_executions": 0}))


if __name__ == "__main__":
    main()
