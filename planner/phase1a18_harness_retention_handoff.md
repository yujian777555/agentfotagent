# Handoff — Phase-1A-18 Harness-Expansion Retention/Adaptation Audit

Repository: yujian777555/agentfotagent
Working branch: research/phase1a18-evotool-actionability-audit
Baseline before this follow-up: 0ef286f0ed0cc8803d6cabc7eb8eec0ff7e27859
Current decision: PHASE1A18_PAUSE_REMAINS; lead status LEAD_UNRESOLVED_MORE_PRIMARY_SOURCE_NEEDED

## First read

1. status.json
2. docs/PHASE1A18_DECISION.md
3. docs/PHASE1A18_STRATEGIC_FEASIBILITY.md
4. docs/PHASE1A18_HARNESS_EXPANSION_RETENTION_AUDIT.md
5. docs/PHASE1A18_EVOTOOL_BLAME_ACTIONABILITY_AUDIT.md
6. docs/RESEARCH_DECISIONS.md
7. src/agentfotagent/environments/tool_world.py
8. src/agentfotagent/tasks/generators.py
9. src/agentfotagent/genome/schema.py

## Research question

When an externally expanding tool/skill/specialist-agent pool grows, can an EC-specific update/selection mechanism preserve previously required behavior while adapting to newly introduced capabilities, at matched evaluation budget and without excessive distractor delegation?

The concrete evidence lead comes from EvoHarnessBench (arXiv:2609.04280v3): delegation drift on forgotten tasks rises from 13% to 25% without adaptation; forgotten tasks often stop invoking previously required specialists; required-agent recall and distractor routing remain in tension. CPE (arXiv:2605.09315v1) explicitly leaves dynamic environments, multi-agent interaction, and expanding capability spaces as future work. This is a boundary to audit, not proof of novelty.

## Critical overlap warnings

- CPE already formalizes old/new capability preservation and gives channel-specific constraints.
- Are Self-Evolving Agents Continual Learners? already studies stability/plasticity and cross-task interference.
- EVOTOOL already evolves modular tool-use policies with blame-aware targeted mutation and diversity-aware selection.
- AEL already combines Thompson Sampling policy selection with slow LLM reflection.
- HarnessForge already jointly evolves harness and policy.
- Harness Updating Is Not Harness Benefit separates update quality from downstream benefit.
- Classical AOS, GP, multiobjective EA, and quality-diversity are required baselines.

Do not propose “add old-task score,” “use NSGA-III,” “add a retention coefficient,” “co-evolve harness and policy,” or “adapt policy selection” as standalone innovations.

## Required next work

1. Compare exact primary-source mechanisms and official code where available for CPE, EVOTOOL, AEL, HarnessForge, and related continual/evolutionary policy search.
2. Record each method's target object, genotype/representation, update/variation rule, selection rule, retention signal, action-space assumption, evaluation budget, and task split.
3. Decide whether any precise EC mechanism gap survives.
4. If only a standard retention objective/archive/scheduler remains, close the lead as NO-GO and keep the pause.
5. Only if a mechanism gap survives may a development-only protocol be drafted. No experiment before separate scope/budget approval.

## Project-code constraint

Current AES uses a fixed ALL_TOOLS set, three task families (key_crate, dial_set, relay_route), and four genes (planning, memory, verification, tool selection). It does not yet implement staged capability expansion or specialist-delegation traces. Do not claim the existing environment already supports the new setting.

## Hard limits

- No live LLM API requests.
- No MetaBox/AES scientific run.
- No GPU job.
- No held-out/test access.
- No new method implementation or Phase-1A-19 handoff.
- Do not modify any other repository.
