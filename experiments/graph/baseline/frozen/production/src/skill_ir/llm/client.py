"""OpenAI-compatible HTTP transport with bounded retries."""

from __future__ import annotations

import json
import random
import time
from datetime import datetime, timezone
import urllib.error
import urllib.request
from email.utils import parsedate_to_datetime
from typing import Any, Callable
from .config import LlmConfig, LlmClientError, LlmConfigError


def _parse_retry_after(value: str | None) -> int | None:
    if not value:
        return None
    try:
        seconds = float(value)
        if seconds >= 0:
            return round(seconds * 1000)
    except ValueError:
        pass
    try:
        timestamp = parsedate_to_datetime(value).timestamp()
    except (TypeError, ValueError, OverflowError):
        return None
    return max(0, int((timestamp - time.time()) * 1000))


def _is_transient_status(status_code: int) -> bool:
    return status_code == 429 or 500 <= status_code <= 599


def _normalize_content(content: Any) -> Any:
    if isinstance(content, (str, dict)):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
        return "\n".join(parts)
    return ""


class LlmClient:
    """OpenAI-compatible chat completion client with bounded transient retries."""

    def __init__(
        self,
        config: LlmConfig | None = None,
        *,
        sleep: Callable[[float], None] = time.sleep,
        random_value: Callable[[], float] = random.random,
        record_calls: bool = False,
        on_record: Callable[[list[dict[str, Any]]], None] | None = None,
    ) -> None:
        self.config = config or LlmConfig.from_env()
        if not self.config.api_key:
            raise LlmConfigError(
                "LLM_API_KEY is required for LLM analysis; "
                "set it in the process environment or project .env."
            )
        self._sleep = sleep
        self._random = random_value
        self.call_records: list[dict[str, Any]] = []
        self._record_calls = record_calls
        self._on_record = on_record
        self._active_call: dict[str, Any] | None = None
        self._active_http: dict[str, Any] | None = None

    def complete(self, prompt: str) -> Any:
        """Send one prompt and return the assistant message content."""

        if not self._record_calls:
            return self._complete(prompt)
        started = time.perf_counter()
        record = {
            "generation": len(self.call_records) + 1,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "running",
            "prompt": prompt,
            "response": None,
            "returned_model": None,
            "usage": None,
            "request_id": None,
            "http_attempts": [],
        }
        self.call_records.append(record)
        self._active_call = record
        try:
            self._notify()
            result = self._complete(prompt)
            record.update(status="complete", response=result)
            last = record["http_attempts"][-1]
            for key in ("returned_model", "usage", "request_id"):
                record[key] = last.get(key)
            return result
        except BaseException as error:
            record.update(
                status=(
                    "interrupted" if isinstance(error, KeyboardInterrupt) else "error"
                ),
                error=str(error),
                error_type=type(error).__name__,
            )
            raise
        finally:
            record["elapsed_seconds"] = time.perf_counter() - started
            self._active_call = None
            self._notify()

    def _notify(self) -> None:
        if self._on_record is not None:
            self._on_record(self.call_records)

    def _recorded_post(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._active_call is None:
            return self._post_once(payload)
        attempt = {
            "status": "running",
            "http_status": None,
            "request_id": None,
            "returned_model": None,
            "usage": None,
            "raw_response": None,
        }
        self._active_call["http_attempts"].append(attempt)
        self._active_http = attempt
        started = time.perf_counter()
        try:
            self._notify()
            response = self._post_once(payload)
            attempt.update(
                status="complete",
                raw_response=response,
                returned_model=response.get("model"),
                usage=response.get("usage"),
            )
            return response
        except BaseException as error:
            attempt.update(
                status=(
                    "interrupted" if isinstance(error, KeyboardInterrupt) else "error"
                ),
                error=str(error),
                error_type=type(error).__name__,
            )
            if isinstance(error, LlmClientError):
                attempt["http_status"] = error.status_code
            raise
        finally:
            attempt["elapsed_seconds"] = time.perf_counter() - started
            self._active_http = None
            self._notify()

    def _complete(self, prompt: str) -> Any:

        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "reasoning_effort": self.config.reasoning_effort,
        }
        attempt = 0
        while True:
            try:
                response = self._recorded_post(payload)
                return self._extract_content(response)
            except LlmClientError as error:
                if not error.transient or attempt >= self.config.max_retries:
                    raise
                backoff = min(
                    self.config.retry_max_backoff_ms,
                    self.config.retry_base_ms * (2**attempt),
                )
                jitter = round(backoff * 0.25 * self._random())
                wait_ms = backoff + jitter
                if error.retry_after_ms is not None:
                    wait_ms = (
                        min(self.config.retry_max_backoff_ms, error.retry_after_ms)
                        + jitter
                    )
                attempt += 1
                self._sleep(wait_ms / 1000)

    def _post_once(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self.config.endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Content-Length": str(len(body)),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.config.timeout_ms / 1000
            ) as response:
                status = int(response.status)
                text = response.read().decode("utf-8", errors="replace")
                if self._active_http is not None:
                    self._active_http.update(
                        http_status=status,
                        raw_response=text,
                        request_id=(getattr(response, "headers", None) or {}).get(
                            "x-request-id"
                        ),
                    )
                if status < 200 or status >= 300:
                    raise LlmClientError(
                        f"LLM HTTP {status}: {text}",
                        status_code=status,
                        transient=_is_transient_status(status),
                    )
                return self._decode_json(text)
        except urllib.error.HTTPError as error:
            text = error.read().decode("utf-8", errors="replace") if error.fp else ""
            headers = error.headers or {}
            if self._active_http is not None:
                self._active_http.update(
                    raw_response=text,
                    http_status=error.code,
                    request_id=headers.get("x-request-id"),
                )
            retry_after = _parse_retry_after(headers.get("Retry-After"))
            raise LlmClientError(
                f"LLM HTTP {error.code}: {text}",
                status_code=error.code,
                retry_after_ms=retry_after,
                transient=_is_transient_status(error.code),
            ) from error
        except (TimeoutError, OSError, urllib.error.URLError) as error:
            raise LlmClientError(
                f"LLM network request failed: {error}",
                transient=True,
            ) from error

    @staticmethod
    def _decode_json(text: str) -> dict[str, Any]:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise LlmClientError(f"LLM response was not JSON: {error}") from error
        if not isinstance(payload, dict):
            raise LlmClientError("LLM response JSON must be an object")
        return payload

    @staticmethod
    def _extract_content(payload: dict[str, Any]) -> Any:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LlmClientError("LLM response has no choices[0]")
        first = choices[0]
        if not isinstance(first, dict):
            raise LlmClientError("LLM response choices[0] must be an object")
        message = first.get("message")
        if not isinstance(message, dict) or "content" not in message:
            raise LlmClientError("LLM response choices[0].message.content is missing")
        return _normalize_content(message["content"])
