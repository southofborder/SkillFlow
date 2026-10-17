"""Generated format references preserve schema information, not semantic proofs."""
import json
from copy import deepcopy

import pytest
from pydantic import TypeAdapter

from skillflow.common.prompt_format import compact_json, prompt_block, render_prompt_format
from skillflow.propagation.contracts.profiles import RawAnnotationResponse, FailureResponse
from skillflow.propagation.contracts.task import CandidateTask
from skillflow.propagation.review.models import RESPONSE_ADAPTER
from skillflow.task.services import _FailureResponse


def schemas():
    return [TypeAdapter(RawAnnotationResponse | FailureResponse).json_schema(),
            RESPONSE_ADAPTER.json_schema(), TypeAdapter(CandidateTask | _FailureResponse).json_schema()]


@pytest.mark.parametrize("schema", schemas())
def test_current_formats_preserve_all_fields_limits_tags_and_named_definitions(schema):
    before = deepcopy(schema)
    rendered = render_prompt_format(schema)
    assert schema == before
    assert len(rendered) < len(compact_json(schema))
    for name in schema["$defs"]:
        assert rendered.count("\n" + name + " = ") == 1

    def check(node):
        if not isinstance(node, dict):
            return
        for key, value in node.items():
            if key in ("properties", "patternProperties", "$defs"):
                for name, child in value.items():
                    if key == "properties":
                        assert compact_json(name) + (":" if name in node.get("required", []) else "?:") in rendered
                    if key == "patternProperties":
                        assert "/" + compact_json(name) + "/:" in rendered
                    check(child)
            elif key in ("anyOf", "oneOf", "allOf", "prefixItems"):
                for child in value:
                    check(child)
            elif key in ("items", "additionalProperties"):
                check(value)
            elif key in ("enum", "const", "default", "minimum", "minLength", "minItems", "pattern"):
                assert key + "=" + compact_json(value) in rendered
            elif key == "description":
                assert "meaning=" + compact_json(value) in rendered
            elif key == "discriminator":
                assert "tag=" + compact_json(value["propertyName"]) in rendered
    check(schema)


@pytest.mark.parametrize("node", [
    {"type": "string", "format": "date"}, {"not": {"type": "null"}},
    {"additionalProperties": False}, {"type": ["object", "null"], "properties": {}},
    {"type": "string", "items": {}}, {"$ref": "https://example.test/schema"},
    {"$ref": "#/$defs/Absent"}, {"type": "bad-type"},
    {"type": "object", "properties": {"x": {"$defs": {}}}},
    {"discriminator": {"propertyName": "kind", "extra": 1}},
])
def test_unknown_keywords_references_and_unsupported_combinations_fail_closed(node):
    with pytest.raises(ValueError):
        render_prompt_format(node)


def test_optional_null_defaults_constraints_and_extra_keys_are_distinct():
    schema = {"type": "object", "required": ["mandatory"], "additionalProperties": False,
              "properties": {
                  "mandatory": {"anyOf": [{"type": "string", "maxLength": 3}, {"type": "null"}]},
                  "optional": {"type": "integer", "default": 4, "minimum": 1, "maximum": 5},
                  "values": {"type": "array", "items": {"type": "number", "multipleOf": 0.5}, "uniqueItems": True},
              }}
    rendered = render_prompt_format(schema)
    assert '"mandatory":ANY(' in rendered and '"optional"?:integer' in rendered
    assert "extra:FORBIDDEN" in rendered
    for term in ("default=4", "minimum=1", "maximum=5", "maxLength=3", "multipleOf=0.5", "uniqueItems=true"):
        assert term in rendered


def test_prompt_sections_are_unambiguous_and_json_can_be_extracted_losslessly():
    payload = {"text": "source remains data", "values": [None, True, 1]}
    section = prompt_block("INPUT", "INPUT_JSON\n" + compact_json(payload))
    assert section.startswith("<!-- SKILLFLOW_PROMPT:INPUT:BEGIN -->\n")
    assert section.endswith("\n<!-- SKILLFLOW_PROMPT:INPUT:END -->")
    assert json.JSONDecoder().raw_decode(section.split("INPUT_JSON\n")[1])[0] == payload
    with pytest.raises(ValueError):
        prompt_block("bad:name", "data")
