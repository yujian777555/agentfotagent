# Phase-1A-16 Candidate Decision

- Date: 2026-10-29
- Repository: yujian777555/agentfotagent
- Branch: phase1a-phase11-unified-agent-ec-roadmap
- Audit: docs/PHASE1A16_TYPED_CONTRACT_GP_AUDIT.md

## Decision

**NO_GO_TYPED_CONTRACT_VARIATION_AS_NEW_METHOD.**

No candidate is approved for implementation. The project is not closed.

## Reason

The generic idea of type-/grammar-/contract-aware evolutionary variation is already covered by:
- Strongly Typed GP (Montana, 1995);
- Grammatically-Based GP (Whigham, 1995);
- systematic GP constraint processing (1996);
- GenProg's test-guided, execution-path-localized program mutation and patch minimization (2009/2012);
- proof-search-based semantics-preserving genetic improvement (2018);
- LLM-seeded many-objective grammar-guided GP (MaOG3P/SBMaOG3P, 2024/2025);
- program synthesis with assumptions/assertions and SMT mutations (2026);
- safe and robust policy synthesis with Bayesian model checking or SMT/model checking.

A domain-specific policy for tool calls does not create novelty by itself. Syntax validity, type validity, state-dependent action preconditions, postconditions, episode success and generalization must be measured separately.

## Residual uncertainty

A narrowly defined temporal-effect-conditioned variation operator is **UNRESOLVED**, not admitted. There is no precise operator, evidence of a missing mechanism, or falsifiable advantage yet. Do not name or implement it as a method.

## Next phase

Phase-1A-17 returns to the charter's H2 hypothesis: transfer of a frozen evolutionary-control policy from a source optimization domain (MetaBox) to a distinct target Agent-policy search domain (AES). Audit:
- hyper-heuristic and adaptive-operator transfer;
- multi-task evolutionary optimization and explicit transfer operators;
- cross-domain controller transfer and state/action abstraction;
- Agent architecture/Harness transfer (Harmony Harness, MaAS, AgentSwift, AEL and related work);
- negative transfer, representation alignment and target-only alternatives.

A transfer candidate is admissible only if the same controller object and its state/action semantics can be defined before seeing target results, and if a fixed mapping can be tested against shuffled mapping, target-only training, random controller, and strong target-specific baselines. If this cannot be defined, reject H2 rather than building a bespoke adapter and calling it transfer.

## Work not done

- No code changes.
- No live LLM API requests.
- No MetaBox/AES performance runs.
- No GPU use.
- No held-out/test access.
