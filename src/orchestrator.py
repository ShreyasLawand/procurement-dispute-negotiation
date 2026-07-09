from src.agents.ca_agent import ContractingAuthorityAgent
from src.agents.bidder_agent import AggrievedBidderAgent
from src.agents.court_agent import CourtAgent
from src.schemas.agent_state import DisputeScenario, NegotiationState, NegotiationMessage, AgentRole
import json

class NegotiationOrchestrator:

    def __init__(self, max_rounds: int = 5):
        self.ca_agent = ContractingAuthorityAgent()
        self.bidder_agent = AggrievedBidderAgent()
        self.court_agent = CourtAgent()
        self.max_rounds = max_rounds

    def run(self, scenario: DisputeScenario) -> NegotiationState:
        state = NegotiationState(scenario=scenario, max_rounds=self.max_rounds)

        print(f"\n{'='*70}\nDISPUTE: {scenario.title}\n{'='*70}\n")

        # --- Pre-negotiation ---
        print(">> Pre-Negotiation Phase\n")
        state.ca_pre_negotiation = self.ca_agent.get_pre_negotiation_statement(scenario)
        print(f"[CA] Opening position: {state.ca_pre_negotiation.opening_position}\n")

        state.bidder_pre_negotiation = self.bidder_agent.get_pre_negotiation_statement(scenario)
        print(f"[BIDDER] Opening position: {state.bidder_pre_negotiation.opening_position}\n")

        # --- Negotiation rounds ---
        ca_history = []
        bidder_history = []

        for round_num in range(1, self.max_rounds + 1):
            print(f"\n--- ROUND {round_num} ---\n")

            ca_msg = self.ca_agent.respond_to_round(scenario, ca_history, round_num)
            print(f"[CA]: {ca_msg}\n")
            ca_history.append(("assistant", ca_msg))
            bidder_history.append(("user", f"Contracting Authority says: {ca_msg}"))
            state.messages.append(NegotiationMessage(round_number=round_num, sender_role=AgentRole.CONTRACTING_AUTHORITY, message=ca_msg))

            bidder_msg = self.bidder_agent.respond_to_round(scenario, bidder_history, round_num)
            print(f"[BIDDER]: {bidder_msg}\n")
            bidder_history.append(("assistant", bidder_msg))
            ca_history.append(("user", f"Aggrieved Bidder says: {bidder_msg}"))
            state.messages.append(NegotiationMessage(round_number=round_num, sender_role=AgentRole.AGGRIEVED_BIDDER, message=bidder_msg))

            # Court compliance check every round
            assessment = self.court_agent.assess_round(scenario, ca_msg, bidder_msg, round_num)
            state.compliance_checks.append(assessment)
            print(f"[COURT] Process followed: {assessment.process_followed} | Manifest error: {assessment.manifest_error_found} | Recommended: {assessment.recommended_action}\n")

            if assessment.recommended_action != "continue negotiation":
                state.resolved = True
                state.resolution_outcome = assessment.recommended_action
                state.adjudicated = True
                print(f"\n>> RESOLUTION REACHED: {assessment.recommended_action}\n")
                break

        if not state.resolved:
            state.resolution_outcome = "deadlock - max rounds reached, escalate to formal proceedings"
            print(f"\n>> DEADLOCK after {self.max_rounds} rounds\n")

        return state

    def save_log(self, state: NegotiationState, filepath: str):
        with open(filepath, "w") as f:
            json.dump(state.model_dump(), f, indent=2, default=str)
        print(f"\nNegotiation log saved to {filepath}")