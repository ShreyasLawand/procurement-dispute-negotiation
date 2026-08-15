# Counterfactual Regret: Simulated Resolution Speed vs Real Litigation Timelines

*Evaluation punch-list item 24. Compares how long each real case actually took to resolve against how
long the simulation takes to reach a compliance finding on the same facts — the closest defensible
version of a counterfactual-regret argument this project's current data supports.*

## What this is not

The original framing of this item was stronger: "in k of n real cases, a settlement existed that both
parties would rationally have preferred to the litigated result." **That claim cannot be honestly made
from the data this project has.** It would require case-scaled litigation cost estimates and a test of
whether *both* parties would actually have accepted the simulated outcome — the dual-acceptance
simulation (punch-list item 23), not yet built. It would also require the simulation's BATNA figures to
scale with the case, and they do not: every Contracting Authority agent, regardless of whether the real
contract is worth £8m (Woods) or £125m (Faraday), is given the identical fixed string — *"costly
(£50k+ legal fees), time-consuming (6-12 months)"* (`src/prompts/ca_prompt.py`). Computing a
counterfactual saving from that figure would be fabricated precision of exactly the kind this project's
whole discipline exists to prevent, applied to the evaluation chapter rather than to the model. This
section reports what can honestly be shown instead: a timeline comparison, and the concrete
prerequisite (case-scaled BATNA costs) that would need to exist before the stronger claim could be made.

## Real timelines vs simulated resolution time

| Case | Real timeline | Real process | Simulated resolution (median) |
|---|---|---|---|
| Lancashire Care | Feb–Jun 2018 (~4 months, two judgments: EWHC 200, EWHC 1589) | Full merits trial | 1–3 rounds, well under a minute |
| Faraday | 2016 (first instance) → Nov 2018 (Court of Appeal) — **~2 years** | Full merits trial, two court levels, reversed on appeal | 1–3 rounds, well under a minute |
| Woods | Jul 2015 (liability) → later 2015 (separate remedies judgment: EWHC 2011, EWHC 2172) | Full merits trial | 1 round, ~25s |
| Parkingeye | 2026, ongoing — interim ruling only; substantive claims not yet heard at time of writing | Interim suspension application (Procurement Act 2023 s.101) | 1–2 rounds, well under a minute |
| Alstom | 2017, interim ruling only; underlying manifest-error claim never resolved | Interim suspension application (pre-2023 American Cyanamid) | 2–5 rounds, under a minute |

For the three cases that were genuine merits trials in reality (Lancashire, Faraday, Woods), the real
process took between four months and two years. The simulation reaches a compliance finding on the same
facts in one to a handful of rounds, each taking on the order of tens of seconds. This gap is not
surprising — an LLM reading a case summary is not equivalent to disclosure, witness evidence, and a
contested hearing — but it is the honest basis for the actual, supportable claim here.

## What this does and does not support

**Supports:** a cheap, near-instant *signal* of the likely compliance finding is available before any
of the real cost of litigation is incurred. For all three merits-trial cases, the simulation's modal
outcome (re-evaluation, in every one) is consistent with the direction of the real result. That is the
core premise behind treating repeated simulation as a form of computational Early Neutral Evaluation
(the framing already adopted in `src/recommendation/settlement_recommendation.py`) — an early,
cheap signal that could in principle shorten the path to a real settlement.

**Does not support:** any claim that this signal would have *changed* what actually happened, that both
real parties would have accepted it, or any specific monetary saving. Faraday in particular is a poor
candidate for even the weaker "early signal" claim — §4.2 of `evaluation-five-cases.md` documents that
the CA/Bidder agents fabricate a factual premise on this specific case (a "scoring discrepancy" that
does not exist in reality), so an early signal generated from that fabricated premise is not a signal
worth trusting, regardless of how quickly it was produced. Speed is not validity.

## What would need to be true before the stronger claim could be made

1. **Case-scaled BATNA costs.** The CA and Bidder BATNA text needs to vary with contract value and
   dispute type, not be a fixed string. A £125m regeneration dispute and an £8m services contract do
   not carry the same real litigation exposure, and treating them identically makes any downstream cost
   comparison meaningless by construction.
2. **The dual-acceptance test (item 23).** A recommendation is only evidence of an available settlement
   if both sides — evaluated independently, on their own private information — would actually accept
   it. Nothing in this project currently tests that.
3. **Real settlement data.** As flagged in `CLAUDE.md`'s "client actions" list, the four (now five) real
   cases used throughout this project are, by Fusion21's own Doc 4, atypical — most procurement disputes
   settle before proceedings, and settlement terms are confidential. Without access to real settlement
   terms from Fusion21's member base, there is no ground truth to validate a counterfactual-regret claim
   against even if items 1 and 2 above were built.

The honest conclusion is a scoping one: this project can currently show that simulated resolution is
much faster than real litigation, and that the direction of the simulated outcome is consistent with
real merits-trial results on the cases it has been tested against. It cannot yet show that a real
settlement existed that both parties would have preferred, because it does not yet have the case-scaled
cost model, the dual-acceptance mechanism, or the real settlement data that claim would require.
