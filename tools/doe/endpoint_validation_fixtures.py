"""Independent English fixtures for the endpoint-demand online pilot.

These assistant-authored references and external checks are not expert labels.
Only ``material`` is a business input; references and acceptance expectations
remain outside the request. No model or network access occurs in this module.
"""
from __future__ import annotations

from copy import deepcopy

from skillflow.propagation.review.material import prepare_review_material
from tools.doe.prompt_screen_fixtures import (
    ev, fixture, goal, inp, ir, local, location, result, segment, spec,
)


def _source_location(name, identity):
    return {**location("runtime_context", name, "task", "task"),
            "operand_refs": [{"instruction_id": identity, "side": "input", "index": 0}]}


def _read(identity, place, output):
    return {identity: spec([segment([
        {"op": "read", "location": place, "output": output}], "context_read")], output),
        "ir_input_dispatch": spec()}


def _send(place, values, demands):
    return {"op": "deliver", "target": place, "inputs": values, "demands": demands}


def _delivered_value(requirement, *, index=0, path=None, expected=None, expected_path=None):
    fields = {}
    for name, value in (("path", path), ("expected", expected), ("expected_path", expected_path)):
        if value is not None:
            fields[name] = value
    return goal(requirement, {"kind": "input", "index": index}, **fields)


def _annotation_ceramic_dispatch():
    source = (
        "For a ceramic shipment, read the complete ceramic_batch from session context. "
        "Send its original run_no to the stamping interface as a single scalar argument. "
        "Then send the dispatch interface one record containing the original glaze and the original batches fields. "
        "Append the same original batches value to firing-ledger.txt and return internally. "
        "The batch also contains a private_lab_note identifying confidential laboratory work; that note is not a parameter or ledger content. "
        "The two interface deployments are unspecified.")
    stamp = _send("stamp", [local("run")], [goal("R1", {"kind": "self"}, "action"),
        _delivered_value("R1", expected=inp(), expected_path=["run_no"])])
    request = {"op": "build", "container": "object", "output": "dispatch_record", "parts": [
        {"path": ["glaze"], "value": local("glaze")}, {"path": ["batches"], "value": local("batches")}]}
    dispatch = _send("dispatch", [local("dispatch_record")], [goal("R2", {"kind": "self"}, "action"),
        _delivered_value("R2", path=["glaze"], expected=inp(), expected_path=["glaze"]),
        _delivered_value("R2", path=["batches"], expected=inp(), expected_path=["batches"])])
    save = {"op": "write", "target": "ledger", "mode": "append", "input": local("batches"),
        "demands": [goal("R3", {"kind": "self"}, "action"),
                    _delivered_value("R3", expected=inp(), expected_path=["batches"])]}
    specifications = _read("ir_batch_read", "batch", "batch")
    specifications.update({
        "ir_batch_stamp": spec([segment([
            {"op": "select_part", "input": inp(), "path": ["run_no"], "output": "run"}]), segment([stamp], None)]),
        "ir_batch_dispatch": spec([segment([
            {"op": "select_part", "input": inp(), "path": ["glaze"], "output": "glaze"},
            {"op": "select_part", "input": inp(), "path": ["batches"], "output": "batches"}, request]), segment([dispatch], None)]),
        "ir_batch_ledger": spec([segment([
            {"op": "select_part", "input": inp(), "path": ["batches"], "output": "batches"}]), segment([save], "fs_write")]),
        "ir_batch_return": spec()})
    specifications["ir_batch_read"]["sensitivity"] = [{"value": local("batch"), "path": ["private_lab_note"],
        "property": "value", "label": "confidential_work", "evidences": [ev()]}]
    example = fixture("annotation_ceramic_dispatch", "annotation", source, [
        "Send the original run_no scalar to the stamping interface.",
        "Send a dispatch record containing the original glaze and batches values to the dispatch interface.",
        "Append the original batches value to firing-ledger.txt."],
        [ir("ir_batch_stamp", "stamp", [result("batch")]),
         ir("ir_batch_dispatch", "dispatch_ceramics", [result("batch")]),
         ir("ir_batch_ledger", "append_batches", [result("batch")]), ir("ir_batch_return", "return", [])],
        specifications, locations={"batch": _source_location("ceramic_batch", "ir_batch_read"),
            "stamp": location("tool", "stamping interface"), "dispatch": location("tool", "dispatch interface"),
            "ledger": location("storage", "firing-ledger.txt", "task", "persistent")},
        source_entry=("ceramic_batch", "ir_batch_read", "batch"))
    example["semantic_checks"] = [
        "Whole context acquisition and its applicable observation stay whole, without a whole-read value seed merely to prepare fields.",
        "The stamping receiver has a run_no scalar content demand; the dispatch receiver has glaze and batches value demands on its actual input paths.",
        "A seed at one receiver, upstream selection, or construction does not replace the other receiver's required content demands.",
        "The append has both action and current batches-payload demands; prior ledger contents are not required.",
        "The confidential laboratory note is declared at the acquired value, without inventing other fields or a network mechanism."]
    example["expected_relations"] = {"read_instruction": "ir_batch_read", "whole_read_seed": False,
        "receiver_fields": {"stamp": [[]], "dispatch": [["glaze"], ["batches"]]},
        "append_field": ["batches"], "sensitivity_field": ["private_lab_note"]}
    return example


