"""Authored source-boundary regressions, not regenerated or migrated GA4 answers.

Each fixture covers an explicit projection of the frozen GA4 source. Unknown
library internals remain opaque. Source snapshots are data and never executed.
The optional confidential-field declaration is a separate synthetic variant;
it is not a claim that GA4 metadata contains credentials.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from skillflow.common.source_evidence import _digest
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.binding_examples import instruction, literal, result
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.task import validate_task_candidate, task_source_files
from skillflow.propagation.data import DataRegistry, LiteralContent, OpaqueContent
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.solver import propagate


ROOT = Path(__file__).parents[1] / "fixtures" / "ga4_alignment_v9"
EACH = {"kind": "each"}


def citation(file, start, end, reason):
    return {"file": "skill/" + file, "start_line": start, "end_line": end, "reason": reason}


def source_bundle(extra=None):
    manifest = json.loads((ROOT / "provenance.json").read_text(encoding="utf-8"))
    files = []
    for row in manifest["files"]:
        content = (ROOT / row["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == row["sha256"]
        files.append({**row, "content": content.decode("utf-8")})
    for path, text in (extra or {}).items():
        files.append({"path": path, "content": text, "sha256": hashlib.sha256(text.encode()).hexdigest()})
    files.sort(key=lambda row: row["path"])
    return {"files": files, "source_sha256": _digest([
        {"path": row["path"], "sha256": row["sha256"]} for row in files])}


def inp(index=0):
    return {"kind": "input", "index": index}


def local(name):
    return {"kind": "local", "name": name}


def value(v):
    return {"kind": "literal", "value": v}


def segment(*ops):
    return {"mode": "local", "returns": [], "ops": list(ops)}


def spec(ev, *segments, output=None, binding=None):
    out = {"evidences": [ev], "segments": list(segments)}
    if output is not None or binding is not None:
        out["output_bindings"] = [{"output_index": 0, "value": local(output) if binding is None else binding}]
    return out


def block(name, instructions, *, context=False):
    return {"block_id": name, "block_name": name, "instructions": instructions,
            "data_source_kind": "context" if context else None, "constraints": []}


def graph(instructions):
    return {"entry_block_id": "main", "blocks": {"main": block("main", instructions)},
            "edges": [], "constraints": [], "declared_context_keys": []}


def location(kind, name, ev, **extra):
    return {"kind": kind, "name": name, "evidences": [ev], **extra}


def demand(path=None, *, target=None, requirement="R1", preserve="value"):
    return {"requirement_id": requirement, "target": target or {"kind": "input", "index": 0},
            "preserve": preserve, "path": path or [],
            "reason": "Preserve the exact source-declared result at this particular boundary."}


def prepare(cfg, semantics, locations, ev, task_text, *, requirements=None, extra_source=None):
    source = source_bundle(extra_source)
    candidate = {"purpose": {"text": task_text, "evidences": [ev]}, "issues": [],
        "requirements": requirements or [{"id": "R1", "text": task_text, "evidences": [ev]}]}
    task = validate_task_candidate(candidate, source_files=task_source_files(source),
                                   source_sha256=source["source_sha256"])
    material = prepare_material(source, cfg, task_baseline=task)
    wire = {"outcome": "completed", "locations": locations, "ir_semantics": semantics,
        "realizations": [{"requirement_id": row["id"]} for row in candidate["requirements"]], "demands": []}
    return material, wire


def solve(material, wire, context=None):
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    registry, state = None, None
    if context is not None:
        registry = DataRegistry("ga4-v9-authored-context")
        bindings = {}
        for name, contents in context.items():
            item = registry.register_source(name, acquired_from="runtime_context:" + name,
                content=OpaqueContent() if contents is None else LiteralContent(value=contents))
            bindings[FlowLocation(kind="runtime_context", name=name)] = frozenset([item.id])
        state = FlowState.from_mapping(bindings)
    solved = propagate(material["cfg"], to_payload(compiled), initial_registry=registry, initial_state=state)
    assert solved.status == "complete", solved.diagnostics
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)
    return {"material": material, "wire": saved, "raw": raw, "compiled": compiled,
            "mapping": mapping, "solved": solved, "facts": facts}


def bulk_fixture(urls):
    """Public URLs -> opaque normalize -> filter -> client -> response save.

    The nonempty branch is structural; opaque string normalization does not
    claim to execute trim or slash insertion. Mapped collection cardinality and
    occurrence ordering are available without evaluating those strings.
    """
    norm = citation("scripts/src/api/bulk-lookup.ts", 64, 75, "Each URL is locally normalized in the original order.")
    bulk = citation("scripts/src/api/bulk-lookup.ts", 149, 190, "An empty URL batch returns before client acquisition; saveResult receives the actual response.")
    filt = citation("scripts/src/api/bulk-lookup.ts", 84, 99, "The nonempty filter contains the actual normalized URL collection.")
    cfg = {"entry_block_id": "entry", "declared_context_keys": ["public_urls"], "constraints": [],
        "blocks": {
            "entry": block("entry", [instruction("ir_args", "acquire_context", [{"type": "context_key", "identifier": "public_urls"}], "urls"),
                instruction("ir_start", "dispatch", [])], context=True),
            "normalize": block("normalize", [instruction("ir_normalize", "invoke", [result("urls")], "normalized"),
                instruction("ir_guard", "dispatch", [result("normalized")])]),
            "nonempty": block("nonempty", [instruction("ir_filter", "invoke", [result("normalized")], "filter"),
                instruction("ir_client", "invoke", [], "client"),
                instruction("ir_report", "invoke", [result("filter"), result("client")], "response"),
                instruction("ir_save", "invoke", [result("response")], "saved"),
                instruction("ir_return", "return", [result("saved")])]),
            "empty": block("empty", [instruction("ir_empty", "return", [literal({"rows": [], "rowCount": 0})])])},
        "edges": [{"source_block_id": "entry", "target_block_id": "normalize"}] + [
            {"source_block_id": "normalize", "target_block_id": target} for target in ("nonempty", "empty")]}
    semantics = {
        "ir_args": spec(bulk, binding=inp()), "ir_start": spec(bulk),
        "ir_normalize": spec(norm, {"kind": "for_each", "collection": inp(), "item": "url",
            "body": [segment({"op": "compute", "inputs": [local("url")], "output": "normalized_url"})],
            "yield": local("normalized_url"), "output": "normalized"}, output="normalized"),
        "ir_guard": spec(bulk, segment({"op": "branch", "input": inp(), "predicate": "nonempty",
            "true_target": "nonempty", "false_target": "empty"})),
        "ir_filter": spec(filt, segment({"op": "build", "container": "object", "parts": [
            {"path": ["filter", "fieldName"], "value": value("pagePath")},
            {"path": ["filter", "inListFilter", "values"], "value": inp()},
            {"path": ["filter", "inListFilter", "caseSensitive"], "value": value(False)}], "output": "filter"}), output="filter"),
        # This fixture projects the normal already-initialized-client boundary.
        "ir_client": spec(bulk, segment({"op": "read", "location": "client", "output": "handle"}), output="handle"),
        "ir_report": spec(bulk, segment({"op": "call", "location": "api", "inputs": [inp(0), inp(1)], "output": "response"}), output="response"),
        "ir_save": spec(bulk, segment({"op": "write", "target": "saved", "mode": "replace", "input": inp(),
            "demands": [demand()]}, {"op": "read", "location": "saved", "output": "actual_saved"}), output="actual_saved"),
        "ir_return": spec(bulk), "ir_empty": spec(bulk)}
    material, wire = prepare(cfg, semantics, {"client": location("runtime_context", "clientInstance", bulk),
        "api": location("remote", "client.runReport", bulk), "saved": location("storage", "bulk-result.json", bulk)},
        bulk, "Return the report and save the actual report result when saving is selected.")
    return solve(material, wire, {"public_urls": urls, "clientInstance": None})


def inspection_fixture():
    ev = citation("scripts/src/api/indexing.ts", 146, 193, "Inspection uses nested requestBody and derives its saved result from response.data.inspectionResult.")
    undefined = citation("scripts/src/api/indexing.ts", 174, 190, "Absent mobile and rich-result fields use the actual JavaScript undefined expression, not null.")
    cfg = graph([instruction("ir_inspect", "invoke", [literal("https://fixture.invalid/page"), literal("sc-domain:fixture.invalid")], "result"),
                 instruction("ir_save", "invoke", [result("result")]), instruction("ir_return", "return", [result("result")])])
    fields = ["inspectionResultLink", "indexStatusResult", "mobileUsabilityResult", "richResultsResult"]
    ops = [{"op": "build", "container": "object", "parts": [
        {"path": ["requestBody", "inspectionUrl"], "value": inp()},
        {"path": ["requestBody", "siteUrl"], "value": inp(1)}], "output": "request"},
        {"op": "call", "location": "api", "inputs": [local("request")], "output": "response"},
        {"op": "select_part", "input": local("response"), "path": ["data", "inspectionResult"], "output": "inspection"}]
    for field in fields:
        ops.append({"op": "select_part", "input": local("inspection"), "path": [field], "output": field})
    ops += [{"op": "compute", "inputs": [], "output": "js_undefined", "evidences": [undefined]}]
    status_fields = ["verdict", "coverageState", "robotsTxtState", "indexingState", "lastCrawlTime",
                     "pageFetchState", "googleCanonical", "userCanonical", "crawledAs"]
    for field in status_fields:
        fallback = value("NEUTRAL" if field == "verdict" else "Unknown") if field in {"verdict", "coverageState"} else local("js_undefined")
        ops += [{"op": "select_part", "input": local("indexStatusResult"), "path": [field], "output": "status_" + field},
            {"op": "compute", "inputs": [local("status_" + field), fallback], "output": "final_" + field}]
    ops += [{"op": "build", "container": "object", "parts": [
                {"path": [field], "value": local("final_" + field)} for field in status_fields], "output": "index_status"},
            {"op": "compute", "inputs": [local("mobileUsabilityResult"), local("js_undefined")], "output": "mobile"},
            {"op": "compute", "inputs": [local("richResultsResult"), local("js_undefined")], "output": "rich"},
            {"op": "build", "container": "object", "parts": [
                {"path": ["inspectionResultLink"], "value": local("inspectionResultLink")},
                {"path": ["indexStatus"], "value": local("index_status")},
                {"path": ["mobileUsability"], "value": local("mobile")},
                {"path": ["richResults"], "value": local("rich")}], "output": "result"}]
    semantics = {"ir_inspect": spec(ev, segment(*ops), output="result"),
        "ir_save": spec(ev, segment({"op": "write", "target": "saved", "mode": "replace", "input": inp(), "demands": [demand()]})),
        "ir_return": spec(ev)}
    return solve(*prepare(cfg, semantics, {"api": location("remote", "urlInspection.index.inspect", ev),
        "saved": location("storage", "inspection-result.json", ev)}, ev, "Return the inspection result and save that result on the save path."))


def environment_fixture():
    init = citation("scripts/src/config/settings.ts", 5, 9, "dotenv config is a zero-argument call that may load environment entries; its return is distinct from environment state.")
    ev = citation("scripts/src/config/settings.ts", 40, 48, "getSettings reads five named environment values and the current directory, retaining their current versions.")
    cfg = graph([instruction("ir_init", "invoke", [], "config_return"),
        instruction("ir_settings", "invoke", [], "settings"), instruction("ir_return", "return", [result("settings")])])
    field_pairs = [("GA4_PROPERTY_ID", "propertyId"), ("GA4_CLIENT_EMAIL", "clientEmail"),
        ("GA4_PRIVATE_KEY", "privateKey"), ("GA4_DEFAULT_DATE_RANGE", "defaultDateRange"), ("SEARCH_CONSOLE_SITE_URL", "siteUrl")]
    settings_ops = [{"op": "read", "location": "env", "output": "current_env"},
                    {"op": "call", "location": "cwd", "inputs": [], "output": "cwd"}]
    for field, output in field_pairs:
        settings_ops += [{"op": "select_part", "input": local("current_env"), "path": [field], "output": field},
            {"op": "compute", "inputs": [local(field), value("30d" if output == "defaultDateRange" else "")], "output": output}]
    settings_ops += [{"op": "compute", "inputs": [local("cwd"), value("results")], "output": "resultsDir"},
        {"op": "build", "container": "object", "parts": [
            {"path": [field], "value": local(field)} for field in [out for _, out in field_pairs] + ["resultsDir"]], "output": "settings"}]
    semantics = {
        "ir_init": spec(init, segment({"op": "read", "location": "env", "output": "before"}),
            {"kind": "cases", "output": "config_result", "cases": [{"name": "config_normal", "phase": "normal",
                "condition": "dotenv config returns; the exact overwritten keys and precedence remain unknown.", "disposition": "return",
                "segments": [segment({"op": "call", "location": "dotenv", "inputs": [], "output": "returned"},
                    {"op": "read", "location": "dotenv_file", "output": "file"},
                    {"op": "compute", "inputs": [local("before"), local("file")], "output": "possible_post"},
                    {"op": "write", "target": "env", "input": local("possible_post"), "mode": "replace", "may": True})],
                "yield": local("returned")}]}, output="config_result"),
        "ir_settings": spec(ev, segment(*settings_ops), output="settings"), "ir_return": spec(ev)}
    material, wire = prepare(cfg, semantics, {"env": location("runtime_context", "process.env", ev),
        "dotenv": location("tool", "dotenv.config", init), "dotenv_file": location("storage", ".env", init),
        "cwd": location("tool", "process.cwd", ev)}, ev, "Read the current settings without substituting config's return value for environment state.")
    wire["demands"] = [demand(target={"instruction_id": "ir_return", "side": "input", "index": 0})]
    return solve(material, wire)


def cache_clock_fixture():
    cache_ev = citation("scripts/src/core/client.ts", 87, 122, "Separate client singleton locations retain existing and newly created handle identities.")
    auth_ev = citation("scripts/src/core/client.ts", 67, 79, "The new Google auth handle depends on actual email and private-key settings.")
    call_ev = citation("scripts/src/api/indexing.ts", 57, 79, "Indexing uses its client, nested request parameters and a separate clock source for the fallback timestamp.")
    cfg = graph([instruction("ir_notify", "invoke", [literal("https://fixture.invalid/a")], "notification"),
        instruction("ir_save", "invoke", [result("notification")]), instruction("ir_return", "return", [result("notification")])])
    cases = []
    for name in ("existing", "created"):
        ops = [{"op": "read", "location": "indexing_cache", "output": "prior"}]
        if name == "created":
            ops += [{"op": "read", "location": "credentials", "output": "credentials"},
                    {"op": "compute", "inputs": [local("credentials")], "output": "new_handle", "evidences": [auth_ev]},
                    {"op": "write", "target": "indexing_cache", "mode": "replace", "input": local("new_handle"), "may": True}]
        cases.append({"name": name, "phase": "normal", "condition": "The indexing singleton is " + ("already present." if name == "existing" else "absent and created from current credentials."),
            "disposition": "return", "segments": [segment(*ops)], "yield": local("prior" if name == "existing" else "new_handle")})
    notify_ops = [{"op": "build", "container": "object", "parts": [
        {"path": ["requestBody", "url"], "value": inp()}, {"path": ["requestBody", "type"], "value": value("URL_UPDATED")}], "output": "request"},
        {"op": "call", "location": "publish", "inputs": [local("handle"), local("request")], "output": "response"},
        {"op": "select_part", "input": local("response"), "path": ["data", "urlNotificationMetadata", "latestUpdate", "notifyTime"], "output": "remote_time"},
        {"op": "select_part", "input": local("response"), "path": ["data", "urlNotificationMetadata", "url"], "output": "remote_url"},
        {"op": "compute", "inputs": [local("remote_url"), inp()], "output": "final_url"}]
    timestamp = {"kind": "cases", "output": "notify_time", "cases": [
        {"name": "remote_time", "phase": "normal", "condition": "The actual response has a truthy notification timestamp.",
         "disposition": "return", "segments": [], "yield": local("remote_time")},
        {"name": "clock_fallback", "phase": "normal", "condition": "The response has no truthy notification timestamp.",
         "disposition": "return", "segments": [segment({"op": "call", "location": "clock", "inputs": [], "output": "now"},
            {"op": "compute", "inputs": [local("now")], "output": "iso"})], "yield": local("iso")}]}
    semantics = {"ir_notify": spec(call_ev, {"kind": "cases", "cases": cases, "output": "handle", "evidences": [cache_ev]},
        segment(*notify_ops), timestamp, segment({"op": "build", "container": "object", "parts": [
            {"path": ["url"], "value": local("final_url")}, {"path": ["type"], "value": value("URL_UPDATED")},
            {"path": ["notifyTime"], "value": local("notify_time")}], "output": "notification"}), output="notification"),
        "ir_save": spec(call_ev, segment({"op": "write", "target": "saved", "input": inp(), "mode": "replace", "demands": [demand()]})),
        "ir_return": spec(call_ev)}
    locations = {name: location("runtime_context", name, cache_ev) for name in ("ga4_cache", "search_cache", "indexing_cache")}
    locations.update(credentials=location("runtime_context", "current_credentials", auth_ev),
        publish=location("remote", "urlNotifications.publish", call_ev), clock=location("tool", "Date clock", call_ev),
        saved=location("storage", "notification-result.json", call_ev))
    return solve(*prepare(cfg, semantics, locations, call_ev, "Return and save the indexing notification with its actual response or clock timestamp."))


def metadata_fixture(*, whole=False, sensitive_variant=False):
    ev = citation("scripts/src/api/metadata.ts", 38 if not whole else 81, 55 if not whole else 95,
        "The actual response is preserved at the selected metadata result boundary.")
    task_ev = citation("references/api-reference.md", 165 if not whole else 185, 174 if not whole else 193,
        "Discovery requires apiName, uiName and description; full-property metadata has its separate whole-response requirement.")
    cfg = graph([instruction("ir_metadata", "invoke", [literal({"name": "properties/fixture/metadata"})], "metadata"),
        instruction("ir_save", "invoke", [result("metadata")]), instruction("ir_return", "return", [result("metadata")])])
    paths = [[]] if whole else [["dimensions", EACH, name] for name in ("apiName", "uiName", "description")]
    semantics = {"ir_metadata": spec(ev, segment({"op": "call", "location": "api", "inputs": [inp()], "output": "response"}), output="response"),
        "ir_save": spec(ev, segment({"op": "write", "target": "saved", "mode": "replace", "input": inp(),
            "demands": [demand(path) for path in paths]})), "ir_return": spec(ev)}
    if not whole:
        semantics["ir_metadata"]["segments"][0]["ops"] += [
            {"op": "select_part", "input": local("response"), "path": ["dimensions"], "output": "dimensions"},
            {"op": "build", "container": "object", "parts": [{"path": ["dimensions"], "value": local("dimensions")}], "output": "discovery"}]
        semantics["ir_metadata"]["output_bindings"][0]["value"] = local("discovery")
    extra = None
    if sensitive_variant:
        extra = {"SENSITIVE-VARIANT.md": "Independent synthetic variant: dimensions in the metadata response contain a privateToken credential field. This is not a statement about the original GA4 API.\n"}
        sens_ev = citation("SENSITIVE-VARIANT.md", 1, 1, "This separate test mutation explicitly declares privateToken confidential.")
        semantics["ir_metadata"]["sensitivity"] = [{"value": local("response"), "path": ["dimensions", 0, "privateToken"],
            "label": "Synthetic private credential", "evidences": [sens_ev]}]
    return solve(*prepare(cfg, semantics, {"api": location("remote", "getMetadata", ev),
        "saved": location("storage", "metadata-result.json", ev)}, task_ev,
        "Preserve the complete metadata response." if whole else "Preserve discovery entries' apiName, uiName and description.", extra_source=extra))


def report_rows_fixture():
    ev = citation("scripts/src/api/reports.ts", 33, 42, "Actual report row values are nested under dimensionValues and metricValues member fields.")
    cfg = graph([instruction("ir_report", "invoke", [literal({"property": "properties/fixture"})], "response"),
        instruction("ir_summary", "invoke", [result("response")]), instruction("ir_raw_save", "invoke", [result("response")]),
        instruction("ir_return", "return", [result("response")])])
    semantics = {"ir_report": spec(ev, segment({"op": "call", "location": "api", "inputs": [inp()], "output": "response"}), output="response"),
        "ir_summary": spec(ev, segment({"op": "deliver", "target": "summary", "inputs": [inp()], "demands": [
            demand(["rows", EACH, field, EACH, "value"]) for field in ("dimensionValues", "metricValues")]})),
        "ir_raw_save": spec(ev, segment({"op": "write", "target": "saved", "mode": "replace", "input": inp(), "demands": [demand()]})),
        "ir_return": spec(ev)}
    # The field-only consumer is deliberately explicit test input, not an
    # invented assertion that GA4 contains a separate summarizer tool call.
    variant = "Independent boundary variant: a report consumer needs only every rows[].dimensionValues[].value and rows[].metricValues[].value; a separate raw-result save requires the entire response.\n"
    variant_ev = citation("ROW-CONSUMER-VARIANT.md", 1, 1, "The separate test consumer declares the field-only requirement; the original report defines the nested row shape.")
    semantics["ir_summary"]["evidences"] = [variant_ev]
    return solve(*prepare(cfg, semantics, {"api": location("remote", "runReport", ev),
        "summary": location("tool", "Explicit test report consumer", variant_ev), "saved": location("storage", "raw-report.json", ev)},
        variant_ev, "Preserve row dimension and metric values for the declared test consumer and the complete raw response for a raw-result save.",
        extra_source={"ROW-CONSUMER-VARIANT.md": variant}))


def comparison_save_fixture():
    """Internal saveResult has actual caller data, settings and metadata inputs.

    The selected normal path assumes the category directory already exists.
    Filename formatting and JSON encoding are left opaque; logical saved
    content retains its metadata/data structure under the runtime abstraction.
    """
    ev = citation("scripts/src/index.ts", 171, 203, "Comparison preserves the actual independently acquired period responses with their own date ranges.")
    saved_ev = citation("scripts/src/core/storage.ts", 55, 92, "saveResult binds its caller's data, reads settings and clock, writes a metadata wrapper, and returns a filepath.")
    cfg = graph([
        instruction("ir_compare", "invoke", [literal({"startDate": "7daysAgo", "endDate": "today"}),
            literal({"startDate": "14daysAgo", "endDate": "7daysAgo"})], "comparison"),
        instruction("ir_save", "invoke", [result("comparison"), literal("reports"), literal("date_comparison")], "filepath"),
        instruction("ir_return", "return", [result("comparison")])])
    comparison_ops = []
    for number in (0, 1):
        comparison_ops += [{"op": "build", "container": "object", "parts": [
            {"path": ["dateRange"], "value": inp(number)},
            {"path": ["dimensions"], "value": value(["date"])},
            {"path": ["metrics"], "value": value(["activeUsers", "sessions", "screenPageViews"])},
            {"path": ["save"], "value": value(False)}], "output": "request" + str(number)},
            {"op": "call", "location": "report_helper", "inputs": [local("request" + str(number))], "output": "response" + str(number)}]
    comparison_ops.append({"op": "build", "container": "object", "parts": [
        {"path": ["period" + str(number + 1), field], "value": inp(number) if field == "dateRange" else local("response" + str(number))}
        for number in (0, 1) for field in ("dateRange", "data")], "output": "comparison"})
    save_ops = [{"op": "read", "location": "settings", "output": "settings"},
        {"op": "select_part", "input": local("settings"), "path": ["resultsDir"], "output": "directory"},
        {"op": "select_part", "input": local("settings"), "path": ["propertyId"], "output": "property"},
        {"op": "call", "location": "clock", "inputs": [], "output": "now"},
        {"op": "compute", "inputs": [local("now")], "output": "iso_time"},
        {"op": "compute", "inputs": [local("directory"), inp(1), inp(2), local("now")], "output": "filepath"},
        {"op": "build", "container": "object", "parts": [
            {"path": ["metadata", "savedAt"], "value": local("iso_time")},
            {"path": ["metadata", "propertyId"], "value": local("property")},
            {"path": ["metadata", "category"], "value": inp(1)},
            {"path": ["metadata", "operation"], "value": inp(2)},
            {"path": ["data"], "value": inp()}], "output": "wrapped"},
        {"op": "write", "target": "saved", "mode": "replace", "input": local("wrapped"), "demands": [demand()]}]
    semantics = {"ir_compare": spec(ev, segment(*comparison_ops), output="comparison"),
        "ir_save": spec(saved_ev, segment(*save_ops), output="filepath"), "ir_return": spec(ev)}
    locations = {"report_helper": location("tool", "runReport return boundary", ev),
        "settings": location("runtime_context", "getSettings current result", saved_ev),
        "clock": location("tool", "Date clock", saved_ev), "saved": location("storage", "symbolic:generated-result-path", saved_ev)}
    return solve(*prepare(cfg, semantics, locations, ev, "Save and return comparison results containing both actual period reports."))
