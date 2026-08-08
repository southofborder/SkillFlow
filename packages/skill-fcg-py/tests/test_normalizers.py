"""Lock the LLM-response normalizers to the JS spec (shared/llm-utils.cjs).

These are behavioral-spec ports; the golden oracle replays the same cached LLM
responses through both engines, so any drift here surfaces as a DOE verdict
flip. Cases mirror the JS branches (fallbacks, keyword maps, clamps, round6).
"""

from skill_fcg.llm import normalizers as N


class TestNormalizeAssistantContent:
    def test_string_passthrough(self):
        assert N.normalize_assistant_content("hello") == "hello"

    def test_list_of_parts(self):
        content = ["a", {"text": "b"}, {"content": "c"}, {"other": 1}, 5]
        # 5 is not str/dict-with-text -> "" ; number path -> "" per JS map fn.
        assert N.normalize_assistant_content(content) == "a\nb\nc\n\n"

    def test_dict_stringified_compact(self):
        assert N.normalize_assistant_content({"a": 1}) == '{"a":1}'

    def test_other_returns_empty(self):
        assert N.normalize_assistant_content(None) == ""
        assert N.normalize_assistant_content(42) == ""


class TestParseLooseJson:
    def test_dict_passthrough(self):
        assert N.parse_loose_json({"x": 1}) == {"x": 1}

    def test_plain_json(self):
        assert N.parse_loose_json('{"a": 2}') == {"a": 2}

    def test_fenced_block(self):
        raw = 'noise\n```json\n{"a": 3}\n```\ntrailing'
        assert N.parse_loose_json(raw) == {"a": 3}

    def test_object_like_slice(self):
        assert N.parse_loose_json('prefix {"a": 4} suffix') == {"a": 4}

    def test_empty_and_garbage(self):
        assert N.parse_loose_json("") is None
        assert N.parse_loose_json("not json at all") is None


class TestNormalizeBoolean:
    def test_bool_passthrough(self):
        assert N.normalize_boolean(True) is True
        assert N.normalize_boolean(False) is False

    def test_numbers(self):
        assert N.normalize_boolean(1) is True
        assert N.normalize_boolean(0) is False

    def test_tokens(self):
        for t in ("true", "yes", "y", "1", "agree", "agrees", "YES"):
            assert N.normalize_boolean(t) is True
        for t in ("false", "no", "n", "0", "disagree", "disagrees"):
            assert N.normalize_boolean(t) is False

    def test_fallback(self):
        assert N.normalize_boolean("maybe") is False
        assert N.normalize_boolean("maybe", True) is True


class TestNormalizeScaledNumber:
    def test_numeric_clamped(self):
        assert N.normalize_scaled_number(0.5) == 0.5
        assert N.normalize_scaled_number(2.0) == 1.0
        assert N.normalize_scaled_number(-1.0) == 0.0

    def test_map_lookup(self):
        assert N.normalize_scaled_number("high", map={"high": 0.8}) == 0.8

    def test_numeric_string(self):
        assert N.normalize_scaled_number("0.3") == 0.3

    def test_fallback_on_empty_and_unknown(self):
        assert N.normalize_scaled_number("", fallback=0.5) == 0.5
        assert N.normalize_scaled_number("weird", fallback=0.25) == 0.25

    def test_custom_range(self):
        assert N.normalize_scaled_number(50, min=0, max=100) == 50


class TestNormalizeSeverity:
    def test_canonical(self):
        assert N.normalize_severity("crit") == "critical"
        assert N.normalize_severity("major") == "high"
        assert N.normalize_severity("moderate") == "medium"
        assert N.normalize_severity("minor") == "low"

    def test_unknown_and_empty(self):
        assert N.normalize_severity("") == ""
        assert N.normalize_severity("nope") == ""


class TestCompositeResults:
    def test_similarity_result(self):
        out = N.normalize_similarity_result('{"similarity": "very_high", "reason": "r"}')
        assert out["similarity"] == 0.9
        assert out["reason"] == "r"
        assert out["has_contradiction"] is False

    def test_similarity_fallback_keys(self):
        out = N.normalize_similarity_result('{"score": 0.42}')
        assert out["similarity"] == 0.42

    def test_similarity_non_object(self):
        assert N.normalize_similarity_result("garbage") is None

    def test_validation_result_defaults(self):
        out = N.normalize_validation_result('{"is_compatible": "yes"}')
        assert out["is_compatible"] is True
        assert out["confidence"] == 0.5
        assert out["reason"] == "LLM semantic validation"
        assert out["data_flow_description"] == "Data flows from source to target"

    def test_review_result(self):
        out = N.normalize_review_result('{"agrees": "y", "confidence": "high", "suggested_severity": "major"}')
        assert out["agrees"] is True
        assert out["confidence"] == 0.85
        assert out["suggested_severity"] == "high"
