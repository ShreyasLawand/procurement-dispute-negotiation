from difflib import SequenceMatcher
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.schemas.agent_state import DisputeScenario

# Keywords identifying a disclosure/procedural dispute (a CPR 31.12 application for
# early specific disclosure, assessed under Roche Diagnostics principles) rather than
# a merits/scoring dispute (assessed under the Court agent's Step 1/2A/2B manifest-
# error review). Both real cases in real-case-test-findings.md extracted
# procedural_stage="interim_application" - dispute_type stayed a scoring/transparency
# label in both, since that describes the underlying grievance, not the procedural
# question actually before the court - so procedural_stage is the reliable signal.
_DISCLOSURE_KEYWORDS = ("disclosure", "interim_application", "interim application")


def is_disclosure_dispute(scenario: "DisputeScenario") -> bool:
    """
    Classifies a scenario as a disclosure/procedural dispute vs. a merits/scoring
    dispute. Deterministic and rule-based rather than a separate LLM call - both real
    cases that exposed the Court agent's "only knows how to assess merits disputes"
    gap were correctly identifiable from their own already-extracted
    procedural_stage, so no new model call (and no new fabrication surface) was
    needed to classify them. See CourtAgent.assess_round(), which picks the
    disclosure-branch prompt when this returns True and leaves the existing
    merits-branch prompt (V3/V4) completely untouched otherwise.
    """
    haystack = f"{scenario.procedural_stage} {scenario.dispute_type}".lower()
    return any(kw in haystack for kw in _DISCLOSURE_KEYWORDS)


def format_contract_value(value: Optional[float]) -> str:
    """
    Renders a scenario's contract_value_gbp for inclusion in an agent prompt.
    None means "not stated in the source document" - a genuinely different fact
    from "the contract is worth £0" - so it must render as plainly unknown, not
    silently become "£0" (which reads to the model as a real fact about the case
    and gets treated as ground truth by downstream reasoning). See
    real-case-test-findings.md, bug #1/#2.
    """
    if value is None:
        return "Not stated in the source documents"
    return f"£{value:,.0f}"


def similarity(a: str, b: str) -> float:
    """Returns a 0-1 similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()


def is_repetitive(new_message: str, previous_messages: List[str], threshold: float = 0.72) -> bool:
    """Checks if new_message is too similar to any prior message from the same speaker."""
    for prev in previous_messages:
        if similarity(new_message, prev) > threshold:
            return True
    return False


def format_previous_statements(previous_messages: List[str]) -> str:
    """Formats an agent's own prior statements for inclusion in the prompt, so it can see and avoid repeating them."""
    if not previous_messages:
        return "(This is your first statement in the negotiation.)"
    formatted = []
    for i, msg in enumerate(previous_messages, 1):
        formatted.append(f"Statement {i}: {msg}")
    return "\n".join(formatted)


def get_round_stage_instruction(round_number: int, max_rounds: int) -> str:
    """
    Returns stage-specific guidance so agents behave differently depending on
    where they are in the negotiation arc, rather than repeating a generic
    'respond to the last message' instruction every round.
    """
    if round_number == 1:
        return (
            "This is the FIRST substantive exchange after opening positions. "
            "Engage directly with the other party's opening position — ask a "
            "clarifying question, challenge a specific claim, or make an initial "
            "offer of transparency or information."
        )
    elif round_number == max_rounds:
        return (
            "This is the FINAL round before deadlock. You must do ONE of the "
            "following: (1) offer a concrete resolution proposal that could end "
            "the dispute, (2) make a genuine final concession to try to break "
            "deadlock, or (3) clearly state that you cannot move further and "
            "that you are prepared to proceed to formal proceedings. Do not "
            "simply repeat an earlier position."
        )
    else:
        return (
            "This is a MIDDLE round. You must directly address the SPECIFIC "
            "point the other party raised in their most recent message. You "
            "must do at least one of: offer a new concession you have not "
            "offered before, ask a new question you have not asked before, or "
            "narrow the disagreement in some concrete way. Do not restate an "
            "argument you have already made in an earlier round."
        )