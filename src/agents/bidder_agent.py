import json
from langchain_ollama import ChatOllama
from src.schemas.agent_state import PreNegotiationStatement, DisputeScenario, AgentRole
from src.prompts.bidder_prompt import BIDDER_SYSTEM_PROMPT

class AggrievedBidderAgent:

    def __init__(self):
        self.llm = ChatOllama(model="llama3.1", temperature=0.4, format="json")
        self.role = AgentRole.AGGRIEVED_BIDDER

    def build_scenario_context(self, scenario: DisputeScenario) -> str:
        return f"""
DISPUTE DETAILS:
- Dispute ID: {scenario.dispute_id}
- Title: {scenario.title}
- Contract Value: £{scenario.contract_value_gbp:,.0f}
- Dispute Type: {scenario.dispute_type}
- Procedural Stage: {scenario.procedural_stage}
- Contracting Authority: {scenario.contracting_authority_name}
- Your Organisation: {scenario.bidder_name}

DISPUTE DESCRIPTION:
{scenario.description}
"""

    def get_pre_negotiation_statement(self, scenario: DisputeScenario) -> PreNegotiationStatement:
        scenario_context = self.build_scenario_context(scenario)

        user_message = f"""
{scenario_context}

You are now entering pre-negotiation. Based on this dispute, provide your 
pre-negotiation statement as a JSON object. Be specific to this scenario.

Respond ONLY with valid JSON, no other text.
"""

        messages = [
            ("system", BIDDER_SYSTEM_PROMPT),
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

        return PreNegotiationStatement(**data)

    def respond_to_round(self, scenario: DisputeScenario, conversation_history: list, round_number: int) -> str:
        scenario_context = self.build_scenario_context(scenario)

        messages = [("system", BIDDER_SYSTEM_PROMPT)]
        messages.append(("user", f"{scenario_context}\n\nNegotiation Round {round_number}. Respond to the Contracting Authority's most recent message. Keep it concise (2-3 paragraphs), assertive but professional, citing specific evidence."))

        for role, content in conversation_history:
            messages.append((role, content))

        # Use non-JSON mode for free-text negotiation responses
        free_llm = ChatOllama(model="llama3.1", temperature=0.4)
        response = free_llm.invoke(messages)
        return response.content.strip()