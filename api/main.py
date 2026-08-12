import asyncio
import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from api.models import ExtractResponse, StartNegotiationRequest, StartNegotiationResponse
from api.sessions import SESSIONS, ollama_lock, start_session
from src.agents.extraction_agent import ScenarioExtractionAgent
from src.utils.document_extraction import combine_documents

app = FastAPI(title="Procurement Dispute Negotiation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

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
    source_text = combine_documents(docs)

    with ollama_lock:
        scenario = _extractor.extract_scenario(
            source_text,
            dispute_id=dispute_id,
            contracting_authority_name=contracting_authority_name,
            bidder_name=bidder_name,
        )
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
