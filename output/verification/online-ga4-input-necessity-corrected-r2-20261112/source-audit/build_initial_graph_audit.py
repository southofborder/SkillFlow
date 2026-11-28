"""Read saved candidate/source records only; never compile, execute or repair."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[3]
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209"
CALL = RUN / "steps/graph/calls/a001"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    response = read(CALL / "response.json")
    graph = json.loads(response) if isinstance(response, str) else response
    validation = read(CALL / "validation.json")
    inventory_path = BASE / "source-boundary-inventory.json"
    inventory = read(inventory_path)
    source_path = RUN / "source/inputs/package/scripts/src/core/storage.ts"
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    instructions = []
    for block_index, block in enumerate(graph["blocks"]):
        for index, instruction in enumerate(block["instructions"]):
            instructions.append({"candidate_ordinal_ir_id": f"ir_{len(instructions)+1:03d}",
                "block_ref": block["block_ref"],
                "path": f"/blocks/{block_index}/instructions/{index}",
                "opcode": instruction["opcode"],
                "source_span": instruction.get("metadata", {}).get("_source_span", {})})
    errors = []
    for block_index, canonical_ir, canonical_result, line in (
        (47, "ir_100", "result_054", 132), (58, "ir_122", "result_066", 163)
    ):
        block = graph["blocks"][block_index]
        instruction = block["instructions"][0]
        assert instruction["inputs"][2] == instruction["outputs"][0]
        base = f"/blocks/{block_index}/instructions/0"
        errors.append({"code": "RESULT_READ_BEFORE_DEFINITION", "block_ref": block["block_ref"],
            "canonical_ir_id_from_saved_diagnostic": canonical_ir,
            "canonical_result_id_from_saved_diagnostic": canonical_result,
            "input_path": base + "/inputs/2", "output_path": base + "/outputs/0",
            "candidate_instruction": instruction,
            "source": {"file": "scripts/src/core/storage.ts", "start_line": line,
                "end_line": line, "quote": source_lines[line-1]},
            "source_reference_method": "The merge itself has no _source_span; its member and keep blocks cite this filter line, and its predecessor map identifies the false filter path.",
            "diagnosis": "The generated header merge consumes its own freshly defined result as the unchanged reject-branch accumulator. Predecessor metadata does not exempt a same-block read before definition under the immutable result contract.",
            "classification": "generated_representation_error_not_a_source_read_before_definition",
            "actionability": "The saved diagnostic identifies the block, canonical IR and input index. The exact candidate input/output paths above locate the self-reference. A correction must retain accepted members and rejected-member non-change through supported predecessor versions; this audit makes no repair."})
    boundary_groups = {}
    counts = {}
    for name in ("api_sites", "save_sites", "url_loops"):
        rows = []
        for site in inventory[name]:
            source = site["source"]
            matches = [row for row in instructions
                if row["source_span"].get("file", "").removeprefix("skill/") == source["file"]
                and row["source_span"].get("start_line", 10**9) <= source["start_line"]
                <= row["source_span"].get("end_line", -1)]
            rows.append({"site_id": site["id"], "function": site["function"], "source": source,
                "candidate_matches": matches,
                "coverage_status": "candidate_representation_only_not_accepted_or_processed" if matches else "not_cited_in_candidate"})
        boundary_groups[name] = rows
        counts[name] = {"finite_source_denominator": len(rows), "candidate_citation_matches": sum(bool(row["candidate_matches"]) for row in rows),
            "accepted_cfg_coverage": "not_established", "processed_coverage": "not_run"}
    raw_refs = {b["block_ref"] for b in graph["blocks"]}
    missing_raw_endpoints = [{"edge_index": index, **edge} for index, edge in enumerate(graph["edges"])
        if edge["source_block_ref"] not in raw_refs or edge["target_block_ref"] not in raw_refs]
    state = read(RUN / "result.json")
    report = {"identity": "ga4-r2-initial-graph-audit-v1",
        "created_at": datetime.now(timezone.utc).isoformat(), "status": "provisional_initial_candidate",
        "run_directory": str(RUN), "source_sha256": inventory["source_sha256"],
        "artifact_identities": {"response_file_sha256": digest(CALL / "response.json"),
            "saved_response_identity": validation["response_sha256"],
            "saved_candidate_identity": validation["candidate_sha256"],
            "validation_file_sha256": digest(CALL / "validation.json"),
            "source_inventory_file_sha256": digest(inventory_path),
            "storage_source_sha256": digest(source_path)},
        "candidate_counts": {"blocks": len(graph["blocks"]), "edges": len(graph["edges"]), "instructions": len(instructions)},
        "saved_validation_status": validation["status"], "saved_diagnostics": validation["diagnostics"],
        "errors": errors,
        "secondary_endpoint_diagnostic": {"diagnostic_count": 10, "raw_candidate_missing_endpoints": missing_raw_endpoints,
            "explanation": "The raw candidate contains both filter headers and all edge endpoints. compiler.py constructs each BasicBlock separately; validation rejects and omits these two blocks. It then retains edges targeting their assigned IDs, so ControlFlowGraph construction reports ten secondary missing endpoints. These do not establish ten separate missing source blocks.",
            "implementation_evidence": ["src/skillflow/graph/ir/basic_block.py:_dataflow_errors", "src/skillflow/graph/extraction/compiler.py:303-324", "src/skillflow/graph/extraction/compiler.py:350-387"]},
        "finite_candidate_coverage_counts": counts, "finite_candidate_coverage": boundary_groups,
        "observed_run_status": {"status": state.get("status"), "stage": state.get("stage"), "stages": state.get("stages", {})},
        "limitations": ["The initial graph is structurally invalid and is not a selected accepted CFG.",
            "Citation and opcode correspondence does not establish semantic fidelity, interface necessity, source-review acceptance or backend coverage.",
            "No processing, demand, deletion or DOE conclusion is established by this candidate audit.",
            "The permitted structural correction may supersede this candidate; final materials require a separate identity-bound audit.",
            "No compile/propagation/DOE/replay was executed, no model or Skill was called, and no active graph or production file was edited."]}
    for name, value in (("initial-graph-audit.json", report),):
        with (BASE / name).open("x", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    markdown = """# Initial CFG candidate audit (provisional)

