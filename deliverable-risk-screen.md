# The Pre-Award Challenge Risk Screen: The Project's Actual Deliverable to Fusion21

*Write-up of `src/risk/challenge_risk.py` as the primary product handed to Fusion21, distinct from
the negotiation simulator and its evaluation chapter (`evaluation-five-cases.md`,
`evaluation-bailii-expansion.md`, `evaluation-counterfactual-regret.md`), which are this project's
academic contribution rather than what a Fusion21 member would actually use day to day.*

## 1. Why this is the deliverable, not the negotiation simulator

Early in this project, the working assumption was that the deliverable was the negotiation
simulator itself — three LLM agents (Contracting Authority, Aggrieved Bidder, Court) replaying a
dispute and reaching a compliance finding. When that work was shown to Fusion21's industry contact
(Phil), his feedback reframed the project: the "heart" of what Fusion21 actually wants is **dispute
prevention**, not a better replay of a dispute that has already started. That single piece of
feedback is the reason this module exists and is the reason it is documented here as the
deliverable, not as one evaluation item among many.

The distinction matters structurally, not just rhetorically. Every other component in this system —
the negotiation simulator, the Court agent's compliance assessment, the settlement recommendation
synthesizer — operates on a dispute that has **already been raised**. This screen is the only
component that runs **before** a dispute exists, on the evaluation record and the draft debrief a
contracting authority is about to send. It is also the only component in the entire system with a
real, observable ground truth available in principle: whether a challenge was raised or not. The
Court agent's "correctness" can only ever be judged indirectly, against real litigated outcomes on a
handful of cases (see `evaluation-five-cases.md`) — this screen's core claim (*"these conditions
raise challenge likelihood"*) is, in principle, directly testable against Fusion21's own member data,
which is why closing that gap is named explicitly as the one thing this module needs from Fusion21
(§7).

## 2. What it is

`assess_challenge_risk(ca_profile, bidder_profile) -> ChallengeRiskAssessment` — a **rule-based
screen with no LLM call**. Sixteen rules, each tied to one field of `CAProfile` or `BidderProfile`
(`src/schemas/agent_state.py`), which are themselves a direct encoding of the "Practical
Considerations" tables in Fusion21's own Doc 1 (*Key Drivers & Interests for Parties in a
Procurement Dispute*) — seven CA-side factors, nine Bidder-side factors. Every rule's `rationale`
field is close-paraphrased from a specific Doc 1 sentence, not invented, and every triggered flag
carries a concrete, specific pre-award `mitigation` — the point of the tool is that these mitigations
are cheap if acted on before the standstill letter goes out, and expensive (litigation) if not.

Output shape:

```
ChallengeRiskAssessment
  overall_risk_band: "low" | "medium" | "high"
  risk_score: float (0.0-1.0, normalised severity-weighted sum)
  flags: [RiskFlag]   # one per triggered rule
  summary: str
```

Each `RiskFlag` names the exact profile field and value that triggered it, the Doc 1 category it
traces to, a severity (`low`/`medium`/`high`), a confidence tag (`known`/`estimated`, see §3), the
rationale, and the mitigation.

## 3. Three design boundaries, each deliberate and each load-bearing

**(a) It predicts "is a challenge likely to be raised," not "would the CA lose if challenged."**
These are different questions. The second requires judging the merits of the evaluation — that is
the Court agent's job, under the strict anti-fabrication discipline documented in `CLAUDE.md`'s
"Court Agent Design" section. Collapsing the two would smuggle a merits judgement in through inputs
(score margin, feedback quality) that actually speak to a *bidder's incentive to challenge*, not to
whether the CA's process was lawful. This module is deliberately silent on the merits — a narrow
score margin raises challenge risk regardless of whether the CA's scoring was actually correct.

**(b) Every flag is confidence-tagged, because not everything a CA might want to know is
observable pre-award.** `CAProfile` fields (documentation quality, panel capability, internal
accountability pressure, and — critically — the debrief the CA is about to send) are fully within
the authority's own knowledge and control before the standstill letter goes out, and are marked
`confidence="known"`. `BidderProfile` fields describing the *losing bidder's own* circumstances
(legal representation, revenue dependence, market conditions) are usually not confidently known to
the CA pre-award and are marked `confidence="estimated"`. A caller who only trusts what the CA can
actually verify can filter on this field directly.

