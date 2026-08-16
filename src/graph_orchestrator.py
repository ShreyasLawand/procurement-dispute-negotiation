from langgraph.graph import StateGraph, END
from src.graph_state import GraphState
from src.agents.ca_agent import ContractingAuthorityAgent
from src.agents.bidder_agent import AggrievedBidderAgent
from src.agents.court_agent import CourtAgent
from src.agents.summary_agent import SummaryAgent
from src.schemas.agent_state import (
    DisputeScenario, NegotiationState, NegotiationMessage, AgentRole
)
from src.utils.event_stream import emit_status
from dataclasses import dataclass
from functools import partial
import json


@dataclass
class AgentBundle:
    """
    The four agents a graph runs with.

    Agents used to be module-level singletons. They can't be any more: the CA and
    Bidder now carry Doc 1 behavioural profiles baked into their system prompts at
    construction, and those vary per dispute. So the bundle is built per scenario
    and bound into the node functions when the graph is compiled.

    The Court and Summary agents take no profile — Doc 1 gives the judiciary a fixed
    interest set with no per-case practical considerations, and the Summary agent is
    non-negotiating — so they are rebuilt but unparameterised.
    """
    ca: ContractingAuthorityAgent
    bidder: AggrievedBidderAgent
    court: CourtAgent
    summary: SummaryAgent


def build_agents(
    scenario: DisputeScenario | None = None,
    court_system_prompt: str | None = None,
) -> AgentBundle:
    """
    Constructs the agent bundle, applying the scenario's Doc 1 profiles if present.

    `court_system_prompt` overrides the active Court prompt for this bundle only —
    that is how the V3/V4 ablation runs without mutating module state, which would
    otherwise leak between batches executed in the same process.
    """
    ca_profile = getattr(scenario, "ca_profile", None) if scenario is not None else None
    bidder_profile = getattr(scenario, "bidder_profile", None) if scenario is not None else None
    return AgentBundle(
        ca=ContractingAuthorityAgent(profile=ca_profile),
        bidder=AggrievedBidderAgent(profile=bidder_profile),
        court=CourtAgent(system_prompt=court_system_prompt),
        summary=SummaryAgent(),
    )


def pre_negotiation_node(state: GraphState, agents: AgentBundle) -> dict:
    """Both agents state their interests, goals, and BATNA before negotiation begins."""
    scenario = state["scenario"]

    print(f"\n{'='*70}\nDISPUTE: {scenario.title}\n{'='*70}\n")
    print(">> Pre-Negotiation Phase\n")
    emit_status("Both parties are preparing their opening positions…", phase="pre_negotiation")

    ca_pre = agents.ca.get_pre_negotiation_statement(scenario)
    print(f"[CA] Opening position: {ca_pre.opening_position}\n")

    bidder_pre = agents.bidder.get_pre_negotiation_statement(scenario)
    print(f"[BIDDER] Opening position: {bidder_pre.opening_position}\n")

    return {
        "ca_pre_negotiation": ca_pre,
        "bidder_pre_negotiation": bidder_pre,
        "round_number": 0,
        "ca_history": [],
        "bidder_history": [],
        "messages": [],
        "compliance_checks": [],
        "resolved": False,
        "adjudicated": False,
    }


def ca_round_node(state: GraphState, agents: AgentBundle) -> dict:
    """CA agent responds for the current round."""
    scenario = state["scenario"]
    round_num = state["round_number"] + 1
    max_rounds = state["max_rounds"]

    print(f"\n{'─'*70}")
    print(f"  ROUND {round_num}")
    print(f"{'─'*70}\n")
    emit_status(f"Contracting Authority is drafting its round {round_num} response…",
                phase="ca_round", round_number=round_num)

    ca_response = agents.ca.respond_to_round(
        scenario, state["ca_history"], round_num, max_rounds=max_rounds
    )
    ca_msg = ca_response.message

    print(f"CONTRACTING AUTHORITY:")
    print(f"   {ca_msg}")
    if ca_response.concession_made:
        print(f"   [Concession offered]: {ca_response.concession_made}")
    print()

    new_ca_history = state["ca_history"] + [("assistant", ca_msg)]
    new_bidder_history = state["bidder_history"] + [("user", f"Contracting Authority says: {ca_msg}")]

    new_message = NegotiationMessage(
        round_number=round_num, sender_role=AgentRole.CONTRACTING_AUTHORITY,
        message=ca_msg, proposal=ca_response.proposal, concession_made=ca_response.concession_made
    )

    return {
        "round_number": round_num,
        "ca_history": new_ca_history,
        "bidder_history": new_bidder_history,
        "messages": state["messages"] + [new_message],
        "last_ca_msg": ca_msg,
    }


