from copy import deepcopy

import pytest

from skillflow.document_guided.entry_occurrences import callable_signature_ports
from skillflow.document_guided.graph_facts import assemble_graph_facts, from_accepted_cfg
from skillflow.document_guided.graph_slots import apply_graph_updates, plan_graph_repair
from skillflow.graph.ir.basic_block import BasicBlock


FILE = "skill/entry.ts"
FILES = {FILE: "export function first(range?: string, options?: Options) { return lookup(range, options); }\n"
               "export function second(range?: string) { return lookup(range); }\n"
               "export function router(packet: Event) { return packet.kind ? first(packet.range) : second(packet.range); }\n"
               "const env = readEnv();\nconst settings = readFile();\n"}


def span(line, end=None):
    return {"file": FILE, "start_line": line, "end_line": end or line}


def receive(name, source, keys, labels):
    return {"ref": name, "source_kind": "context", "operations": [
        {"ref": "take", "opcode": "receive", "inputs": [{"context_key": k} for k in keys],
         "outputs": labels, "source": source}],
        "exit": {"kind": "return", "values": [{"result": label} for label in labels], "source": source}}


def test_same_invocation_is_one_receive_and_distinct_invocations_get_distinct_keys():
    left = receive("left", span(1), ["range", "options"], ["left.range", "left.options"])
    right = receive("right", span(2), ["range"], ["right.range"])
    assembly = assemble_graph_facts({"entry": "left", "blocks": [left, right]}, files=FILES)
    assert assembly.cfg, assembly.gaps
    graph = assembly.cfg
    a, b = [block["instructions"][0] for block in graph["blocks"].values()]
    assert a["inputs"][0]["identifier"] != b["inputs"][0]["identifier"]
    assert a["inputs"][1]["identifier"] == "options"
    assert a["metadata"]["optional_context_inputs"] == [0, 1]
    assert b["metadata"]["optional_context_inputs"] == [0]
    assert {p["parameter"] for p in callable_signature_ports(a, FILES)} == {"range", "options"}
    assert from_accepted_cfg(graph, files=FILES).cfg == graph
    old = assemble_graph_facts(assembly.facts, files=FILES, check_occurrences=False)
    assert old.cfg and a["inputs"][0]["identifier"] not in old.cfg["declared_context_keys"]
    assert from_accepted_cfg(old.cfg, files=FILES, check_occurrences=False).cfg == old.cfg


def test_object_read_then_two_function_uses_is_still_one_read():
    data = receive("route", span(3), ["packet"], ["selected", "range"])
    data["operations"][0]["source_actions"] = [
        {"ref": "read", "kind": "receive", "source": span(3)},
        {"ref": "project", "kind": "value", "source": span(3)}]
    data["exit"] = {"kind": "branch", "conditions": [{"result": "selected"}], "arms": [
        {"target": "first", "condition": "selected == first"},
        {"target": "second", "condition": "selected == second"}], "source": span(3)}
    def call(name):
        return {"ref": name, "source_kind": "normal", "operations": [
            {"ref": "call", "opcode": "call", "inputs": [{"result": "range"}],
             "outputs": [name + ".result"], "source": span(1, 2)}],
            "exit": {"kind": "return", "values": [{"result": name + ".result"}], "source": span(3)}}
    assembly = assemble_graph_facts({"entry": "route", "blocks": [data, call("first"), call("second")]}, files=FILES)
    assert assembly.cfg, assembly.gaps


def test_repair_obligations_do_not_cross_product_same_named_unused_formals():
    text = ("export function left(range?: string, format?: string) { return find(range); }\n"
            "export function right(range?: string, format?: string) { return query(range,format); }\n")
    source = {FILE: text}
    root = receive("ctx", span(1, 2), ["chosen", "range", "format"], ["chosen", "range", "format"])
    root["exit"] = {"kind": "branch", "source": span(1, 2), "conditions": [{"result": "chosen"}],
                    "arms": [{"target": n, "condition": "chosen == " + n} for n in ("left", "right")]}
    blocks = [root]
    for name, used, line in [("left", ["range"], 1), ("right", ["range", "format"], 2)]:
        blocks.append({"ref": name, "source_kind": "normal", "operations": [{
            "ref": "go", "opcode": "call", "inputs": [{"result": v} for v in used],
            "outputs": [], "source": span(line)}], "exit": {"kind": "return", "values": [], "source": span(line)}})
    base = assemble_graph_facts({"entry": "ctx", "blocks": blocks}, files=source)
    slot, = plan_graph_repair(base, files=source)["slots"].values()
    assert {s["name"]: s["parameters"] for s in slot["source_sites"]} == {
        "left": ["range"], "right": ["range", "format"]}


