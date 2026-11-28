"""Inspect saved selected CFG/source only, without compiling or executing it."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[3]
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def core(block):
    return [(i["opcode"], i.get("inputs", []), i.get("outputs", [])) for i in block["instructions"]]


def main():
    stage = RUN / "steps/graph"
    result = read(stage / "result.json")
    assert result["accepted_call"] == "calls/a002"
    validation = read(stage / "calls/a002/validation.json")
    assert validation["status"] == "valid"
    raw = read(stage / "calls/a002/merged-candidate.json")
    wire = read(stage / result["value_file"])
    canonical = read(RUN / "graph/initial.json")["cfg"]
    previous = read(stage / "calls/a001/response.json")
    previous = json.loads(previous) if isinstance(previous, str) else previous
    inventory = read(BASE / "source-boundary-inventory.json")
    blocks = {b["block_ref"]: b for b in raw["blocks"]}
    previous_blocks = {b["block_ref"]: b for b in previous["blocks"]}
    changed = [name for name, block in blocks.items() if core(block) != core(previous_blocks[name])]
    metadata_changed = [name for name, block in blocks.items() if block != previous_blocks[name]]
    instructions = []
    for bi, (draft, normalized) in enumerate(zip(raw["blocks"], wire["blocks"])):
        assert draft["block_ref"] == normalized["block_ref"]
        block_id = f"block_{bi+1:03d}"
        compiled = canonical["blocks"][block_id]
        assert len(draft["instructions"]) == len(normalized["instructions"]) == len(compiled["instructions"])
        for ii, (di, ni, ci) in enumerate(zip(draft["instructions"], normalized["instructions"], compiled["instructions"])):
            assert di["opcode"] == ni["opcode"] == ci["opcode"]
            assert ni["instruction_ref"] == ci["draft_instruction_id"]
            for field in ("inputs", "outputs"):
                assert di.get(field, []) == ni.get(field, [])
                assert len(di.get(field, [])) == len(ci[field])
                for a, b in zip(di.get(field, []), ci[field]):
                    assert a["type"] == b["type"]
                    if a["type"] == "result":
                        assert a["identifier"] == b["semantic_name"]
                    elif a["type"] == "literal":
                        assert a.get("literal_value") == b.get("literal_value")
                    else:
                        assert a["identifier"] == b["identifier"]
            instructions.append({"canonical_block_id": block_id, "canonical_ir_id": ci["id"],
                "block_ref": draft["block_ref"], "draft_path": f"/blocks/{bi}/instructions/{ii}",
                "instruction": di, "source_span": di.get("metadata", {}).get("_source_span", {})})
    edge_pairs = {(e["source_block_ref"], e["target_block_ref"], e.get("condition_text")) for e in raw["edges"]}
    expected_api = {
        "API-01": ("bulk_api", "acquire_ga_report_first_response", "The bulk request preserves property, date range, pagePath/pageTitle dimensions, metric names and normalized URL filter; the SDK's first response is bound to bulk_response."),
        "API-02": ("update_api", "publish_and_acquire_notification_response", "The indexing client, input URL and URL_UPDATED literal are bound to the publication, with requestBody URL/type mapping and its own response."),
        "API-03": ("remove_api", "publish_and_acquire_notification_response", "The indexing client, input URL and URL_DELETED literal are bound to the publication, with requestBody URL/type mapping and its own response."),
        "API-04": ("inspect_api", "acquire_inspection_result", "The Search Console client receives the input URL and separately acquired site URL; response.data.inspectionResult is the retained result."),
        "API-05": ("md_dimensions_api", "acquire_metadata_first_response", "The metadata name derives from the property and /metadata; the first response is subsequently projected to dimensions with [] fallback."),
        "API-06": ("md_metrics_api", "acquire_metadata_first_response", "The metadata name derives from the property and /metadata; the first response is subsequently projected to metrics with [] fallback."),
        "API-07": ("md_full_api", "acquire_metadata_first_response", "The same metadata acquisition has a distinct response that is saved/returned whole by getPropertyMetadata."),
        "API-08": ("active_api", "acquire_realtime_first_response", "Property plus unifiedScreenName/activeUsers literals match getActiveUsers; its own first response is retained."),
        "API-09": ("rt_events_api", "acquire_realtime_first_response", "Property plus eventName/eventCount literals match getRealtimeEvents; its own first response is retained."),
        "API-10": ("rt_pages_api", "acquire_realtime_first_response", "Property plus unifiedScreenName/screenPageViews literals match getRealtimePages; its own first response is retained."),
        "API-11": ("rt_sources_api", "acquire_realtime_first_response", "Property plus firstUserSource/firstUserMedium and activeUsers match getRealtimeSources; its own first response is retained."),
        "API-12": ("report_api", "acquire_ga_report_first_response", "The report client and constructed request acquire the first report response. dimensions/metrics are mapped, limit remains truthy-conditional, and the actually unused filters/orderBy fields are not inserted into the request."),
        "API-13": ("search_api", "acquire_search_response_data", "The Search Console client and constructed siteUrl/requestBody request acquire response.data, preserving start/end dates, dimensions, rowLimit and startRow.")}
    api_rows = []
    for site in inventory["api_sites"]:
        block_ref, opcode, explanation = expected_api[site["id"]]
        matches = [row for row in instructions if row["block_ref"] == block_ref and row["instruction"]["opcode"] == opcode]
        assert len(matches) == 1
        row = matches[0]
        span = row["source_span"]
        assert span["file"].removeprefix("skill/") == site["source"]["file"]
        assert span["start_line"] <= site["source"]["start_line"] <= span["end_line"]
        assert row["instruction"].get("outputs") and blocks[block_ref].get("data_source_kind") == "external"
        api_rows.append({"site_id": site["id"], "source": site["source"], "representation": row,
            "assessment": "source_supported_acquisition_and_response_skeleton", "reason": explanation,
            "remaining_check": "Processing must bind receiver/request/response and interface-required input scopes; argument presence alone is not necessity evidence."})
    save_rows = []
    for site in inventory["save_sites"]:
        source = site["source"]
        rows = [row for row in instructions if row["instruction"]["opcode"] == "save_result"
            and row["source_span"].get("file", "").removeprefix("skill/") == source["file"]
            and row["source_span"].get("start_line", 10**9) <= source["start_line"] <= row["source_span"].get("end_line", -1)]
        assert len(rows) == 1 and not rows[0]["instruction"].get("outputs")
        save_rows.append({"site_id": site["id"], "function": site["function"], "source": source,
            "representation": rows[0], "incoming_edges": [edge for edge in raw["edges"] if edge["target_block_ref"] == rows[0]["block_ref"]],
            "assessment": "source_supported_call_payload_category_operation_and_discarded_return",
            "reason": "The call has its actual data result and category/operation/optional extra operands. Source callers ignore the filepath return and this IR declares no output. Optional save branches remain in the surrounding CFG; high-level aggregate saves remain unconditional.",
            "remaining_check": "Processing and Task correspondence must retain required side effects, apply actual save controls and instantiate each call's settings/clock/file identity."})
    loop_rows = []
    for site, prefix, back in zip(inventory["url_loops"], ("batch", "reindex", "status"), ("batch_member", "reindex_append", "status_append")):
        head, member = prefix + "_head", prefix + "_member"
        assert (head, member, "true") in edge_pairs and (back, head, None) in edge_pairs
        assert blocks[head]["instructions"][-1]["metadata"]["predicate"] == "has_member"
        assert blocks[member]["instructions"][0]["opcode"] == "member"
        loop_rows.append({"site_id": site["id"], "function": site["function"], "source": site["source"],
            "header": blocks[head], "member_body": blocks[member], "backedge_block": blocks[back],
            "edges": [edge for edge in raw["edges"] if edge["source_block_ref"].startswith(prefix + "_")],
            "assessment": "explicit_collection_member_call_accumulation_and_backedge_skeleton",
            "reason": "The collection header tests has_member, the body takes one corresponding URL, the child call has save:false, and results are appended before the backedge. Batch failures propagate; reindex/status retain selected success or catch rows, followed by an aggregate save.",
            "remaining_check": "Processing must preserve occurrence/cardinality/order, exceptions, condition scope and row/URL pairing in its finite loop summary; explicit CFG structure alone does not prove that."})
    corrections = []
    for prefix in ("list", "latest"):
        head, member = prefix + "_filter_head", prefix + "_filter_member"
        carry = blocks[member]["instructions"][1]
        merged_input = blocks[head]["instructions"][0]["inputs"][2]
        assert carry["opcode"] == "carry_filter_accumulator" and carry["outputs"][0] == merged_input
        assert carry["inputs"][0] == blocks[head]["instructions"][0]["outputs"][0]
        assert (member, head, "false") in edge_pairs
        corrections.append({"header": head, "member": member, "carry_instruction": carry,
            "header_merge": blocks[head]["instructions"][0],
            "assessment": "self_reference_removed_using_predecessor_result",
            "remaining_check": "The processing binding should be a direct identity alias of the current accumulator, with no invented content transform or observation. Keep and skip must stay predecessor-scoped."})
    observed = read(RUN / "result.json")
    report = {"identity": "ga4-r2-selected-initial-cfg-audit-v1", "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "selected_initial_cfg_downstream_pending", "run_directory": str(RUN),
        "source_sha256": inventory["source_sha256"],
        "selected_paths": {"stage_result": str(stage / "result.json"), "wire_value": str(stage / result["value_file"]),
            "accepted_candidate": str(stage / "calls/a002/merged-candidate.json"), "canonical_cfg": str(RUN / "graph/initial.json")},
        "identities": {"saved_wire_value_identity": result["value_sha256"], "saved_response_identity": validation["response_sha256"],
            "saved_candidate_identity": validation["candidate_sha256"], "canonical_cfg_file_sha256": sha(RUN / "graph/initial.json"),
            "accepted_candidate_file_sha256": sha(stage / "calls/a002/merged-candidate.json"), "wire_value_file_sha256": sha(stage / result["value_file"]),
            "source_inventory_file_sha256": sha(BASE / "source-boundary-inventory.json")},
        "saved_validation_status": validation["status"],
        "counts": {"blocks": len(raw["blocks"]), "edges": len(raw["edges"]), "instructions": len(instructions),
            "api_sites_represented": len(api_rows), "api_sites_denominator": 13, "save_sites_represented": len(save_rows),
            "save_sites_denominator": 25, "url_loops_represented": len(loop_rows), "url_loops_denominator": 3},
        "correction_comparison": {"previous_instructions": 561, "added_instructions": 2, "core_changed_blocks": changed,
            "metadata_or_other_changed_block_count": len(metadata_changed), "edges_unchanged": previous["edges"] == raw["edges"],
            "notes": "Opcode/input/output changes are confined to four filter blocks. Metadata and prose also changed; structural acceptance alone does not prove their semantic correctness.", "corrections": corrections},
        "api_sites": api_rows, "save_sites": save_rows, "url_loops": loop_rows,
        "source_facts_retained": [
            {"blocks": ["report_prepare", "report_api"], "fact": "filters/orderBy are read/destructured as unused results but are absent from actual API request construction."},
            {"blocks": ["bulk_prepare", "bulk_empty"], "fact": "Empty normalized URLs return rows=[]/rowCount=0 before client acquisition, API and save."},
            {"blocks": ["md_dimensions_project", "md_metrics_project", "md_full_write"], "fact": "Dimension-only and metric-only metadata outputs remain distinct from whole metadata."},
            {"blocks": ["save_location", "save_name"], "fact": "Shared save derives directory from settings.resultsDir, serializes metadata.propertyId and caller data, writes with replace semantics, and returns only filepath; the write itself has no content output."},
            {"blocks": ["reindex_ok", "status_ok"], "fact": "reindex success spreads notification after input URL, allowing response URL overwrite; status success keeps input URL, verdict equality and whole indexStatus only."}],
        "pending_source_review_scope": [
            "Required persistence and empty-input no-save exception must be reconciled in Task correspondence.",
            "The public saved-path return must not create return demands at 25 call sites that discard it.",
            "Separate public helper roots and call-site summaries still require source-backed per-invocation binding, client-cache state and request/response correlation.",
            "Remote input necessity must cite interface/source semantics beyond the supplied actual arguments.",
            "Successful graph structure is not reviewed semantic fidelity, backend processing coverage or complete DOE."],
        "observed_status": {"status": observed.get("status"), "stage": observed.get("stage"), "stages": observed.get("stages", {})},
        "execution": {"model_calls": 0, "skill_executions": 0, "renderer_or_backend_runs": 0, "replays": 0,
            "production_or_active_graph_edits": 0}}
    with (BASE / "selected-graph-audit.json").open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    md = """# Selected initial CFG audit (downstream work pending)

