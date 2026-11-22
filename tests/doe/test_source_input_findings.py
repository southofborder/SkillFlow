"""Source-established errors remain distinct from representation and local gaps."""
from copy import deepcopy

import pytest
from pydantic import TypeAdapter, ValidationError

from skillflow.doe.source_input_findings import (
    SourceInputFindingCandidate, SourceInputMismatchIndex,
    NormalizedSourceInputFinding, SOURCE_INPUT_FINDING_GUIDANCE,
    normalize_source_input_findings, check_source_input_finding_consistency,
)
from skillflow.common.prompt_format import render_prompt_format
from skillflow.doe.input_contract_review import build_input_contract_review, checked_input_contract_review
from skillflow.propagation.contracts.joint import joint_source_files
from tests.doe.test_demand_engine import fixture, inp, literal, evidence
from tests.doe.test_reviewed_input_necessity import compute, rule, row, receipt, solve


def example(kind="missing_argument"):
    values = fixture([compute([inp()], [rule([], [row(0, ["body"])])])])
    entry = next(t for t in values[3].values() if t.get("kind") == "operation" and t["value"]["op"] == "compute")
    finding = {"kind": kind, "target_id": "annotation:" + entry["pointer"],
        "actual": {"kind": "absent_argument"} if kind == "missing_argument" else
                  {"kind": "input_range", "input_index": 0, "path": ["wrong" if kind == "wrong_field" else "missing"]},
        "expected": {"parameter": {"kind": "named", "name": "required_label"},
            "information": {"property": "value", "path": ["label"]}, "source_value": None,
            "description": "The source-defined operation requires a label supplied as its second named parameter."},
        "impacts": [{"kind": "output", "property": "value", "path": []}],
        "requirement_evidences": [evidence()], "occurrence_evidences": [evidence()],
        "reason": "The authored invocation omits the label required by its separately cited output definition."}
    return values, finding


def normalized(values, candidates):
    facts, _, annotation, _ = values
    return normalize_source_input_findings(candidates, files=joint_source_files(annotation["material"]),
        cfg=facts.cfg, raw_annotation=annotation["raw_annotation"], compiled=annotation["compiled_annotation"],
        mapping=annotation["mapping"])


def with_source_findings(values, findings):
    base = receipt(values)
    core = base["review_core"]
    return build_input_contract_review(files=joint_source_files(values[2]["material"]), cfg=values[0].cfg,
        annotation=values[2], review={"status": core["status"], "availability": core["availability"],
            "review": {"schema_version": core["schema_version"], "outcome": "completed", "findings": [],
                "input_contract_checks": core["checks"], "input_projection_checks": core["projection_checks"],
                "source_input_findings": findings}},
        review_material={"partial": core["partial"], "input_contract_binding": core["binding"],
            "input_contract_inventory": core["inventory"]})


@pytest.mark.parametrize("kind", ["missing_argument", "missing_field", "wrong_field"])
def test_known_source_defect_preserves_actual_inputs_and_reports_without_invented_slot(kind):
    values, finding = example(kind)
    before = deepcopy((values[0].records, values[0].data, values[2]["raw_annotation"]))
    reviewed = with_source_findings(values, [finding])
    assert checked_input_contract_review(reviewed, files=joint_source_files(values[2]["material"]),
        cfg=values[0].cfg, annotation=values[2]) == reviewed
    engine, result = solve(values, review=reviewed)
    source_rows = [r for r in result["input_findings"] if r["origin"] == "source_review"]
    assert len(source_rows) == 1
    reported = source_rows[0]
    assert reported["kind"] == ("wrong_input" if kind == "wrong_field" else "missing_input")
    assert reported["source_review_refs"] == [reported["id"]]
    assert reported["source_finding"]["expected"]["source_value"] is None
    assert any(d["code"].startswith("input_contract_source_") for d in result["diagnostics"])
    if kind == "missing_argument":
        assert reported["input_index"] is None and reported["assessment_refs"] == []
        assert all(a["input_index"] == 0 for a in result["input_assessments"]
                   if a["node_kind"] == "op_input" and a["instruction_id"] == "ir_filter")
    assert before == (values[0].records, values[0].data, values[2]["raw_annotation"])


