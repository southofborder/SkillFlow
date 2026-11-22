"""A local unresolved input relation must not poison independent same-sink fields."""
from copy import deepcopy

import pytest

from skillflow.doe.sensitivity_material import prepare_sensitivity_review, validate_sensitivity_result
from skillflow.doe.sensitivity_results import resolve_data_review
from tests.doe.test_demand_engine import evidence
from tests.doe.test_input_contract_preservation import reviewed_fixture
from tests.doe.test_sensitivity_engine import declarations


def scoped_fixture(property):
    transfer = {"rules": [{"output": {"property": "value", "path": []},
        "inputs": [{"input_index": 0, "required": [{"property": "value", "path": ["body"]}],
            "unresolved_ranges": [{"information": {"property": property, "path": ["y"]},
                "gap": {"code": "ambiguous_semantics",
                    "reason": "The source leaves the y-specific fallback relation unspecified; token does not participate in the result.",
                    "missing": "Whether the y field's " + property + " property selects the fallback output label.",
                    "resolution": "Specify whether this exact y information property changes the fallback label selection.",
                    "evidences": [evidence()]}}],
            "remainder": "independent", "reason": "Body is required; only the named y relation is unresolved; token and other fields do not affect the output."}],
        "reason": "The output consists of body and the separately scoped fallback relation; token is excluded from both.",
        "evidences": [evidence()]}]}
    return reviewed_fixture([], transfer=transfer)


@pytest.mark.parametrize("property", ["value", "presence", "cardinality"])
def test_same_sink_scoped_gap_retains_aggregate_limit_but_allows_independent_token_deletion(property):
    values, receipt, request, _ = scoped_fixture(property)
    facts, task, annotation, _ = values
    original = deepcopy((facts.records, facts.data))
    review = prepare_sensitivity_review(facts, task, annotation, request, declarations(), input_contract_review=receipt)
    demand = review.demand_dict()
    result = review.to_dict()
    comparisons = [(sink, resolve_data_review(row, sink, result["derivations"]["sensitivity"]))
                   for sink in result["sinks"] for row in sink["data_reviews"]]
    assert comparisons and result["status"] == "partial"
    for sink, compared in comparisons:
        assert sink["limitations"]  # The y limitation remains visible for the boundary.
        assert compared["path"] == ["token"] and compared["assessment_refs"]
        assert any(a["id"] in compared["assessment_refs"] and any(r["status"] == "deletable" for r in a["ranges"])
                   for a in demand["input_assessments"])
        assert compared["conclusion"] == "excess_supported"
        assert compared["limitations"] == []
        assert compared["reduction"] == {"kind": "exclude_field", "path": ["token"]}
    assert validate_sensitivity_result(result, facts, task, annotation, request, declarations(),
        demand_result=demand, input_contract_review=receipt) == result
    assert (facts.records, facts.data) == original


def test_overlapping_gap_still_blocks_its_own_sensitive_range_and_saved_scope_cannot_be_changed():
    values, receipt, request, _ = scoped_fixture("value")
    facts, task, annotation, _ = values
    for path in (("y",), ("token",)):
        sensitivity = declarations(path)
        review = prepare_sensitivity_review(facts, task, annotation, request, sensitivity, input_contract_review=receipt)
        result = review.to_dict()
        sink = next(s for s in result["sinks"] if s["data_reviews"])
        compact = sink["data_reviews"][0]
        if path == ("y",):
            assert compact["conclusion"] == "no_excess_established" and compact["limitation_refs"]
            compact["limitation_refs"] = []
        else:
            assert compact["conclusion"] == "excess_supported" and compact["limitation_refs"] == []
            compact["limitation_refs"] = list(sink["limitations"])
        with pytest.raises(ValueError, match="scoped relevant limitations"):
            validate_sensitivity_result(result, facts, task, annotation, request, sensitivity,
                demand_result=review.demand_dict(), input_contract_review=receipt)


def test_generic_analysis_limit_still_blocks_independent_same_sink_field():
    from skillflow.doe.sensitivity_engine import SensitivityEngine
    from skillflow.doe.sensitivity_material import build_sensitivity_index
    values, _, _, engine = scoped_fixture("value")
    demand = engine.solve()
    declared = build_sensitivity_index(values[2], declarations())["declarations"]
    tracker = SensitivityEngine(engine, demand, declared)
    tracker.diagnostic("unsupported_sensitive_encoding",
        "The packet encoding at ir_filter is not represented, so its token content relationship cannot be verified.", "ir_filter")
    result = tracker.solve()
    generic = next(d["id"] for d in result["diagnostics"] if d["code"] == "unsupported_sensitive_encoding")
    rows = [row for sink in result["sinks"] for row in sink["data_reviews"]]
    assert rows and all(row["conclusion"] == "no_excess_established" and row["limitation_refs"] == [generic] for row in rows)


def test_report_displays_local_comparison_and_aggregate_boundary_limit_separately():
    from skillflow.doe.sensitivity_report import build_view
    values, receipt, request, _ = scoped_fixture("value")
    review = prepare_sensitivity_review(values[0], values[1], values[2], request, declarations(), input_contract_review=receipt)
    view = build_view(review)
    sinks = [sink for sink in view["sinks"] if sink["rows"]]
    assert sinks and all(sink["limitations"] for sink in sinks)
    assert all(row["conclusion"] == "Excess supported by the current rules" and not row["limitations"]
               for sink in sinks for row in sink["rows"])
