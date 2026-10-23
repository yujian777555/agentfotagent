# Latest Plan — P0-R2: Novelty Collision and Transfer-Object Audit

- Date: 2026-10-23
- Baseline: c1d7400c30f432c4e3abc5df0d7a99cfd7979774
- Status: literature audit partial; no implementation or live API run authorized

## Completed
1. Rechecked current repository state and predecessor-asset evidence boundaries.
2. Completed a first-pass mechanism-level review of EoH, LLaMEA source, LLM4EO, AwesomeDE, Hyperagents, Harmony Harness and related Agent RSI methods.
3. Established that generic H1 (LLM/Agent diagnoses traces and modifies operators) and generic H3 (recursive/bidirectional self-improvement) are not defensible standalone novelty claims.
4. Narrowed H2 to a specific but still unconfirmed hypothesis: transfer the same explicit control object from numerical MetaBox optimization to a structurally different Agent-genotype search space.

## Next task A — Complete nearest-neighbor review
Find and inspect the full LAOS paper and LMCOEA paper/official artifacts. Record only verified method details; if inaccessible, document the limitation and do not overstate novelty.

## Next task B — Define the transfer object before code
Choose exactly one: (i) executable state-action rules, (ii) policy parameters, or (iii) a learned control representation. Specify source observations, target observations, source actions, target actions, invariant semantics, adapter learning data, and the rule that prevents target test leakage. If this cannot be done without hand-authoring target policy, revise H2.

## Next task C — Audit downstream Agent phenotype and evaluator
Compare NeuroEvoScientist and EvoPareto-Agent. Verify each genome field actually changes executable behavior; locate the official evaluator and a genuine random-search arm; identify strong target-domain adaptive baselines. Do not select an environment just because it is already implemented.

## Next task D — Freeze the minimum discriminative experiment
Required arms: standard target EA, random search, strong target adaptive controller, target-only controller tuned on development tasks, source-transfer controller, fixed generic controller, and shuffled mapping negative control. Hold out task families, not just random seeds of the same task. Predefine primary metric and minimum meaningful effect before confirmatory runs.

## Hard constraints
- Evolutionary computation remains the method core.
- Finite-budget allocation is not the research contribution.
- MetaBox is infrastructure, not a contribution.
- Do not add a new NSGA-III implementation before novelty and phenotype gates pass.
- Do not call real LLM APIs until scope and call/token/cost caps are separately approved.
- Do not modify predecessor repositories or claim upstream reports as independently reproduced.

## Exit gate
Implement only after a defensible mechanism-level difference survives comparison with Hyperagents, Harmony Harness, LLM4EO, AwesomeDE/LMCOEA and target-domain Agent evolution baselines. If the cross-representation mapping is merely an adapter or conceptual analogy, stop and revise.
