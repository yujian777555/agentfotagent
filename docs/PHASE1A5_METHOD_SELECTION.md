# Phase-1A-5 Method Selection

## Stage A (3 × deepseek-flash, frozen L-SHADE trajectories)

All three independent proposals **converged** on the same mechanism:
**progress-adaptive population-size reduction** — replace L-SHADE's linear
N(t)=N_init(1−FE/FE_max) with a schedule gated on smoothed relative
improvement, so N shrinks faster on easy functions (F1 converges early) and
slower on hard ones (F10 still improving at N=4).

Candidate fields (see `results/phase1a5/stageA_candidates.json`):
defect=linear N decoupled from progress; patch=modulate reduction rate;
nearest=L-SHADE + AP-SHADE-like adaptive-N; falsification=F10 must improve
≥5–10% without F1/F20 degradation; ablation=linear vs progress-gated vs
fixed alpha.

## Stage B (3 × deepseek-flash adversarial reviews)

| review | verdict | key claim |
|---|---|---|
| 1 | **REJECT** | already covered by jSO/APS/stagnation-gated L-SHADE variants; renaming |
| 2 | **REJECT** | renaming/over-engineering of progress- or stagnation-driven N reduction |
| 3 | **REJECT** | real defect but remedy is stagnation-gated reduction (already closed line); unnecessary smoothing params |

`results/phase1a5/stageB_reviews.json`. 3/3 REJECT, `already_covered=True` twice.

## Threshold check

Per protocol §4/§9: candidate must be distinguishable from nearest prior work
and not a rename. Reviews judge it a rename of existing adaptive-N schemes.

**No candidate passes the gate. Pilot NOT authorized.**
