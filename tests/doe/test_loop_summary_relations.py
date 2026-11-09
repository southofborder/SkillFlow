"""Finite summary relations must preserve content and alternative identities."""
from types import SimpleNamespace

from skillflow.doe.constraint_control import UNKNOWN, collection_size, literal_at
from skillflow.doe.constraint_ranges import ContentRanges
from skillflow.doe.sensitivity_engine import SensitivityEngine, range_presence
from skillflow.propagation.data import Data


EACH = {"kind": "each"}


def _data(identity, content):
    return Data.model_validate({"id": identity, "content": content}).model_dump(mode="json")


def _family(identity, contents):
    return _data(identity, {"form": "loop_summary", "scope": "loop", "producer": identity,
        "variants": [{"inputs": [], "content": content, "dependencies": [], "acquired_from": None}
                     for content in contents]})


def _track(data, identity, path):
    engine = SimpleNamespace(index=SimpleNamespace(data=data), ops={}, expressions={})
    result = SensitivityEngine(engine, {}, {})
    result.seed = lambda: result.emit(identity, {"declaration_id": "credential", "label": "credential",
        "property": "content", "path": path, "excluded_paths": [], "relation": "direct"},
        "explicit_declaration")
    result.track()
    return result


def test_family_alternatives_do_not_copy_one_candidates_label_into_its_sibling():
    data = {
        "a": _data("a", {"form": "literal", "value": {"token": "secret"}}),
        "b": _data("b", {"form": "literal", "value": {"token": "public"}}),
        "family": _family("family", [
            {"form": "known_parts", "parts": [{"path": ["record"], "data": source}], "parts_complete": True}
            for source in ("a", "b")]),
    }
    tracked = _track(data, "a", ["token"])
    assert not tracked.by_data["b"]
    assert any(row["data_id"] == "family" and row["path"] == ["record", "token"]
               for row in tracked.rows.values())


def test_cyclic_accumulation_preserves_contributions_without_counting_variants():
    data = {
        "empty": _data("empty", {"form": "literal", "value": []}),
        "record": _data("record", {"form": "literal", "value": {"token": "secret", "url": "u"}}),
        "family": _family("family", [
            {"form": "literal", "value": []},
            {"form": "accumulated_collection", "base": "family", "added": "record", "mode": "item"}]),
    }
    assert collection_size(data, "family") is None
    assert literal_at(data, "family") is UNKNOWN
    assert range_presence(data, "family", [EACH, "token"]) == "present"
    tracked = _track(data, "record", ["token"])
    family_rows = [row for row in tracked.rows.values() if row["data_id"] == "family"]
    assert family_rows and all(row["path"] == [EACH, "token"] for row in family_rows)
    assert len(tracked.rows) <= 3
    assert not tracked.diagnostics


def test_nested_selection_keeps_all_member_scopes_and_unknown_recursive_tail():
    data = {
        "rows": _data("rows", {"form": "literal", "value": [{"children": [{"secret": "a"}]}]}),
        "outer": _data("outer", {"form": "selection", "base": "rows", "path": [0]}),
        "inner": _data("inner", {"form": "selection", "base": "outer", "path": ["children", 0]}),
        "recursive": _family("recursive", [{"form": "selection", "base": "recursive", "path": ["next"]}]),
    }
    assert range_presence(data, "inner", ["secret"]) == "present"
    assert literal_at(data, "inner", ["secret"]) == "a"
    assert range_presence(data, "recursive", ["secret"]) == "unknown"
    assert literal_at(data, "recursive", ["secret"]) is UNKNOWN
    assert collection_size(data, "recursive") is None


def test_original_content_prohibition_crosses_cyclic_summary_without_plaintext_inference():
    data = {
        "record": _data("record", {"form": "literal", "value": {"secret": "s", "url": "u"}}),
        "family": _family("family", [
            {"form": "accumulated_collection", "base": "family", "added": "record", "mode": "item"}]),
        "alias": _family("alias", [{"form": "selection", "base": "family", "path": []}]),
    }
    tracked = ContentRanges(data).track({"record"}, ["secret"])
    assert any(row["path"] == [EACH, "secret"] and row["relation"] == "direct" for row in tracked["alias"])
    assert not any(row["path"] == [EACH, "url"] for row in tracked["alias"])


def test_retry_literal_request_is_not_counted_as_exactly_one_static_record():
    from skillflow.doe.constraint_engine import ConstraintEngine
    from tests.doe.test_constraints_engine import World, bounded
    world = World()
    request = world.op("retry", "request")
    world.edge("retry", "retry")
    world.edge("retry", "done")
    result = ConstraintEngine(world.engine(bounded([request], limit=1))).check()
    assert result and all(row["status"] != "satisfied" for row in result.values())


def test_request_pairing_rejects_swapped_occurrences_even_with_equal_aggregate_inputs():
    from skillflow.doe.material import _paired_request_inputs
    sent = {"op": "deliver", "inputs": [["a", "b"]], "alternatives": [
        {"inputs": [["a"]], "outputs": [], "bindings": {"member": "0"}},
        {"inputs": [["b"]], "outputs": [], "bindings": {"member": "1"}}]}
    received = {"op": "receive", "inputs": [["a", "b"]], "alternatives": [
        {"inputs": [["a"]], "outputs": [["ra"]], "bindings": {"member": "0"}},
        {"inputs": [["b"]], "outputs": [["rb"]], "bindings": {"member": "1"}}]}
    assert _paired_request_inputs(sent, received)
    received["alternatives"][0]["bindings"] = {"member": "1"}
    received["alternatives"][1]["bindings"] = {"member": "0"}
    assert not _paired_request_inputs(sent, received)


def test_recursive_content_limit_is_scoped_to_producing_loop_not_independent_branch():
    from skillflow.propagation.contracts.limitations import diagnostic_applies
    data = {"family": _family("family", [{"form": "opaque"}])}
    tracked = _track(data, "family", [])
    tracked.engine.ops = {"loop_op": {"position": {"instruction_id": "ir_loop"},
                                     "record": {"outputs": [["family"]]}}}
    tracked.emit("family", {"declaration_id": "credential", "label": "credential", "property": "value",
        "path": ["next"] * (tracked.path_budget + 1), "excluded_paths": [], "relation": "direct"}, "finite_tail")
    diagnostic = next(row for row in tracked.diagnostics.values() if row["code"] == "sensitivity_path_limit")
    assert diagnostic["instruction_id"] == "ir_loop"
    assert diagnostic_applies(diagnostic, {"ir_loop", "ir_after_loop"})
    assert not diagnostic_applies(diagnostic, {"ir_independent"})
