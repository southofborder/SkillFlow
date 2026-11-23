"""Bound validation gaps and explicit contracts in the one shared repair round."""
from copy import deepcopy

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided import runner
from skillflow.document_guided.fragment_revision import merge_processing_revision, processing_scope
from skillflow.document_guided.fragments import fragment_correction_strategy, validate_fragment
from skillflow.document_guided.online import read
from skillflow.document_guided.prompts import build_processing_revision_prompt
from skillflow.propagation.contracts.limitations import validation_gap
from tests.document_guided.test_parallel_runner import Harness, freeze_producer, prompt_scope
from tests.document_guided.test_processing_finite_slots import inputs
from tests.document_guided.test_program_graph_facts import FILES, _revision


def test_quarantined_attachment_gets_explicit_path_and_can_be_repaired_in_place():
    material, prior, _ = inputs()
    cfg = material["cfg"]
    before = deepcopy(prior)
    rejected = prior["ir_semantics"].pop("ir_other_call")
    contract = rejected["segments"][0]["ops"][0].pop("input_contract")
    gap = validation_gap("ir_other_call", [{"code": "input_contract_required",
        "path": "/ir_semantics/ir_other_call/segments/0/ops/0/input_contract", "message": "Missing interface contract"}])
    scope = processing_scope(cfg, cfg, [], prior, [gap], rejected_records={"ir_other_call": rejected})
    slot = scope["slots"]["ir_other_call"]
    assert slot["rejected_record"] == rejected and slot["validation_gaps"] == [gap] and not slot["allow_keep"]
    requirement, = slot["required_attachments"]
    pointer = "/segments/0/ops/0/input_contract"
    assert requirement["attachment_pointer"] == pointer and requirement["input_count"] == len(rejected["segments"][0]["ops"][0]["inputs"])
    assert scope["read_only"]["locations"] == prior["locations"]
    prompt = build_processing_revision_prompt(files=FILES, flow="Frozen flow", runtime_contract={},
                                               scope=scope, global_requirements="Preserve source")
    assert "semantic_input_requirements" in prompt and "tool_input_contract" in prompt
    assert "attachment_pointer" in prompt and "PROCESSING" in prompt
    delta = {"path": pointer, "value": contract}
    restored = merge_processing_revision(prior, scope, {"coverage_slots": [
        {"instruction_id": "ir_other_call", "attachments": [delta]}]})
    assert validate_fragment("processing", restored, material) == before
    for invalid in ([delta, delta], [{"path": "/output_bindings/0", "value": {}}]):
        with pytest.raises(StructuralValidationError, match="exact IR-relative"):
            merge_processing_revision(prior, scope, {"coverage_slots": [
                {"instruction_id": "ir_other_call", "attachments": invalid}]})


def test_undefined_local_authorizes_owner_segments_and_keeps_unrelated_ir_frozen():
    material, prior, _ = inputs()
    ir = "ir_other_call"
    prior["ir_semantics"][ir]["output_bindings"][0]["value"] = {"kind": "local", "name": "missing_producer"}
    with pytest.raises(StructuralValidationError) as invalid:
        validate_fragment("processing", prior, material)
    strategy = fragment_correction_strategy("processing")
    strategy.build_prompt("Complete source", prior, invalid.value.diagnostics)
    assert set(strategy.processing_scope["field_slots"]) == {
        "/ir_semantics/ir_other_call/output_bindings/0/value", "/ir_semantics/ir_other_call/segments"}