def _annotation_folio_return():
    source = (
        "Read the complete music_folio from session context. Send that entire folio unchanged as a single argument to the manuscript vault interface. "
        "The complete manuscript is explicitly required for deposit, including its annotations. "
        "Separately calculate a critique from the complete folio by an unspecified content-processing procedure and return that critique internally. "
        "No local isolation or narrower return mechanism is specified for critique processing. The vault deployment is unspecified.")
    deposit = _send("vault", [inp()], [goal("R1", {"kind": "self"}, "action"),
        _delivered_value("R1", expected=inp())])
    opaque = {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "critique"}
    specifications = _read("ir_folio_read", "folio", "folio")
    specifications.update({"ir_folio_deposit": spec([segment([deposit], None)]),
        "ir_folio_critique": spec([segment([opaque], None)], "critique"), "ir_folio_return": spec()})
    example = fixture("annotation_folio_return", "annotation", source, [
        "Deposit the entire original music_folio unchanged with the manuscript vault interface.",
        "Compute a critique from the complete folio and return the critique internally."],
        [ir("ir_folio_deposit", "deposit_manuscript", [result("folio")]),
         ir("ir_folio_critique", "calculate_critique", [result("folio")], "critique"),
         ir("ir_folio_return", "return", [result("critique")])], specifications,
        locations={"folio": _source_location("music_folio", "ir_folio_read"), "vault": location("tool", "manuscript vault interface")},
        demands=[goal("R2", {"instruction_id": "ir_folio_return", "side": "input", "index": 0})],
        source_entry=("music_folio", "ir_folio_read", "folio"))
    example["semantic_checks"] = [
        "An explicit entire-folio requirement legitimately seeds the vault's actual input with whole-value demand.",
        "The unspecified critique remains opaque with conservative dependency; no unsupported local isolation or sanitizer is inferred.",
        "The internal return uses its real CFG input, without invented public outputs or caller boundaries.",
        "The root acquisition does not need a separate source-claimed whole-value seed solely because acquisition was whole."]
    example["expected_relations"] = {"read_instruction": "ir_folio_read", "whole_read_seed": "not_required_by_acquisition_alone",
        "receiver_fields": {"vault": [[]]}, "opaque_instruction": "ir_folio_critique", "return_instruction": "ir_folio_return"}
    return example


