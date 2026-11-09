"""Prepare the long-source cohort for human references, with no dispatch route.

This source-only preparation intentionally creates no executable transport
protocol or formal gate. Existing frozen prompts and grading rules are copied
byte for byte; source references remain prominently incomplete.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path

from .assessment import build_review_template
from .execution import prepare_schedule
from .inputs import render_direct
from .protocol import sha256, utc_now, write_json
from .review import prepare_review_assignments, prepare_scoring_assignments
from .selection import prepare_reference_packets, verify_reference_packets

SCHEMA = "skillflow-long-cohort-human-preparation-v2"
COPIED_RULES = ("rubric.md", "grading-contract.json", "common-assumptions.md",
                "common-runtime-contract.json", "evaluation-rules-supplement-v1.md")
PROMPTS = ("audit.txt", "chain.txt", "review.txt")
SELECTION_STATE = "source_cohort_frozen_pending_complete_human_references"
FORBIDDEN_RECORDS = ("protocol.json", "cli-protocol.json", "protocol-freeze.json",
                     "formal-gate.json", "gate.json", "reference-freeze.json",
                     "calibration.json", "approvals/import-manifest.json")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _copy_bound(source, target, expected):
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("The prior frozen input changed: " + str(source))
    if target.exists() and target.read_bytes() != raw:
        raise ValueError("A prepared immutable copy differs: " + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(raw)


def _safe_file(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("A prepared file is missing or outside its run: " + relative)
    return path


def verify_preparation(run_dir, corpus_root):
    """Recheck copied source/rules without generating, grading or calling a model."""
    run = Path(run_dir).resolve()
    freeze = read(run / "preparation-freeze.json")
    errors = []
    frozen_files = freeze.get("files", {})
    if (freeze.get("schema_version") != SCHEMA or freeze.get("formal_requests") != 0
            or freeze.get("human_approvals") != 0 or freeze.get("execution_enabled") is not False
            or freeze.get("reference_coverage") != "source_facts_only_not_completed_semantic_gold"):
        errors.append("Preparation freeze does not declare the source-only, incomplete-reference state")
    required = {"source-selection.json", "source-selection-seal.json", "selection.json",
                "schedule.json", "cases/index.json", "preparation-state.json",
                "human-roster.template.json", "human-reference-package.md", "human-reference-package.html",
                "review/private-assignment-map.json", "review/assignments.json",
                "review/private-scoring-map.json", "review/scoring-assignments.json",
                *COPIED_RULES, *("prompts/" + name for name in PROMPTS)}
    missing = required - frozen_files.keys()
    if missing:
        errors.append("Preparation freeze omits required materials: " + ", ".join(sorted(missing)))
    for relative, expected in frozen_files.items():
        try:
            if sha256(_safe_file(run, relative)) != expected:
                errors.append("Prepared bytes changed: " + relative)
        except ValueError as error:
            errors.append(str(error))
    for forbidden in FORBIDDEN_RECORDS:
        if (run / forbidden).exists():
            errors.append("Preparation-only run contains an execution/approval record: " + forbidden)
    if any(p.is_file() for directory in ("mailbox", "workflows")
           for p in (run / directory).rglob("*")):
        errors.append("A source-only preparation unexpectedly contains target requests or outputs")
    packets = verify_reference_packets(corpus_root, run / "cases")
    errors.extend(packets["errors"])
    if packets["packet_count"] != 30:
        errors.append("Preparation requires exactly 30 complete source packets")
    selection = read(run / "selection.json")
    selected, reserves = selection.get("selected", []), selection.get("reserves", [])
    if (len(selected) != 24 or len(reserves) != 6
            or len({item.get("canonical_id") for item in selected + reserves}) != 30
            or [item.get("case_id") for item in selected + reserves] != [f"real-{n:03d}" for n in range(1, 31)]):
        errors.append("Preparation requires 24 distinct selected cases and six distinct reserves in packet order")
    if (selection.get("root_audit_required") is not False
            or selection.get("selection_state") != SELECTION_STATE):
        errors.append("Prepared selection has not recorded the completed root source audit")
    # Missing required material already fails verification. Avoid trusting a
    # partial tree merely because its remaining listed hashes match.
    if not missing:
        proposal, seal = read(run / "source-selection.json"), read(run / "source-selection-seal.json")
        if (seal.get("selection_sha256") != sha256(run / "source-selection.json")
                or seal.get("root_source_audit_complete") is not True or seal.get("formal_requests") != 0
                or [[i.get("canonical_id") for i in selection.get(role, [])] for role in ("selected", "reserves")]
                   != [[i.get("canonical_id") for i in proposal.get(role, [])] for role in ("selected", "reserves")]):
            errors.append("Prepared selection no longer matches its exact root-audited source proposal")
        for role in ("selected", "reserves"):
            for prepared, original in zip(selection.get(role, []), proposal.get(role, [])):
                if any(prepared.get(key) != value for key, value in original.items()
                       if key not in {"case_id", "source_path", "fixtures"}):
                    errors.append("Prepared case differs from its root-audited source identity: "
                                  + str(prepared.get("case_id")))
        if selection.get("packet_index_sha256") != sha256(run / "cases/index.json"):
            errors.append("Prepared packet index differs from its selection binding")
        packet_rows = read(run / "cases/index.json").get("packets", [])
        if [(i.get("case_id"), i.get("canonical_id")) for i in packet_rows] != [
                (i.get("case_id"), i.get("canonical_id")) for i in selected + reserves]:
            errors.append("Source packet identities differ from the prepared selection")
        schedule = read(run / "schedule.json")
        main, reviews = schedule.get("main", []), schedule.get("reviews", [])
        expected_main = {(i["case_id"], method, repeat) for i in selected
                         for method in ("skillflow", "audit", "chain") for repeat in (1, 2, 3)}
        expected_reviews = {(i["case_id"], method, 1) for i in selected for method in ("audit", "chain")}
        identity = lambda rows: {(i.get("case_id"), i.get("method"), i.get("repeat")) for i in rows}
        if (len(main) != 216 or len(reviews) != 48 or identity(main) != expected_main
                or identity(reviews) != expected_reviews
                or len({i.get("workflow_id") for i in main + reviews}) != 264):
            errors.append("Prepared schedule does not contain the fixed 216 main and 48 review workflows")
        for relative, count in (("review/private-scoring-map.json", 264), ("review/scoring-assignments.json", 264),
                                ("review/private-assignment-map.json", 72), ("review/assignments.json", 72)):
            if len(read(run / relative).get("assignments", [])) != count:
                errors.append("Prepared human assignment count differs: " + relative)
        if read(run / "human-roster.template.json").get("reviewers") != []:
            errors.append("Preparation cannot claim registered actual human reviewers")
        for item in selected + reserves:
            relative = f"references/{item['case_id']}.json"
            if relative not in frozen_files:
                errors.append("Preparation freeze omits a pending source reference: " + relative)
                continue
            draft = read(run / relative)
            if (draft.get("human_verified") is not False
                    or draft.get("coverage_state") != "source_facts_only_pending_semantic_reference"
                    or any(v.get("status") != "pending" for v in draft.get("human_verifications", []))):
                errors.append("Prepared source reference claims completed semantic or human verification: " + relative)
    for item in selected:
        for method in ("audit", "chain"):
            expected = render_direct(run, item["case_id"], method).encode("utf-8")
            for repeat in (1, 2, 3):
                path = run / "prepared-prompts" / f"{item['case_id']}_{method}_r{repeat}.txt"
                if not path.is_file() or path.read_bytes() != expected:
                    errors.append("A direct task differs from its full source and frozen prompt: " + str(path))
    return {"schema_version": SCHEMA, "status": "passed" if not errors else "failed",
            "errors": errors, "packet_count": packets["packet_count"], "formal_requests": 0,
            "model_calls": 0, "source_references_complete": False, "human_approvals": 0,
            "execution_enabled": False}


def prepare_long_cohort(run_dir, corpus_root, *, selection_path, prior_run, selection_seal):
    run, corpus, prior = Path(run_dir).resolve(), Path(corpus_root).resolve(), Path(prior_run).resolve()
    if run.exists() and any(run.iterdir()):
        raise ValueError("Use a new empty source-only preparation directory")
    selection_path, selection_seal = Path(selection_path).resolve(), Path(selection_seal).resolve()
    seal_sha256 = sha256(selection_seal)
    manifest, seal = read(selection_path), read(selection_seal)
    if (seal.get("selection_sha256") != sha256(selection_path)
            or seal.get("root_source_audit_complete") is not True
            or seal.get("formal_requests") != 0):
        raise ValueError("Root source audit must bind the exact selected proposal before preparation")
    if (manifest.get("status") != "selection_complete_pending_human_reference"
            or len(manifest.get("selected", [])) != 24 or len(manifest.get("reserves", [])) != 6):
        raise ValueError("A complete stronger-source 24+6 selection is required")
    old_rules, old_materials = read(prior / "evaluation-rules-freeze.json"), read(prior / "materials-freeze.json")
    if "user_request" in manifest or any("user_request" in item for item in manifest["selected"] + manifest["reserves"]):
        raise ValueError("Legacy independent-task catalogs cannot enter Skill-only preparation")
    if any("{user_request}" in (prior / "prompts" / name).read_text(encoding="utf-8") for name in PROMPTS):
        raise ValueError("Legacy independent-request templates cannot enter Skill-only preparation")
    run.mkdir(parents=True, exist_ok=True)
    _copy_bound(selection_path, run / "source-selection.json", seal["selection_sha256"])
    _copy_bound(selection_seal, run / "source-selection-seal.json", seal_sha256)
    for relative in COPIED_RULES:
        _copy_bound(prior / relative, run / relative, old_rules["files"][relative])
    for name in PROMPTS:
        relative = "prompts/" + name
        _copy_bound(prior / relative, run / relative, old_materials["files"][relative])
    prepare_reference_packets(corpus, manifest, run / "cases")
    packet_check = verify_reference_packets(corpus, run / "cases")
    if not packet_check["verified"]:
        raise ValueError("Copied source packets failed verification: " + repr(packet_check["errors"]))
    selected, reserves = [], []
    for index, item in enumerate(manifest["selected"] + manifest["reserves"], 1):
        case_id = f"real-{index:03d}"
        enriched = {**item, "case_id": case_id, "source_path": f"cases/{case_id}/source",
                    "fixtures": []}
        (selected if index <= 24 else reserves).append(enriched)
        draft = read(run / "cases" / case_id / "reference.source-facts-draft.json")
        draft["grading_schema_version"] = read(run / "grading-contract.json")["grading_schema_version"]
        write_json(run / "references" / (case_id + ".json"), draft, immutable=True)
    selection = {**manifest, "selected": selected, "reserves": reserves,
                 "packet_index_sha256": sha256(run / "cases/index.json"),
                 "root_audit_required": False, "selection_state": SELECTION_STATE,
                 "final_seal_scope": "The source cohort is root-audited; complete semantic references, human confirmations and the formal execution protocol remain unsealed."}
    write_json(run / "selection.json", selection, immutable=True)
    schedule = prepare_schedule(run, selected)
    for workflow in schedule["main"]:
        if workflow["method"] in {"audit", "chain"}:
            path = run / "prepared-prompts" / (workflow["workflow_id"] + ".txt")
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(render_direct(run, workflow["case_id"], workflow["method"]).encode("utf-8"))
    prepare_review_assignments(run, [c["case_id"] for c in selected])
    prepare_scoring_assignments(run)
    build_review_template(run)
    state = {"schema_version": SCHEMA, "state": "source_and_human_package_only",
             "selection": "long_complex_v2", "created_at": utc_now(), "formal_requests": 0,
             "human_approvals": 0, "reference_coverage": "source_facts_only_pending_semantic_reference",
             "transport": "not_adopted_for_this_cohort_after_retained_cli_v2_stop",
             "dispatch_enabled": False, "production_semantics": "not_modified_or_snapshotted_by_preparation",
             "required_before_formal": ["Complete all source semantic reference ledgers",
                 "Two actual human confirmations for every exact reference version",
                 "Prospectively fixed common transport and successful native engineering calibration",
                 "Final production/runtime equality verification and formal protocol freeze"],
             "inherited_rules": "Unchanged quality, matching, denominators, human allocation and statistical rules copied from frozen v1; no v1 source-reference approvals inherited."}
    write_json(run / "preparation-state.json", state, immutable=True)
    rows, markup = [], []
    for item in selected + reserves:
        case_id = item["case_id"]
        rows.append(f"| {case_id} | {'Formal' if item in selected else 'Reserve'} | {item['canonical_id']} | {item['version']} | {item['reference_tokens']:,} | [Source](cases/{case_id}/source-bundle.txt) · [Pending ledger](references/{case_id}.json) |")
        markup.append("<tr><td>" + html.escape(case_id) + "</td><td>" + html.escape(item["canonical_id"]) + "</td><td>" + f"{item['reference_tokens']:,}" + "</td><td><a href='cases/" + case_id + "/source-bundle.txt'>Complete source</a> · <a href='references/" + case_id + ".json'>Incomplete source-facts ledger</a></td></tr>")
    guide = "\n".join(["# Long-source human reference package", "",
        "This is preparation only. Formal target calls: zero. Actual human confirmations: zero. The reference ledgers contain partial source facts; empty exposure or receiving-point lists are pending work, not findings of safety.", "",
        "Two independent real human verifiers must establish and check the declared purpose, required results and constraints, every receiving point, necessary sensitive uses, source-supported excess, unresolved issues, and preservation arguments. Assistants may draft; they cannot enter human attestations. Do not inspect any target method outputs or registry safety summaries while constructing these references.", "",
        "Use the exact source files and original-language quotes. Current use is not proof of necessity; declared purpose is not actual user authorization. Normalize exposures by source, sensitive scope, version, condition, recipient and boundary event. Preserve distinctions between current mechanisms and proposed changes, plaintext and possible influence, and unknown and safe.", "",
        "Keep prior reference bytes and reasons before revising. Complete all semantic checks before registering personal confirmations through the existing import-human and freeze-references interfaces. This preparation contains no executable transport protocol and cannot dispatch formal targets. A separate verified formal run/version will be required.", "",
        "The 216 main workflows, 48 fixed reviews, 264 primary human assignments and 72 balanced first-read timed assignments are prospectively prepared. No results or timed scores have been created. Human roles remain unregistered; H1/H2 and R1/R2/R3 are assignment slots, not actual people.", "",
        "| Case | Role | Skill | Version | Reference tokens | Materials |", "|---|---|---|---|---:|---|", *rows, ""])
    (run / "human-reference-package.md").write_text(guide, encoding="utf-8")
    (run / "human-reference-package.html").write_text("<!doctype html><meta charset='utf-8'><title>Long-source reference preparation</title><style>body{font:16px system-ui;margin:32px;max-width:1400px}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}</style><h1>Long-source human reference preparation</h1><p>Partial source-facts ledgers only. No complete semantic gold, actual human confirmations or target outputs. Formal dispatch is disabled.</p><p><a href='human-reference-package.md'>Instructions</a> · <a href='rubric.md'>Common rubric</a> · <a href='human-roster.template.json'>Human registration template</a></p><table><thead><tr><th>Case</th><th>Skill</th><th>Reference tokens</th><th>Materials</th></tr></thead><tbody>" + "".join(markup) + "</tbody></table>", encoding="utf-8")
    files = {p.relative_to(run).as_posix(): sha256(p) for p in sorted(run.rglob("*")) if p.is_file()}
    write_json(run / "preparation-freeze.json", {"schema_version": SCHEMA, "files": files,
        "formal_requests": 0, "human_approvals": 0, "execution_enabled": False,
        "reference_coverage": "source_facts_only_not_completed_semantic_gold"}, immutable=True)
    verification = verify_preparation(run, corpus)
    write_json(run / "preparation-verification.json", verification, immutable=True)
    if verification["status"] != "passed":
        raise ValueError("Source-only preparation verification failed: " + repr(verification["errors"]))
    return {**state, "selected": 24, "reserves": 6, "source_packets": 30,
            "prepared_direct_requests": 144, "verification": verification}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--corpus-root", required=True)
    parser.add_argument("--selection-path")
    parser.add_argument("--selection-seal")
    parser.add_argument("--prior-run")
    args = parser.parse_args(argv)
    if args.command == "verify":
        result = verify_preparation(args.run_dir, args.corpus_root)
    else:
        if not all((args.selection_path, args.selection_seal, args.prior_run)):
            parser.error("prepare requires --selection-path, --selection-seal and --prior-run")
        result = prepare_long_cohort(args.run_dir, args.corpus_root, selection_path=args.selection_path,
                                    selection_seal=args.selection_seal, prior_run=args.prior_run)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
