"""Read-only GA4 entry/request/response witnesses. Usage: python -B trace_report.py --run DIR."""
import argparse
from collections import Counter, defaultdict, deque
from functools import lru_cache
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "online-ga4-entry-review-20261122"))
from source_correctness import Evidence, check_pair, digest, instructions, legacy_spans, recorded_ops, selected_spans

SOURCE = "3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd"
REPORTS, INDEX = "scripts/src/api/reports.ts", "scripts/src/index.ts"
SITES = {"getPageViews": (REPORTS, 114, 121), "getTrafficSources": (REPORTS, 125, 132),
         "siteOverview": (INDEX, 55, 76)}
FIELDS = {"getPageViews": "pageViews", "getTrafficSources": "trafficSources"}
DIMS = {"getPageViews": ["pagePath", "pageTitle"], "getTrafficSources": ["sessionSource", "sessionMedium", "sessionCampaignName"]}
METRICS = {"getPageViews": ["screenPageViews", "activeUsers", "averageSessionDuration"],
           "getTrafficSources": ["sessions", "activeUsers", "newUsers", "bounceRate"]}


def source_line(span, file, first, last, containing=None):
    if not span or str(span.get("file", "")).removeprefix("skill/") != file:
        return False
    lo, hi = span.get("start_line"), span.get("end_line")
    return isinstance(lo, int) and isinstance(hi, int) and first <= lo <= hi <= last and (
        containing is None or lo <= containing <= hi)


def versions(record, side, location):
    return {v for b in record.get(side, {}).get("bindings", []) if b["location"] == location for v in b["data_ids"]}


def read_run(run):
    e = Evidence(run)
    snap = e.read(run / "source/inputs/snapshot.json")
    if snap["source_sha256"] != SOURCE or len(snap["files"]) != 16:
        raise ValueError("This trace is for the bound 16-file GA4 source.")
    sources = {}
    for item in snap["files"]:
        raw = e.inside(run / "source/inputs/package", item["path"]).read_bytes()
        if digest(raw) != item["raw_sha256"]:
            raise ValueError("Source content mismatch: " + item["path"])
        sources[item["path"]] = {"sha256": item["raw_sha256"], "text": raw.decode("utf-8")}
    selection = e.optional(run / "selection.json") or {}
    def bound(ref):
        return e.read(e.inside(run, ref["path"]), ref["sha256"])
    cfg = bound(selection["cfg"])["cfg"] if selection.get("cfg") else {}
    initial = (e.optional(run / "graph/initial.json") or {}).get("cfg", {})
    spans = selected_spans(cfg, initial, legacy_spans(e, initial, sources), sources) if cfg and initial else {}
    compiled, prop, data, records = {}, {}, [], {}
    if selection.get("annotation"):
        manifest = bound(selection["annotation"])
        owner = e.inside(run, selection["annotation"]["path"]).parent
        ref = e.read(owner / "inputs/references.json", manifest["files"]["inputs/references.json"])
        if (ref["cfg"]["sha256"] != selection["cfg"]["sha256"]
            or e.inside(owner, ref["cfg"]["path"]) != e.inside(run, selection["cfg"]["path"])
            or e.inside(owner, ref["source_owner"]["path"]) != run / "source"
            or ref["source_owner"]["manifest_sha256"] != e.read(run / "source/manifest.json")["manifest_sha256"]):
            raise ValueError("Annotation differs from the selected source or CFG.")
        compiled = e.read(owner / "audit/compiled-response.json", manifest["artifacts"]["audit/compiled-response.json"])
        prop = e.optional(run / "propagation/manifest.json") or {}
        if prop:
            base = run / "propagation"
            if (prop["upstream"]["manifest_sha256"] != manifest["manifest_sha256"]
                    or e.inside(base, prop["upstream"]["path"]) != owner):
                raise ValueError("Propagation differs from the selected annotation.")
            records = e.read(base / "records.json", prop["artifacts"]["records.json"])
            data = e.read(base / "data.json", prop["artifacts"]["data.json"])
    return e, selection, cfg, spans, compiled, prop, {d["id"]: d for d in data}, records


