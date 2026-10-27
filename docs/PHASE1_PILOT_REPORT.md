# Phase-1 Pipeline Pilot Report (debug, not confirmatory)

- Source tree: `phase0-r4-fixes` @ `1776e0f` (plus pilot scripts)
- Command: `python scripts/run_phase1_pilot.py`
- Tasks: key_crate + dial_set train seeds 1,2,3 (6 tasks)
- Arms: random_search, target_only_ea, transfer_ea, shuffled_mapping
- Budget: 12 proposals, seeds 11/22/33
- Backend: mock-engineering-v2 (gene semantics intervention-tested; not LLM capability)

## Result

| Arm | best success rate (max over pilot seeds) |
|---|---|
| random_search | 1.0 |
| target_only_ea | 1.0 |
| transfer_ea | 1.0 |
| shuffled_mapping | 1.0 |

**Primary metric (task success) is at ceiling.** All 16 genotypes solve all
pilot train tasks. Transfer cannot improve a saturated fitness landscape.

## Secondary diagnostic (all 16 genomes, mean steps)

Range 9.83–13.0 steps. Efficiency does discriminate. The surrogate source prior
prefers `plan_first` / `check_before_finalize`, which are *slower* on these
tasks (13.0 vs 9.83 for the fastest).

## Decision

`NO_GO_OR_PIVOT` on transfer under the current target difficulty.

Do **not** expand transfer claims. Next research step (after Phase-0 acceptance)
is harder AES task instances and/or an efficiency-aware protocol — not a larger
transfer matrix on the saturated suite.

## Limitations

- Pilot only; 3 seeds; mock policy; surrogate source (not MetaBox-v2).
- Phase-0 remains NOT ACCEPTED pending R4 independent review.
- This is not Agent capability evidence and not a scientific result.
