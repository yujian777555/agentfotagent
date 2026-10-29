# Phase-1A-14 Decision — Expanded Mechanism Audit

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Branch: phase1a-phase11-unified-agent-ec-roadmap
- Main evidence: docs/PHASE1A14_PRIOR_WORK_MATRIX.md
- Candidate record: docs/PHASE1A14_CANDIDATE_SHORTLIST.md

## Decision

**PHASE1A14 = NO_GO_CANDIDATE_SHORTLIST.**

No new EC method is approved. This is not a project-wide NO-GO and does not change the fixed objective: apply a genuinely useful LLM-empowered evolutionary-computation method to improving Agent task performance.

## What changed this phase

The mechanism audit expanded beyond the Phase-1A-12/13 papers and incorporated:
- the 2026 ADAS four-axis taxonomy (target, search strategy, representation, feedback), noting that the inspected survey version is an unreviewed preprint;
- GSME: pathology-keyed quality-diversity archive, deterministic validity/activation/significance gates, paired evaluation and cross-cell recombination;
- AdaEvolve: progress-signal-driven local exploration, island-level bandit scheduling and meta-guidance;
- ELMER and SeDev: controllable semantic mutation strength and semantically adjacent code/policy exploration;
- trajectory analysis of LLM optimizers, finding local refinement around high-performing semantic regions is more predictive than novelty alone;
- DEI: heterogeneous LLM mutation operators in distributed quality-diversity search;
- VERSE, OpenSkill, UCoE, RHO and DemoEvolve: optimizer self-evolution, open-world verification, verifier-harness co-evolution, self-preference from trajectories and demonstration-bootstrapped sparse-feedback harness evolution;
- Life-Harness and EvoHarness-RL: runtime interface adaptation and harness-use policy learning;
- AgentSwift, MaAS, EvoTool, PRISM, TTHE/Evoflux and other previously audited Agent/harness search methods.

The expanded matrix finds no candidate that can currently be distinguished by a substantive update/selection rule rather than by renaming, combining, or changing the benchmark for known methods.

## Candidate-level outcomes

- FCLE: rejected as currently specified.
- Generic trace-guided targeted mutation: already covered.
- Semantic-local/trust-region mutation: covered by direct adjacent work.
- Semantic QD / pathology archive: covered.
- Adaptive LLM-EA search controller: covered by AdaEvolve and prior AOS work.
- Verifier-free or weak-feedback evolution: covered in broad form by OpenSkill/UCoE/RHO/DemoEvolve and related work.
- Runtime harness adaptation: covered in broad form by Life-Harness/GSME/VERSE.
- No surviving candidate: zero.

## Hard limits respected

- No implementation changes to AES runtime.
- No real LLM API calls.
- No MetaBox performance runs.
- No AES scientific runs.
- No GPU runs.
- No held-out/test access.

## Next phase

Phase-1A-15 must not start by generating another list of algorithm names. It should define a narrower target problem in which an EC mechanism has a concrete, measurable role that is not equivalent to generic harness evolution. It should compare the closest non-ADAS literature too (black-box policy search, constrained program synthesis, online adaptation, and EC for structured sequential decision policies), and only then decide whether a candidate exists. If no mechanism passes, record NO-GO without running experiments.

See planner/phase1a15_executor_handoff.md.
