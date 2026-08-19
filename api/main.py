import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from api.models import (
    BatchListEntry,
    ExtractResponse,
    RecommendationResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    StartNegotiationRequest,
    StartNegotiationResponse,
)
from api.sessions import SESSIONS, ollama_lock, start_session
from src.agents.extraction_agent import ScenarioExtractionAgent
from src.recommendation.settlement_recommendation import synthesize_recommendation
from src.risk.challenge_risk import assess_challenge_risk
from src.utils.document_extraction import combine_documents
from src.utils.ollama_connection import connect_to_ronin, current_status, resolve_ollama_host_at_startup

BATCH_RESULTS_DIR = Path(__file__).resolve().parent.parent / "batch_results"

# Must run before any agent is constructed below (or in api/sessions.py, on first
# negotiation) — it sets OLLAMA_HOST in the process environment if nothing was already
# configured and the Ronin GPU tunnel answers. See src/utils/ollama_connection.py.
resolve_ollama_host_at_startup()

app = FastAPI(title="Procurement Dispute Negotiation API")

app.add_middleware(
    CORSMiddleware,
    # A hardcoded single port (5173) breaks the moment Vite has to fall back to 5174+
    # because something else is holding the default port — which is exactly what
    # happened during dev testing. Matching any localhost/127.0.0.1 port covers every
    # Vite fallback without needing to predict which port it lands on.
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1):\d+$",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/system-status")
def system_status():
    """Which Ollama backend this server is using right now, and whether it's actually
    reachable — the frontend polls this to show a GPU-connection hint. Re-checks
    reachability live on every call (see current_status()'s docstring for why)."""
    return current_status()


@app.post("/api/connect-gpu")
def connect_gpu():
    """(Re)establishes the SSH tunnel to the Ronin GPU and points OLLAMA_HOST at it — the
    frontend's "Connect to GPU" button calls this so a dropped tunnel (laptop sleep, network
    blip) can be brought back up without a terminal. Can take up to ~20s (see
    ollama_connection.CONNECT_TIMEOUT_SECONDS); a plain `def` runs it in FastAPI's threadpool
    rather than blocking the event loop. Returns 200 with success=false (not an HTTPException)
    on failure — this is an expected, user-facing outcome, not a server error."""
    return connect_to_ronin()


# Module-level singleton, same pattern as graph_orchestrator.py's agents.
_extractor = ScenarioExtractionAgent()


@app.post("/api/extract", response_model=ExtractResponse)
def extract(
    files: list[UploadFile] = File(...),
    dispute_id: str = Form("UPLOADED-001"),
    contracting_authority_name: str | None = Form(None),
    bidder_name: str | None = Form(None),
):
    # Plain `def`, not `async def` — FastAPI runs sync path functions in its
    # internal threadpool automatically, which is all a single blocking
    # Ollama call needs here.
    docs = [(f.filename or "document", f.file.read()) for f in files]
    if not docs:
        raise HTTPException(400, "No files uploaded")

    try:
        source_text = combine_documents(docs)
    except ValueError as e:
        # Unsupported file type, or a parser-level failure reading the file itself.
        raise HTTPException(400, str(e)) from e

    try:
        with ollama_lock:
            scenario = _extractor.extract_scenario(
                source_text,
                dispute_id=dispute_id,
                contracting_authority_name=contracting_authority_name,
                bidder_name=bidder_name,
            )
    except ValueError as e:
        # Includes ScenarioExtractionAgent's own "not enough usable text" guard —
        # a 400, since the problem is the uploaded document, not the server.
        raise HTTPException(400, str(e)) from e
    except Exception as e:
        # Anything else (Ollama unreachable, model not pulled, malformed LLM output
        # surviving the agent's own repair attempt) used to surface as a bare 500 with
        # no detail — the frontend's ErrorState had nothing to show beyond "Extraction
        # failed (500)". A specific, actionable message here is the fix, not a retry.
        raise HTTPException(
            502,
            f"Could not reach the extraction model, or it returned something unusable: {e}. "
            f"Check that Ollama is running and reachable (see OLLAMA_HOST if you're using "
            f"the Ronin GPU tunnel — /api/system-status reports what this server is "
            f"currently configured to use).",
        ) from e

    return ExtractResponse(scenario=scenario)


