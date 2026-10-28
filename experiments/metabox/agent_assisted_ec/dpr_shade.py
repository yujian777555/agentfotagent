"""DPR-SHADE-like: success-history F/CR + diversity/progress-triggered reset.

Pilot implementation for Phase-1A-4. Not a novelty claim.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class DPRResult:
    cost_curve: List[float]
    regret_curve: Optional[List[float]]
    fes: int
    independent_fes: int
    max_fes: int
    resets: List[Dict[str, Any]]
    n_history: List[int]
    mem_history: List[Tuple[float, float]]
    best_raw: float
    best_regret: Optional[float]
    primary_metric: str = "raw_objective"

    def to_dict(self):
        return {
            "cost_curve": self.cost_curve,
            "regret_curve": self.regret_curve,
            "fes": self.fes,
            "independent_fes": self.independent_fes,
            "max_fes": self.max_fes,
            "resets": self.resets,
            "n_history": self.n_history,
            "mem_history": self.mem_history,
            "best_raw": self.best_raw,
            "best_regret": self.best_regret,
            "primary_metric": self.primary_metric,
        }


def _pairwise_diversity(pop: np.ndarray) -> float:
    n = pop.shape[0]
    if n < 2:
        return 0.0
    # mean pairwise L2 / (dim * range proxy)
    idx = np.random.default_rng(0).choice(n, size=min(n, 20), replace=False)
    sub = pop[idx]
    dsum = 0.0
    cnt = 0
    for i in range(sub.shape[0]):
        for j in range(i + 1, sub.shape[0]):
            dsum += float(np.linalg.norm(sub[i] - sub[j]))
            cnt += 1
    return dsum / max(1, cnt)


def run_dpr_shade(
    problem,
    *,
    max_fes: int,
    seed: int,
    np_init: int = 20,
    mode: str = "full",  # full | no_reset | no_shrink | shuffled_triggers
    theta_s: float = 0.05,
    stall_len: int = 5,
    quantile_window: int = 20,
    rho: float = 0.7,
    n_min: int = 4,
    eps_imm: float = 0.1,
    gen_reset_min: int = 5,
) -> DPRResult:
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

    problem.eval = counting  # type: ignore

    optimum = getattr(problem, "optimum", None)
    if isinstance(optimum, np.ndarray):
        optimum = float(optimum.reshape(-1)[0]) if optimum.size == 1 else None
    elif optimum is not None:
        optimum = float(optimum)

    N = np_init
    H = max(5, np_init // 2)
    M_F = [0.5] * H
    M_CR = [0.5] * H
    k_pos = 0

    try:
        pop = rng.uniform(lb, ub, size=(N, dim))
        fit = np.asarray([counting(ind) for ind in pop], dtype=np.float64)
        fes = N
        best_hist = [float(np.min(fit))]
        resets: List[Dict[str, Any]] = []
        n_hist = [N]
        mem_hist = [(M_F[0], M_CR[0])]
        stall = 0
        div_hist: List[float] = []
        last_reset_gen = -999
        gen = 0

        while fes < max_fes:
            order = rng.permutation(N)
            new_pop = pop.copy()
            new_fit = fit.copy()
            S_F: List[float] = []
            S_CR: List[float] = []
            S_diff: List[float] = []
            successes = 0
            attempts = 0

            for i in order:
                if fes >= max_fes:
                    break
                # sample F, CR from memory (SHADE-style)
                ri = int(rng.randint(H))
                F = float(np.clip(rng.normal(M_F[ri], 0.1), 0.0, 1.0))
                CR = float(np.clip(rng.normal(M_CR[ri], 0.1), 0.0, 1.0))
                # current-to-pbest/1 with archive (simplified)
                pbest = max(1, int(N * 0.1))
                cand = np.argsort(fit)[:pbest]
                p = cand[int(rng.randint(len(cand)))]
                idxs = [j for j in range(N) if j != i]
                a, b = rng.choice(idxs, size=2, replace=False)
                mutant = pop[i] + F * (pop[p] - pop[i]) + F * (pop[a] - pop[b])
                mutant = np.clip(mutant, lb, ub)
                cross = rng.rand(dim) < CR
                cross[rng.randint(dim)] = True
                trial = np.where(cross, mutant, pop[i])
                tf = float(counting(trial))
                fes += 1
                attempts += 1
                if tf < fit[i]:
                    new_pop[i] = trial
                    new_fit[i] = tf
                    successes += 1
                    S_F.append(F)
                    S_CR.append(CR)
                    S_diff.append(abs(fit[i] - tf))
            pop, fit = new_pop, new_fit
            best_hist.append(float(np.min(fit)))

            # SHADE memory update
            if S_F:
                diffs = np.array(S_diff, dtype=float)
                w = diffs / diffs.sum() if diffs.sum() > 0 else np.ones_like(diffs) / len(diffs)
                mf = float((w * np.array(S_F) ** 2).sum() / max(1e-12, (w * np.array(S_F)).sum()))
                mcr = float((w * np.array(S_CR)).sum() / w.sum())
                M_F[k_pos] = mf
                M_CR[k_pos] = mcr
                k_pos = (k_pos + 1) % H

            # progress / collapse events
            succ_frac = successes / max(1, attempts)
            if succ_frac < theta_s:
                stall += 1
            else:
                stall = 0
            div = _pairwise_diversity(pop)
            div_hist.append(div)
            R = float(np.quantile(div_hist[-quantile_window:], 0.2)) if len(div_hist) >= 5 else 0.0
            collapse = div < R
            trigger = (stall >= stall_len or collapse) and (gen - last_reset_gen) >= gen_reset_min

            if trigger:
                if mode == "shuffled_triggers":
                    trigger = bool(rng.rand() < 0.2)
                if trigger and mode in ("full", "no_shrink", "shuffled_triggers"):
                    if mode != "no_reset":
                        M_F = [0.5] * H
                        M_CR = [0.5] * H
                        k_pos = 0
                    new_N = N if mode == "no_shrink" else max(n_min, int(N * rho))
                    resets.append({"gen": gen, "reason": f"stall={stall},div={div:.4f},R={R:.4f}",
                                   "N_before": N, "N_after": new_N})
                    if new_N < N:
                        # keep best new_N individuals
                        orderf = np.argsort(fit)[:new_N]
                        pop = pop[orderf].copy()
                        fit = fit[orderf].copy()
                        N = new_N
                        n_imm = max(0, int(eps_imm * N))
                        if n_imm:
                            imm = rng.uniform(lb, ub, size=(n_imm, dim))
                            imm_fit = np.asarray([counting(ind) for ind in imm], dtype=np.float64)
                            fes += n_imm
                            pop = np.vstack([pop, imm])
                            fit = np.concatenate([fit, imm_fit])
                            N = pop.shape[0]
                            best_hist[-1] = float(min(best_hist[-1], np.min(fit)))
                    stall = 0
                    last_reset_gen = gen

            n_hist.append(N)
            mem_hist.append((M_F[0], M_CR[0]))
            gen += 1

        raw_best = float(best_hist[-1])
        regret = None
        best_regret = None
        primary = "raw_objective"
        if optimum is not None:
            regret = [float(y - optimum) for y in best_hist]
            best_regret = float(raw_best - optimum)
            primary = "regret"
        return DPRResult(
            cost_curve=best_hist, regret_curve=regret, fes=fes,
            independent_fes=indep["n"], max_fes=max_fes, resets=resets,
            n_history=n_hist, mem_history=mem_hist,
            best_raw=raw_best, best_regret=best_regret, primary_metric=primary,
        )
    finally:
        problem.eval = raw_eval  # type: ignore
