from langchain_ollama import ChatOllama
from src.prompts.extraction_prompt import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_TEMPLATE
from src.schemas.agent_state import DisputeScenario
from src.utils.document_extraction import truncate_for_context
from src.utils.compliance_metrics import parse_llm_json

# Below this, there isn't plausibly enough real dispute content for a genuine extraction —
# found by testing what this agent does with EMPTY source text (simulating a scanned/
# image-based PDF that pypdf silently returns no text for, see document_extraction.py):
# rather than erroring, the model fabricated an entire fictional scenario from nothing
# (a specific contract value, a 60/40 scoring formula, a marks correction) with no
# indication anything was wrong. That is exactly the failure mode this project's whole
# anti-fabrication discipline exists to catch — caught here in the one place upstream of
# every other check, so it never reaches the Court agent's grounding checks at all.
MIN_SOURCE_TEXT_CHARS = 200


class ScenarioExtractionAgent:
    """
    Turns raw source document text (a real case judgment, summary, or any
    user-supplied procurement dispute document) into a structured
    DisputeScenario the negotiation agents can work with. Same
    ChatOllama + manual-JSON-parse-with-fallback pattern as the other
    agents, but with a larger context window since it's the one agent that
    reads long raw source text rather than an already-condensed scenario.
    """

    def __init__(self):
        self.llm = ChatOllama(model="llama3.1", temperature=0.2, format="json", num_ctx=8192)

    def _invoke_and_parse(self, user_message: str) -> dict:
        response = self.llm.invoke([
            ("system", EXTRACTION_SYSTEM_PROMPT),
            ("user", user_message),
        ])
        raw_text = response.content.strip()
        return parse_llm_json(raw_text, agent="ScenarioExtractionAgent", call="extract")

    def extract_scenario(
        self,
        source_text: str,
        dispute_id: str,
        contracting_authority_name: str | None = None,
        bidder_name: str | None = None,
    ) -> DisputeScenario:
        stripped = source_text.strip()
        if len(stripped) < MIN_SOURCE_TEXT_CHARS:
            raise ValueError(
                f"No usable text could be extracted from the uploaded document(s) — only "
                f"{len(stripped)} character(s) of content found (need at least "
                f"{MIN_SOURCE_TEXT_CHARS}). This usually means a scanned or image-based PDF "
                f"with no text layer, a password-protected file, or an empty document. Try a "
                f"text-based PDF, a .docx, or a .txt/.md file instead."
            )

        truncated = truncate_for_context(source_text)
        user_message = EXTRACTION_USER_TEMPLATE.format(source_text=truncated)

        data = self._invoke_and_parse(user_message)
        data["dispute_id"] = dispute_id
        if contracting_authority_name:
            data["contracting_authority_name"] = contracting_authority_name
        if bidder_name:
            data["bidder_name"] = bidder_name

        try:
            return DisputeScenario(**data)
        except Exception as first_error:
            # Arbitrary uploaded/researched source text is the highest-risk
            # input in the whole pipeline (unlike the already-grounded
            # round-response retries) — one repair attempt before giving up.
            repair_message = (
                f"{user_message}\n\n"
                f"Your previous JSON response was invalid: {first_error}\n"
                f"Return corrected JSON only, matching the exact structure requested."
            )
            data = self._invoke_and_parse(repair_message)
            data["dispute_id"] = dispute_id
            if contracting_authority_name:
                data["contracting_authority_name"] = contracting_authority_name
            if bidder_name:
                data["bidder_name"] = bidder_name
            return DisputeScenario(**data)
