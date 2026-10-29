# Phase-1A-11 Candidate Audit

- Date: 2026-10-29
- Audited source baseline: `3c3c6293aefa4861047b56d2c4d1057feb6a9b7c` (Phase-1A-10 Corrective + Stage B)
- Audit branch: `phase1a-phase11-unified-agent-ec-roadmap`
- Primary artifacts:
  - `results/phase1a10/candidates_raw.json` blob SHA `32b0784e86999284a970de44843abd412da0443f`
  - `results/phase1a10/evaluation_report.json` blob SHA `a2b309f0c56a5eb8c0fb033da0f2895b09ba6f52`
  - `results/phase1a10/stage_c_review.json` blob SHA `1e43e11e6e7546330d135b87e2951b9ae646bbd3`
  - `docs/PHASE1A10_TASK_CARDS.md`, `docs/PHASE1A10_STAGE_B_RESULTS.md`, `docs/PHASE1A10_STAGE_C_REVIEW.md`, `docs/PHASE1A10_DECISION.md`
- Scope: static artifact and literature audit only. No LLM calls, no code changes to optimizer, no MetaBox run, no test/held-out access.

## Decision summary

**Track A decision: `NO_GO_CURRENT_CANDIDATES`.** None of the four Phase-1A-10 candidates should proceed to implementation or performance testing as a new algorithm claim. Three are variants in the already heavily studied boundary-constraint-handling family; the fourth combines familiar F-parameter lower-bounding and diversity/stagnation-triggered memory reset. The exact combinations may not be byte-for-byte identical to a cited algorithm, but the current artifacts do not establish a sufficiently distinct mechanism or a coherent, fully specified causal rule.

This closes these four candidates, not the overall project objective. It does not prove that LLMs can never assist EC design, nor that EC cannot improve Agent. It means the current candidate set has no justified experiment gate.

## Candidate-by-candidate audit

| Candidate | What the raw proposal actually specifies | Closest prior art / issue | Verdict |
|---|---|---|---|
| `per-dimension-F-floor-with-memory-reset` (A, TASK-05) | `F_i=max(F_sample_i, F_min+(F_max-F_min)(diversity/diversity_0))`; if global diversity remains below `tau` for `W` generations, reset all `M_F[k]` to 0.5. | The name says “per-dimension”, but the formula has no dimension index and uses one population-level diversity scalar; it is not a per-dimension rule as written. Diversity-triggered dimension intervention/reinitialization and adaptive F/CR control are well established (AEPD, ADLA, ADE-DMRM, PaDE-pet, and broad PCM reviews). The memory reset adds a heuristic combination but no distinct state/action semantics. | `MINOR_VARIANT / NOVELTY_UNRESOLVED`; reject current specification. |
| `repair-aware-mutation-resample` (A, TASK-04) | If OOB fraction exceeds `tau`, redraw donor/base indices up to `K` times, fall back to clip, and halve F after a repair event. | Whole-vector mutation resampling until feasible and per-coordinate random reinitialization are both explicitly described BCHMs. Adaptive F changes and boundary handling have extensive prior art. The proposal does not precisely define index exclusions, archive handling, p-best selection, or how the current-to-pbest mutation is preserved under redraw. | `ALREADY_COVERED_CORE / MINOR_VARIANT`; reject current specification. |
| `repair_aware_resampling` (A, TASK-04) | For each OOB coordinate, sample uniformly within the bounds up to K=3 attempts, then clip. | This is the established random reinitialization of infeasible components, combined with a retry cap. It is not the same implementation as whole-vector resampling, but both are standard boundary-handling choices. | `ALREADY_COVERED`; reject. |
| `repair-aware-mutation-reflect` (B, TASK-04) | Reflect OOB coordinates; if still OOB, resample; record a repair flag and multiply memory weight by `1+0.5r`. | Reflection and resampling are standard BCHMs; SHADE already uses improvement-weighted success-history memory. No primary-source evidence was found in this targeted pass proving the exact repair-flag multiplier identical to an earlier rule, so exact novelty remains unresolved. The proposal's causal logic is internally unclear: it says repaired trials have lower success and corrupted directions, yet gives repaired successful trials *more* memory weight. The raw candidate sets `trace_path: "none"`, despite the evaluator's traceable flag; the evidence pointer needs reconciliation before the claim is accepted. | `NOVELTY_UNRESOLVED` plus specification/evidence defects; reject current candidate. |

### Why “four candidates” is misleading

- The two resampling candidates share the same core hypothesis: clipping harms OOB trials and resampling should improve repaired-trial outcomes.
- The reflection candidate changes the same boundary-repair component and adds a memory-weighting heuristic.
- The F-floor candidate is a separate parameter-control/reset family, but its advertised “per-dimension” property is absent from the written formula.
- They are not four independent research directions and must not be counted as four potential contributions.

## Evidence quality and implementation readiness

1. Phase-1A-10 Stage C marked all four as `NEEDS_REVIEW / NOVELTY_UNRESOLVED`, not PASS. No candidate was independently cleared for novelty.
2. Stage D was not run. There is no performance evidence for any of these proposals.
3. Candidate names and evidence fields are not a substitute for an exact algorithm. The reflection candidate's raw `trace_path="none"` conflicts with the evaluator's `evidence_traceable=true` label; audit the evidence registry mapping if this candidate is ever reused.
4. Candidate 1 is semantically misnamed unless the formula is changed to include a true per-coordinate/per-dimension state. Changing the name alone would not create novelty.
5. Candidate 4's weighting rule needs a directionally consistent causal explanation before implementation; otherwise it risks amplifying the same repaired-trial signal alleged to be harmful.
6. The current 24-request budget has already been consumed in Phase-1A-10. This audit authorizes no additional API requests.

## Literature-based rationale

The targeted primary/near-primary literature pass confirms substantial prior art:
- Boks, Kononova, and Wang (GECCO Companion 2021) benchmark 13 boundary constraint handling methods over 28 DE configurations and explicitly describe whole-vector resampling, random reinitialization of OOB components, projection, and reflection.
- Biedrzycki et al. (Swarm and Evolutionary Computation, 2019) study 17 bound-constraint handling methods across seven DE algorithms.
- Tanabe and Fukunaga (IEEE Transactions on Cybernetics, 2020) review and benchmark 24 DE parameter-control methods for F and CR.
- AEPD (Yang et al., IEEE Transactions on Cybernetics, 2015), ADLA (Knowledge-Based Systems, 2020), ADE-DMRM (Expert Systems with Applications, 2024), and PaDE-pet (Expert Systems with Applications, 2023) cover diversity-guided intervention, dimension-level reinitialization, restart/diversity mechanisms, and dimension-improvement-based parameter adaptation.

Full citation details and the precise overlap are recorded in `docs/PHASE1A11_LITERATURE_MATRIX.md`. This was a targeted audit, not proof that every related paper or implementation has been exhaustively searched.

## Required next action

Do not send another open-ended LLM proposal batch for these four tasks. Preserve them as historical candidates and move effort to Track B: determine what the AES must change before evolutionary search over Agent policies is a meaningful scientific experiment. Any later Track A candidate must first pass a human-reviewed mechanism specification and a primary-source novelty gate before any live API budget is requested.
