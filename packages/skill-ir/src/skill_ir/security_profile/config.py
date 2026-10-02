"""Explicit JSON Output configuration for the joint annotation stage only."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import overload

from skill_ir.llm.config import LlmConfig


PUBLIC_CONFIG_FIELDS = (
    "endpoint", "model", "reasoning_effort", "timeout_ms", "max_retries",
    "retry_base_ms", "retry_max_backoff_ms", "response_format",
)


@overload
def annotation_config(base: LlmConfig) -> LlmConfig: ...


@overload
def annotation_config(base: Mapping[str, object]) -> dict: ...


def annotation_config(base: LlmConfig | Mapping[str, object]) -> LlmConfig | dict:
    """Derive a separate config without mutating or silently overriding a caller.

    This is a stage policy, not an environment default. Extraction and semantic
    auditing continue to use the unmodified base configuration.
    """
    current = base.response_format if isinstance(base, LlmConfig) else base.get("response_format")
    if current not in (None, "json_object"):
        raise ValueError("Joint annotation requires response_format='json_object'")
    if isinstance(base, LlmConfig):
        return replace(base, response_format="json_object")
    return {**base, "response_format": "json_object"}


def annotation_public_config(base: LlmConfig) -> dict:
    config = annotation_config(base)
    return {key: getattr(config, key) for key in PUBLIC_CONFIG_FIELDS}
