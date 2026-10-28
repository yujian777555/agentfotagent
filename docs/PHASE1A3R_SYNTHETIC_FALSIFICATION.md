# Phase-1A-3R Synthetic Falsification

Code: `scripts/phase1a3r_synthetic_falsification.py`
Data: `results/phase1a3r/synthetic_falsification.json`
Frozen params: horizon 400, β=1.0, 3 arms, 2 buckets, seeds 11,22,33,44,55.
**This tests credit-estimator decision logic only. Not real optimization.**

## Discriminative-power check (required)

`bucket_baseline_ucb` vs `bucket_ucb`: **max regret difference = 0.0** across
all scenarios × seeds. The experiment **can** detect equivalence (it did).

## Results (mean over 5 seeds, regret ↓ / opt-ID ↑)

| scenario | random | raw_ucb | bucket_ucb | bucket_baseline | ccsoc_qual_adj | oracle |
|---|---:|---:|---:|---:|---:|---:|
| A no confound | 38.9 / .35 | 19.7 / .64 | 23.7 / .57 | 23.7 / .57 | 23.8 / .57 | 0 / 1.0 |
| B state difficulty | 22.1 / .35 | 16.5 / .41 | **16.0 / .48** | 16.0 / .48 | 16.4 / .47 | 0 / 1.0 |
| C quality (exogenous) | 28.0 / .35 | 12.0 / .48 | 14.3 / .48 | 14.3 / .48 | 14.9 / .46 | 0 / 1.0 |
| D near-tie | 0.78 / .34 | 0.82 / .33 | 0.79 / .33 | 0.79 / .33 | 0.77 / .35 | 0 / 1.0 |
| E drift | 40.3 / .33 | 23.1 / .59 | 26.7 / .53 | 26.7 / .53 | 28.0 / .51 | 0 / 1.0 |

## Interpretation per scenario

- **A:** bucketing splits data without benefit — expected; no damage beyond
  sample splitting.
- **B:** bucket UCB > raw UCB — supports state conditioning when best arm
  differs by state. This is the only scenario favoring buckets.
- **C:** quality was exogenous (independent of arm), so no confounding existed;
  quality adjustment cannot help and slightly hurts (extra estimation noise).
  **Limitation:** real traces assign operators conditional on state, which
  correlates with quality — needs a generator with endogenous assignment.
- **D:** all UCBs near chance (true gaps tiny vs noise 0.12) — consistent with
  near-tie instability; no false advantage for fancy estimators.
- **E:** none of the estimators track drift (no decay implemented); raw UCB
  actually best here — **decay design remains open**.

## Answers to protocol questions

1. Experiment **does** detect equivalence (0.0 difference). Good.
2. Confound “advantage” of subtraction: **none** (by construction).
3. No extra decision budget favored any arm (equal pulls).
4. Synthetic only — cannot be cited as optimization performance.

## Limits

- Exogenous contexts/qualities; endogenous assignment not simulated.
- No decay; drift scenario exposes that gap.
- Single noise level; 5 seeds (directional).
