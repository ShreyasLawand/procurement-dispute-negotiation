from src.utils.compliance_metrics import parse_llm_json, metrics
from langchain_ollama import ChatOllama
from src.schemas.agent_state import ComplianceAssessment, DisputeScenario
from src.prompts.zeroshot_prompt import ZEROSHOT_SYSTEM_PROMPT


class ZeroShotAgent:
    """
    Single-LLM zero-shot baseline (evaluation item 22) — one call, no negotiation,
    no multi-agent structure. See zeroshot_prompt.py for why this is deliberately not
    hardened the way CourtAgent is. Same temperature as CourtAgent (0.2) so any
    behavioural difference reflects the architecture, not a sampling-temperature
    confound.
    """

    def __init__(self):
        self.llm = ChatOllama(model="llama3.1", temperature=0.2, format="json")

    def assess(self, scenario: DisputeScenario) -> ComplianceAssessment:
        user_message = f"""
DISPUTE: {scenario.title}
Contract Value: £{scenario.contract_value_gbp:,.0f}
Dispute Type: {scenario.dispute_type}
Procedural Stage: {scenario.procedural_stage}
Contracting Authority: {scenario.contracting_authority_name}
Bidder: {scenario.bidder_name}

FACTS:
{scenario.description}
"""

        messages = [
            ("system", ZEROSHOT_SYSTEM_PROMPT),
            ("user", user_message),
        ]

        response = self.llm.invoke(messages)
        raw_text = response.content.strip()

        data = parse_llm_json(raw_text, agent="ZeroShotAgent", call="assess")
        data["round_number"] = 1
        return ComplianceAssessment(**data)
