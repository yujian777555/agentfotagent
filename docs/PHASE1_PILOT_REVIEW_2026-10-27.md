# Phase-1 Pilot Review — 2026-10-27

## Decision

**NO-GO for the current transfer claim; PIVOT the next experiment.**

Source candidate: `3e48bf5305ba667490358c140dad556f1ebf84e2`  
Pilot report: `docs/PHASE1_PILOT_REPORT.md`  
Raw artifact: `results/pilot_phase1/pilot_results.json`

## What the pilot actually shows

- Six train tasks: three `key_crate` and three `dial_set`.
- Four arms: random search, target-only EA, transfer EA, shuffled mapping.
- Three debugging seeds and 12 proposals per arm.
- All four arms reached success rate 1.0; the report says all 16 genotypes solve all six tasks.
- Mean steps varied from 9.83 to 13.0, and the fixed surrogate prior preferred `plan_first`/verification alleles that were slower on this task set.
- The source prior is a manually fixed surrogate. It is not MetaBox-v2 output and is not Agent-generated strategy knowledge.
- The backend is a scripted mock policy. This is pipeline/engineering evidence, not Agent capability evidence.

Therefore, this pilot demonstrates that the end-to-end pipeline runs and that the current primary success metric is saturated. It does **not** demonstrate transfer benefit, a useful source-domain controller, or scientific novelty.

## Why the next experiment must change

Do not increase the number of seeds or budgets on the same saturated setup. Do not promote the surrogate prior to a scientific method.

Return to the project's intended order:

1. **Phase-1A — Agent-assisted EC on MetaBox-v2.** Use an explicit, constrained, inspectable controller object. An Agent must diagnose real evolutionary search traces and propose controller changes; a fixed hand-written prior does not count.
2. Compare against the unmodified optimizer, strong conventional adaptive baselines, random/ablated controller proposals, and the closest relevant LLM-assisted EC baselines.
3. Use validation tasks for controller selection and a disjoint test set for final evaluation. Freeze seeds, budgets, objective functions and stopping rules before the confirmation run.
4. Require the candidate controller to improve a predeclared metric across tasks/seeds, not only on a single best run. Record failures, runtime, function evaluations and LLM calls/tokens/cost.
5. Only after Phase-1A passes, transfer the same explicitly represented controller object to the AES genotype-search setting. Compare target-only EA and shuffled/state-action mapping controls.
6. Phase-1C bidirectional feedback is conditional on a reproducible Phase-1B transfer benefit.

## Authorization and limits

- CPU/local integration and no-API smoke tests may proceed.
- Live LLM calls require an explicit call/token/cost budget and approval. If unavailable, prepare the adapter and protocol but do not fabricate Agent-generated proposals.
- GPU use is not justified for the current deterministic toy pilot.
- Keep `relay_route` held out; do not tune the controller against held-out results.
- Treat this as a research pivot, not a negative paper result: the current pilot is too small and too saturated to support a scientific conclusion.
