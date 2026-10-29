# Phase-1A-12 Design Decision

- Date: 2026-10-29
- Basis: Phase-1A-11 audits and Phase-1A-12 design specifications.
- Scope: design-only. No code changes, real API calls, MetaBox runs, AES scientific runs or held-out access are authorized.

## Decisions

| Gate | Decision | Reason |
|---|---|---|
| Direct target-domain route | `DESIGN_ONLY_CONDITIONAL_GO` | It directly targets Agent improvement and does not depend on an unvalidated MetaBox controller. But generic prompt/Agent evolution is heavily covered by Promptbreeder, GEPA, EoH/LLaMEA and related work; novelty is unresolved. |
| Transfer route | `NOT_READY` | No source controller has passed Track A, and no specific cross-domain state/action mapping is validated. Transfer remains optional, not the project objective. |
| AES engineering scaffold | `ACCEPTED_FOR_ENGINEERING_ONLY` | Existing independent review supports the scaffold within engineering scope. |
| AES scientific experiments | `NO_GO_UNTIL_ENVIRONMENT_REDESIGN_AND_REVIEW` | 16-genome search is exhaustively enumerable; historical mock results saturated; selection fitness has no gradient on all-success ties; no real LLM backend is available in the audited runtime. |
| H3/bidirectional feedback | `NOT_STARTED` | Neither a validated controller nor transfer evidence exists. |

## Recommended order of work

1. Review the proposed genome-v2 semantics and remove gene overlaps before implementation.
2. Define train/dev-only task generator changes with deterministic reference-solver checks and no held-out outcome access.
3. Freeze the lexicographic fitness and exact baseline contract.
4. Audit direct-target prior work at the mechanism level; do not claim novelty from the combination of LLM + EA + Agent tasks.
5. Only after design review, implement the minimum approved AES changes and run offline engineering tests.
6. Request separate approval for any real-backend pilot. Use `deepseek-flash` only; do not call it until the budget is approved.
7. Keep transfer as a later comparison only if a concrete controller object is validated on its source task and a target mapping can be frozen before target evaluation.

## Falsification criteria

The direct route must be stopped or redesigned if:
- the larger genotype has no behaviorally distinct alleles after canonicalization;
- task difficulty cannot separate fixed and alternative policies without artificial traps;
- exhaustive/random search explains all gains at lower or equal evaluation cost;
- conventional EA does not beat the relevant simple baselines on predeclared metrics;
- any gain disappears on disjoint task families or depends on post-hoc metric choice;
- a primary-source audit finds the proposed mechanism already covered.

The transfer route remains no-go unless the same explicit controller object has a justified source/target semantics and beats target-only optimization and shuffled mapping.

## Overall verdict

**Continue the project, but do not start scientific experiments yet.** The most defensible next activity is design review of AES-v2, task discrimination, and fitness/baseline semantics. This is not a claim that direct LLM-assisted EC is novel or effective. The project-level objective—using EC to improve Agent task performance—remains fixed; the specific route and benefit must be earned by evidence.
