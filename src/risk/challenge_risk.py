"""
Pre-award challenge risk screen — evaluation punch-list item 8.

WHAT THIS IS: a screen a contracting authority (or the framework operator, on
their behalf) runs BEFORE the standstill letter goes out, over the evaluation
record and the draft debrief it's about to send. It flags the practical
conditions Fusion21's own Doc 1 identifies as raising the likelihood of a
challenge, and suggests concrete mitigations — most of which are cheap
(tighten the debrief, document the moderation record) if done before the
letter is sent, and expensive (litigation) if not.

WHY THIS IS THE HIGHEST-LEVERAGE MODULE IN THE PROJECT: everything else here —
the negotiation simulator, the settlement recommendation — operates on a
dispute that has ALREADY started. This is the only component that can stop
one from starting at all, which is what Phil actually said the heart of the
project was ("how can we prevent these dispute negotiations"). It is also the
only component with a real, observable ground truth: challenged vs.
not-challenged. Nothing else in this system has that.

CRITICAL FRAMING — READ BEFORE EXTENDING THIS MODULE:

This screen predicts "is a challenge likely to be RAISED", not "would the CA
LOSE a challenge if one were raised". Those are different questions. The
second one requires judging the merits of the evaluation — exactly the job
the Court agent does, under a strict anti-fabrication discipline (see
CLAUDE.md "Court Agent Design"). Collapsing "likely to be challenged" into
"likely to lose" would smuggle a merits judgement in through the back door,
using inputs (score margin, feedback quality) that speak to a BIDDER'S
INCENTIVE to challenge, not to whether the CA's process was actually lawful.
Keep the two questions separate. This module is silent on the merits.

WHAT IS AND ISN'T CALIBRATED — this matters as much as the framing:

Every rule below traces to a specific, quoted sentence in Fusion21's Doc 1
"Practical Considerations" tables (see the RATIONALE strings — each one is
close-paraphrased from the source document, not invented). Doc 1 gives
DIRECTIONAL relationships ("the closer the scores, the GREATER the
likelihood") — it does not give weights, thresholds, or a formula for
combining factors. The severities and score weights below are a deliberately
simple, transparent first pass (severity-weighted sum, normalised), not a
fitted or validated model. Treat `risk_score`/`overall_risk_band` as an
ORDERING device for triage, not a calibrated probability. Validating this
against real challenged/not-challenged outcomes is exactly the ask logged in
CLAUDE.md's "client actions" list — anonymised pre-action or settlement data
from Fusion21's member base is the one thing that would let this graduate
from a documented heuristic to a measured one.

WHAT IS AND ISN'T OBSERVABLE PRE-AWARD:

CAProfile fields are fully within the authority's own knowledge and control
before the standstill letter goes out — including feedback_quality_received,
which despite living on BidderProfile is really "the debrief I am about to
send", the single most actionable lever this screen has. BidderProfile fields
that describe the LOSING bidder's own circumstances (legal_representation,
revenue_dependence, market_conditions) are usually NOT known to the CA with
confidence pre-award; a few (organisation_size, incumbent, score_margin) are
observable because the CA ran the competition. Flags built on the
not-reliably-observable fields are marked `confidence="estimated"` rather
than `confidence="known"` in their output, and every flag lists which
CAProfile/BidderProfile field it came from so a caller can filter on
confidence if they only trust what the CA can actually verify.
"""

from typing import Literal

from pydantic import BaseModel, Field

from src.schemas.agent_state import BidderProfile, CAProfile

Severity = Literal["low", "medium", "high"]
Confidence = Literal["known", "estimated"]

_SEVERITY_WEIGHT: dict[Severity, float] = {"low": 1.0, "medium": 2.0, "high": 3.5}


