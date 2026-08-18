"""
Tests for src/utils/ollama_connection.py — the GPU-tunnel auto-detection that runs at
API server startup. All requests.get calls are mocked; nothing here touches a real
network or a real Ollama instance, local or remote.
"""

import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import requests

from src.utils.ollama_connection import (
    resolve_ollama_host_at_startup,
    current_status,
    RONIN_TUNNEL_URL,
    LOCAL_OLLAMA_URL,
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """OLLAMA_HOST must not leak between tests, or between this test run and whatever
    the developer's own shell happened to have set."""
    monkeypatch.delenv("OLLAMA_HOST", raising=False)


def _mock_response(status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    return resp


def test_respects_explicitly_set_ollama_host(monkeypatch):
    """An explicit OLLAMA_HOST (e.g. set by start_demo.ps1) must never be overridden,
    even if the Ronin tunnel also happens to be reachable."""
    monkeypatch.setenv("OLLAMA_HOST", "http://example.com:9999")
    with patch("requests.get") as mock_get:
        resolve_ollama_host_at_startup()
        mock_get.assert_not_called()
    assert os.environ["OLLAMA_HOST"] == "http://example.com:9999"


def test_auto_sets_ronin_when_reachable_and_nothing_configured():
    with patch("requests.get", return_value=_mock_response(200)):
        resolve_ollama_host_at_startup()
    assert os.environ["OLLAMA_HOST"] == RONIN_TUNNEL_URL


def test_leaves_unset_when_ronin_unreachable():
    with patch("requests.get", side_effect=requests.ConnectionError()):
        resolve_ollama_host_at_startup()
    assert "OLLAMA_HOST" not in os.environ


def test_current_status_reports_local_default_when_unset():
    with patch("requests.get", return_value=_mock_response(200)):
        status = current_status()
    assert status["ollama_host"] == LOCAL_OLLAMA_URL
    assert status["using_gpu_tunnel"] is False
    assert status["reachable"] is True


def test_current_status_reports_gpu_tunnel_when_configured(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", RONIN_TUNNEL_URL)
    with patch("requests.get", return_value=_mock_response(200)):
        status = current_status()
    assert status["using_gpu_tunnel"] is True
    assert status["reachable"] is True


def test_current_status_reports_unreachable_honestly(monkeypatch):
    """A configured-but-dead tunnel must show reachable=False, not silently succeed —
    this is what the frontend's warning banner keys off of."""
    monkeypatch.setenv("OLLAMA_HOST", RONIN_TUNNEL_URL)
    with patch("requests.get", side_effect=requests.Timeout()):
        status = current_status()
    assert status["using_gpu_tunnel"] is True
    assert status["reachable"] is False


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
