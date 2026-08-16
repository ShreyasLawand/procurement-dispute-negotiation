# BAILII Expansion: Extending the Real-Case Corpus from 5 to 8 Cases

*Evaluation punch-list item 14, originally framed as "scale the Court agent's real-case accuracy
evaluation from 5 to 20-30 real BAILII/TCC procurement judgments." This section reports what was
actually built, and is explicit about where the delivered scope differs from that original framing.*

## Scope: 3 verified cases added, not 20-30

The original framing of this item was calibrated against a very different cost assumption. On the
project's primary hardware, a single 3-round run of the existing pipeline (extraction plus one
full negotiation) takes on the order of **17 minutes** on local, CPU-bound Ollama inference — the
AbbVie n=3 batch below took 2101 seconds (~35 minutes) for 3 runs. At that rate, replicating the
existing methodology (n=8 runs, both V3 and V4 prompts) across 20-30 new cases would mean roughly
**320-480 additional runs**, i.e. multiple days of unattended compute even before accounting for
the research and verification time behind each case. That is not a reasonable scope for one
evaluation pass, and padding the corpus with cases that were not individually fact-checked would
directly contradict this project's own central discipline (never assert a fact the underlying
source does not support).

Mid-session, access to a GPU-backed remote Ollama instance (a University of Manchester "Ronin"
instance, NVIDIA A10G) cut per-call latency roughly 30-fold once the model was warm (~1-1.5s per
call vs. tens of seconds locally), taking a 3-run batch from ~35 minutes to well under a minute of
LLM time. This is a genuine capability change, not just a speed anecdote: it means the "20-30 case"
scope is now realistic in principle for a future session, whereas it was not against the original
hardware. What is reported here is a first, honestly-scoped tranche run against that new capacity:
**3 additional cases, individually verified the same way as the existing 5** (citation, facts, and
disposition checked against primary/secondary sources before being written into the corpus), taking
the real-case corpus from 5 to 8. Scaling further to the originally-envisioned 20-30 is now a matter
of research and verification time, not compute time — a materially different, and much smaller,
remaining obstacle than it was when this item was last scoped.

## Case selection: correcting for a bias in the original 5

Two case-selection criteria were applied, both learned from the existing 5-case corpus:

1. **Genuine merits-trial dispositions only**, not interim suspension-lifting rulings. Two of the
   original 5 cases (Alstom, Parkingeye) are interim rulings only, which `evaluation-five-cases.md`
   already documents as a real limitation — this system's Step 2A/2B design evaluates the *merits*
   of a compliance question, which an interim ruling (turning on balance-of-convenience, not the
   underlying manifest-error allegation) does not actually resolve. Several strong candidates
   surfaced during research were rejected on this basis alone: *Bristol Missing Link v Bristol City
   Council* [2015] EWHC 876 (TCC) and *Camelot UK Lotteries v Gambling Commission* [2022] EWHC 1664
   (TCC) are both suspension-lifting decisions only, with the underlying substantive dispute never
   reaching a documented trial outcome in either case. Both were excluded rather than added despite
   otherwise being well-documented, citable TCC judgments.
2. **At least one case where the contracting authority won outright.** All 5 existing cases involve
   the CA losing (a manifest error or unlawful process found) or a mixed/interim result. A Court
   agent that is only ever tested against cases where a violation exists cannot have its accuracy
   meaningfully assessed — a model that always predicts "violation found" would score perfectly
   against that corpus. *AbbVie Ltd v NHS England* [2019] EWHC 61 (TCC), where NHS England's award
   was upheld and AbbVie's claim was dismissed on the merits, was selected specifically to close
   this gap. *Dukes Bailiffs Ltd v Breckland Council* [2023] EWHC 1569 (TCC) was also considered as
   a CA-win candidate but rejected: it turns on a jurisdictional threshold question (whether the
   Public Contracts Regulations or the Concession Contracts Regulations applied at all) rather than
   on a scoring or process dispute, so it does not exercise this system's Step 1/2A/2B design in any
   meaningful way.

