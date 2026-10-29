"""Phase-1A-8 Stage B: 2x2 factorial — archive × boundary repair.

Four arms:
  A0: standard archive + clip            (must match lshade_canonical exactly)
  A1: no archive (empty donor pool) + clip
  A2: standard archive + parent-midpoint repair
  A3: no archive + parent-midpoint repair

parent-midpoint repair: out-of-bounds coordinate j is set to
  (bound_j + parent_j) / 2  where bound_j = lb or ub as appropriate.

No LLM. No validation/test. Train split only.
algorithm_id: lshade-factorial
provenance:    canonical_reimplementation; not official code
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from .lshade_canonical import (
    linear_n_target,
    sample_cr,
    sample_f,
    select_r1_r2,
    update_memory,
)


@dataclass
class FactorialResult:
    raw_curve: List[float]
    benchmark_cost_curve: List[float]
    regret_curve: Optional[List[float]]
    fes: int
    independent_fes: int
    max_fes: int
    n_history: List[int]
    best_raw: float
    best_benchmark_cost: float
    best_regret: Optional[float]
    optimum: Optional[float]
    optimum_is_lower_bound: bool
    arm_id: str
    use_archive: bool
    repair_method: str
    algorithm_id: str = "lshade-factorial"
    provenance: str = "canonical_reimplementation; not official code"
    fe_exact: bool = True
    # boundary stats
    total_trials: int = 0
    total_oob_trials: int = 0
    total_archive_r2: int = 0
    total_pop_r2: int = 0
    total_success: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_curve": self.raw_curve,
            "benchmark_cost_curve": self.benchmark_cost_curve,
            "regret_curve": self.regret_curve,
            "fes": self.fes,
            "independent_fes": self.independent_fes,
            "max_fes": self.max_fes,
            "n_history": self.n_history,
            "best_raw": self.best_raw,
            "best_benchmark_cost": self.best_benchmark_cost,
            "best_regret": self.best_regret,
            "optimum": self.optimum,
            "optimum_is_lower_bound": self.optimum_is_lower_bound,
            "arm_id": self.arm_id,
            "use_archive": self.use_archive,
            "repair_method": self.repair_method,
            "algorithm_id": self.algorithm_id,
            "provenance": self.provenance,
            "fe_exact": self.fe_exact,
            "total_trials": self.total_trials,
            "total_oob_trials": self.total_oob_trials,
            "total_archive_r2": self.total_archive_r2,
            "total_pop_r2": self.total_pop_r2,
            "total_success": self.total_success,
        }


def _repair_clip(mutant: np.ndarray, lb: float, ub: float, parent: np.ndarray) -> np.ndarray:
    return np.clip(mutant, lb, ub)


def _repair_parent_midpoint(
    mutant: np.ndarray, lb: float, ub: float, parent: np.ndarray
) -> np.ndarray:
    out = mutant.copy()
    lo_mask = out < lb
    hi_mask = out > ub
    out[lo_mask] = (lb + parent[lo_mask]) / 2.0
    out[hi_mask] = (ub + parent[hi_mask]) / 2.0
    return out


REPAIR_FN = {
    "clip": _repair_clip,
    "parent_midpoint": _repair_parent_midpoint,
}


def run_lshade_factorial(
    problem,
    *,
    max_fes: int,
    seed: int,
    use_archive: bool = True,
    repair_method: str = "clip",
    n_init: int = 100,
    n_min: int = 4,
    h_memory: int = 5,
    p_best: float = 0.1,
) -> FactorialResult:
    if repair_method not in REPAIR_FN:
        raise ValueError(f"unknown repair_method: {repair_method}")
    if max_fes < n_init:
        raise ValueError("max_fes must be >= n_init")

    repair_fn = REPAIR_FN[repair_method]
    rng = np.random.RandomState(seed)
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

    problem.eval = counting  # type: ignore[attr-defined]

    optimum = getattr(problem, "optimum", None)
    if isinstance(optimum, np.ndarray):
        optimum = float(optimum.reshape(-1)[0]) if optimum.size == 1 else None
    elif optimum is not None:
        optimum = float(optimum)

    N = int(n_init)
    archive: List[np.ndarray] = []
    M_F = [0.5] * h_memory
    M_CR = [0.5] * h_memory
    k_pos = 0

    total_trials = 0
    total_oob_trials = 0
    total_arch_r2 = 0
    total_pop_r2 = 0
    total_success = 0

    try:
        pop = rng.uniform(lb, ub, size=(N, dim))
        fit = np.asarray([counting(ind) for ind in pop], dtype=np.float64)
        fes = N
        raw_hist = [float(np.min(fit))]
        n_hist = [N]

        while fes < max_fes:
            n_target = linear_n_target(n_init, n_min, fes, max_fes)
            if n_target < N:
                keep = np.argsort(fit)[:n_target]
                pop = pop[keep].copy()
                fit = fit[keep].copy()
                N = n_target
                if len(archive) > N:
                    archive = archive[:N]

            order = rng.permutation(N)
            new_pop = pop.copy()
            new_fit = fit.copy()
            S_F: List[float] = []
            S_CR: List[float] = []
            S_diff: List[float] = []

            for i in order:
                if fes >= max_fes:
                    break
                i = int(i)
                ri = int(rng.randint(h_memory))
                F = sample_f(rng, M_F[ri])
                CR = sample_cr(rng, M_CR[ri])

                n_pbest = max(2, int(N * p_best))
                cand = np.argsort(fit)[:n_pbest]
                p = int(cand[int(rng.randint(len(cand)))])

                if N < 2:
                    continue
                r1, r2 = select_r1_r2(rng, N, len(archive) if use_archive else 0, i)
                r2_from_archive = r2 >= N
                if r2_from_archive:
                    vec_r2 = archive[r2 - N]
                    total_arch_r2 += 1
                else:
                    vec_r2 = pop[r2]
                    total_pop_r2 += 1

                mutant = pop[i] + F * (pop[p] - pop[i]) + F * (pop[r1] - vec_r2)

                # boundary event tracking (before repair)
                oob_mask = (mutant < lb) | (mutant > ub)
                has_oob = bool(np.any(oob_mask))
                if has_oob:
                    total_oob_trials += 1

                mutant = repair_fn(mutant, lb, ub, pop[i])

                cross = rng.rand(dim) < CR
                cross[int(rng.randint(dim))] = True
                trial = np.where(cross, mutant, pop[i])

                tf = float(counting(trial))
                fes += 1
                total_trials += 1

                if tf <= fit[i]:
                    if use_archive:
                        archive.append(pop[i].copy())
                        if len(archive) > N:
                            archive.pop(int(rng.randint(len(archive))))
                    new_pop[i] = trial
                    new_fit[i] = tf
                    S_F.append(F)
                    S_CR.append(CR)
                    S_diff.append(abs(float(fit[i] - tf)))
                    total_success += 1

            pop, fit = new_pop, new_fit
            raw_hist.append(float(np.min(fit)))
            n_hist.append(N)

            if S_F:
                mf, mcr = update_memory(M_F[k_pos], M_CR[k_pos], S_F, S_CR, S_diff)
                M_F[k_pos] = mf
                M_CR[k_pos] = mcr
                k_pos = (k_pos + 1) % h_memory

        best_raw = float(raw_hist[-1])
        if optimum is not None:
            bc_curve = [float(y - optimum) for y in raw_hist]
            best_bc = float(best_raw - optimum)
            lower_ok = all(y >= optimum - 1e-9 for y in raw_hist)
            regret_curve = list(bc_curve) if lower_ok else None
            best_regret = float(best_bc) if lower_ok else None
        else:
            bc_curve = []
            best_bc = float("nan")
            lower_ok = False
            regret_curve = None
            best_regret = None

        arm = f"{'A' if use_archive else 'N'}_{'clip' if repair_method=='clip' else 'mid'}"
        return FactorialResult(
            raw_curve=raw_hist,
            benchmark_cost_curve=bc_curve,
            regret_curve=regret_curve,
            fes=fes,
            independent_fes=indep["n"],
            max_fes=max_fes,
            n_history=n_hist,
            best_raw=best_raw,
            best_benchmark_cost=best_bc,
            best_regret=best_regret,
            optimum=optimum,
            optimum_is_lower_bound=bool(lower_ok),
            arm_id=arm,
            use_archive=use_archive,
            repair_method=repair_method,
            fe_exact=(fes == indep["n"] == max_fes),
            total_trials=total_trials,
            total_oob_trials=total_oob_trials,
            total_archive_r2=total_arch_r2,
            total_pop_r2=total_pop_r2,
            total_success=total_success,
        )
    finally:
        problem.eval = raw_eval  # type: ignore[attr-defined]
