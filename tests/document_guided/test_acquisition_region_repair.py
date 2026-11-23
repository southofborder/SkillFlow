"""A failed acquisition block can be repaired through one real Block[] update."""
from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.graph_facts import assemble_graph_facts
from skillflow.document_guided.graph_slots import apply_graph_updates, plan_graph_repair
from skillflow.document_guided.graph_steps import FACTS, UPDATES, GraphFactsCorrection, repair_input, validate_graph
from tests.document_guided.test_shared_repair_admission import admission_material


FILES = {"skill/SKILL.md": "Call the selected API.\nSave the returned data.\nRead selected files.\nReturn the response.\n"}


def span(line):
    return {"file": "skill/SKILL.md", "start_line": line, "end_line": line}


def op(ref, role, inputs, outputs, line):
    return {"ref": ref, "opcode": role, "source": span(line), "inputs": inputs, "outputs": outputs}


def facts():
    return {"entry": "work", "blocks": [{"ref": "work", "source_kind": "context", "operations": [
        op("invoke", "call", [{"context_key": "method"}], ["response"], 1),
        op("save", "write", [{"result": "response"}], [], 2),
        op("read", "read", [{"context_key": "chosen_files"}], ["content"], 3)],
        "exit": {"kind": "return", "source": span(4), "values": [{"result": "response"}]}}]}


def split(original):
    actions = {op["ref"]: deepcopy(op) for op in original["operations"]}
    actions["invoke"]["inputs"] = [{"result": "method"}]
    actions["read"]["inputs"] = [{"result": "chosen_files"}]
    def jump(target, line):
        return {"kind": "jump", "target": target, "source": span(line)}
    return [
        {"ref": "work", "source_kind": "context", "operations": [
            op("method", "receive", [{"context_key": "method"}], ["method"], 1)], "exit": jump("work.call", 1)},
        {"ref": "work.call", "source_kind": "normal", "operations": [actions["invoke"], actions["save"]],
         "exit": jump("work.files", 2)},
        {"ref": "work.files", "source_kind": "context", "operations": [
            op("files", "receive", [{"context_key": "chosen_files"}], ["chosen_files"], 3)], "exit": jump("work.read", 3)},
        {"ref": "work.read", "source_kind": "normal", "operations": [actions["read"]], "exit": original["exit"]},
    ]


def apply(base, plan, *rows):
    slot, = plan["slots"]
    return apply_graph_updates(base, plan, {"plan_sha256": plan["plan_sha256"],
        "updates": [{"slot_id": slot, "value": row} for row in rows]}, files=FILES)


def test_shape_and_raw_operand_errors_share_one_slot_and_keep_actual_effects():
    raw = facts()
    base = assemble_graph_facts(raw, files=FILES)
    plan = plan_graph_repair(base, files=FILES)
    slot, = plan["slots"].values()
    assert slot["kind"] == "action_region" and slot["path"] == ["blocks", 0]
    assert {g["slot_id"] for g in plan["gaps"]} == {slot["slot_id"]}
    assert {g["code"] for g in plan["gaps"]} == {"acquisition_shape", "context_acquisition_only"}
    revised = apply(base, plan, split(raw["blocks"][0]))
    assert revised.cfg is not None and not revised.patch_diagnostics
    assert [op["opcode"] for b in revised.facts["blocks"] for op in b["operations"]] == [
        "receive", "call", "write", "receive", "read"]


def test_review_of_derived_continuation_instruction_locates_original_operation():
    raw = facts()
    actions = raw["blocks"][0]["operations"]
    actions[0]["opcode"] = "receive"
    actions[-1]["inputs"] = [{"result": "response"}]
    base = assemble_graph_facts(raw, files=FILES)
    tail = base.id_map["blocks"][base.block_layout["work"]["continuation"]]
    finding = {"id": "F001", "domain": "cfg", "target_ids": [f"cfg:/blocks/{tail}/instructions/0/inputs/0"],
               "required_graph_edit": "field", "source_refs": [span(2)]}
    plan = plan_graph_repair(base, findings=[finding], files=FILES)
    slot, = plan["slots"].values()
    assert slot["path"] == ["blocks", 0, "operations", 1, "inputs", 0]
    head = base.id_map["blocks"]["work"]
    finding["target_ids"] = [f"cfg:/blocks/{head}/instructions/1/inputs/0"]
    assert not plan_graph_repair(base, findings=[finding], files=FILES)["slots"]


@pytest.mark.parametrize("failure", ["lost_effect", "new_effect", "reordered_effect", "lost_constraint", "changed_evidence",
                                      "lost_key", "new_key", "repeated_key", "branch", "cycle"])
