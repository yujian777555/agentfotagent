# Phase-1A-3 Research Decision

## Frozen history (do not rewrite)

- A2R: `NO_BENEFIT`. Frozen agent_mech_3 < Fixed Classic DE (17-38-5);
  ≈ deterministic (1-4-55); < random-mech distribution (7/20 wins);
  ablate_no_stag better than full mech; inject fired 5×; shuffled_map
  historically inert (mapping actually unchanged in one build).
- Direct LLM F/CR control: `REJECTED_FOR_CURRENT_PROTOCOL`.
- Phase-1B not authorized.

## Mechanism gap (evidence-backed)

**Operator credit is confounded with search state.** In A2R traces
(840 generations, 60 runs), assignment is policy-triggered (stag≥5 → rand/2):

| operator | n | mean succ | stag_mean | budget_mean |
|---|---:|---:|---:|---:|
| rand/1/bin | 130 | 0.442 | 0.9 | 0.30 |
| rand/2/bin | 710 | 0.261 | 56.1 | 0.54 |

Within `stag<5` only rand/1 appears (130 vs 4); within `stag>=5` only rand/2
(706). **No counterfactual cells exist** — raw Δf/success cannot identify
operator quality. This is exactly why A2R interventions could not be attributed.

Also: 45 generations satisfy both stag≥5 and div≤30; first-match always takes
the operator rule, so diversity injection is shadowed (only 5 gens eligible
under stag<5). Traces confirm mechanism attribution was not possible.

*Check limits:* descriptive; assignment not randomized; success_fraction is
policy-level; cannot be read as causal. Supports **designing** CC-SOC, not
proving it wins.

## Primary candidate: CC-SOC (confound-controlled state-conditioned credit)

See `PHASE1A3_METHOD_CANDIDATES.md` §A.

- Buckets b=φ(stag,div,budget); credit C(a,b)=mean(r|a,b)−mean(r|·,b);
  r=(f_par−f_child)/|f_par|; UCB+coverage; decay with FE half-life.
- Attribution gate (Candidate C) as ablation; PSM (B) as baseline.
- **Novelty: NOVELTY_UNRESOLVED** (contextual bandits / state-aware AOS overlap
  not fully verified). Framing is falsification, not claim.

## Agent role (honest)

Level 2–3: Agent proposes bucketing/reward from published mechanisms + traces;
must beat or match a **hand-coded** CC-SOC. If classical wins, agent adds
nothing → drop LLM from this paper's method core.

## Falsification protocol (formal run — NOT started)

**Platform:** MetaBox BBOB-10D, split_v2: train F1,2,4,6,7,10 / val F13,16,22 /
held-out F19,20,21 only after freeze. Sealed test [5,9,14,17,24] untouched.

**Budget:** 2000 FE, NP=20, dim=10, ≥10 seeds, identical for all arms.

**Arms:** (1) MetaBox DE (2) Fixed Classic F=0.5 CR=0.9 (3) SHADE (verified
config) (4) PSM (Δf-weighted memory) (5) **CC-SOC** (6) CC-SOC without
baseline subtraction (7) UCB over raw Δf, no buckets (8) shuffled bucket labels.

**Primary metric:** regret (optimum-known), paired W-L-T per function×seed.
**Secondary:** success rate, FE exactness, wall time.

**Minimum acceptable gain:** CC-SOC ≥ best baseline on ≥4/6 train functions
and median regret ≤ 0.9× SHADE, with ≥3/6 strict wins.

**NO_BENEFIT if:** ≤3/6 vs SHADE, or shuffled buckets ≡ CC-SOC, or arm (6)/(7)
matches CC-SOC (then novelty reduces to UCB/Δf weighting — likely covered).

**Agent-ablation:** hand-CC-SOC vs Agent-CC-SOC identical protocol; if equal,
report agent as non-contributory.

**Stop rules:** FE mismatch → discard run; any test-split access → invalid;
gains only via more FE → invalid.

## Phase-1B bridge (design only)

CC-SOC's φ (bucketing) and UCB params are evolvable genomes — Phase-1B can
optimize them per Agent-task family with the AES harness. Transfer must keep
credit semantics (within-state baseline), not just operator names. Prove
Phase-1A benefit first.

## Decision

**GO to formal experiment design freeze** (protocol above). Not GO to claim
innovation. If literature check at write-up time shows state-conditioned AOS
with identical credit baseline, relabel as replication and pivot to the
Agent-credit/diagnosis loop only if that is also uncovered.

Deliverables: this doc + literature matrix + method candidates +
`results/phase1a3/credit_confound_check.json`.
