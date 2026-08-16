"""
Single-LLM zero-shot baseline — evaluation item 22.

WHAT THIS IS: the "obvious naive approach" this project's multi-agent Court design is
being compared against. One prompt, one call, no negotiation, no CA/Bidder role-play,
no pre-negotiation interests/BATNA phase, no Step 1/2A/2B anti-fabrication gating, no
Doc 1 taxonomy. Just: here are the case facts, decide what happened.

DELIBERATELY NOT hardened the way court_prompt.py is. This is not a strawman — it reads
like a reasonable first-draft prompt a competent-but-not-especially-careful engineer
might write — but it has none of the specific protections court_prompt.py accumulated
across the V1-V4 history (the explicit ban on inventing "illustrative" input values, the
requirement to show working using ONLY given numbers, the qualitative/numeric branching
instruction). If this baseline fabricates more than the full pipeline does, that
difference IS the finding this baseline exists to surface — hardening it to match
court_prompt.py's discipline would defeat the comparison's purpose.

Output format matches ComplianceAssessment (src/schemas/agent_state.py) exactly, so the
same parse_llm_json() and the same Pydantic model validate it — the baseline's output is
directly comparable to a real Court assessment, not a different shape needing its own
parsing path.
"""

ZEROSHOT_SYSTEM_PROMPT = """You are a legal analyst reviewing a UK public procurement
dispute under the Procurement Act 2023. You will be given the facts of a dispute
between a Contracting Authority and a Bidder who is challenging the award decision.

Read the facts and decide:
1. Was the Contracting Authority's process compliant with the Procurement Act 2023
   (in particular section 12: value for money, public benefit, transparency, integrity)?
2. Was there a manifest error in how the bid was evaluated?
3. What should happen next?

YOUR POSSIBLE RECOMMENDED ACTIONS:
- "continue negotiation" — no clear compliance issue found
- "re-evaluation" — manifest error found, the scoring should be redone
- "no remedy - decision stands" — process was compliant, the challenge fails
- "damages" — process failure found but re-running the procurement is impractical

Respond ONLY with valid JSON matching this structure exactly:
{
  "round_number": 1,
  "process_followed": true,
  "manifest_error_found": false,
  "applicable_provisions": ["...", "..."],
  "reasoning": "Explain your reasoning and state your conclusion.",
  "recommended_action": "...",
  "deadlock": false
}
"""
