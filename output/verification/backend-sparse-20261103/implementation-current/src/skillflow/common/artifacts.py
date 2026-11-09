"""Secret-free durable artifacts and descriptive call metrics."""
from __future__ import annotations

import json
from pathlib import Path

from skillflow.common.artifact_io import atomic_write_text


class ArtifactWriter:
    def __init__(self, secrets: tuple[str, ...]):
        self.secrets = secrets

    def clean(self, value):
        if isinstance(value, str):
            for secret in self.secrets:
                value = value.replace(secret, "[REDACTED]")
            return value
        if isinstance(value, dict):
            return {self.clean(key): self.clean(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [self.clean(item) for item in value]
        return value

    def text(self, path: Path, value: str) -> None:
        atomic_write_text(path, self.clean(value))

    def json(self, path: Path, value) -> None:
        self.text(
            path, json.dumps(self.clean(value), ensure_ascii=False, indent=2) + "\n"
        )


def call_metrics(calls: list[dict]) -> dict:
    attempts = [attempt for call in calls for attempt in call["http_attempts"]]
    usages = [
        attempt["usage"]
        for attempt in attempts
        if isinstance(attempt.get("usage"), dict)
    ]
    totals = {}
    for target, alternatives in {
        "input_tokens": ("input_tokens", "prompt_tokens"),
        "output_tokens": ("output_tokens", "completion_tokens"),
        "total_tokens": ("total_tokens",),
    }.items():
        known = [
            next(
                (usage[key] for key in alternatives if type(usage.get(key)) is int),
                None,
            )
            for usage in usages
        ]
        known = [value for value in known if value is not None]
        totals[target] = sum(known) if known else None
    return {
        "generation_attempts": len(calls),
        "repair_attempts": max(0, len(calls) - 1),
        "http_attempts": len(attempts),
        "http_retries": sum(max(0, len(call["http_attempts"]) - 1) for call in calls),
        "usage_records": len(usages),
        "known_token_usage": totals,
    }


