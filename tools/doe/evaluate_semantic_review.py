"""Prepare independent cases or score recorded reviews with human adjudication.

Preparation and scoring never invoke a model. Example usage:
  python -m tools.doe.evaluate_semantic_review prepare --output .cache/review-eval
  python -m tools.doe.evaluate_semantic_review score --runs .cache/review-eval/runs \
      --adjudication judgments.json --output .cache/review-eval/score.json

An actual experiment requires an explicit run --run-online command. Engineering
tests with an injected client are recorded separately and are not model results.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Literal

from pydantic import model_validator

from skillflow.common.recording import canonical_sha256, read_json, sha_file
from skillflow.common.source_evidence import StrictRecord, Text, Digest
from skillflow.propagation.review.runner import load_review_run, prepare_candidate_run, run_review
from skillflow.propagation.review.services import validate_response
from tools.doe.semantic_review_cases import CORPUS_VERSION, ORACLE_ORIGIN, evaluation_cases


class FindingJudgment(StrictRecord):
    finding_id: Text
    disposition: Literal["matches_oracle", "false_positive", "needs_baseline_review"]
    oracle_ids: list[Text]
    reason: Text

    @model_validator(mode="after")
    def usable_match(self):
        if len(self.oracle_ids) != len(set(self.oracle_ids)):
            raise ValueError("duplicate oracle IDs in adjudication")
        if (self.disposition == "matches_oracle") != bool(self.oracle_ids):
            raise ValueError("a matched finding needs oracle IDs; other dispositions cannot claim matches")
        return self


class CaseAdjudication(StrictRecord):
    case_id: Text
    review_sha256: Digest
    reviewer: Text
    reviewer_kind: Literal["human", "assistant", "unspecified"] = "unspecified"
    judgments: list[FindingJudgment]


class Adjudication(StrictRecord):
    corpus_version: Literal["source-task-demand-semantic-corpus-v1"]
    cases: list[CaseAdjudication]

    @model_validator(mode="after")
    def unique_cases(self):
        ids = [item.case_id for item in self.cases]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate adjudicated case IDs")
        return self


def score_case(case, review, adjudication: CaseAdjudication):
    """Manual adjudication judges matches; code validates ledgers and counts."""
    checked = validate_response(review, case["review_material"], normalized=True)
    if adjudication.case_id != case["id"] or adjudication.review_sha256 != canonical_sha256(review):
        raise ValueError("adjudication is not bound to this case and checked review")
    findings = {finding.id: finding for finding in checked.findings}
    judged = [row.finding_id for row in adjudication.judgments]
    if len(judged) != len(set(judged)) or set(judged) != set(findings):
        raise ValueError("human adjudication must classify each actual finding exactly once")
    oracle = {item["id"]: item for item in case["oracle"]}
    matched = set()
    false_positives = []
    baseline_questions = []
    for row in adjudication.judgments:
        finding = findings[row.finding_id]
        if row.disposition == "false_positive":
            false_positives.append(row.finding_id)
            continue
        if row.disposition == "needs_baseline_review":
            baseline_questions.append(row.finding_id)
            continue
        for identity in row.oracle_ids:
            if identity not in oracle or oracle[identity]["domain"] != finding.domain:
                raise ValueError("human match references an absent oracle or wrong finding domain")
            # Code subtypes are audit hints, not a substitute for the human's
            # evidence-based semantic match (e.g. unsupported vs broadened).
            matched.add(identity)
    return {"case_id": case["id"], "category": case["category"],
        "status": "oracle_gap" if baseline_questions else "adjudicated",
        "review_sha256": adjudication.review_sha256, "reviewer": adjudication.reviewer,
        "reviewer_kind": adjudication.reviewer_kind,
        "true_positives": sorted(matched), "false_negatives": sorted(set(oracle) - matched),
        "false_positives": false_positives, "needs_baseline_review": baseline_questions,
        "judgments": [row.model_dump(mode="json") for row in adjudication.judgments]}


def prepare(output, *, config=None, case_ids=None):
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("evaluation preparation requires a new or empty output directory")
    output.mkdir(parents=True, exist_ok=True)
    entries = []
    cases = evaluation_cases()
    requested = {case["id"] for case in cases} if case_ids is None else set(case_ids)
    if not requested or not requested <= {case["id"] for case in cases}:
        raise ValueError("case_ids must select existing independent corpus cases")
    for case in cases:
        if case["id"] not in requested:
            continue
        directory = output / "runs" / case["id"]
        prepare_candidate_run(case["material"], case["annotation"], run_dir=directory, config=config,
            provenance={"kind": "authored_semantic_evaluation_fixture", "corpus_version": CORPUS_VERSION,
                        "case_id": case["id"], "oracle_sha256": canonical_sha256(case["oracle"]),
                        "notice": "Authored evaluation candidate; no model call was made."})
        entries.append({"case_id": case["id"], "category": case["category"], "oracle": case["oracle"],
            "material_sha256": canonical_sha256(case["review_material"]),
            "prompt_sha256": sha_file(directory / "inputs/prompt.txt")})
    result = {"corpus_version": CORPUS_VERSION, "oracle_origin": ORACLE_ORIGIN,
        "human_expert_confirmation": "not_established", "model_experiment": "not_run", "cases": entries,
        "notice": "These independent synthetic reference cases were authored by an assistant from source text and have not been confirmed by human experts. The oracle and categories remain outside model input; structural validity does not establish detection."}
    (output / "oracle.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def run_cases(output, *, run_online=False, client=None, config=None, env_file=None, case_ids=None):
    """Use the production recorded reviewer; an online call is always explicit."""
    if not run_online and client is None:
        raise ValueError("actual model calls require run_online=True; offline simulations require an explicit injected client")
    if run_online and client is not None:
        raise ValueError("online experiments and injected engineering simulations cannot be mixed")
    if run_online and config is None:
        from skillflow.common.llm.config import LlmConfig
        from skillflow.propagation.annotation.config import annotation_public_config
        config = annotation_public_config(LlmConfig.from_env(env_file=env_file))
    prepared = prepare(output, config=config, case_ids=case_ids)
    statuses = []
    for entry in prepared["cases"]:
        directory = Path(output) / "runs" / entry["case_id"]
        result = run_review(directory, client=client, config=config, env_file=env_file)
        statuses.append({"case_id": entry["case_id"], "status": result["status"],
            "request_observed": result.get("request_validation", {}).get("observed", False),
            "review_sha256": canonical_sha256(result["review"]) if result.get("review") else None})
    result = {"corpus_version": CORPUS_VERSION,
        "origin": "explicit_online_experiment" if run_online else "engineering_simulation", "runs": statuses,
        "notice": "Call completion does not establish detection; semantic performance requires independent item-level matching and false-positive assessment."}
    (Path(output) / "experiment.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def score(runs, adjudication, *, baseline=None):
    """Only validated saved calls can enter the semantic experiment report."""
    ledger = Adjudication.model_validate(adjudication)
    cases = evaluation_cases()
    known = {case["id"] for case in cases}
    judgments = {row.case_id: row for row in ledger.cases}
    baseline_cases = {}
    if baseline is not None:
        if baseline.get("corpus_version") != CORPUS_VERSION:
            raise ValueError("explicit external oracle uses a different corpus version")
        baseline_cases = {row["case_id"]: row for row in baseline["cases"]}
        if len(baseline_cases) != len(baseline["cases"]):
            raise ValueError("explicit external oracle repeats a case")
    if not set(judgments) <= known:
        raise ValueError("adjudication names cases outside the frozen corpus")
    rows = []
    for case in cases:
        path = Path(runs) / case["id"]
        if not (path / "result.json").exists():
            if case["id"] in judgments:
                raise ValueError("adjudication supplied for a case without a recorded review")
            rows.append({"case_id": case["id"], "category": case["category"], "status": "not_run"})
            continue
        loaded = load_review_run(path)
        if canonical_sha256(loaded["material"]) != canonical_sha256(case["review_material"]):
            raise ValueError("recorded review material differs from the independent case")
        recorded_oracle = loaded["manifest"].get("authored_metadata", {}).get("oracle_sha256")
        if recorded_oracle is None:
            # The first explicitly authored v1 pilot predates per-case oracle
            # digests. Never rewrite it or silently claim a stronger binding.
            original = baseline_cases.get(case["id"])
            if (original is None or original["oracle"] != case["oracle"]
                    or original["material_sha256"] != canonical_sha256(loaded["material"])
                    or original["prompt_sha256"] != sha_file(path / "inputs/prompt.txt")):
                raise ValueError("run has no oracle digest; an explicit matching external baseline is required")
            oracle_binding = "explicit_external_baseline"
        elif recorded_oracle != canonical_sha256(case["oracle"]):
            raise ValueError("independent reference oracle changed after the review candidate was frozen")
        else:
            oracle_binding = "candidate_manifest_digest"
        result = loaded["result"]
        if result["status"] != "complete":
            if case["id"] in judgments:
                raise ValueError("failed reviews cannot be entered as adjudicated successes")
            rows.append({"case_id": case["id"], "category": case["category"], "status": "review_failed",
                         "execution_status": result["status"], "reason": result["reason"]})
        elif not result.get("request_validation", {}).get("observed"):
            if case["id"] in judgments:
                raise ValueError("injected/unobserved calls are engineering simulations, not model experiment results")
            rows.append({"case_id": case["id"], "category": case["category"], "status": "engineering_simulation"})
        elif case["id"] not in judgments:
            rows.append({"case_id": case["id"], "category": case["category"], "status": "awaiting_human_adjudication",
                         "review_sha256": canonical_sha256(result["review"])})
        else:
            rows.append({**score_case(case, result["review"], judgments[case["id"]]), "oracle_binding": oracle_binding})
    totals = Counter(row["status"] for row in rows)
    categories = defaultdict(lambda: Counter(true_positives=0, false_negatives=0, false_positives=0, cases=0))
    for row in rows:
        if row["status"] == "adjudicated":
            bucket = categories[row["category"]]
            bucket["cases"] += 1
            for metric in ("true_positives", "false_negatives", "false_positives"):
                bucket[metric] += len(row[metric])
    return {"corpus_version": CORPUS_VERSION, "oracle_origin": ORACLE_ORIGIN,
        "human_expert_confirmation": "not_established", "status_counts": dict(totals), "cases": rows,
        "by_category": {category: dict(counts) for category, counts in categories.items()},
        "notice": "Metrics use synthetic references and evidence-level assessment; reviewer_kind distinguishes human and assistant review. Human expert ground truth is not established. Unrun, failed, and unassessed cases remain separate; engineering tests are not semantic performance measurements."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--output", type=Path, required=True)
    prep.add_argument("--case-id", action="append", dest="case_ids")
    online = commands.add_parser("run")
    online.add_argument("--output", type=Path, required=True)
    online.add_argument("--env-file", type=Path)
    online.add_argument("--run-online", action="store_true")
    online.add_argument("--case-id", action="append", dest="case_ids")
    run = commands.add_parser("score")
    run.add_argument("--runs", type=Path, required=True)
    run.add_argument("--adjudication", type=Path, required=True)
    run.add_argument("--baseline", type=Path, help="explicit external oracle ledger for the first v1 pilot without per-case oracle digests")
    run.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        result = prepare(args.output, case_ids=args.case_ids)
    elif args.command == "run":
        if not args.run_online:
            parser.error("run requires explicit --run-online; prepare is offline")
        result = run_cases(args.output, run_online=True, env_file=args.env_file, case_ids=args.case_ids)
    else:
        result = score(args.runs, read_json(args.adjudication), baseline=read_json(args.baseline) if args.baseline else None)
    if args.command == "score":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("corpus_version",) if key in result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
