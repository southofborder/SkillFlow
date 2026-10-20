"""Fresh first-response evaluation inputs, never production teaching examples.

The sources, graphs, Tasks, and reference annotations are assistant-authored
fixtures. References and semantic acceptance criteria are external evaluation
claims, not expert gold labels, and are not sent as annotation instructions.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib

from skillflow.common.source_evidence import _digest
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.task import task_source_files, validate_task_candidate
from skillflow.propagation.review.material import prepare_review_material


def ev(reason="The source explicitly states this relationship."):
    return {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "reason": reason}


def inp(index=0): return {"kind": "input", "index": index}
def local(name): return {"kind": "local", "name": name}
def literal(value): return {"type": "literal", "literal_value": value}
def result(name): return {"type": "result", "identifier": name}


def goal(requirement, target, preserve="value", **extra):
    return {"requirement_id": requirement, "target": target, "preserve": preserve,
            "reason": "Preserve the specified task information at this actual position.", **extra}


def ir(identity, opcode, inputs, output=None):
    return {"id": identity, "opcode": opcode, "inputs": inputs,
            "outputs": [] if output is None else [result(output)], "constraints": [], "metadata": {}}


def segment(ops, effect="transform", *, mode="default", returns=()):
    event = {"effect": effect, "atomic_ops": [{**op, "evidences": [ev()]} for op in ops]}
    if effect is not None: event["evidences"] = [ev()]
    return {"kind": "processing", "mode": mode, "returns": list(returns), "evidences": [ev()], "events": [event]}


def spec(events=(), output=None):
    value = {"operator": ["agent_runtime"], "operator_evidences": [{"value": "agent_runtime", **ev()}],
             "order": "fixed", "events": list(events), "sensitivity": [],
             "output_bindings": [] if output is None else [{"output_index": 0, "value": local(output), "evidences": [ev()]}]}
    if not events or all(event["effect"] is None for seg in events for event in seg["events"]):
        value["empty_effect_evidences"] = [ev()]
    return value


def location(kind, name, scope="recipient", retention=None):
    return {"kind": kind, "name": name, "operand_refs": [], "access_scope": scope, "retention": retention}


def fixture(name, stage, source, requirements, instructions, specs, *, locations=None, demands=(), gaps=None, source_entry=None):
    context_keys=sorted({operand["identifier"] for item in instructions for operand in item["inputs"] if operand["type"]=="context_key"})
    cfg = {"entry_block_id": "work", "constraints": [], "edges": [], "declared_context_keys": context_keys,
           "blocks": {"work": {"block_id": "work", "block_name": "Evaluation workflow", "instructions": instructions,
                              "constraints": [], "data_source_kind": None}}}
    if source_entry is not None:
        context_name, acquisition_id, output_name = source_entry
        cfg["entry_block_id"]="entry"
        cfg["declared_context_keys"]=[context_name]
        cfg["blocks"]["entry"]={"block_id":"entry","block_name":"Supplied context acquisition","data_source_kind":"context","constraints":[],
            "instructions":[ir(acquisition_id,"read_context",[{"type":"context_key","identifier":context_name}],output_name),ir("ir_input_dispatch","dispatch",[])]}
        cfg["edges"]=[{"source_block_id":"entry","target_block_id":"work","condition_text":None}]
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    sources = {"files": [{"path": "SKILL.md", "content": source, "sha256": digest}],
               "source_sha256": _digest([{"path": "SKILL.md", "sha256": digest}])}
    task_candidate = {"purpose": {"text": " ".join(requirements), "evidences": [ev()]},
        "requirements": [{"id": f"R{i+1}", "text": text, "evidences": [ev()]} for i, text in enumerate(requirements)],
        "source_accounting": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "disposition": "requirement",
            "requirement_ids": [f"R{i+1}" for i in range(len(requirements))], "issue_ids": [],
            "reason": "This synthetic source states the obligations preserved by the offline Task fixture."}], "issues": []}
    task = validate_task_candidate(task_candidate, source_files=task_source_files(sources),
                                   source_sha256=sources["source_sha256"], basis="declared_skill")
    material = prepare_material(sources, cfg, task_baseline=task)
    gaps = gaps or {}
    raw = {"outcome": "completed", "task_revision_id": material["task"]["task_sha256"], "realizations": [],
           "demands": list(demands), "expressions": [], "ir_semantics": specs,
           "locations": locations or {}, "location_evidences": {key: [ev()] for key in (locations or {})}}
    for item in material["task"]["requirements"]:
        rid = item["id"]
        raw["realizations"].append({"requirement_id": rid, "status": "partial" if rid in gaps else "expressed",
            "bindings": [{"target": {"block_id": "work", "path": []}, "reason": "This workflow implements the stated obligation."}],
            "gaps": [{"reason": gaps[rid], "evidences": [ev()]}] if rid in gaps else []})
    return {"name": name, "stage": stage, "material": material, "reference": raw,
            "provenance": "assistant_authored_offline_task_and_evaluation_fixture", "semantic_checks": []}


def _annotation_a():
    source = ("For a sculpture loan receipt, read the loan_form from session context. Return an object with loan_id copied unchanged "
              "from that form and checkcode produced by an isolated local checksum routine over the complete form. The routine returns "
              "only checkcode to the agent; its algorithm is unspecified. The form also contains wrapping_notes. Return the receipt internally.")
    read = {"op": "read", "location": "form_context", "output": "form"}
    pick = {"op": "select_part", "input": inp(), "path": ["loan_id"], "output": "id_text"}
    calc = {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "checksum"}
    build = {"op": "build", "container": "object", "parts": [{"path": ["loan_id"], "value": inp()}, {"path": ["checkcode"], "value": inp(1)}], "output": "receipt"}
    ex = fixture("annotation_a_receipt", "annotation", source, ["Return the original loan_id together with the locally produced checkcode in an internal receipt."],
        [ir("ir_load_loan", "read_form", [], "form"), ir("ir_loan_id", "extract_id", [result("form")], "id_text"),
         ir("ir_loan_checksum", "local_checksum", [result("form")], "checksum"),
         ir("ir_loan_receipt", "compose_receipt", [result("id_text"), result("checksum")], "receipt"),
         ir("ir_loan_return", "return", [result("receipt")])],
        {"ir_load_loan": spec([segment([read], "context_read")], "form"), "ir_loan_id": spec([segment([pick])], "id_text"),
         "ir_loan_checksum": spec([segment([calc], None, mode="local", returns=[local("checksum")])], "checksum"),
         "ir_loan_receipt": spec([segment([build])], "receipt"), "ir_loan_return": spec()},
        locations={"form_context": location("runtime_context", "loan_form", "task", "task")},
        demands=[goal("R1", {"instruction_id": "ir_loan_return", "side": "input", "index": 0})])
    ex["semantic_checks"] = ["loan_id retains an explicit select_part relationship from the context value.",
        "The checksum remains opaque; full-form processing is locally isolated and only its result is returned by that segment.",
        "The final return uses its true CFG input and no invented public output.",
        "No assertion that wrapping_notes is independently sensitive or that checksum is a proven sanitizer."]
    return ex


def _annotation_b():
    source = ("Prepare a parking occupancy bulletin from the supplied envelope. Its bays list contains usable flags; zone_code is optional. "
              "Retain bays whose usable flag is true, calculate their number, and calculate has_room as whether that number exceeds zero. "
              "Call the kiosk update interface with available_count set to that number, has_room set to that Boolean, and zone_code copied "
              "unchanged only when present. Append the same number to occupancy.log. The log encoding is unspecified. Return the number internally.")
    select = {"op": "select_part", "input": inp(), "path": ["bays"], "output": "bays"}
    filtered = {"op": "filter_items", "input": local("bays"), "predicate": "usable is true", "output": "usable_bays",
        "expression": {"expression": {"op": "field", "arg": {"op": "ref", "value": local("bays")}, "path": ["usable"]}, "evidences": [ev()]},
        "demands": [goal("R1", {"kind": "output"}, "shape")]}
    count = {"op": "compute", "inputs": [local("usable_bays")], "dependencies": ["derived"], "output": "available",
        "expression": {"expression": {"op": "count", "arg": {"op": "ref", "value": local("usable_bays")}}, "evidences": [ev()]}}
    boolean = {"op": "compute", "inputs": [local("available")], "dependencies": ["derived"], "output": "has_room",
        "expression": {"expression": {"op": "gt", "left": {"op": "ref", "value": local("available")}, "right": {"op": "literal", "value": 0}}, "evidences": [ev()]}}
    present = {"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "has_zone",
        "expression": {"expression": {"op": "present", "arg": {"op": "field", "arg": {"op": "ref", "value": inp()}, "path": ["zone_code"]}}, "evidences": [ev()]}}
    zone = {"op": "select_part", "input": inp(), "path": ["zone_code"], "output": "zone"}
    build = {"op": "build", "container": "object", "parts": [{"path": ["available_count"], "value": local("available")},
        {"path": ["has_room"], "value": local("has_room")}, {"path": ["zone_code"], "value": local("zone"), "when": local("has_zone")}], "output": "request"}
    send = {"op": "deliver", "target": "kiosk", "inputs": [local("request")], "demands": [goal("R2", {"kind": "self"}, "action"),
        goal("R2", {"kind": "input", "index": 0}, path=["available_count"], expected=local("available")),
        goal("R2", {"kind": "input", "index": 0}, path=["has_room"], expected=local("has_room")),
        goal("R2", {"kind": "input", "index": 0}, path=["zone_code"], expected=local("zone"))]}
    save = {"op": "write", "target": "history", "mode": "append", "input": inp(), "demands": [goal("R3", {"kind": "self"}, "action"), goal("R3", {"kind": "input", "index": 0}, expected=inp())]}
    ex = fixture("annotation_b_occupancy", "annotation", source,
        ["Preserve the usable-bay selection, its number, and the Boolean indicating whether the number exceeds zero.",
         "Send the number, Boolean, and present original zone_code to the kiosk interface; omit absent zone_code.",
         "Append that number to occupancy.log and return it internally; encoding is unspecified."],
        [ir("ir_parking_bulletin", "prepare_update", [result("envelope")], "available"),
         ir("ir_parking_history", "append_number", [result("available")]), ir("ir_parking_return", "return", [result("available")])],
        {"ir_parking_input":spec([segment([{"op":"read","location":"envelope","output":"envelope"}],"context_read")],"envelope"),
         "ir_input_dispatch":spec(),
         "ir_parking_bulletin": spec([segment([select, filtered, count, boolean, present, zone, build]), segment([send], None)], "available"),
         "ir_parking_history": spec([segment([save], "fs_write")]), "ir_parking_return": spec()},
        locations={"envelope": {**location("runtime_context", "parking_envelope", "task", "task"),
            "operand_refs":[{"instruction_id":"ir_parking_input","side":"input","index":0}]},
            "kiosk": location("tool", "kiosk update interface"), "history": location("storage", "occupancy.log", "task", "persistent")},
        demands=[goal("R3", {"instruction_id": "ir_parking_return", "side": "input", "index": 0})],
        source_entry=("parking_envelope","ir_parking_input","envelope"))
    ex["semantic_checks"] = ["Filtering is filter_items with its usable predicate, not whole-member value or collection-root truth as the selection requirement.",
        "has_room refers to a real Boolean computation over count, not the filtered collection.",
        "Optional zone_code retains its original value and an independent presence control; flags are not request members.",
        "Actual kiosk inputs and append payload carry demands; upstream count or action-only seeds do not replace them.",
        "Unspecified encoding alone is not an unexpressed task restriction; preserve the abstract append-content relationship without inventing a format gap."]
    return ex


def _review_case(*, adverse):
    if adverse:
        name="review_b_dispatch"; source=("For a laboratory crate dispatch, read the crate entry from dispatch context. Send only its original tracking_code to the sorter interface. "
            "Save its original slot_count to slot-ledger.txt. The entry also contains handling_note, which is not a sorter parameter or ledger content.")
        first_field, second_field, read_name, tool_name, filename = "tracking_code", "slot_count", "dispatch context", "sorter interface", "slot-ledger.txt"
        reqs=["Send only the original tracking_code to the sorter interface.", "Save the original slot_count to slot-ledger.txt."]
    else:
        name="review_a_display"; source=("Read a complete exhibition display_card from display context. Send the entire display_card unchanged to the exhibition display interface. "
            "Save only its original caption to caption-archive.txt. The card contains heading, caption, and locale; the entire card is explicitly required by the display.")
        first_field, second_field, read_name, tool_name, filename = None, "caption", "display context", "exhibition display interface", "caption-archive.txt"
        reqs=["Send the entire display_card unchanged to the exhibition display interface.", "Save only its original caption to caption-archive.txt."]
    readop={"op":"read","location":"context","output":"entry"}
    if adverse: readop["demands"]=[goal("R1",{"kind":"output"},reason="Preserve the full entry for accessing the tracking code.")]
    ops=[]
    if first_field: ops.append({"op":"select_part","input":inp(),"path":[first_field],"output":"code"})
    send={"op":"deliver","target":"display","inputs":[local("code") if first_field else inp()],"demands":[goal("R1",{"kind":"self"},"action"),goal("R1",{"kind":"input","index":0},expected=inp(),**({"expected_path":[first_field]} if first_field else {}))]}
    pick={"op":"select_part","input":inp(),"path":[second_field],"output":"saved_value"}
    write={"op":"write","target":"archive","mode":"replace","input":local("saved_value"),"demands":[goal("R2",{"kind":"self"},"action")]}
    if not adverse: write["demands"].append(goal("R2",{"kind":"input","index":0},expected=inp(),expected_path=[second_field]))
    sendsegments=([segment(ops)] if ops else [])+[segment([send],None)]
    ex=fixture(name,"review",source,reqs,
        [ir("ir_entry_read","read_entry",[],"entry"),ir("ir_entry_send","send_entry",[result("entry")]),
         ir("ir_entry_save","save_field",[result("entry")]),ir("ir_entry_end","return",[])],
        {"ir_entry_read":spec([segment([readop],"context_read")],"entry"),"ir_entry_send":spec(sendsegments),
         "ir_entry_save":spec([segment([pick]),segment([write],"fs_write")]),"ir_entry_end":spec()},
        locations={"context":location("runtime_context",read_name,"task","task"),"display":location("tool",tool_name),"archive":location("storage",filename,"task","persistent")})
    ex["semantic_checks"] = (["Find the R1 whole-entry output demand at the read as broader than the required tracking_code; domain=annotation, not Task revision.",
        "Find the missing R2 write-content demand, locating the write or realization parent; the existing action seed is legal but insufficient.",
        "Do not require changes to the correct original-field selections or infer networking from interface names."] if adverse else
        ["Do not flag the explicit whole-card delivery demand as excessive solely because it is whole-value.",
         "Do not flag the supported caption write payload as missing; the actual write has both action and content demands.",
         "Use exactly the supplied declaration_index entries; do not invent an additional goal check."])
    ex["expected_findings"] = 2 if adverse else 0
    return ex


def screen_fixtures():
    return [_annotation_a(), _annotation_b(), _review_case(adverse=False), _review_case(adverse=True)]


def review_reference(material, *, adverse=False):
    """An offline response fixture, never supplied in a review request."""
    check={"status":"accepted","reason":"The supplied relation agrees with this synthetic source.","finding_indexes":[]}
    response={"outcome":"completed","source_checks":[{"file":r["file"],"start_line":r["line"],"end_line":r["line"],**deepcopy(check)} for r in material["source_line_universe"]],
        "requirement_checks":[{"requirement_id":r["id"],**deepcopy(check)} for r in material["task"]["requirements"]],
        "declaration_checks":[{"raw_pointer":r["raw_pointer"],**deepcopy(check)} for r in material["declaration_index"]],
        "reviewed_ir_ids":[i["id"] for b in material["cfg"]["blocks"].values() for i in b["instructions"]],"findings":[]}
    if adverse:
        pointers=["/ir_semantics/ir_entry_read/events/0/events/0/atomic_ops/0/demands/0", "/ir_semantics/ir_entry_save/events/1/events/0/atomic_ops/0"]
        for i,pointer in enumerate(pointers):
            target=next(t for t in material["target_index"] if t["kind"]=="annotation" and t["pointer"]==pointer)
            response["findings"].append({"domain":"annotation","target_ids":[target["id"]],"explanation":
                "The complete entry demand exceeds the specified tracking-code requirement." if i==0 else "The write has an action demand but omits its required slot-count payload demand.",
                "evidences":[ev()],"suggestion":"Retain only the task-supported information demand at the relevant value position."})
            response["requirement_checks"][i].update(status="issue",finding_indexes=[i])
        next(x for x in response["declaration_checks"] if x["raw_pointer"]==pointers[0]).update(status="issue",finding_indexes=[0])
    return response