**(c) `risk_score` is an ordering device for triage, not a calibrated probability.** Doc 1 gives
directional relationships ("the closer the scores, the *greater* the likelihood") — it does not give
weights, thresholds, or a combination formula. The severity weights here (`low`=1.0, `medium`=2.0,
`high`=3.5, normalised against the maximum any single real profile could reach) are a transparent
first pass, not a fitted model, and the module's own output says so in every non-trivial `summary`
string. This is stated as plainly in the code as it is here, specifically so it cannot be
misrepresented as more rigorous than it is when shown to Fusion21 or an examiner.

## 4. A caught bug, briefly (full detail already in `CLAUDE.md`)

A manual audit on 15 Aug 2026 found that `market_conditions="slow"` was named in this module's own
docstring as a screened factor but had no corresponding rule — a real gap between what the module
claimed to do and what it actually did. Fixed, and covered by `tests/test_challenge_risk.py`. Also
fixed in the same pass: the score normalizer originally summed the severity weight of every rule
variant including mutually-exclusive ones (`documentation_quality` can be `weak` *or* `partial`,
never both), which inflated the denominator past what any real profile could reach and silently
suppressed every score — the worst-case profile, which should score ~1.0, initially scored 0.88.

## 5. How Fusion21 actually gets this

- **Live product**: `POST /api/risk-assessment` (`api/main.py`) — rule-based, no LLM call, so it
  runs even while a live negotiation is mid-flight elsewhere in the system. `RiskScreenPanel.tsx`
  exposes a **curated 6-field subset** of the full 16-field taxonomy in the live UI — the
  highest-severity, most CA-verifiable factors (evaluation record documentation, evaluation panel
  composition, internal accountability exposure, score margin, the draft debrief itself, and wider
  market conditions) — not the full set, deliberately, to keep the live form usable. Every dropdown
  defaults to "Not screened for," matching the module's own discipline: an unset field is absent
  information, not a low-risk finding.
- **Full taxonomy**: the API and `scripts/assess_challenge_risk.py` accept the complete 16-field
  `CAProfile`/`BidderProfile` for a power user (a Fusion21 procurement adviser, not a self-service
  CA) who wants the full Doc 1 factor set.

## 6. Worked examples against the 8 real cases

None of this system's 8 real cases (`src/cases/real_cases.py`) come with a `CAProfile`/`BidderProfile`
attached — they were built for the negotiation/Court evaluation, not this screen. To demonstrate the
screen honestly rather than assert its usefulness, profile fields below are populated **only** where
the real case's own source text directly states or unambiguously entails the value — no field is
filled in because it would make a more interesting example. Every other field of the 16 was left
unset. This is deliberately the same discipline the rest of this project applies to case research.

| Case | Fields evidenced from the judgment | Result |
|---|---|---|
| Braceurself v NHS England | `score_margin="narrow"` (80.25% vs 82.5%, stated); `incumbent=True` (stated) | **medium**, 0.1719 |
| Lancashire Care v Lancashire CC | `feedback_quality_received="minimal"` (court found reasons "too vague and generic"); `incumbent=True` (stated) | **medium**, 0.1719 |
| Bromcom v United Learning Trust | `incumbent=False` (Arbor, the winner, is the one described as incumbent to part of the estate) | **low**, 0.0 |
| Parkingeye v Velindre | `score_margin="wide"` (68% vs 84%, a 16-point gap — not narrow); `incumbent=True` (stated) | **low**, 0.0625 |
| Woods v Milton Keynes | `incumbent=True` (stated) | **low**, 0.0625 |
| AbbVie v NHS England (CA won) | `organisation_size="large"` (one of three national suppliers) | **low**, 0.0312 |
| Faraday, Alstom | *(no fields set — see below)* | **low**, 0.0 |

**Read this table carefully before drawing a conclusion from it — it is not a validation study.**
All 8 real cases are litigated disputes by construction (that is why they are in this corpus), so
there is no "correctly predicted no challenge" comparison available, and n=6 (Faraday and Alstom
produced no evidenced fields at all) is far too small to claim predictive power either way. What it
*does* honestly show:

- **Two of the six cases reach "medium" from bidder-side facts alone** — Braceurself and Lancashire,
  using nothing the CA needed to estimate, only what the judgment itself states. Both are also two of
  the clearest cases in the corpus where a court found the CA's process actually defective (a
  manifest scoring error; a transparency/adequacy-of-reasons failure). That is a suggestive
  co-occurrence worth naming, not a validated correlation — six cases cannot establish one.
