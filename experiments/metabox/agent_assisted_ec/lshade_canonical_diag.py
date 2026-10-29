"""Phase-1A-7 diagnostic runner for canonical L-SHADE.

Adds fine-grained per-generation mechanism logging WITHOUT altering the
search trajectory. Guarantees:

- No additional RNG draws beyond ``lshade_canonical`` primitives.
- No change to RNG consumption order.
- No change to algorithm branches.

Compared bitwise against ``run_lshade_canonical`` on raw_curve,
benchmark_cost_curve, n_history, and final objective as a blocking gate.

Logged per generation (see ``DIAGNOSTIC_DEFINITIONS``):
1. fe, gen, N
2. best / median / worst objective in current population
3. normalized population diversity (mean of per-dim std / range)
4. successes, attempts, success_rate
5. per-success: F, CR, delta_f
6. M_F[k] / M_CR[k] before and after memory update
7. archive size after generation, n_success_candidates
8. pbest_index_valid (all sampled pbest in top-p set), r_index_valid
9. improvement (prev best - new best), stall counter
10. unit definitions in DIAGNOSTIC_DEFINITIONS

algorithm_id: lshade-canonical-diag
provenance:    canonical_reimplementation; not official code
"""
from __future__ import annotations

import math
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


DIAGNOSTIC_DEFINITIONS: Dict[str, str] = {
    "fe": "cumulative function evaluations after this generation [count]",
    "gen": "generation index, 0-based [count]",
    "N": "population size at generation start after linear reduction [count]",
    "best": "min objective in current population [raw_objective units]",
    "median": "median objective in current population [raw_objective units]",
    "worst": "max objective in current population [raw_objective units]",
    "diversity": "mean over dimensions of std(pop[:,d]) / (ub-lb), dimensionless in [0,~1]",
    "successes": "number of trials that replaced their parent this generation [count]",
    "attempts": "number of trials attempted this generation [count]",
    "success_rate": "successes / attempts, dimensionless in [0,1]",
    "success_F": "list of F values for successful trials [dimensionless]",
    "success_CR": "list of CR values for successful trials [dimensionless]",
    "success_df": "list of |parent_fit - trial_fit| for successes [raw_objective units]",
    "M_F_before": "memory slot value of M_F[k] before update this generation [dimensionless]",
    "M_F_after": "M_F[k] after update (or unchanged if no success) [dimensionless]",
    "M_CR_before": "memory slot M_CR[k] before update [dimensionless]",
    "M_CR_after": "M_CR[k] after update (or unchanged) [dimensionless]",
    "memory_slot": "k index updated this generation, or -1 if no update [index]",
    "archive_size": "external archive size after generation [count]",
    "n_success_candidates": "same as successes; kept for clarity [count]",
    "pbest_ok": "True if every sampled pbest index was within top max(2,floor(p*N)) set [bool]",
    "r_index_ok": "True if r1!=i, r2!=i, r2!=r1 held for all trials [bool]",
    "improvement": "best_before - best_after this generation [raw_objective units], >=0",
    "stall_gen": "consecutive generations with improvement <= 0 at end of this gen [count]",
}


@dataclass
class DiagnosticResult:
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
    algorithm_id: str = "lshade-canonical-diag"
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
            "diagnostic_definitions": DIAGNOSTIC_DEFINITIONS,
        }


def run_lshade_canonical_diag(
    problem,
    *,
    max_fes: int,
    seed: int,
    n_init: int = 100,
    n_min: int = 4,
    h_memory: int = 5,
    p_best: float = 0.1,
) -> DiagnosticResult:
    """Instrumented canonical L-SHADE. Must match run_lshade_canonical bitwise."""
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
        stall = 0
        prev_best = float(np.min(fit))

        while fes < max_fes:
            gen_best_before = prev_best

            # linear reduction (identical to canonical)
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

            # diagnostic accumulators (read-only, no RNG)
            attempts = 0
            successes = 0
            pbest_ok = True
            r_index_ok = True
            success_F: List[float] = []
            success_CR: List[float] = []
            success_df: List[float] = []

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
                # diagnostic: verify p in top set (always true by construction, but record)
                top_set = set(int(c) for c in cand)
                if p not in top_set:
                    pbest_ok = False

                if N < 2:
                    continue
                r1, r2 = select_r1_r2(rng, N, len(archive), i)
                # diagnostic: verify exclusions (by construction true, but record)
                if r1 == i or r2 == i or r2 == r1:
                    r_index_ok = False

                if r2 >= N:
                    vec_r2 = archive[r2 - N]
                else:
                    vec_r2 = pop[r2]

                mutant = pop[i] + F * (pop[p] - pop[i]) + F * (pop[r1] - vec_r2)
                mutant = np.clip(mutant, lb, ub)

                cross = rng.rand(dim) < CR
                cross[int(rng.randint(dim))] = True
                trial = np.where(cross, mutant, pop[i])

                tf = float(counting(trial))
                fes += 1
                attempts += 1

                if tf <= fit[i]:
                    archive.append(pop[i].copy())
                    if len(archive) > N:
                        archive.pop(int(rng.randint(len(archive))))
                    new_pop[i] = trial
                    new_fit[i] = tf
                    S_F.append(F)
                    S_CR.append(CR)
                    S_diff.append(abs(float(fit[i] - tf)))
                    successes += 1
                    success_F.append(F)
                    success_CR.append(CR)
                    success_df.append(abs(float(fit[i] - tf)))

            pop, fit = new_pop, new_fit
            raw_hist.append(float(np.min(fit)))
            n_hist.append(N)

            # memory update (identical)
            k_updated = -1
            m_f_before = list(M_F)
            m_cr_before = list(M_CR)
            if S_F:
                mf, mcr = update_memory(M_F[k_pos], M_CR[k_pos], S_F, S_CR, S_diff)
                M_F[k_pos] = mf
                M_CR[k_pos] = mcr
                k_updated = k_pos
                k_pos = (k_pos + 1) % h_memory

            # ---- diagnostic log (pure observation) ----
            best_now = float(np.min(fit))
            med = float(np.median(fit))
            worst = float(np.max(fit))
            rng_span = ub - lb if ub > lb else 1.0
            diversity = float(np.mean(np.std(pop, axis=0)) / rng_span) if N > 1 else 0.0
            improvement = float(gen_best_before - best_now)
            if improvement <= 0:
                stall += 1
            else:
                stall = 0

            gen_logs.append(
                {
                    "fe": fes,
                    "gen": gen,
                    "N": N,
                    "best": best_now,
                    "median": med,
                    "worst": worst,
                    "diversity": diversity,
                    "successes": successes,
                    "attempts": attempts,
                    "success_rate": (successes / attempts) if attempts > 0 else 0.0,
                    "success_F": success_F,
                    "success_CR": success_CR,
                    "success_df": success_df,
                    "M_F_before": [float(v) for v in m_f_before],
                    "M_F_after": [float(v) for v in M_F],
                    "M_CR_before": [float(v) for v in m_cr_before],
                    "M_CR_after": [float(v) for v in M_CR],
                    "memory_slot": k_updated,
                    "archive_size": len(archive),
                    "n_success_candidates": successes,
                    "pbest_ok": pbest_ok,
                    "r_index_ok": r_index_ok,
                    "improvement": improvement,
                    "stall_gen": stall,
                }
            )
            prev_best = best_now
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

        return DiagnosticResult(
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
