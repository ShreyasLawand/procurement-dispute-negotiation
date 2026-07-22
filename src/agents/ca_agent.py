import json
from langchain_ollama import ChatOllama
from src.schemas.agent_state import PreNegotiationStatement, DisputeScenario, AgentRole, RoundResponse
from src.prompts.ca_prompt import CA_SYSTEM_PROMPT
from src.schemas.agent_state import PreNegotiationStatement, DisputeScenario, AgentRole, RoundResponse

class ContractingAuthorityAgent:
    
    def __init__(self):
        self.llm = ChatOllama(model="llama3.1", temperature=0.3)
        self.role = AgentRole.CONTRACTING_AUTHORITY

    def build_scenario_context(self, scenario: DisputeScenario) -> str:
        return f"""
DISPUTE DETAILS:
- Dispute ID: {scenario.dispute_id}
- Title: {scenario.title}
- Contract Value: £{scenario.contract_value_gbp:,.0f}
- Dispute Type: {scenario.dispute_type}
- Procedural Stage: {scenario.procedural_stage}
- Your Organisation: {scenario.contracting_authority_name}
- Challenging Party: {scenario.bidder_name}

DISPUTE DESCRIPTION:
{scenario.description}
"""

    def get_pre_negotiation_statement(self, scenario: DisputeScenario) -> PreNegotiationStatement:
        scenario_context = self.build_scenario_context(scenario)
        
        user_message = f"""
{scenario_context}

You are now entering pre-negotiation. Based on this dispute, provide your 
pre-negotiation statement as a JSON object. Be specific to this scenario — 
reference the scoring challenge, the £{scenario.contract_value_gbp:,.0f} contract, 
and your legal position under the Procurement Act 2023.

Respond ONLY with valid JSON, no other text before or after.
"""
        
        messages = [
            ("system", CA_SYSTEM_PROMPT),
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

    def respond_to_round(self, scenario: DisputeScenario, conversation_history: list, round_number: int) -> RoundResponse:
        scenario_context = self.build_scenario_context(scenario)

        instruction = f"""
        {scenario_context}

        Negotiation Round {round_number}. Respond to the most recent message from the bidder.

        Respond ONLY with valid JSON matching this exact flat structure — no nesting, no extra keys:
        {{
            "message": "your 2-3 paragraph response here as a single string",
            "proposal": "specific proposal if you are making one, or null",
            "concession_made": "any concession you are offering, or null"
        }}
        """

        # Use the actual role from each tuple — do NOT infer from index position
        messages = [(role, content) for role, content in conversation_history]
        messages.append(("user", instruction))

        json_llm = ChatOllama(model="llama3.1", temperature=0.3, format="json")
        response = json_llm.invoke([("system", CA_SYSTEM_PROMPT)] + messages)

        raw_text = response.content.strip()
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            start = raw_text.find('{')
            end = raw_text.rfind('}') + 1
            data = json.loads(raw_text[start:end])

        return RoundResponse(**data)