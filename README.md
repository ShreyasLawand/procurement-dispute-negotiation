# Modelling Procurement Dispute Resolution via Multi-Agent LLM Negotiation

MSc Data Science Extended Research Project (DATA72000), University of Manchester,
in partnership with Fusion21. Student ID 14265414.

A multi-agent LLM system that simulates a UK procurement dispute — a Contracting
Authority, an Aggrieved Bidder, and a Court modelled on the Technology and
Construction Court — negotiating under the Procurement Act 2023, plus a
non-negotiating Summary agent and a rule-based pre-award challenge risk screen.

**This repository is the Additional Materials submission accompanying the ERP
report.** It exists to let a reader reproduce every figure, table, and claim in
the report without needing anything not included here (bar an Ollama install to
re-run the LLM itself). The report is submitted separately via Turnitin and is
not reproduced in this repo.

## Setup

```bash
git clone https://github.com/ShreyasLawand/procurement-dispute-negotiation.git
cd procurement-dispute-negotiation
pip install -r requirements.txt

# The agents run on a locally hosted Llama 3.1 via Ollama:
ollama pull llama3.1
```

Python 3.13. On Windows, set `PYTHONIOENCODING=utf-8` for any backgrounded or
redirected run — `graph_orchestrator.py`'s console output uses Unicode
box-drawing characters that crash the default `cp1252` console codepage
otherwise.

**A note on timing if running without GPU access.** Every LLM call in this
project is measured to run in a couple of seconds against a tunnelled GPU (see
the report's Appendix C.1), but on CPU-only Ollama a single call took **631
seconds (~10.5 minutes)** in a clean-machine test of the extraction agent
against a real uploaded PDF. A full 3-round negotiation makes roughly 12–15
such calls (pre-negotiation statements, 3 rounds of CA/Bidder/Court, win
statements, the summary), so budget well over an hour for one CPU-only run —
this is expected, not a hang. `python tests/test_langgraph_negotiation.py`
prints each agent's output as it completes, so progress is visible throughout
rather than silent until the end.

## Running it

```bash
python tests/test_langgraph_negotiation.py     # a single negotiation — primary entrypoint
python tests/run_batch_evaluation.py           # batch runner, writes to batch_results/
python scripts/generate_real_case_studies.py   # the 4 real-case demos (extraction + negotiation)
python -m pytest                               # test suite (92 cases)
```

Full API + frontend:

```bash
python -m uvicorn api.main:app --reload --port 8000   # from repo root

cd frontend && npm install && npm run sync-data && npm run dev
```

`npm run sync-data` copies `batch_results/` and the root `negotiation_log_*.json`
files into `frontend/public/data/` — required once before the Analytics page has
anything to show, not automatic.

## Repository structure

```
src/            Python backend — agents (CA, Bidder, Court, Summary, Extraction),
                LangGraph orchestrator, Pydantic schemas, the 23-case verified corpus
scripts/        Every analysis script behind a number in Chapter 3 of the report
                (see "Reproducing the report's figures" below), plus the risk screen
tests/          pytest suite, including the batch evaluation CLI
api/            FastAPI backend — extraction endpoint, streaming (SSE) negotiation
frontend/       React/TypeScript client (Vite + Tailwind) — Home, Negotiate, Cases,
                Analytics, the risk screen
docs/           One real case document used for the live-demo upload flow (see note
                below) and a batch-evaluation findings note
batch_results/  The full evaluation corpus: every batch of negotiation runs behind
                every corpus-wide statistic in Chapter 3
baseline_results/
                Recorded output of the two baselines in Table 3.1 (zeroshot/, no_court/)
negotiation_log_*.json
                Individual negotiation transcripts at the repo root — the 4
                `realcase_*` ones are the report's real-case-study demos; the
                `live_*`/`phase3_*` ones are additional runs from the same corpus
                that several analysis scripts (BATNA, fabrication, citation
                validity, negotiation dynamics, readability) glob over alongside
                batch_results/ — see the table below
```

## Data

**The 23-case verified corpus is self-contained in `src/cases/real_cases.py`** —
each case is a dense factual narrative (citation, contract value, dispute type,
outcome) written as a Python string, individually checked against BAILII or the
National Archives before being committed. No external download is needed to run
anything in this repo; the full citation list, verification method, and the
7 candidates that were researched and rejected are in the report's Appendix A.

**`docs/Prime way care ltd vs The Mayor And Burgesses.pdf`** is a real, small,
public tribunal document used only for the live document-upload demo (shown in
the project video) — it is **not** part of the 23-case evaluation corpus and no
figure in the report depends on it. Kept for anyone wanting to replay that
specific demo; safe to ignore otherwise.

**Fusion21's four internal documents** (interests & drivers, escalation ladder,
negotiation theory, worked examples) that the agent system prompts are specified
against are commercially confidential and are **not included** — this matches
the report's own AI-use statement, which states they are summarised, not
reproduced. Their categories (7 CA / 6 supplier / 6 judiciary interest headings)
are described in the report and visible in the agent prompts under `src/prompts/`,
just not the source documents themselves.

