# Results for thesis — old vs new, by phase

Running log of every figure that changed during the post-survey fix/re-screen work on
`frontend-rebuild`, appended to after each phase rather than written once at the end, so a dropped
session still leaves whatever's done on disk. Nothing under `thesis/` or any `*.tex` file is touched by
this file or by the work it describes — this is a staging document for whoever does that pass next.

---

## Phase 1 — fabrication screen widened to cover numeric (Step 2A) rounds, not just qualitative (Step 2B)

**Commit:** (recorded here at commit time — see git log for the exact hash)
**Files changed:** `scripts/analyze_qualitative_fabrication.py`, `tests/test_qualitative_fabrication.py`

### The claim, old vs new

| | Old (pre-4 Sep 2026) | New (post-widening, corrected 5 Sep 2026) |
|---|---|---|
| Screened population | 425 (qualitative only; numeric rounds skipped entirely) | 460 (425 qualitative + 35 numeric) |
| Flagged suspects | 9 | 19 (9 qualitative, unchanged — 10 numeric, new) |
| **Confirmed genuine Court-originated fabrication** | **0** (all 9 qualitative flags read as the pre-existing upstream CA/Bidder-dialogue pattern, not Court invention) | **9**, spanning 4 cases: 1 Bromcom, 1 Parkingeye, 2 Alstom, 5 Woods |
| Qualitative fabrication rate | 0.0212 (9/425) | 0.0212 (9/425) — byte-for-byte unchanged; the widening only added a new, separate numeric check |
| Numeric fabrication rate | not screened (population gate skipped it) | 0.2857 (10/35) |
| Combined screened fabrication rate | n/a | 0.0413 (19/460) |

### The 9 confirmed Court-originated instances, by exact path

1. Bromcom `batch_results/batch_20260816_165719/run_03.json` round 1
2. Parkingeye `batch_results/batch_20260815_221124/run_06.json` round 1
3. Alstom `batch_results/batch_20260819_205553/run_06.json` round 2
4. Alstom `batch_results/batch_20260819_205553/run_06.json` round 3 (known partial-catch gap — see script docstring)
5. Woods `batch_results/batch_20260819_211359/run_06.json` round 1
6. Woods `batch_results/batch_20260819_211359/run_07.json` round 1
7. Woods `batch_results/batch_20260819_213346/run_05.json` round 1
8. Woods `batch_results/batch_20260819_213346/run_07.json` round 1
9. Woods `batch_results/batch_20260819_213346/run_11.json` round 1

**5 of the 9 are Woods, all under the active V4 Court prompt, all from batches dated 19 August** — after
the 15 August Step 1 gating fix (commit `329848e`) this project's own history describes as having closed
this failure mode. One instance (`batch_20260819_213346/run_07.json` round 1) contains the near-verbatim
banned phrase: *"let's assume the original scores were not provided... a hypothetical score of 60 for
EAS and 40 for Woods."* This qualifies, without contradicting, the narrower existing claim that the
original 16 post-fix runs it was measured against were clean — "the fix closed this failure mode" can no
longer be cited as an unqualified, permanent claim.

**In all 9 instances the fabrication is invented INPUT numbers with subsequently correct arithmetic, not
incorrect arithmetic.** Bromcom and Parkingeye invent a bare declarative dataset with no formula behind
it; the Alstom and Woods instances invent a numeric baseline and then correctly execute the real, stated
formula on it (e.g. Woods: `(0.6 * 85) + (0.4 * 92) = 87.8` — flawless arithmetic on numbers nobody
supplied). A reader checking only "is the maths right" would find nothing wrong in any of these 9 cases.

**Not counted as Court-originated** (read individually and confirmed to be the pre-existing upstream
pattern instead): 1 further numeric-branch suspect (Alstom, `batch_20260815_192629/run_01.json` round 2,
V3 — the Court does symbolic algebra on CA-claimed weights and explicitly declines to assert a concrete
fabricated number) and all 9 qualitative-branch suspects (each is the Court citing a number the CA/Bidder
stated in dialogue and declining to treat it as independently verified fact).

### Where this feeds the thesis

| Thesis location | What changes |
|---|---|
| §3.7 (fabrication-screen methodology/findings) | Headline claim moves from "0/9 flagged were genuine Court fabrication" to "9 confirmed Court-originated fabrication instances, spanning 4 of the corpus's real cases" |
| Table 3.3 | New rows/columns needed for the numeric-branch population (35 screened, 10 flagged, 9 confirmed) alongside the existing qualitative row |
| Figure 3.5's status label | The "closed"/"resolved" status this figure carries for the fabrication finding needs to change to reflect an open, recurring failure mode (Woods), not a closed one |
| Chapter 4, RQ3 answer | RQ3 (does the anti-fabrication discipline hold at corpus scale) needs its answer qualified: holds for the narrowly-measured original 16 post-fix runs, does not hold unqualified across the full corpus |
| Table 4.1, row O3 | Update the observation this row records to name the 9-instance, 4-case scope, not the single Bromcom miss |

