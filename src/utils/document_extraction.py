import io
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

# ~5,000 tokens of headroom under the extraction agent's num_ctx=8192 —
# see src/agents/extraction_agent.py.
CHAR_BUDGET = 20_000


def extract_text(filename: str, content: bytes) -> str:
    """Pulls raw text out of an uploaded document. Supports PDF, DOCX, and
    plain text/markdown — no OCR, no layout preservation, just text."""
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)

    if ext == ".docx":
        from docx import Document

        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)

    if ext in (".txt", ".md"):
        return content.decode("utf-8", errors="replace")

    raise ValueError(f"Unsupported file type: {ext!r} (supported: {sorted(SUPPORTED_EXTENSIONS)})")


def combine_documents(files: list[tuple[str, bytes]]) -> str:
    """Extracts and concatenates text from multiple uploaded documents,
    labelled so the extraction agent can attribute facts to a source."""
    parts = []
    for name, content in files:
        text = extract_text(name, content).strip()
        parts.append(f"=== SOURCE DOCUMENT: {name} ===\n{text}")
    return "\n\n".join(parts)


def truncate_for_context(text: str, budget: int = CHAR_BUDGET) -> str:
    """
    Explicit character-budget truncation — no map-reduce summarizer, a
    deliberate scope simplification given modest local hardware. Keeps the
    head (facts are usually front-loaded in a judgment/case summary) and the
    tail (outcomes/relief are usually back-loaded), drops the middle.
    """
    if len(text) <= budget:
        return text
    head_len = int(budget * 0.7)
    tail_len = budget - head_len
    omitted = len(text) - budget
    return text[:head_len] + f"\n\n[... {omitted:,} characters omitted for length ...]\n\n" + text[-tail_len:]
