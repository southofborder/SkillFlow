"""Action alignment, local repairs and whole-instruction source review."""
from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.document_guided.fragment_revision import (
    merge_processing_revision, merge_sensitivity_revision, processing_scope, sensitivity_scope,
)
from skillflow.document_guided.fragments import assemble_fragments, fragment_correction_strategy, validate_fragment
from skillflow.document_guided.review_correction import ReviewCorrectionStrategy
from skillflow.document_guided.source_review import isolate_source_review, prepare_review_material, validate_source_review
from skillflow.propagation.contracts.references import cfg_instructions
from skillflow.propagation.contracts.task import task_source_files
from tests.document_guided.test_fragments import fixture
from tests.doe.input_review_helpers import source_review_response


REF = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}
CALL = ["segments", 0, "ops", 0]
EXTRA = ["segments", 0, "ops", 1]
OUT = ["output_bindings", 0]


def actions(*refs):
    return [{"ref": ref, "kind": ref, "source": deepcopy(REF)} for ref in refs]


def local_value(record):
    return {"op": "placeholder", "kind": "value", "inputs": [{"kind": "local", "name": "reply"}],
            "output": "sample", "reason": "The service callback selects a reply member under an unspecified policy.",
            "evidences": deepcopy(record["evidences"])}


def test_action_inventory_validates_coordinates_order_and_physical_refs():
    m, _, f = fixture()
    irs = cfg_instructions(m["cfg"])
    p = f["processing"]
    rec = p["ir_semantics"]["ir_call"]
    rec["segments"][0]["ops"].append(local_value(rec))
    irs["ir_call"].setdefault("metadata", {})["source_actions"] = actions("invoke", "callback")
    irs["ir_return"].setdefault("metadata", {})["source_actions"] = actions("exit")
    rec["action_bindings"] = {"invoke": [CALL, OUT], "callback": [EXTRA]}
    assert validate_fragment("processing", p, m) == p
    saved, _, _, mapping = assemble_fragments(p, f["task-correspondence"], f["sensitivity"], m)
    assert mapping["source_action_bindings"]["ir_return"]["bindings"] == {"exit": [["terminator"]]}
    assert mapping["source_action_bindings"]["ir_call"]["bindings"] == rec["action_bindings"]
    assert compile_flat_response(saved, m)[3] == mapping
    for bindings in ({"invoke": [CALL, OUT]}, {"invoke": [EXTRA], "callback": [CALL, OUT]},
                     {"invoke": [CALL, OUT], "callback": [EXTRA, CALL]}):
        rec["action_bindings"] = bindings
        with pytest.raises(StructuralValidationError, match="action_bindings"):
            validate_fragment("processing", p, m)
    del irs["ir_call"]["metadata"]["source_actions"]
    rec["source_actions"] = [{**row, "role": role} for row, role in zip(actions("invoke", "callback"), ("call", "other"))]
    rec["action_bindings"] = {"invoke": [CALL, OUT], "callback": [EXTRA]}
    assert validate_fragment("processing", p, m) == p
    rec["source_actions"][1]["source"]["end_line"] = 999999
    with pytest.raises(StructuralValidationError, match="physical span"):
        validate_fragment("processing", p, m)


def test_missing_action_can_insert_only_its_operations_and_retain_correct_call():
    m, _, f = fixture()
    p = f["processing"]
    rec = p["ir_semantics"]["ir_call"]
    cfg_instructions(m["cfg"])["ir_call"].setdefault("metadata", {})["source_actions"] = actions("invoke", "callback")
    rec["action_bindings"] = {"invoke": [CALL, OUT]}
    before = deepcopy(p)
    with pytest.raises(StructuralValidationError) as invalid:
        validate_fragment("processing", p, m)
    strategy = fragment_correction_strategy("processing")
    strategy.build_prompt("Preserve every source action.", p, invalid.value.diagnostics)
    assert not strategy.selected
    patch = {"fields": [{"path": "/ir_semantics/ir_call/action_bindings",
                         "value": {"invoke": [CALL, OUT], "callback": [EXTRA]}}],
             "insertions": [{"path": "/ir_semantics/ir_call/segments/0/ops", "index": 1, "values": [local_value(rec)]}]}
    corrected = strategy.merge(p, patch)
    assert validate_fragment("processing", corrected, m) == corrected
    assert p == before
    assert corrected["ir_semantics"]["ir_call"]["segments"][0]["ops"][0] == rec["segments"][0]["ops"][0]
    with pytest.raises(StructuralValidationError):
        strategy.merge(p, {"replacements": [{"record_id": "/ir_semantics/ir_call", "value": {}}]})
    broken = deepcopy(corrected)
    broken["ir_semantics"]["ir_call"]["segments"][0]["ops"][1]["op"] = "nonexistent"
    with pytest.raises(StructuralValidationError) as invalid:
        validate_fragment("processing", broken, m)
    strategy.build_prompt("Preserve every source action.", broken, invalid.value.diagnostics)
    assert strategy.merge(broken, {"fields": [{"path": "/ir_semantics/ir_call/segments/0/ops/1",
                                               "value": local_value(rec)}]}) == corrected


