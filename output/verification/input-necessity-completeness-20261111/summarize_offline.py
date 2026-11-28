"""Seal this follow-up's latest scoped XML outcomes without changing old receipts."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[2]
sys.path.insert(0, str(ROOT))
from skillflow.common.recording import implementation_provenance, canonical_sha256

SUPERSESSIONS = [
    {"old": ["tests.document_guided.test_input_contract_completeness", "test_exact_compute_expression_exempts_only_its_own_operation[inline]"],
     "replacement": ["tests.document_guided.test_input_contract_completeness", "test_exact_compute_expression_exempts_only_its_own_operation"],
     "reason": "The supported inline-expression case was retained as the unparameterized test after removing an invalid public target form."},
    {"old": ["tests.document_guided.test_input_contract_completeness", "test_exact_compute_expression_exempts_only_its_own_operation[supplement]"],
     "replacement": ["tests.document_guided.test_input_contract_completeness", "test_public_supplement_does_not_introduce_a_new_operation_target_syntax"],
     "reason": "The initial positive fixture invented an unsupported public operation-target syntax. Its replacement explicitly rejects that syntax; the supported inline operation exemption remains tested separately."},
    {"old": ["tests.document_guided.test_optional_case_segments", "test_exact_ga4_failed_case_compiles_without_editing_extracted_answer"],
     "replacement": ["tests.document_guided.test_optional_case_segments", "test_exact_historical_ga4_case_keeps_omitted_segments_but_requires_current_contracts"],
     "reason": "An unchanged historical answer cannot pass the new mandatory-contract route. The replacement preserves its bytes and equal omitted/explicit-empty diagnostics; six current synthetic cases still prove compilation and assembly equivalence."},
]


def main():
    latest, receipts = {}, []
    parsed = [(p, ET.parse(p).getroot()) for p in DIRECTORY.glob("*.xml")]
    for path, document in sorted(parsed, key=lambda item: (
            next(item[1].iter("testsuite")).get("timestamp", ""), item[0].name)):
        counts, failures, skips = Counter(), [], []
        for case in document.iter("testcase"):
            error = case.find("failure")
            if error is None:
                error = case.find("error")
            skipped = case.find("skipped")
            outcome = "failed" if error is not None else "skipped" if skipped is not None else "passed"
            key = (case.get("classname", ""), case.get("name", ""))
            row = dict(classname=key[0], name=key[1], status=outcome, receipt=path.name)
            if error is not None:
                row["reason"] = error.get("message", "")
                failures.append(row)
            if skipped is not None:
                row["reason"] = skipped.get("message", "")
                skips.append(row)
            latest[key] = row
            counts[outcome] += 1
        receipts.append(dict(path=path.name, started_at=next(document.iter("testsuite")).get("timestamp"),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(), outcomes=dict(counts),
            failed_tests=failures, skipped_tests=skips))
    superseded = []
    for change in SUPERSESSIONS:
        old, replacement = tuple(change["old"]), tuple(change["replacement"])
        if old not in latest:
            continue
        if latest.get(replacement, {}).get("status") != "passed":
            raise ValueError("An obsolete test cannot be superseded without its passing replacement: " + str(replacement))
        superseded.append({**change, "prior_latest_outcome": latest.pop(old),
                           "replacement_outcome": latest[replacement]})
    totals = Counter(row["status"] for row in latest.values())
    provenance = implementation_provenance()
    python_files = {p: h for p, h in provenance["files"].items() if p.startswith("src/") and p.endswith(".py")}
    result = dict(schema_version="skillflow-input-necessity-completeness-acceptance-v1",
        created_at=datetime.now(timezone.utc).isoformat(),
        status="passed" if totals["passed"] and not totals["failed"] else "unresolved_failures",
        distinct_latest_test_outcomes=dict(totals), whole_repository_all_green_claim=False,
        scope="Latest-started per-classname/name union of current test identities in this directory's scoped XML receipts; three explicitly documented obsolete identities are superseded by passing replacements, not relabeled as passes. All initial failures remain preserved.",
        implementation_sha256=provenance["sha256"], python_source_sha256=canonical_sha256(python_files),
        real_model_calls=0, skill_executions=0, historical_replays=0,
        original_real_batch="../online-input-necessity-20261111/four-run-summary.json",
        original_measured_implementation_sha256="09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0",
        receipts=receipts, latest_tests=[latest[k] for k in sorted(latest)],
        superseded_test_identities=superseded,
        interrupted_command_record="integrated-initial-interruption.json",
        limitations=["The corrected implementation has offline evidence only.",
            "Source-reviewed semantic truth is not mechanically proved.",
            "No global minimality or general accuracy claim.", "No analyzed Skill is rewritten."])
    name = "offline-acceptance.json" if result["status"] == "passed" else "offline-unresolved.json"
    target = DIRECTORY / name
    if target.exists():
        raise ValueError("Retain prior aggregate receipts; use a new output name for a revised acceptance")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] == "passed":
        (DIRECTORY / "implementation-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"receipts", "latest_tests"}}, indent=2))


if __name__ == "__main__":
    main()