- **Four of six land "low" despite being real, litigated challenges** — and this is a finding about
  data coverage, not a failure of the screen. Reported TCC/Court of Appeal judgments record legal
  reasoning about what happened; they very rarely record the internal pre-award conditions this
  screen is built to catch (was the evaluation panel procurement-trained, was the audit trail
  complete, was there internal accountability pressure). Those are things a CA knows about its own
  process pre-award — they are structurally not the kind of fact that shows up in a judgment written
  months or years after the fact. Faraday and Alstom score `low` not because nothing was wrong in
  either case, but because their source texts (like most judgments) simply don't state the specific
  pre-award conditions this screen's rules are keyed to.
- **This is exactly the limitation the module's own code already names**: *"an unpopulated
  CAProfile/BidderProfile will always score as low risk, which is a gap in the input, not a
  finding."* The worked examples confirm that this isn't a hedge added for safety — it is the actual
  behaviour, demonstrated on real cases, and it is the direct argument for why this screen has to be
  filled in by the CA from its own knowledge rather than reconstructed after the fact from a
  judgment.

## 7. What would turn this from a documented heuristic into a measured one

The severity weights in §3(c) are Doc 1's directional relationships translated into a transparent,
but not fitted, scoring scheme. The one thing that would let `risk_score` graduate from an ordering
device to an actual calibrated probability is **anonymised pre-action data from Fusion21's member
base** — for procurements that did and did not receive a formal challenge, the same profile fields
this screen already asks for (documentation quality, score margin, feedback quality, and the rest),
plus the outcome. With that, the current severity-weighted-sum heuristic could be replaced or
validated against a fitted model (even something as simple as logistic regression over the 16
factors), and `risk_score` could honestly be reported as a probability rather than a triage ordering.
This is the single concrete ask this module has of Fusion21, and is the natural first entry in a
"Client Actions" list (added to `CLAUDE.md` alongside this write-up, since it was referenced there
twice already but never actually written down).

## 8. Where this sits relative to the rest of the project

Two deliverables, deliberately kept distinct rather than blended into one story:

1. **This screen** — the practical, product-facing answer to Phil's actual framing of the project's
   purpose. Needs no LLM call, runs in milliseconds, and has a real (if not yet realised) path to
   validation against Fusion21's own outcome data.
2. **The negotiation simulator, its Court-prompt ablation, and the statistical/fabrication-screening
   evaluation layers built on top of it** (`evaluation-five-cases.md`, `evaluation-bailii-expansion.md`,
   `evaluation-counterfactual-regret.md`, and the `scripts/analyze_*.py` family) — this is the
   project's academic contribution: a worked methodology for evaluating a multi-agent LLM system on a
   task (legal compliance assessment) where ground truth is scarce and fabrication risk is real. It
   answers the dissertation's own second framing question ("how do we evaluate such solutions and
   negotiations given by agents"), not Fusion21's product ask directly.

The settlement recommendation synthesizer (`src/recommendation/settlement_recommendation.py`) sits
between the two, and is explicitly the lower-priority of the pair: it was the project's own
suggestion to Phil, not his ask, and — as confirmed by reading `api/sessions.py` and `api/main.py`
directly — it is not wired to run live for a real user's real dispute; it only ever reads and
aggregates an already-completed offline batch. It exists because the batch-evaluation infrastructure
built for the dissertation's evaluation chapter turned out to be reframeable as a Monte Carlo signal,
not because Fusion21 asked for an eight-replay-per-dispute product feature. Keep this priority
ordering in mind before investing further build time: the risk screen is the deliverable; the
recommendation synthesizer is a secondary reuse of evaluation infrastructure that happens to also be
useful.

## 9. Limitations, stated plainly

- Not validated against real outcomes — §7 names exactly what would close this gap.
- Severity weights are a transparent heuristic, not a fitted model.
- Several real disputed grounds this project has now researched in depth (evaluation-methodology
  timing, tender-notice value transparency, threshold/exclusion-criteria disputes, and — as Faraday
  shows — process avoidance, choosing not to run a competitive procurement at all) are **not covered
  by any of the 16 current rules**, which are keyed to *evaluating a competition that was run*, not
  to whether one should have been run, or whether its rules were fixed and published correctly in
  advance. §6's Parkingeye and Faraday results are partly a demonstration of this specific coverage
  gap, not just of missing pre-award data.
- The live UI's 6-field curated subset is a usability choice, not a completeness claim — a power
  user wanting the full 16-field Doc 1 taxonomy needs the API or CLI script directly.
