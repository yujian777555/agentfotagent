"""Canonical L-SHADE reimplementation (Tanabe & Fukunaga 2014) + N+I interventions.

NOT official code. Paper-conformant:
- current-to-pbest/1/bin with external archive
- success-history F/CR memory (H slots)
- linear population reduction
- N+I interventions: shrink N x0.7 + replace worst ~10% with uniform immigrants
- memory NOT reset on intervention; linear schedule still applies on top
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np


@dataclass
class LShadeResult:
    cost_curve: List[float]
    regret_curve: Optional[List[float]]
    fes: int
    independent_fes: int
    max_fes: int
    events: List[Dict[str, Any]]
    n_history: List[int]
    best_raw: float
    best_regret: Optional[float]
    primary_metric: str = "raw_objective"
    algorithm_id: str = "lshade-reimpl"

    def to_dict(self):
        return {
            "cost_curve": self.cost_curve,
            "regret_curve": self.regret_curve,
            "fes": self.fes,
            "independent_fes": self.independent_fes,
            "max_fes": self.max_fes,
            "events": self.events,
            "n_history": self.n_history,
            "best_raw": self.best_raw,
            "best_regret": self.best_regret,
            "primary_metric": self.primary_metric,
            "algorithm_id": self.algorithm_id,
        }


def run_lshade(
    problem,
    *,
    max_fes: int,
    seed: int,
    n_init: int = 100,
    n_min: int = 4,
    h_memory: int = 5,
    p_best: float = 0.1,
    interventions: Optional[Sequence[Dict[str, Any]]] = None,
    use_N: bool = False,
    use_I: bool = False,
    trigger_mode: str = "none",  # none | state
    theta_s: float = 0.05,
    stall_len: int = 5,
    gen_reset_min: int = 5,
) -> LShadeResult:
    """Run L-SHADE; optional pre-scheduled N/I interventions (replay)."""
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

    # interventions as sorted list of {"fe": target_fe, "do_N": bool, "do_I": bool}
    ivs = sorted(interventions or [], key=lambda d: d["fe"])
    iv_ptr = 0

    N = n_init
    archive: List[np.ndarray] = []
    M_F = [0.5] * h_memory
    M_CR = [0.5] * h_memory
    k_pos = 0
    stall = 0
    divs: List[float] = []
    last_iv_gen = -999

    try:
        pop = rng.uniform(lb, ub, size=(N, dim))
        fit = np.asarray([counting(ind) for ind in pop], dtype=np.float64)
        fes = N
        best_hist = [float(np.min(fit))]
        events: List[Dict[str, Any]] = []
        n_hist = [N]
        gen = 0

        while fes < max_fes:
            # linear population reduction (L-SHADE)
            n_target = max(n_min, int(round(n_init * (1.0 - fes / max_fes))))
            if n_target < N:
                orderf = np.argsort(fit)[:n_target]
                pop = pop[orderf].copy()
                fit = fit[orderf].copy()
                N = n_target

            order = rng.permutation(N)
            new_pop = pop.copy()
            new_fit = fit.copy()
            S_F: List[float] = []
            S_CR: List[float] = []
            S_diff: List[float] = []
            successes = 0

            for i in order:
                if fes >= max_fes:
                    break
                ri = int(rng.randint(h_memory))
                F = float(np.clip(rng.normal(M_F[ri], 0.1), 0.0, 1.0))
                CR = float(np.clip(rng.normal(M_CR[ri], 0.1), 0.0, 1.0))
                # current-to-pbest/1 with archive
                n_pbest = max(2, int(N * p_best))
                cand = np.argsort(fit)[:n_pbest]
                p = cand[int(rng.randint(len(cand)))]
                idxs = [j for j in range(N) if j != i]
                a = idxs[int(rng.randint(len(idxs)))]
                pool = idxs + [len(pop) + t for t in range(len(archive))]
                b = pool[int(rng.randint(len(pool)))]
                if b >= N:
                    vec_b = archive[b - N]
                else:
                    vec_b = pop[b]
                mutant = pop[i] + F * (pop[p] - pop[i]) + F * (pop[a] - vec_b)
                mutant = np.clip(mutant, lb, ub)
                cross = rng.rand(dim) < CR
                cross[rng.randint(dim)] = True
                trial = np.where(cross, mutant, pop[i])
                tf = float(counting(trial))
                fes += 1
                if tf < fit[i]:
                    archive.append(pop[i].copy())
                    if len(archive) > N:
                        archive.pop(int(rng.randint(len(archive))))
                    new_pop[i] = trial
                    new_fit[i] = tf
                    successes += 1
                    S_F.append(F)
                    S_CR.append(CR)
                    S_diff.append(abs(fit[i] - tf))
            pop, fit = new_pop, new_fit
            best_hist.append(float(np.min(fit)))

            if S_F:
                diffs = np.array(S_diff, dtype=float)
                w = diffs / diffs.sum() if diffs.sum() > 0 else np.ones_like(diffs) / len(diffs)
                mf = float((w * np.array(S_F) ** 2).sum() / max(1e-12, (w * np.array(S_F)).sum()))
                mcr = float((w * np.array(S_CR)).sum() / w.sum())
                M_F[k_pos] = mf
                M_CR[k_pos] = mcr
                k_pos = (k_pos + 1) % h_memory

            # scheduled interventions (replay / matched random)
            while iv_ptr < len(ivs) and fes >= ivs[iv_ptr]["fe"]:
                iv = ivs[iv_ptr]
                iv_ptr += 1
                ev = {
                    "gen": gen,
                    "fes_at_event": fes,
                    "N_before": N,
                    "do_N": bool(iv.get("do_N")),
                    "do_I": bool(iv.get("do_I")),
                }
                if iv.get("do_N"):
                    new_N = max(n_min, int(N * 0.7))
                    ev["N_after_shrink"] = new_N
                    ev["effective_shrink"] = new_N < N
                    if new_N < N:
                        orderf = np.argsort(fit)[:new_N]
                        pop = pop[orderf].copy()
                        fit = fit[orderf].copy()
                        N = new_N
                else:
                    ev["N_after_shrink"] = N
                    ev["effective_shrink"] = False
                n_imm = 0
                if iv.get("do_I") and N > 1:
                    n_imm = max(1, int(0.1 * N))
                    remaining = max_fes - fes
                    n_imm = min(n_imm, remaining)
                    if n_imm > 0:
                        imm = rng.uniform(lb, ub, size=(n_imm, dim))
                        imm_fit = np.asarray([counting(ind) for ind in imm], dtype=np.float64)
                        fes += n_imm
                        orderf = np.argsort(fit)
                        keep_n = max(1, N - n_imm)
                        keep = orderf[:keep_n]
                        pop = np.vstack([pop[list(keep)], imm])
                        fit = np.concatenate([fit[list(keep)], imm_fit])
                        N = pop.shape[0]
                ev["n_immigrants"] = n_imm
                ev["N_after_immigration"] = N
                events.append(ev)
                best_hist[-1] = float(min(best_hist[-1], np.min(fit)))

            n_hist.append(N)
            # state-triggered N+I (in addition to linear schedule)
            if trigger_mode == "state":
                succ_frac = successes / max(1, N)
                stall = stall + 1 if succ_frac < theta_s else 0
                div = float(np.mean(np.std(pop, axis=0))) if N > 1 else 0.0
                divs.append(div)
                R = float(np.quantile(divs[-20:], 0.2)) if len(divs) >= 5 else 0.0
                fire = (stall >= stall_len or (len(divs) >= 5 and div < R)) and (gen - last_iv_gen) >= gen_reset_min
                if fire:
                    ev = {"gen": gen, "fes_at_event": fes, "N_before": N, "do_N": use_N, "do_I": use_I,
                          "trigger": "state"}
                    if use_N:
                        new_N = max(n_min, int(N * 0.7))
                        ev["N_after_shrink"] = new_N
                        ev["effective_shrink"] = new_N < N
                        if new_N < N:
                            orderf = np.argsort(fit)[:new_N]
                            pop = pop[orderf].copy()
                            fit = fit[orderf].copy()
                            N = new_N
                    else:
                        ev["N_after_shrink"] = N
                        ev["effective_shrink"] = False
                    n_imm = 0
                    if use_I and N > 1:
                        n_imm = min(max(1, int(0.1 * N)), max_fes - fes)
                        if n_imm > 0:
                            imm = rng.uniform(lb, ub, size=(n_imm, dim))
                            imm_fit = np.asarray([counting(ind) for ind in imm], dtype=np.float64)
                            fes += n_imm
                            orderf = np.argsort(fit)
                            keep = orderf[: max(1, N - n_imm)]
                            pop = np.vstack([pop[list(keep)], imm])
                            fit = np.concatenate([fit[list(keep)], imm_fit])
                            N = pop.shape[0]
                    ev["n_immigrants"] = n_imm
                    ev["N_after_immigration"] = N
                    events.append(ev)
                    best_hist[-1] = float(min(best_hist[-1], np.min(fit)))
                    last_iv_gen = gen
                    stall = 0
            gen += 1

        raw_best = float(best_hist[-1])
        regret = None
        best_regret = None
        primary = "raw_objective"
        if optimum is not None:
            regret = [float(y - optimum) for y in best_hist]
            best_regret = float(raw_best - optimum)
            primary = "regret"
        return LShadeResult(
            cost_curve=best_hist, regret_curve=regret, fes=fes,
            independent_fes=indep["n"], max_fes=max_fes, events=events,
            n_history=n_hist, best_raw=raw_best, best_regret=best_regret,
            primary_metric=primary,
        )
    finally:
        problem.eval = raw_eval  # type: ignore
