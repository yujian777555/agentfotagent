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

# BBOB-10D function ids 1..24.
BBOB_10D_FUNCS: Tuple[int, ...] = tuple(range(1, 25))

# Standard BBOB families (verified against COCO-BBOB function taxonomy).
BBOB_FAMILIES: Dict[int, str] = {
    **{i: "separable" for i in range(1, 6)},
    **{i: "low_or_mod_conditioning" for i in range(6, 10)},
    **{i: "high_conditioning_unimodal" for i in range(10, 15)},
    **{i: "multimodal_adequate_global" for i in range(15, 20)},
    **{i: "multimodal_weak_global" for i in range(20, 25)},
}

# MetaBox-documented difficult subset (bbob_dataset.py docstring).
METABOX_DIFFICULT: Tuple[int, ...] = (1, 2, 3, 5, 15, 16, 17, 21)

# split_v2 — stratified, versioned (P0-R1-04). v1 split is preserved in manifests.
SPLIT_V2_TRAIN: Tuple[int, ...] = (1, 2, 4, 6, 7, 10, 11, 12, 15, 18, 20, 21)
SPLIT_V2_VAL: Tuple[int, ...] = (3, 8, 13, 16, 22, 23)
SPLIT_V2_HELD_OUT: Tuple[int, ...] = (5, 9, 14, 17, 19, 24)

# v1 (historical, invalidated for function-specific claims)
SPLIT_V1_TRAIN: Tuple[int, ...] = tuple(range(1, 13))
SPLIT_V1_VAL: Tuple[int, ...] = tuple(range(13, 19))
SPLIT_V1_HELD_OUT: Tuple[int, ...] = tuple(range(19, 25))


