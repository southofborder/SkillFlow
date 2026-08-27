"""LLM layer: transport (HTTP POST + retry) and response normalizers.

Faithful Python port of shared/llm-utils.cjs. The normalizers are behavioral
spec — they must not drift from the JS versions, since the golden acceptance
oracle replays the same cached LLM responses through both engines.
"""
