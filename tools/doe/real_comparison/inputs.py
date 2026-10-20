"""Freeze common source inputs and reusable prompts without reference leakage."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from .assessment import build_review_template
from .execution import prepare_schedule
from .protocol import SCHEMA, sha256, write_json, prepare_protocol
from .review import prepare_review_assignments, prepare_scoring_assignments

ROOT = Path(__file__).resolve().parents[3]
PREVIOUS = ROOT / "experiments/doe/runs/direct-baseline-v1-20261019-171200/prompts"
NO_TASK = "No independent user task is supplied. Audit only relative to the Skill's declared purpose; author statements are not verified user authorization."
REVIEW = """Independently review and return a complete corrected English answer to the
original source-only static analysis task below. Preserve original-language
source quotations. You receive no scores, gold reference or reviewer advice.
Use only the original task, its source material, rules and exact first answer.
Do not use tools, files, browsing, other agents or follow-up messages. Distinguish
current mechanisms from proposed changes, supported plaintext from possible
influence, established excess from missing evidence, and ordinary return from
established user delivery. A necessary action does not exempt all its payload.
Return the entire checked answer, not just a correction note. State corrections
briefly without treating agreement as proof of safety or semantic completeness.

ORIGINAL SOURCE-ONLY TASK
{original_task}

EXACT FIRST VISIBLE ANSWER
{original_answer}
"""


def substitute(template, values):
    # Source braces and literal template strings must remain original evidence.
    return re.sub(r"\{(user_request|source_bundle|original_task|original_answer)\}",
                  lambda match: values[match[1]], template)


def _immutable_text(path, text):
    path = Path(path)
    if path.exists() and path.read_bytes() != text.encode("utf-8"):
        raise ValueError(f"Frozen input differs: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(text.encode("utf-8"))


def render_direct(run_dir, case_id, method):
    if method not in {"audit", "chain"} or not re.fullmatch(r"[A-Za-z0-9_-]+", case_id):
        raise ValueError("Invalid direct method or case identity")
    run = Path(run_dir)
    template = (run / "prompts" / f"{method}.txt").read_text(encoding="utf-8")
    source = (run / "cases" / case_id / "source-bundle.txt").read_text(encoding="utf-8")
    return substitute(template, {"user_request": NO_TASK, "source_bundle": source})


def render_review(run_dir, case_id, method, original_answer):
    run = Path(run_dir)
    template = (run / "prompts" / "review.txt").read_text(encoding="utf-8")
    return substitute(template, {"original_task": render_direct(run, case_id, method),
                                 "original_answer": original_answer})


def prepare_inputs(run_dir, corpus_root, *, screening_path=None):
    from .selection import select_cases, prepare_reference_packets, verify_reference_packets
    run, corpus = Path(run_dir), Path(corpus_root)
    prepare_protocol(run)
    manifest = select_cases(corpus, screening_path=screening_path)
    if manifest["status"] != "selection_complete_pending_human_reference":
        return {"status": "not_ready", "selection": manifest,
                "formal_target_calls": 0, "reason": "Complete the source-only screening before freezing formal case packets."}
    packets = prepare_reference_packets(corpus, manifest, run / "cases")
    verification = verify_reference_packets(corpus, run / "cases")
    if not verification["verified"]:
        raise ValueError("Common-source packet verification failed")
    selected, reserves = [], []
    for index, item in enumerate(manifest["selected"] + manifest["reserves"], 1):
        case_id = f"real-{index:03d}"
        enriched = {**item, "case_id": case_id,
                    "source_path": f"cases/{case_id}/source", "user_request": None, "fixtures": []}
        (selected if index <= 24 else reserves).append(enriched)
        source_template = run / "cases" / case_id / "reference.source-facts-draft.json"
        reference = run / "references" / f"{case_id}.json"
        if not reference.exists():
            reference.parent.mkdir(parents=True, exist_ok=True)
            draft = json.loads(source_template.read_text(encoding="utf-8"))
            draft["grading_schema_version"] = "skillflow-real-comparison-grading-v2"
            write_json(reference, draft)
    selection = {**manifest, "selected": selected, "reserves": reserves,
                 "packet_index_sha256": sha256(run / "cases" / "index.json")}
    write_json(run / "selection.json", selection, immutable=True)
    write_json(run / "grading-contract.json", {
        "schema_version": SCHEMA, "grading_schema_version": "skillflow-real-comparison-grading-v2",
        "scope": "Human scoring records only; target answers have no required common output schema.",
        "requires_normalized_claims_receivers_reductions_and_chain_checks": True}, immutable=True)
    for method, filename in (("audit", "direct-audit-final.txt"), ("chain", "full-chain-final.txt")):
        _immutable_text(run / "prompts" / f"{method}.txt", (PREVIOUS / filename).read_text(encoding="utf-8"))
    _immutable_text(run / "prompts" / "review.txt", REVIEW)
    audit = (run / "prompts/audit.txt").read_text(encoding="utf-8")
    assumptions = audit.split("Shared abstract runtime assumptions", 1)[1].split("For each material conclusion", 1)[0]
    _immutable_text(run / "common-assumptions.md", "# Shared abstract runtime assumptions" + assumptions)
    from skillflow.propagation.contracts.runtime_contract import runtime_contract, runtime_contract_binding
    contract = runtime_contract()
    write_json(run / "common-runtime-contract.json", {"contract": contract,
               "binding": runtime_contract_binding(contract),
               "direct_rule_crosswalk": {"1": ["EM01"], "2": ["EM02", "EM03", "EM04"],
                   "3": ["EM03", "EM04", "EM10"], "4": ["EM04", "EM08", "EM11"],
                   "5": ["EM05", "EM12"], "6": ["EM06", "EM09", "EM12", "EM13", "EM15"],
                   "7": ["EM07", "EM12", "EM13"], "8": ["EM10", "EM11", "EM14", "EM15"]},
               "limit": "The crosswalk documents shared semantic assumptions. Native IR fields, compiler restrictions and matching algorithms are not format or representability requirements for direct methods, nor proof of source-level completeness."}, immutable=True)
    schedule = prepare_schedule(run, selected)
    for workflow in schedule["main"]:
        if workflow["method"] in {"audit", "chain"}:
            _immutable_text(run / "prepared-prompts" / f"{workflow['workflow_id']}.txt",
                            render_direct(run, workflow["case_id"], workflow["method"]))
    prepare_review_assignments(run, [c["case_id"] for c in selected])
    prepare_scoring_assignments(run)
    build_review_template(run)
    materials = {}
    materials["common-runtime-contract.json"] = sha256(run / "common-runtime-contract.json")
    materials["grading-contract.json"] = sha256(run / "grading-contract.json")
    materials["common-assumptions.md"] = sha256(run / "common-assumptions.md")
    for relative in ("schedule.json", "review/private-assignment-map.json", "review/assignments.json",
                     "review/private-scoring-map.json", "review/scoring-assignments.json"):
        materials[relative] = sha256(run / relative)
    for folder in ("cases", "prompts", "prepared-prompts"):
        for path in sorted((run / folder).rglob("*")):
            if path.is_file():
                materials[path.relative_to(run).as_posix()] = sha256(path)
    write_json(run / "materials-freeze.json", {"schema_version": SCHEMA, "files": materials,
                                               "selection_sha256": sha256(run / "selection.json"),
                                               "references_and_scores_in_target_view": False}, immutable=True)
    return {"status": "prepared_pending_humans", "selected": 24, "reserves": 6,
            "formal_target_calls": 0, "prepared_direct_requests": 144,
            "reference_packets": len(packets["packets"]),
            "human_confirmations_required": 60}