**Table 3.4 (the existing Woods V3/V4 ablation cells) is confirmed NOT contaminated by this finding.**
The ablation's Woods cell draws from `batch_20260815_200902` (V3) and `batch_20260815_201219` (V4) — both
independently re-screened and confirmed clean of any fabrication suspect. The 5 Woods instances above
come from two entirely different, later batches (`batch_20260819_211359`, `batch_20260819_213346`) that
the ablation table has never referenced.

### Five other analysis scripts re-run for a full fresh figure set (unaffected by this phase's code change; included per instruction to catch anything unexpected moving — nothing did)

All movement below is ordinary corpus growth (141→299 logs since the last-cited 16 Aug 2026 figures, via
the documented BAILII round-2 expansion), not an effect of the fabrication-screen widening — none of
these five scripts touch the fabrication-screen code path.

| Script | 16 Aug 2026 (141 logs) | 5 Sep 2026 (299 logs) |
|---|---|---|
| `check_zeroshot_fabrication.py` | 0/30 ungrounded | 0/30 ungrounded — unchanged |
| `analyze_citation_validity.py` | wrong-regime 27.9%; s12 error 35.7% (5/14) | wrong-regime 23.1%; s12 error 33.3% (7/21) |
| `analyze_batna_outcomes.py` | CA falls_short 2%; Bidder falls_short 18%, beats 23% | CA falls_short 2% (5/299); Bidder falls_short 21%, beats 24% |
| `analyze_negotiation_dynamics.py` | CA concession 0.014→0.456; Bidder 0.0→0.107; similarity 0.106/206 pairs | CA concession 0.013→0.470; Bidder 0.0→0.075; similarity 0.097/426 pairs |
| `analyze_summary_readability.py` | FRE mean 25.2, median 26.7; FKG mean 14.6, median 14.4 | FRE mean 24.7, median 25.9; FKG mean 14.7, median 14.4 |
| `compare_baselines.py` | Heuristic 5/6, full pipeline 6/6, zero-shot 6/6, n=6 | Unchanged — this script's inputs are untouched by Phase 1 |

**Test suite:** 103/103 passed (`pytest tests/`), including the 11 new fabrication-screen tests.

---

## Phase 3 — strip outcome leakage from the 6 leaked merits cases, re-run against clean scenarios

**Files changed:** 6 scenario cache files under `batch_results/_scenarios/`: `faraday-west-berkshire.json`,
`woods-milton-keynes.json`, `bromcom-united-learning-trust.json`, `optima-health-dwp.json`,
`abbvie-nhs-england.json`, `bechtel-hs2.json` — `description` field only, no code changes.

### What was wrong

