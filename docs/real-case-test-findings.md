# Real Case Test Findings — Pre-Presentation Bug Log

Two real UK procurement judgments were run through the system as a test of real-case
grounding. This log records every confirmed bug, with evidence, for use during debugging.

## Test 1: Prime Way Care Ltd v Southwark [2026] EWHC 1845 (TCC)

**True holding:** Interim specific disclosure application under CPR 31.12, applying the
*Roche Diagnostics* principles. The judge does not rule on whether Southwark's scoring
was correct. He assesses whether Prime Way has a prima facie case and whether the
disclosure sought is proportionate, and orders disclosure of five anonymised bidders'
evaluation records into a confidentiality ring.

**System output:**
- `contract_value_gbp` extracted as `0` — the real document is a disclosure hearing and
  never states a headline contract value.
- `procedural_stage` extracted as `"trial"` — actually a pre-disclosure interim application.
- Court agent's compliance review reasons about "manifest error" in the scoring process
  ("it appears the CA may be withholding information... which could indicate a manifest
  error in the evaluation process") — a non sequitur. Withholding disclosure and making a
  scoring error are different legal questions; the real case never assesses scoring merits.
- Final recommended action: **"re-evaluation ordered"** — does not appear anywhere in the
  real judgment.
- The system's own auto-generated scenario summary (shown at the top of the UI) correctly
  states: *"granted the application for early specific disclosure"* — this is accurate. But
  the negotiation runs anyway and the Court agent's own final round contradicts it.

## Test 2: Geodesign Barriers Ltd v Environment Agency [2015] EWHC 1121 (TCC)

**True holding:** Also a CPR 31.12 disclosure application (Coulson J, same judge who wrote
the *Roche* principles). Governed by the **Public Contracts Regulations 2006** (case
predates the Procurement Act 2023 by 8 years). Court refused disclosure of Categories A/B/D
(no such documents existed), **granted disclosure of Categories C and E** (guidance emails
+ competitor bid documents), refused to disclose unsuccessful tenderers' identities, refused
the amendment application, and allowed **one** expert into the confidentiality ring (not two).

**System output:**
- `procedural_stage` again extracted as `"trial"` — same misclassification as Test 1.
- `legal_basis` cites "Procurement Act 2023" and "Public Contracts Regulations 2015" —
  both wrong. The real case is governed by PCR **2006**; 2023 Act didn't exist in 2015;
  "PCR 2015" isn't the correct regulation name at all.
- Aggrieved Bidder's stated interest claims a **"£150,000"** investment figure — this number
  appears nowhere in the source document. Same fabrication pattern as the £0 contract-value
  bug in Test 1, just the opposite direction (inventing a number instead of zeroing one out).
- Court agent's round 2 reasoning cites **"Regulation 86(1) and (3)"** and the **"Freedom of
  Information Act 2000"** — neither appears anywhere in the real judgment. The real case
  cites *Roche*, *Alstom v Eurostar*, *Mears v Leeds*, *Covanta v Merseyside*, *Group M v
  Cabinet Office*. None of these are ever mentioned by the simulated Court agent.
- Same self-contradiction pattern as Test 1: system's own scenario summary is accurate
  ("ordering disclosure of category C and E documents... rejecting the request for
  identities... one expert"), but the negotiation's own final Court verdict lands on
  **"no remedy - decision stands"**, contradicting both the true outcome and the agents'
  own mid-negotiation concessions.

## Cross-case patterns (systematic, confirmed on 2/2 real cases — not one-off bugs)

1. `procedural_stage` defaults/misclassifies to `"trial"` regardless of actual stage.
2. Numeric fields (contract value, investment figures) get zeroed out or invented when not
   stated in the source document, instead of degrading to "not stated."
3. **Court agent has no concept of disclosure/procedural disputes.** It only knows how to
   assess merits/scoring disputes (manifest error, numeric-vs-qualitative). Both real cases
   tested so far are disclosure applications, so the Court agent answers the wrong legal
   question both times.
4. `legal_basis` doesn't adapt to the case's actual date/governing legislation — appears
   hardcoded toward the Procurement Act 2023 regardless of when the case was decided.
5. Court agent occasionally fabricates specific pinpoint citations (regulation numbers,
   statute names) not present in its inputs.
6. **Negotiating agents never consult the extraction pipeline's own correctly-extracted
   outcome.** The scenario summary shown in the UI is accurate in both tests; the live
   negotiation's final Court verdict contradicts it in both tests anyway.

## Fix priority

- **Phase 1 (low risk):** #2, #1, #4 — extraction/defaulting bugs, mechanical fixes.
- **Phase 2 (medium risk):** #5 — constrain Court agent citations to its actual inputs.
- **Phase 3 (high risk, needs regression testing):** #3 and #6 — dispute-type branching
  and grounding the Court's final verdict against the extracted true outcome. This is
  comparable in scope to the original V1→V2→V3 Court agent fix and must not regress the
  validated synthetic scenario results (F21-002 ~100%, F21-001 ~57% agreement).
