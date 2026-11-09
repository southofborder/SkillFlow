"""Small real-source projections prove ordinary GA4 branches are expressible.

These are compiler/propagation regressions, not full-source semantic references.
The TypeScript snapshots are never imported or executed.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from skillflow.common.source_evidence import _digest
from skillflow.document_guided.cfg_wire import normalize_cfg_wire
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.references import cfg_target_from_path
from skillflow.propagation.contracts.task import task_source_files, validate_task_candidate
from skillflow.propagation.material import prepare_material
from skillflow.propagation.models import FlowLocation
from skillflow.propagation.solver import propagate


def inp(index=0):
    return {"kind": "input", "index": index}


def local(name):
    return {"kind": "local", "name": name}


def literal(value):
    return {"type": "literal", "literal_value": value}


def result(name):
    return {"type": "result", "identifier": name}


def ir(opcode, inputs=(), output=None):
    return {"opcode": opcode, "inputs": list(inputs), "outputs": [] if output is None else [result(output)]}


def source_material(graph, relative, first, last):
    root = Path(__file__).parents[1] / "fixtures" / "ga4_boundary_cases"
    manifest = json.loads((root / "provenance.json").read_text(encoding="utf-8-sig"))
    row = next(row for row in manifest["files"] if row["path"] == relative)
    content = (root / relative).read_bytes()
    assert hashlib.sha256(content).hexdigest() == row["sha256"]
    files = [{"path": "scripts/src/" + relative, "content": content.decode("utf-8"), "sha256": row["sha256"]}]
    source = {"files": files, "source_sha256": _digest([{"path": f["path"], "sha256": f["sha256"]} for f in files])}
    citation = {"file": "skill/scripts/src/" + relative, "start_line": first, "end_line": last,
        "reason": "The cited GA4 source supplies this branch and its actual operands."}
    task = validate_task_candidate({"purpose": {"text": "Preserve the declared function behavior.", "evidences": [citation]},
        "requirements": [{"id": "R1", "text": "Preserve the actual result and source-supported conditions.", "evidences": [citation]}], "issues": []},
        source_files=task_source_files(source), source_sha256=source["source_sha256"])
    return prepare_material(source, graph, task_baseline=task), citation


def compile_graph(blocks, edges):
    candidate = normalize_cfg_wire({"entry_block_ref": blocks[0]["block_ref"], "blocks": blocks, "edges": edges})
    compiled = compile_candidate(candidate)
    assert compiled.ok, compiled.diagnostics
    return json.loads(compiled.cfg.to_json())


def binding(value):
    return [{"output_index": 0, "value": value}]


def spec(citation, ops=(), output=None):
    return {"evidences": [citation], "segments": [] if not ops else [{"mode": "local", "returns": [], "ops": list(ops)}],
        "output_bindings": [] if output is None else binding(local(output))}


def base_wire(graph, citation):
    instructions = [row for block in graph["blocks"].values() for row in block["instructions"]]
    return {"outcome": "completed", "realizations": [{"requirement_id": "R1"}], "locations": {},
        "ir_semantics": {row["id"]: spec(citation) for row in instructions},
        "demands": [{"requirement_id": "R1", "target": {"instruction_id": instructions[-1]["id"], "side": "input", "index": 0},
            "preserve": "value", "reason": "Preserve the function result in this boundary projection."}]}


def test_ga4_imported_interface_and_initialized_handle_have_distinct_versions():
    graph = compile_graph([
        {"block_ref": "import", "data_source_kind": "external", "instructions": [
            ir("import_module", [{"type": "external_resource", "identifier": "@googleapis/indexing"}], "module"), ir("dispatch")]},
        {"block_ref": "initialize", "instructions": [
            ir("initialize_client", [result("module"), literal({"client_email": "fixture@example.test", "private_key": "fixture-key"})], "handle"),
            ir("return", [result("handle")])]}],
        [{"source_block_ref": "import", "target_block_ref": "initialize"}])
    material, citation = source_material(graph, "core/client.ts", 8, 122)
    wire = base_wire(graph, citation)
    ids = {row["opcode"]: row["id"] for block in graph["blocks"].values() for row in block["instructions"]}
    wire["locations"]["module"] = {"kind": "tool", "name": "@googleapis/indexing", "evidences": [citation]}
    wire["ir_semantics"][ids["import_module"]] = spec(citation, [{"op": "receive", "location": "module", "inputs": [], "output": "interface"}], "interface")
    wire["ir_semantics"][ids["initialize_client"]] = spec(citation, [{"op": "compute", "inputs": [inp(0), inp(1)],
        "dependencies": ["possible", "possible"], "output": "client"}], "client")
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(graph, to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    imported = next(iter(solved.records.get(ids["import_module"]).events[0].atomic_ops[0].outputs[0]))
    constructed = next(iter(solved.records.get(ids["initialize_client"]).events[0].atomic_ops[0].outputs[0]))
    assert imported != constructed
    assert solved.registry.get(imported).origin.acquired_from != solved.registry.get(constructed).origin.acquired_from
    assert imported in solved.registry.get(constructed).origin.inputs


CASES = {
    "help": ("index.ts", 365, 405, ["/app/index.js", "/app/index.js"],
        {"op": "eq", "left": {"op": "ref", "value": inp(0)}, "right": {"op": "ref", "value": inp(1)}}, "process.argv[1] equals module pathname"),
    "default_date": ("api/reports.ts", 47, 51, [""],
        {"op": "eq", "left": {"op": "ref", "value": inp()}, "right": {"op": "literal", "value": ""}}, "the supplied range string is empty"),
    "optional_save": ("api/indexing.ts", 56, 80, [True], {"op": "ref", "value": inp()}, "save is true"),
    "empty_urls": ("api/bulk-lookup.ts", 153, 171, [[]],
        {"op": "eq", "left": {"op": "count", "arg": {"op": "ref", "value": inp()}}, "right": {"op": "literal", "value": 0}}, "normalizedUrls.length is zero"),
    "file_exists": ("core/storage.ts", 103, 114, ["/results/fixture.json"], None, "existsSync(filepath) is false"),
}


@pytest.mark.parametrize("kind", CASES)
def test_ga4_condition_operands_and_distinct_branch_actions_compile(kind):
    relative, first, last, arguments, expression, condition = CASES[kind]
    branches = ["selected", "other"]
    active = "other" if kind in {"empty_urls", "file_exists"} else "selected"
    action_input = {"url": "https://fixture.invalid/page", "notifyTime": "fixture-time"} if kind == "optional_save" else arguments[0]
    if kind == "help":
        text = (Path(__file__).parents[1] / "fixtures" / "ga4_boundary_cases" / "index.ts").read_text(encoding="utf-8")
        action_input = text.split("if (process.argv[1] === new URL(import.meta.url).pathname) {", 1)[1].split("console.log(`", 1)[1].split("`);", 1)[0]
    branch_blocks = []
    for name in branches:
        if name == active:
            side_effect_only = kind in {"help", "optional_save"}
            instructions = [ir("branch_action_" + name, [literal(action_input)], None if side_effect_only else "branch_value_" + name),
                            ir("return", [literal(None) if side_effect_only else result("branch_value_" + name)])]
        else:
            returned = {"rows": [], "rowCount": 0} if kind == "empty_urls" else arguments[0] if kind == "default_date" else None
            instructions = [ir("return", [literal(returned)])]
        branch_blocks.append({"block_ref": name, "instructions": instructions})
    graph = compile_graph([
        {"block_ref": "guard", "instructions": [ir("condition", list(map(literal, arguments)), "decision"), ir("dispatch", [result("decision")])]},
        *branch_blocks],
        [{"source_block_ref": "guard", "target_block_ref": name, "condition_text": condition if name == "selected" else "not (" + condition + ")"} for name in branches])
    material, citation = source_material(graph, relative, first, last)
    wire = base_wire(graph, citation)
    instructions = [row for block in graph["blocks"].values() for row in block["instructions"]]
    ids = {row["opcode"]: row["id"] for row in instructions}
    wire["locations"] = {"settings": {"kind": "tool", "name": "getSettings", "evidences": [citation]},
        "result": {"kind": "storage", "name": "/results/fixture.json", "evidences": [citation]},
        "console": {"kind": "tool", "name": "console.log", "evidences": [citation]},
        "exists": {"kind": "tool", "name": "existsSync", "evidences": [citation]},
        "report": {"kind": "remote", "name": "GA4 runReport", "evidences": [citation]}}
    condition_ops = ([{"op": "call", "location": "exists", "inputs": [inp()], "output": "exists"},
        {"op": "compute", "inputs": [local("exists")], "dependencies": ["derived"], "output": "decision",
         "expression": {"expression": {"op": "not", "arg": {"op": "ref", "value": local("exists")}}, "evidences": [citation]}}]
        if expression is None else [{"op": "compute", "inputs": [inp(i) for i in range(len(arguments))],
            "dependencies": ["derived"] * len(arguments), "output": "decision",
            "expression": {"expression": expression, "evidences": [citation]}}])
    wire["ir_semantics"][ids["condition"]] = spec(citation, condition_ops, "decision")
    selected, other = [], []
    if kind == "help":
        selected = [{"op": "deliver", "target": "console", "inputs": [inp()]}]
    elif kind == "default_date":
        selected = [{"op": "call", "location": "settings", "inputs": [], "output": "settings"},
                    {"op": "select_part", "input": local("settings"), "path": ["defaultDateRange"], "output": "value"}]
    elif kind == "optional_save":
        selected = [{"op": "write", "target": "result", "mode": "replace", "input": inp()}]
    elif kind == "empty_urls":
        other = [{"op": "call", "location": "report", "inputs": [inp()], "output": "value"}]
    elif kind == "file_exists":
        other = [{"op": "read", "location": "result", "output": "value"}]
    for name, ops in (("selected", selected), ("other", other)):
        if "branch_action_" + name in ids:
            wire["ir_semantics"][ids["branch_action_" + name]] = spec(citation, ops, None if kind in {"help", "optional_save"} else "value")
    wire["expressions"] = [{"target": cfg_target_from_path(graph, ["edges", i, "condition_text"]),
        "expression": {"op": "ref", "value": inp()} if i == 0 else {"op": "not", "arg": {"op": "ref", "value": inp()}},
        "evidences": [citation]} for i in range(2)]
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(graph, to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    dispatch = next(row for row in instructions if row["opcode"] == "dispatch")
    assert len(dispatch["inputs"]) == 1 and dispatch["inputs"][0]["type"] == "result"
    assert len(next(row for row in instructions if row["opcode"] == "condition")["inputs"]) == len(arguments)
    assert len(compiled["expressions"]) == 3  # two edge predicates and the actual condition computation
    actions = {name: [op.op for event in solved.records.get(ids["branch_action_" + name]).events for op in event.atomic_ops]
               if "branch_action_" + name in ids else [] for name in branches}
    if kind == "help":
        assert "deliver" in actions["selected"] and "deliver" not in actions["other"]
    elif kind == "default_date":
        assert actions["selected"] == ["deliver", "receive", "select_part"] and "receive" not in actions["other"]
    elif kind == "optional_save":
        assert "write" in actions["selected"] and "write" not in actions["other"]
    elif kind == "empty_urls":
        assert "receive" not in actions["selected"] and "receive" in actions["other"]
    else:
        assert "read" not in actions["selected"] and "read" in actions["other"]