def bidder_round_node(state: GraphState, agents: AgentBundle) -> dict:
    """Bidder agent responds for the current round."""
    scenario = state["scenario"]
    round_num = state["round_number"]
    max_rounds = state["max_rounds"]
    emit_status(f"Aggrieved Bidder is drafting its round {round_num} response…",
                phase="bidder_round", round_number=round_num)

    bidder_response = agents.bidder.respond_to_round(
        scenario, state["bidder_history"], round_num, max_rounds=max_rounds
    )
    bidder_msg = bidder_response.message

    print(f"AGGRIEVED BIDDER:")
    print(f"   {bidder_msg}")
    if bidder_response.concession_made:
        print(f"   [Concession offered]: {bidder_response.concession_made}")
    print()

    new_bidder_history = state["bidder_history"] + [("assistant", bidder_msg)]
    new_ca_history = state["ca_history"] + [("user", f"Aggrieved Bidder says: {bidder_msg}")]

    new_message = NegotiationMessage(
        round_number=round_num, sender_role=AgentRole.AGGRIEVED_BIDDER,
        message=bidder_msg, proposal=bidder_response.proposal, concession_made=bidder_response.concession_made
    )

    return {
        "ca_history": new_ca_history,
        "bidder_history": new_bidder_history,
        "messages": state["messages"] + [new_message],
        "last_bidder_msg": bidder_msg,
    }


def court_check_node(state: GraphState, agents: AgentBundle) -> dict:
    """Court agent assesses legal compliance for the round just completed."""
    scenario = state["scenario"]
    round_num = state["round_number"]
    emit_status(f"Court is reviewing round {round_num} for compliance…",
                phase="court_check", round_number=round_num)

    assessment = agents.court.assess_round(
        scenario, state["last_ca_msg"], state["last_bidder_msg"], round_num
    )

    print(f"COURT ASSESSMENT:")
    print(f"   Process followed: {assessment.process_followed} | Manifest error: {assessment.manifest_error_found}")
    print(f"   Recommended: {assessment.recommended_action}")
    print(f"   Reasoning: {assessment.reasoning}\n")

    updates = {"compliance_checks": state["compliance_checks"] + [assessment]}

    if assessment.recommended_action != "continue negotiation":
        updates["resolved"] = True
        updates["resolution_outcome"] = assessment.recommended_action
        updates["adjudicated"] = True
        print(f"\n>> RESOLUTION REACHED: {assessment.recommended_action}\n")
    elif round_num >= state["max_rounds"]:
        updates["resolved"] = False
        updates["resolution_outcome"] = "deadlock - max rounds reached, escalate to formal proceedings"
        print(f"\n>> DEADLOCK after {state['max_rounds']} rounds\n")

    return updates


def no_court_check_node(state: GraphState, agents: AgentBundle) -> dict:
    """
    No-Court ablation baseline (evaluation item 22) — skips the Court agent's
    compliance review entirely, bound into "court_check" in place of court_check_node
    above. compliance_checks is deliberately left untouched (stays empty across the
    whole run), so downstream nodes render it as "no checks happened", not as a
    silently-passing review.

    Without an adjudicator, nothing in this graph can ever decide the parties have
    converged — that decision IS court_check_node's recommended_action != "continue
    negotiation" check. So this node's only remaining job is the same max-rounds
    check court_check_node does when the Court itself never resolves anything: run
    to the round limit and deadlock. A version of this ablation that tried to
    fabricate a resolution-detection heuristic from the dialogue text (e.g. "did the
    Bidder's last message sound conciliatory?") would defeat the point of the
    ablation — the finding this baseline exists to surface is precisely that nothing
    in this system resolves anything without judicial adjudication, and reporting an
    always-deadlock result honestly is that finding, not a gap to paper over.
    """
    round_num = state["round_number"]
    emit_status(f"No Court agent in this ablation — round {round_num} recorded without compliance review",
                phase="court_check", round_number=round_num)

    if round_num >= state["max_rounds"]:
        print(f"\n>> DEADLOCK after {state['max_rounds']} rounds (no-Court ablation: nothing can resolve without a Court)\n")
        return {
            "resolved": False,
            "resolution_outcome": "deadlock - max rounds reached, escalate to formal proceedings",
        }
    return {}