def test_local_revision_introduces_source_bound_location_only_for_actual_operation():
    m, _, f = fixture()
    prior = f["processing"]
    ir = "ir_call"
    scope = processing_scope(m["cfg"], m["cfg"], [{"target_ids": ["annotation:/ir_semantics/ir_call"]}], prior)
    fixed = deepcopy(prior["ir_semantics"][ir])
    fixed["segments"][0]["ops"][0]["location"] = "independent_service"
    location = {**prior["locations"]["service"], "name": "Second Service"}
    patch = {"instruction_id": ir, "modeled": fixed, "new_locations": {"independent_service": location}}
    merged = merge_processing_revision(prior, scope, {"coverage_slots": [patch]})
    assert merged["locations"] == {**prior["locations"], "independent_service": location}
    assert validate_fragment("processing", merged, m) == merged
    assert "independent_service" not in prior["locations"]
    for name in ("service", "unused"):
        with pytest.raises(StructuralValidationError):
            merge_processing_revision(prior, scope, {"coverage_slots": [{**patch, "new_locations": {name: location}}]})


def test_new_expression_is_bound_to_its_real_dispatch_operand():
    m, _, f = fixture()
    cfg = m["cfg"]
    block = cfg["blocks"]["sample"]
    terminal = block["instructions"].pop()
    guard = {**deepcopy(terminal), "id": "ir_guard", "opcode": "dispatch"}
    block["instructions"].append(guard)
    cfg["blocks"]["done"] = {**deepcopy(block), "block_id": "done", "block_name": "Done", "instructions": [terminal]}
    cfg["edges"] = [{"source_block_id": "sample", "target_block_id": "done"}]
    p = f["processing"]
    p["ir_semantics"]["ir_guard"] = record = deepcopy(p["ir_semantics"]["ir_return"])
    scope = processing_scope(cfg, cfg, [{"target_ids": ["annotation:/ir_semantics/ir_guard"]}], p)
    expr = {"target": {"instruction_id": "ir_guard", "side": "input", "index": 0},
            "expression": {"op": "literal", "value": True}, "evidences": deepcopy(record["evidences"])}
    patch = {"instruction_id": "ir_guard", "modeled": record, "new_expressions": [expr]}
    new = merge_processing_revision(p, scope, {"coverage_slots": [patch]})
    assert validate_fragment("processing", new, m) == new
    assert new["expressions"] == [expr]
    expr["target"]["instruction_id"] = "ir_call"
    with pytest.raises(StructuralValidationError):
        merge_processing_revision(p, scope, {"coverage_slots": [patch]})


