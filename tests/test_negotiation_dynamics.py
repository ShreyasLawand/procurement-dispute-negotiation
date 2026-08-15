"""
Tests for scripts/analyze_negotiation_dynamics.py, focused on the two bugs caught while building it:
'withdraw our claim/request/objection' (a settlement offer — a large concession) being conflated with
'withdraw our offer/concession/proposal' (an actual retraction), and an inconsistent whitespace gap
between the optional adjective and the noun it modifies in the same regex group.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from analyze_negotiation_dynamics import _RETRACTION_LANGUAGE


def _matches(text: str) -> bool:
    return bool(_RETRACTION_LANGUAGE.search(text))


# --- regression tests for the caught false positives: "withdraw our claim/request/objection" ---------

def test_withdrawing_a_claim_is_not_a_retraction():
    """
    'We are willing to withdraw our claim' is a settlement offer (dropping the whole dispute) — a large
    concession, the opposite of a retraction. An earlier version of _RETRACTION_LANGUAGE matched bare
    'withdraw' and flagged this as a retraction suspect across 4 real corpus messages before this fix.
    Caught by reading each flag's actual trigger context, not by inspection.
    """
    assert _matches("we are willing to withdraw our claim and allow the independent reviewer to decide") is False


def test_withdrawing_a_request_is_not_a_retraction():
    assert _matches("we are willing to withdraw our request for an independent review") is False


def test_withdrawing_an_objection_is_not_a_retraction():
    assert _matches("we are willing to withdraw our objection to the written summary") is False


def test_withdrawing_a_challenge_is_not_a_retraction():
    assert _matches("in exchange, we would withdraw our challenge entirely") is False


# --- regression test for the whitespace gap bug -------------------------------------------------------

def test_withdrawing_an_adjective_qualified_offer_is_caught():
    """
    Regression test: 'our earlier offer' (adjective before noun, no explicit space token in the
    adjective alternative) was silently missed by an earlier version of the pattern because the
    'earlier'/'previous' alternatives had no \\s* before the noun group, while the 'prior' alternative
    (which embedded its own trailing \\s+) happened to work — an inconsistency invisible without testing
    text using each of the three adjectives.
    """
    assert _matches("We withdraw our earlier offer of a partial re-evaluation.") is True
    assert _matches("We withdraw our previous concession.") is True
    assert _matches("We withdraw our prior proposal.") is True


def test_withdrawing_an_offer_with_no_adjective_is_caught():
    assert _matches("We withdraw our offer.") is True


# --- true positives that must still be caught ---------------------------------------------------------

def test_no_longer_stand_by_previous_proposal_is_caught():
    assert _matches("We no longer stand by our previous proposal.") is True


def test_reconsidering_previous_position_is_caught():
    assert _matches("We are willing to reconsider our previous position.") is True


# --- true negatives ------------------------------------------------------------------------------------

def test_refusing_to_concede_is_not_a_retraction():
    """Declining a NEW concession is not retracting an EARLIER one."""
    assert _matches("We will not concede on this point.") is False


def test_standing_by_original_position_is_not_a_retraction():
    assert _matches("We stand by our evaluation.") is False


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
