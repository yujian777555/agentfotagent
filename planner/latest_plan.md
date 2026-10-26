# Latest Plan — P0-R3: Project-Owned Experimental Environment

- Date: 2026-10-26
- Baseline before this planning update: d52f7b43a03f5b1bbddb3990b2c1587322caa3de
- Status: own-environment design frozen for review; scaffold implementation is the next task; no scientific experiment or live API call authorized

## Correction to the previous plan

NeuroEvoScientist and EvoPareto-Agent are **not** candidate environments for this project. They are separate projects and may only be used as read-only references when checking prior-art mechanisms or identifying common evaluation pitfalls. agentfotagent must own its target Agent-evolution environment, genotype/phenotype implementation, evaluator, experiment runner, task manifests, baselines and result provenance.

MetaBox-v2 is retained only as the standardized source-domain optimization substrate. The target environment will be built in this repository as the **Agent Evolution Sandbox (AES)** (working name). AES is an internal experimental system, not a novelty claim by itself.

## Current research evidence

1. Generic Agent-driven operator selection is crowded (EoH/LLaMEA/LLM4EO/LAOS/AwesomeDE/LMCOEA).
2. Generic bidirectional/recursive self-improvement is crowded (including Hyperagents and related systems).
3. Cross-domain transfer remains a high-risk hypothesis. It must be demonstrated against target-only tuning and shuffled-mapping controls.
4. No implementation, MetaBox meta-training, or live LLM API experiment has yet been performed in this repository.

## Task 1 — Implement Phase-0 AES scaffold

Build only the environment and experiment contracts described in [OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md](../docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md).

Required minimum:
- versioned Agent genome schema and normalization;
- explicit genotype-to-phenotype compiler/runtime;
- deterministic controlled multi-step tool-use world with hidden goal predicates;
- procedural task generation with task-family train/dev/held-out manifests and hashes;
- evaluator that derives primary success only from terminal environment state;
- execution trace and immutable run manifest with seed/config/backend provenance;
- mock backend for engineering tests only, never scientific performance claims;
- same-interface random-search and conventional EA baseline skeletons using the identical evaluator;
- tests for every active gene's behavioral effect, deterministic reset/step, leakage prevention, split isolation, cache isolation, failure-closed evaluation and baseline fairness.

Do not implement a new research controller or a new NSGA-III. The purpose of this task is to make the experimental object executable and auditable.

## Task 2 — Planner audit of the environment

After the scaffold is pushed, independently check:
- whether each genome field changes real runtime behavior;
- whether the task suite has verifiable success conditions and nontrivial multi-step solvability;
- whether any hidden state, test answers, cache artifacts or score shortcuts leak into the Agent;
- whether random search and conventional EA use exactly the same evaluator and effective phenotype space;
- whether task-family holdouts test generalization rather than only new seeds.

If a gate fails, repair the scaffold before any scientific experiment.

## Task 3 — Define the transfer object against the executable interfaces

Only after the environment contract passes, specify one transfer object and its source/target state-action semantics. Compare it with LAOS, LMCOEA/AwesomeDE, Harmony Harness and target-only tuning. Include a shuffled-mapping negative control. If transfer is just a manually authored adapter or does not beat target-only tuning, recommend NO-GO/PIVOT.

## Task 4 — Separate experiment authorization

No live API calls, GPU pilot, MetaBox meta-training, or confirmatory task evaluation until a later plan specifies and approves:
- model/backend and version;
- task families and frozen splits;
- evaluation arms, seeds and statistical plan;
- API/token/cost cap and failure handling;
- primary metric and minimum meaningful effect.

## Hard constraints

- Evolutionary computation remains the method core.
- MetaBox is infrastructure, not a contribution.
- Finite-budget allocation is not the core innovation.
- Predecessor repositories are read-only references, never dependencies or result sources.
- Do not equate mock-backend tests with Agent capability evidence.
- Do not claim novelty or successful transfer before confirmatory evidence.

## Exit gate

P0-R3 passes only when the in-repository AES scaffold and its engineering tests are independently reviewed. Research algorithm development begins after that gate, not before.