class RiskFlag(BaseModel):
    """One triggered risk factor, traceable back to a specific profile field
    and a specific sentence in Doc 1."""

    category: str = Field(description="Doc 1 practical-consideration category this traces to")
    field: str = Field(description="The CAProfile/BidderProfile field and value that triggered this")
    severity: Severity
    confidence: Confidence = Field(
        description="'known': the CA can verify this directly. 'estimated': inferred/assumed about the "
        "bidder's circumstances, not confirmed."
    )
    rationale: str = Field(description="Why this raises challenge risk, close-paraphrased from Doc 1")
    mitigation: str = Field(description="A concrete, pre-award action that would reduce this specific flag")


class ChallengeRiskAssessment(BaseModel):
    """The screen's output for one procurement decision, pre-standstill-letter."""

    overall_risk_band: Literal["low", "medium", "high"]
    risk_score: float = Field(ge=0.0, le=1.0, description="Normalised severity-weighted sum — an ordering "
                                                            "device, not a calibrated probability. See module docstring.")
    flags: list[RiskFlag]
    summary: str


# Each rule: (field name, triggering value(s), category, severity, confidence, rationale, mitigation).
# Rationale text is close-paraphrased from Fusion21 Doc 1's "Practical Considerations" tables — see the
# category name for which table (CA or Supplier) it comes from.
_CA_RULES = [
    (
        "documentation_quality", "weak",
        "Approach to Bidder Feedback and Communication", "high", "known",
        "Incomplete documentation, inconsistent evaluation notes, or a weak audit trail push a CA toward "
        "short, vague, defensive responses — and bidders are more inclined to dispute outcomes where the CA "
        "cannot demonstrate the evaluation criteria were applied consistently.",
        "Before the debrief goes out, reconstruct and complete the moderation record for this criterion "
        "specifically — the gap itself is the risk, and it is cheapest to close now.",
    ),
    (
        "documentation_quality", "partial",
        "Approach to Bidder Feedback and Communication", "medium", "known",
        "Serviceable but gapped documentation still limits how much detail can be safely shared, "
        "increasing the chance that the debrief reads as vague or evasive.",
        "Identify the specific gaps before drafting the debrief and either fill them or scope the debrief "
        "to only the well-documented parts.",
    ),
    (
        "panel_capability", "technical_untrained",
        "Composition and Capability of the Evaluation Panel", "high", "known",
        "A panel unfamiliar with transparency, equal treatment and proportionality may not recognise its "
        "own scoring inconsistencies, and may have implicitly favoured the supplier judged 'best for "
        "delivery' rather than the one that scored best against the published methodology.",
        "Have someone with procurement training independently re-read the panel's scoring notes against "
        "the published criteria before the debrief is finalised — catching an inconsistency now is a "
        "correction; catching it after a challenge is a manifest error.",
    ),
    (
        "panel_capability", "mixed",
        "Composition and Capability of the Evaluation Panel", "low", "known",
        "A panel of mixed procurement familiarity has some, but not full, protection against inconsistent "
        "application of the published methodology.",
        "Spot-check the criteria the least procurement-experienced panellists scored.",
    ),
    (
        "internal_accountability_exposure", "high",
        "Risk of Internal Accountability or Disciplinary Action", "medium", "known",
        "Where individuals face personal exposure if irregularities surface, the incentive is to minimise "
        "documentation shared externally and keep responses short and controlled — which itself looks "
        "evasive to a bidder and can escalate a resolvable query into a formal challenge.",
        "Separate the accountability question from the debrief-drafting process — have someone without "
        "personal exposure review what is being sent, so the response is judged on its own merits rather "
        "than shaped by who might be blamed.",
    ),
    (
        "procurement_resource", "limited",
        "Organisational Complexity and Political Sensitivity", "medium", "known",
        "Authorities with limited procurement or legal resource may struggle to respond to a query "
        "effectively or on time, which itself increases the chance a resolvable query escalates.",
        "Flag this procurement for early legal/procurement support specifically at debrief stage, before "
        "the standstill clock is running.",
    ),
    (
        "political_sensitivity", "high",
        "Organisational Complexity and Political Sensitivity", "low", "known",
        "A high-profile contract carries political and reputational stakes that raise the cost of a "
        "challenge without necessarily changing its likelihood — a severity multiplier on consequence, "
        "not a driver of probability.",
        "Ensure senior stakeholders are briefed on the risk profile before the debrief goes out, not after "
        "a challenge is raised.",
    ),
    (
        "third_party_involved", True,
        "3rd Parties", "low", "known",
        "A third-party consultant or advisor involved in the process is motivated to protect their own "
        "organisation from liability, which can complicate a coordinated, consistent response to a query.",
        "Confirm in advance who owns the debrief response if a third party was involved in the evaluation.",
    ),
]

