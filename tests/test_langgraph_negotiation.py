import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph_orchestrator import GraphNegotiationOrchestrator
from src.cases.loader import load_real_scenario
from src.utils.negotiation_helpers import format_contract_value

# Default smoke case. Any slug in src/cases/real_cases.py works; the scenario is
# extracted once and cached under batch_results/_scenarios/.
CASE = os.environ.get("CASE", "parkingeye-velindre")

if __name__ == "__main__":
    scenario = load_real_scenario(CASE)
    print(f"Case: {scenario.title} ({format_contract_value(scenario.contract_value_gbp)})")

    orchestrator = GraphNegotiationOrchestrator(max_rounds=3)
    final_state = orchestrator.run(scenario)
    orchestrator.save_log(final_state, f"negotiation_log_langgraph_{CASE}.json")

    print(f"\n{'='*70}")
    print(f"FINAL OUTCOME: {final_state['resolution_outcome']}")
    print(f"{'='*70}")
