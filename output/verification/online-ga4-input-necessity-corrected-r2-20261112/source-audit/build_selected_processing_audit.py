"""Audit selected processing JSON; never run the analysis or its validators."""
from collections import Counter
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


def walk(value, path=""):
    if isinstance(value, dict):
        yield path, value
        for name, child in value.items():
            yield from walk(child, path + "/" + str(name))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + "/" + str(index))


def main():
    step = RUN / "steps/processing"
    selected = read(step / "result.json")
    assert selected["accepted_call"] == "calls/a002"
    validation = read(step / "calls/a002/validation.json")
    assert validation["status"] == "valid" and not validation.get("diagnostics")
    p = read(step / selected["value_file"])
    previous_validation = read(step / "calls/a001/validation.json")
    cfg = read(RUN / "graph/initial.json")["cfg"]
    irs = {i["id"]: i for b in cfg["blocks"].values() for i in b["instructions"]}
    graph_audit = read(BASE / "selected-graph-audit.json")
    rows = list(walk(p["ir_semantics"], "/ir_semantics"))
    operations = [(path, op) for path, op in rows if "op" in op]
    attachments = [(path + "/" + name, op[name]) for path, op in rows
        for name in ("demand_transfer", "input_contract") if name in op]
    unmodeled = {g["instruction_id"] for g in p["processing_gaps"] if g.get("unmodeled")}
    modeled = set(p["ir_semantics"])
    assert not modeled & unmodeled and modeled | unmodeled == set(irs)
    evidence_fixes = []
    for d in previous_validation["diagnostics"]:
        if d["code"] != "mechanism_evidence_reference":
            continue
        ir = d["path"].split("/")[2]
        evidence = p["ir_semantics"][ir]["evidences"]
        assert evidence == [{"target": {"instruction_id": ir, "path": []}}]
        evidence_fixes.append({"instruction_id": ir, "evidences": evidence})
    raw_input_mismatches, scoped_contract_gaps = [], []
    for path, op in operations:
        for name in ("demand_transfer", "input_contract"):
            if name not in op:
                continue
            rules = op[name]["rules"] if name == "demand_transfer" else [op[name]]
            for index, rule in enumerate(rules):
                prefix = path + "/" + name + (f"/rules/{index}" if name == "demand_transfer" else "")
                if sorted(row["input_index"] for row in rule["inputs"]) != list(range(len(op.get("inputs", [])))):
                    raw_input_mismatches.append(prefix)
                for j, row in enumerate(rule["inputs"]):
                    if row.get("gap") or row.get("unresolved_ranges"):
                        scoped_contract_gaps.append({"path": prefix + f"/inputs/{j}", "output": rule.get("output"), "input_requirement": row})
    carries = []
    for ir in ("ir_103", "ir_126"):
        spec = p["ir_semantics"][ir]
        assert not spec.get("segments") and spec["output_bindings"] == [{"output_index": 0, "value": {"kind": "input", "index": 0}}]
        carries.append({"instruction_id": ir, "processing": spec, "assessment": "direct_identity_binding"})
    api_rows, receiver_concerns = [], []
    for site in graph_audit["api_sites"]:
        ir = site["representation"]["canonical_ir_id"]
        spec = p["ir_semantics"][ir]
        local = list(walk(spec, "/ir_semantics/" + ir))
        calls = [(path, op) for path, op in local if op.get("op") == "call"]
        assert len(calls) == 1 and "input_contract" in calls[0][1]
        call_path, call = calls[0]
        location = p["locations"][call["location"]]
        all_inputs = [obj for _, obj in local if obj.get("kind") == "input"]
        consumes_client_input = any(obj.get("index") == 0 for obj in all_inputs)
        assert irs[ir]["inputs"][0]["type"] == "result"
        row = {"site_id": site["site_id"], "instruction_id": ir, "source": site["source"],
            "processing": spec, "call_location": call["location"], "location": location,
            "assessment": "explicit_call_and_response_binding_present", "consumes_cfg_receiver_input_zero": consumes_client_input,
            "receiver_operand_refs": location.get("operand_refs", [])}
        api_rows.append(row)
        if not consumes_client_input and not location.get("operand_refs"):
            receiver_concerns.append({"site_id": site["site_id"], "instruction_id": ir,
                "cfg_receiver": irs[ir]["inputs"][0], "call_path": call_path,
                "location_id": call["location"],
                "concern": "The actual CFG client/receiver operand is not consumed in the submitted processing references, and the remote location has no operand_refs tying it to that handle. Prose about using the client does not materialize receiver or creation-time credential identity.",
                "review_needed": "Verify the source-backed request/response receiver binding and its task demand; do not infer client deletion or credential irrelevance from this omission."})
    save_rows = []
    for site in graph_audit["save_sites"]:
        ir = site["representation"]["canonical_ir_id"]
        spec = p["ir_semantics"][ir]
        ops = [(path, op) for path, op in walk(spec) if "op" in op]
        assert len(ops) == 1 and ops[0][1]["op"] == "deliver" and ops[0][1]["target"] == "save"
        assert not spec.get("output_bindings")
        save_rows.append({"site_id": site["site_id"], "instruction_id": ir,
            "source": site["source"], "processing": spec,
            "assessment": "local_helper_delivery_present_no_return_output",
            "persistent_write_at_this_ir": False,
            "review_needed": "The actual source saver creates a persistent metadata wrapper and computed path. This site currently delivers its arguments to a task-retained tool named Local saveResult, without per-invocation wrapper/write events. Review must establish the persistent effect and its data/settings/clock/path bindings; a separate public saver root is not that invocation."})
    loop_rows = []
    for loop, prefix, call_ir in zip(graph_audit["url_loops"], ("batch", "reindex", "status"), ("ir_436", "ir_531", "ir_551")):
        selected_blocks = [b for b in cfg["blocks"].values() if b["block_name"].startswith(prefix + "_")]
        included = [i["id"] for b in selected_blocks for i in b["instructions"]]
        assert all(ir in modeled for ir in included)
        loop_rows.append({"site_id": loop["site_id"], "function": loop["function"], "source": loop["source"],
            "modeled_ir_ids": included, "child_call_instruction": call_ir,
            "child_case_names": [case["name"] for segment in p["ir_semantics"][call_ir].get("segments", []) for case in segment.get("cases", [])],
            "child_gaps": [g for g in p["processing_gaps"] if g["instruction_id"] == call_ir],
            "assessment": "header_member_merge_append_and_child_cases_have_specifications",
            "remaining_check": "No backend finite-loop result or preservation/receiver/occurrence proof is available. Clock fallback and attempted-versus-completed request distinctions remain explicit gaps; protected logging/effect completeness still needs source review."})
    inventory_files = [path.relative_to(RUN).as_posix() for path in RUN.rglob("*.json")
        if not any(part in {"implementation-snapshot", "transport", "source"} for part in path.parts)
        and any(word in path.name.lower() for word in ("inventory", "obligation", "contract"))]
    report = {"identity": "ga4-r2-selected-initial-processing-audit-v1", "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "selected_processing_structurally_valid_source_review_and_backend_pending",
        "run_directory": str(RUN),
        "identities": {"saved_value_identity": selected["value_sha256"], "saved_response_identity": validation["response_sha256"],
            "saved_candidate_identity": validation["candidate_sha256"], "value_file_sha256": sha(step / selected["value_file"]),
            "validation_file_sha256": sha(step / "calls/a002/validation.json"), "cfg_file_sha256": sha(RUN / "graph/initial.json")},
        "saved_validation": {"status": validation["status"], "diagnostics": validation.get("diagnostics", [])},
        "coverage": {"actual_ir": len(irs), "modeled_specifications": len(modeled), "explicit_unmodeled_ids": sorted(unmodeled),
            "uncovered_ids": sorted(set(irs)-modeled-unmodeled), "overlap": sorted(modeled & unmodeled),
            "processing_gap_count": len(p["processing_gaps"]), "non_stopping_gap_count": sum(not g.get("unmodeled") for g in p["processing_gaps"])},
        "processing_gaps": p["processing_gaps"],
        "fixes": {"mechanism_reference_repairs": evidence_fixes,
            "schema": {"ir_114": "Input-row reason supplied; dynamic-slice gap retained.",
                "ir_119": "Nested cases replaced by a call to task-retained tool Local listResults; shape passes, source/effect fidelity remains a review concern.",
                "ir_173": "remainder set independent with a separate unresolved value range; scoped gap retained."},
            "coverage": "ir_179 now has call/update_fields processing and its explicit unmodeled gap is removed; ir_419 and ir_423 remain solely unmodeled."},
        "wire_contract_counts": {"compute_operations": sum(op["op"] == "compute" for _, op in operations),
            "inline_expression_computes": sum(op["op"] == "compute" and "expression" in op for _, op in operations),
            "demand_transfer_attachments": sum(path.endswith("/demand_transfer") for path, _ in attachments),
            "demand_transfer_rules": sum(len(contract["rules"]) for path, contract in attachments if path.endswith("/demand_transfer")),
            "tool_input_contract_attachments": sum(path.endswith("/input_contract") for path, _ in attachments),
            "distinct_ir_with_contract": len({path.split("/")[2] for path, _ in attachments}),
            "input_index_coverage_mismatches": raw_input_mismatches},
        "formal_inventory": {"already_materialized_paths": inventory_files,
            "note": "The saved step is structurally valid, so configured validation was accepted. No standalone obligation/review inventory receipt was present at this observation. Wire attachment counts are not assumed to equal compiled request/response obligation counts; no validator or inventory builder was invoked by this audit."},
        "scoped_contract_gaps": scoped_contract_gaps, "carry_bindings": carries,
        "locations": {"count": len(p["locations"]), "kinds": dict(Counter(loc["kind"] for loc in p["locations"].values()))},
        "finite_source_modeling": {"api_sites_with_call_specs": len(api_rows), "api_denominator": 13,
            "save_sites_with_local_helper_delivery": len(save_rows), "save_denominator": 25,
            "explicit_url_loops_with_specifications": len(loop_rows), "loop_denominator": 3},
        "api_sites": api_rows, "save_sites": save_rows, "url_loops": loop_rows,
        "source_review_concerns": {"receiver_identity": receiver_concerns,
            "local_saver_boundary": {"location": p["locations"]["save"], "affected_site_count": len(save_rows),
                "public_persistent_writer": {"instruction_id": "ir_077", "location": p["locations"]["saved"], "processing": p["ir_semantics"]["ir_077"]},
                "concern": "Do not count the 25 task-retained helper deliveries as 25 instantiated persistent writes or assume their argument-only contracts establish all wrapper/receiver/field necessities."},
            "helper_summaries": {"examples": {key: p["locations"][key] for key in ("report", "list", "save")},
                "concern": "Many local source functions are now tool summaries. A source-backed call contract and structural validity do not, by themselves, materialize each helper's internal acquisition, credential, read/write or error effects."}},
        "observed_run_stages": read(RUN / "result.json").get("stages", {}),
        "limits": ["Structural acceptance is distinct from source-review acceptance and semantic fidelity.",
            "The source-boundary counts mean specifications are present, not that effects, data versions, receiver identities or field necessities are correct or processed.",
            "No propagation, demand, input assessment or DOE result is inferred; allowed semantic repair may supersede these materials."],
        "execution": {"model_calls": 0, "skill_executions": 0, "pipeline_or_validator_invocations": 0,
            "replays": 0, "production_or_run_edits": 0}}
    with (BASE / "selected-processing-audit.json").open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    markdown = """# Selected processing audit (source review and backend pending)

Processing `calls/a002` is selected and its saved validation is `valid` with zero diagnostics. Value identity: `533595e3e761dc816c965817bcbe8497c1a8d9f5c505170bf09308b95376d8d0`. Structural acceptance is not semantic or DOE acceptance.

## Coverage and corrected records

The 563-IR graph now has **561 modeled specifications plus two exclusively unmodeled IR (`ir_419`, `ir_423`)**, with no missing or overlapping IDs. There are **13 processing gaps: two stopping unmodeled gaps and 11 other limitations**. The two stopped scopes are optional mobileUsability/richResults merges whose absent branches need JavaScript undefined without a declared operand. Source review must still decide whether these are genuine limits or repairable representation errors.

All 63 formerly rule-only local mechanism records now cite their own actual CFG instruction as a target. `ir_114` supplies the missing row reason; `ir_173` places its value-only uncertainty in a scoped range with independent remainder. The malformed nested cases at `ir_119` were replaced by a local helper tool call. `ir_179` gained processing and no longer overlaps an unmodeled gap. The original rejected response and audit remain unchanged.

Both carry IRs (`ir_103`, `ir_126`) still bind output 0 directly to input 0, adding no compute or observation.

## Contract and gap scopes

The selected wire contains **101 computes: nine inline expressions and 92 demand-transfer contracts with 92 rules**. It also has **146 tool-input contracts across call/deliver operations**, for **209 distinct IR with at least one contract**. Raw input-index accounting matches each operation. These are wire counts; no standalone compiled obligation/review inventory receipt was materialized at observation, and this audit did not invoke its builder.

Two local contract uncertainties remain: `ir_114` requires sorted-list cardinality but records the unavailable dynamic-prefix value selector; `ir_173` retains shape and isolates type-conditioned string value demand. These are specific cited claims, not generic opacity, but their adequacy remains for source review.

## Source-boundary modeling and concrete review concerns

All **13 API sites** have call/result specifications, all **25 saver sites** have delivery specifications, and all **three explicit URL loops** have header/member/merge/append and child-case specifications. These are modeling-presence counts, not backend or semantic completeness.

Two material source-binding concerns remain visible despite structural validity:

1. **Receiver identity:** at all 13 listed SDK sites, processing consumes the request but not CFG input 0's actual client handle; corresponding remote locations have no `operand_refs` tying them to that handle. For example `ir_171` calls `ga` with input 1 only, while its reason says to use the client as receiver. Prose does not materialize receiver or creation-time credential binding. No client deletion or credential irrelevance should be inferred from this omission.
2. **Persistent saver effects:** all 25 source saveResult calls now deliver arguments to a tool location named `Local saveResult`, retained for the task. They contain no per-call persistent wrapper/write events. The independent public saver body does still write serialized metadata plus data to persistent storage at `ir_077`, but that public invocation is not automatically each call site's own settings/clock/path instance. Review must establish the actual persistent effect and wrapper scope; do not count the 25 helper deliveries as 25 correctly modeled persistent writes.

The location inventory grew to 64, including 36 tools; many are local source helper summaries. A helper signature/contract and fresh return do not alone establish its internal acquisition, writes, client state or error effects. Loop child summaries retain normal/pre-request/post-request cases and explicit gaps for clock fallback or attempted-versus-completed requests. Occurrence pairing and protected logging still require review and backend evidence.

No input assessment, deletion, propagation or DOE assertion follows from this audit. Mapping, sensitivity and source review were still pending at observation. Exact selected identities, all local gaps, contract counts, per-site instructions and receiver/saver concerns are in `selected-processing-audit.json`. No model, Skill, pipeline, validator, renderer, backend or replay was run, and no production or active-run artifact was edited.
"""
    with (BASE / "selected-processing-audit.en.md").open("x", encoding="utf-8") as handle:
        handle.write(markdown)
    print(json.dumps({"coverage": report["coverage"], "contracts": report["wire_contract_counts"],
        "receiver_concerns": len(receiver_concerns), "inventory_files": inventory_files,
        "audit_sha256": sha(BASE / "selected-processing-audit.json")}, indent=2))


if __name__ == "__main__":
    main()
