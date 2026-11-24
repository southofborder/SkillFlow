"""A closed projection of three public GA4 invocations from the saved 329-IR experiment."""
from copy import deepcopy
import json
from pathlib import Path
from shutil import copytree, ignore_patterns

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.inputs.snapshot import freeze_input, read_snapshot
from skillflow.document_guided.graph_facts import instruction_ref
from skillflow.propagation.contracts.task import task_source_files


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "tests/fixtures/ga4_entry_occurrences/regression.json"
REPORTS = "skill/scripts/src/api/reports.ts"
INDEX = "skill/scripts/src/index.ts"
WRAPPERS = {"getPageViews": (114, 120), "getTrafficSources": (125, 131)}
SIGNATURES = {**{name: (REPORTS, lines[0]) for name, lines in WRAPPERS.items()},
              "siteOverview": (INDEX, 55)}
FAMILIES = {"getPageViews": (["pagePath", "pageTitle"],
                             ["screenPageViews", "activeUsers", "averageSessionDuration"]),
            "getTrafficSources": (["sessionSource", "sessionMedium", "sessionCampaignName"],
                                  ["sessions", "activeUsers", "newUsers", "bounceRate"])}


def load_material(directory):
    saved = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    package = (ROOT / "experiments/doe/inputs/clawhub-top1000-v1/items"
               / "0481-adamkristopher-ga4-analytics/attempts/20261020T094423659277Z-624ebf/files")
    copytree(package, directory / "package", ignore=ignore_patterns("_meta.json", "skill-card.md"))
    freeze_input(directory / "package", directory / "snapshot", ArtifactWriter(()))
    _, source, _ = read_snapshot(directory / "snapshot")
    assert len(source["files"]) == 16 and source["source_sha256"] == saved["source_sha256"]
    files = task_source_files(source)
    return saved, source, files


def span(file, first, last=None):
    return {"file": file, "start_line": first, "end_line": first if last is None else last}


def result(name):
    return {"result": name}


def ret(values, source):
    return {"kind": "return", "values": [result(name) for name in values], "source": source}


def jump(target, source):
    return {"kind": "jump", "target": target, "source": source}


def signature(name):
    return span(*SIGNATURES[name])


def original_projection(saved):
    """Keep the original pooled receive. Restrict its routing to the three tested methods.

    The archived excerpt separately retains the actual seven-method report selector
    and its shared reports.arguments consumer without rewriting either original.
    """
    blocks = {b["ref"]: deepcopy(b) for b in saved["graph_excerpt"]["blocks"]}
    public = blocks["public_entry"]
    choose_site = blocks["select.site"]
    choose_site["exit"]["arms"][1]["target"] = "select.reports"
    choose_report = blocks["select.reports"]
    choose_report["exit"]["arms"] = [
        {"target": name, "condition": "entry.name == " + name} for name in WRAPPERS]
    site = blocks["site"]
    site["operations"] = site["operations"][:2] + [{
        "ref": "site.assemble", "opcode": "value", "source": span(INDEX, 57, 63),
        "inputs": [result("site.pageViews.response"), result("site.trafficSources.response")],
        "outputs": ["site.results"]}]
    leaves = []
    for name, lines in WRAPPERS.items():
        source = span(REPORTS, *lines)
        leaves.append({"ref": name, "source_kind": "normal", "operations": [{
            "ref": "invoke", "opcode": "call", "source": source,
            "inputs": [result("entry.dateRange")], "outputs": [name + ".response"]}],
            "exit": ret([name + ".response"], source)})
    return {"entry": public["ref"], "blocks": [public, choose_site, choose_report, site, *leaves]}


