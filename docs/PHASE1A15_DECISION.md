# Phase-1A-15 Decision

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Branch: phase1a-phase11-unified-agent-ec-roadmap
- Research-object comparison: docs/PHASE1A15_RESEARCH_OBJECT_COMPARISON.md
- Adjacent literature: docs/PHASE1A15_ADJACENT_EC_LITERATURE_MATRIX.md

## Decision

**NO_GO_NEW_METHOD_CANDIDATE.** No new EC method is admitted at this stage. The project is not closed. The fixed objective remains: apply a genuinely useful LLM-empowered evolutionary-computation method to improve Agent task performance.

**One research object is retained for a narrower literature audit only:** programmatic runtime action-selection policies in a stateful tool-use environment. This is not a novelty claim and does not authorize implementation or experiments.

## Findings

1. Static prompt/module/Harness evolution is crowded. New 2026 papers AEL and HarnessForge specifically cover two-timescale policy selection/reflection and joint Harness–policy evolution. HarnessEvolve and Living-Harness add reference-trajectory alignment and persistent procedure/state-graph updates.
2. Runtime policy evolution is directly related to finite-state controllers, POMDP policy search, GP for RL, NEAT, programmatic policy extraction, safe policy synthesis, and LLM-assisted evolutionary policy discovery (MLES). “Apply an EA/GP to tool-use policies” is not a sufficient method contribution.
3. Reusable controller selection is covered by bandits, adaptive operator selection and hyper-heuristics; AEL makes the Agent-specific overlap particularly direct.
4. Generic LLM-assisted improvement of EC search is covered by EoH/LLaMEA/LMCOEA/LAOS/AdaEvolve/AgentSwift and related work.
5. Joint evolution of policy and evaluator is crowded by verifier-harness co-evolution, gated semantic QD and weak-feedback/self-preference methods; it also requires an independent oracle to prevent evaluator exploitation.
6. Cross-domain transfer from MetaBox to AES remains a high-risk hypothesis, not a method. A same-controller transfer claim requires fixed state/action semantics and must beat target-only and shuffled-map controls.
7. Evaluation itself is a major confound. The 2026 paper *Rethinking the Evaluation of Harness Evolution for Agents* compares harness evolution against matched-budget search/test-time-scaling baselines and reports inconsistent gains and limited held-out generalization; future evaluation must control for added search and feedback, not only compare final score to a static baseline.

## Next step

Phase-1A-16 is restricted to a source-level audit of **typed/contract-aware evolutionary variation for executable stateful tool-use policies**. Compare grammar-guided GP, strongly typed GP, semantic GP, program synthesis, repair operators, policy search, and runtime Agent-policy work. Formulate at most one candidate only if an exact operator or selection-rule gap survives. Otherwise issue NO-GO and stop this route. No experiments.

## Work not done

- No code changes.
- No live LLM API requests.
- No MetaBox or AES performance runs.
- No GPU use.
- No held-out/test access.
