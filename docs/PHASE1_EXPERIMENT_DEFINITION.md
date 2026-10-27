# Phase-1 Experiment Definition (transfer object pilot)

Status: DEBUG PIPELINE PILOT COMPLETED; NOT CONFIRMATORY. Phase-0 R4 is now accepted and merged as an engineering scaffold only. This source→AES transfer pilot remains NO_GO_OR_PIVOT and does not validate transfer benefit.

## Scientific question

Can a source-domain-derived transfer object improve evolutionary search over
AES agent genotypes versus target-only search, and does a shuffled-mapping
negative control rule out accidental benefit?

## Domains

- **Source (surrogate, pilot only):** a deterministic ranking of genome alleles
  derived from a synthetic source landscape (see `transfer/source_prior.py`).
  MetaBox-v2 is the planned production source; the adapter is not wired in
  this pilot. The surrogate is explicitly NOT a novelty claim.
- **Target:** AES `key_crate` + `dial_set` train tasks, scored by
  `StateBasedEvaluator` from environment final state via the real
  genotype→phenotype→tool-world path (mock backend policy; engineering
  semantics of the four genes are already intervention-tested).

## Transfer object

Allele preference weights `w[gene][allele]` in `[0, 1]`. Transfer applies them
as mutation biases when generating offspring in the conventional EA.

## Arms (same genome space, evaluator, task list, budget, seeds)

1. **target_only_ea** — uniform mutation.
2. **transfer_ea** — mutation biased by source allele weights.
3. **shuffled_mapping** — same weight multiset, gene→allele mapping randomly
   permuted (negative control).
4. **random_search** — no transfer.

## Metrics

- Primary: mean task success rate of the best genome over the budget.
- Secondary: proposals, unique genomes, cache hits, wall time.
- Decision: transfer must beat target_only_ea AND shuffled_mapping must not
  match transfer; otherwise NO-GO/PIVOT.

## Pilot protocol

- Seeds: 3 (debug). Budget: 12 genome proposals per arm.
- Train tasks only. Held-out not read in the pilot.
- Artifacts under `results/pilot_phase1/`.


## Post-pilot decision (2026-10-27)

This protocol is retained as the record of the initial pipeline pilot, not as authorization to scale it. The source allele weights are a fixed surrogate, not MetaBox output or Agent-generated knowledge; the primary success metric saturated at 1.0 for every arm. The next scientific gate is Phase-1A: Agent-assisted EC on MetaBox-v2 with real evolutionary trajectories, a constrained controller representation, strong baselines, held-out validation and an explicitly approved LLM call/token/cost budget. Only after a positive source-domain result should this transfer protocol be revisited.