def variants(content):
    return [v["content"] for v in content["variants"]] if content["form"] == "loop_summary" else [content]


class Lineage:
    def __init__(self, data):
        self.data = data

    def field(self, node, path, seen=frozenset()):
        """Structural member IDs only. Incomplete, opaque or ambiguous alternatives supply no proof."""
        if not path:
            return {node}
        if node in seen or node not in self.data:
            return set()
        ids = set()
        for variant in variants(self.data[node]["content"]):
            if variant["form"] == "selection":
                here = self.field(variant["base"], (*variant["path"], *path), seen | {node})
            elif variant["form"] == "known_parts":
                matches = [p for p in variant["parts"] if tuple(p["path"]) == path[:len(p["path"])]]
                if len(matches) != 1:
                    return set()
                part = matches[0]
                here = self.field(part["data"], path[len(part["path"]):], seen | {node})
            else:
                return set()
            if not here:
                return set()
            ids.update(here)
        return ids

    def matches(self, node, expected, seen=frozenset()):
        if node in seen or node not in self.data:
            return False
        choices = variants(self.data[node]["content"])
        def match(c):
            if c["form"] == "literal":
                return c["value"] == expected
            if c["form"] == "selection" and not c["path"]:
                return self.matches(c["base"], expected, seen | {node})
            if c["form"] != "known_parts" or not c.get("parts_complete") or not isinstance(expected, (dict, list)):
                return False
            members = {p["path"][0]: p["data"] for p in c["parts"] if len(p["path"]) == 1}
            return len(members) == len(c["parts"]) == len(expected) and all(
                k in members and self.matches(members[k], v, seen | {node})
                for k, v in (expected.items() if isinstance(expected, dict) else enumerate(expected)))
        return bool(choices) and all(map(match, choices))

    @lru_cache(maxsize=4096)
    def parents(self, node, include_possible=False):
        seen, todo = set(), [node]
        while todo:
            current = todo.pop()
            if current in seen or current not in self.data:
                continue
            seen.add(current)
            origin = self.data[current]["origin"]
            if origin.get("part_of"):
                todo.append(origin["part_of"])
            deps = origin.get("dependencies", [])
            todo.extend(d["data"] for d in deps if include_possible or d["relation"] == "derived")
        return seen


def ingresses(irs, spans, compiled, records, coverage, data):
    out = {name: [] for name in SITES}
    for ir, op in irs.items():
        inputs = op.get("inputs", [])
        for index, operand in enumerate(inputs):
            if operand["type"] != "context_key":
                continue
            key = operand.get("semantic_name") or operand["identifier"]
            if key.replace(":", ".").replace("/", ".").split(".")[-1] != "dateRange":
                continue
            span = spans.get(ir)
            for name, (file, first, last) in SITES.items():
                at_signature = source_line(span, file, first, last, first)
                if not at_signature and name not in key.replace(":", ".").replace("/", ".").split(".")[:-1]:
                    continue
                coords = {"instruction_id": ir, "side": "input", "index": index}
                locs = {k: v for k, v in compiled.get("locations", {}).items() if coords in v["operand_refs"]}
                spec = compiled.get("ir_semantics", {}).get(ir, {})
                reads = {a["output"]: a["location"] for event in spec.get("events", [])
                         for a in event.get("atomic_ops", []) if a["op"] == "read"}
                witnesses = []
                for binding in spec.get("output_bindings", []):
                    val = binding["value"]
                    selected = list(locs.values())
                    if val.get("kind") == "local" and reads.get(val["name"]) in locs:
                        selected = [locs[reads[val["name"]]]]
                    elif val != {"kind": "input", "index": index}:
                        continue
                    if any(len(loc["operand_refs"]) != 1 for loc in selected):
                        continue
                    aliases = [{"kind": loc["kind"], "name": loc["name"]} for loc in selected] or [
                        {"kind": "runtime_context", "name": operand["identifier"]}]
                    rec = records.get(ir, {})
                    actual = set().union(*(versions(rec, "entry_state", loc) for loc in aliases))
                    result = op["outputs"][binding["output_index"]]["identifier"]
                    exit_ids = versions(rec, "exit_state", {"kind": "result", "name": result})
                    actual = {v for v in actual if data.get(v, {}).get("origin", {}).get("acquired_from")}
                    if at_signature and actual and exit_ids:
                        witnesses.append({"result": result, "parameter_data": sorted(actual), "result_data": sorted(exit_ids)})
                out[name].append({"ir": ir, "input_index": index, "key": operand["identifier"],
                                  "basis": "signature" if at_signature else "named_candidate_only",
                                  "coverage": coverage.get(ir, "not_run"), "bindings": witnesses})
    return out


