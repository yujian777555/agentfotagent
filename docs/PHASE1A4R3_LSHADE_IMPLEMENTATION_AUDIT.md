# Phase-1A-4R3 L-SHADE Implementation Audit

## Algorithm identity

**Canonical reimplementation** (`experiments/metabox/agent_assisted_ec/lshade_reimpl.py`)
based on Tanabe & Fukunaga 2014 (DOI 10.1109/CEC.2014.6900380). NOT official
code. Contract-tested: FE exact, linear N(t) reduction to N_min, external
archive, current-to-pbest/1/bin, success-history F/CR memory.

Defaults used: N_init=100, N_min=4, H=5, p_best=0.1 (paper-aligned values).

## N+I intervention semantics

- N: N←⌊0.7N⌋ (≥N_min); `effective_shrink` flag when N actually decreases.
- I: replace worst ⌈0.1N⌉ with uniform random immigrants; FE-counted.
- No memory reset. Linear schedule continues on top.

## Trigger statistics (observed, 120 state runs)

- **k_state = 265–290 events per run** (fires almost every generation at
  10k FE on BBOB — stall/diversity thresholds over-trigger).
- **effective_shrinks = 8/≈280** — N already at N_min for most events; N
  is a no-op and only immigration acts (replacing ~1 individual).
- Random matched schedule: **k_rand = 0** — `exact_fe_schedule` has only
  ~48 FE slots at 200-FE spacing; k≈270 ≫ 48 → schedule impossible.

## Matching contract

**FAILED (0/120 exact matches).** Per pre-registered rules, the
state-vs-matched-random comparison is **invalid**. The failed matching is
reported, not replaced by the unmatchable 4R2-style fallback.
