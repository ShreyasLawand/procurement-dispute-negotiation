from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class AgentRole(str, Enum):
    CONTRACTING_AUTHORITY = "contracting_authority"
    AGGRIEVED_BIDDER = "aggrieved_bidder"
    COURT = "court"

class DisputeScenario(BaseModel):
    dispute_id: str
    title: str
    description: str
    contract_value_gbp: float
    dispute_type: str
    procedural_stage: str
    contracting_authority_name: str
    bidder_name: str

class PreNegotiationStatement(BaseModel):
    role: AgentRole
    interests: List[str]
    goals: List[str]
    batna: str
    opening_position: str
    legal_basis: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)

class NegotiationMessage(BaseModel):
    round_number: int
    sender_role: AgentRole
    message: str
    proposal: Optional[str] = None
    concession_made: Optional[str] = None

class ComplianceAssessment(BaseModel):
    """Court agent's output — focused on legal compliance, not balancing sympathies"""
    round_number: int
    process_followed: bool
    manifest_error_found: bool
    applicable_provisions: List[str]
    reasoning: str
    recommended_action: str  # e.g. "continue negotiation", "re-evaluation", "no remedy - decision stands", "damages"
    deadlock: bool = False

class NegotiationState(BaseModel):
    scenario: DisputeScenario
    round_number: int = 0
    max_rounds: int = 5
    ca_pre_negotiation: Optional[PreNegotiationStatement] = None
    bidder_pre_negotiation: Optional[PreNegotiationStatement] = None
    messages: List[NegotiationMessage] = []
    compliance_checks: List[ComplianceAssessment] = []
    resolved: bool = False
    resolution_outcome: Optional[str] = None
    adjudicated: bool = False
    ca_win_statement: Optional[str] = None
    bidder_win_statement: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        
class RoundResponse(BaseModel):
    """Structured response for a single negotiation round message"""
    message: str = Field(description="The agent's negotiation message this round, in plain prose")
    proposal: Optional[str] = Field(default=None, description="Specific proposal being made, if any")
    concession_made: Optional[str] = Field(default=None, description="Any concession offered this round, if any")