# Phase-1A-16 Executor Handoff — Typed/Contract-Aware Evolution of Runtime Agent Policies

You are the Executor for yujian777555/agentfotagent. Use only this repository. Do not mix state, code, tasks, or claims from openissue, EvoPareto-Agent, CausalEvo-DSH, GLEPPO, or any other project.

## Read first
1. status.json
2. docs/PROJECT_CHARTER.md
3. docs/RESEARCH_DECISIONS.md (D-024, D-025 and latest)
4. docs/PHASE1A14_PRIOR_WORK_MATRIX.md
5. docs/PHASE1A14_DECISION.md
6. docs/PHASE1A15_RESEARCH_OBJECT_COMPARISON.md
7. docs/PHASE1A15_ADJACENT_EC_LITERATURE_MATRIX.md
8. docs/PHASE1A15_DECISION.md
9. docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md

## Locked objective
Apply a genuinely useful LLM-empowered evolutionary-computation method to improve Agent task performance. The Agent-targeted outcome is mandatory; no performance or novelty is presumed. MetaBox→AES transfer remains optional and NOT_READY. AES is an engineering scaffold, not validated Agent-capability evidence.

## Phase-1A-15 conclusion
No method candidate was admitted. The only retained research object is **programmatic runtime action-selection policy in a stateful tool-use environment**, and that is a problem formulation for literature audit, not a novelty claim.

Direct prior work includes:
- Finite-state controllers and policy search for POMDPs/Dec-POMDPs.
- Multi-objective EA for stochastic finite-state controllers.
- NEAT/neuroevolution and genetic programming for RL policies.
- Programmatic policy extraction with local search.
- MLES: multimodal LLM-assisted evolutionary search for programmatic policies (preprint).
- PSyCo/SNES and other safe/constrained policy synthesis.
- AEL, HarnessForge, HarnessEvolve, Living-Harness, GSME and related Agent/harness evolution.
- Rethinking the Evaluation of Harness Evolution: compare with matched-feedback/test-time-scaling baselines and held-out tasks.

Do not claim novelty for “evolve a tool-use policy”, “use LLMs to generate programs”, “use types/grammar to keep programs valid”, “add execution feedback”, or “use safety constraints” alone.

## Phase-1A-16 task
Audit one exact intersection only: **typed/contract-aware evolutionary variation for executable stateful tool-use policies**.

Compare at least:
1. Strongly Typed Genetic Programming (Montana 1995).
2. Grammatically-based Genetic Programming / grammar-guided variation (Whigham 1995 and later grammar-guided GP).
3. Semantic GP, including semantic-aware mutation/crossover and program-behavior distance.
4. Program synthesis and contract-aware/verified program repair.
5. Programmatic policy search and policy extraction.
6. Tool-use Agent runtime policies and recent harness evolution.
7. Non-EC baselines: constrained synthesis/SMT/model checking, local search, LLM-only candidate generation, hand-coded rules.

For each source, document the exact representation, legality/contract guarantee, mutation/crossover/replacement rule, semantic/behavioral feedback, and what failures remain possible. Distinguish syntax/type validity from behavioral correctness and task success.

## Candidate admission gate
Admit at most one method, and only if all are true:
- The exact update/selection operator is stated in executable or mathematical terms.
- It is not simply strongly typed GP, grammar-guided GP, semantic GP, repair-after-mutation, standard program synthesis, or a benchmark/application change.
- The operator addresses a real failure mode of the current policy-search setup and is necessary rather than cosmetic.
- It has a falsifiable negative control, e.g. standard typed GP with identical representation and candidate/evaluation budget.
- Hard action contracts are enforced independently of fitness; invalid or unsafe actions never become acceptable due to reward.
- The evaluator is independent from the candidate policy and cannot be co-evolved to reward exploits.
- Task-family splits and leakage controls are feasible.
- The contribution improves Agent task performance; validity rate alone is not sufficient.

If no candidate survives, record NO_GO and stop. Do not invent a name to make a method look novel.

## Hard limits
- No code implementation.
- No live LLM API requests.
- No MetaBox performance runs.
- No AES scientific experiments.
- No GPU use.
- No held-out/test access.
- If later separately authorized for API use, use deepseek-flash only; never deepseek-v4-pro.

## Required outputs
- docs/PHASE1A16_TYPED_CONTRACT_GP_AUDIT.md
- docs/PHASE1A16_CANDIDATE_DECISION.md
- Update status.json and docs/RESEARCH_DECISIONS.md.
- Create planner/phase1a17_executor_handoff.md with exact next steps and hard limits.
