"""Read one full or partial GA4 run. Print JSON on stdout, without writing or replaying it."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
sys.path[:0] = [str(PROJECT / "src"), str(HERE.parent / "online-ga4-entry-review-20261122")]
from source_correctness import (Evidence, Traces, check_pair, digest, endpoint_matches,
    expected_fields, instructions, legacy_spans, receiver_citations, recorded_ops, selected_spans, source_sites)
from sensitivity_observations import operand_slots
from pydantic import TypeAdapter
from skillflow.common.source_evidence import json_pointer
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.document_guided.sensitivity_entries import entry_catalogue
from skillflow.propagation.contracts.specs import AtomicOp
from skillflow.propagation.selectors import selector_binding


def distribution(values):
    return dict(sorted(Counter(values).items()))


def checked_sources(ev):
    snapshot = ev.optional(ev.run / "source/inputs/snapshot.json")
    sources = {}
    if snapshot is not None:
        read_snapshot(ev.run / "source")
        if snapshot["source_sha256"] != "3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd":
            raise ValueError("GA4 source differs from the verified inventory")
        for row in snapshot["files"]:
            path = ev.inside(ev.run / "source/inputs/package", row["path"])
            data = path.read_bytes()
            if digest(data) != row["raw_sha256"]:
                raise ValueError("GA4 source hash mismatch: " + row["path"])
            sources[row["path"]] = {"text": data.decode("utf-8"), "sha256": row["raw_sha256"]}
    return sources


def selection(ev):
    pin = ev.optional(ev.run / "selection.json") or {}
    def bound(ref):
        return ev.read(ev.inside(ev.run, ref["path"]), ref["sha256"])
    cfg = bound(pin["cfg"])["cfg"] if pin.get("cfg") else None
    owners, compiled, mapping = {}, {}, {}
    if pin.get("annotation"):
        ref = pin["annotation"]
        owner = ev.inside(ev.run, ref["path"]).parent
        manifest = bound(ref)
        refs = ev.read(owner / "inputs/references.json", manifest["files"]["inputs/references.json"])
        if (not cfg or ev.inside(owner, refs["cfg"]["path"]) != ev.inside(ev.run, pin["cfg"]["path"])
                or refs["cfg"]["sha256"] != pin["cfg"]["sha256"]
                or ev.inside(owner, refs["source_owner"]["path"]) != ev.run / "source"
                or refs["source_owner"]["manifest_sha256"] != ev.read(ev.run / "source/manifest.json")["manifest_sha256"]):
            raise ValueError("Selected annotation does not bind the selected source and graph")
        for name, binding in refs.get("fragment_steps", {}).items():
            directory = ev.inside(owner, binding["path"])
            if ev.read(directory / "manifest.json")["manifest_sha256"] != binding["manifest_sha256"]:
                raise ValueError("Selected fragment owner differs: " + name)
            result = ev.read(directory / "result.json")
            owners[name] = ev.read(ev.inside(directory, result["value_file"]), result["value_sha256"])
        compiled, mapping = [ev.read(owner / path, manifest["artifacts"][path])
                             for path in ("audit/compiled-response.json", "audit/compilation-map.json")]
    prop = ev.optional(ev.run / "propagation/manifest.json")
    records = None
    if prop is not None:
        if (not pin.get("annotation") or prop["upstream"]["manifest_sha256"] != manifest["manifest_sha256"]
                or ev.inside(ev.run / "propagation", prop["upstream"]["path"]) != owner):
            raise ValueError("Propagation belongs to another selected annotation")
        records = ev.read(ev.run / "propagation/records.json", prop["artifacts"]["records.json"])
    return pin, cfg, owners, compiled, mapping, prop, records


def covered_by(span, file, line):
    return (span and span.get("file", "").removeprefix("skill/") == file
            and span["start_line"] <= line <= span["end_line"])


def op_sources(mapping):
    """Map retained/exploded call operations through raw ranges to their actual action."""
    wires = {}
    for event in mapping.get("events", []):
        bounds = event.get("raw_atomic_range")
        if not bounds or event["kind"] not in {"slice", "retained"}:
            continue
        for index in range(*bounds):
            pointer = json_pointer(*event["raw_path"], "atomic_ops", index)
            wires[json_pointer(*event["compiled_path"], "atomic_ops", index - bounds[0])] = mapping["wire_paths"].get(pointer)
    indexes = defaultdict(set)
    for ir, row in mapping.get("source_action_bindings", {}).items():
        for ref, paths in row["bindings"].items():
            indexes[(ir, ref)].update(json_pointer("ir_semantics", ir, *path) for path in paths)
    return wires, indexes


def upstream_barriers(cfg, coverage, ir):
    if coverage.get(ir) != "blocked":
        return []
    blocks = {b: [row["id"] for row in block["instructions"]] for b, block in cfg["blocks"].items()}
    owners = {iid: b for b, rows in blocks.items() for iid in rows}
    incoming = defaultdict(set)
    for edge in cfg["edges"]:
        incoming[edge["target_block_id"]].add(edge["source_block_id"])
    pending, seen, result = [(owners[ir], ir)], set(), set()
    while pending:
        b, until = pending.pop()
        if (b, until) in seen:
            continue
        seen.add((b, until))
        prefix = blocks[b][:blocks[b].index(until)] if until else blocks[b]
        stops = [s for s in prefix if coverage.get(s) in {"unmodeled", "execution_error", "unresolved_binding"}]
        if stops:
            result.add(stops[-1])
        else:
            pending.extend((p, None) for p in incoming[b])
    return sorted(result)


def physical_evidence(ev, sources, cfg, compiled, mapping, prop, records, data):
    sites = source_sites(sources)
    if not cfg:
        return {"source_calls": sum(s["category"] == "remote" for s in sites) if sources else None,
                "status": "no_selected_cfg", "calls": None, "search_console_default_save": None}
    graph = (ev.optional(ev.run / "graph/initial.json") or {}).get("cfg", {})
    spans = selected_spans(cfg, graph, legacy_spans(ev, graph, sources), sources)
    irs, ops = instructions(cfg), recorded_ops(compiled, records or {})
    locs, coverage = compiled.get("locations", {}), (prop or {}).get("coverage", {})
    wires, indexes = op_sources(mapping)
    trace = Traces(cfg, compiled, ops)
    pairs = {key: check_pair(key, ops, locs) for key, row in ops.items() if row["op"]["op"] == "receive"}
    projections = defaultdict(list)
    for key, row in ops.items():
        op = row["op"]
        if op["op"] == "select_part":
            chains, complete = trace.ref(row["ir"], row["scope"], {"kind": "local", "name": op["output"]})
            for root, path, _, versions in chains:
                projections[root, tuple(path)].append((key, complete, versions))
    def actions(site, roles):
        answer = []
        for iid, ir in irs.items():
            declared = ir.get("metadata", {}).get("source_actions") or mapping.get("source_action_bindings", {}).get(iid, {}).get("actions", [])
            for a in declared:
                role = a.get("role") or a["kind"]
                if role in roles and covered_by(a["source"], site["file"], site["start_line"]):
                    answer.append((iid, a["ref"], a["source"]))
            if not declared and covered_by(spans.get(iid), site["file"], site["start_line"]):
                answer.append((iid, None, spans[iid]))
        return answer
    def candidates(anchor, roles, pool):
        inventory = actions(anchor, roles)
        def unique(span):
            return sum(other["category"] == anchor["category"] and other["method"] == anchor["method"]
                       and covered_by(span, other["file"], other["start_line"]) for other in sites) == 1
        eligible = [key for key in pool if any(ops[key]["ir"] == i and
            unique(span) and (r is None or wires.get(key) in indexes[i, r]) for i, r, span in inventory)]
        located = [{"ir": i, "action_ref": r, "span": span, "coverage": coverage.get(i),
                    "upstream_barriers_on_cfg_paths": upstream_barriers(cfg, coverage, i)}
                   for i, r, span in inventory]
        return eligible, located
    def versions(iid, side, name):
        return {v for b in (records or {}).get(iid, {}).get(side, {}).get("bindings", [])
                if b["location"] == {"kind": "result", "name": name} for v in b["data_ids"]}
    calls, query_versions = [], set()
    for s in (site for site in sites if site["category"] == "remote"):
        keys, owners = candidates(s, {"call", "receive"}, [k for k in pairs if endpoint_matches(pairs[k]["endpoint"], s["method"])])
        receiver = receiver_citations(s, sources)
        checks = []
        for key in keys:
            pair, iid = pairs[key], ops[key]["ir"]
            handles = []
            for operand_ref in locs[pair["location"]].get("operand_refs", []):
                if operand_ref["instruction_id"] != iid or operand_ref["side"] != "input":
                    continue
                input_value = irs[iid]["inputs"][operand_ref["index"]]
                if input_value["type"] != "result":
                    continue
                name = input_value["identifier"]
                producer = trace.definitions.get(name)
                if not producer:
                    continue
                prior = producer[0]
                span = spans.get(prior)
                if not covered_by(span, receiver[0]["file"], receiver[0]["line"]):
                    continue
                # A compound source span or a multi-output instruction alone cannot identify the handle.
                exact = span["start_line"] == span["end_line"] == receiver[0]["line"] and len(irs[prior]["outputs"]) == 1
                handles.append({"producer_ir": prior, "result": name, "operand_index": operand_ref["index"],
                    "single_line_single_output": exact, "shared_versions": sorted(versions(prior, "exit_state", name) & versions(iid, "entry_state", name))})
            fields = []
            for path in expected_fields(s):
                rows = projections[key, tuple(path)]
                witnessed = set().union(*(vs for _, complete, vs in rows if complete))
                fields.append({"path": path, "declared_selects": [p for p, _, _ in rows],
                               "recorded_version_count": len(witnessed)})
                if s["method"] == "searchanalytics.query" and len(keys) == 1 and pair["recorded"] == "confirmed":
                    query_versions.update(witnessed)
            checks.append({"receive": key, "endpoint": pair["endpoint"], "deliver": pair["deliver_matches"],
                "declared_pair": pair["declared"], "recorded_pair": pair["recorded"],
                "receiver_candidates": handles, "receiver_version_witness": any(
                    h["single_line_single_output"] and h["shared_versions"] for h in handles),
                "response_fields": fields})
        calls.append({"anchor": s["anchor_id"], "file": s["file"], "lines": [s["start_line"], s["end_line"]],
            "method": s["method"], "receiver_source": receiver[0], "located_actions": owners, "matching_calls": checks,
            "unique_recorded_pair": len(keys) == 1 and checks[0]["recorded_pair"] == "confirmed"})
    save, = [s for s in sites if s["category"] == "save" and s["function"] == "querySearchAnalytics"]
    writes, owners = candidates(save, {"call", "write"}, [k for k, r in ops.items()
        if r["op"]["op"] == "write" and locs[r["op"]["target"]]["kind"] == "storage"])
    file_lines = sources[save["file"]]["text"].splitlines()
    source_scope = {line.strip(): i for i, line in enumerate(file_lines[:save["start_line"]], 1)}
    missing_bindings = []
    data_by_id = {r["id"]: r for r in data or []}
    for iid, instruction in irs.items():
        if not any(covered_by(spans.get(iid), save["file"], source_scope[line]) for line in ("save = true,", "if (save) {")):
            continue
        for ei, event in enumerate(compiled.get("ir_semantics", {}).get(iid, {}).get("events", [])):
            guard = (event.get("case") or {}).get("guard")
            if guard and guard.get("path") == ["save"]:
                ref = instruction["inputs"][guard["input_index"]]
                if ref["type"] == "result" and guard["outcome"] < len(guard["tests"]) and guard["tests"][guard["outcome"]]["kind"] == "missing":
                    for value in versions(iid, "entry_state", ref["identifier"]):
                        missing_bindings.append(selector_binding(data_by_id, value, guard, guard["outcome"]))
            for oi, op in enumerate(event.get("atomic_ops", [])):
                selector = op.get("selector")
                if op["op"] != "branch" or not selector or selector["path"] != ["save"]:
                    continue
                for oi_test, test in enumerate(selector["tests"]):
                    if test["kind"] != "missing":
                        continue
                    for _, _, actual in ops[json_pointer("ir_semantics", iid, "events", ei, "atomic_ops", oi)]["rows"]:
                        for alt in actual.get("alternatives", []):
                            for value in alt["inputs"][0]:
                                binding = selector_binding(data_by_id, value, selector, oi_test)
                                if binding and binding.items() <= alt["bindings"].items():
                                    missing_bindings.append(binding)
    write_checks = []
    for k in writes:
        witnessed = [alt for _, _, row in ops[k]["rows"] for alt in row.get("alternatives") or [row]
                     if len(alt["inputs"]) == 1 and alt["inputs"][0] and set(alt["inputs"][0]) <= query_versions]
        write_checks.append({"pointer": k, "recorded_payload_matches_response_data": bool(witnessed),
            "matching_omitted_save_selector": any(binding and binding.items() <= alt.get("bindings", {}).items()
                        for binding in missing_bindings for alt in witnessed)})
    default_save = {"file": save["file"], "default_true_line": source_scope["save = true,"],
        "guard_line": source_scope["if (save) {"], "save_call_line": save["start_line"], "located_actions": owners,
        "storage_writes": write_checks, "recorded_witness_with_absent_save": any(w["matching_omitted_save_selector"] for w in write_checks),
        "witness_scope": "One feasible static write at the source action with a bound missing-save selector and the recorded response.data version."}
    return {"status": "selected", "source_calls": len(calls), "calls": calls, "search_console_default_save": default_save}


def sensitive(declared, cfg, processing, compiled, mapping, records, data):
    catalog = entry_catalogue(cfg, processing)
    access = {a["access_id"]: a for entry in catalog.values() for a in entry["accesses"]}
    declarations = {r["source_access_id"]: r for r in declared}
    result = {"classified_entries": len({r["source_entry_id"] for r in declared}),
        "classified_access_sites": len(declarations), "classified_fields": len({
            (r["source_entry_id"], json.dumps(r["path"], sort_keys=True), r["label"], r["property"], r["source_entry_applicability"]) for r in declared}),
        "declarations": len(declared), "witnessed_access_sites": None, "witnessed_data_versions": None}
    if records is None:
        return result
    inputs, locals_ = defaultdict(set), defaultdict(set)
    origins = {r["id"]: r["origin"].get("acquired_from") for r in data}
    wires, _ = op_sources(mapping)
    incoming = {r["instruction_id"] for r in declared if r["value"]["kind"] == "input"}
    adapter = TypeAdapter(AtomicOp)
    for k, r in recorded_ops(compiled, records).items():
        op = r["op"]
        if op["op"] == "placeholder":
            continue
        for _, _, recorded in r["rows"]:
            if recorded.get("skipped_case_inputs"):
                continue
            if r["ir"] in incoming:
                for ref, values in operand_slots(op, recorded, adapter):
                    if ref["kind"] == "input":
                        inputs[r["ir"], ref["index"]].update(values)
            if op["op"] in {"read", "receive"}:
                locals_[wires.get(k)].update(v for slot in recorded["outputs"] for v in slot)
    witnessed, versions = set(), set()
    for aid, row in declarations.items():
        iid, value, source = row["instruction_id"], row["value"], row["source_entry_location"]
        if value["kind"] == "input":
            at_entry = {v for b in records.get(iid, {}).get("entry_state", {}).get("bindings", [])
                        if b["location"]["kind"] + ":" + b["location"]["name"] == source for v in b["data_ids"]}
            ids = inputs[iid, value["index"]] & at_entry
        else:
            ids = locals_[json_pointer("ir_semantics", iid, *access[aid]["operation_path"])]
        found = {v for v in ids if origins.get(v) == source}
        if found:
            witnessed.add(aid)
            versions.update(found)
    return {**result, "witnessed_access_sites": len(witnessed), "witnessed_data_versions": len(versions)}


def review_activity(ev, selected):
    reviews = {}
    for directory in ("review", "revision/review"):
        stored = ev.optional(ev.run / directory / "result.json")
        if stored is None:
            continue
        review = stored.get("review") or {}
        checks = review.get("gap_checks")
        reviews[directory] = {"status": stored.get("status"), "findings": len(review["findings"]) if "findings" in review else None,
            "gap_checks": None if checks is None else distribution(r["disposition"] for r in checks),
            "masked_boundaries": None if checks is None else distribution(r["masked_boundary"] for r in checks if r.get("masked_boundary") != "none" and r.get("masked_boundary")),
            "missing_cfg_actions": None if checks is None else sum(r.get("cfg_action_missing", False) for r in checks)}
    scope = ev.optional(ev.run / "revision/processing-scope.json")
    gap_slots = {i for i, s in (scope or {}).get("slots", {}).items() if s.get("unmodeled_gaps")}
    target = ev.optional(ev.run / "steps/revision-processing/result.json")
    revised = None
    if target and target.get("value_file"):
        revised = ev.read(ev.inside(ev.run / "steps/revision-processing", target["value_file"]), target["value_sha256"])
    def remained(form):
        if scope is None or form is None:
            return None
        return len(gap_slots & {g["instruction_id"] for g in form.get("processing_gaps", []) if g.get("unmodeled")})
    return {"reviews": reviews, "unmodeled_revision_slots": len(gap_slots) if scope else None,
            "still_unmodeled_after_revision": remained(revised), "still_unmodeled_in_selection": remained(selected)}


def summary(run):
    ev = Evidence(run)
    status = ev.optional(ev.run / "result.json") or {}
    sources = checked_sources(ev)
    pin, cfg, owners, compiled, mapping, prop, records = selection(ev)
    data = ev.read(ev.run / "propagation/data.json", prop["artifacts"]["data.json"]) if prop else None
    formal = ev.optional(ev.run / "doe/manifest.json")
    demand = doe = None
    if formal:
        if not prop or (formal["upstream"]["manifest_sha256"] != prop["manifest_sha256"]
                        or ev.inside(ev.run / "doe", formal["upstream"]["path"]) != ev.run / "propagation"):
            raise ValueError("DOE material belongs to another propagation owner")
        demand, doe = [ev.read(ev.run / "doe" / path, formal["artifacts"][path])
                       for path in ("audit/demand-support.json", "doe-result.json")]
    receipt = ev.optional(ev.run / "audit/input-contract-review.json")
    metrics = ev.optional(ev.run / "metrics.json")
    processing, sensitivity = owners.get("processing"), owners.get("sensitivity")
    coverage = Counter(prop["coverage"].values()) if prop is not None else None
    def propagation():
        if coverage is None:
            return None
        return {"status": prop["status"], "exact_ir": coverage["processed"], "placeholder_ir": coverage["processed_with_placeholder"],
            "executed_whole_barrier_ir": coverage["unmodeled"], "blocked_ir": coverage["blocked"], "coverage": dict(coverage),
            "diagnostic_codes": distribution(r["code"] for r in prop["diagnostics"])}
    physical = physical_evidence(ev, sources, cfg, compiled, mapping, prop, records, data)
    accounting = None
    if metrics is not None:
        accounting = {k: metrics.get(k) for k in ("logical_requests", "native_process_starts",
            "unknown_native_process_starts", "inputs_rejected_before_start", "network_retry_attempts", "known_token_usage",
            "partial_token_usage", "unknown_usage_requests", "total_usage_known", "wall_clock_seconds")}
        def request_kind(row):
            stage = Path(row["logical_request"]).parts[1]
            if stage.startswith("revision"):
                return "shared_revision_correction" if row["structural_correction"] else "shared_revision"
            return "correction" if row["structural_correction"] else "normal"
        accounting["native_by_kind"] = distribution(request_kind(row) for row in metrics["requests"] if row.get("native_process_started") is True)
        accounting["logical_by_kind_in_transport"] = distribution(request_kind(row) for row in
            {r["logical_request"]: r for r in metrics["requests"]}.values())
    return {"identity": "ga4-action-alignment-assessment-v1", "run": str(ev.run), "status": status.get("status"),
        "stage": status.get("stage"), "stages": status.get("stages"), "selection": pin or None,
        "cfg_ir": len(instructions(cfg)) if cfg else None, "source_files": len(sources) if sources else None,
        "selected_declared_whole_gaps": len({r["instruction_id"] for r in compiled.get("processing_gaps", []) if r.get("unmodeled")}) if compiled else None,
        "physical_evidence": physical, "propagation": propagation(), "gap_review": review_activity(ev, processing),
        "selected_contract_review": ({"status": receipt["review_status"], "complete": receipt["source_review_complete"],
            "findings": len(receipt["review_core"]["findings"]), "checks": distribution(x["status"] for x in receipt["checks"]),
            "receipt_sha256": receipt["receipt_sha256"], "demand_uses_receipt": demand["input_contract_review_sha256"] == receipt["receipt_sha256"] if demand else None} if receipt else None),
        "input_assessments": ({"status": demand["status"], "inputs": len(demand["input_assessments"]),
            "ranges": {**dict.fromkeys(("required", "deletable", "unresolved"), 0),
                       **distribution(r["status"] for a in demand["input_assessments"] for r in a["ranges"])},
            "coverage": distribution(a["coverage"] for a in demand["input_assessments"])} if demand else None),
        "sensitivity": sensitive(sensitivity["declarations"], cfg, processing, compiled, mapping, records, data) if sensitivity is not None else None,
        "doe": ({"status": doe["status"], "sinks": len(doe["sinks"]), "candidate_count": sum(len(s["data_reviews"]) for s in doe["sinks"]),
            "conclusions": distribution(r["conclusion"] for s in doe["sinks"] for r in s["data_reviews"])} if doe else None),
        "doe_file_bytes": {p.name: p.stat().st_size for p in (ev.run / "doe").glob("*") if p.name in {"report.html", "report.md", "doe-result.json"}},
        "accounting": accounting,
        "controller": ev.optional(ev.run / "controller-finished.json"), "material_checks": ev.artifacts, "locator_issues": ev.issues}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--run", type=Path, required=True)
    args = cli.parse_args()
    if not args.run.is_dir():
        cli.error("Run directory does not exist")
    print(json.dumps(summary(args.run), ensure_ascii=True, allow_nan=False, indent=2))