_BIDDER_RULES = [
    (
        "score_margin", "narrow",
        "Margin of Competition", "high", "known",
        "The closer the scores between bidders, the greater the perceived likelihood of a successful "
        "challenge — a narrow margin reinforces the losing bidder's belief that errors or inconsistencies "
        "affected the outcome.",
        "A narrow margin is exactly the case that most needs a clear, specific debrief — invest "
        "disproportionate care in explaining precisely why the margin favoured the winner.",
    ),
    (
        "feedback_quality_received", "minimal",
        "Quality of the Procurement Process and Feedback", "high", "known",
        "Bidders are more inclined to dispute outcomes where the CA cannot demonstrate the evaluation "
        "criteria were applied consistently, or where feedback is clear gaps, inconsistencies or poorly "
        "articulated — this is the single most controllable factor in this whole assessment, since the CA "
        "decides what goes in the debrief.",
        "Rewrite the debrief before sending: name the specific criterion, the specific gap in the losing "
        "bid relative to the published descriptors, and the specific strength in the winning bid. Vague "
        "language here is the most preventable driver of a challenge in this entire list.",
    ),
    (
        "feedback_quality_received", "adequate",
        "Quality of the Procurement Process and Feedback", "low", "known",
        "Feedback that covers the basics but leaves questions open gives a losing bidder room to seek "
        "clarification informally before considering a formal challenge.",
        "Anticipate the obvious follow-up question and pre-empt it in the debrief.",
    ),
    (
        "legal_representation", "full",
        "Legal Representation", "medium", "estimated",
        "A bidder with legal representation typically opens with a standard disclosure request, which "
        "raises the likelihood a query becomes a formal, documented process rather than an informal one.",
        "If the losing bidder is known to retain legal counsel, prepare the disclosure pack proactively "
        "rather than reactively.",
    ),
    (
        "revenue_dependence", "high",
        "Financial and Commercial Incentive", "medium", "estimated",
        "Where this contract represents a significant proportion of the bidder's turnover, the financial "
        "incentive to challenge is correspondingly higher.",
        "No pre-award mitigation changes the bidder's stakes — but this raises the priority of getting the "
        "debrief right for this specific bidder.",
    ),
    (
        "relationship_with_winner", "strained",
        "Relationship with the Winning Bidder", "medium", "estimated",
        "A strained, highly competitive relationship with the winning bidder, including disbelief that the "
        "winner is genuinely superior, is an independent driver of challenge motivation separate from the "
        "merits of the evaluation itself.",
        "Where this history is known, the debrief should be written expecting scrutiny specifically "
        "comparing the two bids' relative merits.",
    ),
    (
        "relationship_with_ca", "weak",
        "Relationship Risk with the Contracting Authority", "low", "estimated",
        "Where the relationship with this authority is already weak, the usual deterrent — reluctance to "
        "be seen as difficult for future opportunities — carries less weight.",
        "No specific pre-award mitigation; factor into how much benefit-of-the-doubt to expect.",
    ),
    (
        "organisation_size", "large",
        "Organisational Size and Capability", "low", "known",
        "Larger organisations are generally more willing and able to pursue a challenge, given greater "
        "resources and access to legal support.",
        "No specific pre-award mitigation; factor into response-time planning.",
    ),
    (
        "incumbent", True,
        "Financial and Commercial Incentive", "medium", "known",
        "An incumbent losing bidder has typically built a business plan around retention, and the loss "
        "carries additional financial, operational and reputational weight beyond an ordinary competitor.",
        "Give particular care to explaining continuity/transition points in the debrief, since an incumbent "
        "is uniquely positioned to spot operational inconsistencies in the evaluation.",
    ),
]


