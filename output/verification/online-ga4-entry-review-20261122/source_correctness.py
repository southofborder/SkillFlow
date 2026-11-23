"""Read-only GA4 source acceptance. Usage: python -B source_correctness.py --run PATH [--summary]

Print JSON on stdout. No SkillFlow imports, generation, publication, replay or
file writes. The previous audit supplies source questions, never new answers.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "online-ga4-lossless-delivery-20261119"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PREVIOUS))
from source_boundary_audit import Evidence, digest, instructions, legacy_spans, selected_spans, source_sites


def endpoint_matches(name, method):
    return re.sub("[^a-z0-9]", "", method.lower()) in re.sub("[^a-z0-9]", "", name.lower())


def recorded_ops(compiled, records):
    """Join execution positions to the exact compiled event and lexical scope."""
    ops = {}
    for ir, spec in compiled.get("ir_semantics", {}).items():
        actual = records.get(ir, {}).get("events", [])
        def add(event, prefix, runtime, scope):
            for j, op in enumerate(event["atomic_ops"]):
                path = f"/ir_semantics/{ir}/{prefix}/atomic_ops/{j}"
                rows = []
                for instance, base, r in runtime:
                    if j < len(r["atomic_ops"]):
                        a = r["atomic_ops"][j]
                        if a["op"] != op["op"]:
                            raise ValueError("Record/annotation disagreement at " + path)
                        rows.append((instance, f"{base}/atomic_ops/{j}", a))
                ops[path] = {"ir": ir, "scope": scope, "case": event.get("case"), "op": op, "rows": rows}
        for i, event in enumerate(spec["events"]):
            rec = actual[i] if i < len(actual) else None
            if event.get("kind") == "for_each":
                for k, body in enumerate(event["body"]):
                    rt = [(n, f"/{ir}/events/{i}/instances/{n}/body/{k}", entry["body"][k])
                          for n, entry in enumerate((rec or {}).get("instances", [])) if k < len(entry["body"])]
                    add(body, f"events/{i}/body/{k}", rt, i)
            else:
                add(event, f"events/{i}", [] if rec is None else [(None, f"/{ir}/events/{i}", rec)], None)
    return ops


def alternatives(row):
    return {(json.dumps(a["inputs"], sort_keys=True), json.dumps(a["bindings"], sort_keys=True))
            for a in row.get("alternatives", [])}


def check_pair(key, operations, locations):
    rec = operations[key]
    receive = rec["op"]
    endpoint = locations[receive["location"]]
    expected = [{"kind": endpoint["kind"], "name": endpoint["name"]}]
    matches = [p for p, d in operations.items() if d["ir"] == rec["ir"] and d["scope"] == rec["scope"]
               and d["case"] == rec["case"] and d["op"]["op"] == "deliver"
               and receive.get("request_id") and d["op"].get("request_id") == receive["request_id"]
               and d["op"]["target"] == receive["location"] and d["op"]["inputs"] == receive["inputs"]]
    replies = [p for p, o in operations.items() if o["ir"] == rec["ir"] and o["op"]["op"] == "receive"
               and o["op"].get("request_id") == receive.get("request_id")]
    result = {"receive": key, "location": receive["location"], "endpoint": endpoint["name"],
              "request_id": receive.get("request_id"), "deliver_matches": matches, "ordered_inputs": receive["inputs"],
              "declared": "confirmed" if len(matches) == len(replies) == 1 else "missing_or_ambiguous_pair",
              "recorded": "unreached", "occurrences": []}
    if result["declared"] != "confirmed":
        result["recorded"] = "no_unique_declared_pair"
        return result
    requests = {i: (path, row) for i, path, row in operations[matches[0]]["rows"]}
    receipts = {i: (path, row) for i, path, row in rec["rows"]}
    for i in sorted(requests.keys() | receipts.keys(), key=str):
        dp, d = requests.get(i, (None, {}))
        rp, r = receipts.get(i, (None, {}))
        confirmed = bool(r.get("outputs") and any(r["outputs"]) and d.get("endpoints") == r.get("endpoints") == expected
                         and d.get("inputs") == r.get("inputs") and alternatives(d) == alternatives(r))
        result["occurrences"].append({"instance": i, "deliver_record": dp, "receive_record": rp,
                                     "same_endpoint_args_and_alternatives": confirmed,
                                     "response_data": sorted({x for group in r.get("outputs", []) for x in group})})
    if result["occurrences"]:
        result["recorded"] = "confirmed" if all(a["same_endpoint_args_and_alternatives"] for a in result["occurrences"]) else "not_established"
    return result


class Traces:
    """Follow explicit lexical result bindings and selections. Opaque value transforms stop proof."""
    def __init__(self, cfg, compiled, ops):
        self.cfg, self.specs, self.ops = instructions(cfg), compiled.get("ir_semantics", {}), ops
        self.definitions = {v["identifier"]: (ir, i) for ir, ins in self.cfg.items() for i, v in enumerate(ins["outputs"])}
        self.locals = {(r["ir"], r["scope"], r["op"]["output"]): key for key, r in ops.items() if "output" in r["op"]}
        self.cache = {}

    def ref(self, ir, scope, value, seen=frozenset()):
        if value["kind"] == "alternatives":
            branches = [self.ref(ir, scope, item, seen) for item in value["items"]]
            return [x for group, _ in branches for x in group], all(ok for _, ok in branches)
        if value["kind"] == "input":
            operand = self.cfg[ir]["inputs"][value["index"]]
            owner = self.definitions.get(operand["identifier"]) if operand["type"] == "result" else None
            if not owner or owner in seen:
                return [], False
            parent, index = owner
            bind = next((b for b in self.specs.get(parent, {}).get("output_bindings", []) if b["output_index"] == index), None)
            return self.ref(parent, None, bind["value"], seen | {owner}) if bind else ([], False)
        if value["kind"] != "local":
            return [], False
        key = self.locals.get((ir, scope, value["name"])) or self.locals.get((ir, None, value["name"]))
        if not key or key in seen:
            return [], False
        if key in self.cache:
            return self.cache[key]
        entry = self.ops[key]
        op = entry["op"]
        if op["op"] == "receive":
            data = {x for _, _, r in entry["rows"] for out in r.get("outputs", []) for x in out}
            result = [(key, (), key, data)], True
        elif op["op"] == "select_part":
            parents, complete = self.ref(ir, scope, op["input"], seen | {key})
            traced = []
            for root, path, _, actual in parents:
                # Occurrence-wide candidate sets cannot prove member pairing. The
                # static relation remains visible when that stronger witness is absent.
                data = set()
                if scope is None:
                    for _, _, r in entry["rows"]:
                        for alternative in r.get("alternatives") or [r]:
                            if alternative["inputs"][0] and set(alternative["inputs"][0]) <= actual:
                                data.update(x for group in alternative["outputs"] for x in group)
                traced.append((root, (*path, *op["path"]), key, data))
            result = traced, complete
        else:
            return [], False
        self.cache[key] = result
        return result


def expected_fields(site):
    method = site["method"]
    if method in {"runReport", "runRealtimeReport", "getMetadata"}:
        result = [[0]]
        if site["function"] in {"getAvailableDimensions", "getAvailableMetrics"}:
            result.append([0, "dimensions" if site["function"] == "getAvailableDimensions" else "metrics"])
        return result
    if method == "searchanalytics.query":
        return [["data"]]
    if method == "urlNotifications.publish":
        field = "latestRemove" if "URL_DELETED" in site["source_call"] else "latestUpdate"
        return [["data", "urlNotificationMetadata", "url"], ["data", "urlNotificationMetadata", field, "notifyTime"]]
    if method == "urlInspection.index.inspect":
        return [["data", "inspectionResult"]]
    raise ValueError("Unrecognized frozen GA4 method: " + method)


def field_citation(site, field, sources):
    lines = sources[site["file"]]["text"].splitlines()
    lhs = "response"
    tail = field
    if field[0] == 0:
        tail = field[1:]
    needle = lhs + "".join("." + k for k in tail)
    for i in range(site["start_line"] - 1, min(site["end_line"] + 18, len(lines))):
        line = lines[i].replace("?.", ".")
        if (tail and needle in line) or (not tail and re.search(r"const\s*\[response\]\s*=\s*await", line)):
            return {"file":site["file"],"line":i+1,"text":lines[i].strip()}
    raise ValueError("Missing source field citation for " + str((site["function"], field)))


def receiver_citations(site, sources):
    file = site["file"]
    lines = sources[file]["text"].splitlines()
    for i in range(site["start_line"] - 1, -1, -1):
        match = re.search(r"\bconst\s+" + re.escape(site["receiver_text"]) + r"\s*=\s*(\w+)\(\)", lines[i])
        if not match:
            continue
        helper = "scripts/src/core/client.ts"
        source = sources[helper]["text"].splitlines()
        start = next(n for n,v in enumerate(source) if re.search(r"\bfunction\s+"+re.escape(match[1])+r"\(",v))
        end = next(n for n in range(start+1, len(source)) if source[n].startswith("}"))
        return [{"file":file,"line":i+1,"text":lines[i].strip()},
                {"file":helper,"lines":[start+1,end+1],"function":match[1]}]
    raise ValueError("The source receiver could not be located in " + site["function"])


def audit(run):
    ev = Evidence(run)
    original = PREVIOUS / "initial-source-correctness-audit.json"
    baseline = json.loads(original.read_bytes())
    snapshot = ev.read(ev.run / "source/inputs/snapshot.json")
    sources = {}
    for item in snapshot["files"]:
        content = ev.inside(ev.run / "source/inputs/package", item["path"]).read_bytes()
        sha = digest(content)
        if sha != item["raw_sha256"]:
            raise ValueError("Frozen source mismatch at " + item["path"])
        sources[item["path"]] = {"sha256": sha, "text": content.decode("utf-8")}
    if snapshot["source_sha256"] != baseline["source_sha256"] or {p:s["sha256"] for p,s in sources.items()} != baseline["source_file_sha256"]:
        raise ValueError("Source bytes differ from the physically cited GA4 acceptance inventory")
    sites = [s for s in source_sites(sources) if s["category"] == "remote"]
    selection = ev.optional(ev.run / "selection.json") or {}
    bound = lambda ref: ev.read(ev.inside(ev.run, ref["path"]), ref["sha256"])
    cfg = bound(selection["cfg"])["cfg"] if selection.get("cfg") else {}
    old_cfg = (ev.optional(ev.run / "graph/initial.json") or {}).get("cfg", {})
    spans = selected_spans(cfg, old_cfg, legacy_spans(ev, old_cfg, sources), sources) if cfg and old_cfg else {}
    irs = instructions(cfg)
    compiled, records, coverage = {}, {}, {}
    if selection.get("annotation"):
        ann = bound(selection["annotation"])
        owner = ev.inside(ev.run, selection["annotation"]["path"]).parent
        refs = ev.read(owner / "inputs/references.json", ann["files"]["inputs/references.json"])
        if (refs["cfg"]["sha256"] != selection["cfg"]["sha256"]
                or ev.inside(owner, refs["cfg"]["path"]) != ev.inside(ev.run, selection["cfg"]["path"])
                or ev.inside(owner, refs["source_owner"]["path"]) != ev.run / "source"
                or refs["source_owner"]["manifest_sha256"] != ev.read(ev.run / "source/manifest.json")["manifest_sha256"]):
            raise ValueError("Selected annotation does not bind this exact CFG and source owner")
        compiled = ev.read(owner / "audit/compiled-response.json", ann["artifacts"]["audit/compiled-response.json"])
        prop = ev.optional(ev.run / "propagation/manifest.json")
        if prop:
            if (prop["upstream"]["manifest_sha256"] != ann["manifest_sha256"] or
                    ev.inside(ev.run / "propagation", prop["upstream"]["path"]) != owner):
                raise ValueError("Propagation records do not bind the selected annotation")
            records = ev.read(ev.run / "propagation/records.json", prop["artifacts"]["records.json"])
            coverage = prop["coverage"]
    ops = recorded_ops(compiled, records)
    locations = compiled.get("locations", {})
    remote = {key:check_pair(key, ops, locations) for key, entry in ops.items()
              if entry["op"]["op"] == "receive" and locations[entry["op"]["location"]]["kind"] in {"remote","tool"}}
    trace = Traces(cfg, compiled, ops)
    selected = defaultdict(list)
    for key, row in ops.items():
        if row["op"]["op"] == "select_part":
            chains, complete = trace.ref(row["ir"], row["scope"], {"kind":"local","name":row["op"]["output"]})
            for root, path, step, data in chains:
                selected[root, path].append({"compiled_pointer": step, "all_ref_branches_trace": complete,
                                             "has_recorded_version_chain": bool(data)})

    def owners(old):
        if selection.get("cfg", {}).get("sha256") == baseline["artifact_sha256"]["graph/initial.json"]:
            return [old["instruction_id"]] if old["instruction_id"] in irs else []
        span = old["source_span"]
        return [ir for ir,s in spans.items() if all(s[k] == span[k] for k in ("file","start_line","end_line"))
                and (not old.get("cfg_opcode") or irs[ir]["opcode"] == old["cfg_opcode"])]

    physical = []
    for site in sites:
        old, = [r for r in baseline["remote_receiver_evidence"] if r["source_span"]["file"] == site["file"]
                and r["source_span"]["start_line"] <= site["start_line"] <= r["source_span"]["end_line"]]
        ids = owners(old)
        ir = ids[0] if len(ids) == 1 else None
        belongs = [k for k in remote if ops[k]["ir"] == ir]
        pairs = [k for k in belongs if endpoint_matches(remote[k]["endpoint"], site["method"])]
        evidence = {"file":site["file"], "lines":[site["start_line"],site["end_line"]],
                    "source_call":site["source_call"], "function":site["function"], "method":site["method"],
                    "authenticated_receiver_source":receiver_citations(site, sources),
                    "selected_instruction_candidates":ids, "coverage":coverage.get(ir,"unreached_or_unavailable"),
                    "pairs":[remote[k] for k in pairs], "other_acquisitions":[{"pointer":k,"endpoint":remote[k]["endpoint"]}
                                                                           for k in belongs if k not in pairs]}
        checks = []
        for k in pairs:
            refs = locations[remote[k]["location"]].get("operand_refs", [])
            expected = old["receiver"].get("operand")
            matched = [r for r in refs if expected and r["instruction_id"] == ir and r["side"] == "input"
                       and irs[ir]["inputs"][r["index"]] == expected]
            checks.append({"receive":k, "endpoint_operand_refs":refs, "matching_handle_refs":matched,
                           "status":"confirmed_static_operand_binding" if matched else
                           "unverified_receiver_identity" if refs else "missing_receiver_binding"})
        evidence["receiver"] = checks
        evidence["call_status"] = "unreached_or_unlocated" if not ir or not compiled else (
            "missing_sdk_call_relation" if not pairs else "unique_method_receive" if len(pairs) == 1 else "multiple_candidate_receives")
        evidence["response_fields"] = []
        for field in expected_fields(site):
            steps = [x for k in pairs for x in selected[k, tuple(field)]]
            evidence["response_fields"].append({"path":field,"source_evidence":field_citation(site, field, sources),"explicit_selects":steps,
                "status":"unreached_or_unlocated" if not ir or not compiled else "no_explicit_select_part_chain" if not steps
                else "recorded_projection" if any(s["has_recorded_version_chain"] for s in steps) else "declared_projection"})
        physical.append(evidence)
    wrappers = []
    for old in baseline["report_output_evidence"]:
        ids = owners(old)
        ir = ids[0] if len(ids) == 1 else None
        bindings = []
        for binding in compiled.get("ir_semantics", {}).get(ir, {}).get("output_bindings", []):
            chains, complete = trace.ref(ir, None, binding["value"])
            routes = [{"receive":key,"path":list(path),"last_producer":step,"observed_data_count":len(data)}
                      for key,path,step,data in chains]
            sdk = bool(routes) and complete and all(ops[r["receive"]]["ir"] == ir and r["receive"] in remote and
                                                endpoint_matches(remote[r["receive"]]["endpoint"], "runReport") for r in routes)
            exact = sdk and all(r["path"] == [0] for r in routes)
            proven_exit = set()
            if exact and ir in records:
                name = irs[ir]["outputs"][binding["output_index"]]["identifier"]
                proven_exit = {d for row in records[ir]["exit_state"]["bindings"] if row["location"] == {"kind":"result","name":name}
                               for d in row["data_ids"]}
            terminal = {d for _,_,_,ds in chains for d in ds}
            bindings.append({"output_index":binding["output_index"], "value":binding["value"], "routes":routes,
                "status":"current_sdk_first_projection" if exact else "direct_sdk_reply_without_declared_projection" if
                sdk and all(not r["path"] for r in routes) else "not_established",
                "recorded_exit_matches_projections": bool(proven_exit) and proven_exit == terminal if exact else None})
        wrappers.append({"source_span":{k:old["source_span"][k] for k in ("file","start_line","end_line")},
                         "source_statement":old["source_statement"], "selected_instruction_candidates":ids,
                         "coverage":coverage.get(ir,"unreached_or_unavailable"),"outputs":bindings})
    summary = {"physical_source_sites":len(physical), "sites_with_unique_declared_pair":sum(
        len(s["pairs"]) == 1 and s["pairs"][0]["declared"] == "confirmed" for s in physical),
        "sites_with_unique_recorded_pair":sum(len(s["pairs"]) == 1 and s["pairs"][0]["recorded"] == "confirmed" for s in physical),
        "receiver_checks":dict(Counter(r["status"] for s in physical for r in s["receiver"])),
        "response_projection_checks":dict(Counter(r["status"] for s in physical for r in s["response_fields"])),
        "wrapper_source_sites":len(wrappers), "wrapper_output_checks":dict(Counter(r["status"] for s in wrappers for r in s["outputs"]))}
    return {"identity":"ga4-selected-source-correctness-v1", "run":str(ev.run), "source_sha256":snapshot["source_sha256"],
            "baseline_audit_sha256":digest(original.read_bytes()), "selection":selection,"artifact_hashes":ev.artifacts,
            "summary":summary, "physical_calls":physical,"report_wrappers":wrappers,"locator_issues":ev.issues,
            "limits":["The 13 physical source calls and 19 wrapper questions apply to this byte-identical GA4 source.",
                      "Endpoint names locate candidates. A matching pair requires distinct bound request/response operations and ordered identical arguments. Repeated endpoint names alone cannot identify an authenticated handle.",
                      "Receiver confirmation is static and requires a real endpoint operand bound to the source client. A handle passed as request payload is not a receiver binding.",
                      "An explicit field selection is evidence for that projection. Subsequent fallback, formatting, delivery and all other fields require separate analysis. Missing projection can also mean an undocumented normalized return adapter.",
                      "The trace follows explicit result bindings, alternatives and select_part; opaque, interprocedural, nested-member and transformed return relationships may remain unestablished. No actual network or Skill execution is asserted."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    result = audit(args.run)
    print(json.dumps(result["summary"] if args.summary else result, ensure_ascii=True, indent=2))
