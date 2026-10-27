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


## D-013 — Phase-0 AES scaffold requires corrective pass before acceptance

2026-10-26. Independent static audit of \`987df6dbb21683331968f09acf6160fbbdf005bb\` returned REQUEST CHANGES. The world permits remote state-changing actions that bypass intended multi-step task semantics; planning/verification/memory genes do not all implement their stated downstream decision semantics; PublicTask exposes deterministic seed/generator metadata; BaselineHarness does not preserve raw traces and creates incomplete replacement traces; evaluator handling of malformed states is not fully fail-closed. Executor-reported 56/56 tests were not independently rerun in the audit environment. Fixes and regression tests are required before environment acceptance. No transfer experiments, live API, GPU or MetaBox meta-training until re-audit passes.


## D-014 — Phase-0-R1 remains unaccepted after independent re-review

2026-10-27. Static review of main 3322a9d8eef80308a50c55f25292d4034d94699f and corrective implementation ebd3d996599953c7ab24f61b6ca2ba8b728bc8c9 found residual issues: task IDs encode family/split/seed in model-facing context; relay verification accepts any non-null frequency; missing relay objects bypass locality and are not required by the evaluator; incomplete goal schemas and malformed step values are not fully fail-closed; artifact reconstruction does not detect manifest scores lacking traces; harness reuse can contaminate run accounting/traces; and environment/evaluator/backend versions remain unchanged after semantic modifications. Executor-reported 104/104 tests could not be independently rerun due DNS resolution failure; GitHub check-runs count is zero. Verdict: REQUEST CHANGES. No scientific experiments, live API, GPU, transfer or MetaBox meta-training until a further corrective pass is independently accepted.


## D-015 — Phase-0-R2 test pass does not close all integrity gates

2026-10-27. GitHub Actions independently reproduced the existing suite on exact R2 source commit ec73906e15c048285cff3bca90a4f1f8bed21da8: 127 passed in 0.43s (run 40453697835). Adversarial probes on the same source tree showed that the content-derived runtime ID can be reversed by enumerating the public generator's seed space; the relay evaluator accepts malformed goal values (code=null, frequency=99); the key_crate evaluator accepts object records without required entity types; and artifact reconstruction accepts tampered invalid_actions metrics. Therefore Phase-0 remains REQUEST CHANGES. Fix these issues, add adversarial regression tests, rerun the full suite and seek independent review. No live API, GPU, MetaBox or scientific experiment is authorized by this decision.


## D-017 — R3 test reproduction passes, but environment remains unaccepted

2026-10-27. Independent GitHub Actions run 40459330792 checked out exact R3 candidate source `cd07249a1b4675354b01f9d5ac09ab2ffe4d2033` and reproduced 162 passing tests in 0.87s on Python 3.10.22. Further probes found that integer `success=1` is accepted in place of boolean true, unknown score fields are accepted, and key_crate can succeed with missing crate/surface locations. The original counterexample probe also masks failures for R3-01/R3-04 by treating generic exceptions/assertions as PASS. Phase-0 remains REQUEST CHANGES. Fix R3-05..R3-08, add regression tests, reproduce and seek independent review. No live API, GPU, MetaBox or scientific experiments are authorized.
