# Repository context survey

Read-only survey produced 4 September 2026. Nothing was modified; the only thing
executed was `pytest` (§6), as sanctioned. Where a fact could not be established
from the repository it is marked **cannot determine** rather than guessed.

---

## 1. Tree

Excludes `__pycache__`, `node_modules`, `.git`, and the frontend build.

### `src/`

```
src/
├── __init__.py
├── graph_orchestrator.py        PRIMARY orchestrator: LangGraph StateGraph, .run() and .stream(),
│                                 build_agents(), no_court_check_node (ablation)
├── graph_state.py               TypedDict state schema passed between graph nodes
├── orchestrator.py              Legacy plain-loop orchestrator, retained as fallback
├── agents/
│   ├── __init__.py
│   ├── ca_agent.py              ContractingAuthorityAgent: pre-negotiation, round response, win statement
│   ├── bidder_agent.py          AggrievedBidderAgent: same three calls, bidder side
│   ├── court_agent.py           CourtAgent: per-round ComplianceAssessment; selects merits vs disclosure prompt
│   ├── summary_agent.py         SummaryAgent: non-negotiating, plain-English transcript summary
│   ├── extraction_agent.py      ScenarioExtractionAgent: raw document text -> DisputeScenario
│   └── zeroshot_agent.py        ZeroShotAgent: single-call baseline, deliberately unhardened
├── prompts/
│   ├── __init__.py
│   ├── ca_prompt.py             CA system prompt + build_ca_system_prompt(profile); Doc 1's 7 CA categories
│   ├── bidder_prompt.py         Bidder system prompt + build_bidder_system_prompt(profile); Doc 1's 6 supplier categories
│   ├── court_prompt.py          V3, V4 (derived), DISCLOSURE variants; COURT_SYSTEM_PROMPT = V4
│   ├── extraction_prompt.py     Extraction system prompt: symmetric anti-fabrication / do-not-drop-numbers
│   ├── summary_prompt.py        Summary agent system prompt
│   └── zeroshot_prompt.py       Naive baseline prompt, no Step 1/2A/2B gating by design
├── schemas/
│   ├── __init__.py
│   └── agent_state.py           All Pydantic models: DisputeScenario, ComplianceAssessment,
│                                 RoundResponse, CAProfile, BidderProfile, etc.
├── cases/
│   ├── __init__.py
│   ├── real_cases.py            REAL_CASES dict: 23 verified judgments as source text (955 lines)
│   └── loader.py                load_real_scenario(slug, refresh=False); caches to batch_results/_scenarios/
├── risk/
│   ├── __init__.py
│   └── challenge_risk.py        Pre-award challenge risk screen, 16 rules, no LLM call
├── recommendation/
│   ├── __init__.py
│   └── settlement_recommendation.py   Batch-level aggregation into a settlement recommendation; no LLM call
└── utils/
    ├── __init__.py
    ├── compliance_metrics.py    parse_llm_json(); per-response structural-compliance counters
    ├── negotiation_helpers.py   is_repetitive(), format_contract_value(), is_disclosure_dispute(), stage instructions
    ├── document_extraction.py   PDF/DOCX/TXT text extraction, combine_documents()
    ├── event_stream.py          Thread-local status emitter; no-op unless the API sets one
    └── ollama_connection.py     Ronin tunnel probe/connect, resolve_ollama_host_at_startup()
```

### `api/`

```
api/
├── __init__.py
├── main.py       FastAPI app: /api/extract, /api/negotiations, SSE stream, /api/risk-assessment,
│                  /api/system-status, /api/connect-gpu
├── sessions.py   In-memory session store; bridges sync .stream() into async SSE via thread + queue
└── models.py     Request/response Pydantic models for the API layer
```

### `scripts/`

```
scripts/
├── analyze_ablation_significance.py     Fisher's exact + bootstrap CIs on the V3/V4 ablation
├── analyze_batna_outcomes.py            Classifies outcome_relative_to_batna per role
├── analyze_citation_validity.py         Wrong-regime and s.12 subsection citation checks
├── analyze_negotiation_dynamics.py      Concession rate by round, retraction check, stagnation proxy
├── analyze_outcome_leakage.py           Does scenario.description state the real disposition?
├── analyze_qualitative_fabrication.py   Numeric grounding screen over Step 2B assessments
├── analyze_summary_readability.py       Flesch / Flesch-Kincaid over plain_english_summary
├── assess_challenge_risk.py             CLI for the pre-award risk screen
├── baseline_heuristic.py                Majority-class baseline, fixed prediction, no LLM
├── check_zeroshot_fabrication.py        Applies the grounding screen to zero-shot reasoning texts
├── compare_baselines.py                 Assembles the baselines comparison table
├── count_thesis_words.py                Body word count for the thesis; writes thesis_*/word.count
├── dump_prompt_example.py               Emits docs/prompt-example-court.json
├── generate_real_case_studies.py        Runs real cases end-to-end into negotiation_log_realcase_*.json
├── run_baseline_zeroshot.py             Runs the zero-shot baseline n times over a case
├── synthesize_settlement_recommendation.py   CLI over a completed batch summary
├── start_demo.ps1                       Tunnel + pre-warm + API + frontend, one command
└── stop_demo.ps1                        Tears the above down using .demo-state.json
```

### Batch runner (note: not under `scripts/`)

```
tests/run_batch_evaluation.py            The batch evaluator. See §2.
```

`tests/` also holds 13 `test_*.py` files; `pytest` summary in §6.

---

## 2. Batch running

### Command

```bash
cd procurement-dispute-negotiation
python tests/run_batch_evaluation.py --case <slug> --court-prompt V3|V4|active --runs 8 --rounds 5
```

On Windows, prefix with `PYTHONIOENCODING=utf-8` for any redirected or
backgrounded run — the case texts contain characters cp1252 cannot encode.

### Implementing script

`tests/run_batch_evaluation.py`. CLI (`tests/run_batch_evaluation.py:255-285`):

| Argument | Default | Effect |
|---|---|---|
| `--case` | `parkingeye-velindre` | Slug, constrained to `choices=sorted(REAL_CASES)` |
| `--court-prompt` | `active` | `active` \| `V3` \| `V4`; maps to a prompt constant, `active` passes `None` |
| `--runs` | `8` | Repetitions of the same scenario |
| `--rounds` | `5` | Max negotiation rounds per run |
| `--output-dir` | `batch_results` | Parent directory |
| `--refresh-scenario` | off | Re-extract instead of using cache; breaks comparability |
| `--no-court` | off | No-Court ablation; every run deadlocks by design |

### Scenario selection and repetition

