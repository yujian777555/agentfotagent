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


## D-018 — R4 candidate accepted for engineering gate only

2026-10-27. Independent static review of `phase0-r4-fixes@3e48bf5305ba667490358c140dad556f1ebf84e2` plus hosted CI run 40462185561 confirms 189 full-suite tests, 62 targeted tests, and 7/7 adversarial probes pass. R4-01 strict bool, R4-02 closed score schema, R4-03 key_crate location contract and R4-04 probe failure semantics are accepted for the engineering gate. The candidate is not yet merged into main. This does not establish Agent capability or scientific validity. Review: `docs/PHASE0_R4_INDEPENDENT_REVIEW_2026-10-27.md`.

## D-019 — Saturated surrogate transfer pilot is NO-GO; return to MetaBox source-domain validation

2026-10-27. The Phase-1 debug pilot reaches 1.0 best success rate in all arms; all 16 genotypes solve all six small train tasks. Mean steps differ, but the EA selection objective does not optimize that secondary metric. The source allele prior is hand-written and is not MetaBox output or Agent-generated strategy knowledge. Do not scale this pilot or claim transfer benefit. Next, validate an Agent-generated constrained controller on MetaBox-v2 against strong EC/LLM-assisted baselines and held-out tasks. Only if that gate passes should the same explicit controller be transferred to AES; bidirectional feedback remains conditional on positive transfer evidence. No live API calls without explicit budget approval.


## D-020 — R4 engineering gate merged; next phase returns to MetaBox

2026-10-27. PR #2 merged the reviewed R3/R4 source and tests into main at `9e59401dd78f4be830c45634767bd3f65fb4b4ed`. Integration CI run 40464369334 passed 189 tests, 62 targeted tests and 7/7 probes. Phase-0 acceptance is limited to engineering infrastructure. The current source→AES pilot remains `NO_GO_OR_PIVOT`: all 16 genotypes solve all six small tasks and the source prior is hand-coded, not MetaBox or Agent-generated. Next: validate Agent-assisted EC on MetaBox-v2 against strong baselines and held-out tasks; transfer to AES only after a reproducible positive result. No live LLM API calls without an explicit budget.


## D-021 — Phase-1A P0 accepted narrowly; adaptive-controller gate remains blocked

2026-10-27. Reviewed `phase1a-metabox-smoke@f571b52ba73f6cfcf51901a2af72f4b980699bc7`. Accept the real MetaBox/DE smoke only: 1,500 FE counts agree and same-seed curves reproduce. Do not treat this as evidence of adaptive control. The adapter invokes the controller once on a constant initial state; range actions apply midpoint scalars; mutation strategy/restart are not consumed by upstream DE. The F1–F12/F13–F18/F19–F24 split is uneven by MetaBox easy/difficult labels and BBOB families. P0-R1 must correct action semantics, add trace-conditioned hooks or narrow the action space, version and freeze a stratified split_v2, complete environment provenance and add exact-SHA CI. P1A-1 remains blocked. Full review: `docs/PHASE1A_P0_PLANNER_REVIEW_2026-10-27.md`.


## D-022 — Phase-1A P0 results invalidated for function-specific claims by loader bug

2026-10-27. Source audit of `phase1a-metabox-smoke@f571b52ba73f6cfcf51901a2af72f4b980699bc7` found that `load_function` calls the pinned MetaBox BBOB factory with `difficulty="all"`. That branch ignores `user_train_list`/`user_test_list`, builds all functions F1–F24, and the adapter selects the first item (F1) while labelling it with the requested ID. Therefore all reported F6 smoke runs are actually F1 executions. FE accounting and seed reproducibility remain generic smoke evidence; function identity, F6 scores and split correctness are not accepted. Fix the selector and add actual identity tests for F1/F6/F24 before rerunning. P0 is REQUEST CHANGES and P1A-1 is blocked. See `docs/PHASE1A_P0_PLANNER_REVIEW_2026-10-27.md`.

## D-015 — LLM-empowered EC must target Agent improvement; keep two tracks active

2026-10-29. The project's research target is locked as **LLM-empowered evolutionary computation applied to improving Agent**. Track A audits whether LLM/Agent can discover a genuinely useful EC mechanism; Track B audits and prepares the project-owned AES for evaluating EC-based Agent improvement. A Track A NO-GO does not automatically close Track B. Conversely, the target application does not predetermine that a performance benefit exists: all benefit and transfer claims require independent evidence. H3/bidirectional feedback remains conditional on evidence for both directions. Phase-1A-10 remains `NO_GO_AGENT_DESIGN_ADVANTAGE`; no new API or scientific experiment is authorized by this decision. See `docs/PHASE1A11_UNIFIED_RESEARCH_DIRECTION.md`.

## D-016 — Agent is the fixed application target; MetaBox-to-AES transfer is optional

2026-10-29. The non-negotiable research target is to apply an LLM-empowered evolutionary-computation method to improve Agent task performance. The older H2 proposal (transfer a controller from MetaBox to AES) is one candidate route, not a required architecture or a proven contribution. After Phase-1A-10's `NO_GO_AGENT_DESIGN_ADVANTAGE` and Phase-1A-11's rejection of the four remaining candidates, the next design phase must compare (a) a transfer route after source-domain validation and (b) direct LLM-assisted EC on executable AES Agent policies. Neither route is presumed novel or effective. The direct route must be audited against existing LLM-assisted EA and Agent/prompt/workflow evolution. No scientific run or API call is authorized. See `docs/PHASE1A11_DECISION.md`.


