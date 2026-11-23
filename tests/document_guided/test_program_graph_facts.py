"""Program assembly and targeted CFG repair, using only injected facts."""

from copy import deepcopy

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.graph_facts import assemble_graph_facts, from_accepted_cfg
from skillflow.document_guided.graph_slots import apply_graph_updates, plan_graph_repair
from skillflow.graph.extraction.compiler import compile_candidate


FILES = {"skill/SKILL.md": "Read a value.\nIf missing, read the clock. Always publish the value.\nReturn the result.\n"}


def span(line=1):
    return {"file": "skill/SKILL.md", "start_line": line, "end_line": line}


def facts():
    return {"entry": "start", "blocks": [
        {"ref": "start", "source_kind": "context", "operations": [
            {"ref": "collect", "opcode": "derive", "role": "read", "inputs": [{"context_key": "request"}],
             "outputs": ["value"], "source": span()},
        ], "exit": {"kind": "jump", "target": "done", "source": span(2)}},
        {"ref": "done", "source_kind": "normal", "operations": [],
         "exit": {"kind": "return", "values": [{"result": "value"}, {"literal": None}], "source": span(3)}},
    ]}


def update(base, plan, *rows):
    return apply_graph_updates(base, plan, {"plan_sha256": plan["plan_sha256"],
        "updates": [{"slot_id": slot_id, "value": value} for slot_id, value in rows]}, files=FILES)


def test_program_lowers_facts_and_adds_structural_fields():
    assembled = assemble_graph_facts(facts(), files=FILES)
    assert assembled.cfg is not None
    assert not assembled.slots and not assembled.gaps
    graph = assembled.cfg
    assert graph["entry_block_id"] == "block_001" and graph["declared_context_keys"] == ["request"]
    assert graph["edges"] == [{"source_block_id": "block_001", "target_block_id": "block_002",
                               "condition_text": None}]
    first = graph["blocks"]["block_001"]
    assert first["block_name"] == "start"
    assert [row["opcode"] for row in first["instructions"]] == ["derive", "dispatch"]
    action = first["instructions"][0]
    assert graph["blocks"]["block_002"]["instructions"][-1]["inputs"][1]["literal_value"] is None
    assert action["metadata"]["script_content"] == "Read a value.\n"
    assert action["draft_instruction_id"] == "/blocks/start/operations/collect"
    assert compile_candidate(assembled.candidate).cfg.to_json() == compile_candidate(
        assembled.candidate, canonical_ids=assembled.id_map).cfg.to_json()


def test_reviewed_edge_ordinal_binds_exact_original_arm_after_legacy_reordering():
    raw = facts()
    raw["blocks"][0]["exit"] = {"kind": "branch", "source": span(2),
        "conditions": [{"result": "value"}], "arms": [
            {"target": "done", "condition": "enabled"}, {"target": "done", "condition": "disabled"}]}
    compiled = assemble_graph_facts(raw, files=FILES).cfg
    compiled["edges"].reverse()
    base = from_accepted_cfg(compiled, files=FILES)
    assert base.cfg["edges"][0]["condition_text"] == "disabled"
    plan = plan_graph_repair(base, files=FILES, findings=[
        {"domain": "cfg", "target_ids": ["cfg:/edges/0"], "source_refs": [span(2)]}])
    slot, = plan["slots"].values()
    assert slot["old_value"]["condition"] == "disabled"
    revised = update(base, plan, (slot["slot_id"], {**slot["old_value"], "condition": "not enabled"}))
    assert {edge["condition_text"] for edge in revised.cfg["edges"]} == {"enabled", "not enabled"}


def test_missing_guard_one_slot_does_not_default_or_reauthor_other_facts():
    raw = facts()
    raw["blocks"][0]["exit"] = {"kind": "branch", "arms": [{"target": "done", "condition": "if enabled"}],
                                "source": span(2)}
    draft = assemble_graph_facts(raw, files=FILES)
    assert draft.cfg is None
    slot, = draft.slots.values()
    assert slot["path"] == ["blocks", 0, "exit", "conditions"] and not slot["present"]
    plan = plan_graph_repair(draft, files=FILES)
    assert plan["context"][0]["operations"][0]["outputs"] == ["value"]
    revised = update(draft, plan, (slot["slot_id"], [{"result": "value"}]))
    assert revised.cfg is not None
    assert revised.facts["blocks"][1] == raw["blocks"][1]
    assert revised.facts["blocks"][0]["operations"] == raw["blocks"][0]["operations"]
    assert revised.cfg["blocks"]["block_001"]["instructions"][-1]["inputs"][0]["identifier"] == "result_001"
    assert draft.facts == raw


