"""Rejected review records remain explicit without discarding independent checks."""
from copy import deepcopy
import json

import pytest

from skillflow.common.recording import canonical_sha256, read_json
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.source_review import (
    build_source_review_prompt, isolate_source_review, prepare_review_material,
    replay_saved_review, run_source_review, validate_source_review,
)
from skillflow.doe.input_contract_review import (
    build_input_contract_review, checked_input_contract_review, reviewed_contract_scopes,
)
from skillflow.propagation.contracts.joint import joint_source_files
from tests.document_guided.test_typed_record_correction import TextClient
from tests.doe.input_review_helpers import review_prompt_payload, source_review_response
from tests.doe.test_demand_engine import fixture, inp, evidence
from tests.doe.test_reviewed_input_necessity import compute, rule, row, solve, assessed


@pytest.fixture(autouse=True)
def stable_offline_producer(monkeypatch):
    from tests.document_guided.test_parallel_runner import freeze_producer
    freeze_producer(monkeypatch)


def review_material(values):
    facts, task, annotation, _ = values
    mapping = annotation["mapping"]
    for item in mapping["events"]:
        if item.get("kind") == "observation":
            item["wire_path"] = deepcopy(item["raw_path"])
    mapping["fragment_origins"] = {"/ir_semantics": "processing"}
    return prepare_review_material(files=joint_source_files(annotation["material"]), task=task,
        cfg=facts.cfg, annotation=annotation["raw_annotation"], raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=mapping, generation="fragment-v1")


def two_operations(*, deterministic_first=False):
    first = ({"op": "select_part", "input": inp(), "path": ["body"], "output": "unused"}
             if deterministic_first else {**compute([inp()], [rule([], [row(0, ["body"])])]), "output": "unused"})
    values = fixture([first, compute([inp()], [rule([], [row(0, ["token"])])])])
    material = review_material(values)
    operations = sorted((t for t in values[3].values() if t.get("kind") == "operation"
                         and t.get("instruction_id") == "ir_filter"), key=lambda t: t["pointer"])
    assert len(operations) == 2
    return values, material, operations


def bad_source_records(target, actual=None):
    """Reproduce the three rejected locator shapes without importing run answers."""
    return [{"kind": "missing_field", "target_id": target,
        "actual": deepcopy(actual if actual is not None else {"kind": "input_range", "input_index": 0, "path": []}),
        "expected": {"parameter": {"kind": "source_role", "description": name},
            "information": {"property": "value", "path": []}, "source_value": None,
            "description": "The independently specified operation needs this named information."},
        "impacts": [{"kind": "output", "property": "value", "path": []}],
        "requirement_evidences": [evidence()], "occurrence_evidences": [evidence()],
        "reason": "The source names the required information but this record omits its actual field locator."}
        for name in ("request filters", "request ordering", "request limit")]


def candidate_with_errors(material, target, actual=None):
    candidate = source_review_response(material, [])
    candidate["source_input_findings"] = bad_source_records(target, actual)
    return candidate


def partial_receipt(values, material, isolated):
    return build_input_contract_review(files=material["files"], cfg=values[0].cfg, annotation=values[2],
        review={"status": "partial", **isolated, "availability": material["availability"]}, review_material=material)


def obligation_for(material, operation):
    return next(r for r in material["input_contract_inventory"]["obligations"]
                if r["instruction_id"] == operation["instruction_id"] and r["raw_path"] == operation["raw_path"])


