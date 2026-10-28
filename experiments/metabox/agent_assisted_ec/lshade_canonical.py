"""Canonical L-SHADE reimplementation (Tanabe & Fukunaga 2014).

canonical_reimplementation; not official code.

Reference:
- R. Tanabe and A. S. Fukunaga, "Success-history based parameter adaptation
  in Differential Evolution," IEEE CEC 2014, pp. 71-78.
- Companion SHADE paper (CEC 2013) for memory/archive conventions.

Paper-conformant details implemented here:
- N_target = round(N_init + (N_min - N_init) * FE / max_FE)   [linear reduction]
- F  ~ Cauchy(M_F[k], 0.1);   F > 1 -> 1;  F <= 0 -> resample (cap 100 tries -> 1)
- CR ~ Normal(M_CR[k], 0.1);  clipped to [0, 1]
- M_F  update: Lehmer mean  sum(w*F^2) / sum(w*F)
- M_CR update: weighted arithmetic mean  sum(w*CR) / sum(w)
- weights w = |delta f|; if sum(w)==0 fall back to uniform weights
- empty success set -> do NOT update memory and do NOT advance k_pos
- mutation: current-to-pbest/1/bin with external archive
    u_i = x_i + F*(x_pbest - x_i) + F*(x_r1 - x_r2)
    r1 from population, r1 != i
    r2 from population U archive, r2 != i and r2 != r1
- pbest drawn uniformly from top max(2, floor(p*N)) individuals
- archive capacity tracks current N; trimmed when N shrinks
- binomial crossover with at least one mutant coordinate
- boundary: clip to [lb, ub]  (convention note: some paper variants resample
  between bound and parent; we use clip and record this as an explicit choice)
- selection: minimization, accept trial iff trial_fit <= parent_fit

Metrics semantics (blocking gate, see PHASE1A6_BASELINE_AUDIT.md):
- raw_objective       = problem.eval(x) return value (BBOB bias included)
- optimum             = problem.optimum (value at get_optimal(); NOT always a
                        strict lower bound — F20/Schwefel in metaevobox 2.0.2
                        admits values below the claimed optimum)
- benchmark_cost      = raw_objective - optimum   (may be negative; never
                        called "regret")
- regret              = benchmark_cost IFF a verified lower-bound check passes
                        for the whole trajectory; else None

Experimental-config defaults (may differ from paper competition settings):
- n_init=100, n_min=4, h_memory=5, p_best=0.1
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# schedule / sampling primitives (unit-testable without a problem object)
# ---------------------------------------------------------------------------

def linear_n_target(n_init: int, n_min: int, fes: int, max_fes: int) -> int:
    """Standard L-SHADE linear population-size schedule.

    N_target = round(N_init + (N_min - N_init) * FE / max_FE)
    Endpoints: FE=0 -> n_init, FE=max_FE -> n_min. Monotone non-increasing.
    """
    if max_fes <= 0:
        return int(n_min)
    t = float(fes) / float(max_fes)
    val = n_init + (n_min - n_init) * t
    return int(round(val))


def sample_f(rng: np.random.RandomState, m_f: float) -> float:
    """Cauchy(m_f, 0.1) with standard L-SHADE boundary handling.

    F > 1  -> 1.0
    F <= 0 -> regenerate (up to 100 tries); if still failing return 1.0.
    """
    for _ in range(100):
        # Cauchy via inverse CDF: m + scale * tan(pi*(u-0.5))
        u = rng.rand()
        f = m_f + 0.1 * np.tan(np.pi * (u - 0.5))
        if f > 1.0:
            return 1.0
        if f > 0.0:
            return float(f)
    return 1.0


def sample_cr(rng: np.random.RandomState, m_cr: float) -> float:
    """Normal(m_cr, 0.1) clipped to [0, 1]."""
    cr = float(rng.normal(m_cr, 0.1))
    return float(min(1.0, max(0.0, cr)))


def update_memory(
    m_f: float,
    m_cr: float,
    s_f: Sequence[float],
    s_cr: Sequence[float],
    s_diff: Sequence[float],
) -> Tuple[float, float]:
    """Compute new (M_F, M_CR) from a non-empty success set.

    M_F  = Lehmer mean  sum(w*F^2) / sum(w*F)
    M_CR = weighted arithmetic mean  sum(w*CR) / sum(w)
    w = |delta f|; if sum(w)==0 use uniform weights.
    """
    if len(s_f) == 0:
        raise ValueError("update_memory requires a non-empty success set")
    diffs = np.asarray(s_diff, dtype=np.float64)
    fs = np.asarray(s_f, dtype=np.float64)
    crs = np.asarray(s_cr, dtype=np.float64)
    if diffs.sum() > 0:
        w = diffs / diffs.sum()
    else:
        w = np.ones_like(diffs) / len(diffs)
    denom_f = float((w * fs).sum())
    mf = float((w * fs ** 2).sum() / denom_f) if abs(denom_f) > 1e-12 else m_f
    denom_c = float(w.sum())
    mcr = float((w * crs).sum() / denom_c) if abs(denom_c) > 1e-12 else m_cr
    return mf, mcr


def select_r1_r2(
    rng: np.random.RandomState,
    n_pop: int,
    archive_len: int,
    i: int,
) -> Tuple[int, int]:
    """Draw (r1, r2) with r1 != i, r2 != i, r2 != r1.

    r1 from population indices; r2 from population U archive indices.
    Archive indices are encoded as n_pop + t for t in [0, archive_len).
    """
    if n_pop < 2:
        raise ValueError("need at least 2 population members to draw r1/r2")
    pop_idxs = [j for j in range(n_pop) if j != i]
    r1 = int(pop_idxs[int(rng.randint(len(pop_idxs)))])
    pool = [j for j in pop_idxs if j != r1]
    if archive_len > 0:
        pool = pool + [n_pop + t for t in range(archive_len)]
    if not pool:
        # only possible when n_pop == 2 and archive empty and i excludes one
        # and r1 excludes the other -> cannot happen if n_pop >= 2 and we
        # excluded only i and r1 from a set of size >= 2.
        raise RuntimeError("empty r2 pool")
    r2 = int(pool[int(rng.randint(len(pool)))])
    return r1, r2


# ---------------------------------------------------------------------------
# result container
# ---------------------------------------------------------------------------

@dataclass
class CanonicalResult:
    """One run of canonical L-SHADE.

    Metrics are stored separately; ``regret`` is only populated when the
    lower-bound check passed on the whole trajectory.
    """

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
    algorithm_id: str = "lshade-canonical-reimpl"
    provenance: str = "canonical_reimplementation; not official code"
    fe_exact: bool = True
    log_points: List[Dict[str, Any]] = field(default_factory=list)

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
            "algorithm_id": self.algorithm_id,
            "provenance": self.provenance,
            "fe_exact": self.fe_exact,
            "log_points": self.log_points,
        }


# ---------------------------------------------------------------------------
# main routine
# ---------------------------------------------------------------------------

def run_lshade_canonical(
    problem,
    *,
    max_fes: int,
    seed: int,
    n_init: int = 100,
    n_min: int = 4,
    h_memory: int = 5,
    p_best: float = 0.1,
    log_every: Optional[int] = None,
) -> CanonicalResult:
    """Run canonical L-SHADE on a MetaBox-style problem.

    The problem must expose: ``reset()``, ``dim``, ``lb``, ``ub``, ``eval(x)``
    returning the raw objective, and optional ``optimum``.
    """
    if max_fes < n_init:
        raise ValueError("max_fes must be >= n_init")
    if not (0.0 < p_best <= 1.0):
        raise ValueError("p_best must be in (0, 1]")
    if n_min < 2:
        raise ValueError("n_min must be >= 2")
    if h_memory < 1:
        raise ValueError("h_memory must be >= 1")

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
        log_points: List[Dict[str, Any]] = []
        gen = 0

        if log_every:
            log_points.append(
                {"fe": fes, "gen": gen, "best_raw": raw_hist[-1], "N": N}
            )

        while fes < max_fes:
            # ---- standard linear population reduction -------------------
            n_target = linear_n_target(n_init, n_min, fes, max_fes)
            if n_target < N:
                keep = np.argsort(fit)[:n_target]
                pop = pop[keep].copy()
                fit = fit[keep].copy()
                N = n_target
                # keep archive capacity invariant: |archive| <= N
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

                # pbest from top max(2, floor(p*N))
                n_pbest = max(2, int(N * p_best))
                cand = np.argsort(fit)[:n_pbest]
                p = int(cand[int(rng.randint(len(cand)))])

                # r1, r2 with exclusions
                if N < 2:
                    continue
                r1, r2 = select_r1_r2(rng, N, len(archive), i)
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

                # minimization: accept if trial <= parent
                if tf <= fit[i]:
                    archive.append(pop[i].copy())
                    if len(archive) > N:
                        archive.pop(int(rng.randint(len(archive))))
                    new_pop[i] = trial
                    new_fit[i] = tf
                    S_F.append(F)
                    S_CR.append(CR)
                    S_diff.append(abs(float(fit[i] - tf)))

            pop, fit = new_pop, new_fit
            raw_hist.append(float(np.min(fit)))
            n_hist.append(N)

            # ---- success-history memory update -------------------------
            if S_F:
                mf, mcr = update_memory(M_F[k_pos], M_CR[k_pos], S_F, S_CR, S_diff)
                M_F[k_pos] = mf
                M_CR[k_pos] = mcr
                k_pos = (k_pos + 1) % h_memory

            if log_every and (gen % log_every == 0):
                log_points.append(
                    {"fe": fes, "gen": gen, "best_raw": raw_hist[-1], "N": N}
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

        return CanonicalResult(
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
            fe_exact=(fes == indep["n"] == max_fes),
            log_points=log_points,
        )
    finally:
        problem.eval = raw_eval  # type: ignore[attr-defined]


def verify_function_identity(problem, expected_id: int) -> Dict[str, Any]:
    """Return identity facts; raise if class name does not match expected_id.

    Mirrors adapter.load_function's class-name rule: F{id} -> id.
    """
    class_name = type(problem).__name__
    actual_id = None
    if class_name.startswith("F"):
        tail = class_name[1:].split("_")[0]
        if tail.isdigit():
            actual_id = int(tail)
    if actual_id is None:
        raise RuntimeError(f"cannot derive function identity from class {class_name!r}")
    if actual_id != expected_id:
        raise RuntimeError(
            f"function identity mismatch: requested {expected_id}, loaded {actual_id} ({class_name})"
        )
    return {
        "requested_id": expected_id,
        "actual_id": actual_id,
        "class_name": class_name,
    }
