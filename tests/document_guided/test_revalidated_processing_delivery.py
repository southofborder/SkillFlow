"""Exercise the archived first-response CFG through the normal processing fragment and emitter."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest

from skillflow.common.source_evidence import _digest
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.action_bindings import action_coordinates
from skillflow.document_guided.fragments import assemble_fragments, program_processing_controls, validate_fragment
from skillflow.document_guided.prompts import build_fragment_prompt
from skillflow.propagation.contracts.limitations import validation_gap
from skillflow.propagation.material import prepare_material


ROOT = Path(__file__).resolve().parents[2]
CFG_FILE = ROOT / "output/verification/google-search-outcome-dispatch/recompiled-online-cfg.json"
RUN = ROOT / "experiments/doe/runs/document-guided-google-search-outcome-dispatch-high-20261125-205306"


def arg(i):
    return {"kind": "input", "index": i}


def local(name):
    return {"kind": "local", "name": name}


def bindings(*values):
    return [{"output_index": i, "value": v} for i, v in enumerate(values)]


def segment(*ops):
    return {"mode": "local", "ops": list(ops), "returns": []}


def evidence(ins):
    return {**ins["metadata"]["source_span"], "reason": "The original source contains this operation."}


def render_record(ir):
    stringify = {"op": "compute", "inputs": [arg(0)], "dependencies": ["derived"], "output": "text"}
    fmt = {"op": "compute", "inputs": [arg(1), local("text")], "dependencies": ["derived", "derived"], "output": "message"}
    delivery = {"op": "deliver", "target": "stdout", "inputs": [local("message")]}
    def need(index):
        return {"input_index": index, "required": [{"property": "value", "path": []}],
                "remainder": "independent", "reason": "The source expression uses this operand."}
    for op in (stringify, fmt):
        op["demand_transfer"] = {"rules": [{"output": {"property": "value", "path": []},
            "inputs": [need(i) for i in range(len(op["inputs"]))], "reason": "Conversion depends on its operands.",
            "evidences": [evidence(ir)]}]}
    cases = [{"name": "printed", "phase": "normal", "disposition": "return", "condition": "print completes.",
              "segments": [segment(delivery)]},
             {"name": "failed", "phase": "local_error", "disposition": "throw", "condition": "print raises before delivery.",
              "raise": local("__raised__")}]
    record = {"evidences": [evidence(ir)], "segments": [segment(stringify, fmt), {"kind": "cases",
              "outcome": {"exception_index": 3}, "cases": cases}], "output_bindings": bindings(arg(0), local("text"), local("message"))}
    record["action_bindings"] = {"bind_caught_exception": [["output_bindings", 0]],
        "stringify_exception": [["segments", 0, "ops", 0], ["output_bindings", 1]],
        "format_error": [["segments", 0, "ops", 1], ["output_bindings", 2]],
        "print_error": [list(path) for path, _ in action_coordinates(record) if path[:2] == ("segments", 1)]}
    return record


def prepare_request(ir, blocks):
    incoming = [{"predecessor": blocks[name]["block_id"], "value": arg(i)}
                for i, name in enumerate(["public.supplied_count", "public.default_count"])]
    params = {"op": "build", "output": "params", "container": "object", "parts": [
        {"path": [key], "value": value} for key, value in
        [("q", arg(3)), ("key", arg(4)), ("cx", arg(5)), ("num", local("count"))]]}
    return {"evidences": [evidence(ir)], "segments": [segment({"op": "merge", "incoming": incoming, "output": "count"}, params)],
        "output_bindings": bindings(local("count"), arg(2), local("params")),
        "action_bindings": {"bind_selected_parameter": [["segments", 0, "ops", 0], ["output_bindings", 0]],
                            "bind_url": [["output_bindings", 1]],
                            "build_params": [["segments", 0, "ops", 1], ["output_bindings", 2]]}}


@pytest.fixture(scope="module")
def archived_slice():
    if not CFG_FILE.is_file() or not (RUN / "task/task.json").is_file():
        pytest.skip("Archived 84-IR source regression material is unavailable.")
    cfg = json.loads(CFG_FILE.read_bytes())
    rows = []
    for name in ("SKILL.md", "scripts/search.py"):
        data = (RUN / "source/inputs/package" / name).read_bytes()
        rows.append({"path": name, "content": data.decode(), "sha256": sha256(data).hexdigest()})
    source = {"files": rows, "source_sha256": _digest([{k: r[k] for k in ("path", "sha256")} for r in rows])}
    files = {"skill/" + r["path"]: r["content"] for r in rows}
    material = prepare_material(source, cfg, task_baseline=json.loads((RUN / "task/task.json").read_bytes()))
    blocks = {b["block_name"]: b for b in cfg["blocks"].values()}
    instructions = {ir["id"]: ir for b in blocks.values() for ir in b["instructions"]}
    generated = program_processing_controls(cfg, files)
    points = {"ir_063": render_record(instructions["ir_063"]),
              "ir_067": {"evidences": [evidence(instructions["ir_067"])], "output_bindings": bindings(*map(arg, range(4)))},
              "ir_074": prepare_request(instructions["ir_074"], blocks)}
    # All instructions outside the example are intentionally excluded by the fixture.
    excluded = [validation_gap(ir, [{"code": "outside_example", "path": "/ir_semantics/" + ir,
                                    "message": "Outside this regression slice."}])
                for ir in sorted(instructions.keys() - points.keys() - generated.keys())]
    raw = {"locations": {"stdout": {"kind": "user", "name": "standard output", "evidences": [evidence(instructions["ir_063"])]}},
           "ir_semantics": points, "processing_gaps": [{"instruction_id": "ir_063", "outputs": [1, 2], "control": True,
               "reason": "The availability of intermediate values on earlier conversion failures and partial writes is unresolved.",
               "evidences": [evidence(instructions["ir_063"])]}]}
    return material, files, raw, excluded, generated


def test_actual_processing_prompt_and_fragment_emitter(archived_slice):
    material, files, raw, excluded, generated = archived_slice
    prompt = build_fragment_prompt("processing", files=files, cfg=material["cfg"], documents={
        "flow": (RUN / "steps/flow/document.md").read_text(encoding="utf-8")}, global_requirements="",
        runtime_contract=material["runtime_contract"])
    ids = json.loads(prompt.split("PROGRAM_FILLED_IR_IDS\n", 1)[1].splitlines()[0])
    assert len(ids) == 24 and set(ids) == set(generated)
    fragment = validate_fragment("processing", raw, material, validation_gaps=excluded)
    assert all(fragment["ir_semantics"][ir] == generated[ir] for ir in ids)
    realizations = [{"requirement_id": req["id"], "gaps": [{"reason": "Outside this processing-only example.",
                     "evidences": req["evidences"]}]} for req in material["task"]["requirements"]]
    _, _, compiled, _ = assemble_fragments(fragment, {"realizations": realizations, "demands": []},
        {"declarations": []}, material, validation_gaps=excluded)
    error = compiled["ir_semantics"]["ir_063"]
    binding = error["outcome_bindings"][0]
    assert binding["exception_index"] == 3
    assert {c["disposition"] for c in binding["cases"]} == {"return", "throw"}
    assert [op["op"] for evt in error["events"] for op in evt["atomic_ops"]] == ["compute", "compute", "deliver"]
    assert [row["output_index"] for row in compiled["ir_semantics"]["ir_067"]["output_bindings"]] == [0, 1, 2, 3]
    merge, build = [op for evt in compiled["ir_semantics"]["ir_074"]["events"] for op in evt["atomic_ops"]]
    assert merge["op"] == "merge" and len({r["predecessor"] for r in merge["incoming"]}) == 2
    assert build["op"] == "build" and {tuple(r["path"]) for r in build["parts"]} == {("q",), ("key",), ("cx",), ("num",)}


def test_missing_authored_record_only_targets_that_owner(archived_slice):
    material, _, raw, excluded, _ = archived_slice
    missing = deepcopy(raw)
    del missing["ir_semantics"]["ir_074"]
    with pytest.raises(StructuralValidationError) as rejected:
        validate_fragment("processing", missing, material, validation_gaps=excluded)
    slots = [d["context"]["coverage_slot"] for d in rejected.value.diagnostics if d["code"] == "instruction_coverage"]
    assert [s["instruction_id"] for s in slots] == ["ir_074"]
