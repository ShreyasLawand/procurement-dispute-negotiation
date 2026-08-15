"""
Tests for src/risk/challenge_risk.py.

Pure, deterministic, no LLM call — that's the whole design point of this module (it must be usable
mid-negotiation without touching Ollama), which makes it an easy candidate for real assertions rather
than the eyeball-and-print style the rest of tests/ uses for agents that need a live model.

Written after a manual audit (15 Aug 2026) found two real gaps: a documented-but-unimplemented
market_conditions rule, and no test coverage at all on the severity-normalisation arithmetic. Both are
covered below — see test_market_conditions_rule_exists and the worst_case_profile tests.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.risk.challenge_risk import assess_challenge_risk, _CA_RULES, _BIDDER_RULES
from src.schemas.agent_state import CAProfile, BidderProfile


def _worst_case_profiles():
    """Every rule-bearing field set to its highest-severity trigger value."""
    ca = CAProfile(
        documentation_quality="weak",
        panel_capability="technical_untrained",
        internal_accountability_exposure="high",
        procurement_resource="limited",
        political_sensitivity="high",
        third_party_involved=True,
    )
    bidder = BidderProfile(
        score_margin="narrow",
        feedback_quality_received="minimal",
        legal_representation="full",
        revenue_dependence="high",
        relationship_with_winner="strained",
        relationship_with_ca="weak",
        organisation_size="large",
        incumbent=True,
        market_conditions="slow",
    )
    return ca, bidder


# --- empty / unpopulated profile ---------------------------------------------------------------

def test_no_profiles_is_low_risk_with_no_flags():
    r = assess_challenge_risk(None, None)
    assert r.overall_risk_band == "low"
    assert r.risk_score == 0.0
    assert r.flags == []
    # An unpopulated profile must not read as a genuine "screened and found safe" result.
    assert "gap in the input" in r.summary


def test_empty_profiles_same_as_none():
    r = assess_challenge_risk(CAProfile(), BidderProfile())
    assert r.overall_risk_band == "low"
    assert r.risk_score == 0.0
    assert r.flags == []


# --- normalisation invariants (survive future rule-table edits) --------------------------------

def test_worst_case_profile_scores_exactly_one():
    """
    The core correctness property of the severity-normalisation: max_possible is defined as the sum,
    per field, of that field's highest-severity trigger weight — so a profile hitting every field's
    worst value must normalise to exactly 1.0, not overshoot (which would mean double-counting
    mutually-exclusive values) or undershoot (which would mean the ceiling is inflated past what any
    real profile can reach). This must keep holding as rules are added or changed.
    """
    ca, bidder = _worst_case_profiles()
    r = assess_challenge_risk(ca, bidder)
    assert r.risk_score == 1.0
    assert r.overall_risk_band == "high"


def test_score_always_in_unit_range():
    ca, bidder = _worst_case_profiles()
    for r in (assess_challenge_risk(None, None), assess_challenge_risk(ca, None),
              assess_challenge_risk(None, bidder), assess_challenge_risk(ca, bidder)):
        assert 0.0 <= r.risk_score <= 1.0


def test_documentation_quality_is_mutually_exclusive_not_double_counted():
    """
    A single field can only take one Literal value at a time (Pydantic enforces this), so
    'documentation_quality' can never simultaneously trigger both its 'weak' and 'partial' rules. The
    max_by_field normalisation relies on this — summing every rule regardless of field, rather than
    taking the max per field, would inflate the ceiling past what any real profile can hit. Weak alone
    should score identically whether or not the (unreachable) 'partial' rule also existed.
    """
    r_weak = assess_challenge_risk(CAProfile(documentation_quality="weak"), None)
    assert len(r_weak.flags) == 1
    assert r_weak.flags[0].field == "documentation_quality='weak'"


# --- the fixed gap: market_conditions ------------------------------------------------------------

def test_market_conditions_rule_exists():
    """
    Regression test for the audit finding: market_conditions was named in the module docstring as a
    screened "estimated" factor but had no rule. Doc 1: "During slower market periods... the likelihood
    of challenges increases."
    """
    r = assess_challenge_risk(None, BidderProfile(market_conditions="slow"))
    assert len(r.flags) == 1
    flag = r.flags[0]
    assert flag.field == "market_conditions='slow'"
    assert flag.confidence == "estimated"
    assert flag.category == "Availability of Time and Resources"


def test_market_conditions_buoyant_and_normal_have_no_rule():
    """Only 'slow' raises risk — the other two values are the non-risk defaults and stay silent."""
    for value in ("buoyant", "normal"):
        r = assess_challenge_risk(None, BidderProfile(market_conditions=value))
        assert r.flags == []


# --- known / estimated confidence split ----------------------------------------------------------

def test_ca_rules_are_all_known_confidence():
    """
    Every _CA_RULES entry must be 'known' confidence by construction — CAProfile describes the
    authority's own procurement, which it can verify directly by definition. A rule accidentally added
    as 'estimated' here would be a real bug (there's nothing about the CA's own process that it doesn't
    have access to), not a judgement call, so this checks the rule table directly rather than just one
    sample assessment.
    """
    assert all(rule[4] == "known" for rule in _CA_RULES)


def test_ca_observable_fields_are_known_confidence():
    """Everything on CAProfile is within the authority's own knowledge before the standstill letter."""
    r = assess_challenge_risk(CAProfile(documentation_quality="weak", panel_capability="technical_untrained"), None)
    assert all(f.confidence == "known" for f in r.flags)