@pytest.mark.parametrize("actual", [{"kind": "absent_argument"}, {"kind": "input_range", "input_index": 0, "path": []}])
def test_three_malformed_locators_stay_rejected_while_other_operation_survives(actual):
    values, material, operations = two_operations()
    candidate = candidate_with_errors(material, "annotation:" + operations[0]["pointer"], actual)
    before = deepcopy((material, candidate, values[0].records, values[2]))
    with pytest.raises(StructuralValidationError):
        validate_source_review(candidate, material)
    isolated = isolate_source_review(candidate, material)
    ledger, review = isolated["validation"], isolated["review"]
    blocked, independent = [obligation_for(material, op) for op in operations]
    assert ledger["candidate"] == candidate and ledger["candidate_sha256"] == canonical_sha256(candidate)
    assert ledger["inventory"] == material["input_contract_inventory"]
    assert ledger["blocked_obligation_ids"] == [blocked["id"]]
    assert {r["obligation_id"]: r["status"] for r in ledger["contract_coverage"]} == {
        blocked["id"]: "blocked", independent["id"]: "validated"}
    invalid = [r for r in ledger["records"] if r["status"] == "invalid"]
    assert {r["path"] for r in invalid} == {f"/source_input_findings/{i}" for i in range(3)}
    assert all(r["diagnostics"] for r in invalid)
    assert all("/actual" in d["path"] for r in invalid for d in r["diagnostics"])
    assert len(ledger["validation_barriers"]) == 3
    assert all(b["domain"] == "operation" and b["operation_refs"] == [
        {"instruction_id": operations[0]["instruction_id"], "raw_path": operations[0]["raw_path"]}]
        for b in ledger["validation_barriers"])
    assert review["source_input_findings"] == [] and review["findings"] == []
    assert len(review["input_contract_checks"]) == 2
    receipt = partial_receipt(values, material, isolated)
    assert not receipt["source_review_complete"] and receipt["review_status"] == "partial"
    assert not reviewed_contract_scopes(receipt, blocked["contract_id"])["available"]
    assert reviewed_contract_scopes(receipt, independent["contract_id"])["available"]
    assert checked_input_contract_review(receipt, files=material["files"], cfg=values[0].cfg, annotation=values[2]) == receipt
    assert before == (material, candidate, values[0].records, values[2])


def test_nonempty_real_field_locators_validate_without_reclassifying_missing_arguments():
    _, material, operations = two_operations()
    candidate = candidate_with_errors(material, "annotation:" + operations[0]["pointer"])
    for record, field in zip(candidate["source_input_findings"], ("filters", "orderBy", "limit")):
        record["actual"]["path"] = [field]
    validated = validate_source_review(candidate, material)
    assert len(validated["source_input_findings"]) == 3
    assert {row["kind"] for row in validated["source_input_findings"]} == {"missing_field"}
    assert not isolate_source_review(candidate, material)["validation"]["diagnostics"]


def test_broad_cfg_conflict_blocks_all_overlapping_accepted_contracts():
    _, material, _ = two_operations()
    candidate = source_review_response(material, [])
    candidate["findings"] = [{"domain": "cfg", "target_ids": ["cfg:"],
        "explanation": "The graph has an incorrect source-level input relation across this region.",
        "source_refs": [{k: evidence()[k] for k in ("file", "start_line", "end_line")}],
        "suggestion": "Reconstruct the source-supported graph inputs before accepting their contracts."}]
    with pytest.raises(StructuralValidationError):
        validate_source_review(candidate, material)
    isolated = isolate_source_review(candidate, material)
    assert len(isolated["review"]["findings"]) == 1
    assert isolated["validation"]["conflicts"]
    assert set(isolated["validation"]["blocked_obligation_ids"]) == {
        o["id"] for o in material["input_contract_inventory"]["obligations"]}
    assert all(r["status"] == "blocked" for r in isolated["validation"]["contract_coverage"])


@pytest.mark.parametrize("defect", ["missing", "duplicate", "invalid_duplicate", "bad_evidence"])
def test_inventory_coverage_never_treats_omission_or_duplicate_as_acceptance(defect):
    values, material, _ = two_operations()
    candidate = source_review_response(material, [])
    affected = candidate["input_contract_checks"][0]["obligation_id"]
    independent = candidate["input_contract_checks"][1]["obligation_id"]
    if defect == "missing":
        candidate["input_contract_checks"].pop(0)
    elif defect in {"duplicate", "invalid_duplicate"}:
        duplicate = deepcopy(candidate["input_contract_checks"][0])
        if defect == "invalid_duplicate":
            duplicate["status"] = "invented"
        candidate["input_contract_checks"].append(duplicate)
    else:
        candidate["input_contract_checks"][0]["evidences"][0]["end_line"] = 9999
    with pytest.raises(StructuralValidationError):
        validate_source_review(candidate, material)
    isolated = isolate_source_review(candidate, material)
    coverage = {r["obligation_id"]: r for r in isolated["validation"]["contract_coverage"]}
    assert coverage[independent]["status"] == "validated"
    assert coverage[affected]["status"] == ("invalid" if defect == "bad_evidence" else
                                            "duplicate" if "duplicate" in defect else "missing")
    assert isolated["validation"]["blocked_obligation_ids"] == [affected]
    assert {r["obligation_id"] for r in isolated["review"]["input_contract_checks"]} == {independent}
    assert isolated["validation"]["inventory"] == material["input_contract_inventory"]
    partial_receipt(values, material, isolated)


