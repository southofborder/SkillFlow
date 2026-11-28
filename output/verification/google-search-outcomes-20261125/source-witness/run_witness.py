"""Source-grounded, authored OFFLINE integration witness; never execute the Skill."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-google-search-outcomes-high-20261125-190529"
sys.path.insert(0, str(ROOT / "src"))

from skillflow.common.source_evidence import _digest
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.task import checked_task, task_source_files
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.solver import propagate
from skillflow.doe.input_assessments import deletable_reduction
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.doe.sensitivity_results import resolve_data_review


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ev(first, last=None, reason="Authored offline correspondence to the unmodified real Skill source."):
    return {"file": "skill/scripts/search.py", "start_line": first, "end_line": last or first,
            "reason": reason}


def inp(index=0): return {"kind": "input", "index": index}
def local(name): return {"kind": "local", "name": name}
def lit(value): return {"kind": "literal", "value": value}
def result(name): return {"type": "result", "identifier": name}


def instruction(name, opcode, inputs=(), outputs=(), lines=(14, 14)):
    return {"id": name, "opcode": opcode, "inputs": list(inputs),
            "outputs": [result(name) for name in outputs], "constraints": [],
            "metadata": {"source_span": {"file": "skill/scripts/search.py",
                "start_line": lines[0], "end_line": lines[1]}}}


def segment(ops): return {"mode": "local", "returns": [], "ops": ops}


def semantics(lines, ops=(), output=None):
    return {"evidences": [ev(*lines)], "segments": [segment(list(ops))] if ops else [],
            "output_bindings": [] if output is None else [{"output_index": 0, "value": local(output)}]}


def goal(requirement, target, preserve="value", path=(), reason="Preserve the actual source-required information at this boundary."):
    return {"requirement_id": requirement, "target": target, "preserve": preserve,
            "path": list(path), "reason": reason}


def main():
    # Copy bytes only; do not import/search.py or inspect any actual environment credential.
    files = []
    for relative in ("SKILL.md", "scripts/search.py"):
        original = RUN / "source/inputs/package" / relative
        target = OUT / "source-package" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        content = original.read_bytes()
        assert target.read_bytes() == content
        files.append({"path": relative, "content": content.decode("utf-8"),
                      "sha256": hashlib.sha256(content).hexdigest()})
    source = {"files": files, "source_sha256": _digest([
        {key: row[key] for key in ("path", "sha256")} for row in files])}
    extracted_task = json.loads((RUN / "task/task.json").read_text(encoding="utf-8"))
    task = checked_task(extracted_task, source_files=task_source_files(source), source_sha256=source["source_sha256"])
    requirements = {r.id: r for r in task.requirements}
    assert "q, key, cx, and num" in requirements["R10"].text
    assert "exception's string representation" in requirements["R13"].text
    save("task-extracted-unchanged.json", extracted_task)
    save("source-bundle.json", source)

    entry = []
    for name, token, line in (("query", "sys.argv[1]", 23), ("key", "GOOGLE_API_KEY", 27), ("cx", "GOOGLE_CSE_ID", 28)):
        entry.append(instruction("ir_" + name, "acquire", [{"type": "external_resource", "identifier": token}],
                                 [name], (line, line)))
    entry += [
        instruction("ir_params", "build_request_params", [result(n) for n in ("query", "key", "cx")], ["params"], (8, 13)),
        instruction("ir_get", "requests.get", [result("params"), {"type": "literal", "literal_value": "https://www.googleapis.com/customsearch/v1"}], ["response"], (14, 14)),
        instruction("ir_status", "response.raise_for_status", [result("response")], ["status_error", "status_completed"], (15, 15)),
        instruction("ir_route", "dispatch", [result("status_completed")], lines=(15, 15)),
    ]
    cfg = {"entry_block_id": "request", "blocks": {
        "request": {"block_id": "request", "block_name": "Successful GET followed by status check", "instructions": entry},
        "normal": {"block_id": "normal", "block_name": "Normal continuation outside this slice", "instructions": [
            instruction("ir_normal_end", "return", lines=(16, 16))]},
        "error": {"block_id": "error", "block_name": "Caught status exception and required CLI diagnostic", "instructions": [
            instruction("ir_format", "format_Error_str_exception", [result("status_error")], ["diagnostic"], (37, 38)),
            instruction("ir_stdout", "print", [result("diagnostic")], lines=(38, 38)),
            instruction("ir_exit", "return", [{"type": "literal", "literal_value": 1}], lines=(39, 39)),
        ]},
    }, "edges": [{"source_block_id": "request", "target_block_id": target,
                  "condition_text": condition} for target, condition in (
                      ("normal", "raise_for_status returned normally"),
                      ("error", "raise_for_status raised; handled by except Exception as e"))],
        "constraints": [], "declared_context_keys": []}
    material = prepare_material(source, cfg, task_baseline=task)

    locations = {
        "query": {"kind": "runtime_context", "name": "sys.argv[1]", "evidences": [ev(23)]},
        "key": {"kind": "runtime_context", "name": "GOOGLE_API_KEY", "evidences": [ev(27)]},
        "cx": {"kind": "runtime_context", "name": "GOOGLE_CSE_ID", "evidences": [ev(28)]},
        "google": {"kind": "remote", "name": "https://www.googleapis.com/customsearch/v1", "evidences": [ev(7), ev(14)]},
        "stdout": {"kind": "user", "name": "CLI stdout", "evidences": [ev(38)]},
    }
    specs = {"ir_" + n: semantics((line, line), [{"op": "read", "location": n, "output": n}], n)
             for n, line in (("query", 23), ("key", 27), ("cx", 28))}
    specs["ir_key"]["sensitivity"] = [{"value": local("key"), "path": [], "property": "value",
        "label": "API authentication credential", "evidences": [ev(26, 27)]}]
    specs["ir_params"] = semantics((8, 13), [{"op": "build", "container": "object", "output": "params",
        "parts": [{"path": [field], "value": inp(index)} for index, field in enumerate(("q", "key", "cx"))]
                 + [{"path": ["num"], "value": lit(5)}]}], "params")
    contract = {"inputs": [{"input_index": 0, "required": [{"property": "value", "path": [field]}
                for field in ("q", "key", "cx", "num")], "remainder": "independent",
                "reason": "This source explicitly binds the four named request parameters."}],
        "reason": "Authored source-grounded request interface witness, not an independent external API validation.",
        "evidences": [ev(6, 14)]}
    call = {"op": "call", "location": "google", "inputs": [inp()], "output": "response",
        "input_contract": contract,
        "demands": [goal("R10", {"kind": "self"}, "action")]
            + [goal("R10", {"kind": "input", "index": 0}, path=[field]) for field in ("q", "key", "cx", "num")]}
    specs["ir_get"] = semantics((14, 14), [call], "response")
    specs["ir_status"] = {"evidences": [ev(15)], "segments": [{"kind": "cases", "outcome": {
        "exception_index": 0, "completion_index": 1}, "cases": [
        {"name": "normal", "phase": "normal", "disposition": "return", "condition": "The source status check returns normally.", "segments": []},
        {"name": "http_error", "phase": "local_error", "disposition": "throw", "condition": "The source status check raises an exception, caught by lines 37-39.",
         "segments": [], "raise": local("__raised__")},
    ]}]}
    specs["ir_route"] = semantics((15, 15), [{"op": "branch", "input": inp(), "predicate": "selector",
        "selector": {"path": [], "tests": [{"kind": "equals", "value": True}], "outcome": 0},
        "true_target": "normal", "false_target": "error"}])
    # str(e) and the f-string are opaque derived computations; no unsupported exact string evaluator.
    transfer = {"rules": [{"output": {"property": "value", "path": []},
        "inputs": [{"input_index": 0, "required": [{"property": "value", "path": []}],
                    "remainder": "independent", "reason": "str(e) supplies the diagnostic content."}],
        "reason": "The real f-string is Error: followed by str(e).", "evidences": [ev(38)]}]}
    specs["ir_format"] = semantics((38, 38), [{"op": "compute", "inputs": [inp()],
        "dependencies": ["derived"], "output": "diagnostic", "demand_transfer": transfer}], "diagnostic")
    specs["ir_stdout"] = semantics((38, 38), [{"op": "deliver", "target": "stdout", "inputs": [inp()],
        "demands": [goal("R13", {"kind": "self"}, "action"),
                    goal("R13", {"kind": "input", "index": 0}, reason="R13 explicitly requires the complete Error: plus exception string diagnostic.")]}])
    specs["ir_normal_end"] = semantics((16, 16))
    specs["ir_exit"] = semantics((39, 39))

    realizations = []
    for requirement in task.requirements:
        realizations.append({"requirement_id": requirement.id,
            "bindings": [], "gaps": [] if requirement.id == "R10" else [{
                "reason": "Authored witness covers only successful GET, status outcome and caught diagnostic. Other source behavior is deliberately outside this slice.",
                "evidences": [r.model_dump(mode="json") for r in requirement.evidences]}]})
    wire = {"outcome": "completed", "ir_semantics": specs, "locations": locations,
        "realizations": realizations, "demands": [
            goal("R11", {"instruction_id": "ir_status", "path": []}, "action"),
            goal("R13", {"instruction_id": "ir_exit", "side": "input", "index": 0}),
        ]}
    save("authored-cfg.json", cfg)
    save("authored-wire-annotation.json", wire)
    saved_wire, raw, compiled, mapping = compile_flat_response(wire, material)
    save("authored-raw-annotation.json", raw)
    save("compiled-annotation.json", compiled)
    save("compilation-mapping.json", mapping)

    registry = DataRegistry("google-search-source-grounded-offline-witness")
    state = {}
    for name, value in (("query", "OpenClaw documentation"), ("key", "DEMO_API_KEY_NOT_A_SECRET"), ("cx", "DEMO_CSE_ID")):
        item = registry.register_source(name, acquired_from=locations[name]["name"], at="Artificial public witness input",
                                       content=LiteralContent(value=value))
        state[FlowLocation(kind="runtime_context", name=locations[name]["name"])] = frozenset([item.id])
    solved = propagate(cfg, to_payload(compiled), initial_registry=registry, initial_state=FlowState.from_mapping(state))
    save("propagation.json", {"status": solved.status, "coverage": solved.coverage, "diagnostics": solved.diagnostics,
        "records": solved.records.records_dict(), "registry": solved.registry.to_dict()})
    assert solved.status == "complete", solved.diagnostics
    solved.records.validate()
    facts = materials_from_result(solved, material=material, raw_annotation=raw, compiled_annotation=compiled,
                                  mapping=mapping, wire_annotation=saved_wire)
    review = prepare_joint_sensitivity_review(facts, facts.annotation)
    backward, doe = review.demand_dict(), review.to_dict()
    save("backward-demands.json", backward)
    save("doe-comparisons.json", doe)
    save("input-assessments.json", backward["input_assessments"])

    records = solved.records.records_dict()
    params = next(iter(solved.records.get("ir_params").exit_state.get(FlowLocation(kind="result", name="params"))))
    fields = {field: [v.model_dump(mode="json") for v in solved.registry.resolve_part_candidates(params, [field])]
              for field in ("q", "key", "cx", "num")}
    assert fields["key"][0]["content"] == {"form": "literal", "value": "DEMO_API_KEY_NOT_A_SECRET"}
    assert fields["key"][0]["origin"]["acquired_from"] == "GOOGLE_API_KEY"
    assert records["ir_status"]["outcomes"] and len(records["ir_status"]["outcomes"]) == 2
    assert solved.coverage["ir_stdout"] == solved.coverage["ir_exit"] == "processed"
    normal_entry = records["ir_normal_end"]["entry_state"]["bindings"]
    assert not any(r["location"]["name"] == "status_error" for r in normal_entry)
    exceptions = next(r["data_ids"] for r in records["ir_format"]["entry_state"]["bindings"]
                      if r["location"]["name"] == "status_error")
    assert all(solved.registry.get(identity).content.form == "opaque" for identity in exceptions)
    stdout_assessment = next(row for row in backward["input_assessments"]
        if row["instruction_id"] == "ir_stdout" and row["node_kind"] == "op_input" and row["input_index"] == 0)
    assert any(r["status"] == "required" and r["path"] == [] for r in stdout_assessment["ranges"])
    assert all(r["status"] != "deletable" for r in stdout_assessment["ranges"])
    for data_id in stdout_assessment["data_ids"]:
        assert solved.registry.get(data_id).content.form == "opaque"
        assert deletable_reduction(backward, stdout_assessment["operation_id"], 0, data_id, []) == (None, [])
    reviews = [{"sink_type": sink["boundary"]["sink_type"], "instruction_id": sink["boundary"]["instruction_id"],
                "review": resolve_data_review(row, sink, doe["derivations"]["sensitivity"])}
               for sink in doe["sinks"] for row in sink["data_reviews"]]
    assert not any(row["instruction_id"] == "ir_stdout" for row in reviews)
    assert any(row["instruction_id"] == "ir_get" and row["review"]["path"] == ["key"]
               and row["review"]["relation"] == "direct" for row in reviews)
    assert any(row["requirement_id"] == "R10" and not row["conservative"]
               and row["node"]["instruction_id"] == "ir_get" and row["node"]["kind"] == "op_input"
               and row["path"] == ["key"] and "task_value" in row["rules"]
               for row in backward["derivations"].values())
    range_counts = Counter(row["status"] for item in backward["input_assessments"] for row in item["ranges"])
    assert range_counts["deletable"] == 0
    summary = {"kind": "source_grounded_authored_offline_integration_witness", "automatic_full_audit": False,
        "model_calls": 0, "http_requests": 0, "skill_executions": 0, "historical_replays": 0,
        "source_sha256": source["source_sha256"], "task_sha256": task.task_sha256,
        "task_origin": str(RUN / "task/task.json"), "selected_requirements": {
            key: requirements[key].model_dump(mode="json") for key in ("R10", "R11", "R13")},
        "scope_assumptions": ["CLI/environment validation has succeeded; count omitted, so num=5.",
            "requests.get returns normally; the source status check may return or throw.",
            "Normal status continuation terminates the slice before JSON parsing/success output.",
            "GET transport failures, JSON errors and setup/validation are outside this slice."],
        "authored_inputs": ["compact CFG", "processing/outcome annotations", "Task correspondence/goals", "sensitivity declaration", "interface/format transfer declarations"],
        "forward": {"status": solved.status, "coverage": solved.coverage, "outcome_cases": records["ir_status"]["outcomes"],
                    "exception_ids": exceptions, "request_fields": fields},
        "backward": {"status": backward["status"], "stdout_input_assessment": stdout_assessment,
                     "input_assessments": len(backward["input_assessments"]), "range_counts": dict(range_counts),
                     "rule_counts": dict(Counter(rule for row in backward["derivations"].values() for rule in row["rules"]))},
        "doe": {"status": doe["status"], "resolved_api_key_reviews": reviews,
                "stdout_key_disclosure_established": False, "stdout_whole_input_deletion": None},
        "limitations": ["Source/evidence validation does not independently establish semantic truth of authored annotations.",
            "No source-review receipt is provided; opaque exception construction and transfer decisions retain uncertainty.",
            "No API key field is fabricated in an opaque exception/diagnostic. Absence of a tracked stdout key range is not proof that real Requests diagnostics never contain a key.",
            "Full Task is preserved, with out-of-slice requirements retained and explicit gaps; DOE is expected to remain partial."],
        "checks": {"unmodified_two_file_source": True, "real_extracted_task_unchanged": True,
            "request_key_is_actual_env_source_identity": True, "normal_and_throw_rows_separate": True,
            "stdout_reachable": True, "opaque_exception_not_fabricated_key_payload": True,
            "R13_stdout_input_required": True, "no_stdout_input_deletion": True}}
    save("summary.json", summary)
    save("source-integrity.json", {"original_source_manifest": str(RUN / "source/manifest.json"),
        "source_sha256": source["source_sha256"], "task_sha256": task.task_sha256,
        "files": [{"path": row["path"], "sha256": row["sha256"], "copied_bytes_identical": True} for row in files],
        "task_original_bytes_sha256": hashlib.sha256((RUN / "task/task.json").read_bytes()).hexdigest(),
        "note": "Original files are read-only inputs. Task semantics and sealed digest are retained unchanged; witness CFG/annotation are separately authored."})
    print(json.dumps({"forward": solved.status, "backward": backward["status"], "doe": doe["status"],
        "IRs": len(solved.coverage), "status_outcomes": len(records["ir_status"]["outcomes"]),
        "stdout_ranges": stdout_assessment["ranges"], "output": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
