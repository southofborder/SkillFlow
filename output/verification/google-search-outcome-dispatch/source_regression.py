"""Offline integration regression on the 75-IR graph. Never invoke the audited Skill.

The legacy graph has no machine-readable route roles. ROUTES below and the
replacement processing rows are authored test expectations, not model output.
The two source files, original Task, and original observation stay read-only.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from skillflow.common.source_evidence import _digest
from skillflow.document_guided.action_bindings import action_coordinates
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.document_guided.fragments import assemble_outcome_dispatches
from skillflow.document_guided.graph_facts import assemble_graph_facts, from_accepted_cfg
from skillflow.document_guided.graph_slots import apply_graph_updates, plan_graph_repair
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.solver import propagate
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RUN = ROOT / "experiments/doe/runs/document-guided-google-search-call-routing-high-20261125-194132"
ROUTES = {
    "module.import_sys": ("module.import_json", "module.throw"),
    "module.import_json": ("module.import_requests", "module.throw"),
    "module.import_requests": ("module.import_os", "module.throw"),
    "module.import_os": ("module.guard", "module.throw"),
    "public.request": ("public.status", "public.throw"),
    "public.status": ("public.decode", "public.throw"),
    "public.decode": ("public.return", "public.throw"),
    "cli.usage_print": ("cli.usage_exit", "cli.unhandled"),
    "cli.parse_count": ("cli.bind_count", "cli.unhandled"),
    "cli.read_api_key": ("cli.read_cse_id", "cli.unhandled"),
    "cli.read_cse_id": ("cli.check_credentials", "cli.unhandled"),
    "cli.credential_error_print": ("cli.credential_exit", "cli.unhandled"),
    "inline.request": ("inline.status", "cli.catch_format"),
    "inline.status": ("inline.decode", "cli.catch_format"),
    "inline.decode": ("cli.serialize", "cli.catch_format"),
    "cli.serialize": ("cli.result_print", "cli.catch_format"),
    "cli.result_print": ("cli.done", "cli.catch_format"),
    "cli.catch_format": ("cli.caught_error_print", "cli.unhandled"),
    "cli.caught_error_print": ("cli.caught_error_exit", "cli.unhandled"),
}


def read(path):
    return json.loads(path.read_bytes())


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def graph():
    provenance = read(OUT.parent / "google-search-call-routing-20261125/source-provenance.json")
    source_files = []
    for name, pin in provenance["files"].items():
        body = (RUN / "source/inputs/package" / name).read_bytes()
        assert len(body) == pin["bytes"] and sha256(body).hexdigest() == pin["sha256"]
        source_files.append({"path": name, "content": body.decode(), "sha256": pin["sha256"]})
    source = {"files": source_files, "source_sha256": _digest([
        {"path": f["path"], "sha256": f["sha256"]} for f in source_files])}
    files = {"skill/" + f["path"]: f["content"] for f in source_files}
    old = read(RUN / "steps/graph/value.json")["assembly"]
    facts = deepcopy(old["facts"])
    original_check = assemble_graph_facts(facts, files=files, canonical_ids=old["id_map"])
    missing_routes = [gap for gap in original_check.gaps if gap["code"] == "outcome_targets_required"]
    assert len(missing_routes) == len(ROUTES), original_check.gaps
    save("historical-untyped-diagnostics.json", missing_routes)
    plan = plan_graph_repair(original_check, files=files)
    updates = []
    for sid, slot in plan["slots"].items():
        assert slot["kind"] == "outcome_targets"
        block = facts["blocks"][slot["path"][1]]
        normal, exceptional = ROUTES[block["ref"]]
        assert {normal, exceptional} == set(slot["targets"])
        updates.append({"slot_id": sid, "value": {"on_return": normal, "on_throw": exceptional}})
    assert len(updates) == len(ROUTES)
    built = apply_graph_updates(original_check, plan,
        {"plan_sha256": plan["plan_sha256"], "updates": updates}, files=files)
    assert built.cfg and not built.gaps and not built.patch_diagnostics, built.gaps
    assert from_accepted_cfg(built.cfg, files=files).cfg == built.cfg
    ids = {old_id: built.id_map[k][ref] for k in ("instructions", "blocks", "results")
           for ref, old_id in old["id_map"][k].items()}
    assert len(old["id_map"]["instructions"]) == 75
    save("offline-graph.json", built.cfg)
    save("historical-IR-map.json", {ref: {"old": orig, "new": ids[orig]}
        for ref, orig in old["id_map"]["instructions"].items()})
    return source, built, ids


def arg(i):
    return {"kind": "input", "index": i}


def local(name):
    return {"kind": "local", "name": name}


def literal(value):
    return {"kind": "literal", "value": value}


def segment(*ops):
    return {"mode": "local", "returns": [], "ops": list(ops)}


def compute(output, inputs):
    return {"op": "compute", "inputs": inputs, "dependencies": ["derived"] * len(inputs), "output": output}


def remap(value, ids):
    if isinstance(value, dict):
        return {ids.get(k, k): remap(v, ids) for k, v in value.items()}
    if isinstance(value, list):
        return [remap(v, ids) for v in value]
    return ids.get(value, value) if isinstance(value, str) else value


def protected(ir, name, wire):
    span = ir["metadata"]["source_span"]
    e = {**span, "reason": "Offline regression at the operation in the original Python source."}
    n = len(ir["outputs"])
    spec = {"evidences": [e], "segments": []}
    ret = {"name": "returned", "condition": "The operation returns normally.",
           "phase": "normal", "disposition": "return"}
    def failure(phase):
        return {"name": phase, "phase": phase, "disposition": "throw",
            "condition": {"local_error": "Local processing raises.",
                "pre_request_error": "The operation raises before the request is sent.",
                "post_request_error": "The request was sent, but no response was received."}[phase],
            "raise": local("__raised__")}
    def required(i, path):
        return {"requirement_id": "R9", "target": {"kind": "input", "index": i},
            "preserve": "value", "path": path, "reason": "Required parameter of the declared search request."}
    cases = [ret, failure("local_error")]
    head = []
    ops = []
    yielded = literal(None)
    if name.startswith("module.import_") or name in ("cli.read_api_key", "cli.read_cse_id"):
        if name.startswith("module.import_"):
            loc = name
            wire["locations"][loc] = {"kind": "runtime_context",
                "name": ir["inputs"][0]["identifier"], "evidences": [e]}
        else:
            loc = "environment_key" if name.endswith("api_key") else "environment_cx"
        ops.append({"op": "read", "location": loc, "output": "acquired"})
        yielded = local("acquired")
        if name == "cli.read_api_key":
            spec["sensitivity"] = [{"value": yielded, "case_path": ["segments", 0, "cases", 0],
                "path": [], "property": "value", "label": "API authentication credential", "evidences": [e]}]
    elif name in ("public.request", "inline.request"):
        fields = [required(1, [f]) for f in ("q", "key", "cx", "num")]
        request = {"op": "call", "location": "google", "inputs": [arg(1), arg(2)],
            "output": "response", "demands": [required(0, []), *fields]}
        ops.append(request)
        yielded = local("response")
        after = failure("post_request_error")
        after["segments"] = [segment({"op": "deliver", "target": "google",
            "inputs": [arg(1), arg(2)], "demands": [required(0, []), *fields]})]
        cases = [ret, failure("pre_request_error"), after]
    elif name in ("public.decode", "inline.decode"):
        ops.append(compute("decoded", [arg(0)]))
        yielded = local("decoded")
    elif name.endswith("_print"):
        ops.append({"op": "deliver", "target": "stdout", "inputs": [arg(0)]})
    elif name in ("cli.parse_count", "cli.serialize", "cli.catch_format"):
        if name == "cli.parse_count":
            head.append({"op": "select_part", "input": arg(0), "path": [2], "output": "prefix"})
            prefix = local("prefix")
        elif name == "cli.serialize":
            prefix = arg(0)
        else:
            head.append(compute("prefix", [arg(0)]))
            prefix = local("prefix")
        spec["output_bindings"] = [{"output_index": 0, "value": prefix}]
        ops.append(compute("normal_value", [prefix]))
        yielded = local("normal_value")
    elif name not in ("public.status", "inline.status"):
        raise AssertionError(name)
    if head:
        spec["segments"].append(segment(*head))
    if ops:
        ret["segments"] = [segment(*ops)]
    def required_range(i, paths):
        return {"input_index": i, "required": [{"property": "value", "path": path} for path in paths],
                "remainder": "independent", "reason": "Inputs to this source operation in the regression scenario."}
    for op in [*head, *ops, *(o for case in cases for s in case.get("segments", []) for o in s["ops"])]:
        if op["op"] in ("call", "deliver"):
            paths = [[[]], [[f] for f in ("q", "key", "cx", "num")]] if (
                op.get("location", op.get("target")) == "google") else [[[]]]
            op["input_contract"] = {"inputs": [required_range(i, v) for i, v in enumerate(paths)],
                                    "reason": "Declared search parameters or print payload.", "evidences": [e]}
        elif op["op"] == "compute":
            op["demand_transfer"] = {"rules": [{"output": {"property": "value", "path": []},
                "inputs": [required_range(i, [[]]) for i in range(len(op["inputs"]))],
                "reason": "The conversion takes the indicated value as its operand.", "evidences": [e]}]}
    ret["yield"] = yielded
    spec["segments"].append({"kind": "cases", "outcome": {"return_index": n-2, "exception_index": n-1},
                             "cases": cases})
    actions = ir["metadata"]["source_actions"]
    if len(actions) > 1:
        first, second = (row["ref"] for row in actions)
        groups = {first: [], second: []}
        for path, _ in action_coordinates(spec):
            before = path[0] == "output_bindings" or (head and path[:2] == ("segments", 0))
            groups[first if before else second].append(list(path))
        spec["action_bindings"] = groups
    return spec


def annotation(built, ids, material):
    original = read(RUN / "revision/annotation/audit/wire-annotation.json")
    wire = remap({k: v for k, v in original.items() if not k.startswith("_")}, ids)
    cfg = built.cfg
    lookup = {ir["id"]: ir for b in cfg["blocks"].values() for ir in b["instructions"]}
    wire["processing_gaps"] = []
    for name in ROUTES:
        term = lookup[built.id_map["instructions"][f"/blocks/{name}/exit"]]
        ir = lookup[term["metadata"]["outcome_dispatch"]["producer"]]
        wire["ir_semantics"][ir["id"]] = protected(ir, name, wire)
    assemble_outcome_dispatches(wire, material)
    from skillflow.document_guided.python_handlers import handler_transfers
    wire["ir_semantics"].update(handler_transfers(cfg, {
        "skill/" + row["path"]: row["content"] for row in material["source"]["files"]}))
    return wire


def main():
    source, built, ids = graph()
    task = read(RUN / "task/task.json")
    material = prepare_material(source, built.cfg, task_baseline=task)
    wire = annotation(built, ids, material)
    save("offline-authored-wire.json", wire)
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    registry = DataRegistry("google-search-75-ir-offline")
    seed = {}
    seeds = {"module_name": "__main__", "argv": ["search.py", "sample query"],
             "public_query": "independent query", "public_key": "fixture-public-key",
             "public_cx": "fixture-public-cx", "environment_key": "fixture-cli-key",
             "environment_cx": "fixture-cli-cx"}
    for loc, value in seeds.items():
        address = wire["locations"][loc]["name"]
        d = registry.register_source(loc, acquired_from="runtime_context:" + address, at="fixture",
            content=LiteralContent(value=value))
        seed[FlowLocation(kind="runtime_context", name=address)] = frozenset([d.id])
    for name in ROUTES:
        if name.startswith("module.import_"):
            address = wire["locations"][name]["name"]
            d = registry.register_source(name, acquired_from=address, at="fixture")
            seed[FlowLocation(kind="runtime_context", name=address)] = frozenset([d.id])
    solved = propagate(built.cfg, to_payload(compiled), initial_registry=registry,
                       initial_state=FlowState.from_mapping(seed))
    solved.records.validate()
    # Union the reachable dispositions across CLI argument/credential scenarios.
    # Each scenario is a separate abstract solve on the same graph and Task.
    dispatch_ids = {built.id_map["instructions"][f"/blocks/{name}/exit"] for name in ROUTES}
    def executed(result):
        return {ir for ir, record in result.records.records_dict().items()
                if ir in dispatch_ids and record.get("outcome_routes")}
    covered = {"configured_cli_default_count": sorted(executed(solved))}
    for scenario, loc, val in (("absent_cli_query", "argv", ["search.py"]),
                               ("supplied_cli_count", "argv", ["search.py", "sample query", "0"]),
                               ("empty_cli_credential", "environment_key", "")):
        location = FlowLocation(kind="runtime_context", name=wire["locations"][loc]["name"])
        d = registry.register_source(scenario, acquired_from="runtime_context:" + location.name,
                                     at="fixture", content=LiteralContent(value=val))
        initial = FlowState.from_mapping({**seed, location: frozenset([d.id])})
        extra = propagate(built.cfg, to_payload(compiled), initial_registry=registry, initial_state=initial)
        extra.records.validate()
        covered[scenario] = sorted(executed(extra))
    assert set.union(*(set(v) for v in covered.values())) == dispatch_ids, covered
    save("offline-forward.json", {"status": solved.status, "coverage": solved.coverage,
        "diagnostics": solved.diagnostics, "records": solved.records.records_dict()})
    facts = materials_from_result(solved, material=material, raw_annotation=raw, compiled_annotation=compiled,
                                  mapping=mapping, wire_annotation=saved)
    review = prepare_joint_sensitivity_review(facts, facts.annotation)
    demands, doe = review.demand_dict(), review.to_dict()
    save("offline-doe.json", doe)
    save("offline-demands.json", demands)
    requests = [ids[k] for k in ("ir_020", "ir_057")]
    assert all(solved.coverage[r] == "processed" for r in [*requests, ids["ir_071"]]), solved.diagnostics
    deriv = doe["derivations"]["sensitivity"]
    results = {}
    for ir, origin in zip(requests, ("public_key", "environment_key"), strict=True):
        rows = [row for sink in doe["sinks"] if sink["boundary"]["instruction_id"] == ir
                for row in sink["data_reviews"] if deriv[row["derivation_id"]]["path"] == ["key"]]
        assert rows, (ir, "no key comparison")
        payloads = {deriv[row["derivation_id"]]["data_id"] for row in rows}
        assert all(row["input_index"] == 1 for row in rows)
        endpoint = wire["locations"]["google"]["name"]
        assert all(loc["name"] == endpoint for event in solved.records.records_dict()[ir]["events"]
                   for op in event["atomic_ops"] for loc in op.get("endpoints", []) if loc["kind"] == "remote")
        todo = [row["derivation_id"] for row in rows]
        seen, key_ids = set(), set()
        while todo:
            sid = todo.pop()
            if sid not in seen:
                seen.add(sid)
                signal = deriv[sid]
                if "explicit_declaration" in signal["rules"]:
                    key_ids.add(signal["data_id"])
                todo.extend(signal["parents"])
        expected = seed[FlowLocation(kind="runtime_context", name=wire["locations"][origin]["name"])]
        assert key_ids == expected, (ir, key_ids, expected)
        retained = [d for d in demands["derivations"].values() if d["node"]["instruction_id"] == ir
                    and d["requirement_id"] == "R9" and d["path"] == ["key"] and not d["conservative"]]
        assert retained, ir
        results[ir] = {"key_comparisons": [r["id"] for r in rows], "recipient": endpoint,
            "request_argument": 1, "payload_versions": sorted(payloads), "key_versions": sorted(key_ids),
            "key_origin": wire["locations"][origin]["name"], "R9_precise_demands": len(retained)}
    b = built.id_map["blocks"]
    gate = b["cli.catch_format.exception_match"]
    predecessors = {edge["source_block_id"] for edge in built.cfg["edges"] if edge["target_block_id"] == gate}
    assert predecessors == {b[name] for name in ("inline.request", "inline.status", "inline.decode",
                                                   "cli.serialize", "cli.result_print")}
    for block in predecessors:
        term = built.cfg["blocks"][block]["instructions"][-1]
        assert term["metadata"]["outcome_dispatch"]["on_throw"] == gate
    reached = set()
    todo = [b["public.arguments"]]
    while todo:
        block = todo.pop()
        if block not in reached:
            reached.add(block)
            todo.extend(e["target_block_id"] for e in built.cfg["edges"] if e["source_block_id"] == block)
    assert not reached.intersection({gate, b["cli.result_print"], b["cli.caught_error_print"]})
    assert not any(s["data_reviews"] for s in doe["sinks"] if s["boundary"]["instruction_id"] == ids["ir_071"])
    summary = {"provenance": "Source-grounded authored regression over the historical 75 IR, not online output.",
        "historical_IR": 75, "protected_pairs": len(ROUTES), "task_sha256": task["task_sha256"],
        "source_sha256": source["source_sha256"], "coverage": dict(Counter(solved.coverage.values())),
        "requests": results, "handler_predecessors": sorted(predecessors),
        "exercised_dispatches_by_scenario": covered,
        "cli_error_stdout": solved.coverage[ids["ir_071"]], "stdout_key_established": False,
        "comparison_count": sum(len(s["data_reviews"]) for s in doe["sinks"]),
        "assumptions": ["Configured CLI with omitted count; independent public invocation with omitted count.",
            "The first local subaction in the three composite operations succeeds in this fixture.",
            "Opaque external exception has no inferred message fields. All inputs are synthetic."]}
    save("offline-acceptance.json", summary)
    print(json.dumps(summary, ensure_ascii=True))


if __name__ == "__main__":
    main()