def test_cross_owner_qualified_operands_need_no_branch_to_detect_conflict():
    mixed = receive("mixed", span(1, 2), ["first.range", "second.range"], ["first.result", "second.result"])
    base = assemble_graph_facts({"entry": "mixed", "blocks": [mixed]}, files=FILES)
    assert not base.cfg and [g["code"] for g in base.gaps] == ["acquisition_occurrence"]
    plan = plan_graph_repair(base, files=FILES)
    region, = plan["slots"].values()
    assert region["kind"] == "occurrence_region"
    assert {s["name"] for s in region["source_sites"]} == {"first", "second"}
    attempted = apply_graph_updates(base, plan, {"plan_sha256": plan["plan_sha256"],
        "updates": [{"slot_id": region["slot_id"], "value": region["old_value"]}]}, files=FILES)
    assert not attempted.cfg
    assert "Missing sourced invocation parameter bindings" in attempted.patch_diagnostics[0]["message"]


def test_multiple_sourced_reads_identified_without_a_language_specific_declaration():
    data = receive("mixed", span(4, 5), ["environment", "settings"], ["env", "settings"])
    data["operations"][0]["opcode"] = "read"
    data["operations"][0]["source_actions"] = [
        {"ref": "env", "kind": "read", "source": span(4)}, {"ref": "file", "kind": "read", "source": span(5)}]
    result = assemble_graph_facts({"entry": "mixed", "blocks": [data]}, files=FILES)
    assert not result.cfg and result.gaps[0]["source_sites"] == [span(4), span(5)]


def test_individually_cited_formals_in_one_multiline_signature_remain_one_acquisition():
    path = "skill/entry.py"
    files = {path: "def run(\n  left,\n  right=None,\n):\n    return left, right\n"}
    def line(start, end):
        return {"file": path, "start_line": start, "end_line": end}
    block = receive("both", line(1, 4), ["left", "right"], ["left", "right"])
    block["operations"][0]["source_actions"] = [
        {"ref": "l", "kind": "receive", "source": line(2, 2)},
        {"ref": "r", "kind": "receive", "source": line(3, 3)}]
    base = assemble_graph_facts({"entry": "both", "blocks": [block]}, files=files)
    assert base.cfg, base.gaps
    ir = next(iter(base.cfg["blocks"].values()))["instructions"][0]
    assert [(p["parameter"], p["optional"], p["action_ref"]) for p in callable_signature_ports(ir, files)] == [
        ("left", False, "l"), ("right", True, "r")]


def test_typescript_typed_lists_and_string_defaults_keep_their_ports():
    files = {FILE: 'export function report(rows: string[], names: Map<K,V>, period = "30d") {\n  return run();\n}'}
    block = receive("both", span(1), ["rows", "names", "period"], ["rows", "names", "period"])
    base = assemble_graph_facts({"entry": "both", "blocks": [block]}, files=files)
    ir = next(iter(base.cfg["blocks"].values()))["instructions"][0]
    assert [p["optional"] for p in callable_signature_ports(ir, files)] == [False, False, True]


@pytest.mark.parametrize("fake", [True, ["not a row"], [{"source": {"foo": "wrong"}}]])
def test_bad_model_source_metadata_is_diagnosed_before_using_it_as_a_witness(fake):
    block = receive("left", span(1), ["range"], ["range"])
    block["operations"][0]["metadata"] = {"source_actions": fake}
    base = assemble_graph_facts({"entry": "left", "blocks": [block]}, files=FILES)
    assert base.cfg is None and any(g["code"] == "generated_metadata" for g in base.gaps)


