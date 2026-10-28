# Phase-1A-4 Pilot Protocol (frozen before run)

- Code SHA at run: `56c319064c92c68a5dcaab3b9c6791c35ae25dba`
- Platform: MetaBox metaevobox 2.0.2, BBOB-10D, split_v2 **train only**
- Functions: F1 (separable), F10 (high-cond), F20 (multimodal-weak) — chosen to
  span families; documented before run.
- Seeds 11,22,33 · NP=20 · **500 FE** · minimize · FE exact enforced
- Modes: full / no_reset / no_shrink / shuffled_triggers + official DE + SHADE
- Purpose: execution check + directional signal only (3 seeds).

## DPR-SHADE mechanism (as implemented)

SHADE-style F/CR memory; on (stall≥5 gens or D_t<q20(D)) and ≥5 gens since
last: reset M to 0.5, N←0.7N (min 4), inject 0.1N immigrants.
`shuffled_triggers`: random 20% reset probability (no state conditioning).
`no_reset`: shrink only. `no_shrink`: reset only.
