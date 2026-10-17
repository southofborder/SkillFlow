from tests.propagation.annotation.helpers import authored_prepare_run as prepare_run
from skillflow.propagation.contracts.references import target_key
"""One-response task/demand/sensitivity normalization and identity checks."""
from copy import deepcopy
import json

import pytest
from pydantic import ValidationError

from skillflow.propagation.annotation.services import annotate_skill, compile_response
from skillflow.propagation.annotation.runner import run_annotation, replay_run, RunIdentityError
from skillflow.propagation.annotation.loading import load_annotation_run
from skillflow.propagation.contracts.demand_index import build_demand_target_index
from skillflow.propagation.contracts.joint import joint_source_files, normalize_joint_semantics
from skillflow.propagation.contracts.profiles import RawAnnotationResponse
from skillflow.propagation.contracts.sensitivity import (
    SensitivityDeclaration, validate_sensitivity_candidate, extract_sensitivity_candidate,
)
from tests.propagation.annotation.helpers import prepare_material
from tests.propagation.annotation.helpers import material, valid_raw_response, source_bundle, graph, FakeClient


def evidence(file="skill/SKILL.md"):
    return {"file": file, "start_line": 1, "end_line": 1,
            "reason": "The cited frozen text supports this information classification."}


def declaration(**updates):
    return {"value": {"kind": "input", "index": 0}, "path": ["credential"],
            "property": "value", "label": "credential", "evidences": [evidence()], **updates}


def candidate(ir="ir_filter", scope=(), declarations=None):
    return {"schema_version": "skillflow-sensitivity-candidate-v1", "scopes": [{
        "instruction_id": ir, "scope_path": list(scope),
        "declarations": [declaration()] if declarations is None else declarations}]}


def test_single_joint_call_normalizes_inline_goals_and_expression():
    prepared = material()
    raw = valid_raw_response(prepared)
    op = raw["ir_semantics"]["ir_filter"]["events"][0]["events"][0]["atomic_ops"][0]
    op["demands"] = [{"requirement_id": "R001", "target": {"kind": "output"},
        "preserve": "value", "path": [], "expected": None, "expected_path": [],
        "reason": "Preserve the actual declared result."}]
    raw["realizations"][0].update(status="expressed", gaps=[])
    op["expression"] = {"expression": {"op": "field", "arg": {"op": "ref", "value": op["inputs"][0]},
        "path": ["body"]}, "evidences": [evidence()]}
    raw["ir_semantics"]["ir_read"]["sensitivity"] = [declaration(
        value={"kind": "local", "name": "stage_0"})]
    client = FakeClient(raw)
    compiled = annotate_skill(prepared["source"], prepared["cfg"], client=client, task_baseline=prepared["task"])
    assert len(client.prompts) == 1
    assert compiled["task_ref"]["basis"] == "declared_skill"
    targets = build_demand_target_index(prepared["cfg"], raw)
    goal = compiled["demands"][0]
    assert targets[target_key(goal["target"])]["kind"] == "local_output"
    assert compiled["expressions"][0]["expression"] == op["expression"]["expression"]
    operation = compiled["ir_semantics"]["ir_filter"]["events"][0]["atomic_ops"][0]
    assert "demands" not in operation and "expression" not in operation
    assert "demand" not in compiled and "demands" in compiled and "expressions" in compiled
    assert compiled["ir_semantics"]["ir_read"]["sensitivity"][0]["path"] == ["credential"]


@pytest.mark.parametrize("path", [[True], [-1], [{"kind": "element", "scope": "invented"}], [{"kind": "each", "id": "x"}]])
def test_range_selectors_reject_generated_identity_or_invalid_index(path):
    with pytest.raises(ValidationError):
        SensitivityDeclaration.model_validate(declaration(path=path))


def test_each_is_a_range_template_and_preserves_string_index_distinction():
    parsed = SensitivityDeclaration.model_validate(declaration(path=["rows", {"kind": "each"}, "0", 0]))
    assert parsed.model_dump(mode="json")["path"] == ["rows", {"kind": "each"}, "0", 0]


def test_policy_evidence_allowed_only_for_sensitivity_not_task_or_expression():
    with pytest.raises(TypeError):
        prepare_material(source_bundle(), graph(), policies={"organization.md": "Credentials."})
    prepared = prepare_material(source_bundle(), graph(), user_request="Return the original result.")
    raw = valid_raw_response(prepared)
    raw["ir_semantics"]["ir_filter"]["sensitivity"] = [declaration(evidences=[evidence("policy/organization.md")])]
    with pytest.raises(ValueError, match="file is not frozen"):
        compile_response(raw, prepared)


