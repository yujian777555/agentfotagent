# Phase-1A MetaBox Integration Report (P0 smoke)

Status: **ENGINEERING SMOKE — NOT AGENT CAPABILITY EVIDENCE / NOT CONFIRMATORY**

## 1. Platform pin

| Item | Value |
|---|---|
| Package | `metaevobox` (PyPI) |
| Version | 2.0.2 |
| Git repo | https://github.com/MetaEvo/MetaBox.git |
| Git ref | `v2.0.0` |
| Git SHA | `5565a281ce4e03efc1f6a41230507d5b66637ace` |
| Python | 3.11.15 (isolated venv `D:/metabox-env` via uv) |
| Host | Windows 11 x64, 16 logical CPUs, no GPU |
| Lock | `experiments/metabox/LOCK.json` |

Install commands (recorded in LOCK.json):
```text
uv venv D:/metabox-env --python 3.11
uv pip install --python D:/metabox-env/Scripts/python.exe metaevobox
uv pip install --python D:/metabox-env/Scripts/python.exe --reinstall torch
uv pip install --python D:/metabox-env/Scripts/python.exe pytest
```

## 2. Verified official semantics

- Problem suite: `bbob-10D` via `BBOB_Dataset.get_datasets` / `get_problem_set`
  (24 functions F1–F24, dim=10, bounds ±100).
- Optimizer path: `metaevobox.baseline.bbo.DE.run_episode(problem)` returns
  `{'cost': [...], 'fes': int}`.
- Objective direction: **minimize** (DEAP `weights=(-1.0,)`).
- Reported `cost` is `problem.eval(x) - problem.optimum` when `optimum` is set
  (regret-like; BBOB F4 bias e.g. optimum=1000).
- FE accounting: each individual evaluation increments FEs; adapter independently
  wraps `problem.eval` and matches `result['fes']`.
- `Config.init_config` **overwrites** `maxFEs` by suite (bbob-10D → 20000) and
  `n_logpoint=50`. Adapter sets `maxFEs` **after** `Config()` so all arms share
  the experiment budget.

## 3. Adapter boundary

`experiments/metabox/adapter.py` is the only import surface for `metaevobox`.
AES core (`src/agentfotagent`) does not import MetaBox. Handles expose
`eval/eval_batch/dim/bounds`; optimum is not part of controller state.

## 4. Controller DSL

`experiments/metabox/controller_dsl.py` — closed schema (`aes-controller-dsl-v1`),
typed actions (`set_mutation_strategy`, `set_F_range`, `set_CR_range`, `restart`,
`noop`), bounded F∈[0.1,1], CR∈[0,1], restart≤0.25. Unknown fields/actions/
features/params are rejected. Deterministic compile → SHA-256 controller hash.
No arbitrary Python execution.

Two legal fixed controllers execute through the real DE path (F/CR applied to
official config; rules evaluated against typed state features).

## 5. Smoke experiment

```text
python experiments/metabox/run_smoke.py   # with D:/metabox-env
```

- Problem: bbob-10D **F6**, DE, `max_fes=1500`, seeds 11/22 (+33 for repro)
- Controllers: `fixed_classic_de` (F∈[0.4,0.6]) vs `fixed_explore_de` (F∈[0.8,1.0])
- Results (from `results/phase1a_smoke/manifest.json`):
  - FE accounting: independent_fes == reported_fes == 1500 for all runs
  - Objective direction: minimize confirmed (cost non-increasing in best-so-far)
  - Seed reproducibility: identical cost curves on repeated runs (same seed)
  - Controllers both execute and produce different outcomes
    (classic best≈9.66/19.67 vs explore best≈416/531 on seeds 11/22)

## 6. Frozen protocol split (Task E)

Function-identity disjoint split over BBOB-10D F1–F24 (`split_manifest()`):

| Split | Functions | Count |
|---|---|---|
| train | 1–12 | 12 |
| validation | 13–18 | 6 |
| held-out | 19–24 | 6 |

Manifest hash recorded in `results/phase1a_smoke/manifest.json` and via
`experiments.metabox.adapter.split_manifest()`.

Planned comparison arms (for later authorized runs): fixed DE, SHADE/CMAES if
fair under budget, MetaBBO baseline (e.g. GLEET) if runnable, random-controller
search, Agent-without-diagnosis, Agent-with-diagnosis. Primary metric to be
confirmed from MetaBox official metrics before confirmation; FE budget fixed.

## 7. Tests

```text
# project Python (DSL only)
python -m pytest tests/test_controller_dsl.py -o addopts='' -q   → 8 passed

# MetaBox runtime
D:/metabox-env/Scripts/python.exe -m pytest tests/test_metabox_integration.py tests/test_controller_dsl.py -o addopts='' -q
  → 15 passed
```

## 8. Residual / blockers

- `mutation_strategy` is recorded on config but MetaBox DE implements a fixed
  rand/1-style operator; strategy switching is not yet wired inside DE.
- `restart` action is validated and selectable but not injected into DE loop yet.
- No LLM API used. No GPU. No MetaBBO meta-training.
- Phase-1A P0 remains engineering-only until Planner review.
