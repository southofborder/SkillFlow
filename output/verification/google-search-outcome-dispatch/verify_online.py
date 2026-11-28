"""Verify the selected google-search run from its saved files. No analysis is dispatched."""
import argparse
import ast
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "google-search-full-20261125"))
import render_annotation_inventory as inventory
sys.path.insert(0, str(HERE.parent / "google-search-call-routing-20261125"))
from check_entry_paths import describe


def source_contract(lines):
    """Locate the operations in the packaged source without importing the script."""
    tree = ast.parse("\n".join(lines))
    function, = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "google_search"]
    assignments = {n.targets[0].id: n.value for n in function.body if isinstance(n, ast.Assign)
                   and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
    request, = [n for n in ast.walk(function) if isinstance(n, ast.Call)
                and ast.unparse(n.func) == "requests.get"]
    url = assignments[request.args[0].id]
    params = assignments[next(k.value.id for k in request.keywords if k.arg == "params")]
    handlers = [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler) and ast.unparse(n.type) == "Exception"]
    printer, = [n for h in handlers for n in ast.walk(h) if isinstance(n, ast.Call) and ast.unparse(n.func) == "print"]
    env_key, = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and ast.unparse(n.func) == "os.getenv"
                and isinstance(n.args[0], ast.Constant) and n.args[0].value == "GOOGLE_API_KEY"]
    return {"file": "skill/scripts/search.py", "request_line": request.lineno, "error_print_line": printer.lineno,
            "public_parameters_line": function.lineno, "cli_key_read_line": env_key.lineno,
            "endpoint": ast.literal_eval(url), "fields": {ast.literal_eval(k): v.id for k, v in zip(params.keys, params.values)}}


def source_spans(ir):
    meta = ir.get("metadata", {})
    return [a["source"] for a in meta.get("source_actions", []) if a.get("source")] or (
        [meta["source_span"]] if meta.get("source_span") else [])


def source_occurrence(ir, source, line, site):
    if ir["opcode"] in {"dispatch", "return"}:
        return False
    def exact(s):
        return s.get("file") == source and s.get("start_line") == line == s.get("end_line")
    actions = ir.get("metadata", {}).get("source_actions", [])
    roles = {"call", "receive", "deliver"} if site == "request" else {"call", "deliver"}
    if any(exact(a.get("source", {})) and (a.get("role") or a.get("kind")) in roles for a in actions):
        return True
    if not any(exact(s) for s in source_spans(ir)):
        return False
    opcode = ir["opcode"].lower()
    return (ir.get("metadata", {}).get("method") == "get" or any(w in opcode for w in ("request", "get", "http", "call"))
            if site == "request" else any(w in opcode for w in ("print", "deliver", "stdout")))


def operations(record):
    for e, event in enumerate(record.get("events", [])):
        if event.get("kind") == "for_each":
            for i, instance in enumerate(event["instances"]):
                for b, inner in enumerate(instance.get("body", [])):
                    for j, op in enumerate(inner.get("atomic_ops", [])):
                        yield (e, b, i, j), inner, op
        else:
            for j, op in enumerate(event.get("atomic_ops", [])):
                yield (e, None, None, j), event, op


def contents(data, identity):
    content = data.get(identity, {}).get("content", {})
    return ([v["content"] for v in content["variants"]] if content.get("form") == "loop_summary" else [content])


def fields(data, identity, names, prefix=(), seen=frozenset()):
    """Only explicit field embeddings and whole-value aliases establish member versions."""
    if identity in seen:
        return
    seen = seen | {identity}
    for value in contents(data, identity):
        if value.get("form") == "selection" and not value.get("path"):
            yield from fields(data, value["base"], names, prefix, seen)
        elif value.get("form") == "known_parts":
            for part in value.get("parts", []):
                path = [*prefix, *part["path"]]
                if path and isinstance(path[-1], str) and path[-1] in names:
                    yield path, part["data"]
                else:
                    yield from fields(data, part["data"], names, path, seen)