One scenario per batch, chosen by `--case`. `--runs` sets repetitions of that
same scenario, so within-cell spread is sampling variation on a
non-deterministic model, not case variation. The scenario is loaded via
`load_real_scenario(args.case, refresh=args.refresh_scenario)`
(`tests/run_batch_evaluation.py:276`).

### Output location and shape

`batch_results/batch_<YYYYMMDD_HHMMSS>/` containing `run_01.json` … `run_NN.json`
plus `batch_summary.json` (`tests/run_batch_evaluation.py:140-143`).

`batch_summary.json` top-level keys, from `_build_summary`
(`tests/run_batch_evaluation.py:63-118`):

```
scenario_id, scenario_title, contracting_authority, bidder,
complete,                       # False until the final run lands
n_runs_requested, n_runs_completed_so_far, n_runs_successful, n_runs_failed,
max_rounds, timestamp,
court_prompt_version,           # "V3"/"V4"/... or "no-court-ablation"
include_court,
ca_profile, bidder_profile,     # Doc 1 modifiers, or null
metrics: {
    resolution_rate, deadlock_rate, manifest_error_detection_rate,
    average_rounds_to_conclusion, average_duration_seconds,
    outcome_distribution        # dict of outcome string -> count
},
compliance: { ... structural-compliance counters ... },
individual_runs: [ ... per-run records ... ]
```

The summary is rewritten after **every** run, not only at the end, and carries
`complete`. A batch killed part-way leaves `complete: false`; figures from such a
batch are crash-recovery artefacts, not results.

### Model / endpoint selection

The model name is hardcoded per agent as `model="llama3.1"` (see the table in the
next subsection). Only the *endpoint* is switchable, via the `OLLAMA_HOST`
environment variable, which `langchain_ollama.ChatOllama` respects through the
underlying `ollama` client.

Resolution order (`src/utils/ollama_connection.py:15-24, 47-55, 156`):

1. If `OLLAMA_HOST` is already set, it is respected and never overridden.
2. Otherwise `resolve_ollama_host_at_startup()` probes
   `RONIN_TUNNEL_URL = "http://127.0.0.1:11500"` and sets `OLLAMA_HOST` to it if
   reachable.
3. Otherwise local Ollama (default `:11434`) is left in place.

Tunnel constants: `RONIN_SSH_HOST = "shreyas-negotiation.ronin.manchester.ac.uk"`,
`RONIN_SSH_USER = "ubuntu"`, `TUNNEL_LOCAL_PORT = 11500`.
`connect_to_ronin()` spawns the SSH tunnel on demand and is idempotent; exposed as
`POST /api/connect-gpu`.

**Important caveat, documented in `CLAUDE.md`:** `ChatOllama` resolves
`OLLAMA_HOST` into a fixed client **once, at construction**. Any agent object
built before an `OLLAMA_HOST` change keeps talking to the old endpoint. Agents are
constructed per run inside `run_batch`, so a batch started after the tunnel comes
up is fine; a long-lived object created earlier is not.

### Temperatures

Set per agent at construction, hardcoded in the agent classes — there is no
config file:

| Agent | File:line | Temperature |
|---|---|---|
| Contracting Authority | `src/agents/ca_agent.py:16` | 0.3 |
| Aggrieved Bidder | `src/agents/bidder_agent.py:16` | 0.4 |
| Court | `src/agents/court_agent.py:11` | 0.2 |
| Summary | `src/agents/summary_agent.py:10` | 0.2 |
| Extraction | `src/agents/extraction_agent.py:29` | 0.2 (also `num_ctx=8192`) |
| Zero-shot baseline | `src/agents/zeroshot_agent.py:18` | 0.2 |

The two negotiating agents escalate temperature on a repetition retry:
`ca_agent.py:162` uses `min(0.3 + attempt * 0.2, 0.8)`; `bidder_agent.py:157`
uses `min(0.4 + attempt * 0.2, 0.9)`.

---

## 3. Scenario ingestion

### Source texts

`src/cases/real_cases.py` (955 lines). A single module-level dict `REAL_CASES`
keyed by slug. Each entry:

```python
"parkingeye-velindre": {
    "dispute_id": "REAL-PARKINGEYE-2026",
    "contracting_authority_name": "Velindre University NHS Trust / Cardiff and Vale University Health Board",
    "bidder_name": "Parkingeye Ltd",
    "source_text": (
        "Parkingeye Ltd v Velindre University NHS Trust & Cardiff and Vale University "
        "Health Board [2026] EWHC 1019 (TCC) — the first reported judgment under the "
        "Procurement Act 2023.\n\n"
        ...
    ),
}
```

`source_text` is hand-written dense prose, not a scraped judgment. 23 slugs are
present.

### Extraction agent and prompt

- Agent: `src/agents/extraction_agent.py`
- Prompt: `src/prompts/extraction_prompt.py` (`EXTRACTION_SYSTEM_PROMPT`,
  `EXTRACTION_USER_TEMPLATE`)
- Guard: `MIN_SOURCE_TEXT_CHARS = 200` (`extraction_agent.py:15`), raising before
  any LLM call if the source is shorter (`extraction_agent.py:47-51`).

### `DisputeScenario` (`src/schemas/agent_state.py:109-136`)

```python
class DisputeScenario(BaseModel):
    dispute_id: str
    title: str
    description: str
    # None means "not stated in the source" - genuinely different from a £0 contract,
    # and must be treated as such downstream (see format_contract_value() in
    # negotiation_helpers.py) rather than defaulting to 0, which reads as a real
    # zero-value contract rather than an unknown one. See real-case-test-findings.md.
    contract_value_gbp: Optional[float] = None
    dispute_type: str
    procedural_stage: str
    # The actual legislation/regulations governing this dispute (e.g. "Public
    # Contracts Regulations 2006", "Procurement Act 2023"), extracted from the
    # source rather than assumed - a case predating the 2023 Act cannot be governed
    # by it. None means not stated/inferrable in the source; downstream agents fall
    # back to the Procurement Act 2023 default in that case (see build_ca_system_prompt
    # and build_scenario_context in ca_agent.py/bidder_agent.py).
    governing_legislation: Optional[str] = None
    contracting_authority_name: str
    bidder_name: str

    # Doc 1 behavioural modifiers for this dispute. Both optional and defaulting to
    # None, so every existing scenario constructor keeps working untouched. Because
    # they live on the scenario, they are serialised into every saved negotiation log
    # by save_log() — which is what makes a profiled batch run reproducible after the
    # fact rather than only knowable from the script that launched it.
    ca_profile: Optional[CAProfile] = None
    bidder_profile: Optional[BidderProfile] = None
```

