"""
Tests for graph_orchestrator.py's no_court_check_node (evaluation item 22's no-Court
ablation baseline). The whole point of this node is that it can never resolve a
negotiation early — only court_check_node's recommended_action check can do that, and
this ablation deliberately has no equivalent. These tests lock that behaviour in.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph_orchestrator import no_court_check_node


def _state(round_number: int, max_rounds: int) -> dict:
    return {"round_number": round_number, "max_rounds": max_rounds}


def test_mid_negotiation_never_resolves():
    """Below max_rounds, the ablation must not set resolved/resolution_outcome at all —
    only court_check_node's recommended_action check is allowed to do that, and this
    node has no equivalent mechanism."""
    updates = no_court_check_node(_state(round_number=1, max_rounds=3), agents=None)
    assert "resolved" not in updates
    assert "resolution_outcome" not in updates


def test_at_max_rounds_deadlocks():
    updates = no_court_check_node(_state(round_number=3, max_rounds=3), agents=None)
    assert updates["resolved"] is False
    assert updates["resolution_outcome"] == "deadlock - max rounds reached, escalate to formal proceedings"


def test_past_max_rounds_still_deadlocks():
    """round_number could in principle exceed max_rounds by the time this node runs
    (it increments before the check) - >= not == is the correct comparison."""
    updates = no_court_check_node(_state(round_number=4, max_rounds=3), agents=None)
    assert updates["resolved"] is False


def test_compliance_checks_never_touched():
    """This node must not add to compliance_checks - an empty list at the end of a
    no-Court run is the honest signal that no compliance review happened, not an
    artefact to paper over."""
    state = _state(round_number=3, max_rounds=3)
    state["compliance_checks"] = []
    updates = no_court_check_node(state, agents=None)
    assert "compliance_checks" not in updates


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