The three cases added:

| Case | Citation | Real disposition |
|---|---|---|
| AbbVie v NHS England | [2019] EWHC 61 (TCC) | **CA won.** No manifest error found; claim dismissed. |
| Braceurself v NHS England | [2022] EWHC 1532 (TCC); damages question settled on appeal in [2024] EWCA Civ 39 | Manifest error **found**, but breach not "sufficiently serious" — no damages. Outcome stable at both instances. |
| Bromcom v United Learning Trust | [2022] EWHC 3262 (TCC) | CA lost on **three independent grounds** (unlawful score-averaging, one-sided cost adjustment, unlawful rebate); damages awarded. |

Each entry's `source_text` in `src/cases/real_cases.py` records how it was verified and why it was
selected, in the same style as the existing 5 (see the file's inline comments on each new case).

## Methodology: extraction + single-round negotiation, V4 prompt only, n=3

This tranche deliberately narrows scope on two further axes, both because the specific question
this item asks — "how accurate is the Court agent against real cases" — does not require the full
existing methodology to answer:

- **V4 (active) prompt only, no V3 re-run.** The V3/V4 ablation's question (does Doc 1's 6-category
  judiciary taxonomy change Court behaviour vs. the original 3-line prompt) was already answered on
  5 cases at n=8 in `evaluation-five-cases.md`, with a formal significance layer in
  `scripts/analyze_ablation_significance.py` finding no case reaches p<0.05. Re-running that same
  ablation on 3 more cases would mostly generate more null results at the same statistical
  resolution, not new information about the ablation itself. What these 3 cases *do* usefully add is
  more real-world ground truth to test the (single, active) Court prompt's accuracy against —
  which is what item 14 actually asks for.
- **n=3, not n=8.** A smaller sample per case, traded for spending the saved LLM calls on adding
  a third new case instead of deeper replication of two. Confidence intervals implied by n=3 are
  correspondingly wide; this is reported as a raw finding, not dressed up with a significance test
  it cannot support at this sample size.

One consequence of using the existing pipeline unchanged (`tests/run_batch_evaluation.py --runs 3
--rounds 3`) is worth being explicit about: the Court's `assess_round()` call is grounded in what
the CA and Bidder actually say *that round*, not directly in the case source text — this is a
deliberate design choice (Step 1's gating is about verifying claims actually made, not inventing an
assessment from background facts alone), confirmed by reading `src/agents/court_agent.py` before
building this evaluation. A lighter design that skipped straight from extraction to a single Court
call on the raw scenario, without any CA/Bidder exchange first, was considered and rejected for this
reason — it would have tested a fundamentally different (and weaker) thing than what the Court agent
actually does in production.

## A real bug caught before any of this data could be trusted

The first smoke-test run against the newly-written `braceurself-nhs-england` case crashed with
`UnicodeEncodeError: 'charmap' codec can't encode characters in position 2-71` before a single
result was recorded. Cause: the new case source texts (written in the same dense-narrative style as
the existing 5) use em-dashes and other typographic punctuation throughout, and Windows' default
non-interactive stdout encoding (cp1252) cannot represent them — every `print()` of a scenario title
or negotiation message containing one crashed the run *after* the LLM calls for that run had already
executed, silently discarding the result. This would have produced an artificially low apparent
success rate with no informative error, exactly the kind of failure this project's own discipline
exists to catch before trusting output. Fixed in `tests/run_batch_evaluation.py` by reconfiguring
`sys.stdout`/`sys.stderr` to UTF-8 at the top of the script (a no-op on platforms where stdout is
already UTF-8) — not by removing the punctuation from the case narratives, since the narratives are
factually dense and the bug was in the runner, not the data.

## Results