`scripts/analyze_outcome_leakage.py` (built earlier, not new to this phase) found that 6 of the
corpus's 14 merits-trial scenario descriptions stated the real court's disposition outright (e.g. "the
Court of Appeal reversed... declaring its ineffectiveness"), and `court_prompt.py` separately instructs
the Court agent not to contradict a disposition the scenario states — so agreement figures computed over
those 6 were partly measuring instruction-following, not prediction.

### The rewrite principle

Remove any sentence stating or implying who prevailed or what a court concluded; keep every fact, number,
and formula the case's real record contains, so the Court agent still has a genuine Step 2A/2B task
rather than an emptied-out scenario. Two of the six needed real care, both caught and corrected before
writing anything (see `git log` for the exact turns this happened across):

- **Woods:** an early draft attributed the −40/+6 mark correction to "a disputed re-evaluation of the
  scoring records" — a process that does not exist anywhere in `src/cases/real_cases.py`'s source text.
  Checked directly against the source (lines 227-236): the correction is the trial judge's own
  conclusion, with no real intermediate re-evaluation process at all. Corrected to attribute the figures
  to Woods' own contested claim ("Woods' case is that... EAS's marks require a downward correction of 40
  marks... Woods' marks require an upward correction of 6 marks") rather than inventing a fictional
  process to route around the leak — the exact discipline this project's whole fabrication-screen strand
  exists to enforce, now applied to a scenario edit rather than a Court response.
- **Optima:** an early draft kept "without first seeking clarification" as a settled fact — that's the
  actual crux of the Court of Appeal's finding, so stating it as fact still leaked the answer even though
  no sentence matched the detector's regex. Reworded so the clarification question is Optima's allegation
  and DWP's dispute, not an established fact; kept "Optima's bid scored highest on quality" as a neutral
  record fact but cut "would have been the winning bid but for..." — the counterfactual conclusion
  itself.
- **AbbVie:** the pre-existing cached description had almost no negotiable content (2 thin sentences).
  Pulled the DPM's actual mechanics from `real_cases.py`'s source text — how the mechanism imputes a
  "credited" price for a category a bidder doesn't supply, set at the lowest other bidder's price for
  that category — so the CA/Bidder agents have a real mechanism to argue about, not just "AbbVie says
  it's unfair."

### Re-run: 8 runs / 5 rounds per case, active (V4) prompt, Ronin GPU tunnel

The tunnel dropped twice mid-session (both times: `WinError 10061`, connection actively refused,
independent of anything this session did). Neither drop was worked around — the affected batch was
re-run in full after the tunnel came back, and the contaminated partial batch was left on disk rather
than silently discarded:

| Case | Attempts | Usable result |
|---|---|---|
| faraday-west-berkshire | 1st: 2/8 (tunnel dropped mid-batch, `batch_20260905_130434` — **not cited**) · 2nd: 8/8 (`batch_20260905_131106`) | 8/8 successful |
| woods-milton-keynes | 8/8 (`batch_20260905_131917`) | 8/8 successful |
| bromcom-united-learning-trust | 8/8 (`batch_20260905_132616`) | 8/8 successful |
| optima-health-dwp | 8/8 (`batch_20260905_133047`) | 8/8 successful |
| abbvie-nhs-england | 8/8 (`batch_20260905_133532`) | 8/8 successful |
| bechtel-hs2 | 1st: 0/8 (tunnel dropped before any run started, `batch_20260905_134344` — **not cited**) · 2nd: 8/8 (`batch_20260905_134717`) | 8/8 successful |

### The headline result: agreement dropped, and 5 of 6 cases still predict correctly on their own merits

Old figure (leaked, `court_prompt.py` told not to contradict): **6/6 "correct," but this was partly
compliance, not prediction.** Combined-with-leak-free old figure: 13/14.

**New, honest figure, computed from ONLY the post-strip runs listed above (isolating today's batches
from every pre-existing leaked-era batch for these 6 cases, since `analyze_outcome_leakage.py`'s own
vote-counting naively pools every historical run for a scenario regardless of which version of the
description generated it — see "known measurement gap" below): 5/6 correct.**

| Case | Real | Leak-free-only vote (excl. deadlock) | Modal | Verdict |
|---|---|---|---|---|
| faraday-west-berkshire | lost | 5 lost / 2 won | lost | correct |
| woods-milton-keynes | lost | 5 lost / 2 won | lost | correct |
| bromcom-united-learning-trust | lost | 8 lost / 0 won | lost | correct |
| optima-health-dwp | lost | 8 lost / 0 won | lost | correct |
| **abbvie-nhs-england** | **won** | **5 lost / 3 won** | **lost** | **WRONG** |
| bechtel-hs2 | won | 2 lost / 3 won | won | correct |

**AbbVie is a genuine, unforced miss, not a fabrication or a bug.** Read against the source: the Court
engages the DPM's actual mechanics (does imputing a "credited" price structurally disadvantage a
bidder?) rather than inventing anything, and reaches the wrong answer on 5 of 8 runs once it isn't told
the answer. This qualifies — without contradicting — the corpus's existing "this system tracks real
dispositions reasonably well" claim (`evaluation-bailii-expansion-round2.md`): that claim was measured
substantially on leaked scenarios and needs restating against leak-free evidence specifically.

**Full 14-case corpus, honest leak-free figure: 12/14 (85.7%).** This combines the 5/6 above with the
7/8 that never needed editing (`lancashire-care`, `braceurself-nhs-england`, `energysolutions-nda`,
`consultant-connect-nhs-banes`, `inhealth-nhs-england`, `siemens-mobility-hs2`,
`tnlc-gambling-commission` correct; `turning-point-norfolk` wrong — a pre-existing, already-documented
genuine legal-judgment disagreement, not a new finding). `analyze_outcome_leakage.py --verbose` run
against the full 14-case corpus confirms **0/0 leaked** — every merits scenario is now leak-free.