### Where `description` is populated

The field is produced **entirely by the LLM**. `extract_scenario()` parses the
model's JSON, overrides only four identity fields, and constructs the model
(`src/agents/extraction_agent.py:60-67`):

```python
data["dispute_id"] = dispute_id
if contracting_authority_name:
    data["contracting_authority_name"] = contracting_authority_name
if bidder_name:
    data["bidder_name"] = bidder_name
return DisputeScenario(**data)
```

`description` is never post-processed, filtered, or truncated after this point.
There is no code path anywhere in the repository that removes content from
`description`.

### Every place `description` reaches an agent prompt

| File:line | Context |
|---|---|
| `src/agents/ca_agent.py:37` | Inside `build_scenario_context()`, under `DISPUTE DESCRIPTION:`; that string is prepended to the pre-negotiation prompt, every round-response prompt, and the win-statement prompt |
| `src/agents/bidder_agent.py:37` | Identical construction, bidder side |
| `src/agents/court_agent.py:31` | Inside `assess_round()`'s user message, under `Description:` |
| `src/agents/zeroshot_agent.py:30` | Inside the zero-shot user message, under `FACTS:` |
| `scripts/dump_prompt_example.py:46` | Reconstruction of the Court user message for the appendix JSON; mirrors `court_agent.py` |

Verbatim, `src/agents/ca_agent.py:23-38`:

```python
def build_scenario_context(self, scenario: DisputeScenario) -> str:
    governing_legislation = scenario.governing_legislation or "Procurement Act 2023 (default — not otherwise stated in the source)"
    return f"""
DISPUTE DETAILS:
- Dispute ID: {scenario.dispute_id}
- Title: {scenario.title}
- Contract Value: {format_contract_value(scenario.contract_value_gbp)}
- Dispute Type: {scenario.dispute_type}
- Procedural Stage: {scenario.procedural_stage}
- Governing Legislation: {governing_legislation}
- Your Organisation: {scenario.contracting_authority_name}
- Challenging Party: {scenario.bidder_name}

DISPUTE DESCRIPTION:
{scenario.description}
"""
```

Two prompt constants also *refer* to the description without interpolating it:
`src/prompts/court_prompt.py:123` (citation discipline) and
`court_prompt.py:149` (the grounding-against-stated-outcome block, quoted in §4).

### Caching

Yes. `src/cases/loader.py`:

- Location: `batch_results/_scenarios/<slug>.json`
- Format: `json.dumps(scenario.model_dump(), indent=2, default=str)` — a serialised
  `DisputeScenario`
- 23 files currently present

```python
path = cached_scenario_path(slug, cache_dir)
if path.exists() and not refresh:
    return DisputeScenario(**json.loads(path.read_text(encoding="utf-8")))
```

**Re-extraction is not required to change a scenario.** The cache file is read
directly and validated into the model, so editing the JSON changes what agents
receive on the next run. `--refresh-scenario` forces a fresh LLM extraction and,
per the module docstring, "invalidates comparability with any batch already run
against the cached version."

---

## 4. Prompts

### 4.1 Court agent, V4

V4 is **not** a separate literal. It is derived at import
(`src/prompts/court_prompt.py:275-286`):

```python
COURT_SYSTEM_PROMPT_V4 = COURT_SYSTEM_PROMPT_V3.replace(
    _V3_GUIDING_PRINCIPLES_BLOCK, _V4_INTERESTS_BLOCK
)

if COURT_SYSTEM_PROMPT_V4 == COURT_SYSTEM_PROMPT_V3:
    raise RuntimeError(
        "court_prompt.py: V4 substitution did not apply — _V3_GUIDING_PRINCIPLES_BLOCK "
        "no longer matches the text in COURT_SYSTEM_PROMPT_V3. Fix the anchor before use; "
        "silently falling back to V3 would misreport which prompt an evaluation ran under."
    )

COURT_SYSTEM_PROMPT = COURT_SYSTEM_PROMPT_V4   # line 289
```

So **V4 = V3 with exactly one block swapped**, and the two differ in exactly one
variable. Full V4 text is V3 (`court_prompt.py:48-215`) with lines 161-165
replaced by the V4 interests block.

#### V3 body (`src/prompts/court_prompt.py:48-215`)

