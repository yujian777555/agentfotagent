"""Phase-1A-8 Stage A: boundary-event diagnostic runner for canonical L-SHADE.

Extends the Phase-1A-7 diagnostic approach with boundary-event logging.
Does NOT alter search behavior, RNG consumption, or algorithm branches.

Per-trial boundary events recorded (no extra evaluations):
- mutant coordinates out of bounds BEFORE clipping
- out-of-bounds fraction (coords / dim)
- L2 displacement caused by clipping (repair displacement)
- cosine between original search direction and repair displacement
- whether r2 came from population or archive

Per-generation aggregates:
- n_trials, n_out_of_bounds_trials, total_oob_coords
- mean/max repair displacement L2
- mean cosine direction change (for repaired trials)
- n_archive_sourced, n_pop_sourced (for r2)
- successes, attempts, total improvement

algorithm_id: lshade-canonical-boundary-diag
provenance:    canonical_reimplementation; not official code
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .lshade_canonical import (
    linear_n_target,
    sample_cr,
    sample_f,
    select_r1_r2,
    update_memory,
)


BOUNDARY_DEFINITIONS: Dict[str, str] = {
    "fe": "cumulative FE after this generation [count]",
    "gen": "generation index [count]",
    "N": "population size [count]",
    "best": "min objective [raw_objective]",
    "n_trials": "trials attempted this generation [count]",
    "n_oob_trials": "trials with >=1 out-of-bounds mutant coordinate [count]",
    "oob_trial_frac": "n_oob_trials / n_trials [0,1]",
    "total_oob_coords": "sum of out-of-bounds coordinates across trials [count]",
    "oob_coord_frac": "total_oob_coords / (n_trials * dim) [0,1]",
    "mean_repair_L2": "mean L2 of repair displacement over repaired trials [objective units]",
    "max_repair_L2": "max L2 of repair displacement [objective units]",
    "mean_repair_cosine": "mean cosine between search direction and repair displacement [-1,1]",
    "n_archive_r2": "trials where r2 came from archive [count]",
    "n_pop_r2": "trials where r2 came from population [count]",
    "archive_r2_frac": "n_archive_r2 / n_trials [0,1]",
    "successes": "trials that replaced parent [count]",
    "total_improvement": "sum of |parent_fit - trial_fit| for successes [objective units]",
    "n_archive_events": "archive insertions this generation [count]",
    "archive_size": "archive size after generation [count]",
    "repair_success_rate": "success rate among repaired trials [0,1] or -1 if none",
    "no_repair_success_rate": "success rate among non-repaired trials [0,1] or -1 if none",
}


@dataclass
class BoundaryDiagResult:
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
    gen_logs: List[Dict[str, Any]]
    algorithm_id: str = "lshade-canonical-boundary-diag"
    provenance: str = "canonical_reimplementation; not official code"
    fe_exact: bool = True

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
            "gen_logs": self.gen_logs,
            "algorithm_id": self.algorithm_id,
            "provenance": self.provenance,
            "fe_exact": self.fe_exact,
            "boundary_definitions": BOUNDARY_DEFINITIONS,
        }


def run_lshade_boundary_diag(
    problem,
    *,
    max_fes: int,
    seed: int,
    n_init: int = 100,
    n_min: int = 4,
    h_memory: int = 5,
    p_best: float = 0.1,
) -> BoundaryDiagResult:
    """Instrumented canonical L-SHADE with boundary-event logging."""
    if max_fes < n_init:
        raise ValueError("max_fes must be >= n_init")

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

    try:
        pop = rng.uniform(lb, ub, size=(N, dim))
        fit = np.asarray([counting(ind) for ind in pop], dtype=np.float64)
        fes = N
        raw_hist = [float(np.min(fit))]
        n_hist = [N]
        gen_logs: List[Dict[str, Any]] = []
        gen = 0

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

            # boundary diagnostic accumulators
            n_trials = 0
            n_oob_trials = 0
            total_oob_coords = 0
            repair_L2s: List[float] = []
            repair_cosines: List[float] = []
            n_archive_r2 = 0
            n_pop_r2 = 0
            n_successes = 0
            total_improvement = 0.0
            n_archive_inserts = 0
            repaired_successes = 0
            repaired_count = 0
            unrepaired_successes = 0
            unrepaired_count = 0

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
                r1, r2 = select_r1_r2(rng, N, len(archive), i)
                r2_from_archive = r2 >= N
                if r2_from_archive:
                    vec_r2 = archive[r2 - N]
                    n_archive_r2 += 1
                else:
                    vec_r2 = pop[r2]
                    n_pop_r2 += 1

                mutant = pop[i] + F * (pop[p] - pop[i]) + F * (pop[r1] - vec_r2)

                # ---- boundary event logging (before clipping) ----
                oob_mask = (mutant < lb) | (mutant > ub)
                n_oob = int(np.sum(oob_mask))
                if n_oob > 0:
                    n_oob_trials += 1
                    total_oob_coords += n_oob
                    clipped = np.clip(mutant, lb, ub)
                    repair_disp = clipped - mutant
                    repair_L2 = float(np.linalg.norm(repair_disp))
                    repair_L2s.append(repair_L2)
                    # cosine between search direction (mutant - parent) and repair displacement
                    search_dir = mutant - pop[i]
                    search_L2 = float(np.linalg.norm(search_dir))
                    if search_L2 > 1e-12 and repair_L2 > 1e-12:
                        cos_sim = float(np.dot(search_dir, repair_disp) / (search_L2 * repair_L2))
                        repair_cosines.append(cos_sim)
                    mutant = clipped
                    was_repaired = True
                else:
                    was_repaired = False

                cross = rng.rand(dim) < CR
                cross[int(rng.randint(dim))] = True
                trial = np.where(cross, mutant, pop[i])

                tf = float(counting(trial))
                fes += 1
                n_trials += 1

                if tf <= fit[i]:
                    archive.append(pop[i].copy())
                    if len(archive) > N:
                        archive.pop(int(rng.randint(len(archive))))
                    new_pop[i] = trial
                    new_fit[i] = tf
                    S_F.append(F)
                    S_CR.append(CR)
                    S_diff.append(abs(float(fit[i] - tf)))
                    n_successes += 1
                    n_archive_inserts += 1
                    total_improvement += abs(float(fit[i] - tf))

                if was_repaired:
                    repaired_count += 1
                    if tf <= fit[i]:
                        repaired_successes += 1
                else:
                    unrepaired_count += 1
                    if tf <= fit[i]:
                        unrepaired_successes += 1

            pop, fit = new_pop, new_fit
            raw_hist.append(float(np.min(fit)))
            n_hist.append(N)

            if S_F:
                mf, mcr = update_memory(M_F[k_pos], M_CR[k_pos], S_F, S_CR, S_diff)
                M_F[k_pos] = mf
                M_CR[k_pos] = mcr
                k_pos = (k_pos + 1) % h_memory

            repair_succ_rate = (
                repaired_successes / repaired_count if repaired_count > 0 else -1.0
            )
            no_repair_succ_rate = (
                unrepaired_successes / unrepaired_count if unrepaired_count > 0 else -1.0
            )

            gen_logs.append(
                {
                    "fe": fes,
                    "gen": gen,
                    "N": N,
                    "best": float(np.min(fit)),
                    "n_trials": n_trials,
                    "n_oob_trials": n_oob_trials,
                    "oob_trial_frac": n_oob_trials / n_trials if n_trials > 0 else 0.0,
                    "total_oob_coords": total_oob_coords,
                    "oob_coord_frac": (
                        total_oob_coords / (n_trials * dim) if n_trials > 0 else 0.0
                    ),
                    "mean_repair_L2": float(np.mean(repair_L2s)) if repair_L2s else 0.0,
                    "max_repair_L2": float(np.max(repair_L2s)) if repair_L2s else 0.0,
                    "mean_repair_cosine": (
                        float(np.mean(repair_cosines)) if repair_cosines else 0.0
                    ),
                    "n_archive_r2": n_archive_r2,
                    "n_pop_r2": n_pop_r2,
                    "archive_r2_frac": n_archive_r2 / n_trials if n_trials > 0 else 0.0,
                    "successes": n_successes,
                    "total_improvement": total_improvement,
                    "n_archive_events": n_archive_inserts,
                    "archive_size": len(archive),
                    "repair_success_rate": repair_succ_rate,
                    "no_repair_success_rate": no_repair_succ_rate,
                }
            )
            gen += 1

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

        return BoundaryDiagResult(
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
            gen_logs=gen_logs,
            fe_exact=(fes == indep["n"] == max_fes),
        )
    finally:
        problem.eval = raw_eval  # type: ignore[attr-defined]
