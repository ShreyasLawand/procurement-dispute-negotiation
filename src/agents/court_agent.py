from src.utils.compliance_metrics import parse_llm_json, metrics
from langchain_ollama import ChatOllama
from src.schemas.agent_state import ComplianceAssessment, DisputeScenario
from src.prompts.court_prompt import COURT_SYSTEM_PROMPT, COURT_SYSTEM_PROMPT_DISCLOSURE
from src.utils.negotiation_helpers import format_contract_value, is_disclosure_dispute


class CourtAgent:

    def __init__(self, system_prompt: str | None = None):
        self.llm = ChatOllama(model="llama3.1", temperature=0.2, format="json")
        # Defaults to the active COURT_SYSTEM_PROMPT (V4). Passing V3 explicitly is how
        # the V3/V4 ablation is run without mutating module state, which would otherwise
        # leak between batches in the same process. Only applies to merits/scoring
        # disputes — a disclosure dispute always uses COURT_SYSTEM_PROMPT_DISCLOSURE
        # instead, regardless of this setting, since V3/V4 is an ablation on the
        # merits branch's interest taxonomy specifically and has no disclosure-branch
        # equivalent. See assess_round().
        self.system_prompt = system_prompt or COURT_SYSTEM_PROMPT

    def assess_round(self, scenario: DisputeScenario, ca_message: str, bidder_message: str, round_number: int) -> ComplianceAssessment:
        governing_legislation = scenario.governing_legislation or "Procurement Act 2023 (default — not otherwise stated in the source)"
        disclosure_dispute = is_disclosure_dispute(scenario)

        user_message = f"""
FULL DISPUTE SCENARIO (contains the ground-truth facts you must verify against):
Title: {scenario.title}
Contract Value: {format_contract_value(scenario.contract_value_gbp)}
Governing Legislation: {governing_legislation}
Description:
{scenario.description}

---

ROUND {round_number}

CONTRACTING AUTHORITY'S POSITION THIS ROUND:
{ca_message}

AGGRIEVED BIDDER'S POSITION THIS ROUND:
{bidder_message}

---
"""

        if disclosure_dispute:
            user_message += """
Before reaching your conclusion: assess the prima facie case, specificity,
proportionality, and confidentiality-safeguard questions set out in your
system prompt, using only what the scenario and the parties' statements
actually say. Do not assess manifest error or perform a scoring calculation
— that is not the question this application answers.
"""
        else:
            user_message += """
Before reaching your conclusion: if the scenario description above contains
any formula, sub-scores, or numbers, perform the calculation yourself now
and check it against any score, ranking, or outcome mentioned in the
scenario or in either party's statements. Show this working in your
"reasoning" field. Then assess legal compliance based on your own
independent finding, not on what either party claims.
"""

        user_message += f"""
Set "round_number" to {round_number} in your response.
"""

        active_system_prompt = COURT_SYSTEM_PROMPT_DISCLOSURE if disclosure_dispute else self.system_prompt

        messages = [
            ("system", active_system_prompt),
            ("user", user_message)
        ]

        response = self.llm.invoke(messages)
        raw_text = response.content.strip()

        data = parse_llm_json(raw_text, agent="CourtAgent", call="assess_round")

        data["round_number"] = round_number
        return ComplianceAssessment(**data)