def origins(data, identity):
    """Follow recorded dependencies without claiming their plaintext survives a computation."""
    pending, seen, roots = [identity], set(), {}
    while pending:
        current = pending.pop()
        if current in seen or current not in data:
            continue
        seen.add(current)
        item = data[current]
        origin = item.get("origin", {})
        if origin.get("acquired_from"):
            roots[current] = origin["acquired_from"]
        if origin.get("part_of"):
            pending.append(origin["part_of"])
        pending.extend(origin.get("inputs", []))
        for variant in item.get("content", {}).get("variants", []):
            if variant.get("acquired_from"):
                roots[current] = variant["acquired_from"]
            pending.extend(variant.get("inputs", []))
    return [{"data_id": k, "acquired_from": v} for k, v in sorted(roots.items())]


def explicit_sources(sensitivity, identity, data):
    seen, roots, pending = set(), {}, [identity]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        row = sensitivity[current]
        if "explicit_declaration" in row["rules"]:
            roots[current] = {"derivation_id": current, "declaration_id": row["declaration_id"],
                "data_id": row["data_id"], "label": row["label"], "path": row["path"],
                "upstream_acquisitions": origins(data, row["data_id"])}
        pending.extend(row["parents"])
    return [roots[k] for k in sorted(roots)]


def inspect_site(ir, block, site, activations, contract, inv, by_ir, demands, data):
    key = ir["id"]
    forward = inv["forward"]
    declared = inv["artifacts"]["audit/compiled-response.json"].get("sink_boundaries", [])
    record = forward.get("records.json", {}).get(key, {})
    sensitivity = inv["backward"].get("doe-result.json", {}).get("derivations", {}).get("sensitivity", {})
    declarations = inv["backward"].get("audit/index.json", {}).get("declarations", {})
    by_position = defaultdict(list)
    for sink in by_ir[key]:
        for payload in sink["actual_payload"]:
            pos = payload["position"]
            by_position[(pos["event_index"], pos.get("body_event_index"), pos.get("instance_index"), pos["op_index"])].append((sink, payload))
    operations_seen = []
    for coord, event, op in operations(record):
        if op["op"] != "deliver" or op.get("skipped_case_inputs"):
            continue
        end = op.get("endpoints", [])
        if not end:
            continue
        e, b, i, j = coord
        case = event.get("case") or {}
        row = {"position": {"instruction_id": key, "event_index": e, "body_event_index": b, "instance_index": i,
                            "op_index": j}, "endpoints": end, "case_id": case.get("id"), "phase": case.get("phase"),
               "input_versions": op["inputs"], "members": [], "comparisons": []}
        for slot, versions in enumerate(op["inputs"]):
            for version in versions:
                for path, child in fields(data, version, contract["fields"]):
                    member = {"slot": slot, "path": path, "payload_data_id": version, "member_data_id": child,
                              "upstream_acquisitions": origins(data, child)}
                    if member not in row["members"]:
                        row["members"].append(member)
        row["doe_boundaries"] = []
        for sink, payload in by_position[coord]:
            if payload["inputs"] != op["inputs"]:
                raise ValueError(f"DOE operation versions disagree with propagation at {key}/{coord}")
            row["doe_boundaries"].append({"sink_id": sink["id"], "operation_id": payload["operation_id"],
                "target": sink["boundary"]["target"], "related_requirement_ids": sink["related_requirements"]})
            for review in sink["data_reviews"]:
                if review["operation_id"] != payload["operation_id"]:
                    continue
                slot, sid = review["input_index"], review["derivation_id"]
                signal = sensitivity[sid]
                if signal["data_id"] not in op["inputs"][slot]:
                    raise ValueError(f"Sensitivity version differs from actual payload at {key}/{coord}/{slot}")
                sources = explicit_sources(sensitivity, sid, data)
                for source in sources:
                    source["declaration_location"] = declarations.get(source["declaration_id"])
                row["comparisons"].append({"id": review["id"], "operation_id": payload["operation_id"],
                    "slot": slot, "payload_data_id": signal["data_id"], "path": signal["path"],
                    "relation": signal["relation"], "property": signal["property"], "label": signal["label"],
                    "derivation_id": sid, "declared_sources": sources,
                    "conclusion": review["conclusion"], "reduction": review.get("reduction"),
                    "demand_refs": review["demand_refs"], "limitation_refs": review["limitation_refs"]})
        # Independently retain actual op/slot/path demands, including fields with no sensitivity comparison.
        row["task_demands"] = []
        for did, demand in demands.get((key, e, b, i, j), []):
            node = demand["node"]
            slot = node["slot"]
            if slot is None or slot >= len(op["inputs"]):
                continue
            versions = sorted(set(demand.get("outcome_data_ids", node["data_ids"])).intersection(op["inputs"][slot]))
            if not versions:
                continue
            row["task_demands"].append({"id": did, "requirement_id": demand["requirement_id"],
                "goal_id": demand["seed_goal_id"], "operation_id": node["operation_id"], "slot": slot,
                "path": demand["path"], "property": demand["property"], "conservative": demand["conservative"],
                "payload_versions": versions})
        operations_seen.append(row)
    spec = inv["artifacts"]["audit/compiled-response.json"]
    return {"ir": key, "opcode": ir["opcode"], "block": block, "source": source_spans(ir),
        "site": site, "activation_candidates": activations,
        "coverage": inv["propagation"].get("coverage", {}).get(key), "record_present": bool(record),
        "declared_boundaries": [b for b in declared if b["instruction_id"] == key],
        "propagation_boundaries": [s for s in forward.get("sinks.json", []) if s["instruction_id"] == key],
        "deliveries": operations_seen, "outcomes": record.get("outcomes", []),
        "processing_gaps": [g for g in spec.get("processing_gaps", []) if g["instruction_id"] == key]}


