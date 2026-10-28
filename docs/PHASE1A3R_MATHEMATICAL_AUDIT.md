# Phase-1A-3R Mathematical Audit — CC-SOC

**Verdict on current formula: `CC_SOC_CURRENT_FORMULATION_INSUFFICIENT`.**

## Q1 — Is the second term a shared constant for fixed b?

Yes. C(a,b) = E[r|a,b] − E[r|·,b]. For fixed bucket b, E[r|·,b] does not
depend on a. It is a per-bucket constant c_b.

## Q2 — Same ranking as raw-reward UCB?

Yes, **exactly**. Selection score:

  E[r|a,b] − c_b + β√(log N_b / n(a,b))   vs   E[r|a,b] + β√(log N_b / n(a,b))

Subtracting c_b is order-preserving. With identical estimates, counts and
exploration term, argmax is **identical**. Empirically confirmed:
`max_regret_diff = 0.0` across all synthetic scenarios and seeds
(`results/phase1a3r/synthetic_falsification.json`).

**Consequence:** “baseline subtraction” cannot be an independent contribution.
The honest mechanism is **state-bucketed UCB** on raw rewards (= contextual
bandit over φ(s)). Any claim that subtraction “controls confounds” is false
for within-bucket selection.

## Q3 — Does bucketing control target-individual quality?

No. Within bucket b, parent quality still varies and scales observed r
(Scenario C generator: r = intrinsic(op) + 0.5·quality). Bucket means mix
operator effect and quality mix. Residualizing r on quality **can** change
orderings in principle, but the prototype residualizer in this pass
(`ccsoc_quality_adjusted`) did **not** beat bucket UCB on our scenarios —
needs a design where operator assignment correlates with quality (as in real
traces) before claiming benefit.

## Q4 — Identifiability with disjoint supports?

If op1 only in easy states and op2 only in hard states (as in A2R traces),
E[r|a,b] cells are missing. **Not identifiable** without overlap. Coverage
forcing (try each (a,b) once) creates minimal support but cannot remove
variance; propensity logging / randomized exploration is required for
causal-grade claims.

## Q5 — Coverage vs randomization

Coverage builds a support set (needed). Without recorded selection
probabilities, any IPW/doubly-robust estimator is invalid. Minimal honest
approach: ε-randomized selection with logged propensity.

## Q6 — FE half-life decay

Changes effective sample size and can change orderings when arms are sampled
unevenly; not a free regularizer. Must be specified as exponential weight
w_i = 2^(-ΔFE/half_life) applied in means/variances; our prototype used
unweighted windows — **not implemented**, recorded as open design item.

## Decision

Keep **bucketed UCB** as the honest core (Scenario B shows it beats raw UCB
when states differ). Do **not** claim baseline-subtraction novelty. If a
distinct estimator is wanted, the next candidate is **propensity-logged
ε-greedy + quality-residualized rewards** with proof that rankings differ
from raw UCB on constructed cases — otherwise `NO_GO` on method novelty.
