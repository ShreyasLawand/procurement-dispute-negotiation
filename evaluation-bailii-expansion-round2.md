# BAILII Expansion, Round 2: Extending the Real-Case Corpus from 8 to 21 Cases

*Continuation of `evaluation-bailii-expansion.md` (which took the corpus from 5 to 8).
That write-up explicitly named the remaining obstacle to reaching the original 20-30
target as "research and verification time, not compute time" — this round tests that
claim directly, with the Ronin GPU tunnel now a routine part of the workflow rather
than a novelty.*

## 1. Scope: 13 new cases, corpus now 21

Verified via WebSearch (bailii.org / caselaw.nationalarchives.gov.uk plus law-firm case
notes) before writing, the same discipline applied to every case in this corpus.
**7 genuine merits-trial dispositions** and **6 well-documented interim-only rulings**
(roughly the same ~55:45 proportion as the original corpus's mix, not every candidate
forced into a merits shape it doesn't have):

| New case | Citation | Type | Real disposition |
|---|---|---|---|
| Bechtel v HS2 | [2021] EWHC 458 (TCC) | Merits | CA won (all claims dismissed, 3-week trial) |
| InHealth v NHS England | [2023] EWHC 352 (TCC) | Merits | CA won (bid exclusion upheld) |
| EnergySolutions v NDA | [2016] EWHC 1988 (TCC) | Merits | CA lost (narrow margin, £100m damages claim) |
| Turning Point v Norfolk CC | [2012] EWHC 2121 (TCC) | Merits | CA won (limitation + tender-caveat rejection) |
| Siemens Mobility v HS2 | [2023] EWHC 2768 (TCC) | Merits | CA won (17 claims dismissed) |
| TNLC v Gambling Commission | [2026] EWHC 891 (TCC) | Merits | CA won emphatically (30%+ score gap, £1.3bn claim dismissed) |
| Consultant Connect v NHS BaNES | [2022] EWHC 2037 (TCC) | Merits | CA lost (framework misuse, financial penalties) |
| KBR v MOPAC | [2021] EWHC 3321 (TCC) | Interim | Suspension lifted (CA-favouring) |
| Sysmex v Imperial College Healthcare | [2017] EWHC 1824 (TCC) | Interim | Suspension lifted (CA-favouring) |
| Vodafone v FCDO | [2021] EWHC 2793 (TCC) | Interim | Suspension refused (challenger-favouring) |
| Draeger v London Fire Commissioner | [2021] EWHC 2221 (TCC) | Interim | Suspension refused (challenger-favouring) |
| One Medicare v NHS Northants ICB | [2025] EWHC 63 (TCC) | Interim | Suspension lifted (CA-favouring) |
| Robert Heath Heating v Orbit Group | [2024] EWHC 3039 (TCC) | Interim | Suspension lifted (CA-favouring) |

Candidates researched and explicitly rejected during this round: Amey Highways v West
Sussex CC (a preliminary-issue ruling on abandonment defeating claims, not a clean
merits disposition on the scoring dispute itself); ATOS v BEIS (settled before trial,
no judgment to cite); Group M v Cabinet Office (turned out, on closer reading, to be
another interim suspension ruling despite initially looking like a merits case); Roche
Diagnostics v Mid Yorkshire Hospitals (a disclosure ruling only, no liability finding);
Bristol Missing Link (confirmed on closer reading to have settled via a re-evaluation
agreement before any substantive judgment — the suspension-stage precedent already
excluded in round 1 was, on this deeper check, not even a citable interim disposition).

## 2. This confirms the round-1 claim: research time, not compute time, is now the bottleneck

The 13 new cases required: 12 rounds of parallel WebSearch (~45 queries), individual
verification of each candidate's citation/facts/disposition, and rejection of 5
promising-looking candidates that didn't hold up on closer reading. The actual compute
— pre-extracting all 13 scenarios, then running n=3/rounds=3 batches for all 13 via the
Ronin GPU tunnel — took under an hour end to end, and needed zero manual intervention
beyond launching the batch chain. Getting from 21 to the full 30 is the same
research-bound process, not a different one.

## 3. Extraction: no fabrication, including on cases with no stated contract value

All 13 scenarios were pre-extracted before running any batch, specifically to catch an
extraction-stage problem before spending batch-evaluation cost on it (the exact failure
mode fixed on 16 Aug — see `CLAUDE.md`'s "BAILII expansion" section — was the extraction
agent echoing a concrete number from its own prompt's worked example when a source text
stated no value). Six of the thirteen new source texts deliberately state no explicit
contract value (Turning Point, Siemens Mobility, Consultant Connect, Sysmex, Draeger,
One Medicare, Robert Heath Heating), the same shape of test case that caught the
original bug. **All six correctly returned `0.0`, not an invented figure.** The fix
holds under a substantially larger and more varied test than the single case it was
originally caught and fixed on.

One minor imprecision, not a fabrication, worth noting: EnergySolutions and TNLC's
source texts each state a single prominent monetary figure (a £100m damages claim, a
£1.3bn damages claim) without a separate explicit contract value — the extraction agent
picked up the damages-claim figure as `contract_value_gbp` in both cases. Both numbers
are real and appear in the source text; the extraction instruction ("if genuinely only
one figure is given... use that figure") was followed defensibly, but a damages claim
and a contract value are not the same quantity. Not fixed, because it isn't wrong in the
sense the anti-fabrication discipline cares about (nothing was invented) — flagged here
as a genuine edge case in the extraction instruction's coverage, worth revisiting if
this specific pattern (a damages figure as the only number in a source text) recurs.

## 4. Batch results: 6/7 merits cases match real disposition direction

Run at n=3, rounds=3, active (V4) Court prompt, matching round 1's methodology exactly.

| Case | Real disposition | Simulated outcomes (3 runs) | Direction |
|---|---|---|---|
| Bechtel v HS2 | CA won | 3/3 "no remedy – decision stands" | Correct |
| InHealth v NHS England | CA won | 3/3 "no remedy – decision stands" | Correct |
| EnergySolutions v NDA | CA lost | 3/3 "re-evaluation" | Correct |
| Turning Point v Norfolk CC | CA won | 1/3 "no remedy", 2/3 "re-evaluation" | **Mostly wrong** |
| Siemens Mobility v HS2 | CA won | 3/3 "no remedy – decision stands" | Correct |
| TNLC v Gambling Commission | CA won | 3/3 "no remedy – decision stands" | Correct |
| Consultant Connect v NHS BaNES | CA lost | 3/3 "re-evaluation" | Correct (remedy shape differs — see §5) |

**6 of 7 direction-correct**, consistent with the round-1 tranche (3/3) and with the
baseline-comparison finding in `evaluation-baselines.md` that this system tracks real
dispositions reasonably well on cases with a genuine merits trial to compare against.

The interim-only cases are not scored against a merits disposition (same reasoning as
Alstom/Parkingeye) — reported for completeness: KBR 2/3 no-remedy + 1/3 deadlock, Sysmex
2/3 re-evaluation + 1/3 no-remedy, Vodafone 3/3 re-evaluation, Draeger 2/3 re-evaluation
+ 1/3 deadlock, One Medicare 2/3 re-evaluation + 1/3 no-remedy.

## 5. Turning Point: a genuine legal-reasoning disagreement, not a bug

Read directly rather than assumed from the outcome distribution. Run 2's round-1 Court
reasoning: *"The Council's position seems to imply that Turning Point was aware of the
policy beforehand, but this is not explicitly stated... Therefore, I conclude that
there may be a manifest error in the process."* This is, almost verbatim, **Turning
Point's own losing argument in the real case** — that the Council should have sought
clarification of the caveat before rejecting the tender outright. The real judge
rejected that argument specifically: the no-caveats rule was fair, reasonable, and
common, and the Council was under no obligation to seek clarification before enforcing
it. The simulated Court, reasoning from the same facts, reached the opposite conclusion
on that specific point of judgment.

This is not a fabrication (nothing invented, no ungrounded numbers, the reasoning
engages the real facts throughout) and not a bug in any component checked so far — it
is a genuine disagreement in legal reasoning between the simulated Court and the real
judge, on a case whose real disposition turned on a subtler question (should silence
excuse enforcement of a clearly stated rule?) than the scoring-margin disputes most of
this corpus otherwise turns on. Worth naming as a distinct failure mode from anything
in `evaluation-five-cases.md` or `evaluation-bailii-expansion.md`'s round-1 findings:
those documented fabrication (inventing facts) and drift (a round's rhetoric pulling the
assessment off ground truth); this is neither — it is the Court's own reasoning,
grounded in real facts, reaching a defensibly different legal conclusion than the real
court did. No fix is proposed for this: it is a limitation of what a model's legal
judgment can be expected to match exactly, not an engineering defect.

## 6. Consultant Connect: correct direction, wrong remedy vocabulary — a known corpus-vocabulary gap

All 3 runs correctly found the CA at fault and recommended `"re-evaluation"`. The real
remedy was not re-evaluation, however — it was direct financial penalties on the three
defendant NHS bodies (£10,000 / £8,000 / £4,000), reflecting that this dispute was about
process avoidance (misusing a framework agreement to dodge a genuine competition), not
about a scoring outcome that re-evaluation could actually correct. This is the same
`KNOWN_OUTCOMES` vocabulary limitation already documented for Faraday in
`evaluation-five-cases.md` §8 — this system's five-outcome vocabulary
(`re-evaluation`/`damages`/`no remedy`/`continue negotiation`/`deadlock`) has no way to
express "financial penalty on the contracting authority personally," so "re-evaluation"
is the closest available match to "the CA was found to be at fault." Direction-correct,
remedy-shape-approximate — consistent with, not a new instance separate from, the
existing documented gap.

## 7. What remains for the full 20-30 (or beyond)

21 cases now on disk. Reaching 30 needs roughly 9 more equally-verified cases — on this
round's evidence, that is realistically another 1-2 research sessions of the same shape
as this one, not a different order of difficulty. The corpus is not yet exhausted of
findable candidates; several promising leads (Peterborough City Council v Enterprise
Managed Services [2014] EWHC 3193, Mears Ltd v Shoreline Housing Partnership [2015]
EWHC 1396, and a handful of 2024-2026 Procurement Act 2023 cases mentioned only in
passing during this round's searches) were not run to ground and are candidates for the
next tranche rather than rejected outright.

## 8. Addendum, same session: 2 more cases, corpus now 23

Follow-up research after §7 turned up diminishing returns quickly — most new leads
either weren't procurement disputes at all (Peterborough City Council v Enterprise
Managed Services, checked and confirmed to be an unrelated FIDIC construction-contract
dispute over a solar plant's output; Mears Ltd v Shoreline Housing Partnership,
confirmed to be an NEC3 term-service-contract payment dispute, not a procurement
scoring challenge — both explicitly wrong leads from §7, now resolved rather than left
open) or repeated already-covered patterns (standing/preliminary-issue rulings like IGT
v Gambling Commission, more interim suspension rulings like Alstom v Network Rail and
Boxxe v SoS Justice). Rather than pad the corpus with weaker matches, added the two
genuinely new, well-verified finds and stopped:

- **Optima Health v DWP** — [2024] EWHC 766 (TCC), Freedman J: DWP won at first
  instance (lawful exclusion of a bid with minor pricing non-compliance). Reversed on
  appeal in [2025] EWCA Civ 127: the Court of Appeal held DWP should have sought
  clarification of an obviously minor, correctable error rather than excluding the bid
  outright, and should have awarded the contract to Optima. Real disposition: **DWP
  ultimately lost.** Run at n=3 (active/V4): 3/3 "re-evaluation" — **correct direction**,
  extending this round's merits-case tally to 7/8.
- **Neology UK v Newcastle City Council** — [2020] EWHC 2958 (TCC), an interim ruling
  of a different procedural shape than any other case in this corpus (a summary
  judgment application, not a suspension-lifting application), adding genuine
  procedural diversity rather than a repeat pattern. Run at n=3: 3/3 "re-evaluation" —
  not scored against a merits disposition, same reasoning as every other interim case
  here.

Corpus: **23 cases**, 14 genuine merits-trial dispositions and 9 well-documented
interim-only rulings drawn from this round's two tranches combined with the original 8.