def is_api_key(signal):
    for root in signal["declared_sources"]:
        labels = [root["label"], *(entry["acquired_from"] for entry in root["upstream_acquisitions"])]
        for text in labels:
            clean = text.lower().replace("_", " ").replace("-", " ")
            if "api key" in clean or "api authentication credential" in clean:
                return True
    return False


def key_ingress(graph, records, data, contract):
    result = {"CLI": [], "public": []}
    for block in graph["blocks"].values():
        for ir in block["instructions"]:
            if ir["opcode"] in {"dispatch", "return"}:
                continue
            spans = {(s["start_line"], s["end_line"]) for s in source_spans(ir) if s["file"] == contract["file"]}
            for who, line in (("CLI", contract["cli_key_read_line"]), ("public", contract["public_parameters_line"])):
                if (line, line) not in spans:
                    continue
                actual = set()
                record = records.get(ir["id"], {})
                output_names = {out["identifier"] for out in ir["outputs"]}
                for binding in record.get("exit_state", {}).get("bindings", []):
                    loc = binding["location"]
                    if loc["kind"] == "result" and loc["name"] in output_names:
                        actual.update(binding["data_ids"])
                for _, _, op in operations(record):
                    if op["op"] in {"read", "receive"} and not op.get("skipped_case_inputs"):
                        actual.update(ident for slot in op["outputs"] for ident in slot)
                # Never count ambient context present before an operation as a completed read.
                actual = {ident for ident in actual if "api_key" in
                          (data.get(ident, {}).get("origin", {}).get("acquired_from") or "").lower()}
                result[who].append({"instruction_id": ir["id"], "line": line, "record_present": bool(record),
                                    "actual_key_data_ids": sorted(actual)})
    return result