def config_hash(obj: Mapping[str, Any]) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def split_manifest(version: str = "split_v2") -> Dict[str, Any]:
    if version == "split_v2":
        train, val, held = SPLIT_V2_TRAIN, SPLIT_V2_VAL, SPLIT_V2_HELD_OUT
    else:
        train, val, held = SPLIT_V1_TRAIN, SPLIT_V1_VAL, SPLIT_V1_HELD_OUT

    def _ids(ids: Sequence[int]) -> List[Dict[str, Any]]:
        return [
            {
                "function_id": i,
                "family": BBOB_FAMILIES[i],
                "metabox_difficulty": "difficult" if i in METABOX_DIFFICULT else "easy",
            }
            for i in ids
        ]

    entry = {
        "split_version": version,
        "suite": "bbob-10D",
        "generator": "metaevobox BBOB_Dataset.get_datasets",
        "split_policy": "function-identity disjoint; family-stratified; difficult counts 4/2/2"
        if version == "split_v2"
        else "sequential 12/6/6 (historical)",
        "train_functions": list(train),
        "val_functions": list(val),
        "held_out_functions": list(held),
        "train_entries": _ids(train),
        "val_entries": _ids(val),
        "held_out_entries": _ids(held),
        "metabox_difficult_set": list(METABOX_DIFFICULT),
        "difficult_counts": {
            "train": sum(1 for i in train if i in METABOX_DIFFICULT),
            "val": sum(1 for i in val if i in METABOX_DIFFICULT),
            "held_out": sum(1 for i in held if i in METABOX_DIFFICULT),
        },
        "metabox_git_sha": METABOX_GIT_SHA,
    }
    entry["manifest_hash"] = config_hash({k: v for k, v in entry.items() if k != "manifest_hash"})
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
    actual_class_name: str
    family: str
    dim: int
    lower_bound: float
    upper_bound: float
    objective_direction: str
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
    cfg.maxFEs = int(max_fes)
    cfg.n_logpoint = 50
    cfg.log_interval = max(1, int(max_fes) // 50)
    return cfg


def load_function(function_id: int, difficulty: str = "all") -> ProblemHandle:
    """Load exactly one BBOB-10D function by identity.

    P0-R1-00: ``difficulty='all'`` ignores user lists in the pinned factory and
    returns all 24 functions. We therefore use ``difficulty=None`` with both
    user lists set to the requested id so the official branch that filters by
    ``user_train_list`` / ``user_test_list`` is taken. The wrapper's
    ``function_id`` is derived from the underlying class name, not from the
    request argument.
    """
    mb = import_metabox()
    if function_id not in BBOB_10D_FUNCS:
        raise ValueError(f"unsupported bbob-10D function id: {function_id}")
    cfg = make_config(max_fes=1000)
    # difficulty=None + explicit user lists → official per-id filter branch.
    train_set, test_set = mb["get_problem_set"](
        cfg, "bbob-10D", None, [function_id], [function_id]
    )
    if len(train_set) != 1:
        raise RuntimeError(f"expected exactly 1 problem instance, got {len(train_set)}")
    batch = train_set[0]
    problem = batch[0]
    problem.reset()

    class_name = type(problem).__name__
    # F6 → 6; F24 → 24 (numpy implementation without _torch suffix).
    actual_id = None
    if class_name.startswith("F"):
        tail = class_name[1:].split("_")[0]
        if tail.isdigit():
            actual_id = int(tail)
    if actual_id is None:
        raise RuntimeError(f"cannot derive function identity from class {class_name!r}")
    if actual_id != function_id:
        raise RuntimeError(
            f"function identity mismatch: requested {function_id}, loaded {actual_id} ({class_name})"
        )

    return ProblemHandle(
        problem_id=f"bbob-10D/F{actual_id:02d}",
        function_id=actual_id,
        actual_class_name=class_name,
        family=BBOB_FAMILIES[actual_id],
        dim=int(problem.dim),
        lower_bound=float(problem.lb) if np.isscalar(problem.lb) else float(np.min(problem.lb)),
        upper_bound=float(problem.ub) if np.isscalar(problem.ub) else float(np.max(problem.ub)),
        objective_direction="minimize",
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


# Actions that official DE (pinned) does not execute. P0-R1-03: reject at runtime.
UNSUPPORTED_OFFICIAL_DE_ACTIONS = frozenset({"set_mutation_strategy", "restart"})


def _apply_action(cfg, action: Mapping[str, Any], *, allow_unsupported: bool = False) -> Dict[str, Any]:
    """Apply a compiled controller action. Scalar-only for official DE (P0-R1-01)."""
    name = action.get("action")
    params = action.get("params") or {}
    if name in UNSUPPORTED_OFFICIAL_DE_ACTIONS and not allow_unsupported:
        raise UnsupportedActionError(
            f"official DE does not execute action {name!r}; use controlled_de or remove it"
        )
    if name == "set_F":
        cfg.F = float(params["value"])
        return {"applied": "set_F", "F": float(params["value"])}
    if name == "set_CR":
        cfg.Cr = float(params["value"])
        return {"applied": "set_CR", "Cr": float(params["value"])}
    if name == "set_F_range":
        # Explicit scalar collapse is NOT range semantics — rejected for official DE.
        raise UnsupportedActionError(
            "set_F_range is not range semantics on official DE; use set_F"
        )
    if name == "set_CR_range":
        raise UnsupportedActionError(
            "set_CR_range is not range semantics on official DE; use set_CR"
        )
    if name == "set_mutation_strategy":
        cfg.mutation_strategy = params["strategy"]
        return {"applied": "set_mutation_strategy", "strategy": params["strategy"]}
    if name == "restart":
        cfg.restart_max_fraction = float(params.get("max_fraction", 0.1))
        return {"applied": "restart", "max_fraction": float(params.get("max_fraction", 0.1))}
    if name == "noop":
        return {"applied": "noop"}
    raise UnsupportedActionError(f"unknown action: {name}")


class UnsupportedActionError(RuntimeError):
    pass


def run_optimizer(
    optimizer_name: str,
    problem: ProblemHandle,
    *,
    max_fes: int,
    seed: int,
    controller=None,
) -> Dict[str, Any]:
    """Run one official MetaBox optimizer episode on the given problem.

    Controller is invoked once before the episode (official DE has no mid-run
    hook). For trajectory-conditioned control use ``controlled_de.run_controlled_de``.
    """
    import random as _random

    mb = import_metabox()
    opts = available_optimizers()
    if optimizer_name not in opts:
        raise ValueError(f"unknown optimizer: {optimizer_name}")
    _random.seed(seed)
    np.random.seed(seed)
    cfg = make_config(max_fes=max_fes, seed=seed)
    optimizer = opts[optimizer_name](cfg)
    optimizer.seed(seed)

    applied_action = None
    action_events: List[Dict[str, Any]] = []
    if controller is not None:
        start_state = {
            "improvement_rate": 0.0,
            "stagnation_steps": 0.0,
            "population_diversity": 1.0,
            "success_fraction": 0.0,
            "budget_fraction": 0.0,
        }
        applied_action = controller.select_action(start_state)
        effect = _apply_action(cfg, applied_action, allow_unsupported=False)
        action_events.append({"step": 0, "state": start_state, "action": applied_action, "effect": effect})

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
        "actual_class_name": problem.actual_class_name,
        "family": problem.family,
        "objective_direction": problem.objective_direction,
        "seed": seed,
        "max_fes": max_fes,
        "reported_fes": reported_fes,
        "independent_fes": counter.count,
        "cost_curve": cost,
        "best_cost": cost[-1] if cost else None,
        "controller_hash": getattr(controller, "controller_hash", None),
        "controller_id": getattr(controller, "controller_id", None),
        "applied_action": applied_action,
        "action_events": action_events,
    }
