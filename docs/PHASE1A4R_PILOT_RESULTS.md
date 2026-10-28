# Phase-1A-4R Pilot Results (corrected)

Manifest: `results/phase1a4r/manifest_a4r-2eebcf7b40b1-clean-20261028T155049.json`
(9 runs × 11 arms = 99 rows). Failed gen-index matched run preserved separately.

## Mean metric (↓) — 2×2×2 factorial + controls

| M N I | method | mean |
|---|---|---:|
| 0 0 0 | baseline | 4.93e6 |
| 1 0 0 | memory only | 4.90e6 |
| 0 1 0 | **shrink only** | **3.02e6** |
| 0 0 1 | immigrants only | 4.42e6 |
| 1 1 0 | M+N | 3.45e6 |
| 1 0 1 | M+I | 5.12e6 |
| **0 1 1** | **N+I (no reset)** | **1.16e6** |
| 1 1 1 | state full | 3.25e6 |
| — | matched random timing | 1.38e6 |
| — | official DE | 1.64e7 |
| — | SHADE (MetaBox) | 1.49e7 |

## Paired W-L-T (9 pairs)

| comparison | W-L-T | reading |
|---|---|---|
| state full vs matched random | **3-6** | state timing **not** better |
| state full vs baseline | 7-2 | interventions help |
| state full vs SHADE | 9-0 | external weak at 500 FE |
| state full vs N+I | **3-6** | **memory reset hurts** |
| N+I vs matched | 4-5 | roughly equal |
| N only vs baseline | 6-3 | shrink helps |
| I only vs baseline | 6-3 | immigrants help |
| M only vs baseline | 5-4 | negligible |

## Trigger attribution

**112 fires: stall_only=0, div_only=112.** Stagnation detector is dead;
all interventions are diversity-collapse events. Cooldown blocked 20 attempts.

## FE / integrity

All arms FE exact (500=500). Matched FE schedule: 0/9 exact count matches
(cooldown/endpoint effects) but matched arms did fire (mean 1.38e6 ≠ baseline)
— record `schedule_match_ok=false` honestly.

## Reading

1. **N+I without memory reset is the best configuration** (1.16e6).
2. State triggers do **not** beat matched-random timing (3-6).
3. Memory reset is harmful (full 3.25e6 vs N+I 1.16e6).
4. External SHADE/DE at this budget are far behind — not a meaningful
   quality bar here.
