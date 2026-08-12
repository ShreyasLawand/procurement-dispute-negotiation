import threading
from typing import Callable, Optional

_local = threading.local()


def set_emitter(emitter: Optional[Callable[[dict], None]]) -> None:
    """Registers (or clears) the status emitter for the current thread."""
    _local.emitter = emitter


def emit_status(message: str, **extra) -> None:
    """
    No-op unless a thread-local emitter has been set (only true inside an
    API-driven negotiation thread — see api/sessions.py). Safe to call
    unconditionally from agent/orchestrator code: batch scripts and tests
    that run via GraphNegotiationOrchestrator.run() directly are completely
    unaffected since they never call set_emitter().
    """
    emitter: Optional[Callable[[dict], None]] = getattr(_local, "emitter", None)
    if emitter is not None:
        emitter({"message": message, **extra})
