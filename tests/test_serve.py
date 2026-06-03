"""Tests for the aac serve JSON API server."""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from aac import create_engine
from aac.cli.serve import run as serve_run


def _start_server(port: int, preset: str = "stateless") -> str:
    """Start a serve instance in a daemon thread; return base URL."""
    engine = create_engine(preset)
    t = threading.Thread(
        target=serve_run,
        kwargs=dict(engine=engine, host="127.0.0.1", port=port, preset=preset, quiet=True),
        daemon=True,
    )
    t.start()
    time.sleep(0.25)
    return f"http://127.0.0.1:{port}"


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=3) as r:
        return json.loads(r.read())  # type: ignore[return-value]


def _post(url: str) -> dict:
    req = urllib.request.Request(url, data=b"", method="POST")
    with urllib.request.urlopen(req, timeout=3) as r:
        return json.loads(r.read())  # type: ignore[return-value]


def _status(url: str) -> int:
    try:
        urllib.request.urlopen(url, timeout=3)
        return 200
    except urllib.error.HTTPError as exc:
        return exc.code


@pytest.fixture(scope="module")
def base_url() -> str:
    return _start_server(port=18421)


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_ok(self, base_url: str) -> None:
        data = _get(f"{base_url}/health")
        assert data["status"] == "ok"

    def test_returns_preset(self, base_url: str) -> None:
        data = _get(f"{base_url}/health")
        assert data["preset"] == "stateless"


# ---------------------------------------------------------------------------
# /suggest
# ---------------------------------------------------------------------------

class TestSuggest:
    def test_returns_suggestions_list(self, base_url: str) -> None:
        data = _get(f"{base_url}/suggest?q=prog")
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_limit_respected(self, base_url: str) -> None:
        data = _get(f"{base_url}/suggest?q=prog&limit=3")
        assert len(data["suggestions"]) <= 3

    def test_limit_clamped_at_100(self, base_url: str) -> None:
        data = _get(f"{base_url}/suggest?q=prog&limit=9999")
        assert len(data["suggestions"]) <= 100

    def test_missing_q_returns_400(self, base_url: str) -> None:
        assert _status(f"{base_url}/suggest") == 400

    def test_empty_q_returns_400(self, base_url: str) -> None:
        assert _status(f"{base_url}/suggest?q=") == 400

    def test_suggestions_are_strings(self, base_url: str) -> None:
        data = _get(f"{base_url}/suggest?q=he")
        for s in data["suggestions"]:
            assert isinstance(s, str)


# ---------------------------------------------------------------------------
# /explain
# ---------------------------------------------------------------------------

class TestExplain:
    def test_returns_explanations_list(self, base_url: str) -> None:
        data = _get(f"{base_url}/explain?q=prog")
        assert "explanations" in data
        assert isinstance(data["explanations"], list)

    def test_limit_respected(self, base_url: str) -> None:
        data = _get(f"{base_url}/explain?q=prog&limit=2")
        assert len(data["explanations"]) <= 2

    def test_explanation_fields_present(self, base_url: str) -> None:
        data = _get(f"{base_url}/explain?q=prog&limit=1")
        exp = data["explanations"][0]
        assert "value" in exp
        assert "base_score" in exp
        assert "history_boost" in exp
        assert "final_score" in exp
        assert "source" in exp
        assert "base_components" in exp
        assert "history_components" in exp
        assert "contribution_pct" in exp

    def test_invariant_holds_in_response(self, base_url: str) -> None:
        data = _get(f"{base_url}/explain?q=he")
        for exp in data["explanations"]:
            expected = round(exp["base_score"] + exp["history_boost"], 5)
            assert abs(exp["final_score"] - expected) < 1e-4, (
                f"final_score invariant violated: {exp}"
            )

    def test_missing_q_returns_400(self, base_url: str) -> None:
        assert _status(f"{base_url}/explain") == 400


# ---------------------------------------------------------------------------
# /record
# ---------------------------------------------------------------------------

class TestRecord:
    def test_record_returns_recorded_true(self, base_url: str) -> None:
        data = _post(f"{base_url}/record?q=prog&value=programming")
        assert data["recorded"] is True

    def test_missing_q_returns_400(self, base_url: str) -> None:
        req = urllib.request.Request(
            f"{base_url}/record?value=programming",
            data=b"",
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=3)
            raise AssertionError("expected 400")
        except urllib.error.HTTPError as exc:
            assert exc.code == 400

    def test_missing_value_returns_400(self, base_url: str) -> None:
        req = urllib.request.Request(
            f"{base_url}/record?q=prog",
            data=b"",
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=3)
            raise AssertionError("expected 400")
        except urllib.error.HTTPError as exc:
            assert exc.code == 400


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrors:
    def test_unknown_get_endpoint_returns_404(self, base_url: str) -> None:
        assert _status(f"{base_url}/unknown") == 404

    def test_post_to_suggest_returns_405(self, base_url: str) -> None:
        req = urllib.request.Request(
            f"{base_url}/suggest?q=prog",
            data=b"",
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=3)
            raise AssertionError("expected 405")
        except urllib.error.HTTPError as exc:
            assert exc.code == 405

    def test_invalid_limit_falls_back_to_default(self, base_url: str) -> None:
        data = _get(f"{base_url}/suggest?q=prog&limit=notanumber")
        assert "suggestions" in data  # did not crash

    def test_error_response_has_error_key(self, base_url: str) -> None:
        try:
            urllib.request.urlopen(f"{base_url}/unknown", timeout=3)
        except urllib.error.HTTPError as exc:
            body = json.loads(exc.read())
            assert "error" in body
