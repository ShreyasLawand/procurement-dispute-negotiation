from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from enum import Enum
import json

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
    ca_win_statement: Optional["WinStatement"] = None
    bidder_win_statement: Optional["WinStatement"] = None
    summary: Optional["NegotiationSummary"] = None

    class Config:
        arbitrary_types_allowed = True
        
class RoundResponse(BaseModel):
    """Structured response for a single negotiation round message"""
    message: str = Field(description="The agent's negotiation message this round, in plain prose")
    proposal: Optional[str] = Field(default=None, description="Specific proposal being made, if any")
    concession_made: Optional[str] = Field(default=None, description="Any concession offered this round, if any")

    @field_validator("proposal", "concession_made", mode="before")
    @classmethod
    def coerce_to_string(cls, v: Any) -> Optional[str]:
        """
        Llama 3.1 sometimes returns a dict or bool here instead of a plain
        string, despite instructions. Normalise anything non-string into a
        readable string rather than crashing validation.
        """
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, dict):
            # Convert dict into a readable "key: value" string
            return "; ".join(f"{k}: {val}" for k, val in v.items())
        if isinstance(v, bool):
            return "Yes" if v else None
        # Fallback for any other type (list, number, etc.)
        return str(v)

    @field_validator("message", mode="before")
    @classmethod
    def coerce_message_to_string(cls, v: Any) -> str:
        """Same safety net for the message field itself, just in case."""
        if isinstance(v, str):
            return v
        if isinstance(v, dict):
            return json.dumps(v)
        return str(v)
    
class NegotiationSummary(BaseModel):
    """Post-negotiation reasoning summary — explains the 'why' behind the outcome"""
    key_sticking_points: List[str] = Field(description="The core disagreements that drove the negotiation")
    concessions_summary: str = Field(description="Plain-English summary of what each side offered")
    court_reasoning_summary: str = Field(description="Why the Court reached its final recommendation")
    likely_next_steps: str = Field(description="What would realistically happen next if this were a real dispute")
    plain_english_summary: str = Field(description="A 3-4 sentence summary a non-lawyer could understand")
    
class WinStatement(BaseModel):
    """Post-negotiation reflection — how this agent frames its outcome as a 'win'"""
    role: AgentRole
    outcome_relative_to_batna: str = Field(description="Did this outcome beat, match, or fall short of the agent's BATNA?")
    win_statement: str = Field(description="How this agent frames the outcome as a win, in its own voice")
    what_was_achieved: List[str] = Field(description="Specific interests or goals that were satisfied")
    what_was_conceded: List[str] = Field(description="What this agent had to give up or compromise on")