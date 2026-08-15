from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional, List, Any, Literal
from enum import Enum
from src.utils.compliance_metrics import metrics
import json


def _prose_from_dict(d: dict) -> str:
    """
    Turns a stray structured proposal/concession object (which Llama 3.1
    sometimes returns despite instructions) into a short natural-language
    phrase instead of a raw "key: value; key2: value2" dump. Heuristic, not
    full NLG — the prompt-level fix in ca_prompt/bidder_prompt's round
    instruction is the primary mitigation; this is the backstop for when it
    doesn't fully land.
    """
    parts = []
    for k, val in d.items():
        label = k.replace("_", " ")
        if isinstance(val, bool):
            if val:
                parts.append(label)
            continue
        if isinstance(val, (int, float)) and "percentage" in k.lower():
            parts.append(f"{label} of {val:.0%}" if 0 <= val <= 1 else f"{label} of {val}")
        else:
            parts.append(f"{label}: {val}")
    return ", ".join(parts) if parts else str(d)


def _coerce_narrative_string(v: Any, model: str = "?", field: str = "?") -> str:
    """
    Shared defensive coercion for free-text narrative fields (opening
    positions, BATNAs, win statements, etc.). Llama 3.1 occasionally returns
    a structured object for a field the prompt explicitly asked to be a
    plain string — first caught on RoundResponse.proposal, then again on
    PreNegotiationStatement.opening_position with a different LLM call, so
    this is applied to every comparable narrative field rather than patched
    per-field as each one is individually hit.

    Every coercion is recorded (see src/utils/compliance_metrics.py). This used to
    repair silently, which made the model's real structural reliability invisible.
    """
    if isinstance(v, str):
        return v
    metrics.record_field_coercion(model, field, type(v))
    if isinstance(v, dict):
        return _prose_from_dict(v)
    return str(v)

class AgentRole(str, Enum):
    CONTRACTING_AUTHORITY = "contracting_authority"
    AGGRIEVED_BIDDER = "aggrieved_bidder"
    COURT = "court"

class CAProfile(BaseModel):
    """
    Case-specific behavioural modifiers for the Contracting Authority, taken from
    the "Practical Considerations that will impact upon the Contracting Authority's
    behaviour" table in Fusion21's *Key Drivers & Interests for Parties in a
    Procurement Dispute* (Doc 1).

    These are deliberately NOT baked into the CA system prompt: Doc 1 presents them
    as circumstances that vary case to case, and they are the axes we want to sweep
    experimentally. Every field defaults to None, meaning "unspecified" — an unset
    profile renders no prompt text at all, so existing scenarios and batch baselines
    behave exactly as before.
    """
    # Doc 1 — "Composition and Capability of the Evaluation Panel"
    panel_capability: Optional[Literal["procurement_trained", "mixed", "technical_untrained"]] = None
    # Doc 1 — "Risk of Internal Accountability or Disciplinary Action"
    internal_accountability_exposure: Optional[Literal["low", "medium", "high"]] = None
    # Doc 1 — "Approach to Bidder Feedback and Communication" (driven by confidence in the record)
    documentation_quality: Optional[Literal["robust", "partial", "weak"]] = None
    # Doc 1 — "Operational and Financial Pressures"
    service_criticality: Optional[Literal["routine", "important", "business_critical"]] = None
    # Doc 1 — "Organisational Complexity and Political Sensitivity"
    political_sensitivity: Optional[Literal["low", "medium", "high"]] = None
    procurement_resource: Optional[Literal["well_resourced", "limited"]] = None
    # Doc 1 — "3rd Parties"
    third_party_involved: Optional[bool] = None


class BidderProfile(BaseModel):
    """
    Case-specific behavioural modifiers for the Aggrieved Bidder, taken from the
    "Practical Considerations that will impact upon the Aggrieved (Unsuccessful)
    Bidder behaviour" table in Fusion21's Doc 1. Same defaulting rule as CAProfile.
    """
    # Doc 1 — "Legal Representation"
    legal_representation: Optional[Literal["none", "advisory", "full"]] = None
    # Doc 1 — "Financial and Commercial Incentive"
    revenue_dependence: Optional[Literal["low", "moderate", "high"]] = None
    # Doc 1 — "Margin of Competition"
    score_margin: Optional[Literal["narrow", "moderate", "wide"]] = None
    # Doc 1 — "Quality of the Procurement Process and Feedback"
    feedback_quality_received: Optional[Literal["detailed", "adequate", "minimal"]] = None
    # Doc 1 — "Relationship with the Winning Bidder"
    relationship_with_winner: Optional[Literal["neutral", "competitive", "strained"]] = None
    # Doc 1 — "Relationship Risk with the Contracting Authority"
    relationship_with_ca: Optional[Literal["strong", "neutral", "weak"]] = None
    # Doc 1 — "Availability of Time and Resources"
    market_conditions: Optional[Literal["buoyant", "normal", "slow"]] = None
    # Doc 1 — "Organisational Size and Capability"
    organisation_size: Optional[Literal["sme", "mid_market", "large"]] = None
    incumbent: Optional[bool] = None