@app.post("/api/negotiations", response_model=StartNegotiationResponse)
async def start_negotiation(req: StartNegotiationRequest):
    loop = asyncio.get_running_loop()
    session_id = start_session(req.scenario, req.max_rounds, loop)
    return StartNegotiationResponse(session_id=session_id)


@app.get("/api/negotiations/{session_id}/stream")
async def stream_negotiation(session_id: str):
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(404, "Unknown session_id")

    async def event_generator():
        # Reconnect-after-completion resilience: if the client (re)connects
        # after the run already finished, don't block on an empty queue —
        # replay a synthetic terminal event immediately.
        if session.status != "running" and session.queue.empty():
            if session.status == "done":
                yield f"event: done\ndata: {json.dumps({'session_id': session_id})}\n\n"
            else:
                yield f"event: error\ndata: {json.dumps({'message': session.error})}\n\n"
            return

        while True:
            try:
                event = await asyncio.wait_for(session.queue.get(), timeout=15.0)
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"  # SSE comment line — ignored by EventSource, keeps the connection open
                continue
            yield f"event: {event.event}\ndata: {json.dumps(event.data)}\n\n"
            if event.event in ("done", "error"):
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.get("/api/negotiations/{session_id}")
def get_negotiation(session_id: str):
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(404, "Unknown session_id")
    if session.status == "running":
        return {"status": "running"}
    if session.status == "error":
        return {"status": "error", "message": session.error}
    return {"status": "done", "result": session.final_state}


@app.post("/api/risk-assessment", response_model=RiskAssessmentResponse)
def risk_assessment(req: RiskAssessmentRequest):
    # Rule-based, no LLM call — doesn't touch ollama_lock, can run even while a live
    # negotiation is mid-flight. See src/risk/challenge_risk.py before changing the scoring.
    assessment = assess_challenge_risk(req.ca_profile, req.bidder_profile)
    return RiskAssessmentResponse(assessment=assessment)


@app.get("/api/batches", response_model=list[BatchListEntry])
def list_batches():
    """Completed batches available to synthesize a recommendation from — feeds a picker in the UI."""
    entries = []
    if not BATCH_RESULTS_DIR.exists():
        return entries
    for d in sorted(BATCH_RESULTS_DIR.glob("batch_*"), reverse=True):
        summary_path = d / "batch_summary.json"
        if not summary_path.exists():
            continue
        try:
            s = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        entries.append(BatchListEntry(
            batch_id=d.name,
            scenario_id=s.get("scenario_id", "?"),
            scenario_title=s.get("scenario_title", "?"),
            court_prompt_version=s.get("court_prompt_version"),
            n_runs=s.get("n_runs_successful", 0),
        ))
    return entries


@app.get("/api/recommendation/{batch_id}", response_model=RecommendationResponse)
def get_recommendation(batch_id: str):
    # batch_id comes straight from the URL path — resolve against the known batches
    # directory and reject anything that isn't a real subdirectory of it, rather than
    # trusting the client-supplied name as a filesystem path.
    batch_dir = (BATCH_RESULTS_DIR / batch_id).resolve()
    if BATCH_RESULTS_DIR.resolve() not in batch_dir.parents:
        raise HTTPException(400, "Invalid batch_id")
    summary_path = batch_dir / "batch_summary.json"
    if not summary_path.exists():
        raise HTTPException(404, f"No batch_summary.json for {batch_id}")

    batch_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    try:
        recommendation = synthesize_recommendation(batch_summary)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return RecommendationResponse(recommendation=recommendation)