def test_missing_field_validates_actual_parent_not_existence_of_missing_child():
    values, finding = example("missing_field")
    checked = normalized(values, [finding])[0]
    assert checked["actual"]["path"] == ["missing"]
    index = SourceInputMismatchIndex({"review_core": {"source_input_findings": [checked]}})
    ref = checked["operation_refs"][0]
    assert index.for_operation(ref["instruction_id"], ref["raw_path"])[0]["id"] == checked["id"]
    assert index.for_operation("another_ir", ref["raw_path"]) == []


@pytest.mark.parametrize("change", ["absent_slot", "parent_target", "bad_source", "invented_literal", "wrong_discriminator"])
def test_known_source_defect_requires_real_coordinates_evidence_and_no_invented_input(change):
    values, finding = example("missing_field")
    if change == "absent_slot":
        finding["actual"]["input_index"] = 8
    elif change == "parent_target":
        finding["target_id"] = finding["target_id"].rsplit("/", 1)[0]
    elif change == "bad_source":
        finding["requirement_evidences"][0]["end_line"] = 9999
    elif change == "invented_literal":
        finding["expected"]["source_value"] = {"value": literal("invented correction"), "path": []}
    else:
        finding["kind"] = "missing_argument"
    with pytest.raises(ValueError):
        normalized(values, [finding])


def test_source_error_and_representation_error_cannot_assert_same_use_is_faithful():
    values, candidate = example()
    rows = normalized(values, [candidate])
    conflicting = {"domain": "annotation", "owner": "processing", "target_ids": [candidate["target_id"]]}
    with pytest.raises(ValueError, match="unfaithful"):
        check_source_input_finding_consistency(rows, [conflicting], cfg=values[0].cfg, mapping=values[2]["mapping"])
    for marker in ({"input_contract_obligation_id": "actual_dependency_claim"},
                   {"input_projection_scope_ids": ["actual_projection_claim"]}):
        check_source_input_finding_consistency(rows, [{**conflicting, **marker}], cfg=values[0].cfg, mapping=values[2]["mapping"])
    check_source_input_finding_consistency(rows, [{**conflicting, "target_ids": [candidate["target_id"] + "/demand_transfer"]}],
                                         cfg=values[0].cfg, mapping=values[2]["mapping"])


def test_flat_call_one_source_defect_projects_exact_request_action_and_response_output():
    from tests.doe.test_input_locations import flat_values
    from skillflow.propagation.annotation.binding_examples import evidence as call_evidence
    values, _ = flat_values()
    _, finding = example()
    finding.update(target_id="annotation:/ir_semantics/ir_call/segments/0/ops/0",
        impacts=[{"kind": "action"}, {"kind": "output", "property": "value", "path": ["items"]}],
        requirement_evidences=[call_evidence()], occurrence_evidences=[call_evidence()])
    normalized_finding = normalized(values, [finding])[0]
    refs = normalized_finding["operation_refs"]
    assert len(refs) == 2
    assert sorted(r["impacts"][0]["kind"] for r in refs) == ["action", "output"]
    assert len({tuple(r["raw_path"]) for r in refs}) == 2
    index = SourceInputMismatchIndex({"review_core": {"source_input_findings": [normalized_finding]}})
    assert {index.for_operation(r["instruction_id"], r["raw_path"])[0]["id"] for r in refs} == {normalized_finding["id"]}
    # Another identical invocation cannot be selected through value equality.
    assert index.for_operation("ir_return", refs[0]["raw_path"]) == []


def test_known_source_error_is_not_a_demand_seed_and_disjoint_output_stays_exact():
    from tests.doe.test_demand_engine import candidate
    values, finding = example()
    finding["impacts"] = [{"kind": "output", "property": "value", "path": ["other"]}]
    reviewed = with_source_findings(values, [finding])
    _, result = solve(values, path=["items"], review=reviewed)
    assert any(r["origin"] == "source_review" for r in result["input_findings"])
    assert not any(d["code"].startswith("input_contract_source_") for d in result["diagnostics"])
    request = candidate(values[3]); request["goals"] = []
    _, empty = solve(values, review=reviewed, requested=request)
    assert not empty["derivations"]
    assert not any(d["code"].startswith("input_contract_source_") for d in empty["diagnostics"])


