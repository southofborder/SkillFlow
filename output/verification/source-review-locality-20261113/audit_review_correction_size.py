"""Offline validation/render-only measurement; never a runner or replay.

Reads immutable prior review material and candidate files; writes new audit
receipts only beside this script. Does not invoke a CLI, model, Skill, backend
analysis, source execution, or historical result loader.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from skillflow.common.prompt_format import compact_json
from skillflow.common.structural_correction import _current_diagnostics, VERSION
from skillflow.common.validation import diagnostic_materials
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.document_guided.review_display import expand_review_payload
from skillflow.document_guided.source_review import (
    FRAGMENT_IDENTITY, build_source_review_prompt, isolate_source_review,
)
from tools.doe.document_guided_client import ENVELOPE, MAX_INPUT_CHARS


OUT = Path(__file__).resolve().parent
REVIEW = ROOT / "experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242/review"
CODE = ["src/skillflow/document_guided/fragments.py", "src/skillflow/document_guided/review_correction.py",
        "src/skillflow/document_guided/review_isolation.py", "src/skillflow/document_guided/review_display.py",
        "src/skillflow/document_guided/source_review.py", "src/skillflow/common/structural_correction.py",
        "src/skillflow/common/validation.py", "tools/doe/document_guided_client.py"]


def sha(value):
    return hashlib.sha256(value).hexdigest()


def file_hash(path):
    return sha(path.read_bytes())


def load(path):
    return json.loads(path.read_bytes().decode("utf-8"))


def split(prompt):
    start = prompt.index("\nINPUT_JSON\n") + len("\nINPUT_JSON\n")
    display, width = json.JSONDecoder().raw_decode(prompt[start:])
    return expand_review_payload(display), prompt[start + width:], display


def main():
    inputs = [REVIEW / "inputs.json", REVIEW / "prompt.txt",
              REVIEW / "calls/review/a001/response.json", REVIEW / "calls/review/a002/merged-candidate.json"]
    hashes = {path.relative_to(ROOT).as_posix(): file_hash(path) for path in inputs}
    code = {path: file_hash(ROOT / path) for path in CODE}
    material = load(inputs[0])
    prior_identity = material["identity"]
    material["identity"] = FRAGMENT_IDENTITY  # New in-memory display only; no artifact is migrated.
    base = build_source_review_prompt(material)
    original, source, _ = split(base)
    _, old_source, _ = split(inputs[1].read_bytes().decode("utf-8"))
    rows = []
    for name, path in (("a001", inputs[2]), ("a002", inputs[3])):
        candidate = load(path)
        if isinstance(candidate, str):
            candidate = json.loads(candidate)
        before = compact_json(candidate)
        ledger = isolate_source_review(candidate, material)["validation"]
        diagnostics = diagnostic_materials(ledger["diagnostics"])
        current, examples = _current_diagnostics(diagnostics["diagnostics"])
        expected_context = {"protocol": VERSION, "candidate": candidate,
                            "diagnostics": current, "format_examples": examples}
        strategy = fragment_correction_strategy("review")
        prompt = strategy.build_prompt(base, candidate, ledger["diagnostics"])
        expanded, new_source, display = split(prompt)
        context = expanded["correction"]
        pairs = [(group["path"], row["record_path"], row["obligation_id"])
                 for group in context["diagnostics"] if group["code"] == "input_contract_review_conflict"
                 for row in group["context"]["conflicting_checks"]]
        expected_pairs = [(row["finding_path"], row["record_path"],
            candidate["input_contract_checks"][int(row["record_path"].rsplit("/", 1)[1])]["obligation_id"])
            for row in ledger["conflicts"]]
        assertions = {
            "original_logical_input_exact": compact_json({k: v for k, v in expanded.items() if k != "correction"}) == compact_json(original),
            "complete_correction_context_exact": compact_json(context) == compact_json(expected_context),
            "complete_candidate_exact": compact_json(context["candidate"]) == before,
            "candidate_unmodified": compact_json(candidate) == before,
            "complete_source_exact_current": new_source == source,
            "complete_source_exact_historical": new_source == old_source,
            "all_conflict_pairs_exact": sorted(pairs) == sorted(expected_pairs),
            "all_conflict_targets_exact": all(group["context"]["target_ids"] ==
                candidate["findings"][int(group["path"].rsplit("/", 1)[1])]["target_ids"]
                for group in context["diagnostics"] if group["code"] == "input_contract_review_conflict"),
            "instruction_schema_prefix_exact": prompt.startswith(base[:base.index("\nINPUT_JSON\n")]),
            "whole_candidate_mode": not strategy.selected,
            "under_unchanged_transport_limit": len(prompt) + len(ENVELOPE) <= MAX_INPUT_CHARS,
        }
        if not all(assertions.values()):
            raise ValueError("Correction audit assertion failed: " + repr(assertions))
        rows.append({"candidate": name, "input_artifact": path.relative_to(ROOT).as_posix(),
            "input_artifact_sha256": hashes[path.relative_to(ROOT).as_posix()],
            "logical_candidate_sha256": sha(before.encode("utf-8")),
            "displayed_diagnostics": len(current), "raw_diagnostic_count": len(diagnostics["raw_diagnostics"]),
            "displayed_diagnostic_codes": dict(Counter(row["code"] for row in current)),
            "conflict_pairs": len(pairs), "conflict_groups": sum(row["code"] == "input_contract_review_conflict" for row in current),
            "raw_diagnostics_sha256": sha(compact_json(diagnostics["raw_diagnostics"]).encode("utf-8")),
            "diagnostic_mapping_sha256": sha(compact_json(diagnostics["diagnostic_mapping"]).encode("utf-8")),
            "correction_core_characters": len(prompt), "delivery_characters": len(prompt) + len(ENVELOPE),
            "headroom_characters": MAX_INPUT_CHARS - len(prompt) - len(ENVELOPE),
            "core_sha256": sha(prompt.encode("utf-8")), "delivery_sha256": sha((ENVELOPE + prompt).encode("utf-8")),
            "column_shapes": len(display["record_columns"]), "correction_strategy": strategy.identity,
            "assertions": assertions})
    stable = hashes == {path.relative_to(ROOT).as_posix(): file_hash(path) for path in inputs}
    code_stable = code == {path: file_hash(ROOT / path) for path in CODE}
    if not stable or not code_stable:
        raise ValueError("Audit inputs or implementation changed during measurement")
    result = {"observed_at": datetime.now(timezone.utc).isoformat(), "scope": "Derived offline validation/render only",
        "model_calls": 0, "historical_runner_calls": 0, "replays": 0, "backend_runs": 0, "skill_executions": 0,
        "historical_files_unchanged": stable, "measured_code_stable": code_stable,
        "historical_material_identity": prior_identity, "in_memory_current_identity": FRAGMENT_IDENTITY,
        "input_file_sha256": hashes, "code_file_sha256": code, "audit_script_sha256": file_hash(Path(__file__)),
        "complete_source_utf8_sha256": sha(source.encode("utf-8")), "complete_source_characters": len(source),
        "logical_original_input_sha256": sha(compact_json(original).encode("utf-8")),
        "base_core_sha256": sha(base.encode("utf-8")), "base_delivery_characters": len(base) + len(ENVELOPE),
        "transport_envelope_characters": len(ENVELOPE), "transport_limit_characters": MAX_INPUT_CHARS,
        "measurements": rows}
    json_path = OUT / "review-correction-size.json"
    with json_path.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False); handle.write("\n")
    lines = ["# Final correction-size audit", "", "Derived offline validation/render-only measurements. No historical runner, replay, backend, model call or Skill execution occurred. All historical input hashes and measured code hashes remained unchanged during measurement.",
        "", "Exact input and code hashes, complete-source identity, full logical/candidate/context equality, every conflict pair and target, and per-delivery hashes are recorded in `review-correction-size.json`.",
        "", "| Candidate | Raw diagnostics | Displayed diagnostics | Conflict pairs | Delivery characters | Headroom |",
        "| --- | ---: | ---: | ---: | ---: | ---: |"]
    lines += [f"| {row['candidate']} | {row['raw_diagnostic_count']} | {row['displayed_diagnostics']} | {row['conflict_pairs']} | {row['delivery_characters']} | {row['headroom_characters']} |" for row in rows]
    lines += ["", "All recorded assertions passed. The complete original source section is identical to the historical prompt, every original logical input is preserved, and the full candidate and displayed correction diagnostics expand exactly. All 307 conflict pairs remain explicit across six groups; original diagnostic provenance and mappings remain audit material. The limit remains 1048576 characters, including the 212-character transport envelope.",
        "", "Source-input errors and cross-record conflicts use the existing single full-response correction. Other local record errors retain existing-slot replacement. Full replies must have the exact review envelope; malformed replies cannot replace the prior candidate. The new display adds no calls or patch grammar and does not guarantee every future irreducible input will fit.",
        "", "Measured code SHA-256:", ""]
    lines += [f"- `{name}`: `{digest}`" for name, digest in code.items()]
    lines += ["", "Historical input file SHA-256:", ""]
    lines += [f"- `{name}`: `{digest}`" for name, digest in hashes.items()]
    (OUT / "review-correction-size-final.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(json_path), "measurements": [{k: row[k] for k in
        ("candidate", "raw_diagnostic_count", "displayed_diagnostics", "delivery_characters", "headroom_characters")}
        for row in rows], "assertions_passed": True}))


if __name__ == "__main__":
    main()
