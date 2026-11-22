"""Independent review regressions for accepted input-dependency semantics."""
from copy import deepcopy
from types import SimpleNamespace

from skillflow.doe.input_assessments import derivation_problem_refs
from tests.doe.test_reviewed_input_necessity import compute, rule, row, solve, operation_key, assessed
from tests.doe.test_demand_engine import fixture, inp, local, literal
from tests.doe.test_sink_payload_seeds import synthetic_fixture, label_operations, solve_fixture


def test_action_only_tool_call_without_interface_contract_retains_unknown_inputs():
    engine, result = solve_fixture(synthetic_fixture(label_operations(action_seed=True)))
    key = operation_key(engine, "deliver")
    inputs = assessed(result, key, 0)
    assert result["status"] == "partial"
    assert any(d["code"] == "input_contract_unavailable" for d in result["diagnostics"])
    assert any(value["status"] == "unresolved" for value in inputs["ranges"])
    assert not any(value["status"] == "deletable" for value in inputs["ranges"])


def test_excluding_one_index_does_not_drop_all_each_output_dependencies():
    output = {"property": "value", "path": ["rows", {"kind": "each"}, "x"]}
    values = fixture([compute([inp()], [rule(output["path"], [row(0, ["body"])])],
                               output_parts=[output]),
        {"op": "exclude_parts", "input": local("answer"), "paths": [["rows", 1]], "output": "reduced"}])
    engine, result = solve(values)
    key = operation_key(engine)
    # Either an exact residual rule or an explicit unresolved relation must
    # preserve other members; a single index never excludes the entire family.
    assert any(value["status"] in {"required", "unresolved"}
               for value in assessed(result, key, 0)["ranges"])
    assert not any(value["status"] == "deletable" and value["path"] == [] and not value["excluded_paths"]
                   for value in assessed(result, key, 0)["ranges"])


def test_contract_gap_ancestry_is_a_fixed_point_across_parent_cycles():
    graph = {
        "a": {"parents": ["b", "gap"], "rules": []},
        "b": {"parents": ["a"], "rules": []},
        "gap": {"parents": [], "rules": ["input_contract_gap:diagnostic_gap"]},
    }
    first = derivation_problem_refs(SimpleNamespace(derivations=deepcopy(graph)))
    reordered = {key: deepcopy(graph[key]) for key in ("b", "gap", "a")}
    second = derivation_problem_refs(SimpleNamespace(derivations=reordered))
    assert first == second
    assert first["a"] == first["b"] == first["gap"] == {"diagnostic_gap"}


def test_known_absent_required_field_is_a_missing_input_not_an_invented_value():
    values = fixture([compute([literal({"other": 1})], [rule([], [row(0, ["needed"])])])])
    original = deepcopy(values[0].data)
    engine, result = solve(values)
    assert result["status"] == "partial"
    missing = [finding for finding in result["input_findings"] if finding["kind"] == "missing_input"]
    assert missing and any("needed" in finding["reason"] for finding in missing)
    assert values[0].data == original
