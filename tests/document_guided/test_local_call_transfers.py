"""Local callable forwarding has different witnesses from an external request."""
from copy import deepcopy
import json

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragment_wire import expand_processing_response
from skillflow.document_guided.fragments import validate_fragment
from skillflow.document_guided.local_call_transfers import binding_errors, local_call_inputs


FILE = "skill/sample.py"
CODE = "def join_words(first, second):\n    pair = (first, second)\n    return pair\nleft, right = 'a', 'b'\nanswer = join_words(left, right)\n"


def span(first, last=None):
    return {"file": FILE, "start_line": first, "end_line": last or first}


def port(identifier, name):
    return {"type": "result", "identifier": identifier, "semantic_name": name}


def candidate():
    args = [port("a", "caller.left"), port("b", "caller.right")]
    params = [port("x", "inside.first"), port("y", "inside.second")]
    func = port("func", "functions.join_words")
    declaration = {"id": "decl", "opcode": "value", "inputs": [], "outputs": [func],
                   "metadata": {"source_span": span(1, 3)}}
    source = span(5)
    action = {"kind": "call", "role": "call", "ref": "invoke", "source": source}
    call = {"id": "apply", "opcode": "call", "inputs": [func, *args], "outputs": params, "metadata": {"callee": "join_words",
        "source_span": source, "ordered_argument_bindings": [
            {"actual": a["semantic_name"], "formal": f["semantic_name"]} for a, f in zip(args, params)],
        "source_actions": [action]}}
    exit = {"id": "next", "opcode": "dispatch", "inputs": [], "outputs": [], "metadata": {}}
    body = {"id": "body", "opcode": "value", "inputs": params, "outputs": [], "metadata": {"source_span": span(2)}}
    cfg = {"blocks": {name: {"block_id": name, "instructions": rows} for name, rows in
                    (("declaration", [declaration]), ("caller", [call, exit]), ("inside", [body]))},
           "edges": [{"source_block_id": "caller", "target_block_id": "inside", "condition_text": None}]}
    return cfg, call, action, {FILE: CODE}


def test_generic_local_call_has_distinct_source_actuals_and_formals():
    assert local_call_inputs(*candidate()) == (1, 2)
    row = {"output_bindings": [{"output_index": i, "value": {"kind": "input", "index": i+1}} for i in range(2)]}
    assert binding_errors(row, (1, 2)) == []
    wrong = deepcopy(row)
    wrong["output_bindings"][0]["value"]["index"] = 2
    assert binding_errors(wrong, (1, 2))
    extra = {**row, "segments": [{"mode": "local", "returns": [],
                                 "ops": [{"op": "call", "location": "external", "inputs": [], "output": "new"}]}]}
    assert binding_errors(extra, (1, 2))


def test_formals_consumed_in_different_blocks_or_never_read():
    cfg, op, action, files = candidate()
    files[FILE] = CODE.replace("pair = (first, second)\n    return pair", "left = first\n    return left + second")
    body = cfg["blocks"]["inside"]["instructions"][0]
    body["inputs"] = op["outputs"][:1]
    later = {"id": "later", "opcode": "return", "inputs": op["outputs"][1:], "outputs": [],
             "metadata": {"source_span": span(3)}}
    cfg["blocks"]["later"] = {"block_id": "later", "instructions": [later]}
    cfg["edges"].append({"source_block_id": "inside", "target_block_id": "later", "condition_text": None})
    assert local_call_inputs(cfg, op, action, files) == (1, 2)
    files[FILE] = files[FILE].replace("return left + second", "return left")
    later["inputs"] = []
    assert local_call_inputs(cfg, op, action, files) == (1, 2)
    # A use on the public or caller side cannot consume this invocation's local formals.
    cfg["blocks"]["unrelated"] = {"block_id":"unrelated", "instructions":[{**later, "inputs": op["outputs"]}]}
    assert local_call_inputs(cfg, op, action, files) is None


@pytest.mark.parametrize("fault", ["shadowed", "attribute", "keywords", "decorator", "generator", "wrong_declaration",
    "different_function", "not_body_entry", "formal_not_consumed", "wrong_actual_name", "reversed_formals",
    "unverified_metadata", "conditional", "shared_entry", "other_source_action", "string_literal"])
def test_unproved_locality_never_satisfies_the_external_call_rule(fault):
    cfg, op, action, files = candidate()
    if fault == "shadowed":
        files[FILE] = CODE.replace("left, right = 'a', 'b'", "join_words = other")
    elif fault == "attribute":
        files[FILE] = CODE.replace("answer = join_words(", "answer = service.join_words(")
    elif fault == "keywords":
        files[FILE] = CODE.replace("join_words(left, right)", "join_words(first=left, second=right)")
    elif fault == "decorator":
        files[FILE] = "@decorator\n" + CODE
    elif fault == "generator":
        files[FILE] = CODE.replace("return pair", "yield pair")
    elif fault == "wrong_declaration":
        cfg["blocks"]["declaration"]["instructions"][0]["metadata"]["source_span"] = span(1)
    elif fault == "different_function":
        op["metadata"]["callee"] = "different"
    elif fault == "not_body_entry":
        cfg["blocks"]["inside"]["instructions"][0]["metadata"]["source_span"] = span(3)
    elif fault == "formal_not_consumed":
        cfg["blocks"]["inside"]["instructions"][0]["inputs"] = op["outputs"][:1]
    elif fault == "wrong_actual_name":
        op["inputs"][1]["semantic_name"] = "caller.right"
    elif fault == "reversed_formals":
        op["outputs"] = list(reversed(op["outputs"]))
    elif fault == "unverified_metadata":
        op["metadata"]["ordered_argument_bindings"][0]["actual"] = "unrelated"
    elif fault == "conditional":
        cfg["edges"][0]["condition_text"] = "if called"
    elif fault == "shared_entry":
        cfg["edges"].append({"source_block_id": "declaration", "target_block_id": "inside", "condition_text": None})
    elif fault == "other_source_action":
        action["source"] = span(2)
    else:
        files[FILE] = CODE.replace("left, right = 'a', 'b'", 'example = """') + '"""\n'
    assert local_call_inputs(cfg, op, action, files) is None


def test_unchanged_corrected_model_record_passes_full_processing_only_for_local_forwarding():
    from tests.document_guided.test_revalidated_processing_delivery import ROOT, archived_slice
    archive = ROOT / "experiments/doe/runs/document-guided-google-search-downstream-high-20261125-211940"
    candidate_file = archive / "steps/processing/calls/a002/merged-candidate.json"
    if not candidate_file.is_file():
        pytest.skip("Archived corrected semantic response unavailable.")
    material, *_ = archived_slice.__wrapped__()
    raw = expand_processing_response(json.loads(candidate_file.read_bytes()))
    presented = deepcopy(raw)
    records = validate_fragment("processing", raw, material)
    assert raw == presented and len(records["ir_semantics"]) == 84 and len(records["processing_gaps"]) == 9
    assert records["ir_semantics"]["ir_045"] == raw["ir_semantics"]["ir_045"]
    for ir in ["ir_049", "ir_076"]:
        wrong = deepcopy(raw)
        wrong["ir_semantics"][ir]["segments"] = []
        with pytest.raises(StructuralValidationError):
            validate_fragment("processing", wrong, material)
    wrong = deepcopy(raw)
    wrong["ir_semantics"]["ir_045"]["output_bindings"][0]["value"]["index"] = 2
    with pytest.raises(StructuralValidationError, match="corresponding formal output"):
        validate_fragment("processing", wrong, material)