def summarize_site(site, contract, data):
    if site["site"] == "exception_print":
        prints = [d for d in site["deliveries"] if any(
            "stdout" in end["name"].lower() or "standard output" in end["name"].lower() for end in d["endpoints"])]
        signals = [r for op in prints for r in op["comparisons"] if is_api_key(r)]
        return {"stdout_delivery_recorded": bool(prints),
                "key_signal_comparison_ids": [r["id"] for r in signals],
                "key_signal_relations": dict(Counter(r["relation"] for r in signals)),
                "finding": "recorded_sensitivity_signal" if signals else "api_key_content_not_established"}
    sends = [op for op in site["deliveries"] if any(end["kind"] == "remote" for end in op["endpoints"])]
    endpoints = sorted({end["name"] for op in sends for end in op["endpoints"] if end["kind"] == "remote"})
    url_ids = set()
    for op in sends:
        for slot in op["input_versions"]:
            for identity in slot:
                candidates = [identity, *(member for _, member in fields(data, identity, {"url"}))]
                for candidate in candidates:
                    if any(c.get("form") == "literal" and c.get("value") == contract["endpoint"]
                           for c in contents(data, candidate)):
                        url_ids.add(candidate)
    checks = {}
    for name in contract["fields"]:
        members, comparison_ids, source_ids, demand_ids, reqs = set(), set(), set(), set(), set()
        for op in sends:
            for member in op["members"]:
                if member["path"][-1] == name:
                    members.add(member["member_data_id"])
            for comparison in op["comparisons"]:
                if comparison["path"] and comparison["path"][-1] == name:
                    comparison_ids.add(comparison["id"])
                    for root in comparison["declared_sources"]:
                        source_ids.add(root["data_id"])
            for demand in op["task_demands"]:
                if demand["path"] and demand["path"][-1] == name and not demand["conservative"]:
                    demand_ids.add(demand["id"])
                    reqs.add(demand["requirement_id"])
        checks[name] = {"source_formal": contract["fields"][name], "recorded_member_data_ids": sorted(members),
            "comparison_ids": sorted(comparison_ids), "sensitivity_declaration_data_ids": sorted(source_ids),
            "precise_task_requirement_ids": sorted(reqs), "precise_demand_ids": sorted(demand_ids)}
    return {"remote_send_recorded": bool(sends), "recorded_recipients": endpoints,
        "endpoint_name_matches_source_url": contract["endpoint"] in endpoints,
        "matching_url_argument_data_ids": sorted(url_ids), "fields": checks}


