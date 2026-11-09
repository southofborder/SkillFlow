"""Saved interface failures stay invalid; displayed references use real targets."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from skillflow.common.prompt_format import compact_json
from skillflow.common.source_evidence import json_pointer
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import (
    compile_flat_response, expression_reference_view,
)
from skillflow.document_guided.fragments import assemble_fragments, validate_fragment
from skillflow.document_guided.prompts import build_fragment_prompt
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.references import target_key


FIXTURES = Path(__file__).parents[1] / "fixtures/online_interface_r4/expressions"
VIEW_TITLE = "EXISTING EXPRESSION REFERENCES (program-generated from processing)"
FAILED_REQUIREMENTS = {"010": {"R4", "R6"}, "013": {"R3"}}


def saved_case(case):
    value = json.loads((FIXTURES / (case + ".json")).read_text(encoding="utf-8"))
    material = prepare_material(value["source"], value["cfg"], task_baseline=value["task"])
    return value, material


def reference_corrected_copy(value, case):
    """Test-only authored change, never production correction or historic replay."""
    mapping = deepcopy(value["failed_correspondence"])
    references = expression_reference_view(value["processing"])
    for row in mapping["realizations"]:
        if row["requirement_id"] in FAILED_REQUIREMENTS[case]:
            condition = row["constraints"][0]["condition"]
            row["constraints"][0]["condition"] = deepcopy(next(
                ref["target"] for ref in references
                if ref["target"].get("instruction_id") == condition["instruction_id"]))
    return mapping


def assert_display_references_compile(references, compiled, mapping):
    """Compare with the compiler's own normalized-expression target identities."""
    actual = []
    for row in compiled["expressions"]:
        target = deepcopy(row["target"])
        if "operation_path" in target:
            backend_pointer = json_pointer("ir_semantics", target["instruction_id"], *target["operation_path"])
            wire_pointer = mapping["wire_paths"][backend_pointer]
            # These known wire path components are strings alternating with
            # array indexes; no arbitrary JSON-pointer path becomes a target.
            path = wire_pointer.split("/")[3:]
            target["operation_path"] = [int(part) if part.isdigit() else part for part in path]
        actual.append({"target": target, "expression": row["expression"]})
    assert {target_key(row) for row in references} == {target_key(row) for row in actual}


@pytest.mark.parametrize("case", ["010", "013"])
def test_exact_failed_candidates_are_rejected_without_automatic_reference_rewrite(case):
    value, material = saved_case(case)
    original = deepcopy(value)
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("task-correspondence", value["failed_correspondence"], material,
                          value["processing"])
    actual = {(row["code"], row["path"]) for row in caught.value.diagnostics}
    expected = ({("constraint_expression", "/realizations/3/constraints/0/condition"),
                 ("constraint_expression", "/realizations/5/constraints/0/condition")}
                if case == "010" else {
                    ("constraint_reference", "/realizations/2/constraints/0/condition"),
                    ("constraint_expression", "/realizations/2/constraints/0/condition")})
    assert actual == expected
    assert value == original


@pytest.mark.parametrize("case", ["010", "013"])
def test_copying_displayed_targets_compiles_saved_fragments_and_checks_real_constraints(case):
    from skillflow.propagation.annotation.services import to_payload
    from skillflow.propagation.contracts.demand_index import build_demand_target_index
    from skillflow.propagation.contracts.task import Task
    from skillflow.propagation.loading import materials_from_result
    from skillflow.propagation.solver import propagate
    from skillflow.doe.demand_engine import DemandEngine
    from skillflow.doe.constraint_engine import ConstraintEngine

    value, material = saved_case(case)
    mapping_fragment = reference_corrected_copy(value, case)
    assert validate_fragment("task-correspondence", mapping_fragment, material,
                             value["processing"]) == mapping_fragment
    wire, raw, compiled, mapping = assemble_fragments(value["processing"], mapping_fragment,
                                                     value["sensitivity"], material)
    assert compile_flat_response(wire, material) == (wire, raw, compiled, mapping)
    references = expression_reference_view(value["processing"])
    assert len(references) == (2 if case == "010" else 1)
    assert all(row["target"]["slot"] == {"kind": "self"} for row in references)
    assert all(set(row) == {"target", "expression"} for row in references)
    assert_display_references_compile(references, compiled, mapping)

    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=wire)
    candidate = {"goals": compiled["demands"], "expressions": compiled["expressions"]}
    engine = DemandEngine(facts, Task.model_validate(material["task"]), facts.annotation,
        candidate, build_demand_target_index(material["cfg"], raw))
    checks = list(ConstraintEngine(engine).check().values())
    restored = [row for row in checks if row["requirement_id"] in FAILED_REQUIREMENTS[case]]
    assert len(restored) == len(FAILED_REQUIREMENTS[case])
    assert all(row["kind"] == "only_if" and row["operations"] for row in restored)
    if case == "010":
        assert solved.status == "complete"
        assert {row["requirement_id"] for row in checks if row["status"] == "satisfied"} == {"R2", "R9"}
        # The existing abstract control checker still permits violating paths;
        # fixing a reference does not establish source-level compliance.
        assert {row["status"] for row in restored} == {"potential_violation"}
        assert all(row["witness"] for row in restored)
    else:
        assert solved.status == "incomplete"
        # Keep the saved append/output limitations. They must not turn into a
        # false complete-DOE result merely because R3 now references correctly.
        assert {row["status"] for row in restored} == {"not_established"}
        assert all(any("lacks complete propagation facts" in reason for reason in row["reasons"])
                   for row in restored)


