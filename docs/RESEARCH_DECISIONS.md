# Research Decision Log

## D-001 — Evolutionary computation is the method core
2026-10-23. Agent is the discovery/diagnostic system and the downstream evolution target; EC must be methodologically central.

## D-002 — Validate transfer before a full bidirectional loop
2026-10-23. H2 is the key discriminative gate; H3 is conditional on H2 and is not justified by architectural elegance.

## D-003 — MetaBox is infrastructure, not a contribution
2026-10-23. Standardized evaluation is necessary, but using MetaBox does not itself create novelty.

## D-004 — Finite-budget allocation is not a core innovation
2026-10-23. Evaluation budgets are controlled for fairness; budget allocation is not the thesis centerpiece.

## D-005 — Live LLM API experiments need separate scope/budget approval
2026-10-23. No real API call until the experimental scope and call/token/cost caps are explicitly approved.

## D-006 — Remote state is the evidence baseline
2026-10-23. Prior conversation claims about local code, test counts and evolutionary statistics remain historical/unverified until artifacts are imported and checked.

## D-007 — Generic H1 is not a novelty claim
2026-10-23. LLM4EO explicitly combines evolutionary-state perception with operator-level meta-evolution; LAOS describes LLM-driven adaptive operator selection; EoH/LLaMEA/AwesomeDE/LMCOEA cover LLM-assisted heuristic or EA rule design. H1 can be a prerequisite validation stage, not the central novelty claim.

## D-008 — Generic H3 is not a novelty claim
2026-10-23. Hyperagents modifies the meta-level improvement procedure and reports cross-domain transfer; HGM, CoCoEvolve and RSI-Router cover related lineage, history-driven or recursive improvement mechanisms. A bidirectional loop alone is not novel.

## D-009 — H2 remains a high-risk candidate, not a confirmed gap
2026-10-23. The remaining candidate is transfer of the same explicit controller object from numerical MetaBox tasks into a structurally different Agent-genotype search space, with nontrivial state/action alignment and stringent negative controls. Harmony Harness already covers factorized general/task-specific harness mechanisms and cross-benchmark transfer, so an adapter or generic transfer story is insufficient.

## D-010 — Literature coverage is partial
2026-10-23. LAOS full text/code and LMCOEA full text/code were not obtained in this pass. The project must not claim exhaustive novelty review.


## D-011 — LAOS/LMCOEA do not establish a ready-made cross-representation controller

2026-10-26. The LAOS official GECCO abstract verifies LLM-driven state-conditioned AOS with operator credit assignment and offline/online replay, reinforcing rejection of generic H1. LMCOEA's linked code statically inspected in this pass generates DE-specific MATLAB offspring-update functions and evaluates them on numerical constrained optimization tasks; this is not an off-the-shelf controller for Agent-genotype evolution. The linked repo README claims MIT but no root LICENSE exists in the observed tree, and the implementation contains machine-specific paths; it was not executed. H2 remains unproven until one transfer object and its state/action semantics are defined and shown to differ materially from LAOS, AwesomeDE/LMCOEA, and Harmony Harness. No code or live API experiment is authorized by this decision.


## D-012 — The project must own its target experimental environment

2026-10-26. The prior plan to compare NeuroEvoScientist and EvoPareto-Agent as candidate target environments was conceptually wrong for the project boundary. They are independent projects and can only be consulted read-only as prior-art/evaluation references. agentfotagent must implement its own Agent Evolution Sandbox (AES): versioned genome and phenotype runtime, controlled multi-step tool-use world, verifiable task-success evaluator, frozen task-family splits, baselines, experiment runner and provenance. MetaBox-v2 remains the standardized source-domain substrate. AES is experimental infrastructure, not automatically a novel contribution. Phase-0 implementation must be engineering-only; mock scores are not capability evidence and no live API/MetaBox experiment is authorized. Detailed contract: docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md.
