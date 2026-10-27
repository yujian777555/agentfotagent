# Latest Plan — P0-R3: Project-Owned Experimental Environment

- Date: 2026-10-26
- Baseline before this planning update: d52f7b43a03f5b1bbddb3990b2c1587322caa3de
- Scaffold implementation baseline: d32e07c4599603260757ad64da757877b97587bf
- Status: Phase-0 scaffold implemented; independent static audit at `987df6d` returned REQUEST CHANGES. Blocking semantics/provenance issues must be fixed before acceptance. No scientific experiment or live API call authorized.

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

**Status: COMPLETE (engineering).** Delivered under `src/agentfotagent/`, `tests/`, `configs/`, `results/manifests/`.
Families: `key_crate` (train/dev), `dial_set` (train/dev), `relay_route` (held-out only).
Tests: 56 engineering tests, all passing (`python -m pytest tests`). Mock backend only.

## Task 2 — Planner audit of the environment

After the scaffold is pushed, independently check:
- whether each genome field changes real runtime behavior;
- whether the task suite has verifiable success conditions and nontrivial multi-step solvability;
- whether any hidden state, test answers, cache artifacts or score shortcuts leak into the Agent;
- whether random search and conventional EA use exactly the same evaluator and effective phenotype space;
- whether task-family holdouts test generalization rather than only new seeds.

If a gate fails, repair the scaffold before any scientific experiment.

**Status: PENDING independent Planner review.** Executor self-reports all Phase-0
engineering gates passing (see spec §8.1) but this is not a substitute for audit.

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


## Independent Planner audit result — 2026-10-26

**Verdict: REQUEST CHANGES.** See [PHASE0_INDEPENDENT_AUDIT_2026-10-26.md](../docs/PHASE0_INDEPENDENT_AUDIT_2026-10-26.md).

Blocking items:
1. Tool-world preconditions permit remote unlock/place/dial/relay actions, allowing state teleportation and invalid shortcuts.
2. Planning and verification genes alter traces but do not currently control downstream decisions as their names/specification imply; memory decisions also bypass the phenotype memory interface.
3. PublicTask includes deterministic seed/generator metadata in an interface described as runtime-visible.
4. BaselineHarness discards actual traces and creates synthetic incomplete traces for manifests; the existing reconstruction test does not exercise this path.
5. Evaluator can accept malformed key-crate state when the crate record is missing and can accept an empty dial target mapping.

Additional pre-science concerns: random search/EA duplicate genotypes interact with caching without actual-evaluation accounting; three held-out examples from one known family are only engineering smoke tests, not generalization evidence.

### Next task — Phase-0-R1 corrective pass

Fix only the audit findings, add regression tests, rerun the entire test suite on the pushed commit, update the audit response matrix and status, then stop for independent review. Do not implement transfer, MetaBox meta-training, live APIs or GPU experiments.

**Status: CORRECTIVE PASS IMPLEMENTED (executor).** See docs/PHASE0_R1_AUDIT_RESPONSE.md.

Fixed with regression tests:
1. Tool-world locality preconditions (F1) — remote unlock/place/dial/relay rejected; unlock releases at container; failed actions do not mutate business state. tests/test_tool_preconditions.py
2. Gene semantics (F2) — plan consumed by phase gates; verification reads verify_state and blocks submit; memory uses phenotype.recall(). tests/test_gene_semantics.py
3. Runtime payload isolation (F3) — RuntimeTask vs TaskInstance; backend payload tests. tests/test_runtime_payload_isolation.py
4. Actual-trace provenance (F4) — BaselineHarness keeps EpisodeTraces; best-record genome hash; E2E JSON round-trip reconstruction. tests/test_harness_reconstruction.py
5. Fail-closed evaluator (F5) — tests/test_evaluator_failclosed.py
6. Evaluation accounting (C1) — proposals/unique/cache-hits/episodes. tests/test_evaluation_accounting.py

Full suite rerun on the corrective commit: python -m pytest tests -q (executor-reported all pass; mock backend only).

### Stop

Executor stops. Waiting for independent Planner re-review of the corrective commit. No transfer experiments, MetaBox meta-training, live APIs or GPU runs.