def win_statements_node(state: GraphState, agents: AgentBundle) -> dict:
    """Each agent reflects on the outcome relative to its own BATNA."""
    scenario = state["scenario"]
    outcome = state["resolution_outcome"]

    # Build a short transcript summary to give agents context for their reflection
    transcript_lines = [f"[Round {m.round_number}] {m.sender_role.value}: {m.message}" for m in state["messages"]]
    transcript_summary = "\n".join(transcript_lines)

    print(f"\n{'='*70}")
    print("  POST-NEGOTIATION: WIN STATEMENTS")
    print(f"{'='*70}\n")
    emit_status("Both parties are reflecting on the final outcome…", phase="win_statements")

    ca_win = agents.ca.get_win_statement(scenario, outcome, transcript_summary)
    print(f"CONTRACTING AUTHORITY WIN STATEMENT:")
    print(f"   {ca_win.win_statement}\n")

    bidder_win = agents.bidder.get_win_statement(scenario, outcome, transcript_summary)
    print(f"AGGRIEVED BIDDER WIN STATEMENT:")
    print(f"   {bidder_win.win_statement}\n")

    return {
        "ca_win_statement": ca_win,
        "bidder_win_statement": bidder_win,
    }


def route_after_court(state: GraphState) -> str:
    """
    Conditional edge: decide whether to loop back for another round,
    or move on to the post-negotiation reflection and summary.
    """
    if state.get("resolved") or (state["round_number"] >= state["max_rounds"]):
        return "summary"
    return "continue"


def summary_node(state: GraphState, agents: AgentBundle) -> dict:
    """Post-negotiation: Summary agent reviews the full transcript."""
    print(f"\n{'='*70}")
    print("  GENERATING NEGOTIATION SUMMARY")
    print(f"{'='*70}\n")
    emit_status("Preparing a plain-English summary of the negotiation…", phase="summary")

    # Build a temporary NegotiationState (Pydantic) for the summary agent,
    # which expects that shape.
    temp_state = NegotiationState(
        scenario=state["scenario"],
        round_number=state["round_number"],
        max_rounds=state["max_rounds"],
        ca_pre_negotiation=state["ca_pre_negotiation"],
        bidder_pre_negotiation=state["bidder_pre_negotiation"],
        messages=state["messages"],
        compliance_checks=state["compliance_checks"],
        resolved=state["resolved"],
        resolution_outcome=state["resolution_outcome"],
        adjudicated=state["adjudicated"],
    )

    summary = agents.summary.summarize(temp_state)

    print(f"PLAIN ENGLISH SUMMARY:")
    print(f"   {summary.plain_english_summary}\n")
    print(f"KEY STICKING POINTS:")
    for point in summary.key_sticking_points:
        print(f"   - {point}")
    print()
    print(f"CONCESSIONS:")
    print(f"   {summary.concessions_summary}\n")
    print(f"COURT REASONING:")
    print(f"   {summary.court_reasoning_summary}\n")
    print(f"LIKELY NEXT STEPS:")
    print(f"   {summary.likely_next_steps}\n")

    return {"summary": summary}


def build_negotiation_graph(agents: AgentBundle | None = None, include_court: bool = True):
    """
    Constructs and compiles the LangGraph StateGraph for the negotiation.

    `agents` is bound into each node via functools.partial. Node NAMES are passed
    explicitly and are unchanged, so api/sessions.py::translate_update — which keys
    off those names — is unaffected. `include_court=False` is the no-Court ablation
    baseline (evaluation item 22): binds no_court_check_node in place of
    court_check_node under the same "court_check" node name, so route_after_court and
    every downstream node are untouched — only what happens inside that one node
    differs. See no_court_check_node's docstring for why this ablation always ends in
    deadlock rather than fabricating a resolution-detection heuristic.
    """
    if agents is None:
        agents = build_agents()

    graph = StateGraph(GraphState)

    court_node_fn = court_check_node if include_court else no_court_check_node

    graph.add_node("pre_negotiation", partial(pre_negotiation_node, agents=agents))
    graph.add_node("ca_round", partial(ca_round_node, agents=agents))
    graph.add_node("bidder_round", partial(bidder_round_node, agents=agents))
    graph.add_node("court_check", partial(court_node_fn, agents=agents))
    graph.add_node("win_statements", partial(win_statements_node, agents=agents))
    graph.add_node("summary", partial(summary_node, agents=agents))

    graph.set_entry_point("pre_negotiation")

    graph.add_edge("pre_negotiation", "ca_round")
    graph.add_edge("ca_round", "bidder_round")
    graph.add_edge("bidder_round", "court_check")

    graph.add_conditional_edges(
        "court_check",
        route_after_court,
        {
            "continue": "ca_round",
            "summary": "win_statements",
        }
    )

    graph.add_edge("win_statements", "summary")
    graph.add_edge("summary", END)

    return graph.compile()