def _collect_flags(profile: BaseModel | None, rules: list[tuple]) -> list[RiskFlag]:
    if profile is None:
        return []
    flags = []
    for field, trigger_value, category, severity, confidence, rationale, mitigation in rules:
        value = getattr(profile, field, None)
        if value is not None and value == trigger_value:
            flags.append(RiskFlag(
                category=category, field=f"{field}={trigger_value!r}", severity=severity,
                confidence=confidence, rationale=rationale, mitigation=mitigation,
            ))
    return flags


def assess_challenge_risk(
    ca_profile: CAProfile | None,
    bidder_profile: BidderProfile | None = None,
) -> ChallengeRiskAssessment:
    """
    Scores challenge-raising risk from Doc 1's practical-consideration factors.

    `ca_profile` should reflect the ACTUAL circumstances of this procurement, including the debrief
    you are about to send (`feedback_quality_received` lives on BidderProfile but is really describing
    your own draft — fill it in honestly, not aspirationally). `bidder_profile` is optional; omit fields
    you don't actually know rather than guessing, since a fabricated "known" input is worse than no input —
    see the module docstring's confidence distinction.
    """
    flags = _collect_flags(ca_profile, _CA_RULES) + _collect_flags(bidder_profile, _BIDDER_RULES)

    if not flags:
        return ChallengeRiskAssessment(
            overall_risk_band="low", risk_score=0.0, flags=[],
            summary="No Doc 1 risk factors flagged from the supplied profile fields. This reflects only "
                    "the fields that were actually populated — an unpopulated CAProfile/BidderProfile "
                    "will always score as low risk, which is a gap in the input, not a finding.",
        )

    raw = sum(_SEVERITY_WEIGHT[f.severity] for f in flags)
    # Normalise against the maximum score a single real profile could reach — the highest-severity
    # variant PER FIELD, summed across distinct fields. Summing every rule regardless of field would
    # double-count mutually exclusive alternatives (documentation_quality can be 'weak' OR 'partial',
    # never both), inflating the ceiling past what any real profile can hit and silently suppressing
    # every score below it.
    max_by_field: dict[str, float] = {}
    for field, _trigger, _cat, severity, *_ in _CA_RULES + _BIDDER_RULES:
        max_by_field[field] = max(max_by_field.get(field, 0.0), _SEVERITY_WEIGHT[severity])
    max_possible = sum(max_by_field.values())
    score = round(min(raw / max_possible, 1.0), 4)

    band: Literal["low", "medium", "high"]
    if score >= 0.35:
        band = "high"
    elif score >= 0.15:
        band = "medium"
    else:
        band = "low"

    high_sev = [f for f in flags if f.severity == "high"]
    known_high = [f for f in high_sev if f.confidence == "known"]
    summary_bits = [f"{len(flags)} risk factor(s) flagged ({len(high_sev)} high-severity)."]
    if known_high:
        summary_bits.append(
            "Highest-priority, CA-verifiable factors: " + "; ".join(f.field for f in known_high) + "."
        )
    # A single strong factor rarely clears "medium"/"high" band on its own — the band is an aggregate
    # across the whole profile, by design. Read `flags` regardless of band: a lone high-severity flag
    # (e.g. a narrow score margin) is still the specific, actionable signal, even inside a "low" band.
    if high_sev and band == "low":
        summary_bits.append(
            f"Note: {len(high_sev)} high-severity flag(s) present despite the overall 'low' band — "
            "band is an aggregate, not a substitute for reading the individual flags below."
        )
    summary_bits.append(
        "Risk band and score are an ordering device from a documented, unvalidated heuristic (see module "
        "docstring) — treat as triage, not as a calibrated probability of a challenge being raised."
    )

    return ChallengeRiskAssessment(
        overall_risk_band=band, risk_score=score, flags=flags, summary=" ".join(summary_bits),
    )
