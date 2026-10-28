# Phase-1A-3N Synthetic Protocol (frozen)

Code: `scripts/phase1a3n_endogenous_battery.py`
Data: `results/phase1a3n/endogenous_battery.json`
Params: horizon 600, β=1, seeds 11..110 (10 seeds), ε=0.1 floor, clip=10.

## Generators (true mean known)

| scenario | design |
|---|---|
| A no confounding | constant per-op means; assignment ≈ independent of q |
| B state difficulty | best op differs by bucket; low/high base reward |
| C endogenous quality | r = 0.10+0.6q+δ_op; **behavior assigns op0 mostly to high-q** |
| D near tie | means within 0.004; σ=0.08 |
| E no support | P(op2\|b=1)=0 exactly |
| F drift | best op flips at t=300 |

Marginal-frequency control for C is encoded via ε-floor mixing; full
frequency-matched control remains a follow-up.

## Metrics

regret vs true conditional best; opt-ID rate; switch count; refusal count;
clip counts. 10 paired seeds per cell.

## Pass gates (pre-registered)

1. C: quality method beats bucket UCB with paired support
2. A: no large degradation
3. E: correct refusal / no fake identification
4. ≥1 repeatable ranking difference in the right direction

## Limitations recorded before results

- Estimator chooses actions freely (not forced to behavior policy), so
  support-refusal may be under-exercised.
- d_t, u_t not fully represented.