def test_citing_one_wrong_signature_does_not_establish_a_global_parameter_bundle():
    calls = receive("mixed", span(2), ["range", "options", "runtime.argv"], ["range", "options", "argv"])
    result = assemble_graph_facts({"entry": "mixed", "blocks": [calls]}, files=FILES)
    assert not result.cfg and result.gaps[0]["code"] == "acquisition_occurrence"
    assert result.gaps[0]["source_sites"] == [dict(span(2), name="second", parameters=["range"])]


def test_narrowing_only_the_saved_ga4_source_cannot_repair_its_eighteen_ports(tmp_path):
    from .ga4_entry_occurrence_case import load_material, original_projection, signature
    saved, _, files = load_material(tmp_path)
    raw = original_projection(saved)
    raw["blocks"][0]["operations"][0]["source"] = signature("getPageViews")
    base = assemble_graph_facts(raw, files=files)
    gap, = [g for g in base.gaps if g["code"] == "acquisition_occurrence"]
    assert gap["path"] == "/blocks/0/operations/0/inputs"
    assert {"getPageViews", "getTrafficSources", "siteOverview"} <= {s["name"] for s in gap["source_sites"]}
    plan = plan_graph_repair(base, files=files)
    slot, = plan["slots"].values()
    repeated = apply_graph_updates(base, plan, {"plan_sha256": plan["plan_sha256"], "updates": [{
        "slot_id": slot["slot_id"], "value": slot["old_value"]}]}, files=files)
    assert repeated.cfg is None and repeated.patch_diagnostics and repeated.gaps == base.gaps


def test_occurrence_patch_retains_omitted_neighbor_at_its_original_index(tmp_path):
    from .ga4_entry_occurrence_case import load_material, occurrence_update, original_projection
    saved, _, files = load_material(tmp_path)
    raw = original_projection(saved)
    draft = assemble_graph_facts(raw, files=files)
    plan = plan_graph_repair(draft, files=files)
    slot, = plan["slots"].values()
    changed = [b for b in occurrence_update(raw) if b["ref"] != "getPageViews"]
    next(b for b in changed if b["ref"] == "public_entry")["operations"][0]["outputs"] = ["entry.dateRange"]
    fixed = apply_graph_updates(draft, plan, {"plan_sha256": plan["plan_sha256"], "updates": [
        {"slot_id": slot["slot_id"], "value": changed}]}, files=files)
    assert fixed.cfg, (fixed.gaps, fixed.patch_diagnostics)
    assert [b["ref"] for b in fixed.facts["blocks"]] == [b["ref"] for b in raw["blocks"]]
    original = next(b for b in raw["blocks"] if b["ref"] == "getPageViews")
    assert fixed.facts["blocks"][raw["blocks"].index(original)] == original


def test_joint_source_finding_opens_acquisition_and_actual_consumers_without_a_language_parser():
    from .test_program_graph_facts import FILES as markdown, facts
    base = assemble_graph_facts(facts(), files=markdown)
    assert base.cfg
    finding = {"id": "F1", "domain": "cfg", "required_graph_edit": "action_inventory",
               "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 3}],
               "target_ids": [f"cfg:/blocks/{b}/instructions/0" for b in base.cfg["blocks"]]}
    plan = plan_graph_repair(base, findings=[finding], files=markdown)
    slot, = plan["slots"].values()
    assert slot["kind"] == "occurrence_region" and slot["finding_ids"] == ["F1"]
    assert [b["ref"] for b in slot["old_value"]] == ["start", "done"]


@pytest.mark.parametrize("bad", [[0, 0], ["0"], True, [4], [-1], [{}]])
def test_optional_port_flags_are_program_derived_and_well_typed(bad):
    entry = receive("single", span(2), ["range"], ["range"])
    candidate = {"entry": "single", "blocks": [entry]}
    real = assemble_graph_facts(candidate, files=FILES)
    poisoned = deepcopy(candidate)
    poisoned["blocks"][0]["operations"][0]["metadata"] = {"optional_context_inputs": [0]}
    rejected = assemble_graph_facts(poisoned, files=FILES)
    assert not rejected.cfg and rejected.gaps[0]["code"] == "generated_metadata"
    block = deepcopy(next(iter(real.cfg["blocks"].values())))
    block["instructions"][0]["metadata"]["optional_context_inputs"] = bad
    with pytest.raises(ValueError, match="optional_context_inputs"):
        BasicBlock.model_validate(block)