**Known measurement gap, not fixed in this phase:** `analyze_outcome_leakage.py`'s vote-counting globs
every `run_*.json` ever logged for a scenario's `dispute_id` and pools them into one modal vote,
regardless of which version of the scenario description generated each run. For these 6 cases that
means its raw output (e.g. `abbvie-nhs-england (6/12) WRONG`) mixes 4 old leaked-era votes in with the 8
new leak-free ones. In this instance the pooled figure happens to agree with the isolated leak-free-only
figure on every case's correct/incorrect verdict (confirmed by hand above), so the 12/14 headline number
is not affected here — but the script itself does not distinguish eras, and a future re-run of any of
these 6 cases will keep pooling old and new votes together unless it's changed to filter by scenario
version or run timestamp. Flagged rather than fixed, given time constraints.

### Where this feeds the thesis

Same locations as Phase 1 (§3.7 methodology chapter; new material for the RQ3 answer and the
disposition-tracking claim currently cited from `evaluation-bailii-expansion-round2.md` and
`evaluation-baselines.md`), plus **Table 4.1** should gain a row distinguishing the leaked (6/6,
compliance) figure from the leak-free (12/14, genuine prediction) figure rather than quoting only the
higher one.

**Test suite:** 103/103 passed (`pytest tests/`) before this phase's commit — no code changed, scenario
cache edits only, run as a sanity check regardless.

---

## Phase 4 — rebuild the baselines comparison on the leak-free set

**Files changed:** `scripts/compare_baselines.py` (repointed `FULL_PIPELINE_BATCHES`, fixed a
deadlock-handling bug — see below), `tests/test_compare_baselines.py` (2 new regression tests). New
data: 4 zero-shot re-runs under `baseline_results/zeroshot/`.

### Scope: exactly the original 6-case comparison, not expanded

`compare_baselines.py`'s `REAL_DISPOSITIONS` was left as the original 6 cases (abbvie, braceurself,
bromcom, lancashire, faraday, woods) — per instruction, rebuilt on leak-free data, not widened to the
other 8 leak-free cases in the corpus. Of these 6, 4 (`abbvie`, `bromcom`, `faraday`, `woods`) were
leaked and needed refreshing; `lancashire-care` and `braceurself-nhs-england` were never leaked and are
untouched.

### A second contamination source, caught before trusting the rebuild: zero-shot

The full-pipeline batches were the obvious thing to refresh, but `run_baseline_zeroshot.py` loads from
the exact same `batch_results/_scenarios/<slug>.json` cache Phase 3 edited — and `zeroshot_prompt.py`
has **no** "don't contradict a stated outcome" guard at all, unlike `court_prompt.py`. That means the old
zero-shot baseline was, if anything, more directly exposed to the leak than the Court agent: it would
have read the disposition sentence as a plain fact and could parrot it straight back. Checked directly
(not assumed): all 6 existing zero-shot batches under `baseline_results/zeroshot/` were dated 16 Aug
2026 — before Phase 3 existed, so all 4 for the leaked cases are contaminated the same way the old
full-pipeline batches were. Re-ran zero-shot for `abbvie`, `bromcom`, `faraday`, `woods` at n=5 (matching
the existing convention); `lancashire-care` and `braceurself-nhs-england`'s existing n=5 zero-shot runs
were never leaked and are reused as-is, per the "reuse where n is already adequate" instruction.

### A third issue, exposed rather than caused by the leak-free re-runs: deadlock miscounted as "no violation"

