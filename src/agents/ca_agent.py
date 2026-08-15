from langchain_ollama import ChatOllama
from src.utils.negotiation_helpers import is_repetitive, format_previous_statements, get_round_stage_instruction
from src.prompts.ca_prompt import CA_SYSTEM_PROMPT, CA_WIN_STATEMENT_PROMPT, build_ca_system_prompt
from src.schemas.agent_state import PreNegotiationStatement, DisputeScenario, AgentRole, RoundResponse, WinStatement, CAProfile
from src.utils.event_stream import emit_status
from src.utils.compliance_metrics import parse_llm_json, metrics

class ContractingAuthorityAgent:

    def __init__(self, profile: CAProfile | None = None):
        self.llm = ChatOllama(model="llama3.1", temperature=0.3)
        self.role = AgentRole.CONTRACTING_AUTHORITY
        # Doc 1's per-case behavioural modifiers. None (the default) renders no
        # extra prompt text, so this is identical to the pre-profile behaviour.
        self.profile = profile
        self.system_prompt = build_ca_system_prompt(profile)

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

For "interests", work from your seven primary interests & drivers, but do NOT
simply list the category names back. Select only the categories genuinely engaged
by these facts, and write each entry as:
  "<Category name>: <what that driver concretely means in THIS dispute>"
TOO VAGUE (category name alone): "Continuity of Service / Delivery"
CORRECT SHAPE: "Continuity of Service / Delivery: <what this specific procurement
delivers, and the concrete operational consequence of delay or a re-run given these
facts>"
Fill the angle brackets with the real facts of this dispute. Do not reproduce the
bracketed wording itself.

"batna" and "opening_position" MUST each be a single plain-English string —
NEVER a nested JSON object.
WRONG: "batna": {{"forum": "TCC", "cost_gbp": 50000, "duration_months": 9}}
RIGHT: "batna": "Defend the decision in the TCC — costly (£50k+) and slow
(6-12 months), with a real risk of automatic suspension."

Respond ONLY with valid JSON, no other text before or after.
"""

        messages = [
            ("system", self.system_prompt),
            ("user", user_message)
        ]

        response = self.llm.invoke(messages)
        raw_text = response.content.strip()

        data = parse_llm_json(raw_text, agent="ContractingAuthorityAgent", call="pre_negotiation")

        return PreNegotiationStatement(**data)

    def respond_to_round(self, scenario: DisputeScenario, conversation_history: list,
                          round_number: int, max_rounds: int = 3) -> RoundResponse:
        scenario_context = self.build_scenario_context(scenario)

        # Extract this agent's own previous statements from history, so it can see
        # exactly what it already said and be explicitly told not to repeat it.
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
        temperature = 0.3
        result = None

        for attempt in range(max_attempts):
            instruction = base_instruction
            if attempt > 0:
                instruction += (
                    "\n\nWARNING: Your previous attempt was too similar to a statement "
                    "you already made. You MUST provide substantively different content "
                    "this time — a genuinely new argument, question, or concession."
                )
                temperature = min(0.3 + attempt * 0.2, 0.8)

            json_llm = ChatOllama(model="llama3.1", temperature=temperature, format="json")
            response = json_llm.invoke(
                [("system", self.system_prompt)] + messages + [("user", instruction)]
            )

            raw_text = response.content.strip()
            data = parse_llm_json(raw_text, agent="ContractingAuthorityAgent", call="round_response")

            result = RoundResponse(**data)

            if not is_repetitive(result.message, own_previous):
                return result

            metrics.record_repetition_retry("ContractingAuthorityAgent")
            msg = f"Regenerating Contracting Authority response (attempt {attempt + 2} of {max_attempts})…"
            print(f"   [CA response attempt {attempt + 1} too similar to a prior statement — regenerating]")
            emit_status(msg, role=self.role.value, round_number=round_number, attempt=attempt + 2)

        # If still repetitive after all retries, return the last attempt anyway
        # rather than crashing — better to have a slightly repetitive message
        # than no message at all.
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
            ("system", CA_WIN_STATEMENT_PROMPT),
            ("user", user_message)
        ])

        raw_text = response.content.strip()
        data = parse_llm_json(raw_text, agent="ContractingAuthorityAgent", call="win_statement")

        return WinStatement(**data)