# Court-Prompt Ablation: Five Real-Case Studies

*Section for the evaluation chapter. Covers all five real cases in the V3/V4 Court-prompt ablation
(Lancashire Care, Faraday, Parkingeye, Alstom, Woods) — the last two added specifically to give the
ablation discriminative power the first three could not provide on their own. All figures below are
drawn directly from committed `batch_results/` summaries (n = 8 runs per cell, max 5 rounds, Llama 3.1
8B via Ollama, except where noted); batch identifiers are given so every number here is independently
reproducible from the repository.*

## 1. Why five cases, and why two were added later

The V3/V4 ablation (§ — Court agent, Doc 1 interest taxonomy) tests whether re-specifying the Court
agent's stated interests against Fusion21's own document changes its judgment, not merely its stated
reasoning. On the first three real cases alone — Lancashire Care, Faraday, Parkingeye — that test was
under-powered in one specific way: none of them publishes a scoring formula with sub-scores, so nothing
exercised the Court agent's Step 2A exact-arithmetic branch once the earlier synthetic F21-002 scenario
was retired in favour of real-case-only evaluation. Woods Building Services v Milton Keynes Council
[2015] EWHC 2011 (TCC) was added to restore that coverage — it publishes a real, verified 60% price /
40% quality formula and a real, court-quantified correction. Alstom Transport UK Ltd v London
Underground Ltd [2017] EWHC 1521 (TCC) was added because, on the first three cases, V3 already found
manifest error in every run or nearly every run — a case close enough to the line that Court *judgment*,
not just fact-finding, does the deciding work was needed to see V3 and V4 genuinely diverge.

As reported below, the five-case corpus as a whole surfaces two findings that a smaller corpus would
not have: a systematic mismatch between what two of the five cases actually decided in reality (an
interim procedural ruling) and what the simulation is structurally capable of modelling (only a merits
verdict), and — the more serious of the two — a case (Faraday) whose dispute shape does not fit the
scoring-challenge template every agent prompt in this system implicitly assumes, with a directly
traceable consequence.

## 2. Summary table

| Case | Real dispute type | V3 outcomes | V4 outcomes | V3 resolution / deadlock | V4 resolution / deadlock | V3 avg rounds | V4 avg rounds |
|---|---|---|---|---|---|---|---|
| Lancashire Care | Transparency / adequacy of reasons | 7 re-eval, 1 deadlock | 8 re-eval | 0.875 / 0.125 | 1.00 / 0.00 | 2.75 | 1.25 |
| Faraday | Process avoidance (not scoring) | 6 re-eval, 2 deadlock | 8 re-eval | 0.75 / 0.25 | 1.00 / 0.00 | 3.00 | 1.12 |
| Parkingeye | Transparency (value mis-statement) | 8 re-eval | 8 re-eval | 1.00 / 0.00 | 1.00 / 0.00 | 1.50 | 1.12 |
| Alstom | Technical-threshold manifest error | 4 re-eval, 4 deadlock | 6 re-eval, 2 no-remedy | 0.50 / 0.50 | 1.00 / 0.00 | 4.38 | 2.12 |
| Woods (post-patch) | Numeric scoring correction | 8 re-eval | 8 re-eval | 1.00 / 0.00 | 1.00 / 0.00 | 1.00 | 1.00 |

Batch identifiers: Lancashire V3 `batch_20260815_213642`, V4 `_214210`; Faraday V3 `_214543`, V4
`_215108`; Parkingeye V3 `_220726`, V4 `_221124`; Alstom V3 `_192629`, V4 `_193406`; Woods (post-patch)
V3 `_200902`, V4 `_201219`. Structural compliance is 1.00 in every cell in this table (no JSON repair
needed across any of the ten batches) — see the compliance-instrumentation section elsewhere in this
chapter for the corpus-wide figure, which is lower once earlier, pre-fix batches are included.

A pattern holds across every case where V3 produced any deadlock at all (Lancashire, Faraday, Alstom):
**V4 never deadlocks, and resolves in roughly half the rounds V3 takes.** This is consistent across
three independent cases, not a single-case artefact, and matches Doc 1's fifth judicial-interest
category — *"Efficient Use of Judicial Resources... encourage settlement or the narrowing of
issues"* — which V4 adds to the Court agent's stated interests and V3 does not.

## 3. Lancashire Care NHS Foundation Trust & Blackpool Teaching Hospitals NHS Foundation Trust v Lancashire County Council

### 3.1 Case background

