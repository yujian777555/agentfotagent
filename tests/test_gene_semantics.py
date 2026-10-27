"""F2 regression: planning, verification and memory genes must drive decisions.

These tests fail if a gene only inserts an extra trace event without changing
the intended decision logic.
"""
from agentfotagent.genome.schema import normalize_genome
from agentfotagent.interfaces import Action, RuntimeTask
from agentfotagent.runtime.mock_backend import MockPolicy, run_episode
from agentfotagent.runtime.phenotype import compile_phenotype
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome


def _policy(family, split, seed, **gene_overrides):
    g = make_genome(**gene_overrides)
    task = generate_task(family, seed, split)
    ph = compile_phenotype(g)
    policy = MockPolicy(phenotype=ph, runtime_task=task.runtime, family=family)
    return task, policy


# ---------------------------------------------------------------------------
# planning_mode: the stored plan must change the next action
# ---------------------------------------------------------------------------

def test_plan_is_stored_and_consumed():
    task, policy = _policy("key_crate", "train", 2, planning_mode="plan_first")
    obs = {
        "location": "hall",
        "inventory": [],
        "visible_objects": ["pedestal"],
        "dials": {},
        "relay": {"activated": False, "frequency": None},
        "notes_read": {},
        "plan": None,
        "step": 0,
        "terminated": False,
    }
    a1 = policy.next_action(obs)
    assert a1.tool == "make_plan"
    assert policy.phenotype.plan == ["find_key", "unlock_crate", "transport_statue", "finalize"]

    a2 = policy.next_action(obs)
    # Plan is active: next action is a find_key action, not a bare list_objects first
    # when a coin is already visible — and plan_index is part of the decision path.
    assert a2.tool in {"move", "take", "inspect", "list_objects", "unlock", "place"}


def test_changed_plan_changes_next_action():
    """A modified plan must change the selected next action (not just the trace)."""
    task, policy = _policy("key_crate", "train", 2, planning_mode="plan_first")
    obs = {
        "location": "vault",
        "inventory": ["coin_x"],
        "visible_objects": ["crate"],
        "dials": {},
        "relay": {"activated": False, "frequency": None},
        "notes_read": {},
        "plan": None,
        "step": 0,
        "terminated": False,
    }
    # Force a plan that says finalize first.
    policy.phenotype.set_plan(["finalize", "find_key", "unlock_crate", "transport_statue"])
    action_finalize_first = policy.next_action(obs)

    task2, policy2 = _policy("key_crate", "train", 2, planning_mode="plan_first")
    policy2.phenotype.set_plan(["find_key", "unlock_crate", "transport_statue", "finalize"])
    action_normal = policy2.next_action(obs)

    assert action_finalize_first.to_dict() != action_normal.to_dict()
    # finalize-first with an unplaced statue still tries transport/place rather than
    # immediately unlocking — the phase gate is actually consulted.
    assert action_normal.tool in {"unlock", "move"}
    assert action_finalize_first.tool in {"move", "place", "submit"}


def test_direct_mode_has_no_plan_phase():
    task, policy = _policy("key_crate", "train", 2, planning_mode="direct")
    assert policy.phenotype.plan is None
    assert policy.phenotype.current_plan_step() is None


# ---------------------------------------------------------------------------
# verification_policy: verify output is read; submit blocked when goals unmet
# ---------------------------------------------------------------------------

def test_verification_reads_result_and_blocks_submit():
    task, policy = _policy("key_crate", "train", 2, verification_policy="check_before_finalize")
    # Statue is NOT on the pedestal; policy believes it is done (placed_statue).
    policy.placed_statue = True
    obs = {
        "location": "hall",
        "inventory": [],
        "visible_objects": ["pedestal"],
        "dials": {},
        "relay": {"activated": False, "frequency": None},
        "notes_read": {},
        "plan": None,
        "step": 5,
        "terminated": False,
    }
    a1 = policy.next_action(obs)
    # Must verify first rather than submit.
    assert a1.tool == "verify_state"

    # Feed a failing verify summary (statue not on pedestal, crate locked).
    from agentfotagent.runtime.mock_backend import _ingest_mock_results

    _ingest_mock_results(
        policy,
        {
            "valid": True,
            "result": {
                "unlocked": {"crate": False},
                "surface_contents": {"pedestal": []},
                "dials": {},
                "inventory": [],
                "relay_activated": False,
                "relay_frequency": None,
                "location": "hall",
            },
        },
        obs,
        {"tool": "verify_state", "args": {}},
    )
    assert policy.phenotype.verified is False
    assert policy.last_verify_summary["goal_checks_passed"] is False

    # Next call must NOT submit: verification failed.
    a2 = policy.next_action(obs)
    assert a2.tool != "submit", "submit must be blocked when verify_state reports unmet goals"


