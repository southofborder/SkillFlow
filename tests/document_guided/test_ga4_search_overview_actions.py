"""Bind a real Search Console overview path to executable operations without running the Skill."""
from pathlib import Path
from shutil import copytree, ignore_patterns

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.inputs.snapshot import freeze_input, read_snapshot
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.binding_examples import instruction, literal, result
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.solver import propagate
from tests.propagation.annotation.helpers import prepared_material


def test_overview_log_query_response_default_save_and_report(tmp_path):
    package = (Path(__file__).resolve().parents[2] / "experiments/doe/inputs/clawhub-top1000-v1/items"
               / "0481-adamkristopher-ga4-analytics/attempts/20261020T094423659277Z-624ebf/files")
    # The ingestion metadata and catalogue card sit beside the 16 published Skill files.
    copytree(package, tmp_path / "package", ignore=ignore_patterns("_meta.json", "skill-card.md"))
    freeze_input(tmp_path / "package", tmp_path / "frozen", ArtifactWriter(()))
    _, source, _ = read_snapshot(tmp_path / "frozen")
    assert len(source["files"]) == 16
    assert source["source_sha256"] == "3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd"
    index_file = "skill/scripts/src/index.ts"
    api_file = "skill/scripts/src/api/searchConsole.ts"
    sources = {"skill/" + row["path"]: row["content"].splitlines() for row in source["files"]}

    def site(file, first, last, token):
        assert token in "\n".join(sources[file][first - 1:last])
        return {"file": file, "start_line": first, "end_line": last}

    def evidence(span, reason):
        return {**span, "reason": reason}

    log = site(index_file, 239, 239, "console.log")
    call = site(api_file, 102, 111, "client.searchanalytics.query")
    project = site(api_file, 113, 113, "response.data")
    save = site(api_file, 115, 118, "saveResult(result")
    overview = site(index_file, 240, 249, "results.topQueries")
    publish = site(index_file, 251, 252, "saveResult(results")
    default = site(api_file, 90, 96, "save = true")
    fields = ["topQueries", "topPages", "devicePerformance", "countryPerformance"]
    query_input = {"siteUrl": "example.test", "requestBody": {"dimensions": ["query"]}}
    # A concrete call with omitted save takes the sourced default-save path.
    # Independent response values for the three sibling queries are supplied by the fixture.
    irs = [instruction("ir_query", "get_top_queries", [literal(query_input)], "rows"),
           instruction("ir_report", "assemble_overview", [result("rows"), *map(literal, ([], [], []))], "report"),
           instruction("ir_save", "save_overview", [result("report")]), instruction("ir_exit", "return", [result("report")])]
    actions = [("logging", "other", log), ("query", "call", call),
               ("rows", "value", project), ("default_save", "write", save)]
    irs[0]["metadata"]["source_actions"] = [
        {"ref": ref, "kind": ref, "role": role, "source": span} for ref, role, span in actions]
    cfg = {"entry_block_id": "entry", "edges": [], "declared_context_keys": [], "constraints": [],
           "blocks": {"entry": {"block_id": "entry", "block_name": "Overview", "constraints": [],
                                "instructions": irs, "data_source_kind": None}}}
    material = prepared_material(source, cfg)
    ev = evidence(call, "The client accepts the request and returns the query response.")
    inp = lambda i: {"kind": "input", "index": i}
    local = lambda name: {"kind": "local", "name": name}
    ops = [
        {"op": "placeholder", "kind": "effect", "inputs": [],
         "reason": "The logging implementation and its output destination are outside the selected source.",
         "evidences": [evidence(log, "The source calls the logger before the query.")]},
        {"op": "call", "location": "analytics", "inputs": [inp(0)], "output": "response",
         "evidences": [ev], "input_contract": {"inputs": [{"input_index": 0,
             "required": [{"property": "value", "path": ["siteUrl"]}, {"property": "value", "path": ["requestBody"]}],
             "remainder": "independent", "reason": "The call supplies siteUrl and requestBody."}],
             "reason": "The source enumerates both request members.", "evidences": [ev]}},
        {"op": "select_part", "input": local("response"), "path": ["data"], "output": "rows",
         "evidences": [evidence(project, "The returned result is response.data.")]},
        {"op": "write", "target": "query_file", "input": local("rows"),
         "evidences": [evidence(default, "Save defaults to true."), evidence(save, "Save receives the projected result.")]}]
    bind = {ref: [["segments", 0, "ops", i]] for i, (ref, _, _) in enumerate(actions)}
    bind["rows"].append(["output_bindings", 0])
    def spec(span, operations, output=None):
        row = {"evidences": [evidence(span, "The selected source contains this operation.")],
               "segments": [{"mode": "local", "ops": operations, "returns": []}]}
        if output:
            row["output_bindings"] = [{"output_index": 0, "value": local(output)}]
        return row
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R001"}],
            "locations": {key: {"kind": kind, "name": key, "evidences": [evidence(span, "Source boundary.")]}
                          for key, kind, span in (("analytics", "remote", call), ("query_file", "storage", save),
                                                  ("overview_file", "storage", publish))},
            "ir_semantics": {"ir_query": {**spec(call, ops, "rows"), "action_bindings": bind},
                "ir_report": spec(overview, [{"op": "build", "container": "object", "output": "report",
                    "parts": [{"path": [field], "value": inp(i)} for i, field in enumerate(fields)]}], "report"),
                "ir_save": spec(publish, [{"op": "write", "target": "overview_file", "input": inp(0),
                    "demands": [{"requirement_id": "R001", "target": {"kind": "self"},
                                 "preserve": "action", "reason": "Save the assembled Search Console overview."}]}]),
                "ir_exit": {"evidences": [evidence(overview, "The overview returns the assembled result.")]}}}
    _, _, compiled, mapping = compile_flat_response(wire, material)
    assert mapping["source_action_bindings"]["ir_query"]["bindings"] == bind
    facts = propagate(cfg, to_payload(compiled))
    assert facts.coverage == {"ir_query": "processed_with_placeholder", "ir_report": "processed",
                              "ir_save": "processed", "ir_exit": "processed"}
    lifo = propagate(cfg, to_payload(compiled), schedule="lifo")
    assert (facts.records.records_dict(), facts.registry.to_dict(), facts.coverage) == (
        lifo.records.records_dict(), lifo.registry.to_dict(), lifo.coverage)
    records = facts.records.get("ir_query")
    observed = [op for event in records.events for op in event.atomic_ops]
    assert [op.op for op in observed] == ["placeholder", "deliver", "receive", "select_part", "write"]
    assert observed[-1].inputs[0] == observed[-2].outputs[0]
    assert observed[-3].outputs[0] == observed[-2].inputs[0]
    built = facts.records.get("ir_report").events[0].atomic_ops[0]
    assert built.members[0].path == ["topQueries"] and built.inputs[0] == observed[-2].outputs[0]
    saved = facts.records.get("ir_save").events[0].atomic_ops[0]
    assert saved.inputs[0] == built.outputs[0]
