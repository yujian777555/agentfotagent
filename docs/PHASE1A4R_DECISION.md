# Phase-1A-4R Decision

## Answers to required judgments

1. **Component effects:** N (shrink) and I (immigrants) each help (6-3 vs
   baseline); M (memory reset) ≈ neutral alone and **harmful in combination**
   (full 3.25e6 vs N+I 1.16e6, paired 3-6).
2. **Timing:** state triggers **lose** to matched-random FE timing (3-6).
   Diversity-collapse triggers, not stagnation (stall_only=0).
3. **External baselines:** full beats official DE/SHADE 9-0 at 500 FE —
   budget-limited comparison, not a strong claim.
4. **Execution reliability:** FE exact; failed first run (gen-schedule bug)
   preserved; corrected run uses FE-based matched schedule.

## Verdict

**`METHOD_REVISION_REQUIRED` (narrow).**

- **Close** the memory-reset hypothesis and the stall/quantile *state-trigger*
  hypothesis for this mechanism family.
- **Keep** population-shrink + immigrants as a *plain restart-style operator*
  worth studying — but its benefit is achievable without state conditioning
  (≈ matched random), so the honest research object is **restart policy in
  SHADE-like DE**, not a state detector.
- **No expansion** of the state-triggered full method. No 2000-FE formal run.
- **Agent contribution: not evaluated** this phase (0 LLM calls).

## Next (if continuing)

Empirical study: when do shrink+immigrant restarts help (vs L-SHADE linear
N(t)) on harder/longer budgets — with matched-random timing as a required
control. Before any novelty claim, re-verify literature on restart policies.
Otherwise stop this line.

## Evidence

- code `2eebcf7b40b1…` · results `results/phase1a4r/manifest_a4r-2eebcf7b40b1-clean-20261028T155049.json`
- failed run preserved: `manifest_a4r-944575ce7344-…`
- tests `tests/test_phase1a4r.py` 4 passed; suite green on branch
