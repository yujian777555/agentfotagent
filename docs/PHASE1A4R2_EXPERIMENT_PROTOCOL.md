# Phase-1A-4R2 Experiment Protocol (frozen)

- Code SHA at run: `8abc8b6f01699cddaa6db1bae0aec1fb08789014`
- Arms (4): baseline (no N/I), N_only, NI_state (frozen stall/div triggers),
  NI_random_matched (exact-count FE schedule, state-blind)
- F1/F10/F20 train · seeds 11,22,33 · 500 FE · NP=20 · minimize
- Memory reset M disabled (closed in 4R)
- Identity: DPR-SHADE-like; not full L-SHADE
- Exact-match contract: k_state == k_rand per (function, seed)
- 36 runs; FE exact required; one corrected run only

## Metrics

Per-function regret (optimum-known BBOB) + raw objective; paired W-L-T
per function and total. No cross-function raw averaging for decisions.
