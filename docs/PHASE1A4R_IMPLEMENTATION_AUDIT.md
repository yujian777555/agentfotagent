# Phase-1A-4R Implementation Audit

## Algorithm identity

**Route B: `DPR-SHADE-like`** (v2). Simplified SHADE-style F/CR memory +
current-to-pbest/1. **Differences from official SHADE/L-SHADE:**
- no external archive
- no linear N(t) schedule (N changes only via intervention)
- MetaBox `SHADE`/`DE` remain **independent external implementations**

## Fixed defects vs Phase-1A-4

| defect | fix |
|---|---|
| `no_reset`/`no_shrink` mixed two components | explicit 2×2×2 M,N,I factorial |
| immigrants via shrink branch | `use_I` replaces worst at fixed N (FE-counted) |
| `shuffled_triggers` still state-gated then dropped | new `matched_fe` — FE-threshold schedule, state-blind |
| gen-index matched schedule unreachable | **bug found in 4R run 1** (see failed manifest `a4r-944575c…`): schedule gens > matched-run lifetime → 0 fires. Fixed to FE thresholds |
| trigger attribution missing | log stall/div/both/cooldown/N/M/immigrants per event |

## Trigger statistics (corrected run, 9 runs)

- **112 fires total; stall_only=0; div_only=112** — the stagnation detector never
  fires on its own; all interventions are diversity-collapse driven.
- This confirms Phase-1A-4 suspicion: attributing resets to "stagnation
  detection" was wrong.

## FE / identity

All rows: `fes == independent_fes == 500`. Function identity via `load_function`.
Two manifests kept: failed gen-index matched run and corrected FE-matched run.