def test_whole_instruction_review_is_required_locally_correctable_and_routed_to_processing():
    m, _, f = fixture()
    p = f["processing"]
    rec = p["ir_semantics"].pop("ir_return")
    p["processing_gaps"] = [{"instruction_id": "ir_return", "reason": "The callback return policy is absent.",
                             "control": True, "unmodeled": True, "evidences": rec["evidences"]}]
    wire, raw, compiled, mapping = assemble_fragments(p, f["task-correspondence"], f["sensitivity"], m)
    review = prepare_review_material(files=task_source_files(m["source"]), cfg=m["cfg"], task=m["task"],
        annotation=wire, raw_annotation=raw, compiled=compiled, mapping=mapping, generation="fragment-v1")
    expected, = review["processing_gap_inventory"]
    assert expected["target_id"] == "annotation:/processing_gaps/0"
    answer = source_review_response(review, [])
    gap, = answer.pop("gap_checks")
    isolation = isolate_source_review(answer, review)
    assert [d["code"] for d in isolation["validation"]["diagnostics"]] == ["processing_gap_review"]
    assert isolation["review"]["input_contract_checks"] and not isolation["validation"]["blocked_obligation_ids"]
    generic = {**gap, "reason": "The operation is opaque."}
    rejected = isolate_source_review({**answer, "gap_checks": [generic]}, review)
    assert rejected["review"]["gap_checks"] == [] and rejected["validation"]["diagnostics"]
    mixed = {**gap, "masked_boundary": "none", "cfg_action_missing": False}
    misplaced = isolate_source_review({**answer, "gap_checks": [mixed]}, review)
    assert any("Remove masked_boundary and cfg_action_missing" in d["message"]
               for d in misplaced["validation"]["diagnostics"])
    strategy = ReviewCorrectionStrategy(review, fragment_correction_strategy("review"))
    strategy.build_prompt("Full source.", answer, isolation["validation"]["diagnostics"])
    gap.update(disposition="decompose", supported_action="Retain the terminal return and localize the callback selection.")
    repaired = strategy.merge(answer, {"replacements": [], "insertions": [gap]})
    checked = validate_source_review(repaired, review)
    finding, = checked["findings"]
    assert finding["owner"] == "processing" and finding["target_ids"] == [expected["target_id"]]
    assert list(processing_scope(m["cfg"], m["cfg"], checked["findings"], p)["slots"]) == ["ir_return"]
    from skillflow.doe.input_contract_review import build_input_contract_review, checked_input_contract_review
    ann = {"task": m["task"], "wire_annotation": wire, "raw_annotation": raw,
           "compiled_annotation": compiled, "mapping": mapping}
    args = {"files": review["files"], "cfg": m["cfg"], "annotation": ann}
    receipt = build_input_contract_review(**args, review={"status":"complete", "review": checked,
            "availability": review["availability"]}, review_material=review)
    assert receipt["review_core"]["gap_checks"] == [gap]
    checked_input_contract_review(receipt, **args)


def test_73_missing_ingresses_survive_repeated_processing_revision_and_need_an_explicit_resolution():
    m, _, f = fixture()
    cfg, before = m["cfg"], f["processing"]
    primary = next(iter(cfg["blocks"].values()))["instructions"]
    rows = [deepcopy(primary[0]) for _ in range(73)]
    for i, row in enumerate(rows):
        row["id"] = f"ir_missing_{i}"
        row["outputs"][0]["identifier"] = f"missing_value_{i}"
    primary[-1:-1] = rows
    gaps = [{"instruction_id": row["id"], "missing_from": "processing", "missing_entry": "Service response",
             "reason": "The response boundary is absent from processing.",
             "evidences": deepcopy(before["ir_semantics"]["ir_call"]["evidences"])} for row in rows]
    prior = {"declarations": [], "entry_gaps": gaps}
    scope = sensitivity_scope(cfg, cfg, before, before, [], prior)
    assert not scope["slots"] and not scope["removed_instruction_ids"]
    assert merge_sensitivity_revision(prior, scope, {"slots": []}) == prior
    after = deepcopy(before)
    after["ir_semantics"][rows[0]["id"]] = deepcopy(before["ir_semantics"]["ir_call"])
    scope = sensitivity_scope(cfg, cfg, before, after, [], prior)
    owner, = scope["slots"]
    assert merge_sensitivity_revision(prior, scope, {"slots": [{"instruction_id": owner, "declarations": []}]})["entry_gaps"] == gaps
    entry, = scope["entry_catalogue"]
    patch = {"instruction_id": owner, "declarations": [], "resolved_entry_gaps": [{
        "gap_sha256": canonical_sha256(gaps[0]), "entry_id": entry,
        "reason": "The repaired Service call now exposes its response at this source instruction."}]}
    assert merge_sensitivity_revision(prior, scope, {"slots": [patch]})["entry_gaps"] == gaps[1:]
    patch["resolved_entry_gaps"][0]["entry_id"] = "unrelated_entry"
    with pytest.raises(StructuralValidationError):
        merge_sensitivity_revision(prior, scope, {"slots": [patch]})