## Reproducing the report's figures

LLM sampling is stochastic even at low temperature, so re-running the agents will
not reproduce byte-identical logs — the logs in `batch_results/` and the root
`negotiation_log_*.json` files **are** the computational record. The scripts
below recompute every reported statistic from those logs; running them requires
no LLM calls and no GPU.

| Report figure | Command / source |
|---|---|
| Structural compliance, §3.3 | reads `compliance` from every `batch_results/batch_*/batch_summary.json` |
| V3/V4 ablation, Table 3.2 | `python tests/run_batch_evaluation.py --case <slug> --court-prompt V3\|V4 --runs 8 --rounds 5` |
| Ablation significance, Table 3.2 | `python scripts/analyze_ablation_significance.py` |
| Baseline comparison, Table 3.1 | `python scripts/run_baseline_zeroshot.py`; `compare_baselines.py`; `run_batch_evaluation.py --no-court` |
| Numeric fabrication, Table 3.3 | `python scripts/analyze_qualitative_fabrication.py` |
| Citation validity, §3.7.1 | `python scripts/analyze_citation_validity.py` |
| Concession dynamics, §3.8 | `python scripts/analyze_negotiation_dynamics.py` |
| BATNA outcomes, §3.8 | `python scripts/analyze_batna_outcomes.py` |
| Summary readability, §3.8 | `python scripts/analyze_summary_readability.py` |
| Risk screen, §3.9 | `python scripts/assess_challenge_risk.py` |
| Outcome-leakage audit, §3.4 | `python scripts/analyze_outcome_leakage.py` |
| Logged prompt example, Appendix B.4 | `python scripts/dump_prompt_example.py` |

The six corpus-wide scripts (fabrication, outcome-leakage, BATNA, citation
validity, negotiation dynamics, readability) glob over **every** file in
`batch_results/batch_*/` and every root-level `negotiation_log_*.json` — not a
named subset — which is why the full corpus is included rather than trimmed to
only the batches named in Table 3.1/3.2. At ~7MB total it costs nothing to keep
complete, and keeping it complete is what makes every corpus-wide number in
Chapter 3 independently checkable, not just the headline ones.

Full environment details, per-agent configuration (interest source, sampling
temperature, structured-output schema), the Court prompt's four-revision history,
and further plan-change decisions are in the report's Appendix C — this README
summarises the reproduction path; Appendix C is the authoritative record of *why*
each choice was made.

## Testing

```bash
python -m pytest
```

92 test cases, including a regression test for the outcome-leakage measurement
gap and one for a baseline-comparison bug, both caught and fixed during
evaluation (see `tests/test_outcome_leakage.py`, `tests/test_compare_baselines.py`).