`_full_pipeline_violation_rate()` computed `remedy runs / all successful runs`. Every batch this table
had ever cited before Phase 4 had **zero deadlocks** — 100% resolution, consistent with the
`court_prompt.py` GROUNDING instruction making resolution easier when the Court is told not to
contradict a stated outcome. Once genuinely leak-free negotiations (which do deadlock sometimes) were
substituted in, this silently pulled the rate toward "no violation" every time a case failed to resolve
— `faraday-west-berkshire`'s first (uncorrected) read was 38% ("WRONG") purely because 3 of 8 runs
deadlocked, not because the runs that did resolve disagreed with the real disposition (they were 3
remedy / 2 no-remedy among the 5 that resolved — 60% once deadlocks are excluded from the denominator
entirely, matching `analyze_outcome_leakage.py`'s own convention). Fixed in
`_full_pipeline_violation_rate()` (deadlock excluded from both numerator and denominator, returns `None`
if every run deadlocked) and locked in with 2 new regression tests. `_zeroshot_violation_rate()` needed
no equivalent fix — a single zero-shot call has no rounds and cannot itself deadlock.

### The new table — old vs new

| Case | Real | Old (leaked) heuristic/full/zero-shot | New (leak-free) heuristic/full/zero-shot |
|---|---|---|---|
| abbvie-nhs-england | clean | WRONG / correct / correct | WRONG / **WRONG (62%)** / **WRONG (100%)** |
| braceurself-nhs-england | VIOL | correct / correct / correct | correct / correct / correct (unchanged, never leaked) |
| bromcom-united-learning-trust | VIOL | correct / correct / correct | correct / correct / correct |
| lancashire-care | VIOL | correct / correct / correct | correct / correct / correct (unchanged, never leaked) |
| faraday-west-berkshire | VIOL | correct / correct / correct | correct / correct (60%, post-fix) / correct |
| woods-milton-keynes | VIOL | correct / correct / correct | correct / correct (71%, post-fix) / correct |

**Old headline (CLAUDE.md, `evaluation-baselines.md`): "at n=6, the full pipeline and the naive zero-shot
baseline tie exactly (6/6 direction-correct each); the zero-reasoning heuristic gets 5/6."**

**New headline: all three methods now tie at 5/6** — heuristic 5/6, full pipeline 5/6 (down from 6/6),
zero-shot 5/6 (down from 6/6). **All three miss the identical case, AbbVie, and only AbbVie.** This is a
genuine, structural change to the "does the multi-agent architecture earn its complexity" answer: the
old story was "the multi-agent pipeline ties a naive single LLM call, both clearly beat a zero-reasoning
majority-class guess." The honest, leak-free story is that on this 6-case set, the multi-agent pipeline
no longer demonstrably beats even the zero-reasoning heuristic on raw direction-accuracy — all three
converge on the same single miss. This does not undermine the existing, separately-grounded "why
multi-agent" argument in `evaluation-baselines.md` §8 (the no-Court ablation's 0/18 resolution rate is
untouched by any of this — that finding has nothing to do with outcome leakage), but the accuracy-tie
claim specifically needs restating.

**n=6 still has essentially no statistical power — read the pattern (all three converge on AbbVie
specifically), not the percentage.**

### Where this feeds the thesis

`evaluation-baselines.md`'s headline claim and its §8 argument structure; the RQ3/RQ-does-complexity-earn-
its-keep answer in Chapter 4; any table quoting the old "6/6 tie" figure needs the new "5/6, all three
converge on AbbVie" figure instead.

**Test suite:** 105/105 passed (`pytest tests/`), including 2 new regression tests for the deadlock fix.

---

## Phase 5 — Alstom V3/V4 ablation, n=8 → n=30

**Files changed:** `scripts/analyze_ablation_significance.py` (`CASES["alstom-london-underground"]`
repointed to the new n=30 batches; fixed a header/field bug that assumed n=8 was uniform across every
case, which stopped being true the moment Alstom became asymmetric — now reports `n_v3`/`n_v4`
separately per case rather than a single shared `n`). New data: `batch_results/batch_20260905_143138`
(V3, n=30) and `batch_results/batch_20260905_150536` (V4, n=30).

### Power check, done before spending the GPU time

At n=8, Alstom's V3-vs-V4 resolution gap (50% vs 100%) was the closest to significance of all 5 ablation
cases but still short: p=0.0769. Extrapolating the same observed rates to n=30/arm using the project's
own `fisher_exact_two_tailed()` gave p≈5.8×10⁻⁶ — deep into significant territory, with two conservative
sensitivity checks (V4 imperfect at 93%, V3 higher at 60%) both still landing under p=0.0004. The
crossing point was n=9/arm holding the same rates. Verdict: run it.

### What n=30 actually showed — both rates moved, and the direction held

| | n=8 (original) | n=30 (new) |
|---|---|---|
| V3 resolution rate | 50% (4/8) | **31.0%** (9/29 successful; 1 run failed on an unrelated Pydantic validation error) |
| V4 resolution rate | 100% (8/8) | **85.7%** (24/28 successful; 2 runs failed the same unrelated validation error) |
| Fisher's exact p (resolution) | 0.0769 | **p ≈ 3.96×10⁻⁵** |

**Both n=8 rates were optimistic in different directions — the true gap is smaller than 50-vs-100 looked,
but it is real and clears significance easily.** V3's deadlock rate at n=30 is 69% (20/29), far higher
than the n=8 sample suggested; V4 also isn't literally 100% at this size (4/28 deadlock, 14.3%). The
qualitative finding "V4 resolves more often than V3 on Alstom" holds, and is now statistically
distinguishable from noise — n=8 simply wasn't large enough to say that with confidence, exactly the
gap this phase existed to close.

### Fabrication screen on the new batches, run before trusting the p-value, per instruction

