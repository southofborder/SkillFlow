"""Batch mechanically independent errors without manufacturing semantic seeds."""
from copy import deepcopy
from types import SimpleNamespace

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.propagation.annotation.binding_examples import binding_examples, example_material, sink_demand_examples
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.contracts.realizations import validate_realizations


def test_all_missing_realization_seeds_reported_with_truthful_parent_coordinates():
    fixture = binding_examples()[0]
    material = example_material(fixture)
    rows = [deepcopy(fixture["annotation"]["realizations"][0]) for _ in range(2)]
    for index, row in enumerate(rows):
        row["requirement_id"] = "R" + str(index)
        row.update(status="expressed", gaps=[])
    task = SimpleNamespace(requirements=[SimpleNamespace(id="R0"), SimpleNamespace(id="R1")])
    with pytest.raises(StructuralValidationError) as caught:
        validate_realizations(rows, task=task, cfg=material["cfg"],
                              source_files={"skill/SKILL.md": fixture["source"]}, goals=[])
    assert [row["path"] for row in caught.value.diagnostics] == ["/realizations/0", "/realizations/1"]
    assert all(row["code"] == "realization_seed" for row in caught.value.diagnostics)
    assert sum("format_example" in row.get("context", {}) for row in caught.value.diagnostics) == 1
    assert "not replacement realizations" in caught.value.diagnostics[0]["context"]["format_example"]
    assert all(row["status"] == "expressed" for row in rows)


def test_realization_reference_failures_are_structural_precise_and_batched():
    fixture = binding_examples()[0]
    material = example_material(fixture)
    row = deepcopy(fixture["annotation"]["realizations"][0])
    row.update(status="retained_only", bindings=[
        {"target": {"instruction_id": "absent", "path": []}, "reason": "candidate claim"}],
        gaps=[{"reason": "candidate gap", "evidences": [
            {"file": "missing", "start_line": 1, "end_line": 1, "reason": "candidate evidence"},
            {"file": "skill/SKILL.md", "start_line": 999, "end_line": 1000, "reason": "candidate evidence"}]}])
    task = SimpleNamespace(requirements=[SimpleNamespace(id=row["requirement_id"])])
    with pytest.raises(StructuralValidationError) as caught:
        validate_realizations([row], task=task, cfg=material["cfg"],
                              source_files={"skill/SKILL.md": fixture["source"]}, goals=[])
    assert [item["path"] for item in caught.value.diagnostics] == [
        "/realizations/0/bindings/0/target", "/realizations/0/gaps/0/evidences/0/file",
        "/realizations/0/gaps/0/evidences/1"]


def test_independent_operation_reference_and_boundary_errors_use_raw_paths():
    fixture = sink_demand_examples()[0]
    material = example_material(fixture)
    raw = fixture["annotation"]
    expected = []
    for ir_id, spec in raw["ir_semantics"].items():
        for e, segment in enumerate(spec["events"]):
            if segment["kind"] != "processing":
                continue
            for f, event in enumerate(segment["events"]):
                for o, op in enumerate(event["atomic_ops"]):
                    base = f"/ir_semantics/{ir_id}/events/{e}/events/{f}/atomic_ops/{o}"
                    if "input" in op and op["input"] is not None:
                        op["input"] = {"kind": "input", "index": 999}
                        expected.append(base + "/input")
                    if op["op"] == "deliver":
                        op["target"] = "missing_boundary"
                        expected.append(base + "/target")
    assert len(expected) >= 2
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(raw, material)
    assert set(expected) <= {row["path"] for row in caught.value.diagnostics}
    assert all("processing" not in row["path"] and "select_part" not in row["path"]
               for row in caught.value.diagnostics)