class DisputeScenario(BaseModel):
    dispute_id: str
    title: str
    description: str
    contract_value_gbp: float
    dispute_type: str
    procedural_stage: str
    contracting_authority_name: str
    bidder_name: str

    # Doc 1 behavioural modifiers for this dispute. Both optional and defaulting to
    # None, so every existing scenario constructor keeps working untouched. Because
    # they live on the scenario, they are serialised into every saved negotiation log
    # by save_log() — which is what makes a profiled batch run reproducible after the
    # fact rather than only knowable from the script that launched it.
    ca_profile: Optional[CAProfile] = None
    bidder_profile: Optional[BidderProfile] = None

class PreNegotiationStatement(BaseModel):
    role: AgentRole
    interests: List[str]
    goals: List[str]
    batna: str
    opening_position: str
    legal_basis: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)

    @field_validator("batna", "opening_position", mode="before")
    @classmethod
    def coerce_narrative_fields(cls, v: Any, info: ValidationInfo) -> str:
        return _coerce_narrative_string(v, cls.__name__, info.field_name)

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
    applicable_provisions: List[str] = Field(default_factory=list)
    reasoning: str
    recommended_action: str  # e.g. "continue negotiation", "re-evaluation", "no remedy - decision stands", "damages"
    deadlock: bool = False

    @field_validator("reasoning", mode="before")
    @classmethod
    def coerce_narrative_fields(cls, v: Any, info: ValidationInfo) -> str:
        return _coerce_narrative_string(v, cls.__name__, info.field_name)

class NegotiationState(BaseModel):
    scenario: DisputeScenario
    round_number: int = 0
    max_rounds: int = 5
    ca_pre_negotiation: Optional[PreNegotiationStatement] = None
    bidder_pre_negotiation: Optional[PreNegotiationStatement] = None
    messages: List[NegotiationMessage] = Field(default_factory=list)
    compliance_checks: List[ComplianceAssessment] = Field(default_factory=list)
    resolved: bool = False
    resolution_outcome: Optional[str] = None
    adjudicated: bool = False
    ca_win_statement: Optional["WinStatement"] = None
    bidder_win_statement: Optional["WinStatement"] = None
    summary: Optional["NegotiationSummary"] = None

    model_config = {"arbitrary_types_allowed": True}
        
class RoundResponse(BaseModel):
    """Structured response for a single negotiation round message"""
    message: str = Field(description="The agent's negotiation message this round, in plain prose")
    proposal: Optional[str] = Field(default=None, description="Specific proposal being made, if any")
    concession_made: Optional[str] = Field(default=None, description="Any concession offered this round, if any")

    @field_validator("proposal", "concession_made", mode="before")
    @classmethod
    def coerce_to_string(cls, v: Any, info: ValidationInfo) -> Optional[str]:
        """
        Llama 3.1 sometimes returns a dict or bool here instead of a plain
        string, despite instructions. Normalise anything non-string into a
        readable string rather than crashing validation.
        """
        if v is None:
            return None
        if isinstance(v, str):
            return v
        metrics.record_field_coercion(cls.__name__, info.field_name, type(v))
        if isinstance(v, dict):
            return _prose_from_dict(v)
        if isinstance(v, bool):
            return "Yes" if v else None
        # Fallback for any other type (list, number, etc.)
        return str(v)

    @field_validator("message", mode="before")
    @classmethod
    def coerce_message_to_string(cls, v: Any, info: ValidationInfo) -> str:
        """Same safety net for the message field itself, just in case."""
        if isinstance(v, str):
            return v
        metrics.record_field_coercion(cls.__name__, info.field_name, type(v))
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

    @field_validator(
        "concessions_summary", "court_reasoning_summary", "likely_next_steps", "plain_english_summary", mode="before"
    )
    @classmethod
    def coerce_narrative_fields(cls, v: Any, info: ValidationInfo) -> str:
        return _coerce_narrative_string(v, cls.__name__, info.field_name)

class WinStatement(BaseModel):
    """Post-negotiation reflection — how this agent frames its outcome as a 'win'"""
    role: AgentRole
    outcome_relative_to_batna: str = Field(description="Did this outcome beat, match, or fall short of the agent's BATNA?")
    win_statement: str = Field(description="How this agent frames the outcome as a win, in its own voice")
    what_was_achieved: List[str] = Field(description="Specific interests or goals that were satisfied")
    what_was_conceded: List[str] = Field(description="What this agent had to give up or compromise on")

    @field_validator("outcome_relative_to_batna", "win_statement", mode="before")
    @classmethod
    def coerce_narrative_fields(cls, v: Any, info: ValidationInfo) -> str:
        return _coerce_narrative_string(v, cls.__name__, info.field_name)

NegotiationState.model_rebuild()