def test_six_rewritten_processing_records_report_all_24_missing_attachments_together():
    from skillflow.document_guided.online import validate_step
    from tests.doe.test_reviewed_input_necessity import compute, rule, row

    material, prior, _ = inputs()
    cfg = material["cfg"]
    instructions = next(iter(cfg["blocks"].values()))["instructions"]
    owners = ["ir_call", "ir_other_call", "ir_unfilled", "ir_unaffected", "ir_bulk", "ir_final"]
    for ir in owners[-2:]:
        instruction = deepcopy(instructions[0])
        instruction.update(id=ir, outputs=[{"type": "result", "identifier": ir + "_reply"}])
        instructions.insert(-1, instruction)
        prior["ir_semantics"][ir] = deepcopy(prior["ir_semantics"]["ir_call"])
    # A single modeled receive has one interface obligation. A combined call
    # expands to separate request and reply obligations at the same wire field.
    prior["ir_semantics"][owners[0]]["segments"][0]["ops"][0]["op"] = "receive"
    for ir, count in zip(owners, [0, 3, 3, 3, 12, 2], strict=True):
        spec = prior["ir_semantics"][ir]
        for index in range(count):
            requirement = rule([], [row(0, [])])
            requirement["evidences"] = deepcopy(spec["evidences"])
            operation = compute([{"kind": "input", "index": 0}], [requirement])
            operation["output"] = f"derived_{index}"
            spec["segments"][0]["ops"].append(operation)
    validate_fragment("processing", prior, material)
    findings = [{"domain": "annotation", "owner": "processing",
        "target_ids": [f"annotation:/ir_semantics/{ir}"]} for ir in owners]
    plan = processing_scope(cfg, cfg, findings, prior)
    broken = deepcopy(prior["ir_semantics"])
    expected, patches = {}, {}
    for ir in owners:
        patches[ir] = []
        for index, operation in enumerate(broken[ir]["segments"][0]["ops"]):
            if ir != owners[0] and operation["op"] == "call":
                continue
            field = "demand_transfer" if operation["op"] == "compute" else "input_contract"
            pointer = f"/segments/0/ops/{index}/{field}"
            patches[ir].append({"path": pointer, "value": operation.pop(field)})
            expected[f"/ir_semantics/{ir}{pointer}"] = field
        assert {p["path"] for p in patches[ir]} <= {
            item["attachment_pointer"] for item in plan["slots"][ir]["required_attachments"]}
    assert len(expected) == 24 and list(expected.values()).count("demand_transfer") == 23
    context = {**material, "processing_revision": {"previous": prior, "scope": plan}}
    with pytest.raises(StructuralValidationError) as rejected:
        validate_step("processing_fragment", {"coverage_slots": [
            {"instruction_id": ir, "modeled": broken[ir]} for ir in owners]}, context=context)
    diagnostics = rejected.value.diagnostics
    assert len(diagnostics) == 24 and {d["code"] for d in diagnostics} == {"input_contract_required"}
    assert {d["path"] for d in diagnostics} == expected.keys()

    surviving = deepcopy(prior)
    for ir in owners:
        del surviving["ir_semantics"][ir]
    gaps = [validation_gap(ir, [d for d in diagnostics if d["path"].startswith(f"/ir_semantics/{ir}/")])
            for ir in owners]
    retry = processing_scope(cfg, cfg, [], surviving, gaps, rejected_records=broken)
    restored = validate_step("processing_fragment", {"coverage_slots": [
        {"instruction_id": ir, "attachments": patches[ir]} for ir in owners]},
        context={**material, "processing_revision": {"previous": surviving, "scope": retry}})
    assert restored == prior


def test_archived_aggregate_validation_errors_are_scoped_by_physical_owner():
    material, prior, _ = inputs()
    ids = ["ir_other_call", "ir_call"]
    failures = [{"code": "case_shape", "path": f"/ir_semantics/{ir}/segments/0", "message": "Invalid case"}
                for ir in ids]
    cfg = material["cfg"]
    gaps = [validation_gap(ir, failures) for ir in ids]
    scope = processing_scope(cfg, cfg, [], prior, gaps)
    assert all(scope["slots"][ir]["validation_gaps"][0]["validation_errors"] == [error]
               for ir, error in zip(ids, failures, strict=True))
    assert all(gap["validation_errors"] == failures for gap in gaps)


def test_action_inventory_cannot_be_offered_a_topology_only_edit():
    from skillflow.document_guided.graph_slots import plan_graph_repair
    from skillflow.document_guided.prompts import build_graph_updates_prompt
    base, old, _ = _revision()
    finding = {**old["remaining_findings"][0], "required_graph_edit": "action_inventory"}
    plan = plan_graph_repair(base, files=FILES, findings=[finding])
    assert plan["slots"] == {} and plan["unaddressable_findings"] == [finding["id"]]
    assert "NONEMPTY ARRAY of Block" in build_graph_updates_prompt(files=FILES, plan=old)
    edge = {**finding, "target_ids": ["cfg:/edges/0"], "required_graph_edit": "topology"}
    region, = plan_graph_repair(base, files=FILES, findings=[edge])["slots"].values()
    assert region["kind"] == "region"
    assert base.id_map["blocks"][region["target"]] == base.cfg["edges"][0]["source_block_id"]


def test_injected_shared_repair_recovers_known_validation_failure_with_no_review_finding(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    class MissingContract(Harness):
        def complete(self, stage, prompt):
            if stage == "processing":
                self.calls.append(stage)
                if self.calls.count(stage) > 1:
                    return {"fields": []}
                fragment = deepcopy(self.fragments["processing"])
                segment = {"mode": "default", "ops": [
                    {"op": "compute", "inputs": [], "output": "draft_output", "dependencies": []}]}
                fragment["ir_semantics"]["ir_002"]["segments"].append(segment)
                return fragment
            answer = super().complete(stage, prompt)
            if stage == "revision-processing":
                slot = prompt_scope(prompt)["slots"]["ir_002"]
                assert slot["validation_gaps"] and not slot["allow_keep"]
                assert slot["rejected_record"]["segments"][-1]["ops"][0]["output"] == "draft_output"
                assert slot["required_attachments"][-1]["required_field"] == "demand_transfer"
            return answer
    harness = MissingContract(tmp_path / "run")
    harness.prepare(tmp_path / "source")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["repair_used"] and result["selected_annotation"] == "revision/annotation", result
    decision = read(harness.directory / "audit/shared-repair-decision.json")
    assert decision["finding_count"] == 0 and decision["processing_validation_targets"] == ["ir_002"]
    assert harness.calls.count("processing") == 2 and harness.calls.count("revision-processing") == 1
    assert result["stages"]["revision-processing"]["status"] == "complete"
    assert runner.replay(harness.directory) == result
