"""An explicitly empty member scope is not a missing symbolic reference."""
from copy import deepcopy

from tests.doe.test_demand_engine import fixture, inp, local, literal
from tests.doe.test_sensitivity_engine import declarations, review, rows


def test_known_empty_each_template_is_resolved_without_a_sensitive_instance():
    values = fixture([{"op": "build", "parts": [], "container": "list", "output": "items"}],
                     mode="local", returned=[local("items")])
    before = deepcopy(values[0])
    result = review(values, declarations([{"kind": "each"}, "token"], value=local("items")))
    assert result["status"] == "complete"
    assert result["coverage"]["declarations"] == result["coverage"]["resolved_declarations"] == 1
    assert result["sinks"] and not rows(result)
    assert not result["diagnostics"]
    assert values[0] == before


def test_recorded_empty_foreach_resolves_scoped_declaration_without_running_body():
    def empty_input(cfg):
        for block in cfg["blocks"].values():
            for instruction in block["instructions"]:
                if instruction["id"] == "ir_filter":
                    instruction["inputs"] = [{"type": "literal", "literal_value": []}]

    def scoped(prepared, raw, evidence):
        segment = raw["ir_semantics"]["ir_filter"]["events"][0]
        segment["events"][0]["atomic_ops"][0]["inputs"] = [local("member")]
        raw["ir_semantics"]["ir_filter"]["events"] = [{
            "kind": "for_each", "item": "member", "collection": inp(), "body": [segment],
            "sensitivity": [], "evidences": deepcopy(evidence)}]
        raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"] = inp()

    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "processed"}],
                     mode="local", custom=scoped, graph_change=empty_input)
    event = values[0].records["ir_filter"]["events"][0]
    assert event["kind"] == "for_each" and event["collections"] and event["instances"] == []
    candidate = declarations(value=local("member"))
    candidate["scopes"][0]["scope_path"] = ["events", 0]
    result = review(values, candidate)
    assert result["status"] == "complete"
    assert result["coverage"]["declarations"] == result["coverage"]["resolved_declarations"] == 1
    assert not result["diagnostics"] and not rows(result)


def test_nonempty_collection_with_missing_member_field_is_still_diagnostic():
    values = fixture([{"op": "build", "parts": [{"path": [0], "value": literal({"other": 1})}],
                       "container": "list", "output": "items"}],
                     mode="local", returned=[local("items")])
    result = review(values, declarations([{"kind": "each"}, "token"], value=local("items")))
    assert result["status"] == "partial"
    assert result["coverage"]["resolved_declarations"] == 0
    assert any(item["code"] == "absent_sensitive_range" for item in result["diagnostics"])
    assert not rows(result)