The replacement run's first graph response contains **245 blocks, 232 edges and 561 instruction occurrences**. Saved structural validation rejected it. This is a generated-candidate audit, not accepted CFG or propagation coverage.

## Two primary errors

| Saved IR | Exact candidate input | Generated self-reference | Source filter |
| --- | --- | --- | --- |
| `ir_100` | `/blocks/47/instructions/0/inputs/2` | `list_filtered` is both this merge's input and its new output. | `scripts/src/core/storage.ts:132` |
| `ir_122` | `/blocks/58/instructions/0/inputs/2` | `latest_filtered` is both this merge's input and its new output. | `scripts/src/core/storage.ts:163` |

Both merges try to retain an unchanged accumulator when a filter predicate rejects a member. The initial path uses `[]`; the keep path uses the append result; the reject path incorrectly names the merge's own output. The predecessor table does not exempt this same-block read from the immutable result rule. Source `Array.filter` uses ordinary callbacks and contains no corresponding read-before-definition defect. These are generated representation errors.

The saved diagnostics are actionable: they name the block, canonical instruction, result and input index. The table adds exact draft paths. Any correction must preserve member filtering and unchanged state on rejection using supported predecessor versions. This audit does not modify or manually repair the graph.

## Secondary endpoint diagnostics

All raw candidate edge endpoints exist. The compiler separately constructs and validates BasicBlocks; the two invalid filter headers are omitted from the canonical block map, while their edges remain for subsequent graph validation. That produces ten missing-endpoint messages referring to the same two headers. They are consequences of the two primary self-references, not evidence of ten independent absent source blocks.

## Finite candidate coverage

Source-span and opcode inspection found candidate representations for **13/13 API sites, 25/25 saveResult sites and 3/3 explicit URL loops** from the previously frozen source-only inventory. API sites have acquisition/publish opcodes, save sites have `save_result`, and URL-loop sites have header/member relationships. Exact per-site candidate ordinals and references are in the JSON receipt.

These are provisional representation counts. The graph failed validation; no accepted CFG, processing, propagation, demand or DOE coverage follows. Broad source correspondence also cannot establish request/response identity, condition precision, field necessity, review correctness or preservation. The sole structural correction is a later candidate and requires separate verification.

The response identity is `83929cd7a865ec20b67b983debc49074abd891404b387fc123ad31132c41b806`. Exact raw-file and source hashes, instructions, saved diagnostics and source quotes are preserved in `initial-graph-audit.json`. No production, active run or historical artifact was changed, and no model, Skill, compiler, propagation or replay was executed.
"""
    with (BASE / "initial-graph-audit.en.md").open("x", encoding="utf-8") as handle:
        handle.write(markdown)
    print(json.dumps({"candidate_counts": report["candidate_counts"], "coverage": counts,
        "audit_sha256": digest(BASE / "initial-graph-audit.json")}, indent=2))


if __name__ == "__main__":
    main()
