import json
from langchain_ollama import ChatOllama
from src.utils.negotiation_helpers import is_repetitive, format_previous_statements, get_round_stage_instruction
from src.prompts.bidder_prompt import BIDDER_SYSTEM_PROMPT, BIDDER_WIN_STATEMENT_PROMPT
from src.schemas.agent_state import PreNegotiationStatement, DisputeScenario, AgentRole, RoundResponse, WinStatement
from src.utils.event_stream import emit_status

class AggrievedBidderAgent:

    def __init__(self):
        self.llm = ChatOllama(model="llama3.1", temperature=0.4)
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

    def respond_to_round(self, scenario: DisputeScenario, conversation_history: list,
                          round_number: int, max_rounds: int = 3) -> RoundResponse:
        scenario_context = self.build_scenario_context(scenario)

        own_previous = [content for role, content in conversation_history if role == "assistant"]

        stage_instruction = get_round_stage_instruction(round_number, max_rounds)

        base_instruction = f"""
{scenario_context}

NEGOTIATION ROUND {round_number} of {max_rounds}.

{stage_instruction}

YOUR OWN PREVIOUS STATEMENTS IN THIS NEGOTIATION (do not repeat these):
{format_previous_statements(own_previous)}

Respond ONLY with valid JSON matching this exact flat structure — no nesting, no extra keys:
{{
  "message": "your 2-3 paragraph response here as a single string",
  "proposal": "specific proposal if you are making one, or null",
  "concession_made": "any concession you are offering, or null"
}}

"proposal" and "concession_made" MUST each be a single plain-English string
(or null) — NEVER a nested JSON object.
WRONG: "proposal": {{"partial_award": true, "percentage_of_contract_value": 0.5}}
RIGHT: "proposal": "A partial award covering 50% of the contract value"
"""

        messages = [(role, content) for role, content in conversation_history]

        max_attempts = 3
        temperature = 0.4
        result = None

        for attempt in range(max_attempts):
            instruction = base_instruction
            if attempt > 0:
                instruction += (
                    "\n\nWARNING: Your previous attempt was too similar to a statement "
                    "you already made. You MUST provide substantively different content "
                    "this time — a genuinely new argument, question, or concession."
                )
                temperature = min(0.4 + attempt * 0.2, 0.9)

            json_llm = ChatOllama(model="llama3.1", temperature=temperature, format="json")
            response = json_llm.invoke(
                [("system", BIDDER_SYSTEM_PROMPT)] + messages + [("user", instruction)]
            )

            raw_text = response.content.strip()
            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError:
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1
                data = json.loads(raw_text[start:end])

            result = RoundResponse(**data)

            if not is_repetitive(result.message, own_previous):
                return result

            msg = f"Regenerating Aggrieved Bidder response (attempt {attempt + 2} of {max_attempts})…"
            print(f"   [Bidder response attempt {attempt + 1} too similar to a prior statement — regenerating]")
            emit_status(msg, role=self.role.value, round_number=round_number, attempt=attempt + 2)

        return result

    def get_win_statement(self, scenario: DisputeScenario, resolution_outcome: str, transcript_summary: str) -> WinStatement:
        scenario_context = self.build_scenario_context(scenario)

        user_message = f"""
{scenario_context}

FINAL OUTCOME: {resolution_outcome}

NEGOTIATION SUMMARY:
{transcript_summary}

Provide your post-negotiation win statement as JSON.
"""

        response = self.llm.invoke([
            ("system", BIDDER_WIN_STATEMENT_PROMPT),
            ("user", user_message)
        ])

        raw_text = response.content.strip()
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            start = raw_text.find('{')
            end = raw_text.rfind('}') + 1
            data = json.loads(raw_text[start:end])

        return WinStatement(**data)