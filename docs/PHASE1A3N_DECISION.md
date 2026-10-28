# Phase-1A-3N Decision

## What is established

- Baseline subtraction (old CC-SOC) is a **no-op** (3R). Frozen.
- Bucketed UCB helps only when state changes the optimal arm (B); it is
  essentially contextual-bandit AOS — novelty risk high (3R).
- **Quality residualization (C)**: small gain on the one endogenous-quality
  scenario (7-3 paired; mean −2.3%) but **weak support** (p≈0.17) and slight
  loss on A (4-6). Not a robust win.
- **IPW/DR** win B/E/F for variance/drift reasons; **IPW collapses on C**
  (0-10) — propensity weighting without a quality model is harmful there.
- Support-set refusal was **not exercised** (refused=0): battery lets estimators
  choose freely; fail-closed UNIDENTIFIABLE path untested.
- 0 LLM, 0 MetaBox, 0 test split; synthetic only.

## Literature (targeted, PARTIAL)

State-conditioned/contextual AOS: covered in essence (ALREADY_COVERED risk).
Parent-quality residualization and logged-propensity/DR in EC operator credit:
**not found** in this pass (absence unproven; causal-bandit literature likely
overlaps). Even if novel, current evidence is too weak to justify a new method.

## Gate verdict

**`NO_GO` for a new-algorithm claim on the current evidence.  
`METHOD_REVISION_REQUIRED` for the experimental battery (support-set design).**

Do **not** launch the 2000-FE MetaBox formal experiment.

## Allowed next moves (pick one; do not expand scope)

1. **Path R (empirical/replication, preferred):** honest study “when does
   bucketed AOS beat global AOS / SHADE?” with preregistered BBOB splits —
   publishable as analysis, no algorithm-novelty claim.
2. **Path N2:** fix battery (behavior-policy-driven actions; explicit refusal
   on e=0; shuffle-q / shuffle-e ablations) and rerun once. If C gain does not
   reach pre-set support (e.g. 9-1, mean −10%), record final `NO_GO`.
3. **Stop** this mechanism line and keep Agent as diagnosis/ablation tool in
   whichever path is chosen.

## Formal-experiment status

**NOT AUTHORIZED.** Protocol from 3R remains a draft only.

## Phase-1B

Not started. Even if Path R proceeds, Agent-optimization linkage stays design
notes until Phase-1A has independently validated evidence.
