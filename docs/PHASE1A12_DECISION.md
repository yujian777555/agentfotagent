# Phase-1A-12 Design Decision — Updated After Recent Prior-Art Audit

- Date: 2026-10-29
- Basis: Phase-1A-11 audits, Phase-1A-12 AES design contracts, and a targeted primary-source/official-code audit including EvoTool (ACL 2026).
- Scope: design and literature audit only. No code changes to the AES runtime, real API calls, MetaBox runs, AES scientific runs, GPU use, or held-out access are authorized.

## Updated decisions

| Gate | Decision | Reason |
|---|---|---|
| Direct target-domain LLM-assisted EC as a generic method | **`NO_GO_AS_GENERIC_METHOD`** | EvoPrompt/Promptbreeder cover evolutionary prompt optimization; AgentSquare covers modular Agent search; EvoAgent covers evolutionary multi-agent generation; **EvoTool directly covers trajectory-grounded blame, targeted LLM mutation of tool-use modules, and diversity-aware evolutionary selection**; TTHE/Evoflux cover executable harness/workflow evolution from traces. |
| Direct target-domain research in a narrower mechanism | **`DESIGN_ONLY_GAP_SEARCH`** | Agent remains the fixed application target, but no distinct mechanism has yet been established after this prior-art review. The proposed `aes-genome-v2` is not approved for implementation as a research method until a concrete difference from the nearest work is specified. |
| MetaBox-to-AES transfer | **`NOT_READY`** | No source controller has passed Track A and no specific source/target state-action mapping is validated. Transfer is optional, not the project objective. |
| AES engineering scaffold | **`ACCEPTED_FOR_ENGINEERING_ONLY`** | Existing independent review supports the scaffold within engineering scope. |
| AES scientific experiments | **`NO_GO_UNTIL_ENVIRONMENT_REDESIGN_AND_REVIEW`** | 16-genome search is exhaustively enumerable; historical mock results saturated; EA selection has no gradient on all-success ties; no real LLM Agent backend is available in the audited runtime. |
| H3 / bidirectional feedback | **`NOT_STARTED`** | Neither a validated source controller nor transfer evidence exists. |

## What changed in this decision

The prior version treated the direct route as a conditional design GO while noting novelty uncertainty. The targeted audit of the official EvoTool paper and implementation materially changes that assessment. EvoTool already performs the generic loop that would otherwise be proposed here:
1. decomposes a tool-use Agent policy into Planner, Selector, Caller and Synthesizer modules;
2. uses the LLM to assign blame to a module from a full execution trajectory;
3. uses LLM feedback to mutate only the blamed module;
4. uses diversity-aware evolutionary population selection.

AgentSquare and TTHE/Evoflux further cover generic modular Agent search and executable harness/workflow evolution. Therefore, a larger genome, trace-guided mutation, module-wise edits, diversity selection, or an Agent task benchmark cannot individually or jointly be presented as a new contribution without a more specific mechanism-level difference.

See `docs/PHASE1A12_PRIOR_WORK_COMPARISON.md` for the source/evidence matrix and limitations.

## Disposition of existing Phase-1A-12 design documents

- `PHASE1A12_GENOME_V2_SPEC.md`: retain as a **non-approved design sketch** to make the current 16-genome limitation explicit. Do not implement it yet; its planning/memory/tool/recovery genes overlap AgentSquare/EvoTool and require a distinct method rationale.
- `PHASE1A12_TASK_DIFFICULTY_SPEC.md`: retain as an engineering/evaluation-readiness proposal. Task complexity and failure injection are not a method novelty claim; ToolMaze (2026) already studies dynamic replanning and tool anomaly recovery.
- `PHASE1A12_FITNESS_AND_BASELINE_CONTRACT.md`: retain as a fairness contract. Success-first lexicographic selection and exhaustive enumeration are evaluation correctness requirements, not an algorithm contribution.

## Next work: mechanism-gap search, not experiments

1. Compare the exact mechanisms of EvoTool, AgentSquare, TTHE, Evoflux and the project's prior Hyperagents/Harmony Harness audits. Do not claim an exhaustive literature search; record which full papers/code were actually inspected.
2. Search for an EC-level mechanism that is distinct from LLM prompt mutation, modular Agent search, trajectory blame/targeted mutation, executable workflow evolution, and generic controller transfer.
3. State one candidate only if it has an explicit update/selection rule, a measurable mechanism, and a negative control that can falsify the claimed advantage.
4. If no candidate passes the novelty gate, stop candidate generation and preserve the project state rather than running an under-differentiated pilot.
5. Any later implementation must first pass AES engineering review; any real-backend experiment requires a separate budget approval and must use `deepseek-flash` only.

## Falsification / stopping criteria

The next candidate is `NO_GO` if:
- the proposed mechanism is only a rewording or recombination of EvoTool/AgentSquare/TTHE/Evoflux or already audited prior work;
- the contribution is just a larger genome, harder tasks, a new benchmark wrapper, or an arbitrary fitness tie-breaker;
- exhaustive/random search explains the result without a distinct EC mechanism;
- the exact source/target transfer object is undefined or transfer does not beat target-only and shuffled-mapping controls;
- the proposed gain requires held-out feedback or post-hoc metric selection.

## Final verdict

**Continue the project, but not the generic direct Agent-evolution method and not the transfer experiment.** Agent improvement remains the fixed application target. The specific method is not yet found. No scientific experiment or API call is authorized by this decision.