def test_external_action_cannot_be_discharged_by_placeholder_or_output_and_edits_stay_local():
    m, _, f = fixture()
    prior = f["processing"]
    record = prior["ir_semantics"]["ir_call"]
    original_call = deepcopy(record["segments"][0]["ops"][0])
    instruction = cfg_instructions(m["cfg"])["ir_call"]
    instruction["metadata"]["source_actions"] = actions("call", "other")
    # The call is suppressed. The neighboring local effect needs no interface.
    candidate = {"op":"placeholder", "kind":"value", "inputs":original_call["inputs"], "output":"reply",
                 "reason":"A callback is claimed for the original response.", "evidences":record["evidences"]}
    log = {"op":"placeholder", "kind":"effect", "inputs":[], "reason":"The independent log backend is unspecified.",
           "evidences":record["evidences"]}
    record["segments"][0]["ops"] = [candidate, log]
    record["action_bindings"] = {"call":[CALL, OUT], "other":[EXTRA]}
    with pytest.raises(StructuralValidationError) as invalid:
        validate_fragment("processing", prior, m)
    diagnostics = invalid.value.diagnostics
    assert any(row["code"] == "source_action_role" for row in diagnostics)
    strategy = fragment_correction_strategy("processing")
    strategy.build_prompt("Check both actions.", prior, diagnostics)
    patch = {"fields":[{"path":"/ir_semantics/ir_call/segments/0/ops/0", "value":original_call}]}
    restored = strategy.merge(prior, patch)
    assert validate_fragment("processing", restored, m) == restored
    assert restored["ir_semantics"]["ir_call"]["segments"][0]["ops"][1] == log
    del restored["ir_semantics"]["ir_call"]["segments"][0]["ops"][0]["input_contract"]
    with pytest.raises(StructuralValidationError, match="contract"):
        validate_fragment("processing", restored, m)
    record["action_bindings"] = {"call":[OUT], "other":[CALL,EXTRA]}
    with pytest.raises(StructuralValidationError, match="real call"):
        validate_fragment("processing", prior, m)


def test_same_path_role_witness_respects_case_phases_and_member_scopes():
    from skillflow.document_guided.action_bindings import _role_errors, action_coordinates
    m, _, f = fixture()
    prior = f["processing"]
    ins = cfg_instructions(m["cfg"])["ir_call"]
    call = prior["ir_semantics"]["ir_call"]["segments"][0]
    unknown = {"ops":[{"op":"placeholder"}]}
    def case(phase, operations, disposition="return"):
        return {"phase":phase, "condition":"source guard", "disposition":disposition, "segments":[operations]}
    def errors(segments):
        rec = {"segments":segments}
        return _role_errors(rec, ins, prior, "request", "call", [p for p,_ in action_coordinates(rec)])
    cases = {"kind":"cases", "cases":[case("normal",call),case("normal",unknown)]}
    assert errors([cases])
    cases["cases"][1]["phase"] = "pre_request_error"
    assert not errors([cases])
    cases["cases"][1]["phase"] = "post_request_error"
    assert errors([cases])
    cases["cases"][1]["segments"] = [{"ops":[{"op":"deliver","target":"service"}]}]
    assert not errors([cases])
    def loop(body):
        return {"kind":"for_each","collection":{},"body":body}
    assert errors([loop([cases]),loop([unknown])])
    assert not errors([loop([cases])])


