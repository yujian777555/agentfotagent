# Phase-1A-4R2 Matching Audit

## Prior manifest audit (`a4r-2eebcf7b40b1…`)

| field | value |
|---|---|
| state fires (k) | 10–14 per run |
| matched target | k |
| matched actual fires | **5–6** (gen-cooldown discarded thresholds) |
| `schedule_match_ok` | **False** (0/9) |
| meaning | `n_fires == target_fires` — never held |

**Conclusion:** Phase-1A-4R's 3-6 state-vs-matched result is **invalid** as a
timing comparison (unmatched counts). Retained unchanged as history.

## Fixes for exact matching (implementation only)

1. FE-threshold schedule with spacing ≥25 FE (pre-registered cooldown).
2. `matched_fe` no longer applies generation cooldown to thresholds and does
   not discard a threshold without firing (one fire per threshold).
3. Contract tests assert exactly-k fires (`test_phase1a4r2.py`).

Failed first 4R2 run (`a4r2-1aa651ffda3f…`) preserved: same discard bug.
Corrected run `a4r2-8abc8b6f0169…`: **all_matched=True, 9/9 exact**.
