"""Multi-operator DE with mechanism hooks (Phase-1A-2).

Operators: rand/1/bin, current-to-best/1/bin, rand/2/bin, best/1/bin.
All share FE counting and population update. Mechanism selects operator/F/CR
per generation from public state.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class MultiDEResult:
    cost_curve: List[float]
    regret_curve: Optional[List[float]]
    fes: int
    independent_fes: int
    init_fes: int
    max_fes: int
    action_events: List[Dict[str, Any]]
    best_raw_objective: float
    best_regret: Optional[float]
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
            "best_raw_objective": self.best_raw_objective,
            "best_regret": self.best_regret,
            "primary_metric": self.primary_metric,
            "optimum": self.optimum,
        }


def _features(generation, best_history, diversity, prev_succ, budget_frac, op, F, CR):
    if len(best_history) >= 2 and abs(best_history[-2]) > 1e-12:
        imp = max(0.0, (best_history[-2] - best_history[-1]) / abs(best_history[-2]))
    elif len(best_history) >= 2:
        imp = 1.0 if best_history[-1] < best_history[-2] else 0.0
    else:
        imp = 0.0
    stag = 0
    for i in range(len(best_history) - 1, 0, -1):
        if best_history[i - 1] - best_history[i] > 1e-12:
            break
        stag += 1
    return {
        "generation": float(generation),
        "improvement_rate": float(imp),
        "stagnation_steps": float(stag),
        "population_diversity": float(diversity),
        "success_fraction": float(prev_succ),
        "budget_fraction": float(budget_frac),
        "best": float(best_history[-1]),
        "operator": op,
        "F": float(F),
        "CR": float(CR),
    }


def _mutate(op, pop, i, rng_np, F, best_idx):
    n = pop.shape[0]
    idxs = [j for j in range(n) if j != i]
    if op == "rand/1/bin":
        a, b, c = rng_np.choice(idxs, size=3, replace=False)
        return pop[a] + F * (pop[b] - pop[c])
    if op == "current-to-best/1/bin":
        a, b = rng_np.choice(idxs, size=2, replace=False)
        return pop[i] + F * (pop[best_idx] - pop[i]) + F * (pop[a] - pop[b])
    if op == "rand/2/bin":
        a, b, c, d = rng_np.choice(idxs, size=4, replace=False)
        return pop[a] + F * (pop[b] - pop[c]) + F * (pop[d] - pop[a])
    if op == "best/1/bin":
        a, b = rng_np.choice(idxs, size=2, replace=False)
        return pop[best_idx] + F * (pop[a] - pop[b])
    raise ValueError(op)


def run_multi_de(problem, mechanism, *, max_fes: int, seed: int, np_size: int = 20,
                 F: float = 0.5, Cr: float = 0.5) -> MultiDEResult:
    if max_fes < np_size:
        raise ValueError("max_fes < np_size")
    rng_np = np.random.RandomState(seed)
    problem.reset()
    dim = int(problem.dim)
    lb = float(problem.lb) if np.isscalar(problem.lb) else float(np.min(problem.lb))
    ub = float(problem.ub) if np.isscalar(problem.ub) else float(np.max(problem.ub))

    indep = {"n": 0}
    raw_eval = problem.eval

    def counting(x):
        arr = x if isinstance(x, np.ndarray) else np.asarray(x)
        k = 1 if arr.ndim == 1 else int(arr.shape[0])
        indep["n"] += k
        return raw_eval(x)

    problem.eval = counting  # type: ignore

    optimum = getattr(problem, "optimum", None)
    if isinstance(optimum, np.ndarray):
        optimum = float(optimum.reshape(-1)[0]) if optimum.size == 1 else None
    elif optimum is not None:
        optimum = float(optimum)

    try:
        pop = rng_np.uniform(lb, ub, size=(np_size, dim))
        fitness = np.asarray([counting(ind) for ind in pop], dtype=np.float64)
        fes = np_size
        init_fes = np_size
        best_history = [float(np.min(fitness))]
        events: List[Dict[str, Any]] = []
        cur_F, cur_Cr, cur_op = F, Cr, "rand/1/bin"
        prev_succ = 0.0
        gen = 0
        while fes < max_fes:
            budget_frac = fes / float(max_fes)
            state = _features(gen, best_history, float(np.mean(np.std(pop, axis=0))),
                              prev_succ, budget_frac, cur_op, cur_F, cur_Cr)
            act = mechanism.select(state)
            effect = {"applied": act["action"]}
            if act["action"] == "set_operator":
                cur_op = act["params"]["operator"]
                effect["operator"] = cur_op
            elif act["action"] == "set_F":
                cur_F = float(act["params"]["value"]); effect["F"] = cur_F
            elif act["action"] == "set_CR":
                cur_Cr = float(act["params"]["value"]); effect["CR"] = cur_Cr
            elif act["action"] == "inject_diversity":
                # re-sample worst 20%
                order = np.argsort(fitness)
                k = max(1, np_size // 5)
                for j in order[-k:]:
                    pop[j] = rng_np.uniform(lb, ub, size=dim)
                    fitness[j] = float(counting(pop[j]))
                    fes += 1
                effect["resampled"] = int(k)
            events.append({"step": gen, "state": state, "action": act, "effect": effect,
                           "operator": cur_op, "F": cur_F, "CR": cur_Cr})
            successes = 0
            attempted = 0
            best_idx = int(np.argmin(fitness))
            for i in range(np_size):
                if fes >= max_fes:
                    break
                mutant = _mutate(cur_op, pop, i, rng_np, cur_F, best_idx)
                mutant = np.clip(mutant, lb, ub)
                cross = rng_np.rand(dim) < cur_Cr
                cross[rng_np.randint(dim)] = True
                trial = np.where(cross, mutant, pop[i])
                tf = float(counting(trial))
                fes += 1
                attempted += 1
                if tf < fitness[i]:
                    pop[i] = trial
                    fitness[i] = tf
                    successes += 1
                best_history.append(float(min(best_history[-1], np.min(fitness))))
            prev_succ = successes / attempted if attempted else 0.0
            events[-1]["successes"] = successes
            events[-1]["attempted"] = attempted
            events[-1]["success_fraction_this_gen"] = prev_succ
            events[-1]["fes_after"] = fes
            gen += 1

        raw_best = float(best_history[-1])
        regret = None
        best_regret = None
        primary = "raw_objective"
        if optimum is not None:
            regret = [float(y - optimum) for y in best_history]
            best_regret = float(raw_best - optimum)
            primary = "regret"
        return MultiDEResult(
            cost_curve=best_history, regret_curve=regret, fes=fes,
            independent_fes=indep["n"], init_fes=init_fes, max_fes=max_fes,
            action_events=events, best_raw_objective=raw_best, best_regret=best_regret,
            primary_metric=primary, optimum=optimum,
        )
    finally:
        problem.eval = raw_eval  # type: ignore