def test_multiple_absent_operation_goal_slots_are_collected_without_realization_cascade():
    fixture = sink_demand_examples()[0]
    material = example_material(fixture)
    for spec in fixture["annotation"]["ir_semantics"].values():
        for segment in spec["events"]:
            for event in segment.get("events", []):
                for op in event["atomic_ops"]:
                    if op["op"] == "deliver":
                        seed = deepcopy(op["demands"][0])
                        op["demands"] = [{**seed, "target": {"kind": "input", "index": 999}},
                                         {**seed, "target": {"kind": "input", "index": 1000}}]
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(fixture["annotation"], material)
    assert [row["code"] for row in caught.value.diagnostics] == ["operation_goal_slot", "operation_goal_slot"]
    assert sum("format_example" in row.get("context", {}) for row in caught.value.diagnostics) == 1
    assert "actual input of the enclosing IR" in caught.value.diagnostics[0]["context"]["format_example"]
    assert [row["path"].split("/demands/")[-1] for row in caught.value.diagnostics] == ["0/target", "1/target"]


def test_invalid_failure_references_are_batched_but_valid_failure_stays_terminal():
    from skillflow.common.semantic_failure import SemanticFailure
    from skillflow.propagation.annotation.services import validate_raw_response
    fixture = binding_examples()[0]
    material = example_material(fixture)
    raw = {"outcome": "cannot_assess", "failure": {
        "reason": "必要关系尚不能判断。", "instruction_ids": ["absent"],
        "evidences": [{"rule_id": "absent_rule", "reason": "依据。"},
                      {"file": "missing", "start_line": 1, "end_line": 1, "reason": "依据。"}]}}
    with pytest.raises(StructuralValidationError) as caught:
        validate_raw_response(raw, material)
    assert [row["path"] for row in caught.value.diagnostics] == [
        "/failure/instruction_ids", "/failure/evidences/0/rule_id", "/failure/evidences/1/file"]
    raw["failure"]["instruction_ids"] = list(fixture["annotation"]["ir_semantics"])
    raw["failure"]["evidences"] = [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "reason": "依据。"}]
    with pytest.raises(SemanticFailure):
        validate_raw_response(raw, material)


def test_expression_wrapper_error_selects_one_owner_hint_and_keeps_candidate():
    from skillflow.common.structural_correction import correction_prompt
    fixture = binding_examples()[2]
    operation = fixture["annotation"]["ir_semantics"]["ir_sample_count"]["events"][0]["events"][0]["atomic_ops"][0]
    operation["expression"] = operation["expression"]["expression"]
    before = deepcopy(fixture)
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(fixture["annotation"], example_material(fixture))
    hints = [row["context"]["format_example"] for row in caught.value.diagnostics
             if "format_example" in row.get("context", {})]
    assert len(hints) == 1 and "operation.expression" in hints[0]
    assert "<TaskEvidence>" in hints[0] and "not literal response values" in hints[0]
    prompt = correction_prompt("stage inputs and format", fixture["annotation"], caught.value.diagnostics)
    assert "Wrapper syntax" in prompt and "current" in prompt
    assert fixture == before


def test_unrelated_schema_error_does_not_send_expression_lesson():
    fixture = binding_examples()[0]
    fixture["annotation"]["realizations"][0]["status"] = "not_a_status"
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(fixture["annotation"], example_material(fixture))
    assert all("format_example" not in row.get("context", {}) for row in caught.value.diagnostics)


def _two_requirement_fixture():
    fixture = binding_examples()[0]
    second = deepcopy(fixture["task_candidate"]["requirements"][0])
    second.update(id="R2", text="Retain the additional declared calibration outcome.")
    fixture["task_candidate"]["requirements"].append(second)
    fixture["task_candidate"]["source_accounting"][0]["requirement_ids"].append("R2")
    realization = deepcopy(fixture["annotation"]["realizations"][0])
    realization["requirement_id"] = "R2"
    fixture["annotation"]["realizations"].append(realization)
    material = example_material(fixture)
    fixture["annotation"]["task_revision_id"] = material["task"]["task_sha256"]
    return fixture, material


def test_independent_evidence_capability_and_realization_errors_share_one_response():
    fixture, material = _two_requirement_fixture()
    raw = fixture["annotation"]
    ir_id = next(iter(raw["ir_semantics"]))
    raw["demands"][0]["target"] = {"instruction_id": ir_id, "path": ["id"]}
    operation = raw["ir_semantics"][ir_id]["events"][0]["events"][0]["atomic_ops"][0]
    operation["evidences"][0]["file"] = "skill/missing.txt"
    before = deepcopy(raw)
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(raw, material)
    codes = {row["code"] for row in caught.value.diagnostics}
    assert {"evidence_file", "demand_target_capability", "realization_seed"} <= codes
    seed_rows = [row for row in caught.value.diagnostics if row["code"] == "realization_seed"]
    assert [row["path"] for row in seed_rows] == ["/realizations/1"]
    assert seed_rows[0]["context"]["requirement_id"] == "R2"
    assert raw == before