def test_wrong_cfg_role_and_masked_boundary_produce_both_editable_source_findings():
    m, _, f = fixture()
    prior = f["processing"]
    record = prior["ir_semantics"]["ir_call"]
    instruction = cfg_instructions(m["cfg"])["ir_call"]
    instruction["metadata"]["source_actions"] = actions("other")
    primary = deepcopy(record["segments"][0]["ops"][0])
    record["segments"][0]["ops"].append({"op":"placeholder","kind":"effect","inputs":[],
        "reason":"The fixture omits the state transition at this program location.","evidences":deepcopy(record["evidences"])})
    wire, raw, compiled, mapping = assemble_fragments(prior,f["task-correspondence"],f["sensitivity"],m)
    review = prepare_review_material(files=task_source_files(m["source"]),cfg=m["cfg"],task=m["task"],
        annotation=wire,raw_annotation=raw,compiled=compiled,mapping=mapping,generation="fragment-v1")
    item, = review["processing_gap_inventory"]
    assert item["kind"] == "placeholder" and item["cfg_roles"] == ["other"]
    answer = source_review_response(review, [])
    decision, = answer["gap_checks"]
    del decision["masked_boundary"]
    with pytest.raises(StructuralValidationError):
        validate_source_review(answer, review)
    decision.update(masked_boundary="write", cfg_action_missing=False)
    with pytest.raises(StructuralValidationError, match="repair"):
        validate_source_review(answer, review)
    decision.update(disposition="decompose", supported_action="Model the audit write to its actual storage target.")
    with pytest.raises(StructuralValidationError, match="CFG role"):
        validate_source_review(answer, review)
    decision["cfg_action_missing"] = True
    audited = validate_source_review(answer, review)
    first, second = audited["findings"]
    assert first["owner"] == "processing" and first["target_ids"] == [item["target_id"]]
    assert second["domain"] == "cfg" and second["required_graph_edit"] == "action_inventory"
    from skillflow.doe.input_contract_review import build_input_contract_review, checked_input_contract_review
    args = {"files": review["files"], "cfg": m["cfg"], "annotation":{"task":m["task"],"wire_annotation":wire,
            "raw_annotation":raw,"compiled_annotation":compiled,"mapping":mapping}}
    receipt = build_input_contract_review(**args, review={"status":"complete", "review":audited,
            "availability":review["availability"]}, review_material=review)
    checked_input_contract_review(receipt, **args)
    scope = processing_scope(m["cfg"],m["cfg"],audited["findings"],prior)
    slot = scope["slots"]["ir_call"]
    assert slot["source_rechecks"][0]["placeholder_operation"] == "/segments/0/ops/1"
    op = {"op":"write","target":"audit","input":{"kind":"local","name":"reply"}}
    edit = {"instruction_id":"ir_call", "operations":[{"path":"/segments/0/ops/1","value":op}],
        "new_locations":{"audit":{"kind":"storage","name":"audit","evidences":deepcopy(record["evidences"])}}}
    result = merge_processing_revision(prior,scope,{"coverage_slots":[edit]})
    assert validate_fragment("processing",result,m) == result
    assert result["ir_semantics"]["ir_call"]["segments"][0]["ops"] == [primary,op]
    edit["operations"][0]["path"] = "/segments/0/ops/0"
    with pytest.raises(StructuralValidationError, match="only a listed"):
        merge_processing_revision(prior,scope,{"coverage_slots":[edit]})


def test_exhausted_action_binding_correction_recovers_only_one_source_matched_alignment():
    from skillflow.document_guided.fragments import salvage_fragment
    m, _, f = fixture()
    p = f["processing"]
    rec = p["ir_semantics"]["ir_call"]
    ins = cfg_instructions(m["cfg"])["ir_call"]
    ins["metadata"]["source_actions"] = actions("call","value")
    rec["segments"][0]["ops"].append(local_value(rec))
    issued = deepcopy(p)
    retained, gaps = salvage_fragment("processing", p, m)
    assert not gaps and p == issued
    assert retained["ir_semantics"]["ir_call"]["action_bindings"] == {"call":[CALL,OUT],"value":[EXTRA]}
    assert retained["ir_semantics"]["ir_call"]["segments"] == rec["segments"]
    assert validate_fragment("processing",retained,m) == retained
    # Three same-source effects cannot be uniquely assigned to two named actions.
    first, second = actions("other","other")
    first["ref"], second["ref"] = "log_once", "audit_once"
    ins["metadata"]["source_actions"] = [first, second]
    rec["segments"][0]["ops"] = [{"op":"placeholder", "kind":"effect","inputs":[],
        "reason":"The logging callback behavior is absent.", "evidences":rec["evidences"]} for _ in range(3)]
    rec["output_bindings"] = []
    retained, gaps = salvage_fragment("processing",p,m)
    assert "ir_call" not in retained["ir_semantics"]
    assert retained["ir_semantics"]["ir_return"] == p["ir_semantics"]["ir_return"]
    gap, = gaps
    why = next(d for d in gap["validation_errors"] if d["code"] == "source_action_unresolved")
    assert "log_once" in why["message"] and "audit_once" in why["message"] and "/segments/0/ops/2" in why["message"]


