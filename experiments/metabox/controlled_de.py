"""Project-owned controlled DE with live trajectory → controller hooks.

Official MetaBox DE is untouched and used as the baseline. This loop:
- computes observable search-state features each generation;
- calls the typed controller at a documented cadence (every generation);
- applies supported actions to real F/CR used by mutation/crossover;
- records every state/action/effect event.

Unsupported actions (mutation_strategy, restart) are rejected at runtime.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np


@dataclass
class ControlledDEResult:
    cost_curve: List[float]
    fes: int
    action_events: List[Dict[str, Any]]
    applied_F_history: List[float]
    applied_CR_history: List[float]
    best_cost: float
    objective_direction: str = "minimize"


def _features(
    *,
    generation: int,
    best_history: List[float],
    diversity: float,
    success_fraction: float,
    budget_fraction: float,
) -> Dict[str, float]:
    if len(best_history) >= 2 and best_history[-2] != 0:
        improvement_rate = max(0.0, (best_history[-2] - best_history[-1]) / abs(best_history[-2]))
    else:
        improvement_rate = 1.0 if len(best_history) <= 1 else 0.0
    stagnation = 0
    for i in range(len(best_history) - 1, 0, -1):
        if best_history[i - 1] - best_history[i] > 1e-12:
            break
        stagnation += 1
    return {
        "generation": float(generation),
        "improvement_rate": float(improvement_rate),
        "stagnation_steps": float(stagnation),
        "population_diversity": float(diversity),
        "success_fraction": float(success_fraction),
        "budget_fraction": float(budget_fraction),
    }


def _diversity(pop: np.ndarray) -> float:
    if pop.size == 0:
        return 0.0
    return float(np.mean(np.std(pop, axis=0)))


def run_controlled_de(
    problem,
    controller,
    *,
    max_fes: int,
    seed: int,
    np_size: int = 20,
    F: float = 0.5,
    Cr: float = 0.5,
) -> ControlledDEResult:
    """Minimization DE (rand/1/bin) with per-generation controller hook."""
    rng = random.Random(seed)
    nprng = np.random.RandomState(seed)
    problem.reset()
    dim = int(problem.dim)
    lb = float(problem.lb) if np.isscalar(problem.lb) else float(np.min(problem.lb))
    ub = float(problem.ub) if np.isscalar(problem.ub) else float(np.max(problem.ub))

    pop = nprng.uniform(lb, ub, size=(np_size, dim))
    fitness = np.asarray([problem.eval(ind) for ind in pop], dtype=np.float64)
    fes = np_size
    best_idx = int(np.argmin(fitness))
    best_history = [float(np.min(fitness))]
    events: List[Dict[str, Any]] = []
    F_hist: List[float] = []
    CR_hist: List[float] = []

    cur_F = float(F)
    cur_Cr = float(Cr)

    generation = 0
    while fes < max_fes:
        budget_fraction = fes / float(max_fes)
        state = _features(
            generation=generation,
            best_history=best_history,
            diversity=_diversity(pop),
            success_fraction=0.0,
            budget_fraction=budget_fraction,
        )
        action = controller.select_action(state)
        effect = _apply_to_state(action)
        if effect["applied"] == "set_F":
            cur_F = float(effect["F"])
        elif effect["applied"] == "set_CR":
            cur_Cr = float(effect["Cr"])
        events.append({"step": generation, "state": state, "action": action, "effect": effect})
        F_hist.append(cur_F)
        CR_hist.append(cur_Cr)

        successes = 0
        for i in range(np_size):
            if fes >= max_fes:
                break
            idxs = [j for j in range(np_size) if j != i]
            a, b, c = nprng.choice(idxs, size=3, replace=False)
            mutant = pop[a] + cur_F * (pop[b] - pop[c])
            mutant = np.clip(mutant, lb, ub)
            cross = nprng.rand(dim) < cur_Cr
            cross[nprng.randint(dim)] = True
            trial = np.where(cross, mutant, pop[i])
            trial_f = float(problem.eval(trial))
            fes += 1
            if trial_f < fitness[i]:
                pop[i] = trial
                fitness[i] = trial_f
                successes += 1
            if np.min(fitness) < best_history[-1]:
                best_history.append(float(np.min(fitness)))
            else:
                best_history.append(best_history[-1])
        state2 = _features(
            generation=generation,
            best_history=best_history,
            diversity=_diversity(pop),
            success_fraction=successes / float(np_size),
            budget_fraction=fes / float(max_fes),
        )
        events[-1]["state_after"] = state2
        events[-1]["success_fraction"] = state2["success_fraction"]
        generation += 1

    return ControlledDEResult(
        cost_curve=best_history,
        fes=fes,
        action_events=events,
        applied_F_history=F_hist,
        applied_CR_history=CR_hist,
        best_cost=float(best_history[-1]),
    )


def _apply_to_state(action: Mapping[str, Any]) -> Dict[str, Any]:
    name = action.get("action")
    params = action.get("params") or {}
    if name == "set_F":
        return {"applied": "set_F", "F": float(params["value"])}
    if name == "set_CR":
        return {"applied": "set_CR", "Cr": float(params["value"])}
    if name == "noop":
        return {"applied": "noop"}
    if name == "set_mutation_strategy":
        # Controlled DE currently implements rand/1/bin only; surface as recorded
        # but not silently fake a switch — reject to stay fail-closed.
        raise RuntimeError(f"controlled_de does not execute {name!r} yet")
    if name == "restart":
        raise RuntimeError(f"controlled_de does not execute {name!r} yet")
    raise RuntimeError(f"unknown action: {name!r}")
