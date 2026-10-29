# Phase-1A-12 Genome V2 Specification (Design Only)

Status: proposal only. Not implemented or experimentally validated. No API calls, scientific runs, or held-out access.

## Design principles
- Keep the underlying LLM model and interaction limit fixed across genotypes.
- Genes must change executable policy, not encode answers, task labels, hidden state, or evaluator details.
- Each allele requires a trace-based intervention test.
- Normalize inactive or behaviorally equivalent encodings.
- Do not inflate the genome with decorative parameters.

## Proposed schema
Schema name: `aes-genome-v2`. The nominal product has 3×4×4×3×4×3 = 1,728 combinations before canonicalization. This is not a claim that all are distinct phenotypes; effective size must be computed.

| Gene | Alleles | Intended runtime effect | Required test |
|---|---|---|---|
| planning_policy | direct, plan_first, replan_after_failure | Plan lifecycle; replan after tool failure/no-progress | Same state, trace shows policy-specific plan/replan |
| memory_policy | none, recent_window, failure_indexed, compact_state | Store/retrieve permitted observations | Task requiring reuse of earlier observation |
| verification_policy | none, before_submit, after_risky_action, uncertainty_triggered | Decide when to call public verify tool | Inject incorrect intermediate action and inspect trace |
| tool_selection_policy | fixed, state_conditioned, prerequisite_aware | Rank currently legal tools using public state | State change changes ranking without bypassing tool preconditions |
| recovery_policy | retry_once, inspect_then_retry, alternative_tool, rollback_if_supported | Respond to invalid/transient tool results | Forced failure changes next action; rollback only where environment supports it |
| termination_policy | submit_on_plan_end, submit_after_verify, stop_on_no_progress | Choose when to finalize, never declare success itself | Unsolved state cannot be falsely marked successful |

## Semantic collision risks
- Verification and termination may duplicate the same verify/submit sequence. Canonicalize equivalent combinations or remove one gene.
- Replanning and inspect-then-retry overlap. Define planning as plan lifecycle and recovery as immediate failure response.
- Failure-indexed memory must retain reusable observations, not merely trigger a retry.
- Rollback must be inactive and canonicalized for tasks without reversible actions.
- Uncertainty-triggered verification needs a grounded observable signal; model self-confidence alone is not accepted without calibration.
- Tool-selection policies may reorder only legal tools; environment preconditions remain authoritative.

## Compiler and trace contract
The compiler deterministically maps a normalized genome to a policy configuration. Runtime inputs are public task instructions, permitted observations, fixed-backbone model output, and genotype only. Hidden goals, answer keys, task seeds, split labels, and other candidates' scores must not enter model-visible inputs.

Trace genotype hash, policy branch, prompt/model/decoding version, proposed and executed actions, legality checks, observations, replans, recovery/verification events, terminal state and evaluator result. Token/cost fields are populated only from actual backend usage.

## Gate before implementation
Resolve whether verification and termination are separable; whether recovery and replanning have disjoint semantics; how uncertainty is computed; whether memory changes information use rather than prompt length; and how every allele gets a diagnostic intervention test. If the effective phenotype space collapses near the current 16 configurations, simplify rather than retaining artificial complexity.
