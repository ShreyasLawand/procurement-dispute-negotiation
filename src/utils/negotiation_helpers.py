from difflib import SequenceMatcher
from typing import List


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