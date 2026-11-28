"""Prepare the closed Semia recovery results for a scoped GitHub publication."""

import argparse
import hashlib
import json
from pathlib import Path
import re

from merge_semia_recovery import merge, report_files


COMPARISON = Path(__file__).resolve().parents[1]
REPOSITORY = COMPARISON.parents[2]
RECOVERY = COMPARISON / "runs/semia/semia-recovery-01"
REPORT = COMPARISON / "reports/audit-02"
BRANCH = "codex/semia-recovery-results"
REMOTE_URL = "https://github.com/southofborder/SkillFlow"
CREDENTIAL = re.compile(
    rb"-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{30,}|"
    rb"github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{28,})\b|"
    rb"\bBearer [A-Za-z0-9._-]{24,}", re.IGNORECASE
)
SCOPE = """# GitHub publication scope

This branch contains the matched three-arm report, the 94 recovery case results and their sealed run metadata. The original comparison summary and case rows establish which results were reused. Native prompts, responses and CLI logs are retained in the experiment workspace. The report's path and SHA-256 references identify that raw evidence.

The ClawHub archive files are available in the base Git tree. The cohort manifest records the packages and byte hashes. From the repository root, run `python -B experiments/baselines/comparison/inputs/prepare_clawhub_complex.py prepare` to materialize the exact source packages locally.

[Updated comparison](summary.md) · [Case rows](results.jsonl)
"""


def read(path):
    return json.loads(path.read_bytes())


def candidate_paths():
    state = read(RECOVERY / "summary.json")
    if state["status"] not in {"completed", "partial"} or not (REPORT / "summary.json").is_file():
        return None
    plan = read(RECOVERY / "manifest.json")
    report = read(REPORT / "summary.json")
    ids = [case["case_id"] for case in plan["cases"]]
    if (state["finished_cases"] != 94 or state["not_run"] != 0 or state["pending_case_ids"]
            or state["claimed_unclosed_case_ids"]
            or report["case_count"] != 100 or report["recovered_case_count"] != 94
            or report["retained_original_semia_case_count"] != 6
            or report["cohort_sha256"] != plan["cohort_sha256"]
            or len(ids) != 94 or len(set(ids)) != 94
            or any(not re.fullmatch(r"clawhub-\d{4}", case_id) for case_id in ids)):
        raise ValueError("Recovery and comparison report do not match the 94-case publication")
    paths = [COMPARISON / name for name in (
        "inputs/clawhub-complex.json", "inputs/prepare_clawhub_complex.py",
        "reports/audit-01/summary.json", "reports/audit-01/results.jsonl",
        "reports/audit-02/summary.md", "reports/audit-02/summary.json", "reports/audit-02/results.jsonl",
    )]
    paths.extend((RECOVERY / "manifest.json", RECOVERY / "summary.json"))
    paths.extend(RECOVERY / "cases" / case_id / "result.json" for case_id in ids)
    return paths


def verify_report(payload):
    base = COMPARISON / "reports/audit-01"
    cohort = COMPARISON / "inputs/clawhub-complex.json"
    for name, expected in report_files(*merge(base, RECOVERY, cohort)).items():
        path = (REPORT / name).relative_to(REPOSITORY).as_posix()
        if payload[path] != expected:
            raise ValueError(f"Archived report differs from its validated evidence: {path}")


def safe_payload(paths):
    payload = {}
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(COMPARISON):
            raise ValueError(f"Publication path escapes comparison: {path}")
        raw = path.read_bytes()
        if CREDENTIAL.search(raw) or b"\x00" in raw:
            raise ValueError(f"Publication needs review for unexpected content: {path}")
        payload[path.relative_to(REPOSITORY).as_posix()] = raw
    return payload


def save_once(path, raw):
    try:
        with path.open("xb") as handle:
            handle.write(raw)
    except FileExistsError:
        if path.read_bytes() != raw:
            raise ValueError(f"An existing publication file differs: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="freeze the verified publication file list")
    args = parser.parse_args()
    paths = candidate_paths()
    if paths is None:
        print(json.dumps({"status": "waiting_for_closed_recovery"}))
        return 1 if args.prepare else 0
    payload = safe_payload(paths)
    verify_report(payload)
    if not args.prepare:
        print(json.dumps({"status": "verified_result_scope", "files": len(paths) + 2, "branch": BRANCH}))
        return 0
    scope = REPORT / "publication.md"
    save_once(scope, SCOPE.encode("utf-8"))
    payload.update(safe_payload([scope]))
    manifest = {
        "repository": REMOTE_URL, "branch": BRANCH,
        "files": [{"path": path, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                   "git_blob_sha": hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()}
                  for path, raw in sorted(payload.items())],
    }
    save_once(REPORT / "publication-manifest.json", (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"status": "prepared", "files": len(payload) + 1, "branch": BRANCH}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
