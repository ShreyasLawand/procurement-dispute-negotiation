# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

MSc dissertation project (University of Manchester, supervised by Dr. Tingting Mu) in partnership with Fusion21. Simulates UK procurement dispute negotiation using multi-agent LLMs. Also serves as an industrial deliverable — presented to Fusion21 (the proposing company) and to the academic board.

Three negotiating agents — Contracting Authority (CA), Aggrieved Bidder, Court/Judge — plus a fourth non-negotiating Summary agent (added at supervisor's request). Each agent articulates interests, goals, and BATNA before negotiating, then reflects on how it "won" relative to that BATNA afterward.

**Grounding materials:** UK Procurement Act 2023 (s12 objectives: value for money, public benefit, transparency, integrity), 10-day standstill period, 30-day challenge window, Technology and Construction Court (TCC) as adjudicating venue, Fisher & Ury's *Getting to Yes* (interests over positions, BATNA, ZOPA).

**Real case studies** (see "Real Case Studies" below) — four real UK procurement judgments run through the actual extraction + negotiation pipeline as board-facing demo content, not synthetic scenarios: Lancashire Care (£104m, CA lost), Faraday v West Berkshire (£125m, CA lost on appeal), Parkingeye v Velindre (first-ever Procurement Act 2023 judgment, CA lost), Alstom v London Underground (£112.1m — verified via WebSearch; earlier notes citing ~£1.5bn were unconfirmed for this specific traction-equipment procurement and have been corrected).

**Deliberate scope decision:** the official brief encourages fine-tuning; this project uses prompt engineering + a lightweight document-extraction step instead, justified on time-budget grounds. Not a divergence to "fix," it's a settled decision. Full RAG (vector DB retrieval) remains out of scope — see "Known Gaps."

**Model choice:** all agents (CA/Bidder/Court/Summary) and the extraction agent run on local Ollama/Llama 3.1. `langchain-anthropic`/`anthropic` are already installed in `requirements.txt` for a planned future migration to Claude API (extraction first, agents later) once API credits are available — not yet done, don't assume it.

Repository layout — everything lives under `procurement-dispute-negotiation/`:

1. **`src/`, `scripts/`, `tests/`** — Python backend: multi-agent system using LangGraph + LangChain + Ollama (local Llama 3.1)
2. **`api/`** — FastAPI backend exposing document extraction and live, streaming (SSE) negotiation runs to the frontend
3. **`frontend/`** — TypeScript/React app (Vite + Tailwind v4), Fusion21-branded, built and working. Pages: Home (explainer), Negotiate (upload real documents → live negotiation), Cases (case picker, includes the real case studies), Analytics (batch evaluation metrics). The old `dispute-dashboard-legacy/` (JS/Vite) is deprecated; do not extend it.

## Commands

### Python Backend

```bash
cd procurement-dispute-negotiation

pip install -r requirements.txt

# Requires Ollama running locally with llama3.1 pulled:
# ollama pull llama3.1

python tests/test_full_negotiation.py         # single negotiation (legacy orchestrator)
python tests/test_langgraph_negotiation.py    # LangGraph orchestrator — primary entrypoint
python tests/run_batch_evaluation.py          # batch runner, outputs to batch_results/
python scripts/generate_real_case_studies.py  # runs the 4 real case studies end-to-end (extraction + negotiation)
python test_connection.py                     # quick API connection check
```

**Windows gotcha:** always run Python scripts/servers with `PYTHONIOENCODING=utf-8` set. `graph_orchestrator.py`'s console output uses Unicode box-drawing characters (`─`); Windows' default console codepage (cp1252) crashes on them the moment stdout is redirected (background processes, log files, `uvicorn`). This is not optional for any backgrounded/redirected run.

### API server (new)

```bash
cd procurement-dispute-negotiation
python -m uvicorn api.main:app --reload --port 8000   # -m keeps `src...` imports working like tests/ does
```
Avoid editing backend source while a negotiation is mid-flight with `--reload` on — a reload kills the in-memory session store (`api/sessions.py`).

### Frontend

```bash
cd frontend
npm install
npm run sync-data   # copies ../batch_results/ and root negotiation_log_*.json into public/data/ + manifest.json — required, not automatic
npm run dev
```
Set `VITE_API_BASE` (see `frontend/.env.example`, defaults to `http://localhost:8000`) for the Negotiate page to reach the API server.

## Architecture

```
L1 Presentation   → frontend/ — BUILT. Fusion21-branded, multi-page (Home/Negotiate/Cases/Analytics).
L2 Orchestration  → graph_orchestrator.py (LangGraph StateGraph) — BUILT, primary. Has both
                     .run() (synchronous, used by batch/real-case scripts) and .stream() (used
                     by the live API path). orchestrator.py (legacy plain-loop) — BUILT, fallback.
L2.5 API/Live     → api/ (FastAPI) — BUILT. Bridges LangGraph's sync .stream() generator into
                     async SSE via a background thread + asyncio.Queue (see api/sessions.py).
                     This is the ONE path that calls Ollama directly from a user-facing request;
                     the static Cases/Analytics view still only reads pre-generated JSON.
L3 Agents         → CA, Bidder, Court, Summary, Extraction — BUILT. Model: Llama 3.1 (8B) via
                     Ollama. Target model: Claude API (migration planned, not done).
L4 Knowledge/RAG  → ChromaDB over Procurement Act 2023, TCC Guide, case law — NOT BUILT. The
                     extraction agent (src/agents/extraction_agent.py) is a single-pass LLM
                     synthesis step, not retrieval — don't conflate the two.
L5 Persistence    → Local JSON logs — BUILT. PostgreSQL — NOT BUILT.
```

### Repository structure

```
procurement-dispute-negotiation/
├── api/
│   ├── main.py                     # FastAPI app: /api/extract, /api/negotiations, SSE stream
│   ├── sessions.py                 # in-memory session store, background thread + SSE bridging
│   └── models.py                   # request/response Pydantic models
├── scripts/
│   └── generate_real_case_studies.py   # runs the 4 real cases through extraction + negotiation
├── src/
│   ├── orchestrator.py             # legacy plain-loop orchestrator (fallback)
│   ├── graph_state.py              # LangGraph TypedDict state schema
│   ├── graph_orchestrator.py       # PRIMARY: LangGraph StateGraph orchestrator (.run + .stream)
│   ├── agents/
│   │   ├── ca_agent.py             # ContractingAuthorityAgent
│   │   ├── bidder_agent.py         # AggrievedBidderAgent
│   │   ├── court_agent.py          # CourtAgent
│   │   ├── summary_agent.py        # SummaryAgent (4th, non-negotiating)
│   │   └── extraction_agent.py     # ScenarioExtractionAgent — raw docs -> DisputeScenario
│   ├── prompts/
│   │   ├── ca_prompt.py
│   │   ├── bidder_prompt.py
│   │   ├── court_prompt.py         # revised 3x — see "Court Agent Design" below
│   │   ├── summary_prompt.py
│   │   └── extraction_prompt.py    # mirrors the Court agent's anti-fabrication principle
│   ├── schemas/
│   │   └── agent_state.py          # all Pydantic models
│   ├── scenarios/
│   │   ├── scenario_001.py         # F21-001: synthetic qualitative dispute
│   │   └── scenario_002.py         # F21-002: synthetic numeric dispute
│   └── utils/
│       ├── negotiation_helpers.py  # is_repetitive(), format_previous_statements(), get_round_stage_instruction()
│       ├── document_extraction.py  # PDF/DOCX/TXT text extraction + truncation for extraction agent
│       └── event_stream.py         # thread-local status emitter, no-op unless the API sets one
└── tests/
    ├── test_full_negotiation.py
    ├── test_langgraph_negotiation.py
    └── run_batch_evaluation.py
```

### LangGraph flow (`graph_orchestrator.py`)

```
pre_negotiation → ca_round → bidder_round → court_check
                      ▲                          │
                      └── route_after_court() ────┘
                          "continue" if not resolved and round < max_rounds
                          "summary" if resolved or round >= max_rounds
court_check → win_statements → summary → END
```

`GraphNegotiationOrchestrator.stream(scenario)` yields `{node_name: partial_update_dict}` per super-step (`stream_mode="updates"`) — confirmed empirically: `ca_round_node` returns `round_number` in its update, `bidder_round_node` does NOT, so any consumer merging updates into a running state must always read `round_number` off the merged state, not the raw per-node update (see `api/sessions.py::translate_update`).

### Pydantic schemas (`src/schemas/agent_state.py`)

- `DisputeScenario` — dispute_id, title, description, contract_value_gbp, dispute_type, procedural_stage, contracting_authority_name, bidder_name. No separate structured score fields — everything numeric-relevant lives in the free-text `description`.
- `PreNegotiationStatement` — role, interests[], goals[], batna, opening_position, legal_basis[], confidence_score
- `NegotiationMessage` / `RoundResponse` — round_number, sender_role, message, proposal, concession_made. `RoundResponse` has a `field_validator` coercing dict/bool into strings (Llama 3.1 sometimes returns a JSON object for `proposal` despite instructions) — fixed to produce readable prose (`_prose_from_dict`) rather than a raw `"key: value"` dump; the round-response prompts also now show an explicit right/wrong example.
- `ComplianceAssessment` — Court's structured output: process_followed, manifest_error_found, applicable_provisions[], reasoning, recommended_action, deadlock
- `NegotiationState` — aggregate state; uses forward references, call `.model_rebuild()` at end of file
- `WinStatement` — outcome_relative_to_batna, win_statement, what_was_achieved[], what_was_conceded[]
- `NegotiationSummary` — key_sticking_points[], concessions_summary, court_reasoning_summary, plain_english_summary

## Negotiation Protocol

1. **Scenario Input** — dispute loaded into orchestrator (from a hand-written `scenarios/*.py`, from `scripts/generate_real_case_studies.py`'s extraction step, or live via `POST /api/extract`)
2. **Pre-Negotiation** — CA and Bidder each produce a `PreNegotiationStatement` independently
3. **Negotiation Rounds** — CA/Bidder alternate; Court runs `ComplianceAssessment` after every round
4. **Resolution** — Court's `recommended_action` ∈ {continue negotiation, re-evaluation, no remedy - decision stands, damages}. Non-continue = resolved. Max rounds reached with no resolution = deadlock, escalate to formal proceedings
5. **Win Statements** — both agents reflect on outcome vs. their own BATNA
6. **Summary** — Summary agent produces plain-English explanation of the full transcript

## Court Agent Design (critical — read before touching `court_prompt.py`)

The Court agent assesses **process compliance only** — not who "deserves" to win. This mirrors real UK judicial review of procurement decisions.

This went through three iterations, each with a distinct, empirically-measured failure mode:

| Version | Instruction | Result |
|---|---|---|
| V1 (original) | Judgement-based, no explicit verification | Manifest-error findings tracked whether CA *conceded* in dialogue, not the actual facts — unreliable |
| V2 (verification-only) | Always independently verify any calculation | Fixed concession-dependency on numeric scenarios (100% accuracy) but **overcorrected**: fabricated invented point-systems on qualitative scenarios with no real formula |
| V3 (final, current) | Conditional: compute exactly if a real formula exists; otherwise conduct qualitative rational-basis review with no invented numbers | Restored realistic, non-fabricated judgement on qualitative scenarios (~57% agreement) while keeping 100% accuracy on numeric ones |

**Never let the Court agent fabricate arithmetic on qualitative scenarios.** This is the project's core empirical finding, don't regress it while iterating on prompts.

The extraction agent (`src/prompts/extraction_prompt.py`) deliberately mirrors this same principle: it must not invent a scoring formula for a qualitatively-described source document, and must not report a disputed/mistaken figure (e.g. a mis-stated tender value) as the contract's real value when the source itself distinguishes the two — getting this wrong would poison every downstream Court assessment with a fabricated premise.

### Test scenarios

- **F21-001** — qualitative/ambiguous scoring challenge, no stated formula. Correct behavior: rational-basis review, no invented numbers.
- **F21-002** — numeric scoring error, exact formula given (`Final Score = Quality×0.6 + Price×0.4`). Correct behavior: exact arithmetic verification.

### Batch evaluation

`run_batch_evaluation.py` runs N trials, aggregates agreement rate, manifest-error detection rate, rounds-to-resolution, timing → `batch_results/batch_<timestamp>/`. Current V3 results: 100% accuracy on F21-002 (numeric), ~57% agreement on F21-001 (qualitative, correctly non-fabricated). Treat any committed results tables as needing cross-check against the raw `batch_summary.json` files before citing exact figures anywhere.

## Real Case Studies

`scripts/generate_real_case_studies.py` runs four real UK procurement judgments through the same extraction → negotiation pipeline a live document upload would use (dogfooding), producing `negotiation_log_realcase_<slug>.json` at the repo root, which `frontend/scripts/sync-data.mjs` picks up automatically and tags `isRealCase: true` for a badge in the UI:

- **Lancashire Care & Blackpool Teaching Hospitals NHS FTs v Lancashire County Council [2018] EWHC 1589 (TCC)** — ~£104m, transparency/adequacy-of-reasons failure, CA lost.
- **Faraday Development Ltd v West Berkshire Council [2018] EWCA Civ 2532** — ~£125m, disguised procurement (process-avoidance), CA won at first instance, lost on appeal (first ineffectiveness declaration since 2009).
- **Parkingeye Ltd v Velindre University NHS Trust & Anor [2026] EWHC 1019 (TCC)** — first-ever reported Procurement Act 2023 judgment, ~£10-20m (tender notice mis-stated it as £100,000), CA lost the suspension application.
- **Alstom Transport UK Ltd v London Underground Ltd [2017] EWHC 1521 (TCC)** — £112.1m (verified; corrects an earlier unconfirmed ~£1.5bn figure), automatic-suspension challenge, CA won.

Each case's source text is hand-written dense prose grounded in verified research (case citation, facts, real outcome) — not fabricated numbers or formulas, consistent with the Court/extraction anti-fabrication design above.

## Frontend

React + Vite + TypeScript + Tailwind v4. Fusion21-branded (captured via Playwright from fusion21.co.uk: brand green `#00804A`, ink `#1E212B`, Lato font, pill-shaped buttons) — brand language applied to the app's own layout, not a literal clone of their site chrome. Categorical/status data-viz colors (role colors, compliance stamps) are separately validated for CVD-safety via the `dataviz` skill and are untouched by the rebrand — don't repaint them for brand consistency, they encode meaning, not identity.

Pages: `HomePage` (explainer), `NegotiatePage` (upload → extract → live SSE negotiation, reuses `CaseFileView`), `CasesPage` (static picker, formerly the root `/`), `AnalyticsPage` (batch metrics, unchanged). `CaseFileView` renders both static and live/in-progress negotiations with no separate "live mode" — every section is gated on data presence, including `OutcomeRibbon` which is gated on `resolution_outcome !== null` specifically so a live run doesn't show a misleading "Deadlock" ribbon before any outcome exists.

## Known Gaps (don't assume these are built)

- Full RAG/knowledge layer (ChromaDB, vector retrieval) — not built. The extraction agent is single-pass LLM synthesis with character-budget truncation, not retrieval.
- PostgreSQL persistence — not built, JSON only
- Docker / CI — not built
- Claude API migration — dependencies installed, not wired in; stay on Ollama until explicitly requested
- Pydantic v2 modernization (`model_config` syntax, `Field(default_factory=list)`, explicit `.model_rebuild()`) — recommended, not confirmed applied to live code

## Do Not

- Do not build on or extend `dispute-dashboard-legacy/` — it's deprecated
- Do not let the Court agent (or the extraction agent) fabricate arithmetic/formulas on qualitative scenarios — this is the project's central, hard-won empirical result
- Do not treat `batch_results/` as scratch space — it's evaluation output
- Do not run Python scripts/servers on Windows without `PYTHONIOENCODING=utf-8` if output is redirected/backgrounded — see "Windows gotcha" above
- Do not let the extraction agent report a disputed/mis-stated figure as a scenario's real contract value when the source text itself distinguishes the two (see Parkingeye source text for the pattern)
