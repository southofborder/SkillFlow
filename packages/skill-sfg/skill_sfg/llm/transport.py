"""HTTP transport — faithful port of shared/llm-utils.cjs transport half.

Hand-rolled on urllib (HTTP/1.1) to match the JS behavior with zero runtime
deps. HTTP/2 (the JS LLM_HTTP2 path) is not implemented here; the corpus
endpoints accept HTTP/1.1. Swap in httpx later if HTTP/2 is needed.

The retry policy, Retry-After handling, transient-error classification and
exponential backoff + jitter mirror llm-utils.cjs:157-403 exactly.
"""

from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.request
from typing import Any, Callable

from .normalizers import js_round


class LlmTransportError(Exception):
    """Base for transport failures. Carries fields the retry wrapper inspects."""

    def __init__(self, message: str, *, code: str | None = None,
                 status_code: int | None = None, retry_after_ms: int | None = None):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.retry_after_ms = retry_after_ms


class LlmTimeoutError(LlmTransportError):
    def __init__(self, timeout_ms: int):
        super().__init__(f"HTTP request timed out after {timeout_ms}ms", code="LLM_TIMEOUT")


# --- pure helpers (unit-tested; no network) -------------------------------

def parse_retry_after_ms(value: Any) -> int | None:
    """Port of parseRetryAfterMs (llm-utils.cjs:317-327).

    Retry-After is delta-seconds or an HTTP date. Returns ms or None.
    """
    if value is None or value == "":
        return None
    try:
        seconds = float(value)
        if seconds == seconds and seconds >= 0 and seconds not in (float("inf"), float("-inf")):
            return round(seconds * 1000)
    except (ValueError, TypeError):
        pass
    # HTTP-date form.
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(str(value))
    except (TypeError, ValueError):
        return None
    if dt is None:
        return None
    delta_ms = dt.timestamp() * 1000 - time.time() * 1000
    return int(delta_ms) if delta_ms > 0 else 0


_TRANSIENT_CODES = {
    "ECONNRESET", "ETIMEDOUT", "ECONNREFUSED", "EAI_AGAIN",
    "EPIPE", "ENOTFOUND", "ERR_HTTP2_STREAM_ERROR",
}


def is_transient_transport_error(error: Any) -> bool:
    """Port of isTransientTransportError (llm-utils.cjs:329-340)."""
    if error is None:
        return False
    code = getattr(error, "code", None)
    if code == "LLM_TIMEOUT":
        return True
    if str(code or "") in _TRANSIENT_CODES:
        return True
    status = int(getattr(error, "status_code", 0) or 0)
    if status == 429:
        return True
    if 500 <= status <= 599:
        return True
    return False


def _int_or(value: Any, fallback: int, *, positive: bool = False) -> int:
    try:
        n = int(value)
    except (ValueError, TypeError):
        return fallback
    if positive:
        return n if n > 0 else fallback
    return n if n >= 0 else fallback


def resolve_retry_config(options: dict | None = None) -> dict:
    """Port of resolveRetryConfig (llm-utils.cjs:346-360)."""
    options = options or {}
    max_retries = _int_or(
        options.get("max_retries", os.environ.get("LLM_MAX_RETRIES")), 2)
    base_ms = _int_or(
        options.get("retry_base_ms", os.environ.get("LLM_RETRY_BASE_MS")), 500, positive=True)
    max_backoff_ms = _int_or(
        options.get("retry_max_backoff_ms", os.environ.get("LLM_RETRY_MAX_BACKOFF_MS")),
        8000, positive=True)
    return {"max_retries": max_retries, "base_ms": base_ms, "max_backoff_ms": max_backoff_ms}


def _normalize_timeout_ms(value: Any) -> int:
    try:
        n = int(value)
    except (ValueError, TypeError):
        return 30000
    return n if n > 0 else 30000


def compute_backoff_wait_ms(attempt: int, cfg: dict, *, retry_after_ms: int | None = None,
                            rng: Callable[[], float] = random.random) -> int:
    """The backoff+jitter formula from postJsonWithTimeout (llm-utils.cjs:375-379).

    Extracted so it can be unit-tested deterministically by injecting rng.
    """
    backoff = min(cfg["max_backoff_ms"], cfg["base_ms"] * (2 ** attempt))
    jitter = js_round(backoff * 0.25 * rng())
    if retry_after_ms is not None:
        return min(cfg["max_backoff_ms"], retry_after_ms) + jitter
    return backoff + jitter


# --- the actual POST ------------------------------------------------------

def post_json_once(url: str, payload: dict, options: dict | None = None) -> dict:
    """Single HTTP/1.1 attempt. Raises LlmTransportError subclasses on failure."""
    options = options or {}
    timeout_ms = _normalize_timeout_ms(options.get("timeout_ms") or options.get("timeout") or 30000)
    headers = {"Content-Type": "application/json", **(options.get("headers") or {})}
    body = json.dumps(payload or {}).encode("utf-8")
    headers["Content-Length"] = str(len(body))

    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_ms / 1000) as response:
            text = response.read().decode("utf-8")
            status = response.status
            if status < 200 or status >= 300:
                raise _http_status_error(status, text, dict(response.headers))
            try:
                return json.loads(text)
            except ValueError as exc:
                raise LlmTransportError(f"Invalid JSON response: {exc}")
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise _http_status_error(exc.code, text, dict(exc.headers or {}))
    except TimeoutError:
        raise LlmTimeoutError(timeout_ms)
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        if isinstance(reason, TimeoutError):
            raise LlmTimeoutError(timeout_ms)
        err = LlmTransportError(f"network error: {reason}")
        # Map common socket errno names into the JS transient set.
        errno_name = getattr(getattr(reason, "errno", None), "name", "") or ""
        err.code = _CONNRESET_HINTS.get(type(reason).__name__, errno_name)
        raise err


_CONNRESET_HINTS = {
    "ConnectionResetError": "ECONNRESET",
    "ConnectionRefusedError": "ECONNREFUSED",
    "BrokenPipeError": "EPIPE",
    "gaierror": "EAI_AGAIN",
}


def _http_status_error(status_code: int, text: str, headers: dict) -> LlmTransportError:
    """Port of httpStatusError (llm-utils.cjs:307-314)."""
    retry_after = headers.get("retry-after") or headers.get("Retry-After")
    return LlmTransportError(
        f"HTTP {status_code}: {text}",
        status_code=status_code,
        retry_after_ms=parse_retry_after_ms(retry_after),
    )


def post_json_with_timeout(url: str, payload: dict, options: dict | None = None,
                           *, rng: Callable[[], float] = random.random,
                           sleep: Callable[[float], None] = time.sleep) -> dict:
    """Port of postJsonWithTimeout (llm-utils.cjs:366-384).

    Bounded retry with exponential backoff + jitter for transient failures
    (timeout, network reset/DNS, HTTP 429, HTTP 5xx). Honors Retry-After.
    Auth/4xx (except 429) and schema errors are not retried.
    """
    options = options or {}
    cfg = resolve_retry_config(options)
    attempt = 0
    while True:
        try:
            return post_json_once(url, payload, options)
        except LlmTransportError as error:
            if attempt >= cfg["max_retries"] or not is_transient_transport_error(error):
                raise
            wait_ms = compute_backoff_wait_ms(
                attempt, cfg, retry_after_ms=error.retry_after_ms, rng=rng)
            attempt += 1
            sleep(wait_ms / 1000)
