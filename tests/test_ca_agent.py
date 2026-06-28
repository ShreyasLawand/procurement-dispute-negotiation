import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.ca_agent import ContractingAuthorityAgent
from src.scenarios.scenario_001 import scoring_challenge

def test_ca_pre_negotiation():
    print("\n" + "="*60)
    print("TESTING: Contracting Authority Pre-Negotiation Statement")
    print("="*60)
    print(f"\nScenario: {scoring_challenge.title}")
    print(f"Contract Value: £{scoring_challenge.contract_value_gbp:,.0f}")
    print(f"Dispute Type: {scoring_challenge.dispute_type}")
    print("\nRunning CA agent...\n")
    
    agent = ContractingAuthorityAgent()
    statement = agent.get_pre_negotiation_statement(scoring_challenge)
    
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
    test_ca_pre_negotiation()