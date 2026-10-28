# Phase-1A-4R2 Results (corrected, exact-matched)

Manifest: `results/phase1a4r2/manifest_a4r2-8abc8b6f0169-clean-20261028T163406.json`
36/36 runs · **all_matched=True (9/9 exact k)** · FE exact · 0 failures.

## Mean metric (↓, cross-func average only for scale reference)

| method | mean |
|---|---:|
| baseline | 4.93e6 |
| N_only | 3.02e6 |
| **NI_state** | **1.16e6** |
| NI_random_matched | 3.04e6 |

## Paired W-L-T (9 pairs)

| comparison | total | F1 | F10 | F20 |
|---|---|---|---|---|
| NI_state vs baseline | **8-1** | 2-1 | 3-0 | 3-0 |
| NI_state vs NI_random_matched | **5-4** | **1-2** | **3-0** | **1-2** |
| NI_random_matched vs baseline | 7-2 | 2-1 | 2-1 | 3-0 |
| N_only vs baseline | 6-3 | 1-2 | 3-0 | 2-1 |

## Per-function reading

- **F10:** state beats matched 3-0 — timing may matter here.
- **F1 / F20:** state **loses** to matched 1-2 each — no general timing edge.
- N+I helps vs baseline on all three functions (both arms).

## Trigger / FE logs

State fires per run: 11–14 (all diversity-collapse; stall_only=0 as in 4R).
Matched fires equal k exactly; FE positions recorded in manifest
(e.g. F1 s11: 13 fires at FE 50…450).

## Integrity

optimum-known regret for all three BBOB functions (no negative-regret issue
observed); raw objective stored alongside; independent FE == reported FE == 500.
