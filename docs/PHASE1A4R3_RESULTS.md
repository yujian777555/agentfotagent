# Phase-1A-4R3 Results

Manifest: `results/phase1a4r3/manifest_a4r3-2f13d24beb27-clean-20261028T193948.json`
600 runs (5 arms × 12 train funcs × 10 seeds) · 10,000 FE · FE exact.
**Matching contract: FAILED (0/120)** — see implementation audit.

## Paired W-L-T (per-function totals over 10 seeds)

| comparison | total | funcs won |
|---|---|---|
| NI_random_matched vs L_SHADE | **0-0-120** | 0/12 |
| NI_state vs NI_random_matched | **3-107-10** | 0/12 |
| NI_state vs L_SHADE | **3-107-10** | 0/12 |
| N_only_replay vs L_SHADE | 14-89-17 | 2/12 |
| I_only_replay vs L_SHADE | 4-106-10 | 0/12 |

## Per-function (NI_state vs L_SHADE)

| F | W-L-T |
|---|---|
| 1,2,4,6,7,10,12,15,18 | 0-10-0 |
| 11 | 1-9-0 |
| 20 | 2-8-0 |
| 21 | 0-0-10 |

## Interpretation

1. **NI_random_matched ≡ L_SHADE (120 ties):** random schedule had 0 events
   (k infeasible) → not a valid timing control. Cannot assess "restarts help".
2. **NI_state loses 3-107:** ~270 near-constant interventions (only 8 effective
   shrinks) disrupt L-SHADE's linear schedule and memory; mostly immigrant
   noise at already-minimal N.
3. N-only replay helps 2/12 functions (F1: 3-0-7, F20: 7-3) but not general.

## Integrity

FE 10000=10000 all runs. Canonical L-SHADE reimplementation (not official).
Train split only. 0 LLM. Two manifests (duplicate background launch) —
identical content hash reported by size.
