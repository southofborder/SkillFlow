"""Lossless review display preserves typed values and physical obligations."""
from copy import deepcopy
import json

import pytest

from skillflow.common.prompt_format import compact_json
from skillflow.document_guided.review_display import (
    DISPLAY_IDENTITY, expand_review_payload, pack_review_payload,
)


def payload():
    reason = "Preserve the original selected field and its paired response. " * 20
    evidence = [{"file": "skill/源文.txt", "start_line": 3, "end_line": 7,
                 "reason": reason}]
    obligations = []
    for index in range(40):
        obligations.append({"id": f"obligation_{index}", "contract_id": f"contract_{index}",
            "instruction_id": f"ir_{index}", "operation": "receive" if index % 2 else "deliver",
            "target_id": f"annotation:/ir_semantics/ir_{index}/segments/0/ops/0",
            "request_pair_id": f"pair_{index // 2}", "scopes": [
                {"id": f"required_{index}", "kind": "required", "input_index": 0,
                 "information": {"property": "value", "path": ["profile", "name"]},
                 "effective": [{"property": "presence", "path": ["profile", "name"], "when": "always"},
                               {"property": "value", "path": ["profile", "name"], "when": "present"}],
                 "evidences": evidence, "reason": reason},
                {"id": f"remainder_{index}", "kind": "remainder", "input_index": 0,
                 "path": [], "excluded_paths": [["profile", "name"]], "reason": reason},
                {"id": f"unknown_{index}", "kind": "unresolved", "input_index": 1,
                 "information": {"property": "shape", "path": ["rows", "each"]},
                 "gap": {"code": "missing_field_meaning", "missing": "The role of the extra row field.",
                         "resolution": "Specify its contribution to the returned row count.",
                         "reason": reason, "evidences": evidence}},
                {"id": f"absence_{index}", "kind": "output", "optional": None},
                {"id": f"missing_{index}", "kind": "output"},
            ]})
    return {"input_contract_inventory": {"available": True, "obligations": obligations,
                "projections": [{"id": "projection_1", "request_pair_id": "pair_0",
                    "returned_range": {"property": "value", "path": ["profile", "name"]},
                    "selection_parameter_path": ["fields"], "reason": reason, "evidences": evidence}]},
            "annotation": {"literal": {"id": "original", "reason": reason}, "ordered": [3, 1, 3]},
            "task": {"requirements": [{"id": "R1", "text": reason, "evidences": evidence}]},
            "observations": [{"input_index": 0, "receiver": "recipient_A", "reason": reason}],
            "availability": {"annotation": True}, "fragments": {}, "partial": False}


def test_round_trip_retains_every_obligation_scope_evidence_and_occurrence():
    original = payload()
    before = deepcopy(original)
    display = pack_review_payload(original)
    display_before = deepcopy(display)
    restored = expand_review_payload(display)
    assert display["format"] == DISPLAY_IDENTITY
    assert compact_json(restored) == compact_json(before)
    assert original == before and display == display_before
    assert len(compact_json(display)) < len(compact_json(original))
    rows = restored["input_contract_inventory"]["obligations"]
    assert len(rows) == 40 and len({row["id"] for row in rows}) == 40
    assert {scope["id"] for row in rows for scope in row["scopes"]} == {
        f"{kind}_{index}" for index in range(40)
        for kind in ("required", "remainder", "unknown", "absence", "missing")}
    assert rows[0]["request_pair_id"] == rows[1]["request_pair_id"]
    assert rows[0]["contract_id"] != rows[1]["contract_id"]
    assert "optional" in rows[0]["scopes"][3] and "optional" not in rows[0]["scopes"][4]
    # Shared display values must not turn reconstructed occurrences into mutable aliases.
    rows[0]["scopes"][0]["evidences"][0]["reason"] = "Changed one occurrence."
    assert rows[1]["scopes"][0]["evidences"][0]["reason"] == before["input_contract_inventory"]["obligations"][1]["scopes"][0]["evidences"][0]["reason"]


def test_shared_values_keep_types_near_duplicates_and_order():
    values = [False, 0, True, 1, 1.0, None, "1", "false", "0", [0, False], [False, 0]]
    variants = [{"value": value, "reason": "Repeated exact source evidence. " * 15} for value in values]
    original = {"rows": variants * 12,
                "conditions": [{"receiver": receiver, "version": version, "if_present": optional,
                    "path": path, "evidences": [{"start_line": line, "end_line": line}]} 
                    for receiver, version, optional, path, line in [
                        ("one", 1, True, ["a"], 2), ("two", 1, True, ["a"], 2),
                        ("one", 2, True, ["a"], 2), ("one", 1, False, ["a"], 2),
                        ("one", 1, True, ["b"], 2), ("one", 1, True, ["a"], 3)]]}
    restored = expand_review_payload(pack_review_payload(original))
    assert compact_json(restored) == compact_json(original)
    assert [type(row["value"]) for row in restored["rows"][:len(values)]] == [type(v) for v in values]
    assert restored["conditions"] == original["conditions"]