def test_absent_return_value_is_not_an_explicit_void_return():
    raw = facts()
    del raw["blocks"][1]["exit"]["values"]
    draft = assemble_graph_facts(raw, files=FILES)
    slot, = draft.slots.values()
    assert draft.cfg is None and slot["path"][-1] == "values"
    corrected = update(draft, plan_graph_repair(draft, files=FILES), (slot["slot_id"], []))
    assert corrected.cfg["blocks"]["block_002"]["instructions"][-1]["inputs"] == []


def test_one_bad_patch_record_does_not_erase_a_valid_independent_edit():
    raw = facts()
    del raw["blocks"][0]["operations"][0]["inputs"]
    del raw["blocks"][1]["exit"]["values"]
    before = assemble_graph_facts(raw, files=FILES)
    plan = plan_graph_repair(before, files=FILES)
    slots = {slot["path"][-1]: slot["slot_id"] for slot in plan["slots"].values()}
    revised = update(before, plan, (slots["inputs"], [{"context_key": "name"}]),
                     ("not-authorized", []), (slots["values"], "not-a-value-array"))
    assert revised.cfg is None
    assert revised.facts["blocks"][0]["operations"][0]["inputs"] == [{"context_key": "name"}]
    assert [row["code"] for row in revised.patch_diagnostics] == ["cfg_slot_scope"]
    assert list(revised.slots) == [slots["values"]]


def test_duplicate_slot_records_are_quarantined_together():
    raw = facts()
    del raw["blocks"][1]["exit"]["values"]
    before = assemble_graph_facts(raw, files=FILES)
    plan = plan_graph_repair(before, files=FILES)
    slot, = plan["slots"]
    revised = update(before, plan, (slot, []), (slot, [{"result": "value"}]))
    assert revised.cfg is None and revised.facts == before.facts
    assert [row["code"] for row in revised.patch_diagnostics] == ["cfg_slot_conflict", "cfg_slot_conflict"]


@pytest.mark.parametrize("invalid_value", [
    {"result": "value", "literal": None}, {"result": "unbound"}, {"context_key": ""},
])
def test_result_and_operand_errors_are_single_slots(invalid_value):
    raw = facts()
    raw["blocks"][1]["exit"]["values"] = [invalid_value]
    draft = assemble_graph_facts(raw, files=FILES)
    slot, = draft.slots.values()
    assert draft.cfg is None and slot["path"] == ["blocks", 1, "exit", "values", 0]
    fixed = update(draft, plan_graph_repair(draft, files=FILES), (slot["slot_id"], {"result": "value"}))
    assert fixed.cfg is not None


def test_origins_and_scope_are_checked_no_matter_what_the_reply_claims():
    base = assemble_graph_facts(facts(), files=FILES)
    with pytest.raises(ValueError, match="source differs"):
        plan_graph_repair(base, files={"skill/SKILL.md": "Replacement source.\n"})
    plan = plan_graph_repair(base, files=FILES)
    with pytest.raises(StructuralValidationError, match="belongs to another"):
        apply_graph_updates(base, plan, {"plan_sha256": "0" * 64, "updates": []}, files=FILES)
    plan["mode"] = "slots"
    with pytest.raises(ValueError, match="differs from its bound"):
        update(base, plan)


def _revision():
    base = assemble_graph_facts(facts(), files=FILES)
    base = from_accepted_cfg(base.cfg, files=FILES)
    finding = {"id": "F001", "domain": "cfg", "target_ids": ["cfg:/blocks/block_001"], "source_refs": [span(2)]}
    plan = plan_graph_repair(base, files=FILES, findings=[finding])
    slot, = plan["slots"].values()
    assert slot["kind"] == "region"
    return base, plan, slot


def _split_region(base):
    root = deepcopy(base.facts["blocks"][0])
    ref = root["ref"]
    root["exit"] = {"kind": "branch", "source": span(2), "conditions": [{"result": "result_001"}],
        "arms": [{"target": f"{ref}.selected", "condition": "true"},
                 {"target": f"{ref}.excluded", "condition": "false"}]}

    def jump(name, target):
        return {"ref": name, "source_kind": "normal", "operations": [],
                "exit": {"kind": "jump", "target": target, "source": span(2)}}

    return [root, jump(f"{ref}.selected", f"{ref}.join"),
            jump(f"{ref}.excluded", f"{ref}.join"), jump(f"{ref}.join", "block_002")]


