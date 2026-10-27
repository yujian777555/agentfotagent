# Phase-1A P0-R1 Corrective Report

- Branch: `phase1a-p0-r1-corrective`
- Base: `phase1a-p0-r1@ed3ba4f984bfe0455b78f7e069006b1c89dbe5dc`
- Failed CI being fixed: https://github.com/yujian777555/agentfotagent/actions/runs/40474242482

## Fixed defects

| ID | Defect | Fix | Evidence |
|---|---|---|---|
| CI | Workflow referenced missing `test_controller_dsl.py` / `test_metabox_integration.py` | Run full `pytest tests`; integration job runs `test_p0r1_metabox_fixes.py`, fails if 0 collected; adds smoke run | `.github/workflows/phase1a-metabox.yml` |
| State | `success_fraction` hardcoded 0.0 | Previous generation's `successes/attempted` is passed into the next controller call | `test_next_generation_success_fraction_matches_previous` |
| Test FP | Live-trajectory test accepted F=0.5 only | Asserts both 0.5 and 0.8, fire event state/action/effect consistency | `test_controlled_de_live_trajectory_triggers_rule` |
| FE | controlled `independent_fes` copied from `fes` | Independent wrapper counts every `problem.eval` including init | `test_fe_exact_budget_and_independent_match` |
| Metrics | raw vs regret mixed | `raw_objective` always; `regret` only when optimum known; primary metric labeled | `test_regret_metric_when_optimum_known` / `test_raw_objective_when_optimum_unknown` |
| Traces | only last 10 cost values | Full `cost_curve` + full `action_events` in manifest + on-disk trace with SHA-256 | `results/phase1a_smoke/traces/` |
| Budget | `res.fes >= max_fes` | Exact `== max_fes`; reject `max_fes < np_size` | tests |

## Feature semantics (documented)

- Generation-level. `success_fraction` = previous generation successes/attempted (0 at gen 0).
- `improvement_rate` = (best[t-1]-best[t])/|best[t-1]| per generation.
- `stagnation_steps` = consecutive generations without best improvement.
- Optimum is never in controller state.

## Test results

```text
D:/metabox-env python -m pytest tests/ -o addopts='' -q     → 225 passed
project python -m pytest tests -o addopts='' -q -ra         → 204 passed, 1 skip (no metaevobox)
python experiments/metabox/run_smoke.py (metabox-env)       → FE exact, identity F1/F6/F24, repro OK
git diff --check                                            → clean
python -m json.tool status.json                             → valid
```

New run: `phase1a-smoke-r1c-20261027` at
`results/phase1a_smoke/manifest_phase1a-smoke-r1c-20261027.json`.
Prior artifacts preserved (INVALIDATED + r1 manifests).

## MetaBox provenance honesty

Local/CI install is **PyPI `metaevobox==2.0.2`**. Upstream SHA `5565a281…`
is recorded as the claimed v2.0.0 source pairing (release naming); this run
does **not** byte-verify the wheel against that git tree.

## Non-blocking notes

- Controlled DE is rand/1/bin only; restart/mutation remain fail-closed.
- DEAP creator warnings are upstream noise.

## Boundary

No LLM API, no MetaBBO training, no AES transfer. Awaiting Planner review.
