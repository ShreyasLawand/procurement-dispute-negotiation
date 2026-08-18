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

Does NOT re-resolve while the server is running: if Ronin comes up after the API server
already started on the local fallback, restart the server to pick it up. /api/system-
status still live-checks reachability of whatever host is currently configured, so the
frontend can show an honest "not reachable" state without that requiring a restart to
detect — only picking a *different* host requires one.
"""

import os

import requests

RONIN_TUNNEL_URL = "http://127.0.0.1:11500"
LOCAL_OLLAMA_URL = "http://localhost:11434"
PROBE_TIMEOUT_SECONDS = 2.0


def _is_reachable(base_url: str, timeout: float = PROBE_TIMEOUT_SECONDS) -> bool:
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=timeout)
        return resp.status_code == 200
    except requests.RequestException:
        return False


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
