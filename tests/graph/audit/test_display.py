"""Compact display preserves graph evidence; it is not another Lean proof."""
from copy import deepcopy
import json

import pytest

from skillflow.graph.audit.display import audit_display, compact_facts


def unit(ref, body, *, basis="explicit_graph", graph_ref=None):
    def term(value):
        if isinstance(value, list):
            return '[' + ' '.join(term(item) for item in value) + ']'
        return json.dumps(value, ensure_ascii=False)
    identity = "fact:" + ref
    return {"id": identity, "basis": basis, "graph_refs": [graph_ref or ref],
            "text": term(["certified record", identity, ref, body])}


def test_metadata_decoding_and_exact_code_reference_do_not_rewrite_audit():
    source = {"files": [{"path": "module.py", "content": "# header\r\nprint('中文')\r\n"}]}
    code = "print('中文')\r\n"
    metadata = {"script_content": code, "other": {"condition": "uninterpreted"}}
    item = unit("/blocks/0/instructions/0/metadata_json", json.dumps(metadata), basis="embedded_content")
    document = {"method": "controlled", "units": [item], "derived_links": []}
    original = deepcopy((source, document))
    view = audit_display(source, document)
    assert view["controlled_facts"] == [{"id": item["id"], "basis": "embedded_content", "value": {
        "script_content": {"exact_source_copy": {"file": "module.py", "start_line": 2, "end_line": 2}},
        "other": {"condition": "uninterpreted"}}}]
    assert ''.join(row[1] for row in view["source_files"][0]["lines"]) == source["files"][0]["content"]
    assert (source, document) == original


def test_partial_line_or_changed_code_is_not_replaced():
    source = {"files": [{"path": "module.py", "content": "result = call()\n"}]}
    for code in ("call()", "result = call()", "result=call()\n"):
        item = unit("/blocks/0/instructions/0/metadata_json", json.dumps({"script_content": code}))
        assert compact_facts(source, {"units": [item]})[0]["value"]["script_content"] == code


def test_context_and_literal_contents_are_not_optional_structure():
    source = {"files": []}
    contexts = unit("/contexts", ["未记录"])
    literal = unit("/blocks/0/instructions/0/inputs/0/literal_json", ["记录值", json.dumps(["未记录"])])
    assert [f["value"] for f in compact_facts(source, {"units": [contexts, literal]})] == [["未记录"], ["未记录"]]


def test_definition_links_keep_exact_certified_versions():
    link = {"identifier": "r1", "use_ref": "/blocks/b/instructions/1/inputs/0",
            "definition_ref": "/blocks/b/instructions/0/outputs/0"}
    item = {"id": "fact:/blocks/0/instructions/1/inputs/0:link", "basis": "explicit_graph",
            "graph_refs": [link["use_ref"]], "text": "not needed: verified link already supplied"}
    assert compact_facts({"files": []}, {"units": [item], "derived_links": [link]})[0]["value"] == link


def test_unrecognized_certified_text_or_changed_id_is_rejected():
    item = unit("/entry", "block_1")
    item["id"] = "different"
    with pytest.raises(ValueError, match="identity mismatch"):
        compact_facts({"files": []}, {"method": "controlled", "units": [item]})
    item["text"] = "not a certified record"
    with pytest.raises(ValueError, match="Unsupported certified"):
        compact_facts({"files": []}, {"method": "controlled", "units": [item]})