def occurrence_update(raw):
    """Source-grounded answer to the program's finite correction; no external inputs fabricated."""
    roots = {"public_entry": "getPageViews", "select.site": "siteOverview",
             "select.reports": "getTrafficSources"}
    rows = []
    for old in raw["blocks"]:
        ref = old["ref"]
        if ref in roots:
            name = roots[ref]
            source = signature(name)
            target = "site" if name == "siteOverview" else name
            rows.append({"ref": ref, "source_kind": "context", "operations": [{
                "ref": "receive", "opcode": "receive", "source": source,
                "inputs": [{"context_key": name + ".dateRange"}],
                "outputs": [name + ".suppliedRange"]}], "exit": jump(target, source)})
        else:
            block = deepcopy(old)
            owner = "siteOverview" if ref == "site" else ref
            for op in block["operations"]:
                for operand in op["inputs"]:
                    if operand == result("entry.dateRange"):
                        operand["result"] = owner + ".suppliedRange"
            rows.append(block)
    return rows


def canonical(assembled, block, action=None):
    return assembled.id_map["instructions"][instruction_ref(block, action)]


def inp(index=0):
    return {"kind": "input", "index": index}


def local(name):
    return {"kind": "local", "name": name}


def literal(value):
    return {"kind": "literal", "value": value}


def evidence(site, reason):
    return {**site, "reason": reason}


def segment(ops):
    return {"mode": "local", "ops": ops, "returns": []}


def spec(site, *, segments=(), output=None):
    row = {"evidences": [evidence(site, "This source site supplies the operation.")],
           "segments": list(segments)}
    if output is not None:
        row["output_bindings"] = [{"output_index": 0, "value": output}]
    return row


def input_contract(site, paths):
    return {"inputs": [{"input_index": 0, "required": [
        {"property": "value", "path": path} for path in paths], "remainder": "independent",
        "reason": "The client receives the fields of the constructed GA4 request."}],
        "reason": "The sourced request determines the report.",
        "evidences": [evidence(site, "runReport is called with this request.")]}


def date_cases():
    """The GA4 object path passes its argument through. Falsy ranges use the configured default."""
    site = span(REPORTS, 47, 66)
    tests = [{"kind": "missing"}, {"kind": "null"}, {"kind": "equals", "value": ""},
             {"kind": "object"}]
    names = ["omitted", "null", "empty", "object", "other"]
    cases = []
    for i, name in enumerate(names):
        ev = evidence(site, "Falsy values use the configured range; an object is returned unchanged.")
        if name == "object":
            ops = []
            returned = inp()
        else:
            ops = []
            text = inp()
            if name in {"omitted", "null", "empty"}:
                ops.append({"op": "read", "location": "configured_range", "output": "configured",
                            "evidences": [ev]})
                text = local("configured")
            parsed_at = evidence(span(REPORTS, 58, 72), "Input shorthand selects the start day; endDate is today.")
            rule = {"input_index": 0, "required": [{"property": "value", "path": []}],
                    "remainder": "independent", "reason": "Parsing uses the supplied range string."}
            ops.extend([{"op": "compute", "inputs": [text], "dependencies": ["derived"], "output": "start",
                         "demand_transfer": {"rules": [{"output": {"property": "value", "path": []},
                              "inputs": [rule], "reason": "The day count is taken from the matched string.",
                              "evidences": [parsed_at]}]}, "evidences": [parsed_at]},
                        {"op": "build", "container": "object", "output": "parsed", "parts": [
                            {"path": ["startDate"], "value": local("start")},
                            {"path": ["endDate"], "value": literal("today")}], "evidences": [parsed_at]}])
            returned = local("parsed")
        cases.append({"name": name, "phase": "normal", "disposition": "return", "condition": name,
                      "guard": {"input_index": 0, "path": [], "tests": tests, "outcome": i},
                      "segments": [segment(ops)] if ops else [], "yield": returned, "evidences": [ev]})
    return {"kind": "cases", "output": "parsedRange", "cases": cases, "evidences": [ev]}


