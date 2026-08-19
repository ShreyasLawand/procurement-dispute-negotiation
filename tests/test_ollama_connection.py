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

import src.utils.ollama_connection as ollama_connection
from src.utils.ollama_connection import (
    resolve_ollama_host_at_startup,
    current_status,
    connect_to_ronin,
    disconnect_tunnel,
    RONIN_TUNNEL_URL,
    LOCAL_OLLAMA_URL,
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """OLLAMA_HOST must not leak between tests, or between this test run and whatever
    the developer's own shell happened to have set."""
    monkeypatch.delenv("OLLAMA_HOST", raising=False)


@pytest.fixture(autouse=True)
def clean_tunnel_process():
    """_tunnel_process is module-level mutable state (tracks a real subprocess handle in
    production) — must not leak a mock process handle from one test into the next."""
    ollama_connection._tunnel_process = None
    yield
    ollama_connection._tunnel_process = None


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


def _mock_process(alive=True):
    proc = MagicMock()
    proc.poll.return_value = None if alive else 0
    return proc


def test_connect_is_idempotent_when_already_reachable():
    """The frontend's button can be clicked repeatedly (or double-clicked) — must not spawn
    a redundant tunnel process when one is already up and working."""
    with patch("requests.get", return_value=_mock_response(200)), patch("subprocess.Popen") as mock_popen:
        result = connect_to_ronin()
    mock_popen.assert_not_called()
    assert result["success"] is True
    assert result["already_connected"] is True
    assert os.environ["OLLAMA_HOST"] == RONIN_TUNNEL_URL


def test_connect_spawns_and_succeeds_once_reachable(monkeypatch):
    """Not reachable at first (the tunnel isn't up yet) but reachable on the very next
    check (right after the ssh process is spawned) — the common real-world case."""
    monkeypatch.setattr(ollama_connection.Path, "exists", lambda self: True)
    with patch("subprocess.Popen", return_value=_mock_process(alive=True)) as mock_popen, patch(
        "requests.get", side_effect=[requests.ConnectionError(), _mock_response(200)]
    ):
        result = connect_to_ronin()
    mock_popen.assert_called_once()
    assert result["success"] is True
    assert result["already_connected"] is False
    assert os.environ["OLLAMA_HOST"] == RONIN_TUNNEL_URL


def test_connect_missing_pem_key_is_actionable():
    with patch("requests.get", side_effect=requests.ConnectionError()), patch(
        "pathlib.Path.exists", return_value=False
    ), patch("subprocess.Popen") as mock_popen:
        result = connect_to_ronin()
    mock_popen.assert_not_called()
    assert result["success"] is False
    assert "key" in result["message"].lower()


def test_connect_ssh_binary_missing_is_actionable(monkeypatch):
    monkeypatch.setattr(ollama_connection.Path, "exists", lambda self: True)
    with patch("requests.get", side_effect=requests.ConnectionError()), patch(
        "subprocess.Popen", side_effect=FileNotFoundError()
    ):
        result = connect_to_ronin()
    assert result["success"] is False
    assert "ssh" in result["message"].lower()


def test_connect_does_not_spawn_a_second_process_while_one_is_alive(monkeypatch):
    """If a tunnel process from a previous attempt is still alive (just slow to come up),
    a fresh click must reuse it, not stack a second ssh process on the same local port."""
    ollama_connection._tunnel_process = _mock_process(alive=True)
    monkeypatch.setattr(ollama_connection, "CONNECT_TIMEOUT_SECONDS", 0)
    with patch("requests.get", side_effect=requests.ConnectionError()), patch("subprocess.Popen") as mock_popen:
        result = connect_to_ronin()
    mock_popen.assert_not_called()
    assert result["success"] is False


def test_connect_times_out_with_actionable_message(monkeypatch):
    monkeypatch.setattr(ollama_connection, "CONNECT_TIMEOUT_SECONDS", 0)
    monkeypatch.setattr(ollama_connection.Path, "exists", lambda self: True)
    with patch("requests.get", side_effect=requests.ConnectionError()), patch(
        "subprocess.Popen", return_value=_mock_process(alive=True)
    ):
        result = connect_to_ronin()
    assert result["success"] is False
    assert "timed out" in result["message"].lower()


def test_disconnect_terminates_a_live_process():
    proc = _mock_process(alive=True)
    ollama_connection._tunnel_process = proc
    disconnect_tunnel()
    proc.terminate.assert_called_once()
    assert ollama_connection._tunnel_process is None


def test_disconnect_is_a_noop_with_no_process():
    ollama_connection._tunnel_process = None
    disconnect_tunnel()  # must not raise
    assert ollama_connection._tunnel_process is None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
