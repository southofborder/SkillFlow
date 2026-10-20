"""Frozen schedule and preparation for the source-only collaboration experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "tools/doe/direct_prompts"
DEFAULT_RUN = ROOT / "experiments/doe/runs/direct-baseline-v1-20261019-171200"


def write_once(path: Path, value) -> None:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Frozen file differs: {path}")
    else:
        path.write_bytes(data)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _freeze_case(source, run, case_id, files, user_request=None):
    from tools.doe.direct_baseline import package_bundle
    case = run / "cases" / case_id
    if not case.exists():
        return package_bundle(source, run, case_id, source_files=files, user_request=user_request)
    manifest = json.loads((case / "manifest.json").read_text(encoding="utf-8"))
    expected = {f: sha(source / f) for f in files}
    if {s["path"]: s["sha256"] for s in manifest["sources"]} != expected:
        raise ValueError("Existing frozen case differs from source")
    request_hash = hashlib.sha256(user_request.encode("utf-8")).hexdigest() if user_request is not None else None
    if manifest["user_request_sha256"] != request_hash:
        raise ValueError("Existing frozen user request differs")
    return manifest


def _prepare_main(run, trial_id, case, arm, metadata):
    from tools.doe.direct_baseline import prepare_trial
    existing = run / "trials" / trial_id / "registration.json"
    if existing.exists():
        reg = json.loads(existing.read_text(encoding="utf-8"))
        if reg["case_id"] != case or reg["metadata"] != metadata or reg["template_sha256"] != sha(PROMPTS / f"{arm}.txt") or reg["shared_sha256"] != sha(PROMPTS / "shared.txt"):
            raise ValueError("Existing frozen trial differs from requested preparation")
        return reg
    return prepare_trial(run, trial_id, case, PROMPTS / f"{arm}.txt", shared_path=PROMPTS / "shared.txt", metadata=metadata)


def _initial_schedule(run):
    pilot_ids = ["p001_audit_r1", "p001_chain_r1", "p010_chain_r1", "p010_audit_r1", "p013_audit_r1", "p013_chain_r1"]
    main = []
    for repeat in (1, 2, 3):
        numbers = list(range(1, 13))
        if repeat == 2:
            numbers.reverse()
        for number in numbers:
            arms = ("audit", "chain") if (number + repeat) % 2 == 0 else ("chain", "audit")
            main.extend(f"c{number:02}_{arm}_r{repeat}" for arm in arms)
    reviews = [tid + "_review" for tid in main if tid.endswith("_r1")]
    write_once(run / "schedule.json", {
        "schema_version": "direct-baseline-schedule-v1",
        "pilot": pilot_ids + [tid + "_review" for tid in pilot_ids],
        "heldout": main + reviews,
        "target_calls_planned": 108, "quality_resampling": False,
        "source_reference_calls_and_assessment_calls_excluded_from_target_count": True,
    })


def pilot(run: Path) -> None:
    from tools.doe.direct_baseline import package_bundle, prepare_trial
    prefix = ROOT / "experiments/doe/runs/latest-prompts-pipeline-v1-20261018-124304/audit/english-inputs"
    definitions = {
        "001": (prefix / "001/package", ["SKILL.md"]),
        "010": (prefix / "010/package", ["SKILL.md", "query.yaml", "references/workflow.md"]),
        "013": (ROOT / "experiments/doe/runs/case-013-rerun-v1-20261019-105450/cases/013/inputs/package", ["SKILL.md"]),
    }
    for case, (source, files) in definitions.items():
        _freeze_case(source, run, case, files)
        for arm in ("audit", "chain"):
            _prepare_main(run, f"p{case}_{arm}_r1", case, arm,
                          {"stage": "pilot", "arm": arm, "repeat": 1, "review": False})
    write_once(run / "preregistration.json", {
        "schema_version": "direct-baseline-experiment-v1",
        "reference_status": "assistant_authored_exploratory",
        "purpose": "Test direct source-only audit and full semantic-chain reconstruction; no same-model SkillFlow comparison.",
        "runtime_recorded_model_expected": "gpt-6.1-sol",
        "runtime_recorded_reasoning_effort_expected": "ultra",
        "fork_turns": "none", "tool_access_hard_disabled": False,
        "environment_hard_isolation": False, "tools_forbidden_by_protocol": True,
        "pilot_cases": list(definitions), "pilot_main_repeats": 1,
        "pilot_independent_reviews_per_arm_case": 1,
        "maximum_development_prompt_revisions": 1,
        "heldout_families": 4, "heldout_variants_per_family": 3,
        "heldout_main_repeats": 3, "heldout_independent_review_repeats": [1],
        "heldout_prompt_revisions": 0, "quality_resampling": False,
        "pass_rule": "Every agreed mandatory criterion satisfied; no substantive false positive or function-breaking reduction. Unresolved reference disagreements remain indeterminate.",
        "reference_protocol": "Two separate source-only authors before target output, identity-masked scoring, explicit disputed evidence.",
        "usage_source": "child_thread_turn_response_usage_receipts",
        "monetary_cost": None,
        "prompt_sha256": {p.name: sha(p) for p in sorted(PROMPTS.glob("*.txt"))},
        "prohibited_target_inputs": ["CFG", "Task", "annotation", "propagation", "DOE", "historical reviews", "reference answers", "scores"],
    })
    _initial_schedule(run)


def expanded(run: Path) -> None:
    from tools.doe.direct_baseline import package_bundle, prepare_trial
    corpus = ROOT / "experiments/doe/inputs/direct-baseline-v1"
    catalog = json.loads((corpus / "catalog.json").read_text(encoding="utf-8"))
    for case in catalog["cases"]:
        source = ROOT / case["package_path"]
        if not source.exists():
            source = corpus / case["package_path"]
        request = ROOT / case["user_request_path"]
        if not request.exists():
            request = corpus / case["user_request_path"]
        files = [f["path"] for f in case["source_files"]]
        for f in case["source_files"]:
            if sha(source / f["path"]) != f["sha256"]:
                raise ValueError("Held-out source differs from its sealed catalog")
        if sha(request) != case["user_request_sha256"]:
            raise ValueError("Held-out task differs from its sealed catalog")
        _freeze_case(source, run, case["case_id"], files, request.read_text(encoding="utf-8"))
        for repeat in (1, 2, 3):
            for arm in ("audit", "chain"):
                _prepare_main(run, f"{case['case_id']}_{arm}_r{repeat}", case["case_id"], arm,
                              {"stage": "heldout", "arm": arm, "repeat": repeat, "review": False})
    write_once(run / "heldout-freeze.json", {
        "schema_version": "direct-baseline-heldout-freeze-v1",
        "catalog_sha256": sha(corpus / "catalog.json"),
        "prompt_sha256": {p.name: sha(p) for p in sorted(PROMPTS.glob("*.txt"))},
        "case_ids": [c["case_id"] for c in catalog["cases"]],
        "main_calls_planned": 72, "review_calls_planned": 24,
    })


def review(run: Path, trial_id: str) -> None:
    from tools.doe.direct_baseline import prepare_trial
    trial = run / "trials" / trial_id
    reg = json.loads((trial / "registration.json").read_text(encoding="utf-8"))
    metadata = reg.get("metadata", {})
    arm = metadata.get("arm") or reg.get("arm")
    case_id = reg["case_id"]
    answer = trial / "answer.txt"
    if not answer.exists():
        answer = trial / "response.txt"
    if not answer.exists():
        raise ValueError("Original visible answer must be imported before independent review")
    template = (trial / "template.txt").read_text(encoding="utf-8")
    # Share the exact deliverable instructions, without duplicating source/rules.
    instruction = template.split("{shared_rules}")[0].strip() + "\n" + template.split("{shared_rules}")[1].split("INDEPENDENT USER TASK")[0].strip()
    prepare_trial(run, trial_id + "_review", case_id, PROMPTS / "review.txt",
                  shared_path=trial / "shared.txt", original_answer_path=answer,
                  arm_instruction=instruction,
                  metadata={**metadata, "review": True, "parent_trial_id": trial_id})


def effective_schedule(run: Path) -> dict:
    revised = run / "schedule-revision1.json"
    path = revised if revised.exists() else run / "schedule.json"
    return json.loads(path.read_text(encoding="utf-8"))


def revision1(run: Path) -> None:
    """Use the sole preregistered development revision without overwriting v1."""
    from tools.doe.direct_baseline import prepare_trial
    decision = json.loads((run / "prompt-development-review.json").read_text(encoding="utf-8"))
    if decision["decision"] != "revision1":
        raise ValueError("The isolated pilot-only developer did not recommend a revision")
    base = json.loads((run / "schedule.json").read_text(encoding="utf-8"))
    old_mains = [t for t in base["pilot"] + base["heldout"] if not t.endswith("_review")]
    for tid in old_mains:
        reg = json.loads((run / "trials" / tid / "registration.json").read_text(encoding="utf-8"))
        m = reg["metadata"]
        metadata = {**m, "prompt_revision": 1,
                    "stage": "pilot_revision" if m["stage"] == "pilot" else "heldout"}
        new_id = tid + "_v2"
        new_path = run / "trials" / new_id / "registration.json"
        template = PROMPTS / "revision1" / f"{m['arm']}.txt"
        if new_path.exists():
            existing = json.loads(new_path.read_text(encoding="utf-8"))
            if existing["metadata"] != metadata or existing["template_sha256"] != sha(template):
                raise ValueError("Existing revision trial differs")
            continue
        prepare_trial(run, new_id, reg["case_id"], template,
                      shared_path=run / "trials" / tid / "shared.txt", metadata=metadata)
    def renamed(tid):
        return tid[:-7] + "_v2_review" if tid.endswith("_review") else tid + "_v2"
    revised_pilot = [renamed(t) for t in base["pilot"]]
    revised_heldout = [renamed(t) for t in base["heldout"]]
    write_once(run / "schedule-revision1.json", {
        "schema_version": "direct-baseline-schedule-v1",
        "supersedes_sha256": sha(run / "schedule.json"),
        "reason": "The one preregistered global pilot-only prompt revision; full pilot rerun, originals retained.",
        "pilot": base["pilot"] + revised_pilot,
        "pilot_revision": revised_pilot,
        "heldout": revised_heldout,
        "target_calls_planned": len(base["pilot"]) + len(revised_pilot) + len(revised_heldout),
        "quality_resampling": False,
        "unused_prepared_v1_heldout": base["heldout"],
    })
    write_once(run / "final-prompt-freeze.json", {
        "prompt_revision": 1, "development_revision_budget_used": 1,
        "development_revision_budget_remaining": 0,
        "basis": "Isolated source-only three-pilot review; heldout material excluded from prompt developer.",
        "shared_sha256": sha(PROMPTS / "shared.txt"),
        "review_sha256": sha(PROMPTS / "review.txt"),
        "templates": {arm: sha(PROMPTS / "revision1" / f"{arm}.txt") for arm in ("audit", "chain")},
        "heldout_changes_allowed": False,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("pilot", "expanded", "review", "revision1"))
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--trial-id")
    args = parser.parse_args()
    if args.action == "review":
        review(args.run_dir, args.trial_id)
    else:
        globals()[args.action](args.run_dir)