def _review_custody_release():
    source = (
        "Read the signed custody_memo from session context. The custody endpoint must receive that entire memo unchanged, including its endorsement block. "
        "Also compute release_ok as whether the memo's release_flag equals Boolean true, and return release_ok internally. "
        "The complete memo is a required custody deposit; its other fields are not inputs to the release comparison. Endpoint deployment is unspecified.")
    send = _send("custody", [inp()], [goal("R1", {"kind": "self"}, "action"), _delivered_value("R1", expected=inp())])
    boolean = {"op": "compute", "inputs": [local("release_flag")], "dependencies": ["derived"], "output": "release_ok",
        "expression": {"expression": {"op": "eq", "left": {"op": "ref", "value": local("release_flag")},
                        "right": {"op": "literal", "value": True}}, "evidences": [ev()]}}
    specifications = _read("ir_memo_read", "memo", "memo")
    specifications.update({"ir_memo_deposit": spec([segment([send], None)]),
        "ir_memo_release": spec([segment([
            {"op": "select_part", "input": inp(), "path": ["release_flag"], "output": "release_flag"}, boolean])], "release_ok"),
        "ir_memo_return": spec()})
    example = fixture("review_custody_release", "review", source, [
        "Deposit the entire original custody_memo unchanged at the custody endpoint.",
        "Return whether the original release_flag equals Boolean true."],
        [ir("ir_memo_deposit", "deposit_memo", [result("memo")]),
         ir("ir_memo_release", "compare_release", [result("memo")], "release_ok"),
         ir("ir_memo_return", "return", [result("release_ok")])], specifications,
        locations={"memo": _source_location("custody_memo", "ir_memo_read"), "custody": location("tool", "custody endpoint")},
        demands=[goal("R2", {"instruction_id": "ir_memo_return", "side": "input", "index": 0}, "truth")],
        source_entry=("custody_memo", "ir_memo_read", "memo"))
    example["expected_findings"] = 0
    example["semantic_checks"] = [
        "Do not flag the actual custody input's whole-value seed: deposit of the complete signed memo is explicit.",
        "The release comparison is a genuine Boolean expression, with truth demand at its real return input.",
        "No finding should invent a public return output, networking, a missing field seed, or additional goals.",
        "All existing goal pointers, source lines, requirements and IR identities must be covered exactly."]
    return example


def _review_voucher_delivery():
    source = (
        "Read the complete rebate_voucher from session context. Submit one record containing the voucher's original claim_id and its original credit value to the redemption desk. "
        "Save the same original credit value to credit-register.txt. The voucher also contains a private_case_note, which is neither a redemption parameter nor register content. "
        "The redemption desk deployment is unspecified; return internally.")
    read = {"op": "read", "location": "voucher", "output": "voucher", "demands": [
        goal("R1", {"kind": "output"}, reason="Keep the complete voucher while preparing the redemption submission.")]}
    build = {"op": "build", "container": "object", "output": "submission", "parts": [
        {"path": ["claim_id"], "value": local("claim")}, {"path": ["credit"], "value": local("credit")}],
        "demands": [goal("R1", {"kind": "input", "index": 0}), goal("R1", {"kind": "input", "index": 1})]}
    send = _send("redemption", [local("submission")], [goal("R1", {"kind": "self"}, "action"),
        goal("R1", {"kind": "input", "index": 0}, "shape")])
    save = {"op": "write", "target": "register", "mode": "replace", "input": local("credit"), "demands": [
        goal("R2", {"kind": "self"}, "action"), _delivered_value("R2", expected=inp(), expected_path=["credit"])]}
    example = fixture("review_voucher_delivery", "review", source, [
        "Submit the original claim_id and credit values in a record to the redemption desk.",
        "Save the original credit value to credit-register.txt."],
        [ir("ir_voucher_send", "submit_redemption", [result("voucher")]),
         ir("ir_voucher_save", "save_credit", [result("voucher")]), ir("ir_voucher_return", "return", [])],
        {"ir_voucher_read": spec([segment([read], "context_read")], "voucher"), "ir_input_dispatch": spec(),
         "ir_voucher_send": spec([segment([
             {"op": "select_part", "input": inp(), "path": ["claim_id"], "output": "claim"},
             {"op": "select_part", "input": inp(), "path": ["credit"], "output": "credit"}, build]), segment([send], None)]),
         "ir_voucher_save": spec([segment([
             {"op": "select_part", "input": inp(), "path": ["credit"], "output": "credit"}]), segment([save], "fs_write")]),
         "ir_voucher_return": spec()},
        locations={"voucher": _source_location("rebate_voucher", "ir_voucher_read"),
            "redemption": location("tool", "redemption desk"), "register": location("storage", "credit-register.txt", "task", "persistent")},
        source_entry=("rebate_voucher", "ir_voucher_read", "voucher"))
    example["expected_findings"] = 2
    example["expected_relations"] = {
        "broad_read_goal": "/ir_semantics/ir_voucher_read/events/0/events/0/atomic_ops/0/demands/0",
        "delivery_parent": "/ir_semantics/ir_voucher_send/events/1/events/0/atomic_ops/0",
        "requirement_id": "R1", "domain": "annotation"}
    example["semantic_checks"] = [
        "Report the complete read-output value seed as broader than R1; whole acquisition is not a whole-value task requirement.",
        "Report missing value demands on the actual redemption input's claim_id and credit paths: upstream build seeds plus delivery action/shape do not supply receiver content demands.",
        "Locate the existing broad seed through declaration_index; locate missing seeds at the delivery or realization parent, never an invented goal pointer.",
        "Keep the correct field operations, actual request, existing action/shape seeds and exact register content demands intact.",
        "Use candidate target_ids for annotation locations; any CFG evidence must resolve in the actual CFG, not inside transfer events or operation demands."]
    return example


