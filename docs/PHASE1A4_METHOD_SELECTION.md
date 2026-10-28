# Phase-1A-4 Method Selection

## Candidates (≤3)

1. **DPR-SHADE** — diversity/progress-conditioned population + memory reset.
2. Memory-reset-only SHADE (subset of 1).
3. Joint operator×F selection (dropped: low novelty vs SHADE joint sampling).

## Primary: **DPR-SHADE** (diversity-progress regulated SHADE)

### Defect in base (L-SHADE)

N(t) is a fixed linear FE schedule; F/CR memory M never resets. Both ignore
measured search state. Concretely: early diversity collapse wastes FE on
near-clones while N is still large; post-shift search keeps sampling F/CR from
the previous regime.

### Mechanism (math)

Let D_t = mean pairwise distance of population (normalized by box diameter),
S_t = success fraction in generation t, and R_t = running 20% quantile of D.

At each generation t (after evaluation):

1. **Progress event:** S_t < θ_s (0.05) for L consecutive generations (L=5).
2. **Collapse event:** D_t < R_t (tracked quantile over last W=20 gens).
3. If either event fires **and** ≥ G_min (5) generations since last reset:
   - reset memory M_F=M_CR=0.5 (priors);
   - set N ← max(N_min, ⌊N·ρ⌋), ρ=0.7;
   - inject εN random immigrants (ε=0.1) at current N (cost counted in FE).
4. Otherwise: standard SHADE sampling and linear reduction **on top of** N.

Pseudocode in `experiments/metabox/agent_assisted_ec/dpr_shade.py`.

### Nearest neighbor

L-SHADE (linear N, unreset M). Differences: state-triggered reset+shrink vs
fixed schedule; immigrants; quantile-based collapse detector.

### Why not already covered (risk `NOVELTY_UNRESOLVED`)

Non-linear population reduction and restart variants exist (PARTIAL evidence).
The *joint* D-quantile + success-stagnation trigger for **both** M-reset and N
shrink inside SHADE-style adaptation was not located this pass. Must re-verify
at write-up.

### Falsification

- vs L-SHADE-like (linear N, no reset) at identical FE.
- vs memory-reset-only; vs shrink-only; vs shuffled triggers.
- Failure: no gain on ≥2/3 train functions or gains explained by immigrants alone.

### Agent role (later)

Agent may propose θ_s/ρ/quantile settings from traces — only after hand-DPR
shows signal; equal-budget comparison required.

## Decision

**GO to small real MetaBox pilot** (train functions only, 500 FE, 3 seeds)
on DPR-SHADE vs L-SHADE-style control. Not a novelty claim.
