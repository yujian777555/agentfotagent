# Phase-1A-13 Decision

- Date: 2026-10-29
- Project: agentfotagent only.
- Branch: phase1a-phase11-unified-agent-ec-roadmap.
- Scope: literature and mechanism audit only.
- No code implementation, live API call, MetaBox run, AES scientific experiment, GPU run, or held-out access occurred.

## Decision

**FCLE (Family-Consistent Linkage Evolution): NO_GO_AS_CURRENTLY_SPECIFIED.**

This is a candidate-level rejection, not a project-level rejection.

## Why FCLE does not pass the novelty gate

1. The proposed pairwise interaction estimator is essentially the four-point interaction test from Differential Grouping / fitness-based linkage learning. The full accepted manuscript of Olieman, Bouter and Bosman (IEEE TEVC, 2021) was inspected and explicitly describes this mechanism.
2. The proposed linked-subset operator is GOMEA-style gene-pool optimal mixing; GOMEA/CGOMEA already learn and exploit variable dependencies.
3. Linkage kernels (GECCO 2022) already learn local linkage structures for multiple dependency patterns, weakening the claim that family-specific linkage alone is new.
4. AgentSwift (AAAI 2026) covers workflow/component interaction coverage, task-conditioned value prediction and hierarchical search; AgentSquare covers module evolution/recombination; MaAS covers query-conditioned architecture distributions.
5. EvoTool, Beyond Prompts/PRISM, TTHE, Evoflux, EvoCF, Code Evolution for Control, SEVerA and HASP further crowd out generic claims about trace-guided module edits, executable policy/harness evolution, counterfactual plan mutation and constrained Agent synthesis.
6. Confidence intervals, bootstrap resampling and family-consistency thresholds may be good experimental safeguards, but adding them around an established estimator does not yet constitute a sufficiently distinct EC algorithm.

The full evidence and source limitations are in:
- docs/PHASE1A13_LINKAGE_MECHANISM_AUDIT.md
- docs/PHASE1A13_RECENT_OVERLAP_ADDENDUM.md

## Project-level status

- Fixed target remains: apply a validated LLM-empowered evolutionary-computation method to improve Agent task performance.
- Generic direct Agent-genome evolution remains NO-GO as a claimed novelty.
- MetaBox-to-AES transfer remains NOT_READY.
- AES remains accepted as an engineering scaffold only.
- aes-genome-v2 remains an unapproved design sketch.
- No scientific experiment or API call is authorized.

## Next research task

Continue a mechanism-level gap search, using the 2026 Automated Design of Agentic Systems survey as a taxonomy and explicitly including the newly found EMNLP 2026 paper “Beyond Prompts: Measuring and Optimizing LLM Tool-Agent Harnesses” and arXiv:2610.31326 AgenticEvolve.

Do not generate another list of Agent modules. Compare the actual algorithmic update/selection rules and isolate a research object not already covered by:
- LLM prompt/module/harness evolution;
- trajectory blame or failure-surface routing;
- value-model/MCTS or query-conditioned architecture search;
- generic linkage learning/optimal mixing;
- counterfactual plan mutation;
- generic LLM-agent experimentation;
- budget allocation alone.

If no candidate passes, report NO_GO and explain the evidence rather than forcing a method or starting experiments.
