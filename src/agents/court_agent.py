import json
from langchain_ollama import ChatOllama
from src.schemas.agent_state import ComplianceAssessment, DisputeScenario
from src.prompts.court_prompt import COURT_SYSTEM_PROMPT


class CourtAgent:

    def __init__(self):
        self.llm = ChatOllama(model="llama3.1", temperature=0.2, format="json")

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
            ("system", COURT_SYSTEM_PROMPT),
            ("user", user_message)
        ]

        response = self.llm.invoke(messages)
        raw_text = response.content.strip()

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            start = raw_text.find('{')
            end = raw_text.rfind('}') + 1
            data = json.loads(raw_text[start:end])

        data["round_number"] = round_number
        return ComplianceAssessment(**data)