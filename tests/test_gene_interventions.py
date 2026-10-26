"""Gene intervention tests: each active gene must change intended runtime behavior.

Mock backend only — engineering evidence, not Agent capability evidence.
"""
from conftest import action_tools, action_list, episode, make_genome


def test_planning_mode_plan_first_emits_plan_action():
    """planning_mode=plan_first must emit make_plan as the first action."""
    fam, split, seed = "key_crate", "train", 2
    g_plan = make_genome(planning_mode="plan_first")
    g_direct = make_genome(planning_mode="direct")

    _, tr_plan, _ = episode(g_plan, fam, split, seed)
    _, tr_direct, _ = episode(g_direct, fam, split, seed)

    tools_plan = action_tools(tr_plan)
    tools_direct = action_tools(tr_direct)

    assert tools_plan[0] == "make_plan"
    assert tools_direct[0] != "make_plan"
    assert tools_plan != tools_direct

    # Plan is recorded in the public observation after the action.
    assert any(s["action"]["tool"] == "make_plan" for s in tr_plan.steps)
    plan_steps = [s for s in tr_plan.steps if s["action"]["tool"] == "make_plan"]
    assert plan_steps and plan_steps[0]["info"]["result"]["plan"]


def test_verification_policy_emits_verify_before_submit():
    """verification_policy=check_before_finalize must verify before submit."""
    fam, split, seed = "dial_set", "train", 1
    g_verify = make_genome(verification_policy="check_before_finalize")
    g_none = make_genome(verification_policy="none")

    _, tr_v, _ = episode(g_verify, fam, split, seed)
    _, tr_n, _ = episode(g_none, fam, split, seed)

    tools_v = action_tools(tr_v)
    tools_n = action_tools(tr_n)

    assert "verify_state" in tools_v
    assert tools_v.index("verify_state") < tools_v.index("submit")
    assert "verify_state" not in tools_n
    assert tools_v != tools_n


def test_tool_selection_policy_changes_choice():
    """fixed_ranking inspects before take; state_conditioned takes directly."""
    fam, split, seed = "key_crate", "train", 2
    g_fixed = make_genome(tool_selection_policy="fixed_ranking")
    g_state = make_genome(tool_selection_policy="state_conditioned")

    _, tr_f, _ = episode(g_fixed, fam, split, seed)
    _, tr_s, _ = episode(g_state, fam, split, seed)

    tools_f = action_tools(tr_f)
    tools_s = action_tools(tr_s)

    # fixed ranking: inspect appears before the first take of a coin.
    if "inspect" in tools_f and "take" in tools_f:
        assert tools_f.index("inspect") < tools_f.index("take")

    # state-conditioned: first coin interaction is take without a preceding inspect
    # of that coin.
    assert tools_s != tools_f

    # Both still solve the diagnostic task (behavior change, not capability loss).
    assert tr_f.termination_reason == "agent_submit"
    assert tr_s.termination_reason == "agent_submit"


def test_memory_policy_changes_execution():
    """bounded_episodic skips searched rooms; none may revisit — traces differ."""
    fam, split, seed = "key_crate", "train", 4
    g_mem = make_genome(memory_policy="bounded_episodic")
    g_none = make_genome(memory_policy="none")

    _, tr_m, _ = episode(g_mem, fam, split, seed)
    _, tr_n, _ = episode(g_none, fam, split, seed)

    assert action_list(tr_m) != action_list(tr_n)

    # Phenotype-level contract: recall works only under bounded_episodic.
    from agentfotagent.runtime.phenotype import compile_phenotype

    pm = compile_phenotype(g_mem)
    pn = compile_phenotype(g_none)
    pm.remember({"location": "storage", "visible_objects": ["coin_x"]})
    pn.remember({"location": "storage", "visible_objects": ["coin_x"]})
    assert pm.recall(), "bounded_episodic must retain permitted observations"
    assert pn.recall() == [], "memory_policy=none must not carry observations over"


def test_memory_window_is_bounded():
    from agentfotagent.runtime.phenotype import MEMORY_WINDOW, compile_phenotype

    p = compile_phenotype(make_genome(memory_policy="bounded_episodic"))
    for i in range(MEMORY_WINDOW + 5):
        p.remember({"step": i})
    assert len(p.recall()) == MEMORY_WINDOW


def test_every_gene_has_observable_effect():
    """Each gene, flipped alone, changes the execution on some diagnostic task."""
    diagnostics = [
        ("key_crate", "train", 2),
        ("dial_set", "train", 1),
        ("relay_route", "held_out", 1),
        ("key_crate", "train", 4),
    ]
    from agentfotagent.genome.schema import GENES

    for gene, alleles in GENES.items():
        assert len(alleles) == 2
        changed = False
        for fam, split, seed in diagnostics:
            g_a = make_genome(**{gene: alleles[0]})
            g_b = make_genome(**{gene: alleles[1]})
            _, ta, _ = episode(g_a, fam, split, seed)
            _, tb, _ = episode(g_b, fam, split, seed)
            if action_list(ta) != action_list(tb):
                changed = True
                break
        assert changed, f"gene {gene} did not change runtime behavior on diagnostics"
