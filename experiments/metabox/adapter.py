"""MetaBox-v2 adapter boundary for agentfotagent.

Imports the official `metaevobox` package only inside this package tree.
AES core modules must not depend on MetaBox objects directly.

Pinned platform (see experiments/metabox/LOCK.json):
- package: metaevobox 2.0.2 (PyPI) matching git branch v2.0.0
- source SHA: 5565a281ce4e03efc1f6a41230507d5b66637ace
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

METABOX_PACKAGE = "metaevobox"
METABOX_VERSION_EXPECTED = "2.0.2"
METABOX_GIT_SHA = "5565a281ce4e03efc1f6a41230507d5b66637ace"

# BBOB-10D function ids 1..24. Project-defined identity split (frozen).
BBOB_10D_FUNCS: Tuple[int, ...] = tuple(range(1, 25))
SPLIT_TRAIN: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
SPLIT_VAL: Tuple[int, ...] = (13, 14, 15, 16, 17, 18)
SPLIT_HELD_OUT: Tuple[int, ...] = (19, 20, 21, 22, 23, 24)


def config_hash(obj: Mapping[str, Any]) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def split_manifest() -> Dict[str, Any]:
    entry = {
        "suite": "bbob-10D",
        "generator": "metaevobox BBOB_Dataset.get_datasets",
        "split_policy": "function-identity disjoint 12/6/6 over F1-F24",
        "train_functions": list(SPLIT_TRAIN),
        "val_functions": list(SPLIT_VAL),
        "held_out_functions": list(SPLIT_HELD_OUT),
        "metabox_git_sha": METABOX_GIT_SHA,
    }
    entry["manifest_hash"] = config_hash(entry)
    return entry


def import_metabox():
    """Import official MetaBox APIs lazily and return a namespace dict."""
    import metaevobox
    from metaevobox import Config
    from metaevobox.environment.problem.utils import get_problem_set
    from metaevobox.baseline.bbo import DE, SHADE, CMAES, Random_search

    version = getattr(metaevobox, "__version__", METABOX_VERSION_EXPECTED)
    return {
        "metaevobox": metaevobox,
        "Config": Config,
        "get_problem_set": get_problem_set,
        "DE": DE,
        "SHADE": SHADE,
        "CMAES": CMAES,
        "RandomSearch": Random_search,
        "version": version,
    }


@dataclass
class ProblemHandle:
    """Evaluation-side handle; does not leak optimum into controller state."""

    problem_id: str
    function_id: int
    dim: int
    lower_bound: float
    upper_bound: float
    _problem: Any = field(repr=False)

    def eval(self, x: np.ndarray) -> float:
        self._problem.reset()
        return float(self._problem.eval(np.asarray(x, dtype=np.float64).reshape(-1)))

    def eval_batch(self, xs: np.ndarray) -> np.ndarray:
        self._problem.reset()
        arr = np.asarray(xs, dtype=np.float64)
        return np.asarray(self._problem.eval(arr), dtype=np.float64).reshape(-1)

    @property
    def raw_optimum(self) -> Optional[float]:
        return getattr(self._problem, "optimum", None)


class FECounter:
    """Independent function-evaluation counter (does not trust optimizer bookkeeping)."""

    def __init__(self) -> None:
        self.count = 0

    def wrap(self, eval_fn: Callable[[np.ndarray], Any]) -> Callable[[np.ndarray], Any]:
        def wrapped(x: np.ndarray) -> Any:
            arr = np.asarray(x, dtype=np.float64)
            n = 1 if arr.ndim == 1 else arr.shape[0]
            self.count += int(n)
            return eval_fn(arr)

        return wrapped


def make_config(max_fes: int, seed: int = 0, full_meta_data: bool = False, **extra: Any):
    mb = import_metabox()
    user = {
        "device": "cpu",
        "upperbound": 100,
        "train_problem": "bbob-10D",
        "test_problem": "bbob-10D",
        "train_difficulty": "all",
        "test_difficulty": "all",
        "train_batch_size": 1,
        "test_batch_size": 1,
        "seed": seed,
        "full_meta_data": full_meta_data,
    }
    user.update(extra)
    # Official Config() runs argparse on sys.argv; isolate it from pytest/CLI args.
    import sys as _sys

    old_argv = _sys.argv
    _sys.argv = ["metaevobox-adapter"]
    try:
        cfg = mb["Config"](user)
    finally:
        _sys.argv = old_argv
    # Official init_config overwrites maxFEs by suite; set the experiment budget
    # after construction so all arms share the same FE budget.
    cfg.maxFEs = int(max_fes)
    cfg.n_logpoint = 50
    cfg.log_interval = max(1, int(max_fes) // 50)
    return cfg


def load_function(function_id: int, difficulty: str = "all") -> ProblemHandle:
    mb = import_metabox()
    if function_id not in BBOB_10D_FUNCS:
        raise ValueError(f"unsupported bbob-10D function id: {function_id}")
    cfg = make_config(max_fes=1000)
    train_set, test_set = mb["get_problem_set"](
        cfg, "bbob-10D", difficulty, [function_id], [function_id]
    )
    batch = train_set[0]
    problem = batch[0]
    problem.reset()
    return ProblemHandle(
        problem_id=f"bbob-10D/F{function_id:02d}",
        function_id=function_id,
        dim=int(problem.dim),
        lower_bound=float(problem.lb) if np.isscalar(problem.lb) else float(np.min(problem.lb)),
        upper_bound=float(problem.ub) if np.isscalar(problem.ub) else float(np.max(problem.ub)),
        _problem=problem,
    )


def available_optimizers() -> Dict[str, Any]:
    mb = import_metabox()
    return {
        "DE": mb["DE"],
        "SHADE": mb["SHADE"],
        "CMAES": mb["CMAES"],
        "RandomSearch": mb["RandomSearch"],
    }


def run_optimizer(
    optimizer_name: str,
    problem: ProblemHandle,
    *,
    max_fes: int,
    seed: int,
    controller=None,
) -> Dict[str, Any]:
    """Run one official MetaBox optimizer episode on the given problem.

    Returns a plain dict with independent FE count, reported fes, cost curve
    and objective direction documentation. Minimization is the official
    direction (DEAP weights=(-1,)).
    """
    import random as _random

    mb = import_metabox()
    opts = available_optimizers()
    if optimizer_name not in opts:
        raise ValueError(f"unknown optimizer: {optimizer_name}")
    # Seed all RNGs used by MetaBox/DEAP/numpy for deterministic episodes.
    _random.seed(seed)
    np.random.seed(seed)
    cfg = make_config(max_fes=max_fes, seed=seed)
    optimizer = opts[optimizer_name](cfg)
    optimizer.seed(seed)

    # Apply typed controller (if any) through the official config surface.
    applied_action = None
    if controller is not None:
        start_state = {
            "improvement_rate": 0.0,
            "stagnation_steps": 0.0,
            "population_diversity": 1.0,
            "success_fraction": 0.0,
            "budget_fraction": 0.0,
        }
        applied_action = controller.select_action(start_state)
        _apply_action(cfg, applied_action)

    # Independent FE accounting around problem.eval.
    counter = FECounter()
    original_eval = problem._problem.eval

    def counting_eval(x):
        arr = np.asarray(x) if not isinstance(x, np.ndarray) else x
        n = 1 if arr.ndim == 1 else int(arr.shape[0])
        counter.count += n
        return original_eval(x)

    problem._problem.eval = counting_eval  # type: ignore[method-assign]
    problem._problem.reset()
    try:
        result = optimizer.run_episode(problem._problem)
    finally:
        problem._problem.eval = original_eval  # type: ignore[method-assign]

    reported_fes = int(result.get("fes", -1))
    cost = [float(c) for c in result.get("cost", [])]
    return {
        "optimizer": optimizer_name,
        "problem_id": problem.problem_id,
        "function_id": problem.function_id,
        "seed": seed,
        "max_fes": max_fes,
        "reported_fes": reported_fes,
        "independent_fes": counter.count,
        "objective_direction": "minimize",
        "cost_curve": cost,
        "best_cost": cost[-1] if cost else None,
        "controller_hash": getattr(controller, "controller_hash", None),
        "controller_id": getattr(controller, "controller_id", None),
        "applied_action": applied_action,
    }


def _apply_action(cfg, action: Mapping[str, Any]) -> None:
    """Apply a compiled controller action to the MetaBox config surface."""
    name = action.get("action")
    params = action.get("params") or {}
    if name == "set_mutation_strategy":
        cfg.mutation_strategy = params["strategy"]
    elif name == "set_F_range":
        cfg.F = 0.5 * (float(params["low"]) + float(params["high"]))
        cfg.F_low = float(params["low"])
        cfg.F_high = float(params["high"])
    elif name == "set_CR_range":
        cfg.Cr = 0.5 * (float(params["low"]) + float(params["high"]))
        cfg.CR_low = float(params["low"])
        cfg.CR_high = float(params["high"])
    elif name == "restart":
        cfg.restart_max_fraction = float(params.get("max_fraction", 0.1))
    elif name == "noop":
        return
    else:
        raise ValueError(f"cannot apply action: {name}")