def report_record(owner, source, source_actions=()):
    """Fill the query from the incoming argument; only ingress and configuration values are seeded."""
    dims, metrics = FAMILIES[owner]
    sdk = span(REPORTS, 92, 100)
    sdk_ev = evidence(sdk, "The parsed range is the only dateRanges member in the actual request.")
    ops = [
        {"op": "read", "location": "property", "output": "property",
         "evidences": [evidence(span(REPORTS, 89), "The report uses the configured property.")]},
        {"op": "build", "container": "list", "parts": [{"path": [0], "value": local("parsedRange")}],
         "output": "ranges", "evidences": [sdk_ev]},
        {"op": "build", "container": "object", "output": "request", "parts": [
            {"path": ["property"], "value": local("property")},
            {"path": ["dateRanges"], "value": local("ranges")},
            {"path": ["dimensions"], "value": literal([{"name": x} for x in dims])},
            {"path": ["metrics"], "value": literal([{"name": x} for x in metrics])}],
         "evidences": [sdk_ev, evidence(span(REPORTS, *WRAPPERS[owner]), "The wrapper supplies dimensions and metrics.")]},
        {"op": "call", "location": "analytics", "inputs": [local("request")], "output": "tuple",
         "evidences": [sdk_ev], "input_contract": input_contract(sdk,
              [["property"], ["dateRanges"], ["dimensions"], ["metrics"]])},
        {"op": "select_part", "input": local("tuple"), "path": [0], "output": "response",
         "evidences": [evidence(span(REPORTS, 100), "Array destructuring selects the first SDK response.")]},
        {"op": "write", "target": "saved", "input": local("response"),
         "evidences": [evidence(span(REPORTS, 84, 105), "Both wrappers omit save, which defaults to true.")]}]
    logs = [a for a in source_actions if a["kind"] == "other"]
    segments = []
    if logs:
        segments.append(segment([{"op": "placeholder", "kind": "effect", "inputs": [],
            "reason": "The logging destination and implementation are outside the frozen source.",
            "evidences": [evidence(a["source"], "The caller logs before invoking the wrapper.")]} for a in logs]))
    segments.extend([date_cases(), segment(ops)])
    row = spec(source, segments=segments, output=local("response"))
    if logs:
        from skillflow.document_guided.action_bindings import action_coordinates
        paths = [list(path) for path, _ in action_coordinates(row)]
        assigned = {a["ref"]: [["segments", 0, "ops", i]] for i, a in enumerate(logs)}
        accounted = [p for ls in assigned.values() for p in ls]
        assigned[source_actions[-1]["ref"]] = [p for p in paths if p not in accounted]
        row["action_bindings"] = assigned
    return row


def filled_processing(assembly):
    locations = {}
    for name, kind, source in [("configured_range", "runtime_context", span(REPORTS, 47, 55)),
                               ("property", "runtime_context", span(REPORTS, 88, 89)),
                               ("analytics", "remote", span(REPORTS, 100)),
                               ("saved", "storage", span(REPORTS, 102, 105))]:
        locations[name] = {"kind": kind, "name": name, "evidences": [evidence(source, "Source location.")]}
    records = {}
    for block in assembly.facts["blocks"]:
        ref = block["ref"]
        records[canonical(assembly, ref)] = spec(block["exit"]["source"])
        for op in block["operations"]:
            source = op["source"]
            if block["source_kind"] == "context":
                row = spec(source, output=inp())
            elif op["ref"] == "site.assemble":
                row = spec(source, segments=[segment([{"op": "build", "container": "object", "output": "summary",
                    "parts": [{"path": ["pageViews"], "value": inp(0)},
                              {"path": ["trafficSources"], "value": inp(1)}]}])], output=local("summary"))
            else:
                owner = op.get("metadata", {}).get("callee", ref)
                row = report_record(owner, source, op.get("source_actions", []))
            records[canonical(assembly, ref, op["ref"])] = row
    return {"locations": locations, "ir_semantics": records}