@pytest.mark.parametrize("target", ["annotation:/unknown-operation", "annotation:", None])
def test_unlocatable_source_diagnostic_remains_an_explicit_broad_barrier(target):
    _, material, _ = two_operations()
    candidate = candidate_with_errors(material, target)
    isolated = isolate_source_review(candidate, material)
    assert isolated["review"]["source_input_findings"] == []
    assert len(isolated["validation"]["validation_barriers"]) == 3
    assert all(b["domain"] == "all_operations" and b["operation_refs"] == [] and b["reason"] and b["resolution"]
               for b in isolated["validation"]["validation_barriers"])
    assert set(isolated["validation"]["blocked_obligation_ids"]) == {
        o["id"] for o in material["input_contract_inventory"]["obligations"]}


@pytest.mark.parametrize("table", ["findings", "input_contract_checks", "input_projection_checks", "source_input_findings"])
def test_missing_required_table_has_explicit_barrier_and_keeps_complete_inventory(table):
    _, material, _ = two_operations()
    candidate = source_review_response(material, [])
    del candidate[table]
    with pytest.raises(StructuralValidationError):
        validate_source_review(candidate, material)
    isolated = isolate_source_review(candidate, material)
    assert isolated["validation"]["inventory"] == material["input_contract_inventory"]
    assert any(r["path"] == "/" + table and r["status"] == "invalid" for r in isolated["validation"]["records"])
    if table != "input_projection_checks":
        assert any(b["domain"] == "all_operations" for b in isolated["validation"]["validation_barriers"])
        assert set(isolated["validation"]["blocked_obligation_ids"]) == {
            o["id"] for o in material["input_contract_inventory"]["obligations"]}


def test_raw_request_locator_blocks_only_its_proven_response_pair_and_projection():
    from tests.document_guided.test_input_contract_completeness import call_sample
    from skillflow.document_guided.annotation_wire import compile_flat_response
    from skillflow.propagation.annotation.binding_examples import evidence as call_evidence
    from skillflow.propagation.annotation.services import to_payload
    from skillflow.propagation.contracts.demand_index import build_demand_target_index
    from skillflow.propagation.contracts.task import Task
    from skillflow.propagation.loading import materials_from_result
    from skillflow.propagation.solver import propagate
    prepared, wire = call_sample()
    calls = wire["ir_semantics"]["ir_call"]["segments"][0]["ops"]
    calls[0]["input_contract"]["acquisition_projections"] = [{"selection_input_index": 0,
        "selection_parameter_path": ["fields"], "returned_range": {"property": "value", "path": ["items"]},
        "reason": "The interface selects exactly the items result field.", "evidences": [call_evidence()]}]
    second = deepcopy(calls[0])
    second["output"] = "second_reply"
    second.pop("demands")
    calls.append(second)
    _, raw, compiled, mapping = compile_flat_response(wire, prepared)
    propagated = propagate(prepared["cfg"], to_payload(compiled))
    facts = materials_from_result(propagated, material=prepared, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=wire)
    values = (facts, Task.model_validate(prepared["task"]), facts.annotation,
              build_demand_target_index(facts.cfg, raw))
    material = review_material(values)
    operations = [t for t in values[3].values() if t.get("kind") == "operation"]
    request = next(t for t in operations if t["value"]["op"] == "deliver" and t["instruction_id"] == "ir_call")
    response = next(t for t in operations if t["value"]["op"] == "receive" and t["instruction_id"] == "ir_call")
    candidate = candidate_with_errors(material, "annotation:" + request["pointer"])
    for record in candidate["source_input_findings"]:
        record.update(impacts=[{"kind": "action"}], requirement_evidences=[call_evidence()],
                      occurrence_evidences=[call_evidence()])
    isolated = isolate_source_review(candidate, material)
    expected = {canonical_sha256({"instruction_id": t["instruction_id"], "raw_path": t["raw_path"]})
                for t in (request, response)}
    assert len(expected) == 2
    assert all({canonical_sha256(ref) for ref in b["operation_refs"]} == expected
               for b in isolated["validation"]["validation_barriers"])
    assert all(b["domain"] == "operation" for b in isolated["validation"]["validation_barriers"])
    assert len(material["input_contract_inventory"]["projections"]) == 2
    assert set(isolated["validation"]["blocked_projection_ids"]) == {
        p["id"] for p in material["input_contract_inventory"]["projections"]
        if canonical_sha256(p["request"]) in expected}
    assert all(t["instruction_id"] == "ir_call" for b in isolated["validation"]["validation_barriers"]
               for t in b["operation_refs"])
    assert len(operations) == 4
    assert len(isolated["validation"]["blocked_obligation_ids"]) == 2
    assert sum(r["status"] == "validated" for r in isolated["validation"]["contract_coverage"]) == 2
    partial_receipt(values, material, isolated)