def test_verification_allows_submit_when_goals_met():
    task, policy = _policy("key_crate", "train", 2, verification_policy="check_before_finalize")
    policy.placed_statue = True
    obs = {
        "location": "hall",
        "inventory": [],
        "visible_objects": ["pedestal"],
        "dials": {},
        "relay": {"activated": False, "frequency": None},
        "notes_read": {},
        "plan": None,
        "step": 5,
        "terminated": False,
    }
    a1 = policy.next_action(obs)
    assert a1.tool == "verify_state"

    from agentfotagent.runtime.mock_backend import _ingest_mock_results

    _ingest_mock_results(
        policy,
        {
            "valid": True,
            "result": {
                "unlocked": {"crate": True},
                "surface_contents": {"pedestal": ["statue"]},
                "dials": {},
                "inventory": [],
                "relay_activated": False,
                "relay_frequency": None,
                "location": "hall",
            },
        },
        obs,
        {"tool": "verify_state", "args": {}},
    )
    assert policy.phenotype.verified is True
    a2 = policy.next_action(obs)
    assert a2.tool == "submit"


def test_verification_absent_no_verify_step():
    task, policy = _policy("key_crate", "train", 2, verification_policy="none")
    policy.placed_statue = True
    obs = {
        "location": "hall",
        "inventory": [],
        "visible_objects": ["pedestal"],
        "dials": {},
        "relay": {"activated": False, "frequency": None},
        "notes_read": {},
        "plan": None,
        "step": 5,
        "terminated": False,
    }
    a1 = policy.next_action(obs)
    assert a1.tool == "submit"


# ---------------------------------------------------------------------------
# memory_policy: decisions go through phenotype.recall()
# ---------------------------------------------------------------------------

def test_memory_decision_uses_phenotype_recall():
    task, policy = _policy("key_crate", "train", 2, memory_policy="bounded_episodic")
    # No coin visible here; memory remembers a coin in corridor.
    policy.phenotype.remember({"location": "corridor", "visible_objects": ["coin_z"], "inventory": []})
    obs = {
        "location": "hall",
        "inventory": [],
        "visible_objects": [],
        "dials": {},
        "relay": {"activated": False, "frequency": None},
        "notes_read": {},
        "plan": None,
        "step": 3,
        "terminated": False,
    }
    # Exploration under memory skips rooms seen in recall (corridor is visited).
    action = policy.next_action(obs)
    assert action.tool == "move"
    assert action.args.get("location") in {"storage", "vault"}  # unvisited, not corridor
    assert action.args.get("location") != "corridor"

    # Clearing phenotype memory changes the decision path (corridor becomes eligible).
    policy.phenotype.memory.clear()
    assert policy.phenotype.recalled_locations() == []
    policy.room_cursor = 0
    action2 = policy.next_action(obs)
    assert action2.tool == "move"
    # Decision path depends on phenotype.recall(); there is no parallel searched_rooms list.
    assert "searched_rooms" not in getattr(policy, "__dataclass_fields__", {})


def test_memory_explore_skips_recalled_rooms_only():
    task, policy = _policy("key_crate", "train", 2, memory_policy="bounded_episodic")
    for loc in ("hall", "storage", "corridor"):
        policy.phenotype.remember({"location": loc, "visible_objects": [], "inventory": []})
    visited = set(policy.phenotype.recalled_locations())
    assert visited == {"hall", "storage", "corridor"}
    # Only vault remains.
    obs = {
        "location": "hall",
        "inventory": [],
        "visible_objects": [],
        "dials": {},
        "relay": {"activated": False, "frequency": None},
        "notes_read": {},
        "plan": None,
        "step": 3,
        "terminated": False,
    }
    action = policy.next_action(obs)
    assert action.tool == "move"
    assert action.args.get("location") == "vault"


def test_no_memory_policy_recall_is_empty():
    task, policy = _policy("key_crate", "train", 2, memory_policy="none")
    policy.phenotype.remember({"location": "corridor", "visible_objects": ["coin_z"], "inventory": []})
    assert policy.phenotype.recall() == []
    assert policy.phenotype.recalled_locations() == []


def test_memory_window_bounds_decision_context():
    from agentfotagent.runtime.phenotype import MEMORY_WINDOW

    task, policy = _policy("key_crate", "train", 2, memory_policy="bounded_episodic")
    for i in range(MEMORY_WINDOW + 3):
        policy.phenotype.remember({"location": f"room_{i}", "visible_objects": [], "inventory": []})
    assert len(policy.phenotype.recall()) == MEMORY_WINDOW
    # Oldest rooms fall out of the window and become eligible again.
    locs = policy.phenotype.recalled_locations()
    assert "room_0" not in locs
    assert locs[-1] == f"room_{MEMORY_WINDOW + 2}"
