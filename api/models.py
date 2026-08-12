from pydantic import BaseModel
from src.schemas.agent_state import DisputeScenario


class StartNegotiationRequest(BaseModel):
    scenario: DisputeScenario
    max_rounds: int = 3


class StartNegotiationResponse(BaseModel):
    session_id: str


class ExtractResponse(BaseModel):
    scenario: DisputeScenario
