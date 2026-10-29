# Phase-1A-11 AES Readiness Audit

- Date: 2026-10-29
- Audited code baseline: Phase-1A-10 source tree based on `3c3c6293aefa4861047b56d2c4d1057feb6a9b7c`; docs-only Phase-1A-11 branch.
- No task episodes were executed and no held-out task results were read. Only source, config, review and historical report metadata were inspected.
- No LLM calls, MetaBox experiments, GPU use, or scientific AES experiments.

## Decision

**Track B decision: `AES_BLOCKED_REPAIR_REQUIRED` for scientific performance experiments.**

The AES is a useful, independently reviewed **engineering scaffold**: it has a versioned genotype, phenotype runtime, controlled tool world, state-based evaluator, trace/provenance machinery, and common harness for random search and conventional EA. The Phase-0-R4 review explicitly accepts it for engineering only, not for Agent capability or scientific claims.

The current target experiment is nevertheless not scientifically discriminative:
1. the normalized Agent genotype space has only 16 configurations;
2. the historical six-task pilot saturated at 100% success for all 16 genotypes using a scripted mock backend;
3. the evolutionary baseline selects solely on success rate, so when all candidates tie at 1.0 it has no fitness gradient;
4. the only runtime backend in the audited source package is the mock engineering backend, not a real LLM Agent;
5. train/dev use only two task families and the held-out family has only three task instances.

Do not expand seeds/budget on the same saturated pilot. Repair the task/genotype/objective and backend readiness first.

## Source-level findings

### 1. Genome size and semantics

Audited source:
- `src/agentfotagent/genome/schema.py`, blob SHA `907dd9b37d8e601b1214ddf182dab8d3911b672e`
- `src/agentfotagent/runtime/phenotype.py`
- `src/agentfotagent/runtime/mock_backend.py`, blob SHA `8aab1540365142b0ca6b14613679a5ace4780529`

`aes-genome-v1` has four two-allele genes:
- `planning_mode`: direct / plan_first
- `memory_policy`: none / bounded_episodic
- `verification_policy`: none / check_before_finalize
- `tool_selection_policy`: fixed_ranking / state_conditioned

The `GenomeSpace` constructs the Cartesian product, so the entire canonical space is **2 × 2 × 2 × 2 = 16 genomes**. This is a small finite configuration-selection problem. Before expanding the space, exhaustive evaluation of all 16 configurations should be the reference baseline; otherwise an evolutionary algorithm could appear competitive against an unnecessarily weak random baseline.

The four genes are not merely inert labels in the mock implementation: planning changes whether a plan is emitted first; memory controls bounded retrieval; verification inserts a verify-before-submit action; tool selection changes ranking. However, those are behavioral unit-test properties of a scripted runtime. They do not establish that an LLM-backed Agent benefits from those interventions.

### 2. Mock backend is scripted, not a real Agent

`src/agentfotagent/runtime/mock_backend.py` declares `ENGINEERING_ONLY=True` and identifies `mock-engineering-v2`. It contains a `MockPolicy`, family-specific `DEFAULT_PLANS`, deterministic action-candidate logic and hand-written state tracking. The policy receives an internal `family` field even though that field is not placed in the model-facing payload. This is appropriate for engineering tests, but it means mock task completion cannot show that an LLM inferred the family, reasoned through the task, or improved its behavior through evolutionary selection.

The audited runtime package exposes the mock backend; no production LLM Agent backend is present in the inspected `src/agentfotagent/runtime/` source tree. The Phase-1A-10 DeepSeek calls generated/reviewed **numerical optimizer mechanisms**, not Agent actions in AES. These are different experimental uses and must not be conflated.

### 3. Task coverage and saturation

Audited config:
- `configs/task_splits.json`, blob SHA `3ba59c5c0d448503919881808cefd8a5ba44440b`
- `src/agentfotagent/tasks/generators.py`, blob SHA `962f3b628353488311701be186f753d4023df8c1`
- `docs/PHASE1_PILOT_REVIEW_2026-10-27.md`

The frozen split metadata lists:
- train: 16 tasks (8 `key_crate`, 8 `dial_set`);
- dev: 8 tasks (4 `key_crate`, 4 `dial_set`);
- held-out: 3 tasks, all from `relay_route`.

The family-level split isolation is a useful design feature: `relay_route` is absent from train/dev. However, a held-out family with only three instances is too small for a robust family-generalization claim. Train/dev also cover only two families. No held-out outcomes were inspected in this audit.

The historical pilot review says all 16 genotypes reached 1.0 success on six small train tasks, with mean steps ranging 9.83–13.0. It also says the source prior was a manually fixed surrogate, not MetaBox output or Agent-generated knowledge, and the backend was scripted mock. Therefore the result diagnoses **metric/task saturation**, not successful transfer or an effective evolutionary method.

### 4. Fitness representation prevents selection when success saturates

Audited source:
- `src/agentfotagent/interfaces.py`
- `src/agentfotagent/evolution/conventional_ea.py`, blob SHA `047b1948e7889b32b0223d27b3256e99977b976f`
- `src/agentfotagent/evolution/random_search.py`
- `src/agentfotagent/evolution/harness.py`, blob SHA `0f09a44ba0bdce5ff19e644aad3251a1dbbe6b5a`