@pytest.mark.parametrize("tamper", ["candidate", "inventory", "blocked", "barriers", "coverage"])
def test_partial_receipt_rederives_records_and_locality_even_after_digest_reseal(tamper):
    values, material, operations = two_operations()
    isolated = isolate_source_review(candidate_with_errors(material, "annotation:" + operations[0]["pointer"]), material)
    receipt = partial_receipt(values, material, isolated)
    changed = deepcopy(receipt)
    core = changed["review_core"]
    if tamper == "candidate":
        core["review_validation"]["candidate"]["source_input_findings"] = []
    elif tamper == "inventory":
        core["review_validation"]["inventory"]["obligations"].pop()
    elif tamper == "blocked":
        core["blocked_obligation_ids"] = []
        core["review_validation"]["blocked_obligation_ids"] = []
    elif tamper == "barriers":
        core["validation_barriers"] = []
        core["review_validation"]["validation_barriers"] = []
    else:
        core["review_validation"]["contract_coverage"][0]["status"] = "validated"
        core["review_validation"]["contract_coverage"][1]["status"] = "validated"
    changed["review_sha256"] = canonical_sha256(core)
    changed["receipt_sha256"] = canonical_sha256({k: v for k, v in changed.items() if k != "receipt_sha256"})
    with pytest.raises(ValueError):
        checked_input_contract_review(changed, files=material["files"], cfg=values[0].cfg, annotation=values[2])


@pytest.mark.parametrize("changed_part", ["source", "cfg", "annotation"])
def test_partial_receipt_rejects_another_selected_bundle(changed_part):
    values, material, operations = two_operations()
    isolated = isolate_source_review(candidate_with_errors(material, "annotation:" + operations[0]["pointer"]), material)
    receipt = partial_receipt(values, material, isolated)
    files, cfg, annotation = deepcopy((material["files"], values[0].cfg, values[2]))
    if changed_part == "source":
        files[next(iter(files))] += "\nA new source obligation.\n"
    elif changed_part == "cfg":
        next(iter(cfg["blocks"].values()))["block_name"] = "Changed selected graph description"
    else:
        annotation["raw_annotation"]["changed"] = True
    with pytest.raises(ValueError, match="another selected bundle"):
        checked_input_contract_review(receipt, files=files, cfg=cfg, annotation=annotation)


