"""
Regression test for a real bug found while investigating a user-reported extraction
error: ScenarioExtractionAgent.extract_scenario(), given EMPTY source text (the exact
shape produced when pypdf silently returns no text for a scanned/image-based PDF - see
document_extraction.py), did not error at all. It fabricated an entire fictional
scenario from nothing (a specific contract value, a 60/40 scoring formula, a marks
correction) with no indication anything was wrong - precisely the failure mode this
project's whole anti-fabrication discipline exists to catch, undetected here because
nothing tested this specific input shape before. Fixed with a minimum-length guard that
raises before any LLM call happens at all, so this can be tested without touching Ollama.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.agents.extraction_agent import ScenarioExtractionAgent, MIN_SOURCE_TEXT_CHARS


def test_empty_source_text_raises_before_any_llm_call():
    agent = ScenarioExtractionAgent()
    start = time.time()
    with pytest.raises(ValueError, match="No usable text"):
        agent.extract_scenario("", dispute_id="TEST-001")
    # If this reached the LLM, it would take seconds (a live Ollama round trip);
    # instant failure is itself evidence the guard fired before self.llm.invoke().
    assert time.time() - start < 1.0


def test_whitespace_only_source_text_raises():
    agent = ScenarioExtractionAgent()
    with pytest.raises(ValueError, match="No usable text"):
        agent.extract_scenario("   \n\n   \t  ", dispute_id="TEST-002")


def test_short_source_text_raises():
    agent = ScenarioExtractionAgent()
    short_text = "Too short to be a real dispute."
    assert len(short_text) < MIN_SOURCE_TEXT_CHARS
    with pytest.raises(ValueError, match="No usable text"):
        agent.extract_scenario(short_text, dispute_id="TEST-003")


def test_guard_reports_actual_character_count():
    agent = ScenarioExtractionAgent()
    with pytest.raises(ValueError, match=r"\b5\b"):
        agent.extract_scenario("hello", dispute_id="TEST-004")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