def test_structural_edit_rejects_lost_effects_or_restrictions(failure):
    raw = facts()
    block = raw["blocks"][0]
    block["constraints"] = ["This call uses the selected method."]
    rows = split(block)
    action = rows[1]["operations"][0]
    action["constraints"] = block["constraints"][:]
    base = assemble_graph_facts(raw, files=FILES)
    plan = plan_graph_repair(base, files=FILES)
    good = apply(base, plan, rows)
    assert good.cfg and not good.patch_diagnostics
    if failure == "lost_effect":
        rows[1]["operations"].clear()
    elif failure == "new_effect":
        rows[1]["operations"].append(op("publish", "deliver", [{"result": "response"}], [], 1))
    elif failure == "reordered_effect":
        rows[1]["operations"].reverse()
    elif failure == "lost_constraint":
        del action["constraints"]
    elif failure == "changed_evidence":
        action["source"] = span(3)
    elif failure == "lost_key":
        rows[0]["source_kind"] = "normal"
        rows[0]["operations"][0] = op("method", "value", [{"literal": "default"}], ["method"], 1)
    elif failure == "new_key":
        rows[0]["operations"][0]["inputs"].append({"context_key": "another_file"})
    elif failure == "repeated_key":
        rows[2]["operations"][0]["inputs"].append({"context_key": "method"})
    elif failure == "branch":
        rows[0]["exit"] = {"kind": "branch", "conditions": [{"result": "method"}], "source": span(1),
                           "arms": [{"target": "work.call", "condition": "true"}, {"target": "work.files", "condition": "false"}]}
    else:
        rows[2]["exit"]["target"] = "work"
    rejected = apply(base, plan, rows)
    assert rejected.cfg is None and rejected.facts == raw
    assert rejected.patch_diagnostics[0]["code"] == "cfg_region_boundary"


def test_shape_scope_can_fix_an_independent_required_role_inside_the_same_block():
    raw = facts()
    save = raw["blocks"][0]["operations"][1]
    save["opcode"] = "save_to_disk"
    base = assemble_graph_facts(raw, files=FILES)
    plan = plan_graph_repair(base, files=FILES)
    slot, = plan["slots"].values()
    assert "save" in slot["editable_action_refs"]
    assert {g["code"] for g in plan["gaps"]} >= {"source_action_role", "acquisition_shape"}
    rows = split(raw["blocks"][0])
    rows[1]["operations"][1]["role"] = "write"
    revised = apply(base, plan, rows)
    assert revised.cfg is not None and not revised.patch_diagnostics


def test_a_finding_expands_only_its_own_actions_and_source():
    raw = facts()
    finding = {"id": "F001", "domain": "cfg", "required_graph_edit": "action_inventory",
               "target_ids": ["stage:graph/blocks/work/operations/save"], "source_refs": [span(2)]}
    base = assemble_graph_facts(raw, files=FILES)
    plan = plan_graph_repair(base, files=FILES, findings=[finding])
    rows = split(raw["blocks"][0])
    rows[1]["operations"][1]["ref"] = "corrected_save"
    assert apply(base, plan, rows).cfg is not None
    rows[1]["operations"][0] = op("invoke", "value", [{"literal": None}], ["response"], 1)
    assert apply(base, plan, rows).patch_diagnostics[0]["code"] == "cfg_region_boundary"
    rows = split(raw["blocks"][0])
    rows[3]["operations"].append(op("send", "deliver", [{"result": "content"}], [], 3))
    assert apply(base, plan, rows).patch_diagnostics[0]["code"] == "cfg_region_boundary"


def test_shared_request_gets_prior_patch_rejections_and_can_close_them_once():
    raw = facts()
    strategy = GraphFactsCorrection(FILES)
    correction = strategy._plan(raw)["plan"]
    slot, = correction["slots"]
    rows = split(raw["blocks"][0])
    response = {"plan_sha256": correction["plan_sha256"],
                "updates": [{"slot_id": slot, "value": rows}, {"slot_id": slot, "value": rows}]}
    merged = strategy.merge(raw, response)
    with pytest.raises(StructuralValidationError) as error:
        validate_graph(FACTS, merged, {"files": FILES, "graph_facts_strategy": strategy})
    codes = [d["code"] for d in error.value.diagnostics]
    assert codes.count("cfg_slot_conflict") == 2
    assert "acquisition_shape" in codes and "context_acquisition_only" in codes

    evidence = admission_material()["errors"]["graph"]["evidence"]
    material = evidence["material"]
    terminal = material["validation"]
    terminal.update(candidate_sha256=canonical_sha256(merged), response_sha256=canonical_sha256(response),
                    diagnostics=error.value.diagnostics)
    material.update(candidate_source="candidate", candidate=merged, response=response)
    material["attempts"][-1].update(validation=terminal, validation_sha256=canonical_sha256(terminal))
    evidence.update(source_sha256=canonical_sha256(FILES), material_sha256=canonical_sha256(material))
    shared = repair_input(files=FILES, previous=merged, accepted=False, findings=[], failure_evidence=evidence)
    rejections = shared["plan"]["base"]["patch_diagnostics"]
    assert [d["path"] for d in rejections] == ["/updates/0", "/updates/1"]
    prompt = shared["plan"]
    updated = {"plan_sha256": prompt["plan_sha256"], "updates": [{"slot_id": slot, "value": rows}]}
    final = validate_graph(UPDATES, updated, {"files": FILES, "graph_repair": shared})
    assert final["cfg"] and not final["assembly"]["patch_diagnostics"]
