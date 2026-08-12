import asyncio
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

from src.graph_orchestrator import GraphNegotiationOrchestrator
from src.schemas.agent_state import DisputeScenario
from src.utils.event_stream import set_emitter

REPO_ROOT = Path(__file__).resolve().parent.parent

# Serializes all Ollama-bound work (extraction + every negotiation run) so
# concurrent requests don't thrash a single local Ollama instance.
ollama_lock = threading.Lock()


@dataclass
class StreamEvent:
    event: str
    data: dict


@dataclass
class NegotiationSession:
    id: str
    scenario: DisputeScenario
    max_rounds: int
    status: Literal["running", "done", "error"] = "running"
    queue: "asyncio.Queue[StreamEvent]" = field(default_factory=asyncio.Queue)
    final_state: Optional[dict] = None
    error: Optional[str] = None


SESSIONS: dict[str, NegotiationSession] = {}


def translate_update(node_name: str, full_state: dict) -> Optional[dict]:
    """
    Turns a graph node's completion into a lean SSE payload. Reads from the
    already-merged full_state (not the node's raw partial-update dict) —
    bidder_round_node doesn't return round_number itself (only
    ca_round_node does), so reading off the merged state avoids sending a
    None round_number on bidder-round events.
    """
    if node_name == "pre_negotiation":
        return {
            "ca_pre_negotiation": full_state["ca_pre_negotiation"].model_dump(mode="json"),
            "bidder_pre_negotiation": full_state["bidder_pre_negotiation"].model_dump(mode="json"),
        }
    if node_name in ("ca_round", "bidder_round"):
        return {
            "round_number": full_state["round_number"],
            "message": full_state["messages"][-1].model_dump(mode="json"),
        }
    if node_name == "court_check":
        return {
            "compliance_check": full_state["compliance_checks"][-1].model_dump(mode="json"),
            "resolved": full_state.get("resolved", False),
            "resolution_outcome": full_state.get("resolution_outcome"),
        }
    if node_name == "win_statements":
        return {
            "ca_win_statement": full_state["ca_win_statement"].model_dump(mode="json"),
            "bidder_win_statement": full_state["bidder_win_statement"].model_dump(mode="json"),
        }
    if node_name == "summary":
        return {"summary": full_state["summary"].model_dump(mode="json")}
    return None


def start_session(scenario: DisputeScenario, max_rounds: int, loop: asyncio.AbstractEventLoop) -> str:
    session_id = str(uuid.uuid4())
    session = NegotiationSession(id=session_id, scenario=scenario, max_rounds=max_rounds)
    SESSIONS[session_id] = session

    def push(event: str, data: dict) -> None:
        loop.call_soon_threadsafe(session.queue.put_nowait, StreamEvent(event, data))

    def run() -> None:
        set_emitter(lambda status_data: push("status", status_data))
        try:
            with ollama_lock:
                orchestrator = GraphNegotiationOrchestrator(max_rounds=max_rounds)
                full_state = orchestrator._build_initial_state(scenario)
                for step in orchestrator.stream(scenario):
                    for node_name, update in step.items():
                        full_state.update(update)
                        payload = translate_update(node_name, full_state)
                        if payload is not None:
                            push(node_name, payload)

                session.final_state = full_state
                session.status = "done"
                out_path = REPO_ROOT / f"negotiation_log_live_{session_id[:8]}.json"
                orchestrator.save_log(full_state, str(out_path))
            push("done", {"session_id": session_id})
        except Exception as exc:  # noqa: BLE001 — surfaced to the client, not swallowed
            session.status = "error"
            session.error = str(exc)
            push("error", {"message": str(exc)})
        finally:
            set_emitter(None)

    threading.Thread(target=run, daemon=True).start()
    return session_id
