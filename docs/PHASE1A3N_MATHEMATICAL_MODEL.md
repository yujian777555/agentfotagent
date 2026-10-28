# Phase-1A-3N Mathematical Model

## Estimation targets (distinct)

1. **Std. operator value in state b:** E[r | do(a), b, q standardized]
2. **Conditional best action:** argmax_a E[r | a, x_t]  (x_t = (b,q,d,u))
3. **Long-run algorithm performance** ≠ single-step reward (out of scope here)

This battery estimates (2) via sequential decisions; regret uses the true
conditional mean at each (b,q,t).

## Logged quantities (per decision, recorded at decision time)

- context x_t = (b_t, q_t, d_t, u_t) (here d_t,u_t folded into b/t)
- action a_t, reward r_t
- **true logging propensity** e_t(a) from the behavior policy (known in synthesis)

## Estimators

| id | formula | assumption | bias if violated |
|---|---|---|---|
| raw UCB | mean r over a | none | confounded by b,q |
| bucket UCB | mean r over (a,b) | b sufficient | q mix inside b remains |
| quality residual | mean of r − ĝ_b(q); ĝ = LS of r on q within b | E[r|a,b,q] = μ_a,b + g_b(q) (no interaction) | misspecified g → residual bias |
| IPW | Σ 1(A=a)r/e(a) / Σ 1/e(a) (clipped at 10) | correct logged e, positivity | no overlap → infinite variance / unidentifiable |
| DR | m̂_a(x) + 1(A=a)/e(a)·(r−m̂_a(x)), LOO cross-fit | either m̂ or e correct | both wrong → biased; small e → variance |

**Quality residual is not a causal claim** — it is a conditional-mean
adjustment under the stated additive model.

**Positivity:** cells with e(a)=0 are marked unsupported. Full refusal
requires the selector to consult the support set *before* committing.

## Decision rule

All UCB-style: argmax of estimate + β√(log N_b / n). Same β, same pulls.
