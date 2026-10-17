"""The compact wire format has one authoritative range and limitation owner."""
from copy import deepcopy
import pytest
from pydantic import ValidationError
from skillflow.doe.sensitivity_results import DataReview, SensitivityDerivation, resolve_data_review
from skillflow.doe.demand_results import Derivation
from tests.doe.test_sensitivity_report import fixture
from tests.doe.test_demand_results import result as demand_result


def test_compact_review_restores_exact_range_and_is_an_isolated_view():
    review, _ = fixture()
    result = review.to_dict()
    before = deepcopy(result)
    sink = result["sinks"][0]
    sink["limitations"] = ["limitation_A"]
    resolved = resolve_data_review(sink["data_reviews"][0], sink, result["derivations"]["sensitivity"])
    assert resolved["input_index"] == 1  # Original operation slot, never filtered payload index.
    assert resolved["data_id"] == "D-A" and resolved["path"] == ["secret"]
    assert resolved["limitations"] == ["limitation_A"]
    resolved["path"].append("fake")
    resolved["limitations"].clear()
    assert result["derivations"] == before["derivations"]
    assert sink["limitations"] == ["limitation_A"]
    assert set(sink["data_reviews"][0]) == {
        "id", "operation_id", "input_index", "derivation_id", "conclusion", "reason", "demand_refs", "reduction"}


@pytest.mark.parametrize("field,value", [
    ("data_id", "D-A"), ("label", "credential"), ("property", "value"),
    ("path", []), ("excluded_paths", []), ("relation", "direct"),
    ("declaration_id", "S1"), ("limitations", []),
])
def test_deleted_review_fields_are_not_accepted_as_overrides(field, value):
    review, _ = fixture()
    row = review.to_dict()["sinks"][0]["data_reviews"][0]
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        DataReview.model_validate({**row, field: value})


def test_duplicate_id_inside_derivation_is_rejected():
    review, _ = fixture()
    signal = review.to_dict()["derivations"]["sensitivity"]["SD1"]
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        SensitivityDerivation.model_validate({**signal, "id": "SD1"})


def test_duplicate_id_inside_demand_derivation_is_rejected():
    value = demand_result()["derivations"]["d1"]
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        Derivation.model_validate({**value, "id": "d1"})


def test_unknown_derivation_cannot_be_resolved_from_redundant_fields():
    review, _ = fixture()
    result = review.to_dict()
    sink = result["sinks"][0]
    sink["data_reviews"][0]["derivation_id"] = "missing"
    with pytest.raises(ValueError, match="Dangling"):
        resolve_data_review(sink["data_reviews"][0], sink, result["derivations"]["sensitivity"])
