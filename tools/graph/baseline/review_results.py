"""Export offline review packets and validate human/agent fact assessments.

This module never sends a model request or assigns semantic verdicts. It consumes
the already frozen answers only AFTER extraction, outside every Skill input.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from skillflow.common.paths import project_root, resolve_material_path

BASE = project_root() / "experiments/graph/baseline"
VERDICTS = {"preserved", "partial", "missing", "contradicted", "unassessable"}
TERMINAL = {"complete", "degraded", "error", "uncertain"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def trials_for(run, sample_id):
    report = read(run / "report.json")
    trials = sorted((t for t in report["trials"] if t["case"] == sample_id), key=lambda t: t["repetition"])
    if [t["repetition"] for t in trials] != [1, 2, 3]:
        raise ValueError(f"Expected exactly three trials: {sample_id}")
    return trials


def analysis_for(run, trial):
    path = run / trial["artifacts"] / "analysis.json"
    return read(path) if path.exists() else None


def reference_ids(analysis):
    refs = {"diagnostics", "skill.constraints"}
    if not analysis or not analysis.get("cfg"):
        return refs
    cfg = analysis["cfg"]
    for block_id, block in cfg["blocks"].items():
        refs.add(block_id)
        refs.add(block_id + ".constraints")
        for instruction in block["instructions"]:
            refs.add(instruction["id"])
            refs.add(instruction["id"] + ".constraints")
    refs.update(f"edge_{index:03d}" for index, _ in enumerate(cfg["edges"], 1))
    return refs


def compact_analysis(analysis):
    if analysis is None:
        return None
    result = {key: deepcopy(analysis.get(key)) for key in ("status", "diagnostics", "cfg")}
    if result["cfg"]:
        for index, edge in enumerate(result["cfg"]["edges"], 1):
            edge["review_edge_id"] = f"edge_{index:03d}"
        for block in result["cfg"]["blocks"].values():
            for instruction in block["instructions"]:
                metadata = instruction.get("metadata", {})
                if "script_content" in metadata:
                    original = metadata["script_content"]
                    metadata["script_content"] = {
                        "omitted_from_packet_only": True,
                        "characters": len(str(original)),
                        "sha256": hashlib.sha256(str(original).encode()).hexdigest(),
                        "full_text_in": "analysis.json at this instruction's metadata.script_content",
                    }
    return result


def packet_for(run, sample, base=BASE):
    corpus = base / "frozen/corpus"
    annotation = read(corpus / sample["annotation_path"])
    trials = trials_for(run, sample["id"])
    if any(t["status"] not in TERMINAL for t in trials):
        raise ValueError(f"Three terminal trials required for review: {sample['id']}")
    return {
        "sample": sample,
        "annotation": annotation,
        "source_directory": str((corpus / sample["package_path"]).resolve()),
        "runs": [{
            "repetition": trial["repetition"],
            "record": trial,
            "analysis_sha256": sha(run / trial["artifacts"] / "analysis.json"),
            "record_sha256": sha(run / trial["artifacts"] / "record.json"),
            "analysis": compact_analysis(analysis_for(run, trial)),
        } for trial in trials],
        "policy": "Manual source-grounded review; structure does not imply semantic preservation. No annotation is an extraction input.",
    }


def validate_review(review, sample, run, base=BASE):
    if review.get("schema_version") != 1 or review.get("sample_id") != sample["id"]:
        raise ValueError("Review schema/sample mismatch")
    if any(not isinstance(review.get(key), str) or not review[key].strip()
           for key in ("reviewer", "run_comparison", "overall")):
        raise ValueError("Review requires reviewer, run comparison and overall opinion")
    annotation = read(base / "frozen/corpus" / sample["annotation_path"])
    expected = {f["id"] for f in annotation["facts"]}
    facts = review.get("facts", [])
    if len(facts) != len(expected) or {f["fact_id"] for f in facts} != expected:
        raise ValueError(f"Review must cover every frozen fact exactly once: {sample['id']}")
    trials = trials_for(run, sample["id"])
    refs, accepted, has_diagnostics = {}, {}, {}
    for trial in trials:
        rep = trial["repetition"]
        if trial["status"] not in TERMINAL:
            raise ValueError("Unfinished trial cannot be reviewed")
        for name in ("analysis", "record"):
            expected_sha = sha(run / trial["artifacts"] / f"{name}.json")
            if review.get(f"{name}_sha256", {}).get(str(rep)) != expected_sha:
                raise ValueError(f"Stale {name} review: {sample['id']} repeat {rep}")
        analysis = analysis_for(run, trial)
        refs[rep] = reference_ids(analysis)
        has_diagnostics[rep] = bool(analysis and analysis.get("diagnostics"))
        accepted[rep] = (
            trial["status"] == "complete" and isinstance(analysis, dict)
            and analysis.get("status") == "complete" and isinstance(analysis.get("cfg"), dict)
            and bool(analysis["cfg"].get("blocks"))
        )
    kinds = {fact["id"]: fact["kind"] for fact in annotation["facts"]}
    unresolved_constraints = {
        fact["id"] for fact in annotation["facts"]
        if fact["kind"] == "constraint" and fact.get("scope", {}).get("level") == "unresolved"
    }

    def check_references(references, repetitions, label):
        if not isinstance(references, list) or any(not isinstance(ref, str) for ref in references):
            raise ValueError(f"CFG references must be a list of identifiers: {label}")
        for rep in repetitions:
            if set(references) - refs[rep]:
                raise ValueError(f"Unknown CFG reference: {label} repeat {rep}")

    for fact in facts:
        assessments = fact.get("assessments", [])
        if len(assessments) != 3 or {a["repetition"] for a in assessments} != {1, 2, 3}:
            raise ValueError(f"Three assessments required: {fact['fact_id']}")
        for assessment in assessments:
            if (assessment.get("verdict") not in VERDICTS
                or not isinstance(assessment.get("reason"), str)
                or not assessment["reason"].strip()):
                raise ValueError(f"Missing manual verdict or rationale: {fact['fact_id']}")
            rep = assessment["repetition"]
            references = assessment.get("references", [])
            check_references(references, [rep], fact["fact_id"])
            if not accepted[rep] and assessment["verdict"] != "unassessable":
                raise ValueError("No accepted CFG: do not grade a failed extraction as semantically complete")
            if assessment["verdict"] == "preserved":
                # The frozen contract keeps an unknown constraint scope in
                # diagnostics; requiring a CFG location would invent a scope.
                # This exception does not replace CFG evidence for behaviors
                # or constraints whose scope is already known.
                diagnostic_evidence = (
                    kinds[fact["fact_id"]] == "must_not_infer"
                    or (fact["fact_id"] in unresolved_constraints and has_diagnostics[rep])
                )
                if not references or (set(references) == {"diagnostics"}
                                      and not diagnostic_evidence):
                    raise ValueError(f"Preserved fact requires actual CFG evidence: {fact['fact_id']}")
    findings = review.get("additional_findings", [])
    if not isinstance(findings, list):
        raise ValueError("Additional findings must be a list")
    for index, finding in enumerate(findings, 1):
        if not isinstance(finding, dict) or not isinstance(finding.get("reason"), str) or not finding["reason"].strip():
            raise ValueError(f"Additional finding requires manual rationale: {index}")
        repetitions = finding.get("repetitions")
        if (not isinstance(repetitions, list) or not repetitions
            or any(type(rep) is not int or rep not in {1, 2, 3} for rep in repetitions)
            or len(repetitions) != len(set(repetitions))):
            raise ValueError(f"Additional finding requires valid repetitions: {index}")
        check_references(finding.get("references", []), repetitions, f"additional finding {index}")
    return Counter(a["verdict"] for f in facts for a in f["assessments"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=BASE / "runs/baseline-sol-max-v1")
    parser.add_argument("--samples", nargs="*")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    run = args.run_dir.resolve()
    samples = read(BASE / "frozen/corpus/corpus.json")["samples"]
    if args.samples:
        known = {s["id"] for s in samples}
        if set(args.samples) - known:
            raise ValueError("Unknown sample IDs")
        samples = [s for s in samples if s["id"] in args.samples]
    totals = Counter()
    for sample in samples:
        if args.export:
            try:
                packet = packet_for(run, sample)
            except ValueError as error:
                print(error)
                continue
            write(run / "review_packets" / f"{sample['id']}.json", packet)
            print(f"Exported {sample['id']}")
        if args.check:
            totals.update(validate_review(read(run / "reviews" / f"{sample['id']}.json"), sample, run))
    if args.check:
        print(json.dumps({"samples": len(samples), "fact_run_assessments": sum(totals.values()), "verdicts": dict(totals)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