```
You are the Court / Judge agent in a procurement dispute negotiation system,
modelled on the Technology and Construction Court (TCC) in England and Wales.

YOUR CORE PRINCIPLE — READ CAREFULLY:
Your role is NOT to balance the two sides or decide who is more sympathetic.
UK procurement law is process-based, similar to judicial review. Your ONLY
question is: did the Contracting Authority follow a lawful, rational, and
procedurally correct process? You do not decide who "deserves" to win the
contract — you decide whether the process was compliant.

CRITICAL INSTRUCTION — VERIFICATION, DONE CORRECTLY:

Step 1: First determine whether the scenario contains an OBJECTIVELY
COMPUTABLE fact — meaning the scenario explicitly states BOTH (a) a formula,
percentages, or weightings, AND (b) every specific numeric input value that
formula needs (e.g. BOTH bidders' actual sub-scores). A formula or weighting
stated ALONE, without the specific input values to run it, is NOT objectively
computable — treat that as Step 2B, not Step 2A. A stated correction, delta,
or adjustment (e.g. "the court reduced the winning bidder's marks by 40")
describes an OUTCOME, not an INPUT — it tells you what changed, not the
original figures the formula was applied to, and does not by itself make the
scenario computable.

Step 2A — IF (and only if) Step 1 confirms you have the formula AND every
input value it needs:
You MUST independently perform that exact calculation yourself, using ONLY
the numbers and formula given in the scenario. Do not invent point values,
weightings, or a formula that is not explicitly stated. Show your working.
If your calculation does not match the outcome that was issued, this is a
manifest error, regardless of whether the Contracting Authority admits it.

IF A FORMULA EXISTS BUT THE INPUTS ARE INCOMPLETE (this is a distinct case
from both 2A and 2B — read carefully): do not invent, assume, estimate, or
hypothesise the missing input values to "complete" the calculation, not even
as an illustrative example, and not even if you explicitly label it as an
assumption (e.g. starting a sentence with "let's assume the original scores
were..."). Writing down a number that is not stated in the scenario is
fabricated evidence regardless of how it is framed or hedged — this applies
exactly as much to a "hypothetical" or "illustrative" number as to one
presented as fact. In this case you CANNOT perform Step 2A. Instead: treat
any correction or finding the scenario states as an authoritative fact you
were told, not one you need to independently re-derive from scratch, and
assess the rest of the dispute (was the process compliant, is there a
rational basis for the challenge or the correction) using Step 2B's
qualitative, no-invented-numbers reasoning instead.

Step 2B — IF the scenario does NOT contain an explicit formula (e.g.
qualitative criteria like "specificity, evidence, and named commitments"
with no stated points system, weightings, or calculation method):
Do NOT invent a formula, points system, or calculation — there is nothing to
compute, and any numbers you invent are fabricated, not evidence. In this
case, assess compliance qualitatively instead: was the published criteria
language applied in a way that is rationally defensible, even if you might
have scored it differently yourself? A large score gap alone is NOT proof of
manifest error if the Contracting Authority can point to a rational,
criteria-based justification for the difference. Only conclude manifest
error here if the Contracting Authority's own stated reasoning is internally
inconsistent, contradicts the published criteria's plain wording, or amounts
to no defensible justification at all (e.g. score awarded for something the
submission does not contain).

Do NOT let the Contracting Authority's tone, willingness to "provide
transparency," or procedural concessions (offering audits, feedback
sessions, standstill extensions) substitute for actually being correct —
but equally, do NOT manufacture false numerical precision on a dispute that
is genuinely a matter of qualitative judgement.

CRITICAL INSTRUCTION — CITATION DISCIPLINE (read as carefully as the
verification instruction above; this is the same anti-fabrication discipline
applied to legal citations instead of arithmetic):

Only cite a specific legal provision — a section number, regulation number,
or named statute (e.g. "Regulation 86(3)", "the Freedom of Information Act
2000", "s.51 Procurement Act 2023") — if it is ACTUALLY one of:
(a) a provision explicitly named in the scenario description or in either
    party's statements you have been given this round, or
(b) the general grounding materials already given to you in this system
    prompt: s12 of the Procurement Act 2023 (value for money, public
    benefit, transparency, integrity) and the general TCC / judicial-review
    framework described throughout this prompt.

You do NOT have independent knowledge of every provision of every UK
procurement statute or regulation, and you must not write as though you do.
If you want to make a general legal point that is not tied to a specific
pinpoint citation from (a) or (b) above, make that point in your "reasoning"
text without inventing a citation to support it — a correct general point
with no citation is far better than a specific-sounding citation that does
not exist. This mirrors the numeric anti-fabrication instruction above
exactly: a plausible-sounding but invented regulation number is fabricated
evidence, the same as a plausible-sounding but invented sub-score.

If the scenario states which legislation actually governs this dispute, cite
THAT regime's provisions where relevant, not the Procurement Act 2023 by
default. An older case can be governed by the Public Contracts Regulations
2015 or 2006 instead of the 2023 Act — check the scenario details for this.
Citing 2023 Act provisions for a case that could not legally have been
governed by it (because it predates the Act) is itself a fabricated
citation, not a harmless generalisation — treat it with the same seriousness
as citing a statute that does not exist at all.

GROUNDING AGAINST A STATED REAL OUTCOME: if the scenario description itself
states what a court or tribunal actually decided in this dispute (e.g. "the
court ordered disclosure of...", "the court found no error and dismissed the
challenge"), treat that as an authoritative fact about the outcome — the same
way you already treat a stated scoring correction as authoritative rather
than re-deriving it from scratch. Your assessment of process and compliance
this round is still your own independent judgement, but your
recommended_action must not end up contradicting an outcome the scenario
itself already tells you occurred. A negotiation that reaches a conclusion
flatly contradicting the real, stated disposition of the real dispute it is
modelled on is a failure of this instruction, not a sign of independent
judgement.

YOUR GUIDING PRINCIPLES:                     <-- V3 ONLY; replaced in V4
- Independence — you have no stake in the outcome
- Impartiality — you assess process, not sympathy
- Integrity — you apply the law and the facts as they actually are, not as
  either party frames them, and not as you might invent them

WHAT YOU ASSESS EACH ROUND:
1. Was the published evaluation methodology followed?
2. Is there evidence of a manifest error? Use Step 2A (compute) if the
   scenario is numeric, or Step 2B (qualitative rational-basis check) if it
   is not. Never fabricate a calculation the scenario does not support.
3. Did the Contracting Authority act rationally and in good faith?
4. Were the objectives in s12 of the Procurement Act 2023 upheld (value for
   money, public benefit, transparency, integrity)?

WHAT YOU DO NOT DO:
- You do not decide the bidder should win because their case is more sympathetic
- You do not re-score the bid yourself based on subjective judgment
- You do not split the difference between the parties artificially
- You do not wait for a party to confess before recognising an objectively
  verifiable error
- You do NOT invent a points system, weightings, or arithmetic that is not
  explicitly given in the scenario
- You do NOT invent illustrative or "assumed" sub-scores, component figures,
  or baseline numbers to complete a calculation when the scenario states a
  formula but not the specific inputs it needs — even as a labelled
  hypothetical, even if it makes your working look more complete
- You do NOT cite a specific regulation number, section number, or statute
  name that is not present in the scenario, the parties' statements, or your
  own general grounding materials (s12 Procurement Act 2023, the TCC /
  judicial-review framework) — see CITATION DISCIPLINE above

YOUR POSSIBLE RECOMMENDED ACTIONS:
- "continue negotiation" — no clear compliance issue found, even after your
  own independent check
- "re-evaluation" — manifest error found (whether admitted or not), CA
  should redo the scoring
- "no remedy - decision stands" — process was compliant and independently
  verified (or rationally justified) as correct, bidder's challenge fails
- "damages" — process failure found but re-running procurement is impractical

OUTPUT FORMAT:
Respond ONLY with valid JSON matching this structure exactly:
{
  "round_number": 0,
  "process_followed": true,
  "manifest_error_found": false,
  "applicable_provisions": ["only provisions that are actually present in your inputs or general grounding materials — see CITATION DISCIPLINE above, do not invent regulation numbers or statute names"],
  "reasoning": "State clearly whether this scenario was numeric (Step 2A) or qualitative (Step 2B), show any real calculation you performed using ONLY numbers given in the scenario, or explain your qualitative rational-basis reasoning, then state your conclusion.",
  "recommended_action": "...",
  "deadlock": false
}
```

#### The block that differs — V3 (`court_prompt.py:219-225`)

```python
_V3_GUIDING_PRINCIPLES_BLOCK = """YOUR GUIDING PRINCIPLES:
- Independence — you have no stake in the outcome
- Impartiality — you assess process, not sympathy
- Integrity — you apply the law and the facts as they actually are, not as
  either party frames them, and not as you might invent them
"""
```

#### The block that differs — V4 (`court_prompt.py:227-274`)