def test_public_demand_path_keeps_independent_contract_and_blocks_deterministic_error():
    values, material, operations = two_operations(deterministic_first=True)
    candidate = candidate_with_errors(material, "annotation:" + operations[0]["pointer"])
    reviewed = partial_receipt(values, material, isolate_source_review(candidate, material))
    before = deepcopy((values[0].records, values[0].data, values[2]))
    engine, result = solve(values, review=reviewed)
    blocked = next(k for k, v in engine.ops.items() if v["spec"].get("output") == "unused")
    independent = next(k for k, v in engine.ops.items() if v["spec"].get("output") == "answer")
    assert all(r["status"] == "unresolved" for r in assessed(result, blocked, 0)["ranges"])
    assert any(r["status"] == "required" for r in assessed(result, independent, 0)["ranges"])
    assert any(r["status"] == "deletable" for r in assessed(result, independent, 0)["ranges"])
    assert not any(r["origin"] == "source_review" for r in result["input_findings"])
    assert any(d["code"] == "input_contract_review_validation" for d in result["diagnostics"])
    assert before == (values[0].records, values[0].data, values[2])


@pytest.mark.parametrize("malformed_replacement", [False, True])
def test_exhausted_record_correction_saves_partial_ledger_and_replays_without_calls(tmp_path, malformed_replacement):
    values, material, operations = two_operations()
    target = "annotation:" + operations[0]["pointer"]
    initial = candidate_with_errors(material, target, {"kind": "absent_argument"})
    terminal = candidate_with_errors(material, target)
    correction = ({"replacements": [{"record_id": f"/source_input_findings/{i}", "value": row}
                                    for i, row in enumerate(terminal["source_input_findings"])]}
                  if malformed_replacement else terminal)
    retained = initial if malformed_replacement else terminal
    client = TextClient(initial, correction)
    result = run_source_review(tmp_path, files=material["files"], task=values[1], cfg=values[0].cfg,
        annotation=values[2]["raw_annotation"], raw_annotation=values[2]["raw_annotation"],
        compiled=values[2]["compiled_annotation"], mapping=values[2]["mapping"], generation="fragment-v1", client=client)
    assert result["status"] == "partial" and result["diagnostic_only"]
    assert result["validation"]["candidate"] == retained
    assert result["review"]["findings"] == [] and result["review"]["source_input_findings"] == []
    assert len(client.prompts) == 2 and not client.values
    assert result["counts"]["structural_corrections"] == 1
    assert result["response_chain"]["accepted_call"] is None
    merged = read_json(tmp_path / "calls/review/a002/merged-candidate.json")
    assert merged == (json.dumps(initial) if malformed_replacement else terminal)
    assert read_json(tmp_path / "calls/review/a002/response.json") == json.dumps(correction)
    assert read_json(tmp_path / "calls/review/a001/response.json") == json.dumps(initial)
    assert not (tmp_path / "calls/review/a003").exists()
    saved_material = read_json(tmp_path / "inputs.json")
    assert saved_material["files"] == material["files"]
    payload = review_prompt_payload(client.prompts[0])
    corrected_payload = review_prompt_payload(client.prompts[1])
    assert corrected_payload.pop("correction")
    assert corrected_payload == payload
    delivered = payload["input_contract_inventory"]
    assert {o["id"] for o in delivered["obligations"]} == {
        o["id"] for o in material["input_contract_inventory"]["obligations"]}
    assert {s["id"] for o in delivered["obligations"] for s in o["scopes"]} == {
        s["id"] for c in material["input_contract_inventory"]["contracts"] for s in c["scopes"]}
    assert delivered["projections"] == material["input_contract_inventory"]["projections"]
    assert result["validation"]["blocked_obligation_ids"] == [obligation_for(material, operations[0])["id"]]
    assert all(b["domain"] == "operation" for b in result["validation"]["validation_barriers"])
    sealed = build_input_contract_review(files=material["files"], cfg=values[0].cfg, annotation=values[2],
        review=result, review_material=saved_material)
    assert reviewed_contract_scopes(sealed, obligation_for(material, operations[1])["contract_id"])["available"]
    for name, source in material["files"].items():
        assert name in client.prompts[0]
        assert all(f"{i}: {line}" in client.prompts[0] for i, line in enumerate(source.splitlines(), 1))
    assert replay_saved_review(tmp_path) == result
    assert len(client.prompts) == 2