`SearchRecord` exposes `success_rate` and episode results; it does not expose a directly aggregated step/cost objective. `ConventionalEA` selects tournament parents and truncates the population using only `success_rate`. When every genotype has success rate 1.0, the selection comparisons tie; differences in steps do not influence evolutionary selection. The reported 9.83–13.0 mean-step range therefore cannot rescue this pilot as an EC performance result.

The common harness is a sound engineering start: random search and conventional EA share the normalized genome space, environment, evaluator, maximum-step limit and provenance path. The harness also distinguishes candidate proposals, unique genomes, cache hits and actual episode executions. But the current finite space and saturated binary objective make this comparison non-discriminative. Random search samples with replacement, so repeated proposals are possible; the 16-genome exhaustive baseline must be included.

### 5. Evaluator and environment readiness

Audited source:
- `src/agentfotagent/evaluation/evaluator.py`, blob SHA `674f6b13c6de6fdf3ad72a5a0c0e9053b2ac9f7a`
- `src/agentfotagent/environments/tool_world.py`
- `configs/evaluation_protocol.json`, blob SHA `ee2ef9fa9edc2814f1115b70a39f3277b01f9e33`
- `configs/baselines.json`, blob SHA `f1f2e7b3102407792df55d49c962400e58073cad`

Current versions are aligned in config: `aes-task-gen-v2`, `aes-tool-world-v2`, `aes-evaluator-v2`, `aes-phenotype-v2`, `mock-engineering-v2`. The evaluator derives primary success from the terminal environment state and task-specific hidden goal, ignores the Agent's self-report, and fails closed on unknown goal types and malformed/incomplete goals. The Phase-0-R4 independent review records **ACCEPTED FOR THE ENGINEERING GATE, WITH SCOPE LIMITS** and a 189-test CI run plus seven counterexample probes. This is valid engineering evidence, not Agent capability evidence.

The current task families are deterministic and verifiable, which is useful. The next issue is not to weaken those contracts, but to calibrate a sufficiently informative task distribution and ensure the real Agent backend—not the mock solver—is the component being evaluated.

## Blocking items before scientific experiments

| Gate | Finding | Required action |
|---|---|---|
| B1 — nontrivial search space | Only 16 normalized genomes; exhaustive search is feasible. | Design a richer, behaviorally meaningful genotype/policy grammar. Do not add decorative genes merely to inflate combinations. Add normalization and intervention tests for every allele. |
| B2 — task discrimination | Historical mock pilot is saturated at 100% success. | Create train/dev task variants with controlled distractors, longer dependency chains, recovery after wrong actions, and varied information requirements. Pilot difficulty only on train/dev; freeze a non-saturated protocol before confirmation. |
| B3 — meaningful fitness | Conventional EA ranks only by binary success rate; all-tie results erase selection pressure. | Predefine a lexicographic or multiobjective score: verified success first, then steps/invalid actions/other measured costs among successful episodes. Freeze the objective before tuning. Keep task success primary. |
| B4 — target backend | Only mock backend is present in the audited runtime. | Implement and test a versioned real LLM backend behind the existing interface. Use `deepseek-flash` only if separately authorized; never `deepseek-v4-pro`. |
| B5 — family-level generalization | Train/dev contain two families; held-out has one family and three tasks. | Expand the task suite and reserve multiple independent held-out task families or add a separate published Agent benchmark after the controlled environment passes. Do not use held-out outcomes to tune. |
| B6 — fair EC comparison | Shared harness exists, but current space/objective makes EC comparison uninformative. | Include fixed policy, exhaustive search (for the current 16-genome version), random unique-genome search, and a conventional EA over the same richer space and score. Equalize unique genome evaluations, task episodes, interaction limits and backend conditions. |
| B7 — stochasticity/provenance | Current environment is deterministic and mock-backed; real LLM execution will add stochasticity and cost. | Freeze model/version/decoding, cache semantics, repeated episode seeds, failure accounting and API/token caps before any live run. Keep raw traces and immutable manifests. |

## Recommended next implementation sequence

1. **No scientific run yet.** First make a source-level design proposal for a richer Agent policy genotype. Candidate dimensions could include bounded replanning after failure, memory/retrieval policy, verification triggers, recovery policy, uncertainty-aware tool choice, and termination policy—but each must correspond to an observable runtime intervention and must not simply duplicate another gene.
2. Build a task-difficulty audit using only train/dev metadata and engineering tests. The objective is a range of outcomes where neither the scripted mock nor a trivial fixed policy solves every task. Do not evaluate held-out tasks.
3. Redefine the score and selection contract. Preserve verified task success as the primary metric; use a predeclared tie-breaker such as fewer environment steps and fewer invalid actions, rather than post-hoc choosing whichever metric favors EA.
4. Add a real LLM Agent backend and verify the exact prompt/action interface offline with stubbed HTTP responses. Live API calls require a separate budget approval.
5. Re-run an independent engineering review and freeze the protocol. Only then request authorization for a small real-backend pilot on train tasks. A positive pilot would still require a pre-registered confirmation on untouched tasks.

## Final readiness classification

- Environment engineering: **accepted with scope limits** (per Phase-0-R4 review).
- Agent capability evidence: **none from the mock pilot**.
- EC improves Agent: **not tested / not established**.
- Cross-domain transfer: **not tested / not established**.
- Scientific AES experiment readiness: **blocked pending B1–B6**, with B7 required before real API execution.
