"""Project-owned controlled DE with live trajectory → controller hooks.

Metric semantics (P0-R1-Corrective):
- ``raw_objective``: the true problem.eval value (minimization).
- ``regret`` / official DE ``cost``: raw_objective - problem.optimum when
  optimum is known; otherwise None and only raw_objective is reported.
- Controller state NEVER receives optimum or any evaluation-side hidden value.

FE accounting: independent counter wraps problem.eval; algorithm reports its
own count. Both are recorded separately.

Feature units (generation-level, documented):
- improvement_rate: relative best improvement over the last generation
  ((best[t-1]-best[t]) / max(|best[t-1]|,eps)), unitless.
- stagnation_steps: number of consecutive generations with no best improvement.
- success_fraction: successes / attempted of the **previous** generation
  (0.0 before the first generation).
- population_diversity: mean per-dimension std of the population.
- budget_fraction: fes_used / max_fes.
- generation: 0-based generation index at controller call time.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

import numpy as np


@dataclass
class ControlledDEResult:
    cost_curve: List[float]  # raw best-so-far objective (minimization)
    regret_curve: Optional[List[float]]
    fes: int
    independent_fes: int
    init_fes: int
    max_fes: int
    action_events: List[Dict[str, Any]]
    applied_F_history: List[float]
    applied_CR_history: List[float]
    best_raw_objective: float
    best_regret: Optional[float]
    objective_direction: str = "minimize"
    primary_metric: str = "raw_objective"
    optimum: Optional[float] = None

    def to_manifest_dict(self) -> Dict[str, Any]:
        return {
            "cost_curve": self.cost_curve,
            "regret_curve": self.regret_curve,
            "fes": self.fes,
            "independent_fes": self.independent_fes,
            "init_fes": self.init_fes,
            "max_fes": self.max_fes,
            "action_events": self.action_events,
            "applied_F_history": self.applied_F_history,
            "applied_CR_history": self.applied_CR_history,
            "best_raw_objective": self.best_raw_objective,
            "best_regret": self.best_regret,
            "objective_direction": self.objective_direction,
            "primary_metric": self.primary_metric,
            "optimum": self.optimum,
        }


def _features(
    *,
    generation: int,
    best_history: List[float],
    diversity: float,
    prev_success_fraction: float,
    budget_fraction: float,
    cur_F: float = 0.5,
    cur_Cr: float = 0.5,
) -> Dict[str, float]:
    if len(best_history) >= 2 and abs(best_history[-2]) > 1e-12:
        improvement_rate = max(0.0, (best_history[-2] - best_history[-1]) / abs(best_history[-2]))
    elif len(best_history) >= 2:
        improvement_rate = 1.0 if best_history[-1] < best_history[-2] else 0.0
    else:
        improvement_rate = 0.0
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
        "success_fraction": float(prev_success_fraction),
        "budget_fraction": float(budget_fraction),
        "best": float(best_history[-1]),
        "F": float(cur_F),
        "CR": float(cur_Cr),
    }


def _diversity(pop: np.ndarray) -> float:
    if pop.size == 0:
        return 0.0
    return float(np.mean(np.std(pop, axis=0)))


def _apply_to_state(action: Mapping[str, Any]) -> Dict[str, Any]:
    name = action.get("action")
    params = action.get("params") or {}
    if name == "set_F":
        return {"applied": "set_F", "F": float(params["value"])}
    if name == "set_CR":
        return {"applied": "set_CR", "Cr": float(params["value"])}
    if name == "noop":
        return {"applied": "noop"}
    if name in {"set_mutation_strategy", "restart"}:
        raise RuntimeError(f"controlled_de does not execute {name!r} yet")
    raise RuntimeError(f"unknown action: {name!r}")


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
    if max_fes < np_size:
        raise ValueError(f"max_fes={max_fes} must be >= np_size={np_size}")

    nprng = np.random.RandomState(seed)
    problem.reset()
    dim = int(problem.dim)
    lb = float(problem.lb) if np.isscalar(problem.lb) else float(np.min(problem.lb))
    ub = float(problem.ub) if np.isscalar(problem.ub) else float(np.max(problem.ub))

    independent = {"count": 0}
    original_eval = problem.eval

    def counting_eval(x):
        arr = x if isinstance(x, np.ndarray) else np.asarray(x)
        n = 1 if arr.ndim == 1 else int(arr.shape[0])
        independent["count"] += n
        return original_eval(x)

    problem.eval = counting_eval  # type: ignore[method-assign]

    optimum = getattr(problem, "optimum", None)
    if isinstance(optimum, np.ndarray):
        optimum = float(optimum.reshape(-1)[0]) if optimum.size == 1 else None
    elif optimum is not None:
        optimum = float(optimum)

    try:
        pop = nprng.uniform(lb, ub, size=(np_size, dim))
        # Use the counting wrapper for ALL evaluations (init + loop).
        fitness = np.asarray([counting_eval(ind) for ind in pop], dtype=np.float64)
        fes = np_size
        init_fes = np_size
        best_history = [float(np.min(fitness))]
        events: List[Dict[str, Any]] = []
        F_hist: List[float] = []
        CR_hist: List[float] = []
        cur_F = float(F)
        cur_Cr = float(Cr)
        prev_success_fraction = 0.0

        generation = 0
        while fes < max_fes:
            budget_fraction = fes / float(max_fes)
            state = _features(
                generation=generation,
                best_history=best_history,
                diversity=_diversity(pop),
                prev_success_fraction=prev_success_fraction,
                budget_fraction=budget_fraction,
                cur_F=cur_F,
                cur_Cr=cur_Cr,
            )
            action = controller.select_action(state)
            effect = _apply_to_state(action)
            if effect["applied"] == "set_F":
                cur_F = float(effect["F"])
            elif effect["applied"] == "set_CR":
                cur_Cr = float(effect["Cr"])
            F_hist.append(cur_F)
            CR_hist.append(cur_Cr)
            events.append(
                {
                    "step": generation,
                    "state": dict(state),
                    "action": dict(action),
                    "effect": dict(effect),
                    "F_used": cur_F,
                    "CR_used": cur_Cr,
                }
            )

            successes = 0
            attempted = 0
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
                trial_f = float(counting_eval(trial))
                fes += 1
                attempted += 1
                if trial_f < fitness[i]:
                    pop[i] = trial
                    fitness[i] = trial_f
                    successes += 1
                if float(np.min(fitness)) < best_history[-1]:
                    best_history.append(float(np.min(fitness)))
                else:
                    best_history.append(best_history[-1])

            prev_success_fraction = float(successes) / float(attempted) if attempted else 0.0
            events[-1]["successes"] = successes
            events[-1]["attempted"] = attempted
            events[-1]["success_fraction_this_gen"] = prev_success_fraction
            events[-1]["best_after"] = best_history[-1]
            events[-1]["fes_after"] = fes
            generation += 1

        raw_best = float(best_history[-1])
        regret_curve = None
        best_regret = None
        primary = "raw_objective"
        if optimum is not None:
            regret_curve = [float(y - optimum) for y in best_history]
            best_regret = float(raw_best - optimum)
            primary = "regret"
        return ControlledDEResult(
            cost_curve=best_history,
            regret_curve=regret_curve,
            fes=fes,
            independent_fes=independent["count"],
            init_fes=init_fes,
            max_fes=max_fes,
            action_events=events,
            applied_F_history=F_hist,
            applied_CR_history=CR_hist,
            best_raw_objective=raw_best,
            best_regret=best_regret,
            primary_metric=primary,
            optimum=optimum,
        )
    finally:
        problem.eval = original_eval  # type: ignore[method-assign]