def review_reference(material, *, adverse=False):
    """Complete assistant-authored review; never included in a live request."""
    accepted = {"status": "accepted", "reason": "The declared relation is supported by this fixture's source and current representation.", "finding_indexes": []}
    response = {"outcome": "completed",
        "source_checks": [{"file": item["file"], "start_line": item["line"], "end_line": item["line"], **deepcopy(accepted)}
                          for item in material["source_line_universe"]],
        "requirement_checks": [{"requirement_id": item["id"], **deepcopy(accepted)} for item in material["task"]["requirements"]],
        "declaration_checks": [{"raw_pointer": item["raw_pointer"], **deepcopy(accepted)} for item in material["declaration_index"]],
        "reviewed_ir_ids": [item["id"] for block in material["cfg"]["blocks"].values() for item in block["instructions"]], "findings": []}
    if not adverse:
        return response
    pointers = ["/ir_semantics/ir_voucher_read/events/0/events/0/atomic_ops/0/demands/0",
                "/ir_semantics/ir_voucher_send/events/1/events/0/atomic_ops/0"]
    for index, pointer in enumerate(pointers):
        target = next(item for item in material["target_index"] if item["kind"] == "annotation" and item["pointer"] == pointer)
        response["findings"].append({"domain": "annotation", "target_ids": [target["id"]],
            "explanation": ("The read-output demand preserves the entire voucher, although R1 requires only claim_id and credit at redemption. Acquisition scope does not justify that task demand."
                            if index == 0 else "The redemption call has action and shape demands but lacks value demands on its actual claim_id and credit payload paths. Existing upstream build seeds do not express those receiver requirements."),
            "evidences": [ev(), {"target": {"instruction_id": "ir_voucher_read" if index == 0 else "ir_voucher_send", "side": "output" if index == 0 else "input", "index": 0},
                "reason": "This real CFG operand identifies the acquired or submitted value; the candidate target separately identifies the inspected demand declaration."}],
            "suggestion": ("Remove the unjustified whole-read seed while preserving full acquisition and its applicable observations."
                           if index == 0 else "Keep the actual request unchanged and add R1 field-value demands at deliver input 0 for claim_id and credit; do not replace them with upstream or shape demands.")})
    response["requirement_checks"][0].update(status="issue", finding_indexes=[0, 1])
    next(item for item in response["declaration_checks"] if item["raw_pointer"] == pointers[0]).update(status="issue", finding_indexes=[0])
    return response


def endpoint_validation_fixtures():
    """Return four frozen-input-ready cases with external reference responses."""
    examples = [_annotation_ceramic_dispatch(), _annotation_folio_return(),
                _review_custody_release(), _review_voucher_delivery()]
    for example in examples:
        if example["stage"] == "review":
            material = prepare_review_material(example["material"], example["reference"])
            example["reference_response"] = review_reference(material, adverse=bool(example["expected_findings"]))
        else:
            example["reference_response"] = deepcopy(example["reference"])
    return examples