| Case | Runs | Resolution rate | Manifest error detected | Modal outcome | Avg. duration/run |
|---|---|---|---|---|---|
| AbbVie (CA won in reality) | 3/3 successful | 1.0 | **0.33** (1/3 — a false positive) | 2/3 "no remedy – decision stands" (correct direction); 1/3 "re-evaluation" (incorrect) | 700.5s (local CPU) |
| Braceurself (manifest error found, no damages) | 3/3 successful | 1.0 | **1.0** (3/3 — correct) | 3/3 "re-evaluation" | 31.2s (remote GPU) |
| Bromcom (CA lost, 3 grounds, damages awarded) | 3/3 successful | 1.0 | **1.0** (3/3 — correct) | 3/3 "re-evaluation" | 29.8s (remote GPU) |

Structural compliance (`clean_responses / structured_responses`) was 1.0 across all 9 runs — no
JSON-parse fallbacks, no field coercions, consistent with the compliance-instrumentation work
reported in `CLAUDE.md`.

### AbbVie: the corpus's only real "no violation" ground truth, and where the Court drifts from it

Across AbbVie's 3 runs, round 1 consistently tracked the real outcome correctly: all three opening
Court assessments found no manifest error and recommended either "no remedy – decision stands" or
"continue negotiation," each reasoning explicitly and correctly that the DPM mechanism was found
lawful in the real judgment and that AbbVie's own pricing choices, not a structural defect,
explained its result. Run 3 then **drifted away from that correct finding in round 2**: after the CA
agent's round-1 message included a conciliatory offer ("proposed revisions... clear explanation of
the DPM's purpose"), the Court's round-2 assessment reversed to `manifest_error_found: true`,
reasoning that "NHS England's original scoring methodology was not transparent." Read against the
real case, this is a false positive: the actual High Court judgment made no adverse transparency
finding — it dismissed AbbVie's claim outright.

This is a different failure mode from the Faraday/Alstom premise-fabrication findings already
documented in `evaluation-five-cases.md` and `scripts/analyze_qualitative_fabrication.py` — nothing
here is fabricated, no numbers are invented, and the reasoning is coherent. The mechanism instead
appears to be a structural consequence of how the Court is deliberately grounded: `assess_round()`
evaluates what the CA and Bidder actually argued *that round*, not the case's real disposition. When
a CA agent's negotiating language becomes conciliatory (a natural negotiation dynamic, and by design
not the same thing as an admission of fault), the Court can read that shift as evidence something
was wrong, even on a case where the real-world court found nothing wrong at all. This is worth
flagging as a specific, named risk for any future use of this system's Court output as a
signal — round-over-round drift on a compliant scenario is a distinct and previously unobserved
failure pattern from anything in the original 5-case ablation.

### Braceurself: correct manifest-error detection, and correct restraint when arithmetic isn't grounded

All 3 runs correctly identified the manifest error (the stair-climber/stair-lift misreading) and
recommended re-evaluation — directionally consistent with the real liability finding. Runs 2 and 3
are notable for what they *did not* do: both runs' Court reasoning explicitly noticed that the
scenario states the two percentage scores (80.25% vs. 82.5%) but does not provide the underlying
question-level scoring criteria needed to recompute the gap from first principles, and both
explicitly declined to fabricate that missing structure — falling back to "I will treat this as
Step 2B" rather than inventing sub-scores. This is the Step 1/2A hardening (`court_prompt.py`,
commit `329848e`) working as intended on a case it was not built or tested against.

One limitation worth naming honestly: this system's outcome vocabulary has no way to express the
real case's actual nuance — liability established, but damages specifically denied because the
breach was not "sufficiently serious." All 3 runs converge on "re-evaluation," which captures the
liability finding but has no mechanism to also capture the separate damages-threshold question the
real Court of Appeal spent its judgment on. This is a corpus-vocabulary gap, not a per-run error.

### Bromcom: correct process-failure detection, and a genuine Step 1 fabrication regression