The selected graph is `graph/initial.json`, derived from graph step `calls/a002`; the saved validation is `valid`. Its normalized wire identity is `ad8023ba8286c1dbc91c0f2e914478e96ea673031be289bd825ddac5fd0340aa`. The graph contains **245 blocks, 232 edges and 563 IR**. All raw-to-normalized-to-canonical instruction correspondences were inspected without rerunning compilation or analysis.

## Structural correction

The two invalid merges now consume predecessor-produced `list_filtered_unchanged` and `latest_filtered_unchanged`. Each member block adds a `carry_filter_accumulator` instruction, before its predicate dispatch, returning the current accumulator unchanged. The false edge returns that result to its header; the true keep edge still appends the accepted member. The graph's edges are unchanged. Opcode/input/output changes are confined to these four filter blocks, adding two instructions; metadata/prose also changed and remain subject to semantic review.

This removes the same-block self-reference while retaining the intended filtering skeleton. Processing must implement both carry instructions as identity bindings of the existing value, with no invented transform or observation, and preserve predecessor applicability.

## Source-boundary representation

| Finite source sites | Matching selected representation |
| --- | ---: |
| SDK API acquisitions/publications | 13/13 |
| saveResult call sites | 25/25 |
| Explicit URL loops | 3/3 |

These counts use more than overlapping citations. The API checks inspect receiver inputs, request/result bindings, operation literals and output selection: GA4 first tuple response, Search Console response.data, inspectionResult projection, and URL_UPDATED versus URL_DELETED publication. Per-site reasons and complete instructions are in the JSON audit. They establish represented call skeletons, not interface necessity or backend completeness.

