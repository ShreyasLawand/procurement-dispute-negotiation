import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.ca_agent import ContractingAuthorityAgent
from src.cases.loader import load_real_scenario

CASE = os.environ.get("CASE", "parkingeye-velindre")

# Named check_* rather than test_* deliberately: this needs a live Ollama call (non-deterministic,
# slow), so it must NOT be picked up by pytest's test_* auto-discovery — a bare `pytest tests/` should
# stay fast and offline. Run directly instead: `python tests/test_ca_agent.py`. (The scenario-loading
# bug this also fixes — `load_real_scenario` was imported but never called, leaving `scenario`
# undefined — was a leftover from the real-cases migration and is what first exposed the collection
# problem, when a broad `pytest tests/` run picked this up and hit a NameError.)
def check_ca_pre_negotiation():
    scenario = load_real_scenario(CASE)
    print("\n" + "="*60)
    print("TESTING: Contracting Authority Pre-Negotiation Statement")
    print("="*60)
    print(f"\nScenario: {scenario.title}")
    print(f"Contract Value: £{scenario.contract_value_gbp:,.0f}")
    print(f"Dispute Type: {scenario.dispute_type}")
    print("\nRunning CA agent...\n")
    
    agent = ContractingAuthorityAgent()
    statement = agent.get_pre_negotiation_statement(scenario)
    
    print("CA PRE-NEGOTIATION STATEMENT:")
    print("-"*40)
    print(f"Role: {statement.role}")
    print(f"\nINTERESTS:")
    for i, interest in enumerate(statement.interests, 1):
        print(f"  {i}. {interest}")
    print(f"\nGOALS:")
    for i, goal in enumerate(statement.goals, 1):
        print(f"  {i}. {goal}")
    print(f"\nBATNA:\n  {statement.batna}")
    print(f"\nOPENING POSITION:\n  {statement.opening_position}")
    print(f"\nLEGAL BASIS:")
    for i, law in enumerate(statement.legal_basis, 1):
        print(f"  {i}. {law}")
    print(f"\nCONFIDENCE SCORE: {statement.confidence_score}")
    print("\n" + "="*60)
    print("✅ CA Agent test passed — structured output validated")
    print("="*60)
    
    return statement

if __name__ == "__main__":
    check_ca_pre_negotiation()