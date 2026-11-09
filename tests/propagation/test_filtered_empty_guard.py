"""Filtering a known empty source does not create an unresolved member path."""
import pytest

from skillflow.propagation.loop_guards import guard_values


def record(content):
    return {"content": content}


@pytest.mark.parametrize("predicate,expected", [
    ("has_member", {False}), ("nonempty", {False}), ("empty", {True}),
])
def test_nested_filters_of_empty_collection_have_no_member(predicate, expected):
    data = {"base": record({"form": "literal", "value": []}),
            "first": record({"form": "subset_view", "base": "base", "predicate": "source predicate"}),
            "second": record({"form": "subset_view", "base": "first", "predicate": "another predicate"})}
    assert guard_values(data, ["second"], predicate) == expected


@pytest.mark.parametrize("base", [
    {"form": "literal", "value": [1]}, {"form": "opaque"},
    {"form": "known_parts", "parts": [], "parts_complete": False},
    {"form": "loop_summary", "variants": [{"content": {"form": "literal", "value": []}},
                                          {"content": {"form": "literal", "value": [1]}}]},
])
def test_filter_does_not_prove_membership_or_exhaustion_of_nonempty_or_unknown_base(base):
    data = {"base": record(base), "filtered": record({"form": "subset_view", "base": "base", "predicate": "keep all"})}
    assert guard_values(data, ["filtered"], "has_member", traversal_exit=False) == {False, True}


def test_recursive_summary_stays_unknown_and_does_not_unroll():
    data = {"base": record({"form": "loop_summary", "variants": [
        {"content": {"form": "subset_view", "base": "base", "predicate": "loop predicate"}}]}),
        "filtered": record({"form": "subset_view", "base": "base", "predicate": "filter"})}
    assert guard_values(data, ["filtered"], "has_member") == {False, True}


def test_mixed_empty_and_nonempty_input_candidates_keep_both_routes():
    data = {"empty": record({"form": "literal", "value": []}),
            "filtered": record({"form": "subset_view", "base": "empty", "predicate": "filter"}),
            "nonempty": record({"form": "literal", "value": [1]})}
    assert guard_values(data, ["filtered", "nonempty"], "has_member", traversal_exit=False) == {False, True}


def test_mapping_empty_collection_retains_empty_route_after_filter():
    data = {"base": record({"form": "literal", "value": []}),
            "mapped": record({"form": "mapped_collection", "base": "base", "scope": "map", "members": []}),
            "filtered": record({"form": "subset_view", "base": "mapped", "predicate": "keep"})}
    assert guard_values(data, ["mapped"], "nonempty") == {False}
    assert guard_values(data, ["filtered"], "empty") == {True}


def test_empty_member_record_list_does_not_make_unknown_source_empty():
    data = {"base": record({"form": "opaque"}),
            "mapped": record({"form": "mapped_collection", "base": "base", "scope": "map", "members": []})}
    assert guard_values(data, ["mapped"], "nonempty") == {False, True}
