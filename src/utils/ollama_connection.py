"""
Resolves which Ollama backend the API server uses, auto-preferring the Ronin GPU tunnel
when it's up and nothing was explicitly configured.

WHY THIS EXISTS: extraction and negotiation both run noticeably faster against the
Ronin GPU tunnel (~1-1.5s/call once warm) than local CPU-bound Ollama (tens of seconds
to minutes/call) — see CLAUDE.md's "BAILII expansion" sections. Previously this only
happened if you remembered to `export OLLAMA_HOST=http://127.0.0.1:11500` yourself
before starting the API server (which is what scripts/start_demo.ps1 does). Running the
API server directly (`python -m uvicorn api.main:app`), as during manual testing, skips
that entirely and silently falls back to local Ollama with no indication anything is
slower than it could be.

This resolves automatically at API startup, once, before any agent is constructed:
- If OLLAMA_HOST is already set (by start_demo.ps1, or set by hand), that's respected
  as-is — this module never overrides an explicit choice.
- Otherwise, it probes the standard Ronin tunnel port (127.0.0.1:11500, the port used
  everywhere else in this project) with a short timeout. If it answers, OLLAMA_HOST is
  set to point at it for the rest of the process's life. If not, nothing is set, and the
  ollama client's own default (localhost:11434) applies — a slower demo beats a broken
  one, same reasoning as start_demo.ps1's fallback.

Does NOT re-resolve while the server is running on its own — if Ronin comes up after the API
server already started on the local fallback, either restart the server, or use
connect_to_ronin() below (the "Connect to GPU" button in the frontend calls it via
POST /api/connect-gpu) to bring the tunnel up and repoint OLLAMA_HOST without a restart.
/api/system-status still live-checks reachability of whatever host is currently configured
either way, so the frontend can show an honest "not reachable" state without needing a
restart just to detect that.

connect_to_ronin() exists because the SSH tunnel is a separate, fragile process from the API
server itself — it dies on laptop sleep, network drops, or just closing the terminal window
it was started in, and OLLAMA_HOST then keeps pointing at a dead port until something
restarts the tunnel. Previously that "something" had to be a person with a terminal,
manually re-running the same ssh command from CLAUDE.md/start_demo.ps1. This spawns that same
command from Python instead, so it can be triggered from the frontend.
"""

import atexit
import os
import subprocess
import time
from pathlib import Path

import requests

RONIN_TUNNEL_URL = "http://127.0.0.1:11500"
LOCAL_OLLAMA_URL = "http://localhost:11434"
PROBE_TIMEOUT_SECONDS = 2.0

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PEM_PATH = REPO_ROOT / "shreyas-negotiation.pem"
RONIN_SSH_HOST = "shreyas-negotiation.ronin.manchester.ac.uk"
RONIN_SSH_USER = "ubuntu"
TUNNEL_LOCAL_PORT = 11500
CONNECT_TIMEOUT_SECONDS = 20.0

_tunnel_process: subprocess.Popen | None = None


def _is_reachable(base_url: str, timeout: float = PROBE_TIMEOUT_SECONDS) -> bool:
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=timeout)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def _tunnel_process_alive() -> bool:
    return _tunnel_process is not None and _tunnel_process.poll() is None


def connect_to_ronin() -> dict:
    """(Re)establish the SSH tunnel to Ronin and point OLLAMA_HOST at it. Idempotent — safe
    to call repeatedly (e.g. every click of the frontend's "Connect to GPU" button); reuses
    an already-live tunnel rather than spawning a second one. Only works on the machine that
    holds the SSH key (repo root, gitignored) — this is a local dev/demo tool, not something
    exposed for arbitrary remote callers."""
    global _tunnel_process

    if _is_reachable(RONIN_TUNNEL_URL):
        os.environ["OLLAMA_HOST"] = RONIN_TUNNEL_URL
        return {
            "success": True,
            "already_connected": True,
            "message": "Already connected to the Ronin GPU tunnel.",
        }

    if not PEM_PATH.exists():
        return {
            "success": False,
            "already_connected": False,
            "message": f"No SSH key found at {PEM_PATH}. The tunnel can only be started from "
            f"the machine that holds shreyas-negotiation.pem.",
        }

    if not _tunnel_process_alive():
        try:
            _tunnel_process = subprocess.Popen(
                [
                    "ssh", "-i", str(PEM_PATH), "-N",
                    "-L", f"{TUNNEL_LOCAL_PORT}:localhost:11434",
                    "-o", "BatchMode=yes",
                    "-o", "StrictHostKeyChecking=accept-new",
                    "-o", "ConnectTimeout=10",
                    "-o", "ServerAliveInterval=30",
                    f"{RONIN_SSH_USER}@{RONIN_SSH_HOST}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            return {
                "success": False,
                "already_connected": False,
                "message": "The 'ssh' command was not found on this machine (needs an OpenSSH client installed).",
            }

    start = time.time()
    while time.time() - start < CONNECT_TIMEOUT_SECONDS:
        if _is_reachable(RONIN_TUNNEL_URL):
            os.environ["OLLAMA_HOST"] = RONIN_TUNNEL_URL
            return {
                "success": True,
                "already_connected": False,
                "message": f"Connected to the Ronin GPU tunnel ({round(time.time() - start, 1)}s).",
            }
        time.sleep(1)

    disconnect_tunnel()
    return {
        "success": False,
        "already_connected": False,
        "message": f"Timed out after {int(CONNECT_TIMEOUT_SECONDS)}s waiting for the tunnel to "
        f"come up. Check network access to {RONIN_SSH_HOST} and that the Ronin instance is running.",
    }


def disconnect_tunnel() -> None:
    """Tears down a tunnel this process spawned. Registered at exit so a killed API server
    doesn't leave an orphaned ssh.exe holding port 11500 — the same orphaned-process failure
    mode already fixed once for stop_demo.ps1, see CLAUDE.md."""
    global _tunnel_process
    if _tunnel_process_alive():
        _tunnel_process.terminate()
        try:
            _tunnel_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _tunnel_process.kill()
    _tunnel_process = None


atexit.register(disconnect_tunnel)


def resolve_ollama_host_at_startup() -> None:
    """Call once, at API server startup, before any agent is constructed."""
    if os.environ.get("OLLAMA_HOST"):
        return  # explicit configuration always wins, never overridden
    if _is_reachable(RONIN_TUNNEL_URL):
        os.environ["OLLAMA_HOST"] = RONIN_TUNNEL_URL


def current_status() -> dict:
    """Live status for /api/system-status — re-checks reachability on every call,
    so a tunnel dropping mid-session shows up without needing a server restart."""
    host = os.environ.get("OLLAMA_HOST", LOCAL_OLLAMA_URL)
    using_gpu_tunnel = host.rstrip("/") == RONIN_TUNNEL_URL
    return {
        "ollama_host": host,
        "reachable": _is_reachable(host),
        "using_gpu_tunnel": using_gpu_tunnel,
    }
