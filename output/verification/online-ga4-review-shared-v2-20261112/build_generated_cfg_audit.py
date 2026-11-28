"""Passive mapping of the current accepted initial CFG to frozen source sites.

This helper reads JSON and source text only. It imports no SkillFlow engine or
Skill code and never executes propagation, models, tests, Skills or replay.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


OUTPUT = Path(__file__).resolve().parent
ROOT = OUTPUT.parents[2]
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242"
REMOTE_IR = [184, 282, 299, 317, 219, 228, 237, 191, 198, 205, 212, 119, 250]
SAVE_IR = [186, 291, 335, 308, 321, 223, 232, 239, 193, 200, 207, 214, 121,
           254, 345, 353, 361, 369, 377, 383, 392, 399, 406, 421, 433]
BUNDLED_REMOTE = {191, 198, 205, 212, 219, 228, 237}
LOOPS = [
    ("report_dimension_map", 54, 103, 107, "scripts/src/api/reports.ts", 95, 95),
    ("report_metric_map", 56, 108, 112, "scripts/src/api/reports.ts", 96, 96),
    ("normalize_urls", 77, 150, 159, "scripts/src/api/bulk-lookup.ts", 64, 75),
    ("bulk_metric_map", 89, 177, 181, "scripts/src/api/bulk-lookup.ts", 179, 179),
    ("request_indexing_batch", 165, 328, 333, "scripts/src/api/indexing.ts", 94, 98),
    ("reindex_with_catch", 189, 413, 420, "scripts/src/index.ts", 305, 314),
    ("inspect_with_catch", 195, 425, 432, "scripts/src/index.ts", 328, 341),
    ("list_json_filter", 220, 475, 481, "scripts/src/core/storage.ts", 131, 132),
    ("list_path_map", 223, 482, 486, "scripts/src/core/storage.ts", 133, 133),
    ("latest_operation_filter", 231, 498, 504, "scripts/src/core/storage.ts", 161, 164),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write_new_or_identical(path, text):
    raw = text.encode("utf-8")
    if path.exists() and path.read_bytes() != raw:
        raise ValueError("Preserve the existing initial-snapshot audit; use a separate final audit: " + str(path))
    if not path.exists():
        path.write_bytes(raw)


def main():
    inventory_path = OUTPUT / "source-audit-inventory.json"
    inventory = read(inventory_path)
    if Path(inventory["run"]).resolve() != RUN.resolve():
        raise ValueError("Source inventory belongs to another run")
    for row in inventory["files"]:
        source_path = RUN / "source/inputs/package" / row["file"].removeprefix("skill/")
        if sha(source_path) != row["raw_sha256"]:
            raise ValueError("Current frozen source no longer matches inventory")
    graph_path = RUN / "graph/initial.json"
    step_path = RUN / "steps/graph/result.json"
    accepted = read(step_path)
    if accepted["accepted_call"] != "calls/a002" or accepted["counts"]["structural_corrections"] != 1:
        raise ValueError("This authored audit is for the accepted initial corrected graph only")
    cfg = read(graph_path)["cfg"]
    indexed = {instruction["id"]: (block, instruction) for block in cfg["blocks"].values()
               for instruction in block["instructions"]}

    def record(number):
        identity = f"ir_{number:03}"
        block, instruction = indexed[identity]
        return {"instruction_id": identity, "block_id": block["block_id"],
                "block_name": block["block_name"], "opcode": instruction["opcode"],
                "inputs": instruction["inputs"], "outputs": instruction["outputs"],
                "metadata": instruction["metadata"],
                "incoming_edges": [edge for edge in cfg["edges"] if edge["target_block_id"] == block["block_id"]]}

    def mapped(source_sites, ids, kind):
        if len(source_sites) != len(ids):
            raise ValueError("Source denominator changed")
        rows = []
        for site, number in zip(source_sites, ids):
            actual = record(number)
            if site["source_text"].strip() not in actual["metadata"].get("script_content", ""):
                raise ValueError("Mapped call text is absent: " + site["site_id"])
            row = {key: value for key, value in site.items() if key != "mapping_status"}
            row.update(actual)
            row["cfg_representation"] = "represented_at_distinct_call_boundary"
            row["backend_reached_status"] = "not_assessed_backend_not_available"
            row["match_basis"] = "Exact physical call text plus the original function context, opcode, receiver/argument identity and result identity; broad source-span overlap alone is not used."
            if kind == "save":
                row["modeling_boundary"] = "saveResult call summary; actual nested storage observation awaits processing"
                row["outputs_discard_path"] = actual["outputs"] == []
            elif number in BUNDLED_REMOTE:
                row["modeling_boundary"] = "Bundled getClient/getPropertyId and remote acquisition; current settings/cache and request details are partly declarative"
            else:
                row["modeling_boundary"] = "Explicit remote-call instruction with actual client/request or client/argument operands"
            if number in {119, 184}:
                row["disambiguation"] = "The identical source call string occurs in both reports.ts and bulk-lookup.ts; report_* versus bulk_* block, request and receiver identities select this physical site."
            rows.append(row)
        return rows

    remote = mapped(inventory["remote_api_sites"], REMOTE_IR, "remote")
    saves = mapped(inventory["save_result_sites"], SAVE_IR, "save")
    loops = []
    for name, head, first, last, file, start, end in LOOPS:
        head_id = f"block_{head:03}"
        if not any(item["metadata"].get("predicate") == "has_member"
                   for item in cfg["blocks"][head_id]["instructions"]):
            raise ValueError("Expected loop header changed: " + name)
        blocks = {indexed[f"ir_{number:03}"][0]["block_id"] for number in range(first, last + 1)}
        loops.append({"name": name, "source_ref": {"file": "skill/" + file, "start_line": start, "end_line": end},
            "head_block": head_id, "instructions": [record(number) for number in range(first, last + 1)],
            "boundary_edges": [edge for edge in cfg["edges"] if edge["source_block_id"] in blocks or edge["target_block_id"] in blocks],
            "status": "explicit_CFG_member_merge_and_backedge_structure; finite processing support and member pairing not yet assessed"})
    findings = [
        {"id": "summary_obligation_only", "kind": "source_workflow_representation_gap",
         "source_refs": [{"file": "skill/SKILL.md", "start_line": 53, "end_line": 64}],
         "cfg_locations": ["/constraints/7"],
         "observation": "The graph repeats the saved-JSON read and Markdown summary obligation in constraint 7, but none of its 511 instructions names or represents summary generation, Markdown, tables/trends/recommendations or a summaries-path write. This omission is outside the 13 remote/25 saveResult denominators.",
         "limit": "This is the initial CFG snapshot, not a final Task/review/DOE judgment. Later selected material must be checked independently."},
        {"id": "bundled_remote_acquisition", "kind": "modeling_abstraction_to_check",
         "instruction_ids": [f"ir_{number:03}" for number in sorted(BUNDLED_REMOTE)],
         "observation": "Four realtime and three metadata call sites combine client-getter/property-getter behavior and the SDK call into a single acquisition. Inputs include an external-resource description of cache/current settings; request field and first-response-element details are in metadata.",
         "limit": "Source sites are represented, but credential provenance, current versus cached settings and interface input necessity require processing contracts; a CFG call label alone cannot establish these facts."},
        {"id": "save_summaries", "kind": "modeling_abstraction_to_check",
         "instruction_ids": [f"ir_{number:03}" for number in SAVE_IR],
         "observation": "All 25 source saveResult call sites are distinct call summaries with discarded returned paths. A separate public saveResult body contains write_json_replace at ir_454 and wrapper construction at ir_453. Their effects must be instantiated at each caller; their mere presence does not establish 25 reached storage observations.",
         "limit": "Do not count an outputless save as unnecessary or claim its wrapper/path provenance is processed before backend records exist."},
        {"id": "unused_original_option_reads", "kind": "source_mismatch_and_observation_check",
         "source_refs": [{"file": "skill/scripts/src/api/reports.ts", "start_line": 77, "end_line": 109},
                         {"file": "skill/references/api-reference.md", "start_line": 30, "end_line": 45}],
         "instruction_ids": ["ir_098", "ir_113", "ir_119"],
         "observation": "ir_098 correctly retains filters/orderBy as unused metadata and copies the original destructuring. Its outputs include only dimensions, metrics, dateRange, limit and save, and the request construction has no filter/sort behavior. The source documents options that its actual request ignores.",
         "limit": "The later assessment must preserve the original read/observation fact and distinguish a source mismatch from a contract error or deletion recommendation; no corrected request is invented here."},
        {"id": "loop_try_regions", "kind": "modeling_abstraction_to_check",
         "instruction_ids": ["ir_331", "ir_416", "ir_419", "ir_428", "ir_431"],
         "observation": "The ordinary indexing batch uses a per-member call and append with uncaught failure. reindexUrls and checkIndexStatus combine per-item logging, API helper invocation and successful append into bounded try-region IR, then separate catch appends. The CFG retains save:false, actual URL/outcome pairing declarations, normal-completion dispatch and separate success/failure backedges.",
         "limit": "A caught failure can precede or follow the remote boundary. The CFG declares this distinction; it does not by itself prove that processing records all may-effects, member correlations or observation order."},
    ]
    if any(any(token in json.dumps(instruction).lower() for token in ("summar", "markdown", "trend", "recommend"))
           for _, instruction in indexed.values()):
        raise ValueError("Summary instruction appeared; revise the authored initial-snapshot finding")
    result = {"identity": "skillflow-current-generated-cfg-source-audit-v1",
        "scope": "Initial accepted pre-source-review CFG snapshot only; not a final selected graph and not backend reached coverage.",
        "run": str(RUN), "artifact": str(graph_path), "graph_file_sha256": sha(graph_path),
        "accepted_step": {"result_path": str(step_path), "result_file_sha256": sha(step_path),
            "identity": accepted["identity"], "accepted_call": accepted["accepted_call"],
            "value_sha256": accepted["value_sha256"], "response_chain_sha256": accepted["response_chain_sha256"],
            "structural_corrections": accepted["counts"]["structural_corrections"]},
        "source_inventory_sha256": sha(inventory_path),
        "counts": {"blocks": len(cfg["blocks"]), "instructions": len(indexed), "edges": len(cfg["edges"]),
            "remote_physical_sites": len(remote), "remote_sites_represented": len(remote), "remote_sites_omitted": 0,
            "saveResult_physical_sites": len(saves), "save_sites_represented": len(saves), "save_sites_omitted": 0,
            "distinct_mapped_instructions": len({row["instruction_id"] for row in remote + saves}),
            "bundled_remote_sites": len(BUNDLED_REMOTE), "explicit_member_loop_headers": len(loops),
            "backend_reached_sites": None},
        "remote_api_mappings": remote, "save_result_mappings": saves, "loop_boundaries": loops,
        "supporting_instruction_records": [record(number) for number in [98, 113, 319, 331, 416, 419, 428, 431, 453, 454]],
        "findings": findings,
        "limitations": ["Only accepted graph/initial.json and its accepted graph-step result were inspected; the invalid first graph response was not read as evidence.",
            "No processing, source review, propagation or DOE artifact was inspected for this audit.",
            "The 38-site denominator excludes narrative summary obligations, setup installs, constructor/SDK internals and other source statements.",
            "If semantic repair replaces the CFG, preserve this audit and create a separate final-selected-graph audit."]}
    path = OUTPUT / "generated-cfg-audit.json"
    write_new_or_identical(path, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    lines = ["# Initial accepted GA4 CFG source-site audit", "", result["scope"], "",
        f"Run: `{RUN.name}`. Accepted graph step: `{accepted['accepted_call']}` after one structural correction. The invalid first response was not used as evidence.", "",
        f"Exact graph artifact: `graph/initial.json`; SHA-256 `{result['graph_file_sha256']}`. Accepted step value identity: `{accepted['value_sha256']}`.", "",
        "The accepted snapshot has 237 blocks, 511 IR and 222 edges. All 13 physical remote client calls and all 25 physical saveResult calls map to 38 distinct IR. Each mapped instruction retains the exact physical call text and an appropriate call/response or save boundary. No source-site omission was found within these two denominators. This is representation coverage only; backend reached coverage is not available.", "",
        "## Physical source-to-IR mapping", "", "| Site | Frozen source | Function | IR | Boundary |", "|---|---|---|---|---|"]
    for row in remote + saves:
        boundary = "saveResult summary" if row["site_id"].startswith("save") else "bundled acquisition" if int(row["instruction_id"][3:]) in BUNDLED_REMOTE else "explicit remote call"
        lines.append(f"| {row['site_id']} | `{row['file']}:{row['start_line']}` | {row['function']} | `{row['instruction_id']}` | {boundary} |")
    lines.extend(["", "## Modeling caveats and omissions outside the site denominator", ""])
    for finding in findings:
        lines.extend([f"### {finding['id']}", "", finding["observation"], "", finding["limit"], ""])
    lines.extend(["## Loop boundaries", "", "| Loop | Source | Header | IR range |", "|---|---|---|---|"])
    for loop in loops:
        citation = loop["source_ref"]
        instructions = loop["instructions"]
        lines.append(f"| {loop['name']} | `{citation['file']}:{citation['start_line']}-{citation['end_line']}` | `{loop['head_block']}` | `{instructions[0]['instruction_id']}`–`{instructions[-1]['instruction_id']}` |")
    lines.extend(["", "All ten headers have explicit has_member control and member/accumulator structure. Exact participating instructions and boundary edges are retained in the JSON audit. Processing support, duplicate-member correlation and per-occurrence effects have not yet been checked.", "",
        "If source review later replaces this CFG, this document remains an initial-snapshot audit. The final selected graph requires a separate audit; its results must not be inferred from these mappings.", ""])
    write_new_or_identical(OUTPUT / "generated-cfg-audit.en.md", "\n".join(lines))
    print(json.dumps({"output": str(path), "graph_file_sha256": result["graph_file_sha256"], "counts": result["counts"]}))


if __name__ == "__main__":
    main()