def test_region_control_split_retains_outside_canonical_ids_and_prior_findings():
    base, plan, slot = _revision()
    repaired = update(base, plan, (slot["slot_id"], _split_region(base)))
    assert repaired.cfg is not None
    assert repaired.cfg["blocks"]["block_002"] == base.cfg["blocks"]["block_002"]
    assert repaired.cfg["blocks"]["block_001"]["instructions"][0] == base.cfg["blocks"]["block_001"]["instructions"][0]
    assert repaired.id_map["blocks"]["block_001.selected"] == "block_003"
    assert len(repaired.cfg["edges"]) == 5
    assert plan["remaining_findings"][0]["id"] == "F001"


@pytest.mark.parametrize("bad_outputs", ["not-an-array", [], ["fresh_unrelated_definition"]])
def test_bad_field_against_accepted_cfg_rolls_back_without_losing_independent_edit(bad_outputs):
    base = from_accepted_cfg(assemble_graph_facts(facts(), files=FILES).cfg, files=FILES)
    findings = [{"id": "F001", "domain": "cfg", "target_ids": ["cfg:/blocks/block_001/instructions/0/outputs"],
                 "source_refs": [span(1)]},
                {"id": "F002", "domain": "cfg", "target_ids": ["cfg:/blocks/block_002/instructions/0/inputs/1"],
                 "source_refs": [span(3)]}]
    plan = plan_graph_repair(base, files=FILES, findings=findings)
    slots = {record["finding_ids"][0]: slot for slot, record in plan["slots"].items()}
    repaired = update(base, plan, (slots["F001"], bad_outputs), (slots["F002"], {"literal": True}))
    assert repaired.cfg is not None
    assert repaired.cfg["blocks"]["block_001"] == base.cfg["blocks"]["block_001"]
    assert repaired.cfg["blocks"]["block_002"]["instructions"][0]["inputs"][1]["literal_value"] is True
    assert repaired.patch_diagnostics[0]["code"] == "cfg_slot_rejected"
    assert repaired.patch_diagnostics[0]["causes"]


@pytest.mark.parametrize(("variant", "reason"), [
    ("outside", "outgoing control boundary"),
    ("effect", "preserve the existing actions"),
    ("repeat", "repeated visits"),
])
def test_region_cannot_change_outside_ports_add_unproven_actions_or_repeat_an_effect(variant, reason):
    base, plan, slot = _revision()
    rows = _split_region(base)
    if variant == "outside":
        rows[-1]["exit"]["target"] = "unapproved"
    elif variant == "effect":
        rows[1]["operations"] = [{"ref": "inserted", "opcode": "might_write", "inputs": [],
                                  "outputs": [], "source": span(2)}]
    else:
        rows[-1]["exit"]["target"] = rows[0]["ref"]
    revised = update(base, plan, (slot["slot_id"], rows))
    assert revised.cfg == base.cfg
    assert revised.patch_diagnostics[0]["code"] == "cfg_region_boundary"
    assert reason in revised.patch_diagnostics[0]["message"]


def test_ordered_source_actions_are_bound_to_their_ir_and_validated_individually():
    raw = facts()
    action = raw["blocks"][0]["operations"][0]
    action["source_actions"] = [{"ref": "read", "kind": "acquire", "role": "read", "source": span()},
                                {"ref": "log", "kind": "console", "role": "deliver", "source": span(2)}]
    result = assemble_graph_facts(raw, files=FILES)
    ir = result.cfg["blocks"]["block_001"]["instructions"][0]
    assert ir["metadata"]["source_actions"] == action["source_actions"]
    assert from_accepted_cfg(result.cfg, files=FILES).cfg == result.cfg
    action["source_actions"][1].update(ref="read", source=span(90))
    rejected = assemble_graph_facts(raw, files=FILES)
    assert {gap["code"] for gap in rejected.gaps} == {"source_action_span", "source_action_ref"}
    assert all(gap.get("slot_id") for gap in rejected.gaps)
    assert not rejected.cfg


def test_archived_graphs_and_receipts_preserve_original_bytes_and_identity():
    original = facts()
    del original["blocks"][0]["operations"][0]["role"]
    old = assemble_graph_facts(original, files=FILES, archived=True)
    assert old.to_receipt()["identity"] == "skillflow-graph-facts-v1"
    assert "source_actions" not in old.cfg["blocks"]["block_001"]["instructions"][0]["metadata"]
    assert from_accepted_cfg(old.cfg, files=FILES).cfg == old.cfg
    new = assemble_graph_facts(facts(), files=FILES)
    assert new.cfg["blocks"]["block_001"]["instructions"][0]["metadata"]["source_actions"] == [
        {"ref": "collect", "kind": "derive", "role": "read", "source": span()}]