@pytest.mark.parametrize("kind", ["missing_argument", "missing_field", "wrong_field"])
def test_finding_schema_exposes_exact_kind_and_actual_form(kind):
    schema = SourceInputFindingCandidate.model_json_schema()
    assert schema["discriminator"]["propertyName"] == "kind"
    branch_ref = schema["discriminator"]["mapping"][kind]
    branch = schema["$defs"][branch_ref.rsplit("/", 1)[1]]
    assert branch["properties"]["kind"]["const"] == kind
    actual_ref = branch["properties"]["actual"]["$ref"]
    actual = schema["$defs"][actual_ref.rsplit("/", 1)[1]]
    assert actual["properties"]["kind"]["const"] == (
        "absent_argument" if kind == "missing_argument" else "input_range")
    if kind == "missing_field":
        assert actual["properties"]["path"]["minItems"] == 1
    elif kind == "wrong_field":
        assert actual["properties"]["path"].get("minItems", 0) == 0
    rendered = render_prompt_format(TypeAdapter(list[SourceInputFindingCandidate]).json_schema())
    assert 'tag="kind"' in rendered
    if kind == "missing_field":
        line = next(line for line in rendered.splitlines() if line.startswith("MissingFieldInputRange ="))
        assert '"path":' in line and "minItems=1" in line


@pytest.mark.parametrize("actual", [
    {"kind": "absent_argument"},
    {"kind": "input_range", "input_index": 0, "path": []},
])
def test_both_rejected_online_missing_field_forms_remain_invalid(actual):
    _, finding = example("missing_field")
    finding["actual"] = actual
    with pytest.raises(ValidationError) as error:
        SourceInputFindingCandidate.model_validate(finding)
    locations = [row["loc"] for row in error.value.errors()]
    assert all("actual" in location for location in locations)
    if actual["kind"] == "input_range":
        assert any(location[-1] == "path" for location in locations)


@pytest.mark.parametrize("kind", ["missing_field", "wrong_field"])
def test_existing_range_never_becomes_a_missing_entire_argument(kind):
    _, finding = example(kind)
    finding["kind"] = "missing_argument"
    with pytest.raises(ValidationError):
        SourceInputFindingCandidate.model_validate(finding)


def test_root_wrong_field_preserves_whole_operand_semantics():
    _, finding = example("wrong_field")
    finding["actual"]["path"] = []
    candidate = SourceInputFindingCandidate.model_validate(finding)
    assert candidate.kind == "wrong_field" and candidate.actual.path == []
    assert candidate.model_dump(mode="json")["actual"] == finding["actual"]
    assert "root" not in candidate.model_dump(mode="json")
    with pytest.raises(ValidationError):
        candidate.root = candidate.root


def test_normalized_schema_and_flat_serialization_preserve_strict_locators():
    values, finding = example("missing_field")
    row = normalized(values, [finding])[0]
    candidate = NormalizedSourceInputFinding.model_validate(row)
    assert candidate.id == row["id"]
    assert candidate.target_id == finding["target_id"]
    assert candidate.model_dump(mode="json") == row
    assert "root" not in row
    row["actual"]["path"] = []
    with pytest.raises(ValidationError):
        NormalizedSourceInputFinding.model_validate(row)
    rendered = render_prompt_format(NormalizedSourceInputFinding.model_json_schema())
    assert "minItems=1" in next(
        line for line in rendered.splitlines() if line.startswith("MissingFieldInputRange ="))


def test_concrete_field_locator_uses_native_call_operand_not_cfg_index():
    from skillflow.propagation.annotation.binding_examples import evidence as call_evidence
    from tests.doe.test_input_locations import flat_values

    values, _ = flat_values()
    _, finding = example("missing_field")
    finding.update(target_id="annotation:/ir_semantics/ir_call/segments/0/ops/0",
        impacts=[{"kind": "action"}],
        requirement_evidences=[call_evidence()], occurrence_evidences=[call_evidence()])
    checked = normalized(values, [finding])[0]
    assert checked["actual"]["input_index"] == 0
    finding["actual"]["input_index"] = 1
    with pytest.raises(ValueError, match="absent actual operation input"):
        normalized(values, [finding])


def test_source_role_does_not_authorize_empty_or_synthetic_missing_field_locator():
    _, finding = example("missing_field")
    finding["expected"]["parameter"] = {
        "kind": "source_role", "description": "The source-established request filter role; encoding unspecified."}
    finding["actual"]["path"] = []
    with pytest.raises(ValidationError):
        SourceInputFindingCandidate.model_validate(finding)
    assert "do not guess a path" in SOURCE_INPUT_FINDING_GUIDANCE
    assert 'native output path [0,"rows"], not ["rows"]' in SOURCE_INPUT_FINDING_GUIDANCE
    assert "not its enclosing CFG instruction" in SOURCE_INPUT_FINDING_GUIDANCE
