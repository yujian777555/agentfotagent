# Executor Handoff Prompt — Phase-1A-11

You are the Executor for `yujian777555/agentfotagent`. Continue from branch `phase1a-phase11-unified-agent-ec-roadmap`. Read `status.json`, `docs/PROJECT_CHARTER.md`, `docs/RESEARCH_DECISIONS.md`, `docs/PHASE1A10_DECISION.md`, Stage B/C reports, `docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md`, and the most recent AES pilot/review documents before acting.

## Locked research goal

The project's goal is **LLM-empowered evolutionary computation applied to improving Agent**. Keep two tracks active:
- Track A: establish whether LLM/Agent can discover a genuinely useful EC mechanism.
- Track B: audit and prepare this repository's own AES so EC can be evaluated as a method for improving Agent task performance.

Do not treat the failure of a Track A candidate as a reason to abandon Track B. Do not claim any Agent improvement or transfer benefit before confirmatory evidence. H3/bidirectional feedback remains conditional on evidence for both directions.

## Starting evidence

- Phase-1A-10 branch result SHA: `3c3c6293aefa4861047b56d2c4d1057feb6a9b7c`.
- Phase-1A-10 decision: `NO_GO_AGENT_DESIGN_ADVANTAGE`; 24/24 requests consumed using `deepseek-flash`; 0/36 candidates passed independent review; Stage D not run.
- Current canonical numerical baseline is the Phase-1A-6 L-SHADE reimplementation. Keep old implementation results historically labelled.
- AES is the required target application. Historical pilot saturation (16 genotypes at 1.0 success on six small train tasks) used a hand-written surrogate/mock backend and is not scientific Agent-performance evidence. Verify the actual source and version before relying on this summary.

## Task 1 — Track A candidate and literature audit

Recover and hash the original Phase-1A-10 candidates:
- `per-dimension-F-floor-with-memory-reset`
- `repair-aware-mutation-resample`
- `repair_aware_resampling`
- `repair-aware-mutation-reflect`

Trace each to its source diagnosis, exact rule, implementation target, nearest algorithms, original papers and author code. Use primary sources when possible. Record evidence level and exact formula/section/code location. Distinguish `ALREADY_COVERED`, `MINOR_VARIANT`, `NOVELTY_UNRESOLVED`, and `POTENTIALLY_DISTINCT`. "Not found" is not proof of absence. Do not generate more candidates or make live API calls.

## Task 2 — Track B AES readiness audit

Inspect the current AES implementation and tests:
- each genotype gene's actual behavioral effect;
- genotype-to-phenotype compilation/runtime;
- task nontriviality and success evaluator validity;
- task-family split, leakage prevention, trace/provenance and cache isolation;
- fairness of fixed-agent, random-search and conventional EA baselines;
- whether the prior saturation result indicates tasks too easy, gene effects too weak, evaluator defects, or another cause.

Do not infer from passing engineering tests that Agent capability is established. If the environment fails, propose specific repairs and tests. Do not launch a scientific performance experiment during this audit.

## Task 3 — Define the connection without assuming transfer

Specify what object could connect the tracks. If testing H2, define source-domain state/action/reward on MetaBox and target-domain state/action/reward on AES, plus the exact mapping and adapter. Compare against target-only tuning, random/shuffled mapping and standard EC. A generic adapter or reuse of DE's F/CR values is not enough. Transfer is an empirical hypothesis, not an established result.

## Hard limits for this phase

- 0 real LLM API requests.
- 0 MetaBox performance experiments.
- 0 AES scientific performance experiments.
- 0 GPU hours.
- Do not access test/held-out splits.
- Do not start Stage D.
- Do not reopen closed CC-SOC/quality-credit/IPW-DR, N+I restart, state-trigger superiority, adaptive-N or archive-boundary-interaction claims without a new independently audited hypothesis.
- If a later live LLM experiment is separately authorized, use `deepseek-flash` only; never use `deepseek-v4-pro`.

## Required outputs

- `docs/PHASE1A11_CANDIDATE_AUDIT.md`
- `docs/PHASE1A11_LITERATURE_MATRIX.md`
- `docs/PHASE1A11_AES_READINESS_AUDIT.md`
- `docs/PHASE1A11_DECISION.md`
- Update `status.json` and handoff docs with actual results, source SHA, branch, budget and unexecuted items.

Separate decisions for Track A and Track B. Track A may be `CANDIDATE_READY_FOR_EXPERIMENT_DESIGN` or `NO_GO_CURRENT_CANDIDATES`. Track B may be `AES_READY_FOR_EXPERIMENT_DESIGN` or `AES_BLOCKED_REPAIR_REQUIRED`. H2 may only be marked ready for an experiment design when one explicit transfer object and negative controls are defined. No state means performance has been demonstrated.

Commit and push to this branch, verify remote HEAD and clean worktree where available, then stop and report. Do not automatically start any API or performance run.
