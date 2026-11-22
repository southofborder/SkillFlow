"""Finite obligation insertion preserves strict whole-review validation."""
from copy import deepcopy
import json

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.document_guided.review_correction import (
    ReviewCorrectionStrategy, _diagnostic_display, _parts, review_correction_scope,
)
from skillflow.document_guided.source_review import build_source_review_prompt, validate_source_review
from tests.document_guided.test_source_review_locality import two_operations
from tests.doe.input_review_helpers import source_review_response


def diagnostics(candidate, material):
    with pytest.raises(StructuralValidationError) as caught:
        validate_source_review(candidate, material)
    return caught.value.diagnostics


def strategy_for(material, candidate):
    strategy = ReviewCorrectionStrategy(material, fragment_correction_strategy("review"))
    errors = diagnostics(candidate, material)
    prompt = strategy.build_prompt(build_source_review_prompt(material), candidate, errors)
    return strategy, prompt, errors


def fixture():
    _, material, _ = two_operations()
    complete = source_review_response(material, [])
    initial = deepcopy(complete)
    missing = initial["input_contract_checks"].pop()
    return material, initial, complete, missing


def test_missing_known_slot_is_inserted_without_rewriting_independent_checks():
    material, initial, complete, missing = fixture()
    before = deepcopy((material, initial))
    strategy, prompt, _ = strategy_for(material, initial)
    assert strategy.scope["mode"] == "records"
    assert strategy.scope["records"] == {}
    assert strategy.scope["missing_obligation_ids"] == [missing["obligation_id"]]
    base = _parts(build_source_review_prompt(material))
    corrected = _parts(prompt)
    if "correction" in corrected[1]:
        assert corrected[2] == base[2]
        context = corrected[1].pop("correction")
    else:
        assert corrected[2].startswith(base[2])
        context = json.JSONDecoder().raw_decode(prompt[prompt.rfind('\n{"record_ids":') + 1:])[0]
    assert corrected[1] == base[1]
    assert context["insertion_obligation_indices"] == [len(complete["input_contract_checks"]) - 1]
    merged = strategy.merge(initial, {"replacements": [], "insertions": [missing]})
    assert merged == complete
    assert validate_source_review(merged, material)
    assert before == (material, initial)


def test_missing_remains_a_strict_error_if_a_known_slot_is_not_authored():
    material, initial, _, _ = fixture()
    strategy, _, _ = strategy_for(material, initial)
    merged = strategy.merge(initial, {"replacements": [], "insertions": []})
    errors = diagnostics(merged, material)
    assert any(row["code"] == "review_coverage" for row in errors)


@pytest.mark.parametrize("defect", ["invented", "duplicate", "existing", "wrong_contract", "bad_source", "extra_key"])
def test_inserted_check_never_bypasses_identity_scope_or_source_validation(defect):
    material, initial, _, missing = fixture()
    strategy, _, _ = strategy_for(material, initial)
    changed = deepcopy(missing)
    if defect == "invented":
        changed["obligation_id"] = "invented-obligation"
    elif defect == "existing":
        changed = deepcopy(initial["input_contract_checks"][0])
    elif defect == "wrong_contract":
        changed["contract_id"] = "invented-contract"
    elif defect == "bad_source":
        changed["evidences"][0]["file"] = "missing.md"
    elif defect == "extra_key":
        changed["allow_missing"] = True
    with pytest.raises(StructuralValidationError):
        merged = strategy.merge(initial, {"replacements": [], "insertions": [changed] * (2 if defect == "duplicate" else 1)})
        validate_source_review(merged, material)


def test_existing_conflict_closes_both_sides_and_replacement_preserves_identity():
    material, initial, complete, missing = fixture()
    initial["findings"] = [{"domain": "cfg", "target_ids": ["cfg:"],
        "explanation": "The graph's declared inputs require a source-supported correction.",
        "source_refs": [{"file": next(iter(material["files"])), "start_line": 1, "end_line": 1}],
        "suggestion": "Correct the represented input relationship."}]
    strategy, _, _ = strategy_for(material, initial)
    assert "/findings/0" in strategy.scope["records"]
    assert all(f"/input_contract_checks/{i}" in strategy.scope["records"] for i in range(len(initial["input_contract_checks"])))
    assert set(strategy.scope["evidence"]["dependency_obligation_ids"]) == {
        row["id"] for row in material["input_contract_inventory"]["obligations"]}
    corrected = source_review_response(material, initial["findings"])
    by_id = {row["obligation_id"]: row for row in corrected["input_contract_checks"]}
    changes = [{"record_id": path, "value": by_id[row["obligation_id"]]}
               for path, row in strategy.scope["records"].items() if path.startswith("/input_contract_checks/")]
    merged = strategy.merge(initial, {"replacements": changes, "insertions": [by_id[missing["obligation_id"]]]})
    assert validate_source_review(merged, material)
    assert merged["findings"] == initial["findings"]
    changes[0]["value"] = complete["input_contract_checks"][-1]
    with pytest.raises(StructuralValidationError, match="exact obligation identity"):
        strategy.merge(initial, {"replacements": changes, "insertions": []})