@pytest.mark.parametrize("case", ["010", "013"])
def test_initial_and_repair_mapping_receive_same_compact_view_and_full_source(case):
    value, material = saved_case(case)
    files = {"skill/" + row["path"]: row["content"] for row in value["source"]["files"]}
    kwargs = dict(files=files, documents={"processing": value["processing"]}, cfg=material["cfg"],
                  task=material["task"], global_requirements="Preserve actual source restrictions.")
    initial = build_fragment_prompt("task-correspondence", **kwargs)
    repair = build_fragment_prompt("task-correspondence", **kwargs,
                                   repair_context={"source_rechecks": [{"target_ids": ["R3"]}]})
    expected = expression_reference_view(value["processing"])
    for prompt in (initial, repair):
        shown = prompt.split(VIEW_TITLE + "\n", 1)[1].split("\n\n", 1)[0]
        assert json.loads(shown) == expected
        assert compact_json(expected) == shown
        assert "copy its target exactly" in prompt
        assert "output slot and a path ending in expression/expression" in prompt
        assert 'path=[{"kind":"each"},"access_token"]' in prompt
        assert "does not require a lexical for_each" in prompt
        assert "A sensitivity label alone does not encode a receiver prohibition" in prompt
        assert "RUNTIME_CONTRACT\n" not in prompt
        for file, content in files.items():
            assert file in prompt
            assert all(line in prompt for line in content.splitlines() if line.strip())


def test_case_member_expression_reference_uses_existing_lexical_path_and_omitted_case_default():
    from skillflow.document_guided.interface_examples import (
        CALL_PATH, example_fragments, example_material,
    )
    value, material = example_fragments(), example_material()
    p, m = value["processing"], value["task-correspondence"]
    cases = p["ir_semantics"]["ir_call"]["segments"][0]["body"][0]["cases"]
    del cases[0]["segments"]  # Legal omitted default, preserved in the input.
    operations = cases[1]["segments"][0]["ops"]
    operations.insert(0, {"op": "compute", "inputs": [{"kind": "local", "name": "url"}],
        "output": "has_url", "expression": {"expression": {
            "op": "present", "arg": {"op": "ref", "value": {"kind": "local", "name": "url"}}}}})
    m["operation_demands"][0]["operation_path"][-1] = 1
    reference, = expression_reference_view(p)
    assert reference["target"] == {"instruction_id": "ir_call", "operation_path": CALL_PATH,
                                  "slot": {"kind": "self"}}
    m["realizations"][0]["constraints"] = [{"kind": "only_if",
        "scope": {"kind": "element", "instruction_id": "ir_call", "scope_path": ["segments", 0]},
        "events": [{"instruction_id": "ir_call", "operation_path": [*CALL_PATH[:-1], 1],
                    "slot": {"kind": "self"}}], "condition": deepcopy(reference["target"])}]
    original = deepcopy(p)
    wire, raw, compiled, mapping = assemble_fragments(p, m, value["sensitivity"], material)
    assert p == original
    assert "segments" not in cases[0]
    assert_display_references_compile([reference], compiled, mapping)


def test_existing_cfg_expression_supplement_retains_its_exact_cfg_target():
    value, material = saved_case("010")
    p = value["processing"]
    expression = deepcopy(p["ir_semantics"]["ir_005"]["segments"][0]["ops"][0]["expression"])
    expression["evidences"] = deepcopy(p["ir_semantics"]["ir_005"]["evidences"])
    p["expressions"] = [{"target": {"instruction_id": "ir_005", "path": []}, **expression}]
    references = expression_reference_view(p)
    assert references[0] == {"target": {"instruction_id": "ir_005", "path": []},
                             "expression": expression["expression"]}
    m = reference_corrected_copy(value, "010")
    next(row for row in m["realizations"] if row["requirement_id"] == "R4")["constraints"][0]["condition"] = deepcopy(references[0]["target"])
    wire, raw, compiled, mapping = assemble_fragments(p, m, value["sensitivity"], material)
    assert_display_references_compile(references, compiled, mapping)
    # A display consumer cannot mutate the accepted processing by editing a row.
    references[0]["expression"]["op"] = "invalid"
    assert p["expressions"][0]["expression"]["op"] == "present"

