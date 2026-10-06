"""LLM configuration and environment-file loading."""

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass, field


OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"


class LlmClientError(RuntimeError):
    """Raised when an LLM request cannot be completed."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after_ms: int | None = None,
        transient: bool = False,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after_ms = retry_after_ms
        self.transient = transient


class LlmConfigError(LlmClientError):
    """Raised when required LLM configuration is missing or invalid."""


@dataclass(frozen=True)
class LlmConfig:
    api_key: str = field(repr=False)
    endpoint: str = OPENAI_ENDPOINT
    model: str = "gpt-5.6-sol"
    reasoning_effort: str = "max"
    timeout_ms: int = 600000
    max_retries: int = 2
    retry_base_ms: int = 500
    retry_max_backoff_ms: int = 8000

    def __post_init__(self) -> None:
        if self.reasoning_effort not in {
            "none",
            "low",
            "medium",
            "high",
            "xhigh",
            "max",
        }:
            raise LlmConfigError("Invalid LLM_REASONING_EFFORT")

    @classmethod
    def from_env(
        cls,
        environ: dict[str, str] | None = None,
        *,
        env_file: str | Path | None = None,
    ) -> "LlmConfig":
        values = load_environment(environ=environ, env_file=env_file)

        def positive_int(name: str, default: int, *, allow_zero: bool = False) -> int:
            try:
                value = int(values.get(name, default))
            except (TypeError, ValueError):
                return default
            if value > 0 or (allow_zero and value == 0):
                return value
            return default

        return cls(
            api_key=str(values.get("LLM_API_KEY", "")).strip(),
            endpoint=str(values.get("LLM_ENDPOINT", "")).strip() or cls.endpoint,
            model=str(values.get("LLM_MODEL", "")).strip() or cls.model,
            reasoning_effort=str(values.get("LLM_REASONING_EFFORT", "")).strip()
            or cls.reasoning_effort,
            timeout_ms=positive_int("LLM_TIMEOUT", cls.timeout_ms),
            max_retries=positive_int(
                "LLM_MAX_RETRIES", cls.max_retries, allow_zero=True
            ),
            retry_base_ms=positive_int("LLM_RETRY_BASE_MS", cls.retry_base_ms),
            retry_max_backoff_ms=positive_int(
                "LLM_RETRY_MAX_BACKOFF_MS", cls.retry_max_backoff_ms
            ),
        )


def load_environment(
    *, environ: dict[str, str] | None = None, env_file: str | Path | None = None
) -> dict[str, str]:
    """Resolve settings once, without modifying the process environment.

    An explicit mapping bypasses discovery, but may override an explicit file.
    An explicit file never falls back to another project's credentials.
    """
    env_path = (
        Path(env_file).expanduser().resolve()
        if env_file is not None
        else (_find_nearest_env() if environ is None else None)
    )
    file_values = {}
    if env_path is not None:
        file_values = dict(_parse_env_file(env_path.read_text(encoding="utf-8-sig")))
    return {**file_values, **(os.environ if environ is None else environ)}


def _find_nearest_env() -> Path | None:
    start_paths = [Path.cwd(), Path(__file__).resolve().parent]
    visited: set[Path] = set()
    for start_path in start_paths:
        current = start_path if start_path.is_dir() else start_path.parent
        for directory in (current, *current.parents):
            if directory in visited:
                continue
            visited.add(directory)
            candidate = directory / ".env"
            if candidate.is_file():
                return candidate
    return None


def _parse_env_file(content: str) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise LlmConfigError(f"Malformed .env line {line_number}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not all(
            character.isalnum() or character == "_" for character in key
        ):
            raise LlmConfigError(f"Malformed .env line {line_number}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        else:
            comment_index = value.find(" #")
            if comment_index >= 0:
                value = value[:comment_index].rstrip()
        value = (
            value.replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\'", "'")
        )
        values.append((key, value))
    return values
