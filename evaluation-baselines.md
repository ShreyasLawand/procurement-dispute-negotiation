# Baseline Comparisons: Does the Multi-Agent Architecture Earn Its Complexity?

*Evaluation punch-list item 22. Answers the question a dissertation examiner is most
likely to ask about this project: does the multi-agent negotiation pipeline actually
outperform something simpler, or would a single well-formed prompt get you the same
answers? Three baselines were built and run against this project's real-case corpus:
a majority-class heuristic, a single-LLM zero-shot call, and a no-Court ablation of the
existing pipeline.*

## 1. Scope: 6 of 8 real cases

Comparable on only 6 of this project's 8 real cases. Parkingeye and Alstom are interim-
suspension rulings only — the real court never reached the merits question this system
evaluates — the same exclusion already applied in `evaluation-five-cases.md` and
`evaluation-bailii-expansion.md`. Comparing a merits prediction against a real
disposition that was never itself a merits ruling would not be a meaningful check.

Of the 6 remaining cases, **5 are "CA lost" and only 1 (AbbVie) is "CA won."** This
imbalance is itself load-bearing for how every result below should be read — see §2.

## 2. The heuristic baseline, and the base-rate problem it exists to surface

`scripts/baseline_heuristic.py` — no LLM call, no case-specific reasoning, a single
hardcoded prediction ("manifest error found, recommend re-evaluation") applied
identically to every case. This is the standard "majority-class" baseline from ML
evaluation practice, made explicit rather than left implicit: given the 5:1 imbalance
in §1, a predictor that always guesses the majority class scores **5/6** by base rate
alone, with zero reasoning. Any accuracy number reported for the full pipeline or the
zero-shot baseline has to be read against that floor, not treated as evidence of skill
by itself.

## 3. The zero-shot baseline

`src/agents/zeroshot_agent.py` + `src/prompts/zeroshot_prompt.py` + `scripts/run_baseline_zeroshot.py`
— one LLM call per case, no negotiation, no CA/Bidder role-play, no pre-negotiation
interests/BATNA phase. Deliberately **not** hardened the way `court_prompt.py` is: no
explicit ban on inventing "illustrative" values, no Step 1/2A/2B gating, no Doc 1
taxonomy. It reads like a reasonable first-draft prompt a competent-but-not-especially-
careful engineer might write — not a strawman, but genuinely simpler. Output reuses the
`ComplianceAssessment` schema exactly, so the same `parse_llm_json()` validates it and
its output is directly comparable to a real Court assessment, not a different shape
needing its own parsing path. Run at n=5 per case (30 calls total, via the Ronin GPU
tunnel).

## 4. The no-Court ablation

Added `no_court_check_node` to `graph_orchestrator.py`, bound into the `"court_check"`
graph position via a new `include_court` flag on `build_negotiation_graph` /
`GraphNegotiationOrchestrator` (also wired into `tests/run_batch_evaluation.py` as
`--no-court`). CA and Bidder negotiate normally; no Court agent ever runs.

**This ablation cannot express a violation-found prediction at all, by design.**
Nothing in this graph can decide the parties have converged except
`court_check_node`'s `recommended_action != "continue negotiation"` check — remove the
Court and remove the only mechanism that ever produces a non-deadlock outcome. A
version of this ablation that tried to fabricate a resolution-detection heuristic from
the dialogue text (e.g. "does the Bidder's last message sound conciliatory?") would
defeat the point: the finding this baseline exists to surface is precisely that nothing
in this system resolves anything without judicial adjudication.

Run at n=3 per case, 3 rounds, across all 6 comparable cases (18 runs). **Result:
100% deadlock, 0/18 runs, uniformly across every case** — confirmed exactly as designed,
not a partial or noisy result. `tests/test_no_court_ablation.py` locks the node's
behaviour in directly (mid-negotiation never resolves; only `round >= max_rounds`
deadlocks; `compliance_checks` is never touched).

## 5. A metric correction, caught before trusting the comparison

The first version of the comparison (`scripts/compare_baselines.py`) scored each
system's "violation found" prediction against `manifest_error_found`. On Lancashire —
a transparency/adequacy-of-reasons case, not a scoring/arithmetic one — this
undercounted **both** systems: 2/8 full-pipeline runs and all 5/5 zero-shot runs
correctly recommended `"re-evaluation"` (the right remedy) while leaving
`manifest_error_found=False` — a defensible reading of that field name for a violation
that genuinely isn't a manifest error in the calculation sense, not a reasoning
failure. Verified by reading the actual reasoning text before concluding this, not by
assuming the metric was fine: both systems' Lancashire reasoning explicitly names the
inadequate-reasons transparency failure and reaches the correct remedy.

**Fixed by switching the comparison basis to `recommended_action`/`outcome` against a
`_REMEDY_ACTIONS = {"re-evaluation", "damages"}` set** — did a substantive remedy get
recommended, not specifically whether a box literally labelled "manifest error" got
ticked. `tests/test_compare_baselines.py` regression-tests this against the exact
Lancashire pattern that caught it.