@pytest.mark.parametrize("ref,ir,match", [
    ({"kind": "input", "index": 19}, "ir_filter", "absent input"),
    ({"kind": "input", "index": 0}, "ir_read", "resource identity"),
    ({"kind": "local", "name": "missing"}, "ir_filter", "absent or escapes"),
])
def test_sensitivity_rejects_invalid_symbolic_values(ref, ir, match):
    prepared = material()
    raw = valid_raw_response(prepared)
    with pytest.raises(ValueError, match=match):
        validate_sensitivity_candidate(candidate(ir=ir, declarations=[declaration(value=ref)]),
            prepared["cfg"], raw, joint_source_files(prepared))


def test_foreach_scope_prevents_member_escape_and_preserves_source_member_template():
    prepared = material()
    raw = valid_raw_response(prepared)
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    segment["events"][0]["atomic_ops"][0]["inputs"] = [{"kind": "local", "name": "member"}]
    raw["ir_semantics"]["ir_filter"]["events"] = [{"kind": "for_each", "item": "member",
        "collection": {"kind": "input", "index": 0}, "body": [segment], "sensitivity": [],
        "evidences": deepcopy(segment["evidences"])}]
    raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"] = {"kind": "input", "index": 0}
    scoped = candidate(scope=["events", 0], declarations=[declaration(value={"kind": "local", "name": "member"})])
    validate_sensitivity_candidate(scoped, prepared["cfg"], raw, joint_source_files(prepared))
    scoped["scopes"][0]["scope_path"] = []
    with pytest.raises(ValueError, match="escapes"):
        validate_sensitivity_candidate(scoped, prepared["cfg"], raw, joint_source_files(prepared))
    raw["ir_semantics"]["ir_filter"]["sensitivity"] = [declaration(path=[{"kind": "each"}, "credential"])]
    raw["ir_semantics"]["ir_filter"]["events"][0]["sensitivity"] = [declaration(value={"kind": "local", "name": "member"})]
    compiled = compile_response(raw, prepared)[1]
    assert compiled["ir_semantics"]["ir_filter"]["sensitivity"][0]["path"][0] == {"kind": "each"}
    assert compiled["ir_semantics"]["ir_filter"]["events"][0]["sensitivity"][0]["value"]["name"] == "member"


def test_top_level_goals_cannot_predict_raw_target_hash():
    prepared = material()
    raw = valid_raw_response(prepared)
    target = next(value["target"] for value in build_demand_target_index(prepared["cfg"], raw).values()
                  if value["kind"] == "local_output")
    raw["demands"] = [{"requirement_id": "R001", "target": target,
                           "preserve": "value", "reason": "Preserve this result."}]
    with pytest.raises(ValueError, match="pre-existing CFG"):
        normalize_joint_semantics(raw, prepared)


def test_old_wire_is_not_accepted_by_optional_empty_sensitivity():
    raw = valid_raw_response(material())
    for key in ("task_revision_id", "realizations", "demands", "expressions"):
        raw.pop(key)
    with pytest.raises(ValidationError):
        RawAnnotationResponse.model_validate(raw)


def test_scoped_declarations_never_mutate_input_or_fabricate_data():
    prepared = material()
    raw = valid_raw_response(prepared)
    before = deepcopy(raw)
    extracted = extract_sensitivity_candidate(raw)
    validate_sensitivity_candidate(extracted, prepared["cfg"], raw, joint_source_files(prepared))
    assert raw == before
    assert all(scope["declarations"] == [] for scope in extracted["scopes"])
    assert "data" not in extracted


def test_joint_run_replays_same_frozen_user_request_policy_and_accepted_response(tmp_path):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text(source_bundle()["files"][0]["content"], encoding="utf-8")
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps({"cfg": graph()}), encoding="utf-8")
    directory = tmp_path / "run"
    manifest = prepare_run(source, analysis, run_dir=directory, user_request="Preserve the original result.")
    assert manifest["preparation_status"] == "ready", manifest.get("preparation_error")
    client = FakeClient()
    result = run_annotation(directory, client=client)
    assert result["status"] == "complete", result.get("reason")
    assert len(client.prompts) == 1
    replay = replay_run(directory)
    assert replay["task_ref"] == result["task_ref"] and replay["demands"] == result["demands"]
    loaded = load_annotation_run(directory)
    assert loaded["material"]["user_request"] == "Preserve the original result."
    context_path = directory / "inputs/user-request.json"
    context_path.write_text(json.dumps("Changed purpose."), encoding="utf-8")
    with pytest.raises(RunIdentityError):
        replay_run(directory)
