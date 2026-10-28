# Phase-1A-4 Mechanism Audit

Scope: stop credit-estimation line (`NO_GO_FOR_QUALITY_CREDIT_METHOD` frozen).
Four directions, original-method evidence first.

## A. Success-history adaptation (JADE/SHADE/L-SHADE)

**Formulas (FULL, standard):**
- JADE: μ_CR = mean of successful CRs (arithmetic); μ_F = Lehmer mean of
  successful F; archive of replaced parents (Zhang & Sanderson 2009).
- SHADE: memory M of k historical μ_F/μ_CR; sample F~N(M_F,0.1),
  CR~N(M_CR,0.1); archive size = N (Tanabe & Fukunaga 2013).
- L-SHADE: SHADE + linear population reduction N(t)=round(N_init·(1−t/T)·…)
  (Tanabe & Fukunaga 2014).

**Known handled issues:** external archive (JADE) prevents re-selection of
replaced parents; L-SHADE handles late-stage refinement via N(t).

**Residual gap (operational, not “history ages”):** M is updated by *binary*
success and never reset; when the search stage shifts (diversity collapse /
restart), stale F/CR means keep sampling the old regime. **Existing handling:**
restarts (CMA-ES style) exist; *diversity-triggered memory reset inside SHADE*
was not located in this pass (SECONDARY — absence unproven).

## B. Population size × phase control

L-SHADE's N(t) is a deterministic FE schedule. Assumption: optimal N declines
linearly with budget. **Observable defect:** on deceptive/multi-modal
functions, diversity can collapse long before the schedule reduces N (wasted
FE on clones) or N shrinks before a new basin is found. Related work on
non-linear / adaptive population sizing exists (PARTIAL). Candidate must not
be “another threshold on N(t)” — it must *jointly* condition N and F/CR memory.

## C. Joint mutation/parameter adaptation

SHADE already samples F/CR jointly from the same success history. Operator×F
interaction (e.g. rand/2 needs higher F) is known but rarely modeled
explicitly (SECONDARY). Risk: repackaging state-bucketed credit (closed).

## D. Agent-driven diagnosis

EoH/LLaMEA/AlphaEvolve/ADAS evolve *code* with LLM proposals (PARTIAL/SECONDARY
as before). None of the verified sources implement “Agent reads our typed
trace diagnostics → proposes a *parameter-schedule* change with ablation-tested
attribution”. That is a *process* contribution, not an algorithm; it can wrap
candidate B without being the claimed novelty.

## Verdict per direction

| dir | gap quality | nearest coverage | keep? |
|---|---|---|---|
| A memory reset | operational, measurable | restarts exist; in-SHADE diversity reset unverified | yes (merged into B) |
| B phase-joint N+F/CR | schedule assumption is a real, testable defect | non-linear N(t) variants (PARTIAL) | **primary** |
| C joint operator×F | interaction known | SHADE joint sampling | no (low novelty) |
| D Agent diagnosis | process-level | code-evolution systems | wrapper only |
