# Phase-1A-3N2 Protocol (frozen)

Config hash: `4781d8216fe092cc` — horizon 600, β=1, ε=0.08, σ=0.08, seeds
[11,22,33,44,55,66,77,88,99,110]. Behavior policy logs full propensity
vectors; actions sampled from e_t; same data for all learners.

## Scenario C (primary test)

true μ = 0.10 + 0.6q + δ_op, δ=[0.05, 0.02, 0.0] → **op0 is always best**;
behavior assigns op0 more often to high-q (endogenous baseline shift).

## Pre-registered gates (quality_residual vs bucket_ucb on C)

1. ≥9/10 paired wins  2. mean regret ↓≥10%  3. paired uncertainty supports
4. A non-inferior  5. E refusal 100%  6. shuffle-q weakens C gain  7. equal data/budget

**Any failure → `NO_GO_FOR_QUALITY_CREDIT_METHOD`.**
