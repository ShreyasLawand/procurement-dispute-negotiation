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
