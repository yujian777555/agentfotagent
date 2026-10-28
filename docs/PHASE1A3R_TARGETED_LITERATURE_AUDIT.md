# Phase-1A-3R Targeted Literature Audit

Focus: does anything already cover (i) state-bucketed operator credit,
(ii) target-quality correction, (iii) propensity/doubly-robust operator credit?

## Findings (evidence grades)

| thread | closest works | mechanism | covers bucketed UCB? | covers quality correction? | grade |
|---|---|---|---|---|---|
| State-aware AOS | Fialho et al. 2008 (DMAB AOS); later “AOS with landscape features” (e.g. Sharma/Crepinsek lines) | reward Δf; some use state/phase features | **partially — variants exist** | rare | PARTIAL |
| Contextual bandits in EC | various “contextual operator selection” papers | UCB/Thompson on contexts | **yes in essence** | not with parent-quality residual | PARTIAL |
| Credit assignment noise | RL-AOS (e.g. MARLE), bandit variants | discounted Δf | some | weak | PARTIAL |
| Target-quality / counterfactual | not found in EC AOS under these names | — | no | **not found** (absence unproven) | SECONDARY |
| Propensity/IPW/DR in EC AOS | not found in EC AOS under these names | — | no | no | SECONDARY |
| LLM-driven AOS (LAOS etc.) | LAOS GECCO'25 abstract | LLM picks operator from state+credit | credit not verified | no | SECONDARY |

## Answers

1. **Same/equivalent state-conditioned credit?** Bucketed UCB ≡ standard
   contextual-bandit operator selection. **ALREADY_COVERED risk high** at the
   “state buckets + UCB” level. Cannot claim this as the novel core.
2. **Target-quality correction already done?** Not located in EC AOS under
   common names; **not found ≠ does not exist**. Needs deeper survey
   (IPW/causal bandits literature) before any novelty claim.
3. **True incremental mechanism (if any):** quality-residualized,
   propensity-logged operator credit with explicit overlap. Current
   mathematical audit shows the proposed subtraction is a no-op, so as
   written there is **no** incremental mechanism.
4. **Independent empirical question worth keeping:** “Does bucketed AOS beat
   global AOS on multi-modal/phase-shifting problems?” — replication-grade
   study is honest and publishable as an empirical analysis, not as a new
   algorithm.

## Novelty verdict

- State-bucketed UCB AOS: `ALREADY_COVERED` (essentially contextual bandits).
- Baseline-subtraction credit: **invalidated by math audit**.
- Quality-residual + propensity credit: `NOVELTY_UNRESOLVED` — only viable
  path to a new method; requires verified literature gap + decision-difference
  proof before formal experiments.

## Honesty

This session read method-level sources for JADE/SHADE/L-SHADE/Fialho-class
AOS and abstracts for LAOS/EoH; full-text of the nearest state-aware AOS and
causal-bandit-in-EC papers was **not** obtained. Absence claims are weak.
