"""DPR-SHADE-like with 2x2x2 factorial interventions (M, N, I).

Algorithm identity: **DPR-SHADE-like** — simplified success-history F/CR
(SHADE-style) + current-to-pbest/1. NOT official SHADE/L-SHADE:
no external archive, no linear N(t). Route B per audit.

Components:
  M: reset success-history memory to priors
  N: shrink population (keep best)
  I: inject random immigrants (replace worst; FE-counted)

Trigger modes:
  state     — frozen stall/diversity triggers + cooldown
  schedule  — fixed list of generation indices (for component ablation)
  matched   — intervention generations sampled from cooldown-valid slots
              (independent of search state), count-matched to state run
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np


@dataclass
class DPRResult:
    cost_curve: List[float]
    regret_curve: Optional[List[float]]
    fes: int
    independent_fes: int
    max_fes: int
    events: List[Dict[str, Any]]
    best_raw: float
    best_regret: Optional[float]
    primary_metric: str = "raw_objective"
    algorithm_id: str = "dpr-shade-like-v2"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cost_curve": self.cost_curve,
            "regret_curve": self.regret_curve,
            "fes": self.fes,
            "independent_fes": self.independent_fes,
            "max_fes": self.max_fes,
            "events": self.events,
            "best_raw": self.best_raw,
            "best_regret": self.best_regret,
            "primary_metric": self.primary_metric,
            "algorithm_id": self.algorithm_id,
        }


def _diversity(pop: np.ndarray) -> float:
    n = pop.shape[0]
    if n < 2:
        return 0.0
    rng = np.random.default_rng(0)
    idx = rng.choice(n, size=min(n, 16), replace=False)
    sub = pop[idx]
    total = 0.0
    cnt = 0
    for i in range(sub.shape[0]):
        for j in range(i + 1, sub.shape[0]):
            total += float(np.linalg.norm(sub[i] - sub[j]))
            cnt += 1
    return total / max(1, cnt)


def run_dpr_shade_like(
    problem,
    *,
    max_fes: int,
    seed: int,
    np_init: int = 20,
    use_M: bool = True,
    use_N: bool = True,
    use_I: bool = True,
    trigger_mode: str = "state",
    trigger_schedule: Optional[Sequence[int]] = None,
    trigger_fe_schedule: Optional[Sequence[int]] = None,
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

    schedule = set(trigger_schedule or [])
    fe_schedule = sorted(trigger_fe_schedule or [])
    fe_ptr = 0

    try:
        pop = rng.uniform(lb, ub, size=(N, dim))
        fit = np.asarray([counting(ind) for ind in pop], dtype=np.float64)
        fes = N
        best_hist = [float(np.min(fit))]
        events: List[Dict[str, Any]] = []
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
                ri = int(rng.randint(H))
                F = float(np.clip(rng.normal(M_F[ri], 0.1), 0.0, 1.0))
                CR = float(np.clip(rng.normal(M_CR[ri], 0.1), 0.0, 1.0))
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

            if S_F:
                diffs = np.array(S_diff, dtype=float)
                w = diffs / diffs.sum() if diffs.sum() > 0 else np.ones_like(diffs) / len(diffs)
                mf = float((w * np.array(S_F) ** 2).sum() / max(1e-12, (w * np.array(S_F)).sum()))
                mcr = float((w * np.array(S_CR)).sum() / w.sum())
                M_F[k_pos] = mf
                M_CR[k_pos] = mcr
                k_pos = (k_pos + 1) % H

            succ_frac = successes / max(1, attempts)
            if succ_frac < theta_s:
                stall += 1
            else:
                stall = 0
            div = _diversity(pop)
            div_hist.append(div)
            R = float(np.quantile(div_hist[-quantile_window:], 0.2)) if len(div_hist) >= 5 else 0.0

            stall_fire = stall >= stall_len
            div_fire = div < R and len(div_hist) >= 5
            cooldown_ok = (gen - last_reset_gen) >= gen_reset_min

            if trigger_mode == "state":
                fire = (stall_fire or div_fire) and cooldown_ok
            elif trigger_mode == "schedule":
                fire = gen in schedule and cooldown_ok
            elif trigger_mode == "matched_fe":
                # FE-based timing. Thresholds are pre-spaced (>= cooldown_fe),
                # so generation-cooldown must NOT discard them. Fire when fes
                # crosses the next threshold; do not consume if it would
                # violate FE cooldown (defensive).
                fired_by_fe = False
                while fe_ptr < len(fe_schedule) and fes >= fe_schedule[fe_ptr]:
                    if fe_ptr > 0 and (fe_schedule[fe_ptr] - fe_schedule[fe_ptr - 1]) < 1:
                        fe_ptr += 1
                        continue
                    fired_by_fe = True
                    fe_ptr += 1
                    break  # exactly one fire per threshold
                fire = fired_by_fe
            elif trigger_mode == "matched":
                fire = gen in schedule and cooldown_ok
            else:
                raise ValueError(trigger_mode)

            ev = {
                "gen": gen,
                "stall": stall,
                "stall_fire": stall_fire,
                "div": div,
                "div_R": R,
                "div_fire": div_fire,
                "cooldown_ok": cooldown_ok,
                "fired": fire,
                "succ_frac": succ_frac,
                "N_before": N,
            }

            if fire:
                did_M = use_M
                if did_M:
                    M_F = [0.5] * H
                    M_CR = [0.5] * H
                    k_pos = 0
                new_N = N
                if use_N:
                    new_N = max(n_min, int(N * rho))
                    if new_N < N:
                        orderf = np.argsort(fit)[:new_N]
                        pop = pop[orderf].copy()
                        fit = fit[orderf].copy()
                        N = new_N
                n_imm = 0
                if use_I:
                    n_imm = max(1, int(eps_imm * max(N, 1)))
                    remaining = max_fes - fes
                    n_imm = min(n_imm, remaining)  # FE-safe
                    if n_imm > 0:
                        imm = rng.uniform(lb, ub, size=(n_imm, dim))
                        imm_fit = np.asarray([counting(ind) for ind in imm], dtype=np.float64)
                        fes += n_imm
                        # replace worst
                        orderf = np.argsort(fit)
                        keep = orderf[: max(1, N - n_imm)] if n_imm < N else []
                        if len(keep) > 0:
                            pop = np.vstack([pop[list(keep)], imm])
                            fit = np.concatenate([fit[list(keep)], imm_fit])
                        else:
                            pop = imm
                            fit = imm_fit
                        N = pop.shape[0]
                ev.update({
                    "N_after": N,
                    "n_immigrants": n_imm,
                    "memory_reset": did_M,
                    "shrink": use_N,
                })
                last_reset_gen = gen
                stall = 0
                best_hist[-1] = float(min(best_hist[-1], np.min(fit)))
            events.append(ev)
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
            independent_fes=indep["n"], max_fes=max_fes, events=events,
            best_raw=raw_best, best_regret=best_regret, primary_metric=primary,
        )
    finally:
        problem.eval = raw_eval  # type: ignore


def count_state_triggers(events: Sequence[Dict[str, Any]], use_M=True, use_N=True, use_I=True) -> int:
    return sum(1 for e in events if e.get("fired"))
