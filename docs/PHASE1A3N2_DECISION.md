# Phase-1A-3N2 Decision

## Verdict

**`NO_GO_FOR_QUALITY_CREDIT_METHOD`**

The pre-registered primary gate fails in the *opposite* direction: on the
endogenous-quality scenario, quality-residualized UCB loses to bucket UCB
**0-10** (mean regret 0.00 → 21.03). Shuffling the quality feature restores
performance to 0.00, proving the correction itself causes the harm.

## What the series established

| phase | finding |
|---|---|
| 3R | bucket-baseline subtraction is a decision no-op |
| 3N | quality residual 7-3 weak; IPW/DR gains elsewhere not about quality |
| **3N2** | **quality residual strictly harmful when arm means are q-independent** |

Mechanistic reading: residualization is only justified if the *optimal action*
depends on q (or if g_b(q) is shared across arms and removal changes
orderings). When q only shifts a common baseline, residualization adds noise.

## Stops (per protocol §10)

- No formal 2000-FE MetaBox experiment for this method.
- No Phase-1B.
- No further tuning of this synthetic line.
- CC-SOC / quality-residual / IPW-DR new-algorithm claims: **closed**.

## Next

Return to broader EC-mechanism search for a master's-thesis-grade improvement
with a *verified* gap (e.g. Path R honest empirical study of bucketed vs
global AOS remains legitimate as analysis, not novelty). Agent remains a
diagnosis/ablation tool, not the claimed algorithm.

## Evidence

- code SHA (this commit) — `scripts/phase1a3n2_final_battery.py`
- results `results/phase1a3n2/final_falsification.json`
  (config_hash `4781d8216fe092cc`)
- tests: `tests/test_phase1a3n2.py` (10 passed) + full suite on branch
- 600 logged decisions × 10 seeds × 6 scenarios × 10 learners; 0 LLM; 0 MetaBox