```python
# Doc 1, "Courts / Judiciary" — Primary Interests & Drivers, all six categories.
_V4_INTERESTS_BLOCK = """YOUR PRIMARY INTERESTS & DRIVERS:

1. Upholding the Law & Public Trust
   Maintain the rule of law. Ensure compliance with procurement regulations,
   case law, and the principles of fairness and transparency. Maintain public
   trust in the legal and procurement system. You are bound by the three Is:
   Independence — you have no stake in the outcome; Impartiality — you assess
   process, not sympathy; Integrity — you apply the law and the facts as they
   actually are, not as either party frames them, and not as you might invent
   them.

2. Procedural Correctness over Substantive Merits
   You do not re-run the procurement. You examine rationality, proportionality,
   whether manifest error occurred, and whether the evidence supports the
   decision-making. Your question is "was the procedure lawful?", never "who
   should win?".

3. Ensuring Equality between both Parties
   Provide a fair hearing in which both parties can present their arguments,
   while preventing the bidder from fishing for information beyond what is
   necessary.

4. Proportionality & Remedies
   Choose remedies aligned with the seriousness of the breach: lift or maintain
   the automatic suspension; declare a breach without cancelling the contract;
   award damages where appropriate. Avoid remedies disproportionate to the
   error. On automatic suspension specifically, case law consistently accepts
   public interest and service continuity as decisive considerations.

5. Efficient Use of Judicial Resources
   Encourage settlement or the narrowing of issues, often through mediation.
   Avoid lengthy litigation on matters that could be resolved through disclosure
   or clarification instead.

6. Systemic Integrity
   Follow the Civil Procedure Rules and court guidance. Your decisions set
   precedents that affect future procurement behaviour across the public sector,
   so aim to strike a balance that avoids creating overly burdensome obligations
   for contracting authorities.

PRECEDENCE — these interests inform WHICH REMEDY you recommend once you have
reached a finding. They never change the finding itself. In particular, your
interest in efficient use of judicial resources and in encouraging settlement
must not soften a manifest error you have actually verified under Step 2A or
established under Step 2B, and must not lead you to recommend "continue
negotiation" as a way of avoiding a conclusion the evidence supports.
"""
```

#### The stated-outcome sentence

`src/prompts/court_prompt.py:149-160`, present in both V3 and V4 (it sits in the
shared body, not the swapped block). The operative sentence, lines 155-157:

> Your assessment of process and compliance this round is still your own
> independent judgement, but your **recommended_action must not end up
> contradicting an outcome the scenario itself already tells you occurred.**

The same block is repeated in the disclosure-branch prompt at
`court_prompt.py:394`.

### 4.2 CA round-response prompt

`src/agents/ca_agent.py:118-144`, inside `respond_to_round()`:

```python
base_instruction = f"""
{scenario_context}

NEGOTIATION ROUND {round_number} of {max_rounds}.

{stage_instruction}

YOUR OWN PREVIOUS STATEMENTS IN THIS NEGOTIATION (do not repeat these):
{format_previous_statements(own_previous)}

Only cite a specific figure, score, or breakdown if it is actually stated in
the DISPUTE DETAILS/DESCRIPTION above or was actually said by the other
party earlier in this conversation — do not invent a number about your own
or the other party's evaluation that was not actually given to you.

Respond ONLY with valid JSON matching this exact flat structure — no nesting, no extra keys:
{{
  "message": "your 2-3 paragraph response here as a single string",
  "proposal": "specific proposal if you are making one, or null",
  "concession_made": "any concession you are offering, or null"
}}

"proposal" and "concession_made" MUST each be a single plain-English string
(or null) — NEVER a nested JSON object.
WRONG: "proposal": {{"partial_award": true, "percentage_of_contract_value": 0.5}}
RIGHT: "proposal": "A partial award covering 50% of the contract value"
"""
```

On a repetition retry an extra WARNING paragraph is appended
(`ca_agent.py:155-159`), and temperature escalates.

### 4.3 Bidder round-response prompt

`src/agents/bidder_agent.py:113-139`. **Byte-identical to the CA version above**
except that `{scenario_context}` resolves to the bidder's own
`build_scenario_context()` (which labels the parties "Your Organisation" /
"Contracting Authority" the other way round). The anti-fabrication paragraph is
word-for-word the same, added to both agents in commit `5ee1b6b`.

---

## 5. Analysis scripts

All analysis scripts read committed logs and make **no** model calls, except
`run_baseline_zeroshot.py` and `generate_real_case_studies.py`.

Corpus glob used by the `analyze_*` family: root `negotiation_log_*.json` plus
`batch_results/batch_*/run_*.json` — 299 logs at time of survey.

| Script | Consumes | Emits | Invocation | Thesis figure |
|---|---|---|---|---|
| `analyze_outcome_leakage.py` | `batch_results/_scenarios/*.json`, all run logs | stdout table, leaked/leak-free split | `python scripts/analyze_outcome_leakage.py [--verbose]` | Table 3.2, §3.5; the 7/8 leak-free figure |
| `analyze_qualitative_fabrication.py` | all logs | stdout + `--json` | `python scripts/analyze_qualitative_fabrication.py [--verbose]` | 9 of 425 (2.1%), Table 3.3 |
| `analyze_citation_validity.py` | all logs | stdout counts by bucket | `python scripts/analyze_citation_validity.py` | 162/702 = 23.1%; 7/21 = 33.3%; Figure 3.4 |
| `analyze_ablation_significance.py` | named batch dirs in `CASES` | stdout p-values + bootstrap CIs | `python scripts/analyze_ablation_significance.py` | Table 3.4 Fisher's p column |
| `analyze_batna_outcomes.py` | all logs | stdout per-role classification | `python scripts/analyze_batna_outcomes.py` | Table 3.5 (71%/1%/2%/27%, 24%/0%/21%/56%) |
| `analyze_negotiation_dynamics.py` | all logs | stdout rates | `python scripts/analyze_negotiation_dynamics.py` | 0.013→0.470, 0.000→0.075, 0.097/426, Figure 3.3 |
| `analyze_summary_readability.py` | all logs | stdout Flesch stats | `python scripts/analyze_summary_readability.py` | 24.7 / 25.9 / 14.7 / 57.5, §3.9 |
| `compare_baselines.py` | `batch_results/`, `baseline_results/zeroshot/` | stdout table | `python scripts/compare_baselines.py` | Table 3.1 baselines |
| `baseline_heuristic.py` | nothing (fixed prediction) | prediction dict | imported by `compare_baselines.py` | 5/6 heuristic row |
| `run_baseline_zeroshot.py` | a case slug | `baseline_results/zeroshot/zeroshot_<id>_<ts>/` | `python scripts/run_baseline_zeroshot.py --case <slug> --runs 5` | 6/6 zero-shot row |
| `check_zeroshot_fabrication.py` | zero-shot outputs | stdout | `python scripts/check_zeroshot_fabrication.py` | "0 ungrounded numbers across 30 texts" |
| `assess_challenge_risk.py` | CLI flags | stdout + `--json` | `python scripts/assess_challenge_risk.py --score-margin narrow ...` | §3.11 risk-screen results |
| `synthesize_settlement_recommendation.py` | one `batch_summary.json` | stdout recommendation | `python scripts/synthesize_settlement_recommendation.py <batch_id>` | Not cited as a figure |
| `dump_prompt_example.py` | one run log | `docs/prompt-example-court.json` | `python scripts/dump_prompt_example.py` | Appendix B.4 |
| `count_thesis_words.py` | `thesis_*/`*.tex | stdout + `word.count` | `python scripts/count_thesis_words.py` | Word count on contents page |
| `generate_real_case_studies.py` | `REAL_CASES` | `negotiation_log_realcase_*.json` | `python scripts/generate_real_case_studies.py` | Frontend case studies |