All 3 runs correctly found `process_followed: false` and recommended re-evaluation, consistent with
the real outcome (CA lost on all three grounds). But **run 3's Court reasoning contains an
unambiguous fabrication**, quoted verbatim from `batch_results/batch_20260816_165719/run_03.json`:

> "This scenario is numeric (Step 2A)... Let's assume there were three bidders, and each had a score
> out of 100 for three different criteria: A, B, and C. For simplicity, let's say the scores are as
> follows: Bidder 1: A=80, B=70, C=90 / Bidder 2: A=85, B=75, C=95 / Bidder 3 (Bromcom): A=92, B=82,
> C=98. The Contracting Authority averaged the scores as follows: A: (80+85+92)/3 = 85.67..."

None of these numbers exist anywhere in the Bromcom source text or in either party's dialogue that
round — the real case (like Faraday) is a process/methodology dispute with no published per-bidder
scores. The Court invents a complete illustrative dataset, performs real arithmetic on the invented
numbers, and cites that arithmetic as part of its basis for finding a manifest error. This directly
contradicts the explicit instruction added in the Step 1/2A hardening pass documented in
`CLAUDE.md` — "explicit ban on inventing 'illustrative'/'hypothetical' input values" — and confirms,
independently of the Faraday and Alstom findings already in `evaluation-five-cases.md` and
`scripts/analyze_qualitative_fabrication.py`, that this failure mode is not fully closed. It is now
observed in **three different agents across three different cases** (CA/Bidder on Faraday, CA/Bidder
on Alstom, and now the Court itself on Bromcom) — the third sighting specifically inside the
component whose own system prompt explicitly forbids it. The correct recommendation
("re-evaluation") happened to match the real outcome in this instance, which is precisely why this
kind of error is dangerous: a fabricated justification reaching a coincidentally correct conclusion
looks, from the outside, like the system working.

## What this changes about the project's overall findings

`evaluation-five-cases.md` §8 already names premise fabrication by CA/Bidder agents as a recurring,
cross-case finding. This tranche extends that finding in a way the original 5-case corpus could not:
the fabrication is not confined to the CA/Bidder agents feeding a bad premise to an otherwise-honest
Court — the Court's own Step 1 gating, hardened specifically against this failure mode, can still
fabricate the numeric premise itself under the same case-shape conditions (a real process/methodology
dispute with no published scores, misclassified as numeric). Combined with the AbbVie drift finding
above, both of this tranche's headline results point the same direction: **the Court's per-round,
dialogue-grounded design — a deliberate and in most respects correct choice, since it stops the Court
from being told the answer by the case digest — is also the mechanism behind both new failure
modes**, because grounding in "what was argued this round" instead of "what the case file actually
contains" leaves room for a round's rhetoric (AbbVie) or a misclassified case shape (Bromcom) to pull
the assessment away from the ground truth. Any future work on Step 1 gating should treat this as the
active risk, rather than treating the existing hardening as having closed the question.

## What remains for a full 20-30 case expansion

With the GPU-backed remote inference path now working (`OLLAMA_HOST` pointed at a tunnelled remote
Ollama instance, no code changes required beyond the encoding fix above), the compute cost that made
the original 20-30 case scope impractical is substantially reduced. What remains is the same
research and verification discipline applied to these 3 and the original 5: each additional case
needs its citation, facts, and disposition individually confirmed before being written into
`src/cases/real_cases.py`, in line with this project's standing rule against writing an unverified
fact into the evaluation corpus. Candidate cases surfaced during this session's research but not
(yet) added, because they did not meet the merits-trial-disposition or CA-win-diversity criteria
above: *Bristol Missing Link v Bristol City Council* [2015] EWHC 876 (TCC) and *Camelot UK Lotteries
v Gambling Commission* [2022] EWHC 1664 (TCC) (both interim-suspension-only), and *Dukes Bailiffs v
Breckland Council* [2023] EWHC 1569 (TCC) (jurisdictional threshold question, not a scoring dispute).
