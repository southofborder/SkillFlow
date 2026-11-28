"""Passively map the fresh accepted initial CFG to physical source sites."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value) if isinstance(value, str) else value


def main():
    result_path = RUN / "steps/graph/result.json"
    result = read(result_path)
    call = RUN / "steps/graph" / result["accepted_call"]
    validation = read(call / "validation.json")
    assert validation["status"] == "valid"
    wire = read(call / "merged-candidate.json")
    cfg_path = RUN / "graph/initial.json"
    cfg = read(cfg_path)["cfg"]
    inventory = read(OUT / "source-physical-inventory.json")
    compiled_by_name = {b["block_name"]: b for b in cfg["blocks"].values()}
    instructions, span_checks = [], []
    for bi, block in enumerate(wire["blocks"]):
        compiled_block = compiled_by_name[block["block_ref"]]
        assert len(block["instructions"]) == len(compiled_block["instructions"])
        for ii, raw in enumerate(block["instructions"]):
            compiled = compiled_block["instructions"][ii]
            assert raw["opcode"] == compiled["opcode"]
            span = raw.get("metadata", {}).get("_source_span")
            item = {"instruction_id": compiled["id"], "block_id": compiled_block["block_id"],
                "block_name": block["block_ref"], "raw_pointer": f"/blocks/{bi}/instructions/{ii}",
                "cfg_pointer": f"/blocks/{compiled_block['block_id']}/instructions/{ii}",
                "data_source_kind": compiled_block.get("data_source_kind"),
                "source_span": span, "raw_instruction": raw, "compiled_instruction": compiled}
            instructions.append(item)
            if span:
                source = RUN / "source/inputs/package" / span["file"].removeprefix("skill/")
                lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
                expected = "".join(lines[span["start_line"] - 1:span["end_line"]])
                span_checks.append({"instruction_id": compiled["id"], **span,
                    "valid_range": 1 <= span["start_line"] <= span["end_line"] <= len(lines),
                    "compiled_script_matches_source": compiled.get("metadata", {}).get("script_content") == expected})

    def mapping(sites, kind):
        rows = []
        for site in sites:
            matches = [ir for ir in instructions if ir["source_span"]
                and ir["source_span"]["file"] == site["file"]
                and ir["source_span"]["start_line"] <= site["line"] <= ir["source_span"]["end_line"]]
            primary = [ir for ir in matches if (
                ir["data_source_kind"] == "external" and ir["raw_instruction"]["opcode"].startswith("acquire_")
                if kind == "remote" else ir["raw_instruction"]["opcode"] == "call_saveResult" if kind == "save" else True)]
            rows.append({"source_site": site, "span_matches": matches, "primary_instructions": primary,
                "coverage_status": "accepted_cfg_only_processing_and_records_pending"})
        return rows

    remotes = mapping(inventory["remote_api_sites"], "remote")
    saves = mapping(inventory["save_result_sites"], "save")
    iterations = mapping(inventory["iteration_sites"], "iteration")
    storage = mapping(inventory["storage_implementation_sites"], "storage")
    prior = read(RUN / "steps/graph/calls/a001/response.json")
    old = {b["block_ref"]: b for b in prior["blocks"]}
    current = {b["block_ref"]: b for b in wire["blocks"]}
    changed_blocks = [name for name in current if name not in old or old[name] != current[name]]
    removed_spans, changed_spans = [], []
    for name in old.keys() & current.keys():
        for ii, (before, after) in enumerate(zip(old[name]["instructions"], current[name]["instructions"])):
            left = before.get("metadata", {}).get("_source_span")
            right = after.get("metadata", {}).get("_source_span")
            if left and not right:
                removed_spans.append({"block_name": name, "instruction_index": ii, "prior_span": left})
            elif left and right and left != right:
                changed_spans.append({"block_name": name, "instruction_index": ii, "prior_span": left, "accepted_span": right})
    consumers = Counter(x.get("identifier") for ir in instructions for x in ir["raw_instruction"].get("inputs", [])
                        if x.get("type") == "result")
    summary = [ir for ir in instructions if "summar" in json.dumps(ir["raw_instruction"]).lower()]
    heads = [{"block_id": b["block_id"], "block_name": b["block_name"], "instruction_ids": [i["id"] for i in b["instructions"]]}
             for b in cfg["blocks"].values() if b["block_name"].endswith("_head")]
    notes = [
        "This snapshot is the accepted initial CFG from graph a002. It is not yet the final selected CFG after whole-chain source review or semantic repair.",
        "Structural correction changes the initial count from 266 blocks/675 IR/250 edges to 268 blocks/679 IR/252 edges. Two filter skip blocks carry the previous accumulator into distinct result versions, replacing the self-read merge operands. All a001 artifacts and its preliminary audit remain preserved.",
        "The whole-response correction also rewrites metadata/source spans beyond the two failed merges: 107 spans are removed and 27 altered among shared instructions; 372 accepted spans remain, all within the frozen source and matching their compiled script_content. The client-cache initializer additionally gains three explicit external cache-slot operands. These changes require auditing the accepted material itself; they do not mean source files were removed from the complete prompt.",
        "Every physical remote API site has one explicit external acquisition IR with endpoint identity, receiver handle and request operands. This is CFG representation, not proof that processing modeled or propagation reached the network boundary.",
        "Every physical saveResult call has one call_saveResult IR. These carry payload/category/operation/optional extra operands and write-effect prose. They still require actual storage effects at the calling occurrence; a standalone saveResult body or local-tool operation does not establish caller exposure.",
        "Seven explicit iteration heads cover URL normalization, the three URL loops and storage filter/map/filter. The two report name mappings, bulk metric mapping and storage sort remain within broader build/sort IR. Exact member/field and ordering demand depend on later processing contracts.",
        "The accepted graph preserves source acquisition of filters and orderBy as separate outputs, with zero downstream consumers. It also preserves the truthy limit branch. The documented filter/order obligations remain unfulfilled source behavior; SDK zero-limit semantics remain unproved.",
        "The graph constraints/diagnostics acknowledge the Markdown summary workflow and its absent runtime writer, but there is no summary operation IR. Task analysis-summary remains distinct from implemented TypeScript coverage and needs an explicit realization/gap in the later mapping.",
        "Normal and error outcomes for high-level URL loops describe member pairing and external attempts. Their actual request, response and log/storage events must be inspected in the accepted processing and recorded outcomes before claiming boundary coverage.",
    ]
    value = {"kind": "fresh-accepted-initial-cfg-source-audit", "snapshot": "accepted_initial_cfg_before_source_review",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "binding": {"cfg_file": str(cfg_path.relative_to(ROOT)), "cfg_file_sha256": sha(cfg_path),
            "graph_result_file_sha256": sha(result_path), "accepted_call": result["accepted_call"],
            "accepted_response_file_sha256": sha(call / "response.json"), "accepted_merged_candidate_file_sha256": sha(call / "merged-candidate.json"),
            "accepted_validation_file_sha256": sha(call / "validation.json"), "candidate_declared_sha256": validation["candidate_sha256"],
            "source_inventory_sha256": sha(OUT / "source-physical-inventory.json"), "initial_task_file_sha256": sha(RUN / "task/task.json")},
        "counts": {"blocks": len(cfg["blocks"]), "instructions": len(instructions), "edges": len(cfg["edges"]),
            "remote_sites": len(remotes), "remote_sites_with_exactly_one_acquisition_ir": sum(len(r["primary_instructions"]) == 1 for r in remotes),
            "save_sites": len(saves), "save_sites_with_exactly_one_call_ir": sum(len(r["primary_instructions"]) == 1 for r in saves),
            "iteration_sites_with_span_matches": sum(bool(r["span_matches"]) for r in iterations), "explicit_iteration_heads": len(heads),
            "summary_operation_ir": len(summary), "source_span_checks": len(span_checks),
            "invalid_source_span_ranges": sum(not r["valid_range"] for r in span_checks),
            "compiled_script_source_mismatches": sum(not r["compiled_script_matches_source"] for r in span_checks)},
        "correction_changed_blocks": changed_blocks,
        "correction_removed_source_spans": sorted(removed_spans, key=lambda r: (r["block_name"], r["instruction_index"])),
        "correction_changed_source_spans": sorted(changed_spans, key=lambda r: (r["block_name"], r["instruction_index"])),
        "source_span_checks": span_checks,
        "remote_site_mapping": remotes, "save_site_mapping": saves, "iteration_site_mapping": iterations,
        "storage_implementation_mapping": storage, "explicit_iteration_heads": heads,
        "report_option_consumers": {name: consumers[name] for name in ("report_filters", "report_order", "report_limit")},
        "summary_operations": summary,
        "summary_related_generator_diagnostics": [d for d in wire.get("diagnostics", []) if "summar" in d.lower()],
        "audit_notes": notes,
        "limitations": ["No compiler, validator, solver, propagation, DOE, model or replay was invoked by this passive audit.",
            "Valid source spans and accepted CFG structure do not prove correct source semantics, dynamic reachability or actual network/storage effects.",
            "Rebind and compare the final selected CFG and annotation after whole-chain review; do not silently replace this initial snapshot."]}
    (OUT / "cfg-accepted-initial-audit.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Accepted initial CFG: source audit", "", "The accepted a002 graph contains 268 blocks, 679 IR and 252 edges. Processing is not yet audited in this snapshot.", "",
        "Bound graph/initial.json SHA256: " + value["binding"]["cfg_file_sha256"], "", *["- " + n for n in notes], "",
        "## Remote site mapping", ""]
    lines += [f"- {r['source_site']['file']}:{r['source_site']['line']} → " + ", ".join(i["instruction_id"] for i in r["primary_instructions"]) for r in remotes]
    lines += ["", "## Save site mapping", ""]
    lines += [f"- {r['source_site']['file']}:{r['source_site']['line']} → " + ", ".join(i["instruction_id"] for i in r["primary_instructions"]) for r in saves]
    lines += ["", "Source-span checks: " + json.dumps({k: value["counts"][k] for k in ("source_span_checks", "invalid_source_span_ranges", "compiled_script_source_mismatches")}), "", *value["limitations"]]
    (OUT / "cfg-accepted-initial-audit.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(value["counts"]))
    print("Changed blocks: " + ", ".join(changed_blocks))


if __name__ == "__main__":
    main()