### 5.1 `analyze_outcome_leakage.py`

Detection pattern (`scripts/analyze_outcome_leakage.py:56-68`):

```python
_LEAK = re.compile(
    r"(the court (found|held|ruled|ordered|dismissed|concluded|rejected|allowed)"
    r"|court of appeal"
    r"|judge (found|held|ruled)"
    r"|was (upheld|dismissed|allowed)"
    r"|declaration of ineffectiveness|declaring its ineffectiveness"
    r"|damages were awarded"
    r"|claim (was )?dismissed"
    r"|found in favour"
    r"|ultimately lost|reversed on appeal"
    r"|should have been awarded)",
    re.I,
)
```

Applied sentence-by-sentence over `scenario.description` from the **cached**
scenario, not the source text. Direction mapping (`:71-72`):

```python
_REMEDY = {"re-evaluation", "damages"}
_NO_REMEDY = {"no remedy - decision stands"}
```

Anything else (deadlock, disclosure, out-of-vocabulary) returns `None` and is
excluded from the vote. Ground truth is a hardcoded `MERITS_TRUTH` dict of 14
slugs → `"won"`/`"lost"`.

Output format — stdout, two blocks then a summary:

```
LEAKED - description states the real disposition  (6 cases)
    faraday-west-berkshire           real=lost  simulated=lost (34/35)           correct
    ...
    -> agreement 6/6

LEAK-FREE - description states facts only  (8 cases)
    ...
    -> agreement 7/8

  Combined       : 13/14
  Leak-free only : 7/8   <- the defensible figure
  Leaked         : 6/6   <- the Court was told, and instructed not to contradict
```

### 5.2 Numeric grounding screen

`scripts/analyze_qualitative_fabrication.py`.

Score-shaped number regex (`:73-84`):

```python
_SCORE_NUMBER = re.compile(
    # NB: the first branch deliberately has NO trailing \b — % and the closing digit of "/100" are
    # non-word characters, so a \b immediately after either can never match ordinary text (a \b
    # requires a word/non-word transition, and "% " or "%<end>" is non-word on both sides). An earlier
    # version had this bug and silently missed every bare "NN%" not preceded by the word "score(d)" —
    # caught only by testing extraction against real text with two percentages, not by inspection.
    r"\b(\d{1,3})\s*(?:%|/\s*100)"
    r"|\bscored?\s+(?:a\s+|an?\s+)?(?:of\s+)?(\d{1,3})\b"
    r"|\b(\d{1,3})\s*points?\b",
    re.I,
)
```

Population classifier — this is what decides entry into the 425 (`:56-95`):

```python
_QUALITATIVE_MARKERS = re.compile(
    r"\b(step 2b|this scenario is qualitative|scenario is qualitative|assess.{0,20}qualitatively|"
    r"no explicit formula|without explicit (numbers|formula)|no stated (formula|points system))\b",
    re.I,
)

_NUMERIC_MARKERS = re.compile(
    r"\b(step 2a|this scenario is numeric|scenario is numeric)\b", re.I,
)

def _classify(reasoning: str) -> str:
    """'qualitative' / 'numeric' / 'ambiguous_or_neither' — never guess between the first two."""
    is_qual = bool(_QUALITATIVE_MARKERS.search(reasoning))
    is_num = bool(_NUMERIC_MARKERS.search(reasoning))
    if is_qual and not is_num:
        return "qualitative"
    if is_num and not is_qual:
        return "numeric"
    return "ambiguous_or_neither"
```

Classification is **on the Court's own reasoning text**, not on the scenario. The
screening gate (`:139-140`):

```python
if cls != "qualitative":
    continue
```

Consequence, and the documented Bromcom miss: a run whose reasoning opens "This
scenario is numeric" classifies `numeric`, never enters the 425, and is never
screened — regardless of what it fabricated. Corpus split at survey time:
qualitative 425, numeric 35, ambiguous_or_neither 52.

### 5.3 Baselines table

Four components:

1. **Majority-class** — `scripts/baseline_heuristic.py`. A module-level
   `MAJORITY_CLASS_PREDICTION` dict returned unchanged by `predict(scenario)`;
   no LLM, no case-specific reasoning. `compare_baselines.py:111` hardcodes
   `heuristic_pred = True`.

2. **Zero-shot** — `src/agents/zeroshot_agent.py` + `src/prompts/zeroshot_prompt.py`,
   driven by `scripts/run_baseline_zeroshot.py`. One `ChatOllama` call at
   temperature 0.2, output parsed into the same `ComplianceAssessment` schema:

   ```python
   class ZeroShotAgent:
       def __init__(self):
           self.llm = ChatOllama(model="llama3.1", temperature=0.2, format="json")

       def assess(self, scenario: DisputeScenario) -> ComplianceAssessment:
           user_message = f"""
   DISPUTE: {scenario.title}
   ...
   FACTS:
   {scenario.description}
   """
           messages = [("system", ZEROSHOT_SYSTEM_PROMPT), ("user", user_message)]
   ```

   Writes to `baseline_results/zeroshot/zeroshot_<dispute_id>_<timestamp>/`.

3. **Full pipeline** — ordinary batches in `batch_results/`.

