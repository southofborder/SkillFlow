"""Seal current scoped offline acceptance after the complete receipt exists."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import IDENTITY, POLICY

VERIFY = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def create(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    receipt = VERIFY / "tests-final-integrated.xml"
    cases = ET.parse(receipt).getroot().findall(".//testcase")
    failures = [c.attrib for c in cases if c.find("failure") is not None or c.find("error") is not None]
    skipped = [c.attrib for c in cases if c.find("skipped") is not None]
    identities = [(c.get("classname"), c.get("name")) for c in cases]
    if failures or not cases or len(set(identities)) != len(identities):
        raise ValueError("Final scoped receipt is empty, failed or has duplicate identities")
    current = implementation_provenance()
    before = read(VERIFY / "baseline-provenance.json")
    measurement = read(VERIFY / "integrated-delivery-measurement.json")
    if current["sha256"] != measurement["implementation_sha256"]:
        raise ValueError("Production changed since final rendering proof")
    changed = [name for name in current["files"] if current["files"][name] != before["files"].get(name)]
    removed = sorted(set(before["files"]) - set(current["files"]))
    if set(changed) != {"src/skillflow/document_guided/review_display.py", "src/skillflow/document_guided/source_review.py", "src/skillflow/document_guided/runner.py"} or removed:
        raise ValueError("Production scope differs from the reviewed three-file presentation change")
    if not all(measurement[k] for k in ("old_prompt_byte_identical", "exact_serialized_payload_roundtrip", "source_section_byte_identical", "every_obligation_scope_identity_order_and_descriptor_retained")):
        raise ValueError("Complete preservation proof is missing")
    if measurement["new_delivery_codepoints"] >= measurement["transport_limit_unchanged"]:
        raise ValueError("The reproducer still exceeds the unchanged cap")
    old = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209"
    for name, digest in measurement["original_artifact_hashes_unchanged"].items():
        if sha(old / name) != digest:
            raise ValueError("Historical artifact changed: " + name)
    receipt_data = {"file": receipt.name, "sha256": sha(receipt), "cases": len(cases),
                    "passed": len(cases) - len(skipped), "skipped": len(skipped), "failures": 0,
                    "scope": ["tests/document_guided", "tests/doe/test_input_contract_scopes.py",
                              "tests/doe/test_input_contract_review.py", "tests/common/test_prompt_format.py"]}
    create(VERIFY / "implementation-provenance.json", current)
    acceptance = {"status": "passed", "sealed_at": datetime.now(timezone.utc).isoformat(),
        "implementation_sha256": current["sha256"], "baseline_implementation_sha256": before["sha256"],
        "production_changed_files": changed, "production_removed_files": removed,
        "guided_run_identity": IDENTITY, "policy": POLICY, "final_current_receipt": receipt_data,
        "distinct_current_scoped_passed": len(cases) - len(skipped), "skipped": len(skipped),
        "unresolved_test_failures": 0, "whole_repository_all_green_execution": False,
        "initial_receipts_preserved": ["tests-shared-review-initial.xml", "tests-shared-lifecycle-initial.xml", "tests-adaptive-shared-review.xml"],
        "exact_request_preservation": {k: measurement[k] for k in ("original_delivery_codepoints", "new_delivery_codepoints", "saved_codepoints", "remaining_headroom", "obligation_count", "scope_count", "transport_limit_unchanged")},
        "new_model_calls_during_offline": 0, "skill_execution": False, "historical_analysis_or_replay": False,
        "independent_review": "review-notes.en.md",
        "online_authorization": "Root alone may next prepare and launch exactly one new GA4 and its sole controller-owned zero-call replay; no other cases, probes or historical resumes."}
    create(VERIFY / "offline-acceptance.json", acceptance)
    state = read(VERIFY / "continuation-state.json")
    state.update(status="offline_accepted", implementation_sha256=current["sha256"],
                 offline_acceptance="offline-acceptance.json", production_frozen=True,
                 online_verification="output/verification/online-ga4-review-shared-v2-20261112", new_model_starts=0)
    (VERIFY / "continuation-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (VERIFY / "assessment.en.md").write_text(
        "# Generic source-review input-size acceptance\n\n"
        f"The current implementation `{current['sha256']}` passed {len(cases) - len(skipped)} scoped tests with {len(skipped)} skips and zero failures in one final integrated execution. "
        "This is not a whole-repository test execution. Earlier focused receipts remain preserved and are not added as duplicate passes.\n\n"
        "Only review_display.py, source_review.py and runner.py differ from the accepted baseline production inventory. "
        "The reusable shared-v2 default retains all source and contracts and selects packed delivery only when its JSON plus explanation is shorter. "
        "Seven normal requests, two workers, Task v5 isolation and existing budgets remain unchanged.\n\n"
        "The immutable failed-request reproducer measures 1,079,505 -> 903,775 characters, saving 175,730, with 144,801 below the unchanged 1,048,576 cap. "
        "All 16 source files, 344 obligations and 1,195 scopes survive exact serialized roundtrip, and all tracked historical artifacts retain their hashes. "
        "No model calls, Skill execution, historical analysis or replay occurred in this offline work.\n\n"
        "Coverage includes arbitrary names and counts, nonrepeating inputs, distinct near-duplicates, literal marker collisions, complete and partial materials, "
        "original repair coordinates, mandatory contract coverage, exact transport boundaries and zero-start rejection, injected seven-call/two-worker execution, "
        "repair/re-review and zero-call replay. Independent review found no blocking issue.\n\n"
        "Irreducibly over-limit material still fails explicitly without truncation. Lossless reconstruction does not establish model comprehension. "
        "The one newly authorized GA4 will be separate online evidence.\n\n"
        "See offline-acceptance.json, tests-final-integrated.xml/.log, integrated-delivery-measurement.json, review-notes.en.md, "
        "size-audit/assessment.en.md and docs/doe/review-input-size.md/.zh.md.\n", encoding="utf-8")
    print(json.dumps(acceptance, indent=2))


if __name__ == "__main__":
    main()