Every compliance-check round across both new batches (212 qualitative + 9 numeric + 6 ambiguous/neither =
227 rounds) was screened using the widened Phase 1 check. **17 raw suspects (9 qualitative, 8 numeric);
every one individually read against the same Court-originated-vs-upstream discipline as Phase 1, not
just counted.**

**Result: fabrication recurs. 2 confirmed Court-originated instances, both in the new V4 batch, both
V4 specifically (not V3):**
- `batch_20260905_150536/run_13.json` round 3 — *"Let's assume the raw data for each requirement is as
  follows: Design and Manufacturing Capability: 80/100 × 0.4 = 32..."* — invented three-item sub-score
  dataset, correct weighted arithmetic on it.
- `batch_20260905_150536/run_22.json` round 3 — *"Let's assume the mandatory technical threshold
  requirement is 80 points out of 100"* — invents a concrete point-valued threshold; Alstom's real
  record has no such points-based threshold at all, only a binary pass/fail.

The remaining 15 suspects (all 9 qualitative + 6 of the 8 numeric) are the pre-existing, already-documented
upstream pattern: the Court explicitly attributes the disputed number to a CA/Bidder claim ("according to
the Contracting Authority's records," "as mentioned in the scenario," "provided by London Underground")
and either declines to verify it further or performs a tautological/legitimate calculation on an
attributed input — not inventing new substantive data itself.

**This is not the same 2 Alstom instances Phase 1 already found** (those were in `batch_20260819_205553`,
a different, earlier batch, unaffected by this phase). Corpus-wide Court-originated fabrication count
therefore moves from 9 (Phase 1) to **11**, pending the full corpus refresh below (which will re-derive
this number from scratch rather than by addition, since it's now cheap to just re-run the whole screen).
Notably, both new instances recur under **V4** — extending, not just repeating, the Woods finding from
Phase 1 that the 15 Aug Step 1 gating fix does not reliably close this failure mode under the currently
active prompt.

### Where this feeds the thesis

Chapter 3's fabrication-count table (now 11, not 9, pending the full refresh); the Alstom row of the
V3/V4 ablation table (statistically significant now, not just directionally suggestive); the
"anti-fabrication discipline holds" claim needs the same qualification Phase 1 already required, now
with a third case (Alstom, alongside Woods) showing it recurring specifically under V4.

**Test suite:** 105/105 passed (`pytest tests/`) — no test code changed this phase, ran as a sanity
check after editing `analyze_ablation_significance.py`.

---

## Post-Phase-5 fix — `analyze_outcome_leakage.py`'s vote-pooling gap, closed

Flagged, not fixed, in Phase 3: the script's vote-counting globbed every `run_*.json` ever logged for a
scenario's `dispute_id` and pooled them into one modal vote regardless of which version of the scenario
description generated each run — for the 6 cases Phase 3 stripped leakage from, that silently mixed old
leaked-era votes with new leak-free ones.

**Fix:** every run log already stores `scenario.description` verbatim (it has to — it's inserted into
every agent's prompt). New `collect_votes()` compares each run's own embedded description against the
*current* cached scenario file, byte-for-byte, and only counts the vote if they match exactly. No new
field, no reliance on file timestamps (which are approximate — copies and git operations disturb mtime;
description text embedded in the log itself cannot lie about what was actually run). Runs generated
against a superseded description are now excluded and counted (**113 historical runs excluded
corpus-wide**), not silently pooled in.

**Regression test** (`tests/test_outcome_leakage.py`, 3 tests) uses the real committed corpus, not a
synthetic fixture, per instruction: confirms exactly 8 leak-free abbvie votes (5 lost/3 won) and 7
leak-free faraday votes (5 lost/2 won) survive the filter, confirms lancashire-care's 31 historical votes
are untouched (never leaked, never rewritten), and confirms the fixed script reproduces Phase 3's
hand-verified **12/14** leak-free agreement figure end-to-end, with no manual per-case isolation needed.

Re-running `analyze_outcome_leakage.py` (no `--verbose`) now: **12/14, exact match to Phase 3's
hand-computed number**, and every individual case's vote count (faraday 5/7, woods 5/7, bromcom 8/8,
optima 8/8, abbvie 5/8, bechtel 3/5) matches the hand isolation exactly.

**Test suite:** 108/108 passed (`pytest tests/`), including the 3 new tests.

---

## Full corpus refresh (5 Sep 2026, final pass) — every `analyze_*.py` re-run against the complete corpus

New logs were added by Phases 3-5 (6 leak-free re-runs, 4 zero-shot re-runs, 2 Alstom n=30 batches).
Every script re-run once more; every figure below is fresh, not carried forward. Corpus size at this
point: **406 negotiation logs** (up from 299 at Phase 1's start).

### The one figure that needed real work before trusting it: fabrication count

The corpus refresh alone moved the fabrication screen's raw numbers a lot — screened population
460→**784**, raw suspects 19→**45** — almost entirely because the 227 rounds in the two new Alstom n=30
batches (already screened and reported in Phase 5) and the 6 Phase-3 leak-free re-run batches got folded
into the same corpus-wide scan. **9 of the 45 raw suspects had never been individually read before this
final pass** (they come from the Phase 3 leak-free re-runs of faraday/woods/bechtel, which were re-run
for outcome-leakage reasons and never separately fabrication-screened). Read all 9 against the same
Court-originated-vs-upstream discipline as every other phase:

- **1 confirmed new Court-originated fabrication:** `batch_results/batch_20260905_131917/run_07.json`
  round 2 (Woods, leak-free re-run) — *"Assuming the original scores for Q4.3 were EAS = 8/10 and
  Woods = 9/10"* — invents a specific sub-criterion ("Q4.3") and concrete scores for it that appear
  nowhere in the real record (which only ever states the aggregate ±40/±6 mark correction, never a
  per-criterion breakdown). A 6th Woods instance, distinct from the 5 already found in Phase 1.
- **1 screening-tool false positive, not fabrication** — worth documenting so it isn't miscounted either
  way: the same run's round 1 flagged `'0.4'`/`'0.6'` as ungrounded. These are the real, stated 60%/40%
  price/quality weights, just written by the Court as decimals rather than percentages — the scenario
  text contains "60%" and "40%" as literal strings, so `_number_grounded()`'s exact-substring check
  doesn't recognise "0.6" as the same fact. Not a fix made in this pass (out of scope, flagged like
  Phase 3's other known gaps) — but material to the exact count, so recorded rather than silently
  dropped from either side of the ledger.
- **7 upstream**, all following the pattern already established across every prior phase: numbers
  explicitly attributed to a CA/Bidder dialogue claim, or symbolic algebra where the Court explicitly
  states it lacks concrete inputs and declines to invent them.

**Corpus-wide confirmed Court-originated fabrication count, final: 12** (up from Phase 1's 9): 1 Bromcom,
1 Parkingeye, 4 Alstom (2 original + 2 from the n=30 ablation bump), **6 Woods** (5 original + 1 from
this pass). Denominator 784 screened, 45 raw suspects, 12 confirmed / 32 upstream / 1 screening
false-positive.

### A separate, more serious finding, caught while reading that same round — not caught by any existing screening tool

`batch_results/batch_20260905_131917/run_07.json` round 2's reasoning contains this sentence: *"the
scenario description itself states what a court or tribunal actually decided in this dispute (the court
found no error and dismissed the challenge)."* **Checked directly: that statement does not appear
anywhere in the actual scenario description the Court was given, nor anywhere in `real_cases.py`'s
source text** (`grep` returns zero matches in both files). This is not a number-fabrication the existing
screen could ever catch (it only checks score-shaped numbers against the scenario text) — it is the
Court **fabricating what its own input contained**, then citing that fabrication as grounds for not
contradicting a "stated" outcome. It is also **factually backwards**: the real Woods disposition is that
Woods *won* and the court found manifest error, not that the challenge was dismissed. Whether this
reflects the underlying model's own pretraining "knowledge" of this real, published EWHC judgment
leaking through independent of what the scenario actually says is a real possibility worth naming, not
confirmed here (this is one instance, found by reading, not by a systematic screen — see the
verify-before-submitting checklist below). If so, it is a distinct vulnerability from anything Phase 3's
outcome-leakage strip addressed: that fix controls what the *scenario text* says; it cannot control what
the model already "knows" about a real case from training.

### The other six scripts

| Script | Prior figure (RESULTS-FOR-THESIS.md, Phase 1) | Final (406 logs) | Moved? |
|---|---|---|---|
| `check_zeroshot_fabrication.py` | 0/30 ungrounded | **0/50 ungrounded** | No — n grew (4 new zero-shot batches), rate unchanged |
| `analyze_citation_validity.py` | 702 citations @ 299 logs; wrong-regime 23.1%; s12 error 33.3% (7/21) | **1070 citations @ 406 logs; wrong-regime 15.7% (168); s12 error 30.3% (10/33)** | Yes, both rates — consistent with corpus growth, not a new pattern |
| `analyze_batna_outcomes.py` | CA beats 71%, falls_short 2% (5/299); Bidder beats 24%, falls_short 21% | **CA beats 65%, falls_short 2% (7/406); Bidder beats 22%, falls_short 23%** | Modest movement, same qualitative asymmetry |
| `analyze_negotiation_dynamics.py` | CA concession 0.013→0.470; Bidder 0.0→0.075; similarity 0.097/426 pairs; 0 retractions | **CA concession 0.0123→0.465; Bidder 0.0→0.0701; similarity 0.1188/942 pairs; 0 retractions** | Modest movement, same pattern |
| `analyze_summary_readability.py` | FRE mean 24.7/median 25.9; FKG mean 14.7/median 14.4 | **FRE mean 23.2/median 23.9 (worst case now -22.4); FKG mean 14.9/median 14.6** | Modest movement, same "very difficult, graduate" band |
| `compare_baselines.py` | 5/6, 5/6, 5/6 (Phase 4) | **5/6, 5/6, 5/6 — identical** | No — hardcoded 6-case set, no new inputs since Phase 4 |
| `analyze_ablation_significance.py` | Alstom p=3.96e-5 (Phase 5) | **Identical — no new inputs since Phase 5** | No |

None of this movement is unexpected — every script here (other than the fabrication screen) is
independent of the corpus's fabrication/leakage content and moves only because the denominator (logs
scanned) grew from 299 to 406 across Phases 3-5. Flagged per instruction regardless, since "moved,
even slightly" was the bar, not "moved unexpectedly."

**Test suite, final: 108/108 passed** (`pytest tests/`).

---

## Verify before submitting

Specific, honest items — not a reassurance list. A human should personally check each of these before
any number in this document goes into the thesis:

1. **The Woods "fabricated scenario-attribution" finding is a single instance, found by reading one
   transcript, not a systematic corpus-wide screen.** No existing script checks for a Court claim about
   what its own input contains being false. Before citing this as evidence of parametric-knowledge
   leakage (the model "knowing" a real case's outcome independent of the prompt), someone should
   deliberately search the corpus for the pattern *"the scenario states/describes what happened..."* or
   similar self-referential claims across all 406 logs — this session did not do that, and the true
   prevalence of this failure mode is unknown, not "rare" or "common."
2. **The AbbVie flip (correct → wrong, across all three baselines) rests on one n=8 batch per method.**
   The Alstom ablation in this same session showed both n=8 rates (50%/100%) were meaningfully off from
   the n=30 truth (31%/86%) once the sample grew. There is no equivalent n=30 check for AbbVie — treat
   "AbbVie predicts wrong" as suggestive at current sample size, not as settled, unless it's worth the
   GPU time to verify the same way Alstom was.
3. **The Alstom V4 p-value (3.96×10⁻⁵) is computed from data that includes 2 confirmed fabricated
   reasoning instances, both in the V4 arm.** This session did not re-compute the resolution-rate
   statistics with those 2 runs excluded or re-coded. It is not obvious the direction of the finding
   would change (fabrication ≠ wrong outcome, and 2/28 is a small fraction), but the exact p-value has
   not been checked for sensitivity to this, and should be before it's presented as clean.
4. **`_number_grounded()`'s exact-substring matching has at least one confirmed false-positive mode**
   (decimal-vs-percentage formatting, found this pass) that was documented but not fixed. The 45-suspect,
   12-confirmed count in this document is the product of human reading correcting for this on every
   individual suspect found so far — but the screening tool itself would still misflag the same pattern
   on any future run. Don't trust a future bare `--verbose` run's raw suspect count without the same
   manual check this session did.
5. **Every `batch_summary.json`'s `complete: True` flag was trusted throughout this session**, per the
   project's own established convention — except where a batch's low run-success count was independently
   noticed and excluded by hand (the two contaminated Phase 3 partial batches). `complete: True` is known,
   demonstrated fact within this session, to not imply "all runs succeeded" or "citable." No systematic
   sweep was done to confirm every OTHER cited batch across this document doesn't have a similar,
   unnoticed high-failure-rate problem — the ones that surfaced did so because a tunnel drop made them
   obviously wrong, not because anything was checking for this proactively.
6. **The 113 stale votes excluded by the outcome-leakage fix were verified against exactly 2 cases**
   (abbvie, faraday) plus one never-leaked control (lancashire-care). The other 3 previously-leaked cases
   (woods, bromcom, optima) were trusted to work correctly by the same logic, not independently
   hand-verified the way abbvie/faraday were in Phase 3's manual isolation. Spot-check at least one more
   before citing the fixed script's output as definitively correct.