4. **No-Court ablation** — `--no-court` on the batch runner, wired via
   `include_court` through `build_negotiation_graph`
   (`src/graph_orchestrator.py:300, 318, 356-380`):

   ```python
   court_node_fn = court_check_node if include_court else no_court_check_node
   ```

   `no_court_check_node` (`graph_orchestrator.py:190-212`) leaves
   `compliance_checks` untouched and only performs the max-rounds check, so every
   run deadlocks by construction. Its docstring is explicit that inferring
   resolution from dialogue tone "would defeat the point of the ablation."

Scoring basis (`scripts/compare_baselines.py:69-87`) — deliberately
`recommended_action`, not `manifest_error_found`:

```python
_REMEDY_ACTIONS = {"re-evaluation", "damages"}
...
return round(sum(1 for r in runs if r["outcome"] in _REMEDY_ACTIONS) / len(runs), 3)
```

### 5.4 V3/V4 ablation and Fisher's exact

`scripts/analyze_ablation_significance.py`. Batch pairs are hardcoded
(`:34-46`), e.g.:

```python
CASES = {
    "lancashire-care": ("batch_20260815_213642", "batch_20260815_214210"),
    "faraday-west-berkshire": ("batch_20260815_214543", "batch_20260815_215108"),
    ...
}
```

Fisher's exact is implemented from the hypergeometric definition rather than
adding scipy (`:47-70`), two-tailed by summing every table with the same margins
whose probability is ≤ the observed table's. Verified in
`tests/test_fisher_exact.py` against properties derivable independently of the
implementation. The module docstring states plainly that at n=8 the test has very
low power and p-values must be reported as p-values, not verdicts.

---

## 6. Current state

```
$ git branch --show-current
frontend-rebuild

$ git log --oneline -10
6a3a3fc Act on the examiner review: disclose the Bromcom miss, restore booktabs, add the procurement-remedies literature
93e20ef Trim the body to 8,338 words and add an examiner context pack
cd57077 Answer the supervisor's two questions, and measure the leakage the first one found
75bf61d Add the video run-down for the 15% video component
ffe9cce Fix referencing, close the tables, add three data figures, correct two facts
318ccb2 Consolidate to a single thesis folder and repoint the word-count script
0ffd5c1 Add the dissertation report, and the corpus logs its figures are computed from
5ee1b6b Two anti-fabrication fixes found via a real Fusion21 employee test case
9c000ba Fix two display-layer bugs found in live Geodesign re-test
2f1adb0 Merge real-case-grounding-fix: extraction defaulting bugs, Court citation discipline, and dispute-type branching

$ git status --short
(clean — no output)
```

```
$ ollama list
NAME                       ID              SIZE      MODIFIED
llama3.1:latest            46e0c10c039e    4.9 GB    2 months ago
nomic-embed-text:latest    0a109f422b47    274 MB    5 months ago
llama3.2:latest            a80c4f17acd5    2.0 GB    5 months ago
llama3.2:1b                baf6a787fdff    1.3 GB    6 months ago
llama3:latest              365c0bd3c000    4.7 GB    6 months ago
```

### GPU tunnel

**Not currently reachable.** Local Ollama on `:11434` **is** reachable.
`OLLAMA_HOST` is unset, so a run started now would use local CPU Ollama.

Check command:

```bash
curl -s -m 5 http://127.0.0.1:11500/api/tags >/dev/null && echo REACHABLE || echo "NOT reachable"
```

Equivalent in-project checks: `GET /api/system-status` (reports `ollama_host`,
`reachable`, `using_gpu_tunnel`), or `src/utils/ollama_connection.py::_is_reachable`.
To bring it up: `.\scripts\start_demo.ps1`, or `POST /api/connect-gpu`, or the
raw SSH command in `CLAUDE.md`.

### pytest

```
92 passed in 19.25s
```

### Corpus counts

| Item | Count |
|---|---|
| Batch directories (`batch_results/batch_*`) | 59 |
| Run logs inside batches | 283 |
| Root `negotiation_log_*.json` | 16 |
| **Total logs the analysis scripts see** | **299** |
| Cached scenarios (`batch_results/_scenarios/*.json`) | 23 |

---

## 7. Feasibility notes

Not implemented — assessment only.

### (a) Strip the disposition at ingestion, re-run all 14 merits cases

**Files:** `src/agents/extraction_agent.py` (post-process `description` before
constructing `DisputeScenario`, around lines 60-67), or a new filter module;
`src/prompts/extraction_prompt.py` if done by instruction instead of code;
`batch_results/_scenarios/*.json` (regenerate); optionally
`scripts/analyze_outcome_leakage.py` to reuse `leak_sentences()` as the stripper.

**Harder than it looks:**

- **The detector was built to over-flag.** Its docstring says it "errs toward
  calling a scenario leaked" because a false positive only shrinks the clean
  subset, whereas a false negative inflates the headline claim. Reusing it as a
  *stripper* inverts that safety property: over-flagging now deletes real case
  facts. A sentence like "the court found no error **in the moderation process,
  which the authority had documented in full**" carries evidence the agents need.
- **Sentence-level granularity may be too coarse.** Optima Health's description
  states the first-instance and appellate outcomes in one sentence each; Woods'
  leaking sentence also carries the 60/40 formula and the ±40/+6 mark correction —
  which is precisely the Step 2A input the Woods case exists in the corpus to
  exercise. Stripping it would silently convert Woods from a numeric case to a
  qualitative one and change what the ablation measures.
- **Re-running invalidates comparability.** Every existing batch ran against the
  current cache. New batches are not comparable with old ones, so the V3/V4
  ablation, the baselines table, and every corpus-wide figure in §5 would need
  re-running together or the report would mix two scenario generations.
- **Cost.** 14 cases × 8 runs × 5 rounds on local CPU: the slowest observed
  batch averaged 1,492 s/run. On the GPU tunnel a Woods run averaged ~24 s.
  Tunnel is currently down.
- **Cheaper alternative:** edit the 6 leaking cached JSONs by hand. The cache is
  read directly (§3), so no re-extraction is needed — only re-running the
  negotiations.

### (b) Re-run baselines on the 8 leak-free merits cases instead of 6

**Files:** `scripts/compare_baselines.py` (the case list and its `real` ground
truth); `scripts/run_baseline_zeroshot.py` invocations for the 2 added cases.

**Harder than it looks:**

- **The two sets barely overlap — this is mostly a new comparison, not an
  extension.** Verified against the corpus:

  | | Cases |
  |---|---|
  | In both | Braceurself, Lancashire (2) |
  | Baseline-6 only, all *leaked* | AbbVie, Bromcom, Faraday, Woods (4) |
  | New in leak-free 8 | Consultant Connect, EnergySolutions, InHealth, Siemens Mobility, TNLC, Turning Point (6) |

  So two thirds of the existing baseline table would be discarded and six new
  cases added. The headline "6/6 tie" cannot be partially reused.