class GraphNegotiationOrchestrator:
    """
    Wraps the compiled LangGraph so it can be called the same way as the
    original NegotiationOrchestrator — run(scenario) -> final state, plus
    save_log() for persistence.
    """

    def __init__(self, max_rounds: int = 3, court_system_prompt: str | None = None,
                 include_court: bool = True):
        self.max_rounds = max_rounds
        self.court_system_prompt = court_system_prompt
        self.include_court = include_court
        # Default profile-less graph, kept so an orchestrator is usable without ever
        # seeing a scenario. Scenarios carrying Doc 1 profiles get their own compiled
        # graph in _app_for(), since profiles are baked into agent system prompts at
        # construction time and so cannot be swapped on an already-built agent.
        self.app = build_negotiation_graph(build_agents(None, court_system_prompt), include_court)

    def _app_for(self, scenario: DisputeScenario):
        """
        Returns the compiled graph to run this scenario with. Falls back to the
        shared profile-less app when the scenario declares no profiles, so the
        common path costs nothing extra and pre-existing baselines are byte-for-byte
        reproducible.
        """
        has_profile = (
            getattr(scenario, "ca_profile", None) is not None
            or getattr(scenario, "bidder_profile", None) is not None
        )
        if not has_profile:
            return self.app
        return build_negotiation_graph(
            build_agents(scenario, self.court_system_prompt), self.include_court
        )

    def _build_initial_state(self, scenario: DisputeScenario) -> GraphState:
        return {
            "scenario": scenario,
            "round_number": 0,
            "max_rounds": self.max_rounds,
            "ca_pre_negotiation": None,
            "bidder_pre_negotiation": None,
            "ca_history": [],
            "bidder_history": [],
            "messages": [],
            "compliance_checks": [],
            "last_ca_msg": None,
            "last_bidder_msg": None,
            "resolved": False,
            "resolution_outcome": None,
            "adjudicated": False,
            "ca_win_statement": None,
            "bidder_win_statement": None,
            "summary": None,
        }

    def run(self, scenario: DisputeScenario) -> dict:
        final_state = self._app_for(scenario).invoke(self._build_initial_state(scenario))
        return final_state

    def stream(self, scenario: DisputeScenario):
        """
        Yields one {node_name: partial_state_update} dict per graph
        super-step. Used by the live-negotiation API (api/sessions.py) to
        push SSE events as each node completes; run()/save_log() above are
        untouched and remain the path used by batch scripts and tests.
        """
        yield from self._app_for(scenario).stream(
            self._build_initial_state(scenario), stream_mode="updates"
        )

    def save_log(self, final_state: dict, filepath: str):
        # Convert dict-shaped final state to the Pydantic NegotiationState for
        # a clean, consistent JSON log format — same as the original orchestrator.
        state_obj = NegotiationState(
            scenario=final_state["scenario"],
            round_number=final_state["round_number"],
            max_rounds=final_state["max_rounds"],
            ca_pre_negotiation=final_state["ca_pre_negotiation"],
            bidder_pre_negotiation=final_state["bidder_pre_negotiation"],
            messages=final_state["messages"],
            compliance_checks=final_state["compliance_checks"],
            resolved=final_state["resolved"],
            resolution_outcome=final_state["resolution_outcome"],
            adjudicated=final_state["adjudicated"],
            ca_win_statement=final_state["ca_win_statement"],
            bidder_win_statement=final_state["bidder_win_statement"],
            summary=final_state["summary"],
        )
        with open(filepath, "w") as f:
            json.dump(state_obj.model_dump(), f, indent=2, default=str)
        print(f"\nNegotiation log saved to {filepath}")