def first_barriers(cfg, coverage, diagnostics):
    if not cfg:
        return {"status": "no_selected_cfg", "count": 0, "examples": []}
    starts = set(cfg["blocks"])
    edges = defaultdict(list)
    for edge in cfg["edges"]:
        target = edge["target_block_id"]
        starts.discard(target)
        edges[edge["source_block_id"]].append(target)
    starts.add(cfg["entry_block_id"])
    distances = {root: 0 for root in starts}
    pending = deque(starts)
    while pending:
        block = pending.popleft()
        for target in edges[block]:
            if target not in distances:
                distances[target] = 1 + distances[block]
                pending.append(target)
    by_ir = defaultdict(list)
    for d in diagnostics:
        by_ir[d.get("instruction_id")].append(d.get("code"))
    irs = instructions(cfg)
    producers = {v["identifier"]: i for i, op in irs.items() for v in op["outputs"]}
    downstream = defaultdict(set)
    for ir, op in irs.items():
        for v in op["inputs"]:
            if v["type"] == "result":
                downstream[producers.get(v["identifier"])].add(ir)
    rows = []
    for block, b in cfg["blocks"].items():
        for pos, op in enumerate(b["instructions"]):
            ir = op["id"]
            status = coverage.get(ir)
            if status in {"unmodeled", "not_solved", "execution_error"}:
                rows.append({"block": block, "ir": ir, "coverage": status, "distance_in_blocks": distances.get(block),
                    "position": pos, "codes": by_ir[ir], "input_producers": sorted({
                        producers[v["identifier"]] for v in op["inputs"] if v.get("identifier") in producers}),
                    "direct_users": sorted(downstream[ir]), "next_blocks": edges[block]})
                break
    rows.sort(key=lambda r: (r["distance_in_blocks"] if r["distance_in_blocks"] is not None else 10**9,
                             r["position"], r["ir"]))
    return {"status": "graph_distance_then_instruction_position", "reached_block_barriers": len(rows),
            "examples": rows[:8]}


