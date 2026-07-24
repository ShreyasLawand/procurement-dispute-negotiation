from typing import TypedDict, Optional, List, Tuple
from src.schemas.agent_state import (
    DisputeScenario, PreNegotiationStatement, NegotiationMessage,
    ComplianceAssessment, NegotiationSummary
)


class GraphState(TypedDict):
    """
    LangGraph state — a TypedDict rather than the Pydantic NegotiationState,
    since LangGraph's StateGraph works most reliably with TypedDict schemas.
    We convert to/from the Pydantic NegotiationState when saving the final log.
    """
    scenario: DisputeScenario
    round_number: int
    max_rounds: int

    ca_pre_negotiation: Optional[PreNegotiationStatement]
    bidder_pre_negotiation: Optional[PreNegotiationStatement]

    ca_history: List[Tuple[str, str]]
    bidder_history: List[Tuple[str, str]]

    messages: List[NegotiationMessage]
    compliance_checks: List[ComplianceAssessment]

    last_ca_msg: Optional[str]
    last_bidder_msg: Optional[str]

    resolved: bool
    resolution_outcome: Optional[str]
    adjudicated: bool

    summary: Optional[NegotiationSummary]