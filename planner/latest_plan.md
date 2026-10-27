# Latest Plan — P0-R3: Project-Owned Experimental Environment

- Date: 2026-10-26
- Baseline before this planning update: d52f7b43a03f5b1bbddb3990b2c1587322caa3de
- Scaffold implementation baseline: d32e07c4599603260757ad64da757877b97587bf
- Status: Phase-0-R1 corrective code is pushed (code commit ebd3d99; current main before this review 3322a9d). Independent re-review returned REQUEST CHANGES because residual payload-isolation, verification, fail-closed evaluation, provenance and versioning gaps remain. No scientific experiment or live API is authorized.

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

**Status: REQUEST CHANGES after independent Planner re-review (2026-10-27).** GitHub Actions independently reproduced the existing suite on source commit `ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9`: **104 passed in 0.24s** ([run](https://github.com/yujian777555/agentfotagent/actions/runs/40441941389)). Source review still found residual defects documented in `docs/PHASE0_R1_INDEPENDENT_REVIEW_2026-10-27.md`; passing the existing suite does not close them.

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


## Independent re-review — 2026-10-27

**Verdict: REQUEST CHANGES.** Audit source tree: 3322a9d8eef80308a50c55f25292d4034d94699f; implementation fixes are in ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9. Full report: [PHASE0_R1_INDEPENDENT_REVIEW_2026-10-27.md](../docs/PHASE0_R1_INDEPENDENT_REVIEW_2026-10-27.md).

Residual blockers:
1. RuntimeTask.task_id still encodes {family}/{split}/seed{seed}, and run_episode sends it in backend context; the new payload test checks field names but not encoded values.
2. Relay verification treats any non-null frequency as passing, even if it is wrong.
3. Missing relay objects bypass locality checks in activate_relay / set_frequency; evaluator also accepts a relay-state mapping with no objects["relay"].
4. Fail-closed validation is incomplete: partial dial target maps and missing crate_unlocked goal constraints can pass; malformed step values can still raise during evaluation.
5. Artifact reconstruction does not detect manifest scores with missing traces; reusing a harness can mix traces/accounting across runs.
6. Environment/evaluator/mock-backend version identifiers were not bumped after semantics changed, weakening cache/provenance separation.

Correct only these residual issues, add adversarial regression tests, rerun the complete suite in a reachable environment, update the response matrix and status, push, then stop for another independent review. No transfer, MetaBox, live API or GPU experiments.

## Independent test reproduction of the R1 source tree — 2026-10-27

The full existing R1 suite was independently run through GitHub Actions on the exact R1 source commit `ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9` (Python 3.11.17, Ubuntu): **104 passed in 0.24s**. Run evidence: https://github.com/yujian777555/agentfotagent/actions/runs/40441941389. This is engineering evidence only; the phase remained REQUEST CHANGES because the residual gaps in the independent review were not yet fixed on that tree.

## Phase-0-R2 residual audit response — 2026-10-27

**Basis:** docs/PHASE0_R1_INDEPENDENT_REVIEW_2026-10-27.md (REQUEST CHANGES on ebd3d99).

Executor fixed residual findings R1-01..R1-06 only:
- R1-01 opaque runtime_id (no family/split/seed in backend payload)
- R1-02 relay verification compares expected frequency from note fragments
- R1-03 missing/malformed relay object fail-closed in tools and evaluator
- R1-04 complete dial/key_crate/relay goal schemas; safe step metrics
- R1-05 bidirectional trace/score reconstruction; run-scoped harness state
- R1-06 version identifiers advanced to v2; source commit SHA in run manifests

Response matrix: docs/PHASE0_R2_AUDIT_RESPONSE.md.

R2 full-suite result has now been independently reproduced on exact source commit ec73906e15c048285cff3bca90a4f1f8bed21da8: **127 passed in 0.43s** on GitHub Actions run [40453697835](https://github.com/yujian777555/agentfotagent/actions/runs/40453697835). Adversarial probes in the same run found residual issues; see docs/PHASE0_R2_INDEPENDENT_REVIEW_2026-10-27.md. The suite is engineering-only, not Agent capability evidence.

**Status: RESIDUAL FIXES IMPLEMENTED (executor). NOT ACCEPTED.** Next step is independent code review of the R2 tree — not a scientific experiment. No transfer experiments, MetaBox meta-training, live APIs or GPU runs.


## Independent Phase-0-R2 review — 2026-10-27

**Verdict: REQUEST CHANGES.** The exact R2 code tree at ec73906e15c048285cff3bca90a4f1f8bed21da8 was independently tested on GitHub Actions: 127 passed in 0.43s. The same run executed targeted adversarial probes and found four residual issues: (1) deterministic runtime IDs reveal the seed by brute-force lookup against the public task generator; (2) relay goals with code=None and frequency=99 can pass the evaluator; (3) key_crate states with missing object type records can pass; (4) reconstruction accepts a manifest with invalid_actions tampered from 0 to 999999. Full report: docs/PHASE0_R2_INDEPENDENT_REVIEW_2026-10-27.md; reproducibility record: docs/PHASE0_R2_TEST_REPRODUCTION_2026-10-27.md.

Required next pass:
1. Replace content-derived runtime IDs with a genuinely opaque token or keyed identifier unavailable to the Agent; preserve stable evaluation manifests separately and test seed enumeration attacks.
2. Validate relay goal value types, digit format, frequency range and code/frequency consistency.
3. Make evaluator required-entity validation fail closed for malformed key_crate and relay state records, including required object types and locations.
4. Compare every recorded score field against reconstruction, including success, steps, invalid_actions, repeated_states, termination_reason and final-state hash; add per-field tampering tests.
5. Rerun the complete suite on the corrected source commit, update status and response matrices, then stop for another independent review.

**Status: NOT ACCEPTED.** No scientific experiments, live API, GPU or MetaBox meta-training are authorized until the next independent review accepts the environment.


## Phase-0-R3 independent review — 2026-10-27

Exact R3 candidate source `cd07249a1b4675354b01f9d5ac09ab2ffe4d2033` was independently tested in GitHub Actions run 40459330792: **162 passed in 0.87s** on Python 3.10.22. The candidate remains **REQUEST CHANGES / NOT ACCEPTED** because independent adversarial probes found: (1) persisted `success=True` changed to integer `1` is accepted by reconstruction; (2) unknown score fields are accepted; (3) key_crate succeeds when crate/surface location fields are missing. In addition, `tests/probe_r2_counterexamples.py` falsely reports PASS for both vulnerable and correct outcomes on R3-01 and R3-04 due to its exception handler. Details: `docs/PHASE0_R3_INDEPENDENT_REVIEW_2026-10-27.md`.

Next: fix R3-05 through R3-08, add regression tests including a self-test of the probe harness, rerun the full suite and independent review. Do not merge to main or start scientific experiments.


## Phase-0-R4 independent review and Phase-1 pivot — 2026-10-27

The exact candidate `3e48bf5305ba667490358c140dad556f1ebf84e2` on `phase0-r4-fixes` passed hosted CI run 40462185561: 189 tests passed in 0.64s; 62 targeted tests passed in 0.25s; original/R4 counterexample probes 7/7 PASS. Independent static review accepts this candidate for the **engineering gate only**. The source has not been merged into main; integrate it while preserving the R1–R3 audit trail. Review: `docs/PHASE0_R4_INDEPENDENT_REVIEW_2026-10-27.md`.

The Phase-1 pilot is **NO_GO_OR_PIVOT** for the current transfer setup: all 16 genotypes solved all six small train tasks, the primary success metric is saturated, and the source prior is a hand-written surrogate rather than MetaBox or an Agent-generated controller. Do not scale this pilot.

Next sequence: (1) integrate R4 to main; (2) define and review Phase-1A on MetaBox-v2 where an Agent diagnoses real evolutionary trajectories and proposes constrained controller changes; (3) compare to strong EC and LLM-assisted baselines on held-out tasks; (4) only if Phase-1A is positive, test transfer of the same explicit controller to AES; (5) only if transfer is reproducible, test bidirectional feedback. The pilot review is `docs/PHASE1_PILOT_REVIEW_2026-10-27.md`.

No live LLM API calls until a call/token/cost budget is explicitly approved. Do not use mock results as scientific evidence.


## Post-merge state and next executable phase — 2026-10-27

PR #2 integrated the reviewed R3/R4 AES source, tests and pilot artifacts into `main`. Merge commit: `9e59401dd78f4be830c45634767bd3f65fb4b4ed`. Integration CI run 40464369334 passed on merge tree `f01a7ecc1f007276ff425d4894a8aa57dfc35bac`: 62 targeted tests, 189 full-suite tests and all 7 probes passed. Phase-0 is accepted as engineering infrastructure only; no Agent-capability or scientific claim is established.

**Do next: Phase-1A Agent-assisted EC on MetaBox-v2.** Do not expand the current surrogate-source→AES pilot: every genotype solved all six tasks, the success objective is saturated, and the source prior was manually specified rather than produced by MetaBox or an Agent. Phase-1A must have the Agent inspect actual evolutionary trajectories and propose constrained, executable controller changes. Compare against strong conventional adaptive EC and relevant LLM-assisted EC baselines; freeze objective, evaluation budget, seeds, validation/test split, negative controls and stop rules. Live LLM calls remain disabled until an explicit call/token/cost budget is approved. Only if Phase-1A is reproducibly positive should the same controller object be transferred to AES; bidirectional feedback is conditional on positive transfer evidence.


## Phase-1A MetaBox protocol published — 2026-10-27

Created `docs/PHASE1A_METABOX_PROTOCOL.md`. Immediate next task is P1A-0: pin the official MetaBox-v2 source, inspect the actual installed API/baseline catalog, and run a no-LLM integration smoke that validates FE accounting, objective direction, seed determinism, metric calculation, and typed-controller compilation. Then freeze function-level train/validation/test splits and compare against verified strong baselines.

The Agent pilot requires a real local model or explicit approval for a live API call/token/cost budget; no hand-written surrogate may be presented as Agent-generated knowledge. The current source-prior→AES pilot remains NO_GO_OR_PIVOT. Transfer to AES is conditional on a reproducible positive held-out Phase-1A result.

## Phase-1A P0 MetaBox integration smoke — 2026-10-27

Branch \phase1a-metabox-smoke\. Official metaevobox 2.0.2 (git 5565a281, v2.0.0) installed in isolated Python 3.11.15 venv. Verified BBOB-10D + DE path, minimization direction, FE accounting, seed reproducibility. Typed controller DSL with two legal fixed controllers executed through real MetaBox config. Function-identity split frozen 12/6/6. Report: docs/PHASE1A_METABOX_INTEGRATION_REPORT.md.

**Status: P0 SMOKE COMPLETE (executor).** Awaiting Planner review. No LLM API.

