# Latest Plan — Phase-1A-18 Follow-up: Continual Multi-Agent Delegation Audit

- Date: 2026-11-02
- Repository: yujian777555/agentfotagent
- Branch: research/phase1a18-evotool-actionability-audit
- Status: LEAD_NARROWED; EC_METHOD_GAP_UNRESOLVED; PHASE1A18_PAUSE_REMAINS

## Fixed project objective

The original H1/H2/H3 objective remains in force: an Agent-assisted EC control mechanism must first be discovered/validated on a source-domain optimizer (MetaBox), then transferred to the project-owned Agent Evolution Sandbox (AES); bidirectional feedback is conditional on H2. The target-domain research lead does not itself prove this transfer.

## Primary target-domain problem

Continual, set-valued, graph-structured delegation under an externally expanding specialist-agent pool. Old tasks may stop invoking previously required specialists when the pool changes; the method must preserve required-agent coverage while adapting to new tasks and specialists, without excessive irrelevant delegation or cost.

## Round-2 evidence

The updated audit is in docs/PHASE1A18_HARNESS_EXPANSION_RETENTION_AUDIT.md. New direct/adjacent competitors include:

- EvoMAS (ICML 2026): graph workflow evolution, role specialization, adaptive evolutionary strategies, curriculum cross-stage stability.
- MAS-Orchestra (ICML 2026): holistic multi-agent orchestration trained by function-calling RL/GRPO.
- CARvE / Continual Model Routing (ICML 2026): single-expert routing over an expanding model-ID label space, with asymmetric anchoring, structured negatives and coreset replay.
- MASQD: quality-diversity archive of multi-agent teams.
- Harness Updating Is Not Harness Benefit: separates harness update quality from activation and adherence.
- HarnessForge: joint harness-policy evolution with diagnosis, generation, survivor filtering and policy alignment.
- CPE, EVOTOOL and AEL remain direct overlap controls.

The benchmark metric is clarified: 13% vs 25% delegation drift compares retained vs forgotten old tasks without adaptation. Agent-axis BWT reaches -34.7% on ALE. On EOG, recall improves 79% to 89% while precision stays around 90%; exposing the final agent pool from the beginning outperforms staged cumulative pool changes for the tested Meta-Harness setting.

## Current decision

KEEP_PAUSE; LEAD_NARROWED; EC_METHOD_GAP_UNRESOLVED. Do not create Phase-1A-19. A specific problem setting now has stronger evidence, but the unique EC mechanism remains unproven.

## Next task

Complete a source/code-level mechanism matrix for EvoMAS, CARvE, MAS-Orchestra, MASQD, CPE, HarnessForge, EVOTOOL, AEL and Meta-Harness, then compare against classical graph GP/EA, NSGA-II/III, MAP-Elites/QD, multi-task EC and continual routing. The key question is whether an EC mechanism for preserving required multi-agent delegation sets across external pool changes survives these baselines.

Also verify project-objective compatibility: any target-domain result must still connect to an Agent-assisted EC control mechanism learned on MetaBox. If no valid transfer object can be defined, record the scope mismatch rather than silently changing the project's objective.

## Hard limits

- No live LLM API calls.
- No MetaBox performance experiments.
- No AES scientific runs or environment extension.
- No GPU job.
- No held-out/test access.
- No new algorithm implementation or Phase-1A-19 handoff.
- Do not modify other repositories.


## Round-3 correction: selection is not the remaining gap

CARvE covers continual single-label expert routing, while multi-label class-incremental learning covers expanding multi-label sets and label-dependency graphs. Therefore, do not claim novelty from adding more specialist labels or predicting a multi-agent set. The remaining research question is whether the executable delegation graph (invocation, order, dependencies, information handoff, adherence) can be evolved continually as the external specialist pool changes.

Required metrics: set prediction, actual invocation, graph execution, adherence, end-task success/cost, and per-cohort backward transfer. Selection baselines include CARvE and multi-label class-incremental learning; orchestration baselines include MAS-Orchestra and EvoMAS.
