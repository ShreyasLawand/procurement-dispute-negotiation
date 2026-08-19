import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import NegotiationOrchestrator
from src.cases.loader import load_real_scenario
from src.utils.negotiation_helpers import format_contract_value

# Exercises the LEGACY plain-loop orchestrator. graph_orchestrator.py is the primary
# path — see tests/test_langgraph_negotiation.py.
CASE = os.environ.get("CASE", "parkingeye-velindre")

if __name__ == "__main__":
    scenario = load_real_scenario(CASE)
    print(f"Case: {scenario.title} ({format_contract_value(scenario.contract_value_gbp)})")

    orchestrator = NegotiationOrchestrator(max_rounds=3)  # keep short for first test
    final_state = orchestrator.run(scenario)
    orchestrator.save_log(final_state, f"negotiation_log_legacy_{CASE}.json")

    print(f"\n{'='*70}")
    print(f"FINAL OUTCOME: {final_state.resolution_outcome}")
    print(f"{'='*70}")