## D-023 — FCLE candidate rejected; return to mechanism-level gap search

2026-10-29. Phase-1A-13 audited Family-Consistent Linkage Evolution (FCLE), a candidate that estimated pairwise Agent-policy gene interactions from paired task evaluations and used only family-consistent edges for linkage-based recombination. Reject FCLE as currently specified: its four-point interaction estimator is essentially the fitness-based interaction test used by Differential Grouping / fitness-based linkage learning (Olieman et al., IEEE TEVC 2021), and its linked-subset mixing is GOMEA-style. Local linkage kernels, AgentSwift's workflow/component interaction coverage, AgentSquare's module recombination, and MaAS's query-conditioned architecture distributions further reduce novelty. Additional 2026 overlaps include Beyond Prompts/PRISM, AgenticEvolve, Code Evolution for Control, SEVerA, and HASP. This is a candidate-level NO-GO, not a project-level NO-GO. The target remains applying a validated LLM-empowered EC method to improve Agent task performance. No implementation, API call, MetaBox/AES performance run, GPU run, or held-out access is authorized. Continue Phase-1A-14 mechanism-gap search using the current ADAS survey taxonomy and primary-source mechanism comparisons. See docs/PHASE1A13_LINKAGE_MECHANISM_AUDIT.md, docs/PHASE1A13_RECENT_OVERLAP_ADDENDUM.md, and docs/PHASE1A13_DECISION.md.


## D-024 — Phase-1A-14 expanded audit yields no surviving candidate

2026-10-29. Phase-1A-14 extended the mechanism-level review using the 2026 ADAS taxonomy and additional primary/near-primary sources. The matrix covers GSME, AdaEvolve, ELMER, SeDev, LLM-optimizer trajectory analysis, DEI, VERSE, OpenSkill, UCoE, RHO, DemoEvolve, Life-Harness, EvoHarness-RL, Q-Evolve, AgentSwift, MaAS, EvoTool, PRISM and prior audited work. Every current candidate family either overlaps an existing mechanism (targeted blame/mutation, semantic QD, semantic-local mutation, adaptive LLM-EA, query-conditioned architecture search, verifier/harness co-evolution, runtime adaptation) or is only an evaluation practice rather than a method contribution. Decision: NO_GO_CANDIDATE_SHORTLIST for this phase, not a project-level NO-GO. Fixed objective remains applying a validated LLM-empowered EC method to Agent improvement. No implementation, API call, MetaBox/AES performance experiment, GPU run, or held-out access is authorized. Phase-1A-15 must compare the actual research objects and audit adjacent non-ADAS EC literature before proposing at most one candidate. See docs/PHASE1A14_PRIOR_WORK_MATRIX.md, docs/PHASE1A14_CANDIDATE_SHORTLIST.md, docs/PHASE1A14_DECISION.md and planner/phase1a15_executor_handoff.md.


## D-025 — Phase-1A-15 selects a research object, not a new method

2026-10-29. Compared five objects: (1) static Agent prompt/module/Harness evolution; (2) programmatic runtime action policy in a stateful tool environment; (3) reusable controller selecting among Agent policies; (4) EC mechanisms that improve later Agent policy search; and (5) joint policy/evaluator evolution. Object 2 is retained only as the next literature-audit target because it directly targets runtime task decisions and supports explicit EC representations/operators. It is not novel by itself: finite-state controllers, GP for RL, evolutionary policies, programmatic policy extraction, safe policy synthesis, and LLM-assisted evolutionary policy discovery are prior art. AEL and HarnessForge (EMNLP 2026), alongside HarnessEvolve/Living-Harness preprints, further cover policy selection, harness/policy evolution, reference-trajectory alignment and persistent procedure updates. No candidate is admitted. Phase-1A-16 must audit typed/contract-aware evolutionary variation against strongly typed GP (Montana 1995), grammar-guided GP (Whigham 1995), semantic GP, program synthesis/repair and non-EC baselines. Hard contracts must be independent of fitness; syntax/type validity must not be confused with behavioral correctness or task success. No implementation, live API, MetaBox/AES run, GPU use, or held-out access is authorized. See docs/PHASE1A15_RESEARCH_OBJECT_COMPARISON.md, docs/PHASE1A15_ADJACENT_EC_LITERATURE_MATRIX.md, docs/PHASE1A15_DECISION.md and planner/phase1a16_executor_handoff.md.


## D-026 — Generic typed/contract-aware GP variation is not a new method

2026-10-29. Phase-1A-16 audited strongly typed GP (Montana 1995), grammar-guided GP (Whigham 1995), systematic GP constraint processing (1996), GenProg's test-guided execution-path-localized edits (2009/2012), proof-search-based semantics-preserving genetic improvement (Kocsis & Swan 2018), LLM-seeded many-objective grammar-guided GP (Tao et al. 2024/2025), and recent SMT/abstract-interpretation program synthesis (Dimovski 2026). Generic type-, grammar-, contract-, or test-aware mutation is therefore NO_GO as a new-method claim. Syntax validity, type validity, state-dependent action preconditions, postconditions, episode success and generalization are distinct properties and must not be conflated. A temporal-effect-conditioned operator remains unresolved but is not admitted: no precise rule or mechanism-level gap was established. No implementation or experiments are authorized. Next audit returns to charter hypothesis H2: transfer of a frozen explicit EC controller from MetaBox to AES with fixed state/action mappings. See docs/PHASE1A16_TYPED_CONTRACT_GP_AUDIT.md, docs/PHASE1A16_CANDIDATE_DECISION.md and planner/phase1a17_executor_handoff.md.
