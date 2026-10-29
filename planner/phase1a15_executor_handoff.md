# Phase-1A-15 Executor Handoff — Narrow Problem Formulation Before Candidate Generation

You are the Executor for yujian777555/agentfotagent. Use only this repository for the current project. Do not mix code, results, or project state from openissue, EvoPareto-Agent, CausalEvo-DSH, GLEPPO, or other independent repositories.

## Read first
1. status.json
2. docs/PROJECT_CHARTER.md
3. docs/RESEARCH_DECISIONS.md (especially D-015, D-016, D-023 and the latest entry)
4. docs/PHASE1A12_DECISION.md
5. docs/PHASE1A13_DECISION.md
6. docs/PHASE1A14_PRIOR_WORK_MATRIX.md
7. docs/PHASE1A14_CANDIDATE_SHORTLIST.md
8. docs/PHASE1A14_DECISION.md
9. docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md

## Locked objective
The project must ultimately apply a genuinely useful LLM-empowered evolutionary-computation method to improve Agent task performance. No benefit or novelty is presumed. MetaBox-to-AES transfer is optional and remains NOT_READY. AES is an engineering scaffold only, not validated Agent capability evidence.

## Phase-1A-14 finding
No candidate survived the expanded audit. Direct Agent/harness evolution is crowded by EvoTool, GSME, AgentSwift, MaAS, PRISM, TTHE/Evoflux, VERSE, OpenSkill, UCoE, RHO, DemoEvolve, Life-Harness, EvoHarness-RL, AdaEvolve, ELMER, SeDev, DEI and related work. Do not repackage their mechanisms under new names.

## Task A — Define the actual research object
Before candidate generation, compare these possible research objects:
1. Evolution of static Agent prompts/modules/harnesses.
2. Evolution of runtime action-selection policies in stateful tool environments.
3. Evolution of a reusable controller that selects among Agent policies.
4. Evolution of EC mechanisms that later improve Agent policy search.
5. Joint evolution of the Agent policy and its evaluator/verifier.

For each, define the decision variables, objective, observable feedback, feasible action space, and closest existing methods. Do not select a route based on intuition alone.

## Task B — Audit adjacent non-ADAS literature
The current ADAS papers alone are not enough. Audit primary sources on:
- evolutionary computation for finite-state and programmatic policy search;
- genetic programming / neuroevolution for sequential decision-making and tool-using agents;
- constrained and safe policy synthesis with executable contracts;
- online evolutionary adaptation under environment/task shifts;
- black-box optimization under stochastic, task-correlated outcomes;
- controller selection/hyper-heuristics when action effects are delayed;
- multi-task/generalist policy evolution and cross-task generalization.

For each source, record exact update/selection rules, not just the application label. Distinguish peer-reviewed papers, preprints, abstracts, and secondary descriptions.

## Task C — Candidate admission criteria
Admit at most one candidate, and only if all are true:
1. It has an explicit mathematical or executable update/selection rule.
2. It is not just prompt/harness/module evolution, generic linkage learning, generic QD, generic AOS, a new task generator, or a metric change.
3. The nearest prior work and exact mechanism-level difference are stated.
4. The EC component has a necessary, testable role; exhaustive search or random unique-genome search is not an equally good explanation.
5. A negative control can falsify the claimed mechanism.
6. The proposed evaluation can be performed without leakage and without a prohibited budget or unsafe environment change.

If none passes, produce an explicit NO-GO and stop candidate generation for this phase.

## Hard limits
- No source implementation.
- No live LLM API requests.
- No MetaBox performance experiments.
- No AES scientific experiments.
- No GPU use.
- No held-out/test access.
- If later explicitly authorized, use deepseek-flash only; never use deepseek-v4-pro.

## Required outputs
- docs/PHASE1A15_RESEARCH_OBJECT_COMPARISON.md
- docs/PHASE1A15_ADJACENT_EC_LITERATURE_MATRIX.md
- docs/PHASE1A15_DECISION.md
- Update status.json, docs/RESEARCH_DECISIONS.md, and the handoff with exact source SHA, conclusions and work not done.
