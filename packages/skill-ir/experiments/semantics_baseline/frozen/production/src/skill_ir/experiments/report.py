"""Secret-free, atomic experiment artifacts and descriptive metrics."""

from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
from statistics import mean
from uuid import uuid4


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
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        try:
            temporary.write_text(self.clean(value), encoding="utf-8")
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

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


def aggregate(trials: list[dict]) -> dict:
    attempted = [
        trial for trial in trials if trial["status"] not in {"not_run", "running"}
    ]
    complete = [trial for trial in attempted if trial["status"] == "complete"]
    first = [trial for trial in complete if trial.get("generation_attempts") == 1]
    elapsed = [
        trial["elapsed_seconds"]
        for trial in attempted
        if trial.get("elapsed_seconds") is not None
    ]
    tokens = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        known = [trial.get("known_token_usage", {}).get(key) for trial in attempted]
        known = [value for value in known if value is not None]
        tokens[key] = sum(known) if known else None
    return {
        "planned": len(trials),
        "attempted": len(attempted),
        "complete": len(complete),
        "structural_pass_rate": len(complete) / len(attempted) if attempted else None,
        "first_pass_rate": len(first) / len(attempted) if attempted else None,
        "mean_elapsed_seconds": mean(elapsed) if elapsed else None,
        **{
            key: sum(trial.get(key, 0) for trial in attempted)
            for key in (
                "generation_attempts",
                "repair_attempts",
                "http_attempts",
                "http_retries",
                "usage_records",
            )
        },
        "known_token_usage": tokens,
    }


def write_progress(directory: Path, report: dict, writer: ArtifactWriter) -> None:
    report["summary"] = aggregate(report["trials"])
    report["by_variant"] = {
        variant: aggregate(
            [trial for trial in report["trials"] if trial["variant"] == variant]
        )
        for variant in dict.fromkeys(trial["variant"] for trial in report["trials"])
    }
    writer.json(directory / "report.json", report)
    fields = [
        "case",
        "variant",
        "repetition",
        "status",
        "generation_attempts",
        "repair_attempts",
        "http_attempts",
        "http_retries",
        "elapsed_seconds",
        "blocks",
        "edges",
        "diagnostics",
        "error",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "usage_records",
    ]
    output = io.StringIO(newline="")
    rows = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    rows.writeheader()
    for trial in report["trials"]:
        row = {**trial, **trial.get("known_token_usage", {})}
        row["diagnostics"] = json.dumps(
            trial.get("diagnostics", []), ensure_ascii=False
        )
        rows.writerow(writer.clean(row))
    writer.text(directory / "summary.csv", output.getvalue())
