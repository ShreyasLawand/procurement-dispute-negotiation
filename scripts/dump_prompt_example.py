"""Dump one complete prompt-and-response exchange as JSON.

Asked for by the supervisor on the v1 draft: "it is helpful to provide some json
file as an example, showing how LLM was prompted."

Reconstructs the exact messages sent to the Court agent for a real, committed run,
using the same code path the agent itself uses (CourtAgent.assess_round builds the
user message from the scenario and the two round statements), and pairs them with
the response that run actually logged. No model call is made: the system prompt and
the user message are rebuilt deterministically from source, and the response is read
from the log, so the file is exactly what happened and can be regenerated at will.

    python scripts/dump_prompt_example.py
    python scripts/dump_prompt_example.py --run batch_results/batch_.../run_01.json
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.prompts.court_prompt import COURT_SYSTEM_PROMPT, COURT_SYSTEM_PROMPT_DISCLOSURE  # noqa: E402
from src.schemas.agent_state import DisputeScenario  # noqa: E402
from src.utils.negotiation_helpers import format_contract_value, is_disclosure_dispute  # noqa: E402

DEFAULT_RUN = "batch_results/batch_20260815_200902/run_01.json"
DEFAULT_OUT = "docs/prompt-example-court.json"


def build_user_message(scenario: DisputeScenario, ca_message: str,
                       bidder_message: str, round_number: int) -> str:
    """Mirrors CourtAgent.assess_round's construction exactly."""
    governing = scenario.governing_legislation or \
        "Procurement Act 2023 (default — not otherwise stated in the source)"
    disclosure = is_disclosure_dispute(scenario)

    msg = f"""
FULL DISPUTE SCENARIO (contains the ground-truth facts you must verify against):
Title: {scenario.title}
Contract Value: {format_contract_value(scenario.contract_value_gbp)}
Governing Legislation: {governing}
Description:
{scenario.description}

---

ROUND {round_number}

CONTRACTING AUTHORITY'S POSITION THIS ROUND:
{ca_message}

AGGRIEVED BIDDER'S POSITION THIS ROUND:
{bidder_message}

---
"""
    if disclosure:
        msg += """
Before reaching your conclusion: assess the prima facie case, specificity,
proportionality, and confidentiality-safeguard questions set out in your
system prompt, using only what the scenario and the parties' statements
actually say. Do not assess manifest error or perform a scoring calculation
— that is not the question this application answers.
"""
    else:
        msg += """
Before reaching your conclusion: if the scenario description above contains
any formula, sub-scores, or numbers, perform the calculation yourself now
and check it against any score, ranking, or outcome mentioned in the
scenario or in either party's statements. Show this working in your
"reasoning" field. Then assess legal compliance based on your own
independent finding, not on what either party claims.
"""
    msg += f"""
Set "round_number" to {round_number} in your response.
"""
    return msg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default=DEFAULT_RUN, help="committed run log to draw from")
    ap.add_argument("--round", type=int, default=1, help="which round to dump")
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    log = json.loads((REPO_ROOT / args.run).read_text(encoding="utf-8"))
    scenario = DisputeScenario(**log["scenario"])

    ca = next((m["message"] for m in log["messages"]
               if m["round_number"] == args.round
               and m["sender_role"] == "contracting_authority"), "")
    bidder = next((m["message"] for m in log["messages"]
                   if m["round_number"] == args.round
                   and m["sender_role"] == "aggrieved_bidder"), "")
    check = next(c for c in log["compliance_checks"] if c["round_number"] == args.round)

    disclosure = is_disclosure_dispute(scenario)
    system_prompt = COURT_SYSTEM_PROMPT_DISCLOSURE if disclosure else COURT_SYSTEM_PROMPT

    payload = {
        "_what_this_is": (
            "One complete Court-agent exchange from a real, committed run. The two "
            "request messages are rebuilt from source by the same construction the "
            "agent uses; the response is the one this run actually logged. "
            "Regenerate with scripts/dump_prompt_example.py."
        ),
        "source_run": args.run,
        "round_number": args.round,
        "model": {
            "provider": "ollama",
            "name": "llama3.1",
            "temperature": 0.2,
            "format": "json",
            "note": "format=json constrains decoding to valid JSON; the schema itself "
                    "is enforced afterwards by Pydantic (ComplianceAssessment).",
        },
        "scenario_id": scenario.dispute_id,
        "dispute_type": scenario.dispute_type,
        "procedural_stage": scenario.procedural_stage,
        "prompt_branch": "disclosure" if disclosure else "merits (V4)",
        "request": {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": build_user_message(scenario, ca, bidder, args.round)},
            ]
        },
        "response": {
            "parsed_into": "ComplianceAssessment",
            "content": check,
        },
    }

    out = REPO_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    sys_chars = len(system_prompt)
    usr_chars = len(payload["request"]["messages"][1]["content"])
    print(f"wrote {out.relative_to(REPO_ROOT)}")
    print(f"  scenario     {scenario.dispute_id}  ({payload['prompt_branch']} branch)")
    print(f"  system msg   {sys_chars:,} chars")
    print(f"  user msg     {usr_chars:,} chars")
    print(f"  response     {len(json.dumps(check)):,} chars, "
          f"recommended_action={check['recommended_action']!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