def test_free_text_roles_are_explicit_fixable_and_never_guessed_from_names():
    from skillflow.document_guided.graph_facts import source_action_role

    raw = facts()
    op = raw["blocks"][0]["operations"][0]
    op["opcode"] = "recall_and_readjust"
    del op["role"]
    assert source_action_role({"kind": op["opcode"]}) is None
    rejected = assemble_graph_facts(raw, files=FILES)
    slot, = rejected.slots.values()
    assert slot["path"] == ["blocks", 0, "operations", 0, "role"] and not slot["present"]
    corrected = update(rejected, plan_graph_repair(rejected, files=FILES), (slot["slot_id"], "read"))
    assert corrected.cfg["blocks"]["block_001"]["instructions"][0]["metadata"]["source_actions"][0]["role"] == "read"
    op["opcode"] = "call"
    graph = assemble_graph_facts(raw, files=FILES).cfg
    assert graph["blocks"]["block_001"]["instructions"][0]["metadata"]["source_actions"][0]["role"] == "call"
    op["source_actions"] = [{"ref": "result", "kind": "value", "source": span()}]
    assert any(gap["path"].endswith("/source_actions") for gap in assemble_graph_facts(raw, files=FILES).gaps)
    op["source_actions"] = [{"ref": "send", "kind": "call", "role": "other", "source": span()}]
    assert any(gap["path"].endswith("/source_actions/0/role") for gap in assemble_graph_facts(raw, files=FILES).gaps)


def test_all_free_text_roles_are_diagnosed_even_beside_missing_schema_fields():
    raw = facts()
    op = raw["blocks"][0]["operations"][0]
    del op["role"], op["outputs"]
    op["source_actions"] = [{"ref": ref, "kind": kind, "source": span()} for ref, kind in
                            (("one", "fetchApi"), ("two", "projectResponse"))]
    gaps = assemble_graph_facts(raw, files=FILES).gaps
    assert {row["path"] for row in gaps} == {
        "/blocks/0/operations/0/source_actions/0/role", "/blocks/0/operations/0/source_actions/1/role",
        "/blocks/0/operations/0/outputs"}
    assert all(row.get("slot_id") for row in gaps)


def test_review_can_correct_one_action_field_without_reauthoring_its_siblings():
    base = from_accepted_cfg(assemble_graph_facts(facts(), files=FILES).cfg, files=FILES)
    target = "cfg:/blocks/block_001/instructions/0/metadata/source_actions/0/kind"
    plan = plan_graph_repair(base, files=FILES, findings=[{"id": "F001", "domain": "cfg",
        "required_graph_edit": "field", "target_ids": [target], "source_refs": [span()]}])
    slot, = plan["slots"].values()
    revised = update(base, plan, (slot["slot_id"], "read"))
    assert not revised.patch_diagnostics
    expected = deepcopy(base.cfg)
    expected["blocks"]["block_001"]["instructions"][0]["metadata"]["source_actions"][0]["kind"] = "read"
    assert revised.cfg == expected


def _conditional_action_region():
    raw = facts()
    raw["blocks"][1]["exit"]["constraints"] = ["Return the original value."]
    ops = raw["blocks"][1]["operations"]
    ops.extend({"ref": name, "opcode": name, "role": role, "inputs": [{"result": "value"}], "outputs": [], "source": span(2)}
               for name, role in (("clock_if_missing", "read"), ("publish", "deliver")))
    base = from_accepted_cfg(assemble_graph_facts(raw, files=FILES).cfg, files=FILES)
    finding = {"id": "F002", "domain": "cfg", "required_graph_edit": "action_inventory",
               "target_ids": ["cfg:/blocks/block_002/instructions/0"], "source_refs": [span(2)]}
    plan = plan_graph_repair(base, findings=[finding], files=FILES)
    slot, = plan["slots"].values()
    old = deepcopy(slot["old_value"])
    root = old["ref"]
    guard = {"kind": "branch", "source": span(2), "conditions": [{"result": "result_001"}],
             "arms": [{"target": root + ".clock", "condition": "missing"},
                      {"target": root + ".join", "condition": "present"}]}
    rows = [{**old, "exit": guard, "operations": []},
            {"ref": root + ".clock", "source_kind": "normal", "operations": [
                {"ref": "read_clock", "opcode": "acquire_clock", "role": "read", "inputs": [], "outputs": [], "source": span(2)}],
             "exit": {"kind": "jump", "target": root + ".join", "source": span(2)}},
            {"ref": root + ".join", "source_kind": "normal", "operations": [old["operations"][1]],
             "exit": old["exit"]}]
    return base, plan, slot, rows