def test_raw_annotation_only_reviews_actual_nested_placeholder_and_round_trips_its_physical_target():
    from skillflow.doe.input_contract_review import build_input_contract_review, checked_input_contract_review
    m, _, f = fixture()
    p = f["processing"]
    record = p["ir_semantics"]["ir_call"]
    record["segments"][0]["ops"].append(local_value(record))
    wire, raw, compiled, mapping = assemble_fragments(p, f["task-correspondence"], f["sensitivity"], m)
    files = task_source_files(m["source"])
    review = prepare_review_material(files=files, cfg=m["cfg"], task=m["task"], raw_annotation=raw,
        compiled=compiled, mapping=mapping, generation="fragment-v1")
    subject, = review["processing_gap_inventory"]
    path = subject["target_id"]
    assert path.startswith("annotation:/ir_semantics/ir_call/events/") and "/atomic_ops/" in path
    checked = validate_source_review(source_review_response(review, []), review)
    args = {"files":files, "cfg":m["cfg"], "annotation":{"task":m["task"],"wire_annotation":wire,
            "raw_annotation":raw,"compiled_annotation":compiled,"mapping":mapping}}
    receipt = build_input_contract_review(**args,review={"status":"complete","review":checked,
        "availability":review["availability"]},review_material=review)
    assert receipt["review_core"]["placeholder_review_view"] == "raw_annotation"
    checked_input_contract_review(receipt, **args)


def test_split_call_witness_preserves_exact_runtime_pair_and_action_scope():
    from skillflow.document_guided.action_bindings import verified_split_calls
    from skillflow.propagation.contracts.specs import RawIRSemantics, flatten_raw_spec
    from skillflow.propagation.contracts.uses import request_pairs
    m, _, f = fixture()
    p = f["processing"]
    rec = p["ir_semantics"]["ir_call"]
    declared = cfg_instructions(m["cfg"])["ir_call"]["metadata"]
    declared["source_actions"] = actions("call")
    original = rec["segments"][0]["ops"][0]
    send = {"op":"deliver", "target":"service", "inputs":deepcopy(original["inputs"]),
            "input_contract":deepcopy(original["input_contract"])}
    receive = {"op":"receive", "location":"service", "output":"reply", "inputs":deepcopy(original["inputs"]),
               "input_contract":deepcopy(original["input_contract"])}
    rec["segments"] = [{"ops":[send]}, {"ops":[receive]}]
    response = ["segments",1,"ops",0]
    assert validate_fragment("processing", p, m) == p
    f["task-correspondence"]["operation_demands"][0]["operation_path"] = response
    _, raw, _, mapping = assemble_fragments(p,f["task-correspondence"],f["sensitivity"],m)
    spec = raw["ir_semantics"]["ir_call"]
    assert request_pairs(flatten_raw_spec(RawIRSemantics.model_validate(spec))) == {(1,None,0):(0,None,0)}
    assert verified_split_calls("ir_call", spec, mapping["wire_paths"], rec) == {tuple(response):tuple(CALL)}
    assert [op["op"] for segment in spec["events"] for event in segment["events"] for op in event["atomic_ops"]] == ["deliver","receive"]
    for left, right in (("segments/0/cases/0/segments/0", "segments/0/cases/1/segments/0"),
                        ("segments/0/body/0", "segments/1/body/0")):
        paths = {k: val.replace("/segments/0/ops/0", "/" + left + "/ops/0")
            if val.endswith("/segments/0/ops/0") else val.replace("/segments/1/ops/0", "/" + right + "/ops/0")
            for k,val in mapping["wire_paths"].items()}
        assert verified_split_calls("ir_call", spec, paths, rec) == {}
    declared["source_actions"] = actions("deliver", "call")
    rec["action_bindings"] = {"deliver":[CALL], "call":[response,OUT]}
    with pytest.raises(StructuralValidationError, match="real call"):
        validate_fragment("processing",p,m)
    declared["source_actions"] = actions("call")
    del rec["action_bindings"]
    receive["input_contract"]["inputs"][0]["required"][0]["path"] = ["wrong"]
    with pytest.raises(StructuralValidationError, match="real call"):
        validate_fragment("processing",p,m)
    receive["input_contract"] = deepcopy(send["input_contract"])
    p["locations"]["other"] = {**deepcopy(p["locations"]["service"]), "name":"Independent exception channel"}
    receive["location"] = "other"
    with pytest.raises(StructuralValidationError, match="real call"):
        validate_fragment("processing",p,m)