def test_nested_display_and_reference_shaped_content_remain_literal():
    prior = pack_review_payload(payload())
    original = {"literal_display": deepcopy(prior),
        "literal_objects": [{"$ref": 0}, {"$ref": "v0", "actual": "source literal"},
                            {"$rows": [[0, "literal"]]}, {"$literal_object": [["key", "literal"]]},
                            {"ref": "value_0"}, {"format": DISPLAY_IDENTITY},
                            {"$review_ref": 0}, {"$shared": "s0"}, {"@": 0}],
        "literal_strings": ["$ref", "value_0", "INPUT_JSON\nCOMPLETE SOURCE\n",
            "保留原文🌍\r\n\"quoted\"\t\\", "Same literal. " * 500] * 4}
    restored = expand_review_payload(pack_review_payload(original))
    assert compact_json(restored) == compact_json(original)
    assert restored["literal_display"]["format"] == DISPLAY_IDENTITY


def test_packing_is_deterministic_and_preserves_original_object_key_order():
    def reverse_keys(value):
        if isinstance(value, dict):
            return {key: reverse_keys(value[key]) for key in reversed(list(value))}
        if isinstance(value, list):
            return [reverse_keys(item) for item in value]
        return value
    original = payload()
    reversed_payload = reverse_keys(original)
    a, b = pack_review_payload(original), pack_review_payload(reversed_payload)
    assert compact_json(a) == compact_json(pack_review_payload(deepcopy(original)))
    assert compact_json(expand_review_payload(a)) == compact_json(original)
    assert compact_json(expand_review_payload(b)) == compact_json(reversed_payload)


@pytest.mark.parametrize("value", [None, [], "text", {"format": "unknown-display"}])
def test_decoder_rejects_invalid_display_envelopes(value):
    with pytest.raises((ValueError, TypeError)):
        expand_review_payload(value)


@pytest.mark.parametrize("change", [
    "extra_key", "missing_reference", "cyclic_reference", "nonstring_reference", "mixed_marker",
    "unknown_marker", "boolean_column_index", "missing_column_index", "row_width", "duplicate_columns",
    "duplicate_literal_keys",
])
def test_malformed_explicit_references_and_tables_fail_closed(change):
    display = {"format": DISPLAY_IDENTITY, "record_columns": [["id", "kind"]],
               "shared_values": {}, "payload": {}}
    if change == "extra_key":
        display["ignored"] = "A material field must not silently disappear."
    elif change == "missing_reference":
        display["payload"] = {"$ref": "absent"}
    elif change == "cyclic_reference":
        display["shared_values"] = {"v0": {"$ref": "v1"}, "v1": {"$ref": "v0"}}
        display["payload"] = {"$ref": "v0"}
    elif change == "nonstring_reference":
        display["payload"] = {"$ref": 0}
    elif change == "mixed_marker":
        display["payload"] = {"$ref": "v0", "kind": "literal_or_reference"}
    elif change == "unknown_marker":
        display["payload"] = {"$rows": [], "$literal_object": []}
    elif change == "boolean_column_index":
        display["payload"] = {"$rows": [[False, "a", "required"]]}
    elif change == "missing_column_index":
        display["payload"] = {"$rows": [[4, "a", "required"]]}
    elif change == "row_width":
        display["payload"] = {"$rows": [[0, "a"]]}
    elif change == "duplicate_columns":
        display["record_columns"] = [["id", "id"]]
        display["payload"] = {"$rows": [[0, "a", "b"]]}
    elif change == "duplicate_literal_keys":
        display["payload"] = {"$literal_object": [["x", 1], ["x", 2]]}
    with pytest.raises((ValueError, TypeError)):
        expand_review_payload(display)


def test_repeated_source_shaped_literals_are_not_normalized_or_translated():
    text = "First line.\r\n\r\n原始引文🌍\nlast line with trailing spaces  \r\n"
    original = {"files": {"skill/原文.txt": text}, "duplicates": [text] * 20,
                "evidence": [{"reason": text, "quote": text}] * 20}
    restored = expand_review_payload(pack_review_payload(original))
    assert restored["files"]["skill/原文.txt"].encode("utf-8") == text.encode("utf-8")
    assert json.dumps(restored, ensure_ascii=False, sort_keys=True) == json.dumps(original, ensure_ascii=False, sort_keys=True)


@pytest.mark.parametrize("count", [0, 1, 7, 67])
def test_small_or_nonrepeating_values_retain_every_record_without_assuming_compression(count):
    original = {"arbitrary_skill": f"fixture_{count}", "records": [
        {f"key_{index}": f"unique value {index}", "number": index} for index in range(count)]}
    display = pack_review_payload(original)
    plain = {"format": DISPLAY_IDENTITY, "record_columns": [], "shared_values": {}, "payload": original}
    assert compact_json(expand_review_payload(display)) == compact_json(original)
    assert len(compact_json(display)) <= len(compact_json(plain))
