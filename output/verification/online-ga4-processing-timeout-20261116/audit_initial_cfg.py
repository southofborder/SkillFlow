"""Passive saved-graph/source comparison, without importing SkillFlow."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-processing-shared-high-20261116-225414"
READS = {}


def read(path):
    raw = path.read_bytes()
    READS[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
    return raw.decode("utf-8")


def load(path):
    return json.loads(read(path))


def response(attempt):
    value = load(RUN / "steps/graph/calls" / attempt / "response.json")
    return json.loads(value) if isinstance(value, str) else value


def simple(ir, block, raw):
    return {"instruction_id": ir["id"], "block_id": block["block_id"], "block_name": block["block_name"],
            "opcode": ir["opcode"], "source_span": raw.get("metadata", {}).get("_source_span"),
            "inputs": ir["inputs"], "outputs": ir["outputs"],
            "metadata": {key: value for key, value in ir["metadata"].items() if key != "script_content"}}


def main():
    protocol = load(RUN / "run-protocol.json")
    inventory = load(OUT / "source-physical-inventory.json")
    first, accepted = response("a001"), response("a002")
    cfg = load(RUN / "graph/initial.json")["cfg"]
    step_result = load(RUN / "steps/graph/result.json")
    first_validation = load(RUN / "steps/graph/calls/a001/validation.json")
    final_validation = load(RUN / "steps/graph/calls/a002/validation.json")
    step_value = load(RUN / "steps/graph/value.json")
    assert step_result["accepted_call"] == "calls/a002" and final_validation["status"] == "valid"
    assert len(accepted["blocks"]) == len(cfg["blocks"]) == len(step_value["blocks"])
    source_lines = {}
    for entry in inventory["files"]:
        path = RUN / "source/inputs/package" / entry["path"]
        text = read(path)
        assert READS[path.relative_to(ROOT).as_posix()] == entry["sha256"]
        source_lines["skill/" + entry["path"]] = text.splitlines(keepends=True)
    records, copied_spans = [], 0
    for raw_block, block, projected_block in zip(accepted["blocks"], cfg["blocks"].values(), step_value["blocks"]):
        assert raw_block["block_ref"] == projected_block["block_ref"]
        assert len(raw_block["instructions"]) == len(block["instructions"]) == len(projected_block["instructions"])
        for raw, ir, projected in zip(raw_block["instructions"], block["instructions"], projected_block["instructions"]):
            assert raw["opcode"] == ir["opcode"] == projected["opcode"]
            assert ir["draft_instruction_id"] == projected["instruction_ref"]
            span = raw.get("metadata", {}).get("_source_span")
            if span is not None:
                lines = source_lines[span["file"]]
                assert 1 <= span["start_line"] <= span["end_line"] <= len(lines)
                expected = "".join(lines[span["start_line"] - 1:span["end_line"]])
                assert ir["metadata"]["script_content"] == expected
                copied_spans += 1
            records.append(simple(ir, block, raw))

    def covering(site):
        return [row for row in records if row["source_span"]
                and row["source_span"]["file"] == site["file"]
                and row["source_span"]["start_line"] <= site["line"] <= row["source_span"]["end_line"]]

    remote_opcodes = {"acquire_report_response", "acquire_bulk_report", "acquire_realtime_report",
                      "acquire_property_metadata", "acquire_search_analytics", "publish_url_notification",
                      "acquire_url_inspection"}
    remote_sites = []
    for site in inventory["sites"]["remote_api"]:
        mapped = [row for row in covering(site) if row["opcode"] in remote_opcodes]
        assert len(mapped) == 1
        record = mapped[0]
        explicit = record["opcode"] not in {"acquire_realtime_report", "acquire_property_metadata"}
        remote_sites.append({**site, "generated_instruction": record,
            "boundary_representation": "explicit_receiver_and_request_inputs" if explicit else "composite_acquisition_effect_text",
            "qualification": ("The source call has a generated receiver result and request/body operands; actual processing still requires inspection."
                              if explicit else "The generated operands contain an external API resource and optional literal fields. getClient/getPropertyId are described in metadata, not explicit incoming result operands at this boundary. Processing must establish those internal reads and receiver/routing relationships.")})
    save_sites = []
    for site in inventory["sites"]["save_result"]:
        mapped = [row for row in covering(site) if row["opcode"] == "call_saveResult"]
        assert len(mapped) == 1
        save_sites.append({**site, "generated_instruction": mapped[0],
            "qualification": "The call-site summary is present. No caller-to-filesystem propagation coverage is inferred from the name, citation or independent saveResult implementation."})
    iteration_sites = []
    for site in inventory["sites"]["iteration"]:
        mapped = covering(site)
        assert mapped
        if any(row["opcode"] == "member" for row in mapped) or (site["file"].endswith("storage.ts") and site["line"] == 133):
            representation = "explicit_member_loop_or_combined_filter_map"
        else:
            representation = "opaque_pure_array_transform"
        iteration_sites.append({**site, "source_span_covering_instructions": mapped, "representation": representation})

    first_blocks = {row["block_ref"]: row for row in first["blocks"]}
    accepted_blocks = {row["block_ref"]: row for row in accepted["blocks"]}
    filter_repairs = []
    for prefix, head_id, retained_id in (("list_filter", "ir_479", "ir_482"), ("latest_filter", "ir_498", "ir_501")):
        before = first_blocks[prefix + "_head"]["instructions"][0]
        after = accepted_blocks[prefix + "_head"]["instructions"][0]
        retain = next(row for row in accepted_blocks[prefix + "_body"]["instructions"] if row["opcode"] == "retain_filter_accumulator")
        edges = [edge for edge in accepted["edges"] if edge["source_block_ref"].startswith(prefix)
                 or edge["target_block_ref"].startswith(prefix)]
        assert before["inputs"][1]["identifier"] == before["outputs"][0]["identifier"]
        assert after["inputs"][1]["identifier"] == retain["outputs"][0]["identifier"]
        assert retain["inputs"][0]["identifier"] == after["outputs"][0]["identifier"]
        assert any(edge["source_block_ref"] == prefix + "_body" and edge["target_block_ref"] == prefix + "_head"
                   and edge.get("condition_text") == "false" for edge in edges)
        assert any(edge["source_block_ref"] == prefix + "_keep" and edge["target_block_ref"] == prefix + "_head" for edge in edges)
        filter_repairs.append({"loop": prefix, "head_instruction": head_id, "retained_value_instruction": retained_id,
            "before_merge": before, "after_merge": after, "new_retained_value": retain, "edges": edges,
            "semantic_assessment": "The rejected-member backedge now carries a separately produced unchanged accumulator; the accepted-member path still appends its member, and initial/retained/updated versions feed the head merge. This matches source filter retention semantics at the generated-graph level. Runtime summary support, repeated-member pairing and processing validation remain unestablished here."})

    selected = (RUN / "selection.json").is_file()
    run_result_bytes = (RUN / "result.json").read_bytes()
    run_result = json.loads(run_result_bytes)
    questions = [
        {"id": "composite_remote_boundaries", "ir_ids": [row["generated_instruction"]["instruction_id"] for row in remote_sites if row["boundary_representation"] == "composite_acquisition_effect_text"],
         "observation": "Seven remote sites have getClient/getPropertyId only inside effect descriptions. Explicit graph operands do not establish authentication, cached receiver identity or property routing at those sites.",
         "next_evidence": "Inspect actual processing acquisition/read/call operations, source-reviewed interface scope, and eventual propagation records. Do not count these seven as verified source-faithful direct boundaries yet."},
        {"id": "read_but_unforwarded_fields", "ir_ids": ["ir_089", "ir_093", "ir_099"],
         "observation": "The request omits filters/orderBy consistently with source, and unpack_report_options names them in unused_destructured_fields metadata. They are not separate graph outputs.",
         "next_evidence": "Check whether processing preserves their actual source reads/observations and whether task-relative demand distinguishes implementation behavior from documented filters/orderBy functionality. No deletability verdict is established by this graph."},
        {"id": "caller_storage_bridge", "ir_ids": [row["generated_instruction"]["instruction_id"] for row in save_sites] + ["ir_452", "ir_453"],
         "observation": "All 25 saveResult call summaries exist; a separate saveResult entry serializes metadata/data at ir_452 and writes filepath/JSON at ir_453. Its own arguments are independently acquired.",
         "next_evidence": "Check each caller's transfer to actual filesystem payload and receiver through processing, not name-based matching. Confirm metadata, conditional extraInfo, directory existence and returned filepath requirements."},
        {"id": "summary_provenance", "ir_ids": ["ir_517", "ir_519", "ir_520"],
         "observation": "The natural-language summary has explicit generated read/compose/write IR. Its read metadata explicitly says invocation-to-file provenance remains unresolved; write filename/writer are unspecified.",
         "next_evidence": "Retain this specific limitation and verify Task/mapping evidence. Presence of summary IR does not connect every earlier save to this read."},
        {"id": "loop_and_error_pairing", "ir_ids": ["ir_479", "ir_482", "ir_498", "ir_501", "ir_321", "ir_409", "ir_425"],
         "observation": "Filter loops now have valid retained versions, while requestIndexing and high-level loops still use completion summaries with explicit success/failure alternatives.",
         "next_evidence": "Verify supported processing loop summaries, per-member correlation, save=false behavior and error-path observations. A saved CFG validation pass does not establish backend loop coverage."},
    ]
    result = {
        "version": "fresh-ga4-initial-cfg-passive-audit-v1", "observed_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(RUN), "implementation_sha256": protocol["implementation_sha256"],
        "accepted_initial_graph": "graph/initial.json", "accepted_call": step_result["accepted_call"],
        "final_bundle_selection_exists_at_observation": selected,
        "counts": {"blocks": len(cfg["blocks"]), "instructions": len(records), "edges": len(cfg["edges"]),
                   "source_span_copies_exact": copied_spans, "remote_site_representations": len(remote_sites),
                   "remote_with_explicit_receiver_and_request_operands": sum(row["boundary_representation"] == "explicit_receiver_and_request_inputs" for row in remote_sites),
                   "remote_composite_effect_summaries": sum(row["boundary_representation"] == "composite_acquisition_effect_text" for row in remote_sites),
                   "save_result_site_representations": len(save_sites), "iteration_source_sites_represented": len(iteration_sites),
                   "explicit_member_loop_site_representations": sum(row["representation"] == "explicit_member_loop_or_combined_filter_map" for row in iteration_sites),
                   "opaque_pure_array_transform_site_representations": sum(row["representation"] == "opaque_pure_array_transform" for row in iteration_sites),
                   "opcode_counts": dict(Counter(row["opcode"] for row in records))},
        "correction": {"first_blocks": len(first["blocks"]), "first_instructions": sum(len(row["instructions"]) for row in first["blocks"]),
            "first_edges": len(first["edges"]), "initial_diagnostics": first_validation["diagnostics"],
            "saved_final_validation_status": final_validation["status"], "same_block_refs": set(first_blocks) == set(accepted_blocks),
            "raw_changed_blocks": sum(first_blocks[key] != accepted_blocks[key] for key in first_blocks),
            "edge_array_exactly_equal": first["edges"] == accepted["edges"], "filter_repairs": filter_repairs},
        "remote_sites": remote_sites, "save_result_sites": save_sites, "iteration_sites": iteration_sites,
        "storage_and_summary_instructions": [row for row in records if row["opcode"] in {
            "serialize_saved_result", "write_file", "read_saved_json_for_summary", "compose_markdown", "write_markdown_summary"}],
        "pending_source_questions": questions,
        "run_observation": {"result_sha256": hashlib.sha256(run_result_bytes).hexdigest(), "status": run_result.get("status"),
                            "stage": run_result.get("stage"), "selected_annotation": run_result.get("selected_annotation")},
        "limitations": [
            "This is an accepted initial generated graph, not a final selected annotation bundle.",
            "Generated source-site representation is not source-faithful processing, processed/reached propagation coverage or a field-necessity/DOE result.",
            "Existing saved validation statuses were inspected; no validator, renderer, Skill, model, backend or replay was run.",
            "The graph correction changed 110 raw block objects, including explanatory text; only the two reported filter repairs and listed source boundaries are specifically assessed here."
        ], "bound_artifact_sha256": READS}
    (OUT / "initial-cfg-source-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Initial GA4 CFG: generated representation audit", "",
             f"Run: `{RUN.name}`. The saved graph step accepted `calls/a002` after one structural correction.", "",
             "The accepted initial graph contains **237 blocks, 521 IR and 217 edges**. It represents all **13 remote call sites**, all **25 saveResult caller sites**, and all **11 loop/map/filter/sort source sites**. These are generated representations, not processing or propagation coverage. At this observation no final selection.json exists.", "",
             f"All {copied_spans} supplied source-span copies match the frozen source bytes exactly. Source citations support location, not automatic semantic correctness.", "",
             "## The filter correction", "",
             "The first candidate had 519 IR. Its two filter-head merges read their own output as the rejected-member incoming value, producing two RESULT_READ_BEFORE_DEFINITION errors and secondary missing-edge-endpoint diagnostics. The corrected graph adds ir_482 and ir_501, each retaining the incoming accumulator under a separate result identity. The false branch carries that retained value to the head; the true branch still appends a matching member. Initial, retained and updated values remain separate incoming versions. The 217-edge array is unchanged.", "",
             "This fixes the reported source filter state-flow error without removing the filter branches. It does not establish that processing can encode both loops or that the backend will complete them. The whole replacement also changed 110 raw block objects, including metadata wording; the saved validator pass does not certify every semantic change.", "",
             "## Remote boundary detail", "", "| Source | IR | Representation |", "|---|---|---|"]
    for row in remote_sites:
        lines.append(f"| {row['file']}:{row['line']} | {row['generated_instruction']['instruction_id']} | {row['boundary_representation']} |")
    lines += ["", "Six remote IR expose receiver results plus request/body operands. Four realtime and three metadata acquisitions instead describe getClient/getPropertyId inside effect text, with only external API resource/literal fields as direct operands. Those seven sites are represented, but their credential, cached-handle and property dependencies need processing evidence before they qualify as complete source-faithful boundaries.", "",
              "## Storage, fields and summary", "",
              "All 25 saveResult calls have their own source-matched IR. The independent saveResult implementation includes wrapped serialization (ir_452) and the filesystem write (ir_453). Caller-to-writer transfer still requires inspection of processing and propagation; shared names and citations are insufficient.", "",
              "ir_089 records filters/orderBy only in unused_destructured_fields metadata and does not produce separate values for them. The outgoing request correctly omits them as the source does. The next audit must check preservation of actual read observations and the discrepancy with documented filtering/sorting behavior; this graph alone establishes no deletion verdict.", "",
              "The required saved-JSON read, Markdown composition and write appear as ir_517/519/520. The graph explicitly retains unresolved invocation-to-file provenance and an unspecified summary filename/writer. These gaps must remain specific instead of being replaced with an invented save/read association.", "",
              "## Iteration representation", "", "| Source | Form | Generated instruction IDs with source-span coverage |", "|---|---|---|"]
    for row in iteration_sites:
        lines.append(f"| {row['file']}:{row['line']} | {row['representation']} | {', '.join(item['instruction_id'] for item in row['source_span_covering_instructions'])} |")
    lines += ["", "Seven iteration source sites use explicit member loops or the combined filter/map representation. Three name-to-object maps and one sort remain opaque pure-array transformations. No iteration completion, ordering, pairing or demand claim is inferred from that classification.", "",
              "No Skill, model, validator, renderer, backend or replay was executed for this passive audit. Further changes should be proposed only after the new processing/source-review and final selected results are available."]
    (OUT / "initial-cfg-source-audit.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result["counts"].items() if key != "opcode_counts"}))


if __name__ == "__main__":
    main()
