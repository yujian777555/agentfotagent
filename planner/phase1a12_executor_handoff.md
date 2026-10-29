# Phase-1A-12 Executor Handoff — Agent-Targeted EC Design

You are the Executor for `yujian777555/agentfotagent`. Start by reading:
- `status.json`
- `docs/PROJECT_CHARTER.md`
- `docs/RESEARCH_DECISIONS.md` (especially D-015 and D-016)
- `docs/PHASE1A11_CANDIDATE_AUDIT.md`
- `docs/PHASE1A11_LITERATURE_MATRIX.md`
- `docs/PHASE1A11_AES_READINESS_AUDIT.md`
- `docs/PHASE1A11_DECISION.md`
- `docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md`
- `docs/PHASE1_PILOT_REVIEW_2026-10-27.md`

## Locked project target

The research target is **LLM-empowered evolutionary computation applied to improving Agent task performance**. Track A's current candidates are closed; this does not close the project. AES is an engineering scaffold, not a validated Agent-performance benchmark yet. MetaBox-to-AES transfer is an optional hypothesis, not a mandatory route or a proven contribution. Compare it with direct target-domain LLM-assisted EC.

## Starting evidence

- Phase-1A-11 branch: `phase1a-phase11-unified-agent-ec-roadmap`.
- Phase-1A-11 decision: Track A `NO_GO_CURRENT_CANDIDATES`; Track B `AES_BLOCKED_REPAIR_REQUIRED`; H2 `NOT_READY`; H3 `NOT_STARTED`.
- Current `aes-genome-v1`: four binary genes, exactly 16 normalized genomes.
- Historical mock pilot: all 16 genotypes reached 1.0 success on six small train tasks; mean steps varied but were not used by ConventionalEA's fitness ranking.
- Current `SearchRecord` and `ConventionalEA` use verified success rate as the selection criterion; when all candidates tie at 1.0, selection has no informative fitness gradient.
- Runtime contains the scripted `mock-engineering-v2` backend; it is not an LLM Agent capability test.
- Phase-1A-10 live API budget was consumed. No new API calls are authorized.

## Task 1 — Audit prior work for the two application routes

Build a mechanism-level literature matrix comparing:
A. **Direct route:** LLM-assisted EC evolves executable Agent policies/genotypes in AES.
B. **Transfer route:** first validate an explicit high-level controller on MetaBox, then apply the same controller object to AES.

Review relevant primary papers and official code where possible, including EoH, LLaMEA, Promptbreeder/EvoPrompt, Agent evolution/self-improvement systems, LAOS/LLM4EO, and the project’s already cited Hyperagents/Harmony Harness work. Record search scope and evidence levels. Compare target object, representation, evolutionary operators, role of LLM, task environment, fitness, baselines, and generalization setup. Do not declare novelty from a paper title or an unsearched keyword. Do not run external code or live APIs.

## Task 2 — Design a richer but behaviorally meaningful AES genotype

Propose `aes-genome-v2` as a *specification only*. A possible starting set to evaluate (not automatically accept) is:
- planning: direct / plan-first / replan-after-failure;
- memory: none / recent window / failure-indexed / compact state summary;
- verification: none / before submit / after risky state change / uncertainty-triggered;
- tool selection: fixed / state-conditioned / prerequisite-aware / uncertainty-aware;
- recovery: retry / inspect-then-retry / choose alternative / safe rollback where supported;
- reflection: none / after invalid action / after no progress.

Do not blindly adopt these options. Check redundancy and whether every allele has an observable downstream effect. Define:
- canonical schema and normalization;
- exact genotype-to-prompt/runtime semantics;
- interaction constraints and inactive-gene canonicalization;
- per-gene intervention tests and task cases that reveal its effect;
- a search-space size large enough that exhaustive search is no longer the only reasonable reference, without inflating it with decorative genes.

No source code implementation in this phase unless explicitly approved after review.

## Task 3 — Redesign train/dev task discrimination (do not touch held-out)

The current mock task set saturates. Propose train/dev-only task-generation changes that require real multi-step reasoning and error recovery:
- distractors and variable object counts/locations;
- multi-hop information gathering and dependencies;
- recovery after an invalid or failed action;
- uncertainty or partial/conflicting observations where the environment contract can define an unambiguous success state;
- varied task templates, not merely new seeds of two fixed templates.

Preserve deterministic reset/step, hidden-goal isolation, typed tool preconditions, and terminal-state success predicates. Do not inspect held-out outcomes. State how task difficulty will be calibrated on train/dev and frozen before any confirmation. Avoid choosing difficulty after looking at held-out results.

## Task 4 — Freeze a meaningful fitness contract

Success must remain the primary outcome. Define in advance how to break ties when success saturates. Consider a lexicographic contract:
1. maximize verified success rate;
2. among ties, minimize normalized environment steps on successful episodes;
3. among remaining ties, minimize invalid-action rate.

Or propose a justified multiobjective alternative. Specify aggregation across tasks/seeds, missing/error episodes, cache behavior, and uncertainty reporting. Do not post-hoc select whichever metric favors EC. Make sure `SearchRecord`/selection semantics will actually use the declared objective.

## Task 5 — Fair baseline and experiment design

For current `aes-genome-v1`, exhaustive enumeration of all 16 genotypes is the appropriate reference. For a redesigned larger search space, compare:
- fixed hand-designed Agent;
- random **unique-genome** search;
- conventional EA;
- a strong LLM-only/self-refinement comparator under a matched model-call/episode budget;
- LLM-assisted EC, only if its role and mechanism are explicitly defined;
- relevant ablations and shuffled controls where a mapping/conditioning claim exists.

Equalize evaluated unique genomes, episode count, maximum steps, model/back-end version, task manifests, cache policy and total cost. Do not use a weak baseline to manufacture an EC advantage.

## Task 6 — Decide which route to pursue

Provide separate verdicts:
- `DIRECT_TARGET_ROUTE_READY_FOR_EXPERIMENT_DESIGN` or `DIRECT_TARGET_ROUTE_NO_GO/PIVOT`
- `TRANSFER_ROUTE_READY_FOR_EXPERIMENT_DESIGN` or `TRANSFER_ROUTE_NOT_READY`
- overall recommendation with the exact evidence that would change the decision.

Do not claim either route is novel or effective yet. If both are weakly differentiated from prior work, recommend another research question rather than starting experiments.

## Required outputs

- `docs/PHASE1A12_PRIOR_WORK_COMPARISON.md`
- `docs/PHASE1A12_GENOME_V2_SPEC.md`
- `docs/PHASE1A12_TASK_DIFFICULTY_SPEC.md`
- `docs/PHASE1A12_FITNESS_AND_BASELINE_CONTRACT.md`
- `docs/PHASE1A12_DECISION.md`
- Update `status.json` and handoff docs with source SHA, decisions, and work not done.

## Hard limits

- 0 real LLM API requests.
- 0 MetaBox performance experiments.
- 0 AES scientific performance experiments.
- 0 GPU hours.
- No held-out/test result access.
- Do not reopen closed CC-SOC/quality-credit/IPW-DR, N+I restart, state-trigger superiority, adaptive-N, or archive-boundary interaction claims.
- If a future experiment is later authorized, use `deepseek-flash` only, never `deepseek-v4-pro`.
- Do not claim tests ran unless actually run; a docs-only audit is not a CI pass.

Commit and push to this branch, verify remote HEAD, and stop at the design gate. Do not launch any API or performance run.
