from src.utils.compliance_metrics import parse_llm_json, metrics
from langchain_ollama import ChatOllama
from src.schemas.agent_state import NegotiationSummary, NegotiationState
from src.prompts.summary_prompt import SUMMARY_SYSTEM_PROMPT

class SummaryAgent:

    def __init__(self):
        self.llm = ChatOllama(model="llama3.1", temperature=0.2, format="json")

    def summarize(self, state: NegotiationState) -> NegotiationSummary:
        transcript_lines = []
        for msg in state.messages:
            speaker = "Contracting Authority" if msg.sender_role.value == "contracting_authority" else "Aggrieved Bidder"
            transcript_lines.append(f"[Round {msg.round_number}] {speaker}: {msg.message}")
            if msg.concession_made:
                transcript_lines.append(f"  -> Concession: {msg.concession_made}")

        court_lines = []
        for check in state.compliance_checks:
            court_lines.append(
                f"[Round {check.round_number}] Court: process_followed={check.process_followed}, "
                f"manifest_error={check.manifest_error_found}, "
                f"recommended={check.recommended_action}. Reasoning: {check.reasoning}"
            )

        full_transcript = "\n\n".join(transcript_lines)
        full_court = "\n".join(court_lines)

        user_message = f"""
DISPUTE: {state.scenario.title}
CONTRACT VALUE: £{state.scenario.contract_value_gbp:,.0f}
FINAL OUTCOME: {state.resolution_outcome}

NEGOTIATION TRANSCRIPT:
{full_transcript}

COURT ASSESSMENTS EACH ROUND:
{full_court}

Analyse this completed negotiation and provide your summary as JSON.
"""

        response = self.llm.invoke([
            ("system", SUMMARY_SYSTEM_PROMPT),
            ("user", user_message)
        ])

        raw_text = response.content.strip()
        data = parse_llm_json(raw_text, agent="SummaryAgent", call="summarize")

        return NegotiationSummary(**data)