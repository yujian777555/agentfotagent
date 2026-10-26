# Latest Plan — P0-R2: Novelty Collision and Transfer-Object Audit

- Date: 2026-10-23
- Baseline: 78100d803856575da9ba338ce88e6cd34d9a4c58
- Status: literature audit partial; no implementation or live API run authorized

## Completed
1. Rechecked current repository state and predecessor-asset evidence boundaries.
2. Completed a first-pass mechanism-level review of EoH, LLaMEA source, LLM4EO, AwesomeDE, Hyperagents, Harmony Harness and related Agent RSI methods.
3. Established that generic H1 (LLM/Agent diagnoses traces and modifies operators) and generic H3 (recursive/bidirectional self-improvement) are not defensible standalone novelty claims.
4. Narrowed H2 to a specific but still unconfirmed hypothesis: transfer the same explicit control object from numerical MetaBox optimization to a structurally different Agent-genotype search space.

## Task A result — LAOS / LMCOEA nearest-neighbor review (2026-10-26)
- LAOS: official GECCO 2025 abstract verified. It uses an LLM meta-prompt with progress/best-fitness/diversity and operator-credit information, plus offline and online replay layers. Full text and official code were not obtained; details beyond the abstract remain unverified.
- LMCOEA: publisher-indexed article text and the linked GitHub repository were inspected. The code generates DE-specific MATLAB offspring-update functions, scores them against a baseline DE run, and selects strategy IDs using aggregated numerical-problem rewards. It does not expose a ready-made controller that transfers directly to Agent-genotype search.
- The linked repo README claims MIT, but the observed tree has no root LICENSE; it also contains machine-specific paths and a placeholder API-key literal. It was not run. No live API calls were made.
- Detailed record: [LAOS / LMCOEA Mechanism Audit](../docs/LAOS_LMCOEA_MECHANISM_AUDIT_2026-10-26.md).

## Next task B — Define and falsify one transfer object
Choose exactly one of executable state-action rules, policy parameters, or a learned control representation. Specify source and target observations/actions, invariant semantics, adaptation data, target-test isolation, and a shuffled-mapping negative control. Explicitly test whether the proposal is just LAOS-style AOS, LMCOEA/AwesomeDE-style generated update rules, Harmony Harness transfer, or target-only retraining. If the mapping is only an adapter or conceptual analogy, revise or abandon H2 before coding.

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
