import anthropic
import json
import os
from dotenv import load_dotenv
from src.schemas.agent_state import PreNegotiationStatement, DisputeScenario, AgentRole
from src.prompts.ca_prompt import CA_SYSTEM_PROMPT

load_dotenv()

class ContractingAuthorityAgent:
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-6"
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
        """
        Agent articulates its interests, goals, and BATNA before negotiation starts.
        """
        scenario_context = self.build_scenario_context(scenario)
        
        user_message = f"""
{scenario_context}

You are now entering pre-negotiation. Based on this dispute, provide your 
pre-negotiation statement as a JSON object. Be specific to this scenario — 
reference the scoring challenge, the £{scenario.contract_value_gbp:,.0f} contract, 
and your legal position under the Procurement Act 2023.
        """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=CA_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )
        
        raw_text = response.content[0].text.strip()
        
        # Parse JSON response
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            # If model adds any preamble, extract JSON block
            start = raw_text.find('{')
            end = raw_text.rfind('}') + 1
            data = json.loads(raw_text[start:end])
        
        return PreNegotiationStatement(**data)

    def respond_to_round(self, scenario: DisputeScenario, conversation_history: list, round_number: int) -> str:
        """
        Agent responds during a negotiation round.
        """
        scenario_context = self.build_scenario_context(scenario)
        
        messages = [{"role": "user", "content": f"{scenario_context}\n\nNegotiation Round {round_number}. Respond to the most recent message from the bidder. Keep your response concise (2-3 paragraphs), legally grounded, and focused on finding resolution."}]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            system=CA_SYSTEM_PROMPT,
            messages=messages
        )
        
        return response.content[0].text.strip()