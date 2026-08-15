from pydantic import BaseModel
from src.schemas.agent_state import BidderProfile, CAProfile, DisputeScenario
from src.recommendation.settlement_recommendation import SettlementRecommendation
from src.risk.challenge_risk import ChallengeRiskAssessment


class StartNegotiationRequest(BaseModel):
    scenario: DisputeScenario
    max_rounds: int = 3


class StartNegotiationResponse(BaseModel):
    session_id: str


class ExtractResponse(BaseModel):
    scenario: DisputeScenario


class RiskAssessmentRequest(BaseModel):
    """Both profiles optional/partial — an unset field is 'not screened for', not 'low risk'.
    See src/risk/challenge_risk.py's module docstring before changing this endpoint's behaviour."""
    ca_profile: CAProfile | None = None
    bidder_profile: BidderProfile | None = None


class RiskAssessmentResponse(BaseModel):
    assessment: ChallengeRiskAssessment


class RecommendationResponse(BaseModel):
    recommendation: SettlementRecommendation


class BatchListEntry(BaseModel):
    """One completed batch available for a recommendation — enough for a picker UI."""
    batch_id: str
    scenario_id: str
    scenario_title: str
    court_prompt_version: str | None
    n_runs: int
