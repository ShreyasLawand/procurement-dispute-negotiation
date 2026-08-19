"""
Tests for negotiation_helpers.is_disclosure_dispute() — the deterministic classifier
CourtAgent.assess_round() uses to pick between the merits-branch prompt (unchanged)
and the new disclosure-branch prompt (Phase 3, real-case-test-findings.md). Pure
function, no LLM calls, no network.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.schemas.agent_state import DisputeScenario
from src.utils.negotiation_helpers import is_disclosure_dispute


def _scenario(procedural_stage: str, dispute_type: str = "scoring_challenge") -> DisputeScenario:
    return DisputeScenario(
        dispute_id="TEST-001",
        title="Test v Test",
        description="A test dispute.",
        contract_value_gbp=None,
        dispute_type=dispute_type,
        procedural_stage=procedural_stage,
        contracting_authority_name="Test Authority",
        bidder_name="Test Bidder",
    )


def test_interim_application_is_a_disclosure_dispute():
    # The real classification result for both cases in real-case-test-findings.md.
    assert is_disclosure_dispute(_scenario("interim_application", "scoring_challenge")) is True
    assert is_disclosure_dispute(_scenario("interim_application", "transparency_breach")) is True


def test_disclosure_application_is_a_disclosure_dispute():
    assert is_disclosure_dispute(_scenario("disclosure_application")) is True


def test_disclosure_dispute_type_alone_is_a_disclosure_dispute():
    assert is_disclosure_dispute(_scenario("standstill", "disclosure_application")) is True


def test_trial_is_not_a_disclosure_dispute():
    assert is_disclosure_dispute(_scenario("trial")) is False


def test_standstill_is_not_a_disclosure_dispute():
    assert is_disclosure_dispute(_scenario("standstill")) is False


def test_automatic_suspension_is_not_a_disclosure_dispute():
    assert is_disclosure_dispute(_scenario("automatic_suspension")) is False


def test_appeal_is_not_a_disclosure_dispute():
    assert is_disclosure_dispute(_scenario("appeal")) is False


def test_classification_is_case_insensitive():
    assert is_disclosure_dispute(_scenario("Interim_Application")) is True


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