A £104m, 5-year contract for Public Health Nursing and the 0-19 Healthy Child Programme, awarded to
Virgin Care Services Ltd over the incumbent NHS Trusts' joint bid. The Trusts' challenge was not that a
specific number was wrong, but that the Council's stated reasons for the scoring differential were
*legally inadequate* — too vague and generic to allow either the Trusts or the court to assess whether
a manifest error had occurred at all. At full trial, Stuart-Smith J found in the Trusts' favour on
exactly that basis and set aside the award, requiring the Council to reconsider its decision. This is
the cleanest possible test of the Court agent's transparency/adequacy-of-reasons reasoning, since the
real legal question and the remedy both map onto categories the simulation already has (a compliance
failure requiring the process to be redone).

### 3.2 Results

Resolution rate rises from 0.875 to 1.00 (V3's single deadlocked run resolves under V4), and average
rounds drop from 2.75 to 1.25. Manifest-error detection is identical at 0.75 across both versions — as
with Alstom, V4 changes how efficiently a case concludes once a compliance issue is found, not whether
one is found. The single V3 deadlock and the seven V3 re-evaluation runs both correctly track the real
transparency-failure framing in the reasoning texts sampled; no fabrication or off-premise reasoning was
found in either batch. This is the most straightforwardly successful of the five cases — real dispute
type, real remedy, real outcome direction all map cleanly onto the simulation's vocabulary, and both
prompt versions reach the historically consistent outcome in the overwhelming majority of runs.

## 4. Faraday Development Ltd v West Berkshire Council

### 4.1 Case background

Faraday is not a scoring dispute. West Berkshire Council structured a £125m regeneration deal with St
Modwen Developments Ltd as a conditional land agreement rather than running a competitive procurement
at all; Faraday's claim was that this was process avoidance — the deal was, in substance, a public
works contract that should have been competitively tendered, and Faraday was never given the
opportunity to bid into any process, scored or otherwise. The Court of Appeal agreed in 2018, reversing
the High Court, and made a declaration of ineffectiveness — the first since the remedy was introduced
in 2009 — with a nominal £1 civil penalty. There is no evaluation panel, no published criteria, no
submitted-and-scored bid from Faraday anywhere in the real facts.

### 4.2 Extraction correctly captured this; the negotiation agents did not preserve it

The extraction agent got this right: the cached scenario (`batch_results/_scenarios/faraday-west-
berkshire.json`) carries `dispute_type: "process_avoidance"` — the only real case in this corpus not
labelled `"scoring_challenge"` or `"transparency_breach"` — and its description text is accurate,
naming no bid, no scoring, no evaluation criteria. The failure is downstream.

Sampling the batch transcripts shows the Bidder agent's own pre-negotiation opening position is already
generic and scoring-shaped ("We request a re-evaluation of submitted bids to ensure fairness and
transparency"), despite Faraday never having submitted a bid. By round 1 of several runs, this
generalises into a specific, concrete, and unsupported claim. From `batch_20260815_215108/run_01.json`:

> **Contracting Authority:** "...I would like to clarify whether they are specifically challenging the
> evaluation criteria used for the conditional land agreement..."
>
> **Aggrieved Bidder:** "...we are challenging the evaluation criteria used for the conditional land
> agreement as it relates to the scoring discrepancy between our bid and that of St Modwen Developments
> Ltd. We believe that this discrepancy is a manifest error and warrants a re-evaluation..."

There is no "scoring discrepancy between our bid and that of St Modwen" in the real case — Faraday
never had a bid to compare, and St Modwen was awarded the contract without any competitive process for
either party to be scored against. This is a fabricated factual premise, invented independently by the
CA and Bidder agents (both open in scoring-shaped language before either has introduced the specific
"scoring discrepancy" detail), and it recurs: **3 of 8 V3 runs and 6 of 8 V4 runs contain this specific
fabricated bid-comparison framing**, checked by scanning every run's full transcript for the phrase and
for co-occurring references to "our bid" and "St Modwen." The Court agent, whose Step 1 gating logic
was hardened (§ Woods) to catch *numeric* fabrication, has no equivalent check for a fabricated
*narrative premise* introduced by another agent — it adopts the "scoring discrepancy" framing rather
than catching that it contradicts the scenario description both agents were actually given.

The likely root cause is architectural rather than case-specific: every other scenario this project has
ever run through the pipeline — the deleted synthetic F21-001/F21-002 pair and four of the five real
cases — is a genuine scored-bid dispute, and the CA and Bidder system prompts (`src/prompts/
ca_prompt.py`, `bidder_prompt.py`) were iteratively developed and tuned entirely against that shape.
Neither prompt contains any branching for a dispute where no bid was ever scored. Confronted with
`dispute_type: "process_avoidance"`, both agents default to the only script they have.

### 4.3 Results, and what they mean given §4.2

Both prompt versions reach "re-evaluation" in 8/8 runs (V3: 6/8 re-evaluation, 2/8 deadlock; V4: 8/8
re-evaluation). Manifest-error detection rises from 0.75 (V3) to 1.00 (V4) — a modest shift, and given
the fabrication finding above, one that should not be read as evidence about Faraday's real facts
either way. **"Re-evaluation" is not a coherent remedy for the real Faraday outcome regardless of which
prompt version produces it.** There is no scoring to redo; the real remedy — a declaration of
ineffectiveness — has no corresponding category in `KNOWN_OUTCOMES`
(`src/recommendation/settlement_recommendation.py`) at all, unlike Woods, where "re-evaluation" is at
least the right *kind* of remedy even if less decisive than what actually happened. This is a
vocabulary-coverage gap, not merely a granularity gap: the simulation cannot currently represent
Faraday's real remedy even in principle, and given §4.2, is not reliably negotiating over Faraday's real
facts either.

This is, on reflection, the most consequential finding in the five-case corpus. It does not undermine
the numeric anti-fabrication result that is this project's central finding (§ Court Agent Design) — the
Court agent still does not invent arithmetic here, exactly as designed. It does show that discipline has
a scope boundary: it constrains what the Court agent computes, not what factual premise the negotiation
that precedes it is conducted over, and nothing in the current architecture checks a CA or Bidder
statement against the scenario record the way the Court agent's Step 1 gate checks a numeric claim.

## 5. Parkingeye Ltd v Velindre University NHS Trust & Cardiff and Vale University Health Board

### 5.1 Case background

A car park management contract whose tender notice stated a value of £100,000 against a real value in
the £10–20m range — Parkingeye's central complaint. As with Alstom, this reached the Technology and
Construction Court as an interim application, not a merits trial: the contracting authorities sought to
lift the automatic suspension so they could sign with the winning bidder, NPCG, before Parkingeye's
substantive transparency and evaluation-methodology claims were heard. Under the Procurement Act 2023's
new s.101 public-interest test — the first reported judicial application of that test, replacing the
pre-2023 American Cyanamid approach — Keyser J *refused* to lift the suspension, finding the balance of
public interest favoured letting Parkingeye's challenge proceed to a full hearing. **The substantive
transparency and methodology allegations were, like Alstom's manifest-error allegation, not resolved on
the merits at this stage.**

### 5.2 Results

Both prompt versions reach "re-evaluation" unanimously — 8/8 for V3, 8/8 for V4 — with V4 resolving
modestly faster (1.12 vs 1.50 average rounds) and identical, maximal manifest-error detection (1.00 vs
1.00). The extraction record for this case is accurate — the tender-notice value discrepancy is
faithfully captured as a real, verifiable transparency failure, and (unlike Faraday) the CA and Bidder
agents are negotiating over facts the case actually supports, since Parkingeye is a genuine scored-bid
dispute (68% against NPCG's 84%) with a real, additional transparency defect layered on top.

### 5.3 The same correction applied to Alstom applies here, in the opposite direction

As with Alstom (§6.3 below), it is tempting to read unanimous "re-evaluation" as the simulation
reproducing the real result. The real result was procedural: the suspension was *maintained*, meaning
Parkingeye's challenge survived to be heard, not that a court found the CA's process non-compliant.
"Re-evaluation," in this system's vocabulary, is a merits conclusion the real case has not yet reached.
Directionally, both outcomes favour the challenger over the contracting authority proceeding unchecked —
which is worth noting, since it is the mirror image of Alstom, where the real interim ruling favoured
the contracting authority — but reporting this as mechanistic replication would overstate what a
simulation with no interim-relief mechanism can show. Two of the five cases in this corpus (Alstom,
Parkingeye) were in fact decided at the interim-suspension stage in reality; the simulation models
neither stage distinctly, because it only ever conducts a merits-stage Step 2A/2B assessment. That is a
structural limitation of the current architecture, evidenced now on two independent cases rather than
one, and is addressed as a corpus-level finding in §7.

## 6. Alstom Transport UK Ltd v London Underground Ltd

### 6.1 Case background

A £112.1m contract for AC traction motors and control equipment, awarded to Bombardier over Alstom.
Alstom alleged Bombardier's bid should have failed a mandatory Stage 3 technical threshold and been
excluded — a manifest error in applying the stated evaluation methodology. As with Parkingeye, this
reached the TCC as an application to lift the automatic suspension, decided under the pre-2023 American
Cyanamid test (serious issue to be tried; adequacy of damages; balance of convenience). Stuart-Smith J
found Alstom's evidence of irreparable harm "barely credible," concluded damages would be an adequate
remedy, and lifted the suspension, allowing London Underground to proceed with Bombardier. **Alstom's
underlying manifest-error allegation was never resolved on the merits.**

### 6.2 Results (n = 8, max 5 rounds)

| | V3 | V4 |
|---|---|---|
| Outcome distribution | 4/8 re-evaluation, 4/8 deadlock | 6/8 re-evaluation, 2/8 no remedy – decision stands |
| Resolution rate | 0.50 | **1.00** |
| Deadlock rate | 0.50 | **0.00** |
| Manifest-error detection rate | 0.50 | 0.50 |
| Average rounds to conclusion | 4.38 | **2.12** |
| Average run duration | 56.7s | 34.9s |
| Structural compliance | 1.00 (147/147) | 1.00 (91/91) |

Alstom is the only case in the five-case table where V3 and V4 diverge in outcome *composition*, not
merely in confidence around the same modal outcome — and the manifest-error detection rate is identical
(0.50) across both versions, so the divergence is entirely in what happens *conditional on* a finding,
not in whether one is made.

### 6.3 Interpreting the "no remedy" runs — a necessary correction, not a claim of exact replication

Two of V4's eight runs conclude "no remedy — decision stands"; V3 never reaches this outcome in eight
runs. It is tempting to read this as V4 uniquely reproducing the real-world result. **That reading
overstates what the data supports, and the more precise claim is more useful than the loose one.**

The real Alstom result was an interim procedural ruling — a suspension lifted on a balance-of-
convenience test, with the underlying manifest-error allegation left formally unresolved. "No remedy —
decision stands," in this system's vocabulary, means the Court agent has independently assessed the
*merits* and found the process compliant. Those are not the same kind of event, and the simulation has
no interim-suspension mechanism at all — it cannot reproduce Alstom's actual procedural history
regardless of prompt version. What the two V4 runs do show is directional and practical consistency:
in both the simulation and the real case, the contracting authority's award stands and the challenge
does not succeed in overturning it — evidence that V4's Court agent is at least capable of concluding
in the CA's favour on the merits of a genuinely arguable technical-threshold dispute, which V3 never
does across the same eight runs, but not evidence the simulation replicated the real legal reasoning.
The honest framing is as much a limitation finding — this simulation does not model interim relief or
the automatic-suspension mechanism that actually decided Alstom — as a positive result about V4.

## 7. Woods Building Services v Milton Keynes Council

*(Full case background, the two-layer extraction/fabrication bug, its fix, and post-fix verification
are covered in detail in the standalone Woods section of this chapter — summarised here for the
corpus-level picture.)*

Woods was added to restore Step 2A (exact-arithmetic) coverage, which the other four cases cannot
provide since none publishes a scoring formula with sub-scores. Adding it surfaced a genuine two-layer
defect: an extraction-fidelity gap that summarised the published 60/40 formula out of the scenario
before the Court agent ever saw it (fixed in commit `71d55eb`), and — once that was fixed and the
formula reached the Court agent for the first time — a Step 1 gating gap that let the Court agent
fabricate the missing original sub-scores to force a complete calculation, rather than recognising a
stated correction is not the same as a stated input (fixed in commit `329848e`). Post-fix, both prompt
versions reach "re-evaluation" unanimously in every run, in a single round, with zero fabricated values
found across a systematic scan of all 16 post-fix compliance-check reasoning texts:

| | V3 (post-patch) | V4 (post-patch) |
|---|---|---|
| Outcome distribution | 8/8 re-evaluation | 8/8 re-evaluation |
| Manifest-error detection rate | 1.00 | 1.00 |
| Average rounds to conclusion | 1.00 | 1.00 |
| Structural compliance | 1.00 (64/64) | 1.00 (64/64) |

*(Batches: V3 `batch_20260815_200902`, V4 `_201219`.)* Unlike Alstom and Parkingeye, Woods is a full
merits trial in reality, so "re-evaluation" is a genuinely close match in kind to the real remedy —
though, as with Faraday's vocabulary gap in the opposite direction, the real remedy was in fact more
decisive than "re-evaluation" implies: the court did not merely order the scoring redone, it
independently determined and declared the corrected winner. `KNOWN_OUTCOMES` has no category for a
court-determined re-ranking distinct from an authority-conducted re-evaluation.

## 8. Synthesis across all five cases

1. **V4 resolves faster and deadlocks less, consistently.** Every case where V3 produced any deadlock
   (Lancashire, Faraday, Alstom) shows V4 reaching 0.00 deadlock and roughly half the round count, while
   leaving manifest-error detection materially unchanged in two of the three (Lancashire identical at
   0.75; Alstom identical at 0.50; Faraday shifts from 0.75 to 1.00). This is consistent with Doc 1's
   "Efficient Use of Judicial Resources" category, present in V4's stated interests and absent from
   V3's, and is now evidenced across three independent cases rather than one.

2. **The remedy vocabulary is built for scoring disputes and has real coverage gaps outside that
   shape.** Woods needs a court-determined-ranking category it doesn't have; Faraday needs a
   declaration-of-ineffectiveness category it doesn't have at all. `KNOWN_OUTCOMES`
   (`src/recommendation/settlement_recommendation.py`) was constructed from the Court agent's own
   documented vocabulary, which was in turn built for the scoring-challenge dispute type that
   dominates this corpus — extending it to the shapes exposed here is a concrete, evidenced next step
   rather than a speculative one.

3. **Two of five real cases were decided at the interim-suspension stage in reality, and the
   simulation cannot represent that stage at all.** Alstom and Parkingeye were both decided on
   applications to lift (or maintain) automatic suspension, under materially different legal tests
   (American Cyanamid pre-2023; the Procurement Act 2023 s.101 public-interest test for Parkingeye,
   the first reported application of it), with the underlying merits claim left unresolved in both.
   The simulation only ever conducts a merits-stage Step 2A/2B assessment. Any apparent correspondence
   between a simulated outcome and either case's real result is directional at best (does the
   simulated party who prevails match the real party who prevailed procedurally) and should never be
   read as evidence the simulation reproduced the real legal reasoning.

4. **The anti-fabrication discipline built into the Court agent has a scope boundary the Faraday case
   exposes concretely.** Step 1's gating logic (§ Woods) prevents the Court agent from inventing
   numbers. It does not, and currently cannot, prevent the CA or Bidder agent from inventing a factual
   premise — Faraday's "scoring discrepancy between our bid and St Modwen's" — that contradicts the
   scenario both agents were actually given, nor does it prevent the Court agent from adopting that
   premise uncritically. This recurred in a majority of Faraday's V4 runs (6/8) and a minority of V3's
   (3/8), and is traceable to a specific, checkable cause: every CA/Bidder prompt in this system was
   developed against scored-bid disputes, and neither has a written branch for a case where no bid was
   ever scored.

## 9. Limitations

- **n = 8 per cell, no significance testing performed.** Every rate reported above is an empirical
  proportion from eight repeated runs of the same scenario on a non-deterministic model. None of the
  differences reported here — including the detection-rate shift on Faraday and the round-count
  differences reported throughout — have been tested for statistical significance; all should be read
  as "consistent with a real effect on this sample," not as established results. A Fisher's exact test
  on each case's 2×2 outcome table is a straightforward, not-yet-performed extension.
- **Single scenario per case.** Each case is one procurement dispute, extracted once and cached; the
  eight runs per cell vary only in the LLM's sampling, not in any structural feature of the dispute.
  This measures run-to-run reliability, not sensitivity to case variation.
- **The "historical match" language throughout this section is deliberately hedged, and that hedging is
  itself a limitation being reported, not minimised.** Two of five cases (Alstom, Parkingeye) can only
  ever show directional consistency with their real outcomes, because the simulation has no
  interim-relief mechanism; overclaiming exact real-world replication on either would be exactly the
  kind of fabrication this project's Court-agent design discipline exists to prevent, applied to the
  evaluation write-up rather than to the model under test.
- **The Faraday fabrication finding was checked by string search, not independently re-read run by
  run.** The 3/8 (V3) and 6/8 (V4) figures come from scanning each run's full transcript for the phrase
  "scoring discrepancy" and co-occurring references to "our bid" and "St Modwen." This will miss any
  differently-worded instance of the same underlying fabrication and should be read as a lower bound,
  not an exact count.
- **The Woods bug's generality beyond Woods itself has not been independently tested.** It is reported
  because it was caught on this specific case, not because Woods is known to be the only scenario shape
  capable of triggering it (a formula with a stated correction but incomplete inputs) — nor, by the same
  logic, is Faraday's premise-fabrication finding known to be unique to process-avoidance disputes
  specifically, as opposed to any dispute type this system has not yet been tested against.
