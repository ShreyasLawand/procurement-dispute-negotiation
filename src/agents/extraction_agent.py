import json
from langchain_ollama import ChatOllama
from src.prompts.extraction_prompt import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_TEMPLATE
from src.schemas.agent_state import DisputeScenario
from src.utils.document_extraction import truncate_for_context


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
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            start = raw_text.find("{")
            end = raw_text.rfind("}") + 1
            return json.loads(raw_text[start:end])

    def extract_scenario(
        self,
        source_text: str,
        dispute_id: str,
        contracting_authority_name: str | None = None,
        bidder_name: str | None = None,
    ) -> DisputeScenario:
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
