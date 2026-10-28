# Phase-1A-3N2 Results (single frozen run)

Data: `results/phase1a3n2/final_falsification.json`
Config hash `4781d8216fe092cc`. Behavior-policy frequency check on C:
empirical vs expected propensity max |diff| = 0.0024 (MC-consistent).

## C (primary): mean regret ↓

| learner | regret | opt-ID |
|---|---:|---:|
| bucket_ucb | **0.00** | 1.00 |
| quality_residual_shuffled_q | **0.00** | 1.00 |
| quality_residual | **21.03** | ~0.4 |
| ipw/df variants | 4.6–8.9 | 0.70–0.77 |

**Paired quality_residual vs bucket_ucb: 0-10-0.** Quality residual is strictly
worse on the only scenario built to motivate it.

## Why (mechanism)

δ_op makes **op0 always optimal**; q only shifts the *baseline* reward.
Bucket UCB learns op0 (regret 0). Residualizing r on q removes a
q-dependent baseline and **injects variance** into arm estimates → wrong
ranking. `shuffled_q` (quality scrambled) restores regret to 0.00 — the
harm comes from the correction itself, not from data structure.

## Other scenarios (mean regret)

| scenario | bucket | qual | shuf_q | ipw | dr |
|---|---:|---:|---:|---:|---:|
| A | 0.00 | 0.00 | 0.00 | 4.6 | 8.9 |
| B | 1.18 | 1.17 | 1.17 | 1.6 | 2.3 |
| D | 2.27 | 2.27 | 2.27 | 1.4 | 2.3 |
| E | 61.0 | 61.0 | 61.0 | 61.0 | 61.0 |
| F | 59.7 | 59.8 | 59.8 | 58.1 | 60.0 |

## Support / refusal (E)

zero-propensity cell (b=1,a=2) is excluded from ranking (unit-tested).
`refused=0` counts full-policy refusal only; ranking-level exclusion works
but the **100%-refusal gate metric was not the same quantity** — recorded
as gate-5 measurement mismatch, not a silent pass.

## Gate table

| gate | result |
|---|---|
| C ≥9/10 wins | **FAIL (0-10)** |
| C ↓10% regret | **FAIL (worse: 0→21)** |
| paired uncertainty | **FAIL** |
| A non-inferior | PASS (tie) |
| E refusal | partial (ranking exclusion yes; metric mismatch) |
| shuffle-q weakens gain | PASS as negative control (shuffle removes harm) |
| equal data/budget | PASS |
