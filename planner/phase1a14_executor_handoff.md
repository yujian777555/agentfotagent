# Phase-1A-14 Executor Handoff — Mechanism-Gap Search

You are continuing only the repository yujian777555/agentfotagent, branch phase1a-phase11-unified-agent-ec-roadmap. Do not mix it with openissue, CausalEvo-DSH, EvoPareto-Agent, GLEPPO or other independent projects.

## Read first
1. status.json
2. docs/PROJECT_CHARTER.md
3. docs/RESEARCH_DECISIONS.md (especially D-015 and D-016)
4. docs/PHASE1A12_DECISION.md
5. docs/PHASE1A13_LINKAGE_MECHANISM_AUDIT.md
6. docs/PHASE1A13_RECENT_OVERLAP_ADDENDUM.md
7. docs/PHASE1A13_DECISION.md
8. docs/PHASE1A11_CANDIDATE_AUDIT.md and docs/PHASE1A11_LITERATURE_MATRIX.md

## Locked objective
The project target is to apply a genuinely useful LLM-empowered evolutionary-computation method to improving Agent task performance. This target is fixed, but no benefit or novelty is presumed. MetaBox-to-AES transfer is optional and remains NOT_READY. AES is an engineering scaffold, not validated Agent capability evidence.

## Current decision
Phase-1A-13 rejected FCLE as currently specified. The paired four-point interaction estimator is close to Differential Grouping / fitness-based linkage learning; the linked-subset operator is GOMEA-style; AgentSwift and local linkage kernels further weaken novelty. Do not implement FCLE unless a new, substantive algorithmic distinction is found.

## Required next work: research, not implementation
1. Read the 2026 survey “Automated Design of Agentic Systems: A Survey of Algorithms for Searching, Optimizing, and Evolving LLM Agents, Workflows, and Prompts” as a taxonomy; distinguish peer-reviewed work from preprints.
2. Mechanism-audit “Beyond Prompts: Measuring and Optimizing LLM Tool-Agent Harnesses” (Findings EMNLP 2026), AgenticEvolve (arXiv:2610.31326), and the project's existing EvoTool/AgentSwift/AgentSquare/TTHE/Evoflux/EvoCF comparisons.
3. For each method, record target object, representation, update rule, selection rule, fitness, task split, generalization setup, strongest baseline and evidence level. Do not infer exact algorithm from abstracts alone.
4. Search for an EC mechanism gap that is not merely prompt/module/harness evolution, blame routing, value-model/MCTS search, generic linkage learning, counterfactual plan variation, or experiment/budget allocation.
5. Consider both project tracks without forcing either: (A) Agent-assisted discovery of an EC mechanism, (B) applying a validated EC mechanism to Agent policies. Track A's previous candidates are closed; generic LLM-driven operator selection is crowded. Track B's generic Agent architecture search is crowded.
6. If a candidate emerges, define exact equations/operators and the nearest method it differs from, plus a negative control and falsification criteria. If not, record NO_GO and continue search rather than fabricate novelty.

## Hard limits
- No source implementation in this phase.
- No real LLM API calls.
- No MetaBox performance runs.
- No AES scientific runs.
- No GPU hours.
- No held-out/test access.
- If a later experiment is authorized, use deepseek-flash only; never deepseek-v4-pro.
- Keep literature citations in strict bibliographic format and label paper/code evidence accurately.

## Required outputs
- docs/PHASE1A14_PRIOR_WORK_MATRIX.md
- docs/PHASE1A14_CANDIDATE_SHORTLIST.md (only if one or more candidates survive; otherwise a clear NO_GO record)
- docs/PHASE1A14_DECISION.md
- update status.json and this handoff with exact source SHA, decisions and work not done.