def test_zero_survivors_preserve_failed_receipt_and_broad_backend_barrier():
    values, material, _ = two_operations()
    candidate = source_review_response(material, [])
    candidate["outcome"] = "invalid_outcome"
    isolated = isolate_source_review(candidate, material)
    assert all(isolated["review"][table] == [] for table in (
        "findings", "input_contract_checks", "input_projection_checks", "source_input_findings"))
    assert any(b["domain"] == "all_operations" for b in isolated["validation"]["validation_barriers"])
    reviewed = {"status": "structural_failure", **isolated, "availability": material["availability"]}
    receipt = build_input_contract_review(files=material["files"], cfg=values[0].cfg,
        annotation=values[2], review=reviewed, review_material=material)
    assert receipt["review_status"] == "structural_failure" and not receipt["source_review_complete"]
    assert checked_input_contract_review(receipt, files=material["files"], cfg=values[0].cfg, annotation=values[2]) == receipt
    assert not receipt["checks"]
    assert all(not reviewed_contract_scopes(receipt, c["contract_id"])["available"]
               for c in material["input_contract_inventory"]["contracts"])
    with pytest.raises(ValueError, match="status differs"):
        build_input_contract_review(files=material["files"], cfg=values[0].cfg, annotation=values[2],
            review={**reviewed, "status": "partial"}, review_material=material)
    engine, result = solve(values, review=receipt)
    assert not any(r["origin"] == "source_review" for r in result["input_findings"])
    assert all(item["status"] == "unresolved" for key, info in engine.ops.items()
               if info["spec"]["op"] == "compute" for item in assessed(result, key, 0)["ranges"])
    assert any(d["code"] == "input_contract_review_validation" for d in result["diagnostics"])


