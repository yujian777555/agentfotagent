# Phase-1A-17 Decision — MetaBox-to-AES Controller Transfer

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Branch: phase1a-phase11-unified-agent-ec-roadmap
- Literature matrix: docs/PHASE1A17_TRANSFER_LITERATURE_MATRIX.md
- Alignment audit: docs/PHASE1A17_STATE_ACTION_ALIGNMENT.md

## Decision

**NO_GO_H2_TRANSFER_AS_CURRENTLY_SPECIFIED.**

This is a route-level decision for the current MetaBox-to-AES controller-transfer hypothesis, not a project-level NO-GO. No candidate method is approved, and no experiments are authorized.

## Decisive reasons

1. **No source controller passed the method gate.** Phase-1A-14 had zero surviving candidates; Phase-1A-10 had zero blind-review PASS candidates and Stage D did not run. The project cannot transfer an unapproved or nonexistent source controller.
2. **The state mapping is generic.** Relative progress, stagnation, diversity, operator credit and normalized evaluation progress can be made to look similar across domains, but this is a standard search-state abstraction, not a novel EC mechanism.
3. **The action mapping is many-to-many.** Numeric DE strategies and parameter updates do not map uniquely to structured Agent policy mutations, module recombination, selection and policy injection. Mapping them to explore/exploit/preserve/restart creates a generic hyper-heuristic; bespoke target-side reinterpretation breaks the frozen-transfer claim.
4. **Transfer is already an established EC topic.** A 2025/2026 systematic review covers 47 primary studies and categorizes instance, representation and parameter transfer. Adaptive task/seed transfer and transfer learning in GP hyper-heuristics are existing primary work.
5. **Agent-side transfer is also crowded.** Hyperagents reports cross-domain transfer of meta-level improvement procedures. Harmony Harness factorizes general-purpose and task-specific harness evolution; MESH-Harness studies bandit-guided compositional harness evolution; Meta-Harness searches executable harness code using scores and traces.
6. **The precise intersection remains unresolved, not novel.** No exact primary paper matching “same frozen MetaBox numerical-EC controller directly controls AES Agent-policy evolution” was identified in this targeted audit. That is not sufficient novelty evidence, especially when the source controller and fixed semantic mapping are both missing.

## What remains valid

- The fixed project goal remains to apply a genuinely useful LLM-empowered EC method to improve Agent task performance.
- MetaBox remains source-domain infrastructure, not a contribution.
- AES remains a project-owned engineering scaffold and needs separate validity evidence before scientific claims.
- LLMs may still assist EC, and EC may still improve Agent policies; the current transfer architecture is simply not justified.
- The project is not authorized to make real API calls, run MetaBox performance experiments, run AES scientific experiments, use GPUs, or access held-out/test tasks.

## Stop rule and next step

Stop generating variants of the same cross-domain controller-transfer idea. Do not rename a generic state abstraction or adapter as a new method.

Phase-1A-18 should be a **strategic feasibility reset**, not another candidate list: compare the remaining direct Agent-targeted EC route against retiring this project route, using the fixed objective, prior-work matrix, and concrete evidence requirements. It must not introduce a new algorithm name or run experiments. A continuation recommendation must explain the exact research object and why the EC mechanism is indispensable; otherwise recommend pausing the project rather than looping through more speculative candidates.
