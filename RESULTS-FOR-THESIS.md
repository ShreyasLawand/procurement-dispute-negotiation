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