All 25 save instructions carry the site's payload/category/operation/optional extra and declare no output, matching ignored filepath returns. Optional save branches remain; aggregate high-level saves remain unconditional. The shared saver still reads settings, builds path and metadata wrapper, performs a replace write with no content output and returns its filepath. Required side effects and each call's actual settings/clock/file identity remain processing/mapping obligations.

All three URL loops have has_member headers, one-member selection, child calls with save:false, append/merge relationships and real backedges. Batch rejection propagates, while reindex/status preserve success-versus-catch rows and aggregate saving. Reindex's response URL overwrite and status's indexStatus-only consumption remain explicit. Occurrence/cardinality/order and URL/result correlation still require the processing loop summary and downstream evidence.

## Preserved source facts and remaining checks

The graph retains unused filters/orderBy rather than pretending they affect runReport; empty bulk input returns before API/save; metadata dimension-only and metric-only projections remain separate from full metadata; storage retains the particular settings fields used by path and metadata. These are necessary source facts for field-level analysis, not current deletion conclusions.

Task correspondence must still reconcile empty-input persistence exceptions and avoid demands for ignored saver return values. Public callable roots and summarized call sites need per-invocation/client-state/request-response bindings. Interface input necessity requires separate semantic evidence beyond current arguments. No propagation, input assessment or DOE result was available for this audit; source review and allowed semantic repair may supersede this selected initial graph.

No production, active graph or historical artifact was edited. No model, Skill, renderer, compiler, backend or replay was run. Exact identities, canonical IR references, candidate/source evidence and pending checks are in `selected-graph-audit.json`.
"""
    with (BASE / "selected-graph-audit.en.md").open("x", encoding="utf-8") as handle:
        handle.write(md)
    print(json.dumps({"counts": report["counts"], "audit_sha256": sha(BASE / "selected-graph-audit.json")}, indent=2))


if __name__ == "__main__":
    main()
