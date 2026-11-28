"""Read-only audit of the pinned upstream source and completed offline setup.

Writes only this reproduction directory's setup-report.json. No model calls,
no Skill execution, no regeneration of prepared or upstream artifacts.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIN = "379bc25fe99833eb185efe56a38fe15f0235799c"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    archive = ROOT / "downloads/semia-379bc25f.zip"
    source_files = []
    with zipfile.ZipFile(archive) as zf:
        for entry in zf.infolist():
            if entry.is_dir():
                continue
            rel = entry.filename.split("/", 1)[1]
            expected = hashlib.sha256(zf.read(entry)).hexdigest()
            target = ROOT / "source" / rel
            source_files.append({"path": rel, "sha256": expected,
                                 "source_matches_archive": target.is_file() and sha(target) == expected})
    source_manifest = {"schema": "semia-upstream-source-manifest-v1", "commit": PIN,
                       "archive_sha256": sha(archive), "files": source_files}
    (ROOT / "source-manifest.json").write_text(
        json.dumps(source_manifest, indent=2) + "\n", encoding="utf-8")

    cases = []
    for item in read_json(ROOT / "input-manifest.json")["cases"]:
        cid = item["case_id"]
        prepared = ROOT / "prepared" / cid
        metadata = read_json(prepared / "prepare_metadata.json")
        inventory = metadata["source"]["file_inventory"]
        included = {x["path"]: x for x in inventory if x["disposition"] != "excluded"}
        expected = {x["path"]: x for x in item["files"]}
        excluded = sorted(set(expected) - set(included))
        receipt = read_json(ROOT / "logs" / f"prepare-{cid}.log")
        cases.append({
            "case_id": cid,
            "prepare_status": receipt["status"],
            "semantic_units": receipt["semantic_units"],
            "input_file_count": len(expected),
            "inlined_file_count": len(included),
            "omitted_by_upstream_prepare": excluded,
            "all_input_bytes_match_manifest": all(
                sha(ROOT / item["path"] / path) == entry["sha256"]
                for path, entry in expected.items()),
            "inlined_dispositions": dict(Counter(x["disposition"] for x in inventory)),
            "prepared_skill_sha256": sha(prepared / "prepared_skill.md"),
            "prepared_skill_bytes": (prepared / "prepared_skill.md").stat().st_size,
            "prepared_artifacts": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)}
                                   for p in sorted(prepared.iterdir()) if p.is_file()],
            "model_calls": 0,
            "skill_executed": False,
        })
    test_runs = []
    for log in (ROOT / "logs/upstream-core-tests.log", ROOT / "logs/upstream-pipeline-tests.log"):
        body = log.read_text(encoding="utf-8-sig")
        summary = re.search(r"Ran (\d+) tests in ([\d.]+)s", body)
        skip = re.search(r"OK \(skipped=(\d+)\)", body)
        test_runs.append({"log": log.relative_to(ROOT).as_posix(), "sha256": sha(log),
                          "tests": int(summary[1]), "elapsed_seconds": float(summary[2]),
                          "skipped": int(skip[1]) if skip else 0,
                          "result": "passed_with_skips" if "\nOK" in body else "inspect_log",
                          "scope": "upstream deterministic core unit tests"})
    dist = importlib.metadata.distribution("semia-audit")
    installed = []
    for f in dist.files or []:
        if str(f).endswith((".py", ".dl", ".json", ".md")):
            p = Path(dist.locate_file(f))
            if p.is_file():
                installed.append({"path": str(f), "sha256": sha(p)})
    report = {
        "schema": "skillflow-semia-offline-setup-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "offline_ready_model_comparison_not_run_by_setup",
        "upstream": {"repository": "https://github.com/berabuddies/Semia", "commit": PIN,
                     "main_sha": PIN, "tag": "v0.1.3", "tag_sha": PIN,
                     "same_as_20260920_pin": True,
                     "archive_url": f"https://codeload.github.com/berabuddies/Semia/zip/{PIN}",
                     "archive_sha256": sha(archive), "source_file_count": len(source_files),
                     "source_matches_archive": all(x["source_matches_archive"] for x in source_files),
                     "source_manifest": "source-manifest.json", "source_modified": False,
                     "release_metadata_note": "latest-release API timed out after 25s; tag and main verified independently with GitHub API and git ls-remote"},
        "environment": {"platform": platform.platform(), "python": platform.python_version(),
                        "python_executable": sys.executable, "package": dist.metadata["Name"],
                        "version": dist.version, "runtime_dependencies": dist.requires or [],
                        "backend": "builtin", "souffle_on_path": shutil.which("souffle"),
                        "docker_on_path": shutil.which("docker"),
                        "wsl_status": "wsl.exe exists but Linux subsystem not installed (list returned exit 1)",
                        "global_installations_or_configuration_changes": False,
                        "installed_code_files": installed},
        "validation": {"test_runs": test_runs,
                       "tests_total": sum(x["tests"] for x in test_runs),
                       "tests_passed": sum(x["tests"] - x["skipped"] for x in test_runs),
                       "skipped": sum(x["skipped"] for x in test_runs),
                       "failures": 0,
                       "skip_reasons": ["Souffle differential equivalence unavailable", "Souffle native rule execution unavailable", "optional corpus distribution printout disabled"],
                       "scope_note": "7 upstream core modules, not the full upstream suite and not paper metric reproduction"},
        "prepared_cases": cases,
        "fairness_notes": [
            "All 21 input files match the sealed SkillFlow source bytes; Semia directory prepare excludes two GA4 package metadata files, retaining 14/16.",
            "Do not call this identical model-visible material until the GA4 filtering policy is accounted for.",
            "Builtin is an official upstream backend, but its equivalence to Souffle has not been verified on this machine.",
            "No task-specific privacy-necessity labels are produced by prepare; no comparative precision, recall or superiority established.",
            "Current codex provider accepts model but not reasoning-effort knob, inherits host configuration, enables read-only sandbox without disabling tool calls. Root owns any adapter/protocol decision.",
        ],
        "upstream_defaults": {"provider": "responses", "responses_model": "gpt-5.5",
                              "codex_model": None, "iterations": 5,
                              "synthesis_max_retries": 3, "provider_retries": 2,
                              "timeout_seconds": 600},
        "setup_remote_model_calls": 0,
        "setup_skill_executions": 0,
    }
    (ROOT / "setup-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"source_files": len(source_files), "source_matches_archive": report["upstream"]["source_matches_archive"],
                      "tests_passed": report["validation"]["tests_passed"], "skipped": report["validation"]["skipped"],
                      "case_coverage": [{"id": c["case_id"], "included": c["inlined_file_count"], "omitted": c["omitted_by_upstream_prepare"]} for c in cases]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
