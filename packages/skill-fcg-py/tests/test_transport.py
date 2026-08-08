"""Lock the transport retry/backoff helpers to the JS spec (llm-utils.cjs:307-403).

Network I/O itself is not exercised (no live endpoint); the retry policy,
Retry-After parsing, transient classification and backoff formula are the
load-bearing logic and are tested deterministically with injected rng/sleep.
"""

from email.utils import format_datetime
from datetime import datetime, timezone, timedelta

import pytest

from skill_fcg.llm import transport as T


class TestParseRetryAfterMs:
    def test_delta_seconds(self):
        assert T.parse_retry_after_ms("2") == 2000
        assert T.parse_retry_after_ms(0) == 0

    def test_none_and_empty(self):
        assert T.parse_retry_after_ms(None) is None
        assert T.parse_retry_after_ms("") is None

    def test_http_date_future(self):
        future = datetime.now(timezone.utc) + timedelta(seconds=30)
        ms = T.parse_retry_after_ms(format_datetime(future, usegmt=True))
        assert ms is not None and ms > 0

    def test_http_date_past_clamped_to_zero(self):
        past = datetime.now(timezone.utc) - timedelta(seconds=30)
        assert T.parse_retry_after_ms(format_datetime(past, usegmt=True)) == 0

    def test_garbage(self):
        assert T.parse_retry_after_ms("not-a-date") is None


class TestIsTransientTransportError:
    def test_timeout(self):
        assert T.is_transient_transport_error(T.LlmTimeoutError(1000)) is True

    def test_network_codes(self):
        for code in ("ECONNRESET", "ETIMEDOUT", "ENOTFOUND", "EAI_AGAIN"):
            e = T.LlmTransportError("x", code=code)
            assert T.is_transient_transport_error(e) is True

    def test_429_and_5xx(self):
        assert T.is_transient_transport_error(T.LlmTransportError("x", status_code=429)) is True
        assert T.is_transient_transport_error(T.LlmTransportError("x", status_code=503)) is True

    def test_4xx_not_transient(self):
        assert T.is_transient_transport_error(T.LlmTransportError("x", status_code=401)) is False
        assert T.is_transient_transport_error(T.LlmTransportError("x", status_code=400)) is False

    def test_none(self):
        assert T.is_transient_transport_error(None) is False


class TestResolveRetryConfig:
    def test_defaults(self):
        cfg = T.resolve_retry_config({})
        assert cfg == {"max_retries": 2, "base_ms": 500, "max_backoff_ms": 8000}

    def test_option_overrides(self):
        cfg = T.resolve_retry_config({"max_retries": 5, "retry_base_ms": 100, "retry_max_backoff_ms": 4000})
        assert cfg == {"max_retries": 5, "base_ms": 100, "max_backoff_ms": 4000}

    def test_env_overrides(self, monkeypatch):
        monkeypatch.setenv("LLM_MAX_RETRIES", "3")
        monkeypatch.setenv("LLM_RETRY_BASE_MS", "250")
        cfg = T.resolve_retry_config({})
        assert cfg["max_retries"] == 3
        assert cfg["base_ms"] == 250

    def test_invalid_falls_back(self):
        cfg = T.resolve_retry_config({"retry_base_ms": "abc", "max_retries": -1})
        assert cfg["base_ms"] == 500
        assert cfg["max_retries"] == 2  # negative rejected


class TestBackoffFormula:
    def test_exponential_growth_zero_jitter(self):
        cfg = {"max_retries": 5, "base_ms": 500, "max_backoff_ms": 8000}
        rng = lambda: 0.0
        assert T.compute_backoff_wait_ms(0, cfg, rng=rng) == 500
        assert T.compute_backoff_wait_ms(1, cfg, rng=rng) == 1000
        assert T.compute_backoff_wait_ms(2, cfg, rng=rng) == 2000
        assert T.compute_backoff_wait_ms(3, cfg, rng=rng) == 4000

    def test_backoff_capped(self):
        cfg = {"max_retries": 10, "base_ms": 500, "max_backoff_ms": 8000}
        # 500 * 2^5 = 16000 -> capped to 8000
        assert T.compute_backoff_wait_ms(5, cfg, rng=lambda: 0.0) == 8000

    def test_jitter_added(self):
        cfg = {"max_retries": 5, "base_ms": 500, "max_backoff_ms": 8000}
        # backoff=500, jitter = round(500*0.25*0.5)=63
        assert T.compute_backoff_wait_ms(0, cfg, rng=lambda: 0.5) == 563

    def test_retry_after_overrides_backoff(self):
        cfg = {"max_retries": 5, "base_ms": 500, "max_backoff_ms": 8000}
        # retry_after 3000, capped by max_backoff, + zero jitter
        assert T.compute_backoff_wait_ms(0, cfg, retry_after_ms=3000, rng=lambda: 0.0) == 3000
        # retry_after above cap -> clamped
        assert T.compute_backoff_wait_ms(0, cfg, retry_after_ms=99999, rng=lambda: 0.0) == 8000


class TestPostJsonWithTimeoutRetryLoop:
    def _make(self, outcomes):
        """Return a fake post_json_once that yields the given outcomes in order.

        Each outcome is either a dict (success) or an Exception (raised).
        """
        calls = {"n": 0}

        def fake_once(url, payload, options=None):
            i = calls["n"]
            calls["n"] += 1
            outcome = outcomes[i]
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        return fake_once, calls

    def test_succeeds_first_try(self, monkeypatch):
        fake, calls = self._make([{"ok": True}])
        monkeypatch.setattr(T, "post_json_once", fake)
        out = T.post_json_with_timeout("http://x", {}, {}, rng=lambda: 0.0, sleep=lambda s: None)
        assert out == {"ok": True}
        assert calls["n"] == 1

    def test_retries_transient_then_succeeds(self, monkeypatch):
        fake, calls = self._make([
            T.LlmTransportError("boom", status_code=503),
            {"ok": True},
        ])
        monkeypatch.setattr(T, "post_json_once", fake)
        slept = []
        out = T.post_json_with_timeout("http://x", {}, {}, rng=lambda: 0.0, sleep=slept.append)
        assert out == {"ok": True}
        assert calls["n"] == 2
        assert slept == [0.5]  # one backoff of 500ms

    def test_non_transient_raises_immediately(self, monkeypatch):
        fake, calls = self._make([T.LlmTransportError("nope", status_code=401)])
        monkeypatch.setattr(T, "post_json_once", fake)
        with pytest.raises(T.LlmTransportError):
            T.post_json_with_timeout("http://x", {}, {}, sleep=lambda s: None)
        assert calls["n"] == 1

    def test_exhausts_retries(self, monkeypatch):
        fake, calls = self._make([
            T.LlmTransportError("1", status_code=503),
            T.LlmTransportError("2", status_code=503),
            T.LlmTransportError("3", status_code=503),
        ])
        monkeypatch.setattr(T, "post_json_once", fake)
        with pytest.raises(T.LlmTransportError):
            T.post_json_with_timeout("http://x", {}, {"max_retries": 2},
                                     rng=lambda: 0.0, sleep=lambda s: None)
        assert calls["n"] == 3  # initial + 2 retries
