"""Evaluator tests: success comes from final environment state, not self-report."""
from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.environments.tool_world import ToolWorld
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome
from agentfotagent.runtime.mock_backend import run_episode


def test_success_computed_from_final_state_not_self_report():
    """A trace claiming success must not flip a failed episode to success."""
    task = generate_task("dial_set", 1, "train")
    ev = StateBasedEvaluator()

    # Build a final state that does NOT satisfy the goal (dials at 0).
    final_state = {
        "dials": {"alpha": 0, "beta": 0, "gamma": 0},
        "step": 5,
        "termination_reason": "agent_submit",
        "objects": {},
        "relay": {},
        "inventory": [],
        "location": "console",
    }
    lying_trace = [
        {
            "step_index": 0,
            "action": {"tool": "submit", "args": {}},
            "info": {"valid": True, "self_report_success": True},
            "state_hash": "x",
            "self_report_success": True,
        }
    ]
    result = ev.evaluate(task, final_state, lying_trace)
    assert result.success is False
    assert result.diagnostic["claimed_success"] is True
    assert result.diagnostic["self_report_ignored"] is True


def test_success_when_goal_state_reached():
    task = generate_task("dial_set", 1, "train")
    targets = task.hidden_goal["targets"]
    final_state = {
        "dials": dict(targets),
        "step": 8,
        "termination_reason": "agent_submit",
        "objects": {},
        "relay": {},
        "inventory": [],
        "location": "console",
    }
    result = StateBasedEvaluator().evaluate(task, final_state, [])
    assert result.success is True


def test_key_crate_predicate_requires_object_on_surface():
    task = generate_task("key_crate", 1, "train")
    not_yet = {
        "objects": {
            "statue": {"location": "vault"},
            "crate": {"unlocked": True, "locked": False},
        },
        "step": 10,
        "termination_reason": "agent_submit",
        "dials": {},
        "relay": {},
        "inventory": [],
        "location": "hall",
    }
    assert StateBasedEvaluator().evaluate(task, not_yet, []).success is False

    done = {
        "objects": {
            "statue": {"location": "pedestal"},
            "crate": {"unlocked": True, "locked": False},
        },
        "step": 12,
        "termination_reason": "agent_submit",
        "dials": {},
        "relay": {},
        "inventory": [],
        "location": "hall",
    }
    assert StateBasedEvaluator().evaluate(task, done, []).success is True


def test_key_crate_requires_unlocked_crate():
    task = generate_task("key_crate", 1, "train")
    state = {
        "objects": {
            "statue": {"location": "pedestal"},
            "crate": {"unlocked": False, "locked": True},
        },
        "step": 12,
        "termination_reason": "agent_submit",
        "dials": {},
        "relay": {},
        "inventory": [],
        "location": "hall",
    }
    # Even if statue somehow on pedestal, locked crate goal flag must hold.
    goal = dict(task.hidden_goal)
    assert goal.get("crate_unlocked") is True
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_relay_predicate():
    task = generate_task("relay_route", 1, "held_out")
    freq = task.hidden_goal["frequency"]
    relay_obj = {"relay": {"type": "relay", "location": "hub"}}
    bad = {
        "relay": {"activated": True, "frequency": (freq % 7) + 1},
        "objects": relay_obj,
        "step": 9,
        "termination_reason": "agent_submit",
        "dials": {},
        "inventory": [],
        "location": "hub",
    }
    assert StateBasedEvaluator().evaluate(task, bad, []).success is False

    good = {
        "relay": {"activated": True, "frequency": freq},
        "objects": relay_obj,
        "step": 10,
        "termination_reason": "agent_submit",
        "dials": {},
        "inventory": [],
        "location": "hub",
    }
    assert StateBasedEvaluator().evaluate(task, good, []).success is True


def test_error_termination_fails_closed():
    task = generate_task("dial_set", 1, "train")
    targets = dict(task.hidden_goal["targets"])
    # Goal state but terminated as error → must not count as success.
    state = {
        "dials": targets,
        "step": 3,
        "termination_reason": "error",
        "objects": {},
        "relay": {},
        "inventory": [],
        "location": "console",
    }
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_mock_episode_scores_match_environment_state():
    task = generate_task("key_crate", 2, "train")
    g = make_genome()
    ok, trace, payload = run_episode(task, g, seed=2)
    final_state = payload["final_state"]
    re_eval = StateBasedEvaluator().evaluate(task, final_state, trace.steps)
    assert re_eval.success == ok
    # Success iff statue on pedestal and crate unlocked.
    obj = final_state["objects"]
    assert ok == (obj["statue"]["location"] == "pedestal" and obj["crate"]["unlocked"])
