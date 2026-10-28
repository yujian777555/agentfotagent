# Phase-1A-4 Pilot Results

Manifest: `results/phase1a4/manifest_a4pilot-56c319064c92-clean-20261028T151259.json`
36 runs (3 funcs × 3 seeds × 12 arms) · 500 FE exact · 0 LLM · train only.

## Mean metric (regret/raw, lower better)

| method | all | F1 | F10 | F20 |
|---|---:|---:|---:|---:|
| **shuffled_triggers** | **2.06e6** | 456 | **6.18e6** | **−30.6** |
| dpr_full | 2.70e6 | **407** | 8.09e6 | −26.4 |
| no_shrink | 4.90e6 | 463 | 14.7e6 | −24.4 |
| no_reset | 4.93e6 | 513 | 14.8e6 | −22.9 |
| official DE | 1.64e7 | — | — | — |
| SHADE | 1.49e7 | — | — | — |

## Paired W-L-T (full vs ·)

| opponent | W-L-T | reading |
|---|---|---|
| no_reset | **8-1** | resets help |
| no_shrink | **7-2** | both components help |
| **shuffled_triggers** | **3-6** | **state triggers worse than random** |
| official / SHADE | 9-0 | weak at 500 FE budget |

## Attribution

- Reset vs no-reset: positive.
- **State-conditioned triggers fail the shuffled control.** Random 20% resets
  beat diversity/stall triggers. Therefore the *detector* is not supported;
  benefit is attributable to occasional resets/immigrants, not to the
  state signal — same class of failure as A2R's inert shuffled_map.

## What this supports / does not

Supports: memory+N reset family is executable and worth studying.
Does **not** support: DPR-SHADE's specific stall/quantile triggers, nor any
Agent-diagnosis claim (no Agent in loop this pilot).

## Integrity

FE exact (500=500). Real MetaBox problems (load_function identity-checked).
Official DE/SHADE are independent implementations (reported separately).
3 seeds — directional only. No test/val functions touched.