def audit(run):
    ev, selection, cfg, spans, ann, prop, data, records = read_run(run)
    cov = prop.get("coverage", {})
    irs = instructions(cfg)
    views = Lineage(data)
    entries = ingresses(irs, spans, ann, records, cov, data)
    origins = {n: {v for entry in rows for b in entry["bindings"] for v in b["parameter_data"]}
               for n, rows in entries.items()}
    ops = recorded_ops(ann, records)
    producers = {out["identifier"]: ir for ir, ins in irs.items() for out in ins["outputs"]}
    sites = lambda key: [spans.get(ops[key]["ir"]), *ops[key]["op"].get("evidences", [])]
    in_site = lambda key, site: any(source_line(s, *site) for s in sites(key))
    projections = defaultdict(list)
    saved = defaultdict(list)
    summaries = defaultdict(list)
    for key, op in ops.items():
        spec = op["op"]
        pick = spec["op"] == "select_part" and spec["path"] == [0] and in_site(key, (REPORTS, 77, 108, 100))
        store = spec["op"] == "write" and in_site(key, (REPORTS, 77, 108, 105))
        summary = spec["op"] == "build" and in_site(key, (INDEX, 55, 76))
        if not (pick or store or summary):
            continue
        for _, ref, row in op["rows"]:
            if row.get("skipped_case_inputs"):
                continue
            for alt in row.get("alternatives") or [row]:
                inputs, outputs = alt["inputs"], alt.get("outputs", [])
                if pick and len(inputs) == 1 and len(outputs) == 1:
                    for base in inputs[0]:
                        for value in outputs[0]:
                            if all(c.get("base") == base and c.get("path") == [0] for c in variants(data[value]["content"])):
                                projections[base].append((ref, value))
                if store and len(inputs) == 1 and any(ep["kind"] == "storage" for ep in row.get("endpoints", [])):
                    for value in inputs[0]:
                        saved[value].append(ref)
                if summary and outputs:
                    for m in row.get("members") or []:
                        if m["path"] in [["pageViews"], ["trafficSources"]] and m["value_input_index"] is not None:
                            for value in inputs[m["value_input_index"]]:
                                summaries[value].append((m["path"][0], ref, outputs[0]))

    traced = {k: {"paired_count": 0, "projected_count": 0, "request_examples": [], "examples": []}
              for k in [*FIELDS, *("siteOverview." + field for field in FIELDS.values())]}
    traced_inputs = {key: set() for key in traced}
    counts = Counter()
    def returned(value, file, first, last):
        return [ir for ir, instruction in irs.items() if instruction["opcode"] == "return"
                and source_line(spans.get(ir), file, first, last) and any(
                    v["type"] == "result" and value in versions(records.get(ir, {}), "entry_state",
                        {"kind": "result", "name": v["identifier"]}) for v in instruction["inputs"])]
    def handles(ir, endpoint, request):
        handles = []
        for ref in endpoint["operand_refs"]:
            if ref["instruction_id"] != ir or ref["side"] != "input":
                continue
            operand = irs[ir]["inputs"][ref["index"]]
            if operand["type"] != "result":
                continue
            producer = producers[operand["identifier"]]
            if not source_line(spans.get(producer), REPORTS, 77, 108, 88):
                continue
            witness = versions(records.get(ir, {}), "entry_state", {"kind": "result", "name": operand["identifier"]})
            if witness and request not in witness:
                handles.append({"source_ir": producer, "operand_index": ref["index"], "values": sorted(witness)})
        return handles
    for key, op in ops.items():
        spec = op["op"]
        if spec["op"] != "receive":
            continue
        loc = ann["locations"][spec["location"]]
        if loc["kind"] != "remote" or "runreport" not in "".join(loc["name"].lower().split()):
            continue
        counts["declared_remote_runReport"] += 1
        if not in_site(key, (REPORTS, 77, 108, 100)):
            continue
        counts["physical_report_site"] += 1
        pair = check_pair(key, ops, ann["locations"])
        if pair["declared"] != "confirmed":
            continue
        for occ in pair["occurrences"]:
            if not occ["same_endpoint_args_and_alternatives"]:
                continue
            counts["paired_occurrences"] += 1
            row = next(r for i, _, r in op["rows"] if i == occ["instance"])
            for alt in row.get("alternatives") or [row]:
                if len(alt["inputs"]) != 1 or len(alt["inputs"][0]) != 1 or len(alt.get("outputs", [])) != 1:
                    continue
                request = alt["inputs"][0][0]
                dates = views.field(request, ("dateRanges", 0))
                for date in dates:
                    owners = {n for n, ids in origins.items() if views.parents(date, True) & ids}
                    if len(owners) != 1:
                        continue
                    name = next(iter(owners))
                    ingress_versions = views.parents(date) & origins[name]
                    if not ingress_versions:
                        continue
                    possibilities = FIELDS if name == "siteOverview" else [name]
                    for wrapper in possibilities:
                        if not all((children := views.field(request, (field,))) and all(
                            views.matches(v, [{"name": n} for n in expected]) for v in children)
                            for field, expected in (("dimensions", DIMS[wrapper]), ("metrics", METRICS[wrapper]))):
                            continue
                        for reply in alt["outputs"][0]:
                            label = ("siteOverview." + FIELDS[wrapper] if name == "siteOverview" else wrapper)
                            bucket = traced[label]
                            bucket["paired_count"] += 1
                            request_evidence = {"input": sorted(ingress_versions), "request": request,
                                "dateRanges_0": date, "remote_endpoint": loc["name"], "request_id": pair["request_id"],
                                "source_bound_client_handle_versions": handles(op["ir"], loc, request),
                                "delivery": occ["deliver_record"], "receive": occ["receive_record"], "sdk_tuple": reply}
                            if len(bucket["request_examples"]) < 3:
                                bucket["request_examples"].append(request_evidence)
                            for project_ref, response in projections.get(reply, []):
                                bucket["projected_count"] += 1
                                traced_inputs[label].update(ingress_versions)
                                if len(bucket["examples"]) == 3:
                                    continue
                                bucket["examples"].append({**request_evidence, "select": project_ref, "response_0": response,
                                    "default_save_writes": saved.get(response, []),
                                    "wrapper_returns": returned(response, *SITES[wrapper]),
                                    "overview_member": [{"build": ref, "result_data": ids,
                                        "overview_returns": sorted({ir for node in ids for ir in returned(node, *SITES["siteOverview"])})}
                                        for field, ref, ids in summaries.get(response, []) if field == FIELDS[wrapper]]})
    def publisher(label, bucket):
        name = label.split(".")[0]
        if bucket["projected_count"]:
            status = "paired_request_and_response_field_witnessed"
        elif bucket["paired_count"]:
            status = "paired_request_witnessed_without_response_projection"
        elif not prop:
            status = "propagation_not_run"
        elif not records:
            status = "no_executed_ir_records"
        elif not origins[name]:
            status = "no_source_bound_supplied_range_witness"
        elif not counts["paired_occurrences"]:
            status = "no_witnessed_source_located_report_pair"
        else:
            status = "no_exclusive_version_chain_from_supplied_range_to_wrapper_request"
        return {"status": status, **bucket}
    common = sorted(traced_inputs["siteOverview.pageViews"] & traced_inputs["siteOverview.trafficSources"])
    distinct = bool(traced_inputs["getPageViews"] and traced_inputs["getTrafficSources"]) and (
        traced_inputs["getPageViews"].isdisjoint(traced_inputs["getTrafficSources"]))
    return {"run": run.name, "source_sha256": SOURCE, "selection": selection,
            "propagation_status": prop.get("status", "not_run"), "coverage": dict(Counter(cov.values())),
            "recorded_ir": len(records), "entries": entries, "paired_call_counts": dict(counts),
            "traces": {k: publisher(k, v) for k, v in traced.items()},
            "separate_public_inputs_witnessed": distinct, "common_overview_input_version_count": len(common),
            "common_overview_input_examples": common[:3],
            "first_barriers": first_barriers(cfg, cov, prop.get("diagnostics", [])),
            "limits": ["A trace witnesses one recorded compatible alternative up to its projected SDK response.",
                       "Save and return require their own observable evidence. Empty lists mean no witness.",
                       "Physical SDK call source and a matching remote request/response endpoint are required. Endpoint names do not identify a particular credential handle.",
                       "Opaque dependencies, non-structural request construction, broad source spans and omitted parameters cannot prove a supplied invocation range."],
            "source_positions": {"entry": SITES, "request_and_receive": [REPORTS, 92, 100], "default_save": [REPORTS, 84, 105],
                                 "default_save_operand": "save = true; both wrappers omit save", "tuple_projection": [REPORTS, 100],
                                 "return": [REPORTS, 108], "overview_fields": [INDEX, 60, 63]},
            "hashes": ev.artifacts, "locator_issues": ev.issues}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    arg = parser.parse_args()
    print(json.dumps(audit(arg.run.resolve()), ensure_ascii=True, indent=2, allow_nan=False))
