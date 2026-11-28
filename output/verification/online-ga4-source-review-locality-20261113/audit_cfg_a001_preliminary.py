"""Inspect the rejected fresh graph candidate without compiling or executing it."""
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


def main():
    call = RUN / "steps/graph/calls/a001"
    response_path = call / "response.json"
    candidate = json.loads(response_path.read_text(encoding="utf-8"))
    if isinstance(candidate, str):
        candidate = json.loads(candidate)
    validation = json.loads((call / "validation.json").read_text(encoding="utf-8"))
    inventory = json.loads((OUT / "source-physical-inventory.json").read_text(encoding="utf-8"))
    instructions = [{"block_ref": block["block_ref"], "pointer": f"/blocks/{bi}/instructions/{ii}",
        "data_source_kind": block.get("data_source_kind"), **ir}
        for bi, block in enumerate(candidate["blocks"]) for ii, ir in enumerate(block["instructions"])]

    def mapping(sites, kind):
        result = []
        for site in sites:
            matches = []
            for ir in instructions:
                span = ir.get("metadata", {}).get("_source_span", {})
                if span.get("file") == site["file"] and span.get("start_line", 999999) <= site["line"] <= span.get("end_line", -1):
                    matches.append(ir)
            primary = [ir for ir in matches if (
                ir["data_source_kind"] == "external" and ir["opcode"].startswith("acquire_")
                if kind == "remote" else ir["opcode"] == "call_saveResult" if kind == "save" else True)]
            result.append({"source_site": site, "span_matches": matches, "primary_candidates": primary,
                           "status": "raw_candidate_only_unaccepted"})
        return result

    remote = mapping(inventory["remote_api_sites"], "remote")
    saves = mapping(inventory["save_result_sites"], "save")
    loops = mapping(inventory["iteration_sites"], "iteration")
    consumers = Counter(operand.get("identifier") for ir in instructions for operand in ir.get("inputs", [])
                        if operand.get("type") == "result")
    summary_operations = [ir for ir in instructions if "summar" in json.dumps(ir).lower()]
    notes = [
        "This is a rejected raw response, not the selected CFG. Structural correction a002 remains authoritative only if it passes and is selected.",
        "All 13 physical remote API sites have explicit external acquisition candidates with client handle and request operands; processing must still establish actual request/response and network boundary semantics.",
        "All 25 saveResult sites are represented by call_saveResult instructions with source spans and write-effect descriptions. No caller storage exposure is established until processing/propagation connect these calls to actual write behavior.",
        "The raw runReport acquisition keeps all seven input options including filters and orderBy. Their result names report_filters and report_order have zero consumers in this candidate, preserving actual acquisition while reflecting omission from the outgoing request.",
        "No instruction in this raw candidate represents the Markdown summary workflow. Task requires analysis-summary, so the final mapping/review must account for this omission or retain a concrete gap.",
        "The two direct structural failures are self-read merge outputs in list_filter_head and latest_filter_head. The recorded endpoint failures follow from those rejected block definitions; this passive audit does not independently validate the rest of the graph.",
        "Loop/member calls retain opaque caller boundaries, including normal/error outcomes. Their metadata describes network effects and per-member save=false, but metadata and processed-IR counts alone do not establish actual boundary coverage.",
    ]
    value = {"kind": "fresh-raw-cfg-preliminary-source-audit", "snapshot": "rejected_graph_a001_not_selected",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "binding": {"response_file": str(response_path.relative_to(ROOT)), "response_file_sha256": sha(response_path),
            "validation_file_sha256": sha(call / "validation.json"), "validation_status": validation["status"],
            "candidate_declared_sha256": validation["candidate_sha256"],
            "source_inventory_sha256": sha(OUT / "source-physical-inventory.json")},
        "counts": {"blocks": len(candidate["blocks"]), "instructions": len(instructions), "edges": len(candidate.get("edges", [])),
            "remote_sites_with_primary_candidate": sum(bool(r["primary_candidates"]) for r in remote),
            "save_sites_with_primary_candidate": sum(bool(r["primary_candidates"]) for r in saves),
            "source_iteration_sites_with_span_match": sum(bool(r["span_matches"]) for r in loops),
            "summary_operation_candidates": len(summary_operations)},
        "structural_diagnostics": validation["diagnostics"], "remote_site_mapping": remote,
        "save_site_mapping": saves, "iteration_site_mapping": loops,
        "explicit_head_blocks": [b["block_ref"] for b in candidate["blocks"] if b["block_ref"].endswith("_head")],
        "report_option_consumers": {name: consumers[name] for name in ("report_filters", "report_order", "report_limit")},
        "summary_operations": summary_operations,
        "summary_related_generator_diagnostics": [d for d in candidate.get("diagnostics", []) if "summar" in d.lower()],
        "audit_notes": notes,
        "limitations": ["No graph compiler, validator, propagation, demand solver, DOE or replay was invoked by this helper.",
                        "Source-span matches and metadata are preliminary traceability only, not semantic correctness, reachability or coverage proof."]}
    (OUT / "cfg-a001-preliminary.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Rejected graph a001: preliminary source mapping", "", "This audit is explicitly unselected and preliminary.", "",
        json.dumps(value["counts"]), "", *["- " + s for s in notes], "", "## Recorded structural failures", ""]
    lines += ["- " + d["code"] + " at " + d["path"] + ": " + d["message"] for d in validation["diagnostics"]]
    lines += ["", "Response file SHA256: " + value["binding"]["response_file_sha256"],
              "Validation file SHA256: " + value["binding"]["validation_file_sha256"], "", *value["limitations"]]
    (OUT / "cfg-a001-preliminary.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(value["counts"]))


if __name__ == "__main__":
    main()