@pytest.mark.parametrize("defect", ["outside", "duplicate", "whole", "stale_candidate", "stale_material", "stale_diagnostics"])
def test_merge_permissions_bind_candidate_material_and_diagnostics(defect):
    material, initial, _, missing = fixture()
    strategy, _, _ = strategy_for(material, initial)
    correction = {"replacements": [], "insertions": [missing]}
    if defect in {"outside", "duplicate"}:
        row = {"record_id": "/input_contract_checks/0", "value": initial["input_contract_checks"][0]}
        correction["replacements"] = [row] * (2 if defect == "duplicate" else 1)
    elif defect == "whole":
        correction = initial
    elif defect == "stale_candidate":
        initial["input_contract_checks"][0]["reason"] += " Changed."
    elif defect == "stale_material":
        strategy.material["files"][next(iter(material["files"]))] += "\nChanged source."
    else:
        strategy.diagnostics[0]["message"] += " Changed."
    with pytest.raises(StructuralValidationError):
        strategy.merge(initial, correction)


@pytest.mark.parametrize("defect", ["duplicate_id", "unknown_id", "no_id", "missing_table", "global", "coverage_mismatch", "wrong_conflict"])
def test_ambiguous_or_global_correction_uses_full_replacement(defect):
    material, initial, _, _ = fixture()
    errors = diagnostics(initial, material)
    if defect == "duplicate_id":
        initial["input_contract_checks"].append(deepcopy(initial["input_contract_checks"][0]))
    elif defect == "unknown_id":
        initial["input_contract_checks"][0]["obligation_id"] = "invented"
    elif defect == "no_id":
        initial["input_contract_checks"][0].pop("obligation_id")
    elif defect == "missing_table":
        initial.pop("input_projection_checks")
    elif defect == "global":
        errors.append({"code": "schema", "path": "", "message": "Unknown global defect"})
    elif defect == "coverage_mismatch":
        errors = []
    else:
        errors.append({"code": "input_contract_review_conflict", "path": "/input_contract_checks/0", "message": "Conflict", "context": {}})
    assert review_correction_scope(initial, errors, material)["mode"] == "full"


def test_missing_coverage_display_is_exact_and_does_not_parse_similar_prose():
    ids = ["contract:" + str(i) for i in range(20)]
    prefix = "Input-contract review must cover every expected obligation exactly once; missing "
    errors = [{"code": "review_coverage", "path": "/input_contract_checks", "message": prefix + identity} for identity in ids]
    errors.insert(5, {"code": "review_coverage", "path": "/input_contract_checks", "message": prefix + ids[0] + " (different)"})
    shown = _diagnostic_display(errors, ids, ids)
    assert isinstance(shown, dict)
    assert shown["records"] == [{"index": 5, "diagnostic": errors[5]}]
    table = shown["missing_coverage"]
    restored = {row["index"]: row["diagnostic"] for row in shown["records"]}
    restored.update({index: {"code": table["code"], "path": table["path"],
        "message": table["message_prefix"] + ids[position]} for index, position in zip(table["indices"], table["obligation_indices"])})
    assert [restored[i] for i in range(len(errors))] == errors
    assert len(json.dumps(shown)) < len(json.dumps(errors))


def test_actual_target_overlap_closure_is_transitive_and_keeps_unrelated_records():
    material = {"input_contract_inventory": {"obligations": [{"id": identity} for identity in "abcd"]},
        "input_contract_targets": {identity: ["annotation:/" + identity] for identity in "abcd"}}
    initial = {"outcome": "completed", "findings": [
        {"domain": "annotation", "target_ids": ["annotation:/a", "annotation:/b"]},
        {"domain": "annotation", "target_ids": ["annotation:/b", "annotation:/c"]},
        {"domain": "annotation", "target_ids": ["annotation:/d"]}],
        "input_contract_checks": [{"obligation_id": identity} for identity in "bcd"],
        "input_projection_checks": [], "source_input_findings": []}
    errors = [{"code": "review_coverage", "path": "/input_contract_checks",
        "message": "Input-contract review must cover every expected obligation exactly once; missing a"}]
    scope = review_correction_scope(initial, errors, material)
    assert set(scope["records"]) == {"/findings/0", "/findings/1", "/input_contract_checks/0", "/input_contract_checks/1"}
    assert scope["evidence"]["dependency_obligation_ids"] == ["a", "b", "c"]
    assert scope["evidence"]["retained_record_counts"]["findings"] == 1
    assert scope["evidence"]["retained_record_counts"]["input_contract_checks"] == 1
