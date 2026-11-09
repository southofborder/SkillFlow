"""Read saved JSON/text only; never import or execute SkillFlow or Skill code."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-interface-r4-high-20261104-173522"
OUT = Path(__file__).resolve().parent
CRITERIA = OUT.parent / "source-audit"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


inventory = read(CRITERIA / "boundary-inventory.json")
graph = read(RUN / "graph/revision.json")["cfg"]
wire = read(RUN / "revision/annotation/audit/wire-annotation.json")
compiled = read(RUN / "revision/annotation/audit/compiled-response.json")
records = read(RUN / "propagation/records.json")
data = {v["id"]: v for v in read(RUN / "propagation/data.json")}
manifest = read(RUN / "propagation/manifest.json")
instructions = {i["id"]: i for b in graph["blocks"].values() for i in b["instructions"]}
blocks = {i["id"]: k for k, b in graph["blocks"].items() for i in b["instructions"]}
artifact_names = [
    "selection.json", "graph/revision.json", "revision/annotation/audit/wire-annotation.json",
    "revision/annotation/audit/compiled-response.json", "propagation/manifest.json",
    "propagation/records.json", "propagation/data.json", "propagation/sinks.json",
]
artifact_hashes = {p: digest(RUN / p) for p in artifact_names}


def ids(slots):
    return sorted({v for slot in slots for v in slot})


def ops(ir):
    return [(ei, oi, op) for ei, event in enumerate(records[ir]["events"])
            for oi, op in enumerate(event["atomic_ops"])]


def coordinate(ir, ei, oi):
    return {"instruction_id": ir, "event_index": ei, "op_index": oi}


def brief_data(identifier):
    value = data[identifier]
    return {"id": identifier, "content": value["content"], "origin": value["origin"]}


def actual_op(ir, ei, oi, op):
    return {**coordinate(ir, ei, oi), **op}


def compiled_op(ir, ei, oi):
    return compiled["ir_semantics"][ir]["events"][ei]["atomic_ops"][oi]


def alternative_signature(op):
    return sorted(json.dumps({"inputs": a["inputs"], "bindings": a.get("bindings", {})}, sort_keys=True)
                  for a in op.get("alternatives", []))


def recorded_ancestry(identifier):
    """Follow already saved provenance edges, without applying propagation rules."""
    seen = set()
    pending = [identifier]
    while pending:
        item = pending.pop()
        if item in seen or item not in data:
            continue
        seen.add(item)
        origin = data[item]["origin"]
        pending.extend(origin.get("inputs", []))
        if isinstance(origin.get("part_of"), str):
            pending.append(origin["part_of"])
    return seen


def remote_pairs(ir):
    result = []
    previous = []
    for ei, oi, op in ops(ir):
        if not any(v.get("kind") == "remote" for v in op.get("endpoints", [])):
            continue
        if op["op"] == "deliver":
            previous.append((ei, oi, op))
        elif op["op"] == "receive":
            request_id = compiled_op(ir, ei, oi).get("request_id")
            matches = [(se, so, send) for se, so, send in previous
                       if compiled_op(ir, se, so).get("request_id") == request_id]
            assert len(matches) == 1, (ir, ei, oi, len(matches))
            se, so, send = matches[0]
            result.append({
                "send": actual_op(ir, se, so, send), "receive": actual_op(ir, ei, oi, op),
                "compiled_request_id": request_id,
                "same_request_ids": send["inputs"] == op["inputs"],
                "same_endpoints": send["endpoints"] == op["endpoints"],
                "same_alternative_request_bindings": alternative_signature(send) == alternative_signature(op),
                "request_data": [brief_data(d) for d in ids(send["inputs"])],
                "response_data": [brief_data(d) for d in ids(op["outputs"])],
            })
    return result


api_ir = {
    ("bulk-lookup.ts", 183): "ir_272",
    ("indexing.ts", 62): "ir_257", ("indexing.ts", 119): "ir_257", ("indexing.ts", 152): "ir_238",
    ("metadata.ts", 42): "ir_207", ("metadata.ts", 64): "ir_207", ("metadata.ts", 86): "ir_207",
    ("realtime.ts", 28): "ir_198", ("realtime.ts", 48): "ir_198",
    ("realtime.ts", 68): "ir_198", ("realtime.ts", 88): "ir_198",
    ("reports.ts", 100): "ir_189", ("searchConsole.ts", 102): "ir_226",
}
save_ir = {
    ("bulk-lookup.ts", 188): "ir_275",
    ("indexing.ts", 76): "ir_263", ("indexing.ts", 101): "ir_175",
    ("indexing.ts", 133): "ir_263", ("indexing.ts", 189): "ir_263",
    ("metadata.ts", 51): "ir_219", ("metadata.ts", 73): "ir_219", ("metadata.ts", 91): "ir_219",
    ("realtime.ts", 35): "ir_201", ("realtime.ts", 55): "ir_201",
    ("realtime.ts", 75): "ir_201", ("realtime.ts", 95): "ir_201",
    ("reports.ts", 105): "ir_192", ("searchConsole.ts", 118): "ir_230",
    ("index.ts", 73): "ir_034", ("index.ts", 104): "ir_045", ("index.ts", 135): "ir_056",
    ("index.ts", 162): "ir_067", ("index.ts", 200): "ir_078", ("index.ts", 222): "ir_089",
    ("index.ts", 252): "ir_102", ("index.ts", 272): "ir_111", ("index.ts", 292): "ir_120",
    ("index.ts", 316): "ir_141", ("index.ts", 343): "ir_162",
}


def site_row(site, mapping, mode):
    ir = mapping[(Path(site["file"]).name, site["line"])]
    evidences = wire["ir_semantics"][ir].get("evidences", [])
    matching = [e for e in evidences if e.get("file") == "skill/" + site["file"]
                and e.get("start_line", 0) <= site["line"] <= e.get("end_line", 0)]
    assert matching, (site, ir)
    selected = [(e, o, v) for e, o, v in ops(ir)
                if (v["op"] == "write" if mode == "save" else
                    v["op"] == "deliver" and any(x.get("kind") == "remote" for x in v.get("endpoints", [])))]
    assert selected and all(ids(v["inputs"]) for _, _, v in selected), (site, ir)
    return {
        **site, "primary_instruction_id": ir, "block_id": blocks[ir],
        "opcode": instructions[ir]["opcode"], "source_evidences": matching,
        "candidate_present": True, "coverage": manifest["coverage"][ir],
        "computed_nonempty_boundary": True,
        "computed_coordinates": [coordinate(ir, e, o) for e, o, _ in selected],
        "shared_source_site_count": sum(v == ir for v in mapping.values()),
        "interpretation": "A static computed boundary under the modeled conditions; not a real API call or filesystem write executed by this audit.",
    }


def save_detail(ir):
    e, o, write = next((e, o, v) for e, o, v in ops(ir) if v["op"] == "write")
    payloads = set(ids(write["inputs"]))
    producers = [(pe, po, v) for pe, po, v in ops(ir)
                 if pe < e and set(ids(v["outputs"])) == payloads]
    assert len(producers) == 1, (ir, producers)
    pe, po, producer = producers[0]
    value_input = instructions[ir]["inputs"][0]
    incoming = next((b["data_ids"] for b in records[ir]["entry_state"]["bindings"]
                     if b["location"].get("name") == value_input.get("identifier")), [])
    return {
        "instruction_id": ir, "cfg_value_input": value_input,
        "cfg_arguments": instructions[ir]["inputs"],
        "incoming_value_ids": incoming,
        "serialization": actual_op(ir, pe, po, producer),
        "serialization_input0_equals_incoming_value_ids": set(producer["inputs"][0]) == set(incoming),
        "write": actual_op(ir, e, o, write),
        "serialization_outputs_equal_write_inputs": True,
        "compiled_write_mode": compiled_op(ir, e, o).get("mode", "replace (default)"),
        "saved_payload_data": [brief_data(d) for d in sorted(payloads)],
        "original_value_data": [brief_data(d) for d in incoming],
        "precision": "Opaque serialization records possible dependency, not exact output bytes or guaranteed plaintext containment. Storage endpoints are symbolic may-alias locations.",
    }


source_checks = []
for item in inventory["inventory"]:
    path = RUN / "source/inputs/package" / item["file"]
    observed = digest(path)
    source_checks.append({"file": item["file"], "expected_sha256": item["sha256"],
                          "observed_sha256": observed, "matches": observed == item["sha256"]})
assert all(row["matches"] for row in source_checks)

api_rows = [site_row(v, api_ir, "api") for v in inventory["sites"]["api_request_sites"]]
save_rows = [site_row(v, save_ir, "save") for v in inventory["sites"]["save_result_call_sites"]]
all_remote_pairs = {ir: pairs for ir in records if (pairs := remote_pairs(ir))}
all_writes = [coordinate(ir, e, o) for ir in records for e, o, v in ops(ir) if v["op"] == "write"]
save_details = {ir: save_detail(ir) for ir in sorted(set(save_ir.values()))}
assert all(v["serialization_input0_equals_incoming_value_ids"] for v in save_details.values())
assert all(v[k] for pairs in all_remote_pairs.values() for v in pairs
           for k in ("same_request_ids", "same_endpoints", "same_alternative_request_bindings"))

save_return_map = {"ir_034": "ir_036", "ir_045": "ir_047", "ir_056": "ir_058",
    "ir_067": "ir_069", "ir_078": "ir_080", "ir_089": "ir_091", "ir_102": "ir_104",
    "ir_111": "ir_113", "ir_120": "ir_122", "ir_141": "ir_143", "ir_162": "ir_164",
    "ir_175": "ir_177", "ir_192": "ir_194", "ir_201": "ir_203", "ir_219": "ir_221",
    "ir_230": "ir_232", "ir_263": "ir_265", "ir_275": "ir_277"}
save_return_checks = []
for save, ret in save_return_map.items():
    name = instructions[ret]["inputs"][0]["identifier"]
    returned = next(v["data_ids"] for v in records[ret]["entry_state"]["bindings"] if v["location"]["name"] == name)
    saved = save_details[save]["incoming_value_ids"]
    same = set(saved) == set(returned)
    assert same, (save, ret)
    save_return_checks.append({"save_instruction": save, "return_instruction": ret,
        "returned_location": name, "data_ids": returned, "same_original_value_ids": same,
        "limit": "The value passed into serialization equals the returned value at saved-Data identity level. The written serialization is a distinct Data value; this is not byte equality."})

response_save_paths = []
for api, save in [("ir_189", "ir_192"), ("ir_198", "ir_201"), ("ir_207", "ir_219"),
                  ("ir_226", "ir_230"), ("ir_238", "ir_263"), ("ir_257", "ir_263"), ("ir_272", "ir_275")]:
    response_ids = {d for pair in all_remote_pairs[api] for d in ids(pair["receive"]["outputs"])}
    response_save_paths.append({"api_instruction": api, "save_instruction": save,
        "response_ids": sorted(response_ids),
        "saved_original_values": [{"data_id": item, "recorded_response_ancestors": sorted(response_ids & recorded_ancestry(item))}
                                  for item in save_details[save]["incoming_value_ids"]],
        "limit": "Provenance ancestry alone does not mean complete plaintext inclusion. The shared indexing save has four inspection-result alternatives and one publication-result alternative; each retains its own response ancestry."})

selected_evidence_irs = ["ir_026", "ir_034", "ir_074", "ir_076", "ir_078", "ir_089", "ir_111",
    "ir_180", "ir_187", "ir_196", "ir_201", "ir_205", "ir_210", "ir_213", "ir_215", "ir_217",
    "ir_219", "ir_224", "ir_228", "ir_230", "ir_236", "ir_240", "ir_255", "ir_259", "ir_261",
    "ir_263", "ir_267", "ir_268", "ir_269", "ir_270", "ir_275", "ir_315", "ir_316", "ir_321",
    "ir_322", "ir_323", "ir_324", "ir_349", "ir_350"]

evidence = {
    "identity": "ga4-interface-r4-source-boundary-audit-v1",
    "created_at": datetime.now(timezone.utc).isoformat(), "reviewer": "/root/audit_paused_registry_v9",
    "run": str(RUN.relative_to(ROOT)).replace("\\", "/"),
    "method": "Independent source inventory mapping and saved-JSON relationship inspection using Python standard library only. No SkillFlow import, solver, loader, target, replay, Skill or model execution. No production or original artifact edits.",
    "criteria": [str((CRITERIA / n).relative_to(ROOT)).replace("\\", "/") for n in ("boundary-inventory.json", "correctness-checklist.json")],
    "source_checks": source_checks,
    "original_artifact_sha256": artifact_hashes,
    "selected_inputs": read(RUN / "selection.json"),
    "counts": {
        "generated_ir": len(instructions), "blocks": len(graph["blocks"]),
        "coverage": dict(Counter(manifest["coverage"].values())),
        "processing_gaps": len(wire["processing_gaps"]),
        "processing_gaps_marked_unmodeled": sum(bool(v.get("unmodeled")) for v in wire["processing_gaps"]),
        "api_source_sites": len(api_rows), "api_sites_with_candidate_and_nonempty_computed_boundary": len(api_rows),
        "distinct_primary_api_instruction_ids": len(set(api_ir.values())),
        "save_source_sites": len(save_rows), "save_sites_with_candidate_and_nonempty_computed_boundary": len(save_rows),
        "distinct_primary_save_instruction_ids": len(set(save_ir.values())),
        "all_computed_remote_send_receive_positions": sum(map(len, all_remote_pairs.values())),
        "all_computed_write_positions": len(all_writes),
        "computed_write_positions_by_endpoint_kind": dict(Counter(endpoint["kind"] for ir in records for _, _, operation in ops(ir) if operation["op"] == "write" for endpoint in operation["endpoints"])),
        "compiled_write_modes": dict(Counter(compiled_op(v["instruction_id"], v["event_index"], v["op_index"]).get("mode") for v in all_writes)),
        "all_computed_remote_pairs_with_matching_request_receiver_bindings": sum(map(len, all_remote_pairs.values())),
        "explicit_source_loops": 3,
        "count_limit": "Source sites can share a computed operation, and caller expansions duplicate some source sites. Neither operation count nor Data alternative count is a runtime frequency or exact semantic coverage score.",
    },
    "api_sites": api_rows, "save_sites": save_rows,
    "all_computed_remote_pairs": all_remote_pairs,
    "all_computed_write_coordinates": all_writes,
    "primary_save_payload_traces": save_details,
    "primary_save_return_identity_checks": save_return_checks,
    "primary_response_save_provenance": response_save_paths,
    "selected_instruction_evidence": {ir: {"cfg": instructions[ir], "wire": wire["ir_semantics"][ir], "records": records[ir]} for ir in selected_evidence_irs},
    "processing_gaps": wire["processing_gaps"],
    "propagation_diagnostics": manifest["diagnostics"],
    "missing_part_input_data": brief_data(manifest["diagnostics"][0]["data_id"]),
    "source_supported_nonexecution": [
        {"source": "scripts/src/index.ts:180-193", "instructions": ["ir_074", "ir_076"], "reason": "Both compareDateRanges child runReport calls pass save:false; their saved records contain remote send/receive and no write. Only the outer comparison ir_078 has its own save."},
        {"source": "scripts/src/index.ts:308-309,331-332; scripts/src/api/indexing.ts:96-97", "instructions": ["ir_131", "ir_152", "ir_171"], "reason": "Loop child calls pass save:false and have no storage writes. Loop final saves are separately computed; see loop-audit.json."},
        {"source": "scripts/src/api/bulk-lookup.ts:158-164", "instructions": ["ir_268", "ir_269", "ir_270", "ir_272", "ir_275"], "reason": "The empty normalized URL arm returns before getter/date/API/save. Both CFG branch targets are represented because the public input is unknown; the nonempty arm has computed request and save. This is a structured source condition, not a globally unreachable API site."},
    ],
    "limitations": [
        "All 369 generated IR processed does not establish every source behavior or every natural-language obligation.",
        "Shared realtime, metadata and indexing entries do not yield one independently resolved call identity per source site. Entry-dependent opaque computations retain less precision than source constants and exact request objects.",
        "Caller getter/date and save summaries do not expand cached-client credential provenance, exact filesystem failure order or exact serialization. Standalone getter/storage entries do not establish caller execution.",
        "The analyze-to-corresponding-saved-file-to-Markdown-summary continuation has no executable source/CFG link; ir_349/ir_350 processing gaps preserve that limitation.",
        "ir_323 retains a caught-error input on the succeeded true arm despite branch alternatives at ir_322. Its missing value gives an empty selection and a diagnostic; the successful parsed Data remains. This is a recorded correlation/precision limitation, not proof of an incorrect returned successful value.",
        "The three explicit loops have separate evidence in loop-audit.json. Multiple-generation ambiguity and opaque computations prevent exact sequence, count or feasibility claims.",
        "No general accuracy, semantic equivalence, complete DOE, absence of excess exposure or runtime execution claim is made.",
    ],
}
assert artifact_hashes == {p: digest(RUN / p) for p in artifact_names}
evidence["original_artifacts_unchanged_during_extraction"] = True
(OUT / "boundary-evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(evidence["counts"], ensure_ascii=True))