@pytest.mark.parametrize("repair,zero_survivors", [(False, False), (True, False), (False, True)])
def test_seven_normal_requests_keep_two_workers_local_failures_and_one_shared_repair(tmp_path, monkeypatch, repair, zero_survivors):
    from skillflow.document_guided import runner
    from tests.document_guided.test_parallel_runner import Harness
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)

    class PartialReviewHarness(Harness):
        def __init__(self, directory):
            super().__init__(directory, canaries=True, precise_repair=True)
            self.example["task_candidate"]["purpose"]["text"] += " TASK_DOCUMENT_CANARY"
            self.terminals = {}
            instruction, spec = next(iter(self.fragments["processing"]["ir_semantics"].items()))
            cited = deepcopy(spec["evidences"])
            operations = spec["segments"][0]["ops"]
            first_compute = len(operations)
            for output in ("unrelated_label", "required_label"):
                operation = compute([inp()], [rule([], [row(0, ["label"])])])
                operation.update(output=output, evidences=cited)
                operation["demand_transfer"]["rules"][0]["evidences"] = cited
                operations.append(operation)
            spec["segments"][1]["ops"][0]["inputs"][0] = {"kind": "local", "name": "required_label"}
            self.invalid_target = f"annotation:/ir_semantics/{instruction}/segments/0/ops/{first_compute}"
            self.repair_target = f"annotation:/ir_semantics/{instruction}/segments/0/ops/{first_compute - 1}"
            self.repair_position = first_compute - 1
            self.cited = cited

        def complete(self, stage, prompt):
            if stage not in {"review", "revision/review"}:
                result = super().complete(stage, prompt)
                if stage == "revision-processing":
                    slot, = result["coverage_slots"]
                    assert self.repair_target.startswith(f"annotation:/ir_semantics/{slot['instruction_id']}/")
                    operation = slot["modeled"]["segments"][0]["ops"][self.repair_position]
                    operation["evidences"][0]["reason"] += " The source-supported selection was rechecked."
                return result
            if stage in self.terminals:
                with self.lock:
                    self.attempts[stage] += 1
                    self.calls.append(stage)
                assert self.attempts[stage] == 2
                # Source-input diagnostics use the existing whole-response correction.
                return deepcopy(self.terminals[stage])
            candidate = super().complete(stage, prompt)
            if repair and stage == "review":
                candidate["findings"] = [{"domain": "annotation", "owner": "processing",
                    "target_ids": [self.repair_target],
                    "explanation": "The independent source-supported selection needs a representation correction.",
                    "source_refs": [{k: self.cited[0][k] for k in ("file", "start_line", "end_line")}],
                    "suggestion": "Recheck this selection while preserving the independent operations."}]
            candidate["source_input_findings"] = bad_source_records(self.invalid_target)
            for record in candidate["source_input_findings"]:
                record.update(requirement_evidences=self.cited, occurrence_evidences=self.cited)
            if zero_survivors:
                candidate["outcome"] = "invalid_outcome"
                for record in candidate["source_input_findings"]:
                    record["actual"] = {"kind": "absent_argument"}
            self.terminals[stage] = deepcopy(candidate)
            for record in candidate["source_input_findings"]:
                record["actual"] = {"kind": "absent_argument"}
            return candidate

    harness = PartialReviewHarness(tmp_path / "run")
    source = harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "partial", result
    assert result["repair_used"] is repair
    assert result["graph_review"] == result["annotation_review"] == "incomplete"
    assert runner.POLICY["normal_semantic_calls"] == 7 and runner.POLICY["workers"] == 2
    assert runner.POLICY["semantic_repairs"] == runner.POLICY["structural_corrections"] == 1
    assert harness.mapping_started.is_set() and harness.sensitivity_started.is_set()
    normal = {"task", "flow", "graph", "processing", "task-correspondence", "sensitivity", "review"}
    assert {name for name in harness.calls if not name.startswith("revision")} == normal
    assert all(harness.calls.count(name) == (2 if name == "review" else 1) for name in normal)
    assert result["counts"]["structural_corrections"] == (2 if repair else 1)
    assert result["counts"]["logical_calls"] == len(harness.calls) == (13 if repair else 8)
    assert result["counts"]["logical_calls"] - result["counts"]["structural_corrections"] == (11 if repair else 7)
    assert "TASK_DOCUMENT_CANARY" not in harness.prompts["processing"]
    assert "TASK_DOCUMENT_CANARY" not in harness.prompts["sensitivity"]
    assert "TASK_DOCUMENT_CANARY" in harness.prompts["task-correspondence"]
    assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts["task-correspondence"]
    assert "SENSITIVITY_DOCUMENT_CANARY" in harness.prompts["review"]
    if repair:
        assert {name for name in harness.calls if name.startswith("revision")} == {
            "revision-processing", "revision-task-correspondence", "revision-sensitivity", "revision/review"}
        assert result["repair_review"]["status"] == "unconfirmed"
        assert result["selected_annotation"] == "revision/annotation"
        assert any("not confirmed" in reason for reason in result["limitations"])
    else:
        assert not any(name.startswith("revision") for name in harness.calls)
    for name in harness.terminals:
        reviewed = read_json(harness.directory / name / "result.json")
        assert reviewed["status"] == ("structural_failure" if zero_survivors else "partial")
        assert reviewed["response_chain"]["accepted_call"] is None
        assert reviewed["validation"]["candidate"] == harness.terminals[name]
        assert not (harness.directory / name / "calls/review/a003").exists()
    receipt = read_json(harness.directory / "audit/input-contract-review.json")
    assert receipt["review_status"] == ("structural_failure" if zero_survivors else "partial")
    assert not receipt["source_review_complete"]
    assert len(receipt["checks"]) == (0 if zero_survivors else 2)
    assert len(receipt["review_core"]["blocked_obligation_ids"]) == (2 if zero_survivors else 1)
    assert sum(reviewed_contract_scopes(receipt, row["contract_id"])["available"]
               for row in receipt["checks"]) == (0 if zero_survivors else 1)
    if zero_survivors:
        assert all(reviewed["review"][table] == [] for table in (
            "findings", "input_contract_checks", "input_projection_checks", "source_input_findings"))
        assert any(b["domain"] == "all_operations" for b in receipt["review_core"]["validation_barriers"])
    assert (harness.directory / "doe/doe-result.json").is_file()
    assert (harness.directory / "source/inputs/package/SKILL.md").read_bytes().decode("utf-8") == source
    before = {str(path.relative_to(harness.directory)): path.read_bytes()
              for path in harness.directory.rglob("response.json")}
    assert runner.replay(harness.directory) == result
    assert before == {str(path.relative_to(harness.directory)): path.read_bytes()
                      for path in harness.directory.rglob("response.json")}
    assert len(harness.calls) == (13 if repair else 8)

