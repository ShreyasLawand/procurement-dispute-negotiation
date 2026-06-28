from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class AgentRole(str, Enum):
    CONTRACTING_AUTHORITY = "contracting_authority"
    AGGRIEVED_BIDDER = "aggrieved_bidder"
    COURT = "court"

class DisputeScenario(BaseModel):
    """Input: the dispute to be negotiated"""
    dispute_id: str
    title: str
    description: str
    contract_value_gbp: float
    dispute_type: str  # e.g. "scoring_challenge", "manifest_error", "transparency"
    procedural_stage: str  # e.g. "standstill", "pre-award", "post-award"
    contracting_authority_name: str
    bidder_name: str

class PreNegotiationStatement(BaseModel):
    """What each agent outputs BEFORE negotiation starts"""
    role: AgentRole
    interests: List[str] = Field(description="Core interests this agent is trying to protect")
    goals: List[str] = Field(description="What this agent wants to achieve from this dispute")
    batna: str = Field(description="Best Alternative To a Negotiated Agreement")
    opening_position: str = Field(description="Initial position stated at round 1")
    legal_basis: List[str] = Field(description="Legal provisions this agent relies on")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in position 0-1")

class NegotiationMessage(BaseModel):
    """A single message in a negotiation round"""
    round_number: int
    sender_role: AgentRole
    message: str
    proposal: Optional[str] = None
    concession_made: Optional[str] = None
    legal_compliance_flag: bool = True

class NegotiationState(BaseModel):
    """Full state of the negotiation — passed between LangGraph nodes"""
    scenario: DisputeScenario
    round_number: int = 0
    max_rounds: int = 5
    ca_pre_negotiation: Optional[PreNegotiationStatement] = None
    bidder_pre_negotiation: Optional[PreNegotiationStatement] = None
    messages: List[NegotiationMessage] = []
    resolved: bool = False
    resolution_outcome: Optional[str] = None
    adjudicated: bool = False
    ca_win_statement: Optional[str] = None
    bidder_win_statement: Optional[str] = None