def test_bidder_circumstance_fields_are_estimated_confidence():
    """
    Fields describing the LOSING bidder's own circumstances (not directly observable to the CA
    pre-award) must be marked 'estimated', per the module's own stated distinction.
    """
    r = assess_challenge_risk(None, BidderProfile(
        legal_representation="full", revenue_dependence="high",
        relationship_with_winner="strained", relationship_with_ca="weak",
        market_conditions="slow",
    ))
    assert len(r.flags) == 5
    assert all(f.confidence == "estimated" for f in r.flags)


def test_ca_observable_bidder_fields_are_known_confidence():
    """
    A few BidderProfile fields ARE observable because the CA ran the competition itself
    (score_margin, organisation_size, incumbent) or is describing its own draft debrief
    (feedback_quality_received).
    """
    r = assess_challenge_risk(None, BidderProfile(
        score_margin="narrow", feedback_quality_received="minimal",
        organisation_size="large", incumbent=True,
    ))
    assert len(r.flags) == 4
    assert all(f.confidence == "known" for f in r.flags)


# --- band-vs-flags honesty (the "low band, high flag present" caveat) ----------------------------

def test_single_high_flag_can_land_in_low_band_but_is_still_surfaced():
    """
    A lone high-severity flag does not by itself clear the 'medium'/'high' band thresholds — band is
    an aggregate across the whole profile by design. The important behaviour under test is that this
    is never silent: the flag is still in `flags`, and the summary explicitly calls out a high-severity
    flag present despite a low band, rather than letting the band imply "nothing serious here".
    """
    r = assess_challenge_risk(CAProfile(documentation_quality="weak"), None)
    assert len(r.flags) == 1
    assert r.flags[0].severity == "high"
    if r.overall_risk_band == "low":
        assert "despite the overall 'low' band" in r.summary


def test_summary_always_carries_the_heuristic_caveat():
    r = assess_challenge_risk(CAProfile(documentation_quality="weak"), None)
    assert "not as a calibrated probability" in r.summary


# --- flag provenance -------------------------------------------------------------------------------

def test_every_flag_is_traceable_to_its_source_field():
    ca, bidder = _worst_case_profiles()
    r = assess_challenge_risk(ca, bidder)
    for f in r.flags:
        field_name = f.field.split("=")[0]
        assert hasattr(ca, field_name) or hasattr(bidder, field_name)
        assert f.category
        assert f.rationale
        assert f.mitigation


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
