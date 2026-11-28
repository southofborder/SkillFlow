"""Write a new authored offline fixture using the 65 original Google Search IR IDs."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RUN = ROOT / "experiments/doe/runs/document-guided-google-search-full-high-20261125-172053"
sys.path.insert(0, str(ROOT / "src"))

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import _digest
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.data.summary import content_options
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.solver import propagate
from skillflow.doe.input_assessments import deletable_reduction
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.doe.sensitivity_results import resolve_data_review


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(path):
    return json.loads(path.read_bytes())


def ev(first, last=None, reason=None):
    return {"file": "skill/scripts/search.py", "start_line": first, "end_line": last or first,
            "reason": reason or "Authored offline description of this operation in the unmodified source."}


def inp(i=0):
    return {"kind": "input", "index": i}


def local(name):
    return {"kind": "local", "name": name}


def lit(value):
    return {"kind": "literal", "value": value}


def segment(*ops):
    return {"mode": "local", "returns": [], "ops": list(ops)}


def bind(index, value):
    return {"output_index": index, "value": value}


def sem(line, *segments, outputs=(), action_bindings=None):
    result = {"evidences": [ev(line)], "segments": list(segments), "output_bindings": list(outputs)}
    if action_bindings is not None:
        result["action_bindings"] = action_bindings
    return result


def goal(req, target="self", *, prop="action", path=(), reason=None):
    return {"requirement_id": req, "target": {"kind": target, **({"index": 0} if target == "input" else {})},
            "preserve": prop, "path": list(path),
            "reason": reason or "Retain this source-backed operation or its specified actual value."}


def transfer(line, inputs, reason):
    return {"rules": [{"output": {"property": "value", "path": []}, "inputs": [
        {"input_index": index, "required": [{"property": "value", "path": []}], "remainder": "independent",
         "reason": reason} for index in range(inputs)], "reason": reason, "evidences": [ev(line)]}]}


def compute(name, args, *, line, reason, preserve_inputs=False):
    result = {"op": "compute", "inputs": args, "dependencies": ["derived"] * len(args), "output": name}
    if preserve_inputs:
        result["demand_transfer"] = transfer(line, len(args), reason)
    else:
        result["demand_transfer"] = {"rules": [{"output": {"property": "value", "path": []},
            "inputs": [{"input_index": index, "required": [], "remainder": "unresolved", "reason": reason,
                        "gap": {"code": "unsupported_relation", "reason": "The executable source does not expose this operation's internal content relation.",
                                "missing": "Evidence for the operand properties sufficient to determine the complete library result.",
                                "resolution": "Supply a source-backed model of the operation internals and its value use.",
                                "evidences": [ev(line)]}} for index in range(len(args))],
            "reason": reason, "evidences": [ev(line)]}]}
    return result


def case(line, name, phase, *, body=(), yielded=None, thrown=False, reason=None):
    result = {"name": name, "phase": phase, "disposition": "throw" if thrown else "return",
              "condition": reason or f"This source operation reaches its {name} outcome.",
              "segments": list(body), "evidences": [ev(line)]}
    if yielded is not None:
        result["yield"] = yielded
    if thrown:
        result["raise"] = local("__raised__")
    return result


def protected(line, completion, exception, variants, normal=None):
    ports = {"completion_index": completion, "exception_index": exception}
    if normal is not None:
        ports["return_index"] = normal
    return {"kind": "cases", "outcome": ports, "cases": list(variants), "evidences": [ev(line)]}


def returns_or_raises(line, normal, exception, completion, operation, names=("normal", "raised")):
    return protected(line, completion, exception, [
        case(line, names[0], "normal", body=[segment(operation)], yielded=local(operation["output"])),
        case(line, names[1], "local_error", thrown=True)], normal)


def route(line, normal, exceptional):
    return sem(line, segment({"op": "branch", "input": inp(), "predicate": "selector", "selector": {
        "path": [], "tests": [{"kind": "equals", "value": True}], "outcome": 0},
        "true_target": normal, "false_target": exceptional}))


def deliver(location, arg, *goals):
    return {"op": "deliver", "target": location, "inputs": [arg], "demands": list(goals)}


def write_source():
    files = []
    for name in ("SKILL.md", "scripts/search.py"):
        data = (RUN / "source/inputs/package" / name).read_bytes()
        target = OUT / "source-package" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files.append({"path": name, "content": data.decode("utf-8"), "sha256": sha256(data).hexdigest()})
    source = {"files": files, "source_sha256": _digest([{k: row[k] for k in ("path", "sha256")} for row in files])}
    save("source-bundle.json", source)
    return source


def normalize_terminal_owners(cfg):
    """The same existing terminal owns the actual sys.exit; topology and ports stay fixed."""
    instructions = {ir["id"]: ir for b in cfg["blocks"].values() for ir in b["instructions"]}
    changes = []
    for source, terminal in (("ir_014", "ir_015"), ("ir_030", "ir_031"), ("ir_050", "ir_051")):
        actions = instructions[source]["metadata"]["source_actions"]
        action = actions[-1]
        assert action["ref"].endswith(".exit")
        actions.pop()
        previous = instructions[terminal]["metadata"]["source_actions"]
        assert len(previous) == 1 and previous[0]["source"] == action["source"]
        instructions[terminal]["metadata"]["source_actions"] = [{**previous[0], "ref": action["ref"]}]
        changes.append({"action": action["ref"], "from": source, "to": terminal, "source": action["source"]})
    return changes


def author(old):
    wire = deepcopy(old)
    wire.pop("_fragment_origins", None)
    wire.pop("_validation_gaps", None)
    specs = wire["ir_semantics"]
    # Keep the accepted request build, literal endpoint, input contract and normal
    # paired call, then place it in the outcome of that same invocation.
    for ir in ("ir_036", "ir_056"):
        build, call, *_ = specs[ir]["segments"][0]["ops"]
        key_value = goal("R9", "input", prop="value", path=["params", "key"],
            reason="The Task explicitly requires this invocation's API key in its request key parameter.")
        call["demands"].append(key_value)
        send_on_failure = deliver("google_api", local("request"), goal("R9"), key_value)
        send_on_failure["input_contract"] = deepcopy(call["input_contract"])
        specs[ir]["segments"] = [segment(build), protected(14, 2, 1, [
            case(14, "received_response", "normal", body=[segment(call)], yielded=local("http_response")),
            case(14, "raised_before_transmission", "pre_request_error", thrown=True,
                 reason="A request exception can precede transmission; this path has no remote effect or response."),
            case(14, "raised_after_transmission", "post_request_error", body=[segment(send_on_failure)], thrown=True,
                 reason="The request may have been sent before failure; this alternative retains the request without a successful response."),
        ], normal=0)]
        specs[ir].pop("output_bindings")

    for ir, line, req in (("ir_014", 20, "R6"), ("ir_030", 31, "R8")):
        specs[ir] = sem(line, segment(deliver("stdout", inp(), goal(req), goal(req, "input", prop="value"))))

    count = compute("converted", [local("count_text")], line=24, preserve_inputs=True,
                    reason="Python int consumes the actual selected count string.")
    specs["ir_018"] = sem(24, segment({"op": "select_part", "input": inp(), "path": [2], "output": "count_text"}),
        returns_or_raises(24, 1, 2, 3, count), outputs=[bind(0, local("count_text"))],
        action_bindings={"cli.count.project": [["segments", 0, "ops", 0], ["output_bindings", 0]],
                         "cli.count.convert": [["segments", 1, *suffix] for suffix in (
                             ["outcome"], ["cases", 0, "condition"], ["cases", 0, "segments", 0, "ops", 0],
                             ["cases", 0, "yield"], ["cases", 1, "condition"], ["cases", 1, "raise"],
                             ["cases", 1, "disposition"])]})
    for ident, line, normal, exceptional in (
        ("ir_019", 24, "block_014", "block_012"),
        ("ir_037", 14, "block_022", "block_027"),
        ("ir_039", 15, "block_023", "block_027"),
        ("ir_041", 16, "block_024", "block_027"),
        ("ir_043", 36, "block_025", "block_027"),
        ("ir_045", 36, "block_026", "block_027"),
        ("ir_057", 14, "block_034", "block_033"),
        ("ir_060", 15, "block_036", "block_035"),
        ("ir_063", 16, "block_038", "block_037"),
    ):
        specs[ident] = route(line, normal, exceptional)

    for ident, line in (("ir_038", 15), ("ir_040", 16), ("ir_059", 15), ("ir_062", 16)):
        text = "Status checking" if line == 15 else "JSON decoding"
        op = compute("method_return", [inp()], line=line,
                     reason=f"{text} consumes this invocation's actual acquired HTTP response. Its sufficient internal fields are not established.")
        op["demands"] = [goal("R10", reason=f"Perform {text.lower()} on the actual response in source order.")]
        specs[ident] = sem(line, returns_or_raises(line, 0, 1, 2, op))

    serial = compute("serialized", [inp(), inp(2)], line=36, preserve_inputs=True,
                     reason="json.dumps renders the actual decoded result with indent=2; member-level necessity is separate.")
    specs["ir_042"] = sem(36, returns_or_raises(36, 1, 2, 3, serial), outputs=[bind(0, inp())],
        action_bindings={"cli.results.bind": [["output_bindings", 0]],
                         "cli.results.serialize": [["segments", 0, *suffix] for suffix in (
                             ["outcome"], ["cases", 0, "condition"], ["cases", 0, "segments", 0, "ops", 0],
                             ["cases", 0, "yield"], ["cases", 1, "condition"], ["cases", 1, "raise"],
                             ["cases", 1, "disposition"])]})
    partial = compute("possible_partial_print", [inp()], line=36,
                      reason="An exception during stdout printing leaves the already emitted portion unspecified.")
    partial["dependencies"] = ["possible"]
    specs["ir_044"] = sem(36, protected(36, 1, 0, [
        case(36, "printed", "normal", body=[segment(deliver("stdout", inp(), goal("R11"), goal("R11", "input", prop="value")))]),
        case(36, "raised_before_stdout", "pre_request_error", thrown=True,
             reason="No stdout delivery precedes this local print failure."),
        case(36, "raised_after_possible_partial_stdout", "local_error",
             body=[segment(partial, deliver("stdout", local("possible_partial_print")))], thrown=True,
             reason="This local print failure follows possible partial output, without claiming complete delivery."),
    ]))

    stringify = compute("exception_string", [inp()], line=38, preserve_inputs=True,
                        reason="str(e) depends on the actual selected exception object, with no invented message fields.")
    format_op = compute("diagnostic", [inp(1), local("exception_string")], line=38, preserve_inputs=True,
                       reason="The real diagnostic prints the source literal prefix and the complete str(e).")
    specs["ir_050"] = sem(38, segment(stringify, format_op, deliver("stdout", local("diagnostic"), goal("R12"),
        goal("R12", "input", prop="value", reason="R12 explicitly preserves the full formatted exception diagnostic."))),
        outputs=[bind(0, inp()), bind(1, local("exception_string")), bind(2, local("diagnostic"))],
        action_bindings={"cli.exception.bind": [["output_bindings", 0]],
                         "cli.exception.stringify": [["segments", 0, "ops", 0], ["output_bindings", 1]],
                         "cli.error.format": [["segments", 0, "ops", 1], ["output_bindings", 2]],
                         "cli.error.print": [["segments", 0, "ops", 2]]})

    wire["processing_gaps"] = [gap for gap in wire["processing_gaps"] if not gap.get("unmodeled")]
    wire["processing_gaps"].append({"instruction_id": "ir_050", "reason":
        "The existing graph owns the handler print and following exit but contains no outgoing edge for failure in the handler itself. "
        "This fixture models normal handler delivery and exit; it leaves handler-internal failures unresolved.",
        "evidences": [ev(37, 39)], "locations": ["stdout"], "unmodeled": False})
    realizations = {row["requirement_id"]: row for row in wire["realizations"]}
    realizations["R7"].pop("gaps", None)
    realizations["R9"]["gaps"][0]["reason"] = (
        "Whether GET transmits before failure remains a pair of explicit alternatives. "
        "The source does not establish the external interface's minimum; the Task independently requires the supplied request fields.")
    realizations["R10"]["gaps"][0]["reason"] = "The extent of HTTP-response fields needed for status checking and JSON decoding remains unresolved."
    realizations["R11"]["gaps"].pop()
    realizations["R12"]["gaps"].pop()
    return wire


def seed(wire):
    state = {}
    registry = DataRegistry("google-search-65-ir-authored-offline-witness")
    supplied = {
        "analysis.activation": ["module_evaluation", "public_function"],
        "module_evaluation.__name__": ["__main__", "google_search"],
        "direct_execution.sys.argv": [["search.py"], ["search.py", "example"], ["search.py", "example", "3"]],
        "google_search.invocation.query": ["public example"],
        "google_search.invocation.api_key": ["PUBLIC_DEMO_ONLY"],
        "google_search.invocation.cse_id": ["PUBLIC_DEMO_CX"],
        "google_search.invocation.num_results": [5],
        "process environment: GOOGLE_API_KEY": ["CLI_DEMO_ONLY", None],
        "process environment: GOOGLE_CSE_ID": ["CLI_DEMO_CX", None],
    }
    for location in wire["locations"].values():
        if location["kind"] == "runtime_context":
            supplied.setdefault(location["name"], [f"fixture:{location['name']}"])
    for name, values in supplied.items():
        ids = [registry.register_source(canonical_sha256([name, value]), acquired_from=f"runtime_context:{name}",
               content=LiteralContent(value=value)).id for value in values]
        state[FlowLocation(kind="runtime_context", name=name)] = frozenset(ids)
    return registry, FlowState.from_mapping(state)


def named_evidence(cfg, solved, backward, doe):
    records = solved.records.records_dict()
    projection_registry = DataRegistry.from_dict(solved.registry.to_dict())
    assert set(records) == {ir["id"] for block in cfg["blocks"].values() for ir in block["instructions"]}
    assessments = {(row["operation_id"], row["input_index"]): row for row in backward["input_assessments"]
                   if row["node_kind"] == "op_input"}

    def demands(row, requirement_id, path):
        required = [entry for entry in row["ranges"] if entry["status"] == "required"
                    and entry["path"] == path and entry["property"] == "value"]
        refs = {ref for entry in required for ref in entry["demand_refs"]}
        selected = [ref for ref in sorted(refs)
                    if backward["derivations"][ref]["requirement_id"] == requirement_id]
        assert selected, (row["operation_id"], requirement_id, path)
        return selected

    def capture(label, call, dispatch, seed_ir, expected_blocks, ready, source):
        branch, = [op for event in records[dispatch]["events"] for op in event["atomic_ops"] if op["op"] == "branch"]
        outcomes = records[call]["outcomes"]
        assert set(branch["branch_targets"]) == set(expected_blocks)
        assert {value for outcome in outcomes for value in outcome["completion"]} == set(branch["inputs"][0])
        paths = []
        for sink in doe["sinks"]:
            if (sink["boundary"]["instruction_id"], sink["boundary"]["sink_type"]) != (call, "network_send"):
                continue
            actual, = sink["actual_payload"]
            slot = assessments[(actual["operation_id"], 0)]
            refs = demands(slot, "R9", ["params", "key"])
            observations = []
            for candidate in actual["inputs"][0]:
                parts = projection_registry.resolve_part_candidates(candidate, ["params", "key"])
                options = [option for part in parts for option in content_options(projection_registry, part.id)]
                observations.append({"payload_data_id": candidate, "content_options": options})
            assert any(option == {"form": "literal", "value": ready}
                       for observation in observations for option in observation["content_options"])
            for candidate in slot["data_ids"]:
                assert deletable_reduction(backward, actual["operation_id"], 0, candidate, ["params", "key"]) == (None, [])
            comparisons = [resolve_data_review(row, sink, doe["derivations"]["sensitivity"]) for row in sink["data_reviews"]]
            paths.append({"operation_id": actual["operation_id"], "data_ids": actual["inputs"][0], "key_values": observations,
                          "key_demand_derivations": refs, "compared": comparisons})
        assert len(paths) == 2, (label, paths)
        return {"activation": label, "key_source_ir": seed_ir, "key_source_location": source,
                "call_ir": call, "dispatch_ir": dispatch, "outcomes": outcomes,
                "branch_alternatives": branch["alternatives"], "request_boundaries": paths}

    cli = capture("CLI module execution", "ir_036", "ir_037", "ir_025", ("block_022", "block_027"),
                  "CLI_DEMO_ONLY", "runtime_context:process environment: GOOGLE_API_KEY")
    public = capture("Independent public function call", "ir_056", "ir_057", "ir_052", ("block_033", "block_034"),
                     "PUBLIC_DEMO_ONLY", "runtime_context:google_search.invocation.api_key")
    stdout, = [sink for sink in doe["sinks"] if sink["boundary"]["instruction_id"] == "ir_050"]
    output, = stdout["actual_payload"]
    slot = assessments[(output["operation_id"], 0)]
    refs = demands(slot, "R12", [])
    assert all(all(option["form"] == "opaque" for option in content_options(projection_registry, value))
               for value in slot["data_ids"])
    assert all(deletable_reduction(backward, output["operation_id"], 0, value, []) == (None, []) for value in slot["data_ids"])
    assert not stdout["data_reviews"]  # No exact exception payload or credential inclusion has been established.
    return {"cli": cli, "public": public, "stdout": {"ir": "ir_050", "predecessor_merge_ir": "ir_047",
            "catch_match_ir": "ir_048", "terminal_ir": "ir_051", "operation_id": output["operation_id"],
            "data_ids": slot["data_ids"], "required_demand_derivations": refs, "confirmed_key_exposure": False,
            "delete_supported": False}, "coverage": {ir: solved.coverage[ir] for ir in (
                "ir_004", "ir_025", "ir_036", "ir_037", "ir_047", "ir_048", "ir_050", "ir_051", "ir_052", "ir_056", "ir_057")}}


def main():
    paths = ("selection.json", "graph/initial.json", "task/task.json", "revision/annotation/manifest.json", "revision/annotation/audit/wire-annotation.json",
             "source/inputs/package/SKILL.md", "source/inputs/package/scripts/search.py")
    before = {name: sha256((RUN / name).read_bytes()).hexdigest() for name in paths}
    assert all(before[entry["path"]] == entry["sha256"] for entry in read(RUN / "selection.json").values())
    source = write_source()
    task_path = RUN / "task/task.json"
    task = read(task_path)
    (OUT / "task-extracted-unchanged.json").write_bytes(task_path.read_bytes())
    original_cfg = read(RUN / "graph/initial.json")["cfg"]
    cfg = deepcopy(original_cfg)
    changes = normalize_terminal_owners(cfg)
    save("authored-cfg.json", cfg)
    old = read(RUN / "revision/annotation/audit/wire-annotation.json")
    candidate = author(old)
    save("authored-wire-annotation.json", candidate)
    material = prepare_material(source, cfg, task_baseline=task)
    save("material.json", material)
    try:
        wire, raw, compiled, mapping = compile_flat_response(candidate, material)
    except StructuralValidationError as error:
        save("compile-diagnostics.json", error.diagnostics)
        raise
    save("authored-raw-annotation.json", raw)
    save("compiled-annotation.json", compiled)
    save("compilation-mapping.json", mapping)
    registry, state = seed(wire)
    solved = propagate(cfg, to_payload(compiled), initial_registry=registry, initial_state=state)
    records = solved.records.records_dict()
    save("propagation.json", {"status": solved.status, "coverage": solved.coverage,
        "diagnostics": solved.diagnostics, "records": records, "registry": solved.registry.to_dict()})
    solved.records.validate()
    facts = materials_from_result(solved, material=material, raw_annotation=raw, compiled_annotation=compiled,
                                  mapping=mapping, wire_annotation=wire)
    review = prepare_joint_sensitivity_review(facts, facts.annotation)
    backward, doe = review.demand_dict(), review.to_dict()
    save("backward-demands.json", backward)
    save("doe-comparisons.json", doe)
    save("input-assessments.json", backward["input_assessments"])
    evidence = named_evidence(cfg, solved, backward, doe)
    save("named-ir-evidence.json", evidence)
    assert before == {name: sha256((RUN / name).read_bytes()).hexdigest() for name in paths}
    retained = [ir for ir in old["ir_semantics"] if candidate["ir_semantics"][ir] == old["ir_semantics"][ir]]
    extended = sorted(set(old["ir_semantics"]) - set(retained))
    authored = sorted(set(candidate["ir_semantics"]) - set(old["ir_semantics"]))
    summary = {"kind": "source_grounded_authored_offline_full_graph_witness", "automatic_full_audit": False,
        "online_evidence": False, "model_calls": 0, "http_requests": 0, "skill_executions": 0, "historical_replays": 0,
        "historical_files_sha256": before, "historical_run": str(RUN), "source_sha256": source["source_sha256"],
        "task_sha256": material["task"]["task_sha256"], "original_cfg_sha256": canonical_sha256(original_cfg),
        "authored_cfg_sha256": canonical_sha256(cfg), "terminal_owner_normalization": changes,
        "ir_inventory": sorted(candidate["ir_semantics"]), "blocks": len(cfg["blocks"]),
        "edges": len(cfg["edges"]), "ir": len(candidate["ir_semantics"]),
        "reused_selected_ir_semantics": retained, "extended_selected_ir_semantics": extended,
        "authored_ir_semantics": authored, "statuses": {"forward": solved.status, "backward": backward["status"],
        "doe": doe["status"]}, "coverage": dict(Counter(solved.coverage.values())),
        "input_range_counts": dict(Counter(row["status"] for entry in backward["input_assessments"] for row in entry["ranges"])),
        "modeled_outcome_ir": [ir for ir, record in records.items() if record.get("outcomes")],
        "retained_placeholder": "ir_004", "named_ir_evidence": "named-ir-evidence.json",
        "doe_comparison_counts": dict(Counter(row["conclusion"] for sink in doe["sinks"] for row in sink["data_reviews"])),
        "limits": ["Synthetic invocation and credential values. These are abstract execution alternatives, never observed executions.",
                   "In-scope fixture annotations are independently authored. Historical source review is not applied to modified contracts.",
                   "Broad CLI seeds retain distinct argv and credential candidates. The inherited guard can conservatively retain an absent credential candidate on a modeled request path, and path projection can report missing argv fields across candidates.",
                   "Exception object and string content, response internals, partial output, and local handler interruption remain unresolved."]}
    save("summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("statuses", "coverage", "modeled_outcome_ir", "input_range_counts")}))


if __name__ == "__main__":
    main()
