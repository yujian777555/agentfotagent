# Phase-1A-4R3 Literature Audit

Scope: restart/population-intervention mechanisms in SHADE/L-SHADE lineage.

## 1. L-SHADE (Tanabe & Fukunaga, CEC 2014, DOI 10.1109/CEC.2014.6900380)

**Mechanism (FULL, standard):** SHADE memory M_F/M_CR (k slots, historical
means of successful F/CR); current-to-pbest/1/bin **with external archive**;
linear population reduction N(t)=round(N_init·(1−t/T)·…) down to N_min.

- Population: linear schedule only; no restart/immigration.
- Memory: never reset; archive of replaced parents.
- **Same as N+I?** No — N+I adds *event-triggered* shrink + immigrants.
- **Gap:** no event-triggered intervention; linear schedule assumes uniform progress.

## 2. R-SHADE / RL-SHADE (Tanabe & Fukunaga, CEC 2015, DOI 10.1109/CEC.2015.7257133)

**Mechanism (PARTIAL — abstract/method excerpts):** budget-aware tuning;
R-SHADE = restart-style SHADE; RL-SHADE = L-SHADE variant with restarts for
long budgets. Restarts reinitialize population; exact trigger & immigration
policy not fully verified this pass (SECONDARY for details).

- **ALREADY_COVERED risk HIGH** for "restart + SHADE". Any N+I claim must
  differentiate from R-SHADE's restart schedule and RL-SHADE's long-budget
  regime. Do not rename R-SHADE as novel.

## 3. ARRDE (arXiv 2511.18429)

**Mechanism (SECONDARY — abstract):** non-linear population reduction +
adaptive restart–refine phases. Directly covers dynamic N + restarts.
**ALREADY_COVERED risk HIGH** for population-restart family. We cannot claim
"dynamic N + restart" as new.

## 4. SHADE/L-SHADE variants survey (SWEVO 2026, DOI 10.1016/j.swevo.2026.102286)

**Evidence: SECONDARY.** Confirms dense variant space; treat restart/adaptive-N
as studied territory.

## 5. Immigration / partial re-init in DE

Literature includes immigrants injection, partial reinitialization (e.g.
injected solutions in restart-DE). **SECONDARY.** Replacing worst 10% with
uniform random points is standard exploration injection — **ALREADY_COVERED
as a primitive**; value must come from *when/how*, not the operation itself.

## Verdict

| aspect | status |
|---|---|
| restart + SHADE | **ALREADY_COVERED** (R-SHADE/RL-SHADE) |
| event-triggered N shrink + immigrants vs linear N(t) | empirical question; no novelty claim |
| state-timing | already weak (4R2: 5-4) |

**Conclusion:** this phase is a **reproduction/empirical comparison**, not a
new-algorithm validation. If N+I beats L-SHADE, the honest framing is
"restart-style interventions on L-SHADE" with R-SHADE as nearest neighbor
(not yet run — RL-SHADE/R-SHADE official impl unavailable this session;
recorded as limitation).
