# Latest Plan — Phase-1A-18 Follow-up Evidence Audit

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Branch: research/phase1a18-evotool-actionability-audit
- Base commit: e01e3447dc57d99a28d62d7eb9537894d2cdc0e3
- Status: PRELIMINARY_SOURCE_GROUNDED_LEAD; NOT_REOPENED; CURRENT_METHOD-DISCOVERY_ROUTE_PAUSED

## Fixed objective

The long-term objective remains to find a genuinely useful LLM-empowered evolutionary-computation method and apply it to improve Agent task performance. EC must be methodologically central. MetaBox is infrastructure, not a contribution; the Agent Evolution Sandbox (AES) is the required project-owned target environment, but its existing mock pilot is not scientific evidence.

## Current evidence update

Phase-1A-18 paused speculative candidate generation after direct Agent-evolution, harness-evolution, typed-GP, and MetaBox-to-AES transfer candidates failed their novelty/evidence gates.

A read-only follow-up audit of EVOTOOL's ACL 2026 paper, official implementation, and released replay data found a preliminary mismatch between blamed module frequency and mutation utility in one demo run:

- Caller: 53 proposals, 5 accepted (9.4%), no best-selection-score increase.
- Planner: 29 proposals, 20 accepted (69.0%), all three best-selection-score increases.
- Run: Qwen3-4B, BFCL demo subset, 90 train / 30 selection / 30 test instances, seed 42, 90 generations.

This is not independent replication, not proof that blame attribution is wrong, and not a novelty claim. Historical acceptance-rate scheduling overlaps established AOS/credit assignment, LAOS, and LLM4EO. See docs/PHASE1A18_EVOTOOL_BLAME_ACTIONABILITY_AUDIT.md.

## Decision

Keep PAUSE_CURRENT_AGENT_EC_METHOD_DISCOVERY_ROUTE. Do not create a Phase-1A-19 candidate-generation handoff. The only authorized follow-up is a narrow primary-source audit of LAOS/AOS/LLM4EO and causal/counterfactual credit assignment to decide whether the observed distinction is already known.

## Next task

Use planner/phase1a18_evotool_audit_handoff.md. Obtain LAOS full text and official code if possible; compare the exact credit signal, target object, update equation, and evaluation protocol. If the only remaining idea is acceptance-rate scheduling, close it as already known/minor variant. If an uncovered mechanism survives, submit a separate protocol and budget request before any experiment.

## Hard limits

- No live LLM API calls.
- No MetaBox performance experiment.
- No AES scientific run.
- No GPU job.
- No held-out/test access.
- No new algorithm implementation.
- Do not modify other repositories.

## Historical plan

The previous P0-R3 implementation plan is preserved at planner/phase0_p0_r3_historical_plan.md; the detailed Phase-0/Phase-1A audit trail remains in the linked decision and phase documents.
