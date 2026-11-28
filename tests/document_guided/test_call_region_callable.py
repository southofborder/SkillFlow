"""Closed public google-search draft: a function value is not its first argument."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from skillflow.document_guided.call_region import call_sites


FIXTURE = Path(__file__).with_name("fixtures") / "google_search_callable.json"


def candidate():
    saved = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return saved["facts"], saved["files"]


def invocation(facts):
    return next(op for block in facts["blocks"] for op in block["operations"]
                if op["ref"] == "cli.call_google_search")


def call(facts, files):
    return next(site for site in call_sites(facts, files) if site["caller"] == "cli.invoke_helper")


def test_google_original_inputs_keep_callable_but_compile_as_four_actuals():
    facts, files = candidate()
    original = deepcopy(facts)
    assert invocation(facts)["inputs"][0] == {"result": "module.google_search"}
    assert len(invocation(facts)["inputs"]) == 5
    assert not call(facts, files)["errors"]
    assert facts == original


@pytest.mark.parametrize("change", ["swapped", "missing", "extra", "unproven", "header_only"])
def test_callable_separation_does_not_relax_actual_argument_or_source_checks(change):
    facts, files = candidate()
    op = invocation(facts)
    if change == "swapped":
        op["inputs"][1], op["inputs"][2] = op["inputs"][2], op["inputs"][1]
    elif change == "missing":
        op["inputs"].pop()
    elif change == "extra":
        op["inputs"].append({"result": "module.sys"})
    elif change == "unproven":
        op["inputs"][0] = {"result": "module.sys"}
    else:
        declaration = next(o for b in facts["blocks"] for o in b["operations"]
                           if o["ref"] == "module.define_function")
        declaration["source"]["end_line"] = declaration["source"]["start_line"]
    assert call(facts, files)["errors"]


def test_existing_argument_only_representation_stays_valid():
    facts, files = candidate()
    invocation(facts)["inputs"].pop(0)
    assert not call(facts, files)["errors"]


def test_misleading_callee_metadata_does_not_make_an_unrelated_value_callable():
    facts, files = candidate()
    invocation(facts)["inputs"][0] = {"result": "module.sys"}
    invocation(facts)["metadata"]["callee"] = "google_search"
    assert call(facts, files)["errors"]


@pytest.mark.parametrize("explicit_callable", [True, False])
def test_same_function_passed_as_a_real_argument_is_preserved(explicit_callable):
    facts, files = candidate()
    f = "skill/scripts/search.py"
    files[f] = files[f].replace("google_search(query, api_key, cse_id, num_results)",
                                "google_search(google_search, api_key, cse_id, num_results)")
    op = invocation(facts)
    op["inputs"][1] = {"result": "module.google_search"}
    formal = next(b for b in facts["blocks"] if b["ref"] == "helper.bind")["operations"][0]
    formal["inputs"][5] = {"result": "module.google_search"}
    formal["metadata"]["predecessor_bindings"]["cli.invoke_helper"]["helper.query"] = "module.google_search"
    if not explicit_callable:
        op["inputs"].pop(0)
    assert not call(facts, files)["errors"]