- **Full-pipeline batches exist for all 8, but at uneven n.** Lancashire has 32
  runs across 4 batches; the other seven have 3 runs in 1 batch each. Comparing a
  32-run cell against 3-run cells in one table needs either a stated caveat or
  re-running the seven at matched n.

- **Zero-shot exists for only 2 of the 8.** `baseline_results/zeroshot/` holds
  six directories: AbbVie, Braceurself, Bromcom, Faraday, Lancashire, Woods — i.e.
  exactly the current baseline 6. Of the leak-free 8, only Braceurself and
  Lancashire have zero-shot output. **Six cases × 5 runs = 30 new zero-shot LLM
  calls** would be needed. That is the only LLM cost, and it is modest.

- **The majority-class floor changes, and that is the point.** The current 6 split
  5:1, giving a floor of 5/6. The leak-free 8 split 4:4, giving 4/8 — a much
  weaker predictor, so any result that beats it says more than the current table
  does. `baseline_heuristic.py`'s fixed prediction and `compare_baselines.py:111`'s
  hardcoded `heuristic_pred = True` would both need revisiting, since "always
  predict violation" is no longer the majority class on a 4:4 split.

### (c) Fix the fabrication screen, re-screen all 299 logs

**Files:** `scripts/analyze_qualitative_fabrication.py` only — the gate at line
139-140 and `_SCORE_NUMBER` at 73-84. Regression tests in
`tests/test_qualitative_fabrication.py` will need updating.
`scripts/check_zeroshot_fabrication.py` imports these helpers and inherits any
change.

**Harder than it looks:**

- **The two sub-changes have different risk.** Adding `A=80`-style forms to the
  regex is low risk. Screening `numeric` runs is not: on a genuine Step 2A run the
  Court is *supposed* to state numbers, and those numbers come from the scenario
  but often in derived form (a computed total is grounded in its inputs without
  appearing verbatim). Screening numeric runs against string-presence will
  produce false positives on correct arithmetic. The docstring already records
  exactly this: a prior "79−65=14" instance was a correct derivation flagged as
  suspect.
- **The 2.1% figure and the 425 denominator both move**, so §3.7, Table 3.3,
  Figure 3.5, the threats entry, RQ3, and Table 4.1's O3 row would all need
  updating together. The thesis currently states the bound as "within the screened
  population"; widening the population changes what that sentence means.
- **No model calls needed** — pure re-analysis over committed logs, seconds to run.
- A form like `A=80` has no unit, so distinguishing a fabricated sub-score from a
  section number or a date needs care; the existing regex is narrow deliberately.

### (d) Alstom V3/V4 cell from n=8 to n=30

**Files:** no code change. Two invocations with `--runs 30`, then
`scripts/analyze_ablation_significance.py`'s `CASES` dict updated to the new batch
directory names.

**Harder than it looks:**

- **Cost depends entirely on the tunnel, and the gap is two orders of magnitude.**
  Actual Alstom batch averages from `batch_summary.json`:

  | Batch | Arm | n | avg s/run | avg rounds |
  |---|---|---|---|---|
  | `batch_20260815_192629` | V3 | 8 | 56.7 | 4.38 |
  | `batch_20260815_193406` | V4 | 8 | 34.9 | 2.12 |
  | `batch_20260815_154131` | V3 | 4 | 1,492.1 | 4.00 |
  | `batch_20260815_172120` | V4 | 4 | 738.1 | 1.75 |

  The two ablation cells cited in the thesis are the n=8 pair (56.7 s and 34.9 s);
  the four-figure averages are earlier n=4 batches, and the ~26× gap is
  CPU-vs-tunnel, not case difficulty. So 60 runs (30 × 2 arms) is roughly
  **1.5 hours on the tunnel** and plausibly **15+ hours on local CPU**. The tunnel
  is currently down (§6), so this is gated on bringing it back up.

- **Statistical gain should be checked before spending the compute.** Alstom is
  currently 4/8 vs 8/8, p = 0.0769. If the rates held at n=30 the result would
  clear p < 0.05 comfortably, but rates observed at n=8 are themselves uncertain,
  and Fisher's exact on a 2×2 with one cell at ceiling behaves sharply. A power
  calculation costs nothing and would de-risk the run.

- **Mixed-n reporting.** One case at n=30 alongside four at n=8 makes Table 3.4
  heterogeneous; the caption and the threats-to-validity entry would need to say
  so, and `analyze_ablation_significance.py`'s output does not currently print n
  per cell.

- Everything else in the ablation stays valid — this cell is independent, and only
  the two `CASES` entries for Alstom would change.

### (e) Run a subset of cases against a second Ollama model

**Files:** every agent constructor hardcodes `model="llama3.1"` — `ca_agent.py:16`
and `:157`, `bidder_agent.py:16` and `:157`, `court_agent.py:11`,
`summary_agent.py:10`, `extraction_agent.py:29`, `zeroshot_agent.py:18`. Eight
sites across six files.

**Harder than it looks:**

- **There is no model parameter anywhere.** Threading one through means touching
  `AgentBundle`/`build_agents` (`graph_orchestrator.py:35-53`),
  `GraphNegotiationOrchestrator.__init__`, and `run_batch`, plus a `--model` CLI
  flag. Alternatively an env var read at construction — smaller change, but then
  it is not recorded in `batch_summary.json`.
- **Provenance would be silently wrong.** `batch_summary.json` records
  `court_prompt_version` but has no model field. A second-model batch would be
  indistinguishable from a llama3.1 batch on disk, and every `analyze_*` script
  globs all logs indiscriminately — so a mixed corpus would silently contaminate
  every corpus-wide figure in §5. Adding a `model` key to the summary and a filter
  to the analysis scripts is effectively a prerequisite, not an optional extra.
- **Available locally:** `llama3.2:latest` (2.0 GB), `llama3.2:1b`,
  `llama3:latest`, plus `nomic-embed-text` (embedding only, not usable here).
  Whether the Ronin instance has any model other than `llama3.1` pulled —
  **cannot determine**; the tunnel is down.
- **JSON-mode behaviour differs by model.** The structural-compliance rate
  (0.9986) is a llama3.1 figure; a smaller model such as `llama3.2:1b` may fail
  schema validation far more often, which would exercise the repair path heavily
  and is itself worth reporting rather than treating as noise.
- The prompts are tuned against llama3.1 over four documented revisions, so a
  second model's results measure prompt-portability as much as model capability —
  that confound should be stated rather than discovered later.
