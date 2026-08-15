from src.utils.compliance_metrics import parse_llm_json, metrics
from langchain_ollama import ChatOllama
from src.schemas.agent_state import ComplianceAssessment, DisputeScenario
from src.prompts.court_prompt import COURT_SYSTEM_PROMPT


class CourtAgent:

    def __init__(self, system_prompt: str | None = None):
        self.llm = ChatOllama(model="llama3.1", temperature=0.2, format="json")
        # Defaults to the active COURT_SYSTEM_PROMPT (V4). Passing V3 explicitly is how
        # the V3/V4 ablation is run without mutating module state, which would otherwise
        # leak between batches in the same process.
        self.system_prompt = system_prompt or COURT_SYSTEM_PROMPT

    def assess_round(self, scenario: DisputeScenario, ca_message: str, bidder_message: str, round_number: int) -> ComplianceAssessment:
        user_message = f"""
FULL DISPUTE SCENARIO (contains the ground-truth facts you must verify against):
Title: {scenario.title}
Contract Value: £{scenario.contract_value_gbp:,.0f}
Description:
{scenario.description}

---

ROUND {round_number}

CONTRACTING AUTHORITY'S POSITION THIS ROUND:
{ca_message}

AGGRIEVED BIDDER'S POSITION THIS ROUND:
{bidder_message}

---

Before reaching your conclusion: if the scenario description above contains 
any formula, sub-scores, or numbers, perform the calculation yourself now 
and check it against any score, ranking, or outcome mentioned in the 
scenario or in either party's statements. Show this working in your 
"reasoning" field. Then assess legal compliance based on your own 
independent finding, not on what either party claims.

Set "round_number" to {round_number} in your response.
"""

        messages = [
            ("system", self.system_prompt),
            ("user", user_message)
        ]

        response = self.llm.invoke(messages)
        raw_text = response.content.strip()

        data = parse_llm_json(raw_text, agent="CourtAgent", call="assess_round")

        data["round_number"] = round_number
        return ComplianceAssessment(**data)