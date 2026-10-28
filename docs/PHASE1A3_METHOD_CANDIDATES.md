# Phase-1A-3 Method Candidates

Status: research candidates, not approved innovations. No performance claims.

## Candidate A — Confound-controlled, state-conditioned operator credit (CC-SOC)

### A.1 Defect in the base method

JADE/SHADE reward F/CR by binary “offspring beats parent”. Bandit AOS rewards
Δf of an operator applied to whatever individual happened to be current.
**Confound:** operator credit mixes (i) operator quality, (ii) quality of the
target individual, (iii) search phase (early large Δf vs late tiny Δf).
A2R evidence: switching to rand/2 at stag≥5 did not beat fixed rand/1 —
we never measured whether rand/2 is better *in that state*, only that we ran it.

### Prior handling (must not re-claim)

- Contextual bandits (ML) condition reward on context — generic, not EC credit.
- Landscape-aware / state-aware AOS exist (PARTIAL evidence); formulas rarely
  include propensity or counterfactual baseline within state.
- LAOS puts state in the prompt but credit assignment is abstract-level.

### A.2 Mechanism (math + pseudocode)

Public state buckets b = φ(s_t) (e.g. stag × diversity × budget terciles).

For each operator a and bucket b keep:

- n(a,b): attempts
- r(a,b): mean *normalized improvement*  r = (f_parent − f_child)/|f_parent| (not binary)
- baseline r̄(b): mean improvement of *all* attempts in b (any operator)

**Credit** C(a,b) = r(a,b) − r̄(b)   (difference-in-means within bucket;
removes shared state difficulty).

**Selection:** ε-greedy or UCB over C(a,b); unused (a,b) forced once (coverage).

**Update:** exponential decay with half-life proportional to FE budget to limit
stale history (vs SHADE's unbounded successful memory).

```
for each generation:
  b = φ(state)
  a = argmax_a UCB(C(a,b), n(a,b))
  for each offspring under a:
      r = (f_parent - f_child)/max(|f_parent|, eps)
      update n(a,b), r(a,b), r̄(b)
      decay all C(·,b) toward 0 with half-life
```

**Confounds addressed:** target quality (within-bucket baseline), phase
(buckets), noise (UCB + coverage). **Not a free lunch:** bucket granularity is
a hyperparameter; needs sensitivity analysis.

### A.3 Agent contribution (graded)

Level 3: Agent reads published mechanism + our traces, proposes bucketing and
reward normalization; later Agent diagnoses failed attributions. If a classical
contextual bandit with hand buckets matches it, **agent adds nothing** — must
admit and use the classical method.

### A.4 Novelty risk

- `NOVELTY_UNRESOLVED`: state-aware AOS + contextual bandits exist.
- Distinguishing experiment: compare vs (i) standard SHADE, (ii) bandit AOS
  with raw Δf, (iii) same UCB without baseline subtraction, (iv) shuffled
  bucket labels. If (iv) ≈ CC-SOC, mapping is artifact.
- Papers that could kill it: Fialho et al. 2008+; “operator selection with
  landscape features”; any ICML contextual-bandit-in-EC paper. Verify before
  formal write-up.

---

## Candidate B — Phase-aware success memory with credit decay (PSM)

JADE/SHADE memory μ_F/μ_CR is polluted by early easy successes and never
expires. Proposal: weight successful F/CR updates by Δf and apply exponential
decay tied to measured diversity collapse (a *state event*, not a fixed epoch).

**Defect:** binary-success mean; stale memory.
**Mechanism:** μ ← (1−λ)μ + λ·w·value, w = clipped Δf / median(|Δf| of window),
λ increases when diversity drops below its own running quantile.
**Agent role:** none required (classical algorithm). Honest framing: this is
a SHADE variant; novelty `ALREADY_COVERED` risk high (Δf-weighted SHADE exists
in literature — verify).
**Decision:** keep as strong internal baseline for A, not the paper hero.

---

## Candidate C — Attribution-gated intervention (AGI)

Only apply stagnation/diversity interventions when a cheap online attribution
test says the *last* intervention improved within-state credit (Candidate A's
statistic). Otherwise stay vanilla.

**Defect:** A2R showed blind interventions hurt (ablate_no_stag > mech_3).
**Mechanism:** intervene iff ΔC(a,b) confidence interval excludes 0 over last W
generations for the intervention operator; else default DE.
**Agent role:** Level 3 diagnosis of failed gates.
**Novelty:** `NOVELTY_UNRESOLVED`; gated restarts exist in restart-DE literature
but with fitness thresholds, not credit-CI gates. Lower risk than A but smaller
claim.

---

## Selection

**Primary candidate: A (CC-SOC)** with C as an ablation arm (credit-gated
interventions). B is a baseline. Rationale: only A directly addresses the
confound we measured as fatal in A2R (operator chosen in hard states looked
worse without within-state comparison), and it connects to Phase-1B
(evolution can optimize φ/UCB hyperparams → Agent policy knobs).

**Novelty verdict (pre-experiment):** `NOVELTY_UNRESOLVED` — proceed only to
formal *falsification* protocol, not to claim.
