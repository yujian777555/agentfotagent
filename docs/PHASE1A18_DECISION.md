# Phase-1A-18 Decision

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Assessment: docs/PHASE1A18_STRATEGIC_FEASIBILITY.md

## Decision

**PAUSE_CURRENT_AGENT_EC_METHOD_DISCOVERY_ROUTE.**

The project is not claiming that LLM-empowered evolutionary computation can never improve Agents. The current method-discovery route is paused because no defensible algorithmic gap survives the existing audits and the targeted review of current Agent-evolution literature.

## Why option A failed

Direct Agent-targeted EC research did not meet the required gate:
- EVOTOOL (ACL 2026) already evolves modular tool-use policies using trajectory-grounded blame attribution, targeted mutation and diversity-aware selection.
- HarnessLens (2026 preprint) already covers behavior-aware selective verification and attributable evidence.
- HarnessDev and Evo-Bench explicitly evaluate creation/evolution of Agent harnesses and expose domain/model-dependent results.
- Rethinking Harness Evolution demonstrates why equal-budget search baselines and disjoint held-out tasks are necessary; an evaluation-protocol paper alone would not satisfy the intended algorithmic contribution.
- Generic executable policy evolution is also covered by LLM-driven code evolution for control.
- Earlier Phase-1A-14 through Phase-1A-17 gates found no surviving candidate and no valid MetaBox-to-AES transfer object.

The exact problem required by the handoff—an uncovered, measurable Agent failure mode plus a specific EC mechanism whose effect is not explained by standard GP/EA, random search, local search, AOS, LLM-only search or test-time scaling—has not been established.

## What this decision means

1. Stop generating speculative algorithm candidates and do not create a Phase-1A-19 candidate-generation handoff.
2. Do not implement a new method or run a pilot merely to create positive evidence.
3. Do not use live LLM API, MetaBox performance experiments, AES scientific runs, GPUs or held-out/test tasks.
4. Preserve the repository and all prior negative results.
5. Reopen only when new source-grounded evidence identifies a precise mechanism-level gap or an approved development-only experiment shows a practically meaningful EC-specific advantage against strong equal-budget controls.

This is a pause of the current route, not a claim that the broader scientific objective is impossible. The next useful activity is independent literature monitoring or a genuinely new empirical failure report—not another candidate list.

## Evidence sources

- EVOTOOL, ACL 2026: https://aclanthology.org/2026.acl-long.2016/
- HarnessLens, arXiv:2608.27311: https://arxiv.org/abs/2608.27311
- HarnessDev, arXiv:2609.01437: https://arxiv.org/abs/2609.01437
- Evo-Bench, arXiv:2608.09096: https://arxiv.org/abs/2608.09096
- Rethinking the Evaluation of Harness Evolution for Agents, arXiv:2607.12227: https://arxiv.org/abs/2607.12227
- Code Evolution for Control, arXiv:2601.06845: https://arxiv.org/abs/2601.06845
