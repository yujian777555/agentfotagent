# Phase-1 Experiment Definition (transfer object pilot)

Status: PRE-ACCEPTANCE PIPELINE PILOT. Phase-0 is NOT ACCEPTED until R4
independent review passes. This document defines the experiment; results from
the pilot are directional only and are not confirmatory evidence.

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
