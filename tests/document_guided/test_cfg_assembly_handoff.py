"""A fresh checkout can reproduce the graph-to-processing repair without GA4 archives."""
import json
from pathlib import Path
import runpy

from skillflow.common.artifact_io import file_sha256
from .cfg_assembly_acceptance import run_to_processing, split_ingress


def audit_graph(run):
    helper = Path(__file__).resolve().parents[2] / "output/verification/online-ga4-cfg-assembly-20261123/assess.py"
    return runpy.run_path(str(helper))["stage_audit"](run, "graph")


def test_compiled_graph_reaches_processing_after_one_scoped_correction(tmp_path):
    package = tmp_path / "package"
    package.mkdir()
    text = ("Read the account argument and keep its original value.\n"
            "Pass the chosen account to the operation.\n"
            "Read the user's message, pair it with the chosen account and deliver it there.\n")
    (package / "SKILL.md").write_text(text, encoding="utf-8")

    def span(line):
        return {"file": "skill/SKILL.md", "start_line": line, "end_line": line}

    def jump(target, line):
        return {"kind": "jump", "target": target, "source": span(line)}

    facts = {"entry": "route", "blocks": [
        {"ref": "route", "source_kind": "context", "operations": [], "exit": jump("account", 1)},
        {"ref": "account", "source_kind": "context", "operations": [
            {"ref": "get", "opcode": "receive", "inputs": [{"context_key": "account"}],
             "outputs": ["account"], "source": span(1)},
            {"ref": "choose", "opcode": "value", "inputs": [{"result": "account"}],
             "outputs": ["selected"], "source": span(2)}], "exit": jump("send", 2)},
        {"ref": "send", "source_kind": "context", "operations": [
            {"ref": "message", "opcode": "receive", "inputs": [{"result": "selected"}, {"context_key": "message"}],
             "outputs": ["recipient", "payload"], "source": span(3)},
            {"ref": "emit", "opcode": "deliver", "inputs": [{"result": "recipient"}, {"result": "payload"}],
             "outputs": [], "source": span(3)}],
         "exit": {"kind": "return", "values": [], "source": span(3)}}]}
    evidence = {**span(3), "reason": "The source specifies the delivery of the user's message."}
    task = {"purpose": {"text": "Deliver the message to the selected account.", "evidences": [evidence]},
            "requirements": [{"id": "R1", "text": "Deliver the message.", "evidences": [evidence]}], "issues": []}
    receipt = run_to_processing(package, tmp_path / "run", facts=facts, task=task, flow=text,
                                repair_blocks={"send": split_ingress})
    assert receipt["program_layout"] == {"route": {"kind": "control"},
                                        "account": {"kind": "split", "continuation": "account.body"}}
    assert receipt["repaired_context_reads"] == receipt["original_context_reads"] == 2
    assert receipt["blocks"] == 5 and receipt["lean_units"] > 0
    audit = audit_graph(tmp_path / "run")
    assert audit["status"] == "complete" and audit["accepted_blocks"] == 5
    assert audit["program_assembled_blocks"] == {"control": 1, "split": 1}


def test_graph_audit_distinguishes_no_layout_from_no_graph(tmp_path):
    step = tmp_path / "steps/graph"
    step.mkdir(parents=True)
    (tmp_path / "result.json").write_text('{"stages":{}}', encoding="utf8")
    value = step / "value.json"
    value.write_text('{"cfg":{"blocks":{"a":{}}},"assembly":{}}', encoding="utf8")
    (step / "result.json").write_text(json.dumps({"value_file": "value.json", "value_sha256": file_sha256(value),
        "accepted_call": "calls/a001"}), encoding="utf8")
    accepted = audit_graph(tmp_path)
    assert accepted["status"] == "complete" and accepted["program_assembled_blocks"] == {"control": 0, "split": 0}
    (step / "result.json").write_text('{"status":"structural_failure"}', encoding="utf8")
    failed = audit_graph(tmp_path)
    assert failed["status"] == "structural_failure" and failed["program_assembled_blocks"] is None