## 6. Results

| Case | Real disposition | Heuristic | Full pipeline (V4) | Zero-shot |
|---|---|---|---|---|
| AbbVie | CA won (clean) | WRONG | 33% remedy rate (correct direction) | 0% remedy rate (correct direction) |
| Braceurself | CA lost (violation) | correct | 100% | 100% |
| Bromcom | CA lost (violation) | correct | 100% | 100% |
| Lancashire | CA lost (violation) | correct | 100% | 100% |
| Faraday | CA lost (violation) | correct | 100% | 100% |
| Woods | CA lost (violation) | correct | 100% | 100% |
| **Direction-correct** | | **5/6** | **6/6** | **6/6** |

**The honest headline: at n=6, the full multi-agent pipeline and the naive single-LLM
zero-shot baseline tie on directional accuracy — both get every case right.** The
heuristic gets 5/6, failing only on the one case (AbbVie) where the majority-class
guess is wrong by construction. This is not the result a "more engineering effort
should mean better performance" prior would predict, and it is reported here exactly
as measured rather than reframed to favour the more complex system.

## 7. Does zero-shot fabricate more? Checked directly — no

Given accuracy is tied, the more likely place an unhardened prompt would actually
differ from `court_prompt.py`'s discipline is in *how* it reaches an answer, not
*whether* the answer is right — a fabricated number supporting a correct conclusion is
still a fabrication. `scripts/check_zeroshot_fabrication.py` applies the exact same
screen already used on the Court agent (`analyze_qualitative_fabrication.py`'s
`_extract_score_numbers`/`_number_grounded`) to all 30 zero-shot reasoning texts,
checked against each case's real scenario description.

**Result: 0 ungrounded numbers found across all 30 runs.** No detected fabrication-rate
difference between the hardened Court prompt and the unhardened zero-shot prompt, on
this specific check, on these 6 cases. This is a genuine negative result, not a null
finding papered over — it does not support a "the hardening prevents fabrication"
narrative on this evidence alone. Plausible explanations not yet distinguished: these 6
cases may simply not be the ones where fabrication risk is highest (the Court's own
fabrication instances documented in `evaluation-bailii-expansion.md` and `CLAUDE.md`'s
qualitative-fabrication section were found on Bromcom and Alstom, not evenly across the
corpus); or single-call zero-shot prompting on `llama3.1` may not be as fabrication-
prone as assumed. Worth re-checking specifically on Bromcom/Alstom-shaped cases before
drawing a firm conclusion either way.

## 8. What this does and does not support

**Does not support:** "the multi-agent architecture is more accurate than a simple
baseline." At n=6, it is not — zero-shot ties it, and the gap to the heuristic (which
has zero reasoning at all) is one case wide. Do not cite this project's real-case
accuracy figures as evidence of the multi-agent design's superiority without this
caveat attached.

**Does support**, based on what the ablations actually isolate:

- **The Court agent (or an equivalent adjudication step) is structurally necessary for
  this system to ever resolve anything.** The no-Court ablation's 0/18 deadlock rate is
  not a soft trend, it is the entire result — this is the strongest, cleanest finding
  in this comparison and it is about architecture, not accuracy.
- **The multi-agent design's value proposition is the negotiation *process*, not the
  final verdict.** A single zero-shot call produces one JSON object; the full pipeline
  produces a modelled negotiation — opening positions grounded in stated interests and
  BATNA, rounds of concession and counter-proposal, a Court reviewing the *actual*
  exchange rather than the raw case facts, and win statements reflecting each party's
  outcome against its own declared BATNA. None of that is measurable as "accuracy," and
  none of it exists in the zero-shot baseline at all — but it is the thing that makes
  this project a negotiation *simulation* rather than a classifier with extra steps,
  and it is the actual point of comparison against Fisher & Ury's framework (Doc 3)
  that the dissertation's theoretical grounding argues for.
- **The downstream capabilities built on this project** — the settlement recommendation
  synthesizer's Monte Carlo framing over repeated runs, the live interactive negotiation
  a real user watches unfold, the risk screen's separate practical framing — all
  structurally require the multi-round, multi-agent shape. A single verdict call cannot
  support any of them.

## 9. Limitations

- n=6 for the direction comparison, n=18 for the no-Court ablation's deadlock finding.
  The deadlock finding is robust (100% across every case, by architectural necessity,
  not sampling luck). The direction-accuracy tie is not — a different 6 cases, or more
  runs per case, could plausibly move it either way. Report the pattern, not a
  percentage, exactly as the rest of this project's small-N findings are framed.
- Single model (`llama3.1`), single temperature per agent type, matching every other
  evaluation in this project — this comparison cannot separate "architecture" from
  "this specific model's behaviour under each prompt style."
- The zero-shot fabrication check (§7) used the same detector already built for the
  Court agent, which has its own known limitations (documented in
  `scripts/analyze_qualitative_fabrication.py` and `CLAUDE.md`) — string-presence
  matching against the scenario description, not a general-purpose fact-checker.
