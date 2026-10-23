# P0-R1 Reconciliation Record

**Audit date:** 2026-10-23  
**Scope:** Read-only review of the current `agentfotagent` remote and potentially relevant repositories visible through the connected GitHub account and Library search.  
**Important boundary:** This is not a local-disk audit. “Not found” means not found in the checked remote/connected sources; it does not prove that a file is absent from the user's local computer.

## 1. Current project repository

- Repository: https://github.com/yujian777555/agentfotagent
- Original initial commit: `f7ff93d00c95a89e0232058c7cfd761b726fc75e` — verified via GitHub; message: `Initial commit`.
- Audit-start HEAD: `e36c79edf31712ff68c7569354a682f5f7f56da8` — verified; message: `Initialize research governance and long-term project plan`.
- The governance commit descends from the initial commit and adds the project charter, decision log, plan, and status.
- Current tree contains only `README.md`, `docs/PROJECT_CHARTER.md`, `docs/RESEARCH_DECISIONS.md`, `planner/latest_plan.md`, and `status.json`. There is **no source directory, test suite, Phase 0 simulator, or experiment artifact in this repository**.
- `status.json` correctly labels the prior reported local Phase 0 and “46/46 passed” as historical/unverified for this remote.

### Reported local baseline

The prior short SHA `d46a76d`, a clean working tree, a Phase 0 baseline/simulator, and 46/46 tests were not located in the current `agentfotagent` tree or the connected Library search. GitHub's global short-prefix search returned unrelated commits, so it cannot identify the intended local commit.

**Status:** `HISTORICAL_UNVERIFIED`, not `REPRODUCED`. No code or result is imported based on this short SHA alone.

## 2. Read-only review of related repositories

These repositories are separate projects. They were inspected as prior-art/artifact sources only; none was modified, merged, or treated as the current `agentfotagent` implementation.

### 2.1 EvoController

- Repository: https://github.com/yujian777555/EvoController
- Current remote HEAD checked: `5ea8bef453cd9d25e0fc8874bd0f58c2b156dc94`.
- Relevant source reports: `docs/PHASE2_8_RESULTS.md`, `docs/PHASE2_9_RESULTS.md`, `docs/PHASE3_PAPER_FINALIZATION_PLAN.md`; data artifacts include `results/phase2_9/semantic_action_probe.json` and `results/phase2_9/extreme_contrast_experimentA.json`.
- The project uses custom ZDT experiments; it is **not** a MetaBox-v2 integration.

Repository-reported findings (verified as documents/artifacts in that repo, not independently rerun here):
- Outcome prediction could reach high (R^2), but was mostly state-driven and did not establish action-selection ability.
- Under the compact action/state representation, held-out within-state ranking remained close to random (reported Spearman roughly 0.01–0.06; pairwise AUC roughly 0.50–0.53).
- A richer action-outcome signature did not pass its decision gate; the semantic action abstraction probe was not above its permutation baseline.
- The project’s finalization plan recommends stopping blind model scaling and treating action-credit identifiability as the main limitation of that specific protocol.

**Implication for this project:** Do not repeat a generic ((state, action) \rightarrow future score) predictor and assume that high prediction (R^2) means useful action selection. This negative evidence does **not** falsify LLM-generated interpretable control rules or cross-domain transfer; it is a warning to evaluate interventions and policy choices directly.

### 2.2 EvoPareto-Agent

- Repository: https://github.com/yujian777555/EvoPareto-Agent
- Current remote HEAD checked: `c1be57a60340bcc9f8762f03b8e8965d6800237f`.
- It provides an Agent-genome / NSGA-III configuration-search implementation, but its latest report explicitly says real HTTP calls = 0 and marks live calibration as not executed.

**Implication:** It may be a candidate Stage-B adapter or software substrate after a source audit. Its unit tests and synthetic/configuration fitness are not evidence that transferred evolutionary control improves a real LLM Agent or RSI.

### 2.3 llm-agent-rsi-r12-audit

- Repository: https://github.com/yujian777555/llm-agent-rsi-r12-audit
- Current remote HEAD checked: `7c45f650855cee27b989241b587144049b5696a8`.
- Its README describes an offline HGM/VERSE audit with synthetic analyses and no real LLM API calls.

**Implication:** Useful as adjacent RSI/lineage-method background only. Its synthetic results are not evidence for MetaBox-to-Agent transfer and are not imported as current Phase-A results.

### 2.4 SciTransfer artifact boundary

A Library search surfaced a file named `PHASE0_PROTOCOL.md`, but its content identifies the SciTransfer project and scientific-strategy transfer among scientific domains. It is not the MetaBox / Agent-for-Agent Phase 0 protocol and is **not imported**. This is a concrete example of why filenames alone are insufficient provenance.

## 3. Current evidence classification

| Item | Status | Permitted use |
|---|---|---|
| `agentfotagent` initial commit and governance HEAD | VERIFIED | Repository provenance |
| Phase 0 simulator and 46/46 test claim | HISTORICAL_UNVERIFIED | May be reconciled only if exact source, commit, command, and raw output are supplied or located |
| EvoController phase 2.8/2.9 findings | VERIFIED_AS_REPOSITORY_ARTIFACT; NOT_RERUN_HERE | Negative prior evidence and design warning |
| EvoPareto-Agent code | VERIFIED_AS_SEPARATE_REPO; no real HTTP in latest report | Candidate Stage-B adapter, not real-Agent efficacy evidence |
| R12 offline audit | VERIFIED_AS_SEPARATE_REPO; synthetic/offline | Related-work context only |
| MetaBox-v2 code/docs | VERIFIED_READ_ONLY at tag `v2.0.0`; not installed or run here | Benchmark/API design evidence only |
| Any cross-domain transfer result | NOT_AVAILABLE | No positive or negative efficacy claim is justified yet |

## 4. Reconciliation decision

The current remote is a governance/planning repository, not a code-bearing experimental baseline. The next safe action is to complete the mechanism-level literature matrix and operationalize H1/H2/H3. Do not import the separate repos wholesale, do not claim the old 46/46 result as reproduced, and do not start real API experiments without explicit scope and budget approval.


## 5. Additional repositories and chronology notes

### NeuroEvoScientist

- Remote: <https://github.com/yujian777555/NeuroEvoScientist>
- Observed main HEAD: 4ea11810fc187e81a0d30c8576e706625c34db77
- Its phase-21 final audit and claim audit report task- and backbone-dependent effects from evolving cognitive-architecture components, with holdout analysis on GSM8K, PubMedQA and QASPER.
- Its claim audit explicitly marks “equal-budget evolutionary search beats random search” as unsupported/closed. It is a candidate downstream environment only after checking executable phenotype, evaluator and random-search baseline.

### VETM

- Remote: <https://github.com/yujian777555/VETM>
- Observed main HEAD: 8c154ce5069c7de37b3ad4989459e21c0ace1079
- Studies transfer and validity prediction of evolutionary experience across optimization problems. It is adjacent to transfer research, not direct evidence that a MetaBox-derived policy transfers to Agent RSI.

### Clarification on EvoPareto-Agent evaluation chronology

- The latest report on its Stage-3 workflow/failure-feedback line says that the specific run had real HTTP calls disabled and calibration not executed.
- Separately, a Phase-5 R4-R2 report documents a two-episode native-environment pilot (one success, one episode ending at the 30-step limit). These are different experiments/lines and must not be conflated.
- The two-episode pilot is feasibility evidence only; it does not establish that NSGA-III, PEEM or PPEC outperforms random search or strong Agent-evolution baselines.