def verify(run):
    run = run.resolve()
    result = inventory.load(run / "result.json") if (run / "result.json").is_file() else {}
    report = {"run": run.name, "run_status": result.get("status"), "stage": result.get("stage"),
              "scope": "Saved static model results. A source anchor or a selected CFG edge alone cannot establish delivery."}
    selected = inventory.load(run / "selection.json") if (run / "selection.json").is_file() else {}
    if not all(isinstance(selected.get(key), dict) and selected[key].get("path") and selected[key].get("sha256")
               for key in ("task", "cfg", "annotation")) or not result:
        return {**report, "verification_status": "no_final_selection", "sites": None, "propagation": None,
                "doe": None, "limitations": result.get("limitations", []),
                "stage_statuses": {k: v.get("status") for k, v in result.get("stages", {}).items()}}
    inv = inventory.load_inventory(run, run)
    graph, task, prop = inv["graph"], inv["task"], inv["propagation"]
    contract = source_contract(inventory.read_sources(run)["skill/scripts/search.py"])
    routes = describe(graph)
    doe = inv["backward"].get("doe-result.json", {})
    support = inv["backward"].get("audit/demand-support.json", {})
    all_demands = {**support.get("extra_derivations", {}), **doe.get("derivations", {}).get("demand", {})}
    op_positions = {}
    by_ir = defaultdict(list)
    for sink in doe.get("sinks", []):
        by_ir[sink["boundary"]["instruction_id"]].append(sink)
        for payload in sink["actual_payload"]:
            p = payload["position"]
            op_positions[payload["operation_id"]] = (p["instruction_id"], p["event_index"], p.get("body_event_index"),
                                                    p.get("instance_index"), p["op_index"])
    demands = defaultdict(list)
    for did, d in all_demands.items():
        if d["node"]["kind"] == "op_input" and d["node"]["operation_id"] in op_positions:
            demands[op_positions[d["node"]["operation_id"]]].append((did, d))
    data = {d["id"]: d for d in inv["forward"].get("data.json", [])}
    ingress = key_ingress(graph, inv["forward"].get("records.json", {}), data, contract)
    task_by_id = {r["id"]: r for r in task["requirements"]}
    sites = []
    for block, body in graph["blocks"].items():
        for ir in body["instructions"]:
            for name, stage in (("request_line", "request"), ("error_print_line", "error_output")):
                site = "request" if stage == "request" else "exception_print"
                if source_occurrence(ir, contract["file"], contract[name], site):
                    acts = [act for act, reachable in routes["reachable_sites"].items() if block in reachable[stage]]
                    item = inspect_site(ir, block, site, acts, contract, inv, by_ir, demands, data)
                    item["field_verification"] = summarize_site(item, contract, data)
                    line = contract[name]
                    item["source_cited_requirement_ids"] = [rid for rid, req in task_by_id.items() if any(
                        ev.get("file") == contract["file"] and ev["start_line"] <= line <= ev["end_line"]
                        for ev in req.get("evidences", []))]
                    if site == "request":
                        checks = item["field_verification"]["fields"]["key"]
                        candidates = set(checks["sensitivity_declaration_data_ids"]) | set(checks["recorded_member_data_ids"])
                        checks["matched_source_version_ids_by_entry"] = {
                            who: sorted(candidates.intersection(ident for read in evidence for ident in read["actual_key_data_ids"]))
                            for who, evidence in ingress.items()}
                    if any(d["requirement_id"] not in task_by_id for op in item["deliveries"] for d in op["task_demands"]):
                        raise ValueError("A delivery demand refers to a requirement absent from the selected Task")
                    sites.append(item)
                    break
    specs = inv["artifacts"]["audit/compiled-response.json"]
    diagnostics = prop.get("diagnostics", [])
    gaps = defaultdict(list)
    for gap in specs.get("processing_gaps", []):
        gaps[gap["instruction_id"]].append(gap["reason"])
    blockers = [{"code": d["code"], "ir": d.get("instruction_id"), "reason": d.get("reason"),
                 "gap_reasons": gaps[d.get("instruction_id")], "affected_count": len(d.get("affected_instruction_ids", []))}
                for d in diagnostics]
    reviews = [r for s in doe.get("sinks", []) for r in s["data_reviews"]]
    return {**report, "verification_status": "selected", "selection": inv["selection"], "source": contract,
            "task_sha256": task["task_sha256"], "requirements": task["requirements"],
            "source_entry_blocks": routes["entries"], "structural_checks": routes["checks"],
            "source_key_ingress": ingress, "sites": sites,
            "propagation": {"status": prop.get("status"), "coverage": dict(Counter(prop["coverage"].values())),
                "ir_count": len(prop["coverage"]), "record_count": len(inv["forward"]["records.json"]),
                "declared_boundaries": len(specs.get("sink_boundaries", [])), "recorded_boundaries": len(inv["forward"]["sinks.json"]),
                "blockers": sorted(blockers, key=lambda item: -item["affected_count"])} if prop else None,
            "doe": {"status": doe["status"], "sink_count": len(doe["sinks"]), "comparison_count": len(reviews),
                "conclusions": dict(Counter(r["conclusion"] for r in reviews)),
                "reductions": [{"comparison_id": r["id"], "reduction": r["reduction"]} for r in reviews if r.get("reduction")],
                "blocking_diagnostic_counts": dict(Counter(d["code"] for d in doe.get("diagnostics", []) if d.get("blocking")))} if doe else None}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "boundary-verification.json")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    report = verify(args.run)
    if not args.check_only:
        if args.output.resolve().is_relative_to(args.run.resolve()):
            parser.error("Write the report outside the source run directory.")
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run": report["run"], "status": report["verification_status"],
                      "sites": len(report["sites"]) if report["sites"] is not None else None,
                      "doe": report["doe"]}, ensure_ascii=True))
