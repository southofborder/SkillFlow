"""Mirror of test/semantic-gate-usage.test.js — token-usage accounting."""

from skill_fcg.parser.doc_flow_extractor import (
    new_semantic_gate_usage,
    accumulate_semantic_gate_usage,
    summarize_semantic_gate_usage,
)


def test_accumulates_openai_style_usage_with_cached_tokens_details():
    acc = new_semantic_gate_usage()
    accumulate_semantic_gate_usage(acc, {
        "prompt_tokens": 2546,
        "completion_tokens": 1697,
        "total_tokens": 4243,
        "prompt_tokens_details": {"cached_tokens": 2304},
    })
    assert acc["calls"] == 1
    assert acc["prompt_tokens"] == 2546
    assert acc["completion_tokens"] == 1697
    assert acc["total_tokens"] == 4243
    assert acc["cached_tokens"] == 2304


def test_accepts_alternate_cached_token_field_names():
    a = new_semantic_gate_usage()
    accumulate_semantic_gate_usage(a, {"prompt_tokens": 100, "cached_tokens": 40})
    assert a["cached_tokens"] == 40

    b = new_semantic_gate_usage()
    accumulate_semantic_gate_usage(b, {"prompt_tokens": 100, "prompt_cache_hit_tokens": 55})
    assert b["cached_tokens"] == 55

    c = new_semantic_gate_usage()
    accumulate_semantic_gate_usage(c, {"input_tokens": 80, "output_tokens": 20})
    assert c["prompt_tokens"] == 80
    assert c["completion_tokens"] == 20


def test_sums_usage_across_multiple_calls():
    acc = new_semantic_gate_usage()
    accumulate_semantic_gate_usage(acc, {"prompt_tokens": 1000, "prompt_tokens_details": {"cached_tokens": 900}})
    accumulate_semantic_gate_usage(acc, {"prompt_tokens": 1000, "prompt_tokens_details": {"cached_tokens": 0}})
    assert acc["calls"] == 2
    assert acc["prompt_tokens"] == 2000
    assert acc["cached_tokens"] == 900


def test_ignores_missing_invalid_usage_payloads_without_throwing():
    acc = new_semantic_gate_usage()
    accumulate_semantic_gate_usage(acc, None)
    accumulate_semantic_gate_usage(acc, None)
    accumulate_semantic_gate_usage(acc, "not-an-object")
    assert acc["calls"] == 0


def test_summarize_computes_cache_hit_ratio_and_none_for_no_calls():
    assert summarize_semantic_gate_usage(new_semantic_gate_usage()) is None

    acc = new_semantic_gate_usage()
    accumulate_semantic_gate_usage(acc, {"prompt_tokens": 2000, "prompt_tokens_details": {"cached_tokens": 900}})
    summary = summarize_semantic_gate_usage(acc)
    assert summary["prompt_cache_hit_ratio"] == 0.45
    assert summary["calls"] == 1
