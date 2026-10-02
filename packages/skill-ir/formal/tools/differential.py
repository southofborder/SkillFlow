"""Replayable differential acceptance checks between Python and the Lean core.

Usage from repository root (after building formal/ with the pinned toolchain):
  python packages/skill-ir/formal/tools/differential.py --checker CHECKER.exe

No external network or Skill execution occurs. A missing/broken checker is an
error, never an implicit pass. --prepare-only explicitly records no Lean run.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Callable

from bridge import PACKAGE, PROTOCOL_VERSION, json_bytes, json_hash, project_raw, python_accept
from cases import Case, fixtures, metamorphic_cases, mutation_cases, random_cases, recorded_cases, topology_cases

ROOT = PACKAGE.parents[1]


def write_json(path: Path, value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    # A rerun rechecks every case, but rewriting thousands of identical evidence
    # files adds substantial Windows filesystem/antivirus overhead.
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checker_results(checker: Path, projections: list[dict], timeout: float = 60) -> list[dict]:
    if not projections:
        return []
    request = b"\n".join(json_bytes(item) for item in projections) + b"\n"
    process = subprocess.run([str(checker.resolve())], input=request, capture_output=True,
                             timeout=timeout, check=False)
    if process.returncode:
        raise RuntimeError(f"Lean checker exited {process.returncode}: {process.stderr.decode('utf-8', errors='replace')[:2000]}")
    lines = [line for line in process.stdout.decode("utf-8").splitlines() if line.strip()]
    if len(lines) != len(projections):
        raise RuntimeError(f"Lean checker returned {len(lines)} responses for {len(projections)} requests")
    results = []
    for line in lines:
        value = json.loads(line)
        if not isinstance(value, dict) or (type(value.get("accept")) is not bool and not isinstance(value.get("error"), str)):
            raise RuntimeError(f"invalid Lean checker response: {line[:500]}")
        results.append(value)
    return results


def deletion_candidates(cfg: dict) -> Any:
    """Deterministic reduction order; never repairs the candidate after deletion."""
    for i in range(len(cfg.get("edges", []))):
        value = deepcopy(cfg)
        value["edges"].pop(i)
        yield value
    for key in cfg.get("blocks", {}):
        value = deepcopy(cfg)
        del value["blocks"][key]
        yield value
    for key, block in cfg.get("blocks", {}).items():
        for i in range(len(block.get("instructions", []))):
            value = deepcopy(cfg)
            value["blocks"][key]["instructions"].pop(i)
            yield value


def minimize(cfg: dict, preserves: Callable[[dict], bool], max_checks: int = 120) -> tuple[dict, dict]:
    """Greedy deletion reduction, reporting bounds rather than claiming minimality."""
    current, checks, reductions = deepcopy(cfg), 0, 0
    while checks < max_checks:
        changed = False
        for candidate in deletion_candidates(current):
            if checks >= max_checks:
                break
            checks += 1
            if preserves(candidate):
                current, changed, reductions = candidate, True, reductions + 1
                break
        if not changed:
            return current, {"checks": checks, "reductions": reductions,
                             "deletion_minimal": checks < max_checks, "budget_exhausted": checks >= max_checks}
    return current, {"checks": checks, "reductions": reductions,
                     "deletion_minimal": False, "budget_exhausted": True}


def source_versions(checker: Path | None, command: list[str], manifests: list[Path] | None = None) -> dict:
    source_paths = sorted((PACKAGE / "src" / "skill_ir" / "ir").glob("*.py"))
    source_paths += sorted((PACKAGE / "formal" / "tools").glob("*.py"))
    source_paths += sorted((PACKAGE / "formal").rglob("*.lean"))
    # Build products may contain extracted/generated Lean files; source attestation
    # is scoped to the checked-in formal tree rather than the compiler cache.
    source_paths = [p for p in source_paths if ".lake" not in p.parts]
    source_paths += [PACKAGE / "formal" / "lakefile.toml", PACKAGE / "formal" / "lean-toolchain"]
    source_paths += sorted((PACKAGE / "formal" / "fixtures").glob("*.json"))
    hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): file_hash(p) for p in source_paths}
    toolchain = PACKAGE / "formal" / "lean-toolchain"
    return {"protocol": PROTOCOL_VERSION, "python": sys.version, "platform": platform.platform(),
            "pydantic": importlib.metadata.version("pydantic"),
            "pydantic_core": importlib.metadata.version("pydantic-core"),
            "lean_toolchain": toolchain.read_text(encoding="utf-8").strip() if toolchain.exists() else None,
            "checker_path": str(checker.resolve()) if checker else None,
            "checker_sha256": file_hash(checker) if checker else None,
            "input_manifests": [{"path": str(path.resolve()), "sha256": file_hash(path)} for path in manifests or []],
            "command_argv": command, "cwd": str(Path.cwd()),
            "source_sha256": hashes, "source_bundle_sha256": json_hash(hashes)}


def collect_cases(manifest: Path | None, seed: int, random_count: int, max_blocks: int) -> list[Case]:
    base = fixtures()
    if manifest:
        base += recorded_cases(manifest)
    return (base + list(topology_cases(max_blocks)) + list(random_cases(seed, random_count))
            + list(metamorphic_cases(base)) + list(mutation_cases(base)))


def run(cases: list[Case], output: Path, checker: Path | None,
        command: list[str] | None = None, shrink_budget: int = 120) -> dict:
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if len({case.name for case in cases}) != len(cases):
        raise ValueError("case names must be unique")
    if checker is not None and not checker.is_file():
        raise FileNotFoundError(f"Lean checker does not exist: {checker}")
    manifests = sorted({Path(case.provenance["manifest_path"]) for case in cases if "manifest_path" in case.provenance})
    versions = source_versions(checker, command or [sys.executable, *sys.argv], manifests)
    records, pending, projections = [], [], []
    for index, case in enumerate(cases):
        original_path = output / "cases" / f"{case.name}.json"
        write_json(original_path, asdict(case))
        accepted, error = python_accept(case.cfg)
        record = {"name": case.name, "family": case.family, "input_sha256": json_hash(case.cfg),
                  "input_file": str(original_path), "input_file_sha256": file_hash(original_path),
                  "provenance": case.provenance, "expected_accept": case.expected,
                  "expected_domain": case.expected_domain,
                  "python_accept": accepted, "python_error": error,
                  "lean_evaluated": False, "lean_accept": None, "lean_error": None}
        try:
            projection = project_raw(case.cfg)
        except (ValueError, TypeError) as exc:
            record.update(domain="schema-rejected", schema_error=str(exc), comparison="not-in-core-domain")
        else:
            projection_path = output / "projections" / f"{case.name}.json"
            write_json(projection_path, projection)
            record.update(domain="core", projection_sha256=json_hash(projection),
                          projection_file=str(projection_path), projection_file_sha256=file_hash(projection_path),
                          comparison="not-run")
            projections.append(projection)
            pending.append(index)
        record["expectation_ok"] = (case.expected is None or case.expected == accepted) and ((record["domain"] == "schema-rejected") == (case.expected_domain == "schema"))
        records.append(record)
    if checker:
        # Bounded chunks preserve request/response ordering and avoid platform
        # command-line size limits (all inputs go through stdin, never argv).
        for start in range(0, len(projections), 200):
            results = checker_results(checker, projections[start:start + 200])
            for index, result in zip(pending[start:start + 200], results):
                record = records[index]
                record["lean_evaluated"] = True
                if "error" in result:
                    record.update(lean_error=result["error"], comparison="checker-error")
                else:
                    record["lean_accept"] = result["accept"]
                    record["comparison"] = "agree" if result["accept"] == record["python_accept"] else "disagree"
        for index, record in enumerate(records):
            if record["comparison"] != "disagree":
                continue
            case = cases[index]
            direction = record["python_accept"], record["lean_accept"]

            def preserves(candidate: dict) -> bool:
                try:
                    core = project_raw(candidate)
                except (ValueError, TypeError):
                    return False
                python_result, _ = python_accept(candidate)
                if python_result != direction[0]:
                    return False
                result = checker_results(checker, [core])[0]
                return result.get("accept") is direction[1] and "error" not in result

            minimized, reduction = minimize(case.cfg, preserves, shrink_budget)
            counterexample = output / "counterexamples" / f"{case.name}.json"
            replay_command = [sys.executable, str(Path(__file__).resolve()), "--checker", str(checker.resolve()), "--replay", str(counterexample), "--output", str(output / "replay")]
            write_json(counterexample, {"name": case.name + "-reduced", "family": "counterexample",
                                       "cfg": minimized, "expected": None, "expected_domain": "core",
                                       "provenance": {"original_case": record["input_file"], "original_input_sha256": record["input_sha256"],
                                                      "original_projection_sha256": record["projection_sha256"],
                                                      "reduced_input_sha256": json_hash(minimized),
                                                      "reduced_projection_sha256": json_hash(project_raw(minimized)),
                                                      "python_accept": direction[0], "lean_accept": direction[1],
                                                      "reduction": reduction, "versions": versions, "replay_command_argv": replay_command}})
            record.update(counterexample_file=str(counterexample), counterexample_sha256=file_hash(counterexample), reduction=reduction)
    counters = Counter()
    families: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        labels = ["total", "python_accepted" if record["python_accept"] else "python_rejected"]
        labels.append("schema_rejected" if record["domain"] == "schema-rejected" else "core_domain")
        if record["lean_evaluated"]:
            labels += ["lean_evaluated", "lean_errors" if record["lean_error"] else "lean_accepted" if record["lean_accept"] else "lean_rejected"]
            labels.append(record["comparison"])
        if not record["expectation_ok"]:
            labels.append("expectation_failures")
        counters.update(labels)
        families[record["family"]].update(labels)
    for key in ("total", "core_domain", "schema_rejected", "python_accepted", "python_rejected", "lean_evaluated", "lean_accepted", "lean_rejected", "lean_errors", "agree", "disagree", "expectation_failures"):
        counters.setdefault(key, 0)
    success = checker is not None and not any(counters[k] for k in ("disagree", "lean_errors", "expectation_failures")) and counters["lean_evaluated"] == counters["core_domain"]
    report = {"report_format": "skill-ir-differential-v1", "created_utc": datetime.now(timezone.utc).isoformat(),
              "status": "passed" if success else "prepared-not-checked" if checker is None else "failed",
              "scope": "Finite differential evidence, not a proof of Python/Lean equivalence or source-Skill semantics.",
              "input_contract": "Manifest selects the 30 SHA-256-verified analysis.json cfg objects. Schema rejects are never counted as Lean rejects.",
              "projection_contract": "Field schema normalization followed by injective names, ordered occurrences and exact normalized edge conditions; no Python rule answers cross the bridge.",
              "versions": versions, "counts": dict(counters), "families": {k: dict(v) for k, v in families.items()},
              "case_bundle_sha256": json_hash([{"name": r["name"], "input_sha256": r["input_sha256"]} for r in records]),
              "records": records}
    write_json(output / "report.json", report)
    manifest = {"report_path": str(output / "report.json"), "report_sha256": file_hash(output / "report.json"),
                "case_bundle_sha256": report["case_bundle_sha256"], "versions": versions}
    write_json(output / "attestation.json", manifest)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checker", type=Path)
    parser.add_argument("--prepare-only", action="store_true", help="Write fixtures and Python/schema outcomes; do not claim differential success")
    parser.add_argument("--manifest", type=Path, default=PACKAGE / "formal" / "fixtures" / "review30.json")
    parser.add_argument("--without-review", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "tmp" / "skill-ir-formal" / "differential")
    parser.add_argument("--seed", type=int, default=20260913)
    parser.add_argument("--random-count", type=int, default=160)
    parser.add_argument("--max-blocks", type=int, choices=range(1, 4), default=3)
    parser.add_argument("--shrink-budget", type=int, default=120)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args(argv)
    if args.prepare_only == bool(args.checker):
        parser.error("provide exactly one of --checker or --prepare-only")
    if args.random_count < 0 or args.shrink_budget < 0:
        parser.error("counts and shrink budget must be nonnegative")
    if args.replay:
        value = json.loads(args.replay.read_text(encoding="utf-8"))
        cases = [Case(**value)]
    else:
        cases = collect_cases(None if args.without_review else args.manifest, args.seed, args.random_count, args.max_blocks)
    report = run(cases, args.output, args.checker, shrink_budget=args.shrink_budget)
    print(json.dumps({"status": report["status"], "counts": report["counts"], "report": str(args.output.resolve() / "report.json")}, ensure_ascii=False))
    return 0 if report["status"] in {"passed", "prepared-not-checked"} and not report["counts"]["expectation_failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
