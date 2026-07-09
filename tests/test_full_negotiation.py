import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import NegotiationOrchestrator
from src.scenarios.scenario_001 import scoring_challenge

if __name__ == "__main__":
    orchestrator = NegotiationOrchestrator(max_rounds=3)  # keep short for first test
    final_state = orchestrator.run(scoring_challenge)
    orchestrator.save_log(final_state, "negotiation_log_001.json")

    print(f"\n{'='*70}")
    print(f"FINAL OUTCOME: {final_state.resolution_outcome}")
    print(f"{'='*70}")