def test_unknown_target_suppresses_its_capability_and_seed_cascades_only():
    fixture, material = _two_requirement_fixture()
    raw = fixture["annotation"]
    raw["demands"][0]["target"] = {"instruction_id": "absent_instruction", "path": []}
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(raw, material)
    codes = [row["code"] for row in caught.value.diagnostics]
    assert "target_domain" in codes and "demand_target_capability" not in codes
    assert "demand_target_reference" not in codes
    assert [row["context"]["requirement_id"] for row in caught.value.diagnostics
            if row["code"] == "realization_seed"] == ["R2"]


def test_invalid_transfer_reference_suppresses_dependent_joint_checks():
    fixture, material = _two_requirement_fixture()
    raw = fixture["annotation"]
    ir_id = next(iter(raw["ir_semantics"]))
    op = raw["ir_semantics"][ir_id]["events"][0]["events"][0]["atomic_ops"][0]
    op["input"] = {"kind": "local", "name": "absent_value"}
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(raw, material)
    assert any("/input" in row["path"] for row in caught.value.diagnostics)
    assert all(row["code"] != "realization_seed" for row in caught.value.diagnostics)


def test_current_cfg_union_hint_does_not_edit_the_target_or_candidate():
    from skillflow.common.structural_correction import correction_prompt
    from skillflow.common.validation import diagnostic_materials
    import json
    fixture = binding_examples()[0]
    raw = fixture["annotation"]
    raw["realizations"][0]["bindings"] = [{"target": {"block_id": "sample"}, "reason": "Synthetic correspondence."}]
    before = deepcopy(raw)
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(raw, example_material(fixture))
    material = diagnostic_materials(caught.value.diagnostics)
    assert len(material["diagnostics"]) == 1
    assert material["diagnostics"][0]["path"] == "/realizations/0/bindings/0/target"
    assert len(material["raw_diagnostics"]) > 1
    prompt = correction_prompt("current stage source and schema", raw, caught.value.diagnostics)
    context = json.loads(prompt.split("CURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[1])
    assert len(context["format_examples"]) == 1
    assert len(context["format_examples"][0]["allowed_forms"]) == 4
    assert context["candidate"] == before and raw == before
    assert "path" not in raw["realizations"][0]["bindings"][0]["target"]


def test_normalized_operation_expression_error_projects_to_raw_response():
    from skillflow.common.validation import diagnostic_materials
    fixture = binding_examples()[2]
    raw = fixture["annotation"]
    path = "/ir_semantics/ir_sample_count/events/0/events/0/atomic_ops/0/expression"
    operation = raw["ir_semantics"]["ir_sample_count"]["events"][0]["events"][0]["atomic_ops"][0]
    expression = operation["expression"]
    expression["evidences"].append(deepcopy(expression["evidences"][0]))
    before = deepcopy(raw)
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(raw, example_material(fixture))
    materials = diagnostic_materials(caught.value.diagnostics)
    row = materials["diagnostics"][0]
    assert row["path"] == path
    assert row["context"]["current"] == expression
    assert "target" not in row["context"]["current"]
    assert materials["raw_diagnostics"][0]["path"].startswith("/expressions/")
    assert materials["diagnostic_mapping"][0]["candidate_path"] == path
    assert raw == before


def test_duplicate_supplement_root_error_displays_raw_keys_not_normalized_goals():
    fixture = binding_examples()[3]
    raw = fixture["annotation"]
    raw["expressions"].append(deepcopy(raw["expressions"][0]))
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(raw, example_material(fixture))
    row = caught.value.diagnostics[0]
    assert row["path"] == ""
    assert row["context"]["current_keys"] == list(raw)
    assert "goals" not in row["context"]["current_keys"]
