# Handoff — Continual Multi-Agent Delegation Audit

Repository: yujian777555/agentfotagent
Working branch: research/phase1a18-evotool-actionability-audit
Current decision: KEEP_PAUSE; LEAD_NARROWED; EC_METHOD_GAP_UNRESOLVED
Last verified branch HEAD before this handoff update: c5a382baa90e62b422b0b9f4f0baad57eed31b7c

## First read

1. status.json
2. docs/PHASE1A18_DECISION.md
3. docs/PHASE1A18_STRATEGIC_FEASIBILITY.md
4. docs/PHASE1A18_HARNESS_EXPANSION_RETENTION_AUDIT.md
5. docs/PHASE1A18_EVOTOOL_BLAME_ACTIONABILITY_AUDIT.md
6. docs/RESEARCH_DECISIONS.md
7. docs/PROJECT_CHARTER.md
8. src/agentfotagent/environments/tool_world.py
9. src/agentfotagent/tasks/generators.py
10. src/agentfotagent/genome/schema.py

## Research problem

Continual, set-valued, graph-structured delegation under an externally expanding specialist-agent pool. A task may need multiple specialists and an execution graph; as the external pool changes, old tasks may stop invoking specialists required by previously successful traces.

EvoHarnessBench reports:
- forgotten old tasks have 25% delegation drift vs 13% for retained tasks without adaptation;
- forgotten tasks more often omit previously required specialists;
- agent-axis deployment BWT reaches -34.7% on ALE;
- EOG required-agent recall rises from 79% to 89% under adaptation while precision remains around 90%;
- for Meta-Harness on EOG, final pool from the beginning scores 20.3%, compared with 18.5% under cumulative staged pool evolution and 19.4% under task-specific pool exposure.

## Required prior-art controls

- EvoMAS (ICML 2026): graph-based workflow evolution, role specialization, adaptive operators, curriculum stability.
- MAS-Orchestra (ICML 2026): holistic function-calling RL/GRPO orchestration of complete multi-agent graphs.
- CARvE / CMR (ICML 2026): continual single-expert routing under expanding model IDs with old-ID anchoring, structured negatives and coreset replay.
- MASQD: quality-diversity archive of multi-agent teams.
- CPE: capability-preservation mechanisms for workflows, skills/tools, model and memory.
- HarnessForge: joint harness-policy evolution, module diagnosis, generation, selection and policy alignment.
- EVOTOOL: blame-aware targeted module mutation and diversity-aware selection.
- AEL: TS memory-policy arms and optional planner/tool bandits; default tool set fixed.
- Harness Updating Is Not Harness Benefit: activation and adherence failures.
- Meta-Harness: agentic search over harness code and execution history.
- Classical graph GP/EA, NSGA-II/III, MAP-Elites/QD, multi-task EC and continual routing are mandatory algorithmic controls.

## Current narrow gap hypothesis (not a method claim)

The unresolved setting is multi-label/set-valued delegation with explicit graph dependencies under a temporally changing external agent pool. Single-ID routing (CARvE) is not sufficient; holistic graph orchestration (MAS-Orchestra) and graph evolution with task-difficulty curriculum (EvoMAS) do not by themselves establish old-cohort required-set retention under external pool changes. This boundary may still collapse to standard constrained graph EA/QD; that must be tested in the literature audit before any method design.

## Original project objective gate

The original project is not merely “apply an EA to an Agent.” H1 requires Agent-assisted discovery of an EC control mechanism on a source optimizer; H2 requires transfer of that high-level mechanism from MetaBox to AES; H3 is conditional. No valid source-to-target transfer object has been established. Do not silently convert this project into a target-only multi-agent workflow evolution paper.

## Next work

1. Finish the exact mechanism matrix for the listed methods.
2. Audit classical graph GP/EA, QD, multi-task evolutionary search, and continual routing.
3. Decide whether a unique EC update/variation/selection mechanism remains.
4. If no unique mechanism survives, record NO-GO and keep the pause.
5. If a mechanism survives, draft a development-only protocol; experiments still require separate explicit scope/budget approval.

## Hard limits

- No live LLM API calls.
- No MetaBox/AES scientific run.
- No GPU job.
- No AES environment extension.
- No held-out/test access.
- No new algorithm implementation or Phase-1A-19 handoff.
- Do not modify other repositories.


## Round-3 clarification

Multi-label continual learning already covers expanding specialist-label sets and label-dependency graphs (including Du et al., Pattern Recognition 2026, DOI 10.1016/j.patcog.2026.113657; publisher full text not accessible in the audit) and hierarchical label expansion (Lee et al., ICCV 2023). Do not claim novelty from multi-label selection alone.

The remaining possible gap is continual execution-graph adaptation under external agent-pool changes: actual invocation, dependency order, information handoff, adherence and end-task outcome. These must be distinguished from the predicted specialist set. Compare against CARvE/MLCIL on selection and EvoMAS/MAS-Orchestra on orchestration. No method claim or experiment is authorized.


## Round-4 additions

Mandatory new controls:
- MESH-Harness: global mean reward retention/eviction for fixed-slot module pools; fixed execution model/tool set.
- EvoRouter: joint MAS configuration via insight distillation, OPD and RL; released evaluation code pins five worker IDs.
- RSI-Router: subtask-level model assignment and model-specific skills with Pareto router archive; reported fixed model pair.
- SkillOrchestra: skill handbook, skill-specific agent profiles and sequential mode/agent routing; supports pool config but paper evaluations use fixed pools per setting.
- CollabFlow: learned collaboration graph, evidence-conditioned communication and reward-proportional team distribution.
- Procedural Graphs, RRSI, and Mixture of Self-Improving Branches.

Candidate hypothesis only: global-average module retention may suppress rare cohort-essential delegation subgraphs during external pool expansion. This must be tested against MESH-Harness, EvoMAS, CPE, CollabFlow, standard constrained graph GP/EA, and MAP-Elites/QD. Do not call it novel or implement before the mechanism comparison is complete.