def test_source_bound_action_edit_adds_conditional_site_and_preserves_sibling_identity():
    base, plan, slot, rows = _conditional_action_region()
    revised = update(base, plan, (slot["slot_id"], rows))
    assert not revised.patch_diagnostics, revised.patch_diagnostics
    blocks = revised.cfg["blocks"]
    clock = blocks[revised.id_map["blocks"]["block_002.clock"]]
    assert clock["instructions"][0]["metadata"]["source_actions"][0]["kind"] == "acquire_clock"
    assert blocks["block_001"] == base.cfg["blocks"]["block_001"]
    join = blocks[revised.id_map["blocks"]["block_002.join"]]
    assert join["instructions"] == base.cfg["blocks"]["block_002"]["instructions"][1:]
    assert [e["condition_text"] for e in revised.cfg["edges"] if e["source_block_id"] == "block_002"] == ["missing", "present"]


def test_source_bound_action_edit_can_introduce_a_member_loop_before_an_unchanged_consumer():
    files = {"skill/SKILL.md": "Read a collection.\nVisit each member and publish the result.\nReturn the collection.\n"}
    raw = facts()
    raw["blocks"][1]["operations"] = [{"ref": name, "opcode": name, "role": role, "inputs": [{"result": "value"}],
                                       "outputs": [], "source": span(2)} for name, role in (("map_all", "value"), ("publish", "deliver"))]
    base = from_accepted_cfg(assemble_graph_facts(raw, files=files).cfg, files=files)
    finding = {"id": "F001", "domain": "cfg", "required_graph_edit": "action_inventory",
               "target_ids": ["cfg:/blocks/block_002/instructions/0"], "source_refs": [span(2)]}
    plan = plan_graph_repair(base, findings=[finding], files=files)
    slot, = plan["slots"].values()
    old, root = slot["old_value"], slot["target"]
    iterating = {"kind": "branch", "conditions": [{"result": "result_001"}], "source": span(2),
                 "arms": [{"target": root + ".member", "condition": "has next member"},
                          {"target": root + ".join", "condition": "exhausted"}]}
    member = {"ref": "current", "opcode": "current_member", "role": "value", "inputs": [{"result": "result_001"}],
              "outputs": ["member_value"], "source": span(2)}
    body = {"ref": "visit", "opcode": "visit", "role": "other", "inputs": [{"result": "member_value"}], "outputs": [], "source": span(2)}
    region = [{**old, "operations": [], "exit": iterating},
              {"ref": root + ".member", "source_kind": "normal", "operations": [member, body],
               "exit": {"kind": "jump", "target": root, "source": span(2)}},
              {"ref": root + ".join", "source_kind": "normal", "operations": [old["operations"][1]], "exit": old["exit"]}]
    result = apply_graph_updates(base, plan, {"plan_sha256": plan["plan_sha256"],
                                 "updates": [{"slot_id": slot["slot_id"], "value": region}]}, files=files)
    assert not result.patch_diagnostics, result.patch_diagnostics
    member_id = result.id_map["blocks"][root + ".member"]
    member_ir, consume, _ = result.cfg["blocks"][member_id]["instructions"]
    assert consume["inputs"][0]["identifier"] == member_ir["outputs"][0]["identifier"]
    assert any(e["source_block_id"] == member_id and e["target_block_id"] == root for e in result.cfg["edges"])


@pytest.mark.parametrize("damage", ["unanchored", "skip_sibling", "change_sibling", "repeat_sibling", "outside"])
def test_action_edit_rejects_effects_outside_the_finding(damage):
    base, plan, slot, rows = _conditional_action_region()
    if damage == "unanchored":
        rows[1]["operations"][0]["source"] = span(1)
    elif damage == "skip_sibling":
        rows[1]["exit"] = rows[2]["exit"]
    elif damage == "change_sibling":
        rows[2]["operations"][0]["opcode"] = "different_publish"
    elif damage == "repeat_sibling":
        rows[2]["exit"] = {"kind": "jump", "target": rows[2]["ref"], "source": span(2)}
    else:
        rows[1]["exit"]["target"] = "block_001"
    rejected = update(base, plan, (slot["slot_id"], rows))
    assert rejected.cfg == base.cfg
    assert rejected.patch_diagnostics[0]["code"] == "cfg_region_boundary"
